#!/usr/bin/env python3
"""Extract structured research data from imported publications/working papers pages."""

from __future__ import annotations

import argparse
import json
import re
from html import unescape
from pathlib import Path


TAG_RE = re.compile(r"<[^>]+>")
HREF_RE = re.compile(r'href="([^"]+)"', re.IGNORECASE)
ANCHOR_TEXT_RE = re.compile(r"<a[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)


def split_front_matter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        return "", content
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return "", content
    return parts[0] + "\n---\n", parts[1]


def strip_tags(value: str) -> str:
    text = TAG_RE.sub("", value)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_pdf_url(value: str) -> str:
    for link in HREF_RE.findall(value):
        if link.lower().endswith(".pdf"):
            return link
    return ""


def find_title_from_publication(value: str) -> str:
    plain = strip_tags(value)
    year_match = re.search(r"\b(19|20)\d{2}\b", plain)
    if year_match:
        prefix = plain[: year_match.start()].strip(" .,")
        if prefix:
            return prefix

    prefix = re.split(r"\(with\s+", plain, maxsplit=1, flags=re.IGNORECASE)[0].strip(" .,")
    if prefix:
        return prefix

    anchor_match = ANCHOR_TEXT_RE.search(value)
    if anchor_match:
        return strip_tags(anchor_match.group(1)).strip(" .")

    return plain.strip(" .")


def find_title_from_working(value: str) -> str:
    plain = strip_tags(value)
    prefix = re.split(r"\(with\s+", plain, maxsplit=1, flags=re.IGNORECASE)[0].strip(" .,")
    if prefix:
        return prefix

    anchor_match = ANCHOR_TEXT_RE.search(value)
    if anchor_match:
        return strip_tags(anchor_match.group(1)).strip(" .")

    return plain.strip(" .")


def find_year(value: str) -> int | None:
    match = re.search(r"\b(19|20)\d{2}\b", strip_tags(value))
    if not match:
        return None
    return int(match.group(0))


def find_coauthors(value: str) -> str:
    plain = strip_tags(value)
    match = re.search(r"\(with\s+(.+?)\)\s*", plain, flags=re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip()


def extract_publications(body: str) -> list[dict]:
    chunks = [c.strip() for c in re.split(r"\n\s*\n", body) if c.strip()]
    entries: list[dict] = []
    for chunk in chunks:
        entries.append(
            {
                "title": find_title_from_publication(chunk),
                "year": find_year(chunk),
                "coauthors": find_coauthors(chunk),
                "pdf_url": find_pdf_url(chunk),
                "citation_html": chunk,
            }
        )

    entries.sort(key=lambda x: (x["year"] is None, -(x["year"] or 0), x["title"]))
    return entries


def extract_working_papers(body: str) -> tuple[list[dict], list[dict]]:
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", body, flags=re.IGNORECASE | re.DOTALL)
    papers: list[dict] = []
    works_in_progress: list[dict] = []
    in_progress_section = False

    for para in paragraphs:
        raw = para.strip()
        plain = strip_tags(raw)
        if not plain:
            continue

        if plain.upper() == "WORKS IN PROGRESS":
            in_progress_section = True
            continue

        entry = {
            "title": find_title_from_working(raw),
            "coauthors": find_coauthors(raw),
            "pdf_url": find_pdf_url(raw),
            "citation_html": f"<p>{raw}</p>",
        }

        if in_progress_section:
            works_in_progress.append(entry)
        else:
            papers.append(entry)

    return papers, works_in_progress


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract publications and working paper data")
    parser.add_argument("--publications", required=True, type=Path)
    parser.add_argument("--workingpapers", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    pub_text = args.publications.read_text(encoding="utf-8")
    wp_text = args.workingpapers.read_text(encoding="utf-8")

    _, pub_body = split_front_matter(pub_text)
    _, wp_body = split_front_matter(wp_text)

    publications = {"entries": extract_publications(pub_body)}
    papers, wip = extract_working_papers(wp_body)
    working = {"papers": papers, "works_in_progress": wip}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "publications.json").write_text(
        json.dumps(publications, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (args.out_dir / "working_papers.json").write_text(
        json.dumps(working, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("Structured data extracted")
    print(f"- publications entries: {len(publications['entries'])}")
    print(f"- working papers entries: {len(working['papers'])}")
    print(f"- works in progress entries: {len(working['works_in_progress'])}")


if __name__ == "__main__":
    main()
