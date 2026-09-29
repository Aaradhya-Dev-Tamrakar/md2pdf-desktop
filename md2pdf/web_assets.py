"""Deterministic provisioning for Sidebar browser assets.

The renderer uses exact npm package versions and verifies the package tarball
SHA-512 integrity before extracting only the browser assets it needs.

Assets are cached outside the Python installation so the package remains
installable without shipping binary font files.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import os
import shutil
import tarfile
from pathlib import Path
from urllib.request import Request, urlopen


ASSET_SPEC = {
    "katex": {
        "version": "0.16.11",
        "url": "https://registry.npmjs.org/katex/-/katex-0.16.11.tgz",
        "integrity": "sha512-RQrI8rlHY92OLf3rho/Ts8i/XvjgguEjOkO1BEXcU3N8BqPpSzBNwV/G0Ukr+P/l3ivvJUE/Fa/CwbS6HesGNQ==",
        "files": (
            "package/dist/katex.min.css",
            "package/dist/katex.min.js",
            "package/dist/contrib/auto-render.min.js",
            "package/dist/fonts",
        ),
    },
    "mermaid": {
        "version": "10.9.3",
        "url": "https://registry.npmjs.org/mermaid/-/mermaid-10.9.3.tgz",
        "integrity": "sha512-V80X1isSEvAewIL3xhmz/rVmc27CVljcsbWxkxlWJWY/1kQa4XOABqpDl2qQLGKzpKm6WbTfUEKImBlUfFYArw==",
        "files": ("package/dist/mermaid.min.js",),
    },
}

MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
ASSET_ENV = "MD2PDF_ASSET_DIR"


def default_asset_dir() -> Path:
    configured = os.environ.get(ASSET_ENV)
    if configured:
        return Path(configured).expanduser().resolve()
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or str(Path.home())
        return Path(root) / "md2pdf" / "web-assets"
    return Path.home() / ".cache" / "md2pdf" / "web-assets"


def _verify_integrity(data: bytes, integrity: str) -> None:
    algorithm, encoded = integrity.split("-", 1)
    if algorithm != "sha512":
        raise RuntimeError(f"Unsupported integrity algorithm: {algorithm}")
    expected = base64.b64decode(encoded)
    actual = hashlib.sha512(data).digest()
    if actual != expected:
        raise RuntimeError("Downloaded asset archive failed SHA-512 integrity verification.")


def _safe_member(member: tarfile.TarInfo) -> bool:
    if member.name.startswith("/") or ".." in Path(member.name).parts:
        return False
    return member.isfile() or member.isdir()


def _extract_selected(archive_bytes: bytes, destination: Path, prefixes: tuple[str, ...]) -> None:
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        for member in archive.getmembers():
            if not _safe_member(member):
                continue
            if not any(
                member.name == prefix or member.name.startswith(prefix.rstrip("/") + "/")
                for prefix in prefixes
            ):
                continue
            relative = Path(member.name).relative_to("package/dist")
            target = destination / relative
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"Could not extract asset member: {member.name}")
            with source, open(target, "wb") as output:
                shutil.copyfileobj(source, output)


def _required_assets_present(root: Path) -> bool:
    required = (
        root / "katex.min.css",
        root / "katex.min.js",
        root / "contrib" / "auto-render.min.js",
        root / "fonts",
        root / "mermaid.min.js",
    )
    return all(path.exists() for path in required)


def ensure_web_assets(*, offline: bool = False, asset_dir: Path | None = None) -> Path:
    """Return a verified local browser-asset directory.

    Existing complete caches are reused without network access. Missing caches
    are downloaded from the exact npm tarballs in ASSET_SPEC unless offline is
    requested (or MD2PDF_OFFLINE=1 is set).
    """
    root = (asset_dir or default_asset_dir()).resolve()
    if _required_assets_present(root):
        return root

    if offline or os.environ.get("MD2PDF_OFFLINE") == "1":
        raise RuntimeError(
            f"Sidebar browser assets are not provisioned at {root}. "
            "Run `python -m md2pdf.web_assets` while online, then retry offline."
        )

    root.parent.mkdir(parents=True, exist_ok=True)
    staging = root.with_name(root.name + ".staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    try:
        for package_name, spec in ASSET_SPEC.items():
            request = Request(spec["url"], headers={"User-Agent": "md2pdf-desktop/0.2"})
            with urlopen(request, timeout=60) as response:
                chunks = []
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise RuntimeError(f"{package_name} asset archive exceeds the download limit.")
                    chunks.append(chunk)
            archive_bytes = b"".join(chunks)
            _verify_integrity(archive_bytes, spec["integrity"])
            _extract_selected(archive_bytes, staging, spec["files"])

        if root.exists():
            shutil.rmtree(root)
        staging.rename(root)
        if not _required_assets_present(root):
            raise RuntimeError(f"Asset provisioning completed incompletely: {root}")
        return root
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provision verified local md2pdf Sidebar web assets.")
    parser.add_argument("--offline", action="store_true", help="Only inspect/use an existing local asset cache.")
    parser.add_argument("--asset-dir", type=Path, help="Override the local asset cache directory.")
    args = parser.parse_args(argv)
    path = ensure_web_assets(offline=args.offline, asset_dir=args.asset_dir)
    print(f"Sidebar assets ready: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
