from v2_api_client.library import BaseAPIClient


class DocumentsAPIClient(BaseAPIClient):

    def create_document(self, **kwargs):
        return self.post(self.url("documents"), data=kwargs)
