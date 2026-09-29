"""End-to-end release corpus tests for the Simple renderer."""
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

from md2pdf import convert_simple, inspect_pdf_output

CORPUS = Path(__file__).parent / "fixtures" / "release_corpus.json"
DATA = json.loads(CORPUS.read_text(encoding="utf-8"))


@unittest.skipUnless(
    __import__("shutil").which("pandoc") and __import__("shutil").which("wkhtmltopdf"),
    "pandoc and wkhtmltopdf are required for release corpus integration tests",
)
class SimpleRendererIntegrationTests(unittest.TestCase):
    def test_simple_renderer_produces_release_corpus(self):
        for item in [x for x in DATA["fixtures"] if x["renderer"] == "simple"]:
            with self.subTest(fixture=item["file"]):
                markdown = (CORPUS.parent / item["file"]).read_text(encoding="utf-8")
                with tempfile.TemporaryDirectory() as tmp:
                    output = os.path.join(tmp, "fixture.pdf")
                    convert_simple(markdown, output, margin="10mm")
                    info = inspect_pdf_output(output, extract_text=True)
                    self.assertGreaterEqual(info["pages"], item["min_pages"])
                    from pypdf import PdfReader
                    extracted = "\n".join(page.extract_text() or "" for page in PdfReader(output, strict=False).pages)
                    normalized = re.sub(r"\s+", " ", extracted).strip()
                    for marker in item["required_text"]:
                        self.assertIn(
                            re.sub(r"\s+", " ", marker).strip(),
                            normalized,
                        )


if __name__ == "__main__":
    unittest.main()
