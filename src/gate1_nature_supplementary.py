#!/usr/bin/env python3
"""GATE 1 ROUTE — are Extended Data Tables 1 and 2 published by Nature in a
machine-readable form (xlsx/csv)?

Scope: availability only
------------------------
This script answers *what files exist*, not what is in them. It enumerates the
supplementary and Extended Data files Nature links from the article landing page
and records each one's URL, link text and file extension. It deliberately does
**not** download those files and does **not** parse or interpret their contents:
the availability answer is wanted first, and interpreting a table is a separate
step with a separate gate.

Why this route matters
----------------------
Kill-test 1 is UNRESOLVED because the Extended Data table *bodies* did not
extract from the publisher PDF — they are image- or vector-rendered, so only
headings and captions were recovered (Session 003). A machine-readable xlsx/csv
of the same tables would let that gate be decided on read contents rather than
on an unreadable render. Nature is the publisher of record, so this moves toward
the primary source rather than substituting a secondary one for it.

Exit codes
----------
0 : the landing page was read and its supplementary links enumerated. This is
    an availability finding, not a gate verdict — kill-test 1 stays UNRESOLVED
    until a session actually reads the table contents.
2 : UNRESOLVED — the landing page could not be retrieved.

Usage
-----
    python src/gate1_nature_supplementary.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import REPO_ROOT, FetchError, fetch  # noqa: E402

DOI = "10.1038/s41586-023-05987-9"
DOI_URL = f"https://doi.org/{DOI}"
ARTICLE_URL = "https://www.nature.com/articles/s41586-023-05987-9"
LANDING_HTML = REPO_ROOT / "data" / "nature" / "s41586-023-05987-9_landing.html"
REPORT = REPO_ROOT / "reports" / "gate1_supplementary_availability.json"

HREF = re.compile(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
TAG = re.compile(r"<[^>]+>")

# Extensions that would answer the question in the affirmative, and those that
# would not. Classification is by extension only; no file is opened.
MACHINE_READABLE = (".xlsx", ".xls", ".csv", ".tsv", ".txt", ".json", ".xml")
NOT_MACHINE_READABLE = (".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png", ".tif", ".tiff")

# Link families Nature uses for supplementary and Extended Data assets.
SUPPLEMENTARY_HINT = re.compile(
    r"(supplementar|extended[\s_-]*data|MediaObjects|static-content\.springer\.com|/ESM|source[\s_-]*data)",
    re.I,
)
ED_TABLE_1_2 = re.compile(r"extended[\s_-]*data[\s_-]*table[\s_-]*([12])\b", re.I)


def classify(url: str) -> str:
    """Label a link by file extension. Extension only — nothing is opened."""
    lowered = url.lower().split("?", 1)[0]
    for ext in MACHINE_READABLE:
        if lowered.endswith(ext):
            return f"machine_readable ({ext})"
    for ext in NOT_MACHINE_READABLE:
        if lowered.endswith(ext):
            return f"not_machine_readable ({ext})"
    return "no_file_extension_in_url"


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "check": "gate1_nature_supplementary_availability",
        "question": (
            "Do Nature's supplementary files for this DOI include Extended Data "
            "Tables 1 and 2 in a machine-readable form (xlsx/csv)?"
        ),
        "scope": (
            "Availability only. This check enumerates linked files and classifies "
            "them by extension. It does not download, parse, or interpret any "
            "file's contents, and it stamps no kill-test verdict."
        ),
        "doi": DOI,
        "doi_url": DOI_URL,
        "article_url": ARTICLE_URL,
        "checked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    try:
        # The landing page is manifested: per Rule 2 a file that is not in the
        # manifest is not evidence, and the availability claims rest on it.
        fetch(
            ARTICLE_URL,
            LANDING_HTML,
            note=f"Nature article landing page for doi {DOI} (gate 1 supplementary availability)",
        )
        html = LANDING_HTML.read_text(encoding="utf-8", errors="replace")
        result["landing_html_path"] = LANDING_HTML.relative_to(REPO_ROOT).as_posix()
        result["landing_html_chars"] = len(html)

        links = []
        for href, inner in HREF.findall(html):
            text = TAG.sub(" ", inner)
            text = re.sub(r"\s+", " ", text).strip()
            absolute = urljoin(ARTICLE_URL, href)
            if SUPPLEMENTARY_HINT.search(absolute) or SUPPLEMENTARY_HINT.search(text):
                links.append(
                    {"url": absolute, "link_text": text[:200], "classification": classify(absolute)}
                )

        # De-duplicate on URL, preserving first-seen order.
        seen: set[str] = set()
        unique = []
        for link in links:
            if link["url"] not in seen:
                seen.add(link["url"])
                unique.append(link)

        result["supplementary_link_count"] = len(unique)
        result["supplementary_links"] = unique
        result["machine_readable_links"] = [
            link for link in unique if link["classification"].startswith("machine_readable")
        ]

        # Specifically: anything naming Extended Data Table 1 or 2.
        ed_links = [
            link for link in unique
            if ED_TABLE_1_2.search(link["link_text"]) or ED_TABLE_1_2.search(link["url"])
        ]
        result["extended_data_table_1_2_links"] = ed_links
        result["extended_data_table_1_2_machine_readable"] = [
            link for link in ed_links if link["classification"].startswith("machine_readable")
        ]

        # Mentions in page text, recorded so a null link result can be told apart
        # from the tables not being mentioned at all.
        result["extended_data_table_1_2_text_mentions"] = sorted(
            set(m.group(0) for m in ED_TABLE_1_2.finditer(TAG.sub(" ", html)))
        )

        REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(
            f"Enumerated {len(unique)} supplementary/Extended Data link(s); "
            f"{len(result['machine_readable_links'])} classified machine-readable; "
            f"{len(ed_links)} naming Extended Data Table 1 or 2. "
            f"Wrote {REPORT.relative_to(REPO_ROOT)}. Contents were not opened."
        )
        return 0

    except (FetchError, requests.RequestException) as exc:
        result["status"] = "UNRESOLVED"
        result["blocker"] = f"{type(exc).__name__}: {exc}"
        REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"UNRESOLVED — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
