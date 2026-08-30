# Controlled Pilot ML V1 Report

> This is a pipeline-sanity pilot, not publication-ready performance or evidence of reliable generalization to new HEAs.

1. Independent experimental conditions: **69**.
2. Usable labels: **TRIP 37; ANY-TWIP 36; joint 30**.
3. M2 complete cases: **TRIP 18; ANY-TWIP 18; FCC-strict 9**.
4. M2 classes: TRIP 17/1; ANY-TWIP 13/5; FCC-strict 4/5 positive/negative.
5. Negative strict groups: TRIP 1; ANY-TWIP 3; FCC-strict 3.
6. Valid primary design: `T2_ANY_TWIP__ALL_VERIFIED_USABLE__GROUP_KFOLD_K3`; unsupported targets are not forced.
7. Only balanced Logistic Regression beats the dummy on both mean MCC and balanced accuracy.
8. Positive-only collapse: M0_DUMMY_MOST_FREQUENT 3/3 folds; M1_LOGISTIC_BALANCED 2/3 folds; M2_RANDOM_FOREST_BALANCED 3/3 folds; M3_SVC_RBF_BALANCED 2/3 folds.
9. Negative-class recall is reported below for every fold/model; primary means are Dummy 0.000, Logistic 0.333, Random Forest 0.000, and SVC 0.000.
10. Primary mean MCC is Dummy 0.000, Logistic 0.211, Random Forest 0.000, and SVC -0.149.
11. Fold results are highly variable; means do not hide fold rows or min/median/max aggregates.
12. TRIP is `PILOT_NOT_VALIDATABLE_UNDER_CURRENT_M2` because one negative group survives.
13. ANY-TWIP has a mean above-dummy Logistic result, but it collapses in multiple folds and does not establish robust learnability.
14. FCC-only TWIP is `NOT_CURRENTLY_VALIDATABLE` because only one positive strict group survives.
15. Direct-only filtering removes one medium/author-attributed positive but does not materially change Logistic mean MCC (0.211 to 0.211); it does not resolve fold collapse or establish robustness.
16. Leakage assertions find zero forbidden predictors; preprocessing is fit inside each training fold.
17. The largest limitation is scarce, concentrated negative-group support after complete-case filtering.
18. Next collect direct condition-level TRIP/TWIP negatives with phase resolution, policy-valid Fe/Mn/Co/Cr chemistry, exact numeric test temperature/rate, distinct strict groups/material families, and before/after microscopy/diffraction. Add independent FCC-TWIP-positive groups for strict-phase validation.

## Primary mean diagnostics

| Model_ID | Balanced_Accuracy | MCC | Recall_Class_0 | Recall_Class_1 | Predicted_Positive_Fraction | Positive_Class_Collapse_Fold_n | Evaluated_Fold_n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M0_DUMMY_MOST_FREQUENT | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | 3 | 3 |
| M1_LOGISTIC_BALANCED | 0.6333333333333333 | 0.21081851067789195 | 0.3333333333333333 | 0.9333333333333332 | 0.8888888888888888 | 2 | 3 |
| M2_RANDOM_FOREST_BALANCED | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | 3 | 3 |
| M3_SVC_RBF_BALANCED | 0.4444444444444444 | -0.14907119849998599 | 0.0 | 0.8888888888888888 | 0.9444444444444445 | 2 | 3 |

## Primary fold diagnostics and confusion counts

| Fold | Model_ID | Test_Positive_n | Test_Negative_n | True_Negative_Count | False_Positive_Count | True_Positive_Count | False_Negative_Count | Balanced_Accuracy | MCC | Recall_Class_0 | Recall_Class_1 | Predicted_Positive_Fraction | Failure_Flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | M0_DUMMY_MOST_FREQUENT | 5.0 | 1.0 | 0.0 | 1.0 | 5.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 1 | M1_LOGISTIC_BALANCED | 5.0 | 1.0 | 1.0 | 0.0 | 4.0 | 1.0 | 0.9 | 0.6324555320336759 | 1.0 | 0.8 | 0.6666666666666666 | NONE |
| 1 | M2_RANDOM_FOREST_BALANCED | 5.0 | 1.0 | 0.0 | 1.0 | 5.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 1 | M3_SVC_RBF_BALANCED | 5.0 | 1.0 | 0.0 | 1.0 | 5.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 2 | M0_DUMMY_MOST_FREQUENT | 5.0 | 1.0 | 0.0 | 1.0 | 5.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 2 | M1_LOGISTIC_BALANCED | 5.0 | 1.0 | 0.0 | 1.0 | 5.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 2 | M2_RANDOM_FOREST_BALANCED | 5.0 | 1.0 | 0.0 | 1.0 | 5.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 2 | M3_SVC_RBF_BALANCED | 5.0 | 1.0 | 0.0 | 1.0 | 5.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 3 | M0_DUMMY_MOST_FREQUENT | 3.0 | 3.0 | 0.0 | 3.0 | 3.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 3 | M1_LOGISTIC_BALANCED | 3.0 | 3.0 | 0.0 | 3.0 | 3.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 3 | M2_RANDOM_FOREST_BALANCED | 3.0 | 3.0 | 0.0 | 3.0 | 3.0 | 0.0 | 0.5 | 0.0 | 0.0 | 1.0 | 1.0 | POSITIVE_CLASS_COLLAPSE |
| 3 | M3_SVC_RBF_BALANCED | 3.0 | 3.0 | 0.0 | 3.0 | 2.0 | 1.0 | 0.3333333333333333 | -0.4472135954999579 | 0.0 | 0.6666666666666666 | 0.8333333333333334 | NONE |

## Evidence sensitivity

| Target | Evidence_Pool | M2_n | Positive_n | Negative_n | Positive_Group_n | Negative_Group_n | Validation_Status | Selected_Design_ID | M0_DUMMY_MOST_FREQUENT_MCC_mean | M0_DUMMY_MOST_FREQUENT_Balanced_Accuracy_mean | M0_DUMMY_MOST_FREQUENT_Recall_Class_0_mean | M1_LOGISTIC_BALANCED_MCC_mean | M1_LOGISTIC_BALANCED_Balanced_Accuracy_mean | M1_LOGISTIC_BALANCED_Recall_Class_0_mean | M2_RANDOM_FOREST_BALANCED_MCC_mean | M2_RANDOM_FOREST_BALANCED_Balanced_Accuracy_mean | M2_RANDOM_FOREST_BALANCED_Recall_Class_0_mean | M3_SVC_RBF_BALANCED_MCC_mean | M3_SVC_RBF_BALANCED_Balanced_Accuracy_mean | M3_SVC_RBF_BALANCED_Recall_Class_0_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T2_ANY_TWIP | ALL_VERIFIED_USABLE | 18 | 13 | 5 | 6 | 3 | VALID | T2_ANY_TWIP__ALL_VERIFIED_USABLE__GROUP_KFOLD_K3 | 0.0 | 0.5 | 0.0 | 0.21081851067789195 | 0.6333333333333333 | 0.3333333333333333 | 0.0 | 0.5 | 0.0 | -0.14907119849998599 | 0.4444444444444444 | 0.0 |
| T2_ANY_TWIP | STRICT_DIRECT_EVIDENCE_ONLY | 17 | 12 | 5 | 5 | 3 | VALID | T2_ANY_TWIP__STRICT_DIRECT_EVIDENCE_ONLY__GROUP_KFOLD_K3 | 0.0 | 0.5 | 0.0 | 0.21081851067789195 | 0.6333333333333333 | 0.3333333333333333 | 0.0 | 0.5 | 0.0 | 0.0 | 0.5 | 0.0 |

The only above-dummy mean result is group/evidence-sensitive. Random Forest and the dummy collapse to positive in every primary fold. The pilot answers pipeline feasibility and exposes data gaps; it does not select a publication model.
