from v2_api_client.library import BaseAPIClient


class DocumentsAPIClient(BaseAPIClient):
    base_endpoint = "documents"

    def get_presigned_url(self, filename):
        return self.post(
            self.url("documents/s3-presigned-url"),
            data={"filename": filename},
        )


class DocumentBundlesAPIClient(BaseAPIClient):
    base_endpoint = "document_bundles"
