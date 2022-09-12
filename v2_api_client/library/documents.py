from v2_api_client.library import BaseAPIClient


class DocumentsAPIClient(BaseAPIClient):
    base_endpoint = "documents"

class DocumentBundlesAPIClient(BaseAPIClient):
    base_endpoint = "document_bundles"

    def retrieve_with_submission_type_id(self, submission_type_id):
        return self.retrieve(self.url(self.get_retrieve_endpoint()))
