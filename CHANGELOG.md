# Changelog

All notable changes to this project are documented here.

## [0.3.0] — Phase 3 release-quality candidate

- Added semantic PDF parsing with `pypdf`.
- Added a maintained release regression corpus covering prose, tables, code, Unicode, pagination, math, Mermaid, and GFM alerts.
- Added minimum-page and extracted-text assertions to real renderer integration tests.
- Added installed CLI version reporting and release metadata.
- Added source-distribution/wheel content verification and an automated GitHub Release workflow.
- Kept cross-platform rendering limitations explicit; no byte-identical PDF guarantee is claimed.

## [0.2.0]

Phase 2 productization and renderer reliability baseline.
