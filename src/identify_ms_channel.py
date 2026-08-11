#!/usr/bin/env python3
"""Which CDA per-event signal family is the time-of-flight mass spectrum?

Why this exists
---------------
Kill-test 2 asks for "one raw MS (time-of-flight) signal". COCDA volumes carry
five per-event signal families — MPSIGNALS, QPSIGNALS, QCSIGNALS, QISIGNALS,
QTSIGNALS — and picking the wrong one would silently plot a charge channel and
call it a mass spectrum. Session 005 recorded, as a HYPOTHESIS with no
confidence level, that the multiplier channel (MP) carries the spectrum. A
hypothesis earns status only by becoming a SOURCED CLAIM, so this script settles
it against the archive's own Software Interface Specification rather than
against the plausibility of the family names.

What it does
------------
Fetches ``CDA_SIS_1_0.TXT`` from the archive (manifested, per Rule 2) and
extracts, verbatim, the ``PRODUCT_NAME`` and ``TABLE`` ``DESCRIPTION`` that the
SIS gives for each of the five families, plus the column definitions of the MP
table and the SIS's own description of the TOF mass spectrometer.

It quotes. It does not paraphrase, and it does not decide: the quotations are
written to ``reports/ms_channel_identification.json`` so the adjudication rests
on the source's words.

Usage
-----
    python src/identify_ms_channel.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import REPO_ROOT, FetchError, fetch  # noqa: E402

SIS_BASE = "https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/DOCUMENT/"
SIS_TXT = SIS_BASE + "CDA_SIS_1_0.TXT"
SIS_LBL = SIS_BASE + "CDA_SIS_1_0.LBL"
DEST_DIR = REPO_ROOT / "data" / "cda" / "DOCUMENT"
REPORT = REPO_ROOT / "reports" / "ms_channel_identification.json"

FAMILIES = ("MP", "QI", "QT", "QC", "QP")


def squash(text: str) -> str:
    """Collapse the SIS's fixed-width padding into readable prose."""
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "check": "ms_channel_identification",
        "question": (
            "Which CDA per-event signal family carries the multiplier "
            "time-of-flight mass spectrum?"
        ),
        "source_url": SIS_TXT,
        "source_title": "Cassini CDA Software Interface Specification (CDA_SIS_1_0)",
        "method": (
            "Verbatim quotation from the archive's own SIS. This script decides "
            "nothing; it extracts what the source says."
        ),
    }

    try:
        fetch(SIS_LBL, DEST_DIR / "CDA_SIS_1_0.LBL",
              note="CDA Software Interface Specification label (MS channel identification)")
        sis = fetch(SIS_TXT, DEST_DIR / "CDA_SIS_1_0.TXT",
                    note="CDA Software Interface Specification (MS channel identification)")
        text = sis.read_text(encoding="utf-8", errors="replace")

        # The TOF instrument description, which names the channel by signal.
        # The heading appears twice: once in the table of contents, once as the
        # real section. The TOC hit comes first and captures a page number, so
        # take the longest capture rather than the first.
        candidates = [
            m.group(1)
            for m in re.finditer(
                r"2\.1\.3\.\s*TOF mass spectrometer(.*?)\n\s*2\.2\.", text, re.S
            )
        ]
        tof = max(candidates, key=len) if candidates else None
        if not tof or len(squash(tof)) < 100:
            raise FetchError(
                "could not locate section 2.1.3 (TOF mass spectrometer) in the SIS; "
                "refusing to characterise the instrument without the source text."
            )
        result["tof_spectrometer_section_verbatim"] = squash(tof)

        # Per family: the PRODUCT_ID block and its TABLE-level DESCRIPTION.
        families: dict[str, dict] = {}
        for fam in FAMILIES:
            anchor = re.search(rf'PRODUCT_ID\s*=\s*"{fam}_X+"', text)
            if not anchor:
                raise FetchError(
                    f"no PRODUCT_ID block for family {fam} in the SIS; refusing to "
                    "report on a family the source does not define."
                )
            # Wide enough to reach the second COLUMN block: at 2600 characters the
            # window stopped short of MP's AMPLITUDE column, which is the one
            # carrying the multiplier signal.
            window = text[anchor.start(): anchor.start() + 4500]
            name = re.search(r'PRODUCT_NAME\s*=\s*"([^"]+)"', window)
            desc = re.search(
                r"OBJECT\s*=\s*TABLE.*?DESCRIPTION\s*=\s*\n?\s*\"(.*?)\"", window, re.S
            )
            entry = {
                "product_id_pattern": f"{fam}_XXXXXXXX",
                "product_name_verbatim": squash(name.group(1)) if name else None,
                "table_description_verbatim": squash(desc.group(1)) if desc else None,
            }
            # Column names + units, which is where a time axis gives itself away.
            cols = []
            for col in re.finditer(
                r'NAME\s*=\s*"([A-Z_0-9]+)"\s*\n\s*UNIT\s*=\s*"([^"]+)"\s*\n\s*'
                r'DESCRIPTION\s*=\s*\n?\s*"(.*?)"',
                window,
                re.S,
            ):
                cols.append(
                    {
                        "name": col.group(1),
                        "unit": col.group(2),
                        "description_verbatim": squash(col.group(3)),
                    }
                )
            entry["columns"] = cols
            families[fam] = entry

        result["families"] = families

        REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Source: {SIS_TXT}\n")
        print("SIS 2.1.3 (TOF mass spectrometer), verbatim:")
        print(f"  {result['tof_spectrometer_section_verbatim'][:400]}...\n")
        for fam, entry in families.items():
            print(f"{fam}: {entry['product_name_verbatim']}")
            print(f"    TABLE DESCRIPTION: {entry['table_description_verbatim']}")
            for col in entry["columns"]:
                print(f"    column {col['name']} [{col['unit']}]: {col['description_verbatim']}")
            print()
        print(f"Wrote {REPORT.relative_to(REPO_ROOT)}")
        return 0

    except FetchError as exc:
        result["status"] = "UNRESOLVED"
        result["blocker"] = str(exc)
        REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"UNRESOLVED — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
