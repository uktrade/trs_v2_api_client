from django.conf import settings

from v2_api_client.client import TRSAPIClient


class APIClientMixin:
    @property
    def client(self, *args, **kwargs) -> TRSAPIClient:
        """
        Return an instance of APIClient loaded with the user's token if they are logged in.
        """
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            kwargs.setdefault("token", self.request.user.token)
        else:
            kwargs.setdefault("token", settings.HEALTH_CHECK_TOKEN)
        return TRSAPIClient(*args, **kwargs)

    def call_client(self, *args, **kwargs) -> TRSAPIClient:
        """
        Return an instance of APIClient loaded with the user's token if they are logged in. Can
        accept arguments passed.
        """
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            kwargs.setdefault("token", self.request.user.token)
        return TRSAPIClient(*args, **kwargs)
