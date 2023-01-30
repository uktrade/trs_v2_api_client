from __future__ import annotations

from v2_api_client.library import BaseAPIClient, TRSObject


class SubmissionObject(TRSObject):
    def add_organisation_to_registration_of_interest(
            self,
            organisation_id,
    ):
        return self.custom_action(
            "put",
            "add_organisation_to_registration_of_interest",
            data={
                "organisation_id": organisation_id,
            },
            fields=["id"]
        )

    def update_submission_status(self, new_status):
        return self.custom_action(
            "put",
            "update_submission_status",
            data={
                "new_status": new_status
            },
            fields=["id"]
        )


class SubmissionsAPIClient(BaseAPIClient):
    base_endpoint = "submissions"
    trs_object_class = SubmissionObject


class SubmissionOrganisationMergeRecordAPIClient(BaseAPIClient):
    base_endpoint = "submission_organisation_merge_records"
