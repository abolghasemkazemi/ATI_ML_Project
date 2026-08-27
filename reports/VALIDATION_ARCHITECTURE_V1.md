# Validation Architecture V1

## Outcome

Leakage-safe grouped train/validation partitions are feasible, but only as **limited** validation designs. No candidate qualifies as `VALID_STRONG`. The atomic unit is one replacement-aware independent experimental ML condition: 51 total, with 32 usable for T1 and 30 for T2. Stage children, legacy replacements, summaries, computational records, P017 MD conditions, and replicate-count metadata are excluded.

The recommended grouping control is **`Leakage_Group_Strict` with a conservative `Paper_ID` fallback**. Nineteen conditions lack explicit study/material leakage keys; all such same-paper conditions remain together. All 51 physical-batch IDs are missing, so no batch identity is inferred. In this dataset the effective strict groups coincide with paper boundaries.

An additional exact-source alloy-family audit uses unparsed source composition text (falling back to nominal text, material parent, source Alloy_ID, then paper). It identifies the exact `Fe50Mn30Co10Cr10` text across P003/P011/P013/P014. This is not chemistry reconciliation: it catches obvious equality only. GroupKFold remains a G3 unseen-paper design even when that exact family appears on both sides; the retained deterministic holdouts require zero exact-source family overlap for limited G2 use.

## Group support

- T1/TRIP: 27 positive and 5 negative conditions; negatives occur in 4 papers/effective strict groups.
- T2/TWIP: 24 positive and 6 negative conditions; negatives occur in 4 papers/effective strict groups. P001 supplies 3 of the 6 negatives.
- M2 complete T1: 17 positive and 2 negative conditions; the two negatives occur in only 2 strict groups.
- M2 complete T2: 14 positive and all 6 negative conditions; negatives remain in 4 strict groups.

The negative-class evidence audit copies every effective label unchanged. It grades only the consolidated evidence text: direct initial-to-final or explicit absence is strong, suppression/comparative wording is moderate, and nonspecific or uncopied evidence summaries are limited. One P008 negative retains an explicit consolidated-text gap; Split Design V1 generates no label from that gap and does not silently upgrade its evidence strength.

## Strategy feasibility

| Target   | Design                        | Grouping                                          |   Folds_or_Candidates | Validation_Positive_Range   | Validation_Negative_Range   | All_Folds_Both_Classes   | All_Folds_Zero_Strict_Overlap   | All_Folds_Zero_Exact_Source_Family_Overlap   | Feasibility   | Quality                                                        |
|:---------|:------------------------------|:--------------------------------------------------|----------------------:|:----------------------------|:----------------------------|:-------------------------|:--------------------------------|:---------------------------------------------|:--------------|:---------------------------------------------------------------|
| T1_TRIP  | LEAVE_ONE_PAPER_OUT           | Paper_ID                                          |                    12 | 1-4                         | 0-2                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T1_TRIP  | LEAVE_ONE_STUDY_SERIES_OUT    | Study_Series_ID_WITH_PAPER_FALLBACK               |                    12 | 1-4                         | 0-2                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T1_TRIP  | LEAVE_ONE_MATERIAL_FAMILY_OUT | Leakage_Group_Material_WITH_CONSERVATIVE_FALLBACK |                    17 | 0-4                         | 0-2                         | False                    | False                           | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT, INVALID_GROUP_LEAKAGE |
| T1_TRIP  | GROUP_K_FOLD_K2               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     2 | 12-15                       | 1-4                         | True                     | True                            | False                                        | FEASIBLE      | VALID_LIMITED                                                  |
| T1_TRIP  | GROUP_K_FOLD_K3               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     3 | 7-11                        | 0-4                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T1_TRIP  | GROUP_K_FOLD_K4               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     4 | 6-8                         | 0-2                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T1_TRIP  | GROUP_K_FOLD_K5               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     5 | 4-7                         | 0-3                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T1_TRIP  | DETERMINISTIC_GROUPED_HOLDOUT | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     1 | 5-5                         | 3-3                         | True                     | True                            | True                                         | FEASIBLE      | VALID_LIMITED                                                  |
| T1_TRIP  | DETERMINISTIC_GROUPED_HOLDOUT | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     1 | 6-6                         | 2-2                         | True                     | True                            | True                                         | FEASIBLE      | VALID_LIMITED                                                  |
| T1_TRIP  | DETERMINISTIC_GROUPED_HOLDOUT | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     1 | 6-6                         | 2-2                         | True                     | True                            | True                                         | FEASIBLE      | VALID_LIMITED                                                  |
| T2_TWIP  | LEAVE_ONE_PAPER_OUT           | Paper_ID                                          |                    12 | 0-4                         | 0-3                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T2_TWIP  | LEAVE_ONE_STUDY_SERIES_OUT    | Study_Series_ID_WITH_PAPER_FALLBACK               |                    12 | 0-4                         | 0-3                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T2_TWIP  | LEAVE_ONE_MATERIAL_FAMILY_OUT | Leakage_Group_Material_WITH_CONSERVATIVE_FALLBACK |                    17 | 0-3                         | 0-3                         | False                    | False                           | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT, INVALID_GROUP_LEAKAGE |
| T2_TWIP  | GROUP_K_FOLD_K2               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     2 | 11-13                       | 2-4                         | True                     | True                            | False                                        | FEASIBLE      | VALID_LIMITED                                                  |
| T2_TWIP  | GROUP_K_FOLD_K3               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     3 | 5-10                        | 0-5                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T2_TWIP  | GROUP_K_FOLD_K4               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     4 | 4-7                         | 1-3                         | True                     | True                            | False                                        | FEASIBLE      | VALID_LIMITED                                                  |
| T2_TWIP  | GROUP_K_FOLD_K5               | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     5 | 2-6                         | 0-4                         | False                    | True                            | False                                        | NOT_FEASIBLE  | EXPLORATORY_ONLY, INVALID_CLASS_SUPPORT                        |
| T2_TWIP  | DETERMINISTIC_GROUPED_HOLDOUT | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     1 | 7-7                         | 1-1                         | True                     | True                            | True                                         | FEASIBLE      | VALID_LIMITED                                                  |
| T2_TWIP  | DETERMINISTIC_GROUPED_HOLDOUT | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     1 | 4-4                         | 4-4                         | True                     | True                            | True                                         | FEASIBLE      | VALID_LIMITED                                                  |
| T2_TWIP  | DETERMINISTIC_GROUPED_HOLDOUT | Leakage_Group_Strict_WITH_PAPER_FALLBACK          |                     1 | 6-6                         | 2-2                         | True                     | True                            | True                                         | FEASIBLE      | VALID_LIMITED                                                  |

`FEASIBLE` means every fold has both classes in training and validation and has zero selected grouping-key, paper, study, reviewed material-parent, and strict-group overlap. The separate exact-source-family column determines whether a feasible G3 fold can also support a limited G2 interpretation. GroupKFold construction is label-blind and deterministic: groups are ordered by descending target-usable size and lexical ID, then assigned to the smallest fold. No seeds or label-driven seed search are used.

## Recommended T1 architecture

Primary: **the retained deterministic strict-grouped holdout family**, beginning with `T1_GH_STRICT_01`. The exhaustive, predeclared search retains three partitions with 18-35% validation size, two or three strict validation groups, both full-target classes on both sides, both raw M2-complete classes on both sides, and zero exact-source alloy-family overlap. This is `VALID_LIMITED`, not a performance-estimation guarantee: M2 has only one TRIP-negative complete case on each side of any admissible partition.

Standard label-blind GroupKFold k=2 is class-supported on the full 32-condition T1 roster, but it is **not M2-complete-case compatible**: one fold's M2 validation subset has no negative, while the complementary fold's M2 training subset has no negative. GroupKFold k=3, 4, and 5 fail full-roster class support in at least one validation fold. LOPO and leave-one-study-series-out are not complete binary-validation designs because most held-out groups are positive-only. Alternative retained grouped holdouts are the secondary robustness analysis.

## Recommended T2 architecture

Primary for G3 unseen-paper evaluation: **strict GroupKFold with k=2**. Both folds retain both classes, zero provenance-group overlap, and M2-complete positive/negative support. Exact-source alloy-family overlap means this is not a pure G2 design. Strict GroupKFold k=4 is also G3-feasible but secondary because each validation fold depends on only one negative-supporting paper. The retained deterministic grouped holdouts have zero exact-source family overlap and provide the limited G2 robustness view. GroupKFold k=3 and k=5 are not feasible because at least one validation fold lacks a negative.

## LOPO, repeated holdout, and nested CV

LOPO is **not feasible as a standalone binary cross-validation architecture** for either T1 or T2: many validation papers contain only positives, and P001's T2 fold contains only negatives. Per-paper folds may later be reported as exploratory stress tests, but they cannot replace a class-supported primary design.

Multiple deterministic grouped holdouts are justified for sensitivity to scarce group allocation. Stochastic "repeated holdout" and arbitrary seed hunting are not justified. Nested CV would be statistically excessive: it would repeatedly subdivide only 5/6 negatives and 4 negative-supporting strict groups, while M2 T1 has just 2 complete negatives.

## T3

T3A four-class prediction is **`T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE`**. State 00 has one independent condition, so it cannot occur in both training and validation. No class is merged or hidden.

T3B multilabel evaluation can be considered later only as `EXPLORATORY_ONLY`, using strict grouped partitions that preserve both binary outputs on both sides. This does not make four-state evaluation valid and does not provide independent validation support for state 00.

## Random row split rejection

Ordinary random row-level splitting is rejected. Conditions from the same paper, material parent, composition/alloy family, processing family, temperature series, or strain-rate series can share unmeasured study-specific information. Splitting those siblings across sides would allow memorization of related alloys or experimental practice and produce optimistic generalization estimates. Exact stratification never overrides group independence.

## No test split and no modelling

No three-way train/validation/test partition is created. With current support, reserving a third independent set would further fragment the minority classes. This architecture contains no algorithm selection, feature transformation, resampling, training, prediction, or performance metric.
