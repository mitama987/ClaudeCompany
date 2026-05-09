"""Final render: burn ASS subtitle + SFX cues + optional BGM onto cut.mp4."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def _probe_duration(path: str) -> float:
    res = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        capture_output=True, text=True, check=True,
    )
    return float(res.stdout.strip())


def render(
    cut_video: str = "video_editor/work/cut.mp4",
    ass_path: str = "video_editor/work/subtitle.ass",
    sfx_cues_path: str = "video_editor/work/sfx_cues.json",
    sfx_dir: str = "video_editor/sfx",
    bgm_dir: str = "video_editor/bgm",
    bgm_file: str | None = None,
    bgm_volume: float = 0.10,
    bgm_fade_in: float = 1.5,
    bgm_fade_out: float = 3.0,
    out_path: str = "video_editor/work/out.mp4",
    final_dest: str | None = None,
) -> Path:
    cues = json.loads(Path(sfx_cues_path).read_text(encoding="utf-8"))
    sfx_dir_p = Path(sfx_dir)
    bgm_dir_p = Path(bgm_dir)
    duration = _probe_duration(cut_video)

    def find_sfx(name: str) -> Path | None:
        for ext in (".mp3", ".wav", ".m4a", ".ogg"):
            p = sfx_dir_p / f"{name}{ext}"
            if p.is_file():
                return p
        return None

    bgm_path: Path | None
    if bgm_file:
        bgm_path = Path(bgm_file) if Path(bgm_file).is_absolute() else bgm_dir_p / bgm_file
        bgm_path = bgm_path if bgm_path.is_file() else None
    else:
        bgm_path = None
        if bgm_dir_p.is_dir():
            for pat in ("*.mp3", "*.m4a", "*.ogg", "*.wav"):
                matches = sorted(bgm_dir_p.glob(pat))
                if matches:
                    bgm_path = matches[0]
                    break

    inputs: list[str] = ["-i", cut_video]
    filter_parts: list[str] = []
    amix_inputs: list[str] = ["[0:a]"]

    idx = 1
    for cue in cues:
        sfx_file = find_sfx(cue["sfx"])
        if sfx_file is None:
            print(f"WARN: sfx '{cue['sfx']}' not found, skip", flush=True)
            continue
        inputs += ["-i", str(sfx_file)]
        delay_ms = int(cue["t"] * 1000)
        filter_parts.append(
            f"[{idx}:a]adelay={delay_ms}|{delay_ms},volume=0.55[sfx{idx}]"
        )
        amix_inputs.append(f"[sfx{idx}]")
        idx += 1

    if bgm_path is not None:
        inputs += ["-stream_loop", "-1", "-i", str(bgm_path)]
        fade_out_st = max(0.0, duration - bgm_fade_out)
        filter_parts.append(
            f"[{idx}:a]atrim=0:{duration},asetpts=N/SR/TB,"
            f"afade=t=in:st=0:d={bgm_fade_in},"
            f"afade=t=out:st={fade_out_st}:d={bgm_fade_out},"
            f"volume={bgm_volume}[bgm]"
        )
        amix_inputs.append("[bgm]")
        idx += 1
        print(f"BGM: {bgm_path.name} vol={bgm_volume}", flush=True)

    if len(amix_inputs) > 1:
        weights = " ".join(["1"] * (len(amix_inputs) - 1) + ["1"])
        filter_parts.append(
            f"{''.join(amix_inputs)}amix=inputs={len(amix_inputs)}:duration=first:normalize=0[aout]"
        )
        audio_map = ["-map", "0:v", "-map", "[aout]"]
    else:
        audio_map = ["-map", "0:v", "-map", "0:a"]

    ass_filter_path = ass_path.replace("\\", "/").replace(":", r"\:")
    vf = f"ass='{ass_filter_path}'"

    filter_complex = ";".join(filter_parts) if filter_parts else ""

    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        *inputs,
        "-vf", vf,
    ]
    if filter_complex:
        cmd += ["-filter_complex", filter_complex]
    cmd += [
        *audio_map,
        "-t", f"{duration}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        out_path,
    ]

    print("Running ffmpeg render...", flush=True)
    subprocess.run(cmd, check=True)

    out_p = Path(out_path)
    print(f"Wrote {out_p} ({out_p.stat().st_size/1024/1024:.1f} MB)")

    if final_dest:
        shutil.copy2(out_p, final_dest)
        print(f"Copied to {final_dest}")
    return out_p


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else None
    render(final_dest=dest)
