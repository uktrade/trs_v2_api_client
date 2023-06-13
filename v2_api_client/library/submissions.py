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
            fields=["id"],
        )

    def update_submission_status(self, new_status):
        return self.custom_action(
            "put",
            "update_submission_status",
            data={"new_status": new_status},
            fields=["id"],
        )


class SubmissionOrganisationMergeRecordObject(TRSObject):
    def update(self, data: dict, fields: list = None) -> TRSObject:
        """The SubmissionOrganisationMergeRecordViewSet requires an organisation_id query parameter to
        be passed in the URL, so we need to override the update method to use the self.retrieval_url
        which contains the query parameter (by definition), otherwise we get a 404 error."""
        data = self.api_client.patch(
            self.retrieval_url, data=data
        )
        return self.__class__(data=data, api_client=self.api_client, object_id=data["id"])


class SubmissionsAPIClient(BaseAPIClient):
    base_endpoint = "submissions"
    trs_object_class = SubmissionObject


class SubmissionOrganisationMergeRecordAPIClient(BaseAPIClient):
    base_endpoint = "submission_organisation_merge_records"
    trs_object_class = SubmissionOrganisationMergeRecordObject
