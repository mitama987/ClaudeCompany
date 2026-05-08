from pathlib import Path
import json
import re
import shutil
import struct
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
            "docs/assets/images/plan_compare.png",
            "docs/assets/images/favicon.png",
            "docs/assets/images/developer_portrait.webp",
            "docs/assets/images/addons/addons_ai.webp",
            "docs/assets/images/addons/addons_engagement.webp",
            "docs/assets/images/addons/addons_multi.webp",
            "docs/assets/images/addons/addons_community.webp",
            "docs/assets/images/addons/addons_amazon.webp",
            "docs/assets/images/reviews/review_01.png",
            "docs/assets/images/reviews/review_02.png",
            "docs/assets/images/reviews/review_03.png",
            "docs/assets/images/reviews/review_04.png",
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
            "あなたに合う、買い切りプランを",
            "月額・サブスクは一切ありません",
            "定期投稿（基本）",
            "AI機能なし",
            "複数アカウント非対応",
            "人気No.1",
            "全基本機能 無制限",
            "永続ライセンス",
            "¥2,980の基本版でできること",
            "必要な機能だけ、あとから足せる",
            "ランダム投稿+AI+スプシ取込",
            "自動いいね+フォロー+リプライ",
            "プロキシ+一括登録+共通設定",
            "Keepa連携+在庫監視+自動投稿",
            "3プランを、横で並べて",
            "累計100名以上が選んだ、本物の自動化",
            "含まれるもの",
            "まずは基本版で十分",
            "開発者について",
            "大企業品質を、個人にも。",
            "早稲田大学院",
            "上場企業でAI推進",
            "マイナビ社",
            "XToolsシリーズ",
            "3年の歳月",
            "目安100アカウント",
            "10アカウント程度",
            "投稿時刻をずらす",
            "Macでも使えますか？",
            "必要なPCスペックは？",
            "プロキシには別途費用がかかりますか？",
            "アドオンは後から追加できますか？",
            "Windows 10",
            "月額500〜800円",
            "お問い合わせフォーム",
            "無料版",
            "¥2,980",
            "¥19,800",
            "launch-grip",
            "faq-emphasis",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, html)

        removed_phrases = [
            "信頼材料。",
            "アドオンで広がる",
            "選ばれる理由",
        ]
        for phrase in removed_phrases:
            self.assertNotIn(phrase, html)

        old_site_phrases = [
            "Claude Terminal Shortcuts",
            "Windows Terminal",
            "dangerously-skip-permissions",
        ]
        for phrase in old_site_phrases:
            self.assertNotIn(phrase, html)

        self.assertRegex(html, r"<main\b")
        self.assertRegex(html, r"aria-label=\"[^\"]+\"")
        self.assertIn('rel="icon"', html)
        self.assertIn('"@type": "Product"', html)

    def test_visible_footer_and_addon_duplicate_titles_are_removed(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        visible_text = self.visible_text(html)

        for title in [
            "AI生成パック",
            "エンゲージメントパック",
            "マルチアカウントパック",
            "コミュニティパック",
            "Amazon在庫復活パック",
        ]:
            self.assertNotIn(f"<h3>{title}</h3>", html)

        self.assertNotIn('class="version-history"', html)
        self.assertNotIn('class="site-footer"', html)
        self.assertNotIn("GitHub Pagesで公開できる静的LPです。", visible_text)
        self.assertNotIn("Version History", visible_text)
        self.assertNotIn("ver2.3", visible_text)

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

        self.assertLess(len(visible_text), 9000)
        self.assertIn('src="assets/images/feature_map.png"', html)
        self.assertIn('src="assets/images/random_flow.png"', html)
        self.assertIn('src="assets/images/proxy_protection.png"', html)
        self.assertIn('src="assets/images/community_branch.png"', html)
        self.assertIn('src="assets/images/auto_dm_flow.png"', html)
        self.assertIn('src="assets/images/amazon_flow.png"', html)
        self.assertNotIn('src="assets/images/plan_compare.png"', html)
        self.assertIn('src="assets/images/developer_portrait.webp"', html)
        self.assertIn('src="assets/images/addons/addons_ai.webp"', html)
        self.assertIn('src="assets/images/reviews/review_01.png"', html)
        self.assertNotIn("assets.st-note.com", html)
        self.assertNotIn("C:\\Users\\mitam\\Desktop\\work\\90_other\\ClaudeCompany", html)

    def test_reference_sections_are_added_without_long_page_bloat(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

        expected_order = [
            "必要な機能だけ、短く見る。",
            "あなたに合う、買い切りプランを",
            "¥2,980の基本版でできること",
            "必要な機能だけ、あとから足せる",
            "3プランを、横で並べて",
            "お客様の声",
            "開発者について",
            "よくある質問。",
        ]
        positions = [html.index(text) for text in expected_order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('class="compare-visual', html)
        self.assertIn('class="compare-table', html)
        self.assertIn('class="addon-grid"', html)
        self.assertIn('class="basic-panel', html)
        self.assertIn('class="addon-detail"', html)
        self.assertIn('class="review-grid"', html)
        self.assertIn('class="developer-panel', html)
        self.assertNotIn('class="basic-panel__aside"', html)
        self.assertNotIn('class="addon-item__action"', html)

    def test_reference_sections_have_richer_visual_structure(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        css = (ROOT / "docs/styles.css").read_text(encoding="utf-8")

        rich_classes = [
            "launch-grip__cta",
            "basic-panel__main",
            "addon-item__image",
            "addon-item__best",
            "addon-detail__list",
            "compare-table",
            "review-card",
            "review-card__scroll",
            "developer-copy",
            "developer-proof",
        ]
        for class_name in rich_classes:
            self.assertIn(class_name, html)

        for selector in [
            ".launch-grip",
            ".basic-panel",
            ".addon-item__image",
            ".addon-detail",
            ".compare-visual",
            ".compare-table",
            ".review-grid",
            ".review-card__scroll",
            ".developer-panel",
            ".developer-timeline",
            ".faq-emphasis",
        ]:
            self.assertIn(selector, css)

        self.assertRegex(css, r"\.addon-grid\s*\{[\s\S]*grid-template-columns:\s*repeat\(3,")
        self.assertRegex(css, r"\.review-grid\s*\{[\s\S]*grid-template-columns:\s*1fr;")

    def test_developer_profile_uses_portrait_and_mobile_timeline(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        css = (ROOT / "docs/styles.css").read_text(encoding="utf-8")

        self.assertIn('src="assets/images/developer_portrait.webp"', html)
        self.assertIn('class="developer-timeline"', html)
        self.assertIn('aria-label="スマホ向け開発者プロフィール"', html)
        for phrase in [
            "早稲田大学大学院 修了",
            "上場企業でAI推進担当",
            "プログラミング独学",
            "XToolsPro3開発",
            "X自動化",
            "Instagram自動化",
            "AI推進",
            "スクレイピング",
            "Bot開発",
        ]:
            self.assertIn(phrase, html)

        self.assertRegex(css, r"\.developer-timeline\s*\{[\s\S]*display:\s*none;")
        self.assertRegex(
            css,
            r"@media\s*\(max-width:\s*640px\)\s*\{[\s\S]*\.developer-timeline\s*\{[\s\S]*display:\s*block;",
        )
        self.assertNotRegex(css, r"\.developer-visual\s*\{[^}]*display:\s*none;")

    def test_addons_use_toggles_and_compare_is_a_html_table(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

        self.assertEqual(html.count('<details class="addon-detail">'), 5)
        self.assertEqual(html.count("含まれるものを見る"), 5)
        self.assertEqual(html.count('data-price-free="true"'), 5)
        self.assertIn("投稿案生成・文章の言い換え", html)
        self.assertIn("自動いいね・自動フォロー・自動リプライ", html)
        self.assertIn("アカウント別プロキシ", html)
        self.assertIn("指定コミュニティへの自動投稿", html)
        self.assertIn("Keepa連携による在庫監視", html)
        self.assertIn('<table class="compare-table"', html)
        self.assertIn("比較項目", html)
        self.assertIn("予約投稿", html)
        self.assertIn("新機能の即時利用", html)
        self.assertIn("全5種同梱", html)
        self.assertIn('scope="col"', html)
        self.assertEqual(html.count('class="compare-table__mark"'), 10)
        self.assertNotIn('class="compare-image"', html)
        self.assertNotIn("比較表を画像化しています", html)

        for image_name in [
            "addons_ai.webp",
            "addons_engagement.webp",
            "addons_multi.webp",
            "addons_community.webp",
            "addons_amazon.webp",
        ]:
            with self.subTest(image_name=image_name):
                self.assertIn(f'{image_name}" alt=', html)
                self.assertIn('width="1024" height="610"', html)

    def test_reviews_are_large_and_scrollable_for_readability(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        css = (ROOT / "docs/styles.css").read_text(encoding="utf-8")

        self.assertEqual(html.count('class="review-card__scroll"'), 4)
        self.assertIn('aria-label="お客様の声 1を拡大表示"', html)
        self.assertRegex(css, r"\.review-grid\s*\{[\s\S]*max-width:\s*980px;")
        self.assertRegex(css, r"\.review-card img\s*\{[\s\S]*width:\s*100%;")
        self.assertRegex(css, r"@media\s*\(max-width:\s*640px\)\s*\{[\s\S]*\.review-card img\s*\{[\s\S]*width:\s*760px;")

    def test_reference_faq_is_added_without_touching_minimal_variant(self):
        html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        minimal = (ROOT / "docs/index-minimal.html").read_text(encoding="utf-8")

        faq_order = [
            "APIキーは必要ですか？",
            "Macでも使えますか？",
            "何アカウントまで使えますか？",
            "必要なPCスペックは？",
            "プロキシには別途費用がかかりますか？",
            "無料版から有料版へ移行できますか？",
            "アドオンは後から追加できますか？",
        ]
        positions = [html.index(text) for text in faq_order]
        self.assertEqual(positions, sorted(positions))
        self.assertGreaterEqual(html.count('<details class="faq-item">'), 7)
        self.assertIn('class="faq-more"', html)
        self.assertIn("Mac / Linuxには対応していません", html)
        self.assertIn("メモリ4GB", html)
        self.assertIn("目安100アカウント", html)
        self.assertIn("¥3,200お得", html)
        self.assertIn("<strong>Windows専用</strong>", html)
        self.assertIn('<span class="faq-emphasis">Mac / Linuxには対応していません。</span>', html)

        self.assertNotIn("プロキシには別途費用がかかりますか？", minimal)
        self.assertNotIn("アドオンは後から追加できますか？", minimal)

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
    def png_dimensions(path):
        with path.open("rb") as image_file:
            header = image_file.read(24)
        if not header.startswith(b"\x89PNG\r\n\x1a\n"):
            raise AssertionError(f"{path} is not a PNG file")
        return struct.unpack(">II", header[16:24])

    @staticmethod
    def visible_text(html):
        visible = re.sub(r"<!--[\s\S]*?-->", "", html)
        visible = re.sub(r"<script[\s\S]*?</script>", "", visible)
        visible = re.sub(r"<style[\s\S]*?</style>", "", visible)
        visible = re.sub(r"<[^>]+>", "", visible)
        return re.sub(r"\s+", "", visible)

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
# ver0.12 - 2026-05-06 - Added checks for richer visual structure in reference-inspired sections.
# ver0.13 - 2026-05-06 - Added checks for expanded reference FAQ and preserved minimal variant.
# ver0.14 - 2026-05-06 - Added checks for toggle add-ons, image-based comparison, and developer introduction section.
# ver0.15 - 2026-05-06 - Required the comparison image to be a table-style PNG instead of plan cards.
# ver0.16 - 2026-05-06 - Added checks for mobile developer profile timeline fallback.
# ver0.17 - 2026-05-08 - Added checks for reference pricing/add-ons/reviews, portrait developer image, emphasized FAQ, and floating launch grip.
# ver0.18 - 2026-05-08 - Required a local favicon so the published page avoids browser favicon 404s.
# ver0.19 - 2026-05-08 - Required 3-column add-ons, price-free regenerated add-on images, HTML comparison table, and larger readable reviews.
# ver0.20 - 2026-05-08 - Required cropped previous-style add-on images and larger comparison marks.
# ver0.21 - 2026-05-09 - Required duplicate add-on titles and visible footer/version history to be removed.
