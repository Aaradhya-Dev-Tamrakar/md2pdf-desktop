"""Regression tests for the shared conversion core (stdlib unittest only)."""
import os
import tempfile
import unittest
from unittest import mock

from md2pdf import core

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj << /Type /Page >> endobj\n%%EOF\n"


class PdfValidationTests(unittest.TestCase):
    def test_accepts_pdf_with_signature_page_and_eof(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "valid.pdf")
            with open(path, "wb") as stream:
                stream.write(MINIMAL_PDF)
            core.validate_pdf_output(path)

    def test_rejects_non_pdf_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "not.pdf")
            with open(path, "wb") as stream:
                stream.write(b"not a PDF at all")
            with self.assertRaisesRegex(RuntimeError, "signature"):
                core.validate_pdf_output(path)

    def test_rejects_truncated_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "truncated.pdf")
            with open(path, "wb") as stream:
                stream.write(b"%PDF-1.4\n1 0 obj << /Type /Page >> endobj\n")
            with self.assertRaisesRegex(RuntimeError, "truncated"):
                core.validate_pdf_output(path)

    def test_rejects_missing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "did not create"):
                core.validate_pdf_output(os.path.join(tmp, "missing.pdf"))


class AutoOrchestrationTests(unittest.TestCase):
    def test_falls_back_and_returns_actual_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = os.path.join(tmp, "result.pdf")

            def write_pdf(_markdown, path, **_kwargs):
                with open(path, "wb") as stream:
                    stream.write(MINIMAL_PDF)

            with (
                mock.patch.object(core, "check_tools", return_value={
                    "pandoc": True, "chromium": True,
                    "pdflatex": True, "wkhtmltopdf": True,
                }),
                mock.patch.object(core, "detect_sidebar_needed", return_value=(True, "Mermaid")),
                mock.patch.object(core, "detect_latex_needed", return_value=(False, None)),
                mock.patch.object(core, "convert_sidebar", side_effect=RuntimeError("renderer failed")),
                mock.patch.object(core, "convert_simple", side_effect=write_pdf),
            ):
                backend = core.convert_auto("mermaid diagram", output)

            self.assertEqual(backend, "simple")
            core.validate_pdf_output(output)

    def test_reports_when_no_backend_is_available(self):
        with (
            mock.patch.object(core, "check_tools", return_value={
                "pandoc": False, "chromium": False,
                "pdflatex": False, "wkhtmltopdf": False,
            }),
            mock.patch.object(core, "detect_sidebar_needed", return_value=(False, None)),
            mock.patch.object(core, "detect_latex_needed", return_value=(False, None)),
        ):
            with self.assertRaisesRegex(RuntimeError, "No renderer produced a valid PDF"):
                core.convert_auto("plain text", "unused.pdf")



class MarkdownNormalizationTests(unittest.TestCase):
    def test_preserves_fenced_code_during_global_replacements(self):
        source = (
            "A prose dash — and logic ∧ symbol.\n\n"
            "```python\n"
            "message = '— ∧ θ 📂'\n"
            "print(message)\n"
            "```\n"
        )
        cleaned = core.clean_markdown_for_pdf(source)
        self.assertIn("A prose dash -- and logic", cleaned)
        self.assertIn("message = '— ∧ θ 📂'", cleaned)

    def test_preserves_unclosed_fence_to_end_of_file(self):
        source = "Text —\\n~~~python\\nvalue = '— ∧'\\n"
        cleaned = core.clean_markdown_for_pdf(source)
        self.assertIn("value = '— ∧'", cleaned)

    def test_converts_mermaid_but_preserves_other_fences(self):
        source = (
            "```mermaid\nflowchart TD\nA --> B\n```\n\n"
            "```python\nprint('∨ θ')\n```"
        )
        cleaned = core.clean_markdown_for_pdf(source)
        self.assertIn("Diagram (Flowchart)", cleaned)
        self.assertIn("print('∨ θ')", cleaned)

if __name__ == "__main__":
    unittest.main()
