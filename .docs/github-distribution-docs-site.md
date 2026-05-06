# GitHub Distribution Documentation Site

## Purpose

Claude Code を Windows Terminal から指定プロジェクトで起動するショートカット配布キットのドキュメントサイトを作成する。
GitHub Pages の `/docs` 公開に対応し、利用者が安全に `install.ps1` を確認して実行できる構成にする。

## Scope

- `docs/index.html`: 公開ドキュメント本体。
- `docs/styles.css`: レスポンシブ対応とアクセシビリティ状態。
- `docs/script.js`: コマンドコピー用の軽量 JavaScript。
- `install.ps1`: Windows Terminal 設定にショートカットを追加する配布スクリプト。
- `tests/test_docs_site.py`: TDD 用の静的検証。

## Design Notes

- 最初の画面に導入対象とコマンド導線を表示する。
- `settings.json` 全体や `~/.claude.json` の配布は明示的に避ける。
- `--dangerously-skip-permissions` は標準手順に含めず、利用者が初回に trust ダイアログを承認する設計にする。
- Windows Terminal の既存設定は変更前に `.bak-日時` でバックアップする。
- `-LaunchCommand ccnest` では Windows Terminal 側に `Ctrl+T` を登録せず、ccnest 内部のタブ作成にキー入力を渡す。
- 配色は白、ティール、ブルー、アンバー、ローズを分散して使い、単一色に寄せない。
- タッチターゲットは 44px 以上、フォーカスリングを明示する。

## Test Strategy

`python -m unittest tests.test_docs_site` で以下を確認する。

- 公開サイト、CSS、JS、インストーラー、設計ドキュメントが存在する。
- GitHub 配布、ProjectPath、trust 承認、安全注意がサイトに記載されている。
- 個人の固定パスをサイトに埋め込まない。
- インストーラーがバックアップ、JSON 読み書き、UTF-8 出力を使う。
- `ccnest` 起動時は `Ctrl+T` の Terminal keybinding と NewTab action を追加せず、`claude` / `cc` 起動時は従来どおり追加する。
- CSS/JS にアクセシビリティ対応と Version History がある。

## Version History

ver0.1 - 2026-04-25 - GitHub 配布ドキュメントサイトの設計メモを追加。
ver0.2 - 2026-04-25 - ccnest の Ctrl+T を内部タブに渡す設計メモとテスト方針を追加。
