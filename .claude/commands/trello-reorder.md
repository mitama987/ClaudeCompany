---
description: Trelloリスト内のカードを優先順で並び替える。REST APIで pos を直接指定。「Trello並び替え」「Trelloソート」と言われたら使う。
---

# Trello カード並び替えスキル

リスト内のカードを指定した優先順に並び替える。Trello MCPの`move_card`では同一リスト内で`pos`を正確に指定できず、Trelloの自動正規化で意図通りに並ばないため、**REST APIを直接叩いて `pos` を明示指定**する。

## 引数

$ARGUMENTS

（例：「今日（前半）を優先順で並び替え」「今週リストを締切日順で」など）

## ボード情報

- **ボードID**: `5ffe5b3fa17b04881f2c4fbc`
- **ボード名**: データに基づく原因究明

## リスト一覧

| リスト名 | ID | 用途 |
|---------|-----|------|
| 今日（前半）| `5ffe5b3fa17b04881f2c4fbf` | 今日のタスク |
| 今日（後半）| `5ffe5b3fa17b04881f2c4fbe` | **明日の予定**（名前と用途が異なる） |
| 今週（平日）| `5ffe5b3fa17b04881f2c4fc0` | 今週のタスク |

## Trello API認証

プロジェクトルートの `.env` ファイルから読み込む：

```bash
source .env
# TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID が設定される
```

## 実行手順

### Step 1: 対象リストを特定

ユーザーが明示した場合はそれを、未指定なら **「今日（前半）」** をデフォルトにする。

### Step 2: 現在のカード一覧を取得

Trello MCP の `get_cards_by_list_id` を使う：

- 各カードの `id`, `name`, `due`, `labels`, `desc` の先頭を控える
- 出力が大きくてトークン上限に引っかかる場合は、Explore サブエージェントに「id / name / due / pos だけ抽出」と指示して圧縮する

### Step 3: 優先順を決定

ユーザーが順序を明示していればそれに従う。未指定または曖昧な場合は `AskUserQuestion` で確認する。

**デフォルトの優先順ルール**（今日系リストの場合）:

1. **ルーチン** — 「今日のタスクの優先順位決め」「瞑想」「N-BACK」「メールチェック」
2. **即レス・短文返信** — カード名に「返信」「連絡」「【ココナラ返信】」「【Slack返信】」「【顧客対応】」を含むもの
3. **開発・マーケ** — その他の実作業カード
4. **別枠** — 「昼食」「ジム」など固定時間の生活タスク

同一カテゴリ内では **締切日昇順 → ラベル優先度**（trello-add.md のラベル優先度表参照）でソート。

### Step 4: pos を割り当て

各カードに **10000 刻み** で `pos` を割り当てる：

| 順位 | pos |
|------|-----|
| 1 | 10000 |
| 2 | 20000 |
| 3 | 30000 |
| ... | ... |
| N | N × 10000 |

**なぜ10000刻みか**: 後から1枚挿入する際、中間値（例：15000）で割り込めるようにするため。

### Step 5: REST API で一括更新

bashループで `curl -X PUT` を各カードに実行する：

```bash
source .env

# 優先順に並べた配列: "cardId:pos:表示名"
ORDER=(
  "{cardId1}:10000:ルーチン1"
  "{cardId2}:20000:ルーチン2"
  "{cardId3}:30000:即レス1"
  # ... N枚分続ける
)

for entry in "${ORDER[@]}"; do
  ID=$(echo "$entry" | cut -d: -f1)
  POS=$(echo "$entry" | cut -d: -f2)
  NAME=$(echo "$entry" | cut -d: -f3)
  RESULT=$(curl -sS -X PUT "https://api.trello.com/1/cards/$ID?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN&pos=$POS" -w "HTTP:%{http_code}" -o /tmp/trello_resp.json)
  HTTP=$(echo "$RESULT" | grep -oE "HTTP:[0-9]+")
  ACTUAL_POS=$(grep -oE '"pos":[0-9]+' /tmp/trello_resp.json | head -1)
  echo "[$POS] $NAME → $HTTP $ACTUAL_POS"
done
```

全行が `HTTP:200` かつ `"pos":N`（指定した値）になっていれば成功。

### Step 6: 結果を報告

以下のフォーマットで完了報告：

```
並び替え完了（リスト: {リスト名} / {N}枚）

| # | タスク |
|---|---|
| 1 | {カード名1} |
| 2 | {カード名2} |
...
```

Trelloアプリをリロードすると反映される旨を最後に一言添える。

## 注意事項

- **同一リスト内の並び替え専用**。別リストへの移動は Trello MCP の `move_card` を使う。
- Trelloの `pos` は単純な数値比較で上→下の順。小さいほど上。
- ユーザー命名の順位ルールと、デフォルトルールがぶつかった場合は**ユーザーの指示を優先**。
- カードIDは Trello MCP の `get_cards_by_list_id` レスポンスから取得する（URL末尾の shortLink ではなく `id` フィールド）。
- 並び替え対象が非常に多い（20枚以上）場合、配列定義が長くなるため一時ファイル（例: `/tmp/trello_reorder.sh`）に書き出して実行する選択肢もある。

## 参考

- 同じREST APIパターンは `trello-add.md` の Step 6（新規カード挿入時の pos 計算）で使用している
- 認証情報は `.env` に配置
