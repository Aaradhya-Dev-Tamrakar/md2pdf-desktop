# Markdown → PDF Converter (`md2pdf-desktop`)

An intelligent, publication-grade Markdown to PDF converter with native mathematical typesetting, full vector Mermaid diagrams, GitHub Flavored Markdown (GFM) alerts, automatic table formatting, and modern IDE sidebar visual fidelity.

Three operational surfaces:

- **Desktop Studio** ([`md2pdf_app.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf_app.py)) — A modern desktop GUI built with `ui-ux-pro-max` design standards, live toolchain telemetry, real-time syntax auto-detection, and document metrics.
- **MCP Server** ([`mcp_server/server.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/mcp_server/server.py)) — FastMCP server exposing headless conversion tools to Google Antigravity, Claude Code, and Claude Desktop.
- **PowerShell Sync Engine** ([`sync.ps1`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/sync.ps1)) — Automated git synchronization, pre-commit secret scanning, and toolchain health validation.

All surfaces share a unified conversion core ([`md2pdf/core.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf/core.py)), ensuring identical, textbook-grade output everywhere.

---

## 🚀 Conversion Engines

### 1. 🌟 Sidebar Mode (Default & Recommended)
**Pipeline:** `pandoc` (MD → HTML5 AST) → Injected KaTeX + Mermaid.js → Headless Chromium (Google Chrome / Microsoft Edge) → Vector PDF.

- **Visual Match**: Renders Markdown with visual fidelity matching the modern IDE Markdown preview sidebar (Google Antigravity, VS Code, GitHub).
- **Mermaid Vector Diagrams**: Renders ```` ```mermaid ```` flowcharts, sequence diagrams, and state charts directly into vector SVGs.
- **Crisp KaTeX Math**: Renders both inline `$ ... $` and display `$$ ... $$` formulas (matrices, fractions, Greek letters, integrals) without blurry bitmap rasterization.
- **GFM Alert Callouts**: Transforms `> [!TIP]`, `> [!NOTE]`, `> [!WARNING]`, `> [!IMPORTANT]`, and `> [!CAUTION]` into styled boxes with themed accent borders, background tints, and icons.
- **Dual Themes**:
  - **Light Mode (`theme="light"`, Default)**: Pure white canvas (`#ffffff`), dark slate typography (`#111827`), blue question accents (`#1d4ed8`), violet algorithm headers (`#7c3aed`), and light-themed diagram nodes. Ideal for physical paper printing.
  - **Dark Mode (`theme="dark"`)**: Deep zinc palette (`#18181b`) matching dark IDE preview panels.
- **Smart Page-Break Rules**: Prevents breaking inside math blocks, tables, code listings, and flowchart diagrams.
- **Zero Heavy TeX Overhead**: Uses the Google Chrome or Microsoft Edge executable already installed on your system.

### 2. 📐 LaTeX Formal Mode
**Pipeline:** `pandoc` (MD → LaTeX, via `md2pdf/templates/styled.latex`) → `pdflatex`.

- Native vector LaTeX typesetting with `mathpazo` Palatino typography.
- Monochrome `tcolorbox`-styled callouts (`::: {.callout}`, `::: {.answer}`) and `booktabs` tables.
- Hard line wrapping via `fvextra` (`fontsize=\footnotesize, breaklines=true`) preventing page overflows.
- Default 12.7mm (0.5 in) margins.

### 3. ⚡ Simple Mode
**Pipeline:** `pandoc` (MD → HTML) → `wkhtmltopdf`.

- Fast, lightweight HTML/CSS print engine with `--webtex` formula rendering.

### 4. 🧠 Auto Mode
Content-aware backend selector. Inspects Markdown content:
- If Mermaid diagrams or GFM alerts are detected $\to$ routes to **Sidebar** mode.
- If complex LaTeX math or callout divs are detected $\to$ routes to **Sidebar** (if Chromium present) or **LaTeX** (if `pdflatex` present).
- Otherwise falls back to **Simple** mode.

---

## 🎨 Desktop Studio GUI (`md2pdf_app.py`)

Run the desktop application:
```powershell
python md2pdf_app.py
```

### Studio Highlights
- **`ui-ux-pro-max` Dark Palette**: Deep canvas (`#080c16`), elevated card containers (`#0f172a`), subtle slate borders (`#1e293b`), and vibrant accents.
- **Toolchain Telemetry Badges**: Header pills showing live availability for `Chromium`, `Pandoc`, `LaTeX`, and `wkhtmltopdf`.
- **Dynamic Syntax Auto-Detector**: Automatically analyzes editor text and informs you why a specific engine was chosen.
- **Live Document Stats**: Tracks line count, word count, character count, and file size in real time.
- **Quick Action Bar**: `📂 Open .md File`, `📋 Paste Clipboard`, `🧹 Clear`, and active file badge.
- **Export Presets & Automation**: Quick margin dropdown (`10mm`, `14mm`, `20mm`, `0.5in`), auto-open PDF on completion, and `📁 Show in Folder` shortcut.

---

## 🤖 Model Context Protocol (MCP) Server

The MCP server allows AI coding agents in Google Antigravity or Claude Desktop to convert Markdown files to PDF autonomously.

### Start Standalone:
```powershell
python mcp_server/server.py
```

### Tools Exposed:
1. **`convert_markdown_to_pdf`**
   - `markdown` (string): Source Markdown text.
   - `output_path` (string): Target PDF file path.
   - `mode` (`"sidebar"` | `"latex"` | `"simple"` | `"auto"`, default: `"auto"`).
   - `margin_mm` (int, default: 12).
2. **`detect_latex_needed`**
   - Inspects Markdown and recommends the optimal backend.
3. **`check_conversion_dependencies`**
   - Health check returning tool status and availability.

### Configuration in Google Antigravity / Claude Desktop:
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

## 📦 System Requirements

- **Python 3.8+**
- **Pandoc** (required for all modes):
  ```powershell
  choco install pandoc
  ```
- **Chromium** (for Sidebar mode — either Google Chrome or Microsoft Edge):
  - Pre-installed on Windows (`msedge.exe` or `chrome.exe`).
- **Optional Tools**:
  - `pdflatex` (TeX Live or MiKTeX) for LaTeX Formal mode.
  - `wkhtmltopdf` for Simple mode.

---

## 🔄 Automated Git Synchronization (`sync.ps1`)

The repository includes a dedicated sync engine enforcing pre-commit secret scans and conventional commit standards:

```powershell
# Routine sync: pull, secret scan, commit, and push
.\sync.ps1

# Sync with custom commit message
.\sync.ps1 -m "feat(sidebar): add light paper print theme"

# Check conversion toolchains & probe template
.\sync.ps1 -CheckTools

# Safe pull only
.\sync.ps1 -PullOnly

# Dry run preview
.\sync.ps1 -WhatIf
```

---

## 📂 Repository Structure

- [`md2pdf/core.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf/core.py) — Core conversion pipelines (`convert_sidebar`, `convert_latex`, `convert_simple`, `convert_auto`), AST sanitizers, and CSS templates.
- [`md2pdf_app.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf_app.py) — Modern Tkinter desktop application (`md2pdf Studio`).
- [`mcp_server/server.py`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/mcp_server/server.py) — FastMCP server for AI agent workflows.
- [`md2pdf/templates/styled.latex`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf/templates/styled.latex) — Pandoc LaTeX template for formal print outputs.
- [`md2pdf/templates/callout-boxes.lua`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/md2pdf/templates/callout-boxes.lua) — Lua filter for LaTeX tcolorbox mapping.
- [`sync.ps1`](file:///F:/Aaradhya-Dev-Tamrakar/md2pdf-desktop/sync.ps1) — Automated sync engine and secret guard.
