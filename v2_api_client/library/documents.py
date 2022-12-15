from v2_api_client.library import BaseAPIClient


class DocumentsAPIClient(BaseAPIClient):
    base_endpoint = "documents"


class DocumentBundlesAPIClient(BaseAPIClient):
    base_endpoint = "document_bundles"
