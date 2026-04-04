# Copilot Instructions

## Publishing a New Post

The full workflow to publish a post:

1. Write content in `archives/yyyymmdd.md` (filename determines post date)
2. Convert to HTML:
   ```bash
   python3 scripts/md_to_html.py archives/20260402.md
   ```
3. Register the post into data files:
   ```bash
   python3 scripts/register_post.py archives/20260402.html
   ```
4. Validate the generated HTML:
   ```bash
   ./scripts/check-archive-includes.sh
   # or recursively (includes category pages):
   ./scripts/check-archive-includes.sh --recursive
   ```
5. Add the new post URL to `sitemap.xml` (a `<url>` entry with `<loc>` and `<lastmod>`)

Install the required Python dependency once:
```bash
python3 -m pip install markdown
```

## Architecture

This is a **static site** hosted on GitHub Pages. There is no build system or server — everything is pre-rendered HTML with a thin JS layer.

**Content pipeline:**
- `archives/yyyymmdd.md` → `scripts/md_to_html.py` → `archives/yyyymmdd.html`
- `scripts/register_post.py` then updates two JSON data files and `blog.html`

**Runtime data flow:**
- `assets/data/blog-post-list.json` — full ordered post list; consumed by `assets/js/blog-post-list.js` to dynamically render the post list on `blog.html` and the paginated post cards on `index.html`
- `assets/data/shared-post-widgets.json` — latest 5 posts + category links; consumed by `assets/js/shared-post-widgets.js` to inject sidebar-style widgets into archive pages, `blog.html`, and `index.html`

**CSS/JS dependencies** — archive pages link to `wp-content/` and `wp-includes/` directories (vendored WordPress theme assets) using relative paths starting with `../`. These are static files; do not edit them.

## Key Conventions

### Archive HTML pages (`archives/*.html`)
Every generated archive page must include all three of these — `check-archive-includes.sh` enforces it:
- `<link rel='stylesheet' href='../assets/css/pages/mathjax-fixes.css' ...>`
- `<script src="../assets/js/shared-post-widgets.js"></script>`
- Google Analytics gtag snippet (loader + `gtag("config", ...)`)

**Common typo to avoid:** `asserts/js/shared-post-widgets.js` (not `assets/`). The check script explicitly catches this.

### Markdown → HTML conversion
- The `# H1` title in the `.md` file becomes the page `<title>` and post heading — it is stripped from the body HTML to avoid duplication
- `h2`/`h3` elements get `class="wp-block-heading"` added automatically
- Tables are wrapped in `<figure class="wp-block-table">` with inline border styles
- Math: inline `$...$` and `\(...\)` delimiters are supported via MathJax 4; `%` inside math is auto-escaped to `\%`
- OG image is inferred from the first image found in the markdown

### Post filenames
- New posts: `yyyymmdd.md` (e.g., `20260402.md`) — the date is parsed from the filename
- Suffix variants are allowed for same-day posts (e.g., `20260330a.md`)
- Older migrated posts use numeric IDs (e.g., `archives/2059.html`) — these are legacy

### Data files
- `blog-post-list.json`: `{ "posts": [{ "title", "href", "datetime" }] }` — sorted newest-first; `href` is relative to site root (e.g., `"archives/20260402.html"`)
- `shared-post-widgets.json`: `{ "latestPosts": [...], "categories": [...] }` — `latestPosts` is capped at 5

### Navigation
`register_post.py` auto-injects the `槓桿投資模擬器` nav link into pages that are missing it. If adding nav items manually, ensure they appear in both the `<nav>` header and `<footer>` nav, in both archive pages and category pages.

### MathJax fixes CSS
Put generic formula rendering fixes in `assets/css/pages/mathjax-fixes.css`. Per-page overrides go in that page's own stylesheet. See `assets/css/pages/README-mathjax-fixes.md` for details.
