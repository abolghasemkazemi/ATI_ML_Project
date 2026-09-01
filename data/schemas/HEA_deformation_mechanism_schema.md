# General HEA Deformation Mechanism Dataset Schema

## Purpose and prediction unit

This prospective schema defines a generalized, physics-informed dataset for
predicting the deformation mechanism of high-entropy and medium-entropy alloys:

`alloy composition + processing conditions -> CALPHAD/thermodynamic descriptors -> stacking-fault-energy (SFE) descriptors -> initial microstructure -> machine-learning prediction -> Slip / TWIP / TRIP / Mixed`

One ML-eligible record represents **one independently supported material–processing–initial-microstructure–deformation-test condition immediately before loading**. Repeated strain stages, fields of view, measurements, or specimens are linked observations, not independent samples unless the source supports their independence. Source-native values must be preserved separately from harmonized or calculated values.

This document is a schema only: it contains no collected literature records,
scientific values, inferred labels, or trained models.

## Common conventions

- `NA` means not reported/not available and is never converted to zero.
- Numeric types are nullable. Text and categorical vocabularies retain a
  source-native companion where harmonization is performed.
- `reported experimental` describes measured or author-reported material/test
  information; `calculated` describes CALPHAD, SFE, or derived descriptors.
  Hybrid records must identify each field's origin rather than collapsing the
  two domains.
- Temperature-dependent predictions are stored at their calculation
  temperature; values at different temperatures or from different methods are
  separate linked observations, not silently averaged.
- Every populated scientific field requires source identity and a field-level
  location or computation record. Missing calculated descriptors remain `NA`;
  they are not estimated merely to complete the table.
- Units below are canonical storage units. The original unit and value remain
  in provenance when conversion is necessary.

## Provenance and record identity (required support fields)

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `record_id` | none | string | Administrative | Repository-assigned stable ID | Required; never reuse. |
| `source_id` | none | string | Administrative | Stable paper, report, or computation ID | Required for every record. |
| `doi_or_source_uri` | none | nullable string | Administrative | Publisher DOI or traceable source URI | `NA` only when genuinely unavailable; retain source citation. |
| `material_parent_id` | none | nullable string | Administrative | Documented material/composition lineage | `NA` if lineage is not established; never infer a batch. |
| `physical_batch_id` | none | nullable string | Reported experimental | Source methods/specimen metadata | `NA` unless explicitly documented. |
| `parent_experiment_id` | none | nullable string | Reported experimental | Source experimental design | Required when repeated/stage observations share a parent; otherwise conservatively unique. |
| `observation_id` | none | string | Administrative | Repository-assigned row ID | Required and unique. |
| `observation_role` | controlled category | categorical | Administrative | Curation decision with evidence | Required; distinguish independent condition, linked stage, support, and computational prediction. |
| `data_origin` | controlled category | categorical | Administrative | Source/method | Required: `EXPERIMENTAL`, `CALPHAD`, `DFT`, `MD`, `OTHER_COMPUTATIONAL`, or `HYBRID`. |
| `field_source_location` | page/table/figure/section | string or structured text | Administrative | Source document or computation artifact | Required for populated scientific values; field-level provenance may be stored in a linked long table. |
| `computation_id` | none | nullable string | Calculated | Versioned input deck, database, software, settings, and output | Required for calculated values; `NA` for purely experimental fields. |

## 1. Composition features

Element columns store fractions on the explicitly recorded `composition_basis`.
They must not mix wt.% and at.% within a record or be silently normalized.
Additional elements use the same `element_<symbol>` pattern and are also listed
in `other_alloying_elements` so no chemistry is discarded.

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `composition_as_reported` | source notation | string | Reported experimental | Paper composition/methods, certificate, or source table | Required when composition is reported; preserve verbatim notation. |
| `composition_basis` | `at.%` or `wt.%` | categorical | Reported experimental | Same source as composition | Required for numeric element fractions; never guess or convert without traceable inputs. |
| `element_Fe`, `element_Mn`, `element_Co`, `element_Cr`, `element_Ni`, `element_N` | at.% or wt.% per `composition_basis` | nullable float | Reported experimental | Nominal or measured chemistry table | `NA` when unreported; explicit zero only when source-supported. |
| `other_alloying_elements` | source notation | nullable string/list | Reported experimental | Composition table/formula | `NA` if none are reported; never discard minor elements. |
| `element_<symbol>` | at.% or wt.% per `composition_basis` | nullable float | Reported experimental | Nominal or measured chemistry table | Add a column/long-form entry for every other reported element; no inferred zero. |
| `composition_measurement_scope` | controlled category | categorical | Reported experimental | Source methods | `NA` if unclear; distinguish nominal, bulk measured, and local measurement. |
| `number_of_elements` | count | nullable integer | Calculated | Traceable composition parsing rule | `NA` until basis, inclusion threshold, and complete composition are established. |
| `VEC` | electrons/atom | nullable float | Calculated | Composition plus cited elemental VEC reference | `NA` without complete compatible composition, constants, method, and computation provenance. |
| `mixing_entropy` | J mol^-1 K^-1 | nullable float | Calculated | Composition and documented configurational-entropy equation | `NA` if required fractions/method are unavailable; do not assume ideality silently. |
| `atomic_size_mismatch` | % | nullable float | Calculated | Composition plus cited atomic-radius set and equation | `NA` without a complete compatible basis and referenced radii. |
| `electronegativity_difference` | dimensionless (method-defined) | nullable float | Calculated | Composition plus named electronegativity scale/equation | `NA` unless scale, equation, and composition basis are recorded. |

## 2. Processing features

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `homogenization_temperature` | K | nullable float | Reported experimental | Processing methods | `NA` if absent; retain original value/unit on conversion. |
| `homogenization_time` | h | nullable float | Reported experimental | Processing methods | `NA` if absent; multi-step schedules use a linked step table. |
| `solution_treatment_temperature` | K | nullable float | Reported experimental | Processing methods | `NA` if absent; do not equate with annealing unless source does. |
| `solution_treatment_time` | h | nullable float | Reported experimental | Processing methods | `NA` if absent; multi-step schedules remain ordered. |
| `annealing_temperature` | K | nullable float | Reported experimental | Processing methods | `NA` if absent; retain processing-state identity. |
| `annealing_time` | min | nullable float | Reported experimental | Processing methods | `NA` if absent; preserve source precision. |
| `cold_rolling_reduction` | % thickness reduction | nullable float | Reported experimental | Processing methods | `NA` when unreported; do not infer from qualitative wording. |
| `cooling_condition` | controlled category + source text | nullable categorical/string | Reported experimental | Processing methods | `NA` if absent; retain cooling rate separately when reported. |
| `cooling_rate` | K s^-1 | nullable float | Reported experimental | Processing methods/instrument record | `NA` unless explicitly reported. |
| `processing_route` | ordered text/category | string | Reported experimental | Full synthesis and thermomechanical history | Required for an eligible condition; unknown steps remain explicit rather than invented. |

## 3. CALPHAD and thermodynamic features

All calculated phase fields require calculation temperature, database, software
version, model settings, and composition-state provenance. Equilibrium and
metastable/suppressed-phase calculations are different methods.

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `calphad_temperature` | K | nullable float | Calculated | CALPHAD input/output | Required when any CALPHAD result is populated. |
| `calphad_phase_fractions` | fraction (0–1), phase-keyed | nullable structured numeric | Calculated | Thermo-Calc/CALPHAD output | `NA` when not calculated; never substitute measured fractions. |
| `calphad_fcc_fraction` | fraction (0–1) | nullable float | Calculated | CALPHAD output | `NA` when unavailable; method/state scope required. |
| `fcc_stability` | J mol^-1 or documented method-defined metric | nullable float | Calculated | CALPHAD output and declared definition | `NA` without an explicit metric definition; no qualitative-to-numeric conversion. |
| `bcc_tendency` | J mol^-1 or documented method-defined metric | nullable float | Calculated | CALPHAD metastability/phase output | `NA` without explicit calculation and definition. |
| `hcp_tendency` | J mol^-1 or documented method-defined metric | nullable float | Calculated | CALPHAD metastability/phase output | `NA` without explicit calculation and definition. |
| `gibbs_energy_fcc_minus_hcp` | J mol^-1 | nullable float | Calculated | CALPHAD phase Gibbs energies | `NA` unless sign convention, temperature, database, and state are recorded. |
| `gibbs_energy_fcc_minus_bcc` | J mol^-1 | nullable float | Calculated | CALPHAD phase Gibbs energies | `NA` unless sign convention, temperature, database, and state are recorded. |
| `phase_transition_information` | K and phase/path text | nullable structured text | Calculated or reported experimental (tagged) | CALPHAD transition scan or experimental phase study | `NA` if unavailable; store predicted and observed transitions in separate origin-tagged records. |
| `calphad_software_version` | none | nullable string | Calculated | Computation manifest | Required for calculated CALPHAD fields. |
| `thermodynamic_database` | database name/version | nullable string | Calculated | Computation manifest | Required for calculated CALPHAD fields. |
| `calphad_model_settings` | none | nullable structured text | Calculated | Input deck/computation manifest | Required; include suspended phases and equilibrium/metastable assumptions. |

## 4. Stacking-fault-energy features

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `sfe_value` | mJ m^-2 | nullable float | Experimental or calculated (tagged) | Direct measurement or method-specific computation | `NA` if only a qualitative claim, threshold, or bound exists; never transfer between alloys/methods. |
| `sfe_origin` | controlled category | categorical | Administrative | Source/method | Required with `sfe_value`: `EXPERIMENTAL` or `CALCULATED`. |
| `sfe_calculation_method` | method name/version | nullable string | Calculated | Equation/DFT/CALPHAD/other computation record | Required for calculated SFE; `NA` for experimental SFE. |
| `sfe_measurement_method` | method name | nullable string | Experimental | Experimental methods | Required for experimental SFE; `NA` for calculated SFE. |
| `sfe_temperature` | K | nullable float | Experimental or calculated (tagged) | Measurement conditions or calculation input | Required with a numeric SFE unless source truly omits it, in which case flag review. |
| `sfe_temperature_dependence` | mJ m^-2 K^-1 or method-defined curve/table | nullable float/structured numeric | Experimental or calculated (tagged) | Multi-temperature measurement/calculation | `NA` unless supported at multiple temperatures or explicitly reported. |
| `sfe_uncertainty` | mJ m^-2 | nullable float | Experimental or calculated (tagged) | Reported uncertainty or documented uncertainty analysis | `NA` if unreported; never fabricate error bars. |
| `sfe_uncertainty_type` | SD/SE/CI/range/model/etc. | nullable categorical | Experimental or calculated (tagged) | Same source as uncertainty | Required when uncertainty is populated; unknown reported ± remains explicitly unknown. |
| `sfe_source_scope` | none | string | Administrative | DOI/location or computation ID | Required for every SFE value; identify alloy, state, temperature, and method. |

**Scientific constraint:** SFE is one descriptor, not a deterministic TRIP/TWIP
rule. No universal SFE threshold may generate a mechanism label. Processing,
initial phase state, grain structure, loading, temperature, strain rate, and
other thermodynamic/kinetic factors remain part of the prediction context.

## 5. Initial microstructure features

Only microstructure available before the target-generating deformation test is
eligible as a predictor. Post-test phase fractions and twins are target evidence
or outcomes and must be stored outside these initial fields.

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `grain_size` | um | nullable float | Reported experimental | Pre-test EBSD/microscopy/source table | `NA` if absent; scope and statistic are required when populated. |
| `grain_size_statistic` | mean/median/range/etc. | nullable categorical | Reported experimental | Same source as grain size | `NA` if source omits it; do not assume mean. |
| `recrystallization_fraction` | fraction (0–1) | nullable float | Reported experimental | Pre-test EBSD/microstructure analysis | `NA` when not quantified; qualitative states stay text. |
| `initial_martensite_fraction` | fraction (0–1) | nullable float | Reported experimental | Pre-test XRD/EBSD/TEM | `NA` if absent; identify epsilon-HCP versus alpha-prime. |
| `initial_fcc_fraction` | fraction (0–1) | nullable float | Reported experimental | Pre-test phase characterization | `NA` if absent; never complement another phase unless exhaustive basis is proven. |
| `initial_hcp_fraction` | fraction (0–1) | nullable float | Reported experimental | Pre-test phase characterization | `NA` if absent; initial HCP alone does not establish deformation-induced TRIP. |
| `initial_bcc_fraction` | fraction (0–1) | nullable float | Reported experimental | Pre-test phase characterization | `NA` if absent; distinguish BCC from alpha-prime where source permits. |
| `texture_information` | ODF/pole figure/index/source text | nullable structured text/numeric | Reported experimental | Pre-test EBSD/XRD texture analysis | `NA` when unavailable; retain method, reference frame, and metric definition. |
| `microstructure_measurement_method` | method name/settings | nullable string | Reported experimental | Characterization methods | Required for populated microstructure values. |

## 6. Deformation-condition features

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `testing_temperature` | K | nullable float | Reported experimental | Mechanical-test methods | Required for ML eligibility when available; otherwise `NA` and review, never assume room temperature. |
| `strain_rate` | s^-1 | nullable float | Reported experimental | Mechanical-test methods | `NA` if unreported; distinguish engineering, true, and crosshead-derived rates. |
| `strain_rate_definition` | controlled/source text | nullable categorical/string | Reported experimental | Mechanical-test methods | Required when `strain_rate` is populated if definition is given. |
| `loading_condition` | controlled category + source text | string | Reported experimental | Mechanical-test methods | Required for an eligible condition; e.g., uniaxial tension/compression, cyclic, or shear. |
| `loading_orientation` | source notation | nullable string | Reported experimental | Specimen geometry/texture methods | `NA` if absent; do not infer from figures. |

## 7. Targets

### Primary target: `deformation_mechanism_class`

| Code | Meaning | Evidence requirement |
|---:|---|---|
| 0 | Slip dominated | Source-supported dominance under the exact test condition; missing TRIP/TWIP evidence is not sufficient. |
| 1 | TWIP dominated | Source-supported deformation twinning dominance under the exact condition; pre-existing annealing twins are insufficient. |
| 2 | TRIP (epsilon martensite) | Source-supported deformation-induced FCC-to-HCP/epsilon transformation dominance. |
| 3 | TRIP (alpha-prime martensite) | Source-supported deformation-induced alpha-prime transformation dominance. |
| 4 | Mixed TRIP/TWIP | Source-supported material participation of both deformation-induced transformation and twinning; retain phase/path detail. |

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `deformation_mechanism_class` | code 0–4 | nullable integer/categorical | Curated experimental target | Direct condition-specific experimental evidence and author interpretation | `NA` unless the exact class and dominance/mixed semantics are supported; never create from SFE, CALPHAD, missing evidence, or computational prediction. |
| `mechanism_evidence` | none | nullable structured text | Reported experimental | Condition-specific microscopy/diffraction/in-situ evidence and source text | Required for a populated class; retain phase, deformation stage, and evidence strength. |
| `mechanism_label_source_location` | page/table/figure/section | nullable string | Administrative | Original experimental source | Required for a populated class. |
| `mechanism_label_confidence` | controlled category | nullable categorical | Curated experimental | Documented evidence-grading rule | Required for a populated class; uncertainty never becomes a negative. |

Computationally predicted mechanisms may be retained in a separate
`predicted_mechanism_class` field keyed by `computation_id`, but **must never be
copied into the experimental primary target**. Existing binary/multilabel labels
also remain intact in their versioned datasets; migration to this five-class
target requires an explicit, evidence-reviewed mapping and is not authorized by
this schema.

### Secondary targets (when directly available)

Mechanical responses are outcomes, never predictors in a pre-deformation
mechanism model.

| Feature name | Unit | Data type | Experimental or calculated | Expected source | Missing value policy |
|---|---|---|---|---|---|
| `yield_strength` | MPa | nullable float | Reported experimental | Mechanical-test table/curve with stated definition | `NA` if absent; preserve proof/offset definition and statistic. |
| `ultimate_tensile_strength` | MPa | nullable float | Reported experimental | Tensile-test table/curve | `NA` if absent; do not digitize unless a separately approved protocol permits it. |
| `elongation` | % | nullable float | Reported experimental | Tensile-test table/curve | `NA` if absent; identify total/uniform/fracture measure. |
| `work_hardening_behavior` | MPa, dimensionless, or source-defined | nullable structured numeric/text | Reported experimental or derived (tagged) | Stress–strain/work-hardening report | `NA` if absent; retain definition and derivation, and never use as a pre-test predictor. |
| `mechanical_uncertainty` | target unit | nullable float/structured numeric | Reported experimental | Same source as mechanical target | `NA` if unreported; store uncertainty type and replicate count separately. |

## Eligibility and separation rules

1. Build predictor records only from information available before deformation;
   outcomes and post-test observations cannot leak into features.
2. Keep experimental measurements, author-reported calculations, and new
   repository computations in distinct origin-tagged fields/records. Each new
   computation must retain inputs, database/constants, software/version,
   settings, timestamp, and code/output artifact.
3. Never assign a class from SFE alone. No descriptor threshold, CALPHAD phase
   fraction, or absence of reported evidence creates a mechanism label.
4. Never create artificial labels, pseudo-replicates, or synthetic scientific
   observations. Unresolved or mixed evidence remains `NA` or explicitly mixed
   only when supported.
5. Group related papers, materials, batches, parent experiments, and repeated
   stages during validation. Row count is not independent sample count.
6. Literature collection, descriptor calculation, schema migration, and ML
   training are separate future, reviewed tasks; none is performed here.
