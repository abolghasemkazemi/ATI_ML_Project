# Data audit: 19-paper pre-Pilot dataset

> Generated non-destructively from the four supplied workbooks. No missing scientific value was imputed, estimated, normalised, or replaced by zero. No model was trained.

## Execution environment

The required pandas/openpyxl dependencies could not be installed because the package proxy returned HTTP 403. The standard-library OOXML fallback therefore generated the merged CSV, processed-feature CSV, QC CSV tables, and this report. The `.xlsx` merged/processed copies and matplotlib figures could not be generated in this environment; no substitute outputs or values are claimed for them.

## Dataset dimensions and separation

- **98 rows**, **19 papers**, **19 unique DOI values**, **98 unique Condition_ID values**, and **47 Experiment_Group_ID values**.
- **19 independent experimental groups**; **21 computational/model groups**. There are **29 unresolved-role rows**, which must be reviewed rather than assumed experimental.

## Labels

- Row-level TRIP: {'1': 71, '0': 17, 'NA': 10}
- Row-level TWIP: {'0': 19, '1': 66, 'NA': 13}
- Full row- and scientifically valid independent-experimental-group balances are in `reports/tables/data_quality_report.csv`. A group is reported as ambiguous where its rows disagree; computational groups are excluded from experimental group balance.

## QC findings

- Composition sums outside 100 +/- 1 at.%: **0 rows**.
- Rows participating in a duplicated Condition_ID: **0**.
- Papers with conflicting nonblank DOI values: **0**.
- Rows with missing or syntactically ambiguous TRIP/TWIP/mechanism labels: **62**.
- Rows with suspicious range/negative numeric values: **0**.
- Batches needing schema review: **2 of 4**. Exact differences, reviewed aliases, and preserved extras are listed in `schema_audit.csv`; per-row extras remain JSON in `Unmapped_Fields`.

## Candidate feature availability (ranked)

| Rank | Candidate feature | Available (%) | Missing (%) |
|---:|---|---:|---:|
| 1 | Fe_at% | 91.84 | 8.16 |
| 2 | Cr_at% | 91.84 | 8.16 |
| 3 | Co_at% | 89.80 | 10.20 |
| 4 | Mn_at% | 88.78 | 11.22 |
| 5 | Test_T_K | 86.73 | 13.27 |
| 6 | log10_strain_rate | 70.41 | 29.59 |
| 7 | Strain_rate_s-1 | 70.41 | 29.59 |
| 8 | Ni_at% | 47.96 | 52.04 |
| 9 | Grain_size_um | 43.88 | 56.12 |
| 10 | Cold_rolling_reduction_pct | 41.84 | 58.16 |
| 11 | Annealing_T_K | 41.84 | 58.16 |
| 12 | Homogenization_T_K | 40.82 | 59.18 |
| 13 | Annealing_time_min | 40.82 | 59.18 |
| 14 | Initial_FCC_fraction | 39.80 | 60.20 |
| 15 | Homogenization_time_h | 33.67 | 66.33 |
| 16 | Initial_HCP_fraction | 32.65 | 67.35 |
| 17 | SFE_mJ_m2 | 24.49 | 75.51 |
| 18 | YS_MPa | 21.43 | 78.57 |
| 19 | Hot_rolling_T_K | 21.43 | 78.57 |
| 20 | UTS_MPa | 18.37 | 81.63 |
| 21 | Hot_rolling_reduction_pct | 18.37 | 81.63 |
| 22 | Elongation_pct | 14.29 | 85.71 |
| 23 | True_strain | 11.22 | 88.78 |
| 24 | Si_at% | 11.22 | 88.78 |
| 25 | Shear_modulus_GPa | 11.22 | 88.78 |
| 26 | Poisson_ratio | 11.22 | 88.78 |
| 27 | Mo_at% | 10.20 | 89.80 |
| 28 | C_at% | 10.20 | 89.80 |
| 29 | Elastic_modulus_GPa | 9.18 | 90.82 |
| 30 | Lattice_parameter_nm | 8.16 | 91.84 |
| 31 | Atomic_size_misfit_pct | 8.16 | 91.84 |
| 32 | N_at% | 7.14 | 92.86 |
| 33 | DeltaG_FCC_HCP_J_mol | 7.14 | 92.86 |
| 34 | V_at% | 5.10 | 94.90 |
| 35 | Ti_at% | 5.10 | 94.90 |
| 36 | Uniform_elongation_pct | 4.08 | 95.92 |

## Pre-Pilot assessment

### A. Sufficiency

The dataset is sufficient for a **limited, uncertainty-aware feasibility test of the pipeline**, but not for a meaningful performance claim or final model: only 19 independent experimental groups are available, observations are clustered by paper/group, role resolution is incomplete, and many scientifically important predictors are sparse. Any later Pilot must use grouped and leave-one-paper-out validation and report uncertainty.

### B. Best-supported target

Of the requested targets, **TRIP binary is presently the most supportable feasibility target**, subject to manual label/role review. TWIP binary has less usable group-level support; multilabel and four-class targets fragment the small independent-group sample further. This is a data-support assessment, not a trained-model result.

### C-D. Features

Use only high-coverage composition components and documented test/processing variables shown near the top of the ranked table. Treat zero composition entries as reported zeros, not missing-value replacements. Sparse SFE, DeltaG, phase-fraction, grain-size, elastic, geometric, and onset-stress descriptors should not be primary Pilot inputs unless collection improves. Only `log10_strain_rate` was derived: the committed elemental and binary-enthalpy reference tables contain no constants, so VEC, mismatch, entropy/enthalpy, melting-temperature, and Omega features were deliberately not calculated.

### E. Collection priorities

Collect additional independent experimental alloy-condition groups, prioritising underrepresented TWIP-positive and joint TRIP/TWIP classes; explicitly record row role and group boundaries; resolve DOI and label ambiguities; and extract complete composition basis, test temperature/rate, processing/annealing history, grain size, initial phase fractions, SFE with method/temperature, DeltaG, and mechanical properties. Add referenced elemental/pair constants before enabling further derived features.
