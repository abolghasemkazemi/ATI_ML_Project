# Computational Pipeline Architecture for General HEA Deformation-Mechanism Prediction

## 1. System overview

The proposed system is a **pre-deformation, condition-level, physics-informed prediction pipeline**. A user supplies a new high- or medium-entropy alloy (HEA/MEA) composition, its processing history, and the intended deformation conditions. The system validates and preserves those inputs, generates method- and condition-specific composition, thermodynamic, stacking-fault-energy (SFE), and initial-microstructure descriptors, applies a trained machine-learning model, and returns a mechanism-class prediction with uncertainty and provenance.

The workflow is:

1. Capture the alloy composition, processing route, and planned deformation condition without altering the source representation.
2. Validate units, composition basis, required fields, and prediction-time eligibility. Missing inputs remain missing; they are not silently converted to zero.
3. Calculate analytical composition descriptors from traceable reference data.
4. Run or import CALPHAD results for the specified alloy, thermal history, temperature, database, and model assumptions.
5. Calculate or import SFE descriptors, retaining the method, temperature, phase/reference state, source, and uncertainty.
6. Assemble processing-derived and explicitly pre-deformation microstructure descriptors. Post-deformation evidence and same-test mechanical outcomes are excluded from predictors.
7. Build a versioned feature record that distinguishes experimental observations from calculated quantities and records every computational dependency.
8. Apply the frozen preprocessing pipeline and a validated model to estimate class probabilities.
9. Report the predicted class, probability distribution, applicability/domain warnings, missingness, model and schema versions, and descriptor provenance.

The architecture defines infrastructure and interfaces; it does not assert that all descriptors are currently available or that the five-class target is already trainable. Experimental literature evidence remains the intended basis for mechanism targets, while computational results are predictors or validation evidence—not artificial experimental labels.

## 2. Input layer

Each prediction request represents one alloy/process/test condition. Original user values and normalized machine-readable fields should be stored side by side.

### 2.1 Composition

Required composition inputs are:

- **Elemental fractions:** element-symbol/fraction pairs, with an explicit basis (`at.%`, `wt.%`, mole fraction, or source-reported atomic ratio). The original formula must be retained. Fractions must be checked for range and total, but must not be silently normalized or converted when the basis or required constants are uncertain.
- **Alloy system:** a user-supplied or reproducibly generated family identifier (for example, the set of principal elements). This is descriptive grouping metadata, not a substitute for the full composition.

Validation should reject duplicate element keys and invalid units, flag incomplete or non-closing totals, and distinguish an explicitly reported zero from a missing value.

### 2.2 Processing

The input contract records, when applicable:

- **Homogenization:** temperature, duration, atmosphere, and cooling route.
- **Solution treatment:** temperature, duration, atmosphere, and quench/cooling route.
- **Annealing:** temperature, duration, atmosphere, and position in the process sequence.
- **Cold rolling:** reduction, pass information where known, and sequence relative to heat treatments.
- **Cooling condition:** furnace cooling, air cooling, water/oil quenching, controlled cooling rate, or original free text when no controlled term is defensible.

Processing is an ordered history, not a bag of independent fields. The system should retain raw descriptions, controlled codes, units, sequence, and source provenance. Unknown stages remain absent rather than being assumed not to have occurred.

### 2.3 Deformation

Required planned-test inputs are:

- **Temperature:** numeric value and unit, converted to a canonical unit only through an explicit conversion.
- **Strain rate:** value, unit, and definition (for example, engineering strain rate) where known.
- **Loading condition:** tension, compression, shear, cyclic/fatigue, or another controlled mode, plus orientation, stress state, and specimen direction when available.

The prediction scope must be declared. A model validated for pre-tensile classification cannot silently accept compression, cyclic loading, extreme-rate atomistic conditions, or an unrepresented temperature regime.

## 3. Descriptor generation layer

Every generated descriptor needs a value, unit, method/version, input-condition reference, source type, timestamp, uncertainty or quality flag where available, and missing-value reason. Descriptor generation must be deterministic for identical versioned inputs.

### 3.1 Composition descriptors

- **Valence electron concentration (VEC):** composition-weighted elemental VEC. Store the elemental reference table and citation/version; different valence conventions must not be mixed.
- **Mixing entropy:** ideal configurational mixing entropy calculated on a declared fractional basis. It is a model descriptor and must not be represented as measured entropy.
- **Atomic size mismatch:** a composition-weighted mismatch measure using a documented atomic-radius definition and reference table.
- **Electronegativity difference:** a composition-weighted dispersion using one named electronegativity scale.

These calculations require complete, compatible compositions and traceable constants. If prerequisites are missing, the descriptor remains unavailable with a reason code; the pipeline must not invent constants or impute scientific values during descriptor calculation.

### 3.2 CALPHAD descriptors

For the relevant temperature and process state, candidate outputs include:

- **Phase fractions:** equilibrium and, only where separately modelled, constrained/metastable fractions for FCC, BCC, HCP, and other predicted phases.
- **FCC stability:** method-defined indicators such as FCC phase fraction, driving force, or stability range; the exact definition must accompany the value.
- **BCC/HCP tendency:** phase fractions, driving forces, or competing-phase stability indicators, stored as distinct quantities rather than a single undocumented score.
- **Gibbs energy differences:** phase-specific differences with explicit sign convention, molar/reference basis, temperature, and magnetic/ordering treatment.
- **Phase-transition information:** predicted transition temperatures, phase appearance/disappearance ranges, and relevant metastable boundaries, with calculation assumptions.

Required provenance includes software and version, thermodynamic database and version/license identifier, composition basis, temperature/pressure, active phases, equilibrium or metastable status, suppressed phases, magnetic/ordering models, solver settings, and raw-result artifact hash. CALPHAD equilibrium is model output; it must not overwrite measured initial phase fractions or be presented as deformation kinetics.

### 3.3 SFE descriptors

The SFE feature group includes:

- **SFE value:** value and unit, with fault type and parent phase identified.
- **Calculation method:** thermodynamic estimate, generalized stacking-fault-energy (GSFE) calculation, atomistic method, or experimental inference/measurement.
- **Temperature dependence:** calculation/measurement temperature and, if a curve is used, its sampled range, interpolation policy, and model version.
- **Experimental/calculated source:** explicit origin, publication or computational-run identifier, uncertainty, and evidence grade.

Values from different methods, temperatures, chemical/magnetic states, or stable versus unstable fault definitions must remain separate. A thermodynamic SFE estimate, DFT/atomistic GSFE, and experimentally inferred bound are not interchangeable columns merely because they share energy-per-area units.

### 3.4 Microstructure and deformation descriptors

The feature assembly may include explicitly **pre-deformation** phase fractions, grain size and definition, texture/orientation summaries, precipitate state, annealing-twin state, dislocation-density information, and processing-induced martensite where supported. It may also encode the planned temperature, strain rate, and loading mode. Each measurement must retain technique, material state, and source scope.

Post-test phase evolution, deformation twins, work-hardening response, strength, elongation, fracture features, or any observation made after loading begins are target evidence or outcomes, not pre-deformation predictors.

## 4. Computational tools layer

Tool adapters should expose a common request/result contract while preserving tool-specific inputs, logs, and raw outputs. Tool agreement must not be assumed; cross-tool comparisons require compatible databases, phases, and assumptions.

### 4.1 CALPHAD tools

| Tool | Advantages | Limitations and controls |
|---|---|---|
| **Thermo-Calc** | Mature commercial solver; extensive assessed databases; strong phase-equilibrium, property-diagram, and automation capabilities; commonly used in alloy design. | Requires licensed software/databases; reproducibility depends on database/version and configured models; proprietary internals can limit portability. Equilibrium outputs do not by themselves represent processing kinetics or deformation mechanisms. |
| **pycalphad** | Open-source Python interface; transparent scripting; convenient integration with data pipelines, parameter studies, and reproducible tests. | Scientific coverage depends on the available compatible database and model implementation; convergence and phase-selection choices need auditing; results are not automatically equivalent to a commercial database calculation. |
| **OpenCALPHAD** | Open-source CALPHAD engine suitable for scriptable, inspectable workflows and reduced vendor lock-in. | Database availability, feature coverage, interfaces, and validation breadth may be more limited for a particular HEA system; integration and cross-tool verification can require additional engineering. |

The architecture should implement one adapter per engine and store engine/database provenance in the result rather than forcing outputs into provenance-free phase columns.

### 4.2 SFE tools and approaches

| Approach | Advantages | Limitations and controls |
|---|---|---|
| **Thermodynamic models** | Relatively efficient; connect chemical free-energy differences and interfacial terms to temperature/composition; suitable for screening when assumptions are documented. | Sensitive to thermodynamic database, reference states, interface-energy assumptions, magnetic effects, and metastable-phase treatment; may approximate an intrinsic SFE rather than a complete fault-energy landscape. |
| **GSFE approaches** | Provide the energy landscape along a defined slip path and can distinguish stable and unstable fault energies; useful for mechanistic interpretation. | Computationally expensive; sensitive to supercell, chemistry/configuration, relaxation, magnetic state, exchange-correlation potential or interatomic potential, and often limited temperature treatment. One chemical configuration may not represent a disordered HEA. |
| **Atomistic validation methods** | DFT, molecular statics, and molecular dynamics can test local chemistry, fault structures, dislocation/twin nucleation hypotheses, and trends beyond simple thermodynamic estimates. | Strong scale, rate, potential, boundary-condition, and sampling limitations; DFT is size/temperature constrained, while MD commonly uses rates far above experiments. Validation results must remain computational-domain evidence and cannot become experimental labels. |

A multi-fidelity design may compare thermodynamic SFE with GSFE or atomistic evidence, but should retain separate features, discrepancies, applicability flags, and uncertainties rather than averaging incompatible values.

## 5. Physics interpretation layer

The interpretation layer converts descriptors into **hypotheses and contextual features**, not deterministic labels:

- A **relatively low SFE** under the applicable method and condition may facilitate wider partial-dislocation separation, stacking faults, and an epsilon-martensite tendency, which can increase the possibility of TRIP when the FCC-to-HCP driving force, stress state, kinetics, and initial phase stability also permit transformation.
- An **intermediate SFE regime** may make deformation twinning competitive with dislocation glide and therefore support TWIP possibility, subject to grain size, texture, temperature, strain rate, resolved stress, initial microstructure, and other barriers.
- A **relatively high SFE** may favor easier cross-slip and slip-dominated plasticity relative to faulting, twinning, or martensitic transformation under otherwise comparable conditions.

These are qualitative tendencies, not universal thresholds or if/then rules. Reported SFE regimes depend on alloy system, temperature, method, and definition. Mechanisms may coexist or activate sequentially, and multiple factors control their activation. FCC/BCC/HCP stability, Gibbs driving forces, chemical and magnetic state, grain size, texture, precipitates, processing-induced defects, loading mode, temperature, strain rate, and stress evolution all influence activation. Consequently, this layer may produce interpretable indicators and consistency warnings, but the final class must come from a model trained on condition-specific evidence and validated outside correlated study/material groups.

## 6. Machine-learning layer

### 6.1 Input features

The model-facing feature record may contain:

- **Composition:** elemental fractions and validated analytical composition descriptors.
- **CALPHAD descriptors:** method-specific phase stability, phase fractions, Gibbs energy differences, and transition information.
- **SFE:** method-, temperature-, phase-, and source-specific SFE/GSFE descriptors.
- **Processing:** ordered homogenization, solution-treatment, annealing, rolling, and cooling variables.
- **Microstructure:** only information available at the frozen prediction moment, including initial phase fractions, grain size, texture, precipitates, and initial defect state where supported.
- **Deformation plan:** temperature, strain rate, and loading condition.

Preprocessing (unit conversion, encoding, missingness handling, scaling, and feature selection) must be fitted only on training data and versioned with the model. Paper, DOI, observation IDs, evidence/confidence fields, post-deformation variables, and same-test mechanical outcomes are audit or grouping controls—not ordinary predictors.

### 6.2 Prediction targets

The prospective single-label target contract is:

| Code | Target class |
|---:|---|
| `0` | Slip dominated |
| `1` | TWIP dominated |
| `2` | epsilon TRIP |
| `3` | alpha-prime TRIP |
| `4` | Mixed TRIP/TWIP |

“Dominated” requires an operational evidence definition; occurrence alone is not automatically dominance. The five-class contract must not be backfilled by silently translating existing binary TRIP/TWIP fields. Ambiguous, multi-stage, or insufficiently supported conditions remain unresolved until an explicit evidence review.

### 6.3 Training, validation, and inference contract

Training data should use one justified independent condition per analytical unit. Repeated stages, replicates, sibling processing states, materials, and papers require parent-aware grouping. Validation should prioritize study/material/paper-grouped partitions and report per-class support, class probabilities, calibration where feasible, and uncertainty; row-random splits are not acceptable when related observations can cross folds.

At inference, the service should return all five probabilities, the selected class, an out-of-domain/applicability assessment, missing-feature flags, and the versions of schema, descriptor generators, reference tables, computational databases, preprocessing pipeline, and model. Low confidence or out-of-domain input should trigger abstention/review rather than a falsely certain mechanism assignment.

## 7. Software architecture proposal

```text
src/
├── descriptors/
├── thermodynamics/
├── sfe/
├── preprocessing/
├── models/
└── prediction/
```

- **`src/descriptors/`** — validates composition prerequisites and calculates VEC, ideal mixing entropy, atomic-size mismatch, electronegativity difference, and initial-microstructure/condition feature assemblies. Owns reference-table interfaces but not undocumented constants.
- **`src/thermodynamics/`** — defines the common CALPHAD request/result schema; implements Thermo-Calc, pycalphad, and OpenCALPHAD adapters; manages phase-selection policies, database metadata, run manifests, parsing, and raw-output hashes.
- **`src/sfe/`** — implements or integrates thermodynamic SFE and GSFE/atomistic workflows; keeps stable/unstable and method-specific values separate; records temperature, phase, configuration, uncertainty, and calculation provenance.
- **`src/preprocessing/`** — performs schema validation, unit handling, prediction-time leakage exclusion, categorical encoding, missingness policy, feature alignment, and fitted transformations. Training and inference use the same serialized pipeline.
- **`src/models/`** — contains model definitions, grouped-training/evaluation routines, probability calibration, metrics, model cards, and artifact serialization. It must not contain data-extraction shortcuts or target-derived features.
- **`src/prediction/`** — orchestrates a new request from validated input through descriptor services, feature assembly, applicability checks, model inference, explanation, uncertainty, and a provenance-rich response.

Shared typed schemas, configuration, provenance utilities, and artifact storage may be added as the implementation matures. Clear interfaces should allow a computational tool to be replaced without changing target semantics or erasing its identity.

## 8. Data flow diagram

```text
New HEA prediction request
  ├─ Composition: elements + fractions + basis + alloy system
  ├─ Ordered processing history
  └─ Planned deformation: temperature + strain rate + loading
                         │
                         ▼
              Input/schema validation
       (preserve originals; units; missingness;
        applicability and prediction-time checks)
                         │
          ┌──────────────┼─────────────────┐
          ▼              ▼                 ▼
  Composition       CALPHAD adapter     SFE workflow
  descriptors       + database/run      + method/run
  VEC, entropy,     provenance          provenance
  size, EN          phase/Gibbs data    SFE/GSFE data
          └──────────────┼─────────────────┘
                         ▼
       Pre-deformation microstructure + process/test
                    feature assembly
                         │
                         ▼
          Frozen preprocessing and feature schema
                         │
                         ▼
             Validated five-class ML model
                         │
                         ▼
  Probabilities + Slip/TWIP/epsilon-TRIP/alpha-prime-TRIP/Mixed
       + uncertainty + applicability warnings + explanation
       + input/descriptor/database/model provenance manifest
```

This design is intentionally computational-pipeline-first: it establishes the information contracts, scientific boundaries, and reproducibility requirements needed before constructing a new generalized dataset or authorizing simulations and model training.
