# Markdown → PDF Converter (Desktop App)

Same conversion method used in chat: **pandoc** (MD → HTML) → **wkhtmltopdf** (HTML → PDF, UTF-8 explicit).

## Requirements
- Python 3.8+ (Tkinter included on Windows/macOS by default; on Linux: `sudo apt install python3-tk`)
- **pandoc**
- **wkhtmltopdf**

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
sudo apt install pandoc wkhtmltopdf python3-tk
```

## Run
```
python3 md2pdf_app.py
```

The app will warn you on launch if pandoc or wkhtmltopdf aren't found on PATH.

## Usage
1. Open a `.md` file, or paste/type Markdown directly into the editor.
2. Adjust margins if needed (default 20mm).
3. Click **Convert to PDF…** and choose where to save.
