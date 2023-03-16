import io
from abc import abstractmethod, ABC

import pikepdf


class Extractor:
    def __call__(self, raw_data, content_type):
        data = io.BytesIO(raw_data)
        file_format = content_type

        if file_format == "application/pdf":
            return PDFExtractor().extract(data)


class BaseExtractMetaData(ABC):
    @abstractmethod
    def extract(self, data) -> io.BytesIO:
        raise NotImplementedError()


class PDFExtractor(BaseExtractMetaData):
    def extract(self, data) -> io.BytesIO:
        pdf = pikepdf.open(data)

        try:
            del pdf.Root.Metadata
        except KeyError:
            print("No XMP metadata.")

        try:
            del pdf.docinfo
        except AttributeError:
            print("No docinfo metadata.")

        pdf.save(data)
        pdf.close()

        return data
