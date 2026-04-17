"""目標進捗パネル用ロジック: YAML + スプシ を束ねて進捗JSONを返す."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from .loader import REPO_ROOT
from .revenue_sheet import CredentialsNotConfigured, fetch_with_customer

GOALS_DIR = REPO_ROOT / ".company" / "secretary" / "goals"


def _load_yaml(name: str) -> dict[str, Any]:
    path = GOALS_DIR / name
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_targets() -> dict[str, Any]:
    return _load_yaml("targets.yaml")


def _load_revenue_yaml() -> dict[str, dict[str, Any]]:
    data = _load_yaml("revenue.yaml")
    return data.get("monthly") or {}


def _load_initiatives() -> list[dict[str, Any]]:
    data = _load_yaml("initiatives.yaml")
    return data.get("initiatives") or []


def _merge_monthly(yaml_monthly: dict[str, Any], sheet_monthly: dict[str, int]) -> dict[str, dict[str, Any]]:
    """YAMLを主、スプシを補助として月次を合成."""
    result: dict[str, dict[str, Any]] = {}
    all_months = set(yaml_monthly.keys()) | set(sheet_monthly.keys())
    for m in sorted(all_months):
        y = yaml_monthly.get(m, {}) if isinstance(yaml_monthly.get(m), dict) else {"amount": yaml_monthly.get(m, 0)}
        yaml_amt = int(y.get("amount") or 0)
        sheet_amt = int(sheet_monthly.get(m, 0))
        confirmed = bool(y.get("confirmed", False))
        chosen = yaml_amt if yaml_amt > 0 else sheet_amt
        result[m] = {
            "month": m,
            "amount": chosen,
            "yaml_amount": yaml_amt,
            "sheet_amount": sheet_amt,
            "confirmed": confirmed,
            "note": y.get("note") or "",
        }
    return result


def _linear_forecast(points: list[tuple[int, int]]) -> float | None:
    """直近Nヶ月の線形回帰で次月予測."""
    if len(points) < 2:
        return None
    n = len(points)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    numer = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom = sum((x - mean_x) ** 2 for x in xs)
    if denom == 0:
        return None
    slope = numer / denom
    intercept = mean_y - slope * mean_x
    next_x = max(xs) + 1
    return max(0.0, slope * next_x + intercept)


def _eta_months(current: float, target: float, slope: float) -> int | None:
    if slope <= 0 or current >= target:
        return None
    remaining = target - current
    months = remaining / slope
    if months > 240:  # 20年超なら非現実
        return None
    return int(round(months))


def build_goal_progress(force_sheet_refresh: bool = False) -> dict[str, Any]:
    targets = _load_targets()
    milestones = targets.get("milestones") or {}
    yaml_monthly = _load_revenue_yaml()
    initiatives = _load_initiatives()

    sheet_total = 0
    sheet_monthly: dict[str, int] = {}
    top_customers: dict[str, int] = {}
    monthly_by_customer: dict[str, dict[str, int]] = {}
    sheet_error: str | None = None
    fetched_at: str | None = None

    try:
        sheet_data = fetch_with_customer(refresh=force_sheet_refresh)
        sheet_monthly = sheet_data.get("monthly", {})
        top_customers = sheet_data.get("top_customers", {})
        monthly_by_customer = sheet_data.get("monthly_by_customer", {})
        fetched_at = sheet_data.get("fetched_at")
        sheet_total = sum(sheet_monthly.values())
    except CredentialsNotConfigured as e:
        sheet_error = f"スプシ認証未設定: {e}"
    except Exception as e:
        sheet_error = f"スプシ取得失敗: {type(e).__name__}: {e}"

    combined = _merge_monthly(yaml_monthly, sheet_monthly)

    # 直近の確定月を"current"と見なす
    confirmed_months = [m for m in combined.values() if m["confirmed"] and m["amount"] > 0]
    current = confirmed_months[-1] if confirmed_months else (
        list(combined.values())[-1] if combined else {"month": None, "amount": 0}
    )
    current_amount = current.get("amount", 0) or 0

    # トレンド: 直近6ヶ月の線形回帰
    entries = [m for m in combined.values() if m["amount"] > 0]
    tail = entries[-6:]
    points = [(i, e["amount"]) for i, e in enumerate(tail)]
    forecast = _linear_forecast(points)
    slope = None
    if len(points) >= 2:
        n = len(points)
        mean_x = sum(p[0] for p in points) / n
        mean_y = sum(p[1] for p in points) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in points)
        den = sum((x - mean_x) ** 2 for x, _ in points)
        slope = num / den if den else None

    def pct(value: int, target: int) -> float:
        return round(value / target, 3) if target else 0.0

    progress: dict[str, Any] = {}
    for key, m in milestones.items():
        tgt = int(m.get("monthly_yen") or 0)
        progress[key] = {
            "label": m.get("label"),
            "target_yen": tgt,
            "pct": pct(current_amount, tgt),
            "eta_months": _eta_months(current_amount, tgt, slope or 0),
            "rationale": m.get("rationale"),
        }

    # 直近月の依存度(トップ顧客の寄与率) - スプシデータから
    dependency_pct = 0.0
    top_customer_id = None
    top_customer_amount = 0
    if current.get("month") and monthly_by_customer.get(current["month"]):
        cm = monthly_by_customer[current["month"]]
        if cm:
            top_customer_id, top_customer_amount = max(cm.items(), key=lambda kv: kv[1])
            m_total = sum(cm.values())
            if m_total:
                dependency_pct = round(top_customer_amount / m_total, 3)

    return {
        "current_month": current.get("month"),
        "current_revenue": current_amount,
        "current_confirmed": current.get("confirmed", False),
        "targets": progress,
        "trend": {
            "months": [e["month"] for e in entries],
            "amounts": [e["amount"] for e in entries],
            "confirmed": [e["confirmed"] for e in entries],
            "forecast_next": int(forecast) if forecast is not None else None,
            "slope_per_month": round(slope or 0, 1),
        },
        "dependency": {
            "sheet_top_customer": top_customer_id,
            "sheet_top_customer_amount": top_customer_amount,
            "sheet_top_customer_pct": dependency_pct,
            "note": "スプシ記録分のみ. 全チャネル合算ではない点に注意",
        },
        "initiatives": initiatives,
        "sheet_meta": {
            "fetched_at": fetched_at,
            "sheet_total_recorded": sheet_total,
            "error": sheet_error,
        },
    }
