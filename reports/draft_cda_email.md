# DRAFT — Email to the CDA team, Freie Universität Berlin

> # ⛔ STILL UNSENT
>
> **CLAUDE.md** Step 5 keeps this draft alive while kill-test 1 is `FAIL` or
> `UNRESOLVED`. Kill-test 1 is **`UNRESOLVED`**.
>
> **The premise has narrowed since the first draft, and the ask is now much
> smaller.** We are no longer asking whether identifiers exist. We have the paper,
> we have located both Extended Data tables, and Extended Data Table 2 is titled
> as an event listing. What we do not have is their *contents*: the table bodies
> are rendered as images or vector graphics, so no text could be extracted from
> them.
>
> So the question is no longer "do these identifiers exist?" — it is "does a
> machine-readable form of these tables exist?"
>
> **Precondition for sending — all three must hold:**
>
> 1. **The Nature-hosted Extended Data has been checked first.** Nature is the
>    publisher of record, and a machine-readable version of these tables may
>    already be public there. Asking the authors to hand-assemble something the
>    publisher already distributes wastes their time and signals we did not look.
> 2. **OCR of the table images has been tried, or consciously ruled out.** If OCR
>    is used, every recovered identifier must be cross-checked against the archive
>    before it is relied on — an OCR error in a spacecraft clock count is silent.
> 3. **The recipient address has been taken from the paper's corresponding-author
>    line or the group's public contact page — not guessed.**
>
> **Recipient: `UNRESOLVED`.** No address is filled in below. Inventing a
> plausible one would violate Rule 1.
>
> If step 1 or step 2 yields the table contents, **delete this draft.** It will
> have served its purpose by not being sent.

---

**To:** `<UNRESOLVED — take from the paper's corresponding-author line>`
**Cc:** `<CDA instrument team, if listed separately>`
**Subject:** Machine-readable form of Extended Data Tables 1–2? (Postberg et al. 2023, phosphates at Enceladus)

---

Dear Professor Postberg and colleagues,

I am working on an open, independent reanalysis of Cassini CDA data, using your
2023 detection of phosphates in Enceladus's ejecta (*Nature* **618**, 489–493) as
the validation target: before the pipeline is used for anything new, it has to
reproduce a published result from the public archive.

I have the paper and have located Extended Data Tables 1 and 2. My problem is a
narrow and possibly trivial one: in the PDF I can access, both tables are
rendered as images rather than as text, so I can read their captions but not
their contents. I therefore cannot tell which archived CDA events the nine
phosphate-bearing grains correspond to.

Would you be willing to share whichever of these is easiest for you:

1. **A machine-readable form of Extended Data Tables 1 and 2** — a CSV, a
   spreadsheet, or simply a text-selectable PDF. This would be ideal, since it
   answers the question completely and costs you no assembly work.
2. Failing that, for each of the nine grains: the **spacecraft clock count** (or
   UTC event time), the **CDA event ID** or equivalent internal identifier, and
   the **PDS volume and product name** of the corresponding spectrum, if those
   spectra are archived.

I am not asking for unpublished or reduced data — only for the pointers that let
me select the same events from the public volumes. Anything you send I would cite
to you, and I would be glad to share the pipeline and its outputs with you before
anything is posted publicly.

If a machine-readable version is already published somewhere I have overlooked, a
pointer would be just as welcome and would save you the trouble entirely.

Thank you for your time, and for placing the data in the public archive in the
first place.

With best regards,

`<name>`
`<affiliation, if any>`
`<contact>`
Project: `<repository URL>`

---

## Notes for the sender (not part of the email)

- **What changed from the first draft, and why it matters.** The original asked
  whether per-event identifiers exist at all — a question we had no standing to
  ask, since at that point we had never seen the tables. We have now seen that
  they exist and that Table 2 is titled as an event listing. Asking a narrower
  question we genuinely cannot answer ourselves is both more honest and more
  likely to get a fast reply.
- **The first request is deliberately the cheapest one.** Re-exporting a table
  the authors already have is a two-minute task; hand-assembling nine rows of
  identifiers is not. Leading with the cheap ask respects their time and is more
  likely to succeed.
- **Every `<...>` placeholder must be filled before sending.** They are
  deliberate. Do not let a template angle-bracket reach a real recipient.
- **What this email must not claim.** Do not assert that the identifiers are
  missing from the published record. We know only that we could not extract them
  from the PDF we hold — a limitation of our copy and our method, not a
  demonstrated gap in the publication.
- **Fallback if no reply arrives.** Matching grains to events by the
  observational circumstances given in the paper (encounter, date, ring/plume
  geometry) would be a **HYPOTHESIS** under Rule 5, carrying no stated
  confidence. It must be labelled as inferred and unconfirmed in any write-up,
  never presented as the authors' own identification.
