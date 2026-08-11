#!/usr/bin/env python3
"""KILL-TEST 1 — do the nine phosphate-bearing grains resolve to machine-readable
identifiers (spacecraft clock / event IDs) usable against the PDS archive?

Gate criterion
--------------
PASS  : Extended Data Tables 1 and 2 are located, and they carry per-grain
        identifiers that can be matched against the PDS CDA archive index
        (e.g. spacecraft clock counts, CDA event IDs, or dated event keys).
FAIL  : The tables are located and demonstrably do NOT carry such identifiers.
UNRESOLVED : The tables could not be retrieved or read to completion.

This script gathers *evidence only*. It prints what it found and writes
``reports/killtest1_findings.json``. It deliberately does not stamp a verdict
into ``reports/killtest1.md``: per CLAUDE.md Rule 1 the adjudication is written
by a human-reviewed session against this evidence, so that a regex that happens
to match cannot promote itself into a PASS.

Usage
-----
    python src/killtest1_paper.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import REPO_ROOT, FetchError, fetch  # noqa: E402

PAPER_URL = (
    "https://www.geo.fu-berlin.de/en/geol/fachrichtungen/planet/projects/"
    "habitat_oasis/_layout/Postberg_2023_Nature618_Phosphates_Enceladus.pdf"
)
PAPER_PDF = REPO_ROOT / "data" / "paper" / "Postberg_2023_Nature618_Phosphates_Enceladus.pdf"
FINDINGS = REPO_ROOT / "reports" / "killtest1_findings.json"

# Candidate identifier shapes, each reported separately so the adjudicating
# session can see *which* kind of key (if any) is present. None of these is
# assumed to be correct; they are nets, not conclusions.
IDENTIFIER_PATTERNS = {
    # Cassini spacecraft clock: 10-digit second count, optionally partitioned
    # ("1/1234567890") and optionally with a sub-RTI suffix (":123").
    "sclk_10digit": re.compile(r"\b(?:\d/)?1\d{9}(?::\d{1,3})?\b"),
    # Generic long integer that could serve as an event key.
    "long_integer_8_12": re.compile(r"\b\d{8,12}\b"),
    # ISO-like or DOY timestamps usable to index the archive by time.
    "iso_datetime": re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?\b"),
    "doy_datetime": re.compile(r"\b\d{4}-\d{3}T\d{2}:\d{2}(?::\d{2})?\b"),
    # Explicit event / spectrum labelling.
    "event_id_labelled": re.compile(r"\b(?:event|spectrum|grain)\s*(?:id|no\.?|#)\s*[:=]?\s*\d+\b", re.I),
    # CDA product-style names seen in PDS volumes.
    "cda_product_name": re.compile(r"\b(?:COCDA|CDA)[_\-][A-Z0-9_\-]{3,}\b", re.I),
}

TABLE_HEADINGS = [
    re.compile(r"Extended\s+Data\s+Table\s*1\b", re.I),
    re.compile(r"Extended\s+Data\s+Table\s*2\b", re.I),
]


def extract_pages(pdf_path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("pypdf is required: pip install -e .") from exc

    reader = PdfReader(str(pdf_path))
    return [(page.extract_text() or "") for page in reader.pages]


def main() -> int:
    FINDINGS.parent.mkdir(parents=True, exist_ok=True)
    findings: dict = {
        "gate": "killtest1",
        "question": (
            "Do the nine phosphate-bearing grains resolve to machine-readable "
            "identifiers usable against the PDS archive?"
        ),
        "paper_url": PAPER_URL,
    }

    try:
        fetch(PAPER_URL, PAPER_PDF, note="Postberg et al. 2023 Nature 618, 489-493 (kill-test 1 target)")
    except FetchError as exc:
        findings["status"] = "UNRESOLVED"
        findings["blocker"] = str(exc)
        FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"UNRESOLVED — could not retrieve the paper: {exc}", file=sys.stderr)
        return 2

    pages = extract_pages(PAPER_PDF)
    findings["n_pages"] = len(pages)
    full_text = "\n".join(pages)
    findings["extracted_chars"] = len(full_text)

    # Per-page extracted length. A table page that yields only its caption is
    # the signature of a table rendered as an image: the identifier scan below
    # then reports absence-of-text, NOT absence-of-identifiers. Those imply
    # opposite verdicts, so the adjudicator must be able to tell them apart.
    findings["page_char_counts"] = {str(i + 1): len(p) for i, p in enumerate(pages)}

    # Where do the Extended Data tables appear, if at all? The phrase matches a
    # real table heading AND a body-text cross-reference ("listed in Extended
    # Data Table 1") equally well, so record the character offset of each match
    # and separate the two. Heuristic, stated openly: a heading starts its page
    # (offset below HEADING_MAX_OFFSET, allowing for a running header such as
    # "Article"); anything later is a cross-reference. Raw offsets are kept so
    # the adjudicator can check the split rather than trust it.
    HEADING_MAX_OFFSET = 40
    table_hits: dict[str, dict] = {}
    for pattern in TABLE_HEADINGS:
        occurrences = [
            {"page": i + 1, "offset": m.start()}
            for i, page in enumerate(pages)
            for m in [pattern.search(page)]
            if m
        ]
        heading_pages = sorted(
            {o["page"] for o in occurrences if o["offset"] < HEADING_MAX_OFFSET}
        )
        xref_pages = sorted(
            {o["page"] for o in occurrences if o["offset"] >= HEADING_MAX_OFFSET}
        )
        table_hits[pattern.pattern] = {
            "occurrences": occurrences,
            "heading_pages": heading_pages,
            "cross_reference_pages": xref_pages,
        }
    findings["extended_data_table_pages"] = table_hits
    findings["heading_offset_threshold_chars"] = HEADING_MAX_OFFSET

    # Scan the pages that carry the tables themselves. Cross-reference pages are
    # body prose and would dilute the scan with unrelated matches.
    target_pages = sorted(
        {p for hit in table_hits.values() for p in hit["heading_pages"]}
    )
    findings["scanned_scope"] = (
        f"table heading pages {target_pages}"
        if target_pages
        else "whole document (table headings not located)"
    )
    scope_text = (
        "\n".join(pages[p - 1] for p in target_pages) if target_pages else full_text
    )
    findings["scanned_scope_chars"] = len(scope_text)

    id_hits: dict[str, dict] = {}
    for name, pattern in IDENTIFIER_PATTERNS.items():
        matches = pattern.findall(scope_text)
        uniq = sorted(set(matches))
        id_hits[name] = {"count": len(matches), "unique": len(uniq), "sample": uniq[:25]}
    findings["identifier_candidates"] = id_hits

    # A text layer can be absent in scanned PDFs; distinguish that from a real
    # absence of identifiers. Document-wide presence is NOT sufficient: the body
    # prose can carry a full text layer while the table pages carry none.
    findings["text_layer_present"] = len(full_text.strip()) > 500

    # Verbatim text of each table page. These pages are short when the table is
    # an image, so record them in full: the adjudicator can then read exactly
    # what was and was not recovered instead of inferring it from a count.
    findings["table_page_extracts"] = {
        str(p): pages[p - 1] for p in target_pages
    }

    FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(json.dumps(findings, indent=2))
    print(f"\nEvidence written to {FINDINGS}")
    print("Adjudicate this into reports/killtest1.md by hand (CLAUDE.md Rule 1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
