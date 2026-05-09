"""Expand silence regions with filler/breath word spans from transcript.

Detects short filler words (あー, えー, ...) and breath sounds (すー, ハー, ...)
from Whisper's word-level timestamps and merges their spans into silences.json
so build_cuts will remove them.
"""
from __future__ import annotations

import json
from pathlib import Path


FILLERS: set[str] = {
    # 長音付き・明確なフィラーのみ（単音は誤爆するので除外）
    "あー", "えー", "うー", "んー", "おー", "あぁ", "えぇ",
    "えっと", "えーっと", "えーと", "えと",
    "あのー", "あのう", "あのお",
    "まあ", "まぁ", "まー", "まぁー",
    "そのー",
    "なんかー",
    # 呼吸音（長音記号ありで明確なもの）
    "すー", "スー", "ハー", "はー", "はぁ", "ふぅ", "ふー",
}

TRIM_CHARS = " 　、。,.!?！？「」『』…・"


def is_filler(text: str) -> bool:
    return text.strip(TRIM_CHARS) in FILLERS


def main(
    transcript: str = "video_editor/work/transcript.json",
    silences: str = "video_editor/work/silences.json",
    max_word_duration: float = 0.8,
) -> None:
    data = json.loads(Path(transcript).read_text(encoding="utf-8"))
    regions = json.loads(Path(silences).read_text(encoding="utf-8"))
    before = len(regions)

    hits: list[tuple[float, float, str]] = []
    for seg in data["segments"]:
        for w in seg["words"]:
            if not is_filler(w["text"]):
                continue
            if w.get("start") is None or w.get("end") is None:
                continue
            s, e = float(w["start"]), float(w["end"])
            if e <= s or (e - s) > max_word_duration:
                continue
            hits.append((s, e, w["text"].strip()))

    for s, e, _ in hits:
        regions.append({"start": s, "end": e})

    Path(silences).write_text(
        json.dumps(regions, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Fillers cut: {len(hits)}  (silences: {before} -> {len(regions)})")


if __name__ == "__main__":
    main()
