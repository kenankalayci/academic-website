#!/usr/bin/env python3
"""Validate internal/local-upload links and optionally external links from content files."""

from __future__ import annotations

import argparse
import csv
import json
import re
import socket
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

URL_RE = re.compile(r'https?://[^\s"\)\]<>]+', re.IGNORECASE)
REL_HREF_RE = re.compile(r'href=["\'](/[^"\']+)["\']', re.IGNORECASE)


def collect_content_urls(content_dir: Path) -> set[str]:
    urls: set[str] = set()
    for path in content_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        urls.update(URL_RE.findall(text))
        urls.update(REL_HREF_RE.findall(text))
    return urls


def known_paths(inventory: dict) -> set[str]:
    paths = {"/", "/blog-posts/"}
    for item in inventory.get("published_pages", []):
        slug = item.get("post_name", "")
        if slug == "home":
            paths.add("/")
        elif slug:
            paths.add(f"/{slug}/")
    for item in inventory.get("published_posts", []):
        slug = item.get("post_name", "")
        if slug:
            paths.add(f"/blog-posts/{slug}/")
    return paths


def collect_alias_paths(content_dir: Path) -> set[str]:
    aliases: set[str] = set()
    for path in content_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue

        try:
            fm = text.split("\n---\n", 1)[0]
        except Exception:  # noqa: BLE001
            continue

        lines = fm.splitlines()
        in_aliases = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("aliases:"):
                in_aliases = True
                continue

            if in_aliases:
                if stripped.startswith("-"):
                    alias = stripped.lstrip("-").strip().strip('"').strip("'")
                    if alias and alias.startswith("/"):
                        aliases.add(alias)
                elif stripped and not stripped.startswith("#"):
                    in_aliases = False

    return aliases


def check_external(url: str, timeout: float) -> tuple[bool, str]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return True, str(response.status)
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 405, 406}:
            # Some domains block HEAD; retry with GET.
            try:
                request = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    return True, str(response.status)
            except urllib.error.HTTPError as exc2:
                if exc2.code == 406:
                    return True, "406 bot-protected"
                return False, f"GET-fallback-failed: HTTP Error {exc2.code}"
            except Exception as exc2:  # noqa: BLE001
                return False, f"GET-fallback-failed: {exc2}"
        return False, f"HTTP {exc.code}"
    except (urllib.error.URLError, socket.timeout, ValueError) as exc:
        return False, str(exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate links in Hugo content")
    parser.add_argument("--content-dir", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--static-dir", required=True, type=Path)
    parser.add_argument("--site-domain", default="kenankalayci.com")
    parser.add_argument("--check-external", action="store_true")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    allowed = known_paths(inventory)
    allowed.update(collect_alias_paths(args.content_dir))
    urls = sorted(collect_content_urls(args.content_dir))

    rows: list[dict[str, str]] = []
    for url in urls:
        parsed = urlparse(url)
        status = "ok"
        detail = ""
        check_type = ""

        if url.startswith("/"):
            check_type = "internal_relative"
            path = parsed.path
            if path.startswith("/wp-content/uploads/"):
                target = args.static_dir / path.lstrip("/")
                if not target.exists():
                    status = "fail"
                    detail = "missing local upload file"
            elif path not in allowed:
                status = "warn"
                detail = "path not in known published routes"

        elif parsed.scheme in {"http", "https"}:
            if parsed.netloc.endswith(args.site_domain):
                check_type = "internal_absolute"
                path = parsed.path or "/"
                if path.startswith("/wp-content/uploads/"):
                    target = args.static_dir / path.lstrip("/")
                    if not target.exists():
                        status = "fail"
                        detail = "missing local upload file"
                elif path not in allowed:
                    status = "warn"
                    detail = "path not in known published routes"
            else:
                check_type = "external"
                if args.check_external:
                    ok, info = check_external(url, args.timeout)
                    if not ok:
                        status = "warn"
                    detail = info
                else:
                    detail = "skipped external check"
        else:
            check_type = "other"
            status = "warn"
            detail = "unsupported URL scheme"

        rows.append(
            {
                "url": url,
                "type": check_type,
                "status": status,
                "detail": detail,
            }
        )

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "type", "status", "detail"])
        writer.writeheader()
        writer.writerows(rows)

    total = len(rows)
    fails = len([r for r in rows if r["status"] == "fail"])
    warns = len([r for r in rows if r["status"] == "warn"])

    lines = [
        "# Link Validation Report",
        "",
        f"- Total URLs scanned: {total}",
        f"- Failures: {fails}",
        f"- Warnings: {warns}",
        f"- External checks enabled: {'yes' if args.check_external else 'no'}",
        "",
        "## Non-OK Items",
        "",
        "| Status | Type | URL | Detail |",
        "|---|---|---|---|",
    ]

    non_ok = [r for r in rows if r["status"] != "ok"]
    if non_ok:
        for row in non_ok:
            lines.append(f"| {row['status']} | {row['type']} | `{row['url']}` | {row['detail']} |")
    else:
        lines.append("| ok | n/a | n/a | No issues found |")

    args.out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Validation complete: total={total}, fail={fails}, warn={warns}")


if __name__ == "__main__":
    main()
