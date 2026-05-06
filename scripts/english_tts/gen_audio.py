"""英語学習プロジェクト用 OpenAI TTS ラッパー.

入力:  .company/english/scripts/NN-xxx.en.md
出力:  .company/english/audio/NN-xxx.mp3              (フル音声 1.0x)
       .company/english/audio/NN-xxx_0.75x.mp3
       .company/english/audio/NN-xxx_0.5x.mp3
       .company/english/audio/NN-xxx/bMM-slug.mp3      (ブロック分割 1.0x)
       .company/english/audio/NN-xxx/bMM-slug_0.75x.mp3
       .company/english/audio/NN-xxx/bMM-slug_0.5x.mp3

声 alloy 固定。速度は SPEEDS タプル (1.0, 0.75, 0.5) を全部生成する.

ブロック分割:
    .en.md 内に `<!-- BLOCK 01: Title -->` のマーカーを置くと、
    マーカー間のテキストを1ブロックとして個別 mp3 を生成する.
    マーカーが1つも無ければフルmp3だけ生成する.

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
AUDIO_DIR = ROOT / ".company" / "english" / "audio"

VOICE = "alloy"
SPEEDS: tuple[float, ...] = (1.0, 0.75, 0.5)
MODEL = "gpt-4o-mini-tts"
RESPONSE_FORMAT = "mp3"

BLOCK_RE = re.compile(r"<!--\s*BLOCK\s+(\d+):\s*(.+?)\s*-->", re.IGNORECASE)


def discover_topics() -> list[Path]:
    return sorted(SCRIPTS_DIR.glob("*.en.md"))


def find_topic_file(topic_id: str) -> Path | None:
    matches = list(SCRIPTS_DIR.glob(f"{topic_id}-*.en.md"))
    if not matches:
        return None
    if len(matches) > 1:
        raise SystemExit(f"複数の候補が見つかりました: {matches}")
    return matches[0]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "block"


def clean_for_speech(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    cleaned: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        cleaned.append(line)
    out = "\n".join(cleaned).strip()
    return re.sub(r"\n{3,}", "\n\n", out)


def parse_blocks(body: str) -> list[tuple[int, str, str]]:
    matches = list(BLOCK_RE.finditer(body))
    if not matches:
        return []
    blocks: list[tuple[int, str, str]] = []
    for i, m in enumerate(matches):
        num = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        blocks.append((num, title, body[start:end]))
    return blocks


def speed_suffix(speed: float) -> str:
    if speed == 1.0:
        return ""
    return f"_{speed:g}x"


def synthesize(client: OpenAI, text: str, out_path: Path, speed: float) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice=VOICE,
        speed=speed,
        response_format=RESPONSE_FORMAT,
        input=text,
    ) as response:
        response.stream_to_file(out_path)


def emit_at_speeds(
    text: str,
    parent: Path,
    stem: str,
    label: str,
    client: OpenAI,
    force: bool,
) -> None:
    if not text:
        print(f"[warn] {label} のテキストが空です")
        return
    for speed in SPEEDS:
        out_path = parent / f"{stem}{speed_suffix(speed)}.mp3"
        if out_path.exists() and not force:
            print(f"[skip] {out_path.relative_to(ROOT)} (exists)")
            continue
        print(f"[tts ] {label} @{speed:g}x -> {out_path.relative_to(ROOT)} ({len(text)} chars)")
        synthesize(client, text, out_path, speed)
        print(f"[done] {out_path.relative_to(ROOT)}")


def process(md_path: Path, client: OpenAI, force: bool) -> None:
    post = frontmatter.load(md_path)
    body = post.content
    base = md_path.name.removesuffix(".en.md")

    full_text = clean_for_speech(body)
    emit_at_speeds(full_text, AUDIO_DIR, base, f"full {base}", client, force)

    blocks = parse_blocks(body)
    if not blocks:
        return

    block_dir = AUDIO_DIR / base
    for num, title, raw_block in blocks:
        block_text = clean_for_speech(raw_block)
        slug = slugify(title)
        stem = f"b{num:02d}-{slug}"
        emit_at_speeds(block_text, block_dir, stem, f"b{num:02d} {title}", client, force)


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
