# Split Design V2 Audit

## Selected partitions

| Target | Evidence_Pool | Design_ID | Strategy | Fold | Train_n | Test_n | Train_Positive_n | Train_Negative_n | Test_Positive_n | Test_Negative_n | Train_Group_n | Test_Group_n | Group_Overlap_n | Paper_Overlap_n | Material_Family_Overlap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T2_ANY_TWIP | ALL_VERIFIED_USABLE | T2_ANY_TWIP__ALL_VERIFIED_USABLE__GROUP_KFOLD_K3 | GROUP_KFOLD | 1 | 12 | 6 | 8 | 4 | 5 | 1 | 5 | 2 | 0 | 0 | FORMULA::FE50MN30CO10CR10 |
| T2_ANY_TWIP | ALL_VERIFIED_USABLE | T2_ANY_TWIP__ALL_VERIFIED_USABLE__GROUP_KFOLD_K3 | GROUP_KFOLD | 2 | 12 | 6 | 8 | 4 | 5 | 1 | 4 | 3 | 0 | 0 |  |
| T2_ANY_TWIP | ALL_VERIFIED_USABLE | T2_ANY_TWIP__ALL_VERIFIED_USABLE__GROUP_KFOLD_K3 | GROUP_KFOLD | 3 | 12 | 6 | 10 | 2 | 3 | 3 | 5 | 2 | 0 | 0 | FORMULA::FE50MN30CO10CR10 |
| T2_ANY_TWIP | STRICT_DIRECT_EVIDENCE_ONLY | T2_ANY_TWIP__STRICT_DIRECT_EVIDENCE_ONLY__GROUP_KFOLD_K3 | GROUP_KFOLD | 1 | 11 | 6 | 7 | 4 | 5 | 1 | 4 | 2 | 0 | 0 | FORMULA::FE50MN30CO10CR10 |
| T2_ANY_TWIP | STRICT_DIRECT_EVIDENCE_ONLY | T2_ANY_TWIP__STRICT_DIRECT_EVIDENCE_ONLY__GROUP_KFOLD_K3 | GROUP_KFOLD | 2 | 12 | 5 | 8 | 4 | 4 | 1 | 4 | 2 | 0 | 0 |  |
| T2_ANY_TWIP | STRICT_DIRECT_EVIDENCE_ONLY | T2_ANY_TWIP__STRICT_DIRECT_EVIDENCE_ONLY__GROUP_KFOLD_K3 | GROUP_KFOLD | 3 | 11 | 6 | 9 | 2 | 3 | 3 | 4 | 2 | 0 | 0 | FORMULA::FE50MN30CO10CR10 |

Every selected fold contains both classes, is complete-case M2, and has zero strict-group/paper overlap. Material-family overlap is reported. No random-row split, forced LOPO, or forced k=5 exists.

## Rejected/unsupported candidates

| Target | Evidence_Pool | Rejection_Reason | Candidate_Partition_n |
| --- | --- | --- | --- |
| T1_TRIP | ALL_VERIFIED_USABLE | ONLY_ONE_OR_ZERO_NEGATIVE_GROUPS | 1 |
| T1_TRIP | STRICT_DIRECT_EVIDENCE_ONLY | ONLY_ONE_OR_ZERO_NEGATIVE_GROUPS | 1 |
| T2_ANY_TWIP | ALL_VERIFIED_USABLE | ANOTHER_FOLD_LACKS_CLASS_SUPPORT | 5 |
| T2_ANY_TWIP | ALL_VERIFIED_USABLE | CLASS_SUPPORT_OR_GROUP_SEPARATION_FAILURE | 4 |
| T2_ANY_TWIP | STRICT_DIRECT_EVIDENCE_ONLY | ANOTHER_FOLD_LACKS_CLASS_SUPPORT | 5 |
| T2_ANY_TWIP | STRICT_DIRECT_EVIDENCE_ONLY | CLASS_SUPPORT_OR_GROUP_SEPARATION_FAILURE | 4 |
| T2_FCC_TWIP_STRICT | ALL_VERIFIED_USABLE | ONLY_ONE_OR_ZERO_POSITIVE_GROUPS | 1 |
