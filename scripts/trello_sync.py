"""Trello → MDファイル同期スクリプト.

Trello REST APIでボードの全カード（アーカイブ済含む）と履歴を取得し、
期限が指定日以降のカードを1枚1MDファイルとして保存する。

Usage:
    uv run python scripts/trello_sync.py
    uv run python scripts/trello_sync.py --since 2026-01-01
    uv run python scripts/trello_sync.py --board <board_id>
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import frontmatter
import httpx
from dotenv import load_dotenv

TRELLO_BASE = "https://api.trello.com/1"
DEFAULT_SINCE = "2026-01-01"
REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_ROOT = REPO_ROOT / ".company" / "secretary" / "tasks"


@dataclass
class CardEvent:
    type: str
    date: datetime
    from_list: str | None = None
    to_list: str | None = None
    text: str | None = None


@dataclass
class CardRecord:
    card_id: str
    name: str
    board_name: str
    list_name: str
    status: str
    description: str
    created: date | None
    due: date | None
    completed: date | None
    archived_at: date | None
    labels: list[str]
    members: list[str]
    comments_count: int
    checklist_items: int
    checklist_done: int
    elapsed_days: int | None
    url: str
    events: list[CardEvent] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", default=DEFAULT_SINCE, help="期限フィルタ (YYYY-MM-DD)")
    parser.add_argument("--board", default=None, help="Trello board ID（省略時は.envのTRELLO_BOARD_ID）")
    parser.add_argument("--out", default=str(TASKS_ROOT), help="MD出力先ディレクトリ")
    return parser.parse_args()


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_iso_date(value: str | None) -> date | None:
    dt = parse_iso(value)
    return dt.date() if dt else None


def trello_request(
    client: httpx.Client, path: str, params: dict[str, Any] | None = None
) -> Any:
    resp = client.get(f"{TRELLO_BASE}{path}", params=params, timeout=30.0)
    resp.raise_for_status()
    return resp.json()


def fetch_board(client: httpx.Client, auth: dict[str, str], board_id: str) -> dict[str, Any]:
    return trello_request(client, f"/boards/{board_id}", params=auth)


def fetch_lists(client: httpx.Client, auth: dict[str, str], board_id: str) -> dict[str, str]:
    lists = trello_request(
        client,
        f"/boards/{board_id}/lists",
        params={**auth, "filter": "all", "fields": "name,closed"},
    )
    return {lst["id"]: lst["name"] for lst in lists}


CARD_FIELDS = ",".join(
    [
        "id",
        "name",
        "desc",
        "due",
        "dueComplete",
        "idList",
        "idLabels",
        "labels",
        "idMembers",
        "shortUrl",
        "url",
        "closed",
        "dateLastActivity",
        "badges",
    ]
)


def fetch_cards(client: httpx.Client, auth: dict[str, str], board_id: str) -> list[dict[str, Any]]:
    """Fetch both archived (closed) and active (visible) cards and merge.

    `filter=all`/`filter=open` can hit API_TOO_MANY_CARDS_REQUESTED on large boards,
    but `filter=closed` and `filter=visible` are scoped narrower.
    """
    merged: dict[str, dict[str, Any]] = {}
    for scope in ("closed", "visible"):
        batch = trello_request(
            client,
            f"/boards/{board_id}/cards",
            params={
                **auth,
                "filter": scope,
                "fields": CARD_FIELDS,
                "members": "true",
                "member_fields": "fullName,username",
            },
        )
        for card in batch:
            merged[card["id"]] = card
    return list(merged.values())


def fetch_actions(
    client: httpx.Client, auth: dict[str, str], board_id: str, since: date
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    before: str | None = None
    since_iso = since.isoformat()
    while True:
        params: dict[str, Any] = {
            **auth,
            "filter": "createCard,updateCard:idList,updateCard:closed,commentCard,convertToCardFromCheckItem",
            "limit": 1000,
            "since": since_iso,
        }
        if before:
            params["before"] = before
        batch = trello_request(client, f"/boards/{board_id}/actions", params=params)
        if not batch:
            break
        actions.extend(batch)
        if len(batch) < 1000:
            break
        before = batch[-1]["date"]
    return actions


def fetch_checklists(client: httpx.Client, auth: dict[str, str], board_id: str) -> dict[str, dict[str, int]]:
    checklists = trello_request(
        client,
        f"/boards/{board_id}/checklists",
        params={**auth, "fields": "idCard", "checkItem_fields": "state"},
    )
    result: dict[str, dict[str, int]] = defaultdict(lambda: {"items": 0, "done": 0})
    for cl in checklists:
        card_id = cl.get("idCard")
        if not card_id:
            continue
        for item in cl.get("checkItems", []):
            result[card_id]["items"] += 1
            if item.get("state") == "complete":
                result[card_id]["done"] += 1
    return result


def build_event_index(actions: list[dict[str, Any]]) -> dict[str, list[CardEvent]]:
    index: dict[str, list[CardEvent]] = defaultdict(list)
    for a in actions:
        card_id = (a.get("data") or {}).get("card", {}).get("id")
        if not card_id:
            continue
        action_type = a["type"]
        dt = parse_iso(a["date"])
        if not dt:
            continue
        data = a.get("data") or {}
        event = CardEvent(type=action_type, date=dt)
        if action_type.startswith("updateCard") and "listBefore" in data and "listAfter" in data:
            event.from_list = data["listBefore"].get("name")
            event.to_list = data["listAfter"].get("name")
        elif action_type == "commentCard":
            event.text = data.get("text")
        index[card_id].append(event)
    for events in index.values():
        events.sort(key=lambda e: e.date)
    return index


def created_from_id(card_id: str) -> date | None:
    """Trello ObjectId の先頭8hex が Unix 秒のタイムスタンプ.

    https://help.atlassian.com/s/trello/getting-card-creation-date
    """
    try:
        ts = int(card_id[:8], 16)
        return datetime.fromtimestamp(ts, tz=timezone.utc).date()
    except (ValueError, OSError):
        return None


def compute_card_dates(
    card: dict[str, Any], events: list[CardEvent]
) -> tuple[date | None, date | None, date | None]:
    created_ts: date | None = None
    for e in events:
        if e.type == "createCard" or e.type == "convertToCardFromCheckItem":
            created_ts = e.date.date()
            break
    if created_ts is None:
        created_ts = created_from_id(card["id"])

    due = parse_iso_date(card.get("due"))
    completed: date | None = None
    archived_at: date | None = None

    if card.get("closed"):
        for e in reversed(events):
            if e.type == "updateCard" and ("closed" in (e.type or "") or True):
                archived_at = e.date.date()
                break
        if archived_at is None and events:
            archived_at = events[-1].date.date()

    if card.get("dueComplete"):
        for e in reversed(events):
            if e.type.startswith("updateCard") or e.type == "commentCard":
                completed = e.date.date()
                break
    elif card.get("closed"):
        completed = archived_at

    return created_ts, completed, archived_at


def build_record(
    card: dict[str, Any],
    list_names: dict[str, str],
    board_name: str,
    events: list[CardEvent],
    checklist_counts: dict[str, int],
) -> CardRecord:
    created, completed, archived_at = compute_card_dates(card, events)

    if card.get("closed"):
        status = "archived"
    elif card.get("dueComplete"):
        status = "completed"
    else:
        status = "open"

    labels = [lbl.get("name") or lbl.get("color") or "unlabeled" for lbl in card.get("labels", [])]
    if not labels:
        labels = ["unlabeled"]

    members = [m.get("fullName") or m.get("username", "?") for m in card.get("members", [])]

    reference_end = completed or archived_at or date.today()
    elapsed = (reference_end - created).days if created else None
    if elapsed is not None and elapsed < 0:
        elapsed = 0

    return CardRecord(
        card_id=card["id"],
        name=card.get("name", "").strip(),
        board_name=board_name,
        list_name=list_names.get(card.get("idList", ""), "unknown"),
        status=status,
        description=card.get("desc", "") or "",
        created=created,
        due=parse_iso_date(card.get("due")),
        completed=completed,
        archived_at=archived_at,
        labels=labels,
        members=members,
        comments_count=(card.get("badges") or {}).get("comments", 0),
        checklist_items=checklist_counts.get("items", 0),
        checklist_done=checklist_counts.get("done", 0),
        elapsed_days=elapsed,
        url=card.get("shortUrl") or card.get("url", ""),
        events=events,
    )


SAFE_NAME = re.compile(r"[^0-9A-Za-z_-]+")


def build_filename(record: CardRecord) -> str:
    slug = SAFE_NAME.sub("-", record.name)[:40].strip("-") or "card"
    return f"{record.card_id[:8]}-{slug}.md"


def render_body(record: CardRecord, existing_body: str | None) -> str:
    lines: list[str] = []
    title = f"# {record.name}" if record.name else "# (no title)"
    lines.append(title)
    lines.append("")
    if record.description.strip():
        lines.append(record.description.strip())
        lines.append("")
    lines.append("## コメント・移動履歴")
    for event in record.events:
        ts = event.date.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
        if event.type == "createCard":
            lines.append(f"- {ts} 作成")
        elif event.type.startswith("updateCard") and event.from_list and event.to_list:
            lines.append(f"- {ts} リスト移動: {event.from_list} → {event.to_list}")
        elif event.type == "commentCard":
            text = (event.text or "").strip().replace("\n", " ")
            if len(text) > 120:
                text = text[:117] + "..."
            lines.append(f"- {ts} コメント: {text}")
    if not record.events:
        lines.append("- （履歴なし）")
    if existing_body:
        marker = "## 手動メモ"
        if marker in existing_body:
            tail = existing_body.split(marker, 1)[1]
            lines.append("")
            lines.append(marker)
            lines.append(tail.strip())
    return "\n".join(lines).rstrip() + "\n"


def record_to_frontmatter(record: CardRecord) -> dict[str, Any]:
    def iso(d: date | None) -> str | None:
        return d.isoformat() if d else None

    return {
        "card_id": record.card_id,
        "name": record.name,
        "board": record.board_name,
        "list": record.list_name,
        "status": record.status,
        "created": iso(record.created),
        "due": iso(record.due),
        "completed": iso(record.completed),
        "archived_at": iso(record.archived_at),
        "labels": record.labels,
        "members": record.members,
        "comments_count": record.comments_count,
        "checklist_items": record.checklist_items,
        "checklist_done": record.checklist_done,
        "elapsed_days": record.elapsed_days,
        "url": record.url,
    }


def write_card(record: CardRecord, out_root: Path) -> Path:
    year_month = (record.due or record.created or date.today()).strftime("%Y-%m")
    folder = out_root / year_month
    folder.mkdir(parents=True, exist_ok=True)
    filepath = folder / build_filename(record)

    existing_body: str | None = None
    if filepath.exists():
        existing = frontmatter.load(filepath)
        existing_body = existing.content

    post = frontmatter.Post(content=render_body(record, existing_body))
    post.metadata = record_to_frontmatter(record)
    filepath.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
    return filepath


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    args = parse_args()

    api_key = os.environ.get("TRELLO_API_KEY")
    token = os.environ.get("TRELLO_TOKEN") or os.environ.get("TRELLO_API_TOKEN")
    board_id = args.board or os.environ.get("TRELLO_BOARD_ID")

    if not (api_key and token and board_id):
        sys.stderr.write(
            "ERROR: .envにTRELLO_API_KEY / TRELLO_TOKEN / TRELLO_BOARD_IDが必要です\n"
        )
        return 2

    since = datetime.strptime(args.since, "%Y-%m-%d").date()
    out_root = Path(args.out).resolve()
    auth = {"key": api_key, "token": token}

    with httpx.Client() as client:
        board = fetch_board(client, auth, board_id)
        lists = fetch_lists(client, auth, board_id)
        cards = fetch_cards(client, auth, board_id)
        actions = fetch_actions(client, auth, board_id, since)
        checklists = fetch_checklists(client, auth, board_id)

    events_index = build_event_index(actions)
    written = 0
    skipped_no_due = 0
    skipped_old = 0

    for card in cards:
        due = parse_iso_date(card.get("due"))
        if due is None:
            skipped_no_due += 1
            continue
        if due < since:
            skipped_old += 1
            continue

        record = build_record(
            card,
            lists,
            board.get("name", ""),
            events_index.get(card["id"], []),
            checklists.get(card["id"], {"items": 0, "done": 0}),
        )
        filepath = write_card(record, out_root)
        written += 1
        rel = filepath.relative_to(REPO_ROOT) if filepath.is_absolute() else filepath
        print(f"  wrote {rel} (status={record.status}, elapsed={record.elapsed_days})")

    print()
    print(f"Done. written={written}, skipped_no_due={skipped_no_due}, skipped_before_since={skipped_old}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
