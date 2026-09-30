# PyInstaller build specification for the Windows desktop release.

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


ROOT = Path(SPEC).resolve().parents[2]
MD2PDF_DIR = ROOT / "md2pdf"
TEMPLATES_DIR = MD2PDF_DIR / "templates"
MANIFEST = ROOT / "packaging" / "windows" / "md2pdf-studio.manifest"
VERSION_FILE = ROOT / "packaging" / "windows" / "version_info.txt"

datas = collect_data_files("md2pdf")
for pattern in ("*.latex", "*.lua"):
    for source in sorted(TEMPLATES_DIR.glob(pattern)):
        datas.append((str(source), "md2pdf/templates"))

a = Analysis(
    [str(ROOT / "md2pdf_app.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="md2pdf-studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=str(VERSION_FILE),
    manifest=str(MANIFEST),
)
