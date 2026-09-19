#!/usr/bin/env python3
"""
md2pdf_mcp — Model Context Protocol server for the md2pdf converter.

Exposes the same conversion pipelines as the desktop app (Simple:
pandoc+wkhtmltopdf; LaTeX: pandoc+pdflatex with styled boxes and native math)
as MCP tools, so any MCP client — Claude Desktop/Code, or Google Antigravity —
can convert Markdown to a styled PDF without running the GUI.

Run directly for local testing:
    python3 mcp_server/server.py

Configure in an MCP client's config (Claude Desktop / Antigravity) with:
    {
      "mcpServers": {
        "md2pdf": {
          "command": "python3",
          "args": ["/absolute/path/to/mcp_server/server.py"]
        }
      }
    }
"""

import os
import sys
from enum import Enum

# Allow running this file directly (python3 mcp_server/server.py) by adding
# the repo root to sys.path so `import md2pdf` resolves regardless of CWD.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("md2pdf_mcp")
except (ImportError, ModuleNotFoundError):
    from mcp.server.mcpserver import MCPServer
    mcp = MCPServer("md2pdf_mcp")
from pydantic import BaseModel, Field

from md2pdf import (
    check_tools,
    convert_latex,
    convert_simple,
    detect_latex_needed,
    probe_latex_template,
)


class ConversionMode(str, Enum):
    """Which backend to use for the conversion."""
    SIMPLE = "simple"
    LATEX = "latex"
    AUTO = "auto"


class ConvertInput(BaseModel):
    model_config = {"str_strip_whitespace": True, "extra": "forbid"}

    markdown: str = Field(
        ...,
        description=(
            "The Markdown source to convert. Supports standard Markdown plus, "
            "in LaTeX mode, math ($...$, $$...$$) and fenced callout divs "
            "(::: {.callout} ... ::: for an amber PTR-style box, "
            "::: {.answer} ... ::: for a green summary box)."
        ),
        min_length=1,
    )
    output_path: str = Field(
        ...,
        description=(
            "Absolute (or CWD-relative) filesystem path to write the PDF to, "
            "e.g. '/home/user/output.pdf'. Parent directory must exist."
        ),
        min_length=1,
    )
    mode: ConversionMode = Field(
        default=ConversionMode.AUTO,
        description=(
            "'simple' = pandoc+wkhtmltopdf (fast, plain styling). "
            "'latex' = pandoc+pdflatex (native math, colored section headings, "
            "tcolorbox callout/answer boxes). "
            "'auto' = detect from content (math or callout divs -> latex, "
            "else simple) and fall back to simple if latex isn't available."
        ),
    )
    margin_mm: int = Field(
        default=20,
        description="Page margin in millimeters, applied on all four sides.",
        ge=0,
        le=100,
    )


@mcp.tool(
    name="convert_markdown_to_pdf",
    annotations={
        "title": "Convert Markdown to PDF",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def convert_markdown_to_pdf(params: ConvertInput) -> str:
    """Convert Markdown text to a PDF file on disk.

    Two rendering backends are available. 'simple' (pandoc -> HTML ->
    wkhtmltopdf) is fast and handles plain prose, lists, and tables. 'latex'
    (pandoc -> LaTeX -> pdflatex, via this project's styled template) adds
    native math rendering, color-coded section headings, and callout/answer
    boxes for exam-sheet / formula-sheet style documents — use it whenever
    the content has math or you want the styled-box look. 'auto' picks
    whichever the content needs and is available.

    Args:
        params (ConvertInput): markdown text, output_path, mode, margin_mm.

    Returns:
        str: A short confirmation message naming the file written and which
        mode was actually used (relevant when mode='auto'), or a message
        starting with "Error:" describing what went wrong and how to fix it.
    """
    output_path = os.path.abspath(os.path.expanduser(params.output_path))
    parent = os.path.dirname(output_path) or "."
    if not os.path.isdir(parent):
        return f"Error: output directory does not exist: {parent}"

    tools = check_tools()
    mode = params.mode

    if mode == ConversionMode.AUTO:
        needed, reason = detect_latex_needed(params.markdown)
        latex_available = tools["pandoc"] and tools["pdflatex"]
        mode = ConversionMode.LATEX if (needed and latex_available) else ConversionMode.SIMPLE
        auto_note = f" (auto-detected: {reason or 'no math/callouts found'})"
    else:
        auto_note = ""

    if mode == ConversionMode.SIMPLE:
        if not (tools["pandoc"] and tools["wkhtmltopdf"]):
            missing = [t for t in ("pandoc", "wkhtmltopdf") if not tools[t]]
            return (
                f"Error: simple mode needs {', '.join(missing)} on PATH. "
                f"Install with your OS package manager (e.g. "
                f"'sudo apt install {' '.join(missing)}')."
            )
        try:
            convert_simple(params.markdown, output_path, params.margin_mm)
        except RuntimeError as e:
            return f"Error: conversion failed.\n{e}"
        return f"Saved PDF to {output_path} (mode: simple{auto_note})."

    # mode == LATEX
    if not (tools["pandoc"] and tools["pdflatex"]):
        missing = [t for t in ("pandoc", "pdflatex") if not tools[t]]
        return (
            f"Error: LaTeX mode needs {', '.join(missing)} on PATH. "
            f"Install pandoc and a LaTeX distribution (e.g. TeX Live: "
            f"'sudo apt install pandoc texlive-latex-extra')."
        )
    ok, detail = probe_latex_template()
    if not ok:
        return (
            "Error: pdflatex is installed but the styled template failed to "
            f"compile — a required LaTeX package is likely missing. Detail:\n{detail}"
        )
    try:
        convert_latex(params.markdown, output_path, params.margin_mm)
    except RuntimeError as e:
        return f"Error: conversion failed.\n{e}"
    return f"Saved PDF to {output_path} (mode: latex{auto_note})."


class DetectInput(BaseModel):
    model_config = {"str_strip_whitespace": True, "extra": "forbid"}

    markdown: str = Field(
        ...,
        description="The Markdown text to inspect for math notation or callout divs.",
        min_length=1,
    )


@mcp.tool(
    name="detect_latex_needed",
    annotations={
        "title": "Detect Whether Markdown Needs LaTeX Rendering",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def detect_latex_needed_tool(params: DetectInput) -> str:
    """Check whether Markdown text contains math or callout syntax that only
    the LaTeX backend renders properly, without converting anything.

    Useful before calling convert_markdown_to_pdf with an explicit mode, to
    decide which one to pick (though mode='auto' does this automatically).

    Args:
        params (DetectInput): the markdown text to inspect.

    Returns:
        str: "needed: <reason>" if LaTeX rendering is recommended, or
        "not needed" if the content is plain prose/lists/tables.
    """
    needed, reason = detect_latex_needed(params.markdown)
    return f"needed: {reason}" if needed else "not needed"


@mcp.tool(
    name="check_conversion_dependencies",
    annotations={
        "title": "Check md2pdf Conversion Dependencies",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def check_conversion_dependencies() -> str:
    """Report which conversion backends are actually usable on this machine.

    Checks that pandoc/wkhtmltopdf/pdflatex are on PATH, and additionally
    does a real dry-run compile of the LaTeX template to confirm every
    required package (tcolorbox, mathpazo, etc.) resolves — a bare PATH
    check can't catch a missing LaTeX package.

    Returns:
        str: A short report of which modes ('simple', 'latex') are ready to
        use, and which tools or packages are missing if either is not.
    """
    tools = check_tools()
    lines = []

    simple_ok = tools["pandoc"] and tools["wkhtmltopdf"]
    if simple_ok:
        lines.append("simple: ready (pandoc + wkhtmltopdf found)")
    else:
        missing = [t for t in ("pandoc", "wkhtmltopdf") if not tools[t]]
        lines.append(f"simple: NOT ready — missing: {', '.join(missing)}")

    if tools["pandoc"] and tools["pdflatex"]:
        ok, detail = probe_latex_template()
        if ok:
            lines.append("latex: ready (pandoc + pdflatex found, template compiles)")
        else:
            lines.append(f"latex: NOT ready — template compile failed: {detail}")
    else:
        missing = [t for t in ("pandoc", "pdflatex") if not tools[t]]
        lines.append(f"latex: NOT ready — missing: {', '.join(missing)}")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
