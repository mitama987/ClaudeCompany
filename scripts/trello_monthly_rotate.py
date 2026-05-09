"""Trello月次処理: 月初に「N月」リストの中身を入れ替える。

- 「N-1月」(=旧月)リストを「N月」(=今月)にリネーム
- 「N月以降」リストを「N+1月」(=翌月)にリネーム
- 旧「N月以降」(=新「N+1月」)から、今月締切のカードを「N月」リストへ移動
- 移動カードは元のリスト内順序を維持し、「N月」リストの上部に配置 (pos 10000刻み)
- 「N月」リストの既存カード(旧月の残り)は最下部へ再配置

実行例 (2026-05-02 に実行):
    旧: "4月" / "5月以降"
    新: "5月" / "6月"
    移動: "6月"内の due='2026-05-*' のカードを "5月" の上部に

ボード「データに基づく原因究明」の月次運用前提。リストIDは変わらない。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date


# ボード「データに基づく原因究明」(5ffe5b3fa17b04881f2c4fbc) の月次2リスト
LIST_CURRENT_MONTH = "5ffe5b3fa17b04881f2c4fc3"  # 「N月」(現在の月)
LIST_NEXT_MONTHS = "5ffe5b3fa17b04881f2c4fc4"   # 「N月以降」→「N+1月」


def load_env(path: str = ".env") -> None:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)


def trello_get(path: str) -> list | dict:
    key = os.environ["TRELLO_API_KEY"]
    token = os.environ["TRELLO_TOKEN"]
    sep = "&" if "?" in path else "?"
    url = f"https://api.trello.com/1{path}{sep}key={key}&token={token}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())


def trello_put(path: str, fields: dict) -> dict:
    key = os.environ["TRELLO_API_KEY"]
    token = os.environ["TRELLO_TOKEN"]
    sep = "&" if "?" in path else "?"
    url = f"https://api.trello.com/1{path}{sep}key={key}&token={token}"
    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def resolve_target_month(arg: str | None) -> tuple[int, int]:
    """戻り値: (year, month) 月次処理の対象月。"""
    if arg:
        # "2026-05" or "2026/5" or "5"
        s = arg.replace("/", "-")
        if "-" in s:
            y, m = s.split("-")
            return int(y), int(m)
        today = date.today()
        return today.year, int(s)
    today = date.today()
    return today.year, today.month


def main(argv: list[str]) -> None:
    load_env()

    target_year, target_month = resolve_target_month(argv[1] if len(argv) > 1 else None)
    next_month = target_month + 1 if target_month < 12 else 1
    target_prefix = f"{target_year:04d}-{target_month:02d}"

    print(f"[INFO] 対象月: {target_year}-{target_month:02d} (prefix='{target_prefix}')")
    print(f"[INFO] リネーム: 「N月」→「{target_month}月」 / 「N月以降」→「{next_month}月」")

    # === Step 0: リスト名を変更 ===
    print("\n=== Step 0: Rename lists ===")
    r1 = trello_put(f"/lists/{LIST_CURRENT_MONTH}", {"name": f"{target_month}月"})
    print(f"  {LIST_CURRENT_MONTH}: name={r1['name']!r}")
    r2 = trello_put(f"/lists/{LIST_NEXT_MONTHS}", {"name": f"{next_month}月"})
    print(f"  {LIST_NEXT_MONTHS}: name={r2['name']!r}")

    # === Step 1: 翌月リスト(旧N月以降)から今月締切カードを抽出 ===
    next_cards = trello_get(f"/lists/{LIST_NEXT_MONTHS}/cards?fields=id,name,due,pos")
    next_sorted = sorted(next_cards, key=lambda c: c["pos"])
    target_cards = [
        c for c in next_sorted
        if c.get("due") and c["due"].startswith(target_prefix)
    ]
    print(f"\n[INFO] 「{next_month}月」リスト総カード数: {len(next_sorted)}")
    print(f"[INFO] 今月({target_prefix})締切カード: {len(target_cards)}")

    existing = trello_get(f"/lists/{LIST_CURRENT_MONTH}/cards?fields=id,name,due,pos")
    existing_sorted = sorted(existing, key=lambda c: c["pos"])
    print(f"[INFO] 「{target_month}月」リスト既存カード(旧月の残り): {len(existing_sorted)}")

    # === Step 2: 今月締切カードを今月リスト上部へ ===
    print(f"\n=== Step 2: Move {target_prefix} cards to 「{target_month}月」 list ===")
    for i, card in enumerate(target_cards, start=1):
        pos = i * 10000
        trello_put(
            f"/cards/{card['id']}",
            {"idList": LIST_CURRENT_MONTH, "pos": str(pos)},
        )
        print(
            f"  [{i:2d}/{len(target_cards)}] pos={pos:>6} "
            f"due={card['due'][:10]} {card['name'][:40]}"
        )

    # === Step 3: 既存カードを最下部へ ===
    print(f"\n=== Step 3: Push existing 「{target_month}月」 cards to bottom ===")
    base_pos = (len(target_cards) + 1) * 10000
    for j, card in enumerate(existing_sorted, start=1):
        pos = base_pos + j * 10000
        trello_put(f"/cards/{card['id']}", {"pos": str(pos)})
        print(f"  [{j}/{len(existing_sorted)}] pos={pos:>6} {card['name'][:50]}")

    print("\n[DONE]")


if __name__ == "__main__":
    main(sys.argv)
