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
| `data/paper/Postberg_2023_Nature618_Phosphates_Enceladus.pdf` | 16669185 bytes | `9d9d21c5acbcac3f16c9acb85afc101cea3dc46743d125c66e03324985b0cabe` | 2026-08-10T04:32:10Z | https://www.geo.fu-berlin.de/en/geol/fachrichtungen/planet/projects/habitat_oasis/_layout/Postberg_2023_Nature618_Phosphates_Enceladus.pdf | Postberg et al. 2023 Nature 618, 489-493 (kill-test 1 target) |

---

## Status

**One file retrieved** (Session 003): the kill-test 1 target PDF, row above.
Retrieved by `src/killtest1_paper.py` via `src/enceladus_repro/provenance.py`,
which appended the row automatically. Re-fetching identical bytes is idempotent
and does not duplicate the row.

The file itself is **not committed**, per Rule 3 — `.gitignore` covers `data/*`
except this manifest. Rebuild it by re-running the script, or by fetching the
URL above and checking the bytes against the recorded SHA256.

**Kill-test 2's source has not been fetched.** `sbnarchive.psi.edu` answered a
`HEAD` on its host root in Session 002, but no COCDA volume has been downloaded
and no manifest row exists for one. See
[`reports/killtest2.md`](../reports/killtest2.md), still `UNRESOLVED`.
