from v2_api_client.library import BaseAPIClient


class OrganisationAPIClient(BaseAPIClient):
    base_endpoint = "organisations"

    def add_user_to_organisation(self):
        pass


class OrganisationCaseRoleAPIClient(BaseAPIClient):
    base_endpoint = "organisation_case_roles"
