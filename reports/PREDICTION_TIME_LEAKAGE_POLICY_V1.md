# Prediction-Time Leakage Policy V1

## Frozen prediction task and moment

**Task:** pre-deformation condition-level mechanism prediction.

**Prediction moment:** **immediately before tensile loading begins**.

Given alloy/material information, processing history, initial microstructure, and planned tensile-test conditions known before loading, a future model may predict whether the condition subsequently exhibits TRIP and/or TWIP. Information first observed after loading starts is unavailable at this moment and is forbidden as a primary predictor.

This document freezes eligibility only. It does not choose a final target, train a model, select an algorithm, run cross-validation, impute, encode, normalize, calculate a descriptor, or produce a transformed matrix.

## Preserved target definitions

- **T1 — binary TRIP:** `Effective_TRIP`.
- **T2 — binary TWIP:** `Effective_TWIP`.
- **T3 — joint multilabel:** `Effective_TRIP` and `Effective_TWIP`, with 00 = neither, 10 = TRIP only, 01 = TWIP only, and 11 = both.

`TRIP`, `TWIP`, `Original_TRIP`, `Original_TWIP`, recovered/correction fields, evidence fields, and direct mechanism-state variables are target/evidence fields, never predictors. V1 does not select T1, T2, or T3 as the final ML task.

## Allowed at prediction time

- Source-supported nominal or measured **bulk chemistry**, with basis and scope preserved.
- **Processing history** completed before the tensile test.
- Explicitly pre-test **initial microstructure**, including pre-existing phases or annealing/processing twins when their temporal scope is documented.
- Planned **test temperature, strain rate, loading mode, and loading/orientation** when explicitly reported.
- Eligible pre-test **physics/thermodynamic descriptors** only under method, phase, temperature, paper, and domain controls.

Safe-direct status does not imply completeness or authorize encoding. Safe-conditional status requires its recorded scope gate before inclusion.

## Permanently forbidden primary predictors

- Same-test mechanics: YS, UTS, engineering/true properties, elongation, uniform elongation, hardening response, fracture strain/mode, and their uncertainties.
- Post-deformation or post-fracture phases, twins, post-test KAM/GOS, dislocation density, morphology, and mechanism observations.
- Strain-stage, interrupted-test, in-situ SXRD/EBSD/TEM, stage phase fraction, stage twin fraction, stage KAM, or other observations collected after loading starts.
- TRIP/TWIP labels, target evidence, target confidence/status, or any direct mechanism-state outcome.
- HDI/back stress, strengthening contributions, critical stresses, inferred onsets, adiabatic/dynamic loading quantities, or other fitted/loading-response-derived fields.
- Paper/material/condition identifiers, grouping keys, provenance, QC tiers/status, source location, evidence confidence, and review metadata as ordinary predictors.
- P017 computational rows or paper-native labels in an experimental feature matrix.

These fields remain in the source for interpretation, target adjudication, mechanism–property studies, and audit. Retention never implies predictor eligibility.

## Chemistry policy

Measured bulk and nominal chemistry remain separate source representations. The frozen future conflict policy is:

1. if explicitly measured **bulk specimen/material chemistry** exists, prefer it;
2. otherwise use explicitly nominal chemistry;
3. retain basis, source, and method;
4. never treat local EDS/APT/TEM or feedstock chemistry as specimen bulk without an explicit scope decision;
5. never treat extra melting-charge compensation as final bulk chemistry.

This preference is documentation only. V1 does **not** merge the fields, parse composition strings, normalize at.%, infer an absent element as zero, or calculate elemental/alloy descriptors.

## Processing and test-condition policy

Melting/casting, powder metallurgy/SPS, homogenization, rolling, annealing, quenching/solution treatment, and processing-state information may be pre-test predictors when source-supported. Processing-induced martensite or twins can describe the initial tensile state but never become tensile TRIP/TWIP targets. Processing deformation is distinct from tensile deformation.

Planned temperature, strain rate, loading mode, and orientation are direct safe concepts. This V12 dataset has no dedicated usable loading-mode column and only partial loading-direction coverage. Specimen dimensions are metadata-only in V1 because no core scientific rationale has yet been frozen.

## Initial-microstructure policy

Explicitly pre-test FCC/HCP/BCC/other phases, grain size, recrystallized fraction, initial KAM/GOS, twins, precipitates, and phase-measurement method remain available. XRD and EBSD phase fractions are not assumed interchangeable. Initial annealing twins never establish TWIP. Pre-existing or processing-induced martensite/HCP never establishes tensile TRIP. Generic or post-test phase/twin fields remain blocked.

## Physics and thermodynamic policy

SFE and DeltaG require method-specific provenance and condition scope. Experimental SFE, thermodynamic/CALPHAD SFE, DFT 0 K SFE, MD SFE, FCC stable gamma_sf, and BCC unstable gamma_usf are never collapsed into one feature. `SFE_mJ_m2` is conditional because its rows span heterogeneous methods; the source method/origin fields are eligibility controls, not ordinary predictors.

- Direct experimental SFE may be eligible when measured before testing and condition-relevant.
- Current-paper thermodynamic/CALPHAD SFE is conditional.
- DFT/MD SFE is future physics-ablation-only and is not automatically experimental SFE.
- P017 GSFE is **COMPUTATIONAL_ONLY**.
- P016's assumed 18 mJ/m2 input is metadata/model input, not a material measurement.
- Reference constants remain metadata or conditional future inputs; they are not silently transferred.
- DeltaG is method-, alloy-, paper-, phase-, and temperature-specific and is never transferred across papers/alloys.

No SFE or DeltaG is imputed.

## Computational-domain policy

The twelve exact P017 conditions remain `COMPUTATIONAL_PRIMARY`; they contribute zero experimental conditions. P017 paper-native TRIP/TWIP, SIS-PSR, UTS-PSR, PTM descriptors, extreme MD strain rates, GSFE, and dislocation evolution are computational-only. Native computational labels are not experimental targets, and P017 cannot increase the experimental training count.

## Concrete current-paper decisions

- **P015 post-fracture HCP/phase state:** forbidden post-test predictor; target evidence only.
- **P015 YS/UTS, including engineering and true values:** forbidden same-test mechanical outcomes.
- **P014 HDI/back stress:** forbidden model/loading-derived predictor.
- **P013 strain-resolved SXRD and onset/landmark values:** stage/target evidence only.
- **P012 post-strain martensite/twin observations:** target evidence only.
- **P017 MD conditions and GSFE/stress-regime fields:** computational domain only.
- **P011 initial phase fractions:** potential pre-test predictors with phase/method scope.
- **P012 initial grain size:** pre-test predictor with grain-definition/method scope.

## Frozen feature-family progression

- **M1_CHEMISTRY:** untransformed pre-test chemistry source columns only; measured-first/nominal-fallback policy documented but not applied.
- **M2_CHEMISTRY_PLUS_TEST:** M1 plus planned test temperature, strain rate, and usable orientation/loading fields.
- **M3_PLUS_PROCESSING:** M2 plus eligible pre-test processing fields; route text remains unencoded.
- **M4_PLUS_PHYSICS:** M3 plus method-gated SFE, DeltaG, phase-stability, and related physics candidates; no generic SFE merge and no imputation.
- **M5_PLUS_INITIAL_MICROSTRUCTURE:** M4 plus explicitly pre-test phases, grain/twin/recrystallization/KAM/precipitate descriptors; no post-test field.

`feature_sets_v1.csv` lists raw candidate columns plus non-model method/scope controls. `feature_priority_v1.csv` distinguishes CORE_V1, OPTIONAL_V1, EXPLORATORY_LATER, and NOT_ELIGIBLE. No transformed training matrix exists.

## Readiness decision

1. **Ready for train/validation split design?** Yes—Feature Schema V1 is frozen enough to design grouped splits, because all 343 columns have a primary class and unsafe fields are blocked. This is not authorization to train.
2. **Initial baseline feature family:** M2_CHEMISTRY_PLUS_TEST is the recommended schema baseline for split design because it adds the planned mechanism-driving temperature/rate context without the sparse physics and detailed-microstructure families. Raw chemistry representation/conflict handling must be finalized before matrix construction.
3. **Too sparse for the baseline:** experimental SFE, DeltaG, detailed phase-stability descriptors, KAM/GOS, recrystallized fraction, local/measured chemistry, and several minor-element fields.
4. **Ablation-only:** method-specific DFT/MD/thermodynamic physics, magnetic/computational descriptors, local chemistry, and sparse detailed initial-microstructure descriptors.
5. **Permanently blocked:** targets/evidence, mechanical outcomes, post-test/stage observations, fitted/loading-derived quantities, identifiers/groups as features, provenance/QC as features, and P017-native computational fields in experimental models.

## Next gate

Design paper/study/material-aware train/validation splits using `Leakage_Group_Strict`, `Leakage_Group_Material`, `Study_Series_ID`, `Material_Parent_ID`, and paper identity strictly as grouping controls. Reconcile target-specific split feasibility and the documented measured-versus-nominal representation policy before constructing any predictor matrix. Do not train, impute, encode, normalize, synthesize, or calculate derived descriptors at this gate.
