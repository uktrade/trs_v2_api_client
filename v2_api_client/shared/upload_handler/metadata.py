import io
import zipfile
from abc import abstractmethod, ABC

import pikepdf
from docx import Document
from lxml import etree
from openpyxl import load_workbook


class Extractor:
    def __call__(self, raw_data, content_type):
        data = io.BytesIO(raw_data)
        file_format = content_type

        if file_format == "application/pdf":
            return PDFExtractor().extract(data)
        if (
            file_format
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            return DOCXExtractor().extract(data)
        if (
            file_format
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            return XLSXExtractor().extract(data)
        if (
            file_format == "application/vnd.oasis.opendocument.text"
            or file_format == "application/vnd.oasis.opendocument.spreadsheet"
        ):
            return ODFExtractor().extract(data)

        return data


class BaseExtractMetaData(ABC):
    @abstractmethod
    def extract(self, data) -> io.BytesIO:
        raise NotImplementedError()


class ODFExtractor(BaseExtractMetaData):
    def extract(self, data):
        sanitised_data = io.BytesIO()
        tags = ["creator", "title", "description", "subject"]

        with zipfile.ZipFile(data, "r") as input_odf:
            with zipfile.ZipFile(sanitised_data, "w") as output_odf:
                output_odf.comment = input_odf.comment  # preserve the comment
                for file in input_odf.infolist():
                    if file.filename != "meta.xml":
                        output_odf.writestr(file, input_odf.read(file.filename))
                    else:
                        root = etree.parse(input_odf.open("meta.xml")).getroot()

                        for fields in root[0]:
                            if any([field in fields.tag for field in tags]):
                                fields.text = ""

                        metadata = etree.tostring(root)

        with zipfile.ZipFile(sanitised_data, "a", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("meta.xml", metadata)

        return sanitised_data


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
        sanitised_data = io.BytesIO()
        with zipfile.ZipFile(data, "r") as input_doc:
            with zipfile.ZipFile(sanitised_data, "w") as output_doc:
                for sub_file in input_doc.infolist():
                    if sub_file.filename != "docProps/core.xml":
                        output_doc.writestr(sub_file, input_doc.read(sub_file.filename))
                    else:
                        core_properties = etree.fromstring(
                            input_doc.read(sub_file.filename)
                        )
                        potentially_sensitive_fields = [
                            child
                            for child in core_properties.getchildren()
                            if any(
                                [
                                    field in child.tag
                                    for field in [
                                        "creator",
                                        "comments",
                                        "lastModifiedBy",
                                        "manager",
                                        "identifier",
                                    ]
                                ]
                            )
                        ]
                        for field in potentially_sensitive_fields:
                            field.text = ""
                        sanitised_core_properties = etree.tostring(core_properties)
                        output_doc.writestr(
                            sub_file.filename, sanitised_core_properties
                        )
        return sanitised_data


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
