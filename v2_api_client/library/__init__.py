from apiclient import APIClient, HeaderAuthentication, JsonResponseHandler
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from dotwiz import DotWiz

from v2_api_client.dicts import TrackedChangedDict
from v2_api_client.error_handling import APIErrorHandler


class TRSObject:
    object_id = None
    encoder = DjangoJSONEncoder

    def __init__(self, *args, **kwargs):
        self.data = DotWiz(kwargs.pop("data"))
        self.api_client = kwargs.pop("api_client")
        self.object_id = self.data["id"]
        self.changed_data = {}
        super().__init__(*args, **kwargs)
        # de-serialize dictionary data into python builtins and set as attributes
        # will use generic JSON serializers but also have the ability to write
        # custom ones to deal with more complex data types
        # self.encode_data()

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return getattr(self.data, item)

    def __getitem__(self, item):
        return self.data[item]

    def __repr__(self):
        return f"{self.api_client.base_endpoint[:-1]} object {self.object_id}"

    def __setattr__(self, key, value):
        if key == "data":
            # We don't want to mess with this when we're initially setting the data attribute
            return super().__setattr__(key, value)
        if key in self.data:
            self.changed_data[key] = value
        return super().__setattr__(key, value)

    @property
    def retrieve_url(self):
        return self.api_client.url(self.api_client.get_retrieve_endpoint(self.object_id))

    def custom_action(self, method, action_name, data=None):
        request_method = getattr(self.api_client, method)
        url = f"{self.retrieve_url}/{action_name}/"

        if data:
            return request_method(url, data=data)
        else:
            return request_method(url)

    def save(self):
        if self.changed_data:
            return self.api_client.update(self.object_id, self.changed_data)
        return self.data



class BaseAPIClient(APIClient):
    base_endpoint = None

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

    def __call__(self, object_id=None):
        if object_id:
            return self.retrieve(object_id)
        return self.all()

    def get_request_timeout(self) -> float:
        """Return the number of seconds before the request times out."""
        if self.timeout:
            return float(self.timeout)
        return 40.0

    @staticmethod
    def url(path, **kwargs):
        url = f"{settings.API_BASE_URL}/api/v2/{path}/"
        if kwargs:
            added = False
            for parameter, value in kwargs.items():
                if value:
                    if added:
                        delimiter = "&"
                    else:
                        delimiter = "?"
                    url += f"{delimiter}{parameter}={value}"
                    added = True
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
        # return self.get(self.url(self.get_retrieve_endpoint(id)))
        return [
            TRSObject(
                data=each,
                api_client=self,
            ) for each in self.get(self.url(self.get_base_endpoint()))
        ]

    def retrieve(self, id):
        # return self.get(self.url(self.get_retrieve_endpoint(id)))
        return TRSObject(
            data=self.get(self.url(self.get_retrieve_endpoint(id))),
            api_client=self,
        )

    def update(self, object_id, data):
        return self.put(self.url(self.get_retrieve_endpoint(object_id)), data=data)

    def delete_object(self, id):
        return self.delete(self.url(self.get_retrieve_endpoint(id)))

    def create(self, **kwargs):
        return self.post(self.url(self.get_base_endpoint()), data=kwargs)
