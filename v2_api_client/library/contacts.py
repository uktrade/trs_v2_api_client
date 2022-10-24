from v2_api_client.library import BaseAPIClient
from v2_api_client.trs_object import TRSObject


class ContactObject(TRSObject):
    def change_organisation(self, organisation_id):
        return self.custom_action(
            "patch",
            "change_organisation",
            data={
                "organisation_id": organisation_id,
            }
        )


class ContactsAPIClient(BaseAPIClient):
    base_endpoint = "contacts"
    trs_object_class = ContactObject
