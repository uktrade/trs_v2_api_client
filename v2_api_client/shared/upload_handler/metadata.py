import io
import zipfile
from abc import ABC, abstractmethod

import pikepdf
from lxml import etree


class Extractor:
    def __call__(self, raw_data, content_type):
        data = io.BytesIO(raw_data)
        file_format = content_type

        if file_format == "application/pdf":
            return PDFExtractor().extract(data)
        elif file_format in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]:
            return MicrosoftDocExtractor().extract(data)
        elif (
                file_format == "application/vnd.oasis.opendocument.text"
                or file_format == "application/vnd.oasis.opendocument.spreadsheet"
        ):
            return ODFExtractor().extract(data)
        else:
            # mimetype is not supported
            pass
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


class MicrosoftDocExtractor(BaseExtractMetaData):
    def extract(self, data) -> io.BytesIO:
        sanitised_data = io.BytesIO()
        with zipfile.ZipFile(data, "r") as input_file:
            with zipfile.ZipFile(sanitised_data, "w") as output_file:
                for sub_file in input_file.infolist():
                    if sub_file.filename != "docProps/core.xml":
                        output_file.writestr(sub_file, input_file.read(sub_file.filename))
                    else:
                        core_properties = etree.fromstring(
                            input_file.read(sub_file.filename)
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
                        output_file.writestr(
                            sub_file.filename, sanitised_core_properties
                        )
        return sanitised_data


class PDFExtractor(BaseExtractMetaData):
    def extract(self, data) -> io.BytesIO:
        pdf = pikepdf.open(data)

        try:
            del pdf.Root.Metadata
        except KeyError:
            pass
        try:
            del pdf.docinfo
        except KeyError:
            pass

        # saving the stripped PDF
        new_stripped = io.BytesIO()
        pdf.save(new_stripped)
        pdf.close()

        new_stripped.seek(0)
        return new_stripped
