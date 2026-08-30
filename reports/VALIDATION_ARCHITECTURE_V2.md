# Validation Architecture V2

The task is pre-deformation experimental Effective_TRIP/TWIP prediction using complete-case M2 only. P017 remains computational-only. `Leakage_Group_Strict` is primary with `PAPER::<Paper_ID>` fallback; reported partitions require both classes and zero strict-group overlap. Paper, study, material-parent, and formula/alloy-family overlap are audited but never predictors.

| Target | Source_Negative_n | Source_Negative_Paper_n | Source_Negative_Strict_Group_n | M2_Negative_n | M2_Negative_Strict_Group_n | M2_Negative_Material_Family_n | Validation_Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1_TRIP | 4 | 3 | 3 | 1 | 1 | 1 | PILOT_NOT_VALIDATABLE_UNDER_CURRENT_M2 |
| T2_ANY_TWIP | 5 | 3 | 3 | 5 | 3 | 3 | VALID_GROUPED_PILOT |
| T2_FCC_TWIP_STRICT | 5 | 3 | 3 | 5 | 3 | 3 | PILOT_NOT_VALIDATABLE_UNDER_CURRENT_M2 |

`T2_ANY_TWIP` preserves every usable label. `T2_FCC_TWIP_STRICT` excludes HCP/epsilon and unresolved-positive semantics as NA rather than zero. Direct-evidence filtering is analysis-only. One-or-zero positive/negative-group targets are declared not validatable before fitting. This pilot is not publication-level validation.
