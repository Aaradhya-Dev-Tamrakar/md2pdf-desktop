# Markdown → PDF Converter (`md2pdf-desktop`)

An intelligent, publication-grade Markdown to PDF converter with native mathematical typesetting, automatic ASCII grid table transformation, colored callout boxes, and full UTF-8 Unicode sanitization.

Two ways to use this:

- **Desktop app** (`md2pdf_app.py`) — a responsive Tkinter GUI you run and drive by hand.
- **MCP server** (`mcp_server/server.py`) — the same conversion exposed as Model Context Protocol (MCP) tools, callable by Claude (Desktop/Code) or Google Antigravity.
- **PowerShell Sync Engine** (`sync.ps1`) — automated git synchronization, pre-commit secret scanning, and toolchain health validation.

Both surfaces share a unified conversion core (`md2pdf/core.py`), ensuring identical, textbook-grade output everywhere.

---

## Conversion Modes

- **LaTeX (Default & Recommended)** — `pandoc` (MD → LaTeX, via `md2pdf/templates/styled.latex`) → `pdflatex`.
  - Native vector math equations (matrices, sums, Greek characters, calculus, logic proofs).
  - Colored heading tiers (Red H1, Amber H2, Green H3).
  - `tcolorbox`-styled callout and answer boxes.
  - Automatically wraps long code/verbatim lines with `fvextra` (`fontsize=\footnotesize, breaklines=true, breakanywhere=true`) so contents **never overflow the page margins**.
  - Default **12mm narrow margins** providing 186mm of clean printable width on A4.
- **Simple** — `pandoc` (MD → HTML) → `wkhtmltopdf` (HTML → PDF, UTF-8 explicit).
  - Uses full-width responsive print CSS (zero container margin doubling).
  - Includes `--webtex` so mathematical formulas render as vector images instead of unrendered LaTeX code.
- **Auto** — Content-aware backend selector. Scans Markdown for mathematical symbols (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`) or callout divs (`::: {.callout}`) and automatically selects LaTeX mode if dependencies exist, with seamless fallback to Simple mode.

---

## Intelligent Preprocessing Pipeline (`clean_markdown_for_pdf`)

Before sending Markdown to `pdflatex` or `wkhtmltopdf`, `md2pdf` automatically sanitizes the document:

1. **ASCII Grid Tables $\to$ Native Markdown Tables**:
   Detects ASCII box tables (`+---+---+` and `| ... |`) and transforms them into responsive Markdown pipe tables. In LaTeX mode, these compile into clean `booktabs` / `longtable` environments that wrap text within cell columns.
2. **Unicode Math & Logic Symbol Translation**:
   Converts isolated Unicode logic and Greek glyphs that cause `pdflatex` 8-bit crashes into proper LaTeX math mode (`∨` $\to$ `$\lor$`, `∧` $\to$ `$\land$`, `¬` $\to$ `$\neg$`, `∞` $\to$ `$\infty$`, `ε` $\to$ `$\varepsilon$`, `θ` $\to$ `$\theta$`, `·` $\to$ `$\cdot$`).
3. **Mermaid Flowchart Blocks**:
   Automatically detects ```` ```mermaid ```` code blocks, sanitizes inner node labels, and wraps them into styled callout diagram blocks (`::: {.callout}`).
4. **Emoji Normalization**:
   Replaces 4-byte SMP emojis that cause missing tofu boxes or TeX fatal errors with clean text badges (`[OK]`, `[Target]`, `[Folder]`, `[Warning]`).
5. **LaTeX Delimiter Normalization**:
   Normalizes LLM escaped math delimiters (`\\(` $\to$ `$`, `\\[` $\to$ `$$`).
6. **Corrupted Encoding Stripping**:
   Safely replaces `\ufffd` replacement characters with hyphens.

---

## Requirements & Toolchain

- **Python 3.8+**
- **pandoc** (required for both modes)
- **pdflatex** — LaTeX distribution (TeX Live or MiKTeX). Required packages: `amsmath`, `amssymb`, `booktabs`, `longtable`, `xcolor`, `enumitem`, `mathpazo`, `tcolorbox`, `fancyvrb`, `fvextra`, `calc`, `graphicx`, `caption`, `titlesec`, `hyperref`.
- **wkhtmltopdf** (Simple mode fallback)
- Desktop app only: `tkinter`
- MCP server only: `pip install -r requirements.txt` (`mcp[cli]<2`, `pydantic`)

### Installation

**Windows** (via [Chocolatey](https://chocolatey.org)):
```powershell
choco install pandoc wkhtmltopdf
# For LaTeX mode, install TeX Live or MiKTeX:
choco install miktex
```

**macOS** (via Homebrew):
```bash
brew install pandoc wkhtmltopdf
brew install --cask mactex-no-gui
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install pandoc wkhtmltopdf texlive-latex-extra texlive-fonts-recommended python3-tk
```

---

## Automated Git & Health Sync (`sync.ps1`)

The repository includes an automated synchronization script matching the Super-NLM git engine:

```powershell
# Routine synchronization: pull, security scan, auto-generate conventional commit, and push
.\sync.ps1

# Run toolchain telemetry and compile probe on styled.latex
.\sync.ps1 -CheckTools

# Display repository health and commits ahead/behind
.\sync.ps1 -Status

# Dry-run preview without modifying git state
.\sync.ps1 -WhatIf

# Custom commit message
.\sync.ps1 -m "feat(core): enhance table parser"
```

---

## Option A: Desktop App

```powershell
python md2pdf_app.py
```

- Live dependency checking and real template probe compilation at startup.
- Real-time content scanning for math notation.
- Configurable margin input (defaults to narrow **12mm**).
- Direct file open and conversion output logging.

---

## Option B: MCP Server (Claude, Antigravity)

Install dependencies:
```powershell
pip install -r requirements.txt
```

### Tools Exposed

1. **`convert_markdown_to_pdf`** — `{markdown, output_path, mode: "latex"|"simple"|"auto", margin_mm: 12}` → Converts Markdown and writes PDF to disk.
2. **`detect_latex_needed`** — `{markdown}` → Detects if LaTeX mode is required.
3. **`check_conversion_dependencies`** — Checks status of `pandoc`, `wkhtmltopdf`, `pdflatex`, and compiles a probe test.

### Configure in Google Antigravity / Claude Desktop

In `mcp_config.json`:
```json
{
  "mcpServers": {
    "md2pdf": {
      "command": "python",
      "args": ["F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/mcp_server/server.py"]
    }
  }
}
```

---

## Callout Boxes (LaTeX mode)

Wrap paragraphs in fenced divs for colored callout boxes:

```markdown
::: {.callout}
**Note:** Formulas like $W = \sum_{k=1}^M S_k S_k^T - M \cdot I_n$ are typeset natively.
:::

::: {.answer}
**Final Result:** The empty clause ($\square$) confirms the theorem.
:::
```

---

## Repository Structure

- [`md2pdf/core.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf/core.py) — Core conversion pipelines, ASCII table parser, and Markdown cleaner.
- [`md2pdf/templates/styled.latex`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf/templates/styled.latex) — Production Pandoc LaTeX template with `fvextra` wrapping, narrow margins, and color schemes.
- [`md2pdf/templates/callout-boxes.lua`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf/templates/callout-boxes.lua) — Lua filter converting `.callout` and `.answer` divs into LaTeX `tcolorbox`.
- [`md2pdf_app.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf_app.py) — Tkinter GUI desktop interface.
- [`mcp_server/server.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/mcp_server/server.py) — FastMCP server for AI agent workflows.
- [`sync.ps1`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/sync.ps1) — Automated sync, secret scanner, and health verification engine.
