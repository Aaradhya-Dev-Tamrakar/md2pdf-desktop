__version__ = "0.3.0"

from .core import (
    LATEX_TEMPLATE,
    LUA_FILTER,
    check_tools,
    convert_auto,
    validate_pdf_output,
    inspect_pdf_output,
    build_sidebar_asset_head,
    convert_latex,
    convert_sidebar,
    convert_simple,
    detect_latex_needed,
    detect_sidebar_needed,
    find_chromium,
    probe_latex_template,
)

__all__ = [
    "LATEX_TEMPLATE",
    "LUA_FILTER",
    "check_tools",
    "convert_auto",
    "validate_pdf_output",
    "inspect_pdf_output",
    "__version__",
    "build_sidebar_asset_head",
    "convert_latex",
    "convert_sidebar",
    "convert_simple",
    "detect_latex_needed",
    "detect_sidebar_needed",
    "find_chromium",
    "probe_latex_template",
    "ensure_web_assets",
]

from .web_assets import ensure_web_assets
