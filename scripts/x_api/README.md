# scripts/x_api

X (Twitter) Web版クッキー（`auth_token` / `ct0`）を使ってログイン状態でAPIを叩くための雛形。

## 資格情報の配置

以下のいずれかの方法で `X_AUTH_TOKEN` と `X_CT0` を設定してください（探索順）:

1. **環境変数** (`$env:X_AUTH_TOKEN=...` など)
2. **`~/.config/x-credentials/.env`** （リポ外、推奨）
   ```env
   X_AUTH_TOKEN=...
   X_CT0=...
   ```
3. **`<repo>/.env`** （`.gitignore` 済み）

## 動作確認

```bash
uv run python -m scripts.x_api.example_get_settings
```

ログイン中アカウントの screen_name / language / time_zone が出れば成功。

## 使い方

```python
from scripts.x_api.client import build_client

with build_client() as c:
    r = c.get("/1.1/statuses/user_timeline.json", params={"count": 10})
    print(r.json())
```

## 注意

- `auth_token` / `ct0` はアカウントのフルアクセス権を持つ。共有・コミット厳禁
- IPやUser-Agentが極端に変わるとX側のリスクスコアリングでチャレンジが発生する場合あり
- レート制限を超えるとアカウント一時ロックの可能性あり
- 失効したらブラウザから取り直し（数ヶ月は有効）
