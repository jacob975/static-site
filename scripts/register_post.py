#!/usr/bin/env python3
"""Register a new post into shared widgets data and blog listing.

Usage:
  python3 scripts/register_post.py archives/20260402.html
    python3 scripts/register_post.py archives/20260402.html --category-html archives/category/解構遊戲.html
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import json
import re
import sys
from html import escape
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add a post to shared widgets data and blog.html list"
    )
    parser.add_argument("post_html", type=Path, help="Post HTML path, e.g. archives/20260402.html")
    parser.add_argument(
        "--posts-json",
        type=Path,
        default=Path("assets/data/blog-post-list.json"),
        help="Path to blog post list JSON data file",
    )
    parser.add_argument(
        "--widgets-json",
        type=Path,
        default=Path("assets/data/shared-post-widgets.json"),
        help="Path to widgets JSON data file",
    )
    parser.add_argument(
        "--blog-html",
        type=Path,
        default=Path("blog.html"),
        help="Path to blog.html",
    )
    parser.add_argument(
        "--latest-limit",
        type=int,
        default=5,
        help="Limit latestPosts length. Maximum is always 5.",
    )
    parser.add_argument(
        "--category-html",
        type=Path,
        help="Optional category archive HTML path, e.g. archives/category/解構遊戲.html",
    )
    parser.add_argument(
        "--sitemap",
        type=Path,
        default=Path("sitemap.xml"),
        help="Path to sitemap.xml (skipped if file does not exist)",
    )
    parser.add_argument(
        "--site-url",
        default="https://www.ylchiu.com",
        help="Public base URL used when building sitemap <loc> entries",
    )
    return parser.parse_args()


def must_read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_title(post_html: str, fallback: str) -> str:
    m = re.search(r'<h1 class="wp4wp-page-title[^>]*>(.*?)</h1>', post_html, flags=re.DOTALL)
    if m:
        return strip_tags(m.group(1)).strip()

    m = re.search(r"<title>(.*?)</title>", post_html, flags=re.DOTALL)
    if m:
        title_text = strip_tags(m.group(1)).strip()
        if " - " in title_text:
            return title_text.split(" - ", 1)[0].strip()
        return title_text

    return fallback


def extract_date(stem: str, post_html: str) -> dt.date:
    m = re.search(r'<p class="wb4wp-author-post-date">(.*?)</p>', post_html)
    if m:
        text = m.group(1).strip()
        for fmt in ("%d %b, %Y", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(text, fmt).date()
            except ValueError:
                continue

    m = re.match(r"(\d{8})", stem)
    if m:
        try:
            return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
        except ValueError:
            pass

    return dt.date.today()


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def parse_iso_date(value: str) -> dt.date:
    try:
        return dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return dt.date.min


def extract_cover_image(post_html: str) -> str:
    og_match = re.search(r"<meta\s+property=['\"]og:image['\"]\s+content=['\"](.*?)['\"]", post_html)
    if og_match:
        return og_match.group(1).strip()

    img_match = re.search(r"<img[^>]+src=['\"](.*?)['\"]", post_html, flags=re.IGNORECASE)
    if img_match:
        return img_match.group(1).strip()

    return ""


def normalize_rel_path(path_value: str) -> str:
    return path_value.replace("\\", "/")


def resolve_nav_prefix(path: Path) -> str:
    parts = [p for p in path.parts if p not in ("", ".")]
    if not parts:
        return ""

    if parts[0] == "archives":
        if len(parts) >= 4 and parts[1] == "category" and parts[3] == "page":
            return "../../../../"
        if len(parts) >= 3 and parts[1] == "category":
            return "../../"
        return "../"

    return ""


def ensure_simulator_nav_links(path: Path) -> None:
    text = must_read(path)
    if "槓桿投資模擬器" in text:
        return

    prefix = resolve_nav_prefix(path)
    injected = re.sub(
        rf'(<a href="{re.escape(prefix)}blog\.html"(?: aria-current="page")?>Blog</a></li>)',
        rf'\1\n<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-2201"><a href="{prefix}leverage-simulator.html">槓桿投資模擬器</a></li>',
        text,
        count=2,
    )

    if injected == text:
        return

    path.write_text(injected, encoding="utf-8")


def to_target_relative_href(source_path: Path, target_path: Path, href: str) -> str:
    href = href.strip()
    if not href:
        return href
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or href.startswith("//") or href.startswith("#"):
        return href

    absolute = (source_path.parent / href).resolve()
    relative = os.path.relpath(absolute, target_path.parent.resolve())
    return normalize_rel_path(relative)


def build_category_item_html(post_href: str, image_href: str, title: str, post_date: dt.date) -> str:
    safe_href = escape(post_href, quote=True)
    safe_image_href = escape(image_href, quote=True)
    safe_title = escape(title)
    display_date = post_date.strftime("%d %b, %Y")

    return (
        '<li class="wb4wp-archive-item wb4wp-archive-item-post"><a href="'
        + safe_href
        + '" class="wb4wp-archive-item-blog-link">\n'
        + '  <figure class="wb4wp-archive-item-image">\n'
        + '    <div class="wb4wp-archive-item-image-container">\n'
        + '      <img src="'
        + safe_image_href
        + '" />\n'
        + '    </div>\n'
        + '  </figure>\n\n'
        + '  <h3 class="wb4wp-archive-item-title">\n'
        + '    '
        + safe_title
        + '  </h3>\n\n'
        + '  <p class="wb4wp-archive-item-post-date">\n'
        + '    '
        + display_date
        + '  </p>\n'
        + '</a></li>'
    )


def update_category_html(category_path: Path, item_html: str, post_href_for_dedup: str) -> None:
    text = must_read(category_path)

    ul_match = re.search(
        r'(<ul class="wb4wp-archive-post">)(.*?)(</ul>)',
        text,
        flags=re.DOTALL,
    )
    if not ul_match:
        raise RuntimeError(
            f'Could not find <ul class="wb4wp-archive-post"> block in {category_path}'
        )

    content = ul_match.group(2)
    dedup_pattern = re.compile(
        r'<li class="wb4wp-archive-item wb4wp-archive-item-post">\s*'
        + r'<a href="'
        + re.escape(post_href_for_dedup)
        + r'" class="wb4wp-archive-item-blog-link">.*?</a></li>',
        flags=re.DOTALL,
    )
    content = dedup_pattern.sub("", content)

    content_stripped = content.strip()
    if content_stripped:
        new_content = "\n" + item_html + "\n" + content_stripped + "\n"
    else:
        new_content = "\n" + item_html + "\n"

    updated_ul = ul_match.group(1) + new_content + ul_match.group(3)
    updated_text = text[: ul_match.start()] + updated_ul + text[ul_match.end() :]
    category_path.write_text(updated_text, encoding="utf-8")


def upsert_posts_data(path: Path, title: str, href: str, iso_date: str) -> list[dict[str, str]]:
    posts_data = {"posts": []}
    if path.exists():
        posts_data = json.loads(must_read(path))

    posts = posts_data.get("posts") or []
    if not isinstance(posts, list):
        posts = []

    normalized = []
    for item in posts:
        if not isinstance(item, dict):
            continue
        item_title = str(item.get("title") or "").strip()
        item_href = str(item.get("href") or "").strip()
        item_date = str(item.get("datetime") or "").strip()
        if not item_title or not item_href or not item_date:
            continue
        normalized.append(
            {
                "title": item_title,
                "href": item_href,
                "datetime": item_date,
            }
        )

    normalized = [item for item in normalized if item["href"] != href]
    normalized.append(
        {
            "title": title,
            "href": href,
            "datetime": iso_date,
        }
    )

    normalized.sort(key=lambda item: (parse_iso_date(item["datetime"]), item["href"]), reverse=True)

    posts_data["posts"] = normalized
    path.write_text(json.dumps(posts_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return normalized


def update_widgets_json(path: Path, posts: list[dict[str, str]], latest_limit: int) -> None:
    data = json.loads(must_read(path))

    latest_posts = [{"title": post["title"], "href": post["href"]} for post in posts]

    capped_limit = min(max(latest_limit, 1), 5)
    latest_posts = latest_posts[:capped_limit]

    data["latestPosts"] = latest_posts
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_blog_html(path: Path) -> None:
    text = must_read(path)

    if "id=\"blog-post-list-mount\"" in text:
        return

    heading_anchor = '<h2 class="wp-block-heading">所有文章</h2>'
    if heading_anchor in text:
        replacement = heading_anchor + "\n\n<div id=\"blog-post-list-mount\"></div>"
        updated = text.replace(heading_anchor, replacement, 1)

        # Remove the old hardcoded list block if it exists.
        updated = re.sub(
            r'<ul class="blog-post-list">.*?</ul>',
            "",
            updated,
            count=1,
            flags=re.DOTALL,
        )

        path.write_text(updated, encoding="utf-8")
        return

    ul_match = re.search(
        r'(<ul class="blog-post-list">\s*)(.*?)(\s*</ul>)',
        text,
        flags=re.DOTALL,
    )
    if not ul_match:
        raise RuntimeError("Could not find <ul class=\"blog-post-list\"> block in blog.html")

    replacement = '<div id="blog-post-list-mount"></div>'
    updated = text[: ul_match.start()] + replacement + text[ul_match.end() :]
    path.write_text(updated, encoding="utf-8")


def update_sitemap(path: Path, url: str, iso_date: str) -> None:
    """Upsert a post URL into sitemap.xml.

    - If the <loc> already exists, its <lastmod> is updated.
    - If it does not exist, a new <url> block is appended before </urlset>.
    - If the file does not exist, the function is a no-op.
    """
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")

    existing = re.search(
        r"(<url>\s*<loc>" + re.escape(url) + r"</loc>.*?</url>)",
        text,
        flags=re.DOTALL,
    )

    if existing:
        block = existing.group(1)
        if "<lastmod>" in block:
            new_block = re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{iso_date}</lastmod>", block)
        else:
            new_block = block.replace("</url>", f"    <lastmod>{iso_date}</lastmod>\n  </url>")
        text = text[: existing.start()] + new_block + text[existing.end() :]
    else:
        new_entry = (
            f"  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{iso_date}</lastmod>\n"
            f"    <priority>0.7</priority>\n"
            f"  </url>\n\n"
        )
        text = text.replace("</urlset>", new_entry + "</urlset>")

    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()

    post_path = args.post_html
    if not post_path.exists():
        raise FileNotFoundError(f"Post file does not exist: {post_path}")

    post_html = must_read(post_path)
    stem = post_path.stem
    href = f"archives/{post_path.name}"
    title = extract_title(post_html, fallback=stem)
    post_date = extract_date(stem, post_html)
    cover_image = extract_cover_image(post_html)
    iso_date = post_date.isoformat()

    posts = upsert_posts_data(args.posts_json, title, href, iso_date)
    update_widgets_json(args.widgets_json, posts, args.latest_limit)
    update_blog_html(args.blog_html)
    ensure_simulator_nav_links(args.blog_html)
    ensure_simulator_nav_links(post_path)

    post_url = f"{args.site_url.rstrip('/')}/archives/{post_path.name}"
    update_sitemap(args.sitemap, post_url, iso_date)

    if args.category_html:
        category_post_href = to_target_relative_href(post_path, args.category_html, href)
        category_image_href = to_target_relative_href(post_path, args.category_html, cover_image)
        item_html = build_category_item_html(
            post_href=category_post_href,
            image_href=category_image_href,
            title=title,
            post_date=post_date,
        )
        update_category_html(
            category_path=args.category_html,
            item_html=item_html,
            post_href_for_dedup=category_post_href,
        )
        ensure_simulator_nav_links(args.category_html)

    print(f"Updated posts data: {args.posts_json}")
    print(f"Updated widgets data: {args.widgets_json}")
    print(f"Ensured blog mount exists: {args.blog_html}")
    if args.sitemap.exists():
        print(f"Updated sitemap: {args.sitemap}")
    if args.category_html:
        print(f"Updated category archive: {args.category_html}")
    print(f"Registered post: {href} ({title}, {iso_date})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)