"""Compute keep-segments from silent regions and render concat cut.

Trims each silent gap to a short pad (default 0.1s) to preserve breathing but
tighten the pace. Produces:
  work/segments.json : [{src_start, src_end, out_start, out_end}]
  work/concat.txt    : ffmpeg concat demuxer input
  work/cut.mp4       : concatenated output
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _merge(regions: list[dict]) -> list[dict]:
    sorted_r = sorted(regions, key=lambda r: r["start"])
    merged: list[dict] = []
    for r in sorted_r:
        if merged and r["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], r["end"])
        else:
            merged.append({"start": r["start"], "end": r["end"]})
    return merged


def build_segments(
    silences: list[dict],
    total_duration: float,
    keep_pad: float = 0.1,
    min_segment: float = 0.2,
) -> list[dict]:
    """Turn silent regions into keep-segments (src_start, src_end)."""
    silences = _merge(silences)
    keep: list[tuple[float, float]] = []
    prev_end = 0.0
    for s in silences:
        s_start = max(prev_end, s["start"] + keep_pad / 2)
        s_end = s["end"] - keep_pad / 2
        if s_start > prev_end:
            keep.append((prev_end, s_start))
        prev_end = max(prev_end, s_end)
    if prev_end < total_duration:
        keep.append((prev_end, total_duration))

    segments: list[dict] = []
    out_cursor = 0.0
    for a, b in keep:
        if b - a < min_segment:
            continue
        segments.append({
            "src_start": round(a, 3),
            "src_end": round(b, 3),
            "out_start": round(out_cursor, 3),
            "out_end": round(out_cursor + (b - a), 3),
        })
        out_cursor += b - a
    return segments


def render_cut(src_video: str, segments: list[dict], work_dir: Path) -> Path:
    """Single-pass cut using select/aselect filters.

    Keeps frame-accurate PTS continuity across the whole video — no concat
    boundary errors. Uses setpts/asetpts to renumber PTS on the kept frames.
    """
    cond = "+".join(
        f"between(t,{s['src_start']:.4f},{s['src_end']:.4f})" for s in segments
    )
    cut_out = work_dir / "cut.mp4"

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", src_video,
        "-vf", f"select='{cond}',setpts=N/FRAME_RATE/TB",
        "-af", f"aselect='{cond}',asetpts=N/SR/TB",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-video_track_timescale", "30000",
        str(cut_out),
    ]
    print(f"ffmpeg 1-pass cut: {len(segments)} segments", flush=True)
    subprocess.run(cmd, check=True)
    return cut_out


def main():
    src_video = sys.argv[1] if len(sys.argv) > 1 else "video_editor/work/master_1080p.mp4"
    silences_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("video_editor/work/silences.json")
    work_dir = Path("video_editor/work")

    silences = json.loads(silences_path.read_text(encoding="utf-8"))

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", src_video],
        capture_output=True, text=True, check=True,
    )
    total = float(probe.stdout.strip())

    segs = build_segments(silences, total)
    (work_dir / "segments.json").write_text(
        json.dumps(segs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    kept = sum(s["src_end"] - s["src_start"] for s in segs)
    print(f"{len(segs)} segments, {kept:.1f}s kept / {total:.1f}s ({(1 - kept/total)*100:.1f}% cut)")

    out = render_cut(src_video, segs, work_dir)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
