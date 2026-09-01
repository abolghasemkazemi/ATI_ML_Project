# Literature Mining and Data Extraction Protocol

## 1. Purpose and scope

This protocol governs future literature selection and condition-level extraction for the **General HEA Deformation Mechanism Prediction Framework**. The framework will combine experimental literature observations with provenance-separated CALPHAD and stacking-fault-energy (SFE) descriptors to predict one of five prospective mechanism classes:

1. Slip
2. TWIP
3. TRIP (epsilon martensite)
4. TRIP (alpha-prime martensite)
5. Mixed TRIP/TWIP

The protocol is literature-first because the target must be supported by experimental evidence before computational descriptors can be useful for supervised learning. Dataset size is subordinate to evidence quality, condition identity, independence, and provenance. Admission of a paper does not make every reported condition ML-eligible, and a paper's mechanistic discussion does not automatically establish a label.

This document defines rules only. It does not report a literature search, add papers or scientific values, construct a dataset, calculate descriptors, or authorize model training.

## 2. Unit of extraction and review workflow

The primary extraction unit is a distinct **material–processing–initial-state–deformation condition**, not a paper, figure, row, strain stage, or characterization image. Each source first receives a paper-level eligibility review; each candidate condition then receives a separate completeness, mechanism-evidence, and independence review.

Review proceeds in this order:

1. establish source identity (title, DOI or other stable identifier, version, and paper ID) and check for duplicates;
2. apply paper-level inclusion and exclusion criteria;
3. identify material parents, physical batches when reported, processing branches, deformation conditions, specimens, replicates, and repeated stages;
4. transcribe source-reported values without filling gaps or normalizing the stored raw representation;
5. record evidence separately for each mechanism and condition;
6. assign a prospective target only under the evidence policy in Section 6;
7. perform independent review and the quality-control checks in Section 7; and
8. promote only validated, leakage-safe condition records into a versioned dataset.

Missing or ambiguous information is recorded as missing or unresolved, never as zero, mechanism absence, or an inferred scientific value.

## 3. Literature inclusion criteria

### 3.1 Material scope

A paper may enter the candidate evidence collection when all mandatory information requirements in Section 3.2 are met and its material is:

- a high-entropy alloy (HEA); or
- a medium-entropy alloy (MEA) with an explicit scientific justification for inclusion, such as relevance to the same composition/phase-stability space, mechanism physics, or intended applicability domain.

Metastable FCC or FCC-containing alloys are preferred because they are directly relevant to competition among slip, twinning, and FCC-to-epsilon/alpha-prime transformation. This preference is a prioritization rule, not permission to assume metastability or a mechanism. Other HEA/justified-MEA phase constitutions may be retained when they inform an explicitly defined applicability domain and the five-class target remains scientifically meaningful.

### 3.2 Mandatory information

At least one extractable condition must have all of the following:

- **Chemical composition available:** a nominal or measured composition is reported with enough element and basis information to identify the alloy. Nominal and measured chemistry must remain separate.
- **Processing history available:** the manufacturing route and the processing/heat-treatment state relevant to the tested material are reported. Unknown substeps may remain missing if the condition remains identifiable; the paper must not be treated as fully specified.
- **Deformation condition available:** loading mode plus the reported test temperature and strain rate, crosshead rate, or other source-defined rate basis are captured. A qualitative room-temperature statement may be retained verbatim but must not be converted to an invented Kelvin value.
- **Mechanism evidence available:** at least one acceptable evidence source is tied to the deformed condition and supports evaluation of slip, TWIP, or a phase-specific TRIP pathway. Evidence can remain inconclusive; it must not be converted into a negative label.

### 3.3 Acceptable mechanism evidence

Acceptable evidence sources are:

- electron backscatter diffraction (EBSD), including phase/orientation maps when their state and scope are reported;
- X-ray diffraction (XRD), preferably with identifiable pre-/post-deformation or in-situ phase evolution;
- transmission electron microscopy (TEM), with feature and phase identification;
- scanning electron microscopy (SEM), when the imaged feature and mechanism attribution are sufficiently specific;
- in-situ characterization during deformation;
- stress–strain or work-hardening analysis accompanied by an explicit, condition-specific mechanism discussion by the authors.

Evidence strength depends on what the method actually demonstrates. Direct phase-resolved or crystallographically resolved observation is stronger than response-curve interpretation. Stress–strain analysis with author discussion can make a paper eligible for review, but by itself normally receives low confidence and does not justify a definitive label unless the claim is unambiguous, condition-specific, and accepted under a documented review decision. Initial phases, annealing twins, stacking faults, or martensite present before loading do not establish deformation-induced TRIP or TWIP.

## 4. Literature exclusion criteria

Exclude a paper from the mechanism dataset when any of the following applies:

- chemical composition is absent or too incomplete to identify the studied alloy;
- deformation testing or deformation conditions are absent;
- the work concerns only corrosion, oxidation, or another non-deformation outcome;
- the work reports only phase prediction, CALPHAD screening, SFE calculation, atomistic simulation, or other computational phase/mechanism prediction without relevant experimental mechanical behavior and mechanism evidence;
- no condition-linked mechanism evidence is available;
- the material is outside the HEA/justified-MEA scope;
- the source is a duplicate publication or duplicate representation of an already extracted dataset.

Duplicate exclusion must be documented rather than silently discarded. Conference/journal versions, reviews reproducing primary data, corrigenda, shared data repositories, and multiple papers using the same batch or experiment must be linked in a duplicate/provenance ledger. Prefer the primary or most complete source, retain supplementary sources as provenance links, and count a physical condition only once. A review article may support discovery or interpretation but must not replace the primary source for extracted scientific values or labels.

Computational-only papers may be catalogued separately as method or descriptor references, but they do not enter the experimental target dataset and do not create artificial experimental samples or mechanism labels.

## 5. Data extraction protocol

Every extracted value must retain its source location (table, figure, caption, section, page, supplement, or data file), reporting basis, extraction method (direct text/table, author-supplied data, or explicitly permitted digitization), reviewer, and review status. Raw reported text/value and harmonized analysis fields must be separate. No value may be borrowed from a compositionally similar alloy or another paper.

### A. Material identity

- stable `Paper_ID`, DOI/source identifier, bibliographic version, and source file/version;
- source-reported alloy name and a stable material-parent identifier;
- composition exactly as reported, including element order, values, units/basis (at.%, wt.%, ratio, or other), and nominal/measured status;
- parsed element fractions in separate fields, only when the parsing is unambiguous;
- composition measurement method and spatial scope, where reported;
- alloy family and the scientific justification for any MEA inclusion;
- physical batch, specimen, and replicate identifiers only when the source establishes them.

### B. Processing

- manufacturing route (for example casting, powder processing, additive manufacturing, or mechanical alloying);
- homogenization temperature, duration, atmosphere, and cooling, as reported;
- annealing/solution-treatment temperature, duration, atmosphere, and sequence;
- rolling type, temperature, reduction, pass sequence, and direction;
- cooling condition (water quench, air cool, furnace cool, controlled rate, or source wording);
- ordered processing history, material state at each step, and processing-branch identifier;
- unreported parameters as explicit missing values.

### C. Initial microstructure

- pre-deformation grain size value, unit, statistic/uncertainty, measurement method, phase, and boundary definition;
- initial phase identities and fractions, including measurement method, uncertainty, and sampling scope;
- crystallographic texture and its representation/method;
- initial epsilon and alpha-prime martensite fractions in separate fields;
- initial twins, stacking faults, precipitates, or secondary phases as separate descriptors when reported;
- state timing, which must establish that a candidate predictor was measured before deformation.

### D. Deformation conditions

- test temperature, reported unit, and raw wording;
- strain rate and its basis (true, engineering, crosshead-derived, or other), including units;
- loading mode (tension, compression, shear, cyclic/fatigue, impact, or other);
- loading direction relative to processing/texture, specimen geometry, environment, and termination strain when reported;
- condition ID, parent experiment ID, specimen/replicate ID, and deformation-stage ID;
- whether the record is a primary condition, correlated stage/child observation, aggregate result, or supporting-only observation.

### E. Physical and computational descriptors

- experimental SFE value, unit, temperature, uncertainty, method, model assumptions, and source scope;
- calculated SFE value separately, with SFE definition (thermodynamic, intrinsic, unstable/GSFE, or other), temperature, method, equation/model, magnetic/chemical state, software, database/potential, parameters, and run/source provenance;
- available CALPHAD outputs such as equilibrium/metastable phase fractions, transformation driving forces, activities, or phase-stability quantities, each with temperature, pressure, database, software/version, calculation type, suppressed phases/constraints, and run identifier;
- an explicit origin field (`EXPERIMENTAL`, `CALCULATED_CURRENT_WORK`, or `CALCULATED_LITERATURE`) and missingness reason.

Experimental measurements and computations must never share an unlabeled value field. A computational descriptor does not constitute mechanism evidence and cannot overwrite an observed target.

### F. Targets and evidence

- observed mechanism components for Slip, TWIP, epsilon-TRIP, and alpha-prime-TRIP, each recorded separately as positive, supported negative, or unresolved;
- prospective five-class target, assigned only after component-level review;
- evidence source/method, exact source location, state (initial, in-situ, interrupted, or post-deformation), phase, strain/stress stage, and spatial/sample scope;
- author claim separated from reviewer interpretation;
- evidence grade, confidence level, reviewer, review date, and conflict/uncertainty note;
- predicted mechanism, if later generated, in a separate prediction table/field with model and run provenance.

Optional mechanical outcomes (yield strength, ultimate tensile strength, elongation, and work-hardening response) must remain outcomes or mechanism evidence, not pre-deformation predictors.

## 6. Evidence, target, and confidence policy

### 6.1 Non-inference rules

- **Never infer TRIP or TWIP without evidence.** Composition, SFE, phase-stability theory, work-hardening shape, ductility, grain size, or a mechanism expected in a related alloy is not a label.
- Separate the **observed mechanism** from any author prediction, CALPHAD/SFE expectation, rule-based interpretation, or future ML prediction.
- An initial epsilon or alpha-prime fraction is not evidence of deformation-induced martensite. TRIP requires condition-linked evidence of transformation during deformation or a defensible pre-/post-deformation change.
- Annealing twins are not TWIP. TWIP requires deformation-twin evidence tied to the loading condition.
- Absence of reported evidence is unresolved, not a supported negative.
- Slip is not a default class when TRIP/TWIP evidence is missing. It needs source-supported deformation evidence or a documented exclusion of competing target mechanisms at the condition scope.

### 6.2 Phase-specific TRIP and mixed labels

Epsilon (HCP) martensite and alpha-prime (BCC/BCT) martensite must remain separate component targets. If both occur, preserve both observations and their sequence when reported; do not collapse them into a generic TRIP value. The five-class mapping must follow a predeclared adjudication rule for multi-TRIP cases before dataset release.

Assign **Mixed TRIP/TWIP** only when both deformation-induced transformation and deformation twinning are supported for the same eligible condition or a clearly documented condition-level aggregate. Evidence from different alloy states, deformation temperatures, specimens with unestablished aggregation, or papers must not be combined to create a mixed label.

### 6.3 Confidence levels

Confidence records evidence quality, specificity, consistency, and completeness; it does not alter the source observation:

- **HIGH:** direct, condition-specific, phase/crystallography-resolved evidence (for example in-situ observation or consistent pre-/post-deformation EBSD/XRD/TEM), with no material conflict.
- **MEDIUM:** condition-specific experimental evidence or explicit author attribution supported by suitable characterization, but with limited quantification, sampling, phase identity, or temporal resolution.
- **LOW:** indirect or interpretation-dependent condition-specific evidence, including stress–strain/work-hardening discussion without direct characterization, or evidence with important scope ambiguity. Low-confidence labels require adjudication and should be excluded from the initial validated training target unless a release decision explicitly permits them.
- **UNRESOLVED:** insufficient, contradictory, or non-condition-specific evidence. No definitive class is assigned.

Record uncertainty even for high-confidence observations. Conflicting methods must be retained side by side and adjudicated transparently; do not average away or silently select a preferred result.

Supported negative labels require affirmative, condition-wide evidence appropriate to the mechanism and a documented review rationale. A paper's silence, a single unrepresentative image, or failure to detect a phase without an adequate detection/sampling basis is not a negative.

## 7. Data quality control

### 7.1 Units and representation

- retain the raw reported value, unit, qualifier, and significant figures;
- convert into a canonical analysis field using a documented formula and unit vocabulary;
- never convert qualitative temperatures such as “room temperature” into a numeric value without a reported definition;
- validate dimensional consistency and flag ranges, approximate values, detection limits, and unknown uncertainty types.

### 7.2 Composition checks

- retain nominal and measured compositions separately and record at.%/wt.%/ratio basis;
- calculate a normalized analysis composition only in a derived field, never over the raw composition;
- normalize only when scientifically appropriate and the full reported basis is understood;
- record pre-normalization sum, normalization factor, excluded interstitials/trace elements, rounding tolerance, and validation outcome;
- quarantine rather than repair unexplained totals, missing balance elements, or ambiguous ratio formulas.

### 7.3 Duplicate and identity checks

- compare DOI, title, authors, alloy/batch identity, processing, conditions, figures/tables, and reported values;
- identify duplicate publications, repeated use of the same material batch, overlapping experimental series, and primary/supplement/repository representations;
- select a canonical condition record and link all supporting sources without double counting;
- record the duplicate decision and reviewer in a persistent ledger.

### 7.4 Parent and replicate grouping

- assign paper, study-series, material-parent, physical-batch, parent-experiment, condition, observation, specimen/replicate, and stage identifiers at their documented scopes;
- never invent physical-batch or replicate identity;
- never expand means, error bars, or a reported specimen count into pseudo-replicate rows;
- treat interrupted tests, strain increments, in-situ frames, repeated images, and longitudinal phase fractions from one parent as correlated child observations;
- keep linked parents/replicates/stages in the same validation group, and use paper/study/material grouping as required by the evaluation design;
- count a condition as independent only when the experimental design supports it and the grouping decision is recorded.

### 7.5 Provenance and review controls

- preserve immutable raw source files and raw transcriptions;
- record field-level source location, extraction method, extractor, date, source version/hash where available, and any transformation code/version;
- maintain correction and decision ledgers instead of overwriting history;
- require a second-person or independent-pass review of composition, condition identity, mechanism evidence, labels, and parent grouping before validated release;
- run schema, allowed-value, unit, missingness, uniqueness, referential-integrity, label/evidence, and leakage-timing checks;
- version every interim and released dataset according to existing repository conventions, with row/column counts and change summaries.

## 8. Dataset construction strategy

### Stage 1 — Small validated dataset

Build a deliberately small, manually audited set of independent experimental conditions. Prioritize clear composition/processing/deformation metadata, direct mechanism evidence, phase-specific TRIP/TWIP semantics, class-definition consistency, and diverse supported mechanisms rather than maximizing rows. Require dual review of labels and grouping. Use it to test the schema, extraction form, missingness vocabulary, and QC rules; do not claim model adequacy from pilot size.

### Stage 2 — Expanded literature dataset

Expand systematically across HEA families and scientifically justified MEAs, processing paths, initial microstructures, temperatures, strain rates, and loading modes. Apply the same evidence threshold and provenance requirements; do not relax them to improve class balance. Track search and screening decisions, source overlap, unresolved labels, applicability domains, and group-level class support. Freeze a version only after duplicate, parent/replicate, label, and leakage review.

### Stage 3 — Computational descriptor expansion

After experimental condition identities and targets are frozen, calculate or import CALPHAD/SFE descriptors where method and database/potential coverage are defensible. Preserve run-level provenance, temperature and state alignment, database/tool versions, failure/missingness reasons, and experimental-versus-calculated separation. Add descriptors non-destructively and assess coverage bias. Computational outputs may enrich predictors but may not fill, override, or manufacture experimental mechanism labels.

Progression between stages is gate-based, not calendar- or row-count-based. Before any ML training, reassess independent class support, confidence eligibility, applicability domain, prediction-time leakage, grouped split feasibility, and whether the prospective five-class target is scientifically and statistically viable.

## 9. Protocol outputs for future collection

Future implementation should produce, as separate versioned artifacts:

- a search/screening log and paper eligibility table;
- a source and duplicate/provenance ledger;
- raw, field-level extraction records;
- material/condition/parent/replicate/stage identity tables;
- a component-level mechanism evidence and adjudication table;
- a validated condition table with confidence and missingness metadata;
- computational-run manifests linked to, but distinct from, experimental conditions; and
- a release QC report documenting exclusions, unresolved cases, class support, and known limitations.

None of these artifacts is created by this protocol task.
