#!/usr/bin/env python3
"""Download local wp-content/uploads assets referenced by imported content."""

from __future__ import annotations

import argparse
import csv
import urllib.request
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download referenced local uploads")
    parser.add_argument("--url-csv", required=True, type=Path, help="Path to data/url-inventory.csv")
    parser.add_argument("--out-dir", required=True, type=Path, help="Output static directory root")
    parser.add_argument("--base-url", default="https://kenankalayci.com", help="Base site URL")
    parser.add_argument("--timeout", type=int, default=20, help="Download timeout seconds")
    args = parser.parse_args()

    local_paths: list[str] = []
    with args.url_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("type") == "local_upload_path":
                local_paths.append(row["url_or_path"])

    if not local_paths:
        print("No local upload paths found in CSV")
        return

    downloaded = 0
    failed = 0
    for rel_path in sorted(set(local_paths)):
        rel_path = rel_path.lstrip("/")
        target = args.out_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        source_url = f"{args.base_url.rstrip('/')}/{rel_path}"
        try:
            with urllib.request.urlopen(source_url, timeout=args.timeout) as resp:
                data = resp.read()
            target.write_bytes(data)
            downloaded += 1
            print(f"OK   {rel_path}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {rel_path} :: {exc}")

    print(f"Done. Downloaded: {downloaded}, Failed: {failed}")


if __name__ == "__main__":
    main()
