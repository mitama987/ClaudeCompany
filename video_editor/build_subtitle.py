"""Build ASS subtitle from Whisper word-level timestamps.

For each word, find the keep-range (from segments.json) it falls inside;
group contiguous mapped words into a single subtitle event. This guarantees
that captions appear exactly while the words are being spoken, and that
words cut out by silence/filler removal are dropped from the caption too.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pysubs2


# ---------- normalization ----------

_PRODUCT_PATTERNS = [
    (re.compile(r"X[-\s]*[Tt]ools?\s*Pro(?:\s*\d+)?", re.IGNORECASE), "XToolsPro3"),
    (re.compile(r"Excel\s*Pro(?:\s*\d+)?", re.IGNORECASE), "XToolsPro3"),
    (re.compile(r"[xXｘＸ]ツール[スズ]?プロ\s*[0-9０-９]*"), "XToolsPro3"),
    (re.compile(r"エックス[・ 　]?ツール[スズ]?プロ\s*[0-9０-９]*"), "XToolsPro3"),
]


def normalize_product(text: str) -> str:
    for pat, rep in _PRODUCT_PATTERNS:
        text = pat.sub(rep, text)
    return text


def wrap_two_lines(text: str, max_chars: int = 18) -> str:
    t = text.strip()
    if len(t) <= max_chars:
        return t
    mid = len(t) // 2
    for delta in range(0, len(t)):
        for i in (mid - delta, mid + delta):
            if 0 < i < len(t) and t[i] in "、。， 　":
                return t[: i + 1].rstrip() + r"\N" + t[i + 1 :].lstrip()
    return t[:mid] + r"\N" + t[mid:]


# ---------- keep-range mapping ----------

def _find_keep(src_t: float, keeps: list[dict]) -> dict | None:
    for k in keeps:
        if k["src_start"] <= src_t <= k["src_end"]:
            return k
    return None


def _map_word(w: dict, keeps: list[dict]) -> tuple[float, float] | None:
    """Map a word's src-timeline [start,end] to cut-timeline, dropping if it
    crosses a cut boundary."""
    ws = w.get("start")
    we = w.get("end")
    if ws is None or we is None or we <= ws:
        return None
    k = _find_keep(ws, keeps)
    if k is None or we > k["src_end"]:
        return None
    return (
        k["out_start"] + (ws - k["src_start"]),
        k["out_start"] + (we - k["src_start"]),
    )


# ---------- event grouping ----------

def _group_events(
    transcript: dict,
    keeps: list[dict],
    *,
    max_line_gap: float = 0.45,
    max_line_dur: float = 4.5,
    max_line_chars: int = 30,
    tail_hold: float = 0.15,
) -> list[dict]:
    """Group contiguous mapped words into subtitle lines.

    Gap detection is done on *source-time* (word-level Whisper timestamps),
    not on cut-timeline, so that cut boundaries between words don't create
    false "gaps" that would split one utterance into two lines. The displayed
    time range is still on the cut-timeline.
    """
    lines: list[dict] = []
    current: list[tuple[float, float, str, float, float]] = []
    # tuple: (out_start, out_end, text, src_start, src_end)

    def flush() -> None:
        if not current:
            return
        start = current[0][0]
        end = current[-1][1] + tail_hold
        text = "".join(x[2] for x in current).strip()
        if not text:
            current.clear()
            return
        lines.append({"start": start, "end": end, "text": text})
        current.clear()

    for seg in transcript["segments"]:
        for w in seg["words"]:
            mapped = _map_word(w, keeps)
            if mapped is None:
                flush()
                continue
            out_s, out_e = mapped
            src_s, src_e = float(w["start"]), float(w["end"])
            text = w["text"]

            if current:
                src_gap = src_s - current[-1][4]
                elapsed_src = src_e - current[0][3]
                total_chars = sum(len(x[2]) for x in current) + len(text)
                if (
                    src_gap > max_line_gap
                    or elapsed_src > max_line_dur
                    or total_chars > max_line_chars
                ):
                    flush()
            current.append((out_s, out_e, text, src_s, src_e))
    flush()
    return lines


# ---------- main ----------

def build(
    transcript_path: str = "video_editor/work/transcript.json",
    segments_path: str = "video_editor/work/segments.json",
    emphasis_keywords: list[str] | None = None,
    sfx_keywords: dict[str, list[str]] | None = None,
    out_ass: str = "video_editor/work/subtitle.ass",
    out_sfx_cues: str = "video_editor/work/sfx_cues.json",
) -> None:
    emphasis_keywords = emphasis_keywords or []
    sfx_keywords = sfx_keywords or {}

    transcript = json.loads(Path(transcript_path).read_text(encoding="utf-8"))
    keeps = json.loads(Path(segments_path).read_text(encoding="utf-8"))

    subs = pysubs2.SSAFile()
    subs.info["PlayResX"] = "1920"
    subs.info["PlayResY"] = "1080"

    # YouTube 定番路線: 太めゴシック + 黒縁取り + 下部センター
    base = pysubs2.SSAStyle(
        fontname="Yu Gothic UI",
        fontsize=60,
        primarycolor=pysubs2.Color(255, 255, 255),
        outlinecolor=pysubs2.Color(0, 0, 0),
        backcolor=pysubs2.Color(0, 0, 0, 160),
        bold=True,
        outline=5,
        shadow=1,
        alignment=pysubs2.Alignment.BOTTOM_CENTER,
        marginv=90,
    )
    # Emphasis: 極太 Heavy フォント + 黄色塗り + 黒の太い縁取り
    emph = pysubs2.SSAStyle(
        fontname="Yu Gothic UI Heavy",
        fontsize=88,
        primarycolor=pysubs2.Color(255, 230, 0),
        outlinecolor=pysubs2.Color(0, 0, 0),
        backcolor=pysubs2.Color(0, 0, 0, 220),
        bold=True,
        outline=8,
        shadow=2,
        alignment=pysubs2.Alignment.BOTTOM_CENTER,
        marginv=100,
    )
    subs.styles["Default"] = base
    subs.styles["Emphasis"] = emph

    lines = _group_events(transcript, keeps)

    sfx_cues: list[dict] = []
    emph_count = 0
    for ln in lines:
        text = normalize_product(ln["text"]).strip()
        if not text:
            continue
        is_emph = any(kw in text for kw in emphasis_keywords)
        style = "Emphasis" if is_emph else "Default"
        wrapped = wrap_two_lines(text)
        ev_text = wrapped
        if is_emph:
            ev_text = (
                r"{\fad(100,100)\t(0,180,\fscx115\fscy115)\t(180,360,\fscx100\fscy100)}"
                + wrapped
            )
            emph_count += 1
        subs.append(
            pysubs2.SSAEvent(
                start=int(ln["start"] * 1000),
                end=int(ln["end"] * 1000),
                text=ev_text,
                style=style,
            )
        )
        # SFX
        matched = False
        for sfx_name, kws in sfx_keywords.items():
            if any(kw in text for kw in kws):
                sfx_cues.append({"sfx": sfx_name, "t": round(ln["start"], 3)})
                matched = True
                break
        if not matched and is_emph:
            sfx_cues.append({"sfx": "pop", "t": round(ln["start"], 3)})

    subs.save(out_ass, encoding="utf-8")
    Path(out_sfx_cues).write_text(
        json.dumps(sfx_cues, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {out_ass}  events={len(subs)}  emphasis={emph_count}")
    print(f"Wrote {out_sfx_cues}  cues={len(sfx_cues)}")


if __name__ == "__main__":
    emph_path = Path("video_editor/work/emphasis.json")
    if emph_path.exists():
        cfg = json.loads(emph_path.read_text(encoding="utf-8"))
        build(
            emphasis_keywords=cfg.get("emphasis_keywords", []),
            sfx_keywords=cfg.get("sfx_keywords", {}),
        )
    else:
        build()
