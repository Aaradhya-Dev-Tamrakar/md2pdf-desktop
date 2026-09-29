# Stabilization pass — September 2026

This document records the stabilization baseline and the Phase 2 reliability extensions. It is intentionally not a renderer rewrite.

## Changes

- Centralized external-process invocation in `md2pdf.core._run_process`, with a default timeout and normalized launch/timeout errors.
- Added `validate_pdf_output` to reject missing, empty, non-PDF, truncated, or page-less outputs.
- Applied output validation to Sidebar, LaTeX, and Simple conversion paths.
- Made `convert_auto` report attempted backends and their failures instead of silently swallowing every exception.
- Routed MCP `mode="auto"` through the shared core orchestrator.
- Added standard-library regression tests and a GitHub Actions workflow.
- Moved desktop PDF conversion off the Tkinter UI thread.
- Hardened `sync.ps1` against mixed staging, index mutation during `-WhatIf`, and silent remote rewriting.
- Added package build/installation checks plus real Pandoc + wkhtmltopdf integration coverage.
- Replaced Sidebar CDN-at-render-time loading with exact-version, SHA-512-verified local browser assets and an offline mode.

## Validation contract and limitations

The built-in validator is a lightweight integrity check. It checks the PDF signature, EOF marker, and presence of a page-object marker. It is **not** a full PDF parser and does not prove visual correctness, searchable text, correct math, or diagram fidelity. A later pass should add a parser dependency such as `pypdf` (if acceptable) and integration fixtures rendered with the external toolchain.

The new unit tests do not require Pandoc, Chromium, LaTeX, or wkhtmltopdf because external renderers are mocked in orchestration tests. Real renderer integration tests remain necessary.

## Remaining limitations

- First-time Sidebar asset provisioning still needs network access to obtain the exact npm tarballs. After provisioning, `MD2PDF_OFFLINE=1` enforces cache-only operation.
- Browser engine, operating-system, and font differences can still affect pixel-level output even with fixed web assets.
- Renderer-specific visual pagination behavior is not yet covered by regression fixtures.
- The built-in PDF validator remains lightweight; a later phase can add a full PDF parser and semantic PDF assertions.

## Run tests

```sh
python -m unittest discover -s tests -v
```
