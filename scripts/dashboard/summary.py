"""集計ロジック: ラベル別投下時間・月次推移・統計量."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from statistics import median
from typing import Any

from .loader import TaskCard


def _safe_labels(card: TaskCard) -> list[str]:
    return card.labels or ["unlabeled"]


def _reference_month(card: TaskCard) -> str | None:
    d = card.completed or card.archived_at or card.due or card.created
    return d.strftime("%Y-%m") if d else None


def build_summary(cards: list[TaskCard]) -> dict[str, Any]:
    if not cards:
        return {
            "total_cards": 0,
            "by_status": {},
            "labels": {"days": [], "counts": []},
            "monthly": {"months": [], "series": []},
            "stats": {},
            "period": None,
        }

    by_status: dict[str, int] = defaultdict(int)
    label_days: dict[str, int] = defaultdict(int)
    label_counts: dict[str, int] = defaultdict(int)
    monthly: dict[tuple[str, str], int] = defaultdict(int)
    all_labels: set[str] = set()
    all_elapsed: list[int] = []
    all_comments: list[int] = []
    dues: list[date] = []

    for c in cards:
        by_status[c.status] += 1
        if c.due:
            dues.append(c.due)
        if c.elapsed_days is not None:
            all_elapsed.append(c.elapsed_days)
        all_comments.append(c.comments_count)
        month = _reference_month(c)
        for label in _safe_labels(c):
            all_labels.add(label)
            label_counts[label] += 1
            if c.elapsed_days:
                label_days[label] += c.elapsed_days
            if month:
                monthly[(month, label)] += c.elapsed_days or 0

    labels_sorted = sorted(all_labels, key=lambda l: -label_days.get(l, 0))
    months_sorted = sorted({m for m, _ in monthly.keys()})

    def month_series() -> list[dict[str, Any]]:
        series: list[dict[str, Any]] = []
        for label in labels_sorted:
            series.append(
                {
                    "label": label,
                    "values": [monthly.get((m, label), 0) for m in months_sorted],
                }
            )
        return series

    completed_count = by_status.get("completed", 0) + by_status.get("archived", 0)
    total = len(cards)
    completion_rate = round(completed_count / total, 3) if total else 0.0

    return {
        "total_cards": total,
        "by_status": dict(by_status),
        "labels": {
            "names": labels_sorted,
            "days": [label_days[l] for l in labels_sorted],
            "counts": [label_counts[l] for l in labels_sorted],
        },
        "monthly": {
            "months": months_sorted,
            "series": month_series(),
        },
        "stats": {
            "completion_rate": completion_rate,
            "median_elapsed_days": median(all_elapsed) if all_elapsed else 0,
            "max_elapsed_days": max(all_elapsed) if all_elapsed else 0,
            "median_comments": median(all_comments) if all_comments else 0,
            "sum_elapsed_days": sum(all_elapsed),
        },
        "period": {
            "start": min(dues).isoformat() if dues else None,
            "end": max(dues).isoformat() if dues else None,
        },
    }


def build_scatter(cards: list[TaskCard]) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for c in cards:
        if c.elapsed_days is None:
            continue
        points.append(
            {
                "card_id": c.card_id,
                "name": c.name,
                "x": c.elapsed_days,
                "y": c.comments_count + c.checklist_items,
                "status": c.status,
                "label": (c.labels or ["unlabeled"])[0],
                "url": c.url,
                "file_path": c.file_path,
            }
        )
    return points
