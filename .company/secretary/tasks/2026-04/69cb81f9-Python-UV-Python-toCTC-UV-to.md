---
archived_at: null
board: データに基づく原因究明
card_id: 69cb81f950080c8d4622b38a
checklist_done: 0
checklist_items: 12
comments_count: 0
completed: null
created: '2026-03-31'
due: '2026-04-21'
elapsed_days: 18
labels:
- green
list: 4月
members: []
name: （Pythonではじめる数理最適化を読んでリポジトリ構成の参考にする）長谷川さん、UV環境構築、そもそも何を設定・整備すれば？Pythonバージョン暗い？toCTCに相談するからUV環境構築に関して考えなくても良いかな？to齋藤さん
status: open
url: https://trello.com/c/JBbwfsX1
---

# （Pythonではじめる数理最適化を読んでリポジトリ構成の参考にする）長谷川さん、UV環境構築、そもそも何を設定・整備すれば？Pythonバージョン暗い？toCTCに相談するからUV環境構築に関して考えなくても良いかな？to齋藤さん

UVの環境構築＝pyproject.tomlファイルの整備

‌

Pythonバージョンやライブラリ（Depencency）を記入して、このtomlファイルから別の人も環境を再現できる

Pythonも自動インストール（pyenvも不要）

ライブラリ：uv add {library\_name} = pip install {library\_name}
（uv add は他のライブラリとの整合性チェック、pyproject.tomlへの書き込みも一緒にやってくれる）
高速インストール、従来の10-100倍
requirement.txtも不要

実行 uv run python [main.py](http://main.py "‌")
uv runを付けると起動時に仮想環境に入って、終わったら仮想環境から出る作業を自動でやってくれる
conda activate {env_name}やsorce .venv/bin/activate が不要

‌

‌

公式Pythonインストールだと全部のPCで同じPythonバージョンになって、バージョン変えたい場合は一回uninstallしないといけない

‌

\----------------------

uvインストール方法

インストールコマンド▼

◾Mac / Linux

curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh "‌") | sh

※Homebrewをインストールしているなら👇

brew install uv

◾Windows

powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1 "‌") | iex"

‌

‌

[https://www.youtube.com/watch?v=Kna8zhwO1VA&t=11s](https://www.youtube.com/watch?v=Kna8zhwO1VA&t=11s "smartCard-embed")

## コメント・移動履歴
- 2026-03-31 08:12 作成
- 2026-03-31 08:35 リスト移動: 5月以降 → 4月
- 2026-04-04 14:27 リスト移動: 4月 → 今週（平日）
- 2026-04-05 14:26 リスト移動: 今週（平日） → 今日（後半）
- 2026-04-06 14:26 リスト移動: 今日（後半） → 今日（前半）
- 2026-04-07 09:02 リスト移動: 今日（前半） → 今日（後半）
- 2026-04-07 14:27 リスト移動: 今日（後半） → 今日（前半）
- 2026-04-08 03:20 リスト移動: 今日（前半） → 今日（後半）
- 2026-04-08 14:26 リスト移動: 今日（後半） → 今日（前半）
- 2026-04-09 09:08 リスト移動: 今日（前半） → 今日（後半）
- 2026-04-09 14:26 リスト移動: 今日（後半） → 今日（前半）
- 2026-04-10 04:45 リスト移動: 今日（前半） → 4月
- 2026-04-11 14:28 リスト移動: 4月 → 今週（平日）
- 2026-04-12 14:27 リスト移動: 今週（平日） → 今日（後半）
- 2026-04-13 14:27 リスト移動: 今日（後半） → 今日（前半）
- 2026-04-14 02:51 リスト移動: 今日（前半） → 今日（後半）
- 2026-04-14 14:27 リスト移動: 今日（後半） → 今日（前半）
- 2026-04-15 06:02 リスト移動: 今日（前半） → 今日（後半）
- 2026-04-15 14:26 リスト移動: 今日（後半） → 今日（前半）
- 2026-04-16 05:59 リスト移動: 今日（前半） → 今日（後半）
- 2026-04-16 06:19 リスト移動: 今日（後半） → 4月
