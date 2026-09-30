#!/usr/bin/env python3
"""
md2pdf Studio — Desktop Application
High-fidelity Markdown to PDF Converter with KaTeX Math, Mermaid Graphs & GFM Callouts.

Conversion logic lives in md2pdf/core.py, shared with the MCP server in
mcp_server/server.py so the desktop app, Claude, and Antigravity all produce
identical vector PDF outputs.
"""

import os
import queue
import subprocess
import sys
import threading
import time
import ctypes


# ---------------------------------------------------------------------------
# Windows DPI Awareness
# ---------------------------------------------------------------------------
# Keep Tk from being bitmap-scaled by Windows on high-DPI displays. This must
# run before creating the Tk root window (and before importing tkinter).
def _enable_windows_dpi_awareness():
    """Enable per-monitor DPI awareness before Tkinter is imported.

    Windows APIs can report failure by returning False/an HRESULT rather than
    raising an exception, so check their return values before choosing a
    fallback.
    """
    if sys.platform != "win32":
        return

    try:
        set_context = ctypes.windll.user32.SetProcessDpiAwarenessContext
        set_context.argtypes = [ctypes.c_void_p]
        set_context.restype = ctypes.c_bool

        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 is the pseudo-handle -4.
        if set_context(ctypes.c_void_p(-4)):
            return
    except (AttributeError, OSError):
        pass

    try:
        # Windows 8.1 fallback: 0=unaware, 1=system-aware, 2=per-monitor-aware.
        set_awareness = ctypes.windll.shcore.SetProcessDpiAwareness
        set_awareness.argtypes = [ctypes.c_int]
        set_awareness.restype = ctypes.c_long
        if set_awareness(2) == 0:  # S_OK
            return
    except (AttributeError, OSError):
        pass

    try:
        # Last-resort fallback for older Windows: system-DPI aware (not
        # per-monitor), which is still preferable to bitmap-scaled unaware UI.
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


_enable_windows_dpi_awareness()

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
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = min(1180, max(900, int(screen_w * 0.84)))
        height = min(800, max(650, int(screen_h * 0.84)))
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(900, 620)
        self.root.configure(bg=THEME["bg_root"])

        self.md_path = None
        self.last_output_pdf = None
        self._conversion_in_progress = False
        self._conversion_queue = queue.Queue()
        self._conversion_after_id = None

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
        # Root shell
        shell = tk.Frame(self.root, bg=THEME["bg_root"])
        shell.pack(fill="both", expand=True, padx=18, pady=14)

        # --------------------------------------------------------------
        # Header
        # --------------------------------------------------------------
        header = tk.Frame(shell, bg=THEME["bg_root"])
        header.pack(fill="x", pady=(0, 10))

        brand = tk.Frame(header, bg=THEME["bg_root"])
        brand.pack(side="left", fill="x", expand=True)

        brand_line = tk.Frame(brand, bg=THEME["bg_root"])
        brand_line.pack(anchor="w")
        tk.Label(
            brand_line,
            text="md2pdf",
            bg=THEME["bg_root"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 19, "bold"),
        ).pack(side="left")
        tk.Label(
            brand_line,
            text="  STUDIO",
            bg=THEME["bg_root"],
            fg=THEME["accent_cyan"],
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", pady=(7, 0))

        tk.Label(
            brand,
            text="Markdown → reliable PDF, without the clutter.",
            bg=THEME["bg_root"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(1, 0))

        health = tk.Frame(header, bg=THEME["bg_root"])
        health.pack(side="right", pady=(5, 0))
        health_items = [
            ("Chromium", self.sidebar_ok),
            ("Pandoc", self.have.get("pandoc", False)),
            ("LaTeX", self.latex_ok),
            ("wkhtml", self.have.get("wkhtmltopdf", False)),
        ]
        for name, ok in health_items:
            tk.Label(
                health,
                text=("● " if ok else "○ ") + name,
                bg=THEME["bg_root"],
                fg=THEME["accent_emerald"] if ok else THEME["text_muted"],
                font=("Segoe UI", 8, "bold"),
            ).pack(side="left", padx=(0, 10))

        # --------------------------------------------------------------
        # Command bar
        # --------------------------------------------------------------
        command = tk.Frame(
            shell,
            bg=THEME["bg_card"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        command.pack(fill="x")

        command_left = tk.Frame(command, bg=THEME["bg_card"])
        command_left.pack(side="left", padx=7, pady=7)

        ttk.Button(command_left, text="New", command=self.new_document, style="Secondary.TButton").pack(side="left", padx=3)
        ttk.Button(command_left, text="Open", command=self.open_file, style="Secondary.TButton").pack(side="left", padx=3)
        ttk.Button(command_left, text="Paste", command=self.paste_clipboard, style="Secondary.TButton").pack(side="left", padx=3)
        ttk.Button(command_left, text="Clear", command=self.clear_editor, style="Secondary.TButton").pack(side="left", padx=3)

        self.file_label = tk.Label(
            command,
            text="Scratchpad · No file loaded",
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self.file_label.pack(side="left", padx=(12, 8), fill="x", expand=True)

        self.auto_detect_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            command,
            text="Smart detect",
            variable=self.auto_detect_var,
            command=self._run_auto_detect,
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["text_primary"],
            selectcolor=THEME["bg_card_hover"],
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            highlightthickness=0,
        ).pack(side="right", padx=(5, 8))

        # --------------------------------------------------------------
        # Main workspace: editor + export controls
        # --------------------------------------------------------------
        workspace = tk.PanedWindow(
            shell,
            orient="horizontal",
            bg=THEME["bg_root"],
            bd=0,
            sashwidth=7,
            sashrelief="flat",
            opaqueresize=True,
        )
        workspace.pack(fill="both", expand=True, pady=(10, 10))

        # Editor panel
        editor_card = tk.Frame(
            workspace,
            bg=THEME["bg_card"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        workspace.add(editor_card, minsize=560)

        editor_header = tk.Frame(editor_card, bg=THEME["bg_card"])
        editor_header.pack(fill="x", padx=15, pady=(13, 7))

        left_meta = tk.Frame(editor_header, bg=THEME["bg_card"])
        left_meta.pack(side="left")
        tk.Label(
            left_meta,
            text="MARKDOWN SOURCE",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left_meta,
            text="Write your document",
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(1, 0))

        editor_tools = tk.Frame(editor_header, bg=THEME["bg_card"])
        editor_tools.pack(side="right", pady=(7, 0))
        self.wrap_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            editor_tools,
            text="Wrap",
            variable=self.wrap_var,
            command=lambda: self.text.config(wrap="word" if self.wrap_var.get() else "none"),
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["text_primary"],
            selectcolor=THEME["bg_card_hover"],
            font=("Segoe UI", 8),
            relief="flat",
            bd=0,
            highlightthickness=0,
        ).pack(side="right")

        editor_shell = tk.Frame(
            editor_card,
            bg=THEME["bg_input"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        editor_shell.pack(fill="both", expand=True, padx=12)

        self.text = scrolledtext.ScrolledText(
            editor_shell,
            wrap="word",
            font=("Cascadia Mono", 11),
            bg=THEME["bg_input"],
            fg=THEME["text_primary"],
            insertbackground=THEME["accent_cyan"],
            selectbackground="#21477d",
            selectforeground=THEME["text_primary"],
            padx=17,
            pady=15,
            bd=0,
            relief="flat",
            highlightthickness=0,
            undo=True,
            maxundo=-1,
        )
        self.text.pack(fill="both", expand=True)

        self.text.tag_configure(
            "current_line",
            background="#0f1b2c",
        )

        self.editor_placeholder = tk.Label(
            editor_shell,
            text=(
                "Start with Markdown\n\n"
                "# Your title\n"
                "Write normally — headings, tables, code, math, Mermaid and alerts are supported.\n\n"
                "Tip: use Ctrl+O to open a .md file."
            ),
            bg=THEME["bg_input"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 10),
            justify="left",
            anchor="nw",
            padx=20,
            pady=22,
        )
        self.editor_placeholder.place(x=0, y=0, relwidth=1, relheight=1)
        self.editor_placeholder.bind("<Button-1>", lambda _e: self.text.focus_set())

        editor_footer = tk.Frame(editor_card, bg=THEME["bg_card"])
        editor_footer.pack(fill="x", padx=15, pady=(7, 11))
        self.stats_bar = tk.Label(
            editor_footer,
            text="Lines: 0  ·  Words: 0  ·  Characters: 0",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8),
        )
        self.stats_bar.pack(side="left")
        self.cursor_label = tk.Label(
            editor_footer,
            text="Ln 1, Col 1",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8),
        )
        self.cursor_label.pack(side="right")

        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<KeyRelease>", self._editor_event)
        self.text.bind("<ButtonRelease>", self._editor_event)
        self.text.edit_modified(False)

        # Export panel
        side = tk.Frame(
            workspace,
            bg=THEME["bg_card"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
            width=350,
        )
        workspace.add(side, minsize=330)

        side_body = tk.Frame(side, bg=THEME["bg_card"])
        side_body.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(
            side_body,
            text="EXPORT",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            side_body,
            text="PDF profile",
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(1, 2))
        tk.Label(
            side_body,
            text="Use Smart Detect for most documents, or choose a renderer explicitly.",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8),
            wraplength=305,
            justify="left",
        ).pack(anchor="w", pady=(0, 11))

        smart = tk.Frame(
            side_body,
            bg=THEME["bg_card_hover"],
            highlightbackground=THEME["accent_cyan"],
            highlightthickness=1,
        )
        smart.pack(fill="x")
        self.mode_var = tk.StringVar(value="auto")

        tk.Radiobutton(
            smart,
            variable=self.mode_var,
            value="auto",
            command=self._render_mode_cards,
            bg=THEME["bg_card_hover"],
            activebackground=THEME["bg_card_hover"],
            selectcolor=THEME["accent_blue"],
            relief="flat",
            bd=0,
            highlightthickness=0,
        ).pack(side="left", padx=(10, 2), pady=10)

        smart_copy = tk.Frame(smart, bg=THEME["bg_card_hover"])
        smart_copy.pack(side="left", fill="x", expand=True, padx=(2, 10), pady=9)
        tk.Label(
            smart_copy,
            text="Smart Detect",
            bg=THEME["bg_card_hover"],
            fg=THEME["text_primary"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        self.detect_label = tk.Label(
            smart_copy,
            text="Ready to inspect the document.",
            bg=THEME["bg_card_hover"],
            fg=THEME["accent_cyan"],
            font=("Segoe UI", 8),
            wraplength=260,
            justify="left",
        )
        self.detect_label.pack(anchor="w", pady=(3, 0))

        tk.Label(
            side_body,
            text="RENDERER",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(14, 7))

        cards = tk.Frame(side_body, bg=THEME["bg_card"])
        cards.pack(fill="x")
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        self._mode_cards = {}
        self._mode_card_labels = {}
        renderer_info = [
            ("sidebar_light", "Sidebar Light", "Print layout", self.sidebar_ok),
            ("sidebar_dark", "Sidebar Dark", "IDE-style output", self.sidebar_ok),
            ("latex", "LaTeX Formal", "Academic typesetting", self.latex_ok),
            ("simple", "Simple", "HTML PDF fallback", self.simple_ok),
        ]
        for i, (value, title, desc, available) in enumerate(renderer_info):
            card = tk.Frame(
                cards,
                bg=THEME["bg_input"],
                highlightbackground=THEME["border"],
                highlightthickness=1,
                cursor="hand2" if available else "arrow",
            )
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=3, pady=3)
            card.columnconfigure(0, weight=1)
            self._mode_cards[value] = card

            row = tk.Frame(card, bg=THEME["bg_input"])
            row.pack(fill="x", padx=9, pady=(8, 2))
            title_label = tk.Label(
                row,
                text=title,
                bg=THEME["bg_input"],
                fg=THEME["text_primary"] if available else THEME["text_muted"],
                font=("Segoe UI", 8, "bold"),
            )
            title_label.pack(side="left")
            tk.Label(
                row,
                text="●" if available else "○",
                bg=THEME["bg_input"],
                fg=THEME["accent_emerald"] if available else THEME["text_muted"],
                font=("Segoe UI", 7),
            ).pack(side="right")
            desc_label = tk.Label(
                card,
                text=desc,
                bg=THEME["bg_input"],
                fg=THEME["text_muted"],
                font=("Segoe UI", 7),
                anchor="w",
                justify="left",
            )
            desc_label.pack(fill="x", padx=9, pady=(0, 8))
            self._mode_card_labels[value] = (title_label, desc_label)

            if available:
                handler = lambda _e, v=value: self._select_mode(v)
                for widget in (card, row, title_label, desc_label):
                    widget.bind("<Button-1>", handler)

        tk.Frame(side_body, height=1, bg=THEME["border"]).pack(fill="x", pady=14)

        tk.Label(
            side_body,
            text="PDF SETTINGS",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        settings = tk.Frame(side_body, bg=THEME["bg_card"])
        settings.pack(fill="x", pady=(7, 0))

        tk.Label(
            settings,
            text="Margins",
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9),
        ).grid(row=0, column=0, sticky="w", pady=(0, 7))

        self.margin_var = tk.StringVar(value="14mm")
        ttk.Combobox(
            settings,
            textvariable=self.margin_var,
            values=["10mm", "14mm", "20mm", "0.5in", "0.75in"],
            state="readonly",
            width=9,
            style="Dark.TCombobox",
        ).grid(row=0, column=1, sticky="e", pady=(0, 7))

        tk.Label(
            settings,
            text="After export",
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            font=("Segoe UI", 9),
        ).grid(row=1, column=0, sticky="w")

        self.open_pdf_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            settings,
            text="Open PDF automatically",
            variable=self.open_pdf_var,
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["text_primary"],
            selectcolor=THEME["bg_card_hover"],
            font=("Segoe UI", 8),
            relief="flat",
            bd=0,
            highlightthickness=0,
        ).grid(row=1, column=1, sticky="e")

        tk.Frame(side_body, height=1, bg=THEME["border"]).pack(fill="x", pady=14)

        env_head = tk.Frame(side_body, bg=THEME["bg_card"])
        env_head.pack(fill="x")
        tk.Label(
            env_head,
            text="ENVIRONMENT",
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left")

        self.environment_expanded = False
        self.environment_button = tk.Button(
            env_head,
            text="Show",
            command=self._toggle_environment,
            bg=THEME["bg_card"],
            fg=THEME["accent_cyan"],
            activebackground=THEME["bg_card"],
            activeforeground=THEME["text_primary"],
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.environment_button.pack(side="right")

        self.environment_frame = tk.Frame(side_body, bg=THEME["bg_card"])

        env_summary = f"{sum(1 for ok in self.have.values() if ok)}/{len(self.have)} native tools detected"
        tk.Label(
            side_body,
            text=env_summary,
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(7, 0))

        # --------------------------------------------------------------
        # Bottom status / primary action
        # --------------------------------------------------------------
        bottom = tk.Frame(
            shell,
            bg=THEME["bg_card"],
            highlightbackground=THEME["border"],
            highlightthickness=1,
        )
        bottom.pack(fill="x")

        status_left = tk.Frame(bottom, bg=THEME["bg_card"])
        status_left.pack(side="left", fill="x", expand=True, padx=12, pady=9)

        self.status = tk.Label(
            status_left,
            text="Ready",
            bg=THEME["bg_card"],
            fg=THEME["accent_emerald"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self.status.pack(side="left")

        self.open_folder_btn = ttk.Button(
            bottom,
            text="Reveal output",
            command=self.open_output_folder,
            style="Secondary.TButton",
            state="disabled",
        )
        self.open_folder_btn.pack(side="right", padx=(0, 8), pady=8)

        self.convert_btn = ttk.Button(
            bottom,
            text="Export PDF",
            command=self.convert,
            style="Primary.TButton",
        )
        self.convert_btn.pack(side="right", padx=(0, 8), pady=8)

        self.progress = ttk.Progressbar(
            bottom,
            mode="indeterminate",
            length=85,
        )
        self.progress.pack(side="right", padx=(0, 5), pady=8)

        self._update_mode_cards()
        self._update_placeholder()
        self._update_cursor_status()

    def _make_status(self, parent, text, ok=True):
        return tk.Label(
            parent,
            text=("● " if ok else "○ ") + text,
            bg=THEME["bg_card"],
            fg=THEME["accent_emerald"] if ok else THEME["text_muted"],
            font=("Segoe UI", 8, "bold"),
        )

    def _editor_event(self, _event=None):
        self._update_stats()
        self._update_cursor_status()
        self._update_current_line()
        self._update_placeholder()

    def _update_placeholder(self):
        if not hasattr(self, "editor_placeholder"):
            return
        content = self.text.get("1.0", "end-1c")
        if content.strip():
            self.editor_placeholder.place_forget()
        else:
            self.editor_placeholder.place(x=0, y=0, relwidth=1, relheight=1)

    def _update_cursor_status(self):
        if not hasattr(self, "cursor_label"):
            return
        try:
            line, col = self.text.index(tk.INSERT).split(".")
            self.cursor_label.config(text=f"Ln {int(line):,}, Col {int(col) + 1:,}")
        except (tk.TclError, ValueError):
            pass

    def _update_current_line(self):
        if not hasattr(self, "text"):
            return
        try:
            self.text.tag_remove("current_line", "1.0", "end")
            line = self.text.index(tk.INSERT).split(".")[0]
            self.text.tag_add("current_line", f"{line}.0", f"{line}.0 lineend+1c")
        except tk.TclError:
            pass

    def _select_mode(self, mode):
        available = {
            "sidebar_light": self.sidebar_ok,
            "sidebar_dark": self.sidebar_ok,
            "latex": self.latex_ok,
            "simple": self.simple_ok,
        }.get(mode, False)
        if not available:
            self._set_status("That renderer is unavailable on this machine.", THEME["accent_amber"])
            return
        self.mode_var.set(mode)
        self._update_mode_cards()
        self._run_auto_detect()

    def _render_mode_cards(self):
        self._update_mode_cards()

    def _update_mode_cards(self):
        selected = self.mode_var.get() if hasattr(self, "mode_var") else ""
        for value, card in getattr(self, "_mode_cards", {}).items():
            active = value == selected
            card.configure(
                bg=THEME["bg_card_hover"] if active else THEME["bg_input"],
                highlightbackground=THEME["accent_cyan"] if active else THEME["border"],
            )
            for child in card.winfo_children():
                child.configure(bg=THEME["bg_card_hover"] if active else THEME["bg_input"])
                for nested in child.winfo_children():
                    nested.configure(bg=THEME["bg_card_hover"] if active else THEME["bg_input"])

    def _toggle_environment(self):
        self.environment_expanded = not self.environment_expanded
        if self.environment_expanded:
            self.environment_button.config(text="Hide")
            self.environment_frame.pack(fill="x", pady=(8, 0))
            for child in self.environment_frame.winfo_children():
                child.destroy()
            labels = {
                "pandoc": "Pandoc",
                "chromium": "Chromium",
                "pdflatex": "LaTeX",
                "wkhtmltopdf": "wkhtmltopdf",
            }
            for key, label in labels.items():
                ok = self.have.get(key, False)
                tk.Label(
                    self.environment_frame,
                    text=("● " if ok else "○ ") + label,
                    bg=THEME["bg_card"],
                    fg=THEME["accent_emerald"] if ok else THEME["text_muted"],
                    font=("Segoe UI", 8),
                    anchor="w",
                ).pack(anchor="w", pady=1)
        else:
            self.environment_button.config(text="Show")
            self.environment_frame.pack_forget()

    def new_document(self):
        self.text.delete("1.0", "end")
        self.md_path = None
        self.file_label.config(text="Scratchpad · No file loaded")
        self.stats_bar.config(text="Lines: 0  ·  Words: 0  ·  Characters: 0")
        self._set_status("New document", THEME["text_secondary"])
        self._update_placeholder()
        self._run_auto_detect()

    def _set_status(self, text, color):
        if hasattr(self, "status"):
            self.status.config(text=text, fg=color)

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
        self.file_label.config(text=os.path.basename(path))
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
            self.file_label.config(text="Scratchpad · No file loaded")
            self._update_stats()
            self._run_auto_detect()

    def open_output_folder(self):
        if self.last_output_pdf and os.path.exists(self.last_output_pdf):
            folder = os.path.dirname(os.path.abspath(self.last_output_pdf))
            self._open_path(folder)

    def convert(self):
        if self._conversion_in_progress:
            return

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

        # Snapshot all Tk state before handing work to the background thread.
        theme = "dark" if mode == "sidebar_dark" else "light"
        open_pdf_after = bool(self.open_pdf_var.get())
        renderer = {
            "sidebar_dark": "Sidebar Dark",
            "sidebar_light": "Sidebar Light",
            "latex": "LaTeX",
            "simple": "Simple",
        }[mode]

        self._conversion_in_progress = True
        self.convert_btn.config(state="disabled")
        self.status.config(
            text=f"⏳ Converting with {renderer}...",
            fg=THEME["accent_amber"],
        )

        worker = threading.Thread(
            target=self._convert_worker,
            args=(md_content, save_path, margin, mode, theme, open_pdf_after),
            daemon=True,
            name="md2pdf-conversion",
        )
        worker.start()
        self._conversion_after_id = self.root.after(100, self._poll_conversion)

    def _convert_worker(self, md_content, save_path, margin, mode, theme, open_pdf_after):
        start_time = time.time()
        try:
            if mode in ("sidebar_dark", "sidebar_light"):
                convert_sidebar(md_content, save_path, margin=margin, theme=theme)
            elif mode == "latex":
                convert_latex(md_content, save_path, margin=margin)
            else:
                convert_simple(md_content, save_path, margin=margin)

            file_size_kb = os.path.getsize(save_path) / 1024
            elapsed = time.time() - start_time
            self._conversion_queue.put({
                "ok": True,
                "save_path": save_path,
                "elapsed": elapsed,
                "file_size_kb": file_size_kb,
                "open_pdf": open_pdf_after,
            })
        except Exception as exc:
            self._conversion_queue.put({
                "ok": False,
                "error": str(exc),
            })

    def _poll_conversion(self):
        try:
            result = self._conversion_queue.get_nowait()
        except queue.Empty:
            self._conversion_after_id = self.root.after(100, self._poll_conversion)
            return

        self._conversion_after_id = None
        self._finish_conversion(result)

    def _finish_conversion(self, result):
        self._conversion_in_progress = False
        self.convert_btn.config(state="normal")

        if not result["ok"]:
            error = result["error"]
            self.status.config(
                text=f"❌ Export failed: {error[:100]}",
                fg=THEME["accent_rose"],
            )
            messagebox.showerror("Export Failed", error)
            return

        save_path = result["save_path"]
        elapsed = result["elapsed"]
        file_size_kb = result["file_size_kb"]
        size_str = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{file_size_kb/1024:.2f} MB"

        self.last_output_pdf = save_path
        self.open_folder_btn.config(state="normal")
        self.status.config(
            text=f"✅ Exported in {elapsed:.1f}s: {os.path.basename(save_path)} ({size_str})",
            fg=THEME["accent_emerald"],
        )

        if result["open_pdf"]:
            self._open_path(save_path)

    def _open_path(self, path):
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)


def main():
    _enable_windows_thread_dpi_awareness()
    root = tk.Tk()
    app = MD2PDFStudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
