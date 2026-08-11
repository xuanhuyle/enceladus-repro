# Branch Inventory

Consolidation audit. **No kill-test was run in the session that produced this
file, and no gate verdict is changed by it.**

Everything below is **MECHANICAL FACT**, read out of committed git objects with
`git ls-remote`, `git log`, `git show`, `git diff` and `git merge-tree` at
`2026-08-11T03:29Z`. No claim here rests on any session's recollection of what it
did; each row was read back from the branch itself.

---

## 1. Branches

Three branches exist on `origin`. There are no others.

| Branch | Head SHA | Head commit date (UTC) | Contents |
| --- | --- | --- | --- |
| `main` | `14647fc` | 2026-08-10T03:54:06Z | Empty root commit. **Tracks zero files.** Created only to give the work a base to merge into. |
| `claude/postberg-phosphate-reproduction-mg9sjt` | `b7367fa` | 2026-08-10T18:08:42Z | Project scaffold — rules, skeleton, provenance helper, both kill-test scripts, both gate reports, unsent CDA email draft — plus Session 001 and Session 001b log entries. Retrieved nothing. |
| `claude/host-reachability-check-2nhjpc` | `89ffa77` | 2026-08-10T04:39:06Z | Sessions 002–003. Hosts reachable from that environment; **kill-test 1 actually executed**; paper retrieved and manifested; `killtest1_paper.py` defect fixes. |

### Topology — the two feature branches are siblings, not a stack

```
14647fc  main (empty root)
   └─ 7239dc3  scaffold
        └─ b501baf  ← merge base of both feature branches
             ├─ b7367fa   mg9sjt   (Session 001b log)
             └─ 7ac4275 → 89ffa77  2nhjpc  (Sessions 002, 003)
```

**MECHANICAL FACT** — `git merge-base` of the two feature branches is `b501baf`.
The `2nhjpc` branch forked *before* `b7367fa` was committed.

This matters for consolidation: pull request #2 declares its base as the `mg9sjt`
branch, which reads as a stack, but the underlying fork point is `b501baf`. The
two lines of work are parallel, and neither contains the other.

---

## 2. Gate evidence per branch

### `reports/killtest1_findings.json`

| Branch | `status` field, verbatim | Real evidence? |
| --- | --- | --- |
| `main` | *file does not exist* | No — branch tracks zero files |
| `claude/postberg-phosphate-reproduction-mg9sjt` | `"UNRESOLVED"` | **No — transport blocker only** |
| `claude/host-reachability-check-2nhjpc` | ***field absent*** — the JSON has no `status` key | **Yes — full evidence** |

**On `mg9sjt`** the file has five keys only: `gate`, `question`, `paper_url`,
`status`, `blocker`. The blocker reads:

> `transport failure for https://www.geo.fu-berlin.de/…/Postberg_2023_Nature618_Phosphates_Enceladus.pdf: ProxyError(MaxRetryError("HTTPSConnectionPool(host='www.geo.fu-berlin.de', port=443): …`

No page count, no headings, no identifier scan. Nothing was read.

**On `2nhjpc`** the file carries thirteen keys and real measurements:

| Quantity | Value |
| --- | --- |
| Pages in PDF | `24` pages |
| Text extracted, document-wide | `73748` characters |
| Extended Data Table 1 — heading page | page `21` |
| Extended Data Table 2 — heading page | page `22` |
| Table 1 — cross-references (not headings) | pages `2`, `6`, `7`, `9` |
| Table 2 — cross-references (not headings) | pages `2`, `6`, `11` |
| Scanned scope | `404` characters across pages `21`–`22` |
| Characters on page `21` | `69` |
| Characters on page `22` | `334` |
| `text_layer_present` | `true` (document-wide) |

All six identifier patterns returned `count=0`, `unique=0`: `sclk_10digit`,
`long_integer_8_12`, `iso_datetime`, `doy_datetime`, `event_id_labelled`,
`cda_product_name`.

> **Zero matches is not evidence that identifiers are absent.** `69` and `334`
> characters are heading and caption only — the table bodies never extracted, the
> tables being image- or vector-rendered. "Not read" and "not present" imply
> opposite verdicts (`UNRESOLVED` vs `FAIL`) and this evidence cannot separate
> them.

**Observation, not repaired here** — the successful run's JSON has **no `status`
key at all**. The script sets `status` only on its failure path, so the file that
contains the real evidence is the one that does not say what it concluded.
A reader diffing the two files could mistake the absence for a downgrade. Fixing
that is a script change and belongs to a session doing script work, not to this
inventory.

### `reports/killtest2_findings.json`

| Branch | `status` field, verbatim | Real evidence? |
| --- | --- | --- |
| `main` | *file does not exist* | No |
| `claude/postberg-phosphate-reproduction-mg9sjt` | `"UNRESOLVED"` | **No — transport blocker only** |
| `claude/host-reachability-check-2nhjpc` | `"UNRESOLVED"` | **No — transport blocker only** |

**MECHANICAL FACT** — the two feature branches carry byte-identical
`killtest2_findings.json`; `2nhjpc` never modified it. Both record four keys —
`gate`, `archive_root`, `status`, `blocker` — with the blocker:

> `transport failure listing https://sbnarchive.psi.edu/pds3/cassini/cda/: ProxyError(MaxRetryError("HTTPSConnectionPool(host='sbnarchive.psi.edu', port=443): …`

**No COCDA volume has been downloaded on any branch.**
`reports/killtest2_trace.png` — the kill-test 2 gate artifact — is **absent from
all three branches**.

### No verdict is stamped anywhere

**MECHANICAL FACT** — `git diff b501baf 89ffa77 -- reports/killtest1.md
reports/killtest2.md` is empty. Both gate reports are byte-for-byte identical
across every branch that has them, and both still read `UNRESOLVED`.

---

## 3. Which branch holds the successful kill-test 1 run

# `claude/host-reachability-check-2nhjpc`

**MECHANICAL FACT** — it is the only branch whose `data/MANIFEST.md` contains a
data row:

| Field | Value |
| --- | --- |
| File | `data/paper/Postberg_2023_Nature618_Phosphates_Enceladus.pdf` |
| Size | `16669185` bytes |
| SHA256 | `9d9d21c5acbcac3f16c9acb85afc101cea3dc46743d125c66e03324985b0cabe` |
| Retrieved | `2026-08-10T04:32:10Z` |
| Source | `https://www.geo.fu-berlin.de/en/geol/fachrichtungen/planet/projects/habitat_oasis/_layout/Postberg_2023_Nature618_Phosphates_Enceladus.pdf` |

`mg9sjt` has no data rows; `main` has no manifest.

**`UNRESOLVED`** — that SHA256 has **not been independently verified**. It was
written by the session that performed the download; no second session has
re-fetched the bytes and recomputed the digest. The PDF is gitignored under
Rule 3, so it cannot be checked from the repository alone. This is a provenance
gap, not a discrepancy: nothing contradicts the value, and nothing yet confirms
it.

---

## 4. Do the branches conflict?

**They do not.** Stated plainly, since the answer could have gone either way.

**MECHANICAL FACT** — files changed since the merge base `b501baf`:

| File | `mg9sjt` | `2nhjpc` |
| --- | --- | --- |
| `reports/SESSION_LOG.md` | changed | changed |
| `data/MANIFEST.md` | — | changed |
| `reports/killtest1_findings.json` | — | changed |
| `src/killtest1_paper.py` | — | changed (`+51`, `−9` lines) |

`reports/SESSION_LOG.md` is the **only** file both branches touch.
`git merge-tree b501baf <mg9sjt> <2nhjpc>` emits **`0`** conflict markers: the two
edits land in disjoint regions of that file — `2nhjpc` inserts Sessions 002–003 at
the top, `mg9sjt` appends Session 001b at the bottom. Every other change is
single-sided and merges without contest.

**Ordering wrinkle after any merge, not a conflict.** The log declares "newest
session first." A clean merge yields the order 003, 002, 001, 001b — but 001b's
check-ins ran `04:58Z`–`13:54Z`, ending after Session 003. The Session 001b entry
already carries a note stating this and giving its true position. Renumbering or
reordering is a tidy-up for a later session; it changes no evidence.

---

## 5. Gate status

| Gate | Verdict | Blocking |
| --- | --- | --- |
| **Kill-test 1** — do the nine grains resolve to machine-readable identifiers? | **`UNRESOLVED`** | Table bodies are images; contents never read |
| **Kill-test 2** — parse a COCDA volume, extract one raw MS trace | **`UNRESOLVED`** | `sbnarchive.psi.edu` never reached from any session |

Kill-test 1 is the open gate. It is the go/no-go, and everything downstream stays
blocked until it returns `PASS`.
