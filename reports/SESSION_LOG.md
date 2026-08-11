# Session Log

Per **CLAUDE.md Rule 4**, every session records what was attempted, PASS/FAIL/UNRESOLVED
per gate, and evidence links. Newest session first.

---

## Session 005 — 2026-08-11 — Archive reachable; kill-test 2 exercised for real; paper bytes independently confirmed

**Branch:** `claude/session-005-provenance-gate-6jxjb0`, based on `main` at
`b561dac` by operator instruction.

**Open gate at session start:** kill-test 1, the go/no-go. Unchanged this
session — no verdict stamped, no adjudication attempted.

> **Ordering note.** Session 004's entry is **not in this file**. It lives only on
> the unmerged pull request
> [#3](https://github.com/xuanhuyle/enceladus-repro/pull/3) (branch
> `claude/postberg-phosphate-reproduction-mg9sjt`, head `88c24d2`). This branch
> was based on `main` as instructed, and `main` does not carry it. The two
> entries will need merging; both insert at the top of this file, so a conflict
> is expected there and is not evidence of lost work.

### Gate summary

| Gate | Verdict | Change this session |
| --- | --- | --- |
| Kill-test 1 | **`UNRESOLVED`** | none — not adjudicated. Its Nature-supplementary route was probed and is blocked (below) |
| Kill-test 2 | **`UNRESOLVED`** | **first genuine exercise of the parsing gate**; blocker moved from network to product selection |
| Paper byte provenance (**not a science gate**) | `PASS` | SHA256 re-confirmed independently |

### 1. Host probes — the environment split has closed

**MECHANICAL FACT** — one `HEAD` per host, 30 s timeout, `2026-08-11T03:38:27Z`:

| Host | This session | Session 004 (same day, ~`03:29Z`) |
| --- | --- | --- |
| `sbnarchive.psi.edu` | **`200`** | `CONNECT` `403` |
| `www.geo.fu-berlin.de` | **`200`** | `CONNECT` `403` |

Neither returned `403`, so the operator's stop-condition did not fire and the
session proceeded. This retires the Session 004 **HYPOTHESIS** of an environment
split for these two hosts: the archive answers here.

### 2. Paper provenance — `MATCH`

**MECHANICAL FACT** — `python src/verify_paper_provenance.py` (new this session)
re-fetched the PDF and recomputed its digest:

| Quantity | Value |
| --- | --- |
| Size | `16669185` bytes |
| SHA256 | `9d9d21c5acbcac3f16c9acb85afc101cea3dc46743d125c66e03324985b0cabe` |
| Manifest row it was compared against | retrieved `2026-08-10T04:32:10Z` |
| Result | **`MATCH`** — size and digest both equal |

Evidence: [`paper_provenance_check.json`](paper_provenance_check.json). The
expected digest is read from `data/MANIFEST.md` **before** the fetch, so the
fetch cannot supply its own expectation. `data/MANIFEST.md` is byte-for-byte
unchanged by this check, which is the correct outcome for matching bytes.

This closes the gap flagged in `BRANCH_INVENTORY.md` §3 and in Session 001b: the
digest had only ever been written by the session that downloaded the file. A
second session, on a different day, has now re-fetched and recomputed it.

> **This is provenance, not authentication.** It establishes that the bytes
> served at that URL are stable across sessions. It does **not** verify that the
> PDF is a genuine or correct copy of Postberg et al. 2023, and it must not be
> described that way — the host serving it is not the publisher of record.

### 3. Kill-test 2 — `UNRESOLVED`, but the gate was finally exercised

Full write-up: [`killtest2.md`](killtest2.md), rewritten this session because its
previous text ("the blocker is network only", "needs no edits") had become false.

**MECHANICAL FACT** — how far the run got: archive root listed (`100` `COCDA_*`
volumes); `COCDA_0001/INDEX/INDEX.LBL` + `INDEX.TAB` downloaded and manifested;
**`pdr` parsed the index**, returning `25885` rows with columns
`FILE_SPECIFICATION_NAME`, `RECORD BYTES`, `FILE_RECORDS`, `DATA_SET_ID`; the one
matching MS product located, downloaded and manifested.

**The blocker is no longer transport.** It is that the selected product is empty:
`CDASPECTRA_99084_00100.LBL` declares `ROWS = 0`, and its data file is `602`
bytes — one `RECORD_BYTES` of blank padding. Its `START_TIME`/`STOP_TIME` of
`1999-084` to `2000-100` place it in early cruise. Nothing was mis-parsed, so
this is `UNRESOLVED` and not `FAIL`; every product opened so far parsed correctly.

**Four defects fixed in `src/killtest2_cda.py`**, each found against real archive
files and each fixed by discovering the archive's shape rather than guessing
again: index directory case (`index/` → `404`, `INDEX/` → `200`); path-column
contamination (`FILE_RECORDS` joined into the path, yielding a URL ending
`...LBL 602`); doubled volume segment (paths are archive-root-relative here); and
detached labels (the `.LBL` carries no data, so the companion file must be
fetched or `pdr` silently returns an empty product).

**New: `src/killtest2_survey_products.py`** counts records per product family.
Covering **`COCDA_0101` only**, `292423` entries: five per-event signal families
carry records in bulk — `MPSIGNALS` `60178`, `QCSIGNALS` `60178`, `QISIGNALS`
`60178`, `QTSIGNALS` `55994`, `QPSIGNALS` `55889` entries, all with
`FILE_RECORDS` > 0 — while `CDASPECTRA` holds `1` entry with `550` records and
`CDAEVENTS` `1` entry with `0` records. Evidence:
[`killtest2_product_survey.json`](killtest2_product_survey.json).

> **A wrong claim caught and corrected.** The survey's first draft asserted
> archive-wide coverage. `CUMINDEX.TAB` here is **not** cumulative: every entry in
> `COCDA_0101`'s copy carries the `COCDA_0101` prefix. The script now derives and
> reports `volumes_covered` from the data, and its docstring records the trap. The
> incorrect numbers were never committed.

**Why the gate is still `UNRESOLVED`.** The gate wants "one raw MS
(time-of-flight) signal". Deciding which of five per-event signal families is the
time-of-flight mass spectrum is a determination about instrument channels, not
something the script's regex should settle. That adjudication was **not** made
here, on the same principle that keeps kill-test 1's verdict out of its script.

**HYPOTHESIS** — the raw trace is carried by a per-event signal family rather than
by `CDASPECTRA`, whose own label calls it a `"CASSINI CDA SPECTRA PEAKS TABLE"`.
No confidence level is attached. It earns status only from the archive's
`DOCUMENT/` description or from a successful extraction.

### 4. Gate 1 route — Nature supplementary files — `UNRESOLVED`

**Blocked, and not worked around.** The availability question was not answered.

**MECHANICAL FACT** — `doi.org` resolves (`302`) to
`https://www.nature.com/articles/s41586-023-05987-9`, and `www.nature.com`
answers, but every article request is bounced (`303`) to
`https://idp.nature.com/authorize?...`, and **`idp.nature.com` is denied**.
Verbatim, from `python src/gate1_nature_supplementary.py` (new this session):

```
transport failure for https://www.nature.com/articles/s41586-023-05987-9:
ProxyError(MaxRetryError("HTTPSConnectionPool(host='idp.nature.com', port=443):
Max retries exceeded with url: /authorize?response_type=cookie&client_id=grover&
redirect_uri=https%3A%2F%2Fwww.nature.com%2Farticles%2Fs41586-023-05987-9
(Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection
failed: 403 Forbidden')))"))
```

Evidence: [`gate1_supplementary_availability.json`](gate1_supplementary_availability.json).

**⚠️ Action required — allowlist `idp.nature.com`.** It is Nature's
cookie-setting redirect target; `www.nature.com` being reachable is not
sufficient, because no article page can be read without following it.

The committed script enumerates supplementary and Extended Data links and
classifies them by extension. Per the operator's instruction it reports
**availability only** — it does not download, parse or interpret any file's
contents, and stamps no verdict. It will run to completion unchanged once the
host is allowlisted.

### 5. The CDA email was not sent

`reports/draft_cda_email.md` is untouched and remains unsent, per instruction.

### Manifest note — two rows, one file

**MECHANICAL FACT** — `data/MANIFEST.md` gained seven rows. Two of them record
the same URL and the same SHA256
(`184f8aee7e54433b7acfd4a3d4516bd70fbd2d0e18d3a8639b6bf949f883daba`) under two
local names, `cumindex.tab` and `INDEX.TAB`. Both are true records: the first
run stored the download under its URL basename, and the label-pointer fix then
stored it under the name `CUMINDEX.LBL` actually declares. Rows are appended by
committed code and are not hand-edited, so both were left in place rather than
one being quietly deleted. Running the committed script today produces
`INDEX.TAB` only.

### Rule compliance

- **Rule 2** — every downloaded file is manifested with URL, SHA256, size in
  bytes and UTC timestamp.
- **Rule 3** — `git ls-files data/` returns `data/MANIFEST.md` and nothing else;
  `git check-ignore` confirms the PDF, both index tables and the MS products are
  ignored. No raw archive data is staged.

### Next session must

1. **Adjudicate which product family carries the raw MS trace**, from the
   archive's `DOCUMENT/` volume documentation rather than from family names, then
   re-run kill-test 2 against a volume whose MS product carries rows —
   `python src/killtest2_cda.py --volume COCDA_0101`.
2. **Allowlist `idp.nature.com`**, then re-run
   `python src/gate1_nature_supplementary.py` to get the availability answer for
   Extended Data Tables 1 and 2. Kill-test 1 stays `UNRESOLVED` until then.
3. **Merge Session 004's log entry** from PR #3 with this one; expect a conflict
   at the top of this file and resolve it by keeping both entries.
4. Note that a fresh environment needs `pip install cffi` after `pip install -e .`
   — the system `cryptography` package fails to load its Rust bindings without it,
   exactly as Session 003 predicted. This is an environment defect, so
   `pyproject.toml` is still deliberately unchanged.

---

## Session 003 — 2026-08-10 — Kill-test 1 executed; paper retrieved, table bodies not extractable

**Branch:** `claude/host-reachability-check-2nhjpc`

**Open gate at session start:** kill-test 1 — the go/no-go gate. Kill-test 2 is
also `UNRESOLVED` but sits downstream of it.

### Gate summary

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Kill-test 1 — grains → machine-readable identifiers | **`UNRESOLVED`** — unchanged, awaiting hand adjudication | [`killtest1_findings.json`](killtest1_findings.json) |
| Kill-test 2 — parse COCDA volume, extract MS trace | **`UNRESOLVED`** (not run) | [`killtest2.md`](killtest2.md) |
| Paper retrieval (**not a science gate**) | `PASS` | [`data/MANIFEST.md`](../data/MANIFEST.md) |

`src/killtest1_paper.py` ran to completion (exit `0`) for the first time — in
Session 001 it exited `2` at the fetch. **No verdict was stamped**;
`reports/killtest1.md` is byte-for-byte unchanged this session, by instruction
and by the script's own design.

### Retrieval — MECHANICAL FACT

`python src/killtest1_paper.py` fetched the target PDF:

- `16669185` bytes, SHA256 `9d9d21c5acbcac3f16c9acb85afc101cea3dc46743d125c66e03324985b0cabe`
- Retrieved `2026-08-10T04:32:10Z` from
  `https://www.geo.fu-berlin.de/en/geol/fachrichtungen/planet/projects/habitat_oasis/_layout/Postberg_2023_Nature618_Phosphates_Enceladus.pdf`
- Manifest row appended automatically by `src/enceladus_repro/provenance.py`
- The PDF is **not committed** (Rule 3); `git check-ignore` confirms `data/*`
  covers it, and `MANIFEST.md` is the only tracked file under `data/`

This retires the Session 002 **HYPOTHESIS** for this one host: `www.geo.fu-berlin.de`
served bytes, so the egress block recorded in Session 001 is confirmed lifted
**for that host**. `sbnarchive.psi.edu` has still only answered a `HEAD` on its
host root; no archive volume has been downloaded.

### What the paper contains — MECHANICAL FACT

`24` pages, `73748` characters extracted document-wide.

**Extended Data Tables 1 and 2 are present in the PDF.** Their headings begin
pages `21` and `22`:

- p`21` — `Extended Data Table 1 | CDA set of Type 3 spectra used for this work`
- p`22` — `Extended Data Table 2 | Events of phosphate-rich ice grain recorded by CDA`

The stop-condition set for this session ("if the tables are not in the PDF, say
so and stop") therefore **did not fire**.

### The finding that matters — MECHANICAL FACT

**The table bodies did not extract as text.** Characters recovered from the two
table pages:

| Page | Table | Extracted chars | Content recovered |
| --- | --- | --- | --- |
| `21` | Extended Data Table 1 | `69` | heading line only |
| `22` | Extended Data Table 2 | `334` | heading + caption + footnote only |

Combined scan scope: `404` characters. All six identifier patterns returned
`0` matches — `sclk_10digit`, `long_integer_8_12`, `iso_datetime`,
`doy_datetime`, `event_id_labelled`, `cda_product_name`.

**Zero identifier matches here is not evidence that identifiers are absent.** It
is evidence that the table contents were never read: the tables are rendered as
images or vector graphics, so `pypdf` recovered only the captions. Absence of
extractable text and absence of identifiers imply opposite verdicts
(`UNRESOLVED` versus `FAIL`), and this evidence cannot distinguish them. The
verbatim text of both pages is stored in `table_page_extracts` in the findings
JSON so the adjudicator can read exactly what was recovered.

### Script changes — evidence only, no verdict logic

Two defects in `src/killtest1_paper.py` would have handed the adjudicator
misleading evidence. Both are fixed; neither adds verdict logic:

1. **Scope contamination.** The heading regex matches body-text
   cross-references ("listed in Extended Data Table 1") as readily as a real
   heading, so the scan covered pages `[2, 6, 7, 9, 11, 21, 22]` — five prose
   pages plus the two real tables. Those prose pages contributed the only two
   hits in the previous run (`201604910894`, `spectrum #3`), neither of which
   came from a table. Matches are now split by character offset into
   `heading_pages` and `cross_reference_pages`, raw offsets retained so the
   split can be checked; the scan now covers only pages `[21, 22]`.
2. **Misleading text-layer flag.** `text_layer_present` is document-wide and
   reports `true` — correct but irrelevant, since the body prose has a full text
   layer while the table pages have none. Added `page_char_counts`,
   `scanned_scope_chars`, and verbatim `table_page_extracts`.

### Toolchain repair

`pypdf` failed to import: the system `cryptography` package
(`/usr/lib/python3/dist-packages`) could not load its Rust bindings —
`ModuleNotFoundError: No module named '_cffi_backend'`, surfacing as
`pyo3_runtime.PanicException`. Fixed with `pip install cffi` (`cffi` `2.1.1`,
`pycparser` `3.0`). This is an environment defect, not a project dependency
gap, so `pyproject.toml` was left unchanged — but a fresh environment will hit
it again after `pip install -e .`. The first run crashed *after* a successful
fetch and *before* writing findings, which is why the manifest row predates the
evidence file.

### Not attempted, deliberately

Recovering the table contents needs a different method — OCR of the table
images, or the Nature-hosted supplementary files. **Neither was attempted.**
Both are a change of method and, for the Nature route, a different source; per
the standing instruction and CLAUDE.md's working practice, that decision is the
operator's, not this session's.

### Next session must

1. **Adjudicate `killtest1.md` by hand** from `killtest1_findings.json`. The
   evidence supports a decision about whether the tables were *read*, not about
   whether identifiers exist.
2. Decide the method for recovering the table bodies, if that decision is that
   the gate should proceed.
3. Leave kill-test 2 alone until kill-test 1 returns `PASS` (Rule 1).

---

## Session 002 — 2026-08-10 — Environment reachability check only

**Branch:** `claude/host-reachability-check-2nhjpc`

**Scope:** environment probe only. The operator explicitly instructed: do not run
the kill-tests, do not modify files, do not commit. The commit of this log entry
was authorized separately, afterwards.

### Gate summary

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Kill-test 1 — grains → machine-readable identifiers | **`UNRESOLVED`** (not re-run) | [`killtest1.md`](killtest1.md) |
| Kill-test 2 — parse COCDA volume, extract MS trace | **`UNRESOLVED`** (not re-run) | [`killtest2.md`](killtest2.md) |
| Host reachability (**not a science gate**) | `PASS` — 5/5 host roots answered | table below |
| Network policy identification | **`UNRESOLVED`** (denied locally) | verbatim errors below |

**Neither kill-test was executed this session, so neither verdict moved.** Both
remain `UNRESOLVED` and both still block everything downstream of them. Hosts
answering is *not* a gate result; per **Rule 1** an `UNRESOLVED` gate is cleared
only by running the check to completion.

### Host reachability probe (MECHANICAL FACT)

One `HEAD` per host, redirects **not** followed, 30 s timeout:

```bash
curl -sS -o /dev/null -I -m 30 -w 'HTTP_CODE=%{http_code}\n' https://<host>/
```

| Host | Reachable | HTTP status |
| --- | --- | --- |
| `sbnarchive.psi.edu` | yes | `200` |
| `www.geo.fu-berlin.de` | yes | `200` |
| `www.nature.com` | yes | `303` |
| `static-content.springer.com` | yes | `200` |
| `doi.org` | yes | `301` |

`303` and `301` are redirect responses — the host answered. Redirect targets were
not followed and are therefore not recorded. No host returned `403`, `407`, or
`405`, which per `/root/.ccr/README.md` (lines 46–57) are the egress proxy's
policy-denial and non-CONNECT-rejection codes.

**This supersedes the reachability table in Session 001 for these five hosts
only.** Session 001 recorded all five as `403` on `CONNECT` at ~`02:23Z`; they
answered at ~`04:24Z` the same day. Session 001's table is left unedited as the
historical record of what was true then.

### What this probe does **not** establish

- **Only host roots (`https://<host>/`) were probed — not the kill-test target
  URLs.** `https://www.geo.fu-berlin.de/.../Postberg_2023_Nature618_Phosphates_Enceladus.pdf`
  and `https://sbnarchive.psi.edu/pds3/cassini/cda/` were **not** requested. A
  reachable host root does not establish that those paths resolve, or that the
  bytes behind them are what the kill-tests expect.
- The three PDS mirrors and four literature hosts from Session 001
  (`pds.nasa.gov`, `sbn.psi.edu`, `pds-smallbodies.astro.umd.edu`, `arxiv.org`,
  `europepmc.org`, `www.ncbi.nlm.nih.gov`) were **not** re-probed. Their Session
  001 `403` status stands unverified as of this session.
- No file was downloaded. `data/MANIFEST.md` is unchanged, correctly.

**HYPOTHESIS** — the egress allowlist requested in Session 001 was granted
between the two sessions. Not verified from within this repository; no
confirmation of a policy change was obtainable (see below). This earns status
only by being confirmed from the environment side, or by a kill-test actually
retrieving bytes.

### Network policy identification — `UNRESOLVED`

Visible from `env` (MECHANICAL FACT): `HTTPS_PROXY=http://127.0.0.1:35467`; CA
bundle `/root/.ccr/ca-bundle.crt` exported via `SSL_CERT_FILE`, `CURL_CA_BUNDLE`,
`REQUESTS_CA_BUNDLE`, `NODE_EXTRA_CA_CERTS`; `NO_PROXY` covers loopback, RFC1918
and CGNAT ranges, `*.anthropic.com`, and the package registries.

The **policy name/tier is not visible.** Both calls that would have named it were
refused by the local permission classifier — *not* by the egress proxy. Verbatim,
for `curl -sS "$HTTPS_PROXY/__agentproxy/status"` and for the
`list_environments` tool:

```
Permission for this action was denied by the Claude Code auto mode classifier. Reason: Blocked by classifier.
```

No workaround was attempted. To resolve, allow `Bash(curl:*__agentproxy/status)`
or the `list_environments` tool.

### Next session must

1. **Re-run both kill-tests** — `python src/killtest1_paper.py` and
   `python src/killtest2_cda.py` — against their real target URLs, and replace
   the `UNRESOLVED` verdicts with real outcomes. Host reachability is not a
   substitute for either.
2. Confirm the deep target paths actually resolve, not just the host roots.
3. Hand-adjudicate `killtest1.md` from `killtest1_findings.json`, per its own
   instructions.
4. Confirm `data/MANIFEST.md` gains a row per downloaded file, and that no raw
   archive data is staged for commit.

---

## Session 001 — 2026-08-10 — Project setup and both kill-tests

**Branch:** `claude/postberg-phosphate-reproduction-mg9sjt`

### Gate summary

| Gate | Verdict | Evidence |
| --- | --- | --- |
| Kill-test 1 — grains → machine-readable identifiers | **`UNRESOLVED`** (blocked) | [`killtest1.md`](killtest1.md), [`killtest1_findings.json`](killtest1_findings.json) |
| Kill-test 2 — parse COCDA volume, extract MS trace | **`UNRESOLVED`** (blocked) | [`killtest2.md`](killtest2.md), [`killtest2_findings.json`](killtest2_findings.json) |
| Toolchain self-test (**not a science gate**) | `PASS` | `src/selftest_toolchain.py` |

**Both kill-tests are blocked by network egress policy, not by anything about the
science or the code.** Neither question was actually tested. No downstream work
may proceed until at least kill-test 1 returns `PASS`.

### What was attempted

**Done — needed no network:**

- `CLAUDE.md` — the five standing rules, plus working practice on network blocks,
  reproducibility, and scope discipline.
- Repo skeleton: `/src`, `/data` (gitignored except `MANIFEST.md`), `/reports`,
  `/notebooks`; `pyproject.toml` on Python ≥3.11 with `pdr`, `numpy`,
  `matplotlib`, `requests` (+ `pypdf`, needed to read the paper in kill-test 1).
- `src/enceladus_repro/provenance.py` — the only supported way to put a file
  under `data/`. Logs URL + SHA256 + size + UTC timestamp to `data/MANIFEST.md`
  automatically, so the manifest cannot drift from what is on disk. No retries
  against alternate sources, no cached fallback.
- `src/killtest1_paper.py` and `src/killtest2_cda.py` — complete and runnable.
  Both were executed; both exited `2` (`UNRESOLVED`) and wrote their blockers to
  JSON. They need **no edits** once the hosts are allowlisted.
- `reports/draft_cda_email.md` — drafted **unsent**, per Step 5.

**Blocked:** retrieval of the paper PDF; retrieval of any COCDA volume.

### Evidence that the block is policy, not tooling

Three independent client stacks agree, which rules out TLS and configuration
faults:

| Client | Result |
| --- | --- |
| `curl` | `curl: (56) CONNECT tunnel failed, response 403` |
| Python `requests` | `ProxyError(... 'Tunnel connection failed: 403 Forbidden')` |
| `WebFetch` tool | `{"error_type":"EGRESS_BLOCKED", ...}` |

The proxy's status endpoint logs each denial as
`gateway answered 403 to CONNECT (policy denial or upstream failure)`. A 403 on
`CONNECT` is refused before TLS is negotiated.

And the toolchain itself is proven good: `pdr` 1.4.4 parsed a synthetic PDS3
label (32 rows, 2 columns) and matplotlib rendered a PNG. **The only missing
input is network reach.**

### Host reachability probe (MECHANICAL FACT)

| Host | Result | Needed for |
| --- | --- | --- |
| `www.geo.fu-berlin.de` | **BLOCKED** 403 | Kill-test 1 — the paper PDF |
| `sbnarchive.psi.edu` | **BLOCKED** 403 | Kill-test 2 — the CDA volumes |
| `www.nature.com` | **BLOCKED** 403 | Extended Data / supplementary files |
| `static-content.springer.com` | **BLOCKED** 403 | Nature supplementary file hosting |
| `doi.org` | **BLOCKED** 403 | Citation resolution |
| `pds.nasa.gov` | **BLOCKED** 403 | PDS mirror |
| `sbn.psi.edu` | **BLOCKED** 403 | PDS Small Bodies Node |
| `pds-smallbodies.astro.umd.edu` | **BLOCKED** 403 | PDS mirror |
| `arxiv.org` | **BLOCKED** 403 | Preprint route |
| `europepmc.org`, `www.ncbi.nlm.nih.gov` | **BLOCKED** 403 | Literature route |
| `github.com`, `raw.githubusercontent.com` | OK | Code push |
| `pypi.org` | OK | Dependency install |

No alternate route to the data exists in this environment. No workaround was
attempted, and none would have been used without asking first.

### ⚠️ Action required — allowlist request

To unblock, add to the environment's network egress allowlist:

**Required — kill-test 2 (parsing gate):**
```
sbnarchive.psi.edu
```

**Required — kill-test 1 (go/no-go gate):**
```
www.geo.fu-berlin.de
```

**Strongly recommended — the Extended Data tables may live in the Nature-hosted
supplementary files rather than in that PDF:**
```
www.nature.com
static-content.springer.com
doi.org
```

**Optional fallbacks, if PSI is slow or partially mirrored:**
```
pds.nasa.gov
sbn.psi.edu
pds-smallbodies.astro.umd.edu
```

All are read-only HTTPS `GET` over port 443 against public archives.

Once allowlisted, the whole gate sequence is three commands:

```bash
pip install -e .
python src/killtest1_paper.py     # writes reports/killtest1_findings.json
python src/killtest2_cda.py       # writes reports/killtest2_trace.png on PASS
```

### Next session must

1. Re-run both kill-tests and **replace the `UNRESOLVED` verdicts with real
   outcomes** — do not let them decay into assumed passes.
2. Hand-adjudicate `killtest1.md` from the JSON evidence (the script does not
   stamp its own verdict, by design).
3. Decide on `draft_cda_email.md`: **delete it** if the Extended Data tables do
   carry usable identifiers; send it only if all three preconditions in its
   banner hold.
4. Confirm `data/MANIFEST.md` gained a row per downloaded file, and that no raw
   archive data was staged for commit.

---

## Session 001b — 2026-08-10 04:58Z–13:54Z — Monitoring check-ins

> **Ordering note.** This entry is appended at the end of the file rather than at
> the top, despite post-dating Sessions 002–003, so that it does not collide with
> the edit region those sessions use. Chronologically it is the most recent entry.

**Branch:** `claude/postberg-phosphate-reproduction-mg9sjt` · **Continues:** Session 001

### Gate summary — unchanged

| Gate | Verdict | Change this session |
| --- | --- | --- |
| Kill-test 1 | **`UNRESOLVED`** | none from this session |
| Kill-test 2 | **`UNRESOLVED`** | none from this session |

No gate was advanced here. This session retrieved nothing and computed nothing
about the science.

### What was attempted

Ten scheduled check-ins at roughly one-hour intervals, each re-probing the two
kill-test source hosts and re-reading the state of pull requests #1 and #2.

**MECHANICAL FACT** — every probe from this session returned the same result. One
`HEAD` per host per round, 25 s timeout, `curl` exit code `56`:

| Host | Rounds probed | Result every round |
| --- | --- | --- |
| `sbnarchive.psi.edu` | 10 | `CONNECT tunnel failed, response 403` |
| `www.geo.fu-berlin.de` | 10 | `CONNECT tunnel failed, response 403` |

Kill-test 2's source has never been reachable from this session, so no COCDA
volume has been downloaded and `reports/killtest2_trace.png` still does not exist.

### A sibling session executed kill-test 1

**SOURCED CLAIM** — pull request
[#2](https://github.com/xuanhuyle/enceladus-repro/pull/2) (branch
`claude/host-reachability-check-2nhjpc`, head `89ffa77`, base this branch) reports
Sessions 002–003, in which `www.geo.fu-berlin.de` was reachable and
`src/killtest1_paper.py` ran to completion.

**MECHANICAL FACT** — what this session verified directly, by reading that
branch's committed contents at `89ffa77`:

- `reports/killtest1.md` and `reports/killtest2.md` are byte-for-byte unchanged
  from `b501baf` (`git diff` returns empty for both). No verdict was stamped.
- `data/MANIFEST.md` gained exactly one row: the paper PDF, `16669185` bytes,
  SHA256 `9d9d21c5acbcac3f16c9acb85afc101cea3dc46743d125c66e03324985b0cabe`,
  retrieved `2026-08-10T04:32:10Z`. The PDF itself is not committed.
- `reports/killtest1_findings.json` records `24` pages, `73748` characters
  document-wide, Extended Data Table headings on pages `21` and `22`, and a
  scanned scope of `404` characters across those two pages.
- Verbatim page-21 extract: `Extended Data Table 1 | CDA set of Type 3 spectra
  used for this work`. Page 22 begins `Extended Data Table 2 | Events of
  phosphate-rich ice grain recorded by CDA.`
- All six identifier patterns returned `0` matches within that scope.

**`UNRESOLVED`** — this session did **not** verify the PDF's SHA256 against the
bytes. It never held the file: the source host is blocked here, and `data/` is
gitignored, so the digest above is quoted from that branch's manifest rather than
recomputed. Anyone with network access should re-fetch and confirm.

### Why kill-test 1 is still `UNRESOLVED` and not `FAIL`

**MECHANICAL FACT** — `69` characters extracted from page 21 and `334` from page
22 are heading, caption and footnote only; neither table body extracted. The
tables are image- or vector-rendered.

Zero identifier matches is therefore evidence that the table contents were never
read — not evidence that identifiers are absent. Those two states imply opposite
verdicts (`UNRESOLVED` vs `FAIL`) and the present evidence cannot distinguish
them. The gate stays `UNRESOLVED`.

### Defects found in this session's own kill-test 1 script

**MECHANICAL FACT** — Sessions 002–003 identified two defects in
`src/killtest1_paper.py` as committed at `b501baf`, both confirmed by reading the
code here:

1. The heading regex matched body-text cross-references ("listed in Extended Data
   Table 1") as readily as real headings, so the scan covered pages
   `[2, 6, 7, 9, 11, 21, 22]` — five prose pages beyond the two tables. Both
   identifier hits in that run came from prose, not from any table.
2. `text_layer_present` was computed document-wide, reporting `true` while the
   table pages specifically carry no text layer.

Either would have handed the adjudicator misleading evidence. Both are fixed on
the PR #2 branch.

### Network discrepancy

**MECHANICAL FACT** — this session was denied at `04:58Z`, `05:59Z`, `07:01Z`,
`08:06Z`, `09:26Z`, `10:28Z`, `11:30Z`, `12:33Z` and `13:54Z`; the sibling session
retrieved the PDF at `04:32:10Z`, inside that window.

**HYPOTHESIS** — the two sessions run in different environments with different
egress policies, rather than one policy having opened and closed. Not verified:
the proxy status endpoint reports only this session's own view.

### Repository state

**MECHANICAL FACT** — `main` was created at `14647fc` as an empty root commit; the
two Session 001 commits were rebased onto it (`152f66a`/`9203296` →
`7239dc3`/`b501baf`) and PR #1 opened against it. The repository's default branch
is still this feature branch, not `main`; changing it needs repo-settings access
no session here holds.

### Open decision for the operator

Recovering the Extended Data table bodies requires a change of method, and
possibly of source. Put to the operator `2026-08-10T08:06Z`, unanswered as of
`13:54Z`:

1. **Nature-hosted Extended Data.** Nature is the publisher of record, so this
   moves *toward* the primary source rather than substituting a secondary one for
   it, and may yield machine-readable tables.
2. **OCR of the retrieved PDF.** Same manifested source, no new network
   dependency. If used, every recovered identifier must be cross-checked against
   the archive before use — an OCR error in a spacecraft clock count would be
   silent.
3. **The CDA email.** Its premise has changed: the tables are now known to exist,
   and Extended Data Table 2 is titled as an event listing. `draft_cda_email.md`
   asks whether identifiers exist and should be rewritten before it is sent.

No option was chosen here. Under the scope-discipline rule that choice is the
operator's.

### Next session must

1. Not treat any of the above as advancing a gate. Both remain `UNRESOLVED`.
2. Re-fetch the paper and confirm its SHA256 against the manifest row, since no
   session has yet verified those bytes independently of the one that wrote them.
3. Act on the operator's decision once given — from an environment with network
   access, which this one is not.
