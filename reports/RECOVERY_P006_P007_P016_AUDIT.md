# P006/P007/P016 Scientific Recovery Audit

## Scope and safeguards

All three workbook Paper_ID/DOI pairs matched the canonical records. The immutable workbooks were read only. The output retains all 98 observations and every original column/value; recovered data occupy parallel columns and the evidence ledger. No ML model was trained.

## Recovery results

- **Recovered value cells:** 63 (including already-present values retained as explicit verified comparisons).
- **Features recovered:** DeltaG_FCC_HCP_300K_J_mol, Elongation_pct, Grain_size_um, ISFE_DFT_0K_mJ_m2, Initial_FCC_fraction, Initial_HCP_fraction, Recrystallized_fraction, SFE_assumed_for_calculation_mJ_m2, TRIP, TWIP, UTS_MPa, Uniform_elongation_pct, YS_MPa.
- **Target labels newly made usable:** P006/P006_MC01 TRIP=0; P007/P007_MC04 TWIP=0; P007/P007_MC05 TWIP=1.
- **Unresolved labels remaining in reviewed papers:** P006/P006_MC01 TWIP, P006/P006_MC03 TWIP, P007/P007_MC03 TRIP and TWIP, and condition-specific P016 labels not explicitly mapped by the recovery.
- **Grouping uncertainties resolved:** condition identity for 3 P006 composition conditions and 5 P007 annealing-duration conditions; they remain separate ML conditions.
- **Grouping uncertainties remaining:** specimen/replicate parent linkage for P006/P007 and mapping P016's five recovered conditions plus sequential strain stages onto only three existing observations. These are explicitly marked `MANUAL_MAPPING_REVIEW`.

P006's intrinsic SFE is stored only as **DFT, 0 K** and its DeltaG only as **Thermo-Calc, 300 K**. P007 initial epsilon is a quench-induced starting fraction, not TRIP. P016's 18 mJ/m² is stored only as an assumed calculation input, never as experimental SFE; its unmapped sequential stages remain in manual review.

## Missingness (98-row observation basis)

| Feature family | Before | After |
|---|---:|---:|
| grain size | 55 (56.12%) | 52 (53.06%) |
| SFE | 74 (75.51%) | 69 (70.41%) |
| DeltaG | 91 (92.86%) | 91 (92.86%) |
| initial FCC fraction | 59 (60.20%) | 59 (60.20%) |
| initial HCP fraction | 66 (67.35%) | 61 (62.24%) |
| strain rate | 29 (29.59%) | 29 (29.59%) |
| test temperature | 13 (13.27%) | 13 (13.27%) |
| mechanical properties | 75 (76.53%) | 72 (73.47%) |

Method-specific SFE availability in the table counts separately preserved DFT/assumed values; it does not claim experimental room-temperature SFE coverage. Mechanical-property missingness means all four tracked property fields are absent.

## Usable labelled ML-condition availability

| Target availability | Before | After |
|---|---:|---:|
| TRIP | 47 | 48 |
| TWIP | 44 | 46 |
| joint TRIP/TWIP | 44 | 46 |

Counts are availability counts, not independent-sample or model-readiness claims. Existing labels take precedence; recovered values fill only missing availability for this audit and discrepancies remain review records.
