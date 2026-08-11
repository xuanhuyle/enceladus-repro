# KILL-TEST 2 — Can we parse a COCDA volume and extract one raw MS trace?

## Verdict

# `UNRESOLVED`

**Reason changed in Session 005.** The archive is now reachable, the volume index
parses with `pdr`, and an MS product was located and downloaded. The gate is
still `UNRESOLVED`, but no longer for a network reason:

1. The product the script's MS pattern selects in `COCDA_0001` — `CDASPECTRA` —
   is **empty**: its label declares `ROWS = 0` and its data file is `602` bytes,
   exactly one `RECORD_BYTES` of blank padding. There is no trace in it to plot.
2. The per-event signal families that do carry records (`QTSIGNALS`, `MPSIGNALS`,
   `QCSIGNALS`, `QISIGNALS`, `QPSIGNALS`) were found only after the survey below.
   **Which of them constitutes "the raw MS (time-of-flight) trace" is an
   adjudication, not a mechanical determination**, and this session did not make
   it. See "What still blocks the gate".

`reports/killtest2_trace.png` **does not exist**, and no placeholder has been
created in its place.

> The previous version of this file stated "the blocker is network only" and
> "`src/killtest2_cda.py` is complete and needs no edits." **Both statements are
> now false** and are corrected below. They were true when written; the first
> real run against the archive disproved them.

---

## The question

Can we download one small COCDA volume from the PSI PDS3 archive, parse its
event table with `pdr`, extract one raw MS (time-of-flight) signal, and plot it?

"Ugly is fine; parsed is the gate."

---

## What ran, and how far it got

**MECHANICAL FACT** — `python src/killtest2_cda.py`, Session 005, against
`https://sbnarchive.psi.edu/pds3/cassini/cda/`. Machine-readable evidence:
[`killtest2_findings.json`](killtest2_findings.json).

| Step | Outcome |
| --- | --- |
| List archive root | **reached** — `100` `COCDA_*` volume directories listed |
| Select one volume | `COCDA_0001` (the script's default: first in sorted order) |
| Locate volume index | `COCDA_0001/INDEX/INDEX.LBL` + `INDEX.TAB` |
| Download index | `4640` bytes label, `2717925` bytes table — both manifested |
| **Parse index with `pdr`** | **succeeded** — keys `['LABEL', 'INDEX_TABLE']` |
| Index contents | `25885` rows; columns `FILE_SPECIFICATION_NAME`, `RECORD BYTES`, `FILE_RECORDS`, `DATA_SET_ID` |
| Locate MS product | `COCDA_0001/DATA/CDASPECTRA_99084_00100.LBL` — the only one of `25885` rows matching the MS pattern |
| Download MS product | `68240` bytes label + `602` bytes data file — both manifested |
| **Extract a trace** | **blocked — the product is empty** |

The parsing gate has now been genuinely exercised for the first time: `pdr` read
a real PDS3 label from the real archive and returned a real table. That was never
true before Session 005.

---

## Why the selected product is empty — MECHANICAL FACT

`COCDA_0001/DATA/CDASPECTRA_99084_00100.LBL` declares, verbatim:

```
RECORD_BYTES                    = 602
FILE_RECORDS                    = 0
START_TIME                      = "1999-084T00:00:00"
STOP_TIME                       = "2000-100T00:00:00"
 ROWS                           = 0
```

Its data file `CDASPECTRA_99084_00100.TAB` is `602` bytes — one `RECORD_BYTES`
of blank padding. `START_TIME`/`STOP_TIME` place this volume in early cruise,
years before Saturn orbit insertion.

**This is not a parse failure and must not be recorded as `FAIL`.** Nothing was
mis-read; the product genuinely contains zero rows. The script now says so
explicitly rather than reporting the misleading "no 1-D numeric signal".

---

## Where the records actually are — MECHANICAL FACT

`python src/killtest2_survey_products.py` reads a volume index in full and counts
records per product family. Evidence:
[`killtest2_product_survey.json`](killtest2_product_survey.json).

Covering **`COCDA_0101` only** (`292423` index entries):

| Family | Entries | Entries with `FILE_RECORDS` > 0 | Max `FILE_RECORDS` |
| --- | --- | --- | --- |
| `MPSIGNALS` | `60178` | `60178` | `19` records |
| `QCSIGNALS` | `60178` | `60178` | `18` records |
| `QISIGNALS` | `60178` | `60178` | `18` records |
| `QTSIGNALS` | `55994` | `55994` | `18` records |
| `QPSIGNALS` | `55889` | `55889` | `20` records |
| `CDAAREA` | `1` | `1` | `26` records |
| `CDACOUNTER` | `1` | `1` | `200` records |
| `CDAEVENTS` | `1` | `0` | `0` records |
| `CDASETTINGS` | `1` | `1` | `84` records |
| `CDASPECTRA` | `1` | `1` | `550` records |
| `CDASTAT` | `1` | `1` | `70` records |

Two things follow, both narrow:

- **`CDASPECTRA` is not empty everywhere.** It is empty in `COCDA_0001` and
  carries `550` records in `COCDA_0101`. The emptiness is a property of the
  volume selected, not of the family.
- **The bulk of the volume is per-event signal products** in five families, each
  with tens of thousands of entries, each entry carrying records.

> **Scope warning.** `CUMINDEX.TAB` on this archive is **not** cumulative across
> volumes: every entry in `COCDA_0101`'s copy carries the `COCDA_0101` prefix.
> The table above therefore describes **one volume of one hundred**. An earlier
> draft of the survey script asserted archive-wide coverage; that claim was
> wrong, was caught by reading the parsed values, and has been corrected in the
> script's docstring and output.

---

## Four defects fixed in `src/killtest2_cda.py` — MECHANICAL FACT

Each was found by running against real archive files, and each is fixed by
*discovering* the archive's actual shape rather than substituting a new guess.

1. **Index directory case.** The script requested `<volume>/index/`, which
   returns HTTP `404`; the directory is `<volume>/INDEX/`, which returns HTTP
   `200`. The server's path space is case-sensitive. Fixed by matching the
   volume listing case-insensitively and using the name the server returned.
2. **Path column contamination.** The column filter `(path|file|product)` matched
   both `FILE_SPECIFICATION_NAME` (the path) and `FILE_RECORDS` (an integer
   count), and the two were joined into one string — producing a URL ending
   `...CDASPECTRA_99084_00100.LBL 602`. Fixed by requiring every sampled value in
   a candidate column to be path-shaped, so a column is rejected on its values,
   not accepted on its name.
3. **Doubled volume segment.** `FILE_SPECIFICATION_NAME` is archive-root-relative
   here — every value already begins `COCDA_0001/` — so joining against the
   volume URL produced `.../COCDA_0001/COCDA_0001/DATA/...` and HTTP `404`. Fixed
   by choosing the base from the path's own first segment, which handles both
   PDS3 conventions without assuming either.
4. **Detached labels.** These `.LBL` files carry no data; the table lives in a
   sibling file. Without it `pdr` warns `TABLE file ... not found in path` and
   returns an empty product — which the script would have reported as a missing
   signal. Fixed by fetching the companion data file and failing loudly if it is
   absent.

A fifth defect of the same kind was fixed in the survey script: `CUMINDEX.LBL`
points at `"INDEX.TAB"`, not at `"CUMINDEX.TAB"`, so the downloaded table has to
be stored under the name the label declares or `pdr` cannot find it.

---

## What still blocks the gate

**`UNRESOLVED`, and the remaining step is an adjudication this session did not
make.** The gate asks for "one raw MS (time-of-flight) signal". Five per-event
signal families carry records. Deciding which family is the time-of-flight mass
spectrum — and whether a `~18`-record product is the waveform or a peak listing —
is a scientific determination about instrument channels, not something a regex
should settle. Per the same principle that keeps kill-test 1's verdict out of its
script, that call is left to a reviewing session.

**HYPOTHESIS** — the raw time-of-flight trace is carried by one of the per-event
signal families rather than by `CDASPECTRA`, whose label calls it a
`"CASSINI CDA SPECTRA PEAKS TABLE"` and describes it as a peak evaluation. This
is flagged as conjecture, carries no confidence level, and earns status only by
being confirmed against the archive's own `DOCUMENT/` description or by a
successful extraction.

---

## To resolve

1. Adjudicate which product family carries the raw MS trace, from the archive's
   `DOCUMENT/` volume documentation rather than from the family names.
2. Point the script at a volume whose MS product carries rows — `--volume` is
   already supported, and `COCDA_0101` is known to carry `550` records in
   `CDASPECTRA`:
   ```bash
   python src/killtest2_cda.py --volume COCDA_0101
   ```
3. Replace this verdict with `PASS` or `FAIL` from the actual outcome, and link
   `killtest2_trace.png` as evidence.

A `FAIL` still requires the archive to be reachable **and** a product to refuse
to parse. That has not happened: every product opened so far parsed correctly.
