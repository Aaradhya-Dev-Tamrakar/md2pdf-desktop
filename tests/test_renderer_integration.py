"""End-to-end renderer smoke tests.

These tests intentionally invoke real external renderers. They are skipped
when the native toolchain is unavailable so local unit-test runs stay fast.
"""

import os
import tempfile
import unittest

from md2pdf import check_tools, convert_simple, validate_pdf_output


@unittest.skipUnless(
    check_tools().get("pandoc") and check_tools().get("wkhtmltopdf"),
    "pandoc and wkhtmltopdf are required for renderer integration tests",
)
class SimpleRendererIntegrationTests(unittest.TestCase):
    def test_simple_renderer_produces_valid_pdf(self):
        markdown = """# Integration Test

This document exercises the real Pandoc -> HTML -> wkhtmltopdf pipeline.

| Name | Value |
| --- | --- |
| status | integration |
"""
        with tempfile.TemporaryDirectory() as tmp:
            output = os.path.join(tmp, "integration.pdf")
            convert_simple(markdown, output, margin="10mm")
            validate_pdf_output(output)
            self.assertGreater(os.path.getsize(output), 1024)


if __name__ == "__main__":
    unittest.main()
