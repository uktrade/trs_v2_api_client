from v2_api_client.library import BaseAPIClient


class OrganisationAPIClient(BaseAPIClient):
    base_endpoint = "organisations"

    def get_organisations_by_company_name(self, company_name):
        return self._get_many(self.url(
            f"{self.get_base_endpoint()}/search_by_company_name",
            params={"company_name": company_name}
        ))

class OrganisationCaseRoleAPIClient(BaseAPIClient):
    base_endpoint = "organisation_case_roles"

    def get_with_case_and_organisation(self, organisation_id: str, case_id: str):
        """Returns the OrganisationCaseRole object (if it exists) that is associated with a
        particular case and organisation object.
        """
        return self._get(self.url(self.get_base_endpoint(), params={
            "case_id": case_id,
            "organisation_id": organisation_id
        }))
