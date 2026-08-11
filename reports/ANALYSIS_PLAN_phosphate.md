# Pre-registered analysis plan — phosphate detection in CDA Type 3 spectra

**Status: PRE-REGISTRATION. No analysis has been run. No spectrum has been
fetched. No result exists.**

This document is committed **before** any MP signal product is downloaded, so
that the method cannot later be bent toward the expected answer. Every threshold,
tolerance and selection rule below is fixed at commit time. Changing any of them
after data is touched requires a new commit that states what changed, why, and
what the pre-change rule would have produced.

**Reproduction target — SOURCED CLAIM.** Postberg, F. et al. "Detection of
phosphates originating from Enceladus's ocean." *Nature* **618**, 489–493 (2023).
DOI [10.1038/s41586-023-05987-9](https://doi.org/10.1038/s41586-023-05987-9).

**Gate status at time of writing.** Kill-test 1 is `UNRESOLVED` and unadjudicated;
kill-test 2 is `PASS`. Per Rule 1 nothing downstream of kill-test 1 may proceed
until it returns `PASS`. **This plan is a document, not an execution**, and
running it is gated on that adjudication.

---

## 0. Instrument sources, and what is missing

| Source | Status |
| --- | --- |
| CDA Software Interface Specification, `CDA_SIS_1_0.TXT`, SHA256 `c9e08012187c3c8d7c8c17bdef9a98790314d7c374aab1dccc07d22ba5f149ba` | **Manifested and read.** Cited throughout as *SIS*. |
| CDA Data Handbook | **`UNRESOLVED` — no such document exists in the archive.** `DOCINFO.TXT` (SHA256 `cb4cd57d36a00c1161f6d7e7ea01fda441df0acce0faa5f51ef99ac1271e3838`) lists the `DOCUMENT/` directory contents in full: `DOCINFO.TXT` and `cda_sis_1_0` in `.doc`/`.pdf`/`.txt`/`.lbl`. There is no handbook to cite. |
| `SRAMAETAL2004B` (Srama et al. 2004b), cited *by* the SIS for event-class confirmation and CDA settings | **`UNRESOLVED` — not dereferenced from this repository.** |
| Postberg et al. 2009b, for Type 3 classification, target contamination and impact-speed effects | **`UNRESOLVED` — not dereferenced from this repository.** Carried below only as an attribution, never as a source of a number. |

**SIS §2.3.2, verbatim:** *"The calibration of the TOF mass spectrometer is still
preliminary. In order to determine the mass resolution as well as the instrument
characteristics, particles of known composition were shot in the Heidelberg dust
accelerator onto the flight spare unit."*

The SIS gives **no mass resolution figure, no stretch-factor value, and no
functional form for the mass scale.** Those gaps are registered in §6.

---

## 1. RECORD SELECTION

### 1.1 The problem, stated as fact

**MECHANICAL FACT** (Session 008, `reports/killtest1_findings.json`) — the nine
phosphate-bearing grains of Extended Data Table 2 each resolve to a PDS
`CDAEVENTS` record by UTC, but **the mapping is one-to-many**: each grain's
timestamp has between `1` and `5` candidate records within `2` s.

| Grain | Candidates within `2` s | Match offset |
| --- | --- | --- |
| 1 | `3` | `0` s |
| 2 | `5` | `0` s |
| 3 | `2` | `0` s |
| 4 | `2` | `0` s |
| 5 | `2` | `0` s |
| 6 | `1` | `1` s |
| 7 | `4` | `0` s |
| 8 | `3` | `1` s |
| 9 | `3` | `0` s |

A rule that picks exactly one record per grain must therefore be stated
mechanically and in advance.

### 1.2 Discriminators, and what each is worth

| Field | SIS definition, verbatim | Usable? |
| --- | --- | --- |
| `SPECTRUM_FLAG` | *"A flag indicating if there exists a corresponding mass spectrum for the particle (1) or not (0)."* | **Yes — primary.** Directly encodes the property required. |
| MP product presence | Existence of `MPSIGNALS_*/MP_<EVENT_ID>.LBL` under the volume | **Yes — secondary.** Independent of the flag; confirms the spectrum is actually delivered. |
| `EVENT_QUALITY` | *"The event class takes values between 0 and 4 … 0 - noise 1 - test pulse, 2 - small impact, 3 - strong impact, 4 - impacts with TOF mass spectrum). **Will be supplied in later delivery, when a reliable determination method will be available.**"* | **Conditional.** Value `4` is exactly the wanted class, but the SIS says it may not be populated, and separately that *"this flag value may be poorly reliable."* Used only as a tie-break, never as a filter. |
| `PARTICLE_SPEED` | *"The impact speed of the particle relative to the spacecraft… **Will be supplied in later delivery, when a reliable determination method will be available.**"* | **Weak — not used as a filter.** See §1.4. |
| `SPACECRAFT_SATURN_DISTANCE` | *"The distance from the spacecraft to Saturn in Saturnian radii."* | **Deliberately excluded.** See §1.5. |

### 1.3 ⚠ "Type 3" is not `EVENT_QUALITY == 3`

**HYPOTHESIS-blocking trap, stated now so it cannot be walked into later.** The
paper's "Type 3" is a **spectral classification** of E-ring grain composition.
`EVENT_QUALITY == 3` is the SIS's on-board **quality** class, meaning *"strong
impact"*. They are different taxonomies that collide on the numeral `3`.

**The archive carries no Type 3 field.** Whether Type 3 membership can be
reconstructed from archive fields alone is **`UNRESOLVED`** and is not assumed
anywhere in this plan. Type 3 membership is taken only from Extended Data Tables
1 and 2, which is where the paper asserts it.

### 1.4 Why impact speed is not a filter

Extended Data Table 2's own footnote, verbatim: *"Since the impact speed onto CDA
cannot be measured directly for these grains, the relative velocity of the
spacecraft to a circular Keplerian orbit provides a rough estimate."* The printed
column is a derived estimate, not a measurement, and the archive's
`PARTICLE_SPEED` may be unpopulated. Matching one estimate against a possibly
absent field would manufacture confidence. **Impact speed is recorded for every
candidate and reported, but never used to select.**

### 1.5 Why Saturn distance is not a filter

**MECHANICAL FACT** — for grains `2`, `4`, `5` and `6` the printed Saturn radial
distance disagrees with the archive's `SPACECRAFT_SATURN_DISTANCE` for the
resolved record by `0.55`, `0.17`, `0.13` and `0.13` R_S respectively (Session
008, flagged and uncorrected). Selecting on a column that is already known to
disagree would encode that disagreement into the sample. **Excluded from
selection; reported alongside every selected record.**

### 1.6 The selection rule, fixed now

Applied per grain, in order, and stopping at the first step that yields exactly
one record:

- **S1.** Candidate set = all `CDAEVENTS` records in the volume covering the
  grain's date whose `EVENT_TIME` is within `2.0` s of the printed UTC.
- **S2.** Retain only candidates with `SPECTRUM_FLAG == 1`.
- **S3.** If exactly one remains → **select it.**
- **S4.** Otherwise retain only candidates whose MP product file
  `MPSIGNALS_*/MP_<EVENT_ID>.LBL` exists in the volume. If exactly one
  remains → **select it.**
- **S5.** Otherwise retain only candidates with `EVENT_QUALITY == 4`, **if and
  only if** that field is populated for every remaining candidate. If exactly
  one remains → **select it.**
- **S6.** Otherwise select the candidate minimising `|Δt|` to the printed UTC,
  **provided that minimum is unique.**
- **S7.** If S6 leaves a tie → **abstain for that grain.** Do not pick
  arbitrarily. Carry **all** tied candidates forward and report every downstream
  quantity as a spread across them.
- **S8.** If S2 empties the set → **abstain for that grain**, record it
  `UNRESOLVED`, and do **not** fall back to a record lacking a spectrum.

**Pre-committed reporting.** The number of grains selected, and by which step
each was selected, is reported in full. If fewer than nine are selected, that is
stated in the headline result, not buried. A grain resolved only at S6 or S7 is
labelled as such wherever its spectrum contributes.

---

## 2. PROCESSING CHAIN

### 2.1 Input

**SOURCED CLAIM (SIS, verified Session 006)** — the MP signal table has exactly
two columns: `OFFSET_TIME` [`MICROSECONDS`], *"Flight time measured from
estimated time of impact"*, and `AMPLITUDE` [`MICROVOLTS`], *"Signal value
provided by the multiplier channel."*

### 2.2 Step 1 — time-of-flight to mass calibration

**⚠ `UNRESOLVED` — time origin conflict.** The SIS defines the MP table's
`OFFSET_TIME` as measured *"from estimated time of impact"*, while the
`CDASPECTRA` mass-scale anchors `SCALE_POS1` and `SCALE_POS2` are defined
[`SECOND`] *"from trigger time"*. **These are two different origins.** The SIS
gives no offset between them. This must be resolved, sourced, and committed
**before** any mass scale is computed. Until then the mass calibration cannot be
run, and the correct verdict is `UNRESOLVED`, not `FAIL`.

**Anchors, when the origin question is settled.** The archive supplies its own
mass-scale references in `CDASPECTRA`:

> `SCALE_ID` — *"Identifier flag showing how the mass scale was calculated. 0:
> from impact time only, 1: from impact time and first peak, 2: from two
> reference peaks."*
> `SCALE_POS1` / `SCALE_POS2` [`SECOND`] — *"Reference position (time) of
> first / second peak for mass scale calculation, in second from trigger time."*

- Use the archive's own `SCALE_POS1` and `SCALE_POS2` as the two reference
  positions, for grains where `SCALE_ID == 2`.
- For grains where `SCALE_ID < 2`, the archive did not derive a two-point scale.
  **Mark those grains `UNRESOLVED` and exclude them from co-addition**, reporting
  how many were excluded. Do not substitute a self-derived anchor.

**⚠ `UNRESOLVED` — functional form and stretch factor.** The standard TOF
relation is mass ∝ (flight time − t₀)², but **the SIS states neither the
functional form nor any stretch-factor value**, and no CDA Data Handbook exists
in the archive to supply them (§0). The exponent and the constant are therefore
**unsourced parameters**. They are registered in §6 and must be sourced — from
`SRAMAETAL2004B` or an equivalent primary instrument reference — and committed
before use. **An unsourced constant here is a decision surfaced now, not later.**

**⚠ Circularity guard, fixed now.** A reference line used to anchor the mass
scale **cannot** also serve as evidence for the success criterion. If the
archive's `SCALE_POS1`/`SCALE_POS2` correspond to lines at or within tolerance of
`23` u, `63` u, `125` u, `165` u, `187` u or `149` u, then that line is
**struck from the success criterion** for every grain so anchored, and the
striking is reported. The criterion is then evaluated on the remaining lines
only, and the reduction is stated in the headline result.

### 2.3 Step 2 — baseline correction

- **Method:** per spectrum, subtract a single constant equal to the **median**
  `AMPLITUDE` over the baseline window defined below. Median, not mean, so that
  a real ion peak intruding into the window cannot drag the baseline.
- **Baseline window:** the last `25` % of `OFFSET_TIME` samples in the record.
- **Noise scale:** σ_baseline = standard deviation of `AMPLITUDE` over that same
  window, in `MICROVOLTS`. Used by the detection threshold in §3.

**This window is an unsourced choice.** The SIS specifies no baseline procedure
and no quiet region. It is declared here, in advance, precisely so that it cannot
be tuned later; it is registered in §6.

### 2.4 Step 3 — normalisation

- Each baseline-corrected spectrum is divided by the **sum of its positive
  baseline-corrected amplitude** over the analysed mass range, giving unit total
  signal.
- **Not** normalised to the height of any single line. Normalising to Na⁺ at
  `23` u would make the `23` u criterion trivially true and would rescale every
  phosphate line by a quantity the criterion is supposed to test.

### 2.5 Step 4 — co-addition

- **Common grid:** each spectrum is resampled by linear interpolation onto a
  shared mass grid spanning `10` u to `220` u with spacing `0.1` u.
- **Combination:** arithmetic **mean** across the selected grains, computed
  per grid point over the grains contributing a finite value there.
- **Reported alongside:** the number of contributing grains per grid point, and
  the per-grid-point standard deviation across grains, so a feature carried by a
  single grain cannot masquerade as a property of the set.
- **Abstentions** (§1.6 S7/S8) and `SCALE_ID < 2` exclusions (§2.2) are excluded
  from the mean and reported by count and by grain number.
- **Also produced:** the nine (or fewer) individual calibrated spectra, so the
  co-added result can be checked against its inputs.

---

## 3. SUCCESS CRITERION — fixed now, before any data

### 3.1 Lines under test

**SOURCED CLAIM** — attributed to Postberg et al. 2023 as relayed in the
instruction for this plan. The DOI has not been dereferenced from this
repository, so these assignments are carried as the operator's citation.

| Mass [u] | Assignment | Required |
| --- | --- | --- |
| `23` | Na⁺ | **present** |
| `63` | (NaOH)Na⁺ | **present** |
| `125` | (NaPO₃)Na⁺ | **present** |
| `165` | (Na₂HPO₄)Na⁺ | **present** |
| `187` | (Na₃PO₄)Na⁺ | **present** |
| `149` | (Na₂HPO₃)Na⁺ | **absent** |

### 3.2 Mass tolerance

- **± `1.0` u** for lines at ≤ `100` u.
- **± `2.0` u** for lines at > `100` u.

**This tolerance is an unsourced choice.** The SIS gives no mass-resolution
figure and states the calibration is *"still preliminary"* (§0). The values are
fixed here in advance rather than fitted afterwards, and are registered in §6. If
a sourced mass resolution is later obtained, changing the tolerance requires a
new commit stating what the pre-change tolerance would have produced.

### 3.3 "Present", decided numerically

A line at nominal mass *m* is **present** when **both** hold within the tolerance
window around *m*:

1. There is a local maximum of the co-added, baseline-corrected, normalised
   spectrum inside the window; **and**
2. its amplitude ≥ `5.0` × σ_baseline, with σ_baseline propagated through the
   same normalisation and co-addition as the signal.

The threshold multiplier is **`5.0`**, fixed now.

### 3.4 "Absent", decided numerically

A line is **absent** when the **maximum** amplitude anywhere inside its tolerance
window is **< `5.0` × σ_baseline** — the identical test, failed.

**Asymmetry acknowledged:** "absent" under this definition means *not detected at
5σ*, which is weaker than *not there*. Where the `149` u window's maximum lies
between `3.0` σ and `5.0` σ, the `149` u result is reported as **`UNRESOLVED`
rather than absent**, and the overall criterion is `UNRESOLVED`. Below `3.0` σ it
is absent.

### 3.5 Overall

The criterion is **met** only when all five required lines are present **and**
`149` u is absent, both under the tests above. Any other outcome is reported
**per line**, never as a single collapsed verdict.

---

## 4. FAILURE MODES

### 4.1 Results meaning the pipeline is wrong, not the paper

Each of these is a **pipeline defect to debug**, and none may be reported as
evidence against the publication:

- **No peak at `23` u.** Na⁺ is the dominant line of these spectra. Its absence
  indicates a selection, calibration or baseline failure.
- **A non-monotonic or negative mass scale**, or peaks at masses outside the
  physical range of the analysed grid.
- **A co-added spectrum with fewer samples than its individual inputs**, or with
  contributing-grain counts of zero across a region under test.
- **Selected records whose MP product is missing**, or whose parsed sample count
  disagrees with the label's declared `ROWS` — the same declared-versus-parsed
  check that kill-test 2 used.
- **All lines present, including `149` u.** A spectrum in which every window
  fires is a threshold or baseline failure, not a discovery.

### 4.2 What would be `FAIL`

`FAIL` requires the pipeline's own sanity checks in §4.1 to **pass** — a sane
mass scale, Na⁺ present, inputs intact — **and** one or more of the four
phosphate-bearing lines (`63`, `125`, `165`, `187` u) to be absent, or `149` u
to be present, under the §3 tests.

### 4.3 What would be `UNRESOLVED`

- The time-origin conflict of §2.2 not yet resolved and sourced.
- The stretch factor and functional form of §2.2 still unsourced.
- Fewer than **`5`** of the nine grains yielding a usable calibrated spectrum
  after §1.6 abstentions and §2.2 exclusions. Between `5` and `8`, the analysis
  proceeds and the reduced N is stated in the headline result.
- `149` u falling in the `3.0`–`5.0` σ band (§3.4).
- Any archive fetch blocked by network policy — recorded verbatim, per the
  standing rule, with no substitute source.

**An `UNRESOLVED` outcome is never softened into a `FAIL`, and a `FAIL` is never
softened into `UNRESOLVED` because the result is unwelcome.**

---

## 5. KNOWN CAVEATS CARRIED FORWARD

1. **Four Saturn-distance disagreements.** Grains `2`, `4`, `5`, `6` resolve to
   records whose archive Saturn distance differs from the printed value by
   `0.55`, `0.17`, `0.13`, `0.13` R_S. **Flagged, uncorrected, and excluded from
   selection** (§1.5). If any of those four grains proves decisive to the
   outcome, that fact is reported explicitly.
2. **Timestamp → record is one-to-many** (§1.1). "Resolved" never means unique.
3. **CDA target contamination and impact-speed effects on spectral appearance.**
   Attributed to Postberg et al. 2009b by the operator's instruction.
   **`UNRESOLVED` — not dereferenced from this repository**, so no numerical
   correction derived from it appears in this plan. If contamination lines
   overlap any window in §3.1, that overlap must be sourced and committed before
   the criterion is evaluated.
4. **The instrument calibration is preliminary by the archive's own statement**
   (SIS §2.3.2, §0).
5. **`EVENT_QUALITY` and `PARTICLE_SPEED` may be unpopulated** — the SIS says
   both *"Will be supplied in later delivery"*. The plan does not depend on
   either.
6. **The event class flag *"may be poorly reliable"*** (SIS), and the SIS defers
   to `SRAMAETAL2004B`, which is not dereferenced here.
7. **No CDA Data Handbook exists in the archive** (§0). Every instrument-specific
   choice above is either cited to the SIS or registered as unsourced in §6.
8. **Kill-test 1 is `UNRESOLVED`.** This plan may not be executed until it
   returns `PASS`.

---

## 6. REGISTER OF UNSOURCED PARAMETERS

Surfaced now rather than discovered later. Each must either be sourced and
committed before use, or carried as a declared arbitrary choice with its effect
reported.

| # | Parameter | Value in this plan | Status |
| --- | --- | --- | --- |
| 1 | Mass-scale functional form (exponent) | none | **`UNRESOLVED` — must be sourced before any mass scale is computed** |
| 2 | Stretch factor / mass-scale constant | none | **`UNRESOLVED` — must be sourced** |
| 3 | Offset between "impact time" and "trigger time" origins | none | **`UNRESOLVED` — blocks §2.2** |
| 4 | CDA mass resolution m/Δm | none | **`UNRESOLVED` — the SIS gives no figure** |
| 5 | Mass tolerance | `±1.0` u ≤ `100` u; `±2.0` u > `100` u | **Declared arbitrary**, fixed pre-data |
| 6 | Baseline window | last `25` % of samples | **Declared arbitrary**, fixed pre-data |
| 7 | Detection threshold | `5.0` σ_baseline | **Declared arbitrary**, fixed pre-data |
| 8 | `149` u ambiguity band | `3.0`–`5.0` σ | **Declared arbitrary**, fixed pre-data |
| 9 | Co-addition grid | `10`–`220` u at `0.1` u | **Declared arbitrary**, fixed pre-data |
| 10 | Minimum usable grains | `5` of `9` | **Declared arbitrary**, fixed pre-data |
| 11 | Candidate time window | `2.0` s | Inherited from Session 008's observed match offsets; **declared**, not sourced |

Items 1–4 are **blocking**: the analysis cannot run to completion without them,
and attempting it anyway yields `UNRESOLVED`.

---

## 7. What running this plan will require

No code is written for this analysis yet, deliberately. When kill-test 1 returns
`PASS` and items 1–4 above are sourced, implementation proceeds as committed code
in `/src` against manifested inputs, and every artifact it produces must name the
command that produced it.
