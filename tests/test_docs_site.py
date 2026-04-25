from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DocumentationSiteTests(unittest.TestCase):
    def test_public_site_files_exist(self):
        for relative_path in [
            "docs/index.html",
            "docs/styles.css",
            "docs/script.js",
            "install.ps1",
            ".docs/github-distribution-docs-site.md",
        ]:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_index_documents_github_distribution_flow(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

        required_phrases = [
            "GitHub Pages",
            "install.ps1",
            "ProjectPath",
            "Yes, I trust this folder",
            "dangerously-skip-permissions",
            "Windows Terminal",
            "Version History",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, html)

        self.assertRegex(html, r"<main\b")
        self.assertRegex(html, r"<footer\b")
        self.assertRegex(html, r"aria-label=\"[^\"]+\"")

    def test_index_has_copyable_commands_without_hardcoded_personal_path(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

        self.assertIn('data-copy-target=', html)
        self.assertIn("C:\\path\\to\\project", html)
        self.assertNotIn("C:\\Users\\mitam\\Desktop\\work\\90_other\\ClaudeCompany", html)

    def test_installer_has_non_destructive_safety_measures(self):
        script = (ROOT / "install.ps1").read_text(encoding="utf-8")

        required_patterns = [
            r"param\s*\(",
            r"\$ProjectPath",
            r"Copy-Item",
            r"ConvertFrom-Json",
            r"ConvertTo-Json",
            r"UTF8Encoding",
            r"Version History",
        ]
        for pattern in required_patterns:
            self.assertRegex(script, pattern)

        self.assertNotIn("--dangerously-skip-permissions", script)
        self.assertNotRegex(script, r"Remove-Item\s+-Recurse")

    def test_style_and_script_include_accessibility_and_version_history(self):
        css = (ROOT / "docs/styles.css").read_text(encoding="utf-8")
        js = (ROOT / "docs/script.js").read_text(encoding="utf-8")

        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("Version History", css)
        self.assertIn("aria-live", js)
        self.assertIn("Version History", js)


if __name__ == "__main__":
    unittest.main()


# Version History
# ver0.1 - 2026-04-25 - Added TDD checks for the GitHub distribution documentation site.
