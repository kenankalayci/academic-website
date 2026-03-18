#!/usr/bin/env python3
"""Build redirect artifacts from WordPress XML and imported content inventory."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
}


def get_text(node: ET.Element | None) -> str:
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def target_path(post_type: str, slug: str) -> str:
    if slug == "home":
        return "/"
    if post_type == "post":
        return f"/blog-posts/{slug}/"
    return f"/{slug}/"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate redirect artifacts")
    parser.add_argument("--xml", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    targets: dict[str, tuple[str, str, str]] = {}
    for item in inventory.get("published_pages", []) + inventory.get("published_posts", []):
        slug = item.get("post_name", "")
        ptype = item.get("post_type", "")
        link = item.get("link") or item.get("wordpress_link") or ""
        title = item.get("title", slug)
        if slug and ptype:
            targets[slug] = (target_path(ptype, slug), title, link)

    tree = ET.parse(args.xml)
    root = tree.getroot()
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Invalid XML export: missing channel")

    redirects: set[tuple[str, str, str, str]] = set()

    for item in channel.findall("item"):
        status = get_text(item.find("wp:status", NS))
        post_type = get_text(item.find("wp:post_type", NS))
        slug = get_text(item.find("wp:post_name", NS))
        guid = get_text(item.find("guid"))

        if status != "publish" or post_type not in {"page", "post"}:
            continue

        target, title, canonical_link = targets.get(slug, (target_path(post_type, slug), slug, ""))

        if guid:
            guid_path = urlparse(guid).path or ""
            guid_query = urlparse(guid).query
            if guid_path and guid_path != target:
                source = guid_path
                if guid_query:
                    source = f"{source}?{guid_query}"
                redirects.add((source, target, title, "guid"))

        if canonical_link:
            path = urlparse(canonical_link).path or ""
            if path and path != target:
                redirects.add((path, target, title, "canonical_link"))

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["from", "to", "title", "source"])
        for row in sorted(redirects):
            writer.writerow(row)

    lines = [
        "# Legacy Redirect Candidates",
        "",
        "Generated from WordPress GUID and canonical links.",
        "",
        "| From | To | Title | Source |",
        "|---|---|---|---|",
    ]
    for frm, to, title, source in sorted(redirects):
        lines.append(f"| `{frm}` | `{to}` | {title} | {source} |")

    if not redirects:
        lines.append("| (none) | (none) | (none) | (none) |")

    args.out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {len(redirects)} redirect candidates")


if __name__ == "__main__":
    main()
