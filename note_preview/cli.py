"""CLI entry point for note.com article previewer.

Usage:
    uv run note-preview <MDファイルパス>
    uv run note-preview <MDファイルパス> --no-transform
    uv run note-preview <MDファイルパス> --output out.html
"""

import argparse
import tempfile
import webbrowser
from pathlib import Path

from note_preview.parser import parse_article
from note_preview.renderer import render_html
from note_preview.transformer import transform


def main() -> None:
    parser = argparse.ArgumentParser(description="note.com 記事プレビューア")
    parser.add_argument("file", type=Path, help="記事MDファイルのパス")
    parser.add_argument(
        "--no-transform",
        action="store_true",
        help="note.com変換処理をスキップ（素のMDプレビュー）",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="HTMLファイルの出力先パス",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"エラー: ファイルが見つかりません: {args.file}")
        raise SystemExit(1)

    text = args.file.read_text(encoding="utf-8")
    article = parse_article(text)

    if not args.no_transform:
        article = transform(article)

    html = render_html(article)

    if args.output:
        args.output.write_text(html, encoding="utf-8")
        print(f"保存しました: {args.output}")
    else:
        tmp = Path(tempfile.mkdtemp()) / "note_preview.html"
        tmp.write_text(html, encoding="utf-8")
        print(f"プレビュー: {tmp}")
        webbrowser.open(tmp.as_uri())


if __name__ == "__main__":
    main()
