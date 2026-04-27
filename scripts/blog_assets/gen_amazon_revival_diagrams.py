"""gemini-3-pro-image-preview で Amazon在庫復活ポスト機能 記事の図解を生成するスクリプト

Usage:
    uv run python scripts/blog_assets/gen_amazon_revival_diagrams.py        # 全6枚生成
    uv run python scripts/blog_assets/gen_amazon_revival_diagrams.py 1      # 1枚目のみ
    uv run python scripts/blog_assets/gen_amazon_revival_diagrams.py 2 4    # 2,4枚目のみ

.env から GEMINI_API_KEY を読み込みます。
"""
from __future__ import annotations

import base64
import json
import os
import pathlib
import sys
import urllib.request

from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).resolve().parents[2] / ".env")

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-pro-image-preview"
ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
)

OUTPUT_DIR = pathlib.Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\03_機能仕様\Amazon在庫復活"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


DIAGRAMS = [
    {
        "filename": "diagram_01_overview_flow.png",
        "aspect": "16:9",
        "prompt": """Generate a clean Japanese infographic.
White background, flat design, modern professional style.

Title at top in large bold Japanese text: 「Amazon在庫復活ポスト 全体フロー」

Center: a horizontal flow chart with 6 steps connected by right arrows.
Each step is a rounded rectangle card with an icon + bold Japanese label:
Step 1 (navy, document icon): 「① ASIN登録」「監視対象を1行ずつ追加」
Step 2 (blue, globe icon): 「② Amazon商品ページ取得」「https://amazon.co.jp/dp/{ASIN}」
Step 3 (orange, magnifier icon): 「③ 3値分類で在庫判定」「在庫切れ／在庫あり／判定不能」
Step 4 (red, bell icon): 「④ 復活検知」「在庫切れ→在庫あり 遷移のみ発火」
Step 5 (purple, robot icon): 「⑤ Gemini AI生成」「5パターンからランダム選択」
Step 6 (green, send icon): 「⑥ X 自動投稿」「Playwright経由でツイート」

Bottom caption (small but readable): 「Keepa Plus・PA-API・Gmail OAuth すべて不要」

Style: horizontal flow chart, flat design, navy/blue/orange/red/purple/green color progression. Clean Japanese sans-serif typography. Large readable text. No clutter. 16:9 aspect ratio.""",
    },
    {
        "filename": "diagram_02_3reasons_free.png",
        "aspect": "16:9",
        "prompt": """Generate a clean Japanese infographic.
White background, flat design, modern professional style.

Title at top in large bold Japanese text: 「月額0円で運用できる3つの理由」

Center: 3 columns side by side, each is a tall rounded card with icon + headline + 2 bullet points.

Card 1 (blue, web icon, large「1」badge top-left):
- Headline: 「Amazon商品ページを直接取得」
- Bullet 1: 「公開URLなのでKeepa等の中間サービス不要」
- Bullet 2: 「1ASINあたり1秒前後・21時間遅延なし」

Card 2 (purple, sparkles AI icon, large「2」badge):
- Headline: 「Gemini 2.5-flash の広い無料枠」
- Bullet 1: 「1日数百件まで課金なし」
- Bullet 2: 「APIキー未設定でもテンプレでフォールバック」

Card 3 (green, recycle/reuse icon, large「3」badge):
- Headline: 「既存X投稿エンジンを流用」
- Bullet 1: 「Playwrightベースの投稿基盤を再利用」
- Bullet 2: 「新規依存ライブラリゼロ」

Bottom: a centered green pill banner with bold text: 「= 追加コスト ¥0 / 月」

Style: 3 column flat design infographic. Each card has subtle drop shadow. Bold Japanese sans-serif typography (large readable text). Blue / purple / green color scheme. 16:9 aspect ratio.""",
    },
    {
        "filename": "diagram_03_3class_judge.png",
        "aspect": "4:3",
        "prompt": """Generate a clean Japanese decision tree infographic.
White background, flat design, technical infographic style.

Title at top in bold Japanese: 「3値分類で誤検知ゼロ ― 在庫判定ロジック」

Top: a navy rounded rectangle: 「Amazon商品ページ取得」 with arrow down to: 「id=availability の primary-availability-message を抽出」 (light gray box)

Below: a vertical decision tree with 4 priority-ordered branches (numbered ①②③④):
① Red diamond: 「在庫切れ系キーワード？」 (例: 現在在庫切れ／入荷時期は未定／現在お取り扱いできません)
   → Yes: red box 「False (在庫切れ)」
② Green diamond: 「在庫あり系キーワード？」 (例: 在庫あり／残りN点／通常配送)
   → Yes: green box 「True (在庫あり)」
③ Yellow diamond: 「いずれにも一致しない？」
   → Yes: yellow box 「None (判定不能)」
④ Gray diamond: 「HTTP 取得失敗 (404/503)？」
   → Yes: gray box 「前回値を維持」

Right side annotation (red callout):
「在庫切れ系を最優先で判定 → 『再入荷をお待ちください』のような文に在庫ありキーワードが混ざっても誤検知しない」

Style: vertical decision tree, flat design. Red / green / yellow / gray color coding. Clean Japanese sans-serif typography. Bold readable text.""",
    },
    {
        "filename": "diagram_04_transition_matrix.png",
        "aspect": "4:3",
        "prompt": """Generate a clean Japanese matrix infographic.
White background, flat design, modern table style.

Title at top in bold Japanese: 「復活発火 遷移マトリクス ― 前回 × 今回」

Center: a 5×5 matrix table.
- Top-left corner: small label 「前回 ↓ ／ 今回 →」
- Column headers (top, navy bg, white text): 「在庫あり」 / 「在庫切れ」 / 「判定不能」 / 「取得失敗」
- Row headers (left, navy bg, white text): 「初回 (None)」 / 「在庫切れ (False)」 / 「在庫あり (True)」 / 「判定不能」

Cell contents (use bold large icons):
Row 「初回 (None)」:    🚀復活発火 / ⏸スキップ / ⏸スキップ / ⏸スキップ
Row 「在庫切れ (False)」: 🚀復活発火 / ⏸スキップ / ⏸スキップ / ⏸スキップ
Row 「在庫あり (True)」:  ⏸スキップ / ⏸スキップ / ⏸スキップ / ⏸スキップ
Row 「判定不能」:        ⏸スキップ / ⏸スキップ / ⏸スキップ / ⏸スキップ

Style:
- 復活発火 cells = bright red/orange highlighted background with rocket icon
- スキップ cells = light gray neutral background

Bottom annotation (small but readable):
「在庫切れ→在庫あり と 初回→在庫あり の2パターンだけ発火。HTTP失敗時は前回値を維持して偽通知防止」

Style: clean matrix table infographic. Flat design. Navy headers, red/orange highlight cells, gray neutral cells. Bold Japanese sans-serif typography. Large readable text.""",
    },
    {
        "filename": "diagram_05_5patterns.png",
        "aspect": "16:9",
        "prompt": """Generate a clean Japanese infographic.
White background, flat design, modern professional style.

Title at top in bold Japanese: 「AI生成5パターン ― 訴求軸を変えて反応率UP」

Center: a horizontal row of 5 colored cards, each card has a unique icon, pattern name, and example tagline.

Card 1 (blue, sparkle icon): 「① オリジナル」 — 「在庫復活🎉」を全面に
Card 2 (purple, question-mark icon): 「② 質問形式」 — 「待望の再入荷」+「こんな方に👇」
Card 3 (red, fire icon): 「③ セール訴求」 — 「緊急速報」「割引率OFF⚡️」
Card 4 (orange, scale/balance icon): 「④ 比較訴求」 — 「最安値↓現在価格」
Card 5 (green, news icon): 「⑤ 速報」 — 「速報 在庫復活‼️」

Above all 5 cards: a centered dice icon + arrow text: 「🎲 在庫復活ごとにランダム選択」

Bottom annotation:
「同じASINでも毎回違う切り口で投稿 → ROM専フォロワーにも飽きられない＋スパム判定回避」

Style: horizontal 5-column flat card layout, each card with subtle shadow and icon. Blue/purple/red/orange/green color scheme. Bold Japanese sans-serif typography. Large readable text. 16:9 aspect ratio.""",
    },
    {
        "filename": "diagram_06_compare_table.png",
        "aspect": "4:3",
        "prompt": """Generate a clean Japanese comparison table infographic.
White background, flat design, professional table style.

Title at top in bold Japanese: 「既存代替手段との比較 ― 6手段の特性」

Center: a 7-row × 5-column table.

Header row (navy background, white bold text):
「手段」 / 「コスト」 / 「リアルタイム性」 / 「設定難易度」 / 「EXE配布適性」

Data rows (left column = method name in bold):

Row 1 (entire row highlighted with gold/yellow background and a 「★おすすめ」 badge on the left):
「Amazon直接スクレイピング (本機能)」 / 「無料」 / 「数分〜」 / 「★☆☆」 / 「最適」

Row 2:
「Keepa RSS」 / 「月€19」 / 「即時」 / 「★☆☆」 / 「△ ユーザーに課金要求」

Row 3:
「Keepa商品ページHTML」 / 「無料」 / 「21時間遅延」 / 「★☆☆」 / 「△ 遅延が致命的」

Row 4:
「Amazon PA-API」 / 「無料」 / 「即時」 / 「★★★」 / 「× Associate売上実績必須」

Row 5:
「Gmail (Keepa通知)」 / 「無料」 / 「数分」 / 「★★★」 / 「× OAuth審査の壁」

Row 6:
「手動チェック」 / 「無料」 / 「人力次第」 / 「★☆☆」 / 「× 自動化されない」

Style guide:
- Header row: navy (#0B2545) background with white bold text
- Row 1 (本機能): gold/yellow (#FFE08A) background, with a small「★おすすめ」navy ribbon on the very left
- Other rows: alternating white / very light gray
- Cell text: bold readable Japanese
- 「最適」 in green, 「△」 in yellow/orange, 「×」 in red

Style: clean comparison table infographic. Flat design. Bold Japanese sans-serif typography. Large readable text. 4:3 aspect ratio.""",
    },
]


def gen(prompt: str, out_path: pathlib.Path, aspect: str) -> None:
    body = json.dumps(
        {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": aspect},
            },
        }
    ).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())
    for part in result["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            img_bytes = base64.b64decode(part["inlineData"]["data"])
            out_path.write_bytes(img_bytes)
            print(f"  saved: {out_path} ({len(img_bytes)} bytes)")
            return
    raise RuntimeError(f"no image in response: {json.dumps(result)[:500]}")


def main() -> None:
    if len(sys.argv) > 1:
        targets = [int(x) for x in sys.argv[1:]]
    else:
        targets = list(range(1, len(DIAGRAMS) + 1))

    print(f"Model: {MODEL}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Targets: {targets}")
    print()

    for i in targets:
        if not (1 <= i <= len(DIAGRAMS)):
            print(f"  skip: index {i} out of range")
            continue
        d = DIAGRAMS[i - 1]
        print(f"[{i}/{len(DIAGRAMS)}] {d['filename']}  aspect={d['aspect']}")
        out_path = OUTPUT_DIR / d["filename"]
        try:
            gen(d["prompt"], out_path, d["aspect"])
        except Exception as e:
            print(f"  ERR: {type(e).__name__}: {e}", file=sys.stderr)
        print()

    print("Done.")


if __name__ == "__main__":
    main()
