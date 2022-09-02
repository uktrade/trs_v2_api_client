from v2_api_client.library import BaseAPIClient, TRSObject


class CasesAPIClient(BaseAPIClient):
    base_endpoint = "cases"

    class CaseObject(TRSObject):
        def add_user(self, user_id):
            self.custom_action("post", "add_user", data={"user": user_id})
