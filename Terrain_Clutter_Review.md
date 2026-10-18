# Review of `Terrain_Clutter_36_Recommendations_Chatgpt.xlsx`

Nothing in this project held an earlier terrain/clutter matrix, so there was no prior
version of mine to diff against. I reviewed the ChatGPT file on its merits — structure
measured, content judged against RF practice — and wrote a corrected version in the same
36-row shape so the two sit side by side.

- Source file: `Terrain_Clutter_36_Recommendations_Chatgpt.xlsx` (2 sheets, 36 data rows)
- My version: `Terrain_Clutter_36_Recommendations_Claude.xlsx` (4 sheets; the full
  finding list with evidence is on the **Findings vs ChatGPT** sheet)

## What it gets right

The `Engineering Guidance` sheet is the better half of the file and is worth keeping
as-is: the RET sign-convention warning, "±1° is a conservative trial, not an
unconditional setting", the approval gate, "assess colocated carriers independently,
don't copy RET blindly", and "only change the specifically identified offending facing
neighbour". The conditional framing throughout — nothing is an unconditional
instruction — is the right posture for a tilt table.

## Measured structure

| Column | Distinct values across 36 rows |
|---|---|
| Source Recommendation | 14 |
| CO-sector Recommendation | **2** |
| Tier-1 Neighbours | **2** |
| Distinct (Source, CO, Tier-1) triples | 19 — 23 rows share a triple |

Source variants per terrain, across all six clutter classes: Flat 4, Rolling 2, Hilly 2,
Mountainous 2, Valley 2, Ridge 2.

All six `Special / Open Areas` rows repeat the `Rural – Low Vegetation / Open` text
verbatim in all four content columns. The 25-word boilerplate in `Remarks` appears in
36/36 rows and is 60% of that column's characters.

## The findings that change a network

**F10 — no MO unit (critical).** Ericsson `electricalAntennaTilt` (RetSubUnit /
RetDeviceData) is in **tenths of a degree**: "+1°" is `+10` in the MO. The file never
says so. This is the one error that silently produces a wrong change rather than a
debatable one.

**F12 — no AAS caveat (critical).** On massive-MIMO sectors the attribute may be absent
or inert; tilt there is a beam-set / digital-tilt choice. The sheet gives no way to tell
whether a row applies to the sector in front of you.

**F2 / F18 — the table is terrain-driven, not terrain × clutter.** Outside Flat, every
clutter class gets the same source text bar a dense-urban suffix. On Rolling, Hilly,
Mountainous and Valley, `Rural – High Vegetation / Forest` and `Dense Urban / Commercial`
receive effectively the same tilt advice. Those are near-opposite cases: dense urban
wants tight dominance and more downtilt; in forest, foliage loss dominates at the horizon
and tilt is a weak lever.

**F6 / F7 / F8 — the terrain axis mixes two dimensions.** Flat/Rolling/Hilly/Mountainous
are terrain *roughness*; Valley/Basin and Ridge are *site position within* terrain.
Collapsed into one axis, the highest-overshoot case in most networks — a ridge site in
mountainous terrain — has no row. It also leaves the Valley cell recommending both
−1° and +1° with no floor-vs-rim test, and the Rolling cell assuming a crest site when a
trough site needs the opposite action.

**F13 / F14 — the conditionals do no work.** Every recommendation hangs on "if overshoot
verified", and overshoot is never defined. There is no rollback threshold, soak period or
sample floor, so a change cannot be audited and a bad one is not caught.

**F9 — "±1°" is unanchored.** No antenna height, HBA, vertical beamwidth or target
distance. ±1° is ~15% of a 6.5° high-gain panel's VBW but ~7% of a 15° low-band panel's.

**F16 — tilt is presented as the only lever.** For a hole behind a ridge, RET cannot work
at all; azimuth, HBW, power, CIO/HO offsets, layer priority and new sectors are often the
correct and cheaper fix.

Also: F11 no band/layer dimension, F15 total tilt and RET stops unstated, F17 seasonality
observed but never acted on, F19 Flat × Forest advises uptilt where foliage, not pointing,
sets the edge.

## What my version does differently

Same 36 keys, so rows line up one-for-one. Twelve columns instead of seven:

- **Source** composed from an authored clutter action *and* an authored terrain
  qualifier, plus six hand-written overrides where composition would mislead
  (Ridge × Rural-Open as the explicit worst case, Valley × Special for over-water
  ducting, Mountainous × Forest where RET should not be spent at all, and three more).
  36 distinct source cells, 36 distinct triples.
- **Trigger** — the measured precondition: TA-derived serving-distance P95 > k × ISD
  (k = 1.2 dense urban / 1.5 urban-suburban / 2.0 rural), ≥7 days, ≥10k samples; weak
  edge = ≥5% of edge samples below −110 dBm with no better-ranked neighbour; plus a
  beyond-2×-ISD share test on exposed terrain.
- **Change size** — 0.25 × VBW cap per trial, with per-row deviations (no RET trial in
  forest; a permitted second step on ridge-over-open).
- **Verify / rollback** — named thresholds on edge RSRP P5, SINR, HO success,
  accessibility/retainability and PRB-normalised throughput, with soak lengths.
- **Better lever if tilt is the wrong tool** — per clutter and terrain.
- **Applicability check** — passive-RET vs AAS gate first, then height/VBW/mech-tilt/
  stops/band.
- **Remarks** carry only row-specific physics. The repeated policy moved to the
  Engineering Guidance sheet as named rules CS-1, VR-1, AG-1, AP-1, CB-1, so rows
  reference a rule and state only their deviation from it.
- **Inputs Required** sheet lists what must be recorded before any row applies, and which
  column each input blocks.

The six controls from the original Engineering Guidance sheet are all kept.

---

# Addendum — three-way comparison, after the Claude + Gemini file

`Terrain_Clutter_RF_Recommendation_Claude_Gemini.xlsx` turned up after the review above
was written. It is the strongest of the three files by a wide margin, and most of what I
flagged against the ChatGPT sheet it had already solved. The merged deliverable is
`Terrain_Clutter_RF_Recommendation_MERGED.xlsx` — that file verbatim, with eight columns
and two sheets appended and nothing removed.

## Where the Claude + Gemini file wins

- **Numeric deltas, not prose.** `+4°`/`0°`/`−2°` per cell, with a target EDT range in
  33/36 rows. A delta is a work order; a sentence is an opinion. It has only 8 distinct
  source values against ChatGPT's 14 — and carries far more information.
- **Clutter actually drives the answer, including sign flips.** Flat Dense Urban `+2°`
  downtilt, Flat Rural `−2°` uptilt, Flat Special `+3°` downtilt. The ChatGPT sheet never
  flips sign by clutter at all. This was my finding F2/F18 and it does not apply here.
- **Both failure modes in all 36 rows** — a dominant-issue branch plus an "if the
  opposite is observed instead" branch. This is the right structure: terrain and clutter
  predict the *likely* problem, not the actual one. Neither of my other two files does
  this, and it is the single best idea in any of the three.
- **`Special / Open Areas` defined and distinct in all six terrains**, reasoned correctly
  (no clutter loss → already overshooting → downtilt), which is the opposite of Gemini's
  uptilt. My findings F1 and F18 do not apply.
- **Concrete figures**: 0.7 × ISD beam-centre target, TA ≥90% within ~0.5 km, overlap
  >30%, RSRP ≥ −100 dBm, mechanical tilt as the fallback when EDT range is exhausted.
- **Site position handled** — Valley Suburban splits valley-floor from slope/rim sites
  with different values. My findings F7 and F8 do not apply.
- **An audit trail**: 28 conflicting cells colour-coded, a `Conflict Details` sheet
  adjudicating each, and 3 cells corrected in Gemini's favour. Neither other file shows
  its working.

## What still had to be added (8 new columns, J–Q)

Two gaps are in **both** files, including my own:

- **MO units (`MO-1`).** `electricalAntennaTilt` is in tenths of a degree on
  RetSubUnit / RetDeviceData — the `+4°` rows are `+40`. Neither file says so. Column J
  converts every row.
- **AAS gate (`AP-1`).** On massive-MIMO the attribute may be absent or inert; tilt is a
  beam-set / digital-tilt choice. The only "massive" in the file is "massive
  interference". Column M gates every row.

One is a finding **against** the Claude + Gemini file:

- **Step size contradicts its own Notes sheet (`ST-1`).** The Notes cap changes at 2° per
  iteration, but 14 rows carry `+3°` or `+4°` and **11 of those never say "in steps"**.
  A planner reading only the row would make a single move the Notes forbid. Column K
  states the staging for each affected row.

The rest complete what that file had started:

- **`VB-1`** step sized against vertical beamwidth — `+4°` on a 6–8° panel is 50–67% of
  the beamwidth. Mentioned once in the Ridge Dense Urban row, never applied as a rule.
- **`VR-1`** numeric revert thresholds. The file names the right KPIs and a 24–72 h wait
  but gives no threshold at which to undo the change. Uptilt rows are judged on what they
  cost the neighbours, not on the served cell's own RSRP gain.
- **`VR-2`** soak length by clutter — 24–72 h holds only where traffic is dense; rural
  needs 14 days, venues a full occupancy cycle, and a forest cell must not soak across a
  leaf-on/leaf-off transition.
- **`PC-1`** per-carrier application. Both files treat low band as a remedy to mention
  rather than the axis the table is applied along.
- **`CB-1`** change batching. The file argues exactly this when rejecting Gemini's
  cluster-wide change, but never promotes it to a rule the other 35 rows inherit.

## Ranking

1. **Claude + Gemini** — the only one of the three that is usable as a work instruction.
2. **My review build** (`..._Claude.xlsx`) — better gating, units and rollback discipline,
   but prose where the Claude + Gemini file has numbers.
3. **ChatGPT** — 2 distinct values in the co-sector column across 36 rows, 2 in tier-1,
   six rows duplicated verbatim, and 60% of the Remarks column one repeated sentence.

Verified on the merged file: columns A–I identical to the original in all 37 rows
including cell fills, `Legend` and `Conflict Details` untouched, `Notes` appended to only.
