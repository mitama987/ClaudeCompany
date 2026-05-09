"""gemini-3-pro-image-preview で X凍結祭り記事の図解を生成するスクリプト

Usage:
    uv run python gen_x_freeze_diagrams.py        # 全4枚生成
    uv run python gen_x_freeze_diagrams.py 1      # 1枚目のみ
    uv run python gen_x_freeze_diagrams.py 2 4    # 2,4枚目のみ

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
    r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\02_ナレッジ\X凍結・BAN"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


DIAGRAMS = [
    {
        "filename": "diagram_01_凍結条件マトリクス.png",
        "aspect": "1:1",
        "prompt": """Generate a clean Japanese infographic.
White background, flat design, modern professional style.

Title at top in large bold Japanese text: 「2026年4月 X凍結条件マトリクス」

Center: a vertical table with 5 rows. Each row has a condition label (left) and a verdict mark (right). Use red ✗ for "それでも凍結" and yellow ? for unverified.
Row 1: 「稼働年数（1年〜2ヶ月）」 — 赤×「それでも凍結」
Row 2: 「プロキシ使用」 — 赤×「それでも凍結」
Row 3: 「投稿量（1日10〜150ポスト）」 — 赤×「それでも凍結」
Row 4: 「公式API使用」 — 赤×「それでも凍結」
Row 5: 「投稿内容の類似性」 — 黄?「未検証・鍵の可能性」

Bottom: a green arrow pointing down with bold text 「→ 投稿内容こそが鍵」

Style: navy / red / yellow / green flat color scheme. Sans-serif Japanese typography. Clean, infographic style. No clutter.""",
    },
    {
        "filename": "diagram_02_クラスタリング間引き仮説.png",
        "aspect": "1:1",
        "prompt": """Generate a clean Japanese concept diagram.
White background, flat design, network/cluster visualization.

Title at top in bold Japanese: 「クラスタリング＋間引き仮説」

Three columns with arrows:
Left column label「Step 1: 多数のアカウント」: 12 small avatar icons (mix of shapes representing different accounts, scattered).
Middle column label「Step 2: 投稿内容で同種をクラスタリング」: same icons grouped into 3 colored circles (cluster 1: red, cluster 2: blue, cluster 3: green). Arrow from left to middle.
Right column label「Step 3: クラスタ内で相対評価 → 上位以外を凍結」: same 3 clusters but each cluster shows 1-2 icons with green ✓ (残す) and the rest with red ✗ (凍結). Arrow from middle to right.

Bottom caption: 「同条件でも凍結される/されないの差は、クラスタ内の相対順位で決まる」

Style: flat design, clean infographic, network visualization. Navy, red, blue, green color scheme. Sans-serif Japanese typography.""",
    },
    {
        "filename": "diagram_03_URL付投稿の価格差.png",
        "aspect": "4:3",
        "prompt": """Generate a clean Japanese comparison infographic.
White background, flat design, side-by-side comparison style.

Title at top in bold Japanese: 「X API 価格改定（2026-04-20）— プレーン vs URL付」

Two large vertical panels side by side:
LEFT PANEL (green theme): Top label 「プレーンポスト」. Center huge text 「$0.015 / 件」 in green. Below: small icon of a text-only post (speech bubble with text lines).
RIGHT PANEL (red theme): Top label 「URL付ポスト」. Center huge text 「$0.2 / 件」 in red. Below: small icon of a post with link (speech bubble with text + link icon).

Between the two panels, a large yellow circular badge with bold text 「13倍差」.

Bottom horizontal banner: 「→ URL付投稿は X 側から重点監視されている可能性」

Style: clean comparison infographic, large readable Japanese text, flat design. Green / red / yellow color accents on white.""",
    },
    {
        "filename": "diagram_04_異議申し立て3回フロー.png",
        "aspect": "3:4",
        "prompt": """Generate a clean Japanese vertical flow diagram.
White background, flat design, sequential step-by-step infographic.

Title at top in bold Japanese: 「異議申し立て継続返信フロー（最大3回）」

5 vertical numbered cards connected by down-arrows:

Card 1 (red, locked icon): 「① 凍結／永久凍結通達が届く」
Down arrow with label「AIで英語の異議申し立て文を作成」
Card 2 (orange, mail icon): 「② 1回目の返信を送る」
Down arrow with label「却下メール / 永久凍結通達が返ってくる」
Card 3 (orange, mail icon): 「③ 同じメールに2回目の返信」
Down arrow with label「再度却下されても諦めない」
Card 4 (orange, mail icon): 「④ 3回目の返信」
Down arrow with green checkmark
Card 5 (green, unlocked icon): 「⑤ アカウント解除」

Right side annotations:
- Next to Card 1: 「『このアカウントは復活できません』と書かれていても諦めない」
- Next to Card 5: 「2026-04-19 頃から解除発出フェーズ」

Style: vertical flow chart, professional infographic. Red → orange → green color progression. Clean Japanese typography.""",
    },
    {
        "filename": "thumbnail_X凍結祭り.png",
        "aspect": "16:9",
        "prompt": """Generate a clean Japanese-language note article thumbnail. 16:9 aspect ratio, modern flat infographic style, white to very light gray background.

Top half:
- Large bold Japanese title (top-center, 2 lines):
  Line 1: 「【2026年4月】X凍結祭り現場レポート」
  Line 2 (slightly smaller, navy): 「判明した条件・復活術・新型シャドウバン対策」
- Title in deep navy color (#0B2545), very thick sans-serif typography (Noto Sans JP / Meiryo style), high readability.

Bottom half:
- A horizontal row of 5 small condition pills (rounded rectangles), each with an icon and a short Japanese label:
  Pill 1 (red ✗): 「稼働年数」
  Pill 2 (red ✗): 「プロキシ」
  Pill 3 (red ✗): 「投稿量」
  Pill 4 (red ✗): 「公式API」
  Pill 5 (yellow ?): 「投稿内容?」
- Below the pills, centered, a single bold green arrow pointing right with bold Japanese text:
  「→ 投稿内容こそが鍵」

Style:
- Flat infographic, navy / red / yellow / green color scheme
- Clean Japanese sans-serif typography, large readable text
- No clutter, designed to stand out in note.com timeline
- 16:9 aspect ratio, web-quality
- Title text MUST be readable and accurate Japanese characters""",
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
