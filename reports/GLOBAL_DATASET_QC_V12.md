# Global Dataset QC V12

## Scope and census

- Dataset: `master_19papers_recovery_v12_qc.csv`, generated from immutable recovery_v11.
- Total master rows: **192**; original 334-column scientific content is cell-preserved.
- Replacement-aware independent experimental conditions: **51**.
- Exact independent computational conditions: **12** (P017 only).
- QC roles: `{'EXPERIMENTAL_STAGE_CHILD': 71, 'EXPERIMENTAL_PRIMARY_CONDITION': 51, 'LEGACY_EXACT_REPLACED': 21, 'LEGACY_COMPUTATIONAL': 20, 'OTHER_REVIEW': 14, 'COMPUTATIONAL_PRIMARY_CONDITION': 12, 'LEGACY_COLLAPSED': 2, 'SUMMARY_SUPPORT': 1}`.
- P0 issues: **0**; P1 issues: **26**.

## Experimental target distribution

- TRIP: 27 positive, 5 negative, 19 NA.
- TWIP: 24 positive, 6 negative, 21 NA.
- Joint: 00=1, 10=5, 01=4, 11=17; partially labelled=8; fully unlabeled=16.

## Integrity findings

No silent scientific correction was made. Stage observations, in-situ/longitudinal children, aggregate replicate metadata, legacy/exact representations, and computational records are excluded from the experimental condition index. The audit preserves NA != 0; intermediate-stage absence != condition-wide negative; annealing/initial twins != tensile TWIP; pre-existing/processing HCP != tensile TRIP; local != bulk chemistry; nominal != measured chemistry; method-specific SFE classes; and computational-native != experimental targets.

Unresolved target conditions remain:

| Paper_ID | Record_ID |
| --- | --- |
| P003 | P003_MC02 |
| P003 | P003_MC03 |
| P003 | P003_MC05 |
| P003 | P003_MC06 |
| P007 | P007_MC_A600_5h |
| P016 | P016_MC_400C_3min |
| P016 | P016_MC_400C_10min |
| P016 | P016_MC_650C_3min |
| P016 | P016_MC_650C_10min |
| P016 | P016_MC_750C_10min |
| P008 | P008_MC_N0_HOMO |
| P008 | P008_MC_N0_FC |
| P008 | P008_MC_N2p6_HOMO |
| P011 | P011_MC_A9_298K |
| P011 | P011_MC_A11_298K |
| P012 | P012_MC_BASE_RT |
| P012 | P012_MC_MO_RT |
| P012 | P012_MC_C_RT |
| P012 | P012_MC_BASE_77K |
| P012 | P012_MC_MO_77K |
| P014 | P014_MC_ASCAST |
| P014 | P014_MC_CR |
| P014 | P014_MC_A650 |
| P014 | P014_MC_A700 |

## Coverage and missingness

Lowest-coverage audited features/families:

| Feature_Name | NonMissing_Count | Missing_Count | Coverage_Percent |
| --- | --- | --- | --- |
| GOS | 0 | 51 | 0.0 |
| Loading_mode | 0 | 51 | 0.0 |
| True_stress_metrics | 2 | 49 | 3.92 |
| Other_initial_phases | 4 | 47 | 7.84 |
| KAM | 5 | 46 | 9.8 |
| Experimental_SFE | 6 | 45 | 11.76 |
| Recrystallized_fraction | 6 | 45 | 11.76 |
| DeltaG | 9 | 42 | 17.65 |

Experimental SFE coverage counts only source/reported experimental-equivalent SFE and excludes DFT, MD, CALPHAD/thermodynamic, assumed/reference, FCC/BCC GSFE distinctions. DeltaG remains method-specific calculated evidence; no values were back-calculated or transferred across papers.

## Provenance and source status

Exact condition provenance: `{'COMPLETE': 58, 'PARTIAL': 5}`. Gaps are reported, never fabricated. P018 and P019 remain **SOURCE_UNAVAILABLE_PENDING_REVIEW**; their legacy computational rows are preserved but not promoted.

## Leakage audit

High-risk post-loading/model-derived fields include: HCP_fraction_at_condition, Twin_fraction_or_Sigma3, Postfracture_HCP_fraction, Effective_TRIP, Effective_TWIP, YS_MPa, UTS_MPa, Elongation_pct, Uniform_elongation_pct, Engineering_YS_MPa, Engineering_UTS_MPa, True_Yield_Stress_MPa, True_UTS_MPa, Fracture_Mode, HDI_Hardening, Critical_twin_stress_MPa, Critical_TRIP_stress_MPa. Mechanical properties remain outcomes/supporting metadata with `PREDICTOR_ELIGIBILITY_UNRESOLVED`. P017 MD fields are computational-only and cannot improve experimental coverage.

## Paper contribution

| Paper_ID | Independent_Experimental_Conditions | Independent_Computational_Conditions | Experimental_Stage_Children | Computational_Stage_Children | Usable_TRIP | Usable_TWIP | Usable_Joint | Source_Availability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P001 | 3 | 0 | 5 | 0 | 3 | 3 | 3 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P002 | 3 | 0 | 0 | 0 | 3 | 3 | 3 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P003 | 7 | 0 | 0 | 0 | 3 | 3 | 3 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P004 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P005 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P006 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P007 | 5 | 0 | 5 | 0 | 4 | 4 | 4 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P008 | 6 | 0 | 0 | 0 | 4 | 3 | 3 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P009 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P010 | 3 | 0 | 6 | 0 | 3 | 3 | 3 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P011 | 4 | 0 | 6 | 0 | 2 | 2 | 2 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P012 | 6 | 0 | 20 | 0 | 3 | 4 | 1 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P013 | 1 | 0 | 10 | 0 | 1 | 1 | 1 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P014 | 5 | 0 | 4 | 0 | 1 | 1 | 1 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P015 | 2 | 0 | 0 | 0 | 2 | 2 | 2 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P016 | 6 | 0 | 6 | 0 | 3 | 1 | 1 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P017 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE |
| P018 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | SOURCE_UNAVAILABLE_PENDING_REVIEW |
| P019 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | SOURCE_UNAVAILABLE_PENDING_REVIEW |

## Limitations and recommendation

Structurally, the dataset is ready for a controlled, leakage-aware feature-schema design because identities, domains, replacement gates, roles, target coverage, missingness, and provenance gaps are explicit. It is **not scientifically/statistically ready for final ML training**: support is only 51 dependent literature conditions; negatives are scarce; joint labels are fewer; paper/material-family dependence is strong; unresolved labels and sparse initial microstructure, experimental SFE, DeltaG, and measured chemistry remain; and predictor leakage policy is not finalized. TRIP has the largest usable count but this alone does not establish adequacy.

Recommended next phase: resolve the queued source-specific target and provenance gaps (beginning with the listed unresolved conditions and P018/P019 source acquisition), then define a frozen pre-test/test-condition-only candidate schema with paper/material-group validation rules before any modelling.
