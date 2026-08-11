# enceladus-repro

Independent reproduction of the phosphate detection reported in **Postberg et al.
2023, *Nature* 618, 489–493**, from public Cassini CDA archive data — used as the
validation gate for an open reanalysis pipeline.

The pipeline has to reproduce a known result from the public archive before it is
trusted with anything new.

## Status

| Gate | Verdict |
| --- | --- |
| **Kill-test 1** — do the nine phosphate-bearing grains resolve to machine-readable identifiers? | **`UNRESOLVED`** — source host blocked by network policy |
| **Kill-test 2** — parse a COCDA volume and extract one raw MS trace | **`UNRESOLVED`** — archive host blocked by network policy |

Neither question has been tested. Both are blocked on network egress, not on the
code: the toolchain is verified working (`pdr` 1.4.4 parses PDS3 labels here).

**The allowlist request needed to unblock is in
[`reports/SESSION_LOG.md`](reports/SESSION_LOG.md).**

## Read this first

**[`CLAUDE.md`](CLAUDE.md)** holds the binding standing rules — fail-closed
verification, units and provenance on every number, no raw data in git, mandatory
session logging, and the MECHANICAL FACT / SOURCED CLAIM / HYPOTHESIS
distinction. They are binding on every contributor, human or agent.

The short version: **if it is not verified, it says `UNRESOLVED`.** Nothing in
this repository is allowed to rest on recollection or plausibility.

## Layout

```
CLAUDE.md                      standing rules (binding)
src/
  enceladus_repro/provenance.py  the only supported way to fetch into data/
  killtest1_paper.py             gate 1 — runnable, currently blocked
  killtest2_cda.py               gate 2 — runnable, currently blocked
  selftest_toolchain.py          toolchain check — NOT a science gate
data/
  MANIFEST.md                    URL + SHA256 of every retrieved file
  (everything else gitignored — raw archive data is never committed)
reports/
  killtest1.md, killtest2.md     gate verdicts with evidence
  draft_cda_email.md             drafted, UNSENT, contingent
  SESSION_LOG.md                 per-session record + allowlist request
notebooks/
```

## Running the gates

```bash
python -m venv .venv && ./.venv/bin/pip install -e .
./.venv/bin/python src/selftest_toolchain.py   # toolchain only, works offline
./.venv/bin/python src/killtest1_paper.py      # needs www.geo.fu-berlin.de
./.venv/bin/python src/killtest2_cda.py        # needs sbnarchive.psi.edu
```

Exit codes: `0` = PASS · `1` = FAIL (ran, criterion unmet) · `2` = UNRESOLVED
(could not run).

Kill-test 1 writes evidence to JSON but **does not stamp its own verdict** —
`reports/killtest1.md` is adjudicated by hand, so that a regex which happens to
match cannot promote itself into a `PASS`.
