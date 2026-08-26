# P012 recovery v7 audit

## 1–6. Preservation and hierarchy
- recovery_v7 total rows: **163**. All **137** recovery_v6 rows and all six P012 legacy rows are retained unchanged in their original columns and order.
- Exactly six recovered P012 independent experimental conditions and **20** non-independent repeated-stage observations were added. The three material parents share strict leakage group `P012_SERIES01`; material leakage uses the parent IDs. Batch and tensile replicate IDs remain NA.
- All six legacy rows map exactly by composition and temperature, not row order, to the six replacements in `reports/tables/p012_recovery_v7_legacy_mapping.csv` and are excluded from duplicate independent counting.

## 7–14. Recovered descriptors
- Measured chemistry is primary and unnormalised; nominal chemistry is separate. In particular measured carbon **0.6 at.%** is distinct from nominal **0.5 at.%**.
- The solution-annealed initial state is qualitatively single-phase FCC; exact FCC fraction remains NA and direct HCP absence is 0.
- Initial Sigma3 fractions 0.381/0.528/0.567 are explicitly `ANNEALING_TWIN` and never target evidence. Grain size excluding twins (54/40/34 um) and including twins as HABs (28/26/23 um) remain separate.
- Six temperature-specific calculated SFE and DeltaG records retain their thermodynamic methods, status, interfacial energy, molar surface density, and provenance. They are not experimental measurements.
- RT mechanics are Base 140/398/98, Mo 191/484/~80, C 213/581/~80 (YS/UTS/TE). C-77 K is 510/1022/~110; Base/Mo cryogenic values remain NA and Fig.4 was not digitized.

## 15–17. Targets and chronology
- RT targets are TRIP NA/TWIP 1; Base-77 K and Mo-77 K are TRIP 1/TWIP NA; C-77 K is TRIP 1/TWIP 1. Slip is 1 for all six.
- Stage negatives remain stage-specific and never promote condition negatives. Carbon-77 K chronology explicitly preserves Slip+TWIP at 0.1 followed by TWIP+TRIP from 0.2 onward.

## 18–21. Count impact
| Metric | recovery_v6 | recovery_v7 |
|---|---:|---:|
| Independent experimental conditions | 42 | 48 |
| Usable TRIP | 30 | 33 |
| Usable TWIP | 27 | 31 |
| Usable joint labels | 27 | 28 |

## 22–24. Leakage, gaps, blockers
- Stages inherit the strict/material parent grouping and cannot become independent samples. XRD n=5 is lattice-parameter reliability only and creates neither tensile replicates nor rows.
- Missing P012 fields: physical batch, tensile replicate identity/count, exact Base/Mo 77 K mechanical properties, exact initial FCC fraction, and numerical lattice friction stress. The Mo early-stage Results/caption ambiguity is retained in the stage note.
- Remaining P1/P2 blockers: small/imbalanced independent support, unresolved target reviews in other papers, computational/experimental separation, prediction-time feature leakage, sparse grain/phase/SFE/DeltaG coverage, empty traceable descriptor constants, and no final ML-ready target. No ML, feature engineering, derived descriptor, normalization, pseudo-replication, figure digitization, or fabrication occurred.
