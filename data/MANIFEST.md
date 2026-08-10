# Data Manifest

Provenance record for every file retrieved into `data/`, per **CLAUDE.md Rule 2**.

Raw archive data is **never committed** (Rule 3). This manifest plus the fetch
code in `src/` is what makes the inputs rebuildable: any reader can re-download
from the URL and verify the bytes against the recorded SHA256.

**A file that is not listed here is not evidence** and must not be used to
support a claim.

Rows are appended automatically by
[`src/enceladus_repro/provenance.py`](../src/enceladus_repro/provenance.py);
do not hand-edit them. Timestamps are UTC, at the moment of retrieval.

| File (repo-relative) | Size | SHA256 | Retrieved (UTC) | Source URL | Note |
| --- | --- | --- | --- | --- | --- |
<!-- MANIFEST-ROWS -->

---

## Status

**No files have been retrieved.** Both kill-test source hosts are blocked by
this environment's network egress policy, so no download has been attempted to
completion. See [`reports/killtest1.md`](../reports/killtest1.md) and
[`reports/killtest2.md`](../reports/killtest2.md) for the verbatim errors, and
[`reports/SESSION_LOG.md`](../reports/SESSION_LOG.md) for the allowlist request.

This empty table is the correct state, not an oversight: under Rule 1 an
unreachable source yields `UNRESOLVED` and no manifest row, rather than a
placeholder.
