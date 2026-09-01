# GitHub research project library

This directory is a lightweight, provenance-conscious index. Repositories are linked rather than cloned. Entries whose supplied project name did not identify a unique owner/repository use an explicit GitHub repository-discovery URL; resolve and review the exact repository before using its code or scientific outputs. A reference is not an endorsement, and no values, labels, samples, or datasets are imported here.

| Project | Category | Purpose | Relevance | Priority |
| ------- | -------- | ------- | --------- | -------- |
| [Ahadzadeh2022/SFE](SFE/Ahadzadeh2022_SFE.md) | SFE | Stacking-fault-energy calculations and related analysis workflows. | A direct reference for SFE methodology and phase-stability descriptor provenance; values must not be transferred without alloy-, method-, and temperature-specific validation. | High |
| [gsfe_workflow](SFE/gsfe_workflow.md) | SFE | Workflow automation for generalized stacking-fault-energy calculations. | May support reproducible GSFE/SFE descriptor generation and method documentation for FeMnCoCrN, while remaining separate from experimental labels. | High |
| [OpenCALPHAD examples](CALPHAD/OpenCALPHAD_examples.md) | CALPHAD | Open-source CALPHAD software with examples for thermodynamic equilibrium and Gibbs-energy calculations. | Potential basis for provenance-controlled phase-stability descriptors, provided a suitable assessed database and alloy-specific calculation protocol are documented. | High |
| [Gibbs energy prediction projects](CALPHAD/Gibbs_energy_prediction_projects.md) | CALPHAD | Repository-discovery reference for projects that predict or calculate Gibbs energy. | Could inform DeltaG feature workflows, but candidate repositories and their thermodynamic validity must be reviewed before use. | Medium |
| [HEA_Mechanisms](HEA/HEA_Mechanisms.md) | HEA | Repository-discovery reference for HEA deformation-mechanism tools and data. | Potential source of mechanism taxonomies or workflows relevant to TRIP/TWIP; labels cannot be imported without source-level verification. | High |
| [hea-bench](ML_materials/hea_bench.md) | ML_materials | Repository-discovery reference for benchmark datasets and models for high-entropy alloys. | May provide benchmark design and grouped-evaluation ideas, subject to composition, target, provenance, and independence review. | Medium |
| [HEA corrosion ML projects](ML_materials/HEA_corrosion_ML.md) | ML_materials | Repository-discovery reference for machine-learning studies of HEA corrosion. | Useful mainly for HEA featurization and validation patterns; corrosion targets are not substitutes for TRIP/TWIP mechanisms. | Low |
| [HEA energy adsorption projects](ML_materials/HEA_adsorption_energy.md) | ML_materials | Repository-discovery reference for HEA adsorption-energy prediction and surface modelling. | May offer composition encodings or uncertainty practices, but surface adsorption is outside the deformation-mechanism target domain. | Low |
| [CMS-EAM projects](Atomistic/CMS_EAM.md) | Atomistic | Repository-discovery reference for concentration-dependent or composition-aware EAM projects. | May support atomistic studies of composition-dependent defect energetics, but computational outputs must remain domain-separated from experiments. | Medium |
| [atomman](Atomistic/atomman.md) | Atomistic | Python toolkit for atomistic calculations, defect construction, and simulation analysis. | Could support reproducible fault, dislocation, and elastic calculations used as explicitly computational descriptors. | High |
| [pafi](Atomistic/pafi.md) | Atomistic | Repository-discovery reference for projected-average-force integration and activated-process calculations. | May help study atomistic barriers for transformations or defect motion; relevance is indirect until a validated FeMnCoCrN potential exists. | Medium |
| [Stress-field related projects](Atomistic/stress_field_projects.md) | Atomistic | Repository-discovery reference for dislocation and elastic stress-field implementations. | Could provide physically motivated stress or defect descriptors, but derived quantities require validated assumptions and provenance. | Medium |

## Use safeguards

- Review repository licenses, versions, methods, dependencies, and primary references before adoption.
- Keep computational outputs distinct from experimental observations.
- Do not transfer SFE, Gibbs energy, potential-derived, or other scientific values across alloys, methods, or temperatures without scientific justification and provenance.
- Do not use an external repository to overwrite TRIP/TWIP labels or to treat repeated observations as independent samples.
