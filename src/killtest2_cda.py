#!/usr/bin/env python3
"""KILL-TEST 2 — can we parse the PDS3 Cassini CDA archive and pull one raw MS
(time-of-flight) signal out of it with ``pdr``?

Gate criterion
--------------
PASS  : one COCDA volume's index parses with pdr, and one raw MS trace is
        extracted and plotted to reports/killtest2_trace.png.
FAIL  : the volume downloads but the event table or the MS product cannot be
        parsed.
UNRESOLVED : the archive could not be reached.

"Ugly is fine; parsed is the gate." The plot is a labelled sanity check, not a
scientific figure.

Design note
-----------
The on-disk layout of the CDA volumes is *discovered*, not assumed: this script
walks the Apache directory listing rather than hardcoding a guessed path. Per
CLAUDE.md, a guessed path that happens to work is still a guess. If the listing
does not look the way this script expects, it fails loudly and says so.

Only ONE volume is touched, and downloads are size-capped, so this never pulls
the whole archive.

Usage
-----
    python src/killtest2_cda.py [--volume COCDA_0xxx]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from enceladus_repro.provenance import REPO_ROOT, FetchError, fetch  # noqa: E402

ARCHIVE_ROOT = "https://sbnarchive.psi.edu/pds3/cassini/cda/"
DATA_DIR = REPO_ROOT / "data" / "cda"
PLOT_PATH = REPO_ROOT / "reports" / "killtest2_trace.png"
FINDINGS = REPO_ROOT / "reports" / "killtest2_findings.json"

MAX_PRODUCT_BYTES = 50 * 1024 * 1024  # refuse to pull anything large
HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)

# File suffixes a PDS3 index may point at. Used only to recognise path-shaped
# values; nothing is fetched on the strength of its extension alone.
PDS_SUFFIXES = (".lbl", ".tab", ".dat", ".img", ".fmt", ".txt")

# Which per-event family carries the time-of-flight mass spectrum.
#
# SOURCED CLAIM — Cassini CDA Software Interface Specification, CDA_SIS_1_0.TXT,
# https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/DOCUMENT/CDA_SIS_1_0.TXT
# Section 2.1.3, "TOF mass spectrometer", verbatim: "The TOF mass spectrometer
# consists of the chemical analyser target (CAT), chemical analyser grid located
# 3 mm in front of the CAT, and the multiplier dynodes connected with the Dynode
# Logarithmic Amplifier (MP signal). ... positive plasma ions are separated very
# quickly from the plasma and accelerated toward the multiplier, forming a
# time-of-flight mass spectrum."
#
# The MP table alone describes its time axis as flight time: OFFSET_TIME
# [MICROSECONDS] is "Flight time measured from estimated time of impact", and
# AMPLITUDE [MICROVOLTS] is "Signal value provided by the multiplier channel".
# QI, QT, QC and QP all measure "Time after triggering event" against a
# RECONSTRUCTED_*_CHARGE in COULOMBS — they are charge channels, not spectra.
# Evidence: reports/ms_channel_identification.json, from src/identify_ms_channel.py.
#
# The earlier pattern (r"\bMS\b|mass|tof|spectr") matched only CDASPECTRA, the
# "SPECTRA PEAKS TABLE" — an evaluated peak listing, not the raw trace.
MS_PRODUCT = re.compile(r"(?:^|/)MPSIGNALS[^/]*/|(?:^|/)MP_\d+\.(?:LBL|TAB)$", re.I)


def looks_like_path_column(series) -> bool:
    """True when a column's *values* look like file paths.

    Matching column names alone is not sufficient. COCDA_0001's index carries
    both ``FILE_SPECIFICATION_NAME`` (the real path) and ``FILE_RECORDS`` (an
    integer record count); the name regex matches both, and joining the record
    count into the path yielded a corrupted URL (observed Session 005). Every
    sampled value must be path-shaped, so an ambiguous column is rejected rather
    than accepted on a majority vote.
    """
    sample = [str(v).strip().strip('"') for v in series.head(20)]
    if not sample:
        return False
    return all("/" in v or v.lower().endswith(PDS_SUFFIXES) for v in sample)


def product_url_for(rel: str, volume: str, volume_url: str) -> str:
    """Resolve an index path to an absolute URL.

    PDS3 ``FILE_SPECIFICATION_NAME`` is volume-relative on some volumes and
    archive-root-relative on others. COCDA_0001 uses the latter — every value
    begins with ``COCDA_0001/`` — so joining against the volume URL doubled the
    volume segment and returned HTTP 404 (observed Session 005). The base is
    chosen by inspecting the path itself rather than assuming either convention.
    """
    first_segment = rel.split("/", 1)[0]
    if first_segment.lower() == volume.lower():
        return urljoin(ARCHIVE_ROOT, rel)
    return urljoin(volume_url, rel)


def list_dir(url: str) -> list[str]:
    """Return hrefs from an Apache-style directory listing.

    Raises FetchError on any non-200 so a policy denial surfaces as UNRESOLVED
    rather than as an empty listing that reads like "nothing here".
    """
    try:
        response = requests.get(url, timeout=120)
    except requests.RequestException as exc:
        raise FetchError(f"transport failure listing {url}: {exc!r}") from exc
    if response.status_code != 200:
        raise FetchError(f"HTTP {response.status_code} listing {url}")

    entries = []
    for href in HREF.findall(response.text):
        if href.startswith(("?", "#", "/", "http")) or href in ("../",):
            continue
        entries.append(href)
    return entries


def pick_volume(explicit: str | None) -> str:
    """Choose exactly one COCDA volume to work with."""
    entries = list_dir(ARCHIVE_ROOT)
    volumes = [e.rstrip("/") for e in entries if re.match(r"(?i)cocda[_\-]?\d+", e.rstrip("/"))]
    if not volumes:
        raise FetchError(
            f"no COCDA_* volume directories found at {ARCHIVE_ROOT}. "
            f"Listing returned: {entries[:40]}"
        )
    if explicit:
        if explicit not in volumes:
            raise FetchError(f"requested volume {explicit!r} not in archive; available: {volumes}")
        return explicit
    return sorted(volumes)[0]


def find_index_files(volume_url: str) -> dict[str, str]:
    """Locate the volume's index table + label by walking the volume tree.

    The index subdirectory's name is *discovered* from the volume listing rather
    than assumed. PDS3 volumes conventionally uppercase it (``INDEX/``) and
    sbnarchive.psi.edu serves a case-sensitive path space, so a hardcoded
    lowercase ``index/`` returns HTTP 404 (observed on COCDA_0001, Session 005).
    Matching case-insensitively against the listing the server actually returns
    avoids replacing one cased guess with another.
    """
    volume_entries = list_dir(volume_url)
    index_dirs = [
        entry for entry in volume_entries
        if entry.endswith("/") and entry.rstrip("/").lower() == "index"
    ]
    # Some volumes keep index products at the volume root, so it is searched too.
    search_urls = [urljoin(volume_url, entry) for entry in index_dirs] + [volume_url]

    found: dict[str, str] = {}
    for url in search_urls:
        try:
            entries = list_dir(url)
        except FetchError:
            continue
        for entry in entries:
            lower = entry.lower()
            if lower.startswith("index") and lower.endswith((".tab", ".lbl")):
                found[lower] = urljoin(url, entry)
        if found:
            break
    if not found:
        raise FetchError(
            f"no index.tab / index.lbl located under {volume_url} "
            f"(searched, in order: {search_urls}). "
            "The volume layout differs from what this script expects; inspect "
            "the listing by hand rather than letting the script guess."
        )
    return found


def load_with_pdr(label_path: Path):
    import pdr

    data = pdr.read(str(label_path))
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--volume", default=None, help="e.g. COCDA_0001")
    args = parser.parse_args()

    FINDINGS.parent.mkdir(parents=True, exist_ok=True)
    findings: dict = {"gate": "killtest2", "archive_root": ARCHIVE_ROOT}

    try:
        volume = pick_volume(args.volume)
        findings["volume"] = volume
        volume_url = urljoin(ARCHIVE_ROOT, volume + "/")
        findings["volume_url"] = volume_url
        print(f"[killtest2] using volume {volume} -> {volume_url}")

        index_files = find_index_files(volume_url)
        findings["index_files"] = index_files

        local_index: dict[str, Path] = {}
        for name, url in index_files.items():
            dest = DATA_DIR / volume / "index" / name
            fetch(url, dest, note=f"{volume} volume index ({name}) for kill-test 2")
            local_index[name] = dest

        label = next((p for n, p in local_index.items() if n.endswith(".lbl")), None)
        if label is None:
            raise FetchError(f"index label (.lbl) not among downloaded files: {list(local_index)}")

        index = load_with_pdr(label)
        keys = list(getattr(index, "keys", lambda: [])())
        findings["index_pdr_keys"] = [str(k) for k in keys]
        print(f"[killtest2] pdr parsed index; keys = {keys}")

        table = None
        for key in keys:
            candidate = index[key]
            if hasattr(candidate, "columns"):
                table = candidate
                findings["index_table_key"] = str(key)
                break
        if table is None:
            raise FetchError(f"no tabular object in parsed index; keys were {keys}")

        findings["index_n_rows"] = int(len(table))
        findings["index_columns"] = [str(c) for c in table.columns]
        print(f"[killtest2] index rows = {len(table)}; columns = {list(table.columns)}")

        # Locate an MS (time-of-flight mass spectrum) product from the index.
        named_cols = [c for c in table.columns if re.search(r"(path|file|product)", str(c), re.I)]
        path_cols = [c for c in named_cols if looks_like_path_column(table[c])]
        findings["name_matched_columns"] = [str(c) for c in named_cols]
        findings["path_like_columns"] = [str(c) for c in path_cols]
        if not path_cols:
            raise FetchError(
                f"no column with path-shaped values in index; name matched "
                f"{[str(c) for c in named_cols]}, all columns were "
                f"{[str(c) for c in table.columns]}. "
                "Cannot locate a product without guessing."
            )

        ms_rows = []
        for _, row in table.iterrows():
            joined = " ".join(str(row[c]) for c in path_cols)
            if MS_PRODUCT.search(joined):
                ms_rows.append(joined)
        findings["ms_candidate_count"] = len(ms_rows)
        findings["ms_candidate_sample"] = ms_rows[:10]

        if not ms_rows:
            raise FetchError(
                "index parsed, but no MS/time-of-flight product identifiable from "
                f"path-like columns {[str(c) for c in path_cols]}. "
                "Inspect reports/killtest2_findings.json and refine by hand."
            )

        # Fetch and parse the first MS candidate.
        rel = ms_rows[0].strip().strip('"').replace("\\", "/").lstrip("/")
        product_url = product_url_for(rel, volume, volume_url)
        findings["ms_product_url"] = product_url
        head = requests.head(product_url, timeout=60, allow_redirects=True)
        size = int(head.headers.get("content-length", "0"))
        if size > MAX_PRODUCT_BYTES:
            raise FetchError(f"MS product {product_url} is {size} bytes; over cap {MAX_PRODUCT_BYTES}")

        dest = DATA_DIR / volume / Path(rel).name
        fetch(product_url, dest, note=f"{volume} raw MS (time-of-flight) product for kill-test 2")

        # PDS3 labels here are DETACHED: the .LBL carries only the description and
        # the data lives in a sibling file. Without it pdr warns "TABLE file not
        # found in path" and yields an empty product (observed Session 005), which
        # would otherwise be misread as a parse failure. The companion's name is
        # taken from the label's ^TABLE pointer where that names a real file, and
        # otherwise from the label's own basename, which is the archive's actual
        # convention here — the pointer on COCDA_0001 reads "CDASPECTRA.TAB" while
        # the file on disk is CDASPECTRA_99084_00100.TAB.
        if dest.suffix.upper() == ".LBL":
            companion = Path(rel).with_suffix(".TAB").as_posix()
            data_url = product_url_for(companion, volume, volume_url)
            findings["ms_data_file_url"] = data_url
            probe = requests.head(data_url, timeout=60, allow_redirects=True)
            if probe.status_code != 200:
                raise FetchError(
                    f"detached label {product_url} downloaded, but its companion data "
                    f"file {data_url} returned HTTP {probe.status_code}. The data file "
                    "is where the trace lives; refusing to report on the label alone."
                )
            data_bytes = int(probe.headers.get("content-length", "0"))
            findings["ms_data_file_bytes"] = data_bytes
            if data_bytes > MAX_PRODUCT_BYTES:
                raise FetchError(
                    f"MS data file {data_url} is {data_bytes} bytes; over cap "
                    f"{MAX_PRODUCT_BYTES} bytes"
                )
            fetch(
                data_url,
                dest.with_suffix(".TAB"),
                note=f"{volume} MS data file accompanying {dest.name} for kill-test 2",
            )

        product = load_with_pdr(dest)

        # An empty product is not a parsing failure, and must not be reported as
        # one. COCDA_0001's only spectra product declares ROWS = 0 and its .TAB is
        # a single blank record, so there is no trace in it to extract.
        declared_rows = None
        label_text = dest.read_text(encoding="utf-8", errors="replace")
        rows_match = re.search(r"^\s*ROWS\s*=\s*(\d+)", label_text, re.M)
        if rows_match:
            declared_rows = int(rows_match.group(1))
            findings["ms_declared_rows"] = declared_rows
        if declared_rows == 0:
            raise FetchError(
                f"MS product {Path(rel).name} in {volume} is empty: its label declares "
                f"ROWS = {declared_rows} and its data file is {findings.get('ms_data_file_bytes')} "
                "bytes. Nothing was mis-parsed — there is no trace in this product. "
                "Select a volume whose MS product carries rows (see --volume)."
            )

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        # An MP product is a two-column table, not a bare array: OFFSET_TIME
        # against AMPLITUDE. Both axes therefore carry the units the label itself
        # declares, rather than a sample index and an uncalibrated DN count.
        ms_table = None
        for key in getattr(product, "keys", lambda: [])():
            obj = product[key]
            if hasattr(obj, "columns"):
                ms_table = obj
                findings["ms_signal_key"] = str(key)
                break
        if ms_table is None:
            raise FetchError(
                f"no tabular object in MS product; keys {list(product.keys())}"
            )

        cols = {str(c).upper(): c for c in ms_table.columns}
        if "OFFSET_TIME" not in cols or "AMPLITUDE" not in cols:
            raise FetchError(
                "MS product parsed, but it lacks the OFFSET_TIME/AMPLITUDE columns "
                f"the SIS specifies for an MP signal table; columns were "
                f"{[str(c) for c in ms_table.columns]}. Refusing to plot a column "
                "chosen by guess."
            )

        time_us = np.asarray(ms_table[cols["OFFSET_TIME"]], dtype=float)
        amplitude_uv = np.asarray(ms_table[cols["AMPLITUDE"]], dtype=float)
        if time_us.size < 2:
            raise FetchError(
                f"MS product has {time_us.size} row(s); a trace needs at least two "
                "points. Nothing was mis-parsed."
            )

        # Units are read off the label rather than hardcoded, so a future volume
        # that changes them cannot silently mislabel the axes.
        def unit_for(column: str, fallback: str) -> str:
            block = re.search(
                rf'NAME\s*=\s*"{column}".*?UNIT\s*=\s*"([^"]+)"', label_text, re.S
            )
            return block.group(1).strip() if block else fallback

        time_unit = unit_for("OFFSET_TIME", "MICROSECONDS")
        amp_unit = unit_for("AMPLITUDE", "MICROVOLTS")
        findings["ms_signal_samples"] = int(time_us.size)
        findings["ms_time_unit"] = time_unit
        findings["ms_amplitude_unit"] = amp_unit
        findings["ms_time_range"] = [float(np.nanmin(time_us)), float(np.nanmax(time_us))]
        findings["ms_amplitude_range"] = [
            float(np.nanmin(amplitude_uv)), float(np.nanmax(amplitude_uv))
        ]

        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(time_us, amplitude_uv, lw=0.9, marker="o", ms=3)
        ax.set_xlabel(f"Flight time from estimated impact [{time_unit.lower()}]")
        ax.set_ylabel(f"Multiplier signal amplitude [{amp_unit.lower()}]")
        ax.set_title(
            f"KILL-TEST 2 — raw CDA MP time-of-flight mass spectrum\n"
            f"{volume} · {Path(rel).name} · {time_us.size} samples "
            f"(MECHANICAL FACT: parsed by src/killtest2_cda.py)"
        )
        ax.grid(alpha=0.3)
        fig.tight_layout()
        PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(PLOT_PATH, dpi=140)
        findings["plot"] = str(PLOT_PATH.relative_to(REPO_ROOT))
        findings["status"] = "PASS"
        print(f"[killtest2] PASS — wrote {PLOT_PATH}")

    except FetchError as exc:
        findings["status"] = "UNRESOLVED"
        findings["blocker"] = str(exc)
        FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"UNRESOLVED — {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # parsing genuinely failed -> that is a FAIL, not a block
        findings["status"] = "FAIL"
        findings["error"] = f"{type(exc).__name__}: {exc}"
        FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
        print(f"FAIL — {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    FINDINGS.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
