from v2_api_client.library import BaseAPIClient, TRSObject


class InvitationObject(TRSObject):
    def send(self):
        self.custom_action("post", "send_invitation")


class InvitationsAPIClient(BaseAPIClient):
    base_endpoint = "invitations"
    trs_object_class = InvitationObject
