#!/usr/bin/env python3
"""Normalize internal kenankalayci.com links inside generated content bodies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urlparse

LEGACY_INTERNAL_PATH_MAP = {
    "/blog-posts/confusopoly-why-companies-are-motivated-to-deliberately-confuse/": "/confusopoly-why-companies-are-motivated-to-deliberately-confuse/",
    "/blog-posts/links-and-resources/": "/links-and-resources/",
    "/uncategorized/confusopoly-companies-motivated-deliberately-confuse/": "/blog-posts/confusopoly-companies-motivated-deliberately-confuse/",
    "/home/": "/",
    "/location/": "/contact-2/",
}

ABSOLUTE_INTERNAL_RE = re.compile(r"https?://kenankalayci\.com(?P<path>/[^\"'\s<]*)", re.IGNORECASE)

KNOWN_EXTERNAL_URL_REWRITES = {
    "http://marcfbellemare.com/wordpress/10053": "https://marcfbellemare.com/wordpress/10053",
    "http://marcfbellemare.com/wordpress/12060": "https://marcfbellemare.com/wordpress/12060",
    "http://marcfbellemare.com/wordpress/12797": "https://marcfbellemare.com/wordpress/12797",
    "http://www.privatehealth.gov.au": "https://www.privatehealth.gov.au",
    "href=\"privatehealth.gov.au\"": "href=\"https://www.privatehealth.gov.au\"",
    "https://www.brown.edu/Research/Shapiro/pdfs/foursteps.pdf": "https://www.brown.edu/research/shapiro/pdfs/foursteps.pdf",
    "https://www.brown.edu/Research/Shapiro/pdfs/applied_micro_slides.pdf": "https://www.brown.edu/research/shapiro/pdfs/applied_micro_slides.pdf",
}


def normalize_body(body: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw_path = match.group("path") or "/"
        parsed = urlparse(raw_path)
        path = parsed.path or "/"
        query = f"?{parsed.query}" if parsed.query else ""

        if path.startswith("/wp-content/uploads/"):
            return f"{path}{query}"

        canonical = LEGACY_INTERNAL_PATH_MAP.get(path, path)
        return f"{canonical}{query}"

    normalized = ABSOLUTE_INTERNAL_RE.sub(repl, body)
    for old, new in KNOWN_EXTERNAL_URL_REWRITES.items():
        normalized = normalized.replace(old, new)
    return normalized


def split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return "", text
    return parts[0] + "\n---\n", parts[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize internal absolute links in content files")
    parser.add_argument("--content-dir", required=True, type=Path)
    args = parser.parse_args()

    updated = 0
    for path in sorted(args.content_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        front_matter, body = split_front_matter(text)
        new_body = normalize_body(body)
        if new_body != body:
            path.write_text(front_matter + new_body, encoding="utf-8")
            updated += 1
            print(f"UPDATED {path.relative_to(args.content_dir.parent)}")

    print(f"Done. Updated files: {updated}")


if __name__ == "__main__":
    main()
