from apiclient import APIClient, HeaderAuthentication, JsonResponseHandler
from django.conf import settings

from error_handling import APIErrorHandler

class BaseAPIClient(APIClient):
    def __init__(
            self,
            response_handler=JsonResponseHandler,
            error_handler=APIErrorHandler,
            **kwargs
    ):
        authentication_method = HeaderAuthentication(
            token=kwargs.get("token") or settings.HEALTH_CHECK_TOKEN,
            parameter="Authorization",
            scheme="Token"
        )
        super().__init__(
            authentication_method=authentication_method,
            response_handler=response_handler,
            error_handler=error_handler,
            **kwargs
        )

    @staticmethod
    def url(path):
        return f"{settings.API_BASE_URL}/api/v2/{path}"
