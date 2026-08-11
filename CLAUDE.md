# enceladus-repro — Standing Rules

Independent reproduction of the phosphate detection reported in Postberg et al.
2023, *Nature* **618**, 489–493, from public Cassini CDA archive data. This
repository is the validation gate for an open reanalysis pipeline.

**The project's credibility lives in these rules, not in anyone's judgment.**
They are binding on every contributor, human or agent, in every session. When a
rule and a deadline conflict, the rule wins and the deadline slips.

---

## 1. Fail-closed

Never assert a scientific claim without **either** a source URL **or** a
computation reproducible from code committed in this repository.

If verification fails, cannot be completed, or is blocked, write
**`UNRESOLVED`** and state precisely what is missing. **Never guess.** Never
fill a gap with recollection, plausibility, or a value "from the literature"
that is not accompanied by its source.

A blocked verification is `UNRESOLVED`, not `FAIL`, and never `PASS`:

- **`PASS`** — the check ran and the criterion was met.
- **`FAIL`** — the check ran and the criterion was not met.
- **`UNRESOLVED`** — the check could not be run to completion, or the evidence
  was insufficient to decide.

An `UNRESOLVED` gate blocks everything downstream of it. Do not proceed past a
gate that has not returned `PASS`, and do not soften an `UNRESOLVED` into a
`PASS` because the remaining work looks obvious.

## 2. Every number carries units and provenance

No bare numbers anywhere — not in reports, code comments, commit messages, plot
axes, or table cells. Every quantity states its **unit** and where it came from:
a source URL with a locator (page/table/figure), or the script and commit that
computed it.

Every downloaded file gets its **URL + SHA256** logged in
[`data/MANIFEST.md`](data/MANIFEST.md), with the UTC retrieval timestamp. A file
that is not in the manifest is not evidence and must not be used to support a
claim.

## 3. Never commit raw archive data

Raw archive data stays out of git, permanently. `/data` is gitignored except for
`MANIFEST.md`.

Commit only: **code, manifests, small derived tables, plots, reports.**

Rationale beyond repo size: the archive is the authority on its own bytes. We
record how to re-fetch and how to verify (SHA256), so any reader can rebuild the
inputs from the primary source rather than trusting our copy.

## 4. Every session ends with a log entry

Every session writes or updates [`reports/SESSION_LOG.md`](reports/SESSION_LOG.md)
with:

- what was **attempted**,
- **PASS / FAIL / UNRESOLVED** per gate,
- **evidence links** (file paths, URLs, commit SHAs).

This is not optional and not deferred to "next session." A session that produced
nothing still logs that it produced nothing, and why.

## 5. Three claim types, always distinguished

All writing in this repository — reports, comments, commit messages, docstrings —
labels every substantive claim as exactly one of:

- **MECHANICAL FACT** — computed here, by committed code, from a manifested
  input. Cite the script and the artifact.
- **SOURCED CLAIM** — asserted by an external source. Cite the URL and the
  locator within it. The source is responsible for the claim; we are responsible
  for quoting it correctly.
- **HYPOTHESIS** — our own conjecture. Flag it as such. **State no confidence
  level**, numeric or verbal. Do not write "likely", "probably", "we expect", or
  a percentage. A hypothesis earns status only by becoming a MECHANICAL FACT or a
  SOURCED CLAIM.

Unlabeled prose is treated as a defect in review.

---

## Working practice

### Network and access

If a step is blocked by network policy, sandbox permissions, or credentials:
**stop that step and report exactly what needs to be enabled.** Do not work
around it — no alternate mirrors, no substituting a secondary source for a
primary one, no reconstructing blocked content from memory or from search
snippets. Record the block as `UNRESOLVED` with the verbatim error.

### Reproducibility

Every artifact in `/reports` must be regenerable by running committed code in
`/src` against manifested inputs. If you cannot name the command that produced a
file, it does not belong in the repository.

Scripts fail loudly. Prefer a hard error over a default value, an inferred path,
or a silent fallback — a guessed path that happens to work is still a guess.

### Scope discipline

The reproduction target is the specific claim under test. Do not extrapolate
from a reproduced result to the broader habitability argument; that is a
separate claim with separate evidence.

### Provenance of this file

**SOURCED CLAIM** — Target publication: Postberg, F. et al. "Detection of
phosphates originating from Enceladus's ocean." *Nature* **618**, 489–493 (2023).
DOI: [10.1038/s41586-023-05987-9](https://doi.org/10.1038/s41586-023-05987-9).
The DOI is recorded as the citation of record; it has **not** been dereferenced
and verified from within this repository (see
[`reports/killtest1.md`](reports/killtest1.md) for access status).
