---
name: gmail-to-trello
description: 未読Gmailを確認し、選択したメールをTrelloタスクとして追加するスキル。「メールからタスク」「Gmail Trello」と言われたら使う。
user_invocable: true
---

# Gmail → Trello タスク追加スキル

未読Gmailを取得し、ユーザーが選んだメールをTrelloカードとして追加する一連のワークフロー。

## 使用方法

```
/gmail-to-trello                # 未読メール確認 → Trello追加（デフォルト）
/gmail-to-trello 10             # 未読メール10件を取得して確認
/gmail-to-trello search <query> # Gmail検索結果からTrello追加
```

## API情報

### Gmail (GWS CLI)

- **ツール**: GWS CLI (`gws` コマンド)
- **対象アカウント**: mitama987@gmail.com
- **前提**: 環境変数 `GOOGLE_WORKSPACE_CLI_CLIENT_ID` / `GOOGLE_WORKSPACE_CLI_CLIENT_SECRET` が設定済み、`gws auth login` 認証済み
- **環境変数の読み込み**: Bash実行時に `export` で設定する

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="REDACTED_GWS_CLIENT_ID"
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="REDACTED_GWS_CLIENT_SECRET"
```

### Trello

- **ボードID**: `5ffe5b3fa17b04881f2c4fbc`
- **ボード名**: データに基づく原因究明

**リスト一覧:**

| リスト名 | ID | 用途 |
|---------|-----|------|
| 今日（前半）| `5ffe5b3fa17b04881f2c4fbf` | 今日のタスク |
| 今日（後半）| `5ffe5b3fa17b04881f2c4fbe` | **明日の予定**（名前と用途が異なるので注意） |
| 今週（平日）| `5ffe5b3fa17b04881f2c4fc0` | 今週のタスク |
| 3月 | `5ffe5b3fa17b04881f2c4fc3` | 3月のタスク |
| 4月以降 | `5ffe5b3fa17b04881f2c4fc4` | 4月以降のタスク |

### Trello API認証

```bash
source .env
# TRELLO_API_KEY, TRELLO_TOKEN が設定される
```

## 処理フロー

### Step 1: 未読メール取得（inboxのみ）

Bashで `gws` コマンドを実行してJSON形式でinboxの未読メールを取得する。
**常に `in:inbox` フィルタを付けること。** プロモーション・ソーシャル等のタブは除外する。

#### Step 1-1: メッセージID一覧を取得

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="REDACTED_GWS_CLIENT_ID"
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="REDACTED_GWS_CLIENT_SECRET"
gws gmail users messages list --params '{"userId":"me","q":"is:unread in:inbox","maxResults":20}' --format json
```

- デフォルトで上限20件。件数指定がある場合は `maxResults` を変更する
- JSON出力から `messages` 配列を取得（各要素に `id`, `threadId` が含まれる）

#### Step 1-2: 各メッセージのヘッダー情報を取得

Step 1-1で取得した各メッセージIDについて、ヘッダー情報（差出人・件名・日時）を取得する。
複数メッセージは**並行して**Bashで取得し高速化する。

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="REDACTED_GWS_CLIENT_ID"
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="REDACTED_GWS_CLIENT_SECRET"
gws gmail users messages get --params '{"userId":"me","id":"<messageId>","format":"metadata","metadataHeaders":["From","Subject","Date"]}' --format json
```

- 各メッセージの `payload.headers` から `From`, `Subject`, `Date` を抽出する
- 5件以下なら1つのBashコマンドで `&&` 連結、6件以上なら複数のBash呼び出しに分けて並行実行する

#### search引数がある場合

```bash
gws gmail users messages list --params '{"userId":"me","q":"<検索クエリ> in:inbox","maxResults":20}' --format json
```

※ searchクエリにも `in:inbox` を付加する

### Step 2: メール一覧を表示

取得したJSONを以下の表形式で表示する:

```
| # | 日時 (JST) | 差出人 | 件名 |
|---|-----------|--------|------|
| 1 | MM/DD HH:MM | 差出人名 | 件名 |
```

- 日時は UTC → JST (+9時間) に変換して `MM/DD HH:MM` 形式
- 差出人はメールアドレス部分を省略し名前のみ表示
- 末尾に未読件数のサマリーを表示

### Step 3: ユーザーにタスク化するメールを選択させる

`AskUserQuestion` で、どのメールをTrelloに追加するか確認する。

選択肢の例:
- 「全件追加」
- 「対応が必要なもの（通知・プロモを除外）」
- 「自分で選ぶ」

ユーザーの回答に応じて対象メールを確定する。

### Step 4: メール本文を取得し返信案を作成

選択されたメールの本文を `gws gmail +read` で取得する。

```bash
export GOOGLE_WORKSPACE_CLI_CLIENT_ID="REDACTED_GWS_CLIENT_ID"
export GOOGLE_WORKSPACE_CLI_CLIENT_SECRET="REDACTED_GWS_CLIENT_SECRET"
gws gmail +read --message-id <メッセージID>
```

各メールの内容を読み、**返信案（ドラフト）**を作成する。

**返信案の作成ルール:**
- 差出人の名前で「〇〇様」と宛名を付ける
- 「お世話になっております。夕凪です。」から始める（ユーザー名は文脈に応じて変更）
- メールの質問・問題に対する具体的な回答・手順を記載
- 丁寧だが簡潔に。箇条書きや番号付きリストを活用
- 末尾は「よろしくお願いいたします。」で締める

### Step 5: Trelloカード作成

選択された各メールについて、Trello MCP の `mcp__trello__add_card_to_list` で並行してカードを作成する。

**カード情報の構成ルール:**

| フィールド | 値 |
|-----------|-----|
| `name` | `【カテゴリ】要約タスク名` |
| `listId` | 締切日ベースで自動判定（下記参照） |
| `dueDate` | 当日の場合 `YYYY-MM-DDT15:00:00.000Z` (= JST翌日0時) |
| `description` | 下記テンプレート参照 |
| `labels` | `["5ffe5b40a17b04881f2c51a6"]` （blue_dark ラベル（Trello既存デフォルト）） |

**カード説明（description）テンプレート:**

```markdown
## メール内容
- **差出人**: 差出人名 (プラットフォーム)
- **受信日時**: YYYY/MM/DD HH:MM JST
- **内容**: メール内容の要約

## 返信案
---
（Step 4で作成した返信案をここに記載）
---

リンク: （ココナラDM/トークルームURL等があれば記載）
```

**ラベル:**
- blue_dark ラベル（Trello既存デフォルト） (ID: `5ffe5b40a17b04881f2c51a6`, color: `blue`) を必ず付与する
- `mcp__trello__add_card_to_list` の `labels` パラメータに `["5ffe5b40a17b04881f2c51a6"]` を指定

**カード名のカテゴリ:**
- ココナラのメッセージ → `【ココナラ返信】`
- 顧客からの問い合わせ → `【顧客対応】`
- 通知系 → `【確認】`
- その他 → `【対応】`

**リスト自動判定（期限未指定時は「今日」扱い）:**

1. **今日** → `今日（前半）` (ID: `5ffe5b3fa17b04881f2c4fbf`)
2. **明日** → `今日（後半）` (ID: `5ffe5b3fa17b04881f2c4fbe`)
3. **今週中** → `今週（平日）` (ID: `5ffe5b3fa17b04881f2c4fc0`)
4. **今月中** → 当月リスト
5. **来月以降** → `4月以降` (ID: `5ffe5b3fa17b04881f2c4fc4`)

※ ユーザーが明示的にリスト・期限を指定した場合はそちらを優先する。

### Step 5.5: リスト内カードの優先度ソート

カード追加後、対象リストの全カードをラベル優先度 + 締切日で並び替える。

#### ソートルール

**第1キー: ラベル色の優先度（上が先）**

| 優先度 | ラベル | ID |
|--------|--------|-----|
| 1 | blue_dark（ダークブルー） | `5ffe5b40a17b04881f2c51a6` |
| 2 | 緑 | `5ffe5b40a17b04881f2c5196` |
| 3 | 黒 | `644b05b30003aaa5d54794c2` |
| 4 | その他（ラベルなし含む） | - |

- 複数ラベル付きカードは最高優先度のラベルで判定

**第2キー: 締切日（早い順）**
- 同じラベルグループ内で `due` 昇順
- `due=null` はグループ内の最後

#### 実行手順

1. `mcp__trello__get_cards_by_list_id` で対象リストの全カードを取得
2. 上記ルールでソート順を決定
3. `pos` 値を65536刻みで再割り当て（1番目=65536, 2番目=131072, ...）
4. Bash `curl` で変更が必要なカードのみ更新:

```bash
source .env
curl -s -o /dev/null -X PUT "https://api.trello.com/1/cards/{cardId}?pos={newPos}&key=${TRELLO_API_KEY}&token=${TRELLO_TOKEN}"
```

5. 複数カードの `pos` 更新は1つの Bash コマンドで連結して実行（`&&` で繋ぐ）

### Step 6: 結果報告

完了後、以下の形式で報告する:

```
**Trelloに追加しました！**（blue_dark ラベル（Trello既存デフォルト）付き）

| カード | リスト | リンク |
|--------|--------|--------|
| カード名 | リスト名 | https://trello.com/c/xxx |
```

その後、必ず **返信案の要約** を以下の形式で表示する（毎回必須）:

```
**返信案の要約:**
- **相手名**: 要件の要約 → 返信のポイント（1行で簡潔に）
```

この要約があることで、ユーザーがすぐに返信内容を把握し、カードを開かずに対応方針を確認できる。

### Step 7: 秘書TODO記録（.companyが存在する場合のみ）

`.company/` ディレクトリが存在する場合、`secretary/todos/YYYY-MM-DD.md` に追記する。

- ファイルが存在しない場合は新規作成（テンプレートは `# TODO - YYYY-MM-DD`）
- 既存の場合は追記（同日1ファイルルール）
- フォーマット:

```markdown
## Gmailからのタスク (HH:MM追加)

- [ ] タスク名 | 優先度: 高 | 期限: YYYY-MM-DD
```

## 注意事項

- GWS CLIは `gmail.modify` スコープで認証済み（読み書き可能だが、このスキルでは読み取りのみ使用）
- 締切日は必ず JST で解釈する
- 同じ締切日のカードが既にある場合は、そのカードの直後に配置
- 複数カードを追加する際は `mcp__trello__add_card_to_list` を**並行呼び出し**して高速化する
- GWS CLI認証が切れている場合は `gws auth login` で再認証する

---

Version History
- ver1.0 | 2026-04-04 | 初版作成。Gmail未読取得→Trelloカード追加の一連ワークフローをスキル化
- ver1.1 | 2026-04-04 | メール本文から返信案を自動生成しカード説明に記載。blue_dark ラベル（Trello既存デフォルト）自動付与を追加
- ver1.2 | 2026-04-04 | カード追加後にリスト内をラベル優先度(青>緑>黒>他)+締切日で自動ソートするStep 5.5を追加
- ver1.3 | 2026-04-06 | Step 6の結果報告で返信案の要約を毎回必須表示するよう明記
- ver1.4 | 2026-04-06 | Step 1を2段階に変更。まず未読件数を確認し、全件取得する方式に（上限20件）
- ver1.5 | 2026-04-10 | Gmail取得をGAS WebアプリAPIからGWS CLI (`gws`コマンド) に移行。リダイレクト処理・GAS実行制限を撤廃
- ver1.6 | 2026-04-12 | デフォルト取得をinboxのみに変更。`+triage`(全未読)から`in:inbox`フィルタ付きAPI呼び出しに移行。2段階取得（ID一覧→ヘッダー情報）に変更
