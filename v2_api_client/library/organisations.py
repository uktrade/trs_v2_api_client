from v2_api_client.library import BaseAPIClient
from v2_api_client.trs_object import TRSObject


class OrganisationObject(TRSObject):
    def add_user(self, user_id, group_name, confirmed, **kwargs):
        return self.custom_action(
            "put",
            "add_user",
            data={
                "user_id": user_id,
                "organisation_security_group": group_name,
                "confirmed": confirmed,
            },
            **kwargs,
        )

    def find_similar_organisations(self, **kwargs):
        return self.custom_action("get", "find_similar_organisations", **kwargs)

    def has_similar_organisations(self, **kwargs):
        return self.custom_action("get", "has_similar_organisations", **kwargs)

    def organisation_card_data(self, **kwargs):
        return self.custom_action("get", "get_organisation_card_data", **kwargs)


class OrganisationAPIClient(BaseAPIClient):
    base_endpoint = "organisations"
    trs_object_class = OrganisationObject

    def get_organisations_by_company_name(self, company_name, **kwargs):
        return self._get_many(
            self.url(
                f"{self.get_base_endpoint()}/search_by_company_name",
                params={"company_name": company_name, **kwargs},
            )
        )

    def get_organisation_cards(self, *args):
        urls = [
            self.url(
                self.get_retrieve_endpoint(object_id, "get_organisation_card_data"),
            )
            for object_id in args
        ]
        return self.get_concurrently(urls)


class OrganisationCaseRoleAPIClient(BaseAPIClient):
    base_endpoint = "organisation_case_roles"

    def get_with_case_and_organisation(self, organisation_id: str, case_id: str):
        """Returns the OrganisationCaseRole object (if it exists) that is associated with a
        particular case and organisation object.
        """
        return self._get_many(
            self.url(
                self.get_base_endpoint(),
                params={"case_id": case_id, "organisation_id": organisation_id},
            )
        )


class OrganisationMergeRecordObject(TRSObject):
    def get_draft_merged_organisation(self, **kwargs):
        return self.custom_action("get", "get_draft_merged_organisation", **kwargs)

    def get_draft_merged_selections(self, current_duplicate_id=None, **kwargs):
        """Returns what the Organisation would look like if the current merge selection were applied.
        Can also be used to get a list of identical fields between the draft organisation and the
        current duplicate being considered.
        """
        params = kwargs.pop("params", {})
        if current_duplicate_id:
            params["current_duplicate_id"] = current_duplicate_id

        return self.custom_action(
            "get", "get_draft_merged_selections", params=params, **kwargs
        )

    def merge_organisations(self, **kwargs):
        return self.custom_action("post", "merge_organisations", **kwargs)

    def reset(self, **kwargs):
        """Resets all potential duplicates to their fresh state, pending and all attributes forgotten"""
        return self.custom_action("patch", "reset", **kwargs)

    def get_duplicate_cases(self, **kwargs):
        return self.custom_action("get", "get_duplicate_cases", **kwargs)


class OrganisationMergeRecordAPIClient(BaseAPIClient):
    base_endpoint = "organisation_merge_records"
    trs_object_class = OrganisationMergeRecordObject


class DuplicateOrganisationMergeAPIClient(BaseAPIClient):
    base_endpoint = "duplicate_organisation_merges"


class OrganisationUserAPIClient(BaseAPIClient):
    base_endpoint = "organisation_users"
