---
description: Notionの統合TODO DBにタスクを直接追加する。「Notion追加」と言われたら使う。
---

# Notion TODO 追加スキル

ユーザーの指示からNotionの統合TODO DBにタスクを作成する。

## 引数

$ARGUMENTS

## DB情報

- **統合TODO DB ID**: `33f0df73-1957-8182-846d-cbf9362688a2`
- **プロジェクト管理 DB ID**: `33f0df73-1957-8150-9631-e7857be9a971`

## プロジェクトID一覧

| プロジェクト名 | ページID |
|---|---|
| XTP2 | `33f0df73-1957-819d-9035-cc7965d1eaa8` |
| ITP2 | `33f0df73-1957-819d-862b-da6783fcb262` |
| コンテンツ販売 | `33f0df73-1957-8174-b955-d4b7df59b4c3` |
| ブログ / note | `33f0df73-1957-81f3-aabe-de87b958f685` |
| ココナラ | `33f0df73-1957-810d-bc03-dd0f8bd309d7` |
| Twitter Bot | `33f0df73-1957-8198-a4d0-d08e3341bd2b` |

## 実行手順

### Step 1: 引数を解析

ユーザーの入力から以下を特定:
- **タスク名**（必須）
- **時間枠**（任意。デフォルト: 今日）
- **優先度**（任意。デフォルト: 中）
- **カテゴリ**（任意。文脈から推定）
- **プロジェクト**（任意。文脈から推定）
- **期限日**（任意。相対指定も計算）
- **所要時間**（任意。分単位）
- **メモ**（任意）

### Step 2: Notionにページ作成

Python urllib で Notion REST API を呼び出す:

```python
import urllib.request, json, os

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
TODO_DB_ID = "33f0df73-1957-8182-846d-cbf9362688a2"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

page_data = {
    "parent": {"database_id": TODO_DB_ID},
    "properties": {
        "タスク名": {"title": [{"text": {"content": task_name}}]},
        "ステータス": {"status": {"name": "未着手"}},
        "時間枠": {"select": {"name": timeframe}},
        "優先度": {"select": {"name": priority}},
        "ソース": {"select": {"name": "Notion"}}
    }
}

# オプションプロパティを追加
if category:
    page_data["properties"]["カテゴリ"] = {"select": {"name": category}}
if project_id:
    page_data["properties"]["プロジェクト"] = {"relation": [{"id": project_id}]}
if due_date:
    page_data["properties"]["期限日"] = {"date": {"start": due_date}}
if estimated_minutes:
    page_data["properties"]["所要時間（分）"] = {"number": estimated_minutes}
if memo:
    page_data["properties"]["メモ"] = {"rich_text": [{"text": {"content": memo}}]}

body = json.dumps(page_data).encode("utf-8")
req = urllib.request.Request("https://api.notion.com/v1/pages", data=body, headers=headers, method="POST")
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read().decode("utf-8"))
```

### Step 3: 結果を報告

```
追加しました！

- タスク: {タスク名}
- 時間枠: {時間枠}
- 優先度: {優先度}
- プロジェクト: {プロジェクト名}（あれば）
- 期限: {MM/DD}（あれば）
```

## 注意事項

- 期限日は JST で解釈する
- プロジェクトは文脈から自動推定（XTP関連→XTP2、ブログ関連→ブログ/note等）
- Trelloへのミラーが必要な場合は `trello-add` スキルも併用する
