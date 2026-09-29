"""End-to-end Sidebar renderer smoke test using local browser assets."""

import os
import tempfile
import unittest

from md2pdf import convert_sidebar, validate_pdf_output
from md2pdf.web_assets import ensure_web_assets


@unittest.skipUnless(
    os.environ.get("MD2PDF_SIDEBAR_INTEGRATION") == "1",
    "Sidebar integration test is opt-in",
)
class SidebarRendererIntegrationTests(unittest.TestCase):
    def test_sidebar_uses_local_katex_and_mermaid_assets(self):
        markdown = """# Sidebar Integration

Inline math: $x^2 + y^2 = z^2$.

```mermaid
flowchart TD
    A[Start] --> B[Render]
    B --> C[Done]
```
"""
        asset_dir = ensure_web_assets(offline=True)
        self.assertTrue((asset_dir / "katex.min.js").is_file())
        self.assertTrue((asset_dir / "mermaid.min.js").is_file())
        with tempfile.TemporaryDirectory() as tmp:
            output = os.path.join(tmp, "sidebar.pdf")
            convert_sidebar(markdown, output, margin="10mm", theme="light")
            validate_pdf_output(output)
            self.assertGreater(os.path.getsize(output), 1024)


if __name__ == "__main__":
    unittest.main()
