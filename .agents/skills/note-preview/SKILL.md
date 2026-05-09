# note.com 記事プレビュースキル

ローカルの Markdown 記事ファイルを note.com 風の HTML に変換し、ブラウザでプレビュー表示するスキル。note-edit スキルと同じ変換処理（挨拶文挿入、テーブル→リスト変換、悩みパターン→引用化、CTAリンク置換等）を適用した状態で確認できる。

## 使用方法

```
/note-preview <記事MDファイルパス>
```

- **引数**: プレビューする記事の MD ファイルパス（`_generated.md` 等）
- スキルはファイルを読み込み、note.com 風の HTML を生成してブラウザで表示する

例: `/note-preview 02_note/00_XToolsPro4/X APIまとめ_generated.md`

## 処理フロー

### Step 1: ファイルパスの確認
1. 引数で指定された MD ファイルが存在するか確認
2. ファイルが見つからない場合、`50_ブログ/02_note/` 配下を検索して候補を提示

### Step 2: プレビュー実行
プロジェクトディレクトリで以下を実行:

```bash
cd C:/Users/mitam/Desktop/work/90_other/ClaudeCompany
uv run note-preview "<MDファイルの絶対パス>"
```

ブラウザが自動で開き、note.com 風のプレビューが表示される。

### Step 3: オプション付き実行（必要に応じて）

#### 変換なしプレビュー
note.com 変換処理を適用せず、素の Markdown をそのまま HTML 化して表示:
```bash
uv run note-preview "<MDファイルパス>" --no-transform
```

#### HTML ファイル保存
ブラウザで開かずに HTML ファイルとして保存:
```bash
uv run note-preview "<MDファイルパス>" --output "<出力先パス>.html"
```

## 適用される変換処理

note-edit スキルと同じ以下の変換が自動適用される:

1. **挨拶文挿入**: 先頭に「こんにちは！SNS自動化ツール開発歴7年のYouパパです。」
2. **悩みパターン→引用化**: H2 前の疑問文連続を引用ブロック + 中黒箇条書きに変換
3. **テーブル→リスト変換**: note.com 非対応のテーブルを箇条書きに変換
4. **CTA リンク置換**: `[リンク]` を XToolsPro3 の note 版 LP URL に置換
5. **番号付きリスト変換**: `1. テキスト` を通常段落に変換
6. **空行正規化**: H2/H3 直前のみ空行を挿入

## バージョン履歴

- ver 1.0 - 2026/04/12 - 初版作成。note.com 風 HTML プレビュー、全変換処理対応
