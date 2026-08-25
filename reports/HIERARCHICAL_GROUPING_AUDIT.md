# Hierarchical grouping audit

## Findings and redesign

The legacy `Experiment_Group_ID` was too coarse: it pooled different processing/test conditions and, in three groups, multiple deformation stages. Consequently, ten old groups appeared target-conflicted even when the rows described either distinct conditions or time-ordered mechanism activation. The redesign keeps paper provenance, assigns a conservative specimen/test parent, separates condition identity from row identity, and uses a stage ID only for linked deformation observations. No scientific value or TRIP/TWIP label was changed.

## Independence census

| Measure | Count |
|---|---:|
| Total observations | 98 |
| Experimental observations (including experimental observations in hybrid studies) | 72 |
| Computational observations (including computational roles in hybrid papers) | 26 |
| Hybrid-origin observations | 21 |
| Unresolved-origin observations | 0 |
| Unique Parent_Experiment_ID (all origins) | 82 |
| Unique experimental ML_Condition_ID | 55 |
| Repeated deformation-stage observations | 19 |
| Summary rows | 1 |
| Unresolved grouping cases | 11 |

## Target distributions

Mixed 0/1 stage series are represented as activation-positive at condition/parent level **and explicitly enumerated below**, rather than majority-voted or called conflicts.

### A. Observation level
| Target | 0 | 1 | unresolved |
|---|---:|---:|---:|
| TRIP | 17 | 71 | 10 |
| TWIP | 19 | 66 | 13 |

### B. Independent experimental ML-condition level
| Target | 0 | 1 | unresolved |
|---|---:|---:|---:|
| TRIP | 11 | 36 | 8 |
| TWIP | 11 | 33 | 11 |

### C. Experimental parent-experiment level
| Target | 0 | 1 | unresolved |
|---|---:|---:|---:|
| TRIP | 11 | 36 | 8 |
| TWIP | 11 | 33 | 11 |

Sequential stage-dependent groups are: **P001_G01, P004_G01, P005_G01**.

## Previous conflict resolution

- Previous conflicting groups: **10**.
- Artificial grouping conflicts resolved: **7**.
- Legitimate sequential-mechanism cases: **3**.
- Genuinely ambiguous target conflicts after regrouping: **0**.
- Conflict groups requiring original-paper grouping review: **1**.

The row-level grouping uncertainty is separate: **11 observations** in **P006, P007, and P016** need specimen/test linkage verification.

## Manual paper review

- Target labels/evidence: **P001, P002, P003, P004, P005, P006, P007, P008, P010, P011, P012, P013, P014, P015, P016, P017, P018**.
- Grouping: **P006, P007, P016**.
- Potential major-feature recovery (absence means only “not present in current extraction,” not “not reported”):
  - Grain_size: P006, P008, P009, P010, P011, P012, P013, P014, P015, P016, P017, P019
  - SFE: P004, P006, P007, P008, P009, P010, P011, P012, P013, P014, P016, P017, P018, P019
  - SFE_method: P004, P006, P007, P008, P009, P010, P011, P012, P013, P014, P016, P017, P018, P019
  - Initial_FCC_fraction: P008, P009, P010, P011, P012, P013, P014, P016, P017, P018, P019
  - Initial_HCP_fraction: P007, P008, P009, P010, P011, P012, P013, P014, P015, P016, P017, P018, P019
  - DeltaG: P001, P003, P004, P005, P007, P008, P009, P010, P011, P012, P013, P014, P015, P016, P017, P018, P019
  - Strain_rate: P005, P009, P018, P019
  - Test_temperature: P018
  - Processing_information: none
  - Mechanical_properties: P004, P005, P006, P009, P010, P013, P014, P017, P018, P019
  - TRIP_evidence: P004, P005
  - TWIP_evidence: none

## Usable condition counts and readiness

- Revised independent experimental ML conditions: **55**.
- TRIP-usable (nonmissing condition result): **47**.
- TWIP-usable: **44**.
- Joint TRIP/TWIP-usable: **44**.

These are label-availability counts, not proof of feature completeness or final eligibility. Pure computational rows are excluded; hybrid-paper rows count only where their observation role is experimental.

- **Final ML: NO.** Target evidence, 11 low-confidence grouping rows, sparse major descriptors, and small/imbalanced independent support remain unresolved.
- **Pilot ML: NO at present.** P1 label/grouping review should precede even exploratory performance estimates; pipeline-only dry runs remain acceptable but are not scientific ML results.
- **Targeted data expansion: YES.** Expansion should add genuinely independent, provenance-rich experimental conditions after existing-paper P1/P2 recovery, without resampling or synthetic data.
