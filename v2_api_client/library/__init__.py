from __future__ import annotations

import urllib
from typing import Union
from uuid import UUID

from apiclient import APIClient, HeaderAuthentication, JsonResponseHandler
from django.conf import settings

from v2_api_client.error_handling import APIErrorHandler
from v2_api_client.trs_object import TRSObject


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

    def __call__(
            self,
            arg: Union[str, UUID, dict, None] = None,
            fields: list[str] = None,
            params: dict = None
    ) -> Union[TRSObject, list[TRSObject]]:
        """
        Can do the following:

        Retrieval of a single object with a string/UUID ID
        Retrieval of all objects
        Creation of a new object with a data dictionary

        Parameters
        ----------
        arg : ID of the object
        fields : A list of fields you want returned by the API
        params : a dict of query parameters to append to the URL

        Returns
        -------
        An instance of a TRSObject OR list of TRSObjects

        Usage
        -------
        self({object_id}) --> Retrieves a single instance - GET
        self() --> Lists all instances - GET
        self({"key": "value"}) --> Creates and retrieves a single instance - POST
        """
        if arg is None:
            # it's called with no args, return all
            url = self.url(self.get_base_endpoint(), fields=fields, params=params)
            return self._get_many(url)
        if isinstance(arg, str) or isinstance(arg, UUID):
            # it's called with a str or UUID ID, retrieve one instance
            url = self.url(self.get_retrieve_endpoint(arg), fields=fields, params=params)
            return self._get(url=url)
        if isinstance(arg, dict):
            # it's called with a dict, create and retrieve one instance
            url = self.url(self.get_base_endpoint(), fields=fields, params=params)
            return self._post(url=url, data=arg)

    def get_trs_object_class(self):
        return self.trs_object_class

    def get_request_timeout(self) -> float:
        """Return the number of seconds before the request times out."""
        if self.timeout:
            return float(self.timeout)
        return 20.0

    @staticmethod
    def url(path: str, fields: list = None, params: dict = None) -> str:
        """
        Helper function to generate URLs using the API_BASE_URL and path provided.

        Parameters
        ----------
        path : the path of the API endpoint
        fields : what fields you want returned by the API as defined by the "query" GET parameter
        params : a dictionary of query parameters you want appended to the URL

        Returns
        -------
        a complete URL
        """
        url = f"{settings.API_BASE_URL}/api/v2/{path}/"
        if fields:
            fields = {"query": f"{{{','.join(fields)}}}"}
        if fields or params:
            if not fields:
                fields = {}
            if not params:
                params = {}
            if query_parameters := urllib.parse.urlencode({**params, **fields}):
                url += f"?{query_parameters}"
        return url

    def get_base_endpoint(self):
        return self.base_endpoint

    def get_retrieve_endpoint(self, object_id: Union[str, UUID], *args) -> str:
        """
        Gets the retrieve() endpoint for this particular APIClient. Can also take any number of
        *args which are appended to the URL delimited by forward slashes
        Parameters
        ----------
        object_id : ID of the object in question
        args : list of paths to append to the URL

        Returns
        -------
        str
        """
        retrieve_url = f"{self.get_base_endpoint()}/{object_id}"

        for extra_path in args:
            retrieve_url += f"/{extra_path}"
        return retrieve_url

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

    def delete_object(self, object_id: Union[str, UUID]):
        """
        Deletes an object.

        Parameters
        ----------
        object_id : ID of the object you want to delete
        """
        return self.delete(self.url(self.get_retrieve_endpoint(object_id)))

    def _post(self, url: str, data: dict):
        """Wraps POST requests to return a TRSObject"""
        trs_object_class = self.get_trs_object_class()
        data = self.post(url, data=data)
        return trs_object_class(
            data=data,
            api_client=self,
            object_id=data["id"],
            retrieval_url=self.get_retrieve_endpoint(object_id=data["id"])
        )

    def _get(self, url: str):
        """Wraps GET requests to return a TRSObject"""
        trs_object_class = self.get_trs_object_class()
        data = self.get(url)
        return trs_object_class(
            data=data,
            api_client=self,
            object_id=data["id"],
            retrieval_url=url
        )

    def _get_many(self, url: str):
        """Wraps GET requests to an endpoint that returns a list of objects"""
        trs_object_class = self.get_trs_object_class()
        return [
            trs_object_class(
                data=each,
                api_client=self,
                lazy=False,
                retrieval_url=self.get_retrieve_endpoint(object_id=each["id"])
            ) for each in self.get(url)
        ]
