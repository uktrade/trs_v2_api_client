from __future__ import annotations

import urllib
from functools import singledispatchmethod
from uuid import UUID

from apiclient import APIClient, HeaderAuthentication, JsonResponseHandler
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from dotwiz import DotWiz
from v2_api_client.error_handling import APIErrorHandler


class TRSObject:
    object_id = None
    encoder = DjangoJSONEncoder

    def custom_get_attribute(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return getattr(self.data_dict, item)

    def custom_set_attribute(self, key, value):
        if key == "data":
            # We don't want to mess with this when we're initially setting the data attribute
            return super().__setattr__(key, value)
        if key in self.data:
            self.changed_data[key] = value
        return super().__setattr__(key, value)


    def __init__(self, *args, **kwargs):
        #self.__dict__["_data"] = DotWiz(kwargs.pop("data"))
        #self.__dict__["lazy"] = kwargs.pop("lazy")
        #self.__dict__["has_retrieved_data"] = False
        #self.__dict__["api_client"] = kwargs.pop("api_client")
        #self.__dict__["object_id"] = self.data["id"]
        #self.__dict__["changed_data"] = {}
        super().__init__(*args, **kwargs)
        self.lazy = kwargs.pop("lazy")
        self.has_retrieved_data = False
        if not self.lazy:
            self.data = DotWiz(kwargs.pop("data"))
            self.object_id = self.data["id"]
        self.api_client = kwargs.pop("api_client")
        self.changed_data = {}

        self.__getattribute__ = custom_get_attribute
        self.__setattr__ = custom_set_attribute

    def __getitem__(self, item):
        return self.data_dict[item]

    def __repr__(self):
        return f"{self.api_client.base_endpoint[:-1]} object {self.object_id}"

    @property
    def data_dict(self):
        if self.lazy and not self.has_retrieved_data:
            self.has_retrieved_data = True
            self._data = self.api_client.get(self._data)
        return self._data

    @property
    def retrieve_url(self):
        return self.api_client.url(self.api_client.get_retrieve_endpoint(self.object_id))

    def custom_action(self, method, action_name, data=None):
        request_method = getattr(self.api_client, method)
        url = f"{self.retrieve_url}{action_name}/"
        if method == "GET":
            return request_method(url)
        else:
            if not data:
                data = dict()
            return request_method(url, data=data)

    def save(self):
        if self.changed_data:
            return self.api_client.update(self.object_id, self.changed_data)
        return self.data

    def update(self, data):
        return self.api_client.update(self.object_id, data)

    def delete(self):
        return self.api_client.delete(self.url(self.get_retrieve_endpoint(self.object_id)))

    def refresh(self):
        refreshed_object = self.api_client.retrieve(id=self.object_id)
        self.data = refreshed_object.data
        self.changed_data = {}
        return self


class BaseAPIClient(APIClient):
    base_endpoint = None
    trs_object_class = TRSObject

    def __init__(
            self,
            response_handler=JsonResponseHandler,
            error_handler=APIErrorHandler,
            **kwargs
    ):
        self.timeout = kwargs.pop("timeout", None)
        authentication_method = HeaderAuthentication(
            token=kwargs.pop("token", settings.HEALTH_CHECK_TOKEN),
            parameter="Authorization",
            scheme="Token",
            extra={"X-Origin-Environment": settings.ENVIRONMENT_KEY}
        )
        super().__init__(
            authentication_method=authentication_method,
            response_handler=response_handler,
            error_handler=error_handler,
            **kwargs
        )

    @singledispatchmethod
    def __call__(self, arg, fields: list = None):
        return self()

    @__call__.register
    def _(self, arg: str, fields: list = None):
        return self.retrieve(id=arg, fields=fields)

    @__call__.register
    def _(self, arg: UUID, fields: list = None):
        return self.retrieve(id=arg, fields=fields)

    @__call__.register
    def _(self, arg: dict, fields: list = None):
        return self.create(data=arg, fields=fields)

    def get_trs_object_class(self):
        return self.trs_object_class

    def get_request_timeout(self) -> float:
        """Return the number of seconds before the request times out."""
        if self.timeout:
            return float(self.timeout)
        return 20.0

    @staticmethod
    def url(path, fields=None, **kwargs):
        url = f"{settings.API_BASE_URL}/api/v2/{path}/"
        if fields:
            fields = {"query": f"{{{','.join(fields)}}}"}
        if fields or kwargs:
            if query_parameters := urllib.parse.urlencode({**kwargs, **fields}):
                url += f"?{query_parameters}"
        return url

    def get_base_endpoint(self):
        return self.base_endpoint

    def get_retrieve_endpoint(self, id: str, *args) -> str:
        """
        Gets the retrieve() endpoint for this particular APIClient. Can also take any number of
        *args which are appended to the URL delimited by forward slashes
        Parameters
        ----------
        id : str - ID of the object in question
        args : list - list of paths to append to the URL

        Returns
        -------
        str
        """
        retrieve_url = f"{self.get_base_endpoint()}/{id}"
        for extra_path in args:
            retrieve_url += f"/{extra_path}"
        return retrieve_url

    def all(self):
        trs_object_class = self.get_trs_object_class()
        return [
            trs_object_class(
                data=each,
                api_client=self,
            ) for each in self.get(self.url(self.get_base_endpoint()))
        ]

    def retrieve(self, id, fields=None, lazy=True):
        trs_object_class = self.get_trs_object_class()
        if lazy:
            data = self.url(self.get_retrieve_endpoint(id), fields=fields)
        else:
            data = self.get(self.url(self.get_retrieve_endpoint(id), fields=fields))
        return trs_object_class(
            data=data,
            api_client=self,
            lazy=lazy
        )

    def update(self, object_id, data):
        return self.put(self.url(self.get_retrieve_endpoint(object_id)), data=data)

    def delete_object(self, id):
        return self.delete(self.url(self.get_retrieve_endpoint(id)))

    def create(self, data, fields=None):
        trs_object_class = self.get_trs_object_class()
        return trs_object_class(
            data=self.post(self.url(self.get_base_endpoint(), fields=fields), data=data),
            api_client=self
        )
