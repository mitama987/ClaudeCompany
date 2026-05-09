"""Whisper transcription with word-level timestamps."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    _sp = Path(sys.executable).parent.parent / "Lib" / "site-packages"
    for _pkg in ("cublas", "cudnn", "cuda_nvrtc"):
        _d = _sp / "nvidia" / _pkg / "bin"
        if _d.is_dir():
            os.add_dll_directory(str(_d))

from faster_whisper import WhisperModel


def format_srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main(audio_path: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    model = WhisperModel("large-v3", device="cuda", compute_type="float16")

    segments_iter, info = model.transcribe(
        audio_path,
        language="ja",
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 400},
        beam_size=5,
    )

    print(f"detected language: {info.language}, duration: {info.duration:.1f}s", flush=True)

    segments = []
    srt_lines: list[str] = []
    for idx, seg in enumerate(segments_iter, start=1):
        words = [
            {"start": w.start, "end": w.end, "text": w.word}
            for w in (seg.words or [])
        ]
        segments.append({
            "id": idx,
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
            "words": words,
        })
        srt_lines.append(str(idx))
        srt_lines.append(f"{format_srt_time(seg.start)} --> {format_srt_time(seg.end)}")
        srt_lines.append(seg.text.strip())
        srt_lines.append("")
        print(f"[{seg.start:7.2f} - {seg.end:7.2f}] {seg.text.strip()}", flush=True)

    (out / "transcript.json").write_text(
        json.dumps({"language": info.language, "duration": info.duration, "segments": segments}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "transcript.srt").write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"\nWrote {out/'transcript.json'} and {out/'transcript.srt'}")


if __name__ == "__main__":
    audio = sys.argv[1] if len(sys.argv) > 1 else "video_editor/work/audio16k.wav"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "video_editor/work"
    main(audio, outdir)
