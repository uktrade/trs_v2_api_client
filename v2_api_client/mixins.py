from v2_api_client.client import APIClient
from django.conf import settings

class APIClientMixin:
    @property
    def client(self, *args, **kwargs):
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            kwargs.setdefault("token", self.request.user.token)
        return APIClient(*args, **kwargs)
