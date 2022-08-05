from v2_api_client.client import APIClient


class APIClientMixin:
    @property
    def client(self, *args, **kwargs) -> APIClient:
        """
        Return an instance of APIClient loaded with the user's token if they are logged in.
        """
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            kwargs.setdefault("token", self.request.user.token)
        return APIClient(*args, **kwargs)

    def call_client(self, *args, **kwargs) -> APIClient:
        """
        Return an instance of APIClient loaded with the user's token if they are logged in. Can
        accept arguments passed.
        """
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            kwargs.setdefault("token", self.request.user.token)
        return APIClient(*args, **kwargs)
