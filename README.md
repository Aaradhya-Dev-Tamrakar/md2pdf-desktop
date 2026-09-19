# Markdown → PDF Converter

Two ways to use this:

- **Desktop app** (`md2pdf_app.py`) — a Tkinter GUI you run and drive by hand.
- **MCP server** (`mcp_server/server.py`) — the same conversion exposed as tools, callable by Claude (Desktop/Code) or Google Antigravity.

Both share one conversion core (`md2pdf/core.py`), so output is identical regardless of which one you use.

## Conversion modes

- **Simple** — pandoc (MD → HTML) → wkhtmltopdf (HTML → PDF, UTF-8 explicit). Fast, minimal deps.
- **LaTeX** — pandoc (MD → LaTeX, via `md2pdf/templates/styled.latex`) → pdflatex. Native math rendering, colored section headings, and `tcolorbox`-styled callout boxes — replicates the exam-sheet / formula-sheet style.
- **Auto** (MCP only, and the desktop app's "Auto-detect" checkbox) — scans the Markdown for math (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`) or `::: {.callout}` / `::: {.answer}` divs and picks LaTeX if found and available, else Simple. Bare currency like `$5 and $10` is recognized as prose, not math.

## Requirements

- Python 3.8+
- **pandoc** (required for both modes)
- **wkhtmltopdf** (Simple mode)
- **pdflatex** — from a LaTeX distribution (LaTeX mode). Needs: `amsmath`, `amssymb`, `booktabs`, `longtable`, `xcolor`, `enumitem`, `mathpazo`, `tcolorbox`, `fancyvrb`, `hyperref`, `titlesec`. TeX Live and MiKTeX ship all of these by default.
- Desktop app only: Tkinter (included on Windows/macOS by default; on Linux: `sudo apt install python3-tk`)
- MCP server only: `pip install -r requirements.txt` (installs `mcp[cli]<2` and `pydantic`)

### Install dependencies

**Windows** (with [Chocolatey](https://chocolatey.org)):

```choco install pandoc wkhtmltopdf

```

Or download installers manually: [pandoc](https://pandoc.org/installing.html), [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html). For LaTeX mode, install [MiKTeX](https://miktex.org/download).

**macOS** (with Homebrew):

```brew install pandoc wkhtmltopdf
brew install --cask mactex-no-gui   # for LaTeX mode
```

**Linux (Debian/Ubuntu):**

```sudo apt install pandoc wkhtmltopdf texlive-latex-extra python3-tk

```

---

## Option A: Desktop app

```python3 md2pdf_app.py

```

At launch the app checks each mode's dependencies for real, not just whether a binary is on PATH. LaTeX mode gets a live dry-run compile of the styled template — this catches a missing LaTeX package (e.g. `tcolorbox` not installed) before you hit Convert, not after; a failure shows the exact LaTeX error on hover. The mode selector defaults to LaTeX if that dry-run succeeds, otherwise Simple.

With **Auto-detect from content** checked (on by default), the app scans the editor as you type or load a file and switches to LaTeX mode automatically per the rule above.

Usage: open a `.md` file or paste Markdown into the editor, pick a mode (or let auto-detect choose), adjust margins if needed (default 20mm), and click **Convert to PDF…**.

---

## Option B: MCP server (Claude, Antigravity)

Install the server's dependencies once:

```pip install -r requirements.txt

```

Run it standalone to sanity-check it starts:

```python3 mcp_server/server.py

```

(It will sit waiting for stdio input — that's normal for an MCP server. Ctrl+C to stop.)

### Tools exposed

- **`convert_markdown_to_pdf`** — `{markdown, output_path, mode: "simple"|"latex"|"auto", margin_mm}` → converts and writes the PDF, returns a confirmation naming the file and mode used.
- **`detect_latex_needed`** — `{markdown}` → reports whether the content has math/callout syntax, without converting.
- **`check_conversion_dependencies`** — no input → reports which of Simple/LaTeX mode are actually usable right now (including the real LaTeX-package dry-run, not just a PATH check).

### Configure in Claude Desktop / Claude Code

Add to your MCP config (`claude_desktop_config.json`, or via `claude mcp add` for Claude Code):

```json
{
  "mcpServers": {
    "md2pdf": {
      "command": "python3",
      "args": ["/absolute/path/to/md2pdf-desktop/mcp_server/server.py"]
    }
  }
}
```

### Configure in Google Antigravity

Open the "..." menu in the Agent panel → **MCP Servers** → **Manage MCP Servers** → **View raw config**, and add the same shape to `mcp_config.json`:

```json
{
  "mcpServers": {
    "md2pdf": {
      "command": "python3",
      "args": ["/absolute/path/to/md2pdf-desktop/mcp_server/server.py"]
    }
  }
}
```

Save and restart Antigravity completely.

Use an absolute path in both configs — the server resolves its own templates relative to its file location, but the client needs the full path to launch it regardless of your shell's working directory.

---

## Callout boxes (LaTeX mode)

Wrap a paragraph in a fenced div to render it as a colored box:

```markdown
::: {.callout}
**PTR 1:** Important point to remember, with math like $\beta = 3.63$.
:::

::: {.answer}
Summary or final-answer text.
:::
```

`.callout` renders as an amber box (PTR/notes style); `.answer` renders as a green box (summary/answer style). Section headings (`#`, `##`, `###`) are auto-colored red/amber/green. All standard Markdown math and tables render natively via pdflatex.

## Files

- `md2pdf/core.py` — shared conversion logic (both backends, detection, dependency probing)
- `md2pdf/templates/styled.latex` — pandoc LaTeX template for LaTeX mode
- `md2pdf/templates/callout-boxes.lua` — pandoc Lua filter turning `.callout`/`.answer` divs into styled boxes
- `md2pdf_app.py` — Tkinter desktop app
- `mcp_server/server.py` — MCP server exposing the same conversion as tools
- `requirements.txt` — Python deps for the MCP server
