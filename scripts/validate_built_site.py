#!/usr/bin/env python3
"""Run lightweight, dependency-free quality checks against generated Hugo HTML."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.h1_count = 0
        self.canonical = ""
        self.description = ""
        self.og_image = ""
        self.is_redirect = False
        self.main_depth = 0
        self.main_text: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag == "main":
            self.main_depth += 1
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href") or ""
        if tag == "meta" and values.get("name") == "description":
            self.description = values.get("content") or ""
        if tag == "meta" and values.get("property") == "og:image":
            self.og_image = values.get("content") or ""
        if tag == "meta" and values.get("http-equiv", "").lower() == "refresh":
            self.is_redirect = True
        if tag == "img" and "alt" not in values:
            self.errors.append("image is missing an alt attribute")
        if tag == "a":
            href = values.get("href") or ""
            if href.startswith("http://kenankalayci.com"):
                self.errors.append(f"insecure internal link: {href}")
            if values.get("target") == "_blank":
                rel = set((values.get("rel") or "").split())
                if "noopener" not in rel:
                    self.errors.append(f'target="_blank" link lacks rel="noopener": {href}')

    def handle_endtag(self, tag: str) -> None:
        if tag == "main" and self.main_depth:
            self.main_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.main_depth:
            self.main_text.append(data)


def page_url_path(path: Path, public_dir: Path) -> str:
    relative = path.relative_to(public_dir)
    if relative.name == "index.html":
        parent = relative.parent.as_posix()
        return "/" if parent == "." else f"/{parent}/"
    return f"/{relative.as_posix()}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-dir", type=Path, default=Path("public"))
    args = parser.parse_args()
    public_dir = args.public_dir.resolve()

    failures: list[str] = []
    canonicals: dict[str, str] = {}
    forbidden_hosts = (
        "fonts.googleapis.com",
        "fonts.gstatic.com",
        "google.com/maps/embed",
        "counter.theconversation.edu.au",
    )

    html_files = sorted(public_dir.rglob("*.html"))
    if not html_files:
        failures.append("no generated HTML files found")

    for path in html_files:
        source = path.read_text(encoding="utf-8")
        page = PageParser()
        page.feed(source)
        label = page_url_path(path, public_dir)

        for host in forbidden_hosts:
            if host in source:
                failures.append(f"{label}: forbidden third-party request remains: {host}")

        if page.is_redirect:
            continue

        if page.h1_count != 1:
            failures.append(f"{label}: expected exactly one h1, found {page.h1_count}")
        if not page.description.strip():
            failures.append(f"{label}: missing meta description")
        if not page.og_image.strip():
            failures.append(f"{label}: missing og:image")
        if page.canonical:
            previous = canonicals.get(page.canonical)
            if previous:
                failures.append(f"{label}: duplicate canonical also used by {previous}")
            canonicals[page.canonical] = label
        else:
            failures.append(f"{label}: missing canonical URL")

        visible_main = re.sub(r"\s+", " ", " ".join(page.main_text)).strip()
        if len(visible_main) < 40:
            failures.append(f"{label}: main content appears empty")
        failures.extend(f"{label}: {error}" for error in page.errors)

        for href in re.findall(r'href=["\']([^"\']+)', source, flags=re.IGNORECASE):
            parsed = urlparse(href)
            if parsed.scheme or parsed.netloc or href.startswith(("#", "mailto:", "tel:")):
                continue
            clean = parsed.path
            if not clean.startswith("/"):
                continue
            candidate = public_dir / clean.lstrip("/")
            exists = (
                candidate.is_file()
                or (candidate / "index.html").is_file()
                or (candidate.with_suffix(".html")).is_file()
            )
            if not exists:
                failures.append(f"{label}: unresolved generated link: {href}")

    if failures:
        print("Built-site validation failed:")
        for failure in sorted(set(failures)):
            print(f"- {failure}")
        return 1

    print(f"Built-site validation passed: {len(html_files)} HTML files checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
