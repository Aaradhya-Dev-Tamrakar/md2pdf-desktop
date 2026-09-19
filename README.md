# Markdown → PDF Converter (Desktop App)

Two conversion modes, selectable in the app:

- **Simple** — pandoc (MD → HTML) → wkhtmltopdf (HTML → PDF, UTF-8 explicit). Fast, minimal deps.
- **LaTeX** — pandoc (MD → LaTeX, via `templates/styled.latex`) → pdflatex. Native math rendering, colored section headings, and `tcolorbox`-styled callout boxes — replicates the exam-sheet / formula-sheet style.

## Requirements
- Python 3.8+ (Tkinter included on Windows/macOS by default; on Linux: `sudo apt install python3-tk`)
- **pandoc** (required for both modes)
- **wkhtmltopdf** (Simple mode)
- **pdflatex** — from a LaTeX distribution (LaTeX mode). Needs the packages: `amsmath`, `amssymb`, `booktabs`, `longtable`, `xcolor`, `enumitem`, `mathpazo`, `tcolorbox`, `fancyvrb`, `hyperref`, `titlesec`. TeX Live and MiKTeX ship all of these by default.

## Install dependencies

**Windows** (with [Chocolatey](https://chocolatey.org)):
```
choco install pandoc wkhtmltopdf
```
Or download installers manually:
- https://pandoc.org/installing.html
- https://wkhtmltopdf.org/downloads.html

**macOS** (with Homebrew):
```
brew install pandoc wkhtmltopdf
```

**Linux (Debian/Ubuntu):**
```
sudo apt install pandoc wkhtmltopdf texlive-latex-extra python3-tk
```

## Run
```
python3 md2pdf_app.py
```

The app checks each mode's dependencies independently and warns on launch if anything required is missing; the mode selector defaults to LaTeX if `pdflatex` is available, otherwise Simple.

## Usage
1. Open a `.md` file, or paste/type Markdown directly into the editor.
2. Pick a conversion mode: **Simple** or **LaTeX**.
3. Adjust margins if needed (default 20mm).
4. Click **Convert to PDF…** and choose where to save.

### LaTeX mode: callout boxes
In LaTeX mode, wrap a paragraph in a fenced div to render it as a colored box (handled by `templates/callout-boxes.lua`):

```markdown
::: {.callout}
**PTR 1:** Important point to remember, with math like $\beta = 3.63$.
:::

::: {.answer}
Summary or final-answer text.
:::
```

`.callout` renders as an amber box (PTR/notes style); `.answer` renders as a green box (summary/answer style). Section headings (`#`, `##`, `###`) are auto-colored red/amber/green. All standard Markdown math (`$...$`, `$$...$$`) and tables render natively via pdflatex.

## Files
- `md2pdf_app.py` — the app
- `templates/styled.latex` — pandoc LaTeX template for LaTeX mode
- `templates/callout-boxes.lua` — pandoc Lua filter that turns `.callout`/`.answer` divs into styled boxes
