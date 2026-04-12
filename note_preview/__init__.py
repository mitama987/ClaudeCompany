"""note.com article preview tool."""

from dataclasses import dataclass, field


@dataclass
class Block:
    """A single content block in a note.com article."""

    type: str  # 'h2', 'h3', 'p', 'ul', 'blockquote', 'table', 'ol', 'image', 'empty'
    content: str = ""
    html: str = ""
    items: list[str] = field(default_factory=list)  # For ul blocks
    rows: list[list[str]] = field(default_factory=list)  # For table blocks (raw data)
    headers: list[str] = field(default_factory=list)  # For table blocks (header row)


@dataclass
class Article:
    """A parsed note.com article."""

    title: str = ""
    date: str = ""
    tags: list[str] = field(default_factory=list)
    source: str = ""
    blocks: list[Block] = field(default_factory=list)
