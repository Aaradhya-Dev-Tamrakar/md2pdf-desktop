"""Semantic PDF validation regression tests."""
from io import BytesIO
import os
import tempfile
import unittest

from pypdf import PdfWriter

from md2pdf import inspect_pdf_output


def valid_pdf_bytes():
    stream = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(stream)
    return stream.getvalue()


class SemanticPdfValidationTests(unittest.TestCase):
    def test_valid_pdf_is_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "valid.pdf")
            with open(path, "wb") as stream:
                stream.write(valid_pdf_bytes())
            info = inspect_pdf_output(path, extract_text=True)
            self.assertEqual(info["pages"], 1)
            self.assertIsInstance(info["text_chars"], int)

    def test_invalid_pdf_with_signature_and_eof_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "broken.pdf")
            with open(path, "wb") as stream:
                stream.write(b"%PDF-1.7\n1 0 obj << /Type /Page >> endobj\n%%EOF\n")
            with self.assertRaisesRegex(RuntimeError, "could not be parsed"):
                inspect_pdf_output(path)
