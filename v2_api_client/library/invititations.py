from v2_api_client.library import BaseAPIClient, TRSObject


class InvitationObject(TRSObject):
    def send(self):
        return self.custom_action("post", "send_invitation")

    def create_user_from_invitation(self, password):
        self.custom_action(
            "post",
            "create_user_from_invitation",
            data={"password": password})


class InvitationsAPIClient(BaseAPIClient):
    base_endpoint = "invitations"
    trs_object_class = InvitationObject
