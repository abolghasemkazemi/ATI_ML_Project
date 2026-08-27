# Grouped Split Design V1 Audit

This is split design and feasibility analysis only. No model, transformed matrix, imputation, normalization, encoding, descriptor calculation, resampling, synthetic sample, or performance metric was produced.

## A. Independent experimental conditions

**51** replacement-aware independent experimental ML conditions.

## B. T1 usable

**32**: 27 positive, 5 negative.

## C. T2 usable

**30**: 24 positive, 6 negative.

## D. Joint usable

**27**: 00=1, 10=5, 01=4, 11=17.

## E. Target-positive groups

At the recommended strict-with-paper-fallback level: T1=12, T2=11.

## F. Target-negative groups

At the recommended strict-with-paper-fallback level: T1=4, T2=4. These are four papers for each target.

## G. Valid T1 split candidates

**3** unique M2-compatible train/validation partitions, all `VALID_LIMITED`; valid strategies: DETERMINISTIC_GROUPED_HOLDOUT.

## H. Valid T2 split candidates

**9** unique M2-compatible train/validation partitions, all `VALID_LIMITED`; valid strategies: DETERMINISTIC_GROUPED_HOLDOUT, GROUP_K_FOLD_K2, GROUP_K_FOLD_K4.

## I. LOPO feasibility for T1

**NOT_FEASIBLE** as a complete binary validation design; positive-only held-out papers lack validation negatives.

## J. LOPO feasibility for T2

**NOT_FEASIBLE** as a complete binary validation design; most papers are positive-only and P001 is negative-only.

## K. GroupKFold feasibility for T1

**TARGET-ROSTER FEASIBLE but M2-INCOMPATIBLE for k=2**; k=3, 4, and 5 are not target-roster feasible under the deterministic label-blind strict-group allocation. GroupKFold is therefore not the recommended T1 M2 design.

## L. GroupKFold feasibility for T2

**FEASIBLE_LIMITED for k=2 and k=4**; k=3 and k=5 are not feasible because a validation fold lacks negatives.

## M. Recommended grouping level

`Leakage_Group_Strict` with conservative `Paper_ID` fallback. It is the safest fully covered key and currently coincides with paper boundaries. Physical batch is unavailable for all 51 conditions and is never inferred.

## N. Recommended T1 validation design

Deterministic strict grouped holdout family; primary candidate `T1_GH_STRICT_01`, with the other retained candidates as allocation sensitivity checks.

## O. Recommended T2 validation design

Strict GroupKFold k=2 as primary; strict GroupKFold k=4 and deterministic grouped holdouts as secondary robustness designs.

## P. M2 complete-case class support

T1: 17 positive and 2 negative complete cases; negatives occur in 2 papers/strict groups. T2: 14 positive and 6 negative complete cases; negatives occur in 4 papers/strict groups. M2 therefore removes 3/5 T1 negatives but 0/6 T2 negatives.

## Q. Joint four-class feasibility

**`T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE`** because state 00 is a singleton and cannot be independently present on both sides.

## R. Multilabel future feasibility

**EXPLORATORY_ONLY / potentially supportable output-wise** using T1/T2-compatible strict grouped partitions. This does not validate four-state discrimination or state 00.

## S. Generalization levels currently supportable

G1 is exploratory interpolation only; G2 is valid-limited only for retained strict holdouts with zero exact unparsed source-alloy-family overlap; G3 is valid-limited through multi-paper grouped partitions, not universal LOPO. Exact-text separation is not chemically reconciled equivalence.

## T. Principal statistical limitation

Only 5 TRIP and 6 TWIP negatives occur in four strict groups each; M2 reduces TRIP negatives to two groups, and joint state 00 has one condition.

## U. Principal scientific limitation

Conditions are strongly paper/study/material dependent, 19 conditions need paper fallback hierarchy, all physical batches are unknown, and exact `Fe50Mn30Co10Cr10` source text spans P003/P011/P013/P014. Differently written but chemically equivalent cross-paper families remain unresolved because chemistry has not been reconciled.

## V. Exact next step

Predeclare `T1_GH_STRICT_01` for an exploratory T1 baseline and the complete T2 GroupKFold-k=2 design, then construct a source-preserving **untransformed** M2 condition table under `CHEMISTRY_SOURCE_POLICY_V1.md`, retaining `Composition_Source` and missingness. Do not train until that table and its split intersections pass a new provenance/leakage audit; targeted acquisition of independent negative material families remains the scientific priority.

## Input provenance (SHA-256)

- `data/processed/experimental_condition_index_v12.csv`: `2b4f9a3d1cc4e662c285b1621720d8a83819def9d74d58f76be1d1895c732467`
- `data/processed/master_19papers_recovery_v12_qc.csv`: `4dec9a87c0c3f0f38a4ff676681ae0bacf09d247e7136770baf2d1eb27928406`
- `data/schema/feature_schema_v1.csv`: `09291b1197eab6314cd851bef0baac5c4f9a86a0ff551af9f7bacfe0c2d380b7`
- `data/schema/feature_sets_v1.csv`: `d647bef447eb489eca307905fb2b23aed764aaff75a130d45d1c6faa1127a5a7`
- `data/schema/feature_priority_v1.csv`: `91e53822bf892a33d75ddb18ebce7f78e7e5483e15047f0375c6464fc9c10a9f`
- `data/schema/domain_manifest_v1.csv`: `3eb717e69666e6ae92bbe89972bfaf26e66e5887609c2a083f1f7803702976ef`
- `reports/FEATURE_SET_COVERAGE_V1.csv`: `112bdec1e4973765314d6e892fbe79e06627ee8ed9ca9f47c95dd1d4c53258a8`
- `reports/TARGET_FEATURE_AVAILABILITY_V1.csv`: `9edeace350d981d0f32705a501235e4b1f20d92e949d85de22e51877e5061112`
- `reports/PREDICTION_TIME_LEAKAGE_POLICY_V1.md`: `05286a6800cdc0cd45f3f5bd3bb5a2edd0bd41cd4ff5beec1388be98de9d3465`
- `reports/FEATURE_SCHEMA_V1_AUDIT.md`: `670d625d13075c677d273fa9e2022e40dcaa5ecd1f2022354acb336322c4664b`
- `reports/GLOBAL_DATASET_QC_V12.md`: `d81d0fe47f706435fdeb331a6e927b27e1b24f7c848ea7f20cbacfe5623046d0`

## Frozen safeguards

- Random row splitting is rejected.
- Group independence wins over exact stratification.
- P017 and every computational/stage/legacy/summary row are excluded.
- No class is merged; all labels and source scientific values are unchanged.
- No oversampling, undersampling, SMOTE, synthetic alloy, imputation, chemistry reconciliation, or model training occurred.
