"""
md2pdf.core — shared Markdown -> PDF conversion logic.

This module contains the exact conversion pipelines used by the desktop app
(md2pdf_app.py) and the MCP server (mcp_server/server.py), so both surfaces
behave identically. No Tkinter or MCP imports here — pure stdlib + regex.
"""

import os
import re
import shutil
import subprocess
import tempfile

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEX_TEMPLATE = os.path.join(PACKAGE_DIR, "templates", "styled.latex")
LUA_FILTER = os.path.join(PACKAGE_DIR, "templates", "callout-boxes.lua")

# ---------------------------------------------------------------------------
# Content-based LaTeX-need detection
# ---------------------------------------------------------------------------
_DISPLAY_MATH = re.compile(r"\$\$.+?\$\$", re.S)
_INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)(?!\s)([^$\n]+?)(?<!\s)\$(?!\$)")
_PAREN_MATH = re.compile(r"\\\(.+?\\\)", re.S)
_BRACKET_MATH = re.compile(r"\\\[.+?\\\]", re.S)
_CURRENCY_ONLY = re.compile(r"[\d,.\s]+")
_CALLOUT_PATTERN = re.compile(r":::\s*\{\.(callout|answer)\}")


def _has_inline_math(md_content: str) -> bool:
    # Reject inline $...$ spans that are just bare currency amounts, e.g.
    # "price is $5 and $10 total", so plain prose doesn't force LaTeX mode.
    for m in _INLINE_MATH.finditer(md_content):
        if not _CURRENCY_ONLY.fullmatch(m.group(1)):
            return True
    return False


def detect_latex_needed(md_content: str):
    """Return (needed: bool, reason: str | None) — whether this Markdown uses
    math or callout divs that only the LaTeX backend renders properly."""
    if _CALLOUT_PATTERN.search(md_content):
        return True, "callout/answer box"
    if _DISPLAY_MATH.search(md_content) or _has_inline_math(md_content):
        return True, "math notation"
    if _PAREN_MATH.search(md_content) or _BRACKET_MATH.search(md_content):
        return True, "math notation"
    return False, None


# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------
def check_tools():
    """Return {"pandoc": bool, "wkhtmltopdf": bool, "pdflatex": bool}."""
    return {t: shutil.which(t) is not None for t in ("pandoc", "wkhtmltopdf", "pdflatex")}


def probe_latex_template():
    """Actually compile a trivial doc through templates/styled.latex to
    confirm every LaTeX package it needs resolves. Returns (ok, detail)."""
    if not os.path.isfile(LATEX_TEMPLATE):
        return False, f"Missing template: {LATEX_TEMPLATE}"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            md_file = os.path.join(tmp, "probe.md")
            pdf_file = os.path.join(tmp, "probe.pdf")
            with open(md_file, "w", encoding="utf-8") as f:
                f.write("# Probe\n\nHello $x^2$.\n")
            cmd = [
                "pandoc", md_file,
                "--template", LATEX_TEMPLATE,
                "--pdf-engine", "pdflatex",
                "-V", "margin=20",
                "-o", pdf_file,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, result.stderr.strip()[-800:]
            return True, None
    except Exception as e:
        return False, str(e)


DEFAULT_CSS = """
<style>
body { font-family: Georgia, 'Times New Roman', serif; font-size: 12pt; line-height: 1.55;
       color: #1a1a1a; max-width: 720px; margin: 0 auto; padding: 10px 20px; }
h1 { font-size: 18pt; text-align: center; margin-bottom: 4px; }
h2 { font-size: 13pt; border-bottom: 1px solid #999; padding-bottom: 4px; margin-top: 22px; }
h3 { font-size: 12pt; margin-top: 16px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0 12px 0; padding-left: 22px; }
li { margin-bottom: 4px; }
hr { border: none; border-top: 1px solid #ccc; margin: 14px 0; }
strong { color: #111; }
code { background: #f2f2f2; padding: 1px 4px; border-radius: 3px; font-size: 10.5pt; }
pre { background: #f2f2f2; padding: 10px; border-radius: 4px; overflow-x: auto; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
th { background: #f2f2f2; }
</style>
"""


# ---------------------------------------------------------------------------
# Conversion pipelines
# ---------------------------------------------------------------------------
def convert_simple(md_content: str, save_path: str, margin: int = 20) -> None:
    """Markdown -> PDF via pandoc (MD -> HTML) -> wkhtmltopdf (HTML -> PDF).
    Raises RuntimeError with the tool's stderr on failure.
    """
    with tempfile.TemporaryDirectory() as tmp:
        md_file = os.path.join(tmp, "doc.md")
        html_file = os.path.join(tmp, "doc.html")

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        result = subprocess.run(
            ["pandoc", md_file, "-o", html_file, "--standalone"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pandoc failed:\n{result.stderr}")

        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        html = html.replace("</head>", DEFAULT_CSS + "</head>")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        result = subprocess.run(
            [
                "wkhtmltopdf", "--encoding", "utf-8",
                "--margin-top", f"{margin}mm", "--margin-bottom", f"{margin}mm",
                "--margin-left", f"{margin}mm", "--margin-right", f"{margin}mm",
                html_file, save_path,
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"wkhtmltopdf failed:\n{result.stderr}")


def convert_latex(md_content: str, save_path: str, margin: int = 20) -> None:
    """Markdown -> PDF via pandoc's LaTeX writer + pdflatex, using the
    custom styled.latex template (colored heading tiers, tcolorbox
    callouts, booktabs tables, native math). Supports fenced divs:
      ::: {.callout} ... :::   -> amber PTR-style box
      ::: {.answer}  ... :::   -> green answer-summary box
    Raises RuntimeError with the tool's stderr on failure.
    """
    if not os.path.isfile(LATEX_TEMPLATE):
        raise RuntimeError(f"Missing template: {LATEX_TEMPLATE}")

    with tempfile.TemporaryDirectory() as tmp:
        md_file = os.path.join(tmp, "doc.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        filter_args = ["--lua-filter", LUA_FILTER] if os.path.isfile(LUA_FILTER) else []
        cmd = (
            ["pandoc", md_file]
            + filter_args
            + [
                "--template", LATEX_TEMPLATE,
                "--pdf-engine", "pdflatex",
                "-V", f"margin={margin}",
                "-o", save_path,
            ]
        )

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"pandoc/pdflatex failed:\n{result.stderr}")


def convert_auto(md_content: str, save_path: str, margin: int = 20):
    """Pick LaTeX mode if the content needs it and it's available, else
    Simple mode. Returns the mode actually used ("latex" or "simple")."""
    needed, _reason = detect_latex_needed(md_content)
    tools = check_tools()
    latex_available = tools["pandoc"] and tools["pdflatex"]
    if needed and latex_available:
        convert_latex(md_content, save_path, margin)
        return "latex"
    convert_simple(md_content, save_path, margin)
    return "simple"
