#!/usr/bin/env python3
"""
Batch read Google Docs 1-6 for VirtuaLab Digital identity absorption.
Uses curl to fetch the plain-text export of each publicly-shared Google Doc.
Much more reliable than canvas-based browser extraction.
"""

import subprocess
import sys
import time
import os

DOCS = [
    {
        "id": "1owWGkax4roPbYI2JYGs9XIm7yGMQl-vCzQ57a5_QlbE",
        "url": "https://docs.google.com/document/d/1owWGkax4roPbYI2JYGs9XIm7yGMQl-vCzQ57a5_QlbE/edit?tab=t.0#heading=h.wzni588l0f0b",
    },
    {
        "id": "1LQ4eZlXwlQ7z42FFl-r1ry_4xb_5yXVWQABhFhCET9A",
        "url": "https://docs.google.com/document/d/1LQ4eZlXwlQ7z42FFl-r1ry_4xb_5yXVWQABhFhCET9A/edit?tab=t.rmn8z5izwda6",
    },
    {
        "id": "1Yg1hhPqjKY14DgVEZVURwOgkaPVufANAqacZd1m7uK8",
        "url": "https://docs.google.com/document/d/1Yg1hhPqjKY14DgVEZVURwOgkaPVufANAqacZd1m7uK8/edit?tab=t.0",
    },
    {
        "id": "1tT1wzcH_4y5ycxZSyiKpLqBigVklhdox2MXotnQ8lY0",
        "url": "https://docs.google.com/document/d/1tT1wzcH_4y5ycxZSyiKpLqBigVklhdox2MXotnQ8lY0/edit?tab=t.0",
    },
    {
        "id": "1jptG_rVD1IB7v_G4JY_w9MpVHkUAU0QZB6lGhXRZ-FY",
        "url": "https://docs.google.com/document/d/1jptG_rVD1IB7v_G4JY_w9MpVHkUAU0QZB6lGhXRZ-FY/edit?tab=t.0",
    },
    {
        "id": "1LHgnnQVLHTbYyI4vubW8ZTZ0_6hhUi2A9QTAInJsI_E",
        "url": "https://docs.google.com/document/d/1LHgnnQVLHTbYyI4vubW8ZTZ0_6hhUi2A9QTAInJsI_E/edit?tab=t.0",
    },
]

OUTPUT_FILE = "/home/z/my-project/download/docs_batch_1.txt"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


def fetch_doc_text(doc_id):
    """Fetch the plain-text export of a Google Doc."""
    export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "-A", UA, "--max-time", "30", export_url],
            capture_output=True,
            text=True,
            timeout=45,
        )
        text = result.stdout
        # Strip BOM if present
        if text.startswith("\ufeff"):
            text = text[1:]
        return text.strip()
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT fetching {doc_id}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"  ERROR fetching {doc_id}: {e}", file=sys.stderr)
        return ""


def main():
    print(f"Starting batch txt export: {len(DOCS)} docs", file=sys.stderr)
    print(f"Output: {OUTPUT_FILE}", file=sys.stderr)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("")

    total_lines = 0
    for i, doc in enumerate(DOCS):
        doc_id = doc["id"]
        url = doc["url"]
        print(f"\n[{i+1}/{len(DOCS)}] Fetching {doc_id}...", file=sys.stderr)

        text = fetch_doc_text(doc_id)
        lines = text.split("\n")
        total_lines += len(lines)

        print(f"  Got {len(lines)} lines, {len(text)} chars", file=sys.stderr)

        # Show first line as title
        if lines:
            print(f"  Title: {lines[0][:100]}", file=sys.stderr)

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n===DOC ID: {doc_id}===\n")
            f.write(f"URL: {url}\n")
            f.write(f"Lines: {len(lines)} | Chars: {len(text)}\n")
            f.write(f"{'='*60}\n")
            f.write(text + "\n")
            f.write(f"\n{'='*60}\n")

    print(f"\nDone! Total: {total_lines} lines across {len(DOCS)} docs", file=sys.stderr)
    print(f"Saved to: {OUTPUT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
