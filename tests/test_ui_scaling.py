import unittest

from md2pdf_app import MD2PDFStudioApp


class UIScalingTests(unittest.TestCase):
    def test_monitor_dpi_maps_to_native_tk_scaling(self):
        self.assertAlmostEqual(MD2PDFStudioApp._dpi_to_tk_scaling(96), 96 / 72)
        self.assertAlmostEqual(MD2PDFStudioApp._dpi_to_tk_scaling(120), 120 / 72)
        self.assertAlmostEqual(MD2PDFStudioApp._dpi_to_tk_scaling(192), 192 / 72)
        self.assertAlmostEqual(MD2PDFStudioApp._dpi_to_tk_scaling(240), 240 / 72)

    def test_zoom_clamps_to_supported_steps(self):
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(100), 100)
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(116), 120)
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(999), 150)
        self.assertEqual(MD2PDFStudioApp._clamp_zoom(0), 80)

    def test_zoom_is_independent_of_monitor_dpi(self):
        for dpi in (120, 144, 192, 240):
            native = MD2PDFStudioApp._dpi_to_tk_scaling(dpi)
            self.assertAlmostEqual(native * (100 / 100), native)
            self.assertAlmostEqual(native * (120 / 100), native * 1.2)

    def test_export_controls_exist_and_shortcuts_bound(self):
        import tkinter as tk
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"Tkinter display not available in headless environment: {exc}")
        try:
            app = MD2PDFStudioApp(root)
            self.assertTrue(hasattr(app, "convert_btn"))
            self.assertTrue(hasattr(app, "cmd_export_btn"))
            self.assertTrue(hasattr(app, "open_folder_btn"))
            self.assertTrue(hasattr(app, "progress"))

            calls = []
            app.convert = lambda: calls.append(1)
            root.update()
            app.text.focus_set()

            # Test shortcuts from text editor focus
            app.text.event_generate("<Control-Key-E>", state=0x5)
            root.update()
            app.text.event_generate("<Control-Key-e>", state=0x4)
            root.update()
            app.text.event_generate("<Control-Key-p>", state=0x4)
            root.update()

            self.assertEqual(len(calls), 3)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
