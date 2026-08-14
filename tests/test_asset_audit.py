import tempfile
import unittest
from pathlib import Path

from scripts.audit_assets import analyse_asset
from scripts.fetch_logos import Candidate, allowed_for_primary


class AssetAuditTests(unittest.TestCase):
    def test_clean_svg_passes_without_embedded_content(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "logo.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0h10v10H0z"/></svg>')
            result = analyse_asset(path)
            self.assertEqual(result["asset_type"], "vector")
            self.assertEqual(result["issues"], [])

    def test_primary_svg_rejects_embedded_text_but_fallback_allows_it(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "fallback.svg"
            path.write_text('<svg viewBox="0 0 10 10"><text x="0" y="5">ABC</text></svg>')
            self.assertIn("svg-embedded-text", analyse_asset(path)["issues"])
            self.assertNotIn("svg-embedded-text", analyse_asset(path, "fallback")["issues"])

    def test_transparent_canvas_rect_is_not_a_background(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "logo.svg"
            path.write_text(
                '<svg viewBox="0 0 240 75"><rect class="f" width="240" height="75"/>'
                '<path d="M0 0h10v10H0z"/></svg>'
            )
            self.assertNotIn("possible-svg-background-rectangle", analyse_asset(path)["warnings"])

    def test_bank_primary_policy_rejects_app_icons_and_page_images(self):
        row = [""] * 14
        row[2] = "bank"
        app = Candidate("https://example.test/app.png", "app-store", "app-icon")
        page = Candidate("https://example.test/banner.png", "brand-site-img", "wordmark")
        official = Candidate("https://example.test/logo.svg", "brand-site", "wordmark")
        self.assertFalse(allowed_for_primary(row, app))
        self.assertFalse(allowed_for_primary(row, page))
        self.assertTrue(allowed_for_primary(row, official))
        self.assertTrue(allowed_for_primary(row, app, is_override=True))

    def test_payment_primary_policy_rejects_app_icons_and_page_images(self):
        row = [""] * 14
        row[2] = "payment"
        app = Candidate("https://example.test/app.png", "app-store", "app-icon")
        page = Candidate("https://example.test/banner.png", "brand-site-img", "wordmark")
        official = Candidate("https://example.test/logo.svg", "brand-site", "wordmark")
        self.assertFalse(allowed_for_primary(row, app))
        self.assertFalse(allowed_for_primary(row, page))
        self.assertTrue(allowed_for_primary(row, official))

    def test_svg_rejects_html_and_embedded_raster_payloads(self):
        with tempfile.TemporaryDirectory() as temp:
            html_path = Path(temp) / "error.svg"
            html_path.write_text("<!doctype html><html><body>not an svg</body></html>")
            image_path = Path(temp) / "embedded.svg"
            image_path.write_text('<svg viewBox="0 0 10 10"><image href="data:image/png;base64,AAAA"/></svg>')
            self.assertIn("invalid-svg", analyse_asset(html_path)["issues"])
            self.assertIn("svg-embedded-raster", analyse_asset(image_path)["issues"])


if __name__ == "__main__":
    unittest.main()
