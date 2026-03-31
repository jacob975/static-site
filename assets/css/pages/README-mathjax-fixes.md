# MathJax Fixes for Archive Pages

This project uses a shared stylesheet to prevent MathJax formulas from being clipped (especially lower parts of glyphs in inline/display math).

## Shared file

- Path: `assets/css/pages/mathjax-fixes.css`
- Purpose: Keep MathJax CHTML output visible and stable across archive article pages.

## How it is loaded

- Every top-level archive article page in `archives/*.html` includes:
  - `<link rel='stylesheet' href='../assets/css/pages/mathjax-fixes.css' media='all' />`
- The link is inserted near the end of each page `<head>`.

## Maintenance rules

1. Put generic formula rendering fixes in `assets/css/pages/mathjax-fixes.css`.
2. Avoid duplicating the same MathJax rules in per-page files like `archives-2035.css`.
3. If a single page needs exceptional handling, keep page-only overrides in that page's own stylesheet.
4. After updates, verify at least one page with inline math and one with display math.

## Quick check commands

From repository root:

```bash
rg -l "mathjax-fixes.css" archives/*.html | wc -l
ls archives/*.html | wc -l
```

Both numbers should match.

## Full include checker script

Use the checker script to validate archive pages for all required includes:

- `mathjax-fixes.css`
- `assets/js/shared-post-widgets.js`
- Google Analytics snippet (`gtag` loader + `gtag("config", ...)`)
- typo path check: `asserts/js/shared-post-widgets.js`

Run from repository root:

```bash
./scripts/check-archive-includes.sh
```

Optional: include category pages under `archives/**`:

```bash
./scripts/check-archive-includes.sh --recursive
```

Exit code:

- `0`: all checks passed
- `1`: at least one file is missing required includes (or has typo path)
