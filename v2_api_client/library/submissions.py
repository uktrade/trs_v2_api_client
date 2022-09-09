from __future__ import annotations
from v2_api_client.library import BaseAPIClient, TRSObject


class SubmissionObject(TRSObject):
    def add_organisation_to_registration_of_interest(
        self,
        organisation_id,
        contact_id
    ):
        return self.custom_action(
            "put",
            "add_organisation_to_registration_of_interest",
            data={
                "organisation_id": organisation_id,
                "contact_id": contact_id
            }
        )


class SubmissionsAPIClient(BaseAPIClient):
    base_endpoint = "submissions"
    trs_object_class = SubmissionObject
