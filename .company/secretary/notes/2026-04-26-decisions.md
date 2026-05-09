# 意思決定ログ - 2026-04-26

## 決定事項

### ClaudeCompanyリポジトリのファイル整理

**背景**: ルート直下に10個以上のスクリプトファイルが散乱しており「フォルダが汚い」状態。前回（同日中）にCSV移動・生成物の `outputs/` 集約は実施済み。今回はPythonスクリプトの分類整理を実施。

**実施した整理**:

1. **scripts/blog_assets/ を新設** - note.com / Brain記事用のアセット生成スクリプトを集約
   - `gen_apps_stripe_diagrams.py`（Apps API vs Stripe記事の図解）
   - `gen_diagrams.py`（XToolsPro3記事の図解）
   - `gen_thumbnail.py`（Brain記事サムネ）
   - `gen_x_freeze_diagrams.py`（X凍結祭り記事の図解）
   - `generate_xapi_diagrams.py`（X API料金改定記事・matplotlib版）
   - `generate_xapi_diagrams_gemini.py`（X API料金改定記事・Gemini版）

2. **scripts/gmail/ を新設** - Gmail関連ユーティリティを集約
   - `decode_mail.py`
   - `download_attachment.py`

3. **不要ファイル削除**
   - `main.py`（uv init のhello worldテンプレ、未使用）

4. **コード修正**: 移動した2スクリプトの `.env` 読み込みパスを `__file__.parent / ".env"` → `__file__.resolve().parents[2] / ".env"` に変更（プロジェクトルート参照に統一）。`scripts/trello_sync.py` のREPO_ROOT方式と整合。

**結果**:
- ルート直下のPythonファイル: 10 → 0
- ルートに残る個別ファイル: `README.md`, `install.ps1`, `pyproject.toml`, `uv.lock`（プロジェクト基本ファイルのみ）

### 部署構成について

**判断**: 新規部署は作成せず、現状の secretary + marketing(X運用) を維持。

**Why**:
- 散らかっていたファイルは「コード（スクリプト）」であり、`.company/`（組織ドキュメント）ではなく `scripts/` に整理するのが適切
- ブログ・note記事関連の作業は marketing部門の対象範囲を拡張するか、必要になった時に新部署を作る方がシンプル
- 個人開発者は部署を増やしすぎると逆に管理負荷が上がる

**今後のトリガー**: note.com/Brain記事の企画・執筆タスクが2回以上発生した場合は、改めて「ブログ運用」部門の新設を提案する。

### v2 自動Companyモードの導入

**決定**: プロジェクトルートに `CLAUDE.md` を新設し、`@.company/CLAUDE.md` と `@.company/secretary/CLAUDE.md` を import する形で、毎チャット時に秘書モードが自動適用されるようにした。

**Why**:
- 毎回 `/company` を打たずに済むようにしたいというユーザー要望
- CLAUDE.md は Claude Code 起動時に自動ロードされる仕組みを利用
- フックではなくCLAUDE.md方式を選択（シンプル・他スキルとの競合リスクなし）

**v2移行の状況**:
- マイグレーションガイド (https://shin-sibainu.github.io/cc-company/guide/migration) を確認
- `.company/` には `ceo/` も `reviews/` も存在せず、構造的にすでに v2 に準拠
- `.company/CLAUDE.md` および `secretary/CLAUDE.md` の中身も最新v2テンプレートと一致（末尾改行差のみ）→ 実質リフレッシュ不要
- 結論: マイグレーション処理は発生せず、自動Company化のためのルートCLAUDE.md追加のみで完了
