from v2_api_client.library import BaseAPIClient


class CasesAPIClient(BaseAPIClient):
    def get_cases(self, **kwargs):
        return self.get(self.url("cases", **kwargs))
