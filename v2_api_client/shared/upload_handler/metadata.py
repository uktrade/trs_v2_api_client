import io
import mimetypes
import os
import tempfile
import zipfile
import shutil
import glob
from abc import ABC, abstractmethod
from pathlib import Path
import pikepdf
from lxml import etree


class Extractor:
    def __call__(self, raw_data, content_type):
        data = io.BytesIO(raw_data)
        file_format = content_type
        was_stripped = True

        print(file_format)

        if file_format == "application/pdf":
            data = PDFExtractor().extract(data)
        elif file_format in (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/msword",
            "application/vnd.ms-excel",
            "application/vnd.ms-excel.sheet.macroenabled.12",
            "application/vnd.ms-excel.sheet.binary.macroenabled.12",
            "application/vnd.ms-word.document.macroenabled.12",
        ):
            data = MicrosoftDocExtractor().extract(data)
        elif file_format in (
            "application/vnd.oasis.opendocument.text",
            "application/vnd.oasis.opendocument.spreadsheet",
        ):
            data = OpenDocumentExtractor().extract(data)
        elif file_format == "application/zip":
            data = ZIPExtractor().extract(data)
        else:
            # mimetype is not supported
            was_stripped = False

        return was_stripped, data


extractor = Extractor()


class BaseExtractMetaData(ABC):
    @abstractmethod
    def extract(self, data) -> io.BytesIO:
        raise NotImplementedError()


class ZIPExtractor(BaseExtractMetaData):
    def extract(self, data):
        with zipfile.ZipFile(data, "r") as input_zip:
            with tempfile.TemporaryDirectory() as tmpdirname:
                with tempfile.TemporaryDirectory() as output_tmpdirname:
                    input_zip.extractall(tmpdirname)
                    tmpdirname += "/**"
                    file_length_counter = 0
                    for input_file_path in glob.glob(tmpdirname, recursive=True):
                        if not os.path.isfile(input_file_path):
                            continue
                        file_length_counter += 1
                        file_name = Path(input_file_path).name
                        output_file_path = os.path.join(output_tmpdirname, file_name)
                        if mimetype := mimetypes.guess_type(file_name)[0]:
                            with open(input_file_path, "rb") as file_bytes:
                                _, stripped_bytes = extractor(
                                    file_bytes.read(), mimetype
                                )
                                with open(output_file_path, "wb") as f:
                                    f.write(stripped_bytes.read())
                        else:
                            # the mimetype cannot be determined, so we just copy the file
                            shutil.copyfile(input_file_path, output_file_path)

                    # checking that the new zip file contains the same number of files as the
                    # original zip file
                    assert file_length_counter == len(os.listdir(output_tmpdirname))
                    stripped_zip_path = shutil.make_archive(
                        os.path.join(tmpdirname, "stripped"), "zip", output_tmpdirname
                    )
                    stripped_zip_file = open(stripped_zip_path, "rb")
                    stripped_zip_bytes = stripped_zip_file.read()
                    stripped_zip_file.close()

        return stripped_zip_bytes


class OpenDocumentExtractor(BaseExtractMetaData):
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

        sanitised_data.seek(0)
        return sanitised_data


class MicrosoftDocExtractor(BaseExtractMetaData):
    def extract(self, data) -> io.BytesIO:
        sanitised_data = io.BytesIO()
        with zipfile.ZipFile(data, "r") as input_file:
            with zipfile.ZipFile(sanitised_data, "w") as output_file:
                for sub_file in input_file.infolist():
                    if sub_file.filename != "docProps/core.xml":
                        output_file.writestr(
                            sub_file, input_file.read(sub_file.filename)
                        )
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

        sanitised_data.seek(0)
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
