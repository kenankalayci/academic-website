#!/usr/bin/env python3
"""Import published WordPress pages/posts from a WXR export into Hugo content files.

This script intentionally keeps HTML content untouched inside Markdown files so we can
preserve formatting and links during the first migration pass.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET

NS = {
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "wp": "http://wordpress.org/export/1.2/",
}

LOCAL_UPLOAD_RE = re.compile(r"https?://kenankalayci\.com/(wp-content/uploads/[^\"'\s)]+)", re.IGNORECASE)
ANY_PDF_RE = re.compile(r"https?://[^\"'\s)]+\.pdf", re.IGNORECASE)
TWITTER_WIDGET_RE = re.compile(
    r'<a class="twitter-follow-button"[^>]*>.*?</a><script[^>]*platform\.twitter\.com/widgets\.js[^>]*></script>',
    re.IGNORECASE,
)
GOOGLE_MAPS_IFRAME_RE = re.compile(r"<iframe[^>]*google\.com/maps/embed[^>]*></iframe>", re.IGNORECASE)
ABSOLUTE_INTERNAL_RE = re.compile(r"https?://kenankalayci\.com(?P<path>/[^\"'\s<]*)", re.IGNORECASE)

LEGACY_INTERNAL_PATH_MAP = {
    "/blog-posts/confusopoly-why-companies-are-motivated-to-deliberately-confuse/": "/confusopoly-why-companies-are-motivated-to-deliberately-confuse/",
    "/blog-posts/links-and-resources/": "/links-and-resources/",
    "/uncategorized/confusopoly-companies-motivated-deliberately-confuse/": "/blog-posts/confusopoly-companies-motivated-deliberately-confuse/",
    "/home/": "/",
    "/location/": "/contact-2/",
}

KNOWN_EXTERNAL_URL_REWRITES = {
    "http://marcfbellemare.com/wordpress/10053": "https://marcfbellemare.com/wordpress/10053",
    "http://marcfbellemare.com/wordpress/12060": "https://marcfbellemare.com/wordpress/12060",
    "http://marcfbellemare.com/wordpress/12797": "https://marcfbellemare.com/wordpress/12797",
    "http://www.privatehealth.gov.au": "https://www.privatehealth.gov.au",
    "href=\"privatehealth.gov.au\"": "href=\"https://www.privatehealth.gov.au\"",
    "https://www.brown.edu/Research/Shapiro/pdfs/foursteps.pdf": "https://www.brown.edu/research/shapiro/pdfs/foursteps.pdf",
    "https://www.brown.edu/Research/Shapiro/pdfs/applied_micro_slides.pdf": "https://www.brown.edu/research/shapiro/pdfs/applied_micro_slides.pdf",
}


@dataclass
class Item:
    title: str
    post_name: str
    post_type: str
    status: str
    link: str
    post_date: str
    modified_date: str
    content_html: str


def text(node: ET.Element | None, default: str = "") -> str:
    if node is None or node.text is None:
        return default
    return node.text.strip()


def slugify_fallback(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\-\s]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "untitled"


def parse_items(xml_path: Path) -> tuple[list[Item], str]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Could not find channel element in XML export")

    base_url = text(channel.find("wp:base_site_url", NS), "https://kenankalayci.com")

    parsed: list[Item] = []
    for item in channel.findall("item"):
        content_node = item.find("content:encoded", NS)
        parsed_item = Item(
            title=text(item.find("title")),
            post_name=text(item.find("wp:post_name", NS)),
            post_type=text(item.find("wp:post_type", NS)),
            status=text(item.find("wp:status", NS)),
            link=text(item.find("link")),
            post_date=text(item.find("wp:post_date", NS)),
            modified_date=text(item.find("wp:post_modified", NS)),
            content_html=(content_node.text or "") if content_node is not None else "",
        )

        if not parsed_item.post_name:
            parsed_item.post_name = slugify_fallback(parsed_item.title)

        parsed.append(parsed_item)

    return parsed, base_url


def write_markdown(path: Path, item: Item) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    date_val = item.post_date if item.post_date else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    lastmod_val = item.modified_date if item.modified_date else date_val
    front_matter = (
        "---\n"
        f'title: "{item.title.replace(chr(34), chr(39))}"\n'
        f"date: {date_val}\n"
        f"lastmod: {lastmod_val}\n"
        f"slug: {item.post_name}\n"
        f'wordpress_link: "{item.link}"\n'
        "---\n\n"
    )

    body = clean_html_for_static(item.content_html).strip()
    if body:
        body += "\n"

    path.write_text(front_matter + body, encoding="utf-8")


def collect_links(items: Iterable[Item]) -> tuple[set[str], set[str]]:
    local_uploads: set[str] = set()
    pdf_links: set[str] = set()
    for item in items:
        html = item.content_html or ""
        local_uploads.update(match.group(1) for match in LOCAL_UPLOAD_RE.finditer(html))
        pdf_links.update(match.group(0) for match in ANY_PDF_RE.finditer(html))
    return local_uploads, pdf_links


def clean_html_for_static(content_html: str) -> str:
    cleaned = content_html or ""
    cleaned = TWITTER_WIDGET_RE.sub(
        '<a href="https://twitter.com/Kalayci_Kenan" rel="noopener" target="_blank">Follow @Kalayci_Kenan on X</a>',
        cleaned,
    )
    cleaned = GOOGLE_MAPS_IFRAME_RE.sub(
        '<a href="https://www.google.com/maps/place/Colin+Clark+Building,+University+of+Queensland/" rel="noopener" target="_blank">Open Colin Clark Building on Google Maps</a>',
        cleaned,
    )
    for old, new in KNOWN_EXTERNAL_URL_REWRITES.items():
        cleaned = cleaned.replace(old, new)
    cleaned = normalize_internal_urls(cleaned)
    return cleaned


def normalize_internal_urls(content_html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw_path = match.group("path") or "/"
        if raw_path.startswith("/wp-content/uploads/"):
            return raw_path
        return LEGACY_INTERNAL_PATH_MAP.get(raw_path, raw_path)

    return ABSOLUTE_INTERNAL_RE.sub(repl, content_html)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import WordPress XML into Hugo content")
    parser.add_argument("--xml", required=True, type=Path, help="Path to WordPress XML export")
    parser.add_argument("--content-dir", required=True, type=Path, help="Hugo content directory")
    parser.add_argument("--data-dir", required=True, type=Path, help="Data output directory")
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path("reports"),
        help="Report output directory for CSV/TXT artifacts",
    )
    args = parser.parse_args()

    items, base_url = parse_items(args.xml)

    published_pages = [i for i in items if i.post_type == "page" and i.status == "publish"]
    published_posts = [i for i in items if i.post_type == "post" and i.status == "publish"]

    for page in published_pages:
        if page.post_name in {"home", ""}:
            md_path = args.content_dir / "_index.md"
        else:
            md_path = args.content_dir / page.post_name / "index.md"
        write_markdown(md_path, page)

    for post in published_posts:
        md_path = args.content_dir / "blog-posts" / f"{post.post_name}.md"
        write_markdown(md_path, post)

    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "base_url": base_url,
        "counts": {
            "total_items": len(items),
            "published_pages": len(published_pages),
            "published_posts": len(published_posts),
            "attachments": len([i for i in items if i.post_type == "attachment"]),
            "draft_items": len([i for i in items if i.status == "draft"]),
        },
        "published_pages": [asdict(i) for i in published_pages],
        "published_posts": [asdict(i) for i in published_posts],
    }

    (args.data_dir / "content-inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    local_uploads, pdf_links = collect_links(published_pages + published_posts)

    with (args.reports_dir / "url-inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["type", "url_or_path"])
        for path in sorted(local_uploads):
            writer.writerow(["local_upload_path", path])
        for url in sorted(pdf_links):
            writer.writerow(["pdf_link", url])

    with (args.reports_dir / "pdf-inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pdf_url", "is_local_domain"])
        for url in sorted(pdf_links):
            writer.writerow([url, str("kenankalayci.com/wp-content/uploads/" in url).lower()])

    report_lines = [
        "WordPress import summary",
        f"- Base URL: {base_url}",
        f"- Published pages imported: {len(published_pages)}",
        f"- Published posts imported: {len(published_posts)}",
        f"- Attachments in export: {inventory['counts']['attachments']}",
        f"- Draft items excluded: {inventory['counts']['draft_items']}",
        f"- Local upload paths referenced in content: {len(local_uploads)}",
        f"- PDF links referenced in content: {len(pdf_links)}",
    ]
    (args.reports_dir / "import-report.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("Import complete")
    for line in report_lines:
        print(line)


if __name__ == "__main__":
    main()
