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
| `data/nature/s41586-023-05987-9_table4.html` | 165740 bytes | `39b92932900c44253906ce3f15157275fb3e2439afee6daa57156fe94c8c598f` | 2026-08-11T18:04:26Z | https://www.nature.com/articles/s41586-023-05987-9/tables/4 | Nature Extended Data Table 4 page for doi 10.1038/s41586-023-05987-9 (kill-test 1) |
| `data/nature/s41586-023-05987-9_table3.html` | 165657 bytes | `b163da1fe92b04d1d4e60b92e88e85aca0f26bcc3892289e5b80eafc8d76eb86` | 2026-08-11T18:04:23Z | https://www.nature.com/articles/s41586-023-05987-9/tables/3 | Nature Extended Data Table 3 page for doi 10.1038/s41586-023-05987-9 (kill-test 1) |
| `data/nature/s41586-023-05987-9_table2.html` | 165375 bytes | `838648eed2afde3c4e6bf02fa4fbb215e356cfef0db31803efcfb8dee9375427` | 2026-08-11T18:04:20Z | https://www.nature.com/articles/s41586-023-05987-9/tables/2 | Nature Extended Data Table 2 page for doi 10.1038/s41586-023-05987-9 (kill-test 1) |
| `data/nature/s41586-023-05987-9_table1.html` | 164902 bytes | `b3f3050c9b62aa637464f4285f2330d6a96d2914b86be69ff1c1c8a7c7fbd3eb` | 2026-08-11T18:04:17Z | https://www.nature.com/articles/s41586-023-05987-9/tables/1 | Nature Extended Data Table 1 page for doi 10.1038/s41586-023-05987-9 (kill-test 1) |
| `data/nature/s41586-023-05987-9_landing.html` | 500808 bytes | `25718ed64b20b962b8ae2f466a2e5df2df0c7d7171eaad124c52f35f7050ef45` | 2026-08-11T17:40:30Z | https://www.nature.com/articles/s41586-023-05987-9 | Nature article landing page for doi 10.1038/s41586-023-05987-9 (gate 1 supplementary availability) |
| `data/nature/s41586-023-05987-9_landing.html` | 500802 bytes | `639dcdadbf902e89c5283423bff3733da80019f37fe6094c042efcaca0323627` | 2026-08-11T17:39:15Z | https://www.nature.com/articles/s41586-023-05987-9 | Nature article landing page for doi 10.1038/s41586-023-05987-9 (gate 1 supplementary availability) |
| `data/cda/COCDA_0101/MP_02860426.TAB` | 19342 bytes | `069af06e5cb9862fe4d2b4edc9a36745cda47a715e0a500d45af90d231a89274` | 2026-08-11T17:38:46Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/DATA/MPSIGNALS_17181_17258/MP_02860426.TAB | COCDA_0101 MS data file accompanying MP_02860426.LBL for kill-test 2 |
| `data/cda/COCDA_0101/MP_02860426.LBL` | 4560 bytes | `2e344b3a2e4484b883f613c19c31c56420a2cdcb1524e8f5f75d72cfae74a33a` | 2026-08-11T17:38:44Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/DATA/MPSIGNALS_17181_17258/MP_02860426.LBL | COCDA_0101 raw MS (time-of-flight) product for kill-test 2 |
| `data/cda/COCDA_0101/index/index.tab` | 30704415 bytes | `184f8aee7e54433b7acfd4a3d4516bd70fbd2d0e18d3a8639b6bf949f883daba` | 2026-08-11T17:38:27Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/INDEX/INDEX.TAB | COCDA_0101 volume index (index.tab) for kill-test 2 |
| `data/cda/COCDA_0101/index/index.lbl` | 4640 bytes | `1b94a32cd956c7db5bd30c8ab54ce5635a390c0f79e7a4c7bf3aa2ec8710bdf2` | 2026-08-11T17:38:24Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/INDEX/INDEX.LBL | COCDA_0101 volume index (index.lbl) for kill-test 2 |
| `data/cda/DOCUMENT/CDA_SIS_1_0.TXT` | 251314 bytes | `c9e08012187c3c8d7c8c17bdef9a98790314d7c374aab1dccc07d22ba5f149ba` | 2026-08-11T17:34:43Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/DOCUMENT/CDA_SIS_1_0.TXT | CDA Software Interface Specification (archive primary documentation) |
| `data/cda/DOCUMENT/CDA_SIS_1_0.LBL` | 3840 bytes | `49ec02a98c08a2eeb26e44ca4847c55945ee12b2ccaae1b80917fb3093a0df9c` | 2026-08-11T17:34:42Z | https://sbnarchive.psi.edu/pds3/cassini/cda/COCDA_0101/DOCUMENT/CDA_SIS_1_0.LBL | CDA Software Interface Specification (archive primary documentation) |
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
