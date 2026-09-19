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


def ascii_grid_to_markdown(block: str) -> str:
    """Converts an ASCII grid table (with +---+ borders) into a native Markdown pipe table."""
    lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
    if not lines or not lines[0].startswith('+') or not lines[-1].startswith('+'):
        return block
    rows = []
    is_grid = True
    for line in lines:
        if re.match(r'^\+[-+=|]+\+$', line):
            continue
        elif line.startswith('|') and line.endswith('|'):
            cells = [c.strip() for c in line[1:-1].split('|')]
            rows.append(cells)
        else:
            is_grid = False
            break
    if not is_grid or len(rows) < 1:
        return block

    # Check if first row is a banner/title row (1 single cell)
    if len(rows) > 1 and len(rows[0]) == 1 and len(rows[1]) > 1:
        title = rows[0][0]
        header = rows[1]
        data_rows = rows[2:]
        prefix = f"**{title}**\n\n" if title else ""
    else:
        prefix = ""
        header = rows[0]
        data_rows = rows[1:]

    col_count = len(header)
    md = [prefix + "| " + " | ".join(header) + " |"]
    md.append("|" + "|".join([":---" for _ in range(col_count)]) + "|")
    for r in data_rows:
        while len(r) < col_count:
            r.append("")
        md.append("| " + " | ".join(r[:col_count]) + " |")
    return "\n".join(md)


def clean_markdown_for_pdf(md_content: str, mode: str = "auto") -> str:
    """
    Sanitizes and normalizes markdown for high-quality, bug-free PDF rendering:
    1. Automatically transforms ASCII grid tables (+---+ borders) into native Markdown tables.
    2. Replaces Unicode emojis that crash pdflatex or render as missing squares.
    3. Converts Unicode box-drawing characters and geometric symbols into clean ASCII.
    4. Formats Mermaid graph blocks into readable callout diagram blocks with sanitized characters.
    5. Converts isolated Unicode math/logic symbols (¬, ∨, ∧, ∞, ε, θ, ·) into LaTeX math mode.
    6. Normalizes escaped LaTeX delimiters (\\( -> $, \\[ -> $$).
    7. Strips corrupted encoding artifacts (e.g. \\ufffd).
    """
    if not md_content:
        return ""

    text = md_content.replace('\ufffd', '-')

    # Convert ASCII grid code blocks into native Markdown pipe tables
    def _replace_ascii_tables(match):
        code_body = match.group(1).strip()
        lines = [l.strip() for l in code_body.splitlines() if l.strip()]
        if (
            lines
            and lines[0].startswith('+')
            and lines[-1].startswith('+')
            and all(l.startswith(('+', '|')) for l in lines)
        ):
            converted = ascii_grid_to_markdown(code_body)
            if converted != code_body:
                return converted
        return match.group(0)

    text = re.sub(
        r'```(?:text|ascii)?\s*\n(\+[-+=|]+\+\n.*?\n\+[-+=|]+\+)\s*\n```',
        _replace_ascii_tables,
        text,
        flags=re.DOTALL,
    )

    # Convert naked ASCII grid tables (not in code blocks)
    def _replace_naked_ascii_tables(match):
        table_text = match.group(1).strip()
        converted = ascii_grid_to_markdown(table_text)
        return "\n\n" + converted + "\n\n"

    text = re.sub(
        r'(?:^|\n)(\+[-+=|]+\+\n(?:[+|].*?\n)+\+[-+=|]+\+)(?=\n|$)',
        _replace_naked_ascii_tables,
        text,
    )

    # Common unicode and emoji normalization
    replacements = {
        '📂': '[Folder]', '📁': '[Folder]', '🎯': '[Target]', '🎬': '[Video]',
        '✅': '[OK]', '✔': '[OK]', '❌': '[X]', '⏳': '[Pending]', '🎉': '',
        '⚠️': '[Warning]', '•': '-', '—': '--', '–': '-',
        '“': '"', '”': '"', '‘': "'", '’': "'", '°': ' deg',
        '▲': '^', '▼': 'v', '►': '>', '◄': '<',
        '│': '|', '─': '-', '┌': '+', '┐': '+', '└': '+', '┘': '+',
        '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
        '□': '[ ]', '⌊': '[', '⌋': ']', '↓': 'v', '↑': '^',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Strip remaining 4-byte SMP emojis for LaTeX safety
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)

    # Convert Mermaid code fences to clean diagram callouts
    def _replace_mermaid(match):
        diagram_code = match.group(1).strip()
        # Clean logic & math symbols inside mermaid code block to ascii
        diagram_code = (
            diagram_code.replace('∨', ' OR ')
            .replace('∧', ' AND ')
            .replace('¬', '~')
            .replace('θ', 'theta')
            .replace('ε', 'eps')
            .replace('∞', 'inf')
        )
        return f"::: {{.callout}}\n**Diagram (Flowchart):**\n```\n{diagram_code}\n```\n:::"

    text = re.sub(r'```mermaid\s*\n(.*?)\n```', _replace_mermaid, text, flags=re.DOTALL)

    # Clean logic and math symbols outside mermaid
    text = text.replace('∨', r' $\lor$ ')
    text = text.replace('∧', r' $\land$ ')
    text = text.replace('¬', r' $\neg$ ')
    text = text.replace('∞', r' $\infty$ ')
    text = text.replace('ε', r' $\varepsilon$ ')
    text = text.replace('θ', r' $\theta$ ')
    text = text.replace('·', r' $\cdot$ ')

    # Normalize escaped LaTeX brackets from LLM outputs
    text = re.sub(r'\\\\\(', '$', text)
    text = re.sub(r'\\\\\)', '$', text)
    text = re.sub(r'\\\\\[', '$$', text)
    text = re.sub(r'\\\\\]', '$$', text)

    return text


DEFAULT_CSS = """
<style>
@page {
    size: a4 portrait;
    margin: 0;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1a1a1a;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}
h1 { font-size: 16pt; text-align: center; margin-bottom: 6px; color: #b21818; }
h2 { font-size: 13pt; border-bottom: 1.5px solid #b57c0a; padding-bottom: 3px; margin-top: 18px; color: #b57c0a; }
h3 { font-size: 11.5pt; margin-top: 14px; color: #1e6e3c; }
h4 { font-size: 10.5pt; margin-top: 10px; color: #333; }
p { margin: 5px 0; }
ul, ol { margin: 4px 0 8px 0; padding-left: 20px; }
li { margin-bottom: 3px; }
hr { border: none; border-top: 1px solid #ccc; margin: 12px 0; }
strong { color: #111; }
code { background: #f2f2f2; padding: 1px 4px; border-radius: 3px; font-family: Consolas, monospace; font-size: 8.5pt; }
pre { background: #f8f9fa; border: 1px solid #e2e8f0; padding: 8px 12px; border-radius: 4px; font-family: Consolas, monospace; font-size: 8pt; white-space: pre-wrap; word-wrap: break-word; word-break: break-word; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 8.5pt; table-layout: auto; word-wrap: break-word; }
th, td { border: 1px solid #cbd5e1; padding: 5px 8px; text-align: left; }
th { background: #f1f5f9; font-weight: 600; }
img { max-width: 100%; height: auto; }
.math.display { text-align: center; margin: 8px 0; overflow-x: auto; }
</style>
"""


# ---------------------------------------------------------------------------
# Conversion pipelines
# ---------------------------------------------------------------------------
def convert_simple(md_content: str, save_path: str, margin: int = 12) -> None:
    """Markdown -> PDF via pandoc (MD -> HTML) -> wkhtmltopdf (HTML -> PDF).
    Uses full-width responsive print CSS and --webtex for math rendering.
    Raises RuntimeError with the tool's stderr on failure.
    """
    cleaned = clean_markdown_for_pdf(md_content, mode="simple")
    with tempfile.TemporaryDirectory() as tmp:
        md_file = os.path.join(tmp, "doc.md")
        html_file = os.path.join(tmp, "doc.html")

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(cleaned)

        result = subprocess.run(
            ["pandoc", md_file, "-o", html_file, "--standalone", "--webtex"],
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
                "--enable-local-file-access",
                "--margin-top", f"{margin}mm", "--margin-bottom", f"{margin}mm",
                "--margin-left", f"{margin}mm", "--margin-right", f"{margin}mm",
                html_file, save_path,
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"wkhtmltopdf failed:\n{result.stderr}")


def convert_latex(md_content: str, save_path: str, margin: int = 12) -> None:
    """Markdown -> PDF via pandoc's LaTeX writer + pdflatex, using the
    custom styled.latex template (colored heading tiers, tcolorbox
    callouts, booktabs tables, native math).
    Automatically sanitizes unsupported Unicode glyphs prior to compilation.
    Raises RuntimeError with the tool's stderr on failure.
    """
    if not os.path.isfile(LATEX_TEMPLATE):
        raise RuntimeError(f"Missing template: {LATEX_TEMPLATE}")

    cleaned = clean_markdown_for_pdf(md_content, mode="latex")

    with tempfile.TemporaryDirectory() as tmp:
        md_file = os.path.join(tmp, "doc.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(cleaned)

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


def convert_auto(md_content: str, save_path: str, margin: int = 12):
    """Pick LaTeX mode if the content needs it and it's available, else
    Simple mode. Falls back to Simple mode on pdflatex failure."""
    needed, _reason = detect_latex_needed(md_content)
    tools = check_tools()
    latex_available = tools.get("pandoc") and tools.get("pdflatex")
    if needed and latex_available:
        try:
            convert_latex(md_content, save_path, margin)
            return "latex"
        except Exception:
            pass
    convert_simple(md_content, save_path, margin)
    return "simple"

