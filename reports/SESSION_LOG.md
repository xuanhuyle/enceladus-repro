# Session Log

Per **CLAUDE.md Rule 4**, every session records what was attempted, PASS/FAIL/UNRESOLVED
per gate, and evidence links. Newest session first.

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
