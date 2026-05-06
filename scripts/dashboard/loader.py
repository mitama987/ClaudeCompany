"""MDファイル群から集計用データを読み込むモジュール."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import frontmatter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TASKS_ROOT = REPO_ROOT / ".company" / "secretary" / "tasks"


@dataclass
class TaskCard:
    card_id: str
    name: str
    board: str
    list: str
    status: str
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
    file_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "name": self.name,
            "board": self.board,
            "list": self.list,
            "status": self.status,
            "created": self.created.isoformat() if self.created else None,
            "due": self.due.isoformat() if self.due else None,
            "completed": self.completed.isoformat() if self.completed else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "labels": self.labels,
            "members": self.members,
            "comments_count": self.comments_count,
            "checklist_items": self.checklist_items,
            "checklist_done": self.checklist_done,
            "elapsed_days": self.elapsed_days,
            "url": self.url,
            "file_path": self.file_path,
        }


def _parse_date(v: Any) -> date | None:
    if v is None:
        return None
    if isinstance(v, date):
        return v
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, str):
        try:
            return date.fromisoformat(v)
        except ValueError:
            return None
    return None


def load_all(root: Path = TASKS_ROOT) -> list[TaskCard]:
    cards: list[TaskCard] = []
    if not root.exists():
        return cards
    for path in sorted(root.rglob("*.md")):
        doc = frontmatter.load(path)
        meta = doc.metadata
        if not meta.get("card_id"):
            continue
        cards.append(
            TaskCard(
                card_id=str(meta["card_id"]),
                name=str(meta.get("name") or ""),
                board=str(meta.get("board") or ""),
                list=str(meta.get("list") or ""),
                status=str(meta.get("status") or "unknown"),
                created=_parse_date(meta.get("created")),
                due=_parse_date(meta.get("due")),
                completed=_parse_date(meta.get("completed")),
                archived_at=_parse_date(meta.get("archived_at")),
                labels=list(meta.get("labels") or []),
                members=list(meta.get("members") or []),
                comments_count=int(meta.get("comments_count") or 0),
                checklist_items=int(meta.get("checklist_items") or 0),
                checklist_done=int(meta.get("checklist_done") or 0),
                elapsed_days=(
                    int(meta["elapsed_days"]) if meta.get("elapsed_days") is not None else None
                ),
                url=str(meta.get("url") or ""),
                file_path=str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
            )
        )
    return cards
