#!/usr/bin/env python3
"""KILL-TEST 2 SUPPORT — which CDA product families exist, and which carry rows?

Why this exists
---------------
Kill-test 2 asks whether one raw MS (time-of-flight) trace can be extracted from
the PDS3 Cassini CDA archive. On COCDA_0001 the only product matching the MS
pattern — ``CDASPECTRA`` — declares ``ROWS = 0`` and its data file is a single
blank record. Sampling three further volumes by hand showed the same shape, so
the family the MS pattern selects looked empty wherever it was checked. This
reads an index in full and reports, per product family, how many entries carry
records — which is how the ``QTSIGNALS`` per-event family was found.

Scope warning, learned the hard way
-----------------------------------
``CUMINDEX.TAB`` on this archive is **not** cumulative across volumes. Every
entry in COCDA_0101's copy carries the ``COCDA_0101`` prefix, so reading it
describes that one volume, not the archive. The volumes actually covered are
therefore derived from the data and reported in ``volumes_covered``; no claim is
made about volumes absent from that list.

This script stamps no verdict. It reports counts so that kill-test 2 can be
adjudicated on read evidence.

Usage
-----
    python src/killtest2_survey_products.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import REPO_ROOT, FetchError, fetch  # noqa: E402

CUMINDEX_LBL = "https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/INDEX/CUMINDEX.LBL"
CUMINDEX_TAB = "https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/INDEX/CUMINDEX.TAB"
DEST_DIR = REPO_ROOT / "data" / "cda" / "COCDA_0101" / "index"
REPORT = REPO_ROOT / "reports" / "killtest2_product_survey.json"

# Group products into families from the first path segment below DATA/, taking
# its leading alphabetic run and dropping any date-range stamp:
#   COCDA_0050/DATA/CDASPECTRA_08214_08244.TAB              -> CDASPECTRA
#   COCDA_0101/DATA/QTSIGNALS_17181_17258/QT_02920663.LBL   -> QTSIGNALS
# Keying on the segment below DATA/ rather than on the filename is what makes the
# per-event QTSIGNALS products group together instead of scattering.
FAMILY = re.compile(r"/DATA/([A-Za-z]+)")


def main() -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "check": "killtest2_product_survey",
        "question": (
            "Across every COCDA volume, which product families carry rows, and is "
            "any CDASPECTRA product non-empty?"
        ),
        "source_label": CUMINDEX_LBL,
        "source_table": CUMINDEX_TAB,
    }

    try:
        import pdr

        label = DEST_DIR / "cumindex.lbl"
        fetch(CUMINDEX_LBL, label, note="COCDA_0101 cumulative index label (kill-test 2 survey)")

        # Detached label: the data file must sit alongside it under the exact name
        # the label's ^POINTER declares. CUMINDEX.LBL points at "INDEX.TAB", not at
        # "CUMINDEX.TAB", so saving the download under its own URL basename leaves
        # pdr unable to find the table. The name is read from the label rather than
        # assumed.
        label_text = label.read_text(encoding="utf-8", errors="replace")
        pointer = re.search(r"^\s*\^\w+\s*=\s*\"([^\"]+)\"", label_text, re.M)
        if not pointer:
            raise FetchError(
                f"no ^POINTER record found in {CUMINDEX_LBL}; cannot tell what the "
                "data file is called without guessing."
            )
        data_name = pointer.group(1).strip()
        result["label_pointer"] = data_name
        fetch(
            CUMINDEX_TAB,
            DEST_DIR / data_name,
            note="COCDA_0101 cumulative index table (kill-test 2 survey)",
        )

        data = pdr.read(str(label))
        keys = [str(k) for k in data.keys()]
        result["pdr_keys"] = keys

        table = None
        for key in data.keys():
            if hasattr(data[key], "columns"):
                table = data[key]
                result["table_key"] = str(key)
                break
        if table is None:
            raise FetchError(f"no tabular object in cumulative index; keys were {keys}")

        result["total_rows"] = int(len(table))
        result["columns"] = [str(c) for c in table.columns]

        spec_col = "FILE_SPECIFICATION_NAME"
        rec_col = "FILE_RECORDS"
        for needed in (spec_col, rec_col):
            if needed not in table.columns:
                raise FetchError(
                    f"cumulative index has no {needed!r} column; columns were "
                    f"{[str(c) for c in table.columns]}. Refusing to guess a substitute."
                )

        # Count, per family, how many entries declare a non-zero record count.
        totals: dict[str, int] = defaultdict(int)
        nonempty: dict[str, int] = defaultdict(int)
        max_records: dict[str, int] = defaultdict(int)
        volumes: set[str] = set()
        for spec, records in zip(
            table[spec_col].astype(str), table[rec_col].astype("int64"), strict=False
        ):
            cleaned = spec.strip().strip('"')
            volumes.add(cleaned.split("/", 1)[0])
            match = FAMILY.search(cleaned)
            family = match.group(1).upper() if match else "UNMATCHED"
            totals[family] += 1
            if records > 0:
                nonempty[family] += 1
            max_records[family] = max(max_records[family], int(records))

        # Reported so no reader mistakes a one-volume survey for an archive-wide one.
        result["volumes_covered"] = sorted(volumes)
        result["volumes_covered_count"] = len(volumes)

        families = sorted(totals, key=lambda f: -totals[f])
        result["families"] = [
            {
                "family": f,
                "entries": totals[f],
                "entries_with_records_gt_zero": nonempty[f],
                "max_file_records": max_records[f],
            }
            for f in families
        ]

        spectra = [row for row in result["families"] if row["family"] == "CDASPECTRA"]
        result["cdaspectra"] = spectra[0] if spectra else None
        result["any_nonempty_cdaspectra"] = bool(spectra and spectra[0]["entries_with_records_gt_zero"])

        REPORT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Surveyed {result['total_rows']} index entries covering volume(s): {result['volumes_covered']}")
        for row in result["families"]:
            print(
                f"  {row['family']:<14} entries={row['entries']:<7} "
                f"with_records>0={row['entries_with_records_gt_zero']:<7} "
                f"max_FILE_RECORDS={row['max_file_records']} records"
            )
        print(f"\nAny non-empty CDASPECTRA product: {result['any_nonempty_cdaspectra']}")
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
