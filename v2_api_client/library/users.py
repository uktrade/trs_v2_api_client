from v2_api_client.library import BaseAPIClient

class UsersAPIClient(BaseAPIClient):
    def login(self, email, password, invitation_code=None, **kwargs):
        return self.post(self.url("login"), data={
            "email": email,
            "password": password,
            "invitation_code": invitation_code,
            **kwargs
        })
