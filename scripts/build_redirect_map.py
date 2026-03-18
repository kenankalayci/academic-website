#!/usr/bin/env python3
"""Build a redirect mapping table from WordPress links to Hugo paths."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlparse


def to_target(post_type: str, slug: str) -> str:
    if post_type == "post":
        return f"/blog-posts/{slug}/"
    if slug == "home":
        return "/"
    return f"/{slug}/"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate redirect-map.csv from content inventory")
    parser.add_argument("--inventory", required=True, type=Path, help="Path to data/content-inventory.json")
    parser.add_argument("--out", required=True, type=Path, help="Output CSV path")
    args = parser.parse_args()

    payload = json.loads(args.inventory.read_text(encoding="utf-8"))
    rows: list[tuple[str, str, str]] = []

    for item in payload.get("published_pages", []) + payload.get("published_posts", []):
        src = item.get("wordpress_link", "")
        post_type = item.get("post_type", "")
        slug = item.get("post_name", "")
        target = to_target(post_type, slug)

        if not src:
            continue

        parsed = urlparse(src)
        source_path = parsed.path or "/"

        # Keep only meaningful deltas where old path does not already match target.
        if source_path != target:
            rows.append((source_path, target, "301"))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["from", "to", "code"])
        for row in sorted(set(rows)):
            writer.writerow(row)

    print(f"Wrote {len(set(rows))} redirect rows to {args.out}")


if __name__ == "__main__":
    main()
