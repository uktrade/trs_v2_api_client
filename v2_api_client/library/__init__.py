from apiclient import APIClient, HeaderAuthentication, JsonResponseHandler
from django.conf import settings

from v2_api_client.error_handling import APIErrorHandler


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

    def get_request_timeout(self) -> float:
        """Return the number of seconds before the request times out."""
        if self.timeout:
            return float(self.timeout)
        return 10.0

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

    def get_retrieve_endpoint(self, id):
        return f"{self.get_base_endpoint()}/{id}"

    def all(self):
        return [

        ]


        return self.get(self.url(self.get_base_endpoint()))

    def retrieve(self, id):
        return TRSObject(
            data=self.get(self.url(f"{self.get_retrieve_endpoint(id)}")),
            api_client=self
        )

    def update(self, id, data):
        return TRSObject(self.post(self.url(f"{self.get_retrieve_endpoint(id)}")))


class TRSObject:
    model_id = None

    def __init__(self, *args, **kwargs):
        self.api_client = kwargs.pop("api_client")
        self.data = kwargs.pop("data")
        super().__init__(*args, **kwargs)
        # de-serialize dictionary data into python builtins and set as attributes
        # will use generic JSON serializers but also have the ability to write
        # custom ones to deal with more complex data types

    def save(self):
        self.api_client.update(self, self.post_data)

    @property
    def post_data(self):
        # serialize python attributes to json so it can be sent to API
        pass
