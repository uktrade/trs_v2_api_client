from v2_api_client.library import BaseAPIClient


class InvitationsAPIClient(BaseAPIClient):
    base_endpoint = "invitations"

    def send(self, invitation_id):
        return self.post(
            self.url(self.get_retrieve_endpoint(invitation_id, "send_invitation")),
            data={}
        )
