---
description: Trelloの月次リスト処理。「N月」「N月以降」リストを当月/翌月にリネームし、当月締切カードを「N月以降」から「N月」に移す。「Trello月次」「月次処理」「Trello月変え」と言われたら使う。
---

# Trello 月次ローテーションスキル

ボード「データに基づく原因究明」の月次処理を一発で行う。月初に1回実行する想定。

## 引数

$ARGUMENTS

省略時は今日の年月を対象月として処理する。明示する場合は `2026-05` / `2026/05` / `5`（年は今年扱い）のいずれかで指定可能。

## ボード情報

- **ボードID**: `5ffe5b3fa17b04881f2c4fbc`
- **ボード名**: データに基づく原因究明

## 対象リスト（IDは固定、名前は月毎に変わる）

| 役割 | ID | 月初の状態 → 処理後の状態 |
|------|----|----|
| 「N月」(当月) | `5ffe5b3fa17b04881f2c4fc3` | 旧月名 → 当月名（例: 4月 → 5月） |
| 「N月以降」(翌月以降) | `5ffe5b3fa17b04881f2c4fc4` | 旧「N月以降」→ 翌月名（例: 5月以降 → 6月） |

## 処理内容

1. **リネーム**
   - `LIST_CURRENT_MONTH` を「{当月}月」に
   - `LIST_NEXT_MONTHS` を「{翌月}月」に
2. **カード移動**
   - 翌月リスト（旧「N月以降」）から `due` が当月のカードを抽出
   - 元のリスト内順序を維持して、当月リストの上部に `pos` 10000刻みで配置
3. **既存カードの押し下げ**
   - 当月リストの既存カード（旧月の残り）を最下部へ再配置（pos = 移動分 + 10000刻み）

## 実行手順

### 1. 認証情報の確認

`.env` に `TRELLO_API_KEY` と `TRELLO_TOKEN` がある前提。

### 2. スクリプト実行

```bash
PYTHONIOENCODING=utf-8 python scripts/trello_monthly_rotate.py
# または対象月を明示:
PYTHONIOENCODING=utf-8 python scripts/trello_monthly_rotate.py 2026-05
```

実行ログに以下が表示される:
- リネーム結果（HTTP 200 + name）
- 翌月リストの総カード数 / 当月締切カード数 / 既存カード数
- 移動した各カードの `pos` / `due` / 名前
- 押し下げた既存カードの `pos` / 名前

### 3. 結果報告

ユーザーには以下のフォーマットで報告:

```
Trello月次処理完了

- 「{旧月}」→「{当月}」にリネーム
- 「{旧月}以降」→「{翌月}」にリネーム
- 当月締切カード {N}枚 を {当月}リスト上部へ移動
- 既存カード {M}枚 を最下部へ
```

## 注意事項

- スクリプトは `urllib` のみで動作（追加依存なし）
- `--data-urlencode` を bash で使うとShift-JIS化け（Windows）するため、Python経由で UTF-8 送信する
- リスト名のハードコード参照（trello-add.md / trello-reorder.md）は古い月のままになる可能性あり。気づいたら別途更新する
- 翌月リストにあるカードは `due` が当月のもののみ移動。`due` 未設定や来月以降のカードは移動しない

## 関連スクリプト

- `scripts/trello_monthly_rotate.py` — 本処理本体
- `scripts/trello_rename_lists.py` — リネーム単体（必要時）

## 参考

- `.claude/commands/trello-add.md` — カード追加
- `.claude/commands/trello-reorder.md` — 同一リスト内並び替え
