# Stabilization pass — September 2026

This branch contains a focused reliability pass. It is intentionally not a renderer rewrite.

## Changes

- Centralized external-process invocation in `md2pdf.core._run_process`, with a default timeout and normalized launch/timeout errors.
- Added `validate_pdf_output` to reject missing, empty, non-PDF, truncated, or page-less outputs.
- Applied output validation to Sidebar, LaTeX, and Simple conversion paths.
- Made `convert_auto` report attempted backends and their failures instead of silently swallowing every exception.
- Routed MCP `mode="auto"` through the shared core orchestrator.
- Added standard-library regression tests and a GitHub Actions workflow.

## Validation contract and limitations

The built-in validator is a lightweight integrity check. It checks the PDF signature, EOF marker, and presence of a page-object marker. It is **not** a full PDF parser and does not prove visual correctness, searchable text, correct math, or diagram fidelity. A later pass should add a parser dependency such as `pypdf` (if acceptable) and integration fixtures rendered with the external toolchain.

The new unit tests do not require Pandoc, Chromium, LaTeX, or wkhtmltopdf because external renderers are mocked in orchestration tests. Real renderer integration tests remain necessary.

## Known issues not addressed here

- Sidebar rendering still loads KaTeX and Mermaid from remote CDN URLs; offline/deterministic rendering needs vendored assets.
- Markdown normalization still uses global string replacements in places; an AST-aware transform should replace those in a dedicated change.
- The Tkinter conversion action still runs synchronously on the UI thread.
- The sync script's staging/remote behavior needs a separate safety-focused review.
- Renderer-specific visual pagination behavior is not yet covered by regression fixtures.

## Run tests

```sh
python -m unittest discover -s tests -v
```
