# KILL-TEST 2 — Can we parse a COCDA volume and extract one raw MS trace?

## Verdict

# `UNRESOLVED`

**Reason: the PDS archive host is denied by this environment's network egress
policy.** No volume was downloaded, so the parsing gate was never exercised
against real data.

`reports/killtest2_trace.png` **does not exist**, and no placeholder has been
created in its place.

---

## The question

Can we download one small COCDA volume from the PSI PDS3 archive, parse its
event table with `pdr`, extract one raw MS (time-of-flight) signal, and plot it?

"Ugly is fine; parsed is the gate."

---

## What was attempted

**MECHANICAL FACT** — `src/killtest2_cda.py` was executed. It exited `2`
(`UNRESOLVED`) at the first step, listing the archive root. Machine-readable
evidence: [`killtest2_findings.json`](killtest2_findings.json).

Target: `https://sbnarchive.psi.edu/pds3/cassini/cda/`

### Verbatim error

```
transport failure listing https://sbnarchive.psi.edu/pds3/cassini/cda/:
ProxyError(MaxRetryError("HTTPSConnectionPool(host='sbnarchive.psi.edu', port=443):
Max retries exceeded with url: /pds3/cassini/cda/ (Caused by ProxyError('Unable to
connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))"))
```

Proxy status endpoint, independently:

```json
{
  "ts": "2026-08-10T02:23:25.005Z",
  "kind": "connect_rejected",
  "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
  "host": "sbnarchive.psi.edu:443"
}
```

Every PDS mirror probed is blocked too: `pds.nasa.gov`, `sbn.psi.edu`,
`pds-smallbodies.astro.umd.edu` — all `403` on `CONNECT`. There was no reachable
alternate source to be tempted by, and none would have been used without asking.

---

## The blocker is network only — the toolchain is proven

This matters for scoping the fix, so it was tested rather than assumed.

**MECHANICAL FACT** — `src/selftest_toolchain.py` builds a synthetic PDS3
label + fixed-width ASCII table, parses it with `pdr`, and renders a PNG:

```
SELFTEST PASS — pdr 1.4.4 parsed 32 rows,
columns=['SAMPLE_INDEX', 'AMPLITUDE']; matplotlib wrote 16322 bytes.
```

So `pdr` reads PDS3 labels correctly in this environment, and the plotting path
works end to end.

> **This self-test is NOT kill-test 2 and carries no scientific weight.** It
> touches no Cassini data and no archive content. It exists solely to separate
> *"`pdr` does not work here"* from *"the archive is unreachable"*. The answer is
> the latter. Kill-test 2 remains `UNRESOLVED` until it runs against the real
> PSI archive.

---

## What the committed script will do once unblocked

`src/killtest2_cda.py` is complete and needs no edits. It:

1. **Discovers** the volume layout by walking the directory listing — it does
   not hardcode a guessed path. Per **CLAUDE.md**, a guessed path that happens to
   work is still a guess.
2. Selects **exactly one** COCDA volume (`--volume` to override), so the whole
   archive is never pulled.
3. Fetches `index.tab` + `index.lbl` through
   `enceladus_repro.provenance.fetch`, which logs **URL + SHA256 + UTC timestamp**
   to `data/MANIFEST.md` automatically (Rule 2).
4. Parses the index with `pdr` and reports row count and column names.
5. Locates an MS/time-of-flight product from the index, size-capped at 50 MB.
6. Plots it to `reports/killtest2_trace.png` with **units on both axes**
   (sample index [dimensionless]; amplitude [instrument DN, uncalibrated]).

It distinguishes the two failure modes the gate cares about:

- unreachable archive → exit `2`, `UNRESOLVED`
- archive reachable but the product will not parse → exit `1`, **`FAIL`**

That second path is the real gate. It has not yet been reached.

---

## To resolve

1. Allowlist `sbnarchive.psi.edu` (see [`SESSION_LOG.md`](SESSION_LOG.md)).
2. Re-run:
   ```bash
   python src/killtest2_cda.py
   ```
3. Replace this verdict with `PASS` or `FAIL` from the actual outcome, and link
   `killtest2_trace.png` as evidence.
