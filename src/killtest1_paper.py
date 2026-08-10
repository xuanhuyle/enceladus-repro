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

    # Where do the Extended Data tables appear, if at all?
    table_hits: dict[str, list[int]] = {}
    for pattern in TABLE_HEADINGS:
        hits = [i + 1 for i, page in enumerate(pages) if pattern.search(page)]
        table_hits[pattern.pattern] = hits
    findings["extended_data_table_pages"] = table_hits

    # If the tables are present, scan those pages specifically; otherwise scan
    # the whole document so the report can say what *is* there.
    target_pages = sorted({p for hits in table_hits.values() for p in hits})
    findings["scanned_scope"] = (
        f"pages {target_pages}" if target_pages else "whole document (tables not located)"
    )
    scope_text = (
        "\n".join(pages[p - 1] for p in target_pages) if target_pages else full_text
    )

    id_hits: dict[str, dict] = {}
    for name, pattern in IDENTIFIER_PATTERNS.items():
        matches = pattern.findall(scope_text)
        uniq = sorted(set(matches))
        id_hits[name] = {"count": len(matches), "unique": len(uniq), "sample": uniq[:25]}
    findings["identifier_candidates"] = id_hits

    # A text layer can be absent in scanned PDFs; distinguish that from a real
    # absence of identifiers.
    findings["text_layer_present"] = len(full_text.strip()) > 500

    FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(json.dumps(findings, indent=2))
    print(f"\nEvidence written to {FINDINGS}")
    print("Adjudicate this into reports/killtest1.md by hand (CLAUDE.md Rule 1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
