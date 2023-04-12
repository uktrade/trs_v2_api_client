from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler, StopUpload

from v2_api_client.shared.upload_handler.metadata import Extractor


class ExtractMetadataFileUploadHandler(FileUploadHandler):
    def file_complete(self, file_size):
        pass

    def receive_data_chunk(self, raw_data, start):
        if len(raw_data) > settings.FILE_MAX_SIZE_BYTES:
            raise StopUpload(settings.FILE_MAX_SIZE_BYTES_ERROR)

        extractor = Extractor()
        sanitised_data = extractor(raw_data, self.content_type)

        return sanitised_data.getvalue()
