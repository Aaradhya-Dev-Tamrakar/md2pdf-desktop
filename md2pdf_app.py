#!/usr/bin/env python3
"""
md2pdf Studio — Desktop Application
High-fidelity Markdown to PDF Converter with KaTeX Math, Mermaid Graphs & GFM Callouts.

Conversion logic lives in md2pdf/core.py, shared with the MCP server in
mcp_server/server.py so the desktop app, Claude, and Antigravity all produce
identical vector PDF outputs.
"""

import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from md2pdf import (
    check_tools,
    convert_auto,
    convert_latex,
    convert_sidebar,
    convert_simple,
    detect_latex_needed,
    detect_sidebar_needed,
    find_chromium,
    probe_latex_template,
)

# ---------------------------------------------------------------------------
# UI Theme Colors (ui-ux-pro-max Deep Slate Palette)
# ---------------------------------------------------------------------------
THEME = {
    "bg_root": "#080c16",
    "bg_card": "#0f172a",
    "bg_card_hover": "#1e293b",
    "bg_input": "#0b1120",
    "border": "#1e293b",
    "border_highlight": "#38bdf8",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "accent_blue": "#2563eb",
    "accent_cyan": "#0284c7",
    "accent_emerald": "#10b981",
    "accent_amber": "#f59e0b",
    "accent_rose": "#f43f5e",
    "accent_purple": "#8b5cf6",
}


class MD2PDFStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("md2pdf Studio — Markdown to Vector PDF")
        self.root.geometry("980x760")
        self.root.minsize(820, 620)
        self.root.configure(bg=THEME["bg_root"])

        self.md_path = None
        self.last_output_pdf = None

        self._check_deps()
        self._configure_styles()
        self._build_ui()

    def _check_deps(self):
        self.have = check_tools()
        self.sidebar_ok = self.have.get("pandoc", False) and self.have.get("chromium", False)
        self.simple_ok = self.have.get("pandoc", False) and self.have.get("wkhtmltopdf", False)

        self.latex_detail = None
        if self.have.get("pandoc", False) and self.have.get("pdflatex", False):
            ok, detail = probe_latex_template()
            self.latex_ok = ok
            self.latex_detail = detail
        else:
            self.latex_ok = False

        self.missing_deps = [t for t, ok in self.have.items() if not ok]

    def _configure_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Frame styles
        self.style.configure("Root.TFrame", background=THEME["bg_root"])
        self.style.configure("Card.TFrame", background=THEME["bg_card"], relief="flat")
        self.style.configure("Header.TFrame", background=THEME["bg_root"])

        # Label styles
        self.style.configure(
            "Title.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 14, "bold"),
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_muted"],
            font=("Segoe UI", 9),
        )
        self.style.configure(
            "CardTitle.TLabel",
            background=THEME["bg_card"],
            foreground=THEME["text_secondary"],
            font=("Segoe UI", 9, "bold"),
        )
        self.style.configure(
            "Badge.TLabel",
            background=THEME["bg_card"],
            foreground=THEME["text_muted"],
            font=("Consolas", 8),
            padding=(4, 2),
        )
        self.style.configure(
            "Status.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_secondary"],
            font=("Segoe UI", 9),
        )

        # Radio button styles
        self.style.configure(
            "Card.TRadiobutton",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            font=("Segoe UI", 9, "bold"),
            focuscolor=THEME["bg_card"],
        )
        self.style.map(
            "Card.TRadiobutton",
            foreground=[("active", THEME["accent_cyan"])],
            background=[("active", THEME["bg_card"])],
        )

        # Checkbutton styles
        self.style.configure(
            "Card.TCheckbutton",
            background=THEME["bg_card"],
            foreground=THEME["text_secondary"],
            font=("Segoe UI", 9),
            focuscolor=THEME["bg_card"],
        )
        self.style.map(
            "Card.TCheckbutton",
            foreground=[("active", THEME["text_primary"])],
            background=[("active", THEME["bg_card"])],
        )

        # Primary Button style
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=THEME["accent_blue"],
            foreground="#ffffff",
            padding=(16, 8),
            relief="flat",
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8"), ("pressed", "#1e40af")],
            foreground=[("active", "#ffffff")],
        )

        # Secondary Button style
        self.style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 9),
            background=THEME["bg_card_hover"],
            foreground=THEME["text_primary"],
            padding=(10, 5),
            relief="flat",
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#334155"), ("pressed", "#1e293b")],
            foreground=[("active", "#ffffff")],
        )

        # Combobox style
        self.style.configure(
            "Dark.TCombobox",
            background=THEME["bg_input"],
            foreground="#ffffff",
            fieldbackground=THEME["bg_input"],
            darkcolor=THEME["border"],
            lightcolor=THEME["border"],
        )

    def _build_ui(self):
        # 1. Header Bar
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x", padx=16, pady=(12, 6))

        title_box = ttk.Frame(header, style="Header.TFrame")
        title_box.pack(side="left")

        ttk.Label(title_box, text="⚡ md2pdf Studio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_box,
            text="High-Fidelity Markdown → Vector PDF (Chromium · KaTeX · Mermaid · GFM Alerts)",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        # Telemetry Badges on Top Right
        badge_box = ttk.Frame(header, style="Header.TFrame")
        badge_box.pack(side="right", pady=4)

        self._create_telemetry_pill(badge_box, "Chromium", self.sidebar_ok, "Chrome/Edge available")
        self._create_telemetry_pill(badge_box, "Pandoc", self.have.get("pandoc", False), "Pandoc available")
        self._create_telemetry_pill(badge_box, "LaTeX", self.latex_ok, "pdflatex + tcolorbox", optional=True)
        self._create_telemetry_pill(badge_box, "wkhtml", self.simple_ok, "wkhtmltopdf", optional=True)

        # 2. Action Toolbar
        toolbar = tk.Frame(self.root, bg=THEME["bg_card"], bd=1, relief="solid")
        toolbar.pack(fill="x", padx=16, pady=4)

        tool_inner = ttk.Frame(toolbar, style="Card.TFrame")
        tool_inner.pack(fill="x", padx=8, pady=6)

        ttk.Button(
            tool_inner,
            text="📂 Open .md File",
            command=self.open_file,
            style="Secondary.TButton",
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            tool_inner,
            text="📋 Paste Clipboard",
            command=self.paste_clipboard,
            style="Secondary.TButton",
        ).pack(side="left", padx=6)

        ttk.Button(
            tool_inner,
            text="🧹 Clear",
            command=self.clear_editor,
            style="Secondary.TButton",
        ).pack(side="left", padx=6)

        self.file_label = tk.Label(
            tool_inner,
            text="📄 Scratchpad / No file loaded",
            bg=THEME["bg_input"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9),
            padx=10,
            pady=4,
            relief="solid",
            bd=1,
        )
        self.file_label.pack(side="left", padx=10)

        # 3. Conversion Mode Card
        mode_card = tk.Frame(self.root, bg=THEME["bg_card"], bd=1, relief="solid")
        mode_card.pack(fill="x", padx=16, pady=6)

        mode_inner = ttk.Frame(mode_card, style="Card.TFrame")
        mode_inner.pack(fill="x", padx=10, pady=8)

        ttk.Label(mode_inner, text="ENGINE SELECTION", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 4))

        default_mode = "sidebar_light" if self.sidebar_ok else ("latex" if self.latex_ok else "simple")
        self.mode_var = tk.StringVar(value=default_mode)

        row_modes = ttk.Frame(mode_inner, style="Card.TFrame")
        row_modes.pack(fill="x")

        ttk.Radiobutton(
            row_modes,
            text="☀️ Sidebar Light (Print Paper + KaTeX + SVG Mermaid)",
            variable=self.mode_var,
            value="sidebar_light",
            style="Card.TRadiobutton",
        ).pack(side="left", padx=(0, 14))

        ttk.Radiobutton(
            row_modes,
            text="🌙 Sidebar Dark (IDE Dark Theme)",
            variable=self.mode_var,
            value="sidebar_dark",
            style="Card.TRadiobutton",
        ).pack(side="left", padx=14)


        ttk.Radiobutton(
            row_modes,
            text="📐 LaTeX Formal (pdflatex)",
            variable=self.mode_var,
            value="latex",
            style="Card.TRadiobutton",
        ).pack(side="left", padx=14)

        ttk.Radiobutton(
            row_modes,
            text="⚡ Simple (wkhtmltopdf)",
            variable=self.mode_var,
            value="simple",
            style="Card.TRadiobutton",
        ).pack(side="left", padx=14)

        # Auto-detect notification pill
        self.auto_detect_var = tk.BooleanVar(value=True)
        row_detect = ttk.Frame(mode_inner, style="Card.TFrame")
        row_detect.pack(fill="x", pady=(6, 0))

        ttk.Checkbutton(
            row_detect,
            text="Auto-detect engine from content",
            variable=self.auto_detect_var,
            style="Card.TCheckbutton",
        ).pack(side="left")

        self.detect_label = tk.Label(
            row_detect,
            text="Ready to detect syntax",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8, "italic"),
        )
        self.detect_label.pack(side="left", padx=12)

        # 4. Markdown Editor Frame
        editor_card = tk.Frame(self.root, bg=THEME["bg_card"], bd=1, relief="solid")
        editor_card.pack(fill="both", expand=True, padx=16, pady=4)

        self.text = scrolledtext.ScrolledText(
            editor_card,
            wrap="word",
            font=("Consolas", 10),
            bg=THEME["bg_input"],
            fg="#f8fafc",
            insertbackground=THEME["accent_cyan"],
            selectbackground="#1e3a8a",
            selectforeground="#ffffff",
            bd=0,
            padx=10,
            pady=10,
            undo=True,
        )
        self.text.pack(fill="both", expand=True, padx=2, pady=2)
        self._detect_after_id = None
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<KeyRelease>", self._update_stats)

        # Editor Statistics Ribbon
        self.stats_bar = tk.Label(
            editor_card,
            text="Lines: 0  •  Words: 0  •  Characters: 0",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8),
            anchor="e",
            padx=10,
            pady=2,
        )
        self.stats_bar.pack(fill="x")

        # 5. Export Footer
        footer = tk.Frame(self.root, bg=THEME["bg_card"], bd=1, relief="solid")
        footer.pack(fill="x", padx=16, pady=(6, 12))

        footer_inner = ttk.Frame(footer, style="Card.TFrame")
        footer_inner.pack(fill="x", padx=12, pady=8)

        # Left options
        opts_box = ttk.Frame(footer_inner, style="Card.TFrame")
        opts_box.pack(side="left")

        tk.Label(
            opts_box,
            text="Page Margins:",
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(0, 6))

        self.margin_var = tk.StringVar(value="14mm")
        margin_combo = ttk.Combobox(
            opts_box,
            textvariable=self.margin_var,
            values=["10mm", "14mm", "20mm", "0.5in", "0.75in"],
            width=7,
        )
        margin_combo.pack(side="left", padx=4)

        self.open_pdf_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opts_box,
            text="Open PDF after export",
            variable=self.open_pdf_var,
            style="Card.TCheckbutton",
        ).pack(side="left", padx=16)

        # Right CTA
        cta_box = ttk.Frame(footer_inner, style="Card.TFrame")
        cta_box.pack(side="right")

        self.open_folder_btn = ttk.Button(
            cta_box,
            text="📁 Show in Folder",
            command=self.open_output_folder,
            style="Secondary.TButton",
            state="disabled",
        )
        self.open_folder_btn.pack(side="left", padx=(0, 8))

        self.convert_btn = ttk.Button(
            cta_box,
            text="🚀 Export to PDF",
            command=self.convert,
            style="Primary.TButton",
        )
        self.convert_btn.pack(side="right")

        # 6. Status Bar
        self.status = tk.Label(
            self.root,
            text="● Ready",
            bg=THEME["bg_root"],
            fg=THEME["accent_emerald"],
            font=("Segoe UI", 9),
            anchor="w",
            padx=20,
        )
        self.status.pack(fill="x", pady=(0, 6))

    def _create_telemetry_pill(self, parent, name, is_ok, tooltip_text, optional=False):
        color = THEME["accent_emerald"] if is_ok else (THEME["text_muted"] if optional else THEME["accent_rose"])
        symbol = "●" if is_ok else "○"
        pill = tk.Label(
            parent,
            text=f"{symbol} {name}",
            bg=THEME["bg_card"],
            fg=color,
            font=("Segoe UI", 8, "bold"),
            padx=6,
            pady=2,
            bd=1,
            relief="solid",
        )
        pill.pack(side="left", padx=3)

    def _on_text_modified(self, _event=None):
        self.text.edit_modified(False)
        self._update_stats()
        if self._detect_after_id is not None:
            self.root.after_cancel(self._detect_after_id)
        self._detect_after_id = self.root.after(350, self._run_auto_detect)

    def _update_stats(self, _event=None):
        raw_content = self.text.get("1.0", "end-1c")
        lines = len(raw_content.splitlines()) if raw_content else 0
        words = len(raw_content.split())
        chars = len(raw_content)
        self.stats_bar.config(text=f"Lines: {lines:,}  •  Words: {words:,}  •  Chars: {chars:,}")

    def _run_auto_detect(self):
        self._detect_after_id = None
        if not self.auto_detect_var.get():
            self.detect_label.config(text="", fg=THEME["text_muted"])
            return

        content = self.text.get("1.0", "end")
        if not content.strip():
            self.detect_label.config(text="Empty document", fg=THEME["text_muted"])
            return

        needed_sidebar, reason_sidebar = detect_sidebar_needed(content)
        if needed_sidebar and self.sidebar_ok:
            self.detect_label.config(
                text=f"⚡ Auto-detected: {reason_sidebar} → Sidebar Mode selected",
                fg=THEME["accent_cyan"],
            )
            current_mode = self.mode_var.get()
            if current_mode not in ("sidebar_dark", "sidebar_light"):
                self.mode_var.set("sidebar_dark")
            return

        needed_latex, reason_latex = detect_latex_needed(content)
        if needed_latex:
            if self.latex_ok:
                self.detect_label.config(
                    text=f"📐 Auto-detected: {reason_latex} → LaTeX Mode selected",
                    fg=THEME["accent_emerald"],
                )
                self.mode_var.set("latex")
            else:
                self.detect_label.config(
                    text=f"⚠ Detected {reason_latex}, but LaTeX compiler is missing",
                    fg=THEME["accent_amber"],
                )
        else:
            self.detect_label.config(text="Plain document → Standard conversion", fg=THEME["text_muted"])

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown Files", "*.md *.markdown *.txt"), ("All Files", "*.*")],
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.md_path = path
        self.file_label.config(text=f"📄 {os.path.basename(path)}")
        self._update_stats()
        self._run_auto_detect()

    def paste_clipboard(self):
        try:
            clip = self.root.clipboard_get()
            if clip:
                self.text.insert(tk.INSERT, clip)
                self._update_stats()
                self._run_auto_detect()
        except Exception:
            pass

    def clear_editor(self):
        if messagebox.askyesno("Clear Editor", "Clear all content from the editor?"):
            self.text.delete("1.0", "end")
            self.md_path = None
            self.file_label.config(text="📄 Scratchpad / No file loaded")
            self._update_stats()
            self._run_auto_detect()

    def open_output_folder(self):
        if self.last_output_pdf and os.path.exists(self.last_output_pdf):
            folder = os.path.dirname(os.path.abspath(self.last_output_pdf))
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])

    def convert(self):
        mode = self.mode_var.get()

        if mode in ("sidebar_dark", "sidebar_light") and not self.sidebar_ok:
            messagebox.showerror(
                "Missing Dependencies",
                "Sidebar mode requires Pandoc and Google Chrome or Microsoft Edge.",
            )
            return
        if mode == "simple" and not self.simple_ok:
            messagebox.showerror("Missing Dependencies", "Simple mode requires Pandoc and wkhtmltopdf.")
            return
        if mode == "latex" and not self.latex_ok:
            messagebox.showerror("Missing Dependencies", "LaTeX mode requires Pandoc and pdflatex.")
            return

        md_content = self.text.get("1.0", "end").strip()
        if not md_content:
            messagebox.showwarning("Empty Content", "No Markdown content found in the editor to convert.")
            return

        margin = self.margin_var.get().strip() or "14mm"

        default_name = "output.pdf"
        initial_dir = None
        if self.md_path:
            default_name = os.path.splitext(os.path.basename(self.md_path))[0] + ".pdf"
            initial_dir = os.path.dirname(self.md_path)

        save_path = filedialog.asksaveasfilename(
            title="Export PDF to",
            defaultextension=".pdf",
            initialdir=initial_dir,
            initialfile=default_name,
            filetypes=[("PDF Documents", "*.pdf")],
        )
        if not save_path:
            return

        self.status.config(text="⏳ Converting document to high-fidelity PDF...", fg=THEME["accent_amber"])
        self.convert_btn.config(state="disabled")
        self.root.update_idletasks()

        start_time = time.time()
        try:
            if mode == "sidebar_dark":
                convert_sidebar(md_content, save_path, margin=margin, theme="dark")
            elif mode == "sidebar_light":
                convert_sidebar(md_content, save_path, margin=margin, theme="light")
            elif mode == "latex":
                convert_latex(md_content, save_path, margin=margin)
            else:
                convert_simple(md_content, save_path, margin=margin)

            elapsed = time.time() - start_time
            file_size_kb = os.path.getsize(save_path) / 1024
            size_str = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{file_size_kb/1024:.2f} MB"

            self.last_output_pdf = save_path
            self.open_folder_btn.config(state="normal")
            self.status.config(
                text=f"✅ Exported in {elapsed:.1f}s: {os.path.basename(save_path)} ({size_str})",
                fg=THEME["accent_emerald"],
            )

            if self.open_pdf_var.get():
                if sys.platform == "win32":
                    os.startfile(save_path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", save_path])
                else:
                    subprocess.run(["xdg-open", save_path])

        except Exception as e:
            self.status.config(text=f"❌ Export failed: {str(e)[:100]}", fg=THEME["accent_rose"])
            messagebox.showerror("Export Failed", str(e))
        finally:
            self.convert_btn.config(state="normal")


def main():
    root = tk.Tk()
    app = MD2PDFStudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
