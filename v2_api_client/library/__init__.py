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
        return self.get(self.url(self.get_base_endpoint()))

    def get_one(self, id):
        return self.get(self.url(f"{self.get_retrieve_endpoint(id)}"))

    def update(self):
        return
