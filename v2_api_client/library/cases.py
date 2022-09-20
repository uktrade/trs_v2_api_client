from v2_api_client.library import BaseAPIClient, TRSObject


class CaseObject(TRSObject):
    def add_user(self, user_id):
        self.custom_action("post", "add_user", data={"user": user_id})


class CasesAPIClient(BaseAPIClient):
    base_endpoint = "cases"
    trs_object_class = CaseObject

    def open_to_roi(self):
        return self._get_many(self.url(self.get_base_endpoint(), params={"open_to_roi": True}))
