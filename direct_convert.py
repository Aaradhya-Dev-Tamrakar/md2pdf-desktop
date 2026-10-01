#!/usr/bin/env python3
"""Direct conversion entrypoint for Windows context menu and CLI shortcuts.

Converts a Markdown file directly to PDF without opening the full editor UI,
with an optional notification toast on completion and error alerts on failure.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk

# Ensure repository root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from md2pdf import (
    convert_auto,
    convert_latex,
    convert_sidebar,
    convert_simple,
    find_pandoc,
)


def _enable_windows_thread_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        user32 = ctypes.windll.user32
        dpi_context_per_monitor_v2 = ctypes.c_void_p(-4)
        user32.SetThreadDpiAwarenessContext.restype = ctypes.c_void_p
        user32.SetThreadDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        user32.SetThreadDpiAwarenessContext(dpi_context_per_monitor_v2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            pass


def _show_toast(pdf_path: str, backend_name: str, file_size_kb: float, elapsed: float):
    """Show a non-blocking modern dark toast in the bottom-right corner."""
    try:
        root = tk.Tk()
    except tk.TclError:
        return

    root.title("md2pdf Studio")
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    bg_color = "#0f172a"
    card_bg = "#1e293b"
    fg_color = "#f8fafc"
    sub_color = "#94a3b8"
    accent_color = "#38bdf8"
    border_color = "#334155"

    frame = tk.Frame(root, bg=bg_color, highlightbackground=border_color, highlightthickness=1)
    frame.pack(fill="both", expand=True)

    header = tk.Frame(frame, bg=bg_color)
    header.pack(fill="x", padx=12, pady=(10, 4))

    tk.Label(
        header,
        text="● md2pdf Studio",
        fg=accent_color,
        bg=bg_color,
        font=("Segoe UI", 9, "bold"),
    ).pack(side="left")

    close_btn = tk.Label(
        header,
        text="✕",
        fg=sub_color,
        bg=bg_color,
        font=("Segoe UI", 9),
        cursor="hand2",
    )
    close_btn.pack(side="right")
    close_btn.bind("<Button-1>", lambda _e: root.destroy())

    filename = os.path.basename(pdf_path)
    size_text = f"{file_size_kb:.1f} KB" if file_size_kb < 1024 else f"{file_size_kb / 1024:.2f} MB"

    tk.Label(
        frame,
        text=f"Exported {filename}",
        fg=fg_color,
        bg=bg_color,
        font=("Segoe UI", 10, "bold"),
        anchor="w",
    ).pack(fill="x", padx=12, pady=(0, 2))

    tk.Label(
        frame,
        text=f"{backend_name} · {size_text} · {elapsed:.1f}s",
        fg=sub_color,
        bg=bg_color,
        font=("Segoe UI", 8),
        anchor="w",
    ).pack(fill="x", padx=12, pady=(0, 10))

    actions = tk.Frame(frame, bg=bg_color)
    actions.pack(fill="x", padx=12, pady=(0, 10))

    def open_pdf(_e=None):
        try:
            os.startfile(pdf_path)
        except OSError:
            pass
        root.destroy()

    def open_folder(_e=None):
        try:
            subprocess.Popen(["explorer", f"/select,{pdf_path}"])
        except OSError:
            pass
        root.destroy()

    open_btn = tk.Button(
        actions,
        text="Open PDF",
        command=open_pdf,
        bg=accent_color,
        fg="#0f172a",
        activebackground="#7dd3fc",
        activeforeground="#0f172a",
        font=("Segoe UI", 8, "bold"),
        relief="flat",
        bd=0,
        padx=10,
        pady=3,
        cursor="hand2",
    )
    open_btn.pack(side="left", padx=(0, 6))

    folder_btn = tk.Button(
        actions,
        text="Show in Folder",
        command=open_folder,
        bg=card_bg,
        fg=fg_color,
        activebackground=border_color,
        activeforeground=fg_color,
        font=("Segoe UI", 8),
        relief="flat",
        bd=0,
        padx=10,
        pady=3,
        cursor="hand2",
    )
    folder_btn.pack(side="left")

    root.update_idletasks()
    width = 340
    height = 115
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = screen_w - width - 20
    y = screen_h - height - 60
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.after(6000, root.destroy)
    root.mainloop()


def direct_convert(
    input_path: str,
    output_path: str | None = None,
    mode: str = "auto",
    margin: str = "14mm",
    open_after: bool = False,
    notify: bool = True,
) -> int:
    source = os.path.abspath(os.path.expanduser(input_path))
    if not os.path.isfile(source):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("md2pdf Error", f"Source file does not exist:\n{source}")
        root.destroy()
        return 1

    if not output_path:
        output_path = os.path.splitext(source)[0] + ".pdf"
    output = os.path.abspath(os.path.expanduser(output_path))

    try:
        with open(source, "r", encoding="utf-8") as handle:
            content = handle.read()
    except (OSError, UnicodeError) as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("md2pdf Read Error", f"Failed to read file:\n{exc}")
        root.destroy()
        return 1

    start_time = time.time()
    try:
        if mode == "auto":
            backend = convert_auto(content, output, margin=margin, theme="light")
        elif mode in ("sidebar", "sidebar_light"):
            convert_sidebar(content, output, margin=margin, theme="light")
            backend = "sidebar_light"
        elif mode == "sidebar_dark":
            convert_sidebar(content, output, margin=margin, theme="dark")
            backend = "sidebar_dark"
        elif mode == "latex":
            convert_latex(content, output, margin=margin)
            backend = "latex"
        elif mode == "simple":
            convert_simple(content, output, margin=margin)
            backend = "simple"
        else:
            raise ValueError(f"Unknown renderer mode: {mode}")

        elapsed = time.time() - start_time
        file_size_kb = os.path.getsize(output) / 1024

        friendly_names = {
            "sidebar": "Sidebar Light",
            "sidebar_light": "Sidebar Light",
            "sidebar_dark": "Sidebar Dark",
            "latex": "LaTeX Formal",
            "simple": "Simple",
        }
        backend_name = friendly_names.get(backend, str(backend))

        if open_after:
            try:
                os.startfile(output)
            except OSError:
                pass

        if notify:
            _show_toast(output, backend_name, file_size_kb, elapsed)

        return 0
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "md2pdf Export Failed",
            f"Failed to export {os.path.basename(source)} to PDF:\n\n{exc}",
        )
        root.destroy()
        return 1


def main(argv: list[str] | None = None) -> int:
    _enable_windows_thread_dpi_awareness()

    parser = argparse.ArgumentParser(
        prog="direct_convert",
        description="Direct conversion runner for md2pdf Studio context menu.",
    )
    parser.add_argument("input", help="Source Markdown file")
    parser.add_argument("-o", "--output", help="Output PDF path")
    parser.add_argument(
        "-m",
        "--mode",
        choices=("auto", "sidebar", "sidebar_light", "sidebar_dark", "latex", "simple"),
        default="auto",
        help="Renderer mode (default: auto)",
    )
    parser.add_argument("--margin", default="14mm", help="Page margin (default: 14mm)")
    parser.add_argument("--open", action="store_true", help="Open PDF immediately after export")
    parser.add_argument("--no-notify", action="store_true", help="Suppress the completion toast")

    args = parser.parse_args(argv)
    return direct_convert(
        args.input,
        output_path=args.output,
        mode=args.mode,
        margin=args.margin,
        open_after=args.open,
        notify=not args.no_notify,
    )


if __name__ == "__main__":
    raise SystemExit(main())
