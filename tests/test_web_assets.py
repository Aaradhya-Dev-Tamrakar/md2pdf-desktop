import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from md2pdf import core
from md2pdf.web_assets import ASSET_SPEC, _verify_integrity, ensure_web_assets


class WebAssetTests(unittest.TestCase):
    def test_sidebar_asset_head_uses_only_local_file_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "katex.min.css").write_text("/* test */", encoding="utf-8")
            (root / "katex.min.js").write_text("window.katex = {};", encoding="utf-8")
            (root / "contrib").mkdir()
            (root / "contrib" / "auto-render.min.js").write_text("window.renderMathInElement = () => {};", encoding="utf-8")
            (root / "mermaid.min.js").write_text("window.mermaid = {};", encoding="utf-8")
            with mock.patch.object(core, "ensure_web_assets", return_value=root):
                head = core.build_sidebar_asset_head()
            self.assertNotIn("cdn.jsdelivr.net", head)
            self.assertEqual(head.count("file://"), 4)

    def test_offline_mode_rejects_missing_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "not provisioned"):
                ensure_web_assets(offline=True, asset_dir=Path(tmp) / "missing")

    def test_asset_specs_are_exactly_pinned(self):
        self.assertEqual(ASSET_SPEC["katex"]["version"], "0.16.11")
        self.assertEqual(ASSET_SPEC["mermaid"]["version"], "10.9.3")
        for spec in ASSET_SPEC.values():
            algorithm, encoded = spec["integrity"].split("-", 1)
            self.assertEqual(algorithm, "sha512")
            self.assertTrue(encoded)

    def test_integrity_verifier_rejects_tampered_bytes(self):
        with self.assertRaisesRegex(RuntimeError, "integrity"):
            _verify_integrity(b"tampered", ASSET_SPEC["katex"]["integrity"])


if __name__ == "__main__":
    unittest.main()
