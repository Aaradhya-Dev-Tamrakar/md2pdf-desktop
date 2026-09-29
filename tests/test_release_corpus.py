"""Release corpus metadata contract tests."""
import json
from pathlib import Path
import unittest

CORPUS = Path(__file__).parent / "fixtures" / "release_corpus.json"


class ReleaseCorpusContractTests(unittest.TestCase):
    def test_corpus_schema_and_files(self):
        data = json.loads(CORPUS.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 1)
        self.assertEqual(len(data["fixtures"]), 6)
        for item in data["fixtures"]:
            self.assertIn(item["renderer"], {"simple", "sidebar"})
            self.assertGreaterEqual(item["min_pages"], 1)
            self.assertTrue(item["required_text"])
            self.assertTrue((CORPUS.parent / item["file"]).is_file())


if __name__ == "__main__":
    unittest.main()
