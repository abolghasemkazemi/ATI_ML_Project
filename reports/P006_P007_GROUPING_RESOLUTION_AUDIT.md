# P006/P007 grouping resolution audit

## Preservation

- recovery_v2 rows: **108**; recovery_v3 rows: **113**. All existing rows remain in their original order.
- Existing scientific/source cells are unchanged. Only the reviewed `ML_Condition_ID` metadata changes on eight parent rows; twenty additive hierarchy/property fields were introduced.
- Five workbook-backed P007 stage children were added. No ML was trained and no replicate or specimen was synthesized.

## 1. P006 final hierarchy

| Condition_ID   | Study_Series_ID   | Material_Parent_ID   | ML_Condition_ID   | Leakage_Group_Strict   | Physical_Batch_ID   | Replicate_ID   |
|:---------------|:------------------|:---------------------|:------------------|:-----------------------|:--------------------|:---------------|
| P006_C01       | P006_SERIES01     | P006_MAT_Ni20Fe20    | P006_MC_Ni20Fe20  | P006_SERIES01          | <NA>                | <NA>           |
| P006_C02       | P006_SERIES01     | P006_MAT_Ni15Fe15    | P006_MC_Ni15Fe15  | P006_SERIES01          | <NA>                | <NA>           |
| P006_C03       | P006_SERIES01     | P006_MAT_Ni15Fe10    | P006_MC_Ni15Fe10  | P006_SERIES01          | <NA>                | <NA>           |

## 2. P007 final hierarchy

| Condition_ID   | Study_Series_ID   | Material_Parent_ID   | ML_Condition_ID   | Leakage_Group_Strict   | Physical_Batch_ID   | Replicate_ID   |
|:---------------|:------------------|:---------------------|:------------------|:-----------------------|:--------------------|:---------------|
| P007_C01       | P007_SERIES01     | P007_MAT01           | P007_MC_A600_1h   | P007_SERIES01          | <NA>                | <NA>           |
| P007_C02       | P007_SERIES01     | P007_MAT01           | P007_MC_A600_2h   | P007_SERIES01          | <NA>                | <NA>           |
| P007_C03       | P007_SERIES01     | P007_MAT01           | P007_MC_A600_5h   | P007_SERIES01          | <NA>                | <NA>           |
| P007_C04       | P007_SERIES01     | P007_MAT01           | P007_MC_A600_10h  | P007_SERIES01          | <NA>                | <NA>           |
| P007_C05       | P007_SERIES01     | P007_MAT01           | P007_MC_A600_72h  | P007_SERIES01          | <NA>                | <NA>           |

## 3–6. Group and unknown-ID counts

| Audit | P006 | P007 |
|---|---:|---:|
| Material parents | 3 | 1 |
| Study series | 1 | 1 |
| Parent conditions with unknown physical batch | 3 | 5 |
| Parent conditions with unknown replicate ID | 3 | 5 |

## 7. Aggregate-property handling

P007 Table 3 is represented by separate `YS_mean`, `YS_uncertainty`, `UTS_mean`, `UTS_uncertainty`, `TE_mean`, `TE_uncertainty`, `UE_mean`, and `UE_uncertainty` fields. All five rows have `uncertainty_type=UNKNOWN_REPORTED_PM`; all `Replicate_n` values remain NA. The ± values created **zero** synthetic replicate rows.

## 8. Stage-child handling

| Observation_ID        | Parent_ML_Condition_ID   | ML_Condition_ID   | Observation_Role   | Leakage_Group_Strict   |
|:----------------------|:-------------------------|:------------------|:-------------------|:-----------------------|
| P007_OBS_A6001_eps20  | P007_MC_A600_1h          | P007_MC_A600_1h   | REPEATED_STAGE     | P007_SERIES01          |
| P007_OBS_A6002_eps20  | P007_MC_A600_2h          | P007_MC_A600_2h   | REPEATED_STAGE     | P007_SERIES01          |
| P007_OBS_A60010_eps20 | P007_MC_A600_10h         | P007_MC_A600_10h  | REPEATED_STAGE     | P007_SERIES01          |
| P007_OBS_A60072_eps10 | P007_MC_A600_72h         | P007_MC_A600_72h  | REPEATED_STAGE     | P007_SERIES01          |
| P007_OBS_A60072_eps20 | P007_MC_A600_72h         | P007_MC_A600_72h  | REPEATED_STAGE     | P007_SERIES01          |

All five are correlated `REPEATED_STAGE` children. Split assignment must use their parent `ML_Condition_ID` (or the stricter series group), so a child cannot cross folds independently of its parent.

## 9. Independent ML-condition counts before vs after

The P006/P007 identity strings comprised **8** unique legacy ML-condition IDs before resolution and **8** reviewed ML conditions after resolution (3 P006 + 5 P007). The five new stage rows add **0** independent ML conditions.

## 10. Leakage risks before vs after

Before: parent/material/study/batch/replicate concepts were not separately represented, P007 sibling conditions could be split without a shared material key, and the interrupted stages were absent. After: strict study groups, material parents, distinct ML conditions, explicit unknown batch/replicate fields, and child-to-parent linkage are separate. Residual risk is controlled—not erased—because physical batch and replicate metadata remain genuinely unknown.

## 11. Remaining unresolved P1 issues

P006/P007 parent-linkage is **resolved at the material/study hierarchy level** and can leave the P1 blocker list. Unknown `Physical_Batch_ID`, `Replicate_ID`, P007 Table 3 replicate count, and ± statistic type remain metadata limitations, not hierarchy blockers. Other P1 issues remain: P007 A600-5 target review, broader target ambiguity, computational-domain separation, small/imbalanced support, empty descriptor reference constants, feature-leakage eligibility, and final target selection. No ML was trained.
