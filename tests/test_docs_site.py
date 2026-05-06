from pathlib import Path
import json
import re
import subprocess
import tempfile
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
            "ccnest",
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

    def test_installer_leaves_ctrl_t_for_ccnest_internal_tabs(self):
        settings = self.run_installer_with_launch_command("ccnest")

        shortcut_ids = {
            action["id"]
            for action in settings["actions"]
            if action["id"].startswith("ClaudeTerminalShortcuts.")
        }
        shortcut_keys = [
            key.lower()
            for binding in settings["keybindings"]
            for key in self.as_list(binding.get("keys"))
        ]

        self.assertIn("ClaudeTerminalShortcuts.SplitRight", shortcut_ids)
        self.assertIn("ClaudeTerminalShortcuts.SplitDown", shortcut_ids)
        self.assertNotIn("ClaudeTerminalShortcuts.NewTab", shortcut_ids)
        self.assertNotIn("ctrl+t", shortcut_keys)

    def test_installer_keeps_ctrl_t_terminal_tab_for_standard_launchers(self):
        for launch_command in ["claude", "cc"]:
            with self.subTest(launch_command=launch_command):
                settings = self.run_installer_with_launch_command(launch_command)
                keybindings = {
                    binding["id"]: [key.lower() for key in self.as_list(binding.get("keys"))]
                    for binding in settings["keybindings"]
                }

                self.assertEqual(
                    keybindings["ClaudeTerminalShortcuts.NewTab"],
                    ["ctrl+t"],
                )

    def test_style_and_script_include_accessibility_and_version_history(self):
        css = (ROOT / "docs/styles.css").read_text(encoding="utf-8")
        js = (ROOT / "docs/script.js").read_text(encoding="utf-8")

        self.assertIn(":focus-visible", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("Version History", css)
        self.assertIn("aria-live", js)
        self.assertIn("Version History", js)

    @staticmethod
    def as_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def run_installer_with_launch_command(self, launch_command):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_path = temp_path / "project"
            project_path.mkdir()
            settings_path = temp_path / "settings.json"
            settings_path.write_text(
                json.dumps(
                    {
                        "actions": [
                            {
                                "id": "Existing.NewTab",
                                "name": "Existing new tab",
                                "command": {
                                    "action": "newTab",
                                    "commandline": "cmd /k existing",
                                    "startingDirectory": str(project_path),
                                },
                            }
                        ],
                        "keybindings": [
                            {"id": "Existing.NewTab", "keys": "ctrl+t"},
                            {"id": "Existing.Other", "keys": ["ctrl+x"]},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "install.ps1"),
                    "-ProjectPath",
                    str(project_path),
                    "-LaunchCommand",
                    launch_command,
                    "-SettingsPath",
                    str(settings_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            return json.loads(settings_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()


# Version History
# ver0.1 - 2026-04-25 - Added TDD checks for the GitHub distribution documentation site.
# ver0.2 - 2026-04-25 - Added installer behavior tests for ccnest Ctrl+T routing.
