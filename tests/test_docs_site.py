from pathlib import Path
import json
import re
import shutil
import subprocess
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]


class DocumentationSiteTests(unittest.TestCase):
    def test_public_site_files_exist(self):
        for relative_path in [
            "docs/index.html",
            "docs/index-minimal.html",
            "docs/styles.css",
            "docs/script.js",
            "docs/assets/images/feature_map.png",
            "docs/assets/images/random_flow.png",
            "docs/assets/images/proxy_protection.png",
            "docs/assets/images/community_branch.png",
            "docs/assets/images/auto_dm_flow.png",
            "docs/assets/images/amazon_flow.png",
            "install.ps1",
            ".docs/github-distribution-docs-site.md",
            ".docs/xtp3-rich-lp.md",
        ]:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_index_documents_xtoolspro3_landing_page(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

        required_phrases = [
            "XToolsPro3",
            "API不要",
            "X自動投稿を、",
            "もっと自然に。",
            "ランダム投稿",
            "プロキシ",
            "コミュニティ投稿",
            "自動DM",
            "Amazon在庫復活",
            "選ばれる理由",
            "¥2,980の基本版でできること",
            "必要になったら足せるアドオン",
            "3プランを横で比較",
            "信頼材料",
            "AI生成パック",
            "マルチアカウントパック",
            "目安100アカウント",
            "10アカウント程度",
            "投稿時刻をずらす",
            "無料版",
            "¥2,980",
            "¥19,800",
            "GitHub Pages",
            "Version History",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, html)

        old_site_phrases = [
            "Claude Terminal Shortcuts",
            "Windows Terminal",
            "dangerously-skip-permissions",
        ]
        for phrase in old_site_phrases:
            self.assertNotIn(phrase, html)

        self.assertRegex(html, r"<main\b")
        self.assertRegex(html, r"<footer\b")
        self.assertRegex(html, r"aria-label=\"[^\"]+\"")
        self.assertIn('"@type": "Product"', html)

    def test_minimum_landing_page_variant_is_preserved(self):
        minimal = (ROOT / "docs/index-minimal.html").read_text(encoding="utf-8")

        self.assertIn("XToolsPro3", minimal)
        self.assertIn("必要な機能だけ、短く見る。", minimal)
        self.assertIn("月額なし。買い切りで始める。", minimal)
        self.assertNotIn("必要になったら足せるアドオン", minimal)
        self.assertNotIn("3プランを横で比較", minimal)

    def test_hero_headline_has_fixed_two_line_break(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        css = (ROOT / "docs/styles.css").read_text(encoding="utf-8")

        self.assertIn('<span class="headline-line">X自動投稿を、</span>', html)
        self.assertIn('<span class="headline-line">もっと自然に。</span>', html)
        self.assertRegex(css, r"\.headline-line\s*\{[\s\S]*display:\s*block;")

    def test_index_is_concise_and_uses_local_visual_assets(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        visible_text = re.sub(r"<script[\s\S]*?</script>", "", html)
        visible_text = re.sub(r"<style[\s\S]*?</style>", "", visible_text)
        visible_text = re.sub(r"<[^>]+>", "", visible_text)
        visible_text = re.sub(r"\s+", "", visible_text)

        self.assertLess(len(visible_text), 7200)
        self.assertIn('src="assets/images/feature_map.png"', html)
        self.assertIn('src="assets/images/random_flow.png"', html)
        self.assertIn('src="assets/images/proxy_protection.png"', html)
        self.assertIn('src="assets/images/community_branch.png"', html)
        self.assertIn('src="assets/images/auto_dm_flow.png"', html)
        self.assertIn('src="assets/images/amazon_flow.png"', html)
        self.assertNotIn("assets.st-note.com", html)
        self.assertNotIn("C:\\Users\\mitam\\Desktop\\work\\90_other\\ClaudeCompany", html)

    def test_reference_sections_are_added_without_long_page_bloat(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

        expected_order = [
            "選ばれる理由",
            "必要な機能だけ、短く見る。",
            "月額なし。買い切りで始める。",
            "¥2,980の基本版でできること",
            "必要になったら足せるアドオン",
            "3プランを横で比較",
            "信頼材料",
            "よくある質問。",
        ]
        positions = [html.index(text) for text in expected_order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('class="compare-table"', html)
        self.assertIn('class="addon-grid"', html)

    def test_feature_copy_appears_before_feature_images(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

        feature_names = [
            ("ランダム投稿", "random_flow.png"),
            ("プロキシ", "proxy_protection.png"),
            ("コミュニティ投稿", "community_branch.png"),
            ("自動DM", "auto_dm_flow.png"),
            ("Amazon在庫復活", "amazon_flow.png"),
        ]
        for heading, image_name in feature_names:
            with self.subTest(heading=heading):
                self.assertLess(html.index(heading), html.index(image_name))

        self.assertNotIn('class="feature-cards"', html)
        self.assertNotIn('class="feature-card', html)

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
        self.assertIn(".skip-link", css)
        self.assertIn("Version History", css)
        self.assertIn("IntersectionObserver", js)
        self.assertIn("details", js)
        self.assertIn("Version History", js)

    @staticmethod
    def as_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def run_installer_with_launch_command(self, launch_command):
        temp_path = ROOT / f"tmp-tests-{uuid.uuid4().hex}"
        temp_path.mkdir()

        try:
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
        finally:
            shutil.rmtree(temp_path, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()


# Version History
# ver0.1 - 2026-04-25 - Added TDD checks for the GitHub distribution documentation site.
# ver0.2 - 2026-04-25 - Added installer behavior tests for ccnest Ctrl+T routing.
# ver0.3 - 2026-05-06 - Reworked public site checks for the concise XToolsPro3 GitHub Pages landing page.
# ver0.4 - 2026-05-06 - Pointed installer integration tests at a writable workspace temp root.
# ver0.5 - 2026-05-06 - Avoided hidden temp directories so Windows sandboxed tests can create child folders.
# ver0.6 - 2026-05-06 - Replaced tempfile usage with explicit workspace directories to avoid restrictive ACLs.
# ver0.7 - 2026-05-06 - Added checks for rich SVG feature assets and copy-before-image feature layout.
# ver0.8 - 2026-05-06 - Updated public site checks for GPT Images 2 PNG feature assets.
# ver0.9 - 2026-05-06 - Required every feature item to use the full-width copy-first feature layout.
# ver0.10 - 2026-05-06 - Added checks for fixed two-line hero headline and clearer account limit FAQ copy.
# ver0.11 - 2026-05-06 - Added checks for concise reference-inspired sections, add-ons, and plan comparison.
