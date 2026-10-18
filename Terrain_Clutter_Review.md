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
