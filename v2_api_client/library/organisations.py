from v2_api_client.library import BaseAPIClient
from v2_api_client.trs_object import TRSObject
import concurrent.futures

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
            **kwargs
        )


class OrganisationAPIClient(BaseAPIClient):
    base_endpoint = "organisations"
    trs_object_class = OrganisationObject

    def _get_many(self, url):
        """Fetches all organisations concurrently using the Python ThreadPoolExecutor with a paginated API endpoint"""
        results = []
        response = self.get(url)
        pages = response["total_pages"]

        URLS = [f"{url}?page={number}" for number in range(1, pages + 1)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(self.get, url): url for url in URLS}

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results.extend(future.result()["results"])
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))

        trs_object_class = self.get_trs_object_class()

        return [trs_object_class(data=result, api_client=self, lazy=False, object_id=result["id"]) for result in results]

    def get_organisations_by_company_name(self, company_name, **kwargs):
        return self._get_many(self.url(
            f"{self.get_base_endpoint()}/search_by_company_name",
            params={"company_name": company_name, **kwargs}
        ))


class OrganisationCaseRoleAPIClient(BaseAPIClient):
    base_endpoint = "organisation_case_roles"

    def get_with_case_and_organisation(self, organisation_id: str, case_id: str):
        """Returns the OrganisationCaseRole object (if it exists) that is associated with a
        particular case and organisation object.
        """
        return self._get_many(self.url(self.get_base_endpoint(), params={
            "case_id": case_id,
            "organisation_id": organisation_id
        }))


class OrganisationUserClient(BaseAPIClient):
    base_endpoint = "organisation_users"
