# Feature Schema V2 Audit

Feature Schema V2 classifies all **596** V17-QC fields with no unresolved role. V1 policy is retained and every post-V1/P020-P023 field receives explicit review.

| Schema_Role | Field_n |
| --- | --- |
| PROVENANCE_ONLY | 123 |
| PREDICTOR_SAFE_DIRECT | 104 |
| PREDICTOR_SAFE_CONDITIONAL | 88 |
| METADATA_ONLY | 61 |
| LEAKAGE_POST_TEST | 59 |
| TARGET_ONLY | 48 |
| LEAKAGE_MECHANICAL_OUTCOME | 36 |
| LEAKAGE_MODEL_DERIVED | 24 |
| COMPUTATIONAL_ONLY | 23 |
| GROUPING_ONLY | 18 |
| IDENTIFIER_ONLY | 12 |

Pilot M2 contains exactly six numeric predictors: `Fe_at%, Mn_at%, Co_at%, Cr_at%, Test_T_K, Strain_rate_s-1`. All are required; no imputation or inferred zero is allowed. Scaling occurs only inside Logistic/SVC training folds.

| Column_Name | Schema_Role | CORE_M2 | Scientific_Justification |
| --- | --- | --- | --- |
| Fe_at% | PREDICTOR_SAFE_DIRECT | True | Direct source-supported information available before loading. |
| Mn_at% | PREDICTOR_SAFE_DIRECT | True | Direct source-supported information available before loading. |
| Co_at% | PREDICTOR_SAFE_DIRECT | True | Direct source-supported information available before loading. |
| Cr_at% | PREDICTOR_SAFE_DIRECT | True | Direct source-supported information available before loading. |
| Test_T_K | PREDICTOR_SAFE_DIRECT | True | Direct source-supported information available before loading. |
| Strain_rate_s-1 | PREDICTOR_SAFE_DIRECT | True | Direct source-supported information available before loading. |
| GND_density_m-2 | LEAKAGE_POST_TEST | False | The field is observed only after tensile deformation starts or after fracture. |
| Engineering_YS_MPa | LEAKAGE_MECHANICAL_OUTCOME | False | The field is an outcome of the same tensile test whose mechanisms are predicted. |
| Postfracture_HCP_fraction | LEAKAGE_POST_TEST | False | The field is observed only after tensile deformation starts or after fracture. |
| TWIP_Phase | TARGET_ONLY | False | Target definition/evidence; never a predictor |
| SDI_MPa | LEAKAGE_MECHANICAL_OUTCOME | False | Same-test mechanical outcome |
| PostTest_FCC_fraction | LEAKAGE_POST_TEST | False | Observed after loading begins |
| PostTest_HCP_fraction | LEAKAGE_POST_TEST | False | Observed after loading begins |
| PostTest_Twin_Evidence | LEAKAGE_POST_TEST | False | Observed after loading begins |
| TRIP_Onset_True_Stress_MPa | LEAKAGE_MODEL_DERIVED | False | Derived from observed response/mechanism |
| WH_Rate_at_Slope_Change_MPa | LEAKAGE_MODEL_DERIVED | False | Derived from observed response/mechanism |
| ThermoCalc_Software | COMPUTATIONAL_ONLY | False | Computational context outside experimental predictors |
| ThermoCalc_Database | COMPUTATIONAL_ONLY | False | Computational context outside experimental predictors |

Mechanical outcomes, post-test phases/twins/GND/KAM, target evidence, onset/work-hardening, identifiers/groups/provenance, and computational context are excluded. Thermo-Calc remains model context; local EDS is never promoted to bulk chemistry.
