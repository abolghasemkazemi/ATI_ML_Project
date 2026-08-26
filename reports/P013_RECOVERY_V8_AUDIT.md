# P013 recovery v8 audit

## 1–7. Rows, hierarchy, mappings, and count impact
- Total recovery_v8 rows: **169**; all **163** recovery_v7 rows are byte-value/order preserved, including **5** P013 legacy rows.
- One exact independent condition (`P013_MC_ASCAST_RT`) and exactly five non-independent landmark children were appended. The four interval definitions exist only in the supporting table. All legacy rows are `LEGACY_COLLAPSED`, map scientifically to the exact condition, and are excluded from independent counting.
- Independent / usable TRIP / usable TWIP / usable joint counts: **48/33/31/28 before → 49/34/32/29 after**.

## 8–17. Initial state, mechanics, chronology, and mechanism scope
- Canonical initial bulk HCP is **~0.33**, by transmission SXRD Rietveld; EBSD/OM phase fraction is rejected because polishing can induce surface TRIP. It is explicitly thermal/pre-existing HCP, distinct from deformation-induced growth to **~0.77** at fracture. FCC is NA rather than an unsupported 0.67 complement; MnO ~0.01 is separate.
- Gamma-FCC grain size is **40.2 +/- 10.7 um**; plate-like HCP remains qualitative. Measured engineering YS/UTS/elongation are **319 MPa / 726 MPa / 36%**. SXRD TRIP onset ~250 MPa and final true stress ~950 MPa remain distinct.
- Chronology is elastic observable-bulk Stage I; TRIP+slip Stage II; epsilon-HCP tensile TWIP from ~530 MPa Stage III; epsilon-HCP compression TWIP from ~655 MPa Stage IV. Stage negatives never become condition negatives. Mechanism scope is gamma-FCC to epsilon-HCP TRIP and epsilon-HCP TWIP, not gamma-FCC twinning.

## 18–22. Physics and remaining P013 gaps
- Phase-specific gamma-FCC dislocation density (~1.4e14 to ~8.2e14 m^-2), HCP slip modes, phase load partitioning, phase-average elastic properties, reflection-specific moduli, lattice parameters, and strengthening terms are retained in the phase-physics table. Reflection and phase-average moduli are not interchangeable.
- Lattice friction 179 MPa remains `SECONDARY_REFERENCE_INPUT`; calculated YS 321 +/- 31 MPa remains `CURRENT_PAPER_CALCULATED`, separate from measured 319 MPa and flagged for later leakage review.
- P013 SFE and DeltaG remain NA. Other gaps are measured bulk chemistry, exact RT Kelvin, physical batch, tensile replicate count/identity, numeric HCP lath size, and undigitized intermediate SXRD quantities.

## 23–28. Target availability, leakage, and overall blockers
- Effective condition targets are verified TRIP=1/TWIP=1/Slip=1; original legacy targets remain untouched. The exact condition adds one usable joint condition and children add none.
- Leakage audit: strict/material groups are explicit; all stages share their parent, intervals and ten-image loading acquisitions are metadata only, final/mechanical/mechanism physics remain outcome fields requiring predictor-eligibility review, and legacy/exact representations cannot double-count.
- Remaining P1/P2 blockers: small/imbalanced independent support, other-paper target review, computational/experimental separation, prediction-time leakage, sparse grain/phase/SFE/DeltaG coverage, empty traceable descriptor constants, and no final ML-ready target. No ML, feature engineering, derived descriptor, normalization, digitization, or fabrication occurred.
