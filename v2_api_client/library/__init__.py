from __future__ import annotations

import urllib
from functools import singledispatchmethod
from typing import Union
from uuid import UUID

from apiclient import APIClient, HeaderAuthentication, JsonResponseHandler
from apiclient.utils.typing import OptionalDict
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from dotwiz import DotWiz

from v2_api_client.error_handling import APIErrorHandler


class TRSObject:
    """An object returned by the TRS API.

    When making a call to the API, you will receive a response containing a dictionary of data. e.g.
    A dictionary of a submission object you have retrieved using a submission ID.

    The TRSObject class makes accessing, updating, and refreshing this object easy, it wraps the
    dictionary in a DotWiz object which allows you to parse it through both dot and key-lookup
    notation, e.g:

    submission = self.client.submissions({submission_id})  # submission is a TRSObject instance
    submission.type.name --> "Registration of Interest"
    submission["type"]["name"] --> "Registration of Interest"

    You can also use this object to easily update via the API, e.g.

    submission.update({"type": {submission_type_id}}) --> Newly updated submission TRSObject.

    The TRSObject also makes calling custom actions (those defined by an @action decorator in the
    API) easy. Furthermore, lazy loading is used to reduce unnecessary calls to the API, by passing
    a TRSObject a retrieval_url instead of actual response data, the object will only contact the
    API when strictly necessary (for example when accessing the DotWiz data).
    """
    object_id = None
    encoder = DjangoJSONEncoder

    def __init__(self, *args, **kwargs):
        self.lazy = kwargs.pop("lazy", None)
        self.has_retrieved_data = False
        self.object_id = kwargs.pop("object_id", None)

        if self.lazy:
            self.retrieval_url = kwargs.pop("retrieval_url")
            self._data = {}
        else:
            self._data = DotWiz(kwargs.pop("data"))

        self.api_client = kwargs.pop("api_client")
        self.changed_data = {}

        super().__init__(*args, **kwargs)

    def __getattribute__(self, item):
        """Allows for data_dict lookup through self.{key_name}"""
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return getattr(self.data_dict, item)

    def __getitem__(self, item):
        """Allows for data_dict lookup through self["key_name"]"""
        return self.data_dict[item]

    def __contains__(self, item):
        """Allows for 'if x in self' statements"""
        return item in self.data_dict

    def __repr__(self):
        """Generates a string representation of this object using the base_endpoint defined in the
        API client that generated it."""
        return f"{self.api_client.base_endpoint[:-1]} object {self.object_id}"

    @property
    def data_dict(self):
        """Wrapped in a property to allow for lazy retrieval from the API.

        First checks if this is a lazy object and if the API has not been contacted yet, if so,
        it will make the request and save the response in the private _data attribute.

        If the ._data attribute exists, it just returns that instead.
        """
        if self.lazy and not self.has_retrieved_data:
            self.has_retrieved_data = True
            data = DotWiz(self.api_client.get(self.retrieval_url))
            self._data = data

        return self._data

    def custom_action(
            self,
            method: str,
            action_name: str,
            data: OptionalDict = None,
            fields: list = None
    ):
        """
        Constructs and sends a request to a custom action in the API defined by a function
        wrapped with the @action decorator

        Parameters
        ----------
        method : the method to make the request with, e.g. GET or POST
        action_name : the name of the method in the API, marked by the url_path argument normally
        data : data to pass along with the request
        fields : what fields do you want the API to return

        Returns
        -------
        TRSObject or a list of them. Typically... All of the custom actions in the API should
        return a single object or a list of them, this is NOT guaranteed.
        """
        request_method = getattr(self.api_client, method)
        url = self.api_client.url(
            self.api_client.get_retrieve_endpoint(self.object_id, action_name),
            fields=fields
        )
        if method == "GET":
            request = request_method(url)
        else:
            if not data:
                data = dict()
            request = request_method(url, data=data)

        return request

    def update(self, data: dict, fields: list = None) -> TRSObject:
        """
        Sends a PATCH request to the API to update this object with the data provided.

        Parameters
        ----------
        data : the dictionary of data to send as part of the request
        fields : what fields you want returned in the response

        Returns
        -------
        A new TRSObject
        """
        return self.api_client.update(self.object_id, data, fields=fields)

    def delete(self):
        """Deletes this object."""
        return self.api_client.delete_object(self.object_id)

    def refresh(self) -> TRSObject:
        """Refreshes this object in-place by retrieving it again from teh API."""
        refreshed_object = self.api_client.retrieve(id=self.object_id)
        self.data = refreshed_object.data
        self.changed_data = {}
        return self


class BaseAPIClient(APIClient):
    """The Base client from which all specific object clients inherit from.

    Exposes all necessary instantiation behaviour and methods such as create, update, and retrieve.

    Uses singledispatchmethod to allow for dynamic instantiation depending on the type of arguments
    passed.
    """
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
        raise Exception(
            "You have to call the API client with either an: ID to retrieve a single object or a "
            "dictionary to create a new object. If you want to retrieve all objects as a list,"
            " please call .all()"
        )

    @__call__.register
    def _(self, arg: str, fields: list = None) -> TRSObject:
        """
        Retrieval of a single object with a string ID
        Parameters
        ----------
        arg : ID of the object
        fields : A list of fields you want returned by the API

        Returns
        -------
        An instance of a TRSObject

        Usage
        -------
        self({object_id})
        """
        return self.retrieve(id=arg, fields=fields)

    @__call__.register
    def _(self, arg: UUID, fields: list = None) -> TRSObject:
        """
        Retrieval of a single object with a UUID ID
        Parameters
        ----------
        arg : ID of the object
        fields : A list of fields you want returned by the API

        Returns
        -------
        An instance of a TRSObject

        Usage
        -------
        self({object_id})
        """
        return self.retrieve(id=arg, fields=fields)

    @__call__.register
    def _(self, arg: dict, fields: list = None) -> TRSObject:
        """
        Created of a single object.
        Parameters
        ----------
        arg : dictionary containing key/values you want in the new object
        fields : A list of fields you want returned by the API

        Returns
        -------
        An instance of a TRSObject

        Usage
        -------
        new_object = self({"key": "value", "name": "test"})
        """
        return self.create(data=arg, fields=fields)

    def get_trs_object_class(self):
        return self.trs_object_class

    def get_request_timeout(self) -> float:
        """Return the number of seconds before the request times out."""
        if self.timeout:
            return float(self.timeout)
        return 20.0

    @staticmethod
    def url(path: str, fields: list = None, **kwargs) -> str:
        """
        Helper function to generate URLs using the API_BASE_URL and path provided.

        Parameters
        ----------
        path : the path of the API endpoint
        fields : what fields you want returned by the API as defined by the "query" GET parameter
        kwargs : a dictionary of query parameters you want appended to the URL

        Returns
        -------
        a complete URL
        """
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

    def all(self, fields: list = None) -> list:
        """
        Returns all objects, a LIST
        Parameters
        ----------
        fields : what fields you want returned for each object

        Returns
        -------
        A list of TRSObject's
        """
        url = self.url(self.get_base_endpoint(), fields=fields)
        return self._get_many(url)

    def retrieve(self, id: Union[str, UUID], fields: list = None) -> TRSObject:
        """
        Gets a single object, a RETRIEVE

        Parameters
        ----------
        id : ID of the object you want
        fields : list of fields you want returned

        Returns
        -------
        An instance of TRSObject
        """
        url = self.url(self.get_retrieve_endpoint(id), fields=fields)
        return self._get(url)

    def update(self, object_id: Union[str, UUID], data: dict, fields: list = None) -> TRSObject:
        """
        Updates a particular object.

        Parameters
        ----------
        object_id : ID of the object you want to update
        data : dictionary of data you want to change
        fields : what fields you want returned

        Returns
        -------
        TRSObject
        """
        trs_object_class = self.get_trs_object_class()
        data = self.patch(self.url(self.get_retrieve_endpoint(object_id), fields=fields), data=data)
        return trs_object_class(
            data=data,
            api_client=self,
            object_id=data["id"]
        )

    def delete_object(self, id: Union[str, UUID]):
        """
        Deletes an object.

        Parameters
        ----------
        id : ID of the object you want to delete
        """
        return self.delete(self.url(self.get_retrieve_endpoint(id)))

    def create(self, data: dict, fields: list = None) -> TRSObject:
        """
        Creates a new object.

        Parameters
        ----------
        data : a dictionary of the data you want the new object to have
        fields : a list of fields you want the API to return

        Returns
        -------
        TRSObject
        """
        trs_object_class = self.get_trs_object_class()
        data = self.post(self.url(self.get_base_endpoint(), fields=fields), data=data)
        return trs_object_class(
            data=data,
            api_client=self,
            object_id=data["id"]
        )

    def _get(self, url: str, params: OptionalDict = None):
        """Wraps GET requests to return a TRSObject"""
        trs_object_class = self.get_trs_object_class()
        data = self.get(url, params=params)
        return trs_object_class(
            data=data,
            api_client=self,
            object_id=data["id"]
        )

    def _get_many(self, url: str, params: OptionalDict = None):
        """Wraps GET requests to an endpoint that returns a list of objects"""
        trs_object_class = self.get_trs_object_class()
        return [
            trs_object_class(
                data=each,
                api_client=self,
                lazy=False
            ) for each in self.get(url, params=params)
        ]
