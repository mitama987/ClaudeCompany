---
description: Notionの統合TODO DBから週次レビューレポートを生成する。「週次レビュー」と言われたら使う。
---

# 週次レビュースキル

Notionの統合TODO DBを分析し、今週の進捗レポートを生成する。

## 引数

$ARGUMENTS

## DB情報

- **統合TODO DB ID**: `33f0df73-1957-8182-846d-cbf9362688a2`
- **プロジェクト管理 DB ID**: `33f0df73-1957-8150-9631-e7857be9a971`

## 実行手順

### Step 1: 今日の日付と今週の範囲を計算

```python
from datetime import datetime, timedelta

today = datetime.now()
# 今週の月曜日
monday = today - timedelta(days=today.weekday())
monday_str = monday.strftime("%Y-%m-%d")
today_str = today.strftime("%Y-%m-%d")
# 2週間前（長期待機チェック用）
two_weeks_ago = (today - timedelta(days=14)).strftime("%Y-%m-%d")
```

### Step 2: Notion APIで3種類のクエリを実行

Python urllib で Notion REST API を呼び出す:

```python
import urllib.request, json

NOTION_TOKEN = "***REMOVED***"
TODO_DB_ID = "33f0df73-1957-8182-846d-cbf9362688a2"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def query_db(filter_obj):
    body = json.dumps({"filter": filter_obj}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.notion.com/v1/databases/{TODO_DB_ID}/query",
        data=body, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["results"]
```

#### クエリ A: 今週完了タスク

```python
completed = query_db({
    "and": [
        {"property": "ステータス", "status": {"equals": "完了"}},
        {"property": "完了日", "date": {"on_or_after": monday_str}}
    ]
})
```

#### クエリ B: 期限超過タスク

```python
overdue = query_db({
    "and": [
        {"property": "ステータス", "status": {"does_not_equal": "完了"}},
        {"property": "期限日", "date": {"before": today_str}}
    ]
})
```

#### クエリ C: 長期待機タスク（2週間以上）

Notion APIでは作成日でのフィルタが直接できないため、全待機中タスクを取得して手動フィルタ:

```python
waiting = query_db({
    "property": "ステータス", "status": {"equals": "待機中"}
})
# created_time が2週間以上前のものを抽出
long_waiting = [t for t in waiting if t["created_time"] < two_weeks_ago + "T00:00:00.000Z"]
```

### Step 3: 全体統計を取得

```python
# 全未完了タスク
all_active = query_db({
    "property": "ステータス", "status": {"does_not_equal": "完了"}
})
```

### Step 4: レポート生成

以下のフォーマットで表示:

```
📊 週次レビュー（{monday_str} 〜 {today_str}）

## ✅ 今週の完了タスク（{len(completed)}件）
{各タスク名をリスト表示}

## ⚠️ 期限超過タスク（{len(overdue)}件）
{各タスク名 + 期限日をリスト表示}
→ 対応を検討してください

## 💤 長期待機タスク（{len(long_waiting)}件）
{各タスク名 + 作成日をリスト表示}
→ 退避 or 削除を検討してください

## 📈 サマリー
- 今週完了: {len(completed)}件
- 未完了（アクティブ）: {len(all_active)}件
- 期限超過: {len(overdue)}件
- 長期待機: {len(long_waiting)}件
```

### Step 5（オプション）: レポートをNotionに保存

ユーザーが「保存して」と指示した場合、ハブページ（`33f0df73-1957-816f-932c-c51f468a61f8`）配下に
`週次レビュー {today_str}` という名前のページを作成し、レポート内容をブロックとして書き込む。

## 注意事項

- 完了日が未設定のタスクは今週完了にカウントしない
- プロジェクト管理DBの収益情報も併せて表示すると有用（ユーザーが要望した場合）
- レポートは日本語で出力する
