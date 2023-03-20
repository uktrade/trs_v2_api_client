import os
import unittest

import pikepdf
from docx import Document
from openpyxl import Workbook, load_workbook

from v2_api_client.shared.upload_handler.metadata import Extractor


class DocumentMetadataTest(unittest.TestCase):
    AUTHOR = "TRA"
    TITLE = "Extract Document Metadata"

    def setUp(self) -> None:
        self.create_pdf_document()
        self.create_docx_document()
        self.create_xlsx_document()

    def tearDown(self) -> None:
        os.remove(self.pdf_file)
        os.remove(self.docx_file)
        os.remove(self.xlsx_file)

    def test_instantiate_document_metadata(self):
        self.assertIsInstance(self.pdf_document, Extractor)

    def test_extract_pdf_metadata(self):
        self.assertEqual(["TRA"], self.pdf.open_metadata()["dc:creator"])
        self.assertEqual("Extract Document Metadata", self.pdf.open_metadata()["dc:title"])

        with open(self.pdf_file, "rb") as file:
            raw_data = file.read()
            content_type = "application/pdf"

            sanitised_data = self.pdf_document(raw_data, content_type)
            metadata = str(pikepdf.open(sanitised_data).open_metadata())

            self.assertNotIn("TRA", metadata)
            self.assertNotIn("Extract Document Metadata", metadata)

    def test_extract_docx_metadata(self):
        self.assertEqual("TRA", self.docx.core_properties.author)
        self.assertEqual("Extract Document Metadata", self.docx.core_properties.title)

        with open(self.docx_file, "rb") as file:
            raw_data = file.read()
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            sanitised_data = self.docx_document(raw_data, content_type)
            metadata = Document(sanitised_data).core_properties

            fields = [
                attr
                for attr in dir(metadata)
                if isinstance(getattr(metadata, attr), str)
                and not attr.startswith("_")
            ]

            for field in fields:
                self.assertNotIn("TRA", getattr(metadata, field))
                self.assertNotIn("Extract Document Metadata", getattr(metadata, field))

    def test_extract_xlsx_metadata(self):
        self.assertEqual("TRA", self.xlsx.properties.creator)
        self.assertEqual("Extract Document Metadata", self.xlsx.properties.title)

        with open(self.xlsx_file, "rb") as file:
            raw_data = file.read()
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            sanitised_data = self.xlsx_document(raw_data, content_type)
            metadata = load_workbook(sanitised_data).properties

            fields = [
                attr
                for attr in dir(metadata)
                if isinstance(getattr(metadata, attr), str)
                and not attr.startswith("_")
                and not attr == "tagname"
                and not attr == "namespace"
            ]

        for field in fields:
            self.assertNotIn("TRA", getattr(metadata, field))
            self.assertNotIn("Extract Document Metadata", getattr(metadata, field))

    def create_pdf_document(self):
        self.pdf = pikepdf.new()

        with self.pdf.open_metadata() as meta:
            meta["dc:creator"] = [self.AUTHOR]
            meta["dc:title"] = self.TITLE

        self.pdf_file = os.path.join(os.path.dirname(__file__), "fixture.pdf")
        self.pdf.save(self.pdf_file)

        self.pdf_document = Extractor()

    def create_docx_document(self):
        self.docx = Document()
        self.docx_metadata = self.docx.core_properties
        self.docx_metadata.author = self.AUTHOR
        self.docx_metadata.title = self.TITLE

        self.docx_file = os.path.join(os.path.dirname(__file__), "fixture.docx")
        self.docx.save(self.docx_file)

        self.docx_document = Extractor()

    def create_xlsx_document(self):
        self.xlsx = Workbook()
        self.xlsx_metadata = self.xlsx.properties
        self.xlsx_metadata.creator = self.AUTHOR
        self.xlsx_metadata.title = self.TITLE

        self.xlsx_file = os.path.join(os.path.dirname(__file__), "fixture.xlsx")
        self.xlsx.save(self.xlsx_file)

        self.xlsx_document = Extractor()
