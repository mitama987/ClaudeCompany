"""Generate 3 diagrams for the X API pricing update note article using Gemini API."""
from __future__ import annotations

import base64
import json
import urllib.request
from pathlib import Path

API_KEY = "AIzaSyAAmWfDSIg_kTUAVJWteuphVDrPAL8AK6k"
MODEL = "gemini-3-pro-image-preview"
ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
)

OUT = Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_LP・販売記事\_attachments\20260418_XAPI改定"
)
OUT.mkdir(parents=True, exist_ok=True)


def gen(prompt: str, out_path: Path, aspect_ratio: str = "16:9") -> None:
    data = json.dumps(
        {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": aspect_ratio},
            },
        }
    ).encode()
    req = urllib.request.Request(
        ENDPOINT, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())
    for part in result["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            img = base64.b64decode(part["inlineData"]["data"])
            out_path.write_bytes(img)
            print(f"saved: {out_path}")
            return
    raise RuntimeError(f"no image in response: {json.dumps(result)[:500]}")


PROMPT_01 = """
Create a clean Japanese-language infographic titled「X API 大改定 2026/4/20 施行 ― 3つの大きな柱」.
Subtitle: 「2026-04-17 X Developer Platform Team 発表」

Layout: 3 vertical cards side by side on white background, each with a colored rounded border and a badge in the upper right corner.

Card 1 (green border, border color #17BF63):
- Number badge (top left): circled「1」white-on-green
- Badge (top right, green pill): 「値下げ」
- Title (green, large bold):「読み取り 激安化」
- Subtitle (dark):「Owned Reads が $0.001/req に」
- 4 bullet points (with・prefix, Japanese):
  ・1,000リクエスト=$1
  ・自分のツイート/フォロワー
  ・/いいね/ブックマーク 等
  ・「吸い出し系」ほぼ無料圏

Card 2 (red/magenta border, border color #E0245E):
- Number badge (top left): circled「2」white-on-red
- Badge (top right, red pill): 「値上げ」
- Title (red, large bold):「投稿 値上げ」
- Subtitle (dark):「プレーン$0.015 / URL付き$0.20」
- 4 bullet points:
  ・プレーン +50% ($0.01→$0.015)
  ・URL付き +1,900% (20倍)
  ・100本/日・URL付きなら
  ・月 約97,200円 コース

Card 3 (orange border, border color #F4A261):
- Number badge (top left): circled「3」white-on-orange
- Badge (top right, orange pill): 「機能削除」
- Title (orange, large bold):「書込み系 廃止」
- Subtitle (dark):「API書込みがSelf-Serveから消滅」
- 4 bullet points:
  ・自動フォロー/アンフォロー
  ・自動いいね
  ・引用RT (quote_tweet_id)
  ・Self-Serveでは今後不可

Footer (italic gray):「1ドル=162円（2026-04-01 手数料込レート） / 月30日換算」

Style: flat design, clean sans-serif Japanese typography (Noto Sans JP / Meiryo style),
white background (#FFFFFF), card backgrounds light gray (#F5F8FA). Use exact Japanese characters provided. High quality, 16:9 infographic, no decorative illustrations — purely typographic card layout.
"""

PROMPT_02 = """
Create a clean Japanese-language infographic bar chart.

Title (bold, centered):「POST /2/tweets の単価 Before / After ― URL付きは20倍の衝撃」

X-axis categories (2 groups):「プレーン投稿」「URL付き投稿」
Y-axis label:「1投稿あたりの単価 (USD)」, range 0 to 0.25

For each category, show two vertical bars side by side:
- Gray bar = 旧料金 (〜2026/4/19)
- Blue/red bar = 新料金 (2026/4/20〜)

Data:
Group 1「プレーン投稿」:
  - Gray bar height 0.010, labeled「$0.010」above the bar
  - Blue bar (#1DA1F2) height 0.015, labeled「$0.015」above, and「+50%」label above that in blue bold

Group 2「URL付き投稿」:
  - Gray bar height 0.010, labeled「$0.010」above the bar
  - Red/pink bar (#E0245E) height 0.200, labeled「$0.200」above, and「20倍 (+1,900%)」label above that in red bold

Legend (upper left):
  ▪ 旧料金 (〜2026/4/19) in gray
  ▪ 新料金 (2026/4/20〜) in color

Add a subtle arrow from the URL付き gray bar up to the URL付き red bar showing the dramatic jump.

Style: clean flat infographic, white background, horizontal grid lines, professional. No extra decorations. 16:9 aspect. Use exact Japanese characters as specified. Numbers must be rendered precisely as shown.
"""

PROMPT_03 = """
Create a Japanese-language infographic bar chart.

Title (bold, centered):「月額コスト試算 ― 投稿本数 × プレーン/URL付き (1USD=162円, 月30日換算)」
Subtitle (slightly smaller, centered):「1ヶ月のAPI投稿コスト」

X-axis:「10本/日」「50本/日」「100本/日」
Y-axis:「月額コスト (円)」, formatted with thousands commas (e.g., 40,000), range 0 to about 110,000

Bars (side-by-side pairs for each category):
- 10本/日: blue #1DA1F2 bar = 約729円 ($4.50) / red #E0245E bar = 約9,720円 ($60.00)
- 50本/日: blue bar = 約3,645円 ($22.50) / red bar = 約48,600円 ($300.00)
- 100本/日: blue bar = 約7,290円 ($45.00) / red bar = 約97,200円 ($600.00)

Labels above each bar: 2 lines, "約XXX円" on top, "($XX.XX)" on bottom, in the matching bar color bold.
Legend top-left (the legend text must be EXACTLY as shown below, do not add color names or hex codes):
▪ プレーン投稿
▪ URL付き投稿
(Use blue #1DA1F2 for プレーン, red #E0245E for URL付き as bar colors only — not in the label text)

Callout box (light peach background #FFF4E6, orange border #F4A261), placed in upper right area of the chart:
「URL付き100本/日 なら
月 約97,200円 (約13倍) に」

Style: clean flat infographic, white background, horizontal grid lines, clean Japanese sans-serif typography, professional. Single chart filling the frame (no second chart). 16:9 aspect ratio. All Japanese characters must be rendered exactly. Numbers formatted precisely as shown.
"""


PROMPT_04 = """
Create a clean Japanese-language infographic titled「戦略A｜プロフィールURL誘導型（1アカウント運用）」.

Layout: A flow diagram on white background, showing a single X (Twitter) account运用 flow:

LEFT SIDE - X Account card (blue #1DA1F2 border, rounded rectangle):
- Top: icon/avatar placeholder + handle「@main_account」 (simple circle + @handle text)
- Middle: 「プロフィール欄」 section with a small URL chip showing「🔗 https://your-lp.com」in a highlighted blue box labeled「誘導先URLはプロフィールに1箇所だけ」
- Below: 3 tweet cards stacked, each labeled「プレーン投稿（URLなし）」with body text like 「○○について解説します！詳細はプロフへ！」「✅ ポイント3つまとめ 詳しくはプロフのリンクから」「今日のTIP！ 続きはプロフへ👆」

CENTER - Arrow flow pointing right:
- A big curved/bent arrow labeled「読者がプロフへ飛ぶ」 going from posts to the profile URL chip, then from profile URL chip to the right side

RIGHT SIDE - Destination card (green #17BF63 border):
- Title:「誘導先（LP / note / LINE公式）」
- Content preview silhouette

BOTTOM badges (green checkmark pills, arranged horizontally):
✅ URL付き投稿ゼロ
✅ API料金 月 約7,290円まで（100本/日プレーン）
✅ 垢バンリスク最小化
✅ 1アカウントで完結

Footer note (small gray):「デメリット: 1クリック余計にかかるのでCVは若干落ちる。プロフの誘導コピーで補う」

Style: flat design, clean sans-serif Japanese typography (Meiryo / Noto Sans JP style), white background (#FFFFFF), soft rounded corners, professional infographic. No decorative illustrations — typographic + simple geometric shapes only. 16:9 aspect ratio. Japanese characters must be rendered exactly as shown.
"""

PROMPT_05 = """
Create a clean Japanese-language infographic titled「戦略B｜アシスタントアカウント返信型（2アカウント運用）」.

Layout: A flow diagram on white background, showing TWO X (Twitter) accounts in a parent-reply relationship:

TOP - Main account card (blue #1DA1F2 border):
- Icon circle + handle「@main_account（本アカウント）」
- Tweet card label「プレーン投稿（URLなし）」with body: 「○○についてまとめました！詳細はアシスタントの返信をご覧ください！👇」
- Green badge: 「URL付き投稿ゼロ → クリーンを維持」

A curved「リプライでぶら下がる」arrow going downward from main tweet to the reply.

BOTTOM - Assistant account reply card (orange #F4A261 border, visually indented to the right to show it's a reply):
- Icon circle + handle「@assistant_sub（アシスタント）」
- Small「↳ 返信」 indicator
- Tweet card label「URL付きリプライ」with body:「詳細はこちら → https://your-lp.com」
- Orange badge:「URLはここだけ」

RIGHT - Destination card (green #17BF63 border):
- Title:「誘導先（LP / note / LINE公式）」
- Arrow from URL in reply to this card
- Label on arrow:「リプから直接URLへ」

BOTTOM badges (two columns):
Left column (green checkmarks):
✅ 本アカウントはクリーン
✅ 導線が同一タイムライン内で完結
✅ フォロワー資産を守りやすい

Right column (orange warnings):
⚠ 2アカウント管理が必要
⚠ アシスタント側はURL料金/バンリスクあり（本数は大幅に絞れる）

Footer note (small gray):「向いている人: 既にサブアカウントを持っている / 本アカの凍結ダメージが大きい」

Style: flat design, clean sans-serif Japanese typography (Meiryo / Noto Sans JP style), white background (#FFFFFF), soft rounded corners, professional infographic. Keep the two accounts visually distinct (blue for main, orange for assistant). Tweet cards should look like X/Twitter tweet cards (rounded rectangle with handle + body text). 16:9 aspect ratio. Japanese characters must be rendered exactly as shown.
"""


def main() -> None:
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("all", "1"):
        gen(PROMPT_01, OUT / "diagram_01_xapi_summary.png")
    if target in ("all", "2"):
        gen(PROMPT_02, OUT / "diagram_02_xapi_write_pricing.png")
    if target in ("all", "3"):
        gen(PROMPT_03, OUT / "diagram_03_xapi_monthly_cost.png")
    if target in ("all", "4"):
        gen(PROMPT_04, OUT / "diagram_04_strategy_a_profile_url.png")
    if target in ("all", "5"):
        gen(PROMPT_05, OUT / "diagram_05_strategy_b_assistant_reply.png")
    print(f"done ({target}).")


if __name__ == "__main__":
    main()
