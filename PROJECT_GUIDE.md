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
| `Paper_ID` | Stable project identifier for a source paper (currently P001-P023); the outer provenance and leave-one-paper-out grouping unit. New primary sources beyond the original P001-P019 set receive the next stable ID after DOI/source-identity and duplicate review. |
| `DOI` | Published-document identifier retained for source verification and duplicate/provenance auditing. |
| `Study_Series_ID` | Study-wide experimental series. Use as the strict within-study leakage group when all sibling conditions must remain together. |
| `Material_Parent_ID` | Composition/material-series parent, distinct from physical batch and analytical condition. It may group processing branches while retaining distinct `ML_Condition_ID` values. |
| `Physical_Batch_ID` | Documented melt, ingot, or physical batch only. It remains NA when the source does not establish batch identity. |
| `Replicate_ID` | Explicitly documented replicate specimen identity only. Unknown replicate identity or a reported ± value never creates an ID. |
| `Parent_Experiment_ID` | Parent specimen or test series. Observations descending from one parent must remain together during splitting. Conservative unique parents are used when linkage is not demonstrated. |
| `Condition_ID` | Original extracted row condition, preserved unchanged; it is not by itself proof of independence. |
| `ML_Condition_ID` | Stage-collapsed experimental/computational condition identity. Experimental counting additionally requires an experimental origin/role; computational conditions never enter experimental counts. |
| `Parent_ML_Condition_ID` | Parent condition referenced by a child/stage observation. Such children inherit the parent's split assignment and do not become independent samples. |
| `Observation_ID` | Unique row-level observation identity (`OBS###`), independent of whether the observation is experimental, computational, repeated-stage, or summary material. |
| `Deformation_Stage_ID` | Identity for a repeated strain/deformation stage within a parent experiment; NA when the row is not identified as a repeated stage. |
| `Experiment_Group_ID` | Legacy extracted grouping field. It is retained for provenance and audit but is not the current leakage-safe identity. In the hierarchical file it is also copied to `Original_Experiment_Group_ID`. |
| `Data_Origin` | Scientific origin: `EXPERIMENTAL`, `MD`, `DFT`, `CALPHAD`, `OTHER_COMPUTATIONAL`, `HYBRID`, or `UNRESOLVED`. |
| `Observation_Role` | Analytical role from the controlled vocabulary; it governs counting and eligibility rather than changing scientific values. |
| `Grouping_Confidence` / `Grouping_Review_Required` | Confidence/review gate for the inferred hierarchy. LOW rows must not be treated as settled linkage. |
| `Leakage_Group_Strict` / `Leakage_Group_Material` | Separate validation keys for strict study-series holdout and material-parent holdout; neither overloads batch, replicate, condition, or observation identity. |
| aggregate property fields | Published means and uncertainties are stored separately (`YS/UTS/TE/UE_mean` and `_uncertainty`), with `uncertainty_type` and `Replicate_n`; unknown statistic type is `UNKNOWN_REPORTED_PM`, and no pseudo-replicates are generated. |

The current hierarchy was constructed conservatively from the post-safe-QC dataset and refined by source-reviewed recovery workbooks. Explicitly linked strain series share parents; otherwise conditions are kept separate. P006 now has three composition-specific material parents under `P006_SERIES01`; P007 has five annealing conditions under shared material parent `P007_MAT01` and `P007_SERIES01`; P016 has exact condition/stage linkage. P020 adds one independent in-situ tensile condition, `P020_MC_TRIPHEA_INSITU`, under `P020_SERIES01` and `P020_MAT_FE50MN30CO10CR10`; its six loading stages are correlated children. P021 adds exactly five independent annealing/grain-size/test-temperature tensile conditions under `P021_SERIES01` and the new `P021_MAT_FE50MN17p5CR12p5CO10NI5SI5` family. Its four room-temperature grain-size states and one 77 K state remain distinct conditions but share strict study/material leakage groups; the reported minimum of three specimens is aggregate metadata and creates no replicate rows. P022 adds five separately fabricated as-cast chemistry variants under `P022_SERIES01`, with one material parent and one primary tensile condition for each of C0, C2, C4, C2Mo1, and C2Mo2. Its three 40%-strain EBSD records are correlated stage children of C2/C2Mo1/C2Mo2 and never increase independent support. P023 adds seven exact room-temperature tensile conditions under `P023_SERIES01` and `P023_MAT_FE39MN20CO20CR15SI5AL1`, all derived from one double-pass-FSP material branch and its 650/850 C anneals. Ten pre-test processing-state phase records are retained separately; the three 750 C states are supporting-only because no condition-specific tensile results are reported. P023 before/after deformation evidence and work-hardening-derived onset remain support/target metadata rather than extra master rows. P006/P007/P020/P021/P022/P023 physical batch and replicate identity remain unknown metadata, not unresolved material-parent hierarchy. P023 `Replicate_n=3` is aggregate condition metadata and creates no replicate rows. This section must be updated whenever identity architecture changes.

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
| `master_19papers_recovery_v3` | `data/processed/master_19papers_recovery_v3.csv` | 19 | 113 | P006/P007 material/study/condition hierarchy, explicit unknown batch/replicate metadata, P007 aggregate-property uncertainty, and five correlated P007 stage children; all v2 rows retained | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v4` | `data/processed/master_19papers_recovery_v4.csv` | 19 | 118 | Verified P008 six-state hierarchy and condition-scoped recovery; all v3 rows retained, five exact rows added, one legacy row exactly mapped, and ambiguous C01 excluded from duplicate counting | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v5` | `data/processed/master_19papers_recovery_v5.csv` | 19 | 127 | Verified P010 hierarchy: all 118 v4 rows unchanged, three exact alloy conditions and six correlated stages appended, with measured chemistry, magnetism, effective-target corrections, and provenance | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v6` | `data/processed/master_19papers_recovery_v6.csv` | 19 | 137 | Verified P011 hierarchy: all 127 v5 rows unchanged, four exact primary conditions and six correlated stages appended; source states, method-separated SFE, chemistry scopes, corrections, and provenance retained | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v7` | `data/processed/master_19papers_recovery_v7.csv` | 19 | 163 | Verified P012 hierarchy: all 137 v6 rows unchanged, six exact primary conditions and twenty correlated stages appended; measured/nominal chemistry, initial twins, method/temperature-specific SFE/DeltaG, targets, and provenance retained | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v8` | `data/processed/master_19papers_recovery_v8.csv` | 19 | 169 | Verified P013 hierarchy: all 163 v7 rows unchanged, one exact condition and five canonical landmark children appended; interval chronology remains supporting-only | HISTORICAL RECOVERY DATASET / PRESERVED |
| `master_19papers_recovery_v9` | `data/processed/master_19papers_recovery_v9.csv` | 19 | 178 | Verified P014 hierarchy: all 169 v8 rows unchanged, five exact primary conditions and four correlated A600 stages appended; legacy rows retained but excluded from replacement double counting | HISTORICAL RECOVERY DATASET / PRESERVED |
| `master_19papers_recovery_v10` | `data/processed/master_19papers_recovery_v10.csv` | 19 | 180 | Verified P015 hierarchy: all 178 v9 rows unchanged and two exact experimental temperature conditions appended; eight MD stages remain supporting-only | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v11` | `data/processed/master_19papers_recovery_v11.csv` | 19 | 192 | Verified P017 computational hierarchy: all 180 v10 rows unchanged and twelve exact MD tensile conditions appended in an experimental-target-ineligible domain | CURRENT RECOVERY DATASET / CANONICAL BASE UNCHANGED |
| `master_19papers_recovery_v12_qc` | `data/processed/master_19papers_recovery_v12_qc.csv` | 19 | 192 | Non-destructive global QC annotation of immutable recovery v11; all 334 source columns are cell-preserved, nine QC metadata columns are appended, and separate indexes retain 51 replacement-aware experimental conditions and 12 P017 computational conditions | CURRENT GLOBAL-QC DATASET / SCIENTIFIC VALUES UNCHANGED |
| `master_19papers_recovery_v13` | `data/processed/master_19papers_recovery_v13.csv` | 19 | 207 | Verified P002 source-specific recovery over immutable V12-QC: all 192 input rows and 343 input columns are cell-preserved; three exact annealing-defined replacements, ten correlated mechanism observations, two Hall-Petch support states, and field-level provenance are appended | HISTORICAL RECOVERY DATASET / PRESERVED |
| `master_extended_recovery_v14` | `data/processed/master_extended_recovery_v14.csv` | 20 | 214 | Verified P020 extension over immutable recovery V13: all 207 V13 rows and all 390 V13 columns are cell-preserved; one new independent in-situ tensile condition and six correlated stage/end-point observations are appended with phase-specific target and field provenance | HISTORICAL EXTENDED RECOVERY DATASET / PRESERVED |
| `master_extended_recovery_v15` | `data/processed/master_extended_recovery_v15.csv` | 21 | 219 | Verified P021 extension over immutable recovery V14: all 214 V14 rows and all 454 V14 columns are cell-preserved; five exact independent experimental tensile conditions are appended with grain-size/test-state hierarchy, source-scoped targets, leakage controls, and exhaustive field provenance | HISTORICAL EXTENDED RECOVERY DATASET / PRESERVED |
| `master_extended_recovery_v16` | `data/processed/master_extended_recovery_v16.csv` | 22 | 227 | Verified P022 extension over immutable recovery V15: all 219 V15 rows and all 497 V15 columns are cell-preserved; five separately fabricated as-cast chemistry conditions and three correlated 40%-strain EBSD children are appended with raw atomic-ratio formulas, source-graded targets, leakage controls, and exhaustive field provenance | HISTORICAL EXTENDED RECOVERY DATASET / PRESERVED |
| `master_extended_recovery_v17` | `data/processed/master_extended_recovery_v17.csv` | 23 | 234 | Verified P023 extension over immutable recovery V16: all 227 V16 rows and all 524 V16 columns are cell-preserved; seven exact FSP/annealing tensile conditions are appended, while ten pre-test phase states, 750 C support-only states, before/after evidence, curve-inferred onset, local EDS, Thermo-Calc context, and physics gaps remain scope-separated with exhaustive provenance | CURRENT EXTENDED RECOVERY DATASET / GLOBAL QC-SCHEMA-SPLITS REQUIRE REFRESH |

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

P022 establishes a raw atomic-ratio composition rule: formulas of the form Fe50Mn30Co10Cr10CxMoy are preserved exactly as reported with `Original_Composition_Basis=ATOMIC_RATIO_AS_REPORTED`. The x/y additions are not automatically normalized to 100 at.%, and normalized elemental fields remain NA unless a source explicitly reports them. This is source preservation, not chemistry reconciliation; the rule applies whenever a paper reports an unnormalized atomic-ratio formula.

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

Source text such as “room temperature” remains raw text when no exact numeric temperature is supplied; it must not be converted automatically to 298 K. A missing tensile strain rate remains NA/NOT_REPORTED. Overall flat-specimen dimensions are retained separately and are not silently promoted into gauge-length/width/thickness fields when the source does not define them as gauge geometry.

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

An XRD “single-FCC matrix” statement does not erase a secondary phase directly observed by microscopy; P022 C4 therefore retains direct interdendritic carbide evidence alongside its XRD matrix description. Possible sigma precipitation mentioned only through prior-work discussion is not current-paper measured evidence. General literature SFE ranges or thresholds remain support-only context and never become alloy-specific numeric SFE; qualitative C/Mo direction statements remain nonnumeric.

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

Pre-existing martensite does not by itself establish TRIP. Initial twins and annealing twins do not establish TWIP. Processing-induced transformation and phase reversion do not by themselves establish TRIP. Pre-test stacking faults generated during cryogenic immersion remain initial-state evidence and do not establish TWIP. These phenomena remain scientifically relevant descriptors, but are distinct from deformation-induced target mechanisms. When the source resolves the twinning phase, a positive TWIP label must retain a phase tag and mode rather than silently becoming FCC twinning. P013 and P020 contain HCP-phase tensile/compression-twinning evidence; P021 RT40 contains direct low-abundance mechanical-twin occurrence with unresolved twin-phase identity, which supports TWIP=1 at a lower evidence grade without implying dominance. P022 distinguishes author-attributed condition evidence from direct microscopy: C0 TRIP=1 is medium-grade author attribution, while C2/C2Mo1/C2Mo2 TWIP=1 comes from direct 40%-strain EBSD. “TRIP-to-TWIP” or dominance wording never creates TRIP=0, and missing twin/phase microscopy never creates a negative label. This preservation rule does not itself redefine the global target. Any future definition change requires a new Decision Log entry; old definitions and decisions must not be erased.

### P023 recovery-v17 source-specific semantics

P023 represents the nominal `Fe39Mn20Co20Cr15Si5Al1` at.% family under one FSP/annealing material parent. Vacuum arc casting, double-pass FSP, and the 650/750/850 C by 5/15/30 min water-quenched grid remain explicit processing hierarchy. The ten D-pass/annealed phase-fraction states are pre-test support records. Exactly seven states have primary tensile conditions; all three 750 C states are supporting-only and never become primary conditions or pseudo-samples. The reported three specimens per condition remain `Replicate_n=3` aggregate metadata with unknown physical-batch and replicate identity.

Nominal composition, measured-bulk composition, and local chemistry remain distinct. P023 measured bulk/post-melt chemistry is NA. The quantitative as-cast and D-pass Fig.1e EDS values are local elemental-distribution measurements only; they never overwrite nominal chemistry or become bulk chemistry. No composition value is normalized, no annealed grain-size or matrix-Al curve is digitized, and the as-cast 120 +/- 12 um grain size remains supporting material-state information while D-pass 0.79 +/- 0.05 um is the only recovered primary-state grain size.

All ten Fig.2c FCC/HCP fractions are pre-tensile processing-state evidence. Initial HCP, including 0.70 for 650-15 and 0.57 for 850-30, does not itself establish tensile TRIP. P023 assigns TRIP=1 only where direct before/after EBSD shows tensile FCC loss and HCP-epsilon increase: 0.30/0.70 to 0.06/0.94 for 650-15 and 0.43/0.57 to 0.10/0.90 for 850-30. Both conditions also retain TWIP=1 with `TWIP_Phase=HCP_EPSILON` and Slip=1 from direct epsilon-phase twinning and `<c+a>` slip. This is HCP-epsilon twinning, not silently reinterpreted FCC deformation twinning. The other five tensile conditions remain TRIP/TWIP/Slip NA with `INSUFFICIENT_FOR_ZERO`; work-hardening curves alone create neither positive nor negative labels.

P023 post-test phase fractions, twins, GND/dislocation information, and IPF evidence are target/leakage records, never pre-test predictors. The 650-15 onset values (924 MPa true stress, approximately 840 MPa engineering stress, approximately 10% strain/elongation association, and 2983 MPa WH rate) remain curve-inferred or mechanical-response-derived metadata; no direct experimental stage row is created. Thermo-Calc/TCHEA2 remains computational context and its equilibrium predictions never override EBSD/XRD observations. Current-paper alloy-specific numeric SFE and FCC-to-HCP DeltaG remain NA without calculation or cross-paper transfer.

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

Post-deformation variables, mechanism evidence text, label-confidence fields, and direct outcomes must also be screened for feature/target leakage before modelling. Processing-induced TRIP/TWIP and pre-test or annealing twins are precursor history, not tensile-mechanism targets. Source-modality conflicts must remain explicit rather than be silently reconciled. Mechanically derived HDI/back-stress quantities are potential target-leakage features and are ineligible by default pending an explicit prediction-time policy.

### Feature Schema V1 and frozen prediction-time policy

Feature Schema V1 freezes the task as **pre-deformation condition-level mechanism prediction**. The prediction moment is **immediately before tensile loading begins**. A future model may use only alloy/material information, processing history, explicitly initial microstructure, planned tensile-test conditions, and method-appropriate pre-test physics information known at that moment to predict subsequent `Effective_TRIP` and/or `Effective_TWIP`. T1 (TRIP), T2 (TWIP), and T3 (joint multilabel 00/10/01/11) remain possible tasks; no final target is selected.

The authoritative column-level catalog is `data/schema/feature_schema_v1.csv`; it assigns one primary prediction-time class to every one of the 343 V12 master columns. The frozen rules are:

- Post-test/post-fracture microstructure is never a primary predictor.
- YS, UTS, elongation, uniform elongation, true properties, work hardening, fracture mode, and other same-test mechanical outcomes are never primary predictors.
- Strain-stage, interrupted-test, in-situ, and other evidence observed after loading starts is target/stage evidence only, not a pre-deformation predictor.
- Loading-response-derived HDI/back stress, strengthening, critical-stress, onset, dynamic-heating, and fitted response fields are permanently blocked.
- Paper, DOI, condition, observation, study, material, batch, replicate, parent, and leakage-group identifiers are identity/grouping controls and never ordinary predictors.
- Source, evidence, method, confidence, review, QC tier/status, and provenance fields are audit/eligibility controls and never ordinary predictors.
- Initial/annealing twins may describe the pre-test state but never establish TWIP; pre-existing or processing-induced martensite/HCP may describe the initial state but never establish tensile TRIP.
- Measured bulk chemistry and nominal chemistry remain distinguishable. The documented future conflict policy prefers measured bulk chemistry when present and otherwise nominal chemistry, but V1 does not implement a merged composition. Local EDS/APT/TEM and feedstock chemistry never silently become specimen bulk chemistry.
- SFE and DeltaG retain method, phase/structure, temperature, paper, and domain scope. Experimental, thermodynamic/CALPHAD, DFT 0 K, MD, P017 FCC stable gamma_sf, and P017 BCC unstable gamma_usf values are not collapsed. P016's assumed 18 mJ/m2 input is not a direct material measurement.
- The 51 replacement-aware experimental conditions and twelve P017 computational conditions remain separate. P017 native labels, GSFE, PTM, SIS/UTS-PSR, MD rates, and trajectory data cannot enter the experimental feature matrix or target pool.

The cumulative untransformed source-column groups are: **M1_CHEMISTRY**; **M2_CHEMISTRY_PLUS_TEST**; **M3_PLUS_PROCESSING**; **M4_PLUS_PHYSICS**; and **M5_PLUS_INITIAL_MICROSTRUCTURE**. `data/schema/feature_sets_v1.csv` records candidates and non-model method/scope controls. `data/schema/feature_priority_v1.csv` uses `CORE_V1`, `OPTIONAL_V1`, `EXPLORATORY_LATER`, and `NOT_ELIGIBLE` based on scientific relevance, scope, heterogeneity, and coverage rather than a numeric coverage threshold alone. M2 is the recommended initial schema baseline for split design; sparse M4 physics and detailed M5 fields remain optional/ablation candidates.

Feature Schema V1 performs no imputation, encoding, normalization, composition reconciliation, feature engineering, synthetic-data generation, or ML training. It creates no transformed training matrix. The full policy and readiness decision are in `reports/PREDICTION_TIME_LEAKAGE_POLICY_V1.md` and `reports/FEATURE_SCHEMA_V1_AUDIT.md`.

### Grouped Split Design V1

**Post-V17 status:** this section records the frozen V12 design and its counts; it is retained for reproducibility but is stale after P002 recovery V13 and the P020/P021/P022/P023 extensions. No candidate, manifest, M2 completeness statistic, group-support result, or four-state count below may be used as current V17 evidence until Global QC, coverage/schema statistics, and grouped split feasibility are refreshed. V17 includes the P021 Fe50Mn17.5Cr12.5Co10Ni5Si5 family, five P022 chemistry variants within one strict P022 study group, and seven P023 FSP/annealing siblings within one strict P023 study/material group; no frozen V12 split artifact has been edited to accommodate them.

Grouped Split Design V1 freezes the evaluation unit as one replacement-aware independent experimental `ML_Condition_ID` from `experimental_condition_index_v12.csv`. The 51-condition roster excludes stage children, legacy replacements/collapsed rows, summaries, replicate-count metadata, all computational conditions, and every P017 MD record. T1 is binary `Effective_TRIP` on 32 usable conditions (27/5); T2 is binary `Effective_TWIP` on 30 (24/6); T3A is the four-state 00/10/01/11 target on 27 jointly labelled conditions, while T3B is a possible future two-output multilabel formulation. No target value or class definition is changed.

The audited hierarchy is `Paper_ID`, `Study_Series_ID`, `Material_Parent_ID`, `Physical_Batch_ID`, `Leakage_Group_Strict`, and `Leakage_Group_Material`. The recommended split control is **`Leakage_Group_Strict` with a conservative `Paper_ID` fallback**. Nineteen conditions lack explicit strict/study/material keys, so same-paper conditions remain together rather than receiving invented group identities. All 51 physical-batch IDs are missing; effective batch audit groups use material/paper fallbacks only as split controls and never assert a physical batch. At present the 12 effective strict groups coincide with the 12 papers contributing independent experimental conditions.

**Group independence wins over exact stratification.** No ordinary row-random split is scientifically valid when a paper, material, composition/alloy family, processing family, temperature series, or strain-rate series could cross training and validation. Pure one-material-out folds that leave sibling materials from the same strict study in training are also invalid. Valid candidates have zero paper, study, material, and strict-group overlap. Multiple deterministic grouped holdouts may be retained for allocation sensitivity, but arbitrary seed hunting and stochastic repetition to manufacture balance are prohibited.

Negative support is the binding limitation. Full T1 negatives occur in four papers/strict groups and full T2 negatives occur in four; P001 supplies three of six T2 negatives. Raw M2 complete cases are T1 17 positive/2 negative across only two negative-supporting papers and T2 14 positive/6 negative across four. Accordingly, the primary T1 M2 design is the deterministic strict-grouped holdout family (`T1_GH_STRICT_01` first); label-blind strict GroupKFold k=2 is class-supported on the full T1 roster but is M2-incompatible, and k=3/4/5 fail full-roster fold support. The primary T2 design is strict GroupKFold k=2; k=4 and deterministic grouped holdouts are secondary robustness designs. LOPO is not a complete class-supported design for either target. Nested CV is statistically excessive at the current group/minority support.

T3A is frozen as **`T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE`** because state 00 is a singleton and cannot occur independently in both training and validation. Classes are not merged or hidden. T3B may be reconsidered only as an exploratory output-wise binary evaluation using strict T1/T2-compatible groups; that does not validate four-state discrimination or state 00.

Future generalization claims use: **G1**, new condition of a related material (intentional material overlap; exploratory interpolation only); **G2**, unseen material parent/alloy variant (valid-limited only when the enclosing strict study/paper is also held); and **G3**, unseen study/paper family (valid-limited through class-supported multi-paper grouped partitions, not universal LOPO). An exact, unparsed source-text family audit identifies `Fe50Mn30Co10Cr10` across P003/P011/P013/P014. The retained deterministic holdouts separate exact source families for limited G2 use; GroupKFold remains a G3 design when that family crosses folds. This exact-text control is not chemistry reconciliation, and differently written but chemically equivalent families remain unresolved.

Before any matrix construction, measured bulk chemistry is preferred only when it is explicitly valid bulk specimen/material evidence; otherwise nominal composition is used, and a future `Composition_Source` must retain `MEASURED_BULK` or `NOMINAL`. Local EDS, APT, TEM-local, scanned-region, precipitate, grain-boundary, and feedstock chemistry never silently substitute for bulk. Grouped Split Design V1 applies no chemistry reconciliation. It also freezes **no resampling**: no duplication, oversampling, undersampling, SMOTE, or synthetic alloy/sample generation. No ML training, algorithm selection, transformed matrix, imputation, encoding, normalization, descriptor calculation, prediction, or performance metric has occurred. Authoritative outputs are `reports/VALIDATION_ARCHITECTURE_V1.md`, `reports/SPLIT_DESIGN_V1_AUDIT.md`, and the versioned candidate/manifest files under `data/splits/`.

## 11. Current Dataset Status

Repository-generated reports establish:

- A lightweight GitHub research-project library indexes and scientifically screens 12 supplied project/project-family references across SFE, CALPHAD, HEA, atomistic, and materials-ML categories. Every entry records scientific role, FeMnCoCrN relevance, allowed usage, and a final project-specific priority. Repositories remain linked rather than cloned; ambiguous project-family names retain GitHub discovery links and only provisional family-level evaluations pending exact owner/repository resolution. This resource imports no scientific data or values and changes no dataset, target, or model state.

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
- Recovery v3 preserves all 108 recovery-v2 rows and appends five P007 interrupted-test child observations (113 rows total). P006 has three distinct composition material parents under one strict study series; P007 has five annealing-time ML conditions under one material parent and study series. Batch IDs, replicate IDs/counts, and the meaning of Table 3 ± values remain unknown rather than inferred. The P007 children add zero independent ML conditions, and no target decision changes.
- Recovery v4 preserves all 113 v3 observations, adds five exact P008 records, maps P008_C02 to N2.6-PC, and retains ambiguous P008_C01 under manual review/excluded from duplicate counting. P008 has six exact conditions in two material parents under one strict study series. A strict role-based recount identifies 40 independent experimental condition rows (36 in v3), correcting the earlier 58 estimate that did not consistently enforce the independent-role eligibility gate; usable effective-label counts are 30/27/27 for TRIP/TWIP/joint.
- Recovery v5 preserves every v4 row unchanged and appends three exact P010 alloy conditions plus six correlated stage children (127 rows). P010 shares one strict study series but retains three alloy-specific material parents. Strict independent-condition count is 43; effective usable counts are 33/30/30 for TRIP/TWIP/joint. Alloy III legacy 0/0 remains in its original row while the exact recovered condition is effectively 1/1.
- Recovery v8 preserves all 163 v7 rows, adds exactly one P013 independent condition and five landmark children (169 rows), and retains four interval definitions outside the master. Strict independent conditions are 49 and usable effective TRIP/TWIP/joint counts are 34/32/29. P013 bulk initial thermal HCP (0.33), deformation-induced growth (to ~0.77), phase-specific TWIP, stress measures, and strengthening provenance remain scope-separated; SFE/DeltaG remain NA.
- Recovery v9 preserves all 169 v8 rows, adds five exact P014 conditions and four non-independent A600 stage children (178 rows), and excludes the five retained legacy representations from replacement double counting. Strict independent conditions remain 49; usable effective TRIP/TWIP/joint counts are 30/28/25 because four unsupported legacy 1/1 labels become NA/NA in exact rows while A600 remains verified 1/1. Nominal-only chemistry, missing tensile temperature, unknown +/- statistic type, processing-induced CR mechanisms, twin origin, A650 EBSD/XRD conflict, A600 chronology, and HDI leakage are explicit.
- Recovery v10 preserves all 178 v9 rows and appends exactly two experimental P015 conditions (180 rows). The two retained hybrid/computational-role legacy rows map to, but do not replace-count with, exact 298 K and 77 K conditions. Strict independent conditions increase 49→51 and usable effective TRIP/TWIP/joint counts increase 30/28/25→32/30/27. Eight MD snapshots remain outside the master in a supporting computational-stage table. P015 establishes a strong initial-to-final TRIP=0 at 298 K and verified 1/1 at 77 K.
- Recovery v11 preserves all 180 v10 rows and appends exactly twelve P017 MD tensile conditions (192 rows) under two molar-ratio material parents and `P017_SERIES01`. Independent experimental conditions and usable effective TRIP/TWIP/joint counts remain 51 and 32/30/27. P017 paper-native labels describe reversible BCC↔FCC(HCP/SF) transformation and principally BCC nanotwinning, remain target-ineligible, and never populate experimental effective targets. Five longitudinal atomistic sequences remain non-independent supporting records. FCC stable gamma_sf and BCC unstable gamma_usf remain distinct 0 K EAM features.
- Recovery v12 QC preserves all 192 v11 rows and 334 scientific/provenance columns, adds nine audit-only columns, and publishes separate 51-condition experimental and twelve-condition computational indexes. It changes no scientific value.
- Recovery v13 preserves all 192 V12-QC rows and all 343 input columns, appends three exact P002 processing conditions, ten correlated evidence records, and two non-independent Hall-Petch support states (207 rows, 390 columns). Three P002 legacy primary rows map to exact replacements, so independence remains 51. Verified A600 `NA/NA` replaces unsupported effective legacy `0/0`, changing usable TRIP/TWIP/joint support to 31/29/26 with 27/4 and 24/5 binary class counts and joint states `10=5`, `01=4`, `11=17`, `00=0`. V12 QC/schema/splits are therefore stale.
- Extended recovery v14 preserves every V13 row and all 390 V13 columns, then appends one exact P020 independent experimental condition and six non-independent real-time neutron observations (214 rows, 454 columns). P020 is a new DOI/source rather than a legacy replacement, so replacement-aware experimental support increases 51→52. Usable TRIP/TWIP/joint counts become 32/30/27; binary classes are 28/4 and 25/5, and joint states are `10=5`, `01=4`, `11=18`, `00=0`. P020 retains initial FCC/HCP 0.79/0.21, HCP-specific TWIP, and missing supplement/SFE/DeltaG fields without inference. All existing QC/schema/split statistics remain stale.
- Extended recovery v15 preserves every V14 row and all 454 V14 columns, then appends exactly five independent P021 tensile conditions (219 rows, 497 columns) with no child or pseudo-replicate rows. Replacement-aware experimental support increases 52→57. Usable TRIP/TWIP/joint support becomes 34/31/28; binary classes are 30/4 and 26/5, and joint states are `10=5`, `01=4`, `11=19`, `00=0`. P021 contributes direct RT40 TRIP/TWIP, direct 77 K TRIP with TWIP unresolved, three source-conservative unresolved RT grain-size states, exact mechanics, pre-test microstructure, and post-test leakage evidence. Global QC/schema/split statistics remain stale.
- Extended recovery v16 preserves every V15 row and all 497 V15 columns, then appends five independent P022 as-cast chemistry conditions and three correlated 40%-strain EBSD children (227 rows, 524 columns). Replacement-aware experimental support increases 57→62. Usable TRIP/TWIP/joint support becomes 35/34/28; binary classes are 31/4 and 29/5, while joint states remain `10=5`, `01=4`, `11=19`, `00=0`. P022 adds medium-grade author-attributed C0 TRIP and direct EBSD TWIP for C2/C2Mo1/C2Mo2, no negative or joint-labelled condition, and raw unnormalized chemistry/missing-metadata safeguards. Global QC/schema/split statistics remain stale.
- Extended recovery v17 preserves every V16 row, all 524 V16 columns, source values, missingness states, and row order, then appends exactly seven independent P023 room-temperature tensile conditions (234 rows, 584 columns) without supporting-state, stage, or pseudo-replicate rows. Replacement-aware experimental support increases 62→69. Usable TRIP/TWIP/joint support becomes 37/36/30; binary classes are 33/4 and 31/5, while joint states become `10=5`, `01=4`, `11=21`, `00=0`. P023 contributes two direct before/after FCC-to-HCP TRIP positives and two HCP-epsilon TWIP positives, keeps five conditions unresolved, and retains ten pre-test processing states in supporting tables. Global QC/schema/split statistics remain stale.

## 12. Known Problems and Limitations

| Issue ID | Description | Scientific impact | Priority | Status | Resolution |
|---|---|---|---|---|---|
| ISS-001 | Mechanism-label ambiguity remains for P007 A600-5 and other queued papers; P016's two 400 C conditions and 750 C/10 min and P002 A600 correctly remain unresolved rather than forced binary. | Targets may be biased or semantically inconsistent. | P1 | UNDER_REVIEW | Recovery v13 preserves P002 A600 legacy `0/0` only as original labels and sets the exact replacement's effective targets to `NA/NA` because “hindered/suppressed” is insufficient negative evidence. Continue source-specific review without inferring negatives. |
| ISS-002 | Computational/model rows coexist with experimental rows. | Silent pooling would confound domains and independence. | P1 | RESOLVED_ARCHITECTURALLY | Separate V12 condition indexes and Feature Schema V1/domain manifest freeze the boundary: P017 and other non-equivalent computational-only fields cannot enter the experimental predictor or target pool. Future analyses must preserve this rule. |
| ISS-003 | Repeated deformation-stage rows are correlated. | Random row splits would leak parent information and inflate performance. | P1 | RESOLVED_ARCHITECTURALLY | Parent/stage identities and split-group invariants are explicit in recovery v3; grouped validation remains mandatory in any future modelling. |
| ISS-004 | P006/P007 material-parent and study-series linkage required source resolution; physical batch and replicate identity are not reported. | Conflating unknown batch/replicate metadata with hierarchy could either leak siblings or fabricate identities. | P1 | RESOLVED | Recovery v3 establishes three P006 material parents under one study series and five P007 conditions under one material parent/study series. Batch and replicate fields remain NA and are metadata limitations, not hierarchy blockers. |
| ISS-005 | Small and imbalanced independent target classes. | Limits stable training, calibration, subgroup evaluation, and performance claims. | P1 | OPEN | V17 has 33/4 TRIP and 31/5 TWIP positive/negative conditions. P023 adds two positives to each target and two joint positives but no negative-family support. V12 group-support and M2 figures are stale; refresh them only after the current collection batch. Expand diverse independent negatives without fabrication or resampling. |
| ISS-006 | Extended recovery V17 replacement-aware counting identifies 69 independent experimental ML conditions, with only 37 TRIP-labelled, 36 TWIP-labelled, and 30 jointly labelled. | Effective sample size remains small despite 234 master rows. | P1 | OPEN | P023 contributes seven exact independent conditions, but five remain unresolved for both targets. V12 split candidates cannot be reused as current; rerun Global QC, coverage/schema statistics, and grouped split design before matrix construction. |
| ISS-007 | V12 reported grain size as 56.12% missing; V13 added scoped P002 sizes, V14 added an approximately 40 um P020 FCC-average size, V15 added exact P021 sizes, and V17 adds the P023 D-pass value 0.79 ± 0.05 um. P023 as-cast 120 ± 12 um is supporting material-state information, while annealed grain sizes remain NA. | Important microstructure dependence may be omitted or selection-biased. | P2 | OPEN | Refresh V17 coverage after collection; retain phase/state and twin-boundary-exclusion definitions instead of merging scopes, keep P022 numeric grain size NA, and never digitize P023 annealed grain-size curves. |
| ISS-008 | V12 reported SFE as 75.51% missing and methods are heterogeneous; V13 recovers a P002 thermodynamic estimate, P021 contributes only an author-inferred upper bound, P022 has qualitative/general support only, and P020/P023 remain numeric NA. | Sparse/method-confounded phase-stability descriptor. | P2 | OPEN | Keep P020-P023 numeric SFE NA where direct current-paper values are absent. Preserve method/temperature/paper scope, refresh coverage later, and perform no imputation or cross-paper transfer. |
| ISS-009 | V12 reported DeltaG as 92.86% missing; V13 recovers P002 `-292 J/mol` at 300 K by Thermo-Calc TCFE7, while P020, P021, P022, and P023 remain NA. | Phase-stability modelling is poorly supported. | P2 | OPEN | Refresh V17 coverage later and retain sign, temperature, CALPHAD method, alloy, and paper scope; never calculate or transfer P020-P023 DeltaG. |
| ISS-010 | V12 initial FCC/HCP coverage is stale. V13-V16 add scope-specific initial-state evidence, and V17 adds ten exact P023 pre-test FCC/HCP records spanning D-pass and the 650/750/850 C annealing grid. | Initial state can be confused with deformation-induced transformation or tensile twinning, and a matrix phase description can obscure secondary phases. | P2 | OPEN | Refresh V17 coverage while preserving each measurement/state scope. P023 initial HCP never establishes tensile TRIP; only direct before/after phase change supports its positive TRIP labels. |
| ISS-011 | Source batches retain noncanonical/unmapped fields and free-text schema inconsistencies. | Automated harmonization can lose meaning. | P2 | UNDER_REVIEW | Safe aliases applied; extras retained in `Unmapped_Fields`; 2/4 batches still need schema review. |
| ISS-012 | Elemental and binary-enthalpy reference tables contain headers only; constants and citations are undocumented. | Most alloy descriptors cannot be scientifically validated or calculated. | P1 | OPEN | Populate only traceable constants with references and validation tests. |
| ISS-013 | Mechanical outcomes and post-deformation descriptors could create feature leakage. | Models could predict labels using consequences of the mechanism. | P1 | RESOLVED_ARCHITECTURALLY / V17 REFRESH REQUIRED | Feature Schema V1 freezes the pre-tensile rule for 343 V12 fields. V17 has 584 columns; P023 mechanical response, SDI, work-hardening onset, post-test phase fractions, GND/dislocation information, and twins are explicitly outcome/target evidence and never pre-test predictors. Inventory and coverage must be regenerated before use. |
| ISS-014 | No final target or final ML-ready dataset exists. | Model comparison/publication claims would be premature. | P1 | OPEN | P023 V17 adds two jointly positive conditions, but joint `00` remains absent. V12 Feature Schema coverage and Grouped Split Design V1 are historical only and do not include P002/P020/P021/P022/P023 changes. Refresh QC/coverage/schema/splits after collection before any matrix; no model may yet be trained. |
| ISS-015 | Raw workbook row totals per batch are not stated in generated reports. | Dataset-version documentation cannot safely assign batch row counts. | P3 | DEFERRED | Reported as “Not separately reported”; generate a source-batch census if needed. |
| ISS-016 | P010 supplemental initial-phase fractions, tensile properties, method-specific absolute SFE, exact grain sizes, and batch/replicate identities are unavailable. | P010 descriptors remain incomplete; qualitative phase and relative SFE evidence cannot substitute for exact values. | P2 | OPEN | Obtain Supplemental Figs. S2/S4 and method-specific supplemental SFE evidence; preserve NA until source-supported. |

## 13. Manual Review Queue

The row-level details belong in `reports/tables/manual_review_queue.csv` (336 condition/field tasks), `mechanism_review.csv` (62 rows), `hierarchical_id_review.csv`, and `paper_manual_review_plan.csv`; they must not be duplicated or silently replaced here.

- **P1 target-label review:** P001–P007 and P010–P018. P008 exact-condition targets are reviewed; its two HOMO labels and N0-FC TWIP remain explicitly unresolved.
- **Completed P1 grouping review:** P006, P007, and P016 parent/material/condition/stage architecture is resolved. Unknown P006/P007 physical-batch and replicate identities remain explicitly NA and must not be inferred.
- **P2 recoverable-feature-only review:** P009 and P019.
- V13 partially resolves P002 grain-size, strain-rate, initial-HCP, thermodynamic-SFE, and DeltaG gaps. P002 still lacks measured bulk chemistry, exact numeric test temperature, exact numeric initial FCC fractions, experimental SFE, physical-batch/replicate identities and individual results, A600 UTS/elongation and direct post-test mechanism evidence, a numeric A800 10% HCP fraction, and direct A800 post-test twin imaging. The older generated paper plan remains a V12-era queue and must be refreshed before it is treated as current.
- V14 adds P020 as a new primary experimental source. P020 still lacks quantitative post-melt bulk chemistry, the missing supplement's tensile temperature/rate/geometry/replicate metadata, physical-batch identity, numeric alloy-specific SFE and DeltaG, and a directly reported HCP fracture fraction. Preserve all as NA; do not borrow them from P003/P011/P013/P014. Its HCP-phase TWIP tag and six correlated in-situ stages must survive future QC/schema refreshes.
- V15 adds P021 as a new primary experimental source with five exact annealing/grain-size/test-temperature conditions. P021 still lacks quantitative post-melt bulk chemistry, physical-batch and individual-replicate identities/results, exact numeric initial FCC fractions, condition-specific post-test mechanism evidence for the 10.0/19.5/149.6 um RT states, a condition-wide binary 77 K TWIP decision, direct numeric alloy-specific SFE, and DeltaG. Preserve these gaps as NA. The 77 K pre-test stacking faults, RT40 low-abundance mechanical-twin evidence, indexed-region-only post-fracture HCP fractions, and alpha-BCT/Hall-Petch leakage separation must survive future refreshes.
- V16 adds P022 as an as-cast C/Mo chemistry-perturbation study with five material parents/primary conditions and three correlated 40%-strain EBSD children. P022 still lacks quantitative post-melt bulk chemistry, physical-batch and replicate identities/count/results, exact numeric test temperature and strain rate, exact FCC fractions, numeric grain sizes, direct C0 phase evolution, C4 mechanism evidence, condition-wide TRIP evidence for C2/C2Mo1/C2Mo2, twin fractions, numeric alloy-specific SFE, and DeltaG. Preserve these gaps as NA. Raw atomic-ratio formulas, C0 author-attributed evidence grade, direct TWIP stage provenance, C4 carbide/XRD coexistence, and the no-negative-from-TRIP-to-TWIP rule must survive future refreshes.
- V17 adds P023 as one Fe39Mn20Co20Cr15Si5Al1 material family with seven exact primary tensile conditions and ten pre-test processing-state records. P023 still lacks measured bulk chemistry, physical-batch and individual-replicate identities/results, exact numeric room temperature, annealed numeric grain sizes and matrix-Al curve values, exact mechanics for D-pass/650-5/850-X, direct condition targets for D-pass/650-5/650-30/850-5/850-15, numeric current-paper SFE, and DeltaG. Preserve these gaps as NA. Local EDS separation, 750-X supporting-only status, initial-HCP safeguards, HCP-epsilon TWIP phase tags, curve-inferred onset classification, post-test leakage, and Thermo-Calc observation/prediction separation must survive future refreshes.
- **Completed/reduced by recovery v1:** P006/P007 condition identities and three new target-availability gaps; P006 grain size, DFT 0 K intrinsic SFE, Thermo-Calc 300 K DeltaG, and mechanical-property evidence; P007 initial HCP fractions and mechanical-property verification. Method-specific values remain separate rather than closing experimental-SFE gaps.
- **Still manual:** P006/P006_MC01 and MC03 TWIP and P007 A600-5 TRIP/TWIP target evidence. P006/P007 batch/replicate metadata remain unknown unless future source evidence supports them; this no longer blocks the resolved hierarchy.
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
| 1 | Data extraction | IN PROGRESS: the original 19-paper extraction is preserved; P020, P021, P022, and P023 form the verified extended-source recovery set beyond P019. |
| 2 | QC and provenance | IN PROGRESS: V12 global QC remains preserved; P002 V13 and P020-P023 V14-V17 add field-level provenance. V17 Global QC and coverage refresh remain required after the current source-collection batch. |
| 3 | Hierarchical experimental identity | IMPLEMENTED WITH CONSERVATIVE FALLBACKS: V17 has 69 replacement-aware conditions. P023 adds seven tensile siblings under one strict series and one material parent; ten processing states remain supporting-only and no replicate/stage row is appended. Physical-batch and individual-replicate metadata remain NA. The full V17 index must be regenerated. |
| 4 | Target verification | IN PROGRESS: operational definitions and queue exist; source verification incomplete. |
| 5 | Targeted literature expansion | IN PROGRESS: P020, P021, P022, and P023 are the first four new verified primary experimental papers beyond P001-P019; additional collection may continue before global refresh. |
| 6 | Pilot ML | NOT STARTED; not scientifically justified yet. |
| 7 | Feature engineering | INFRASTRUCTURE ONLY; `log10_strain_rate` implemented, constants-dependent features blocked. |
| 8 | Model comparison | NOT STARTED. |
| 9 | Grouped/external validation | V12 SPLIT DESIGN V1 PRESERVED BUT STALE FOR V17: P002/P020/P021/P022/P023 changed target support, joint `00` remains zero, and P023 adds seven siblings within one strict study/material group. Rerun grouped feasibility after collection and before matrix construction. No model validation or performance result has occurred. |
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
| DEC-012 | 2026-08-26 | Represent P008 as six exact processing-state conditions under two material parents and one strict study series; retain C01 as manual review and map only C02 exactly. | Chemistry, processing, and evidence support six state identities, but the generic legacy C01 state is not proven and must not be double-counted. | `reports/P008_RECOVERY_V4_AUDIT.md`; `reports/tables/p008_recovery_v4_hierarchy.csv` | IMPLEMENTED |
| DEC-013 | 2026-08-26 | Keep P008 phase/SFE evidence scope-specific: BCC alpha is separate from HCP/TRIP, FCC complements remain NA, and alloy-level SFE is not duplicated into condition fields. | Phase identity and measurement scope are scientifically non-interchangeable; complements and state assignments would be unsupported derivations. | `reports/tables/p008_recovery_v4_provenance.csv`; `reports/tables/p008_recovery_v4_corrections.csv` | IMPLEMENTED |
| DEC-014 | 2026-08-26 | Represent P010 as three exact alloy conditions plus six non-independent stage children; preserve legacy targets and apply Alloy III 1/1 only through recovered/effective fields. Keep approximate magnetic transitions, low-temperature behavior, PM/AFM computation, and relative SFE trends scope-separated. | Minor deformation-induced HCP is positive TRIP evidence, repeated stages are correlated, and neither qualitative phase identity nor relative/static computational SFE supports fabricated numeric values. | `reports/P010_RECOVERY_V5_AUDIT.md`; `reports/tables/p010_recovery_v5_corrections.csv` | IMPLEMENTED |
| DEC-015 | 2026-08-26 | Represent P017 as twelve independent computational conditions under two molar-ratio material parents and one strict series, never as experimental conditions or replicates; keep longitudinal snapshots correlated and supporting-only. | Extreme-rate MD cases are distinct computational conditions, while atomic snapshots are repeated observations of their parent trajectories and cannot increase independence. | `reports/P017_RECOVERY_V11_AUDIT.md`; `reports/tables/p017_recovery_v11_computational_conditions.csv` | IMPLEMENTED |
| DEC-016 | 2026-08-26 | Keep P017 native reversible BCC↔FCC(HCP/SF) TRIP and primarily BCC nanotwinning separate from experimental FCC→HCP TRIP/FCC deformation-TWIP targets; treat PTM HCP as HCP-or-stacking-fault unless phase attribution is explicit. | The paper's native mechanism and local-structure definitions are not experimentally target-equivalent, and PTM local HCP also detects FCC stacking faults. | `reports/tables/p017_recovery_v11_source_safeguards.csv`; `reports/P017_RECOVERY_V11_AUDIT.md` | IMPLEMENTED |
| DEC-017 | 2026-08-26 | Preserve P017 FCC stable gamma_sf separately from BCC unstable gamma_usf, and retain SIS-PSR/UTS-PSR as dedicated computational stress-regime metrics. | Structure, stability definition, method, and domain differ; merging these values into generic SFE or experimental YS/UTS fields would change their scientific meaning. | `reports/tables/p017_recovery_v11_gsfe_sfe.csv`; `reports/P017_RECOVERY_V11_AUDIT.md` | IMPLEMENTED |
| DEC-0028 | 2026-08-27 | Adopt recovery V12 QC as a non-destructive audit layer over immutable recovery v11, with separate replacement-aware experimental and exact computational indexes; do not treat the QC layer as a scientific correction or an ML-ready dataset. | Global counting, domain, replacement, target, missingness, provenance, and leakage decisions must be explicit without changing source values or converting missing evidence into negatives. | `scripts/global_qc_v12.py`; `reports/GLOBAL_DATASET_QC_V12.md`; `reports/DATASET_READINESS_V12.md` | IMPLEMENTED / ML GATES OPEN |
| DEC-0029 | 2026-08-27 | Freeze Feature Schema V1 at the moment immediately before tensile loading; allow only source-supported pre-test direct/conditional fields, permanently block target/outcome/post-test/stage/loading-derived fields, and keep identifiers/groups/provenance/QC and P017 computation outside ordinary experimental predictors. | Pre-deformation TRIP/TWIP prediction must use only information genuinely available before the outcome-generating tensile test, preserve method/domain distinctions, and prevent study/dependence memorization. | `data/schema/feature_schema_v1.csv`; `reports/PREDICTION_TIME_LEAKAGE_POLICY_V1.md`; `reports/FEATURE_SCHEMA_V1_AUDIT.md`; `tests/test_feature_schema_v1.py` | IMPLEMENTED / READY FOR SPLIT DESIGN ONLY |
| DEC-0030 | 2026-08-27 | Freeze Grouped Split Design V1 around `Leakage_Group_Strict` with conservative paper fallback; group independence overrides stratification, retained holdouts also separate exact unparsed source-alloy families, T1 uses deterministic M2-compatible strict holdouts, T2 uses strict GroupKFold k=2 for G3, T3A remains invalid because 00 is a singleton, and no resampling or ML is authorized. | Related paper/study/material conditions must not cross folds; exact `Fe50Mn30Co10Cr10` text spans four papers; full negative support is only four strict groups per target; M2 reduces T1 negatives to two groups; LOPO is class-incomplete; and four-class state 00 cannot be independently represented on both sides. | `data/splits/split_candidates_v1.csv`; `data/splits/split_manifest_v1.csv`; `reports/VALIDATION_ARCHITECTURE_V1.md`; `reports/SPLIT_DESIGN_V1_AUDIT.md`; `tests/test_grouped_split_design_v1.py` | IMPLEMENTED / MATRIX-CONSTRUCTION GATE ONLY |
| DEC-0031 | 2026-08-28 | Integrate P002 as three exact 600/700/800 C processing-defined tensile conditions under one study series/material parent, retain all five legacy rows, and count only exact replacements. Preserve historical labels as `Original_*`; set exact A600 `Effective_TRIP/Effective_TWIP` to `NA/NA`. | DOI, chemistry, annealing, rate, mechanics, and targets map three legacy primary representations exactly, but “hindered/suppressed” plus missing post-test characterization cannot support binary absence. Non-destructive replacement prevents double counting and silent label revision. | `reports/P002_RECOVERY_V13_AUDIT.md`; `reports/tables/p002_recovery_v13_legacy_mapping.csv`; `reports/tables/p002_recovery_v13_decision_correction_ledger.csv` | IMPLEMENTED |
| DEC-0032 | 2026-08-28 | Apply the official 800 C > 700 C TRIP corrigendum without changing EBSD fractions; keep A700 as direct high-confidence TRIP/TWIP, A800 TWIP as medium-confidence author condition attribution rather than direct A800 TEM, and never derive tensile TWIP from pre-test annealing/processing twins. | The corrigendum fixes a comparison typo only. A700 has direct post-test TEM/SAED/HR-STEM twin evidence; A800 has direct TRIP but no dedicated post-test twin micrograph; initial twins precede tensile loading. | `reports/tables/p002_recovery_v13_corrigendum.csv`; `reports/tables/p002_recovery_v13_target_evidence.csv`; `reports/tables/p002_recovery_v13_initial_microstructure.csv` | IMPLEMENTED |
| DEC-0033 | 2026-08-28 | Preserve P002 SFE approximately 14 mJ/m2 as a 300 K current-paper thermodynamic estimate and DeltaG=-292 J/mol as a 300 K Thermo-Calc TCFE7 result; keep cited equation inputs and Hall-Petch sigma0/k method-scoped, with Hall-Petch fits classified as mechanical-response-derived leakage. | Experimental, calculated, reference-input, and response-derived quantities are not interchangeable. Transferring them across alloys/papers or treating Hall-Petch fits as pre-test primary predictors would change meaning and leak outcomes. | `reports/tables/p002_recovery_v13_physics_thermodynamics.csv`; `reports/tables/p002_recovery_v13_hall_petch_support.csv`; `reports/P002_RECOVERY_V13_AUDIT.md` | IMPLEMENTED |
| DEC-0034 | 2026-08-28 | Treat V12 Global QC, Feature Schema V1 coverage, and Grouped Split Design V1 as preserved but stale after P002 V13; do not construct matrices or train until all three layers and feature coverage are refreshed. | V13 retains 51 independent conditions but changes usable TRIP/TWIP/joint support to 31/29/26 and removes the former joint 00 observation; it also expands the source schema from 343 to 390 columns. | `data/processed/master_19papers_recovery_v13.csv`; `reports/P002_RECOVERY_V13_AUDIT.md`; `tests/test_p002_recovery_v13.py` | ACTIVE REFRESH GATE |
| DEC-0035 | 2026-08-28 | Extend stable source IDs beyond the original P001-P019 set by assigning verified new primary sources the next Paper_ID after DOI/source/duplicate review. Integrate P020 as one condition under `P020_SERIES01` and `P020_MAT_FE50MN30CO10CR10`, separate from P013 and other nominally identical alloys. | A common nominal-composition string does not establish the same melt, batch, processing state, study, or specimen. P020 is a separately prepared in-situ neutron study and has no legacy V13 representation. | `reports/P020_RECOVERY_V14_AUDIT.md`; `reports/tables/p020_recovery_v14_study_identity.csv`; `reports/tables/p020_recovery_v14_hierarchy.csv` | IMPLEMENTED |
| DEC-0036 | 2026-08-28 | Assign P020 condition targets TRIP=1/TWIP=1/Slip=1 from dynamic real-time evidence while tagging TWIP as HCP tensile/compression twinning. Initial HCP=0.21 does not establish TRIP, and six in-situ stages remain non-independent; stage-specific zeros never become condition negatives. | EBSD/neutron report initial FCC/HCP 0.79/0.21, then real-time FCC loss; neutron grain reorientation identifies HCP twinning near 400 and 730 MPa. Phase and time scope are necessary to prevent target-semantic and independence errors. | `reports/tables/p020_recovery_v14_target_evidence.csv`; `reports/tables/p020_recovery_v14_in_situ_stage_evidence.csv`; `reports/tables/p020_recovery_v14_scientific_safeguards.csv` | IMPLEMENTED |
| DEC-0037 | 2026-08-28 | Leave P020 test temperature/rate/geometry/replicate fields NA because the cited supplement is absent; store approximately 200 MPa only as observable elastic-deviation onset; leave SFE/DeltaG and fracture HCP fraction NA without cross-paper transfer or complement calculation. | The main article does not provide the missing tensile details, a conventional 0.2% offset definition, numeric P020 SFE/DeltaG, or exact HCP-at-fracture value. Inference or transfer would fabricate scientific meaning. | `reports/tables/p020_recovery_v14_processing.csv`; `reports/tables/p020_recovery_v14_mechanical_response.csv`; `reports/tables/p020_recovery_v14_phase_evolution.csv`; `reports/P020_RECOVERY_V14_AUDIT.md` | IMPLEMENTED / REFRESH GATE ACTIVE |
| DEC-0038 | 2026-08-28 | Integrate P021 as five exact independent tensile conditions under `P021_SERIES01` and the new `P021_MAT_FE50MN17p5CR12p5CO10NI5SI5` family. Treat annealing/grain-size/test-temperature combinations as condition identities, retain all siblings in one strict leakage group, and store the reported minimum of three specimens only as aggregate replicate metadata. | The source defines four RT grain-size conditions plus a 77 K test of the 40.9 um annealed state. Distinct planned tests are independent condition units, whereas reported average specimen count does not justify pseudo-replicates or batch identity. | `reports/tables/p021_recovery_v15_hierarchy.csv`; `reports/tables/p021_recovery_v15_condition_grid.csv`; `reports/P021_RECOVERY_V15_AUDIT.md` | IMPLEMENTED |
| DEC-0039 | 2026-08-28 | Assign P021 RT40 TRIP=1/TWIP=1/Slip=1 and 77K40 TRIP=1/TWIP=NA/Slip=1; leave the 10.0, 19.5, and 149.6 um RT targets NA. Grade RT40 TWIP as low-abundance, medium-strength direct occurrence with unresolved twin-phase identity. Initial annealing twins and 77 K pre-test stacking faults never generate TWIP labels. | RT40 has direct EBSD/TEM epsilon-HCP plus explicit text reporting a few mechanical twins. The cryogenic condition has strong XRD/EBSD/TEM TRIP evidence but insufficient condition-wide twin evidence for either binary value. Work-hardening plateaus and absence language do not establish mechanism labels. | `reports/tables/p021_recovery_v15_targets.csv`; `reports/tables/p021_recovery_v15_initial_microstructure.csv`; `reports/P021_RECOVERY_V15_AUDIT.md` | IMPLEMENTED |
| DEC-0040 | 2026-08-28 | Keep P021 post-fracture HCP fractions 0.149/0.562 as indexed-region-only target evidence; preserve alpha-BCT non-detection separately from positive FCC→HCP TRIP; retain raw `<23 mJ/m2` only as an author-inferred SFE upper bound with numeric SFE NA; leave DeltaG NA; and classify Hall-Petch sigma0=198 MPa/k=368 MPa um^0.5 as response-derived leakage. | Post-test phase fractions, pathway non-detection, mechanism-inferred bounds, absent thermodynamic quantities, and fits to tensile yield response have different meanings and prediction-time eligibility. Converting, transferring, or using them as direct pre-test predictors would fabricate or leak evidence. | `reports/tables/p021_recovery_v15_postfracture_evidence.csv`; `reports/tables/p021_recovery_v15_sfe_physics.csv`; `reports/tables/p021_recovery_v15_hall_petch_support.csv`; `reports/P021_RECOVERY_V15_AUDIT.md` | IMPLEMENTED / REFRESH GATE ACTIVE |

| DEC-0041 | 2026-08-28 | Integrate P022 as five exact independent as-cast chemistry conditions under `P022_SERIES01`, with one material parent per C0/C2/C4/C2Mo1/C2Mo2 variant; keep three 40%-strain EBSD observations as correlated children. Preserve Fe50Mn30Co10Cr10CxMoy formulas as `ATOMIC_RATIO_AS_REPORTED` without 100-at.% normalization or measured-bulk substitution. | The source separately fabricates five chemistry variants and reports x/y as atomic-ratio additions. Stage microscopy is repeated evidence from three parent tensile conditions, not additional samples; normalization would alter source chemistry. | `reports/tables/p022_recovery_v16_material_parents.csv`; `reports/tables/p022_recovery_v16_condition_hierarchy.csv`; `reports/tables/p022_recovery_v16_raw_composition_formulas.csv` | IMPLEMENTED |
| DEC-0042 | 2026-08-28 | Assign P022 C0 TRIP=1 only as MEDIUM author-attributed condition evidence; assign C2/C2Mo1/C2Mo2 TWIP=1 from direct 40%-strain EBSD; leave every opposite target component and all C4 targets NA. “TRIP-to-TWIP” wording, dominance, missing microscopy, and C0 initial HCP never generate negative or additional positive labels. | C0 is explicitly the paper's TRIP reference but lacks current-paper post-test phase mapping. Direct approximately 60-degree <111> deformation-twin boundaries establish TWIP occurrence in the three alloyed conditions, while condition-wide phase-transformation absence is not demonstrated. | `reports/tables/p022_recovery_v16_target_evidence.csv`; `reports/tables/p022_recovery_v16_40pct_twin_observations.csv`; `reports/P022_RECOVERY_V16_AUDIT.md` | IMPLEMENTED |
| DEC-0043 | 2026-08-28 | Retain P022 C4 direct interdendritic carbides alongside its XRD single-FCC-matrix description; keep exact RT Kelvin, strain rate, numeric grain size, current-alloy SFE, and DeltaG NA. Store only C2/C2Mo1 approximate direct-text mechanics as outcome leakage; keep SFE thresholds support-only and qualitative C/Mo trends nonnumeric. | Matrix-phase XRD and microscopy secondary-phase evidence have different scopes. The source does not report the missing test/physics values, and Figure 3, prior-work sigma discussion, literature thresholds, or a stated elongation decrease cannot supply them. | `reports/tables/p022_recovery_v16_initial_microstructure.csv`; `reports/tables/p022_recovery_v16_mechanical_response.csv`; `reports/tables/p022_recovery_v16_sfe_physics_safeguards.csv` | IMPLEMENTED / REFRESH GATE ACTIVE |
| DEC-0044 | 2026-08-30 | Integrate P023 as seven exact independent room-temperature tensile conditions under `P023_SERIES01` and `P023_MAT_FE39MN20CO20CR15SI5AL1`; retain D-pass plus nine annealed states as ten supporting pre-test phase records, with 750-X never promoted to tensile conditions. Store n=3 only as aggregate replicate metadata and keep local EDS separate from nominal and missing bulk chemistry. | The source reports seven condition-specific tensile responses, ten pre-test processing states, and three tested specimens per condition without individual identities/results. Supporting states and aggregate counts cannot become extra samples, and local elemental-distribution EDS cannot substitute for bulk chemistry. | `reports/tables/p023_recovery_v17_processing_states.csv`; `reports/tables/p023_recovery_v17_tensile_conditions.csv`; `reports/tables/p023_recovery_v17_composition_local_eds.csv`; `reports/P023_RECOVERY_V17_AUDIT.md` | IMPLEMENTED |
| DEC-0045 | 2026-08-30 | Assign P023 650-15 and 850-30 `Effective_TRIP=1`, `Effective_TWIP=1`, and `Slip=1` from direct tensile before/after FCC-to-HCP evidence plus reported epsilon-phase twinning and `<c+a>` slip. Tag both TWIP positives `HCP_EPSILON`; leave the other five condition targets NA and create no negative from missing evidence or work-hardening curves. | Pre-test HCP does not establish tensile TRIP. Direct FCC loss/HCP increase establishes the two transformations, while source-explicit twinning occurs in HCP epsilon rather than FCC. Curve shape and mechanistic discussion alone are insufficient for project-quality binary labels. | `reports/tables/p023_recovery_v17_before_after_evidence.csv`; `reports/tables/p023_recovery_v17_target_evidence.csv`; `reports/P023_RECOVERY_V17_AUDIT.md` | IMPLEMENTED |
| DEC-0046 | 2026-08-30 | Keep P023 mechanical properties, SDI, post-test phase/GND/twin evidence, and the 650-15 work-hardening-derived onset outside pre-test predictors. Classify 924 MPa true stress, approximately 840 MPa engineering stress, approximately 10% strain, and 2983 MPa work-hardening rate as current-paper curve inference rather than a direct experimental stage. Preserve Thermo-Calc/TCHEA2 only as model context and leave numeric SFE/DeltaG NA. | Outcomes and post-deformation evidence leak the mechanism target, curve-inferred onset is not an interrupted-test/microscopy observation, equilibrium predictions are not measured fractions, and the current paper reports no alloy-specific numeric SFE or FCC-to-HCP DeltaG. | `reports/tables/p023_recovery_v17_mechanical_response.csv`; `reports/tables/p023_recovery_v17_wh_onset.csv`; `reports/tables/p023_recovery_v17_thermocalc_context.csv`; `reports/tables/p023_recovery_v17_sfe_deltag_gaps.csv` | IMPLEMENTED / REFRESH GATE ACTIVE |

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

### LOG-0011 — 2026-08-26 — P006/P007 Parent and Leakage Hierarchy Resolution

**Objective**

Integrate the supplied P006/P007 parent/replicate grouping resolution into recovery v3 without pseudo-replication, leakage, target changes, or invented scientific metadata.

**Input**

Recovery v2 and `data/interim/manual_recovery/P006_P007_parent_replicate_grouping_resolution.xlsx`.

**Actions Performed**

Added reusable study-series, material-parent, physical-batch, replicate, condition-parent, strict/material leakage-group, and aggregate-property fields. Assigned three P006 composition parents and five P007 annealing conditions under their reviewed series/material hierarchy. Stored the P007 Table 3 means and uncertainties separately, and appended five interrupted-test observations as correlated children. Generated a detailed audit/table and regression tests.

**Scientific Decisions**

P006 compositions are distinct material conditions but share a strict study group. P007 annealing conditions are distinct ML conditions but siblings under one material parent and strict study group. Unknown physical batch, replicate identity/count, and ± statistic type remain NA/`UNKNOWN_REPORTED_PM`; none is inferred. Stage observations are not independent ML samples and cannot cross folds separately from their parent. Existing P006/P007 target decisions remain unchanged.

**Data Changes and Validation**

Recovery v3 has 113 rows: all 108 v2 rows in original order plus five P007 stage children. Existing scientific/source cells are unchanged; eight reviewed condition `ML_Condition_ID` values are updated. The full 22-test suite passes and checks workbook immutability, row/value preservation, exact group assignments, unknown identifiers, aggregate uncertainty semantics, zero pseudo-replicates, and child-parent split linkage. No ML was trained.

**Problems Resolved and Remaining**

ISS-004 parent/material/study linkage is resolved and may be removed from the P1 blocker list. P006/P007 unknown physical batches and replicates are genuine source-metadata limitations, not hierarchy blockers. P007 A600-5 and broader target review, domain separation, small support, empty constants, feature eligibility/leakage screening, and final-target selection remain P1 work.

**Git Commit**

Commit message: `Integrate P006 P007 grouping hierarchy into recovery v3`. The final hash is assigned after this entry is written.

### LOG-0012 — 2026-08-26 — Verified P008 Scientific Evidence Integration

**Objective**

Integrate the verified P008 workbook into recovery v4 conservatively, without modelling, derived descriptors, figure digitization, unsupported complements, or silent target/value replacement.

**Input and actions**

Verified the workbook Paper_ID/DOI and six exact source conditions. Preserved all 113 recovery-v3 rows; mapped only P008_C02 to N2.6-PC, retained P008_C01 under manual identity review, added the other five exact conditions, and established study/material leakage groups with unknown batch/replicate IDs. Generated condition, auxiliary-N, correction, and cell-provenance tables plus a detailed audit and regression tests.

**Scientific decisions and corrections**

HOMO targets remain NA. Exact effective targets are N0-PC 1/1, N0-FC 1/NA, N2.6-PC 0/1, and N2.6-FC 0/1. N2.6-PC's 0.24 pre-existing BCC alpha fraction remains separate from zero identified HCP and does not create FCC=1 or TRIP evidence. N2.6 SFE ≈26 is alloy-level current-study TEM evidence; N0 6.5 is a secondary reference. Recovery and deformation twins, local and bulk chemistry, and raw RT text versus numeric standardization remain separate. Supplementary Table S1 gaps remain NA.

**Data changes and validation**

Recovery v4 has 118 observations and six exact P008 conditions. A strict independent-role recount changes the project-wide estimate from 36 in v3 to 40 in v4; this supersedes the older 58 estimate that did not consistently apply the role eligibility gate. Usable effective TRIP/TWIP/joint condition counts change from 28/25/25 to 30/27/27. All 26 tests pass and enforce v3 preservation, hierarchy/mapping, target missingness, phase separation, nonduplicated SFE, auxiliary exclusion, and complete provenance. No ML was trained.

**Remaining problems and next step**

P008 HOMO mechanisms, N0-FC TWIP, exact RT Kelvin, exact FCC fractions, intermediate-N bulk chemistry/targets, missing Supplementary Table S1 mechanics, and batch/replicate identities remain unresolved. Continue P1 target review with P010/P011 or other queued papers before modelling; retain grouped validation and the role-based independent-count definition.

**Git Commit**

Commit message: `Integrate verified P008 evidence into recovery v4`. The final hash is assigned after this entry is written.

### LOG-0013 — 2026-08-26 — Verified P010 Scientific Evidence Integration

**Objective and input**

Integrate `P010_scientific_evidence_recovery_VERIFIED.xlsx` into recovery v5 as dataset construction only, preserving recovery v4 and all legacy target fields.

**Actions and scientific decisions**

Appended three exact alloy conditions and six correlated deformation-stage children; recovered unnormalized wet chemistry with element-wise uncertainties, processing, raw room-temperature status, geometry, qualitative initial phases, approximate magnetic transitions, computational PM/AFM scope, and qualitative relative SFE trends. Applied Alloy III's 0/0→effective 1/1 correction non-destructively. Kept stage fractions separate, children non-independent, and all siblings in one strict study leakage group with alloy-specific material groups.

**Data changes and validation**

Recovery v5 contains 127 rows, including every one of 118 recovery-v4 rows unchanged. Strict independent experimental conditions increase 40→43 and usable effective TRIP/TWIP/joint counts increase 30/27/27→33/30/30. The full 30-test suite passes, including workbook immutability, complete row preservation, hierarchy, correction, fraction separation, missingness, temperature-scope, leakage, and provenance checks. No ML or derived descriptors were produced.

**Remaining problems and next step**

Supplemental Figs. S2/S4, method-specific absolute SFE evidence, exact grain sizes, and batch/replicate identities remain unavailable; corresponding fields remain NA. Obtain those source materials and continue P1 target review before modelling.

**Git Commit**

Commit message: `Integrate verified P010 evidence into recovery v5`. The final hash is assigned after this entry is written.


### DEC-0023 — P011 evidence hierarchy and provenance (2026-08-26)

P011 uses one feedstock, one material parent, four SPS processing states, and four primary tensile conditions; A8 is source-state context only. A reported tensile n=3 is aggregate metadata and never creates pseudo-replicates. Initial Sigma3 boundaries are annealing twins and cannot establish TWIP; deformation TWIP requires condition-specific evidence. Current-paper thermodynamic SFE values remain temperature-specific, alloy-level calculated evidence and remain separate from secondary ab-initio ranges. Feedstock EDS and local A10 scanned-region EDS are distinct scopes. Exact replacements, rather than unchanged legacy rows, govern independent counting.


### LOG-0014 — 2026-08-26 — Verified P011 Scientific Evidence Integration

**Objective and input**

Integrate `P011_scientific_evidence_recovery_VERIFIED.xlsx` into recovery v6 as dataset construction only, preserving recovery v5 and original targets.

**Actions and scientific decisions**

Preserved all 127 v5 rows, appended four exact tensile conditions and six correlated stages, and exported source-state, SFE, legacy-mapping, correction, and cell-provenance tables. A8 remains source context only. The n=3 tensile count remains aggregate metadata. Feedstock and local EDS, initial and deformation HCP, initial XRD and fracture TEM lattice parameters, primary and alternative grain size, and thermodynamic versus secondary SFE remain separate. Initial Sigma3 annealing twins never create TWIP. A10-298 is effectively 1/1; A10-77 is 1/0 from explicit negative twin evidence; A9/A11 remain NA/NA.

**Data changes and validation**

Recovery v6 has 137 rows. Its 127-row prefix preserves every recovery-v5 cell in all existing columns. Four exact P011 rows replace five legacy P011 rows for strict independent counting, changing the independent estimate 43→42 and usable effective TRIP/TWIP/joint counts 33/30/30→30/27/27. Six stages add no independent samples. Regression tests cover preservation, hierarchy, targets, negative evidence, twin/HCP semantics, replicate handling, composition/SFE scopes, missingness, leakage, and provenance. No ML, derived descriptors, digitization, or fabricated values were produced.

**Unresolved issues and next step**

A9 exact UTS/UE, A9/A11 targets, 15% HCP fractions, A8 EBSD/tensile evidence, physical batch, and individual replicate identities remain NA. Broader target review, leakage-feature eligibility, domain separation, sparse descriptors, and small support remain P1/P2 blockers.

**Git Commit**

Commit message: `Integrate verified P011 evidence into recovery v6`. The final hash is assigned after this entry is written.

### DEC-0024 — P012 condition/stage evidence and composition semantics (2026-08-26)

P012 has three material parents under strict study series `P012_SERIES01` and exactly six primary tensile conditions (three alloys at 298 K and 77 K). Repeated strain observations are correlated children, never independent samples. A stage-specific negative is not promoted to a condition-level zero without explicit condition-wide negative evidence. Thus all RT conditions are TRIP NA/TWIP 1, Base-77 K and Mo-77 K are TRIP 1/TWIP NA, and C-77 K is TRIP 1/TWIP 1. Carbon's low-strain Slip+TWIP followed by TWIP+TRIP is represented chronologically, not only as a collapsed label. Measured composition is primary without normalization while nominal composition remains separate (especially measured C=0.6 versus nominal C=0.5 at.%). Initial Sigma3 boundaries are annealing twins and cannot establish TWIP. SFE and DeltaG remain calculated, method-specific, and temperature-specific; XRD n=5 applies only to lattice-parameter reliability and never creates tensile replicates.

### LOG-0015 — 2026-08-26 — Verified P012 Scientific Evidence Integration

**Objective and input**

Integrate `P012_scientific_evidence_recovery_VERIFIED.xlsx` into recovery v7 as dataset construction only, preserving recovery v6 and all legacy scientific values/targets.

**Actions and scientific decisions**

Preserved all 137 v6 rows, appended six exact tensile conditions and twenty non-independent stage observations, and exported hierarchy, stage, physics, provenance, legacy-mapping, and decision/correction tables. Recovered unnormalized measured and separate nominal chemistry, full processing/test context, two grain-size definitions, phase absence without fabricating FCC=1, initial annealing-twin fractions, lattice parameters with XRD-only replicate scope, calculated SFE/DeltaG at both temperatures, directly reported mechanics, and strict effective targets. Original legacy targets remain unchanged and are separately represented on exact rows; exact replacements govern use without duplicate counting. No Base/Mo cryogenic mechanics, numerical friction stress, derived descriptors, normalized chemistry, figure digitization, or pseudo-replicates were created.

**Data changes and validation**

Recovery v7 has 163 rows: the unchanged 137-row v6 prefix, six exact conditions, and twenty stage children. Strict role-eligible experimental conditions increase 42→48; usable effective TRIP/TWIP/joint counts increase 30/27/27→33/31/28. Tests enforce workbook immutability, complete prefix preservation, exact hierarchy/targets, stage chronology and negative-label scope, chemistry/twin/replicate semantics, missing cryogenic mechanics, physics methods/temperatures, mappings, and provenance. No ML was trained.

**Unresolved issues and next step**

P012 physical-batch and tensile-replicate identities, exact initial FCC fractions, Base/Mo 77 K mechanics, and numerical lattice friction stress remain NA. The Mo early-stage Results/caption ambiguity remains explicit. Broader target review, prediction-time leakage eligibility, computational-domain separation, small support, sparse descriptors, and missing traceable reference constants remain P1/P2 blockers.

**Git Commit**

Commit message: `Integrate verified P012 evidence into recovery v7`. The final hash is assigned after this entry is written.

### DEC-0025 — P013 longitudinal evidence and phase/stress semantics (2026-08-26)

P013 is one independent as-cast room-temperature tensile condition. Its four consecutive mechanism intervals are supporting chronology, while exactly five landmarks are canonical non-independent children; neither can create extra samples. Observable stage negatives never become condition negatives. Initial ~0.33 epsilon-HCP is bulk-SXRD thermal/pre-existing martensite, not tensile TRIP, and EBSD/OM surface fractions are noncanonical because polishing may induce TRIP. FCC remains NA because MnO is present and no normalization is justified. TWIP is epsilon-HCP-specific; engineering YS/UTS remain distinct from SXRD/true-stress thresholds. Secondary lattice friction and current-paper calculated YS retain their provenance and leakage status. P013 SFE/DeltaG remain NA.

### LOG-0016 — 2026-08-26 — Verified P013 Scientific Evidence Integration

**Objective and input**

Integrate `P013_scientific_evidence_recovery_VERIFIED.xlsx` into recovery v8 as dataset construction only, preserving recovery v7 and all legacy scientific values and targets.

**Actions and scientific decisions**

Preserved all 163 v7 rows and appended one exact independent condition plus five non-independent landmark observations. Exported hierarchy, interval, landmark, phase-physics, target, provenance, legacy-mapping, and correction/decision tables. Kept bulk SXRD HCP separate from polishing-sensitive EBSD, thermal initial HCP separate from mechanically induced growth, MnO separate from phase complements, phase-average moduli separate from reflection moduli, and measured engineering mechanics separate from SXRD/true-stress thresholds. Legacy targets remain untouched. No intermediate curves were digitized, and no SFE, DeltaG, chemistry, RT Kelvin, FCC complement, or HCP grain size was fabricated.

**Data changes and validation**

Recovery v8 has 169 rows: its 163-row prefix is unchanged, followed by one condition and five landmark children. Strict independent conditions increase 48 to 49 and usable effective TRIP/TWIP/joint counts increase 33/31/28 to 34/32/29. Regression tests cover preservation, hierarchy, chronology, negative scope, phase and stress semantics, physics separation, legacy exclusion, and provenance. No ML or feature engineering was performed.

**Unresolved issues and next step**

P013 measured bulk chemistry, exact source RT Kelvin, physical batch and tensile replicate identities/count, numeric HCP size, intermediate SXRD values, SFE, and DeltaG remain NA. Overall target review, leakage eligibility, computational separation, small support, sparse descriptors, and missing reference constants remain P1/P2 blockers.

**Git Commit**

Commit message: `Integrate verified P013 evidence into recovery v8`. The final hash is assigned after this entry is written.

### DEC-0026 — P014 processing/target separation and source semantics (2026-08-26)

P014 has five exact primary tensile conditions under one material parent and strict study series; the four A600 strain/fracture observations are correlated children. Cold-rolling-induced HCP and twins are stored as processing TRIP/TWIP and never promoted to CR tensile targets. Initial/annealing twins likewise never establish TWIP; direct deformation-twin evidence begins at A600 30% strain, while 15% TWIP remains NA. A650 EBSD 0.001 HCP is preserved with its single-FCC text/XRD conflict. Unstated tensile temperature remains NA, Table 1 +/- is `UNKNOWN_REPORTED_PM`, and n=3 creates no pseudo-replicates. The LUR-derived 631.2 MPa HDI contribution is a potential target-leakage feature. P014 SFE and DeltaG remain NA.

### LOG-0017 — 2026-08-26 — Verified P014 Scientific Evidence Integration

**Objective and input**

Integrate `P014_scientific_evidence_recovery_VERIFIED.xlsx` into recovery v9 as dataset construction only, preserving recovery v8 and all legacy scientific values and targets.

**Actions and scientific decisions**

Preserved all 169 v8 rows, appended five exact tensile conditions and four non-independent A600 stage observations, and exported hierarchy, processing-state, stage, target, HDI/strengthening, source-consistency, provenance, legacy-mapping, and correction/decision tables. Recovered nominal-only chemistry, processing, initial phase/grain/KAM/GOS descriptors, aggregate mechanics and uncertainty, and A600 chronology. Processing-induced CR TRIP/TWIP and initial twins remain separate from tensile targets. A650's modality conflict, absent test temperature, unknown +/- type, and reference-versus-current-paper strengthening inputs remain explicit. Legacy 1/1 targets are untouched; exact effective targets are A600 1/1 and NA/NA for the other four states.

**Data changes and validation**

Recovery v9 has 178 rows: its 169-row v8 prefix is unchanged, followed by five exact conditions and four stage children. Replacement-aware strict independent count remains 49. Effective usable TRIP/TWIP/joint counts change 34/32/29 to 30/28/25 because exact evidence does not support four legacy joint labels. Tests cover preservation, hierarchy, targets, twin/processing separation, stages, phase conflict, descriptors, uncertainty/replicate semantics, missingness, strengthening leakage, mappings, and provenance. No ML, feature engineering, derived alloy descriptors, or digitization was performed.

**Unresolved issues and next step**

P014 measured bulk chemistry, explicitly stated tensile temperature, physical batch/replicate identities, individual replicate results, +/- statistic type, and numeric SFE/DeltaG remain unavailable. Overall label review, predictor leakage eligibility, computational separation, small support, sparse descriptors, and traceable reference constants remain P1/P2 blockers.

**Git Commit**

Commit message: `Integrate verified P014 evidence into recovery v9`. The final hash is assigned after this entry is written.

### DEC-0027 — P015 evidence domains, stress semantics, and strong negatives (2026-08-26)

P015 has exactly two independent experimental conditions under `P015_SERIES01` and material parent `P015_MAT_FE50MN20CR20NI10`; n=3 is aggregate tensile metadata and creates no pseudo-replicates. Experimental targets are governed by XRD/EBSD/TEM, never by the eight correlated MD stages. A condition-level mechanism negative is strong when explicit initial-to-final evidence shows phase absence: initial single FCC plus post-fracture single FCC establishes 298 K TRIP=0. Methods/body 1e-3 s^-1 governs over erroneous 1000 s^-1 figure captions, whose conflict remains logged. Engineering and true stresses remain separate. Temperature-specific current-paper MD SFE remains computational; Table 2 Gamma_SF=10.97 is reuse rather than duplicate evidence, and interface energy is a reference input. Critical stresses and inferred 77 K onsets remain model outputs; the 298 K model carries limited validity. DeltaG remains NA.

### LOG-0018 — 2026-08-26 — Verified P015 Scientific Evidence Integration

**Objective and input**

Integrate `P015_scientific_evidence_recovery_VERIFIED.xlsx` into recovery v10 as dataset construction only, preserving recovery v9 and all legacy scientific values and targets.

**Actions and scientific decisions**

Preserved all 178 v9 rows and appended exactly two experimental tensile conditions. Exported hierarchy, post-fracture evidence, target evidence, SFE/critical-stress physics, MD stages, source consistency, provenance, legacy mapping, and correction/decision tables. Retained nominal-only Fe50Mn20Cr20Ni10 chemistry and the extra Mn charge as processing metadata, initial HCP=0 without fabricating FCC=1, approximate grain size, engineering and true properties separately, experimental 1e-3 s^-1 alongside the caption conflict, direct condition targets, computational MD SFE, model thresholds/onsets, and unresolved DeltaG. Eight MD snapshots remain supporting-only and non-independent.

**Data changes and validation**

Recovery v10 has 180 rows: its 178-row v9 prefix is unchanged, followed by 298 K and 77 K exact conditions. Strict independent conditions increase 49→51 and usable effective TRIP/TWIP/joint counts increase 30/28/25→32/30/27. Regression tests cover preservation, source identity, hierarchy, replicate handling, chemistry, initial/final phase semantics, rate conflict, targets, mechanics, physics/model provenance, computational separation, mappings, and field provenance. No ML, feature engineering, alloy descriptor calculation, digitization, or fabrication was performed.

**Unresolved issues and next step**

P015 post-melt bulk chemistry, batch and individual replicate identity/results, numeric initial FCC and final 77 K HCP fractions, numeric KAM, experimental SFE, alloy-specific DeltaG, and direct stage onset observations remain NA. Global target review, prediction-time leakage eligibility, domain separation, small support, sparse descriptors, and traceable reference constants remain P1/P2 blockers.

**Git Commit**

Commit message: `Integrate verified P015 evidence into recovery v10`. The final hash is assigned after this entry is written.

## 21. Current Project State

| Item | Current snapshot (2026-08-30) |
|---|---|
| Current stage | P023 scientific evidence recovery V17 is complete as the fourth verified new-source extension beyond P019. V12 Global QC, Feature Schema V1 coverage, and Grouped Split Design V1 remain preserved historical artifacts but are stale for V17. No ML training, feature transformation, or performance evaluation has occurred. |
| Current canonical dataset | `data/interim/master_19papers_hierarchical_ids.csv` |
| Current recovery source dataset | `data/processed/master_extended_recovery_v17.csv` (234 rows, 584 columns; all 227 V16 rows and all 524 V16 columns cell-preserved) |
| Current global-QC dataset | `data/processed/master_19papers_recovery_v12_qc.csv` remains the last completed QC artifact, but it does not assess P002 V13 or P020-P023 V14-V17 and is not current for the 234-row extended dataset. |
| Current feature schema | Feature Schema V1 remains the frozen V12 prediction-time policy and classifies 343 V12 fields. V17 has 584 columns; P023 local-EDS/bulk safeguards, processing states, pre/post phase scopes, HCP-TWIP phase tags, mechanics, work-hardening onset, Thermo-Calc context, and SFE/DeltaG gaps require a non-destructive refresh without weakening the pre-tensile rules. |
| Current grouped split design | Grouped Split Design V1 remains a reproducible V12 artifact only. V17 has changed usable support, lacks joint `00`, and adds seven P023 sibling conditions within one strict study/material group; no V1 candidate or manifest is a current V17 split. |
| Frozen prediction moment | Pre-deformation condition-level mechanism prediction, immediately before tensile loading begins. |
| Proposed feature-family progression | The V12 M1-M5 hierarchy and M2 baseline focus remain intended policy, but candidate counts and complete-case support are stale after V17. No transformed matrix exists. |
| Number of papers | 23 primary source IDs in the extended recovery dataset: original P001-P019 plus new P020, P021, P022, and P023. |
| Number of rows | 234: the immutable 227-row V16 prefix plus seven P023 independent conditions; the ten processing states, n=3 replicate metadata, and curve-inferred onset create no master rows. |
| Latest independent-condition estimate | 69 replacement-aware experimental ML conditions. P023 contributes seven exact tensile conditions; its ten supporting phase-state records do not count. The twelve P017 computational conditions remain separate and unchanged. A refreshed V17 condition index is required after collection. |
| Current target status | Under review. V17 usable conditions are TRIP 37 (33/4), TWIP 36 (31/5), and joint 30 (`10=5`, `01=4`, `11=21`, `00=0`). P023 adds two direct TRIP positives and two HCP-epsilon TWIP positives as two fully joint-labelled conditions, with no new negative. Group-level and M2-complete support are not refreshed. |
| Major unresolved issue | Independent negative support remains only 4 TRIP and 5 TWIP, joint `00` remains absent, and 39 conditions have at least one unresolved target component. P023 measured bulk chemistry, physical-batch/individual-replicate metadata, exact numeric room temperature, annealed grain sizes/matrix-Al values, five condition targets, numeric SFE, and DeltaG remain unresolved; global descriptors remain sparse. Paper/material dependence and stale V12 QC/schema/split statistics block matrix construction or confirmatory claims. |
| Next action | Continue verified new-paper recovery if the collection batch is still open. When collection pauses, run a non-destructive V17 Global QC refresh, then refresh feature coverage/schema statistics and redesign grouped T1/T2/T3 splits with P020-P023/common-family controls. Do not train, impute, encode, normalize, resample, synthesize, reconcile chemistry, or calculate alloy descriptors yet. |

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

### LOG-0018 — 2026-08-26 — P017 Computational Evidence Recovery v11

**Objective**

Integrate the verified P017 atomistic evidence into a new recovery version without changing recovery-v10 rows or experimental target counts.

**Input**

`data/interim/manual_recovery/P017_scientific_evidence_recovery_VERIFIED.xlsx` and `data/processed/master_19papers_recovery_v10.csv`.

**Actions Performed**

Added a workbook-driven integration script, twelve exact computational conditions, two unnormalized molar-ratio material parents, ten supporting evidence/provenance/decision tables, a thirty-point audit, and P017 regression tests. Reviewed eight legacy rows by DOI, alloy, temperature, and strain rate rather than row order. Four exact legacy identities map to verified replacements; four unsupported 600 K representations are retained as collapsed computational legacy records.

**Scientific Decisions**

P017 contributes zero experimental ML samples. Paper-native reversible phase transformation and BCC twinning remain separate from experimental effective targets. PTM HCP is not automatically epsilon martensite; FCC stable and BCC unstable fault energies remain separate; 1e8–1e10 s^-1 MD rates cannot join quasi-static experimental distributions; SIS-PSR/UTS-PSR are not experimental YS/UTS; longitudinal snapshots are non-independent.

**Data Changes**

All 180 v10 rows are unchanged. Twelve exact `COMPUTATIONAL_MD` rows were appended, producing 192 rows. Experimental independent and usable TRIP/TWIP/joint counts remain 51 and 32/30/27. No feature engineering, alloy descriptor calculation, curve digitization, experimental fabrication, or ML occurred.

**Validation**

The integration script validates prefix preservation, DOI/domain flags, twelve-condition identity, target ineligibility, and count stability. P017-specific and full regression suites plus `git diff --check` were run; detailed results are recorded in the task commit report.

**Problems Found / Remaining**

P017 has no exact Al0.5 initial BCC fraction or experimental-equivalent chemistry/targets/SFE; dense atomic curves remain intentionally undigitized. Global open P1/P2 blockers remain small/imbalanced independent support, unresolved labels elsewhere, sparse core descriptors, computational separation, and predictor-leakage review.

### LOG-0019 — 2026-08-27 — Global Dataset QC V12

**Objective and input**

Complete a global, non-destructive scientific/data-integrity QC pass over `data/processed/master_19papers_recovery_v11.csv` without restarting valid partial V12 work, changing source scientific values, training ML, engineering features, imputing data, or creating synthetic records.

**Actions and scientific decisions**

Completed the V12 QC generator, separate replacement-aware experimental and exact-computational condition indexes, nineteen required QC/readiness reports, and V12 regression tests. Classified row roles, duplicate/replacement handling, target integrity, feature coverage, SFE/DeltaG method scope, composition and initial microstructure, leakage risk, provenance, missingness, condition QC tiers, paper contribution, computational isolation, and open issues. Retained P017 exclusively in the computational condition index and left P018/P019 unavailable-source rows unpromoted. Corrected only QC implementation defects found during validation: a P015 molecular-dynamics SFE false positive caused by matching `TEM` inside “temperature,” omitted P008 TEM provenance, unsupported Notes-based loading-mode/GOS coverage, hard-coded computational audit statuses, and an incorrect report column-count expression.

**Data changes and validation**

Recovery v11 and V12 QC each contain 192 rows. All 334 source columns, every source cell, and the full source missingness mask are equal; V12 appends only nine `QC_*` metadata columns. The indexes contain 51 unique independent experimental conditions and 12 exact P017 computational conditions; P017 contributes zero experimental conditions. Experimental usable target counts remain TRIP 32, TWIP 30, and joint 27. All 15 P018/P019 source rows remain cell-equal. No NA was converted to zero, no imputation or normalization occurred, no feature engineering or alloy descriptor calculation occurred, and no scientific value was fabricated. `python -m pytest -q tests/test_global_qc_v12.py` passes 13 tests; `python -m pytest -q` passes 71 tests (40 existing pandas future warnings only). The generator's preservation assertions and an independent dataframe/missingness comparison also pass.

**Files created or modified**

Created `scripts/global_qc_v12.py`, `tests/test_global_qc_v12.py`, the V12 QC master and two condition indexes under `data/processed/`, and nineteen V12 reports under `reports/`. Updated this guide. No recovery-v11 or earlier scientific artifact is included as a task modification.

**Problems resolved and remaining**

The global replacement/domain/role census and audit outputs are reproducible and internally consistent. Remaining blockers are scientific rather than repaired by software: 24 conditions with incomplete target components, only 5 TRIP-negative and 6 TWIP-negative conditions, 27 joint labels, P018/P019 source unavailability, partial provenance for five exact records, sparse measured chemistry/initial microstructure/experimental SFE/DeltaG, strong paper/material dependence, and unresolved final predictor eligibility. V12 is structurally suitable for controlled feature-schema design with gates, but it is not ready for final ML training.

**Next recommended step**

Resolve the prioritized source/target/provenance queue, acquire P018/P019 source material, and define a frozen pre-test/test-condition-only schema plus grouped paper/material validation policy before reassessing modelling readiness.

**Git Commit**

Commit message: `Complete global dataset QC V12`. The final hash is assigned after this entry is written.

### LOG-0020 — 2026-08-27 — Feature Schema V1 and Frozen Prediction-Time Leakage Policy

**Objective and input**

Freeze a scientifically defensible pre-deformation feature schema over the QC-validated V12 dataset, using `master_19papers_recovery_v12_qc.csv`, the separate 51-condition experimental and twelve-condition computational indexes, and the V12 feature/leakage/readiness audits. The task was schema design only: no ML, split execution, imputation, encoding, normalization, feature engineering, synthetic data, digitization, or scientific-value modification.

**Actions performed**

Created a deterministic header-checked schema generator, one row for every 343 V12 master columns, cumulative M1–M5 raw-column manifests, per-column scientific priority, six-domain manifest, descriptive feature-set and target-specific coverage reports, a frozen prediction-time policy, a complete A–V schema audit, and nineteen V1 regression tests. Updated `.gitignore` only to track the four required `data/schema` CSVs. The generator fails if a master field is omitted, duplicated, or replaced by a non-master feature.

**Scientific decisions**

The prediction moment is immediately before tensile loading. Exactly 48 fields are safe-direct and 57 safe-conditional; conditional eligibility always retains scope/method controls. Targets/evidence remain target-only. Thirty post-test fields, 25 same-test mechanical outcomes, and nine fitted/loading-derived fields are permanently blocked. Nineteen computational-only fields cannot join the experimental feature space. Fourteen grouping and nine identifier fields are split/identity controls only; 104 provenance and ten metadata fields are not ordinary predictors. Initial twins/martensite remain pre-test state rather than target evidence. Measured bulk, nominal, feedstock, and local chemistry remain distinct; the measured-first/nominal-fallback policy is documented but not applied. Experimental, thermodynamic/CALPHAD, DFT/MD, assumed, reference, and P017 GSFE concepts remain method/domain-separated.

M1 through M5 contain 26, 31, 50, 70, and 105 untransformed candidate source columns. CORE_V1 raw complete-case counts are 40, 31, 31, 31, and 26 of 51; optional/exploratory candidates and method controls are not silently required or filled in those counts. M2 chemistry plus test conditions is recommended only as the first schema baseline for split design. Physics and sparse detailed microstructure remain future ablation families.

**Data changes and validation**

No scientific dataset was written or changed. Recovery v11 and V12 remain 192 rows; V12 remains the same 343 columns with all 334 recovery-v11 source columns and missingness states preserved. Experimental/computational counts remain 51/12, P017 remains absent from the experimental index, and usable target counts remain 32 TRIP, 30 TWIP, and 27 joint. No NA became zero; no missing value was imputed; no composition was normalized or reconciled; no VEC, atomic-size mismatch, mixing entropy/enthalpy, Omega, electronegativity mismatch, or other derived descriptor was calculated; and no transformed training matrix or model was created. `python -m pytest -q tests/test_feature_schema_v1.py` passes 19 tests. `python -m pytest -q` passes 90 tests with 40 pre-existing pandas future warnings.

**Files created or modified**

Created `scripts/feature_schema_v1.py`, `tests/test_feature_schema_v1.py`, four CSVs under `data/schema/`, four V1 reports under `reports/`, and updated `.gitignore` and this guide.

**Problems resolved and remaining**

The preliminary V12 eligibility gate is resolved: every V12 column now has one frozen primary class and unresolved-review count is zero. Mixed-scope fields are conservative and explicit; for example, only pre-test P014 KAM may be conditional while P011 interrupted/fracture-stage KAM remains post-test and excluded. Remaining blockers are target completeness/class imbalance, unavailable P018/P019 sources, sparse measured chemistry/SFE/DeltaG/detailed initial state, representation choices not yet implemented, and paper/material-aware target-specific split feasibility. Feature Schema V1 is ready for split design, not ML training.

**Next recommended step**

Design grouped train/validation splits for T1/T2/T3 feasibility using paper/study/material/leakage identifiers only as grouping controls, beginning with M2 and predeclaring measured-bulk-versus-nominal representation. Continue target/source review. Do not construct a training matrix, train, impute, encode, normalize, synthesize, or engineer features yet.

**Git Commit**

Commit message: `Define feature schema v1 and prediction-time leakage policy`. The final hash is assigned after this entry is written.

### LOG-0021 — 2026-08-27 — Grouped Split Design V1

**Objective and inputs**

Design and audit leakage-safe grouped train/validation feasibility for T1 binary TRIP, T2 binary TWIP, and T3 joint TRIP/TWIP using the QC-validated 51-condition experimental index, immutable V12 master, frozen Feature Schema V1 manifests, and V1/V12 audits. This task was split design only: no predictor matrix, chemistry reconciliation, imputation, transformation, resampling, model, prediction, or performance metric.

**Actions performed**

Created a deterministic generator, a 51-condition grouping-key audit, all-level target distributions, full and M2 class/group support, negative-evidence and positive-family audits, M2 class-family support, G1/G2/G3 feasibility, chemistry-source policy, validation architecture, A–V split audit, versioned split candidates and assignment manifests, and split-specific regression tests. Audited Paper, Study Series, Material Parent, Physical Batch, strict leakage, material leakage, and exact unparsed source-alloy-family overlap. Evaluated LOPO, leave-one-study-series-out, leave-one-material-family-out, deterministic label-blind GroupKFold k=2/3/4/5, and an exhaustive predeclared grouped-holdout search. No random seeds were searched.

**Scientific and statistical decisions**

The atomic unit remains the replacement-aware independent experimental ML condition. `Leakage_Group_Strict` with paper fallback is the recommended grouping key; all related paper/study/material groups remain independent across sides, and group independence overrides exact stratification. Nineteen conditions require conservative paper fallback, while all physical batch identities remain NA rather than inferred. Random row splitting and pure material splits that cross the enclosing strict study are invalid.

T1 has 27/5 positive/negative support in four negative papers/strict groups. M2 retains 17/2 and only two negative groups. The primary T1 design is therefore one of three M2-compatible deterministic strict holdouts, beginning with `T1_GH_STRICT_01`. Full-roster strict GroupKFold k=2 is class-supported but its M2 intersections lose the negative class on opposite sides; k=3/4/5 are not full-roster feasible. T2 has 24/6 in four negative groups, and M2 retains 14/6; strict GroupKFold k=2 is primary for G3, while k=4 and three deterministic holdouts are secondary. Exact `Fe50Mn30Co10Cr10` source text spans P003/P011/P013/P014, so GroupKFold is not a pure G2 design; every retained holdout has zero exact-source-family overlap. LOPO is not a complete class-supported design for either target. No candidate is `VALID_STRONG`; M2-compatible valid-limited counts are T1=3 and T2=9.

T3 four-state counts remain 00=1, 10=5, 01=4, 11=17. T3A is `T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE`; no class was merged. T3B may later be explored output-wise on strict grouped splits, but cannot validate state 00. G1 is exploratory related-material interpolation, G2 is limited and must also preserve strict study boundaries, and G3 is limited to class-supported multi-paper partitions rather than universal LOPO. Nested CV is excessive at current minority/group support.

The future chemistry policy prefers explicitly valid measured bulk evidence, otherwise nominal composition, and retains `Composition_Source=MEASURED_BULK|NOMINAL`; local EDS/APT/TEM and feedstock chemistry cannot silently substitute for bulk. The policy was not executed. The negative audit preserves all 5 TRIP and 6 TWIP negatives unchanged and grades consolidated evidence strength; the P008 N2p6-FC TRIP negative retains its consolidated evidence-text gap rather than being upgraded or relabelled.

**Data changes and safeguards**

No source scientific data or source missingness changed. The 192-row V12 master, 51/12 experimental/computational condition separation, binary counts, and joint states remain unchanged. P017, computational conditions, stages, legacy representations, summaries, and replicate metadata enter no split roster. Manifests contain each target-usable condition exactly once per valid target/split/feature-set assignment, with only `TRAIN` and `VALIDATION`; no test set, duplicated minority row, omitted majority row, SMOTE record, or synthetic alloy was created.

**Validation**

The generator's internal preservation, target, group-overlap, class-support, manifest, determinism, and no-training assertions pass. `python -m pytest -q tests/test_grouped_split_design_v1.py` passed 22 tests. `python -m pytest -q` passed 112 tests with 40 pre-existing pandas `FutureWarning` messages. The task-scoped diff check passed; the whole-worktree check remains obstructed only by trailing whitespace in unrelated pre-existing recovery-file edits that are excluded from this commit.

**Problems resolved and remaining**

Target-specific grouped feasibility and a source-selection policy are now explicit and reproducible. Remaining P1/P2 limitations are 24 incomplete target components, scarce independent negatives, M2's two-negative T1 subset, joint 00 singleton, unavailable P018/P019 sources, missing physical batches and partial hierarchy, the exact source-text family spanning four papers plus unresolved differently written equivalence, sparse measured chemistry/initial microstructure/experimental SFE/DeltaG, and the consolidated P008 negative-evidence text gap. Split feasibility does not imply model adequacy.

**Next recommended step**

Predeclare `T1_GH_STRICT_01` and the full T2 GroupKFold-k=2 design, then construct and re-audit an untransformed, source-preserving M2 condition table under the frozen chemistry policy. Continue targeted recovery/collection of genuinely independent negative material families. Do not train, impute, encode, normalize, calculate descriptors, resample, or synthesize yet.

**Git Commit**

Commit message: `Design grouped validation splits v1`. The final hash is assigned after this entry is written.

### LOG-0022 — 2026-08-28 — P002 Scientific Evidence Recovery V13

**Objective and inputs**

Integrate the verified P002 scientific-evidence workbook into a new recovery version over `data/processed/master_19papers_recovery_v12_qc.csv`, without altering any V12-QC row/cell, fabricating missing values, creating pseudo-replicates, performing feature engineering, or training ML. The verified paper DOI is `10.1016/j.msea.2020.140441`; the official corrigendum DOI is `10.1016/j.msea.2021.142419`.

**Actions performed**

Added a hash-gated, workbook-driven recovery script; `master_19papers_recovery_v13.csv`; three exact P002 processing-defined primary conditions; ten correlated EBSD/XRD/TEM stage/post-test evidence records; two non-independent Hall-Petch support states; twelve hierarchy/processing/microstructure/mechanics/stage/target/physics/Hall-Petch/corrigendum/provenance/legacy/decision tables; a source audit; and eleven P002 regression tests. Every one of the 192 V12-QC rows and every value in its 343 columns remains cell/order preserved. The verified workbook is retained byte-unchanged as a reproducible recovery input.

**Hierarchy, legacy mapping, and replicate handling**

Created `P002_MC_A600_RT`, `P002_MC_A700_RT`, and `P002_MC_A800_RT` under `P002_SERIES01` and `P002_MAT_FE40MN10CO20CR20NI10`. All share strict/material leakage keys and are independent condition-level records. `Physical_Batch_ID` and `Replicate_ID` remain NA. The reported three tensile specimens per annealing temperature are stored only as `Replicate_n=3`; no individual or pseudo-replicate rows were created.

Mapped `P002_C01/C02/C03` to A800/A700/A600 by DOI, nominal composition, annealing temperature, room-temperature representation, strain rate, mechanics, and targets—not row order. All five legacy P002 rows remain unchanged; only the exact replacements count independently. The equiatomic comparator and legacy CALPHAD descriptor remain support-only.

**Scientific decisions**

Applied the official corrigendum interpretation that A800 shows more pronounced TRIP than A700; the published EBSD fractions were not altered. A700 remains direct high-confidence TRIP=1/TWIP=1/Slip=1 from EBSD plus near-fracture TEM/SAED/HR-STEM. A800 remains TRIP=1/TWIP=1/Slip=1, but its TWIP evidence is explicitly medium-confidence author condition attribution supported by the study conclusion, not direct A800 post-test TEM. A600 legacy `0/0` is preserved only as `Original_TRIP/Original_TWIP`; its exact effective targets are `NA/NA` with `INSUFFICIENT_FOR_ZERO`, because hindered/suppressed activation and absent post-test characterization do not prove absence. Pre-test annealing/processing twins never establish tensile TWIP.

Chemistry remains nominal Fe40Mn10Co20Cr20Ni10 at.% with quantitative measured bulk composition NA; qualitative EDS/STEM-EDS homogeneity is not promoted to bulk chemistry. Source-text room temperature is retained with numeric `Test_T_K=NA`. All three initial states are qualitative single FCC with direct `Initial_HCP_fraction=0`, while exact numeric FCC fractions remain NA.

Recovered P002 SFE approximately 14 mJ/m2 at 300 K only as a current-paper thermodynamic estimate and DeltaG=-292 J/mol at 300 K only as a Thermo-Calc TCFE7 result. Preserved 22.2 J/mol transformation strain energy and 15 mJ/m2 interface energy as reference-model inputs, and 2.98e-5 mol/m2 planar density plus 0.3587 nm lattice constant with derivation provenance. Hall-Petch sigma0 approximately 139 MPa and k approximately 504 MPa um^0.5 remain mechanical-response-derived leakage values, not primary predictors.

**Rows and target-count changes**

V13 contains 207 rows: 192 preserved inputs plus 3 exact primary conditions, 10 correlated evidence records, and 2 support rows. Replacement-aware independent experimental support remains 51. Usable TRIP changes 32 to 31 (27 positive, 4 negative); TWIP changes 30 to 29 (24 positive, 5 negative); joint support changes 27 to 26. Joint states are now `10=5`, `01=4`, `11=17`, and `00=0`. No class was merged and no effective negative was manufactured.

**Validation**

The integration assertions and `python -m pytest -q tests/test_p002_recovery_v13.py` pass all 11 tests. They cover source/workbook hashes, full prefix preservation, source/corrigendum identity, exact hierarchy and counts, no pseudo-replication, nominal-only chemistry, initial-state and twin guardrails, target evidence grades, A600 NA semantics, stage fractions/non-independence, physics/Hall-Petch scope, legacy double-count prevention, complete field-level provenance, and absence of modelling/resampling/feature engineering. `python -m pytest -q` passes all 123 repository tests with 40 pre-existing pandas `FutureWarning` messages. The full-suite run regenerated the same seven previously audited line-ending/serialization/path-rendering artifacts; only those seven were restored to their committed state. `git diff --check` then passes.

**Remaining gaps and downstream gate**

P002 still lacks quantitative post-melt bulk chemistry, exact numeric test temperature, physical-batch/individual-replicate identities and results, exact initial FCC fractions, A600 UTS/elongation and direct post-test mechanism characterization, an exact A800 10% HCP fraction, direct A800 post-test twin imaging, and some state-specific uncertainty values. V12 Global QC, feature coverage, Feature Schema V1 coverage statistics, and Grouped Split Design V1 are preserved but stale for V13. The exact next step is a non-destructive V13 QC refresh followed by coverage/schema-statistic refresh and grouped split redesign. No matrix construction or ML is authorized before those gates.

**Git Commit**

Commit message: `Integrate verified P002 evidence into recovery v13`. The final hash is assigned after this entry is written.

### LOG-0023 — 2026-08-28 — P020 Extended Scientific Evidence Recovery V14

**Objective and inputs**

Integrate `data/interim/manual_recovery/P020_scientific_evidence_recovery_VERIFIED.xlsx` as a new primary experimental source beyond P001-P019 over the immutable 207-row recovery V13 base. This task was dataset recovery only: no model, predictor matrix, feature engineering, imputation, normalization, composition reconciliation, descriptor calculation, curve digitization, resampling, or synthetic record was authorized.

**Actions performed**

Added a SHA-256-gated, workbook-driven integration script; `master_extended_recovery_v14.csv`; one exact primary condition; six correlated real-time neutron stage/end-point rows; twelve P020 identity/hierarchy/processing/microstructure/mechanics/target/phase/stage/method/provenance/safeguard/decision tables; a source audit; and sixteen P020 regression tests. Every V13 row, value, missingness state, column, and row order is retained as the V14 prefix. The verified workbook is read-only and byte-preserved.

**Hierarchy and extended-source policy**

Assigned new stable `Paper_ID=P020` only after proving that neither its ID nor DOI existed in V13. Created one independent condition, `P020_MC_TRIPHEA_INSITU`, under `P020_SERIES01` and `P020_MAT_FE50MN30CO10CR10`; physical batch, replicate identity, and replicate count remain NA. Six in-situ observations link to the primary condition and are never independent. P020 is not merged into P013/P003/P011/P014 despite shared nominal Fe50Mn30Co10Cr10 text; its common alloy-family text is grouping-audit metadata only and not a predictor or sample identity.

**Scientific decisions**

Preserved direct initial FCC/HCP fractions 0.79/0.21, approximately 40 um equiaxed FCC grains, and approximately 4 um HCP laths. The initial HCP is pre-existing and does not establish TRIP; condition TRIP=1 comes from continuous real-time FCC loss beginning near 200 MPa and persisting to fracture. TWIP=1 is explicitly HCP-phase `{10.2}` tensile twinning near 400 MPa followed by compression/multiple HCP twinning near 730 MPa and approximately 15% strain; it is never represented as FCC twinning. Slip=1 retains FCC/HCP phase-specific interpretation. Stage-I zeros are pre-yield only, and slower TRIP above approximately 25% strain remains stage-positive rather than becoming absence.

The missing supplement prevents defensible test-temperature, strain-rate, geometry, or replicate inference. Approximately 200 MPa remains an observable elastic-deviation onset rather than conventional 0.2% offset YS. The reported 1046 MPa ultimate strength and 34% elongation retain raw/source stress-strain wording and remain mechanical-outcome leakage. Direct fracture FCC approximately 0.17 is stored, while HCP=0.83 is not derived. P020 SFE and DeltaG remain NA; no value is transferred from another Fe50Mn30Co10Cr10 source.

**Rows and target-count changes**

V14 contains 214 rows and 454 columns: the unchanged 207-row/390-column V13 prefix plus one independent primary condition and six non-independent observations. Replacement-aware independent experimental support increases 51→52. Usable TRIP/TWIP/joint support changes 31/29/26→32/30/27; binary classes become 28/4 and 25/5, and joint states become `10=5`, `01=4`, `11=18`, `00=0`. P020 adds no negative support.

**Validation**

The integration script's source-hash, workbook-hash, full-prefix preservation, identity, hierarchy, non-independence, target semantics, method, missingness, count, and exhaustive master-field provenance assertions pass. `python -m pytest -q tests/test_p020_recovery_v14.py` passes 16 tests; `python -m pytest -q` passes all 139 repository tests with 40 pre-existing pandas `FutureWarning` messages. The full suite regenerated the same seven previously audited line-ending/serialization/path-rendering artifacts; exactly those seven files were restored to their committed content. `git diff --check` then passes.

**Remaining gaps and downstream gate**

P020 lacks quantitative post-melt bulk chemistry, the absent supplement's tensile metadata, physical-batch identity, P020-specific numeric SFE/DeltaG, and an explicitly reported HCP fracture fraction. V12 Global QC, Feature Schema coverage, feature coverage, and Grouped Split Design artifacts remain historical and stale; they are not refreshed during an open paper-collection batch. When collection pauses, refresh all four layers non-destructively before matrix construction.

**Git Commit**

Commit message: `Integrate verified P020 evidence into extended recovery v14`. The final hash is assigned after this entry is written.

### LOG-0024 — 2026-08-28 — P021 Extended Scientific Evidence Recovery V15

**Objective and inputs**

Integrate `data/interim/manual_recovery/P021_scientific_evidence_recovery_VERIFIED.xlsx` as a new verified experimental source over the immutable `data/processed/master_extended_recovery_v14.csv` base. This task was dataset recovery only: no model, predictor matrix, feature engineering, imputation, normalization, composition reconciliation, alloy-descriptor calculation, figure digitization, pseudo-replication, resampling, or synthetic record was authorized.

**Actions performed**

Added a SHA-256-gated, workbook-driven V15 integration script; `master_extended_recovery_v15.csv`; exactly five P021 primary tensile conditions; twelve study/hierarchy/processing/condition-grid/initial-microstructure/mechanics/post-fracture/target/SFE/Hall-Petch/provenance/decision tables; an A–Z audit; and twenty P021 regression tests. Every V14 row, source-column value, missingness state, and row order remains preserved as the V15 prefix. The verified workbook is retained byte-unchanged. Master-field provenance covers every populated P021 field and each deliberate scientific NA, while supporting physics and Hall-Petch values retain condition scope and predictor eligibility.

**Hierarchy, composition, processing, and replicate handling**

Assigned new `Paper_ID=P021` only after an exact DOI search returned no V14 representation. Created four 298 K conditions with 10.0, 19.5, 40.9, and 149.6 um grains plus one 77 K condition reusing the 40.9 um annealed state, all under `P021_SERIES01` and `P021_MAT_FE50MN17p5CR12p5CO10NI5SI5`. Each anneal/grain-size/test-temperature combination is one independent condition; all siblings share strict/material leakage groups. Physical batch and replicate identity remain NA. `Replicate_n=3` means the reported minimum of at least three specimens and creates no replicate rows.

Nominal `Fe50Mn17.5Cr12.5Co10Ni5Si5` at.% and its exact processing route are retained without normalization. Quantitative post-melt bulk chemistry remains NA; qualitative EDS/BSE homogenization is not promoted to bulk composition. All five initial states remain fully recrystallized single FCC with direct HCP=0 and alpha-BCT=0 but exact FCC fraction NA. Abundant annealing twins never establish tensile TWIP. The cryogenic row retains `PROFUSE_PRETEST_STACKING_FAULTS` before loading, without treating them as TWIP or post-test leakage.

**Target and leakage decisions**

The 10.0, 19.5, and 149.6 um RT conditions remain TRIP/TWIP/Slip NA with `INSUFFICIENT_FOR_ZERO` because mechanical plateaus are not direct mechanism evidence. RT40 is TRIP=1/TWIP=1/Slip=1: EBSD/TEM directly establish FCC→epsilon-HCP and the source explicitly reports a few mechanical twins. Its TWIP occurrence is graded LOW abundance and MEDIUM strength relative to TRIP, with twin phase unresolved. The 77 K state is TRIP=1/TWIP=NA/Slip=1; strong XRD/EBSD/TEM TRIP evidence does not justify a binary twin assignment.

Post-fracture HCP fractions 0.149 and 0.562 remain indexed-region-only target evidence and are absent from the other grain-size conditions. Alpha-BCT non-detection remains pathway-specific and never cancels positive FCC→HCP TRIP. Numeric SFE remains NA; raw `<23 mJ/m2` is stored only as an author-inferred upper bound, and 77 K SFE remains qualitative. DeltaG remains NA. Hall-Petch sigma0=198 MPa and k=368 MPa um^0.5 remain current-paper fits from tensile yield response and `MODEL_DERIVED_LEAKAGE`.

**Rows and target-count changes**

V15 contains 219 rows and 497 columns: the unchanged 214-row/454-column V14 prefix plus five P021 independent conditions. Replacement-aware experimental support increases 52→57. Usable TRIP/TWIP/joint support changes 32/30/27→34/31/28; binary classes become 30/4 and 26/5, and joint states become `10=5`, `01=4`, `11=19`, `00=0`. These counts are generated from the replacement-aware condition pool rather than hard-coded after-counts.

**Validation**

The integration generator's source/workbook hashes, full-prefix preservation, identity/duplicate checks, exact hierarchy, replicate semantics, chemistry, processing, microstructure, target, leakage, physics, count-delta, and exhaustive provenance assertions pass. `python -m pytest -q tests/test_p021_recovery_v15.py` passes all 20 tests. `python -m pytest -q` passes all 159 repository tests with 40 pre-existing pandas `FutureWarning` messages. The full suite mechanically regenerated the same seven previously audited historical artifacts; exactly those seven files were restored to their committed content before final diff review. `git diff --check` passes on the complete staged task.

**Remaining gaps and downstream gate**

P021 lacks quantitative post-melt bulk chemistry, physical-batch and individual-replicate identities/results, exact numeric initial FCC fractions, direct post-test mechanism evidence for the 10.0/19.5/149.6 um RT states, condition-wide 77 K TWIP evidence, direct numeric alloy-specific SFE, and DeltaG. Global QC, feature coverage/schema statistics, and grouped split artifacts remain intentionally stale during the open collection batch. Refresh them non-destructively only after paper collection pauses and before any matrix construction.

**Git Commit**

Commit message: `Integrate verified P021 evidence into extended recovery v15`. The final hash is assigned after this entry is written.

### LOG-0025 — 2026-08-28 — P022 Extended Scientific Evidence Recovery V16

**Objective and inputs**

Integrate `data/interim/manual_recovery/P022_scientific_evidence_recovery_VERIFIED.xlsx` as a new verified experimental source over the immutable `data/processed/master_extended_recovery_v15.csv` base. This task was dataset recovery only: no model, predictor matrix, feature engineering, imputation, chemistry normalization, composition reconciliation, alloy-descriptor calculation, Figure 3 digitization, pseudo-replication, resampling, or synthetic record was authorized.

**Actions performed**

Added a SHA-256-gated, workbook-driven V16 integration script; `master_extended_recovery_v16.csv`; five exact primary conditions; three correlated 40%-strain EBSD children; twelve study/material/hierarchy/composition/processing/microstructure/mechanics/stage/target/physics/provenance/decision tables; an A-X audit; and twenty-two P022 regression tests. Every V15 row, source-column value, missingness state, and row order remains preserved as the V16 prefix. The verified workbook is retained byte-unchanged. Master-field provenance covers every populated P022 field and each deliberate scientific NA; supporting general SFE thresholds are separately marked support-only and not assigned as condition values.

**Hierarchy, raw composition, processing, and missing metadata**

Assigned new `Paper_ID=P022` only after the exact DOI search returned no V15 representation. Created `P022_MC_C0_ASCAST_RT`, `P022_MC_C2_ASCAST_RT`, `P022_MC_C4_ASCAST_RT`, `P022_MC_C2MO1_ASCAST_RT`, and `P022_MC_C2MO2_ASCAST_RT` under one strict `P022_SERIES01` group and five chemistry-specific material parents. Each is one independent condition. The C2/C2Mo1/C2Mo2 40%-strain observations remain correlated children; physical batch, replicate identity/count, and individual results remain NA, with no pseudo-replicates.

Preserved the five Fe50Mn30Co10Cr10CxMoy formulas exactly with `ATOMIC_RATIO_AS_REPORTED`. No 100-at.% normalization or element concentration was calculated, and quantitative post-melt bulk chemistry remains NA. All specimens remain as-cast after arc melting under Ti-gettered high-purity Ar in a water-cooled Cu crucible and at least five remelts; no homogenization, rolling, or annealing was invented. `Test_T_Raw=room temperature` is retained while exact numeric temperature and tensile strain rate remain NA. The 22 x 2.5 x 1.5 mm flat-specimen dimensions are preserved without promotion to gauge fields.

**Microstructure and target decisions**

C0 retains initial FCC+HCP with both numeric fractions NA; pre-existing as-cast HCP does not generate TRIP. C2/C4/C2Mo1/C2Mo2 retain XRD single-FCC(-matrix) states with HCP=0 and exact FCC fraction NA. C4 direct interdendritic carbides remain present alongside the XRD matrix description. Dendrite morphologies remain qualitative, numeric grain size remains NA, and the prior-work sigma possibility for C2Mo2 is not promoted to current-paper evidence.

C0 is Effective_TRIP=1/TWIP=NA/Slip=NA with MEDIUM author-attributed condition evidence, not direct current-paper post-test phase mapping. C2, C2Mo1, and C2Mo2 are TRIP=NA/TWIP=1/Slip=NA from direct approximately 60-degree <111> deformation-twin boundaries at 40% strain; C2Mo1 retains the largest qualitative population and no fraction is digitized. C4 remains NA/NA/NA. P022 creates no strong negative: “TRIP-to-TWIP” wording, TWIP dominance, missing microscopy, and pre-existing HCP do not generate TRIP=0, TWIP=0, or additional positive labels.

**Mechanical and physics safeguards**

Recovered only approximate direct-text C2 UTS/elongation (600 MPa/67.4%) and C2Mo1 UTS/elongation (658 MPa/89.8%). YS and all other exact mechanical fields remain NA; Figure 3 and the stated C2Mo2 elongation decrease were not digitized or converted. All recovered mechanics remain `MECHANICAL_OUTCOME_LEAKAGE`.

Current-alloy numeric SFE and DeltaG remain NA. The 15-45 mJ/m2 TWIP range and <15 mJ/m2 TRIP threshold remain secondary general support-only records, never P022 condition values. C/Mo SFE effects remain `QUALITATIVE_DIRECTION_ONLY` and no FeMnCoCr physics value was imported.

**Rows and target-count changes**

V16 contains 227 rows and 524 columns: the unchanged 219-row/497-column V15 prefix plus five primary conditions and three correlated children. Replacement-aware experimental support increases 57→62. Usable TRIP/TWIP/joint support changes 34/31/28→35/34/28; binary classes become 31/4 and 29/5, while joint states remain `10=5`, `01=4`, `11=19`, `00=0`. These counts are generated from the replacement-aware condition pool rather than hard-coded after-counts.

**Validation**

The generator's source/workbook hashes, full-prefix preservation, DOI identity/duplicate check, exact hierarchy, non-independence, raw composition, missing metadata, microstructure, carbide/XRD coexistence, target evidence grade, negative-label safety, mechanics, SFE/DeltaG, count deltas, and exhaustive provenance assertions pass. `python -m pytest -q tests/test_p022_recovery_v16.py` passes all 22 tests. `python -m pytest -q` passes all 181 repository tests with 40 existing pandas `FutureWarning` messages. The full suite mechanically regenerated the same seven previously audited historical artifacts; exactly those seven files were restored to committed content before final review.

**Remaining gaps and downstream gate**

P022 lacks quantitative post-melt bulk chemistry; physical-batch, replicate identity/count, and individual results; exact numeric test temperature and strain rate; exact FCC fractions; numeric grain sizes; direct C0 post-test phase evolution; C4 mechanism evidence; condition-wide TRIP evidence for C2/C2Mo1/C2Mo2; twin fractions; numeric alloy-specific SFE; and DeltaG. Global QC, feature coverage/schema statistics, and grouped split artifacts remain intentionally stale during the open collection batch. Refresh them non-destructively only after paper collection pauses and before any matrix construction.

**Git Commit**

Commit message: `Integrate verified P022 evidence into extended recovery v16`. The final hash is assigned after this entry is written.

### LOG-0026 — 2026-08-30 — P023 Extended Scientific Evidence Recovery V17

**Objective and inputs**

Integrate `data/interim/manual_recovery/P023_scientific_evidence_recovery_VERIFIED.xlsx` as a new verified experimental source over the immutable `data/processed/master_extended_recovery_v16.csv` base. This task was dataset recovery only: no ML, feature engineering, imputation, chemistry normalization, derived alloy descriptors, curve digitization, pseudo-replication, stage fabrication, or cross-paper physics transfer was authorized.

**Actions performed**

Added a SHA-256-gated, workbook-driven V17 integration script; `master_extended_recovery_v17.csv`; seven exact primary tensile conditions; fifteen study/composition/FSP/processing-state/phase/tensile/mechanical/precipitation/before-after/target/onset/Thermo-Calc/gap/provenance/decision tables; an A-AC audit; and twenty-four P023 regression tests. Every V16 row, all 524 V16 scientific/source columns, every value and missingness state, and row order remain preserved as the V17 prefix. The verified workbook is retained byte-unchanged. Exhaustive provenance covers every populated P023 master field and deliberate scientific NA.

**Hierarchy, processing, chemistry, and replicates**

Assigned `Paper_ID=P023` only after exact DOI/source identity and duplicate checks found no V16 representation. Created `P023_MC_DPASS_RT`, `P023_MC_650_5_RT`, `P023_MC_650_15_RT`, `P023_MC_650_30_RT`, `P023_MC_850_5_RT`, `P023_MC_850_15_RT`, and `P023_MC_850_30_RT` under `P023_SERIES01` and `P023_MAT_FE39MN20CO20CR15SI5AL1`. D-pass plus nine annealed 650/750/850 C states form ten supporting pre-test phase records; 750-X has no primary tensile row. `Replicate_n=3` is aggregate metadata only; physical batch and individual replicate IDs/results remain NA.

Preserved the nominal Fe39Mn20Co20Cr15Si5Al1 at.% composition exactly without normalization. As-cast and D-pass Fig. 1e EDS values remain local elemental-distribution measurements and never populate measured bulk chemistry, which remains NA. Retained vacuum arc casting, approximately 300 um source vacuum notation, Ar backfill, ingot geometry, double-pass FSP parameters, Cu backing, Ar shielding, D-pass grain size 0.79 ± 0.05 um, as-cast supporting grain size 120 ± 12 um, annealing/water-quench grid, RT raw test notation, 1e-3 s^-1 rate, and tensile geometry without inventing numeric Kelvin or annealed grain sizes.

**Phase, precipitation, targets, and leakage decisions**

Recovered all ten Fig. 2c pre-test FCC/HCP fractions and SD values exactly. Initial HCP never creates TRIP. Direct pre/post changes 0.30/0.70→0.06/0.94 for 650-15 and 0.43/0.57→0.10/0.90 for 850-30 establish tensile FCC-to-HCP epsilon TRIP; explicit epsilon-phase twinning and `<c+a>` slip establish `Effective_TWIP=1`, `TWIP_Phase=HCP_EPSILON`, and `Slip=1` for both. The other five tensile conditions remain TRIP/TWIP/Slip NA with `INSUFFICIENT_FOR_ZERO`; no zero follows from absent evidence or work-hardening curves.

Precipitation descriptions remain pre-test and qualitative. P023 post-test fractions, twins, GND/dislocation information, mechanics, SDI, and work-hardening quantities remain leakage/outcome evidence. The 650-15 values 924 MPa true stress, approximately 840 MPa engineering stress, approximately 10% strain, and 2983 MPa work-hardening rate are classified as current-paper curve-inferred onset, not microscopy measurement or a direct experimental stage. Thermo-Calc/TCHEA2 remains model context and does not override EBSD/XRD. Numeric current-paper SFE and FCC-to-HCP DeltaG remain NA.

**Rows, targets, and validation**

V17 contains 234 rows and 584 columns: the unchanged 227-row/524-column V16 prefix plus seven independent P023 tensile conditions. Replacement-aware experimental support increases 62→69. Usable TRIP/TWIP/joint support changes 35/34/28→37/36/30; binary classes become 33/4 and 31/5, while joint states become `10=5`, `01=4`, `11=21`, `00=0`. Counts are calculated programmatically.

The generator's input hashes, full-prefix preservation, DOI/source-family safeguards, exact hierarchy, supporting-state exclusion, replicate handling, nominal/local/bulk chemistry separation, test metadata, grain size, all ten phase fractions, direct target evidence, HCP-TWIP semantics, unresolved-target safety, mechanics/stress basis, onset classification, physics gaps, no-digitization rules, and exhaustive provenance assertions pass. `python -m pytest -q tests/test_p023_recovery_v17.py` passes all 24 tests. `python -m pytest -q` passes all 205 repository tests with 40 existing pandas `FutureWarning` messages. The full suite mechanically regenerated the same seven previously audited historical artifacts; exactly those files were restored to committed content. Final `git diff --check` and staged diff checks pass.

**Remaining gaps and downstream gate**

P023 lacks measured post-melt bulk chemistry; physical-batch and individual-replicate identities/results; exact numeric room temperature; annealed numeric grain sizes and matrix-Al curve values; exact mechanics for D-pass, 650-5, and 850-X; direct condition-quality TRIP/TWIP evidence for D-pass, 650-5, 650-30, 850-5, and 850-15; numeric alloy-specific SFE; and DeltaG. Global QC, feature coverage/schema statistics, and grouped split artifacts remain intentionally stale during the open collection batch. Refresh them non-destructively only after paper collection pauses and before any matrix construction.

**Git Commit**

Commit message: `Integrate verified P023 evidence into extended recovery v17`. The final hash is assigned after this entry is written.


### LOG-0027 — 2026-09-01 — GitHub Research Resource Library

**Objective and scope**

Organize the previously supplied metallurgy and materials-ML GitHub project references without cloning external repositories or changing scientific datasets. This was resource management only; no model training, data modification, synthetic data, scientific-value generation, or TRIP/TWIP label change was performed.

**Actions performed**

Created `resources/github_projects/` with SFE, CALPHAD, HEA, Atomistic, and ML_materials categories, twelve per-project Markdown reference entries, and a consolidated README table. Added the requested tracked `literature/` workspace and documented the resource/literature locations in the root README. Exact repository URLs are retained where the supplied name identifies them; broad names without a unique owner/repository use transparent GitHub repository-discovery links rather than invented coordinates.

**Scientific and provenance safeguards**

Each entry states purpose, possible FeMnCoCrN TRIP/TWIP relevance, and priority. The library explicitly prohibits treating links as endorsements, transferring unvalidated scientific values across alloy/method/temperature scopes, mixing computational and experimental domains, overwriting mechanism labels, or converting repeated observations into independent samples. No raw, interim, processed, split, report, or model artifact was modified.

**Validation**

A structural/content check verified all five required category directories, the requested project fields in every project entry, the consolidated table, twelve unique indexed entries, and the absence of nested Git repositories or large files. `git diff --check` passed.

**Git Commit**

Commit message: `Add metallurgy ML research GitHub resource library`. The final hash is assigned after this entry is written.


### LOG-0028 — 2026-09-01 — Scientific Screening of GitHub Resources

**Objective and scope**

Scientifically screen every Markdown reference in `resources/github_projects/` for its role and relevance to the FeMnCoCrN HEA TRIP/TWIP ML project. This task evaluated reference suitability only: no repository was downloaded, no dataset or mechanism label was modified, and no ML model was trained.

**Actions performed**

Added a `Scientific evaluation` section to all twelve project entries. Each section now states the scientific role, FeMnCoCrN relevance, allowed usage from the controlled set (feature engineering, SFE calculation, CALPHAD thermodynamics, and validation/reference only), and final priority (`Essential`, `Useful`, `Reference only`, or `Not relevant`). Expanded the consolidated README with `Scientific role`, `Possible ML usage`, and `Final priority` columns and definitions for interpreting the final-priority scale.

**Evaluation boundary and safeguards**

Concrete repository links were evaluated at the documented capability level, without executing or downloading their code. Entries represented only by GitHub discovery links received provisional project-family evaluations rather than invented implementation-specific claims; exact repository, license, methods, scope, and provenance must be resolved before adoption. Computational descriptors remain separate from experimental evidence and cannot overwrite TRIP/TWIP labels.

**Validation**

A structural/content check verified exactly twelve project entries; one scientific-evaluation section per entry; all required evaluation fields; controlled usage labels and final-priority values; and exact agreement between entry metadata and the twelve-row consolidated index. No file under `data/` or `models/` changed. `git diff --check` passed.

**Git Commit**

Commit message: `Evaluate GitHub resources for TRIP TWIP research`. The final hash is assigned after this entry is written.
