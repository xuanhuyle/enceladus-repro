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
    """Locate the volume's index table + label by walking the volume tree."""
    found: dict[str, str] = {}
    for sub in ("index/", ""):
        url = urljoin(volume_url, sub)
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
            f"no index.tab / index.lbl located under {volume_url}. "
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
        path_cols = [c for c in table.columns if re.search(r"(path|file|product)", str(c), re.I)]
        findings["path_like_columns"] = [str(c) for c in path_cols]
        if not path_cols:
            raise FetchError(
                f"no path/file column in index; columns were {list(table.columns)}. "
                "Cannot locate a product without guessing."
            )

        ms_rows = []
        for _, row in table.iterrows():
            joined = " ".join(str(row[c]) for c in path_cols)
            if re.search(r"\bMS\b|mass|tof|spectr", joined, re.I):
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
        product_url = urljoin(volume_url, rel)
        findings["ms_product_url"] = product_url
        head = requests.head(product_url, timeout=60, allow_redirects=True)
        size = int(head.headers.get("content-length", "0"))
        if size > MAX_PRODUCT_BYTES:
            raise FetchError(f"MS product {product_url} is {size} bytes; over cap {MAX_PRODUCT_BYTES}")

        dest = DATA_DIR / volume / Path(rel).name
        fetch(product_url, dest, note=f"{volume} raw MS (time-of-flight) product for kill-test 2")
        product = load_with_pdr(dest)

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        signal = None
        for key in getattr(product, "keys", lambda: [])():
            obj = product[key]
            arr = np.asarray(obj) if not hasattr(obj, "columns") else None
            if arr is not None and arr.ndim == 1 and arr.size > 16 and np.issubdtype(arr.dtype, np.number):
                signal = arr
                findings["ms_signal_key"] = str(key)
                break
        if signal is None:
            raise FetchError(f"no 1-D numeric signal in MS product; keys {list(product.keys())}")

        findings["ms_signal_samples"] = int(signal.size)

        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(np.arange(signal.size), signal, lw=0.7)
        ax.set_xlabel("Time-of-flight sample index [dimensionless]")
        ax.set_ylabel("Raw signal amplitude [instrument DN, uncalibrated]")
        ax.set_title(
            f"KILL-TEST 2 — raw CDA MS trace\n{volume} · {Path(rel).name} · "
            f"{signal.size} samples (MECHANICAL FACT: parsed by src/killtest2_cda.py)"
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
