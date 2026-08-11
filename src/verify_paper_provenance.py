#!/usr/bin/env python3
"""Re-fetch the target paper PDF and compare its SHA256 against the manifest row.

What this checks, and what it does NOT
--------------------------------------
This is a **provenance** check, not an authentication check.

It answers exactly one question: *do the bytes served today at the manifested
URL hash to the same SHA256 that ``data/MANIFEST.md`` already records?*

It does **not** verify that the PDF is a genuine, correct, or complete copy of
Postberg et al. 2023, and it must not be described as verifying the paper. The
host serving the file is not the publisher of record. A MATCH means the byte
stream is stable across sessions and hosts; it says nothing about the content's
authority.

Exit codes
----------
0 : MATCH     — recomputed digest equals the manifest's recorded digest.
1 : MISMATCH  — the fetch completed and the digests differ.
2 : UNRESOLVED — the fetch or the manifest read could not be completed.

Per CLAUDE.md Rule 1, a blocked run is UNRESOLVED, never FAIL.

Note on manifest side effects
-----------------------------
The expected digest is read from ``data/MANIFEST.md`` **before** the fetch, so a
row appended by the fetch itself cannot be mistaken for the expectation. The
committed ``fetch`` helper appends a row only when the bytes differ from every
row already recorded; on a MATCH the manifest is left byte-for-byte unchanged.

Usage
-----
    python src/verify_paper_provenance.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import (  # noqa: E402
    MANIFEST,
    REPO_ROOT,
    FetchError,
    fetch,
    sha256_file,
)

# Same URL constant as src/killtest1_paper.py. Kept literal rather than imported
# so this check does not depend on the kill-test module's import side effects.
PAPER_URL = (
    "https://www.geo.fu-berlin.de/en/geol/fachrichtungen/planet/projects/"
    "habitat_oasis/_layout/Postberg_2023_Nature618_Phosphates_Enceladus.pdf"
)
PAPER_REL = "data/paper/Postberg_2023_Nature618_Phosphates_Enceladus.pdf"
PAPER_PDF = REPO_ROOT / PAPER_REL
REPORT = REPO_ROOT / "reports" / "paper_provenance_check.json"

# Manifest row shape, per data/MANIFEST.md:
#   | `<rel path>` | <n> bytes | `<sha256>` | <UTC ts> | <url> | <note> |
_ROW = re.compile(
    r"^\|\s*`(?P<rel>[^`]+)`\s*\|\s*(?P<size>\d+)\s*bytes\s*\|\s*`(?P<sha>[0-9a-f]{64})`"
    r"\s*\|\s*(?P<retrieved>[^|]+?)\s*\|\s*(?P<url>[^|]+?)\s*\|",
    re.M,
)


def manifest_rows_for(rel_path: str) -> list[dict[str, str]]:
    """Return every manifest row whose repo-relative path equals ``rel_path``.

    Fails loudly rather than defaulting: a missing manifest or an unparseable
    table is a blocker, not something to work around.
    """
    if not MANIFEST.exists():
        raise FetchError(f"{MANIFEST} does not exist; nothing to compare against.")
    text = MANIFEST.read_text(encoding="utf-8")
    rows = [m.groupdict() for m in _ROW.finditer(text)]
    if not rows:
        raise FetchError(
            f"no parseable provenance rows found in {MANIFEST}. The row format "
            "this check expects is documented in its regex; inspect the file by "
            "hand rather than letting this script guess."
        )
    return [r for r in rows if r["rel"] == rel_path]


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result: dict = {
        "check": "paper_provenance",
        "what_this_checks": (
            "Whether bytes served today at the manifested URL hash to the SHA256 "
            "already recorded in data/MANIFEST.md. This is provenance, not "
            "authentication: it does not verify that the PDF is a genuine or "
            "correct copy of the published paper."
        ),
        "url": PAPER_URL,
        "manifest_path": MANIFEST.relative_to(REPO_ROOT).as_posix(),
        "target_path": PAPER_REL,
        "checked_at_utc": checked_at,
    }

    try:
        # Read the expectation BEFORE fetching, so the fetch cannot supply it.
        prior = manifest_rows_for(PAPER_REL)
        if len(prior) != 1:
            raise FetchError(
                f"expected exactly one manifest row for {PAPER_REL}, found "
                f"{len(prior)}. Refusing to choose one; resolve the manifest by hand."
            )
        expected = prior[0]
        result["expected_sha256"] = expected["sha"]
        result["expected_size_bytes"] = int(expected["size"])
        result["expected_row_retrieved_utc"] = expected["retrieved"]
        result["expected_row_url"] = expected["url"]

        if expected["url"] != PAPER_URL:
            raise FetchError(
                "the manifest row's source URL differs from this check's URL "
                f"constant.\n  manifest: {expected['url']}\n  this check: {PAPER_URL}\n"
                "Refusing to compare digests across two different sources."
            )

        # Re-fetch. Appends a manifest row only if the bytes are new.
        fetch(PAPER_URL, PAPER_PDF, note="Postberg et al. 2023 re-fetch for provenance check")

        observed_sha = sha256_file(PAPER_PDF)
        observed_size = PAPER_PDF.stat().st_size
        result["observed_sha256"] = observed_sha
        result["observed_size_bytes"] = observed_size

        size_match = observed_size == int(expected["size"])
        sha_match = observed_sha == expected["sha"]
        result["size_match"] = size_match
        result["sha256_match"] = sha_match

        if sha_match and size_match:
            result["status"] = "MATCH"
            print(
                f"MATCH — re-fetched {observed_size} bytes; SHA256 {observed_sha} "
                f"equals the manifest row recorded {expected['retrieved']}."
            )
            REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
            return 0

        result["status"] = "MISMATCH"
        print(
            "MISMATCH — the bytes served now differ from the manifest row.\n"
            f"  expected sha256 {expected['sha']} ({expected['size']} bytes)\n"
            f"  observed sha256 {observed_sha} ({observed_size} bytes)",
            file=sys.stderr,
        )
        REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 1

    except FetchError as exc:
        result["status"] = "UNRESOLVED"
        result["blocker"] = str(exc)
        REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"UNRESOLVED — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
