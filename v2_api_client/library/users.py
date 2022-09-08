from v2_api_client.library import BaseAPIClient


class UsersAPIClient(BaseAPIClient):
    base_endpoint = "users"

    def get_user_by_email(self, email):
        return self.get_trs_object_class()(self.get(self.url(f"{self.get_base_endpoint()}/get_user_by_email/{email}")))

    def login(self, email, password, invitation_code=None, **kwargs):
        return self.post(self.url("login"), data={
            "email": email,
            "password": password,
            "invitation_code": invitation_code,
            **kwargs
        })
