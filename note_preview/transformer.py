"""Content transformer for note.com article preview.

Applies the same transformations that the note-edit browser automation
skill uses when posting articles to note.com.
"""

import re
from copy import deepcopy

from note_preview import Article, Block

CTA_URL = "https://note.com/youpapalife/n/nbe13855e40d2"
GREETING = "こんにちは！SNS自動化ツール開発歴7年のYouパパです。"

# Patterns that identify "worry" paragraphs (悩みパターン)
_WORRY_ENDINGS = re.compile(
    r"(ませんか？|ですよね？|でしょうか？|しまう。|つかない。|ありませんか？)$"
)
_WORRY_SUMMARY = re.compile(
    r"(こんな悩み|そんな悩み|こんなお悩み|そんなお悩み|悩んでいませんか)"
)


def _strip_html(html: str) -> str:
    """Remove HTML tags to get plain text."""
    return re.sub(r"<[^>]+>", "", html)


# ---------------------------------------------------------------------------
# Individual transformation steps
# ---------------------------------------------------------------------------


def inject_greeting(article: Article) -> None:
    """Insert the standard greeting as the first block."""
    article.blocks.insert(0, Block(type="p", html=GREETING))


def convert_worry_pattern(article: Article) -> None:
    """Convert consecutive worry paragraphs before the first H2 into a blockquote."""
    blocks = article.blocks

    # Find the index of the first h2
    first_h2 = len(blocks)
    for i, b in enumerate(blocks):
        if b.type == "h2":
            first_h2 = i
            break

    # Scan paragraphs before the first h2 for worry patterns
    worry_start = None
    worry_end = None
    summary_idx = None

    for i in range(first_h2):
        b = blocks[i]
        if b.type != "p":
            continue
        plain = _strip_html(b.html) if b.html else b.content
        if _WORRY_SUMMARY.search(plain):
            summary_idx = i
        elif _WORRY_ENDINGS.search(plain):
            if worry_start is None:
                worry_start = i
            worry_end = i

    if worry_start is None:
        return

    # Collect worry lines: include ALL paragraphs between worry_start and worry_end
    # (not just those matching _WORRY_ENDINGS, since intermediate lines are also part
    # of the worry block, e.g. lines ending with 面倒。)
    worry_lines: list[str] = []
    indices_to_remove: list[int] = []

    for i in range(worry_start, (worry_end or worry_start) + 1):
        b = blocks[i]
        if b.type == "p":
            plain = _strip_html(b.html) if b.html else b.content
            if not _WORRY_SUMMARY.search(plain):
                worry_lines.append(f"・{plain}")
                indices_to_remove.append(i)

    if not worry_lines:
        return

    # Also remove summary line if it exists (we'll re-add it after the blockquote)
    summary_block = None
    if summary_idx is not None:
        summary_block = blocks[summary_idx]
        if summary_idx not in indices_to_remove:
            indices_to_remove.append(summary_idx)

    # Sort indices in reverse for safe removal
    indices_to_remove.sort(reverse=True)

    # Determine insertion point (where the first worry block was)
    insert_at = min(indices_to_remove)

    # Remove the old blocks
    for idx in indices_to_remove:
        blocks.pop(idx)

    # Insert blockquote at the position of the first worry block
    blockquote = Block(type="blockquote", content="\n".join(worry_lines))
    blocks.insert(insert_at, blockquote)

    # Insert summary line after blockquote if it existed
    if summary_block is not None:
        blocks.insert(insert_at + 1, summary_block)


def convert_tables_to_lists(article: Article) -> None:
    """Convert table blocks to unordered list blocks.

    note.com does not support HTML tables, so each data row is converted
    to a list item with ``header: value`` pairs joined by `` / ``.
    """
    for i, block in enumerate(article.blocks):
        if block.type != "table":
            continue
        headers = block.headers
        items: list[str] = []
        for row in block.rows:
            pairs = []
            for col_idx, cell in enumerate(row):
                header = headers[col_idx] if col_idx < len(headers) else ""
                pairs.append(f"{header}: {cell}")
            items.append(" / ".join(pairs))
        article.blocks[i] = Block(type="ul", items=items)


def replace_cta_links(article: Article) -> None:
    """Replace ``[リンク]`` placeholders with the actual CTA link."""
    link_html = f'<a href="{CTA_URL}">リンク</a>'
    for block in article.blocks:
        if block.html:
            block.html = block.html.replace("[リンク]", link_html)
        if block.content:
            block.content = block.content.replace("[リンク]", link_html)
        if block.items:
            block.items = [item.replace("[リンク]", link_html) for item in block.items]


def convert_ordered_lists(article: Article) -> None:
    """Convert ordered list blocks to numbered paragraphs.

    note.com has no ``<ol>`` support, so ``1. text`` is rendered as a
    plain paragraph preserving the number prefix.
    """
    # Group consecutive ol blocks, then replace each group with numbered paragraphs
    i = 0
    while i < len(article.blocks):
        if article.blocks[i].type != "ol":
            i += 1
            continue
        # Found the start of an ol group
        start = i
        items: list[str] = []
        while i < len(article.blocks) and article.blocks[i].type == "ol":
            items.append(article.blocks[i].content)
            i += 1
        # Replace the group with numbered paragraphs
        new_blocks = []
        for num, text in enumerate(items, 1):
            new_blocks.append(Block(type="p", html=f"{num}. {text}"))
        article.blocks[start:i] = new_blocks
        i = start + len(new_blocks)


def normalize_empty_lines(article: Article) -> None:
    """Ensure empty blocks appear only before h2/h3, and that every h2/h3 is preceded by one."""
    blocks = article.blocks
    if not blocks:
        return

    # First pass: remove all empty blocks
    blocks = [b for b in blocks if b.type != "empty"]

    # Second pass: insert empty blocks before h2/h3 (except at the very beginning)
    result: list[Block] = []
    for i, block in enumerate(blocks):
        if block.type in ("h2", "h3") and result:
            # Only add empty block if the previous block isn't already empty
            if not result or result[-1].type != "empty":
                result.append(Block(type="empty"))
        result.append(block)

    article.blocks = result


# ---------------------------------------------------------------------------
# Main transform function
# ---------------------------------------------------------------------------


def transform(article: Article) -> Article:
    """Apply all note.com content transformations to an article.

    Transformations are applied in order:
    1. Inject greeting
    2. Convert worry pattern to blockquote
    3. Convert tables to lists
    4. Replace CTA links
    5. Convert ordered lists to numbered paragraphs
    6. Normalize empty lines
    """
    article = deepcopy(article)
    inject_greeting(article)
    convert_worry_pattern(article)
    convert_tables_to_lists(article)
    replace_cta_links(article)
    convert_ordered_lists(article)
    normalize_empty_lines(article)
    return article
