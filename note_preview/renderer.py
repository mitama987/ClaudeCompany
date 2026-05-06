"""Render Article to HTML matching note.com's published article style."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from note_preview import Article, Block

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _block_to_html(block: Block) -> str:
    """Convert a single Block to its HTML representation."""
    if block.type == "h2":
        return f"<h2>{block.content}</h2>"
    if block.type == "h3":
        return f"<h3>{block.content}</h3>"
    if block.type == "p":
        text = block.html if block.html else block.content
        return f"<p>{text}</p>"
    if block.type == "ul":
        items = "".join(f"<li><p>{item}</p></li>" for item in block.items)
        return f"<ul>{items}</ul>"
    if block.type == "ol":
        items = "".join(f"<li><p>{item}</p></li>" for item in block.items)
        return f"<ol>{items}</ol>"
    if block.type == "blockquote":
        inner = block.content.replace("\n", "<br>")
        return f"<figure><blockquote><p>{inner}</p></blockquote></figure>"
    if block.type == "table":
        header_cells = "".join(f"<th>{h}</th>" for h in block.headers)
        header_row = f"<tr>{header_cells}</tr>" if block.headers else ""
        body_rows = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in block.rows
        )
        return f"<table><thead>{header_row}</thead><tbody>{body_rows}</tbody></table>"
    if block.type == "image":
        return f'<div class="note-image-placeholder">[画像: {block.content}]</div>'
    if block.type == "empty":
        return "<p><br></p>"
    return ""


def render_html(article: Article) -> str:
    """Render an Article to a self-contained HTML string."""
    css_path = TEMPLATES_DIR / "note_com.css"
    css = css_path.read_text(encoding="utf-8")

    body_html = "\n".join(_block_to_html(b) for b in article.blocks)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
    )
    template = env.get_template("article.html")

    return template.render(
        title=article.title,
        date=article.date,
        tags=article.tags,
        css=css,
        body_html=body_html,
    )
