# P014 recovery v9 audit

## 1–7. Preservation, hierarchy, mappings, and counts
- recovery_v9 has **178 rows**. All **169 recovery_v8 rows** are retained unchanged and all **5 P014 legacy rows** remain present.
- Exactly five primary conditions (`P014_MC_ASCAST`, `P014_MC_CR`, `P014_MC_A600`, `P014_MC_A650`, `P014_MC_A700`) and four correlated A600 children were added. Children are non-independent; tensile n=3 is aggregate metadata and creates no pseudo-replicates.
- Legacy rows map by DOI, processing state and annealing temperature to the five exact conditions. Exact rows replace them only for counting, preventing double counting.
- Independent / usable TRIP / usable TWIP / usable joint: **49/34/32/29 before → 49/30/28/25 after**.

## 8–18. Chemistry, processing, initial state, and tensile properties
- Chemistry is nominal Fe50Mn30Co10Cr10 at.% only; measured chemistry is NA. Processing preserves vacuum levitation melting under Ar, five melts, block cutting, room-temperature rolling from about 5 to 2.75 mm at about 0.05 mm/pass, and 600/650/700 C, 10 min, water-quenched anneals. The 45% reduction is explicitly `DERIVED_FROM_REPORTED_5_TO_2.75_MM_THICKNESS`.
- CR processing TRIP/TWIP is 1/1 but its later tensile targets remain NA/NA. Pre-test/annealing twins never establish tensile TWIP.
- EBSD initial FCC/HCP is 0.795/0.205, 0.739/0.261, 1/0, 0.999/0.001, and 1/0. A650 retains `TRACE_EBSD_HCP_CONFLICTS_WITH_SINGLE_FCC_TEXT_XRD` rather than erasing the modality conflict.
- Grain sizes +/- uncertainty are 28.03+/-5.12, 0.71+/-0.18, 0.79+/-0.30, 1.10+/-0.57, and 1.16+/-0.60 um. KAM values 0.04/0.80/0.85/0.39/0.30 deg retain direct EBSD-label status. GOS recrystallized fractions are A600 0.102, A650 0.658, A700 0.747; none is fabricated for as-cast/CR.
- Test temperature is raw `Not explicitly specified` and numeric Test_T_K is NA. Table 1 YS/UTS/fracture elongation means and +/- values are separate, `UNKNOWN_REPORTED_PM`, with n=3 and no individual replicate rows.

## 19–25. Targets, chronology, HDI, and gaps
- Only A600 is verified condition-level TRIP=1/TWIP=1 (also Slip=1 and HDI=1). As-cast, CR, A650 and A700 remain NA/NA.
- A600 chronology is initial 0 HCP with pre-existing twins but no TWIP target; 15% HCP=0.184, TRIP=1/TWIP=NA; 30% HCP=0.604 and fracture HCP=0.651, both TRIP=1/TWIP=1 with direct deformation-twin evidence. Early slip+TRIP evolves to TWIP/HDI/dislocation interaction while TRIP tends toward saturation.
- The HDI contribution 631.2 MPa is retained in the strengthening table as `CURRENT_PAPER_FIT_INTERCEPT/REPORTED_CONTRIBUTION` and a `POTENTIAL_TARGET_LEAKAGE_FEATURE`; the 689 MPa YS comparison is outcome-derived. M=3.06 and alpha=0.2 are model inputs; G=76 GPa and k=226 MPa/um^0.5 are reference inputs, not P014 measurements.
- P014 numeric SFE and DeltaG remain NA. Remaining P014 gaps are explicit tensile temperature, measured bulk chemistry, batch/replicate identities, individual replicate values, and the +/- statistic definition.

## 26–31. Completeness and remaining blockers
- Five conditions now have processing, phase, grain size, KAM, mechanics and uncertainty metadata; three annealed states add direct GOS fractions. This is descriptor recovery, not feature engineering.
- Remaining overall P1/P2 blockers are unresolved labels in P014 and other papers, small/imbalanced independent support, predictor leakage eligibility (especially post-loading HDI), computational/experimental separation, sparse descriptors/reference constants, and no final ML-ready target. No ML, derived alloy descriptors, plot digitization, or fabrication occurred.
