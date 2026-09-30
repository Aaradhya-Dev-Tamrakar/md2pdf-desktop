import unittest

from md2pdf_app import MD2PDFStudioApp


class UIScalingTests(unittest.TestCase):
    def test_preferred_tk_scaling_tracks_display_dpi(self):
        self.assertAlmostEqual(MD2PDFStudioApp._preferred_tk_scaling(96), 4 / 3)
        self.assertAlmostEqual(MD2PDFStudioApp._preferred_tk_scaling(120), 5 / 3)
        self.assertAlmostEqual(MD2PDFStudioApp._preferred_tk_scaling(192), 8 / 3)

    def test_zoom_clamps_to_supported_steps(self):
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(100), 100)
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(116), 120)
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(999), 150)
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(0), 80)


if __name__ == "__main__":
    unittest.main()
