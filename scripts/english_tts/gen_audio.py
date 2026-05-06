"""英語学習プロジェクト用 OpenAI TTS ラッパー.

入力:  .company/english/scripts/NN-xxx.en.md
出力:  outputs/english/audio/NN-xxx.mp3

声・速度はプロジェクト方針で固定 (alloy / 1.0).

使い方:
    uv run python scripts/english_tts/gen_audio.py --topic 01
    uv run python scripts/english_tts/gen_audio.py --topic 01 02 03
    uv run python scripts/english_tts/gen_audio.py --all
    uv run python scripts/english_tts/gen_audio.py --topic 01 --force
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import frontmatter
from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / ".company" / "english" / "scripts"
AUDIO_DIR = ROOT / "outputs" / "english" / "audio"

VOICE = "alloy"
SPEED = 1.0
MODEL = "gpt-4o-mini-tts"
RESPONSE_FORMAT = "mp3"


def discover_topics() -> list[Path]:
    return sorted(SCRIPTS_DIR.glob("*.en.md"))


def find_topic_file(topic_id: str) -> Path | None:
    matches = list(SCRIPTS_DIR.glob(f"{topic_id}-*.en.md"))
    if not matches:
        return None
    if len(matches) > 1:
        raise SystemExit(f"複数の候補が見つかりました: {matches}")
    return matches[0]


def extract_speech_text(md_path: Path) -> str:
    """Markdown から音声化対象のテキストを抽出する.

    - frontmatter (---) は除外
    - h1/h2 などの見出し行 (#で始まる行) は除外
    - 空行は段落区切りとして残す
    - HTMLコメントは削除
    """
    post = frontmatter.load(md_path)
    body = post.content

    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)

    cleaned_lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def synthesize(client: OpenAI, text: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice=VOICE,
        speed=SPEED,
        response_format=RESPONSE_FORMAT,
        input=text,
    ) as response:
        response.stream_to_file(out_path)


def process(md_path: Path, client: OpenAI, force: bool) -> None:
    out_path = AUDIO_DIR / f"{md_path.stem.removesuffix('.en')}.mp3"

    if out_path.exists() and not force:
        print(f"[skip] {out_path.relative_to(ROOT)} (exists, use --force)")
        return

    text = extract_speech_text(md_path)
    if not text:
        print(f"[warn] {md_path.relative_to(ROOT)} に音声化対象テキストがありません")
        return

    print(f"[tts ] {md_path.relative_to(ROOT)} -> {out_path.relative_to(ROOT)} ({len(text)} chars)")
    synthesize(client, text, out_path)
    print(f"[done] {out_path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenAI TTS for English learning scripts")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--topic", nargs="+", help="トピック番号 (例: 01) を1つ以上")
    group.add_argument("--all", action="store_true", help="全トピックを処理")
    parser.add_argument("--force", action="store_true", help="既存mp3を上書き")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY が見つかりません (.env または環境変数)", file=sys.stderr)
        return 1

    client = OpenAI(api_key=api_key)

    if args.all:
        targets = discover_topics()
    else:
        targets = []
        for topic_id in args.topic:
            normalized = topic_id.zfill(2)
            md_path = find_topic_file(normalized)
            if md_path is None:
                print(f"[warn] topic {normalized} のスクリプトが見つかりません", file=sys.stderr)
                continue
            targets.append(md_path)

    if not targets:
        print("対象スクリプトがありません", file=sys.stderr)
        return 1

    for md_path in targets:
        process(md_path, client, force=args.force)

    return 0


if __name__ == "__main__":
    sys.exit(main())
