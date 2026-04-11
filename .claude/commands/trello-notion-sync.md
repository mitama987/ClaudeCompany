---
description: TrelloカードをNotionの統合TODO DBに同期する。「Trello同期」と言われたら使う。
---

# Trello → Notion 同期スキル

TrelloボードのアクティブなカードをNotionの統合TODO DBに同期する。

## 引数

$ARGUMENTS

## DB情報

- **Notion 統合TODO DB ID**: `33f0df73-1957-8182-846d-cbf9362688a2`
- **Trello ボードID**: `5ffe5b3fa17b04881f2c4fbc`

## Trelloリスト → Notion マッピング

| Trelloリスト | リストID | 時間枠 | ステータス |
|---|---|---|---|
| 今日（前半） | `5ffe5b3fa17b04881f2c4fbf` | 今日 | 進行中 |
| 今日（後半） | `5ffe5b3fa17b04881f2c4fbe` | 明日 | 未着手 |
| 今週（平日） | `5ffe5b3fa17b04881f2c4fc0` | 今週 | 未着手 |
| 4月 | 当月リスト（get_listsで確認） | 今月 | 未着手 |
| 5月以降 | get_listsで確認 | 来月以降 | 未着手 |
| 夢 | get_listsで確認 | いつか | 未着手 |
| 退避タスク | get_listsで確認 | — | 待機中 |
| 退避タスク（本業） | get_listsで確認 | — | 待機中 |
| 完了リスト | get_listsで確認 | — | 完了 |

## Notion API認証

```bash
# Notion REST API を使う場合
NOTION_TOKEN="***REMOVED***"
```

※ MCP経由の場合は `mcp__notionApi__API-post-page` を使用。APIバージョン制約で DB作成は REST API 直接呼び出しが必要な場合あり。

## 実行手順

### Step 1: Trelloボードをアクティブにする

```
mcp__trello__set_active_board(boardId: "5ffe5b3fa17b04881f2c4fbc")
```

### Step 2: 各リストのカードを取得

上記マッピング表の各リストに対して `mcp__trello__get_cards_by_list_id` を実行。

### Step 3: Notion側で既存カードを確認

Python urllib で Notion API を呼び出し、統合TODO DBをクエリ:

```python
import urllib.request, json

NOTION_TOKEN = "***REMOVED***"
TODO_DB_ID = "33f0df73-1957-8182-846d-cbf9362688a2"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# TrelloカードIDでフィルタ
filter_data = {
    "filter": {
        "property": "TrelloカードID",
        "rich_text": {"equals": card_id}
    }
}
body = json.dumps(filter_data).encode("utf-8")
req = urllib.request.Request(
    f"https://api.notion.com/v1/databases/{TODO_DB_ID}/query",
    data=body, headers=headers, method="POST"
)
```

### Step 4: 同期処理

各Trelloカードに対して:

1. **Notion未登録** → 新規ページ作成（`POST /v1/pages`）
2. **Notion登録済み** → プロパティ更新（`PATCH /v1/pages/{page_id}`）
   - Trello側のリスト変更 → 時間枠・ステータスを更新
   - Trello側の期限変更 → 期限日を更新
   - Trello側のカード名変更 → タスク名を更新

### Step 5: Notionページ作成フォーマット

```python
page_data = {
    "parent": {"database_id": TODO_DB_ID},
    "properties": {
        "タスク名": {"title": [{"text": {"content": card_name}}]},
        "ステータス": {"status": {"name": status}},
        "時間枠": {"select": {"name": timeframe}},
        "TrelloカードID": {"rich_text": [{"text": {"content": card_id}}]},
        "Trelloリンク": {"url": card_url},
        "ソース": {"select": {"name": "Trello"}},
    }
}
# 期限日がある場合
if due_date:
    page_data["properties"]["期限日"] = {"date": {"start": due_date[:10]}}
```

### Step 6: 結果を報告

```
同期完了！

- 新規追加: {N}件
- 更新: {N}件
- スキップ（変更なし）: {N}件
- 合計: {N}件
```

## 注意事項

- 完了リストのカードは ステータス=完了 で同期する
- 退避タスクリストのカードは ステータス=待機中 で同期する（時間枠は設定しない）
- 同期の競合は「Trello優先」（Trelloが主軸のため）
- 月名リスト（3月、4月等）は動的に判定する（`get_lists`で最新を確認）
