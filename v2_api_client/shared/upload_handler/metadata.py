import io
from abc import abstractmethod, ABC
from docx import Document

import pikepdf


class Extractor:
    def __call__(self, raw_data, content_type):
        data = io.BytesIO(raw_data)
        file_format = content_type

        if file_format == "application/pdf":
            return PDFExtractor().extract(data)
        if file_format == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return DOCXExtractor().extract(data)


class BaseExtractMetaData(ABC):
    @abstractmethod
    def extract(self, data) -> io.BytesIO:
        raise NotImplementedError()


class DOCXExtractor(BaseExtractMetaData):
    def extract(self, data) -> io.BytesIO:
        docx = Document(data)

        fields = [
            attr
            for attr in dir(docx.core_properties)
            if isinstance(getattr(docx.core_properties, attr), str) and not attr.startswith("_")
        ]

        for field in fields:
            setattr(docx.core_properties, field, "")

        docx.save(data)

        return data


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
