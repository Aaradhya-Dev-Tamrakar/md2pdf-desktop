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

def _enable_windows_thread_dpi_awareness():
    """Set the current GUI thread to Per-Monitor V2 before Tk creates windows."""
    if sys.platform != "win32":
        return

    try:
        set_context = ctypes.windll.user32.SetThreadDpiAwarenessContext
        set_context.argtypes = [ctypes.c_void_p]
        set_context.restype = ctypes.c_void_p

        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = (HANDLE)-4.
        previous = set_context(ctypes.c_void_p(-4))
        if previous:
            return
    except (AttributeError, OSError, OverflowError):
        pass

    # Older Windows fallback: Per-Monitor V1.
    try:
        set_awareness = ctypes.windll.shcore.SetProcessDpiAwareness
        set_awareness.argtypes = [ctypes.c_int]
        set_awareness.restype = ctypes.c_long
        set_awareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except (AttributeError, OSError, OverflowError):
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
    """Desktop workspace for Markdown → PDF conversion."""

    ZOOM_STEPS = (80, 90, 100, 110, 120, 130, 140, 150)

    def __init__(self, root):
        self.root = root
        self.preferences_path = self._get_preferences_path()

        prefs = self._load_preferences()
        self.theme_mode = prefs.get("theme", "dark")
        self.accent_name = prefs.get("accent", "blue")
        self.zoom_percent = self._clamp_zoom(prefs.get("zoom", 100))

        self.root.title("md2pdf Studio")
        self.root.configure(bg="#0b0c0e")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.md_path = None
        self.last_output_pdf = None
        self.dirty = False
        self._conversion_in_progress = False
        self._conversion_queue = queue.Queue()
        self._conversion_after_id = None
        self._detect_after_id = None
        self._dpi_after_id = None
        self._current_dpi = 96
        self._build_snapshot = None

        self._configure_display_scaling(initial=True)
        self._configure_window()
        self._check_deps()
        self._configure_styles()
        self._build_ui()
        self._bind_shortcuts()
        self._update_document_state()
        self._update_editor_metrics()
        self._update_cursor_status()
        self._run_auto_detect()
        self._start_dpi_monitor()

    # ------------------------------------------------------------------
    # Preferences / scaling
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp_zoom(value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 100
        return min(MD2PDFStudioApp.ZOOM_STEPS, key=lambda x: abs(x - value))

    @staticmethod
    def _preferred_tk_scaling(dpi):
        """Return Tk's pixels-per-point scale for a physical display DPI."""
        try:
            dpi = float(dpi)
        except (TypeError, ValueError):
            dpi = 96.0
        dpi = max(72.0, min(384.0, dpi))
        return (96.0 / 72.0) * (dpi / 96.0)

    @staticmethod
    def _get_preferences_path():
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "md2pdf-studio", "preferences.json")

    def _load_preferences(self):
        try:
            with open(self.preferences_path, "r", encoding="utf-8") as handle:
                data = __import__("json").load(handle)
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, TypeError):
            return {}

    def _save_preferences(self):
        try:
            directory = os.path.dirname(self.preferences_path)
            os.makedirs(directory, exist_ok=True)
            with open(self.preferences_path, "w", encoding="utf-8") as handle:
                __import__("json").dump(
                    {
                        "theme": self.theme_mode,
                        "accent": self.accent_name,
                        "zoom": self.zoom_percent,
                    },
                    handle,
                    indent=2,
                )
        except OSError:
            pass

    def _get_window_dpi(self):
        if sys.platform == "win32":
            try:
                dpi = int(ctypes.windll.user32.GetDpiForWindow(self.root.winfo_id()))
                if dpi > 0:
                    return dpi
            except (AttributeError, OSError, TypeError, ValueError):
                pass

        try:
            dpi = int(round(float(self.root.winfo_fpixels("1i"))))
            if dpi > 0:
                return dpi
        except (tk.TclError, ValueError, TypeError):
            pass
        return 96

    def _configure_display_scaling(self, initial=False):
        dpi = self._get_window_dpi() if not initial else 96
        if initial and sys.platform == "win32":
            try:
                dpi = int(ctypes.windll.user32.GetDpiForSystem())
            except (AttributeError, OSError, TypeError, ValueError):
                dpi = 96

        self._current_dpi = dpi or 96
        base = self._preferred_tk_scaling(self._current_dpi)
        scale = base * (self.zoom_percent / 100.0)

        try:
            self.root.tk.call("tk", "scaling", scale)
        except tk.TclError:
            pass

    def _start_dpi_monitor(self):
        self._check_for_dpi_change()
        self._dpi_after_id = self.root.after(1200, self._start_dpi_monitor)

    def _check_for_dpi_change(self):
        try:
            dpi = self._get_window_dpi()
        except tk.TclError:
            return

        if dpi and abs(dpi - self._current_dpi) >= 8:
            self._current_dpi = dpi
            self._configure_display_scaling()
            self._update_scale_indicators()

    def _effective_display_scale(self):
        return (self._current_dpi / 96.0) * (self.zoom_percent / 100.0)

    def set_zoom(self, value):
        target = self._clamp_zoom(value)
        if target == self.zoom_percent:
            return
        self.zoom_percent = target
        self._configure_display_scaling()
        self._update_scale_indicators()
        self._save_preferences()

    def zoom_in(self):
        current = self.ZOOM_STEPS.index(self.zoom_percent)
        if current < len(self.ZOOM_STEPS) - 1:
            self.set_zoom(self.ZOOM_STEPS[current + 1])

    def zoom_out(self):
        current = self.ZOOM_STEPS.index(self.zoom_percent)
        if current > 0:
            self.set_zoom(self.ZOOM_STEPS[current - 1])

    def reset_zoom(self):
        self.set_zoom(100)

    # ------------------------------------------------------------------
    # Theme system
    # ------------------------------------------------------------------

    ACCENTS = {
        "blue": {
            "accent": "#2563eb",
            "accent_hover": "#3b82f6",
            "accent_soft_light": "#e8efff",
            "accent_soft_dark": "#172744",
        },
        "violet": {
            "accent": "#7c3aed",
            "accent_hover": "#8b5cf6",
            "accent_soft_light": "#f0e9ff",
            "accent_soft_dark": "#281c45",
        },
        "teal": {
            "accent": "#0f766e",
            "accent_hover": "#14b8a6",
            "accent_soft_light": "#e4f7f4",
            "accent_soft_dark": "#123936",
        },
        "emerald": {
            "accent": "#047857",
            "accent_hover": "#10b981",
            "accent_soft_light": "#e7f7f1",
            "accent_soft_dark": "#12382e",
        },
        "rose": {
            "accent": "#be123c",
            "accent_hover": "#e11d48",
            "accent_soft_light": "#fff0f3",
            "accent_soft_dark": "#411a26",
        },
        "amber": {
            "accent": "#b45309",
            "accent_hover": "#d97706",
            "accent_soft_light": "#fff4df",
            "accent_soft_dark": "#402b14",
        },
    }

    BASE_THEMES = {
        "dark": {
            "root": "#090a0c",
            "surface": "#111315",
            "surface_2": "#17191c",
            "surface_3": "#1d2024",
            "input": "#0c0e10",
            "text": "#f4f5f7",
            "text_2": "#c1c6ce",
            "text_3": "#7d848e",
            "border": "#282d33",
            "border_soft": "#20242a",
            "success": "#34d399",
            "warning": "#f5b84b",
            "danger": "#fb7185",
        },
        "light": {
            "root": "#f3f4f6",
            "surface": "#ffffff",
            "surface_2": "#f7f8fa",
            "surface_3": "#eceff2",
            "input": "#fbfbfc",
            "text": "#111315",
            "text_2": "#454b53",
            "text_3": "#7b828b",
            "border": "#dfe3e7",
            "border_soft": "#e9ecef",
            "success": "#047857",
            "warning": "#b45309",
            "danger": "#be123c",
        },
    }

    def _colors(self):
        colors = dict(self.BASE_THEMES.get(self.theme_mode, self.BASE_THEMES["dark"]))
        colors.update(self.ACCENTS.get(self.accent_name, self.ACCENTS["blue"]))
        colors["selected"] = colors["accent_soft_dark" if self.theme_mode == "dark" else "accent_soft_light"]
        colors["editor_line"] = "#14171b" if self.theme_mode == "dark" else "#f3f5f7"
        colors["control_text"] = colors["text_2"]
        return colors

    def _apply_visual_preferences(self, theme=None, accent=None):
        if theme is not None:
            self.theme_mode = theme
        if accent is not None:
            self.accent_name = accent

        snapshot = self._snapshot_document()
        self._cancel_scheduled_callbacks()

        if hasattr(self, "ui_container"):
            self.ui_container.destroy()

        self.root.configure(bg=self._colors()["root"])
        self._configure_styles()
        self._build_ui()

        self._restore_document(snapshot)
        self._save_preferences()
        self._update_document_state()
        self._update_editor_metrics()
        self._update_cursor_status()
        self._run_auto_detect()

    def toggle_theme(self):
        self._apply_visual_preferences(theme="light" if self.theme_mode == "dark" else "dark")

    def choose_accent(self, name):
        if name in self.ACCENTS:
            self._apply_visual_preferences(accent=name)

    # ------------------------------------------------------------------
    # Window / dependencies / styling
    # ------------------------------------------------------------------

    def _configure_window(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        width = max(1180, int(screen_w * 0.84))
        height = max(760, int(screen_h * 0.84))
        width = min(width, max(1180, screen_w - 48))
        height = min(height, max(760, screen_h - 72))
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(
            int(980 * max(1.0, self._current_dpi / 96.0)),
            int(650 * max(1.0, self._current_dpi / 96.0)),
        )

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

    def _configure_styles(self):
        c = self._colors()
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure(
            "MD.TButton",
            background=c["surface_3"],
            foreground=c["text"],
            padding=(12, 7),
            font=("Segoe UI", 9),
            borderwidth=0,
            relief="flat",
        )
        self.style.map(
            "MD.TButton",
            background=[("active", c["border"]), ("pressed", c["border_soft"]), ("disabled", c["surface_2"])],
            foreground=[("disabled", c["text_3"])],
        )

        self.style.configure(
            "MDPrimary.TButton",
            background=c["accent"],
            foreground="#ffffff",
            padding=(17, 9),
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            relief="flat",
        )
        self.style.map(
            "MDPrimary.TButton",
            background=[("active", c["accent_hover"]), ("pressed", c["accent"]), ("disabled", c["surface_3"])],
            foreground=[("disabled", c["text_3"])],
        )

        self.style.configure(
            "MD.TCombobox",
            fieldbackground=c["surface_3"],
            background=c["surface_3"],
            foreground=c["text"],
            arrowcolor=c["text_2"],
            bordercolor=c["border"],
            lightcolor=c["border"],
            darkcolor=c["border"],
            padding=(7, 5),
        )

        self.style.configure(
            "MD.Horizontal.TProgressbar",
            troughcolor=c["surface_3"],
            background=c["accent"],
            bordercolor=c["surface_3"],
            lightcolor=c["accent"],
            darkcolor=c["accent"],
        )

    def _label(self, parent, text="", size=10, weight="normal", color=None, bg=None, **kwargs):
        c = self._colors()
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, weight),
            fg=color or c["text"],
            bg=bg or c["surface"],
            **kwargs,
        )

    def _button(self, parent, text, command, primary=False, **kwargs):
        style = "MDPrimary.TButton" if primary else "MD.TButton"
        return ttk.Button(parent, text=text, command=command, style=style, **kwargs)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        c = self._colors()
        self.ui_container = tk.Frame(self.root, bg=c["root"])
        self.ui_container.pack(fill="both", expand=True, padx=16, pady=13)

        self._build_header()
        self._build_command_bar()

        workspace = tk.PanedWindow(
            self.ui_container,
            orient="horizontal",
            bg=c["root"],
            bd=0,
            sashwidth=7,
            sashrelief="flat",
            opaqueresize=True,
        )
        workspace.pack(fill="both", expand=True, pady=(9, 9))

        editor_panel = self._build_editor_panel()
        export_panel = self._build_export_panel()

        scale = self._effective_display_scale()
        workspace.add(editor_panel, minsize=max(560, int(530 * scale)))
        workspace.add(export_panel, minsize=max(350, int(345 * scale)))

        self._build_statusbar()
        self._update_scale_indicators()

    def _build_header(self):
        c = self._colors()
        header = tk.Frame(self.ui_container, bg=c["root"])
        header.pack(fill="x", pady=(0, 9))

        brand = tk.Frame(header, bg=c["root"])
        brand.pack(side="left", fill="x", expand=True)

        row = tk.Frame(brand, bg=c["root"])
        row.pack(anchor="w")
        tk.Label(
            row,
            text="md2pdf",
            bg=c["root"],
            fg=c["text"],
            font=("Segoe UI", 18, "bold"),
        ).pack(side="left")
        tk.Label(
            row,
            text="  STUDIO",
            bg=c["root"],
            fg=c["accent"],
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left", pady=(7, 0))

        tk.Label(
            brand,
            text="A focused Markdown workspace for reliable PDF output.",
            bg=c["root"],
            fg=c["text_3"],
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(1, 0))

        controls = tk.Frame(header, bg=c["root"])
        controls.pack(side="right", pady=(3, 0))

        self.dpi_label = tk.Label(
            controls,
            text="DPI 100%",
            bg=c["root"],
            fg=c["text_3"],
            font=("Segoe UI", 8, "bold"),
        )
        self.dpi_label.pack(side="left", padx=(0, 9))

        self.zoom_out_button = tk.Button(
            controls,
            text="−",
            command=self.zoom_out,
            width=2,
            bg=c["surface_3"],
            fg=c["text"],
            activebackground=c["border"],
            activeforeground=c["text"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.zoom_out_button.pack(side="left")

        self.zoom_label = tk.Label(
            controls,
            text="100%",
            bg=c["surface_3"],
            fg=c["text"],
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=5,
        )
        self.zoom_label.pack(side="left", padx=1)

        self.zoom_in_button = tk.Button(
            controls,
            text="+",
            command=self.zoom_in,
            width=2,
            bg=c["surface_3"],
            fg=c["text"],
            activebackground=c["border"],
            activeforeground=c["text"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.zoom_in_button.pack(side="left", padx=(0, 8))

        self._button(
            controls,
            "Reset",
            self.reset_zoom,
        ).pack(side="left", padx=(0, 7))

        theme_name = "Light" if self.theme_mode == "dark" else "Dark"
        self._button(
            controls,
            theme_name,
            self.toggle_theme,
        ).pack(side="left", padx=(0, 7))

        accent_button = tk.Menubutton(
            controls,
            text=f"Accent · {self.accent_name.title()}",
            bg=c["surface_3"],
            fg=c["text"],
            activebackground=c["border"],
            activeforeground=c["text"],
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
        )
        accent_menu = tk.Menu(
            accent_button,
            tearoff=0,
            bg=c["surface"],
            fg=c["text"],
            activebackground=c["accent"],
            activeforeground="#ffffff",
            relief="flat",
            bd=1,
        )
        for name in self.ACCENTS:
            accent_menu.add_command(
                label=name.title(),
                command=lambda n=name: self.choose_accent(n),
            )
        accent_button.configure(menu=accent_menu)
        accent_button.pack(side="left")

    def _build_command_bar(self):
        c = self._colors()
        bar = tk.Frame(
            self.ui_container,
            bg=c["surface"],
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        bar.pack(fill="x")

        left = tk.Frame(bar, bg=c["surface"])
        left.pack(side="left", padx=7, pady=7)
        for label, command in (
            ("New", self.new_document),
            ("Open", self.open_file),
            ("Paste", self.paste_clipboard),
            ("Save", self.save_file),
        ):
            self._button(left, label, command).pack(side="left", padx=3)

        tk.Frame(bar, width=1, bg=c["border"]).pack(side="left", fill="y", pady=8, padx=8)

        self.file_label = tk.Label(
            bar,
            text="Scratchpad · No file loaded",
            bg=c["surface"],
            fg=c["text_2"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        self.file_label.pack(side="left", fill="x", expand=True)

        auto_text = tk.Frame(bar, bg=c["surface"])
        auto_text.pack(side="right", padx=(0, 9))
        tk.Label(
            auto_text,
            text="Smart detect",
            bg=c["surface"],
            fg=c["text_2"],
            font=("Segoe UI", 8),
        ).pack(side="left", padx=(0, 5))

        self.auto_detect_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            auto_text,
            variable=self.auto_detect_var,
            command=self._run_auto_detect,
            bg=c["surface"],
            fg=c["text"],
            activebackground=c["surface"],
            activeforeground=c["text"],
            selectcolor=c["surface_3"],
            relief="flat",
            bd=0,
            highlightthickness=0,
        ).pack(side="left")

    def _build_editor_panel(self):
        c = self._colors()
        panel = tk.Frame(
            self.ui_container,
            bg=c["surface"],
            highlightbackground=c["border"],
            highlightthickness=1,
        )

        header = tk.Frame(panel, bg=c["surface"])
        header.pack(fill="x", padx=14, pady=(12, 7))

        left = tk.Frame(header, bg=c["surface"])
        left.pack(side="left")
        tk.Label(
            left,
            text="MARKDOWN SOURCE",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            text="Write your document",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(1, 0))

        self.document_state = tk.Label(
            header,
            text="Saved",
            bg=c["surface"],
            fg=c["success"],
            font=("Segoe UI", 8, "bold"),
        )
        self.document_state.pack(side="right", pady=(6, 0))

        shell = tk.Frame(
            panel,
            bg=c["input"],
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        shell.pack(fill="both", expand=True, padx=12)

        self.text = scrolledtext.ScrolledText(
            shell,
            wrap="word",
            font=("Cascadia Mono", 11),
            bg=c["input"],
            fg=c["text"],
            insertbackground=c["accent"],
            selectbackground=c["accent"],
            selectforeground="#ffffff",
            padx=17,
            pady=15,
            bd=0,
            relief="flat",
            highlightthickness=0,
            undo=True,
            maxundo=-1,
        )
        self.text.pack(fill="both", expand=True)
        self.text.tag_configure("current_line", background=c["editor_line"])

        self.editor_placeholder = tk.Label(
            shell,
            text=(
                "Start with Markdown\n\n"
                "# Your title\n"
                "Write normally — headings, tables, code, math, Mermaid and alerts are supported.\n\n"
                "Ctrl+O  Open    Ctrl+S  Save    Ctrl+Shift+E  Export\n"
                "Ctrl+Plus / Ctrl+Minus  Zoom"
            ),
            bg=c["input"],
            fg=c["text_3"],
            font=("Segoe UI", 10),
            justify="left",
            anchor="nw",
            padx=20,
            pady=22,
        )
        self.editor_placeholder.place(x=0, y=0, relwidth=1, relheight=1)
        self.editor_placeholder.bind("<Button-1>", lambda _e: self.text.focus_set())

        footer = tk.Frame(panel, bg=c["surface"])
        footer.pack(fill="x", padx=14, pady=(7, 10))

        self.stats_bar = tk.Label(
            footer,
            text="Lines 0  ·  Words 0  ·  Characters 0",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8),
        )
        self.stats_bar.pack(side="left")

        self.cursor_label = tk.Label(
            footer,
            text="Ln 1, Col 1",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8),
        )
        self.cursor_label.pack(side="right")

        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<KeyRelease>", self._on_editor_event)
        self.text.bind("<ButtonRelease>", self._on_editor_event)
        self.text.bind("<Control-MouseWheel>", self._on_control_wheel)
        self.text.edit_modified(False)

        return panel

    def _build_export_panel(self):
        c = self._colors()
        panel = tk.Frame(
            self.ui_container,
            bg=c["surface"],
            highlightbackground=c["border"],
            highlightthickness=1,
        )

        body = tk.Frame(panel, bg=c["surface"])
        body.pack(fill="both", expand=True, padx=15, pady=14)

        tk.Label(
            body,
            text="EXPORT",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            body,
            text="PDF profile",
            bg=c["surface"],
            fg=c["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(1, 2))
        tk.Label(
            body,
            text="Smart Detect handles most documents automatically. Manual renderers remain available below.",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8),
            wraplength=320,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        smart = tk.Frame(
            body,
            bg=c["selected"],
            highlightbackground=c["accent"],
            highlightthickness=1,
        )
        smart.pack(fill="x")

        self.mode_var = tk.StringVar(value="auto")
        tk.Radiobutton(
            smart,
            variable=self.mode_var,
            value="auto",
            command=self._run_auto_detect,
            bg=c["selected"],
            activebackground=c["selected"],
            selectcolor=c["accent"],
            relief="flat",
            bd=0,
            highlightthickness=0,
        ).pack(side="left", padx=(9, 2), pady=9)

        copy = tk.Frame(smart, bg=c["selected"])
        copy.pack(side="left", fill="x", expand=True, padx=(1, 9), pady=8)

        tk.Label(
            copy,
            text="Smart Detect",
            bg=c["selected"],
            fg=c["text"],
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        self.detect_label = tk.Label(
            copy,
            text="Ready to inspect the document.",
            bg=c["selected"],
            fg=c["accent_hover"],
            font=("Segoe UI", 8),
            wraplength=290,
            justify="left",
        )
        self.detect_label.pack(anchor="w", pady=(2, 0))

        tk.Label(
            body,
            text="RENDERER",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(13, 6))

        cards = tk.Frame(body, bg=c["surface"])
        cards.pack(fill="x")
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        self._mode_cards = {}
        renderer_info = [
            ("sidebar_light", "Sidebar Light", "Print layout", self.sidebar_ok),
            ("sidebar_dark", "Sidebar Dark", "Dark output", self.sidebar_ok),
            ("latex", "LaTeX Formal", "Academic", self.latex_ok),
            ("simple", "Simple", "HTML fallback", self.simple_ok),
        ]
        for i, (value, title, desc, available) in enumerate(renderer_info):
            card = tk.Frame(
                cards,
                bg=c["input"],
                highlightbackground=c["border"],
                highlightthickness=1,
                cursor="hand2" if available else "arrow",
            )
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=3, pady=3)
            self._mode_cards[value] = card

            title_row = tk.Frame(card, bg=c["input"])
            title_row.pack(fill="x", padx=8, pady=(8, 2))
            title_label = tk.Label(
                title_row,
                text=title,
                bg=c["input"],
                fg=c["text"] if available else c["text_3"],
                font=("Segoe UI", 8, "bold"),
            )
            title_label.pack(side="left")
            tk.Label(
                title_row,
                text="●" if available else "○",
                bg=c["input"],
                fg=c["success"] if available else c["text_3"],
                font=("Segoe UI", 7),
            ).pack(side="right")

            tk.Label(
                card,
                text=desc,
                bg=c["input"],
                fg=c["text_3"],
                font=("Segoe UI", 7),
                anchor="w",
            ).pack(fill="x", padx=8, pady=(0, 8))

            if available:
                handler = lambda _event, v=value: self._select_mode(v)
                for widget in (card, title_row, title_label):
                    widget.bind("<Button-1>", handler)

        tk.Frame(body, height=1, bg=c["border_soft"]).pack(fill="x", pady=13)

        tk.Label(
            body,
            text="OUTPUT",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        output_row = tk.Frame(body, bg=c["surface"])
        output_row.pack(fill="x", pady=(6, 5))

        self.output_var = getattr(self, "output_var", tk.StringVar(value=""))
        self.output_entry = tk.Entry(
            output_row,
            textvariable=self.output_var,
            bg=c["surface_3"],
            fg=c["text"],
            insertbackground=c["accent"],
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=c["border"],
            highlightcolor=c["accent"],
        )
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 6))
        self._button(output_row, "Browse", self.choose_output).pack(side="right")

        settings = tk.Frame(body, bg=c["surface"])
        settings.pack(fill="x", pady=(4, 0))
        tk.Label(
            settings,
            text="Margins",
            bg=c["surface"],
            fg=c["text_2"],
            font=("Segoe UI", 9),
        ).grid(row=0, column=0, sticky="w", pady=4)

        self.margin_var = getattr(self, "margin_var", tk.StringVar(value="14mm"))
        ttk.Combobox(
            settings,
            textvariable=self.margin_var,
            values=["10mm", "14mm", "20mm", "0.5in", "0.75in"],
            state="readonly",
            width=8,
            style="MD.TCombobox",
        ).grid(row=0, column=1, sticky="e")

        self.open_pdf_var = getattr(self, "open_pdf_var", tk.BooleanVar(value=True))
        tk.Checkbutton(
            settings,
            text="Open PDF automatically",
            variable=self.open_pdf_var,
            bg=c["surface"],
            fg=c["text_2"],
            activebackground=c["surface"],
            activeforeground=c["text"],
            selectcolor=c["surface_3"],
            font=("Segoe UI", 8),
            relief="flat",
            bd=0,
            highlightthickness=0,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(7, 0))

        tk.Frame(body, height=1, bg=c["border_soft"]).pack(fill="x", pady=13)

        env_head = tk.Frame(body, bg=c["surface"])
        env_head.pack(fill="x")
        tk.Label(
            env_head,
            text="ENVIRONMENT",
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8, "bold"),
        ).pack(side="left")

        self.environment_expanded = getattr(self, "environment_expanded", False)
        self.environment_button = tk.Button(
            env_head,
            text="Hide" if self.environment_expanded else "Show",
            command=self._toggle_environment,
            bg=c["surface"],
            fg=c["accent_hover"],
            activebackground=c["surface"],
            activeforeground=c["text"],
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.environment_button.pack(side="right")

        self.environment_frame = tk.Frame(body, bg=c["surface"])
        if self.environment_expanded:
            self.environment_frame.pack(fill="x", pady=(7, 0))
        self._populate_environment()

        return panel

    def _build_statusbar(self):
        c = self._colors()
        bar = tk.Frame(
            self.ui_container,
            bg=c["surface"],
            highlightbackground=c["border"],
            highlightthickness=1,
        )
        bar.pack(fill="x")

        left = tk.Frame(bar, bg=c["surface"])
        left.pack(side="left", padx=11, pady=8)

        self.status_dot = tk.Label(
            left,
            text="●",
            bg=c["surface"],
            fg=c["success"],
            font=("Segoe UI", 8),
        )
        self.status_dot.pack(side="left", padx=(0, 5))

        self.status = tk.Label(
            left,
            text="Ready",
            bg=c["surface"],
            fg=c["text_2"],
            font=("Segoe UI", 8, "bold"),
        )
        self.status.pack(side="left")

        hint = "Ctrl+Shift+E Export  ·  Ctrl+0 Reset Zoom"
        tk.Label(
            bar,
            text=hint,
            bg=c["surface"],
            fg=c["text_3"],
            font=("Segoe UI", 8),
        ).pack(side="right", padx=11)

    # ------------------------------------------------------------------
    # Document / editor
    # ------------------------------------------------------------------

    def _snapshot_document(self):
        if not hasattr(self, "text"):
            return {"content": "", "cursor": "1.0"}
        try:
            content = self.text.get("1.0", "end-1c")
            cursor = self.text.index(tk.INSERT)
        except tk.TclError:
            content, cursor = "", "1.0"
        return {"content": content, "cursor": cursor}

    def _restore_document(self, snapshot):
        if not hasattr(self, "text"):
            return
        self.text.delete("1.0", "end")
        if snapshot.get("content"):
            self.text.insert("1.0", snapshot["content"])
        try:
            self.text.mark_set(tk.INSERT, snapshot.get("cursor", "1.0"))
            self.text.see(tk.INSERT)
        except tk.TclError:
            pass
        self.text.edit_modified(False)
        self._update_placeholder()
        self._update_current_line()

    def _set_document(self, content, path=None, dirty=False):
        if hasattr(self, "text"):
            self.text.delete("1.0", "end")
            if content:
                self.text.insert("1.0", content)
            self.text.edit_modified(False)
        self.md_path = path
        self.dirty = dirty

        if path:
            self.output_var.set(os.path.splitext(path)[0] + ".pdf")
        else:
            self.output_var.set(os.path.join(os.getcwd(), "output.pdf"))

        self._update_document_state()
        self._update_editor_metrics()
        self._update_cursor_status()
        self._update_placeholder()
        self._update_current_line()
        self._run_auto_detect()

    def _update_placeholder(self):
        if not hasattr(self, "editor_placeholder"):
            return
        try:
            empty = not self.text.get("1.0", "end-1c").strip()
            if empty:
                self.editor_placeholder.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                self.editor_placeholder.place_forget()
        except tk.TclError:
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

    def _update_document_state(self):
        if not hasattr(self, "file_label"):
            return
        name = os.path.basename(self.md_path) if self.md_path else "Scratchpad · No file loaded"
        if self.md_path:
            self.file_label.config(text=name + ("  •" if self.dirty else ""))
        else:
            self.file_label.config(text=name)

        if hasattr(self, "document_state"):
            self.document_state.config(
                text="Unsaved changes" if self.dirty else "Saved",
                fg=self._colors()["warning"] if self.dirty else self._colors()["success"],
            )

    def _update_editor_metrics(self):
        if not hasattr(self, "text"):
            return
        try:
            raw = self.text.get("1.0", "end-1c")
            lines = len(raw.splitlines()) if raw else 0
            words = len(raw.split())
            chars = len(raw)
            self.stats_bar.config(
                text=f"Lines {lines:,}  ·  Words {words:,}  ·  Characters {chars:,}"
            )
        except tk.TclError:
            pass

    def _update_cursor_status(self):
        if not hasattr(self, "text") or not hasattr(self, "cursor_label"):
            return
        try:
            line, col = self.text.index(tk.INSERT).split(".")
            self.cursor_label.config(text=f"Ln {int(line):,}, Col {int(col) + 1:,}")
        except (tk.TclError, ValueError):
            pass

    def _on_editor_event(self, _event=None):
        self._update_editor_metrics()
        self._update_cursor_status()
        self._update_current_line()
        self._update_placeholder()

    def _on_control_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        return "break"

    def _on_text_modified(self, _event=None):
        try:
            self.text.edit_modified(False)
        except tk.TclError:
            return

        self.dirty = True
        self._update_document_state()
        self._update_editor_metrics()
        self._update_placeholder()

        if self._detect_after_id is not None:
            try:
                self.root.after_cancel(self._detect_after_id)
            except tk.TclError:
                pass
        self._detect_after_id = self.root.after(300, self._run_auto_detect)

    # ------------------------------------------------------------------
    # Mode detection / renderer selection
    # ------------------------------------------------------------------

    def _friendly_mode_name(self, mode):
        return {
            "auto": "Smart Detect",
            "sidebar_light": "Sidebar Light",
            "sidebar_dark": "Sidebar Dark",
            "latex": "LaTeX Formal",
            "simple": "Simple",
        }.get(mode, mode)

    def _select_mode(self, mode):
        available = {
            "sidebar_light": self.sidebar_ok,
            "sidebar_dark": self.sidebar_ok,
            "latex": self.latex_ok,
            "simple": self.simple_ok,
        }.get(mode, False)

        if not available:
            self._set_status(
                f"{self._friendly_mode_name(mode)} is unavailable on this machine.",
                self._colors()["warning"],
            )
            return

        self.mode_var.set(mode)
        self._run_auto_detect()

    def _run_auto_detect(self):
        if not hasattr(self, "detect_label"):
            return

        if self._detect_after_id is not None:
            self._detect_after_id = None

        content = self.text.get("1.0", "end") if hasattr(self, "text") else ""
        if not content.strip():
            self.detect_label.config(
                text="Ready to inspect the document.",
                fg=self._colors()["accent_hover"],
            )
            self._update_mode_cards()
            return

        if not self.auto_detect_var.get():
            self.detect_label.config(
                text="Smart detection is off.",
                fg=self._colors()["text_3"],
            )
            self._update_mode_cards()
            return

        mode = self.mode_var.get()
        if mode != "auto":
            self.detect_label.config(
                text=f"Manual renderer: {self._friendly_mode_name(mode)}",
                fg=self._colors()["text_2"],
            )
            self._update_mode_cards()
            return

        needed_sidebar, reason_sidebar = detect_sidebar_needed(content)
        needed_latex, reason_latex = detect_latex_needed(content)

        if needed_sidebar and self.sidebar_ok:
            self.detect_label.config(
                text=f"Detected: {reason_sidebar}",
                fg=self._colors()["accent_hover"],
            )
        elif needed_latex and self.latex_ok:
            self.detect_label.config(
                text=f"Detected: {reason_latex}",
                fg=self._colors()["success"],
            )
        elif needed_latex and not self.latex_ok:
            self.detect_label.config(
                text="Math detected; LaTeX unavailable. Smart mode will use a compatible fallback.",
                fg=self._colors()["warning"],
            )
        else:
            self.detect_label.config(
                text="No special features detected; a standard renderer is sufficient.",
                fg=self._colors()["text_2"],
            )

        self._update_mode_cards()

    def _update_mode_cards(self):
        if not hasattr(self, "_mode_cards"):
            return
        c = self._colors()
        selected = self.mode_var.get()
        for mode, card in self._mode_cards.items():
            active = mode == selected
            bg = c["selected"] if active else c["input"]
            card.config(
                bg=bg,
                highlightbackground=c["accent"] if active else c["border"],
            )
            for child in card.winfo_children():
                child.config(bg=bg)
                for nested in child.winfo_children():
                    nested.config(bg=bg)

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------

    def _populate_environment(self):
        c = self._colors()
        if not hasattr(self, "environment_frame"):
            return

        for child in self.environment_frame.winfo_children():
            child.destroy()

        items = (
            ("Pandoc", self.have.get("pandoc", False)),
            ("Chromium", self.have.get("chromium", False)),
            ("LaTeX", self.latex_ok),
            ("wkhtmltopdf", self.have.get("wkhtmltopdf", False)),
        )

        for label, ok in items:
            tk.Label(
                self.environment_frame,
                text=("● " if ok else "○ ") + label,
                bg=c["surface"],
                fg=c["success"] if ok else c["text_3"],
                font=("Segoe UI", 8),
                anchor="w",
            ).pack(anchor="w", pady=1)

    def _toggle_environment(self):
        self.environment_expanded = not self.environment_expanded
        if self.environment_expanded:
            self.environment_button.config(text="Hide")
            self.environment_frame.pack(fill="x", pady=(7, 0))
        else:
            self.environment_button.config(text="Show")
            self.environment_frame.pack_forget()

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def new_document(self):
        if self.text.get("1.0", "end-1c").strip():
            choice = messagebox.askyesno(
                "New document",
                "Replace the current Markdown document?",
            )
            if not choice:
                return

        self._set_document("", None, False)
        self._set_status("New document", self._colors()["text_2"])

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Open Markdown",
            filetypes=[
                ("Markdown files", "*.md *.markdown"),
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except (OSError, UnicodeError) as exc:
            messagebox.showerror("Open failed", str(exc))
            return

        self._set_document(content, path, False)
        self._set_status(f"Opened {os.path.basename(path)}", self._colors()["success"])

    def paste_clipboard(self):
        try:
            content = self.root.clipboard_get()
        except tk.TclError:
            self._set_status("Clipboard has no readable text.", self._colors()["warning"])
            return

        if content:
            self.text.insert(tk.INSERT, content)
            self.text.see(tk.INSERT)
            self.dirty = True
            self._update_document_state()
            self._on_editor_event()
            self._run_auto_detect()

    def save_file(self):
        path = self.md_path
        if not path:
            path = filedialog.asksaveasfilename(
                title="Save Markdown",
                defaultextension=".md",
                initialfile="untitled.md",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("All files", "*.*"),
                ],
            )
            if not path:
                return False

        try:
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(self.text.get("1.0", "end-1c"))
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))
            return False

        self.md_path = path
        self.dirty = False
        self.output_var.set(os.path.splitext(path)[0] + ".pdf")
        self._update_document_state()
        self._set_status(f"Saved {os.path.basename(path)}", self._colors()["success"])
        return True

    def clear_editor(self):
        if not self.text.get("1.0", "end-1c").strip():
            return
        if messagebox.askyesno("Clear editor", "Clear the Markdown document?"):
            self._set_document("", None, False)
            self._set_status("Editor cleared", self._colors()["text_2"])

    def choose_output(self):
        current = self.output_var.get().strip()
        initial_dir = os.path.dirname(current) if current else None
        initial_file = os.path.basename(current) if current else "output.pdf"

        path = filedialog.asksaveasfilename(
            title="Choose PDF output",
            defaultextension=".pdf",
            initialdir=initial_dir,
            initialfile=initial_file,
            filetypes=[("PDF documents", "*.pdf")],
        )
        if path:
            self.output_var.set(path)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _resolve_mode(self, content):
        selected = self.mode_var.get()
        if selected != "auto":
            return selected

        needed_sidebar, _ = detect_sidebar_needed(content)
        needed_latex, _ = detect_latex_needed(content)

        if needed_sidebar and self.sidebar_ok:
            return "sidebar_light"
        if needed_latex and self.latex_ok:
            return "latex"
        if self.sidebar_ok:
            return "sidebar_light"
        if self.latex_ok:
            return "latex"
        if self.simple_ok:
            return "simple"
        return None

    def convert(self):
        if self._conversion_in_progress:
            return

        content = self.text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showwarning(
                "Nothing to export",
                "Add Markdown content before exporting.",
            )
            self.text.focus_set()
            return

        mode = self._resolve_mode(content)
        if not mode:
            messagebox.showerror(
                "No renderer available",
                "No compatible PDF renderer is currently available. Check Environment.",
            )
            return

        available = {
            "sidebar_light": self.sidebar_ok,
            "sidebar_dark": self.sidebar_ok,
            "latex": self.latex_ok,
            "simple": self.simple_ok,
        }
        if not available.get(mode, False):
            messagebox.showerror(
                "Renderer unavailable",
                f"{self._friendly_mode_name(mode)} is not currently available.",
            )
            return

        save_path = self.output_var.get().strip()
        if not save_path:
            self.choose_output()
            save_path = self.output_var.get().strip()
        if not save_path:
            return

        if not save_path.lower().endswith(".pdf"):
            save_path += ".pdf"
            self.output_var.set(save_path)

        save_path = os.path.abspath(os.path.expanduser(save_path))
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Output error", str(exc))
            return

        margin = self.margin_var.get().strip() or "14mm"
        theme = "dark" if mode == "sidebar_dark" else "light"
        open_pdf_after = bool(self.open_pdf_var.get())

        self._conversion_in_progress = True
        self.convert_btn.config(state="disabled")
        self.progress.start(8)

        self._set_status(
            f"Exporting with {self._friendly_mode_name(mode)}…",
            self._colors()["warning"],
        )

        worker = threading.Thread(
            target=self._convert_worker,
            args=(content, save_path, margin, mode, theme, open_pdf_after),
            daemon=True,
            name="md2pdf-conversion",
        )
        worker.start()
        self._conversion_after_id = self.root.after(100, self._poll_conversion)

    def _convert_worker(self, content, save_path, margin, mode, theme, open_pdf_after):
        start_time = time.time()
        try:
            if mode == "auto":
                backend = convert_auto(
                    content,
                    save_path,
                    margin=margin,
                    theme=theme,
                )
            elif mode in ("sidebar_light", "sidebar_dark"):
                convert_sidebar(content, save_path, margin=margin, theme=theme)
                backend = "sidebar"
            elif mode == "latex":
                convert_latex(content, save_path, margin=margin)
                backend = "latex"
            elif mode == "simple":
                convert_simple(content, save_path, margin=margin)
                backend = "simple"
            else:
                raise ValueError(f"Unsupported renderer: {mode}")

            size_kb = os.path.getsize(save_path) / 1024
            self._conversion_queue.put(
                {
                    "ok": True,
                    "save_path": save_path,
                    "elapsed": time.time() - start_time,
                    "file_size_kb": size_kb,
                    "open_pdf": open_pdf_after,
                    "backend": backend,
                }
            )
        except Exception as exc:
            self._conversion_queue.put({"ok": False, "error": str(exc)})

    def _poll_conversion(self):
        try:
            result = self._conversion_queue.get_nowait()
        except queue.Empty:
            if self._conversion_in_progress:
                self._conversion_after_id = self.root.after(100, self._poll_conversion)
            return

        self._conversion_after_id = None
        self._finish_conversion(result)

    def _finish_conversion(self, result):
        self._conversion_in_progress = False
        self.convert_btn.config(state="normal")
        self.progress.stop()

        if not result["ok"]:
            self._set_status("Export failed.", self._colors()["danger"])
            messagebox.showerror("Export failed", result["error"])
            return

        save_path = result["save_path"]
        self.last_output_pdf = save_path
        self.open_folder_btn.config(state="normal")

        size_kb = result["file_size_kb"]
        size_text = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb / 1024:.2f} MB"
        backend = {
            "sidebar": "Sidebar",
            "latex": "LaTeX",
            "simple": "Simple",
        }.get(result.get("backend"), result.get("backend", "PDF"))

        self._set_status(
            f"PDF ready · {os.path.basename(save_path)} · {backend} · {size_text} · {result['elapsed']:.1f}s",
            self._colors()["success"],
        )

        if result["open_pdf"]:
            self._open_path(save_path)

    # ------------------------------------------------------------------
    # Status / shortcuts
    # ------------------------------------------------------------------

    def _set_status(self, text, color):
        if hasattr(self, "status"):
            self.status.config(text=text)
            self.status_dot.config(fg=color)

    def _update_scale_indicators(self):
        c = self._colors()
        if hasattr(self, "zoom_label"):
            self.zoom_label.config(
                text=f"{self.zoom_percent}%",
                bg=c["surface_3"],
                fg=c["text"],
            )
        if hasattr(self, "dpi_label"):
            dpi_percent = round((self._current_dpi / 96.0) * 100)
            self.dpi_label.config(
                text=f"DPI {dpi_percent}%",
                fg=c["text_3"],
                bg=c["root"],
            )

    def _open_path(self, path):
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=False)
            else:
                subprocess.run(["xdg-open", path], check=False)
        except OSError as exc:
            messagebox.showerror("Open failed", str(exc))

    def open_output_folder(self):
        if self.last_output_pdf and os.path.exists(self.last_output_pdf):
            self._open_path(os.path.dirname(os.path.abspath(self.last_output_pdf)))
        else:
            output = self.output_var.get().strip()
            if output:
                self._open_path(os.path.dirname(os.path.abspath(output)))

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda _e: self.open_file())
        self.root.bind("<Control-s>", lambda _e: self.save_file())
        self.root.bind("<Control-n>", lambda _e: self.new_document())
        self.root.bind("<Control-Shift-E>", lambda _e: self.convert())
        self.root.bind("<Control-Shift-e>", lambda _e: self.convert())
        self.root.bind("<Control-KeyPress-equal>", lambda _e: self.zoom_in())
        self.root.bind("<Control-KeyPress-plus>", lambda _e: self.zoom_in())
        self.root.bind("<Control-KeyPress-minus>", lambda _e: self.zoom_out())
        self.root.bind("<Control-KeyPress-0>", lambda _e: self.reset_zoom())

    def _cancel_scheduled_callbacks(self):
        for attr in ("_detect_after_id", "_conversion_after_id"):
            value = getattr(self, attr, None)
            if value is not None:
                try:
                    self.root.after_cancel(value)
                except tk.TclError:
                    pass
                setattr(self, attr, None)

    def _on_close(self):
        if self._conversion_in_progress:
            messagebox.showwarning(
                "Export in progress",
                "Please wait for the current export to finish before closing.",
            )
            return

        self._save_preferences()
        if self._dpi_after_id is not None:
            try:
                self.root.after_cancel(self._dpi_after_id)
            except tk.TclError:
                pass
        if self.dirty:
            choice = messagebox.askyesnocancel(
                "Unsaved changes",
                "Save Markdown changes before closing?",
            )
            if choice is None:
                return
            if choice and not self.save_file():
                return
        self.root.destroy()


def main():
    _enable_windows_thread_dpi_awareness()
    root = tk.Tk()
    _enable_windows_thread_dpi_awareness()
    app = MD2PDFStudioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
