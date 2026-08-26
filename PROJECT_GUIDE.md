# ML(ati) Project Guide

This document is the single source of truth for the scientific and computational history, present state, and governing practices of the ML(ati) metallurgy project. It is not merely a changelog.

## Codex Maintenance Rule

> After every meaningful repository task, PROJECT_GUIDE.md must be updated before the task is considered complete.

Future Codex work must:

1. perform the requested task;
2. validate the result;
3. update `PROJECT_GUIDE.md`;
4. append a Work Log entry;
5. update Current Project State;
6. update Known Problems if necessary;
7. update Decision Log if a scientific/methodological decision was made; and
8. include `PROJECT_GUIDE.md` in the commit.

Historical Work Log entries are append-only: do not rewrite or erase them. Correct or supersede an entry with a new entry that references it.

## 1. Scientific Objective

The current objective is a literature-based machine-learning study of deformation mechanisms in metastable high-/medium-entropy alloys, with particular emphasis on transformation-induced plasticity (TRIP) and twinning-induced plasticity (TWIP). The project uses published experimental and computational literature data; no new experimental testing is currently assumed. The final objective is a publication-quality scientific study, not merely a software demonstration. Neither novelty nor expected ML performance is assumed or exaggerated in advance of evidence.

## 2. Current Scientific Hypothesis

Composition, processing history, testing conditions, thermodynamic/physical descriptors, and microstructural descriptors may collectively contain predictive information about activation of TRIP and TWIP mechanisms. This is a working hypothesis to be tested rather than a fact to be assumed.

## 3. Current ML Targets

Currently considered targets are:

- binary TRIP;
- binary TWIP; and
- multilabel TRIP/TWIP.

A joint mechanism classification may be considered later. Final target selection depends on dataset size, class balance, label quality, and support from genuinely independent conditions. No final target has yet been selected and no model has yet been trained.

## 4. Data Philosophy

These rules are permanent:

- Never invent missing scientific values.
- NA is not zero.
- Never convert uncertain labels to negative labels.
- Never remove difficult rows simply to improve model performance.
- Preserve scientific uncertainty.
- Preserve DOI and `Paper_ID` provenance.
- Preserve original extracted values.
- Computational and experimental observations must remain distinguishable.
- Repeated deformation stages are not automatically independent samples.
- Do not artificially solve class imbalance by fabricating scientific data.
- Any scientific correction must be traceable.
- Raw literature files must remain immutable.

## 5. Dataset Architecture

| Identifier/field | Scientific meaning |
|---|---|
| `Paper_ID` | Stable project identifier for a source paper (currently P001–P019); the outer provenance and leave-one-paper-out grouping unit. |
| `DOI` | Published-document identifier retained for source verification and duplicate/provenance auditing. |
| `Parent_Experiment_ID` | Parent specimen or test series. Observations descending from one parent must remain together during splitting. Conservative unique parents are used when linkage is not demonstrated. |
| `Condition_ID` | Original extracted row condition, preserved unchanged; it is not by itself proof of independence. |
| `ML_Condition_ID` | Stage-collapsed experimental/computational condition identity. Experimental counting additionally requires an experimental origin/role; computational conditions never enter experimental counts. |
| `Observation_ID` | Unique row-level observation identity (`OBS###`), independent of whether the observation is experimental, computational, repeated-stage, or summary material. |
| `Deformation_Stage_ID` | Identity for a repeated strain/deformation stage within a parent experiment; NA when the row is not identified as a repeated stage. |
| `Experiment_Group_ID` | Legacy extracted grouping field. It is retained for provenance and audit but is not the current leakage-safe identity. In the hierarchical file it is also copied to `Original_Experiment_Group_ID`. |
| `Data_Origin` | Scientific origin: `EXPERIMENTAL`, `MD`, `DFT`, `CALPHAD`, `OTHER_COMPUTATIONAL`, `HYBRID`, or `UNRESOLVED`. |
| `Observation_Role` | Analytical role from the controlled vocabulary; it governs counting and eligibility rather than changing scientific values. |
| `Grouping_Confidence` / `Grouping_Review_Required` | Confidence/review gate for the inferred hierarchy. LOW rows must not be treated as settled linkage. |

The current hierarchy was constructed conservatively from the post-safe-QC dataset. Explicitly linked strain series share parents; otherwise conditions are kept separate. P006, P007, and P016 retain low-confidence grouping-review flags. This section must be updated whenever identity architecture changes.

## 6. Dataset Versions

Records in this table are permanent and must not be removed.

| Dataset Version | File | Papers | Rows | Purpose | Status |
|---|---|---:|---:|---|---|
| Raw batch P001–P005 | `data/raw/TRIP_TWIP_First5_FULL_EXTRACTION.xlsx` | 5 | Not separately reported | Immutable source workbook | RAW / IMMUTABLE |
| Raw batch P006–P010 | `data/raw/TRIP_TWIP_P006_P010_FULL_EXTRACTION.xlsx` | 5 | Not separately reported | Immutable source workbook | RAW / IMMUTABLE |
| Raw batch P011–P015 | `data/raw/TRIP_TWIP_P011_P015_FULL_EXTRACTION.xlsx` | 5 | Not separately reported | Immutable source workbook | RAW / IMMUTABLE |
| Raw batch P016–P019 | `data/raw/TRIP_TWIP_P016_P019_FULL_EXTRACTION.xlsx` | 4 | Not separately reported | Immutable source workbook | RAW / IMMUTABLE |
| `master_19papers_raw` | `data/interim/master_19papers_raw.csv` | 19 | 98 | Canonical-schema, provenance-preserving merge | HISTORICAL BASELINE |
| `master_19papers_raw_pre_qc` | `data/interim/master_19papers_raw_pre_qc.csv` | 19 | 98 | Frozen pre-forensic-QC merge | HISTORICAL / FROZEN |
| `master_19papers_post_safe_qc` | `data/interim/master_19papers_post_safe_qc.csv` | 19 | 98 | Safe schema-alias and representation corrections; no inferred labels | VALIDATED QC INPUT |
| `master_19papers_features` | `data/processed/master_19papers_features.csv` | 19 | 98 | Pilot derived-feature output; only `log10_strain_rate` populated because reference constants are empty | NONCANONICAL FEATURE DEMO |
| `master_19papers_hierarchical_ids` | `data/interim/master_19papers_hierarchical_ids.csv` | 19 | 98 | Adds leakage-safe parent, ML-condition, observation, stage, origin, role, confidence, and review identities | CURRENT CANONICAL DATASET (REBUILT 2026-08-25) |
| `master_19papers_recovery_v1` | `data/processed/master_19papers_recovery_v1.csv` | 19 | 98 | Non-destructive, provenance-linked integration of verified P006/P007/P016 recovery; original columns retained and recovered values stored in parallel | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v2` | `data/processed/master_19papers_recovery_v2.csv` | 19 | 108 | Manual P006/P016 resolution: retains 98 legacy rows, adds four exact P016 conditions and six correlated stage children, and applies effective targets through an explicit correction ledger | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |

## 7. Feature Dictionary

`Source` below means the immediate repository source; all literature fields ultimately retain paper/DOI and source-location provenance. Missingness percentages are row-level values from the current generated audit (98 rows), where available. `Reported` means extracted rather than calculated by this repository.

### Composition

| Feature | Meaning | Unit | Source | Experimental/Calculated | Calculation method | Missingness | Current ML status | Scientific caveats |
|---|---|---|---|---|---|---:|---|---|
| `Original_Composition` | Composition text as extracted | source notation | literature extraction | Reported | none | Not summarized | Preserve/provenance | Never overwrite with parsed values. |
| `Composition_basis` | Basis of reported composition | categorical | literature extraction / safe alias | Reported | none | Not summarized | Required metadata | at.% and wt.% must not be silently mixed. |
| `Fe_at%`, `Cr_at%`, `Co_at%`, `Mn_at%`, `Ni_at%` | Principal elemental fractions | at.% | literature extraction | Reported | none | 8.16%, 8.16%, 10.20%, 11.22%, 52.04% | Candidate after QC | A zero explicitly reported is not an imputed missing value; totals are flagged, not normalized. |
| `N_at%`, `C_at%`, `Mo_at%`, `Si_at%`, `Ti_at%`, `V_at%` | Minor/alloying elemental fractions | at.% | literature extraction | Reported | none | 92.86%, 89.80%, 89.80%, 88.78%, 94.90%, 94.90% | Sparse / retain | Sparse absence may mean unreported or absent; interpretation needs composition-basis review. |
| `Other_elements` | Elements outside explicit schema | source notation | literature extraction | Reported | none | Not summarized | Preserve/manual parsing | Must not be discarded when deriving descriptors. |

### Processing and testing

| Feature | Meaning | Unit | Source | Experimental/Calculated | Calculation method | Missingness | Current ML status | Scientific caveats |
|---|---|---|---|---|---|---:|---|---|
| `Processing_route`, `Cast_method`, `Cooling_route` | Processing-history descriptions | categorical/text | literature extraction | Reported | none | Not summarized | Candidate after harmonization | Free text and schema variation require controlled coding without loss of originals. |
| `Homogenization_T_K`, `Homogenization_time_h` | Homogenization schedule | K; h | literature extraction | Reported | none | 59.18%; 66.33% | Candidate but sparse | Multi-step schedules may not fit scalar fields. |
| `Hot_rolling_T_K`, `Hot_rolling_reduction_pct` | Hot-rolling conditions | K; % | literature extraction | Reported | none | 78.57%; 81.63% | Sparse | Reduction definition and sequence need checking. |
| `Cold_rolling_reduction_pct` | Cold-rolling reduction | % | literature extraction | Reported | none | 58.16% | Candidate | Processing path remains essential context. |
| `Annealing_T_K`, `Annealing_time_min` | Annealing schedule | K; min | literature extraction | Reported | none | 58.16%; 59.18% | Candidate | Annealing twins are not TWIP-positive evidence. |
| `Test_T_K` | Mechanical-test temperature | K | literature extraction | Reported | none | 13.27% | Primary candidate | Must describe the labelled condition, not an unrelated calculation. |
| `Strain_rate_s-1` | Applied strain rate | s⁻¹ | literature extraction | Reported | none | 29.59% | Primary candidate | Engineering/true and nominal/local definitions may differ. |
| `True_strain`, `Local_strain`, `Deformation_stage` | Observation point within deformation | dimensionless; dimensionless; text | literature extraction | Reported | none | `True_strain`: 88.78%; others not summarized | Grouping/stage metadata | Stage rows are correlated and not automatically independent. |
| `Gauge_length_mm`, `Gauge_width_mm`, `Specimen_thickness_mm` | Specimen geometry | mm | literature extraction | Reported | none | Not summarized | Context / exploratory | Geometry and test mode can affect comparability. |

### Microstructure, phase stability, SFE, and DeltaG

| Feature | Meaning | Unit | Source | Experimental/Calculated | Calculation method | Missingness | Current ML status | Scientific caveats |
|---|---|---|---|---|---|---:|---|---|
| `Grain_size_um`, `Grain_size_SD_um` | Characteristic grain size and spread | µm | literature extraction | Usually experimental | paper-specific | 56.12%; not summarized | Important but incomplete | Definition, distribution, phase, and measurement method may differ. |
| `Initial_FCC_fraction`, `Initial_HCP_fraction` | Pre-deformation phase fractions | fraction as extracted | literature extraction | Experimental or study-specific | paper-specific | 60.20%; 67.35% | Important but incomplete | Must be distinguished from deformation-induced fractions and checked for percent/fraction conventions. |
| `Initial_twin_boundary_status` | Pre-existing/annealing twin state | categorical/text | literature extraction | Experimental | paper-specific | Not summarized | Context / target safeguard | Initial or annealing twins do not establish TWIP. |
| `HCP_fraction_at_condition`, `Twin_fraction_or_Sigma3`, `Twin_thickness_nm`, `HCP_lath_or_lamella_note` | Condition/stage microstructure | fraction/text; nm | literature extraction | Usually experimental | paper-specific | Not summarized | Exploratory / stage-aware | Do not leak post-deformation outcomes into a pre-condition predictive model. |
| `SFE_mJ_m2`, `SFE_error_mJ_m2`, `SFE_method` | Stacking-fault energy, uncertainty, and method | mJ m⁻²; categorical | literature extraction | Experimental or calculated, method-specific | paper-specific; repository never estimates SFE | 75.51%; others not summarized | Sparse; do not pool blindly | Temperature, composition, intrinsic/extrinsic definition, and experimental/DFT/CALPHAD method matter. |
| `DeltaG_FCC_HCP_J_mol`, `DeltaG_method` | FCC→HCP thermodynamic driving/free-energy descriptor and method | J mol⁻¹; categorical | literature extraction | Usually calculated | paper-specific | 92.86%; method not summarized | Very sparse | Sign convention, temperature, reference states, and CALPHAD/DFT method must remain explicit. |
| `CSRO_present` | Reported chemical short-range order | categorical | literature extraction | Experimental or calculated | paper-specific | Not summarized | Exploratory | Evidence and threshold are heterogeneous. |

### Physical and mechanical properties

| Feature | Meaning | Unit | Source | Experimental/Calculated | Calculation method | Missingness | Current ML status | Scientific caveats |
|---|---|---|---|---|---|---:|---|---|
| `Elastic_modulus_GPa`, `Shear_modulus_GPa`, `Poisson_ratio` | Elastic descriptors | GPa; GPa; dimensionless | literature extraction | Experimental or calculated | paper-specific | 90.82%; 88.78%; 88.78% | Sparse | Test/calculation method and temperature matter. |
| `Lattice_parameter_nm`, `Atomic_size_misfit_pct` | Structural/misfit descriptors reported by papers | nm; % | literature extraction | Experimental or calculated | paper-specific | 91.84%; 91.84% | Sparse | Do not confuse reported misfit with repository-derived delta. |
| `YS_MPa`, `UTS_MPa` | Yield and ultimate tensile strengths | MPa | literature extraction | Experimental | paper-specific | 78.57%; 81.63% | Outcome/context | Potential leakage if mechanism prediction is intended before testing. |
| `Elongation_pct`, `Uniform_elongation_pct` | Total and uniform elongation | % | literature extraction | Experimental | paper-specific | 85.71%; 95.92% | Outcome/context | Definition and gauge length vary. |
| onset/critical-stress fields | Twin/TRIP onset strain and critical stress | strain; MPa | literature extraction | Experimental/model-dependent | paper-specific | Not summarized | Exploratory | Mechanism outcomes, unsuitable as pre-test predictors. |
| dynamic-heating fields | Adiabatic temperature and dynamic SFE change | K; mJ m⁻² | literature extraction | Calculated/estimated | paper-specific | Not summarized | Exploratory | Keep model assumptions and dynamic-test provenance. |

### Mechanism labels and evidence

| Feature | Meaning | Unit | Source | Experimental/Calculated | Calculation method | Missingness | Current ML status | Scientific caveats |
|---|---|---|---|---|---|---:|---|---|
| `TRIP`, `TWIP` | Operational mechanism targets | 1/0/NA | literature extraction | Evidence label | definitions in §8 | 10.20%; 13.27% | Under manual review | No target was changed by audits; ambiguity must remain NA/reviewed. |
| `Slip`, `Stacking_faulting`, `HCP_to_FCC_reversion` | Other mechanism flags | 1/0/NA | literature extraction | Evidence label | paper evidence | Not summarized | Exploratory | Absence of reporting is not a negative label. |
| `Dominant_mechanism` | Extracted mechanism interpretation | categorical/text | literature extraction | Evidence summary | paper-specific | Not summarized | Review aid | “Dominant” does not imply other mechanisms are absent. |
| `Evidence_TRIP`, `Evidence_TWIP`, `Characterization_methods`, `Source_location`, `Label_confidence` | Label evidence and provenance | text/categorical | literature extraction | Reported metadata | none | Not summarized | Required for verification | Evidence strength and modality vary by study. |

### Derived alloy and future image descriptors

| Feature | Meaning | Unit | Source | Experimental/Calculated | Calculation method | Missingness | Current ML status | Scientific caveats |
|---|---|---|---|---|---|---:|---|---|
| `log10_strain_rate` | Log-transformed positive strain rate | log10(s⁻¹) | `Strain_rate_s-1` | Calculated | `log10(rate)` for rate > 0 | 29.59% | Implemented candidate | Nonpositive/missing input propagates NA. |
| `VEC_derived`, `Atomic_size_mismatch_delta_pct`, `Configurational_entropy_J_molK`, `Mixing_enthalpy_kJ_mol`, `Omega`, `Electronegativity_mismatch`, `Melting_temperature_weighted_K` | Candidate composition descriptors | feature-specific | composition + external constants | Calculated | §15 | Effectively 100% in current output except configurational entropy can be composition-only in pandas implementation; stdlib output deliberately leaves undocumented-constant descriptors absent | Infrastructure only | Empty reference tables prevent validated use; incomplete compositions and missing constants must propagate NA. |
| image-derived descriptors (future) | Quantitative morphology, phase, texture, defect, or spatial descriptors | method-specific | EBSD/TEM/STEM/SEM/OM/phase-map images | Calculated from published images | not yet defined | Not applicable | Not implemented extension | Must preserve paper, figure/panel, scale, processing, and segmentation provenance. |

## 8. Target Definitions

| Target value | Operational definition |
|---|---|
| `TRIP = 1` | Deformation-induced martensitic transformation was observed or explicitly modelled for the specified mechanical condition. |
| `TRIP = 0` | Adequate condition-specific evidence explicitly supports absence/suppression of deformation-induced martensitic transformation; lack of mention alone is insufficient. |
| `TRIP = NA` | Evidence is absent, ambiguous, not condition-specific, computationally incomparable, or otherwise insufficient for a defensible binary label. |
| `TWIP = 1` | Deformation twinning occurred during the specified mechanical condition. |
| `TWIP = 0` | Adequate condition-specific evidence explicitly supports absence/suppression of deformation twinning; lack of mention alone is insufficient. |
| `TWIP = NA` | Evidence is absent, ambiguous, not condition-specific, computationally incomparable, or otherwise insufficient for a defensible binary label. |

Pre-existing martensite does not by itself establish TRIP. Initial twins and annealing twins do not establish TWIP. Processing-induced transformation and phase reversion do not by themselves establish TRIP. These phenomena remain scientifically relevant descriptors, but are distinct from deformation-induced target mechanisms. Any future definition change requires a new Decision Log entry; old definitions and decisions must not be erased.

## 9. Experimental vs Computational Data

- **Experimental:** measured processing, test, microstructure, properties, and mechanism evidence are retained with method/source metadata.
- **MD:** molecular-dynamics observations remain `Data_Origin=MD` and are not silently treated as experimental samples.
- **DFT:** DFT-derived quantities must retain method/calculation provenance; no current pure-DFT row class was identified in the hierarchy, but the architecture must support it.
- **CALPHAD:** thermodynamic/model conditions remain identifiable and method/temperature/reference-state specific.
- **Other computational:** model/design-only observations remain isolated from experimental parents.
- **Hybrid studies:** `HYBRID` identifies papers combining computational and experimental work. Each observation's role still determines eligibility; the label does not license silent pooling.

Computational data may support descriptor development, triangulation, or a separately validated model, but pooling with experiments requires an explicit scientific rationale, compatible target semantics, domain indicators, grouped validation, and a Decision Log entry.

## 10. Data Leakage Rules

Rows from the same parent experiment must not be randomly distributed between training and test data. Repeated stages stay with their parent and are not automatically independent training examples. Future validation candidates include `GroupKFold`, `StratifiedGroupKFold` when feasible, and Leave-One-Paper-Out. Any deviation must be scientifically justified and documented in both the Work Log and Decision Log.

Post-deformation variables, mechanism evidence text, label-confidence fields, and direct outcomes must also be screened for feature/target leakage before modelling.

## 11. Current Dataset Status

Repository-generated reports establish:

- **19 papers and 98 extracted rows/observations.** Row count is not equivalent to independent sample count.
- **72 experimental observations**, **26 computational observations** (including two computational roles in a hybrid paper), and **21 hybrid-origin observations**; origin and analytical-role counts intentionally overlap for hybrid papers.
- **55 unique experimental `ML_Condition_ID` values**, **19 repeated deformation-stage observations**, **1 summary row**, **0 unresolved-origin rows**, and **11 low-confidence grouping rows**.
- Currently usable labelled experimental ML conditions: TRIP **47**, TWIP **44**, and joint TRIP/TWIP **44**. These stage-aware availability counts include three explicitly reported stage series and are not claims of complete predictors or final ML eligibility.
- Ten legacy group conflicts resolve into seven artificial pooling conflicts and three legitimate sequential-mechanism series (P001_G01, P004_G01, P005_G01); none remains a demonstrated post-regrouping label conflict.
- Observation-level labels: TRIP 17 zero / 71 one / 10 unresolved; TWIP 19 zero / 66 one / 13 unresolved.
- Stage-aware independent-condition labels: TRIP 11 zero / 36 one / 8 unresolved; TWIP 11 zero / 33 one / 11 unresolved.
- The earlier pre-hierarchy audit counted only 19 independent experimental groups because its identity scheme was unresolved; the hierarchical audit supersedes that estimate without deleting its historical record.
- Recovery v1 preserves all 98 rows and original values. It adds 63 provenance records/value comparisons, verifies three previously unavailable target labels, and changes usable condition availability from 47 to 48 for TRIP, 44 to 46 for TWIP, and 44 to 46 jointly. These are availability counts, not model-readiness claims.
- Recovery v2 preserves those 98 legacy rows, reclassifies P016_C03 as a non-ML collapsed legacy record, adds four missing exact P016 condition rows and six correlated stage children (108 rows total), and establishes 58 experimental ML conditions. Recovery-aware usable condition availability changes from v1's 48/46/46 to 50/45/45 for TRIP/TWIP/joint after the evidence-based P006_C03 TWIP correction. Canonical target cells remain preserved; effective values and original/effective provenance are explicit.

## 12. Known Problems and Limitations

| Issue ID | Description | Scientific impact | Priority | Status | Resolution |
|---|---|---|---|---|---|
| ISS-001 | Mechanism-label ambiguity remains for P007 A600-5 and other queued papers; P016's two 400 C conditions and 750 C/10 min correctly remain unresolved rather than forced binary. | Targets may be biased or semantically inconsistent. | P1 | UNDER_REVIEW | Recovery v2 resolves the documented P006 discrepancy and P016 exact-condition targets through effective fields/ledger; continue source-specific review without inferring negatives. |
| ISS-002 | Computational/model rows coexist with experimental rows. | Silent pooling would confound domains and independence. | P1 | UNDER_REVIEW | `Data_Origin`/`Observation_Role` added; modelling separation still required. |
| ISS-003 | Repeated deformation-stage rows are correlated. | Random row splits would leak parent information and inflate performance. | P1 | UNDER_REVIEW | Parent/stage identities added; future grouped validation is mandatory. |
| ISS-004 | P006/P007 condition identities are verified, but their specimen/replicate parent linkage remains unresolved. P016 condition/stage hierarchy is now resolved. | Parent grouping and group splits may change after source review. | P1 | UNDER_REVIEW | Keep conservative P006/P007 parents; recovery v2 uses exact P016 condition parents and correlated child stages. |
| ISS-005 | Small and imbalanced independent target classes. | Limits stable training, calibration, subgroup evaluation, and performance claims. | P1 | OPEN | Expand diverse independent conditions; do not fabricate data. |
| ISS-006 | Only 58 independent experimental ML conditions are presently identified, fewer fully labelled for each target. | Effective sample size remains small despite 108 observation rows. | P1 | OPEN | Targeted collection and source review before pilot ML. |
| ISS-007 | Grain size is 56.12% missing. | Important microstructure dependence may be omitted or selection-biased. | P2 | OPEN | Recover from listed papers; retain definition/method. |
| ISS-008 | SFE is 75.51% missing and methods are heterogeneous. | Sparse/method-confounded phase-stability descriptor. | P2 | OPEN | Extract method/temperature-specific values; no empirical imputation. |
| ISS-009 | DeltaG is 92.86% missing. | Phase-stability modelling is poorly supported. | P2 | OPEN | Targeted extraction/collection with sign/method provenance. |
| ISS-010 | Initial FCC/HCP fractions are 60.20%/67.35% missing. | Initial state can be confused with deformation-induced transformation. | P2 | OPEN | Review source figures/tables and preserve measurement basis. |
| ISS-011 | Source batches retain noncanonical/unmapped fields and free-text schema inconsistencies. | Automated harmonization can lose meaning. | P2 | UNDER_REVIEW | Safe aliases applied; extras retained in `Unmapped_Fields`; 2/4 batches still need schema review. |
| ISS-012 | Elemental and binary-enthalpy reference tables contain headers only; constants and citations are undocumented. | Most alloy descriptors cannot be scientifically validated or calculated. | P1 | OPEN | Populate only traceable constants with references and validation tests. |
| ISS-013 | Mechanical outcomes and post-deformation descriptors could create feature leakage. | Models could predict labels using consequences of the mechanism. | P1 | OPEN | Define prediction timepoint and feature eligibility before pilot ML. |
| ISS-014 | No final target or final ML-ready dataset exists. | Model comparison/publication claims would be premature. | P1 | OPEN | Complete target verification and targeted expansion first. |
| ISS-015 | Raw workbook row totals per batch are not stated in generated reports. | Dataset-version documentation cannot safely assign batch row counts. | P3 | DEFERRED | Reported as “Not separately reported”; generate a source-batch census if needed. |

## 13. Manual Review Queue

The row-level details belong in `reports/tables/manual_review_queue.csv` (336 condition/field tasks), `mechanism_review.csv` (62 rows), `hierarchical_id_review.csv`, and `paper_manual_review_plan.csv`; they must not be duplicated or silently replaced here.

- **P1 target-label review:** P001–P008 and P010–P018.
- **P1 grouping review:** P006, P007, and P016 (11 observations; exact missing evidence is specimen/replicate identity and test-series linkage).
- **P2 recoverable-feature-only review:** P009 and P019.
- Important paper-specific gaps include grain size (P002, P006, P008–P017, P019), SFE (P002, P004, P006–P014, P016–P019), initial phase fractions (principally P007–P019), strain rate (P002, P005, P009, P014, P018, P019), and test temperature (P002, P018). The generated paper plan is authoritative for the exact current list.
- **Completed/reduced by recovery v1:** P006/P007 condition identities and three new target-availability gaps; P006 grain size, DFT 0 K intrinsic SFE, Thermo-Calc 300 K DeltaG, and mechanical-property evidence; P007 initial HCP fractions and mechanical-property verification. Method-specific values remain separate rather than closing experimental-SFE gaps.
- **Still manual:** P006/P007 specimen and replicate linkage; P006/P006_MC01 and MC03 TWIP; P007 A600-5 TRIP/TWIP; all attempted mappings of P016's 650/750 °C conditions and sequential stages to the existing three observations. The detailed status is authoritative in `grouping_pdf_review.csv` and `target_evidence_review.csv`.
- **Superseding recovery v2 resolution:** P006_C01 TWIP remains NA, P006_C02 is TRIP=0/TWIP=1, and P006_C03 is TRIP=1/TWIP=NA via the correction ledger. P016 now has six exact conditions; its six stages are correlated children and legacy C03 is non-ML. P007 A600-5 and P006/P007 specimen/replicate linkage remain manual P1 work.

## 14. Literature Collection Strategy

Prioritize papers that add diverse, independent experimental alloy/processing/test conditions rather than papers that merely increase row count. Current needs are:

- verified TRIP-negative and TWIP-negative conditions;
- TRIP-only, TWIP-only, and TRIP+TWIP conditions;
- explicit links among alloy, specimen, processing, test, and observation stage;
- well-documented processing, test temperature, strain rate, grain size, and initial phase fractions;
- method- and temperature-specific SFE;
- phase-stability/DeltaG descriptors where available; and
- explicit pre-test state and post-/in-situ mechanism evidence.

Existing-paper recovery should precede indiscriminate collection. Selection criteria, search terms, inclusion/exclusion rules, and duplicate handling must be logged when a formal review protocol is established.

## 15. Derived Feature Policy

Candidate descriptors and their present definitions are:

| Descriptor | Formula/definition | Constants source/reference | Implementation | Validation status |
|---|---|---|---|---|
| VEC | `Σ x_i VEC_i` | `data/external/element_properties.csv`; references not yet populated | `src/features/build_features.py` | BLOCKED: undocumented constants |
| Atomic-size mismatch | `100 sqrt[Σ x_i(1-r_i/r_bar)^2]` | same; atomic radii and references not yet populated | same | BLOCKED |
| Configurational entropy | `-R Σ x_i ln(x_i)`, `R=8.31446261815324 J mol⁻¹ K⁻¹` | gas constant embedded in implementation; composition from extraction | same | Infrastructure tested; scientific input completeness still requires review |
| Mixing enthalpy | `4 Σ(i<j) H_ij x_i x_j` | `data/external/binary_mixing_enthalpies.csv`; references not yet populated | same | BLOCKED |
| Omega | `T_m S_mix / abs(H_mix)` with `H_mix` converted from kJ/mol to J/mol | elemental and pair tables above | same | BLOCKED |
| Electronegativity mismatch | `sqrt[Σ x_i(χ_i-χ_bar)^2]` | elemental table; references not yet populated | same | BLOCKED |
| Weighted melting temperature | `Σ x_i T_m,i` | elemental table; references not yet populated | same | BLOCKED |
| log10 strain rate | `log10(Strain_rate_s-1)` for positive rates | extracted strain rate; no elemental constants | pandas and standard-library pipelines | IMPLEMENTED; 69/98 available |

Calculations require at.% totals within 100 ± 1 and do not normalize incomplete/suspicious compositions. Missing required composition, a missing elemental constant, or a missing binary pair propagates NA. Conflicting sources must not be averaged silently. Never calculate a derived scientific feature using undocumented constants. Formula, constants source, scholarly reference, implementation version, and validation evidence must be updated here before a descriptor becomes ML-eligible.

## 16. ML Strategy

| Stage | Description | Current status/evidence |
|---:|---|---|
| 1 | Data extraction | IN PROGRESS: 19-paper pilot extraction exists; expansion planned. |
| 2 | QC and provenance | IN PROGRESS: merge, audits, safe QC, DOI/source fields, and review queues exist; manual source review remains. |
| 3 | Hierarchical experimental identity | IN PROGRESS: hierarchy implemented; P006/P007/P016 unresolved. |
| 4 | Target verification | IN PROGRESS: operational definitions and queue exist; source verification incomplete. |
| 5 | Targeted literature expansion | NOT STARTED in repository evidence. |
| 6 | Pilot ML | NOT STARTED; not scientifically justified yet. |
| 7 | Feature engineering | INFRASTRUCTURE ONLY; `log10_strain_rate` implemented, constants-dependent features blocked. |
| 8 | Model comparison | NOT STARTED. |
| 9 | Grouped/external validation | PLANNED only. |
| 10 | Explainability and metallurgical interpretation | NOT STARTED. |
| 11 | Publication analysis | NOT STARTED. |

Stages overlap operationally, but none may be marked complete unless repository evidence supports completion.

## 17. Candidate Models

Possible future candidates include Logistic Regression, KNN, SVM, Decision Tree, Random Forest, Extra Trees, Gradient Boosting, XGBoost, LightGBM, and CatBoost. This list does not imply that any model has been trained, endorsed, ranked, or selected. Final selection depends on target semantics, effective sample size, class balance, missingness, feature types, calibration needs, interpretability, and leakage-safe validation feasibility.

## 18. Image-Based Extension

A future extension may extract descriptors from EBSD, TEM, STEM, SEM, optical microscopy (OM), phase maps, and other microstructure figures. Image-derived features are an extension, not automatically part of the primary model. Every image and descriptor must preserve `Paper_ID`, DOI, figure/panel, modality, scale/calibration, image-processing steps, and licensing/source provenance. Segmentation uncertainty, representativeness, resolution, repeated images from one specimen, and publication-image artifacts require explicit validation.

## 19. Decision Log

Append-only: never delete old decisions. If one changes, add a new decision that references the superseded decision.

| Decision ID | Date | Decision | Reason | Evidence | Status |
|---|---|---|---|---|---|
| DEC-001 | 2026-08-25 | Do not train final ML on the initial 19-paper dataset. | Effective independent support, label quality, and important-feature coverage are insufficient for publication-grade claims. | `reports/DATA_AUDIT.md`; `reports/QC_BEFORE_AFTER.md` | ACTIVE |
| DEC-002 | 2026-08-25 | Preserve experimental/computational separation. | Domains and target evidence are not automatically comparable or independent. | `README.md`; `reports/HIERARCHICAL_GROUPING_AUDIT.md` | ACTIVE |
| DEC-003 | 2026-08-25 | Introduce hierarchical experimental identifiers. | Legacy groups mixed repeated stages/conditions and could cause leakage or false label conflicts. | `scripts/build_hierarchical_ids.py`; `reports/HIERARCHICAL_GROUPING_AUDIT.md` | IMPLEMENTED / REVIEW OPEN |
| DEC-004 | 2026-08-25 | Safe QC must not infer or alter TRIP/TWIP labels. | No flagged mechanism value was scientifically repairable without source review. | `reports/TARGET_DEFINITION_AUDIT.md`; `reports/QC_BEFORE_AFTER.md` | ACTIVE |
| DEC-005 | 2026-08-25 | Use `master_19papers_hierarchical_ids.csv` as the current canonical dataset. | It preserves all 98 post-safe-QC observations and adds the current leakage-safe identity fields. | `reports/HIERARCHICAL_GROUPING_AUDIT.md` | ACTIVE |
| DEC-006 | 2026-08-25 | Make this guide mandatory and append-only for meaningful repository work. | Scientific reasoning and computational history must persist across tasks. | User instruction; `AGENTS.md` | ACTIVE |
| DEC-007 | 2026-08-25 | Adopt `ML_Condition_ID` as the stage-aware condition-counting unit and report sequential activation explicitly. | A physical test can produce multiple stage observations with changing mechanisms; majority collapse or conflict labelling would erase valid metallurgy. | `reports/tables/group_conflict_resolution.csv`; `reports/HIERARCHICAL_GROUPING_AUDIT.md` | ACTIVE / REVIEW OPEN |
| DEC-008 | 2026-08-26 | Keep PDF recovery in a separate, evidence-gated ledger; never apply recovered values directly to the canonical dataset. | Source values require explicit page/figure/table/section provenance, original units, extraction method, confidence, and review before any later controlled integration. | `scripts/prepare_pdf_recovery.py`; `data/interim/scientific_data_recovery.csv`; `tests/test_pdf_recovery.py` | ACTIVE |
| DEC-009 | 2026-08-26 | Integrate verified recovery into a new version using parallel recovered fields, while leaving the hierarchical canonical dataset and all original columns read-only. | This permits evidence use without silent replacement and keeps DFT SFE, Thermo-Calc DeltaG, assumed SFE, initial phase, and stage evidence scientifically distinct. | `scripts/integrate_verified_recovery.py`; `reports/RECOVERY_P006_P007_P016_AUDIT.md`; `tests/test_verified_recovery.py` | IMPLEMENTED / REVIEW OPEN |
| DEC-010 | 2026-08-26 | Treat P016_C03 as a preserved non-ML collapsed legacy row; represent six exact P016 heat-treatment conditions and retain deformation stages as correlated children. | The source separates 650 C durations and documents stage sequences, so forcing C03 to one source condition or counting stages independently would create false identity and leakage. | `P006_P016_manual_mapping_resolution.xlsx`; `scripts/integrate_manual_mapping_resolution.py`; `reports/RECOVERY_V2_AUDIT.md` | IMPLEMENTED |
| DEC-011 | 2026-08-26 | Invalidate P006_C03's unsupported TWIP=0 to effective NA through a correction ledger while preserving its original value. | Project semantics require explicit negative evidence; TRIP-dominant evidence does not prove absence of deformation twins. | `reports/tables/recovery_v2_target_correction_ledger.csv`; `reports/RECOVERY_V2_AUDIT.md` | IMPLEMENTED |

## 20. Project Work Log

### LOG-0001 — 2026-08-25 — Repository and Project Structure Creation

**Objective**

Establish a reproducible research repository layout for data, code, notebooks, reports, models, results, and figures.

**Input**

Initial repository and README state. Further task-prompt details are not recoverable from repository evidence.

**Actions Performed**

Created the research directory structure, `.gitignore`, dependency list, and an initial scientific/project README.

**Files Created**

Directory placeholder files, `.gitignore`, `requirements.txt`, and README content (see commit `e041d56`).

**Files Modified**

`README.md`.

**Scientific Decisions**

Organized the repository around immutable raw data and separated interim, processed, reporting, modelling, and publication artifacts.

**Data Changes**

No scientific values were changed.

**Validation**

Repository commit records the created structure. Exact historical validation commands are not recoverable from repository evidence.

**Problems Found**

Not recoverable from repository evidence.

**Problems Resolved**

A reproducible project skeleton was established.

**Remaining Problems**

No scientific dataset or pipeline had yet been validated at this stage.

**Next Recommended Step**

Build a provenance-preserving merge/QC/feature pipeline.

**Git Commit**

`e041d56b78ae0de1e85f30f649ed9ba18f6adf0e` — `Set up reproducible research project structure`.

### LOG-0002 — 2026-08-25 — Pipeline and Derived-Feature Infrastructure

**Objective**

Build a non-destructive literature-data merge, validation, audit, and transparent derived-feature foundation without fitting a model.

**Input**

Expected literature workbooks, canonical first-workbook schema, and empty traceable-reference templates.

**Actions Performed**

Implemented pandas-based merge and validation modules, audit support, notebooks, explicit feature formulas, tests, and external constant templates. Required complete constants and valid composition totals; prohibited SFE estimation and silent imputation.

**Files Created**

Core modules under `src/data`, `src/features`, and `src/analysis`; two planning/audit notebooks; external reference templates; `tests/test_pipeline.py`; report placeholders.

**Files Modified**

`README.md`, `.gitignore`, and `requirements.txt`.

**Scientific Decisions**

The first workbook defines the canonical schema; exact cleaned names are mapped, extras are preserved, missing inputs propagate NA, and raw data remain untouched. Candidate formulas were implemented but not claimed as validated scientific features without referenced constants.

**Data Changes**

No scientific values were changed.

**Validation**

Synthetic pipeline tests were added. Exact historical test output is not recoverable from repository evidence.

**Problems Found**

Elemental/pair constants needed scholarly provenance; real workbook execution was still pending.

**Problems Resolved**

Created auditable, provenance-preserving infrastructure and formula definitions.

**Remaining Problems**

Reference tables were empty and actual data coverage/quality were unknown.

**Next Recommended Step**

Run the pipeline on supplied workbooks and audit generated results.

**Git Commit**

`55802e429c8661271c845ef755915baeaf285316` — `Build provenance-preserving metallurgy data pipeline`.

### LOG-0003 — 2026-08-25 — 19-Paper Merge and Initial Data-Quality Audit

**Objective**

Merge four source workbooks and quantify dataset dimensions, provenance, labels, missingness, and pilot feasibility.

**Input**

Four immutable workbooks spanning P001–P019 and pipeline code. The environment could not install pandas/openpyxl because its package proxy returned HTTP 403, so a standard-library OOXML runner was used.

**Actions Performed**

Merged exact whitespace-cleaned schema matches, preserved extras in `Unmapped_Fields`, generated DOI/schema/data-quality tables, generated a processed CSV, and wrote the audit. No model was trained.

**Files Created**

`scripts/run_pipeline_stdlib.py`, `data/interim/master_19papers_raw.csv`, `data/processed/master_19papers_features.csv`, and initial report tables.

**Files Modified**

`README.md` and `reports/DATA_AUDIT.md`.

**Scientific Decisions**

The 19-paper data were designated a feasibility/pipeline-validation dataset, not a final ML dataset. Grouped and paper-held-out validation were required for future work. Undocumented-constant derived features were not calculated.

**Data Changes**

Rows before/after merge: source-batch totals not separately reported / 98 merged rows. The merged file had 89 columns; the processed CSV added `log10_strain_rate` (90 columns). Labels were not changed. Missing scientific values were not filled.

**Validation**

Generated audit reported 19 papers, 19 DOI values, 98 unique `Condition_ID` values, 47 legacy experiment groups, zero duplicate-condition rows, zero DOI conflicts, and zero out-of-tolerance composition sums.

**Problems Found**

Sixty-two mechanism-flagged rows, schema differences in 2/4 batches, sparse key features, uncertain row roles, and only 19 groups then counted as independent experimental groups.

**Problems Resolved**

Established a reproducible merged baseline and quantified data quality without destructive cleanup.

**Remaining Problems**

Target/role review, hierarchical identities, reference constants, missing features, and larger independent support remained.

**Next Recommended Step**

Perform forensic QC and define a safe correction/manual-review boundary.

**Git Commit**

`912c63f7dae36930322a8688eef2ec55d0ac04f9` — `Run 19-paper merge and data quality audit`.

### LOG-0004 — 2026-08-25 — Forensic QC and Target Audit

**Objective**

Freeze the pre-QC merge, distinguish safe representation fixes from scientific interpretation, audit targets/roles/groups/features, and create manual-review queues.

**Input**

All four raw workbooks and the 98-row merge.

**Actions Performed**

Read immutable workbooks directly; classified mechanism flags; applied only exact schema aliases and formatting/representation corrections; produced before/after, target-definition, correction, feature, group, role, missingness, and review artifacts.

**Files Created**

`master_19papers_raw_pre_qc.csv`, `master_19papers_post_safe_qc.csv`, `scripts/run_forensic_qc.py`, `tests/test_forensic_qc.py`, two Markdown reports, and eight detailed QC tables.

**Files Modified**

`README.md`.

**Scientific Decisions**

No mechanism flag was defensibly repairable without reading sources. Initial/pre-existing martensite, initial/annealing twins, processing transformation, and phase reversion were separated from deformation-induced target meaning. Difficult rows and uncertainty were preserved.

**Data Changes**

Rows before/after: 98/98. TRIP missing before/after: 10/10. TWIP missing: 13/13. Safe representation/schema-alias corrections: 129 cells; canonical post-QC width: 94 columns. Labels changed: 0. IDs changed: 0. No missing scientific value was imputed.

**Validation**

Generated reports classified all 62 mechanism flags and produced 336 manual-review tasks across 18 papers; tests covered forensic safeguards.

**Problems Found**

Existing groups combined stages and sometimes different conditions, causing ten artificial group-level conflicts. Sparse phase/SFE/DeltaG/processing fields and label ambiguity remained.

**Problems Resolved**

Safe schema aliases were recovered and all corrections made traceable; the scientific review boundary was explicit.

**Remaining Problems**

Original-paper review, hierarchy redesign, and targeted collection remained necessary before ML.

**Next Recommended Step**

Introduce parent/condition/observation/stage identifiers without relabelling targets.

**Git Commit**

`5d9209210072c56154ede2c64c89500829f9e707` — `Add forensic QC review for 19-paper dataset`.

### LOG-0005 — 2026-08-25 — Hierarchical Experimental Identity

**Objective**

Separate parent experiments, independent conditions, repeated stages, summaries, and computational conditions to support leakage-safe counting and future validation.

**Input**

`master_19papers_post_safe_qc.csv`, forensic role fields, and explicit links present in extracted text.

**Actions Performed**

Preserved legacy groups, assigned `Parent_Experiment_ID`, unique `Observation_ID`, repeated-stage IDs, `Data_Origin`, `Observation_Role`, grouping reasons/confidence, and paper-level review priorities; generated an independence census.

**Files Created**

`data/interim/master_19papers_hierarchical_ids.csv`, `scripts/build_hierarchical_ids.py`, `tests/test_hierarchical_ids.py`, `reports/HIERARCHICAL_GROUPING_AUDIT.md`, and two review tables.

**Files Modified**

None reported by the commit beyond created artifacts.

**Scientific Decisions**

Only explicitly documented strain series share a parent; all other conditions receive conservative separate parents. Pure computational observations are isolated; hybrid experimental conditions may count as experimental only by observation role. Parent labels are not decided by majority vote.

**Data Changes**

Rows before/after: 98/98. Columns before/after: 94/103. Added `Original_Experiment_Group_ID`, `Parent_Experiment_ID`, `Observation_ID`, `Deformation_Stage_ID`, `Data_Origin`, `Observation_Role`, grouping-review/reason/confidence fields. TRIP/TWIP values changed: 0. The hierarchy identified 72 experimental and 26 computational observations, 52 independent conditions, 19 repeated-stage rows, and one summary row.

**Validation**

All ten legacy group conflicts disappeared under condition/parent-aware evaluation; zero parent-level conflicts remained. Tests checked identity uniqueness, preservation, and role behavior.

**Problems Found**

Eleven rows in P006, P007, and P016 lack sufficient evidence for high-confidence specimen/test-series linkage.

**Problems Resolved**

Stage evolution no longer masquerades as a label conflict, and a leakage-safe split key now exists.

**Remaining Problems**

Manual grouping and target review remain; current independent counts are estimates subject to source verification.

**Next Recommended Step**

Review P006/P007/P016 grouping and P1 target evidence in original papers, then expand independent class support.

**Git Commit**

`90464c474539cba605aa551fd7d9abb2350ca14a` — `Add leakage-safe hierarchical observation identities`.

### LOG-0006 — 2026-08-25 — Persistent Project Guide and Agent Workflow

**Objective**

Create a permanent scientific/computational project guide, backfill verifiable history, and require future agents to maintain it.

**Input**

Git history, `README.md`, code, generated CSV dimensions, audit reports, review queues, and current canonical dataset.

**Actions Performed**

Reconstructed five major project stages from repository evidence; documented objectives, hypothesis, architecture, versions, features, targets, leakage rules, limitations, decisions, strategy, roadmap, and current status; created root agent instructions; linked the guide from README.

**Files Created**

`PROJECT_GUIDE.md`; `AGENTS.md`.

**Files Modified**

`README.md`.

**Scientific Decisions**

Designated the hierarchical-ID CSV as the current canonical dataset and made guide maintenance append-only and mandatory. No target, model, scientific result, or performance claim was introduced.

**Data Changes**

No scientific values were changed.

**Validation**

Verified repository evidence and CSV dimensions; checked required headings/content; ran the repository test suite and documentation checks (results recorded in the task's final report and Git history).

**Problems Found**

Existing information was distributed across commits, reports, code, and queues; raw-batch row totals and some historical validation commands were not recoverable from repository evidence.

**Problems Resolved**

Established one durable source of truth and an agent enforcement file without rewriting historical scientific artifacts.

**Remaining Problems**

All OPEN/UNDER_REVIEW issues in §12 remain; documentation does not substitute for source-paper review.

**Next Recommended Step**

Resolve P1 grouping/target reviews before pilot modelling or broad feature engineering.

**Git Commit**

Commit message: `Add persistent ML(ati) project guide and agent workflow`. The final hash is assigned by Git after this entry is written; see repository history.


### LOG-0007 — 2026-08-25 — Stage-Aware Hierarchical Identity Completion

**Objective**

Complete and validate the requested paper → parent experiment → ML condition → observation/stage hierarchy for all 98 observations without ML training or scientific relabelling.

**Input**

`master_19papers_post_safe_qc.csv`, the earlier hierarchy, forensic review tables, and extracted stage/role/provenance evidence.

**Actions Performed**

Added explicit `ML_Condition_ID` and `Grouping_Confidence`; rebuilt the dataset and 98-row identity review; created conflict-resolution, 19-paper manual-review, and feature-recovery tables; recalculated stage-aware label distributions and readiness findings; strengthened preservation tests.

**Files Created**

`reports/tables/group_conflict_resolution.csv` and `reports/tables/existing_paper_feature_recovery_plan.csv`.

**Files Modified**

The hierarchy builder/test, versioned hierarchical CSV, three generated audit/review artifacts, this guide, and the final report.

**Scientific Decisions**

Stage-linked observations share one ML condition and retain distinct stage identities. Mixed 0/1 values within an explicit stage series represent observed activation at condition level, are enumerated, and are never majority-voted. Pure computational conditions are excluded from experimental counts.

**Data Changes**

Rows remained 98; all 94 pre-existing columns and TRIP/TWIP values remained unchanged. The identity/QC columns were appended/regenerated. The revised census contains 55 experimental ML conditions; 47/44/44 have usable TRIP/TWIP/joint labels.

**Validation**

Regenerated artifacts and compared every pre-existing source column value; checked unique/nonmissing observation IDs, controlled vocabularies, all 19 plan rows, and conflict classification. Full test commands and results are recorded in the task final response.

**Problems Found**

The earlier hierarchy omitted `ML_Condition_ID`, used `Confidence` rather than `Grouping_Confidence`, excluded stage-only tests from independent-condition counts, and lacked the requested conflict and feature-recovery tables.

**Problems Resolved**

All requested identity fields/tables now exist. Seven old conflicts were artificial pooling; three were sequential evolution; no post-regrouping conflict is established as genuinely ambiguous.

**Remaining Problems**

P006/P007/P016 grouping and P001–P008/P010–P018 target evidence require original-paper review; important descriptors remain sparse.

**Next Recommended Step**

Perform the P1 source-paper review before pilot ML, then recover P2 features and expand with genuinely independent experimental conditions.

**Git Commit**

Commit message: `Add hierarchical experimental identity and leakage-safe grouping audit`. The final hash is assigned after this entry is written.

### LOG-0008 — 2026-08-26 — Scientific PDF Data-Recovery Preparation

**Objective**

Prepare a reproducible, non-destructive review system for recovering missing scientific information and verifying target/grouping evidence in the original 19 papers, without modelling, relabelling, imputation, or canonical-data edits.

**Input**

The 98-row hierarchical canonical dataset, current QC/audit tables, P1/P2 issues, and metadata already present in the repository. No PDFs were supplied or committed.

**Actions Performed**

Created a 19-paper manifest, a 1,568-row blank observation/feature recovery ledger, condition-level target review queue, focused grouping review for P006/P007/P016, feature-priority ranking, paper-priority ranking, a deterministic generator/validator, PDF directory instructions, and workflow tests. The hierarchical redesign completed on 2026-08-25 remains intact and is now the identity foundation for source review.

**Files Created**

`data/raw/papers/paper_manifest.csv`, `data/raw/papers/README.md`, `data/interim/scientific_data_recovery.csv`, `reports/tables/target_evidence_review.csv`, `reports/tables/grouping_pdf_review.csv`, `reports/tables/feature_recovery_priority.csv`, `reports/tables/paper_review_queue.csv`, `scripts/prepare_pdf_recovery.py`, and `tests/test_pdf_recovery.py`.

**Files Modified**

`.gitignore` and `PROJECT_GUIDE.md`.

**Scientific Decisions**

PDFs are local, untracked review inputs. `Recovered_Value` remains blank until source-supported; a recovery row cannot be `VERIFIED` without value, evidence type/location, extraction method, and confidence. Original values and units are retained verbatim in the ledger. Target labels and hierarchy are read-only during review; regrouping or relabelling requires a later explicit, reviewed correction workflow rather than silent overwrite.

**Data Changes**

No frozen/raw/pre-QC/canonical scientific file was modified; no observation was deleted; no TRIP/TWIP label or existing scientific value changed; no missing value was filled. The new files are review metadata/templates only.

**Validation**

The workflow checks exactly one manifest row for each P001–P019, 98-observation identity coverage, canonical/pre-QC-column equality, blank initial recovered values, evidence requirements for verified records, required paper scopes, ranked 19-paper coverage, and Git exclusion of `data/raw/papers/*.pdf`. The full 14-test suite passed.

**Problems Found**

All 19 DOI values are present, but titles are absent from repository metadata for P006–P015. No source PDFs are currently available, so DOI/title matching and scientific evidence verification remain pending. A potentially recoverable count means a gap is queued for inspection, not that the source necessarily reports it.

**Problems Resolved**

The project now has a reproducible evidence-capture boundary that cannot silently overwrite canonical data, plus explicit paper, feature, target, and grouping priorities.

**Remaining Problems**

ISS-001 and ISS-004 remain open until PDFs are reviewed. All feature gaps remain unfilled, all current labels remain unchanged, and no PDF metadata/content match has been verified.

**Next Recommended Step**

Supply locally named `P001.pdf` through `P019.pdf` in `data/raw/papers/`, run `python scripts/prepare_pdf_recovery.py --verify-pdfs`, then manually verify manifest DOI/title matches and review papers in `paper_review_queue.csv` order, beginning with P016, P006, and P007. Record source evidence before any `Recovered_Value`, and do not integrate recovered data into the canonical dataset in this stage.

**Git Commit**

Commit message: `Prepare evidence-gated scientific PDF recovery workflow`. The final hash is assigned after this entry is written.

### LOG-0009 — 2026-08-26 — Verified P006/P007/P016 Evidence Integration

**Objective**

Integrate three supplied scientific evidence-recovery workbooks into a new non-destructive 19-paper dataset version while preserving hierarchy, method distinctions, uncertainty, and cell-level provenance.

**Input**

The P006, P007, and P016 recovery workbooks in `data/interim/manual_recovery/`, the 98-row hierarchical canonical dataset, and the evidence/grouping review ledgers.

**Actions Performed**

Verified every workbook Paper_ID and DOI; mapped P006 by unique composition and P007 by annealing duration; mapped only P016's two exact 400 °C conditions and left incompatible/unrepresented annealed and strain-stage mappings for manual review. Generated recovery v1, updated all three review tables, wrote an audit, and added deterministic integration and preservation tests.

**Files Created**

`data/processed/master_19papers_recovery_v1.csv`, `reports/RECOVERY_P006_P007_P016_AUDIT.md`, `scripts/integrate_verified_recovery.py`, and `tests/test_verified_recovery.py`.

**Files Modified**

`data/interim/scientific_data_recovery.csv`, `reports/tables/target_evidence_review.csv`, `reports/tables/grouping_pdf_review.csv`, and this guide.

**Scientific Decisions**

Original values and labels remain read-only. Recovered data use parallel fields and a provenance ledger. P006 DFT intrinsic SFE at 0 K is distinct from experimental room-temperature SFE, and its Thermo-Calc DeltaG remains 300 K/method-specific. P007 quench-induced epsilon is an initial phase fraction, A600-5 remains unresolved, and stage evidence is not collapsed. P016's 18 mJ/m² is an assumed calculation input only; stage mappings were not guessed.

**Data Changes**

Rows before/after: 98/98; original columns/cells changed: 0; recovery records/value comparisons: 63. Missingness fell for grain size (56.12% to 53.06%), separately tracked method-specific SFE availability (75.51% to 70.41%), initial HCP fraction (67.35% to 62.24%), and mechanical-property availability (76.53% to 73.47%). Other requested families were unchanged on the defined observation basis. Usable label availability changed from 47/44/44 to 48/46/46 for TRIP/TWIP/joint.

**Validation**

The full 17-test suite passed with `PYTHONPATH=.`. Tests verify immutable workbook hashes, 98-row/order preservation, exact equality of every original column, no unresolved-to-negative conversion, method separation, and a complete evidence-ledger row for every populated recovered cell.

**Problems Found**

P016 supplies five conditions and six stage records while the canonical data have only three observations; the apparent P016_C03 annealing temperature conflicts with the 750 °C/3 min condition suggested by its elongation, so mapping is not defensible. The recovered P006_MC03 TWIP assessment is unresolved while its original value is 0; this discrepancy was retained, not overwritten.

**Problems Resolved**

Condition identity is now verified for three P006 compositions and five P007 annealing states. Three previously unavailable target labels have direct condition-specific support, and major P006/P007 descriptor evidence now has explicit source/method provenance.

**Remaining Problems**

P006/P007 specimen/replicate parent linkage, P006 TWIP gaps, P007 A600-5 labels, P016 condition/stage mapping, and broader P1/P2 gaps remain under manual review. Recovery v1 is not a final ML-ready dataset.

**Next Recommended Step**

Resolve P016 hierarchy against source/specimen identities and adjudicate the P006 TWIP discrepancy before any modelling; then continue evidence recovery for other high-priority papers.

**Git Commit**

Commit message: `Integrate verified P006 P007 P016 recovery evidence`. The final hash is assigned after this entry is written.

### LOG-0010 — 2026-08-26 — P006/P016 Manual Mapping Resolution and Recovery v2

**Objective**

Apply the supplied manual resolution workbook exactly, create recovery v2 without training, and rerun hierarchy, leakage, target, provenance, missingness, and usable-condition audits.

**Input**

Recovery v1 and `data/interim/manual_recovery/P006_P016_manual_mapping_resolution.xlsx`.

**Actions Performed**

Built a deterministic integration script; retained all 98 legacy rows; assigned exact identities to the two existing 400 C P016 rows; reclassified P016_C03 as collapsed legacy/non-ML; added four missing exact condition records and six correlated stage children; added effective targets and a P006 correction ledger; generated a consolidated audit and preservation/semantics tests.

**Files Created**

`data/processed/master_19papers_recovery_v2.csv`, `reports/tables/recovery_v2_target_correction_ledger.csv`, `reports/RECOVERY_V2_AUDIT.md`, `scripts/integrate_manual_mapping_resolution.py`, and `tests/test_manual_mapping_resolution.py`.

**Files Modified**

`.gitignore` and this guide.

**Scientific Decisions**

P016_C03 cannot represent either exact 650 C duration and is excluded from ML without deletion. Exact 400/650/750 C by 3/10 min identities are represented separately. Stage observations remain correlated children. P006_C03 retains original TWIP=0 for provenance, while its effective value is NA because explicit negative evidence is absent.

**Data Changes**

Recovery v2 contains 108 rows: 98 retained legacy rows, four new exact P016 conditions, and six stage children. It contains 58 independent experimental ML conditions. Effective usable TRIP/TWIP/joint availability changes from 48/46/46 to 50/45/45. No raw, canonical, or recovery-v1 target cell was overwritten.

**Validation**

The full 19-test suite passed. Tests enforce workbook immutability, 98-row legacy preservation, equality of legacy scientific/source fields, exact P016 hierarchy, correlated stage linkage, P006 original/effective target separation, and unique observations. The generated audit additionally reports hierarchy, leakage, provenance, target, missingness, and condition availability checks.

**Problems Found**

The earlier recovery could not safely map P016_C03 and left an unsupported P006_C03 TWIP negative in canonical data.

**Problems Resolved**

P016's exact condition/stage hierarchy and the P006 target discrepancy are resolved non-destructively.

**Remaining Problems**

P006/P007 specimen/replicate linkage, P007 A600-5 labels, broader queued target verification, computational-domain separation, small/imbalanced support, missing reference constants, sparse descriptors, feature leakage eligibility, and final-target selection remain P1 blockers.

**Next Recommended Step**

Resolve remaining P006/P007 grouping and P007 target evidence, then address the other P1 target/leakage gates before any ML training.

**Git Commit**

Commit message: `Integrate P006 P016 mapping resolution into recovery v2`. The final hash is assigned after this entry is written.

## 21. Current Project State

| Item | Current snapshot (2026-08-26) |
|---|---|
| Current stage | P006/P016 manual resolution integrated in recovery v2; remaining P006/P007 grouping and broader target review continue; no ML training. |
| Current canonical dataset | `data/interim/master_19papers_hierarchical_ids.csv` |
| Current recovery dataset | `data/processed/master_19papers_recovery_v2.csv` (108 rows; all 98 legacy rows and canonical original values preserved) |
| Number of papers | 19 |
| Number of rows | 108 observations: 98 legacy, four new exact P016 conditions, and six correlated P016 stage children; row count is not independent sample count. |
| Latest independent-condition estimate | 58 experimental ML conditions; P016 hierarchy is resolved, while P006/P007 parent linkage remains uncertain. |
| Current target status | Under review. Recovery-v2 effective usable labelled ML conditions: TRIP 50, TWIP 45, joint 45; unresolved labels remain NA and no final target is selected. |
| Major unresolved issue | P006/P007 parent linkage, P007 A600-5 and broader target gaps, leakage eligibility, sparse descriptors/reference constants, and small support remain. |
| Next action | Resolve remaining P006/P007 grouping/target reviews and other P1 gates; do not train until target and leakage gates are satisfied. |

## 22. Publication Roadmap

The eventual paper should contain:

1. Introduction
2. Literature/Data methodology
3. Dataset construction
4. Metallurgical descriptor design
5. ML methodology
6. Validation
7. Results
8. Explainability
9. Metallurgical interpretation
10. Limitations
11. Conclusions

The roadmap is prospective. Do not write conclusions before analysis supports them, and do not present pipeline feasibility as scientific predictive performance.
