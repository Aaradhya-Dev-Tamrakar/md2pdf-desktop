#!/usr/bin/env python3
"""
Markdown to PDF Converter — Desktop App
Requires: pandoc, wkhtmltopdf (both must be installed and on PATH)
  - macOS:   brew install pandoc wkhtmltopdf
  - Windows: choco install pandoc wkhtmltopdf   (or download installers)
  - Linux:   sudo apt install pandoc wkhtmltopdf
"""

import os
import re
import shutil
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LATEX_TEMPLATE = os.path.join(SCRIPT_DIR, "templates", "styled.latex")
LUA_FILTER = os.path.join(SCRIPT_DIR, "templates", "callout-boxes.lua")

# Signals that the Markdown content actually needs the LaTeX backend:
# math ($...$, $$...$$, \(...\), \[...\]) or a styled callout/answer div.
_DISPLAY_MATH = re.compile(r"\$\$.+?\$\$", re.S)
_INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)(?!\s)([^$\n]+?)(?<!\s)\$(?!\$)")
_PAREN_MATH = re.compile(r"\\\(.+?\\\)", re.S)
_BRACKET_MATH = re.compile(r"\\\[.+?\\\]", re.S)
_CURRENCY_ONLY = re.compile(r"[\d,.\s]+")
_CALLOUT_PATTERN = re.compile(r":::\s*\{\.(callout|answer)\}")


def _has_inline_math(md_content):
    # Reject inline $...$ spans that are just bare currency amounts, e.g.
    # "price is $5 and $10 total", so plain prose doesn't force LaTeX mode.
    for m in _INLINE_MATH.finditer(md_content):
        if not _CURRENCY_ONLY.fullmatch(m.group(1)):
            return True
    return False


def detect_latex_needed(md_content):
    """Return (needed, reason) — whether this Markdown uses math or callout
    divs that only the LaTeX backend renders properly."""
    if _CALLOUT_PATTERN.search(md_content):
        return True, "callout/answer box"
    if _DISPLAY_MATH.search(md_content) or _has_inline_math(md_content):
        return True, "math notation"
    if _PAREN_MATH.search(md_content) or _BRACKET_MATH.search(md_content):
        return True, "math notation"
    return False, None


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


class MD2PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown → PDF Converter")
        self.root.geometry("760x640")
        self.md_path = None

        self._check_deps()
        self._build_ui()

    def _check_deps(self):
        self.have = {t: shutil.which(t) is not None for t in ("pandoc", "wkhtmltopdf", "pdflatex")}
        # Simple mode needs pandoc+wkhtmltopdf.
        self.simple_ok = self.have["pandoc"] and self.have["wkhtmltopdf"]
        # LaTeX mode needs pandoc+pdflatex AND the template's packages actually
        # installed (tcolorbox, mathpazo, etc.) — a bare `which pdflatex` can't
        # tell us that, so do a cheap real compile of the template on a stub doc.
        self.latex_detail = None
        if self.have["pandoc"] and self.have["pdflatex"]:
            ok, detail = self._probe_latex_template()
            self.latex_ok = ok
            self.latex_detail = detail
        else:
            self.latex_ok = False
        self.missing_deps = [t for t, ok in self.have.items() if not ok]

    def _probe_latex_template(self):
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

    def _add_tooltip(self, widget, text):
        tip = {"win": None}

        def show(_event):
            if tip["win"] is not None:
                return
            x = widget.winfo_rootx() + 10
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            win = tk.Toplevel(widget)
            win.wm_overrideredirect(True)
            win.wm_geometry(f"+{x}+{y}")
            ttk.Label(
                win, text=text, background="#333", foreground="white",
                wraplength=600, justify="left", padding=6,
            ).pack()
            tip["win"] = win

        def hide(_event):
            if tip["win"] is not None:
                tip["win"].destroy()
                tip["win"] = None

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        top = ttk.Frame(self.root)
        top.pack(fill="x", **pad)

        ttk.Button(top, text="Open .md File", command=self.open_file).pack(side="left")
        self.file_label = ttk.Label(top, text="No file loaded — paste or type Markdown below")
        self.file_label.pack(side="left", padx=10)

        if self.missing_deps:
            warn = ttk.Label(
                self.root,
                text=f"⚠ Missing tools: {', '.join(self.missing_deps)}. "
                     f"Simple mode needs pandoc+wkhtmltopdf; LaTeX mode needs pandoc+pdflatex.",
                foreground="#b00020",
                wraplength=720,
            )
            warn.pack(fill="x", padx=10, pady=(0, 6))
        elif self.have["pandoc"] and self.have["pdflatex"] and not self.latex_ok:
            warn = ttk.Label(
                self.root,
                text="⚠ pdflatex is installed but a required LaTeX package is missing "
                     "(e.g. tcolorbox) — LaTeX mode will fail. See detail on hover.",
                foreground="#b00020",
                wraplength=720,
            )
            warn.pack(fill="x", padx=10, pady=(0, 6))
            self._add_tooltip(warn, self.latex_detail or "Unknown LaTeX error")

        # Conversion mode selector
        mode_frame = ttk.LabelFrame(self.root, text="Conversion mode")
        mode_frame.pack(fill="x", padx=10, pady=(0, 6))
        self.mode_var = tk.StringVar(value="latex" if self.latex_ok else "simple")
        ttk.Radiobutton(
            mode_frame, text="Simple (HTML/CSS via wkhtmltopdf)",
            variable=self.mode_var, value="simple",
        ).pack(side="left", padx=(8, 4), pady=4)
        ttk.Radiobutton(
            mode_frame, text="LaTeX (styled boxes + native math via pdflatex)",
            variable=self.mode_var, value="latex",
        ).pack(side="left", padx=4, pady=4)

        self.auto_detect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            mode_frame, text="Auto-detect from content",
            variable=self.auto_detect_var,
        ).pack(side="left", padx=(16, 4), pady=4)

        self.detect_label = ttk.Label(mode_frame, text="", foreground="#0a6")
        self.detect_label.pack(side="left", padx=6)

        # Text editor
        editor_frame = ttk.LabelFrame(self.root, text="Markdown content")
        editor_frame.pack(fill="both", expand=True, padx=10, pady=6)
        self.text = scrolledtext.ScrolledText(editor_frame, wrap="word", font=("Consolas", 11))
        self.text.pack(fill="both", expand=True, padx=6, pady=6)
        self._detect_after_id = None
        self.text.bind("<<Modified>>", self._on_text_modified)

        # Margin controls
        margin_frame = ttk.Frame(self.root)
        margin_frame.pack(fill="x", padx=10, pady=(0, 6))
        ttk.Label(margin_frame, text="Margins (mm):").pack(side="left")
        self.margin_var = tk.StringVar(value="20")
        ttk.Entry(margin_frame, textvariable=self.margin_var, width=5).pack(side="left", padx=6)

        # Bottom bar
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=10)
        ttk.Button(bottom, text="Convert to PDF…", command=self.convert).pack(side="right")

        self.status = ttk.Label(self.root, text="Ready", foreground="#444")
        self.status.pack(fill="x", padx=10, pady=(0, 8))

    def _on_text_modified(self, _event=None):
        # Tk's <<Modified>> virtual event requires the flag to be cleared
        # manually, or it only ever fires once per widget lifetime.
        self.text.edit_modified(False)
        if self._detect_after_id is not None:
            self.root.after_cancel(self._detect_after_id)
        self._detect_after_id = self.root.after(400, self._run_auto_detect)

    def _run_auto_detect(self):
        self._detect_after_id = None
        if not self.auto_detect_var.get():
            self.detect_label.config(text="")
            return
        content = self.text.get("1.0", "end")
        needed, reason = detect_latex_needed(content)
        if needed:
            self.detect_label.config(text=f"Detected {reason} → LaTeX mode")
            if self.latex_ok:
                self.mode_var.set("latex")
            else:
                self.detect_label.config(
                    text=f"Detected {reason}, but LaTeX mode unavailable — see warning above",
                    foreground="#b00020",
                )
        else:
            self.detect_label.config(text="", foreground="#0a6")

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Select Markdown file",
            filetypes=[("Markdown files", "*.md *.markdown *.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.md_path = path
        self.file_label.config(text=os.path.basename(path))
        self._run_auto_detect()

    def convert(self):
        mode = self.mode_var.get()
        if mode == "simple" and not self.simple_ok:
            messagebox.showerror("Missing dependencies", "Simple mode needs: pandoc, wkhtmltopdf")
            return
        if mode == "latex" and not self.latex_ok:
            messagebox.showerror("Missing dependencies", "LaTeX mode needs: pandoc, pdflatex")
            return

        md_content = self.text.get("1.0", "end").strip()
        if not md_content:
            messagebox.showwarning("Empty content", "There is no Markdown content to convert.")
            return

        try:
            margin = int(self.margin_var.get())
        except ValueError:
            margin = 20

        default_name = "output.pdf"
        if self.md_path:
            default_name = os.path.splitext(os.path.basename(self.md_path))[0] + ".pdf"

        save_path = filedialog.asksaveasfilename(
            title="Save PDF as",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF files", "*.pdf")],
        )
        if not save_path:
            return

        self.status.config(text="Converting…")
        self.root.update_idletasks()

        try:
            if mode == "latex":
                self._run_conversion_latex(md_content, save_path, margin)
            else:
                self._run_conversion(md_content, save_path, margin)
            self.status.config(text=f"Saved: {save_path}")
            messagebox.showinfo("Done", f"PDF saved to:\n{save_path}")
        except Exception as e:
            self.status.config(text="Failed")
            messagebox.showerror("Conversion failed", str(e))

    def _run_conversion(self, md_content, save_path, margin):
        with tempfile.TemporaryDirectory() as tmp:
            md_file = os.path.join(tmp, "doc.md")
            html_file = os.path.join(tmp, "doc.html")

            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_content)

            # Markdown -> HTML via pandoc
            result = subprocess.run(
                ["pandoc", md_file, "-o", html_file, "--standalone"],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"pandoc failed:\n{result.stderr}")

            # Inject CSS
            with open(html_file, "r", encoding="utf-8") as f:
                html = f.read()
            html = html.replace("</head>", DEFAULT_CSS + "</head>")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html)

            # HTML -> PDF via wkhtmltopdf (UTF-8 explicit to handle en/em dashes etc.)
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

    def _run_conversion_latex(self, md_content, save_path, margin):
        """Markdown -> PDF via pandoc's LaTeX writer + pdflatex, using the
        custom styled.latex template (colored heading tiers, tcolorbox
        callouts, booktabs tables, native math). Supports fenced divs:
          ::: {.callout} ... :::   -> amber PTR-style box
          ::: {.answer}  ... :::   -> green answer-summary box
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


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except Exception:
        pass
    app = MD2PDFApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
