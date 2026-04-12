"""Markdown parser for note.com article preview."""

import re

import yaml

from note_preview import Article, Block


def inline_format(text: str) -> str:
    """Convert inline Markdown formatting to HTML.

    - **text** -> <strong>text</strong>
    - [text](url) -> <a href="url">text</a>  (but not ![[...]])
    - `code` -> <code>code</code>
    """
    # Bold: **text** -> <strong>text</strong>
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Links: [text](url) -> <a href="url">text</a>
    # Negative lookbehind to avoid matching ![[...]] (image syntax)
    text = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Inline code: `code` -> <code>code</code>
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def parse_article(text: str) -> Article:
    """Parse a Markdown article with YAML frontmatter into an Article."""
    article = Article()

    # Split frontmatter from body
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter_str = parts[1]
            body = parts[2].lstrip("\n")
            frontmatter = yaml.safe_load(frontmatter_str)
            if isinstance(frontmatter, dict):
                article.title = str(frontmatter.get("title", ""))
                article.date = str(frontmatter.get("date", ""))
                tags = frontmatter.get("tags", [])
                if isinstance(tags, list):
                    article.tags = [str(t) for t in tags]
                article.source = str(frontmatter.get("source", ""))

    lines = body.split("\n")
    blocks: list[Block] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # H1 title - set as article title, exclude from blocks
        if line.startswith("# ") and not line.startswith("## "):
            title_text = line[2:].strip()
            if not article.title:
                article.title = title_text
            i += 1
            continue

        # H2
        if line.startswith("## "):
            blocks.append(Block(type="h2", content=line[3:].strip()))
            i += 1
            continue

        # H3
        if line.startswith("### "):
            blocks.append(Block(type="h3", content=line[4:].strip()))
            i += 1
            continue

        # Unordered list: consecutive `- ` lines grouped into one block
        if line.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].startswith("- "):
                item_text = lines[i][2:].strip()
                items.append(inline_format(item_text))
                i += 1
            blocks.append(Block(type="ul", items=items))
            continue

        # Blockquote: consecutive `> ` lines grouped into one block
        if line.startswith("> "):
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:].strip())
                i += 1
            blocks.append(Block(type="blockquote", content="\n".join(quote_lines)))
            continue

        # Table: consecutive `| ... |` lines grouped into one block
        if line.startswith("|") and line.endswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].startswith("|") and lines[i].endswith("|"):
                table_lines.append(lines[i])
                i += 1
            headers: list[str] = []
            rows: list[list[str]] = []
            for idx, tline in enumerate(table_lines):
                cells = [c.strip() for c in tline.strip("|").split("|")]
                if idx == 0:
                    headers = cells
                elif idx == 1:
                    # Separator row (---|---), skip
                    continue
                else:
                    rows.append(cells)
            blocks.append(Block(type="table", headers=headers, rows=rows))
            continue

        # Ordered list: `N. text`
        if re.match(r"^\d+\.\s", line):
            content = re.sub(r"^\d+\.\s", "", line).strip()
            blocks.append(Block(type="ol", content=content))
            i += 1
            continue

        # Image: ![[filename]]
        if line.startswith("![[") and line.endswith("]]"):
            filename = line[3:-2].strip()
            blocks.append(Block(type="image", content=filename))
            i += 1
            continue

        # Empty line: only insert if next non-empty line starts with ## or ###
        if line.strip() == "":
            # Look ahead for the next non-empty line
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and (
                lines[j].startswith("## ") or lines[j].startswith("### ")
            ):
                blocks.append(Block(type="empty"))
            i += 1
            continue

        # Everything else: paragraph with inline formatting
        blocks.append(Block(type="p", html=inline_format(line)))
        i += 1

    article.blocks = blocks
    return article
