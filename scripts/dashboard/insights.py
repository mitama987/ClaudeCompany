"""ルールベース示唆生成: 配分偏り・時間超過・議論過多・放置・完了率低下."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any

from .loader import TaskCard


def _label_days(cards: list[TaskCard]) -> dict[str, int]:
    total: dict[str, int] = defaultdict(int)
    for c in cards:
        if c.elapsed_days is None:
            continue
        for label in c.labels or ["unlabeled"]:
            total[label] += c.elapsed_days
    return dict(total)


def _p95(values: list[int]) -> float:
    if not values:
        return 0.0
    sorted_v = sorted(values)
    idx = int(len(sorted_v) * 0.95)
    idx = min(idx, len(sorted_v) - 1)
    return float(sorted_v[idx])


def build_insights(cards: list[TaskCard]) -> list[dict[str, Any]]:
    insights: list[dict[str, Any]] = []
    if not cards:
        return insights

    # 1. 配分偏り（ラベル別合計時間の最大/最小 > 5倍）
    totals = _label_days(cards)
    if len(totals) >= 2:
        max_label, max_days = max(totals.items(), key=lambda kv: kv[1])
        min_label, min_days = min(
            ((k, v) for k, v in totals.items() if v > 0), key=lambda kv: kv[1], default=(None, 0)
        )
        if min_days > 0 and max_days / min_days > 5:
            insights.append(
                {
                    "level": "warning",
                    "icon": "⚠️",
                    "title": "ラベル別時間配分の偏り",
                    "message": (
                        f"「{max_label}」{max_days}日 vs 「{min_label}」{min_days}日。"
                        f"配分比 {round(max_days/min_days, 1)}倍。収益系ラベルとの釣合を確認推奨"
                    ),
                }
            )

    # 2. 時間超過（中央値の3倍以上）
    elapsed = [c.elapsed_days for c in cards if c.elapsed_days]
    if elapsed:
        med = median(elapsed)
        threshold = max(med * 3, 14)
        over = sorted(
            [c for c in cards if c.elapsed_days and c.elapsed_days >= threshold],
            key=lambda c: -(c.elapsed_days or 0),
        )[:5]
        for c in over:
            insights.append(
                {
                    "level": "danger",
                    "icon": "🚨",
                    "title": "時間超過タスク",
                    "message": (
                        f"「{c.name}」{c.elapsed_days}日（中央値 {med:.0f}日 の "
                        f"{(c.elapsed_days or 0) / max(med, 1):.1f}倍）"
                    ),
                    "card_id": c.card_id,
                    "url": c.url,
                }
            )

    # 3. 議論過多（コメント数 p95超）
    comments = [c.comments_count for c in cards]
    p95_comments = _p95(comments)
    if p95_comments >= 5:
        for c in sorted(cards, key=lambda c: -c.comments_count)[:3]:
            if c.comments_count >= p95_comments:
                insights.append(
                    {
                        "level": "info",
                        "icon": "💬",
                        "title": "議論過多タスク",
                        "message": f"「{c.name}」コメント{c.comments_count}件。意思決定が滞っている可能性",
                        "card_id": c.card_id,
                        "url": c.url,
                    }
                )

    # 4. 未完了放置（open × elapsed >= 30日）
    today = date.today()
    stale = sorted(
        [
            c
            for c in cards
            if c.status == "open" and c.created and (today - c.created).days >= 30
        ],
        key=lambda c: (c.created or today),
    )[:5]
    for c in stale:
        days = (today - c.created).days if c.created else 0
        insights.append(
            {
                "level": "warning",
                "icon": "⏳",
                "title": "未完了放置タスク",
                "message": f"「{c.name}」{days}日未完了。中断検討または細分化を推奨",
                "card_id": c.card_id,
                "url": c.url,
            }
        )

    # 5. 完了率低下（直近30日の完了率 < 過去平均 × 0.5）
    window_days = 30
    cutoff = today - timedelta(days=window_days)
    recent = [c for c in cards if c.due and c.due >= cutoff]
    past = [c for c in cards if c.due and c.due < cutoff]
    if recent and past:
        recent_rate = sum(1 for c in recent if c.status in ("completed", "archived")) / len(recent)
        past_rate = sum(1 for c in past if c.status in ("completed", "archived")) / len(past)
        if past_rate > 0 and recent_rate < past_rate * 0.5:
            insights.append(
                {
                    "level": "warning",
                    "icon": "📉",
                    "title": "直近の完了率低下",
                    "message": (
                        f"直近{window_days}日の完了率 {recent_rate:.0%} "
                        f"vs 過去平均 {past_rate:.0%}。タスク細分化 or 優先度見直しを推奨"
                    ),
                }
            )

    # 6. ポジティブ示唆（最も投下したジャンル）
    if totals:
        max_label, max_days = max(totals.items(), key=lambda kv: kv[1])
        insights.append(
            {
                "level": "info",
                "icon": "📊",
                "title": "最注力ジャンル",
                "message": f"「{max_label}」に合計 {max_days}日 投下。これが主戦場",
            }
        )

    return insights
