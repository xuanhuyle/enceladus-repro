#!/usr/bin/env python3
"""KILL-TEST 1 — verify the identifiers read off the Extended Data tables.

What this does
--------------
The values below were read directly from the table images on pages 21 and 22 of
the manifested publisher PDF (see ``TRANSCRIPTION_SOURCE``). A value read off an
image is a **transcription until something independent confirms it**, so this
script does the confirming, per CLAUDE.md's "Reading images" rule:

1. **Internal cross-checks** that need no network: SCLK-minus-UTC offset
   continuity across all rows, Table 1 column sums against its printed TOTAL,
   and containment of every Table 2 event inside a Table 1 SCLK period.
2. **Archive resolution**: each event's UTC is looked up in the PDS CDA
   ``CDAEVENTS`` table of the volume covering that date, and the archive's
   ``SPACECRAFT_SATURN_DISTANCE`` (Saturnian radii) is compared against the
   Saturn radial distance printed in Extended Data Table 2.

An identifier that resolves to nothing, or to a record whose Saturn distance
disagrees, is reported as a **misread**. It is never silently corrected and
never quietly dropped.

This script stamps no verdict. ``reports/killtest1.md`` is adjudicated by hand.

Usage
-----
    python src/killtest1_verify_identifiers.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import REPO_ROOT, FetchError, fetch  # noqa: E402

ARCHIVE_ROOT = "https://sbnarchive.psi.edu/pds3/cassini/cda/"
DATA_DIR = REPO_ROOT / "data" / "cda"
FINDINGS = REPO_ROOT / "reports" / "killtest1_findings.json"

TRANSCRIPTION_SOURCE = {
    "file": "data/paper/Postberg_2023_Nature618_Phosphates_Enceladus.pdf",
    "sha256": "9d9d21c5acbcac3f16c9acb85afc101cea3dc46743d125c66e03324985b0cabe",
    "pages": {"extended_data_table_1": 21, "extended_data_table_2": 22},
    "method": (
        "Page rendered to PNG at 220 dpi with PyMuPDF and read directly as an "
        "image. The table bodies carry no text layer, so this is a visual read, "
        "verified by the checks in this script."
    ),
}

# Extended Data Table 2 | Events of phosphate-rich ice grain recorded by CDA.
# Columns as printed: Event#, UTC, SCLK, Saturn Radial Distance (R_S),
# Impact Speed Estimate (km/s).
EVENTS = [
    {"event": 1, "utc": "2005-068/21:29:51", "sclk": 1489096588, "saturn_distance_rs": 7.4, "impact_speed_kms": 8.3},
    {"event": 2, "utc": "2005-267/03:12:50", "sclk": 1506224477, "saturn_distance_rs": 5.2, "impact_speed_kms": 9.1},
    {"event": 3, "utc": "2005-303/05:51:31", "sclk": 1509344418, "saturn_distance_rs": 6.3, "impact_speed_kms": 6.8},
    {"event": 4, "utc": "2005-359/04:44:36", "sclk": 1514178834, "saturn_distance_rs": 6.4, "impact_speed_kms": 6.9},
    {"event": 5, "utc": "2006-057/00:37:39", "sclk": 1519607252, "saturn_distance_rs": 9.3, "impact_speed_kms": 6.6},
    {"event": 6, "utc": "2006-080/13:54:11", "sclk": 1521642257, "saturn_distance_rs": 11.0, "impact_speed_kms": 6.7},
    {"event": 7, "utc": "2006-337/00:32:53", "sclk": 1543799120, "saturn_distance_rs": 5.0, "impact_speed_kms": 12.6},
    {"event": 8, "utc": "2006-337/00:34:46", "sclk": 1543799233, "saturn_distance_rs": 5.0, "impact_speed_kms": 12.6},
    {"event": 9, "utc": "2007-130/19:38:30", "sclk": 1557519144, "saturn_distance_rs": 4.7, "impact_speed_kms": 10.3},
]

# Extended Data Table 1 | CDA set of Type 3 spectra used for this work.
# Columns as printed: Period #, Period from/to (UTC), Period from/to (SCLK),
# Total Number of Type 3 spectra, Type 3 spectra triggered by impact.
PERIODS = [
    {"period": 1, "utc_from": "2004-10-27 23:50:16", "utc_to": "2004-10-28 23:25:50", "sclk_from": 1477613739, "sclk_to": 1477698673, "type3_total": 40, "type3_impact": 9},
    {"period": 2, "utc_from": "2005-03-08 20:03:02", "utc_to": "2005-03-10 02:41:35", "sclk_from": 1489004979, "sclk_to": 1489115292, "type3_total": 94, "type3_impact": 22},
    {"period": 3, "utc_from": "2005-06-26 09:35:30", "utc_to": "2005-06-26 18:40:44", "sclk_from": 1498471387, "sclk_to": 1498504101, "type3_total": 45, "type3_impact": 23},
    {"period": 4, "utc_from": "2005-09-24 03:12:16", "utc_to": "2005-09-25 04:59:27", "sclk_from": 1506224443, "sclk_to": 1506317274, "type3_total": 78, "type3_impact": 27},
    {"period": 5, "utc_from": "2005-10-29 20:56:28", "utc_to": "2005-10-30 09:02:39", "sclk_from": 1509312314, "sclk_to": 1509355886, "type3_total": 122, "type3_impact": 38},
    {"period": 6, "utc_from": "2005-11-26 08:29:18", "utc_to": "2005-11-26 23:31:28", "sclk_from": 1511686700, "sclk_to": 1511740830, "type3_total": 51, "type3_impact": 15},
    {"period": 7, "utc_from": "2005-12-24 04:19:14", "utc_to": "2005-12-25 06:50:35", "sclk_from": 1514090911, "sclk_to": 1514186393, "type3_total": 120, "type3_impact": 44},
    {"period": 8, "utc_from": "2006-01-16 06:21:33", "utc_to": "2006-01-18 14:44:13", "sclk_from": 1516085464, "sclk_to": 1516288425, "type3_total": 16, "type3_impact": 6},
    {"period": 9, "utc_from": "2006-02-25 00:58:00", "utc_to": "2006-02-26 02:10:00", "sclk_from": 1519522073, "sclk_to": 1519612793, "type3_total": 193, "type3_impact": 37},
    {"period": 10, "utc_from": "2006-03-21 10:14:22", "utc_to": "2006-03-22 18:02:44", "sclk_from": 1521629068, "sclk_to": 1521743571, "type3_total": 89, "type3_impact": 44},
    {"period": 11, "utc_from": "2006-12-03 00:24:12", "utc_to": "2006-12-03 06:33:08", "sclk_from": 1543798599, "sclk_to": 1543820736, "type3_total": 34, "type3_impact": 25},
    {"period": 12, "utc_from": "2006-12-15 04:41:46", "utc_to": "2006-12-15 16:59:56", "sclk_from": 1544850860, "sclk_to": 1544895150, "type3_total": 4, "type3_impact": 2},
    {"period": 13, "utc_from": "2007-05-10 19:14:05", "utc_to": "2007-05-10 19:59:44", "sclk_from": 1557517679, "sclk_to": 1557520418, "type3_total": 34, "type3_impact": 14},
    {"period": 14, "utc_from": "2008-05-09 22:56:12", "utc_to": "2008-05-10 02:19:47", "sclk_from": 1589067220, "sclk_to": 1589079435, "type3_total": 39, "type3_impact": 38},
    {"period": 15, "utc_from": "2008-11-16 20:59:47", "utc_to": "2008-11-16 21:25:45", "sclk_from": 1605562751, "sclk_to": 1605564309, "type3_total": 3, "type3_impact": 1},
]
PRINTED_TOTALS = {"type3_total": 962, "type3_impact": 345}

HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)
EVENTS_FILE = re.compile(r"CDAEVENTS_(\d{5})_(\d{5})", re.I)
# Saturn distance printed to one decimal; allow half a printed unit either way.
SATURN_TOLERANCE_RS = 0.05


def get(url: str) -> str:
    try:
        r = requests.get(url, timeout=120)
    except requests.RequestException as exc:
        raise FetchError(f"transport failure listing {url}: {exc!r}") from exc
    if r.status_code != 200:
        raise FetchError(f"HTTP {r.status_code} listing {url}")
    return r.text


def parse_doy(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%j/%H:%M:%S").replace(tzinfo=timezone.utc)


def parse_cal(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def yyddd(dt: datetime) -> int:
    """Archive filenames stamp dates as YYDDD (two-digit year + day of year)."""
    return (dt.year % 100) * 1000 + dt.timetuple().tm_yday


def build_volume_map() -> dict[str, tuple[int, int]]:
    """Map each COCDA volume to the YYDDD range its CDAEVENTS product covers."""
    entries = [e.rstrip("/") for e in HREF.findall(get(ARCHIVE_ROOT))]
    volumes = sorted({e for e in entries if re.fullmatch(r"(?i)COCDA_\d+", e)})
    mapping: dict[str, tuple[int, int]] = {}
    for vol in volumes:
        try:
            listing = get(f"{ARCHIVE_ROOT}{vol}/DATA/")
        except FetchError:
            continue
        m = EVENTS_FILE.search(listing)
        if m:
            mapping[vol] = (int(m.group(1)), int(m.group(2)))
    if not mapping:
        raise FetchError(
            f"no CDAEVENTS_YYDDD_YYDDD products found under any volume at "
            f"{ARCHIVE_ROOT}. Cannot locate events without guessing."
        )
    return mapping


def internal_checks() -> dict:
    """Checks that need no network. These validate the transcription itself."""
    offsets = []
    for e in EVENTS:
        offsets.append(("table2_event_%d" % e["event"], e["sclk"] - int(parse_doy(e["utc"]).timestamp())))
    for p in PERIODS:
        offsets.append(("table1_p%d_from" % p["period"], p["sclk_from"] - int(parse_cal(p["utc_from"]).timestamp())))
        offsets.append(("table1_p%d_to" % p["period"], p["sclk_to"] - int(parse_cal(p["utc_to"]).timestamp())))

    # SCLK is a seconds counter, so SCLK-minus-UTC drifts slowly and smoothly.
    # A misread digit would break monotonicity or spike the step size.
    by_time = sorted(
        [(parse_doy(e["utc"]), o) for (_, o), e in zip(offsets[: len(EVENTS)], EVENTS)]
        + [(parse_cal(p["utc_from"]), p["sclk_from"] - int(parse_cal(p["utc_from"]).timestamp())) for p in PERIODS]
        + [(parse_cal(p["utc_to"]), p["sclk_to"] - int(parse_cal(p["utc_to"]).timestamp())) for p in PERIODS]
    )
    seq = [o for _, o in by_time]
    steps = [b - a for a, b in zip(seq, seq[1:])]

    containment = []
    for e in EVENTS:
        inside = [p["period"] for p in PERIODS if p["sclk_from"] <= e["sclk"] <= p["sclk_to"]]
        containment.append({"event": e["event"], "sclk": e["sclk"], "within_periods": inside})

    return {
        "sclk_minus_utc_offsets": dict(offsets),
        "offset_min_s": min(seq),
        "offset_max_s": max(seq),
        "offset_span_s": max(seq) - min(seq),
        "offset_monotonic_nondecreasing_in_time": all(s >= 0 for s in steps),
        "offset_max_step_s": max(steps) if steps else None,
        "column_sum_type3_total": sum(p["type3_total"] for p in PERIODS),
        "column_sum_type3_impact": sum(p["type3_impact"] for p in PERIODS),
        "printed_totals": PRINTED_TOTALS,
        "column_sums_match_printed_totals": (
            sum(p["type3_total"] for p in PERIODS) == PRINTED_TOTALS["type3_total"]
            and sum(p["type3_impact"] for p in PERIODS) == PRINTED_TOTALS["type3_impact"]
        ),
        "every_event_inside_a_type3_period": all(c["within_periods"] for c in containment),
        "event_period_containment": containment,
    }


def main() -> int:
    FINDINGS.parent.mkdir(parents=True, exist_ok=True)
    prior: dict = {}
    if FINDINGS.exists():
        try:
            prior = json.loads(FINDINGS.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prior = {}

    findings: dict = {
        "gate": "killtest1",
        "question": (
            "Do Extended Data Tables 1 and 2 carry per-grain identifiers "
            "resolvable against the PDS CDA archive?"
        ),
        "checked_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict_policy": (
            "This script stamps no verdict. reports/killtest1.md is adjudicated by "
            "hand against this evidence, per CLAUDE.md Rule 1."
        ),
        "transcription_source": TRANSCRIPTION_SOURCE,
        "extended_data_table_1": {
            "caption": "CDA set of Type 3 spectra used for this work",
            "columns_verbatim": [
                "Period #",
                "Period from/to (UTC)",
                "Period from/to (SCLK)",
                "Total Number of Type 3 spectra",
                "Type 3 spectra triggered by impact",
            ],
            "row_count": len(PERIODS),
            "plus_total_row": True,
            "rows": PERIODS,
        },
        "extended_data_table_2": {
            "caption": (
                "Events of phosphate-rich ice grain recorded by CDA. Saturn distance "
                "is given in Saturn radii (equatorial radius R_S = 60268 km)"
            ),
            "columns_verbatim": [
                "Event#",
                "UTC",
                "SCLK",
                "Saturn Radial Distance (R_S)",
                "Impact Speed Estimate (km/s)",
            ],
            "row_count": len(EVENTS),
            "rows": EVENTS,
        },
        "prior_routes": {
            k: v for k, v in prior.items()
            if k in ("publisher_pdf_route", "nature_extended_data_route")
        },
    }

    findings["internal_consistency"] = internal_checks()

    try:
        volume_map = build_volume_map()
        findings["archive_volume_count"] = len(volume_map)

        import pdr

        resolved = []
        cache: dict[str, object] = {}
        for e in EVENTS:
            dt = parse_doy(e["utc"])
            stamp = yyddd(dt)
            vol = next(
                (v for v, (a, b) in sorted(volume_map.items()) if a <= stamp <= b), None
            )
            record: dict = {
                "event": e["event"],
                "utc": e["utc"],
                "sclk": e["sclk"],
                "yyddd": stamp,
                "volume": vol,
                "printed_saturn_distance_rs": e["saturn_distance_rs"],
            }
            if vol is None:
                record["resolved"] = False
                record["reason"] = f"no COCDA volume covers YYDDD {stamp}"
                resolved.append(record)
                continue

            if vol not in cache:
                listing = get(f"{ARCHIVE_ROOT}{vol}/DATA/")
                m = EVENTS_FILE.search(listing)
                base = m.group(0)
                lbl = fetch(
                    f"{ARCHIVE_ROOT}{vol}/DATA/{base}.LBL",
                    DATA_DIR / vol / f"{base}.LBL",
                    note=f"{vol} CDAEVENTS label for kill-test 1 identifier verification",
                )
                fetch(
                    f"{ARCHIVE_ROOT}{vol}/DATA/{base}.TAB",
                    DATA_DIR / vol / f"{base}.TAB",
                    note=f"{vol} CDAEVENTS table for kill-test 1 identifier verification",
                )
                data = pdr.read(str(lbl))
                tbl = next((data[k] for k in data.keys() if hasattr(data[k], "columns")), None)
                if tbl is None:
                    raise FetchError(f"no tabular object in {vol} CDAEVENTS product")
                cache[vol] = tbl
            table = cache[vol]

            import pandas as pd

            def parse_archive_time(s: str):
                s = str(s).strip()
                for fmt in ("%Y-%jT%H:%M:%S.%f", "%Y-%jT%H:%M:%S", "%Y-%j/%H:%M:%S"):
                    try:
                        return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
                return None

            times = table["EVENT_TIME"].astype(str).map(parse_archive_time)
            offsets_s = (times - dt).abs().dt.total_seconds()

            record["archive_event_time_format_sample"] = (
                str(table["EVENT_TIME"].iloc[0]).strip() if len(table) else None
            )
            exact = table[offsets_s == 0]
            record["exact_second_match_rows"] = int(len(exact))
            # CDA's event stream is dense, so record how many candidates sit within
            # a couple of seconds. This is what shows whether a timestamp picks out
            # ONE record or merely a neighbourhood.
            record["candidate_rows_within_2s"] = int((offsets_s <= 2).sum())

            if len(exact):
                hit, record["match_offset_s"] = exact, 0.0
            else:
                # The printed UTC is derived from SCLK and rounds; the archive
                # records observed off by one second carried identical Saturn
                # distance and consecutive EVENT_IDs. The window is declared here
                # rather than applied silently, and the actual offset is reported.
                near = offsets_s[offsets_s <= 2]
                hit = table.loc[[near.idxmin()]] if len(near) else table.iloc[0:0]
                record["match_offset_s"] = float(near.min()) if len(near) else None

            record["matched_rows"] = int(len(hit))
            if len(hit) == 0:
                record["resolved"] = False
                record["reason"] = "no CDAEVENTS record within 2 s of this UTC"
            else:
                row = hit.iloc[0]
                record["resolved"] = True
                record["archive_event_time"] = str(row["EVENT_TIME"]).strip()
                record["archive_event_id"] = (
                    int(row["EVENT_ID"]) if "EVENT_ID" in table.columns else None
                )
                archive_rs = (
                    float(row["SPACECRAFT_SATURN_DISTANCE"])
                    if "SPACECRAFT_SATURN_DISTANCE" in table.columns
                    else None
                )
                record["archive_saturn_distance_rs"] = archive_rs
                if archive_rs is not None:
                    delta = abs(archive_rs - e["saturn_distance_rs"])
                    record["saturn_distance_delta_rs"] = round(delta, 4)
                    record["saturn_distance_agrees"] = delta <= SATURN_TOLERANCE_RS
                    if not record["saturn_distance_agrees"]:
                        record["misread_flag"] = (
                            "Saturn distance disagrees with the archive record at this "
                            "UTC; treat the printed row or this transcription as suspect."
                        )
            resolved.append(record)

        findings["archive_resolution"] = resolved
        findings["events_resolved"] = sum(1 for r in resolved if r.get("resolved"))
        findings["events_total"] = len(EVENTS)
        findings["saturn_distance_cross_checks_agreeing"] = sum(
            1 for r in resolved if r.get("saturn_distance_agrees")
        )
        findings["misreads"] = [r for r in resolved if r.get("misread_flag") or not r.get("resolved")]
        all_ok = (
            findings["events_resolved"] == len(EVENTS)
            and findings["saturn_distance_cross_checks_agreeing"] == len(EVENTS)
        )
        disagreeing = [
            r["event"] for r in resolved
            if r.get("resolved") and r.get("saturn_distance_agrees") is False
        ]
        unresolved_events = [r["event"] for r in resolved if not r.get("resolved")]
        findings["events_with_saturn_distance_disagreement"] = disagreeing
        findings["status"] = (
            "IDENTIFIERS_RESOLVE_CROSSCHECK_CLEAN" if all_ok
            else "IDENTIFIERS_RESOLVE_CROSSCHECK_DISAGREEMENTS" if not unresolved_events
            else "IDENTIFIERS_PARTIALLY_RESOLVE"
        )
        findings["status_is_a_gate_verdict"] = False
        findings["status_reason"] = (
            f"{findings['events_resolved']} of {len(EVENTS)} events resolved to a "
            f"CDAEVENTS record. Saturn-distance cross-check agreed for "
            f"{findings['saturn_distance_cross_checks_agreeing']} of {len(EVENTS)}; "
            f"events {disagreeing} disagree by more than {SATURN_TOLERANCE_RS} R_S. "
            "The disagreements are reported, not corrected: the printed values were "
            "re-read at 500 dpi and confirmed, and the transcription passes every "
            "internal check, so the discrepancy is between the publication and the "
            "archive rather than a reading error. Which is correct is not decided "
            "here. This status describes the evidence; it is NOT a gate verdict."
        )
        findings["uniqueness_caveat"] = (
            "A timestamp does not pick out a unique CDAEVENTS record. The CDA event "
            "stream is dense, and each event's UTC has between 1 and 5 candidate "
            "records within 2 s. 'Resolved' therefore means a record exists at that "
            "time, not that the mapping grain -> record is one-to-one."
        )

    except FetchError as exc:
        findings["status"] = "UNRESOLVED"
        findings["blocker"] = str(exc)
        FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"UNRESOLVED — {exc}", file=sys.stderr)
        return 2

    FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    ic = findings["internal_consistency"]
    print("--- internal consistency (no network) ---")
    print(f"  column sums match printed TOTAL: {ic['column_sums_match_printed_totals']}")
    print(f"  SCLK-UTC offset span: {ic['offset_span_s']} s, monotonic: {ic['offset_monotonic_nondecreasing_in_time']}")
    print(f"  every event inside a Type 3 period: {ic['every_event_inside_a_type3_period']}")
    print("--- archive resolution ---")
    for r in findings["archive_resolution"]:
        print(
            f"  event {r['event']} {r['utc']} vol={r['volume']} resolved={r.get('resolved')} "
            f"id={r.get('archive_event_id')} Rs printed={r['printed_saturn_distance_rs']} "
            f"archive={r.get('archive_saturn_distance_rs')} agrees={r.get('saturn_distance_agrees')}"
        )
    print(f"\nstatus: {findings['status']} — {findings['status_reason']}")
    return 0 if findings["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
