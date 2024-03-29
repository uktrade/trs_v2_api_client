from __future__ import annotations

from apiclient.utils.typing import OptionalDict
from django.core.serializers.json import DjangoJSONEncoder
from dotwiz import DotWiz

from v2_api_client.decoders import encode


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
        if self.lazy:
            self._data = {}
        else:
            self._data = DotWiz(kwargs.pop("data"))
            self.encode_nested_dict(self._data)

        self.api_client = kwargs.pop("api_client", None)
        self.object_id = kwargs.pop("object_id", None)
        self.retrieval_url = kwargs.pop("retrieval_url", None)
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

    def encode_nested_dict(self, in_dict: dict) -> None:
        """
        Recursively encodes all values the in_dict (in-place).

        e.g.

        {
            "sub_dict": {
                "date_created": "2023-03-21T13:23:20"
            }
        }

        --->
        TURNS TO
        --->

        {
            "sub_dict": {
                "date_created": datetime.datetime(year=2023, month=3, day=21, hour=13, minute=23)
            }
        }

        Parameters
        ----------
        in_dict : a dictionary that you want to encode

        Returns
        -------
        None, it performs the encoding in-place
        """
        for k, v in in_dict.items():
            if isinstance(v, DotWiz):
                self.encode_nested_dict(v)
            elif isinstance(v, list):
                for o in v:
                    if isinstance(o, DotWiz):
                        self.encode_nested_dict(o)
            else:
                in_dict[k] = encode(v)

    @property
    def data_dict(self):
        """Wrapped in a property to allow for lazy retrieval from the API.

        First checks if this is a lazy object and if the API has not been contacted yet, if so,
        it will make the request and save the response in the private _data attribute.

        If the ._data attribute exists, it just returns that instead.
        """
        if self._data:
            return self._data

        if self.lazy and self.retrieval_url:
            data = DotWiz(self.api_client.get(self.retrieval_url))
            self._data = data
            self.object_id = data["id"]
            self.encode_nested_dict(self._data)

        return self._data

    def custom_action(
        self,
        method: str,
        action_name: str,
        data: OptionalDict = None,
        fields: list = None,
        params: dict = None,
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
        params : what URL parameters you want to add to the API request

        Returns
        -------
        TRSObject or a list of them. Typically... All of the custom actions in the API should
        return a single object or a list of them, this is NOT guaranteed.
        """
        request_method = getattr(self.api_client, method)
        url = self.api_client.url(
            self.api_client.get_retrieve_endpoint(self.object_id, action_name),
            fields=fields,
            params=params,
        )
        if method in ["GET", "get"]:
            response = request_method(url)
        else:
            if not data:
                data = dict()
            response = request_method(url, data=data)

        return response

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

    def refresh(self, remove_query_params: bool = False) -> TRSObject:
        """
        Refreshes this object in-place by retrieving it again from the API.

        Parameters
        ----------
        remove_query_params : if True, all previous query params use to retrieve this object will
        be forgotten and a *fresh* retrieval will be made. If False, the same query parameters
        used to retrieve this object will be used to refresh it

        Returns
        -------
        self
        """
        if remove_query_params:
            url = self.api_client.get_retrieve_endpoint(object_id=self.object_id)
        else:
            url = self.retrieval_url
        refreshed_object = self.api_client._get(url=url, object_id=self.object_id)
        self.data = refreshed_object.data
        self.changed_data = {}
        return self
