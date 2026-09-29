"""Command-line interface for md2pdf Studio."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from md2pdf import __version__, convert_auto, convert_latex, convert_sidebar, convert_simple


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="md2pdf",
        description="Convert a Markdown document to PDF using the md2pdf renderers.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", type=Path, help="Source Markdown file")
    parser.add_argument("-o", "--output", type=Path, help="Output PDF path (default: input name with .pdf)")
    parser.add_argument(
        "-m", "--mode", choices=("auto", "sidebar", "latex", "simple"),
        default="auto", help="Renderer mode (default: auto)",
    )
    parser.add_argument("--margin", default="0.5in", help="Page margin (default: 0.5in)")
    parser.add_argument("--theme", choices=("light", "dark"), default="light", help="Sidebar theme")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.input.expanduser()
    if not source.is_file():
        print(f"Input file does not exist: {source}", file=sys.stderr)
        return 2
    output = (args.output or source.with_suffix(".pdf")).expanduser()
    if source.resolve() == output.resolve():
        print("Input and output paths must be different.", file=sys.stderr)
        return 2

    try:
        markdown = source.read_text(encoding="utf-8")
        if args.mode == "auto":
            backend = convert_auto(markdown, str(output), margin=args.margin, theme=args.theme)
        elif args.mode == "sidebar":
            convert_sidebar(markdown, str(output), margin=args.margin, theme=args.theme)
            backend = "sidebar"
        elif args.mode == "latex":
            convert_latex(markdown, str(output), margin=args.margin)
            backend = "latex"
        else:
            convert_simple(markdown, str(output), margin=args.margin)
            backend = "simple"
        print(f"Created {output} (renderer: {backend})")
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
