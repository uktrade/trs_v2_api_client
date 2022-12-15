from v2_api_client.library import BaseAPIClient


class InvitationsAPIClient(BaseAPIClient):
    def send_invitation(self, invitation_id):
        return self.post(
            self.url(f"invitations/{invitation_id}/send_invitation"),
            data={}
        )
