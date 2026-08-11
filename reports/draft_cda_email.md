# DRAFT — Email to the CDA team, Freie Universität Berlin

> # ⛔ DO NOT SEND YET
>
> This draft exists because **CLAUDE.md** Step 5 fires automatically when
> kill-test 1 is `FAIL` or `UNRESOLVED`. Kill-test 1 is currently `UNRESOLVED`.
>
> **But it is `UNRESOLVED` for an environmental reason, not a scientific one:**
> the paper PDF host is blocked by our network egress policy, so we have never
> seen Extended Data Tables 1 and 2. **The identifiers this email asks for may
> already be published in them.**
>
> Sending it now would ask a research group to hand-assemble information we have
> not yet checked is public. That wastes their time and signals we did not do our
> homework.
>
> **Precondition for sending — all three must hold:**
> 1. `www.geo.fu-berlin.de` (or another route to the paper + its Extended Data)
>    is allowlisted, and `python src/killtest1_paper.py` has actually run.
> 2. The Extended Data tables have been read, and the per-grain identifiers are
>    genuinely **absent** or genuinely **insufficient** to index the PDS archive.
> 3. The recipient address has been taken from the paper's corresponding-author
>    line or the group's public contact page — **not guessed.**
>
> **Recipient: `UNRESOLVED`.** No address is filled in below. We could not reach
> the group's web page or the paper to read one, and inventing a plausible
> address would violate Rule 1.
>
> If, after step 2, the identifiers **are** present in the Extended Data, delete
> this draft. It will have served its purpose by not being sent.

---

**To:** `<UNRESOLVED — take from the paper's corresponding-author line>`
**Cc:** `<CDA instrument team, if listed separately>`
**Subject:** Request: per-event identifiers for the nine phosphate-bearing grains (Postberg et al. 2023)

---

Dear Professor Postberg and colleagues,

I am working on an open, independent reanalysis of Cassini CDA data, using your
2023 detection of phosphates in Enceladus's ejecta (*Nature* **618**, 489–493) as
the validation target: before the pipeline is used for anything new, it has to
reproduce a known result from the public archive.

I have been unable to map the nine phosphate-bearing grains onto specific events
in the PDS CDA archive at PSI. `<CONFIRM BEFORE SENDING: state here exactly what
you did read and what was missing from it — e.g. "Extended Data Tables 1 and 2
identify the grains within the paper, but I could not find a key that resolves
them to archived records." Do not assert this until you have actually read those
tables; see precondition 2 above.>`

Would you be willing to share, for each of the nine grains, whichever of these
you already have on hand:

1. the **spacecraft clock count** (or UTC event time) of the impact event;
2. the **CDA event ID** or equivalent internal identifier;
3. the **PDS volume and product name** of the corresponding MS spectrum, if the
   spectra used in the paper are archived.

Anything that lets me select the same events from the archive would be enough —
I am not asking for reduced or unpublished data, only for the pointers into the
public volumes. Whatever you send I would cite to you, and I would be glad to
share the resulting pipeline and its outputs with you before anything is posted
publicly.

If these identifiers are already published somewhere I have overlooked, a pointer
would be just as welcome and would save you the trouble.

Thank you for your time, and for placing the data in the public archive in the
first place.

With best regards,

`<name>`
`<affiliation, if any>`
`<contact>`
Project: `<repository URL>`

---

## Notes for the sender (not part of the email)

- **Kept short and specific on purpose.** It asks for three concrete fields for
  nine known objects, offers an escape hatch ("if this is already published"),
  and does not ask for unpublished or proprietary data. That is the version most
  likely to get a quick reply.
- **Fill in every `<...>` placeholder before sending.** They are deliberate. Do
  not let a template angle-bracket reach a real recipient.
- If no reply arrives, the fallback is to match grains to events by the
  observational circumstances given in the paper (encounter, date, ring/plume
  geometry) and to state plainly in the write-up that the mapping is **inferred
  and unconfirmed** — a **HYPOTHESIS** under Rule 5, carrying no stated
  confidence — rather than presenting it as the authors' own identification.
