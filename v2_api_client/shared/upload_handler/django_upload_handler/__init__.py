from zipfile import BadZipFile

from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from pikepdf import PdfError

from v2_api_client.shared.upload_handler.metadata import Extractor

FILE_MAX_SIZE_BYTES_ERROR = (
    f"The selected file must be smaller than "
    f"{round(settings.FILE_MAX_SIZE_BYTES / (1024 * 1024))}MB"
)


class ExtractMetadataFileUploadHandler(FileUploadHandler):
    def file_complete(self, file_size):
        pass

    def receive_data_chunk(self, raw_data, start):
        if len(raw_data) > settings.FILE_MAX_SIZE_BYTES:
            raise StopUpload(FILE_MAX_SIZE_BYTES_ERROR)

        extractor = Extractor()
        try:
            _, sanitised_data = extractor(raw_data, self.content_type)
        except (BadZipFile, PdfError):
            raise StopUpload("There was an error processing this file")


        if isinstance(sanitised_data, bytes):
            return sanitised_data
        else:
            return sanitised_data.getvalue()
