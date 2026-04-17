# Trello タスク分析ダッシュボード

Trelloの全カード（期限が2026-01-01以降）を1枚=1MDファイルとして記録し、
FastAPI+Chart.jsでジャンル別投下時間や時間超過の示唆を出す。

## 構成

```
Trello REST API
    │
    ▼
scripts/trello_sync.py
    ▼
.company/secretary/tasks/YYYY-MM/{card-id-slug}.md    ← 1カード=1MD
    ▼
scripts/dashboard/server.py (FastAPI, :3940)
    ├─ /api/summary     ラベル別・月次集計
    ├─ /api/scatter     経過日数×エンゲージメント
    ├─ /api/insights    ルールベース示唆
    └─ /api/refresh     Trelloから再同期（POST）
    ▼
scripts/dashboard/static/index.html  (Chart.js)
```

既存の `cc-company-dashboard (:3939)` はそのまま使える。本ダッシュボードは別ポート(:3940)。

## セットアップ

`.env` に以下を設定（既にある想定）:

```
TRELLO_API_KEY=xxxx
TRELLO_TOKEN=xxxx
TRELLO_BOARD_ID=5ffe5b3fa17b04881f2c4fbc
```

## 使い方

### 初回・定期同期

```
uv run python scripts/trello_sync.py
# オプション: --since 2026-01-01 --board <board_id>
```

### ダッシュボード起動

```
uv run uvicorn scripts.dashboard.server:app --port 3940 --reload
```

ブラウザで http://127.0.0.1:3940/

画面の「🔄 Trello 再同期」ボタンでMDファイル再生成も可能。

## MDファイル仕様

```markdown
---
card_id: "<Trello card id>"
name: "<title>"
board: "<board name>"
list: "<current list>"
status: archived | completed | open
created: "YYYY-MM-DD"        # カードIDの先頭8hex（Unix秒）から復元
due: "YYYY-MM-DD"
completed: "YYYY-MM-DD"
archived_at: "YYYY-MM-DD"
labels: ["label1", "label2"]
members: ["Name"]
comments_count: 0
checklist_items: 0
checklist_done: 0
elapsed_days: 0
url: "https://trello.com/c/xxx"
---

# タイトル

（Trello description）

## コメント・移動履歴
- YYYY-MM-DD HH:MM 作成
- YYYY-MM-DD HH:MM リスト移動: X → Y
- YYYY-MM-DD HH:MM コメント: ...
```

`## 手動メモ` という見出しで追記した内容は次回同期でも保持される。

## 示唆ルール（`scripts/dashboard/insights.py`）

| レベル | ルール | 条件 |
|---|---|---|
| warning | ラベル配分の偏り | ラベル別時間合計の max/min > 5倍 |
| danger  | 時間超過タスク | 経過日数 >= max(中央値×3, 14日) |
| info    | 議論過多 | コメント数 p95超（>= 5） |
| warning | 未完了放置 | status=open × 作成から30日以上 |
| warning | 完了率低下 | 直近30日の完了率 < 過去平均 × 0.5 |
| info    | 最注力ジャンル | ラベル別時間合計のトップ |

## 制約と今後の課題

- Trello APIには時間トラッキングが無いため、経過日数（作成日→完了日）を主指標に
- ラベル名が空のカードは `label.color` で代替（black / green 等）→ Trello側でラベル名を付けると解釈が向上
- 2026-01-01以降のactionsのみ取得しているので、それ以前に作成されたカードの作成日はカードIDから復元
- 3000件超のボードでも `filter=closed` + `filter=visible` の二段取得で API_TOO_MANY_CARDS_REQUESTED を回避
