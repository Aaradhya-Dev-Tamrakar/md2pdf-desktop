# Changelog

All notable changes to this project are documented here.

## [0.4.0] — Studio UI/UX and adaptive display scaling

- Added DPI-aware desktop scaling with a separate persisted UI zoom control (80–150%).
- Added Ctrl+Plus/Ctrl+Minus/Ctrl+0 and Ctrl+mouse-wheel zoom controls.
- Added display-DPI monitoring so UI scaling can follow monitor changes while preserving the selected zoom.
- Added persistent light/dark appearance and six accent palettes.
- Reworked the desktop layout around Markdown editing, renderer selection, PDF settings, and export.
- Added clearer renderer/environment status, output-path controls, editor metrics, and export progress.
- Added desktop app syntax validation and adaptive-scaling unit tests.

## [0.3.0] — Phase 3 release-quality candidate

- Added semantic PDF parsing with `pypdf`.
- Added a maintained release regression corpus covering prose, tables, code, Unicode, pagination, math, Mermaid, and GFM alerts.
- Added minimum-page and extracted-text assertions to real renderer integration tests.
- Added installed CLI version reporting and release metadata.
- Added source-distribution/wheel content verification and an automated GitHub Release workflow.
- Kept cross-platform rendering limitations explicit; no byte-identical PDF guarantee is claimed.

## [0.2.0]

Phase 2 productization and renderer reliability baseline.
