"""Detect silent regions with ffmpeg silencedetect."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def detect(input_path: str, noise_db: str = "-30dB", min_silence: float = 0.4) -> list[tuple[float, float]]:
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats",
        "-i", input_path,
        "-af", f"silencedetect=noise={noise_db}:d={min_silence}",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = res.stderr

    events = re.findall(r"silence_(start|end):\s*([0-9.]+)", out)
    regions: list[tuple[float, float]] = []
    cur_start: float | None = None
    for kind, t_s in events:
        t = float(t_s)
        if kind == "start":
            cur_start = t
        else:
            regions.append((cur_start if cur_start is not None else 0.0, t))
            cur_start = None
    return regions


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "video_editor/work/master_1080p.mp4"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("video_editor/work/silences.json")
    noise_db = sys.argv[3] if len(sys.argv) > 3 else "-30dB"
    min_sil = float(sys.argv[4]) if len(sys.argv) > 4 else 0.4

    regions = detect(src, noise_db, min_sil)
    out.write_text(json.dumps([{"start": s, "end": e} for s, e in regions], indent=2), encoding="utf-8")
    print(f"Found {len(regions)} silent regions (>= {min_sil}s, {noise_db}). Written {out}")
    for s, e in regions[:10]:
        print(f"  silent {s:7.2f}-{e:7.2f} ({e-s:.2f}s)")
    if len(regions) > 10:
        print(f"  ... and {len(regions)-10} more")


if __name__ == "__main__":
    main()
