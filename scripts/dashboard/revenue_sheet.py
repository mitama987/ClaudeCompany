"""Yパパツールマーケット スプシから月別売上を集計.

認証: GOOGLE_APPLICATION_CREDENTIALS 環境変数 or 既定のJSON鍵ファイルを利用.
シート: マスター!F2:U10000 (F=登録日, U=売上額)
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

SPREADSHEET_ID = "1QU9IgrjsfDTDRtLnn3f9S3fj9jgjBVlVyjKFrIQzJU0"
SHEET_RANGE = "マスター!F2:V10000"  # F=登録日, U=売上額, V=備考など余白
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_PATH = REPO_ROOT / ".cache" / "revenue-monthly.json"
CACHE_TTL_SEC = 3600

DEFAULT_KEY_PATH = (
    r"C:\Users\mitam\Desktop\work\30_XTP2_POST_r5\xtools-docs-auth-9322b5c556f3.json"
)

_DATE_PATTERNS = [
    ("%Y-%m-%d", re.compile(r"^\d{4}-\d{1,2}-\d{1,2}")),
    ("%Y/%m/%d", re.compile(r"^\d{4}/\d{1,2}/\d{1,2}")),
    ("%Y.%m.%d", re.compile(r"^\d{4}\.\d{1,2}\.\d{1,2}")),
    ("%m/%d/%Y", re.compile(r"^\d{1,2}/\d{1,2}/\d{4}")),
]

_EXCEL_EPOCH = datetime(1899, 12, 30)  # Lotus/Excel serial date basis


def _excel_serial_to_date(v: float) -> datetime | None:
    try:
        days = float(v)
    except (TypeError, ValueError):
        return None
    if days < 10000 or days > 100000:
        return None
    from datetime import timedelta
    return _EXCEL_EPOCH + timedelta(days=days)


class CredentialsNotConfigured(RuntimeError):
    """認証情報がセットされていないときに投げる."""


def _credential_path() -> Path:
    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p
    default = Path(DEFAULT_KEY_PATH)
    if default.exists():
        return default
    raise CredentialsNotConfigured(
        ".envにGOOGLE_APPLICATION_CREDENTIALS=<service account JSONの絶対パス>を設定してください"
    )


def _build_service():
    creds = service_account.Credentials.from_service_account_file(
        str(_credential_path()), scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _parse_date(raw: Any) -> datetime | None:
    if raw is None or raw == "":
        return None
    # Excel serial number (float/int from UNFORMATTED_VALUE)
    if isinstance(raw, (int, float)):
        return _excel_serial_to_date(float(raw))
    raw = str(raw).strip()
    if not raw:
        return None
    # Pure number string → treat as serial
    try:
        return _excel_serial_to_date(float(raw))
    except ValueError:
        pass
    for fmt, rx in _DATE_PATTERNS:
        if rx.match(raw):
            try:
                return datetime.strptime(raw[: len(fmt.replace("%", "")) + 6], fmt)
            except ValueError:
                continue
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_amount(raw: str) -> int:
    if not raw:
        return 0
    cleaned = re.sub(r"[^\d\-]", "", str(raw))
    if not cleaned or cleaned == "-":
        return 0
    try:
        return int(cleaned)
    except ValueError:
        return 0


def _use_cache() -> dict[str, Any] | None:
    if not CACHE_PATH.exists():
        return None
    age = time.time() - CACHE_PATH.stat().st_mtime
    if age > CACHE_TTL_SEC:
        return None
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_cache(payload: dict[str, Any]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_monthly(refresh: bool = False) -> dict[str, Any]:
    """月別売上合計 + 上位顧客の寄与 を返す.

    Returns:
      {
        "monthly": {"2025-04": 0, ..., "2026-03": 80280},
        "top_customers": {"m840419": 100000, ...},
        "monthly_by_customer": {"2026-03": {"m840419": 30000, ...}},
        "fetched_at": "2026-04-18T..."
      }
    """
    if not refresh:
        cached = _use_cache()
        if cached:
            return cached

    service = _build_service()
    resp = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_RANGE, valueRenderOption="UNFORMATTED_VALUE")
        .execute()
    )
    rows = resp.get("values", [])

    monthly: dict[str, int] = defaultdict(int)
    customer_total: dict[str, int] = defaultdict(int)
    monthly_customer: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in rows:
        # F(index 0) = 登録日, U(index 14) = 売上額
        # マスター!F2:V → 列 F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V (index 0..16)
        # U は index 15 (F=0, U=0+15=15)
        if len(row) < 16:
            continue
        registered_at = row[0] if row else ""
        amount_raw = row[15] if len(row) > 15 else ""
        customer_id = row[-1] if row and len(row) > 1 else ""  # fallback
        # A列(ユーザーID)は別レンジだと取れない。とりあえず行頭の登録日の手前は取得していない。
        # 月別集計には登録日と売上額だけあればよい
        dt = _parse_date(str(registered_at))
        amount = _parse_amount(amount_raw)
        if not dt or amount <= 0:
            continue
        key = dt.strftime("%Y-%m")
        monthly[key] += amount

    payload: dict[str, Any] = {
        "monthly": dict(sorted(monthly.items())),
        "top_customers": dict(
            sorted(customer_total.items(), key=lambda kv: -kv[1])[:10]
        ),
        "monthly_by_customer": {m: dict(v) for m, v in monthly_customer.items()},
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
    }
    _write_cache(payload)
    return payload


def fetch_with_customer(refresh: bool = False) -> dict[str, Any]:
    """A列(ユーザーID)も含めて取得する拡張版."""
    if not refresh:
        cached = _use_cache()
        if cached and cached.get("has_customer"):
            return cached

    service = _build_service()
    resp = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range="マスター!A2:V10000",
            valueRenderOption="UNFORMATTED_VALUE",
        )
        .execute()
    )
    rows = resp.get("values", [])

    monthly: dict[str, int] = defaultdict(int)
    customer_total: dict[str, int] = defaultdict(int)
    monthly_customer: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in rows:
        # A=ユーザーID(0), F=登録日(5), U=売上額(20)
        if len(row) < 21:
            continue
        customer_id = str(row[0] or "").strip() or "unknown"
        registered_at = row[5]
        amount_raw = row[20]
        dt = _parse_date(str(registered_at))
        amount = _parse_amount(amount_raw)
        if not dt or amount <= 0:
            continue
        key = dt.strftime("%Y-%m")
        monthly[key] += amount
        customer_total[customer_id] += amount
        monthly_customer[key][customer_id] += amount

    payload = {
        "monthly": dict(sorted(monthly.items())),
        "top_customers": dict(sorted(customer_total.items(), key=lambda kv: -kv[1])[:10]),
        "monthly_by_customer": {m: dict(sorted(v.items(), key=lambda kv: -kv[1])[:5]) for m, v in monthly_customer.items()},
        "fetched_at": datetime.now().isoformat(timespec="seconds"),
        "has_customer": True,
    }
    _write_cache(payload)
    return payload


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    data = fetch_with_customer(refresh=True)
    print(f"months: {len(data['monthly'])}")
    for k, v in list(data["monthly"].items()):
        print(f"  {k}: JPY {v:,}")
    print("top customers:")
    for k, v in list(data["top_customers"].items())[:5]:
        print(f"  {k}: JPY {v:,}")
