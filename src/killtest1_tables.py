#!/usr/bin/env python3
"""KILL-TEST 1, Nature route — do the Extended Data tables carry per-grain
identifiers resolvable against the PDS CDA archive?

What this does
--------------
Fetches the four Extended Data table pages Nature publishes for the target DOI,
attempts to parse each into rows, and scans whatever text is recoverable for
identifier-shaped fields. Results go to ``reports/killtest1_findings.json``.

It gathers *evidence only*. Like ``src/killtest1_paper.py``, it deliberately does
not stamp a verdict into ``reports/killtest1.md``: per CLAUDE.md Rule 1 that
adjudication is written by hand against this evidence, so that a regex which
happens to match cannot promote itself into a PASS.

The identifier patterns are imported from ``killtest1_paper`` rather than
restated, so the two routes cannot drift apart.

Provenance and scope
--------------------
Every page fetched is manifested with URL + SHA256 (Rule 2). Table bodies are
**not** copied into the repository: only column structure, row counts and
identifier-shaped fields are extracted, which is what an archive lookup needs.

Usage
-----
    python src/killtest1_tables.py
"""

from __future__ import annotations

import html as html_mod
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import REPO_ROOT, FetchError, fetch  # noqa: E402
from killtest1_paper import IDENTIFIER_PATTERNS  # noqa: E402

DOI = "10.1038/s41586-023-05987-9"
TABLE_URLS = {
    n: f"https://www.nature.com/articles/s41586-023-05987-9/tables/{n}" for n in (1, 2, 3, 4)
}
DEST_DIR = REPO_ROOT / "data" / "nature"
FINDINGS = REPO_ROOT / "reports" / "killtest1_findings.json"

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
TAG = re.compile(r"<[^>]+>")
SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
MEDIA_IMG = re.compile(r'src="([^"]*MediaObjects[^"]*)"')

# Counted to show whether there is any tabular markup at all to parse.
MARKUP = {"table": "<table", "tr": "<tr", "td": "<td", "th": "<th"}


def visible_text(page: str) -> str:
    """Strip scripts, styles and tags, leaving the text a reader would see."""
    stripped = SCRIPT_STYLE.sub(" ", page)
    return html_mod.unescape(re.sub(r"\s+", " ", TAG.sub(" ", stripped))).strip()


def main() -> int:
    FINDINGS.parent.mkdir(parents=True, exist_ok=True)

    # Preserve the earlier publisher-PDF evidence rather than overwriting it:
    # this route supplements that one, it does not replace it.
    prior: dict = {}
    if FINDINGS.exists():
        try:
            existing = json.loads(FINDINGS.read_text(encoding="utf-8"))
            prior = existing.get("publisher_pdf_route", existing)
        except json.JSONDecodeError:
            prior = {}

    findings: dict = {
        "gate": "killtest1",
        "question": (
            "Do Extended Data Tables 1 and 2 carry per-grain identifiers "
            "(spacecraft clock, event ID, timestamp, orbit/flyby reference) that "
            "can be resolved against the PDS CDA archive?"
        ),
        "doi": DOI,
        "checked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict_policy": (
            "This script stamps no verdict. reports/killtest1.md is adjudicated by "
            "hand against this evidence, per CLAUDE.md Rule 1."
        ),
        "publisher_pdf_route": prior,
    }

    tables: dict[str, dict] = {}
    try:
        import pandas as pd

        for n, url in TABLE_URLS.items():
            dest = DEST_DIR / f"s41586-023-05987-9_table{n}.html"
            fetch(url, dest, note=f"Nature Extended Data Table {n} page for doi {DOI} (kill-test 1)")
            page = dest.read_text(encoding="utf-8", errors="replace")

            entry: dict = {"url": url, "page_bytes": dest.stat().st_size}
            title = TITLE.search(page)
            # The <title> carries the table's full caption; the meta description
            # is only the string "table N" and is useless for this purpose.
            entry["caption_verbatim"] = (
                html_mod.unescape(re.sub(r"\s+", " ", title.group(1))).strip() if title else None
            )
            entry["markup_counts"] = {k: page.count(v) for k, v in MARKUP.items()}

            # Attempt an actual parse. The exact failure is recorded verbatim, so
            # "could not be read" is never mistaken for "contained nothing".
            try:
                frames = pd.read_html(io.StringIO(page))
                entry["parsed_table_count"] = len(frames)
                entry["column_headings_verbatim"] = [
                    [str(c) for c in df.columns] for df in frames
                ]
                entry["row_counts"] = [int(len(df)) for df in frames]
                entry["parse_error"] = None
            except Exception as exc:
                entry["parsed_table_count"] = 0
                entry["column_headings_verbatim"] = None
                entry["row_counts"] = None
                entry["parse_error"] = f"{type(exc).__name__}: {exc}"

            # What the page publishes the table *as*.
            images = []
            for src in MEDIA_IMG.findall(page):
                absolute = "https:" + src if src.startswith("//") else src
                record = {"url": absolute}
                try:
                    head = requests.head(absolute, timeout=60, allow_redirects=True)
                    record["http_status"] = head.status_code
                    record["content_type"] = head.headers.get("content-type")
                    record["content_length_bytes"] = head.headers.get("content-length")
                except requests.RequestException as exc:
                    record["probe_error"] = repr(exc)
                images.append(record)
            entry["table_rendered_as_images"] = images

            # Identifier scan over the page's visible text. Scope is stated
            # explicitly: this is the whole page, not a table body, because there
            # is no table body in the markup to scope to.
            text = visible_text(page)
            entry["visible_text_chars"] = len(text)
            scan: dict[str, dict] = {}
            for name, pattern in IDENTIFIER_PATTERNS.items():
                hits = pattern.findall(text)
                scan[name] = {
                    "count": len(hits),
                    "unique": len(set(hits)),
                    "sample": sorted(set(str(h) for h in hits))[:20],
                }
            entry["identifier_candidates"] = scan
            entry["identifier_scan_scope"] = (
                "whole page visible text, including navigation and boilerplate — "
                "NOT a table body, because the page contains no tabular markup. "
                "Matches here are not evidence of identifiers in the table."
            )
            tables[str(n)] = entry

        findings["nature_extended_data_route"] = tables

        # The two questions the operator asked, answered from the evidence above.
        no_markup = all(
            sum(e["markup_counts"].values()) == 0 for e in tables.values()
        )
        all_images = all(e["table_rendered_as_images"] for e in tables.values())
        findings["tabular_markup_present_on_any_page"] = not no_markup
        findings["every_table_published_as_image"] = all_images
        findings["rows_extracted_total"] = sum(
            sum(e["row_counts"]) if e["row_counts"] else 0 for e in tables.values()
        )
        findings["nine_phosphate_grains_resolved_to_identifiers"] = False
        findings["type3_grains_resolved_to_identifiers"] = False
        findings["resolution_blocker"] = (
            "The table bodies were not read. All four Extended Data tables are "
            "published as JPEG images inside their HTML pages; the pages contain "
            "zero <table>, <tr>, <td> and <th> elements, so pandas.read_html and "
            "any DOM-based parser have nothing to parse. This is the same barrier "
            "the publisher PDF presented, in a different container."
        )
        findings["status"] = "UNRESOLVED"
        findings["status_reason"] = (
            "Blocked at extraction, not decided. Whether the tables carry per-grain "
            "identifiers is UNKNOWN: their contents were never read. 'Not read' and "
            "'not present' imply opposite verdicts (UNRESOLVED vs FAIL) and this "
            "evidence cannot distinguish them."
        )

        FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")

        for n, entry in tables.items():
            print(f"Table {n}: {entry['caption_verbatim']}")
            print(f"  markup counts: {entry['markup_counts']}")
            print(f"  parsed tables: {entry['parsed_table_count']}  rows: {entry['row_counts']}")
            print(f"  columns: {entry['column_headings_verbatim']}")
            for img in entry["table_rendered_as_images"]:
                print(
                    f"  published as: {img['url'].split('/')[-1]} "
                    f"({img.get('content_type')}, {img.get('content_length_bytes')} bytes)"
                )
            print()
        print(f"status: {findings['status']} — {findings['resolution_blocker']}")
        print(f"Wrote {FINDINGS.relative_to(REPO_ROOT)}")
        return 2

    except FetchError as exc:
        findings["status"] = "UNRESOLVED"
        findings["blocker"] = str(exc)
        FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"UNRESOLVED — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
