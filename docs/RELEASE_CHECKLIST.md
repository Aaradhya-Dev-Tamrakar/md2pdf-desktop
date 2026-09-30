# Release Checklist

Phase 3 is the release-quality verification layer for the existing Phase 2 feature set.

## Automated gates

- [x] Python 3.10 / 3.11 / 3.12 regression matrix.
- [x] Build source distribution and wheel.
- [x] Verify packaged LaTeX/Lua templates in both distributions.
- [x] Smoke-test the installed wheel and `md2pdf --version`.
- [x] Parse integration PDFs with `pypdf`.
- [x] Run the Simple renderer against the release corpus.
- [x] Run the Sidebar/Chromium renderer against specialized fixtures with offline assets.
- [x] Require minimum page counts and extracted-text markers for release fixtures.
- [x] Generate GitHub Release artifacts from `v*` tags.
- [x] Build a Windows x64 `md2pdf Studio` executable with an embedded Per-Monitor V2 manifest.

## Manual gates before publishing

- [ ] Select and add an explicit repository license. Phase 3 does not infer a license choice.
- [ ] Verify Pandoc, Chromium/Chrome/Edge, TeX (when used), and wkhtmltopdf versions on the supported Windows environment.
- [ ] Visually inspect the corpus PDFs on the primary target environment, especially pagination, equations, Mermaid diagrams, fonts, and GFM alerts.
- [ ] Confirm the release notes and installation instructions match the target artifact.
- [ ] Launch the Windows bundle on the supported high-DPI Windows environment and verify crisp UI, zoom persistence, theme persistence, and native renderer discovery.
- [ ] Create the version tag only after CI is green on the exact commit intended for release.

## Scope boundary

The project does not claim byte-for-byte PDF reproducibility across operating systems or browser/font stacks. The automated contract is parseability, page existence, selected semantic markers, and renderer-specific corpus coverage.
