# Feasibility Study: General HEA Deformation-Mechanism Prediction Framework

## 1. Executive assessment

The proposed framework is **practically achievable as a staged, multi-fidelity research program**, but it is not presently feasible as a universal, fully automated predictor for arbitrary high-entropy alloys (HEAs). Composition descriptors and a provenance-aware literature dataset are technically straightforward. The principal constraints are thermodynamic-database coverage, the cost and method dependence of stacking-fault-energy (SFE) calculations, incomplete processing/microstructure reporting, and limited independent, defensible Slip/TWIP/TRIP/Mixed labels.

A credible minimum viable pipeline (MVP) can use traceable analytical composition descriptors, reported pre-deformation process and microstructure fields, method-separated reported or thermodynamic SFE, available CALPHAD results, and conservative grouped machine-learning validation. It must support missing values and cannot require CALPHAD or SFE for every condition. An advanced pipeline can add licensed HEA databases, automated equilibrium/metastable calculations, uncertainty propagation, selected generalized stacking-fault-energy (GSFE) calculations, and atomistic validation. These higher-fidelity calculations should validate or enrich selected regions of chemistry space rather than be treated as a prerequisite for every literature condition.

The framework could support an Elsevier-level research article if its contribution is framed as a rigorously validated, uncertainty-aware and provenance-preserving framework rather than a universally accurate mechanism classifier. Publication readiness depends more on independent label quality, leakage-safe external or grouped validation, and ablation/uncertainty analysis than on adding the most expensive simulation method.

### Feasibility by component

| Component | Practical feasibility | Principal constraint | Appropriate initial role |
|---|---|---|---|
| Analytical composition descriptors | High | Traceable, convention-consistent elemental reference data | Core MVP features |
| CALPHAD | Moderate and alloy-system dependent | Assessed database coverage and licensing | Optional/missingness-aware MVP; core advanced feature family |
| Thermodynamic SFE | Moderate | Database/reference-state/interface assumptions | Screening descriptor with uncertainty and method tags |
| GSFE/atomistic SFE | Low to moderate at broad scale | Cost, disordered configurations, magnetism, potentials and temperature | Targeted validation, not exhaustive production |
| Literature process/microstructure/labels | Technically feasible, scientifically labor-intensive | Missingness, inconsistent definitions, correlated observations and class imbalance | Target/evidence backbone |
| Machine learning | Conditionally feasible | Independent sample and class support, not raw row count | Begin only after dataset and validation gates are met |

## 2. Computational workflow feasibility

### A. Composition descriptors

For atomic fractions \(c_i\), the intended descriptors are simple deterministic calculations once the composition basis and reference constants are valid:

- **Valence electron concentration (VEC):** a composition-weighted elemental valence value. Implementation is easy, but the adopted valence convention must be fixed and cited.
- **Ideal mixing entropy:** \(-R\sum_i c_i\ln c_i\). Implementation is easy for a complete atomic-fraction vector. It is an ideal configurational descriptor, not measured thermodynamic entropy; zero fractions are omitted from the logarithm.
- **Atomic size mismatch:** a weighted dispersion about the composition-weighted mean radius. Implementation is easy to moderate because metallic, covalent and other radius definitions are not interchangeable.
- **Electronegativity difference:** a weighted dispersion on a declared scale. Implementation is easy, but one scale must be used consistently.

#### Availability and data sources

Suitable reference data can come from peer-reviewed elemental-property compilations, critically reviewed handbooks, or versioned materials-data packages whose underlying definitions and citations are inspectable. Composition may come from nominal alloy definitions or measured bulk chemistry, but these must remain separate. Weight-to-atomic conversion requires complete chemistry and traceable atomic weights; an uncertain basis must not be silently converted or normalized.

The repository should maintain a versioned reference table containing element, value, unit or convention, original source, source version/date, and any applicability note. Package convenience APIs may assist implementation, but package output is not sufficient provenance by itself. A descriptor should remain unavailable when an element or composition basis is unsupported.

#### Implementation difficulty and resources

The arithmetic, validation and unit tests are low difficulty and run effectively instantaneously on a normal computer. The scientifically significant work is reference-table governance: choosing consistent definitions, citing them, testing known limiting cases, and preventing silent normalization. Descriptor uncertainty can be explored by recomputing against defensible alternative conventions, but alternatives should not be averaged without justification.

**Assessment:** fully feasible for the MVP once the open P1 reference-constant gap is resolved with traceable sources. These descriptors are useful but cannot independently determine deformation mechanism.

### B. CALPHAD calculations

#### Tool options

| Tool | Feasibility and strengths | Database and multicomponent constraints | License/deployment implications |
|---|---|---|---|
| **Thermo-Calc** | Mature equilibrium/metastable calculations, batch automation, property diagrams and established alloy workflows. Often the lowest engineering-risk route when an appropriate database is available. | Useful HEA coverage depends on the licensed assessed database and the specific element/phase space. Extrapolation grows less reliable away from assessed binaries/ternaries and validated multicomponent regions. Convergence does not prove physical validity. | Commercial engine and database licenses are required. Compute nodes, containers and collaborators may need separate or network licensing; raw input, version and results must be archived for reproducibility. |
| **pycalphad** | Open-source, Python-native, transparent and well suited to reproducible parameter sweeps and pipeline integration. | It does not supply universal HEA thermodynamics. A compatible TDB database with permission and relevant assessments is still required. Model support, phase definitions, numerical convergence and performance must be validated per system. | The software is open-source, but many high-value databases are not. Deployment is straightforward when a redistributable database exists. |
| **OpenCALPHAD** | Open-source engine that reduces solver vendor lock-in and permits inspectable scripted calculations. | The decisive limitation remains database availability. Interface maturity, supported models, automation effort and validation breadth may be less convenient for a particular multicomponent system. | Engine use can be open, subject to its license, while database rights remain separate. Additional adapter and validation effort should be budgeted. |

#### Database availability for HEAs

No engine makes an unassessed composition space reliable. HEA calculations require a database whose elements, solution phases, ordered phases, magnetic models and relevant compounds overlap the proposed chemistry. A database marketed for HEAs may still be strong only within particular subspaces. Higher component count expands the chance of missing parameters and extrapolation; it also increases possible phases, numerical complexity and the difficulty of validating metastable states.

Every result therefore needs the database name and version, permitted phase set, suppressed phases, temperature/pressure path, equilibrium or metastable status, magnetic/ordering treatment, convergence status and raw-output identifier. Predictions should carry an applicability flag based on database coverage and validation evidence. CALPHAD equilibrium phase fraction must not replace a measured initial phase fraction or be interpreted as deformation kinetics.

#### Multicomponent limitations

- Assessments are built largely from lower-order systems; multicomponent calculations can compound extrapolation uncertainty.
- Composition-dependent magnetic and ordering effects can materially affect FCC/HCP/BCC relative stability.
- Trace elements and precipitates may require phases or elements not jointly covered by one database.
- Equilibrium calculations may poorly represent rapid quenching, segregation, retained metastable phases or a specific process history. Scheil, constrained equilibrium or kinetic calculations answer different questions and must be identified separately.
- Solver agreement is not an independent validation when tools use the same thermodynamic description; disagreement may reflect model support or numerical choices rather than physics alone.

#### Alternatives when full CALPHAD is unavailable

1. Retain literature-reported, source-scoped phase-stability or Gibbs-energy results as method-tagged fields.
2. Use measured pre-deformation phase constitution as an experimental descriptor, without pretending it is a CALPHAD substitute.
3. Calculate only within well-covered alloy subsystems and mark other conditions out of domain.
4. Train a missingness-aware baseline without CALPHAD, then perform a paired-subset ablation where reliable calculations exist.
5. Use targeted first-principles or atomistic calculations to investigate a narrow scientific question, not to fabricate broad database coverage.
6. Collaborate with a licensed thermodynamics group or acquire a suitable commercial database for the advanced phase.

**Assessment:** technically automatable, but scientifically and financially conditional. CALPHAD should be optional in the MVP and database-qualified in the advanced pipeline.

### C. SFE calculation

SFE is not a single method-independent ground truth. Stable intrinsic SFE, unstable fault energies, fault-path barriers, temperature-dependent effective values and experimentally inferred bounds answer different questions. All values require fault type, parent phase, units, temperature, chemical configuration, magnetic state, method and uncertainty.

| Approach | Expected accuracy and interpretability | Computational cost | Scalability |
|---|---|---|---|
| **Thermodynamic SFE models** | Useful for composition/temperature trends when FCC-to-HCP free-energy differences, interfacial terms, molar/area conversion and magnetic/reference states are appropriate. Accuracy may be dominated by database and interface-energy assumptions; uncertainty should be propagated or sensitivity-tested. | Low once reliable CALPHAD quantities and model inputs exist; broad parameter sweeps are practical on a workstation. | Best screening option, but only across database-qualified chemistry and temperature space. |
| **Electronic-structure GSFE (commonly DFT)** | Can resolve stable/unstable energies and slip paths with controlled electronic structure. Results are sensitive to supercell size, local chemical arrangements, relaxation, magnetic configuration, exchange-correlation treatment and finite-temperature approximations. A single ordered configuration is not representative of a disordered HEA. | High: many atomic configurations, fault displacements and magnetic states may be needed; convergence studies multiply cost. | Poor for exhaustive large HEA datasets; appropriate for selected alloys and mechanistic validation on HPC. |
| **Classical atomistic GSFE / molecular statics** | Efficient if a validated multicomponent interatomic potential covers the chemistry and defect physics. Potential error can exceed the trend of interest; validation against experiment or first-principles data is essential. | Moderate; workstation use may be possible for small statics problems, with HPC useful for ensembles. | Moderate only for alloy spaces with credible potentials. |
| **Molecular dynamics** | Adds temperature, evolving defects and local processes but operates at limited length/time scales and commonly non-experimental strain rates. It tests hypotheses rather than directly reproducing experimental labels. | Moderate to very high depending on atoms, duration, replicas and potential. | Suitable for targeted campaigns on CPU/GPU clusters, not universal per-record enrichment. |

#### Recommended SFE strategy

Use a tiered strategy: (1) preserve reported experimental or calculated values without conflation; (2) use thermodynamic SFE as a screening feature where inputs are qualified; (3) perform sensitivity analysis for interface, magnetic and reference-state assumptions; and (4) choose a small, scientifically motivated subset for GSFE/atomistic validation. Compare methods as separate estimates with discrepancies and uncertainty, rather than averaging them into one SFE column. Experimental validation may include suitably scoped literature measurements/inferences or new collaboration-based measurements; a mechanism label itself must not be used as a circular SFE measurement.

**Assessment:** thermodynamic SFE is moderately scalable; robust GSFE/atomistics across general HEA composition space is not. Targeted multi-fidelity validation is feasible.

### D. Experimental data requirements

Literature evidence is required because computational thermodynamics and SFE do not by themselves establish the observed deformation mechanism. One analytical record should represent a defensible alloy/process/test condition, with repeated stages and related specimens linked to their parent rather than treated as independent samples.

| Information | Minimum fields and scope | Why it is required / frequent limitation |
|---|---|---|
| **Composition** | Original formula; nominal or measured status; at.%/wt.%/ratio basis; bulk/local measurement scope; elemental values; DOI/paper and location | Defines chemistry and descriptor eligibility. Nominal, bulk and local chemistry cannot be substituted silently. |
| **Processing history** | Ordered casting/AM/powder route, homogenization, rolling/deformation, annealing/solution treatment, time, temperature, atmosphere and cooling/quench; initial-state identifier | Processing controls segregation, phase state, grain size and defects. Missing steps must remain unknown. |
| **Initial microstructure** | Pre-test FCC/BCC/HCP/other phases and fractions; grain size plus definition; texture; precipitates; twins/stacking faults/dislocation state; measurement method and material state | Needed to separate initial phases or annealing twins from deformation-induced TRIP/TWIP and to avoid outcome leakage. |
| **SFE** | Value/bound, units, temperature, method, fault/phase definition, experimental/calculated origin, uncertainty, assumptions and source location | Heterogeneous values cannot be pooled as equivalent. Missing SFE should remain missing. |
| **Observed mechanism** | Slip/TWIP/epsilon-TRIP/alpha-prime-TRIP/Mixed evidence; occurrence versus dominance; phase of twinning; loading stage; technique; direct/author-attributed/inferred evidence grade; unresolved state | Provides the target. Initial martensite/twins and absence of reported evidence do not establish positive/negative labels. |
| **Deformation condition** | Test temperature, strain rate and definition, loading mode, orientation/specimen direction, stress state and endpoint | Mechanism labels are condition-specific, not permanent alloy properties. |
| **Mechanical properties** | Yield definition and stress basis, UTS, elongation type, work-hardening measures, mean/uncertainty/replicate count and units | Useful secondary outcomes and scientific context, but same-test response is excluded from pre-test mechanism predictors. |
| **Independence/provenance** | DOI, stable paper ID, material/batch/replicate/parent condition IDs, observation/stage ID, source location, extraction/review record | Required for auditability and grouped validation; reported averages do not create pseudo-replicates. |

Manual source review is likely the dominant labor requirement. A quality gate should distinguish directly observed mechanisms from author interpretation, and occurrence from dominance. Conditions without defensible labels remain useful for descriptor coverage or future prediction but not supervised target training.

## 3. Resource requirements

### 3.1 Software

#### MVP stack

- Python and environment locking;
- tabular/numerical tooling such as pandas, NumPy and SciPy;
- scikit-learn for preprocessing, grouped validation, baselines, calibration and metrics;
- plotting/reporting tools such as Matplotlib and seaborn;
- schema/unit validation tools where useful;
- Git, checksums, structured configuration and an artifact manifest for provenance;
- optional pycalphad plus a legally usable, scientifically relevant TDB database.

The exact dependencies should be pinned when implementation begins. An open-source-only MVP can calculate analytical descriptors and train/evaluate literature-based baselines. Open-source CALPHAD is possible only when a suitable database is available; the engine and database are separate dependencies.

#### Advanced or commercial dependencies

- Thermo-Calc and one or more suitable licensed thermodynamic/mobility databases, with automation and compute-node rights as needed;
- OpenCALPHAD or pycalphad adapters for comparison where database permissions allow;
- electronic-structure software for DFT/GSFE, subject to its own license, pseudopotential/data rights and HPC installation;
- atomistic software such as LAMMPS with validated multicomponent potentials;
- a workflow scheduler and experiment/artifact tracking for large parameter sweeps;
- optional container or module environments, provided commercial license terms permit them.

Commercial software is not mandatory for the MVP or for a publishable methods article, but a credible database is mandatory for any claimed CALPHAD result. Budget planning must separately cover the solver, databases, automation/API access and cluster licensing.

### 3.2 Hardware

#### Normal computer

A current multicore laptop or workstation with ordinary developer memory and storage is sufficient for reference-table validation, analytical descriptors, literature tables, pycalphad trials on limited systems, preprocessing, conventional tabular ML, grouped cross-validation and documentation. Storage needs are modest for tabular artifacts but should include raw CALPHAD outputs and environment manifests. Memory/runtime should be benchmarked on the actual database and phase set rather than promised generically.

#### Workstation or small server

A higher-memory multicore workstation is beneficial for wide CALPHAD grids, bootstrap/grouped-validation repeats, explainability calculations, and small classical atomistic/statics studies. Parallel jobs need deterministic run identifiers and must not overwrite each other.

#### HPC

HPC is **not required for the MVP**. It becomes necessary or strongly advantageous for:

- DFT GSFE convergence across multiple disordered chemical and magnetic configurations;
- first-principles finite-temperature or large-supercell studies;
- statistically meaningful molecular-dynamics replicas or large defect systems;
- broad CALPHAD/SFE uncertainty sweeps when turnaround or memory becomes limiting;
- nested validation/hyperparameter experiments once the dataset is scientifically adequate.

An advanced HPC plan should account for CPU/GPU architecture, per-job memory, scratch and archival storage, scheduler integration, software/database licenses on compute nodes, checkpointing, raw output retention and a realistic allocation. A pilot benchmark should determine resources before requesting a large allocation.

## 4. Proposed realistic workflow

### 4.1 Minimum viable pipeline: available-resource path

1. **Freeze the scientific contract.** Define condition identity, five-class evidence rules, prediction moment, domain, exclusions and abstention policy before dataset construction.
2. **Create traceable elemental reference tables.** Add cited, versioned VEC, radius and electronegativity definitions; validate compositions and calculate analytical descriptors only when prerequisites are satisfied.
3. **Construct a provenance-rich experimental condition table.** Extract composition, ordered processing, initial microstructure, deformation condition, observed mechanism evidence and mechanical outcomes. Link repeated observations and group related conditions.
4. **Retain SFE/CALPHAD opportunistically.** Import source-reported or calculate thermodynamic descriptors only for compatible, qualified conditions. Store method/database/temperature provenance and missing-reason codes. Do not exclude every condition lacking these fields.
5. **Audit target and feature readiness.** Report independent per-class support, missingness by class/alloy family, evidence grades, label ambiguity, source-family overlap and prediction-time leakage exclusions.
6. **Establish transparent baselines.** Only after the open data gates are met, compare composition/process-only and initial-microstructure models with physics-enriched subsets. Use simple regularized/tree baselines before complex methods.
7. **Validate by independent group.** Keep paper/study/material/parent conditions together. Prefer held-out alloy families or genuinely external papers when support permits. Report classwise results, calibration/uncertainty, confidence intervals and abstentions; do not use repeated rows as sample-size inflation.
8. **Perform ablation and sensitivity analysis.** Test whether CALPHAD/SFE adds reproducible value beyond composition and processing, and whether conclusions survive uncertain labels and descriptor definitions.

This path can run on a normal workstation with open-source software. It can demonstrate feasibility and yield a defensible baseline, but it should not claim coverage outside represented chemistry, processing, loading and database domains.

### 4.2 Advanced pipeline: additional-tool path

1. Acquire or access assessed HEA thermodynamic databases and automate versioned Thermo-Calc and/or open-engine calculations.
2. Define database-coverage and calculation-quality scores; compare selected tool/database combinations using matched assumptions.
3. Generate equilibrium and scientifically justified metastable/processing-aware descriptors, without equating them to observed kinetics.
4. Propagate thermodynamic and interfacial assumptions into SFE uncertainty distributions or sensitivity intervals.
5. Select representative, boundary and disagreement cases for DFT GSFE or validated-potential atomistics on HPC.
6. Where feasible, obtain independent experimental validation through literature-held-out tests or collaboration; pre-register which results validate SFE, phase state and deformation mechanism.
7. Train a multi-fidelity or missingness-aware model that preserves fidelity/domain indicators and can abstain outside validated applicability.
8. Release reproducible schemas, code, permitted inputs, manifests, grouped splits and sensitivity results; do not redistribute restricted databases.

The advanced path requires commercial access and/or collaborators, HPC allocation, substantially more scientific review, and explicit uncertainty modelling. It should be pursued after the MVP establishes that label support and validation design justify the investment.

## 5. Scientific risks and mitigation

| Risk | Consequence | Mitigation and decision gate |
|---|---|---|
| **SFE uncertainty and method heterogeneity** | Spurious thresholds, method-confounded ML relationships and incorrect mechanistic interpretation | Preserve method-specific fields; record temperature/fault/magnetic/configuration assumptions; quantify sensitivity; validate selected cases experimentally and with higher-fidelity GSFE/atomistics; never use one universal threshold. |
| **Missing or out-of-domain CALPHAD databases** | Unreliable phase/Gibbs descriptors or systematic feature missingness by alloy family | Qualify coverage before calculation; use a hybrid experimental/computational approach; retain measured initial phases; allow CALPHAD-missing baselines; collaborate/acquire databases only for justified systems; flag extrapolation and abstain. |
| **Limited or imbalanced TRIP/TWIP labels** | Unstable multiclass models, incomplete folds and exaggerated accuracy | Use careful literature selection for independent, condition-specific evidence; prioritize true negative and Slip-dominated support; leave ambiguous labels unresolved; group related conditions; report per-class support and avoid synthetic scientific labels. |
| **Occurrence versus dominance ambiguity** | The proposed five classes cannot be assigned consistently | Write an evidence rubric before migration; retain binary/source labels; require direct or explicitly graded evidence for dominance; allow unresolved/multilabel analysis and abstention. |
| **Processing and microstructure missingness** | Composition or paper identity becomes a proxy; poor cross-study transfer | Preserve missingness reasons and measurement scope; compare feature tiers on matched subsets; conduct missingness-by-class/source audits; seek targeted validation rather than generic imputation. |
| **Leakage from post-test evidence or mechanics** | Inflated prediction performance | Freeze the prediction moment before loading; use post-test phase/twin evidence only to establish targets and mechanics as secondary outcomes; audit every feature and preprocessing transformation. |
| **Correlated observations and alloy-family overlap** | Optimistic validation and understated uncertainty | Use parent/study/material/paper groups; collapse or link stages; disclose effective independent count; include family-held-out or external validation where feasible. |
| **Thermodynamic-to-kinetic mismatch** | Equilibrium stability is overinterpreted as a deformation prediction | Treat CALPHAD/SFE as descriptors, include test state and initial microstructure, discuss kinetics and stress-state limitations, and validate mechanism predictions experimentally. |
| **Small data with high-dimensional chemistry** | Overfit, poorly calibrated models and unstable feature importance | Prefer parsimonious models, nested grouped tuning only when support permits, regularization, bootstrap/group sensitivity, predeclared feature families and honest uncertainty/abstention. |
| **Reproducibility/licensing limits** | Others cannot rerun commercial calculations | Publish input schemas, versions, settings, hashes and derived-result provenance; release open-engine demonstrations where legal; state database restrictions; archive raw outputs without redistributing protected content. |

## 6. Publication feasibility

### Can it produce an Elsevier-level research article?

**Yes, conditionally.** The integration of processing-aware experimental evidence with provenance-separated CALPHAD/SFE descriptors is scientifically publishable if the work demonstrates more than a flowchart and avoids claiming universal mechanism prediction. Journal suitability will depend on scope and execution; no publisher tier or acceptance can be guaranteed.

#### Potential scientific novelty

- a general HEA condition-level mechanism contract that distinguishes Slip, TWIP, epsilon-TRIP, alpha-prime-TRIP and Mixed behavior;
- explicit coupling of composition, ordered processing, initial microstructure, test conditions, thermodynamic stability and method-resolved SFE;
- multi-fidelity uncertainty and applicability handling rather than an undocumented single SFE feature;
- evidence-graded targets, strict pre-deformation leakage control and parent/study/material-grouped validation;
- a quantitative ablation showing when physics-derived descriptors improve—or fail to improve—generalization beyond composition/process baselines;
- transparent negative results about database or label coverage, which can itself define realistic boundaries for the field.

Novelty must be demonstrated against a focused literature review at publication time; it cannot be assumed from architecture alone.

#### Expected limitations to disclose

- restricted alloy-system, phase, processing and loading coverage;
- incomplete and non-random literature reporting;
- small, imbalanced independent class support, especially defensible negative and dominance labels;
- heterogeneous SFE definitions and uncertainties;
- CALPHAD database extrapolation and commercial reproducibility constraints;
- equilibrium/atomistic scale mismatch with experimental deformation kinetics;
- inability to infer causality from a retrospective observational dataset;
- reduced precision or abstention for out-of-domain alloys.

#### Required validation

At minimum, a research article should include:

1. a reproducible schema, target rubric and provenance audit;
2. independent-condition and per-class support—not raw-row sample claims;
3. prediction-time leakage review and grouped study/material/paper validation;
4. simple, competitive composition/process baselines;
5. physics-feature ablations on both full missingness-aware and matched subsets;
6. uncertainty/calibration and out-of-domain or applicability analysis;
7. sensitivity to ambiguous labels, descriptor conventions, CALPHAD database/model choices and SFE assumptions;
8. case-level error analysis grounded in processing and microstructure;
9. preferably an untouched external literature set or prospective experimental/collaborative validation;
10. for advanced claims, targeted experimental or higher-fidelity validation of SFE/phase-stability disagreements.

Without defensible external/grouped validation and adequate class support, the output is more appropriately a feasibility/methodology or curated-data article than a general predictive-model article. Expensive calculations cannot compensate for weak or dependent targets.

## 7. Feasibility decision and immediate boundaries

The project should proceed **stage-gated**:

- **Proceed now:** reference-data governance, evidence/target rubric design, software interfaces, missingness/applicability rules, and infrastructure planning.
- **Proceed before ML only after explicit gates:** generalized dataset construction, independent label audit, class-support assessment, current feature-leakage inventory and grouped split feasibility.
- **Defer until justified:** broad commercial CALPHAD production, exhaustive SFE generation, DFT/MD campaigns and model training.

Success for the MVP is not a high accuracy number. It is a reproducible determination of whether the available independent evidence supports the proposed targets and whether physics-informed descriptors add validated information. No paper collection, simulation, model training, dataset creation, scientific-value generation or label modification was performed for this feasibility evaluation.
