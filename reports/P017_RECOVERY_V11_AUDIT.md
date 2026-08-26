# P017 recovery v11 audit

## 1–8. Rows, hierarchy, counts, and domain separation
- recovery_v11 total rows: **192**. All **180 recovery_v10 rows** are value/order preserved; **8 P017 legacy rows** remain. Twelve exact P017 computational conditions were identified and appended; exact independent computational count is **12**.
- Independent experimental conditions before/after: **51 → 51**. P017 contributes zero. Independent P017 computational conditions: **12**. Every exact row is `COMPUTATIONAL_MD`, `COMPUTATIONAL_CONDITION`, experimental-independent false, and target-ineligible; experimental splitting/class balance cannot include it.

## 9–17. Composition, state, grids, stresses, and native mechanisms
- Two parents retain molar-ratio formulas `Al0.5Cr1Co1Fe1Cu1Ni1` and `Al1.5Cr1Co1Fe1Cu1Ni1`; measured bulk chemistry and at.% normalization remain NA. Post-quench tensile states are BCC-dominant, never FCC. Al0.5 exact BCC fraction is NA; Al1.5 retains raw `>0.95` with approximate direct-text status, never numeric 0.95.
- At 1e10 s^-1 the temperature grid is 300/700/1000/1300 K for each alloy; at 300 K the rate grid is 1e10/1e9/1e8 s^-1. These extreme MD rates remain outside the experimental distribution.
- SIS-PSR / UTS-PSR (GPa), in workbook order: **[(5.0, None), (4.0, None), (3.4, None), (2.9, None), (3.7, 4.2), (3.6, 4.0), (2.1, 3.6), (1.5, 2.5), (1.3, 2.5), (1.1, 1.4), (2.0, 2.6), (2.0, 3.0)]**. Dedicated fields are used; experimental YS/UTS remain NA.
- Paper-native TRIP: **12 positive / 0 negative**. Paper-native TWIP: **8 positive / 4 negative**. These reversible BCC↔FCC(HCP/SF) and BCC-nanotwinning labels do not populate experimental targets. TWIP-induced TRIP is observed in **3** conditions; TRIP-induced TWIP in **8**.

## 18–23. PTM, GSFE, correlated sequences, and dislocations
- PTM HCP means `HCP_or_SF_atomic_fraction`, not automatically bulk epsilon martensite; no dense curve or atomic snapshot time series was digitized and no fraction was merged with EBSD/XRD.
- Structure-specific 0 K EAM values remain separate: FCC stable gamma_sf = **-14/-27 mJ m-2** (Al0.5/Al1.5); BCC unstable gamma_usf = **610/579 mJ m-2**. All are `CURRENT_PAPER_MD_CALCULATED`, `NOT_EXPERIMENTAL_SFE`.
- GSFE provenance retains 20 unit cells/direction; FCC x[11-2], y[111], z[1-10], a/6<112> on (111); BCC x[111], y[1-10], z[11-2], a/2<111> on a (110)-type plane; lateral x/z PBC.
- Five high-value Fig.20/21/24/25 sequences remain correlated, non-independent supporting records. They include Fig.20 TRIP-induced TWIP, the ISF→ESF and SF-interaction BCC-nucleation landmarks, Fig.24 TWIP-induced TRIP, and Fig.25 bidirectional coupling.
- Phase-specific Shockley partial, BCC perfect-dislocation, temperature/annihilation, Al1.5 defect-network, and rate/stress-transformation fluctuation findings are retained only as atomistic descriptors, never automatic pre-test predictors.

## 24–30. Legacy, leakage, target stability, and gaps
- Legacy mapping: **{'EXACT_CONDITION_MATCH_LEGACY_RETAINED_EXCLUDED_FROM_DOUBLE_COUNT': 4, 'LEGACY_COLLAPSED_COMPUTATIONAL': 4}**. Matching used DOI/alloy/temperature/rate, never row order. Legacy rows are retained; exact matches cannot double-count, and 600 K legacy representations absent from the verified grid are marked collapsed computational.
- Experimental usable TRIP/TWIP/joint counts before/after: **32/30/27 → 32/30/27** (unchanged). No P017 row enters experimental class balance or train/test splitting.
- Remaining P017 gaps: exact Al0.5 initial BCC fraction, experimental bulk chemistry, physical batch/replicate concepts (not applicable to MD), numeric undigitized phase/dislocation curves, and experimental-equivalent targets/SFE remain unavailable by design.
- Remaining global P1/P2 blockers: small/imbalanced independent experimental support, unresolved labels in other papers, enforced computational separation, sparse grain size/SFE/DeltaG/initial-phase descriptors, and predictor-leakage review. No ML, feature engineering, descriptor calculation, experimental fabrication, or curve digitization occurred.
