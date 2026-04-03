#!/usr/bin/env python3
"""Convert Markdown posts into static HTML pages for this site.

Usage examples:
  python3 scripts/md_to_html.py archives/20260402.md
  python3 scripts/md_to_html.py archives/20260402.md -o archives/20260402.html
  python3 scripts/md_to_html.py archives/20260402.md --author "Yi-Lung Chiu"
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import importlib
import re
import sys
from pathlib import Path

try:
    markdown = importlib.import_module("markdown")
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: markdown\n"
        "Install it with: python3 -m pip install markdown"
    ) from exc


HEAD_TEMPLATE = """<!doctype html>
<html dir="ltr" lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <title>{doc_title}</title>
    <meta property='og:type' content='article' />
    <meta property='og:title' content='{doc_title}' />
    <meta property='og:url' content='{og_url}' />
    <meta property='og:image' content='{og_image}' />
    <meta name='twitter:card' content='summary_large_image' />
    <meta name='twitter:title' content='{doc_title}' />
    <meta name='twitter:image' content='{og_image}' />

    <link rel='stylesheet' href='https://fonts.googleapis.com/css?display=swap&family=Lato:400|Montserrat:400' />

    <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$','$']],
        processEscapes: true
      }},
      options: {{
        ignoreHtmlClass: 'tex2jax_ignore|editor-rich-text'
      }}
    }};
    </script>

    <link rel='dns-prefetch' href='https://cdn.jsdelivr.net/' />
    <link rel='dns-prefetch' href='https://www.googletagmanager.com/' />

    <link rel='stylesheet' id='ivory-search-styles-css' href='../wp-content/plugins/add-search-to-menu/public/css/ivory-search.min.css%3Fver=5.5.14.css' media='all' />
    <link rel='stylesheet' id='wb4wp-theme-css' href='../wp-content/themes/wb4wp-wordpress-theme-production/dist/main.css%3Fver=1.0.1307.css' media='all' />
    <link rel='stylesheet' id='wb4wp-theme-blog-css' href='../wp-content/themes/wb4wp-wordpress-theme-production/dist/blog/blog.css%3Fver=1.0.1307.css' media='all' />
    <link rel='stylesheet' id='wb4wp-theme-jetpack-css' href='../wp-content/themes/wb4wp-wordpress-theme-production/dist/jetpack/jetpack.css%3Fver=1.0.1307.css' media='all' />
    <link rel='stylesheet' id='navigation-5-css' href='../wp-content/themes/wb4wp-wordpress-theme-production/dist/navigation-5/navigation-5.css%3Fver=1.0.1307.css' media='all' />
    <link rel='stylesheet' id='footer-4-css' href='../wp-content/themes/wb4wp-wordpress-theme-production/dist/footer-4/footer-4.css%3Fver=1.0.1307.css' media='all' />
    <link rel='stylesheet' id='wp-block-paragraph-css' href='../wp-includes/blocks/paragraph/style.min.css%3Fver=6.9.4.css' media='all' />
    <link rel='stylesheet' id='wp-block-heading-css' href='../wp-includes/blocks/heading/style.min.css%3Fver=6.9.4.css' media='all' />
    <link rel='stylesheet' id='wp-block-list-css' href='../wp-includes/blocks/list/style.min.css%3Fver=6.9.4.css' media='all' />
    <link rel='stylesheet' id='wp-block-categories-css' href='../wp-includes/blocks/categories/style.min.css%3Fver=6.9.4.css' media='all' />
    <link rel='stylesheet' id='wp-block-latest-posts-css' href='../wp-includes/blocks/latest-posts/style.min.css%3Fver=6.9.4.css' media='all' />
    <link rel='stylesheet' id='wp-block-table-css' href='../wp-includes/blocks/table/style.min.css%3Fver=6.9.4.css' media='all' />
    <link rel='stylesheet' id='block-generic-section-css' href='../wp-content/plugins/wb4wp-wordpress-plugin-bluehost-production/build/block-generic-section.css%3Fver=29ffbded135d1e494ff0b47bd8c692ad.css' media='all' />
    <link rel='stylesheet' id='wp-block-columns-css' href='../wp-includes/blocks/columns/style.min.css%3Fver=6.9.4.css' media='all' />
    <link rel='stylesheet' id='container-css' href='../wp-content/plugins/wb4wp-wordpress-plugin-bluehost-production/build/container.css%3Fver=63371796415726a33c060cd169fcd144.css' media='all' />
    <link rel='stylesheet' id='wp-block-search-css' href='../wp-includes/blocks/search/style.min.css%3Fver=6.9.4.css' media='all' />
    <script src="../wp-includes/js/jquery/jquery.min.js%3Fver=3.7.1" id="jquery-core-js"></script>
    <script src="../wp-includes/js/jquery/jquery-migrate.min.js%3Fver=3.4.1" id="jquery-migrate-js"></script>

    <!-- Google tag (gtag.js) snippet added by Site Kit -->
    <script src="https://www.googletagmanager.com/gtag/js?id=GT-WF8BSRC" id="google_gtagjs-js" async></script>
    <script id="google_gtagjs-js-after">
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("set","linker",{{"domains":["ylchiu.com"]}});
    gtag("js", new Date());
    gtag("set", "developer_id.dZTNiMT", true);
    gtag("config", "GT-WF8BSRC");
    </script>

    <link rel='shortlink' href='../archives/{slug}.html' />
    <link rel='stylesheet' href='../assets/css/common.css' media='all' />
    <link rel='stylesheet' href='../assets/css/pages/mathjax-fixes.css' media='all' />

    <style>
      .post-content-image {{
        width: 50%;
        max-width: 100%;
        height: auto;
      }}

      .spoiler {{
        color: #000;
        background-color: #000;
      }}
    </style>

</head>
<body class="wp-singular post-template-default single single-post postid-{slug} single-format-standard wp-embed-responsive wp-theme-wb4wp-wordpress-theme-production wb4wp-wordpress-theme-production">

<nav class="wb4wp-navbar background-id_1 navigation-5 sticky">
    <div class="wb4wp-wrapper">
        <div class="wb4wp-brand">
            <a href="../index.html" aria-label="Home" rel="home">
                <div class="wb4wp-text">YLC</div>
            </a>
        </div>

        <div class="wb4wp-menu-container">
            <div class="wb4wp-menu">
                <ul id="menu-bluehost-website-builder" class="wb4wp-menu-items">
                    <li class="menu-item"><a href="../index.html">Home</a></li>
                    <li class="menu-item"><a href="../intro.html">Intro</a></li>
                    <li class="menu-item"><a href="../blog.html">Blog</a></li>
                    <li class="menu-item"><a href="../leverage-simulator.html">槓桿投資模擬器</a></li>
                </ul>
            </div>
        </div>

        <button class="wb4wp-button wb4wp-menu-button" aria-label="Open Menu">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
        </button>
    </div>
</nav>

<div id="page" class="site kv-site kv-main">
    <main id="primary" class="site-main">
        <header>
            <h1 class="page-title screen-reader-text">{page_title}</h1>
        </header>

        <article id="post-{slug}" class="post-{slug} post type-post status-publish format-standard has-post-thumbnail hentry category-4">
            <header class="wb4wp-blog-container entry-header wp4wp-header-image-layout-2 wp4wp-header-image">
                <p class="wb4wp-author-post-date">{date_human}</p>
                <div class="wbwp4-cover has-no-cover">
                    <h1 class="wp4wp-page-title page-title entry-title has-huge-font-size">{page_title}</h1>
                </div>
            </header>

            <div class="wb4wp-blog-container">
                <content class="kv-page entry-content">
                    <div class="kv-page-content">
"""


FOOT_TEMPLATE = """
                        <div id="shared-post-widgets-mount"></div>

                        <hr class="wp-block-separator is-style-wide">
                        <div class="wp4wp-header-meta">
                            <div class="wb4wp-author">
                                <div class="wb4wp-author-detail">
                                    <p class="wb4wp-author-name has-small-font-size">{author}</p>
                                    <p class="wb4wp-author-post-date">{date_human}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </content>
            </div>
        </article>
    </main>
</div>

<footer class="footer-4 wb4wp-footer" style="--wb4wp-footer-background: var(--wb4wp-text-background);--wb4wp-footer-text: var(--wb4wp-font-color-text);--wb4wp-footer-text-softer: var(--wb4wp-font-color-text-softer);--wb4wp-footer-colophon-background: var(--wb4wp-text-background-stronger);--wb4wp-footer-social-background: var(--wb4wp-text-social-background);--wb4wp-footer-social-color: var(--wb4wp-text-social-icon);--wb4wp-footer-border-color: var(--wb4wp-background-on-text-10);--wb4wp-footer-link: var(--wb4wp-font-color-text-softer);--wb4wp-footer-link-hover: var(--wb4wp-font-color-text);">
    <div class="wb4wp-container">
        <div class="wb4wp-footer-section wb4wp-footer-header wb4wp-divider-line">
            <nav class="wb4wp-footer-nav">
                <ul class="wb4wp-footer-menu-items">
                    <li class="menu-item"><a href="../index.html">Home</a></li>
                    <li class="menu-item"><a href="../intro.html">Intro</a></li>
                    <li class="menu-item"><a href="../blog.html">Blog</a></li>
                    <li class="menu-item"><a href="../leverage-simulator.html">槓桿投資模擬器</a></li>
                </ul>
            </nav>
        </div>
        <div class="wb4wp-footer-section wb4wp-footer-body">
            <div class="wb4wp-info-block">
                <a class="wb4wp-copy contact-link" href="mailto:{email}">{email}</a>
            </div>
        </div>
    </div>
    <div class="wb4wp-colophon">
        <div class="wb4wp-left">
            <p class="wb4wp-copyright">&copy; {year}</p>
        </div>
    </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js?ver=6.9.4" id="mathjax-js"></script>
<script src="../wp-content/themes/wb4wp-wordpress-theme-production/dist/navigation-5/navigation-5.js%3Fver=1.0.1307" id="navigation-5-js"></script>
<script src="../assets/js/shared-post-widgets.js"></script>
</body>
</html>
"""


def extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def parse_date(stem: str, override: str | None) -> dt.date:
    if override:
        return dt.datetime.strptime(override, "%Y-%m-%d").date()

    m = re.match(r"(\d{8})", stem)
    if m:
        try:
            return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
        except ValueError:
            pass
    return dt.date.today()


def escape_percent_in_math(md_text: str) -> str:
    """Escape '%' only inside math delimiters so MathJax renders it literally."""

    def escape_content(content: str) -> str:
        return re.sub(r"(?<!\\)%", r"\\%", content)

    def replace_dollar_math(match: re.Match[str]) -> str:
        inner = escape_content(match.group(1))
        return f"${inner}$"

    def replace_paren_math(match: re.Match[str]) -> str:
        inner = escape_content(match.group(1))
        return f"\\({inner}\\)"

    # Inline math with $...$
    md_text = re.sub(r"(?<!\\)\$(.+?)(?<!\\)\$", replace_dollar_math, md_text, flags=re.DOTALL)
    # Inline math with \(...\)
    md_text = re.sub(r"\\\((.+?)\\\)", replace_paren_math, md_text, flags=re.DOTALL)
    return md_text


def find_first_image(markdown_text: str) -> str | None:
    html_img = re.search(r"<img\s+[^>]*src=['\"]([^'\"]+)['\"]", markdown_text, flags=re.IGNORECASE)
    if html_img:
        return html_img.group(1)

    md_img = re.search(r"!\[[^\]]*\]\(([^)\s]+)", markdown_text)
    if md_img:
        return md_img.group(1)

    return None


def to_absolute_image_url(image_src: str | None, base_url: str) -> str:
    if not image_src:
        return f"{base_url}/wp-content/uploads/default-og.jpg"
    if image_src.startswith("http://") or image_src.startswith("https://"):
        return image_src

    cleaned = image_src.lstrip("./")
    while cleaned.startswith("../"):
        cleaned = cleaned[3:]
    return f"{base_url}/{cleaned}"


def add_heading_classes(html_body: str) -> str:
    html_body = re.sub(r"<h2\b[^>]*>", '<h2 class="wp-block-heading">', html_body)
    html_body = re.sub(r"<h3\b[^>]*>", '<h3 class="wp-block-heading">', html_body)
    return html_body


def remove_first_h1(html_body: str) -> str:
    return re.sub(r"^\s*<h1\b[^>]*>.*?</h1>\s*", "", html_body, count=1, flags=re.DOTALL)


def style_tables(html_body: str) -> str:
    def repl(match: re.Match[str]) -> str:
        table_html = match.group(0)
        table_html = re.sub(
            r"<table\b[^>]*>",
            '<table style="width:100%;border-collapse:collapse;">',
            table_html,
            count=1,
        )
        table_html = re.sub(
            r"<th\b[^>]*>",
            '<th style="border:1px solid #ccc;padding:8px;text-align:left;">',
            table_html,
        )
        table_html = re.sub(
            r"<td\b[^>]*>",
            '<td style="border:1px solid #ccc;padding:8px;">',
            table_html,
        )
        return f'<figure class="wp-block-table">\n{table_html}\n</figure>'

    return re.sub(r"<table\b[^>]*>.*?</table>", repl, html_body, flags=re.DOTALL)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert a markdown article to site-style HTML")
    parser.add_argument("input", type=Path, help="Input markdown path")
    parser.add_argument("-o", "--output", type=Path, help="Output html path")
    parser.add_argument("--site-url", default="https://ylchiu.com", help="Public site base URL")
    parser.add_argument("--author", default="Yi-Lung Chiu", help="Author name")
    parser.add_argument("--email", default="ylchiu@gapp.nthu.edu.tw", help="Footer email")
    parser.add_argument("--title-suffix", default="Yi Lung Chiu", help="Suffix for <title>")
    parser.add_argument("--date", help="Post date in YYYY-MM-DD")
    return parser


def resolve_output_path(input_path: Path, output_arg: Path | None) -> Path:
    """Resolve final output path.

    Rules:
    - If -o is omitted, use input path with .html suffix.
    - If -o points to an existing directory, write to <dir>/<input_stem>.html.
    - Otherwise, treat -o as file path.
    """
    if output_arg is None:
        return input_path.with_suffix(".html")

    if output_arg.exists() and output_arg.is_dir():
        return output_arg / f"{input_path.stem}.html"

    return output_arg


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    in_path = args.input
    if not in_path.exists():
        parser.error(f"Input file does not exist: {in_path}")

    out_path = resolve_output_path(in_path, args.output)
    if out_path.exists() and out_path.is_dir():
        parser.error(f"Output path resolves to a directory, expected a .html file: {out_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    slug = out_path.stem

    md_text = in_path.read_text(encoding="utf-8")
    md_text = escape_percent_in_math(md_text)
    page_title = extract_title(md_text, fallback=slug)
    post_date = parse_date(slug, args.date)
    date_human = post_date.strftime("%d %b, %Y")

    body_html = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "sane_lists"],
        output_format="html5",
    )
    body_html = remove_first_h1(body_html)
    body_html = add_heading_classes(body_html)
    body_html = style_tables(body_html)

    doc_title = f"{page_title} - {args.title_suffix}"
    og_url = f"{args.site_url.rstrip('/')}/archives/{slug}.html"
    og_image = to_absolute_image_url(find_first_image(md_text), args.site_url.rstrip("/"))

    html_doc = (
        HEAD_TEMPLATE.format(
            doc_title=html.escape(doc_title),
            og_url=html.escape(og_url),
            og_image=html.escape(og_image),
            slug=html.escape(slug),
            page_title=html.escape(page_title),
            date_human=html.escape(date_human),
        )
        + body_html
        + FOOT_TEMPLATE.format(
            author=html.escape(args.author),
            date_human=html.escape(date_human),
            email=html.escape(args.email),
            year=post_date.year,
        )
    )

    out_path.write_text(html_doc, encoding="utf-8")
    print(f"Generated: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())