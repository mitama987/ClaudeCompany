"""Generate Brain article thumbnail via Gemini Images API (gemini-3-pro-image-preview).

Usage:
    uv run python gen_thumbnail.py

Writes PNG to the current directory and prints its absolute path.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

MODEL = "gemini-3-pro-image-preview"
ASPECT_RATIO = "16:9"  # Brain推奨 1280x670 ≒ 16:8.4 にほぼ一致

PROMPT = """
Create a horizontal sales-page header image (thumbnail) for a Japanese product.
Aspect ratio 16:9, very high resolution, professional tech-infographic style.

Background: rich gradient from dark navy (#0B1530) on the left to deep purple (#2A1257) on the right, with subtle digital grid lines and faint glowing particles for a high-tech feel.

Center-left text block (must render the Japanese characters EXACTLY as written, no romaji, no garbled characters):
  - Main headline (huge, bold white): 「XToolsPro3」
  - Sub headline 1 (medium, neon cyan #00E5FF): 「X(Twitter)自動投稿ツール」
  - Sub headline 2 (medium, neon cyan #00E5FF): 「複数アカウントも楽々管理」
Use a clean modern Japanese sans-serif typeface (Noto Sans JP / Meiryo style). Strong drop shadow on the headline so it pops on the dark background.

Right side visual:
  - A large stylized black "X" logo (post-Twitter rebrand style) with bright cyan and magenta neon edge glow.
  - Small floating tweet/post cards (rounded white rectangles with simple text lines and avatar dots) flying around the X, with thin glowing arrows that suggest scheduled, automated multi-account posting.
  - Subtle circuit-board lines and gear icons flowing into the X to imply automation.

Overall composition:
  - High contrast, sharp edges, vibrant neon highlights against the dark gradient.
  - No watermarks, no URLs, no small body paragraphs, no captions.
  - No English filler text; the only large text on the image is the three Japanese lines above.
  - Looks like a premium Japanese tech product header / Brain-style thumbnail.
""".strip()


def main() -> int:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY env var is not set", file=sys.stderr)
        return 2
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"
    )

    payload = json.dumps(
        {
            "contents": [{"role": "user", "parts": [{"text": PROMPT}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": ASPECT_RATIO},
            },
        }
    ).encode()

    print(f"Generating thumbnail with model={MODEL} aspectRatio={ASPECT_RATIO} ...", file=sys.stderr)
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTPError {e.code}: {body[:1000]}", file=sys.stderr)
        return 1

    parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            png = base64.b64decode(part["inlineData"]["data"])
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            out = Path(f"xtools_thumbnail_{ts}.png")
            out.write_bytes(png)
            print(out.resolve())
            return 0

    print(f"no image in response: {json.dumps(result)[:1000]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
