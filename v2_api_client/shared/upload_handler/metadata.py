import io
from abc import abstractmethod, ABC

import pikepdf
from docx import Document
from openpyxl import load_workbook


class Extractor:
    def __call__(self, raw_data, content_type):
        data = io.BytesIO(raw_data)
        file_format = content_type

        if file_format == "application/pdf":
            return PDFExtractor().extract(data)
        if file_format == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return DOCXExtractor().extract(data)
        if file_format == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return XLSXExtractor().extract(data)


class BaseExtractMetaData(ABC):
    @abstractmethod
    def extract(self, data) -> io.BytesIO:
        raise NotImplementedError()


class XLSXExtractor(BaseExtractMetaData):
    def extract(self, data) -> io.BytesIO:
        xlsx = load_workbook(data)

        fields = [
            attr
            for attr in dir(xlsx.properties)
            if isinstance(getattr(xlsx.properties, attr), str)
            and not attr.startswith("_")
            and not attr == "tagname"
            and not attr == "namespace"
        ]

        for field in fields:
            setattr(xlsx.properties, field, "")

        xlsx.save(data)

        return data


class DOCXExtractor(BaseExtractMetaData):
    def extract(self, data) -> io.BytesIO:
        docx = Document(data)

        fields = [
            attr
            for attr in dir(docx.core_properties)
            if isinstance(getattr(docx.core_properties, attr), str)
            and not attr.startswith("_")
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
