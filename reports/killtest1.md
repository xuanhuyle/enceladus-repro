# KILL-TEST 1 — Do the nine phosphate-bearing grains resolve to machine-readable identifiers?

## Verdict

# `UNRESOLVED`

**Reason: the target document could not be retrieved. This environment's network
egress policy denies the host.** The question was never actually tested.

Under **CLAUDE.md Rule 1**, a check that could not be run to completion is
`UNRESOLVED` — not `FAIL`, and never `PASS`. This gate blocks everything
downstream of it.

---

## The question

Do the nine phosphate-bearing grains reported in Postberg et al. 2023 resolve to
machine-readable identifiers — spacecraft clock counts, CDA event IDs, or
equivalent keys — that can be matched against the PDS Cassini CDA archive?

This is a go/no-go gate. If the grains cannot be tied to specific archived
events, an independent reanalysis cannot start from the same measurements, and
the reproduction as scoped is not possible from public data alone.

### Adjudication criteria (for whoever re-runs this)

| Verdict | Condition |
| --- | --- |
| `PASS` | Extended Data Tables 1 and 2 are located **and** carry per-grain keys resolvable against the PDS CDA index. |
| `FAIL` | The tables are located and demonstrably carry **no** such keys. |
| `UNRESOLVED` | The tables could not be retrieved or read to completion. ← **current state** |

---

## What was attempted

**MECHANICAL FACT** — `src/killtest1_paper.py` was executed against the target
URL. It exited `2` (`UNRESOLVED`) without retrieving any bytes. Machine-readable
evidence: [`killtest1_findings.json`](killtest1_findings.json).

Target URL:

```
https://www.geo.fu-berlin.de/en/geol/fachrichtungen/planet/projects/habitat_oasis/_layout/Postberg_2023_Nature618_Phosphates_Enceladus.pdf
```

### Verbatim error

```
transport failure for https://www.geo.fu-berlin.de/.../Postberg_2023_Nature618_Phosphates_Enceladus.pdf:
ProxyError(MaxRetryError("HTTPSConnectionPool(host='www.geo.fu-berlin.de', port=443):
Max retries exceeded ... (Caused by ProxyError('Unable to connect to proxy',
OSError('Tunnel connection failed: 403 Forbidden')))"))
```

The egress proxy's own status endpoint independently records the denial:

```json
{
  "ts": "2026-08-10T02:23:22.787Z",
  "kind": "connect_rejected",
  "detail": "gateway answered 403 to CONNECT (policy denial or upstream failure)",
  "host": "www.geo.fu-berlin.de:443"
}
```

### The block is a policy denial, not a tooling fault

Three independent checks agree, which rules out the usual false causes:

1. **`curl`** → `curl: (56) CONNECT tunnel failed, response 403`
2. **`requests`** (via `src/killtest1_paper.py`) → `Tunnel connection failed: 403 Forbidden`
3. **The `WebFetch` tool**, which uses a different client stack →
   `{"error_type":"EGRESS_BLOCKED","domain":"www.geo.fu-berlin.de"}`

A 403 on `CONNECT` is refused at the policy layer, before TLS. This is not a
certificate problem, not a proxy misconfiguration, and not a transient outage.
Per the environment's proxy documentation, policy denials must be reported
rather than retried or routed around.

### No fallback was used, deliberately

Every alternative literature host was also probed and is **also blocked**:
`doi.org`, `www.nature.com`, `static-content.springer.com`, `arxiv.org`,
`europepmc.org`, `www.ncbi.nlm.nih.gov` — all `403` on `CONNECT`.

Had one been open, it would still not have been used without checking first:
substituting a secondary source for the primary one is exactly the kind of
quiet workaround **CLAUDE.md** forbids.

---

## What this report does **not** claim

This is the important part.

- **No claim is made about the contents of Extended Data Tables 1 and 2.** They
  have not been seen. Their existence, numbering, and structure remain unverified
  from within this repository.
- **No claim is made about whether the identifiers exist.** The question is open,
  not answered in the negative.
- **No claim is made about the paper's findings.** Nothing about phosphates,
  grain counts, or Enceladus's ocean has been verified here.

The citation in `CLAUDE.md` is recorded as a **SOURCED CLAIM** carried from the
project brief; its DOI has **not** been dereferenced from this environment.

---

## To resolve

1. Allowlist `www.geo.fu-berlin.de` (and, for the Nature-hosted supplementary
   files, `www.nature.com` + `static-content.springer.com` + `doi.org`).
   The exact request is in [`SESSION_LOG.md`](SESSION_LOG.md).
2. Re-run — the script is committed and needs no changes:
   ```bash
   python src/killtest1_paper.py
   ```
3. It writes evidence to `killtest1_findings.json`, scanning the Extended Data
   pages for six candidate identifier shapes (Cassini SCLK, long integers, ISO
   and DOY timestamps, labelled event IDs, CDA product names).
4. **Adjudicate this file by hand from that evidence.** The script deliberately
   does not stamp its own verdict, so that a regex which happens to match cannot
   promote itself into a `PASS`.

Because this gate is `UNRESOLVED`, **CLAUDE.md** Step 5 fires: a request to the
CDA team is drafted at [`draft_cda_email.md`](draft_cda_email.md) — **unsent**,
and explicitly contingent on this gate being re-run first.
