from v2_api_client.library import BaseAPIClient, TRSObject


class CaseObject(TRSObject):
    def add_user(self, user_id):
        self.custom_action("post", "add_user", data={"user": user_id})

    def get_invitations(self):
        return self.custom_action("get", "get_invitations")

    def get_submissions(self, params):
        return self.custom_action("get", "get_submissions", params=params)

    def get_status(self):
        return self.custom_action("get", "get_status")

    def get_applicant(self):
        return self.custom_action("get", "get_applicant")

    def get_public_file(self):
        return self.custom_action("get", "get_public_file")

class CasesAPIClient(BaseAPIClient):
    base_endpoint = "cases"
    trs_object_class = CaseObject

    def open_to_roi(self):
        return self._get_many(
            self.url(self.get_base_endpoint(), params={"open_to_roi": True})
        )

    def get_case_by_number(self, case_number, fields=None):
        case_object = self._get(
            self.url(
                self.get_base_endpoint() + "/get_case_by_number",
                params={"case_number": case_number},
                fields=fields,
            )
        )
        case_object.object_id = case_object.id  # we need to force an evaluation
        return case_object