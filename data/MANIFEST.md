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
| `data/cda/COCDA_0101/index/INDEX.TAB` | 30704415 bytes | `184f8aee7e54433b7acfd4a3d4516bd70fbd2d0e18d3a8639b6bf949f883daba` | 2026-08-11T03:50:49Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/INDEX/CUMINDEX.TAB | COCDA_0101 cumulative index table (kill-test 2 survey) |
| `data/cda/COCDA_0101/index/cumindex.tab` | 30704415 bytes | `184f8aee7e54433b7acfd4a3d4516bd70fbd2d0e18d3a8639b6bf949f883daba` | 2026-08-11T03:50:21Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/INDEX/CUMINDEX.TAB | COCDA_0101 cumulative index table (kill-test 2 survey) |
| `data/cda/COCDA_0101/index/cumindex.lbl` | 4640 bytes | `1b94a32cd956c7db5bd30c8ab54ce5635a390c0f79e7a4c7bf3aa2ec8710bdf2` | 2026-08-11T03:50:19Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/INDEX/CUMINDEX.LBL | COCDA_0101 cumulative index label (kill-test 2 survey) |
| `data/cda/COCDA_0001/CDASPECTRA_99084_00100.TAB` | 602 bytes | `d11fe280600d7027c878fed5be990a908485577e9f35df2472359e762b69d196` | 2026-08-11T03:49:01Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0001/DATA/CDASPECTRA_99084_00100.TAB | COCDA_0001 MS data file accompanying CDASPECTRA_99084_00100.LBL for kill-test 2 |
| `data/cda/COCDA_0001/CDASPECTRA_99084_00100.LBL` | 68240 bytes | `b046ad0ff5a77bc0933e09da7da1a6b04bdb2e855370d305e55eb38941975a69` | 2026-08-11T03:45:13Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0001/DATA/CDASPECTRA_99084_00100.LBL | COCDA_0001 raw MS (time-of-flight) product for kill-test 2 |
| `data/cda/COCDA_0001/index/index.tab` | 2717925 bytes | `1f5e321ca2ef529e2685754344ac013f723fe8b62eb31185c63507c6070b4533` | 2026-08-11T03:43:23Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0001/INDEX/INDEX.TAB | COCDA_0001 volume index (index.tab) for kill-test 2 |
| `data/cda/COCDA_0001/index/index.lbl` | 4640 bytes | `cddf7f04e152ccc187b286c34f786b37d1259a361d0eec87976291a93ca21239` | 2026-08-11T03:43:22Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0001/INDEX/INDEX.LBL | COCDA_0001 volume index (index.lbl) for kill-test 2 |
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
