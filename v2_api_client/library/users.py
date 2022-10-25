from v2_api_client.library import BaseAPIClient, TRSObject


class UserObject(TRSObject):
    def send_verification_email(self):
        return self.custom_action("get", "send_verification_email")

    def add_group(self, *args):
        """Adds user to the groups defined in args"""
        for group_name in args:
            result = self.custom_action("put", "change_group", data={"group_name": group_name})
        return result

    def delete_group(self, group_name):
        """Deletes user from Group group_name"""
        return self.custom_action("delete", "change_group", data={"group_name": group_name})


class UsersAPIClient(BaseAPIClient):
    base_endpoint = "users"
    trs_object_class = UserObject

    def get_user_by_email(self, email):
        return self._get(self.url(f"{self.get_base_endpoint()}/get_user_by_email/{email}"))

    def login(self, email, password, invitation_code=None, **kwargs):
        return self.post(self.url("login"), data={
            "email": email,
            "password": password,
            "invitation_code": invitation_code,
            **kwargs
        })


class TwoFactorAuthsAPIClient(BaseAPIClient):
    base_endpoint = "two_factor_auths"
