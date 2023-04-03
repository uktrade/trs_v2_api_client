from v2_api_client.library import BaseAPIClient
from v2_api_client.trs_object import TRSObject


class ContactObject(TRSObject):
    def change_organisation(self, organisation_id):
        return self.custom_action(
            "patch",
            "change_organisation",
            data={
                "organisation_id": organisation_id,
            },
        )

    def add_to_case(self, case_id, organisation_id=None, primary=False):
        return self.custom_action(
            "patch",
            "add_to_case",
            data={
                "case_id": case_id,
                "organisation_id": organisation_id,
                "primary": "yes" if primary else "no",
            },
        )


class ContactsAPIClient(BaseAPIClient):
    base_endpoint = "contacts"
    trs_object_class = ContactObject


class CaseContactsAPIClient(BaseAPIClient):
    base_endpoint = "case_contacts"
