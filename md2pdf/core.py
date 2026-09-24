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
_MERMAID_PATTERN = re.compile(r"```mermaid\s*\n", re.IGNORECASE)
_GFM_ALERT_PATTERN = re.compile(
    r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", re.MULTILINE | re.IGNORECASE
)


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


def detect_sidebar_needed(md_content: str):
    """Return (needed: bool, reason: str | None) — whether this Markdown uses
    Mermaid diagrams, GFM alert boxes, or math that benefits from Chromium/KaTeX rendering."""
    if _MERMAID_PATTERN.search(md_content):
        return True, "Mermaid flowchart/diagram"
    if _GFM_ALERT_PATTERN.search(md_content):
        return True, "GFM alert box (> [!TIP])"
    needed_latex, reason_latex = detect_latex_needed(md_content)
    if needed_latex:
        return True, reason_latex
    return False, None


# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------
def find_chromium() -> str | None:
    """Locate installed Google Chrome or Microsoft Edge executable."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    for name in ("chrome", "google-chrome", "msedge", "chromium"):
        p = shutil.which(name)
        if p:
            return p
    return None


def check_tools():
    """Return tool availability dict."""
    return {
        "pandoc": shutil.which("pandoc") is not None,
        "wkhtmltopdf": shutil.which("wkhtmltopdf") is not None,
        "pdflatex": shutil.which("pdflatex") is not None,
        "chromium": find_chromium() is not None,
    }


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
                "-V", "margin=0.5in",
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
    color: #000000;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}
h1 { font-size: 16pt; text-align: center; margin-bottom: 6px; color: #000000; font-weight: 700; }
h2 { font-size: 13pt; border-bottom: 1.5px solid #000000; padding-bottom: 3px; margin-top: 18px; color: #000000; font-weight: 700; }
h3 { font-size: 11.5pt; margin-top: 14px; color: #000000; font-weight: 600; }
h4 { font-size: 10.5pt; margin-top: 10px; color: #000000; font-weight: 600; }
p { margin: 5px 0; color: #000000; }
ul, ol { margin: 4px 0 8px 0; padding-left: 20px; }
li { margin-bottom: 3px; }
hr { border: none; border-top: 1px solid #333333; margin: 12px 0; }
strong { color: #000000; font-weight: 700; }
code { background: #f4f4f4; border: 1px solid #ddd; padding: 1px 4px; border-radius: 2px; font-family: Consolas, monospace; font-size: 8.5pt; color: #000000; }
pre { background: #f8f8f8; border: 1px solid #333333; padding: 8px 12px; border-radius: 2px; font-family: Consolas, monospace; font-size: 8pt; white-space: pre-wrap; word-wrap: break-word; word-break: break-word; color: #000000; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 8.5pt; table-layout: auto; word-wrap: break-word; }
th, td { border: 1px solid #000000; padding: 5px 8px; text-align: left; }
th { background: #f0f0f0; font-weight: 600; color: #000000; }
img { max-width: 100%; height: auto; }
a { color: #000000; text-decoration: underline; }
.math.display { text-align: center; margin: 8px 0; overflow-x: auto; color: #000000; }
</style>
"""


def _normalize_margin(margin) -> str:
    """Normalizes margin parameter to a valid string with units (e.g. '0.5in', '12mm')."""
    s = str(margin).strip()
    if s.replace('.', '', 1).isdigit():
        return f"{s}mm"
    return s


# ---------------------------------------------------------------------------
# Conversion pipelines
# ---------------------------------------------------------------------------
def convert_simple(md_content: str, save_path: str, margin: str = "0.5in") -> None:
    """Markdown -> PDF via pandoc (MD -> HTML) -> wkhtmltopdf (HTML -> PDF).
    Uses full-width responsive print CSS, formal black & white palette, and --webtex.
    Raises RuntimeError with the tool's stderr on failure.
    """
    cleaned = clean_markdown_for_pdf(md_content, mode="simple")
    margin_str = _normalize_margin(margin)
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
                "--margin-top", margin_str, "--margin-bottom", margin_str,
                "--margin-left", margin_str, "--margin-right", margin_str,
                html_file, save_path,
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"wkhtmltopdf failed:\n{result.stderr}")


def convert_latex(md_content: str, save_path: str, margin: str = "0.5in") -> None:
    """Markdown -> PDF via pandoc's LaTeX writer + pdflatex, using the
    custom styled.latex template (formal black & white typography, monochrome
    tcolorbox callouts, booktabs tables, native math).
    Automatically sanitizes unsupported Unicode glyphs prior to compilation.
    Raises RuntimeError with the tool's stderr on failure.
    """
    if not os.path.isfile(LATEX_TEMPLATE):
        raise RuntimeError(f"Missing template: {LATEX_TEMPLATE}")

    cleaned = clean_markdown_for_pdf(md_content, mode="latex")
    margin_str = _normalize_margin(margin)

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
                "-V", f"margin={margin_str}",
                "-o", save_path,
            ]
        )
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"pandoc/pdflatex failed:\n{result.stderr}")


# ---------------------------------------------------------------------------
# Sidebar Mode Templates & Helpers (Chromium + KaTeX + Mermaid.js)
# ---------------------------------------------------------------------------
def transform_gfm_alerts(md_text: str) -> str:
    """Transforms GFM alert blocks (> [!TIP] ...) into structured HTML callouts."""
    alert_types = {
        "NOTE": {"color": "#3b82f6", "icon": "ℹ️"},
        "TIP": {"color": "#22c55e", "icon": "💡"},
        "IMPORTANT": {"color": "#a855f7", "icon": "📌"},
        "WARNING": {"color": "#eab308", "icon": "⚠️"},
        "CAUTION": {"color": "#ef4444", "icon": "🛑"},
    }

    pattern = re.compile(
        r'^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][ \t]*\n((?:^>.*$\n?)+)',
        re.MULTILINE | re.IGNORECASE
    )

    def _replace_alert(m):
        atype = m.group(1).upper()
        raw_body = m.group(2)
        body_lines = []
        for line in raw_body.splitlines():
            if line.startswith('> '):
                body_lines.append(line[2:])
            elif line.startswith('>'):
                body_lines.append(line[1:])
            else:
                body_lines.append(line)
        body_content = "\n".join(body_lines)
        cfg = alert_types.get(atype, alert_types["NOTE"])
        
        return (
            f'\n\n<div class="markdown-alert markdown-alert-{atype.lower()}">\n'
            f'<div class="markdown-alert-title">{cfg["icon"]} <strong>{atype}</strong></div>\n'
            f'<div class="markdown-alert-content">\n\n{body_content}\n\n</div>\n'
            f'</div>\n\n'
        )

    return pattern.sub(_replace_alert, md_text)


def prepare_mermaid_for_html(md_text: str) -> str:
    """Converts ```mermaid fences into <pre class="mermaid"> for Mermaid.js rendering."""
    def _replace_mermaid(m):
        code = m.group(1).strip()
        return f'\n\n<pre class="mermaid">\n{code}\n</pre>\n\n'

    return re.sub(r'```mermaid\s*\n(.*?)\n```', _replace_mermaid, md_text, flags=re.DOTALL)


def clean_markdown_for_sidebar(md_content: str) -> str:
    """Sanitizes and prepares markdown for modern Chromium/KaTeX/Mermaid rendering."""
    if not md_content:
        return ""
    text = md_content.replace('\ufffd', '-')
    text = transform_gfm_alerts(text)
    text = prepare_mermaid_for_html(text)

    # Normalize escaped brackets from LLMs
    text = re.sub(r'\\\\\(', '$', text)
    text = re.sub(r'\\\\\)', '$', text)
    text = re.sub(r'\\\\\[', '$$', text)
    text = re.sub(r'\\\\\]', '$$', text)
    return text


SIDEBAR_DARK_CSS = """
<style>
@page {
    size: a4 portrait;
    margin: 14mm 14mm 14mm 14mm;
}
:root {
    --bg-primary: #18181b;
    --bg-secondary: #27272a;
    --text-primary: #f4f4f5;
    --text-secondary: #a1a1aa;
    --border-color: #3f3f46;
    --accent: #38bdf8;
}
body {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    padding: 0;
    margin: 0;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 700;
    margin-top: 1.4em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
    break-after: avoid;
}
h1 { font-size: 18pt; border-bottom: 2px solid var(--border-color); padding-bottom: 6px; }
h2 { font-size: 14pt; border-bottom: 1px solid var(--border-color); padding-bottom: 4px; }
h3 { font-size: 12pt; color: #38bdf8 !important; }
h4 { font-size: 11pt; }
p, li {
    color: #e4e4e7 !important;
}
a {
    color: #38bdf8 !important;
    text-decoration: underline;
}
code {
    background: #27272a !important;
    color: #f43f5e !important;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: Consolas, "JetBrains Mono", monospace;
    font-size: 9pt;
}
pre {
    background: #27272a !important;
    border: 1px solid var(--border-color);
    padding: 10px 14px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: Consolas, "JetBrains Mono", monospace;
    font-size: 8.5pt;
    color: #f4f4f5 !important;
    page-break-inside: auto;
    break-inside: auto;
}
pre code {
    background: transparent !important;
    color: inherit !important;
    padding: 0;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 8.5pt;
    page-break-inside: auto;
    break-inside: auto;
}
th, td {
    border: 1px solid var(--border-color);
    padding: 6px 10px;
    text-align: left;
}
th {
    background-color: #27272a !important;
    color: #ffffff !important;
    font-weight: 600;
}
tr:nth-child(even) {
    background-color: rgba(255, 255, 255, 0.02) !important;
}
hr {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 18px 0;
}
blockquote {
    border-left: 4px solid var(--border-color);
    margin: 10px 0;
    padding: 6px 14px;
    color: var(--text-secondary);
    background: rgba(255, 255, 255, 0.02);
}
/* GFM Alerts */
.markdown-alert {
    border-left: 4px solid #3b82f6;
    border-radius: 4px;
    padding: 10px 14px;
    margin: 14px 0;
    background: rgba(255, 255, 255, 0.03);
    page-break-inside: auto;
    break-inside: auto;
}
.markdown-alert-title {
    font-weight: 700;
    margin-bottom: 6px;
    font-size: 9.5pt;
    display: flex;
    align-items: center;
    gap: 6px;
}
.markdown-alert-content {
    font-size: 9.5pt;
    color: #e4e4e7;
}
.markdown-alert-note { border-color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
.markdown-alert-note .markdown-alert-title { color: #60a5fa; }
.markdown-alert-tip { border-color: #22c55e; background: rgba(34, 197, 94, 0.1); }
.markdown-alert-tip .markdown-alert-title { color: #4ade80; }
.markdown-alert-important { border-color: #a855f7; background: rgba(168, 85, 247, 0.1); }
.markdown-alert-important .markdown-alert-title { color: #c084fc; }
.markdown-alert-warning { border-color: #eab308; background: rgba(234, 179, 8, 0.1); }
.markdown-alert-warning .markdown-alert-title { color: #facc15; }
.markdown-alert-caution { border-color: #ef4444; background: rgba(239, 68, 68, 0.1); }
.markdown-alert-caution .markdown-alert-title { color: #f87171; }

/* KaTeX Math */
.katex-display {
    margin: 10px 0;
    overflow-x: auto;
    page-break-inside: auto;
    break-inside: auto;
}
.katex {
    color: #f4f4f5 !important;
}

/* Mermaid Graphs */
.mermaid {
    display: flex;
    justify-content: center;
    background: #18181b !important;
    margin: 12px auto;
    padding: 8px;
    max-width: 100%;
    page-break-inside: auto;
    break-inside: auto;
}
.mermaid svg {
    max-width: 100% !important;
    max-height: 650px !important;
    height: auto !important;
}
</style>
"""

HTML_SIDEBAR_WRAPPER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Document</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  {css}
</head>
<body>
  {body}
  <script>
    mermaid.initialize({{
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {{
        darkMode: true,
        background: '#18181b',
        mainBkg: '#27272a',
        textColor: '#f4f4f5',
        lineColor: '#718096',
        primaryColor: '#27272a',
        primaryTextColor: '#f4f4f5',
        primaryBorderColor: '#52525b',
        secondaryColor: '#3f3f46',
        tertiaryColor: '#18181b'
      }}
    }});
    
    document.addEventListener("DOMContentLoaded", async function() {{
      renderMathInElement(document.body, {{
        delimiters: [
          {{left: "$$", right: "$$", display: true}},
          {{left: "$", right: "$", display: false}},
          {{left: "\\\\(", right: "\\\\)", display: false}},
          {{left: "\\\\[", right: "\\\\]", display: true}}
        ],
        throwOnError: false
      }});
      
      try {{
        await mermaid.run({{ querySelector: '.mermaid' }});
      }} catch (err) {{
        console.error("Mermaid render error:", err);
      }}
      window.__RENDER_COMPLETE = true;
    }});
  </script>
</body>
</html>
"""


def convert_sidebar(md_content: str, save_path: str, margin: str = "14mm", theme: str = "dark") -> None:
    """Converts Markdown to PDF using Headless Chromium + KaTeX + Mermaid.js.
    Provides identical visual fidelity to the modern IDE Markdown preview sidebar.
    """
    chrome = find_chromium()
    if not chrome:
        raise RuntimeError("Google Chrome or Microsoft Edge executable not found on system.")

    cleaned = clean_markdown_for_sidebar(md_content)

    with tempfile.TemporaryDirectory() as tmp:
        md_file = os.path.join(tmp, "doc.md")
        body_html_file = os.path.join(tmp, "body.html")
        final_html_file = os.path.join(tmp, "final.html")

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(cleaned)

        # Render markdown to HTML fragment via pandoc
        res = subprocess.run([
            "pandoc", md_file,
            "-f", "markdown+raw_html+pipe_tables",
            "-t", "html5",
            "-o", body_html_file,
        ], capture_output=True, text=True)

        if res.returncode != 0:
            raise RuntimeError(f"pandoc failed:\n{res.stderr}")

        with open(body_html_file, "r", encoding="utf-8") as f:
            body_content = f.read()

        full_html = HTML_SIDEBAR_WRAPPER.format(css=SIDEBAR_DARK_CSS, body=body_content)

        with open(final_html_file, "w", encoding="utf-8") as f:
            f.write(full_html)

        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--allow-running-insecure-content",
            "--virtual-time-budget=10000",
            "--run-all-compositor-stages-before-draw",
            "--no-pdf-header-footer",
            f"--print-to-pdf={save_path}",
            final_html_file,
        ]

        p_res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if not os.path.isfile(save_path) or os.path.getsize(save_path) == 0:
            raise RuntimeError(f"Chromium PDF generation failed:\n{p_res.stderr}")


def convert_auto(md_content: str, save_path: str, margin: str = "0.5in"):
    """Pick Sidebar/Chromium mode if the content needs it (Mermaid/GFM alerts/math)
    and Chromium is available. Otherwise falls back to LaTeX mode, then Simple mode."""
    tools = check_tools()
    needed_sidebar, _reason_sidebar = detect_sidebar_needed(md_content)

    if needed_sidebar and tools.get("chromium") and tools.get("pandoc"):
        try:
            convert_sidebar(md_content, save_path, margin=margin)
            return "sidebar"
        except Exception:
            pass

    needed_latex, _reason_latex = detect_latex_needed(md_content)
    latex_available = tools.get("pandoc") and tools.get("pdflatex")
    if needed_latex and latex_available:
        try:
            convert_latex(md_content, save_path, margin)
            return "latex"
        except Exception:
            pass

    convert_simple(md_content, save_path, margin)
    return "simple"


