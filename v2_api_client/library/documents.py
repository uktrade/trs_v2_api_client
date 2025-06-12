from v2_api_client.library import BaseAPIClient


class DocumentsAPIClient(BaseAPIClient):
    base_endpoint = "documents"

    def get_presigned_url(self, filename, av_scanned_at=None, av_passed=None):
        data = {"filename": filename}
        if av_passed:
            data["av_passed"] = av_passed
        if av_scanned_at:
            data["av_scanned_at"] = av_scanned_at

        return self.post(
            self.url("documents/s3-presigned-url"),
            data=data,
        )


class DocumentBundlesAPIClient(BaseAPIClient):
    base_endpoint = "document_bundles"
