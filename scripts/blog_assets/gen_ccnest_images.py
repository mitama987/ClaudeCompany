"""ccnest紹介note記事用のサムネイル＋H2挿絵をGemini Image APIで一括生成する。

サムネ1枚 + H2挿絵7枚を並列で叩く。
出力先：C:/Users/mitam/Desktop/work/50_ブログ/images/ccnest_Claude_Code向けターミナル多重化ツール_generated/
"""

from __future__ import annotations

import base64
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API_KEY = "AIzaSyAAmWfDSIg_kTUAVJWteuphVDrPAL8AK6k"
MODEL = "gemini-3-pro-image-preview"
ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
)
OUT_DIR = Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\images\ccnest_Claude_Code向けターミナル多重化ツール_generated"
)
BASENAME = "ccnest_Claude_Code向けターミナル多重化ツール_generated"

THUMBNAIL_PROMPT = """情報商材スタイルのプロフェッショナルなブログサムネイル画像を作成してください。

【テーマ】Claude Code専用のターミナル多重化ツール「ccnest」の紹介。tmuxを置き換える次世代開発ツール。
【世界観】luxurious tech success, premium developer tool, futuristic terminal
【感情訴求】curiosity & excitement（好奇心＋興奮）

【三層構造レイアウト】
- 上段: 小さなリボン帯で「2026年最新版」と日本語表記（白抜き極太ゴシック）
- 中央: 最大の極太日本語タイポグラフィで「tmuxはもう要らない」（ゴールドのメタリックグラデーション、3D・ベベル加工、強い縁取り）。その下に少し小さく「ccnest」（白×電気青、3D）
- 下段: 暗いパネル帯の上に、3つの円形ゴールドバッジで横並び：左「設定不要」中央「1コマンド導入」右「Claude Code特化」（白の極太ゴシック）

【背景】dark navy and deep black base, golden particles, light streaks coming from the center, abstract digital energy waves, terminal-window silhouettes floating subtly in the background, glowing code-like patterns
【背景オブジェクト】floating glowing terminal panes overlapping like a multiplexer, with subtle Rust gear icon glowing in gold
【配色】base: black & deep navy, main: rich gold, accent: electric blue & white
【装飾】subtle golden laurel wreath partially around the center title, faint glowing particles, light flares
【アスペクト比】16:9 (1920x1080)
【全体トーン】premium tech, cinematic, high contrast, professional clickbait

日本語テキストは正確に描画してください。誤字・余計な文字・ローマ字混入は避けてください。"""

H2_HEADINGS = [
    {
        "n": 1,
        "title": "ccnestとは",
        "concept": "abstract scene of multiple floating terminal windows overlapping in a 3D space, glowing with code lines, suggesting a multiplexer concept, dark navy and gold, no text, no letters, no numbers, no words, cinematic lighting",
    },
    {
        "n": 2,
        "title": "ccnestを使うメリット",
        "concept": "abstract scene of golden checkmark badges floating upward, energy beams rising, suggesting benefits and advantages, dark navy and gold, no text, no letters, no numbers, no words, cinematic upward motion",
    },
    {
        "n": 3,
        "title": "ccnestの主な機能",
        "concept": "abstract scene of multiple glowing keyboard keys floating in space with connection lines like a circuit, suggesting features and capabilities, dark navy and gold with electric blue accents, no text, no letters, no numbers, no words",
    },
    {
        "n": 4,
        "title": "ccnestのデメリットと注意点",
        "concept": "abstract scene of warning triangles and caution markers softly glowing in a dark space, balanced composition suggesting honest disclosure, dark navy and amber-orange accents, no text, no letters, no numbers, no words, cinematic",
    },
    {
        "n": 5,
        "title": "tmuxやccmuxとの違い",
        "concept": "abstract scene of three contrasting glowing orbs side by side suggesting comparison between tools, with light streaks connecting and contrasting them, dark navy and gold, no text, no letters, no numbers, no words, professional",
    },
    {
        "n": 6,
        "title": "ccnestのインストール",
        "concept": "abstract scene of a single large upward arrow made of light, like a rocket trail or installation progress, energy bursting upward, dark navy and gold with electric blue, no text, no letters, no numbers, no words, dynamic motion",
    },
    {
        "n": 7,
        "title": "関連リンク・次のアクション",
        "concept": "abstract scene of an opening doorway of light leading to a brighter horizon, suggesting next steps and call to action, dark navy and warm gold, no text, no letters, no numbers, no words, cinematic invitation",
    },
]


def build_h2_prompt(concept: str) -> str:
    return f"""Create a 16:9 abstract blog illustration image with these specifications:

Style: Abstract, cinematic, professional blog illustration, dark theme
Mood: Premium, high-tech, motivational, sophisticated
Color palette: Black and deep navy base, rich gold main, white and electric blue accents
Composition: {concept}

Strict requirements:
- NO text, NO words, NO letters, NO numbers anywhere in the image
- Pure abstract illustration, symbolic and metaphorical
- 16:9 aspect ratio
- Cohesive with a black/navy + gold tech blog series
- High contrast, cinematic lighting, professional quality
- Subtle particles, light streaks, glow effects allowed
"""


def generate_one(prompt: str, output_path: Path, label: str) -> tuple[str, bool, str]:
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9"},
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read())
        for part in body["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                img = base64.b64decode(part["inlineData"]["data"])
                output_path.write_bytes(img)
                return (label, True, str(output_path))
        return (label, False, "no inlineData in response")
    except Exception as exc:
        return (label, False, f"{type(exc).__name__}: {exc}")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, str, Path]] = []
    jobs.append(
        (
            "thumbnail",
            THUMBNAIL_PROMPT,
            OUT_DIR / f"{BASENAME}_thumbnail.png",
        )
    )
    for h in H2_HEADINGS:
        jobs.append(
            (
                f"heading_{h['n']} ({h['title']})",
                build_h2_prompt(h["concept"]),
                OUT_DIR / f"{BASENAME}_heading_{h['n']}.png",
            )
        )

    print(f"Total jobs: {len(jobs)}")
    print(f"Output: {OUT_DIR}")
    print(f"Model: {MODEL}\n")

    results: list[tuple[str, bool, str]] = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        future_to_label = {
            ex.submit(generate_one, prompt, path, label): label
            for label, prompt, path in jobs
        }
        for fut in as_completed(future_to_label):
            label, ok, info = fut.result()
            status = "OK" if ok else "FAIL"
            print(f"[{status}] {label} -> {info}")
            results.append((label, ok, info))

    failed = [r for r in results if not r[1]]
    print(f"\nDone. Success: {len(results) - len(failed)} / {len(results)}")
    if failed:
        print("Failed jobs:")
        for label, _, info in failed:
            print(f"  - {label}: {info}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
