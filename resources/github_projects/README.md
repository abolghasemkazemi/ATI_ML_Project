# GitHub research project library

This directory is a lightweight, provenance-conscious index. Repositories are linked rather than cloned. Entries whose supplied project name did not identify a unique owner/repository use an explicit GitHub repository-discovery URL; resolve and review the exact repository before using its code or scientific outputs. A reference is not an endorsement, and no values, labels, samples, or datasets are imported here.

Final priorities reflect suitability for this project, not general scientific quality. `Essential` means the capability is central to the planned scientific workflow; it does not authorize use without validation. `Useful` indicates plausible direct support, `Reference only` limits use to methodological comparison, and `Not relevant` identifies a mismatched target domain.

| Project | Category | Purpose | Relevance | Scientific role | Possible ML usage | Final priority |
| ------- | -------- | ------- | --------- | --------------- | ----------------- | -------------- |
| [Ahadzadeh2022/SFE](SFE/Ahadzadeh2022_SFE.md) | SFE | SFE calculation methods | Potential phase-stability descriptor methodology | SFE methodology | SFE calculation; Feature engineering | Useful |
| [gsfe_workflow](SFE/gsfe_workflow.md) | SFE | Automated GSFE workflows | Reproducible computational SFE provenance | GSFE workflow | SFE calculation; Feature engineering | Useful |
| [OpenCALPHAD examples](CALPHAD/OpenCALPHAD_examples.md) | CALPHAD | Thermodynamic equilibrium and Gibbs energy | Potential alloy-specific phase-stability descriptors | CALPHAD platform | CALPHAD thermodynamics; Feature engineering | Essential |
| [Gibbs energy prediction projects](CALPHAD/Gibbs_energy_prediction_projects.md) | CALPHAD | Gibbs-energy project discovery | Candidate DeltaG methods requiring resolution | Unresolved project family | CALPHAD thermodynamics; Validation/reference only | Reference only |
| [HEA_Mechanisms](HEA/HEA_Mechanisms.md) | HEA | HEA mechanism project discovery | Candidate mechanism taxonomy requiring source review | Unresolved mechanism resource | Validation/reference only | Reference only |
| [hea-bench](ML_materials/hea_bench.md) | ML_materials | HEA benchmark project discovery | Potential benchmarking and validation patterns | Unresolved benchmark resource | Feature engineering; Validation/reference only | Useful |
| [HEA corrosion ML projects](ML_materials/HEA_corrosion_ML.md) | ML_materials | HEA corrosion ML discovery | Workflow reference only; target domain differs | Cross-domain workflow reference | Validation/reference only | Reference only |
| [HEA energy adsorption projects](ML_materials/HEA_adsorption_energy.md) | ML_materials | HEA adsorption project discovery | Surface target is outside deformation mechanisms | Out-of-domain project family | Validation/reference only | Not relevant |
| [CMS-EAM projects](Atomistic/CMS_EAM.md) | Atomistic | Composition-aware EAM discovery | Candidate defect descriptors if a potential is validated | Candidate potential family | Feature engineering; SFE calculation | Useful |
| [atomman](Atomistic/atomman.md) | Atomistic | Atomistic construction and analysis toolkit | Reproducible computational defect descriptors | General atomistic toolkit | Feature engineering; SFE calculation | Useful |
| [pafi](Atomistic/pafi.md) | Atomistic | Activated-process project discovery | Indirect barrier methodology requiring validation | Activated-process reference | Validation/reference only | Reference only |
| [Stress-field related projects](Atomistic/stress_field_projects.md) | Atomistic | Stress-field project discovery | Indirect defect-physics reference | Unresolved stress-field resource | Validation/reference only | Reference only |

## Use safeguards

- Review repository licenses, versions, methods, dependencies, and primary references before adoption.
- Resolve GitHub discovery links to exact repositories before treating their evaluations as implementation-specific.
- Keep computational outputs distinct from experimental observations.
- Do not transfer SFE, Gibbs energy, potential-derived, or other scientific values across alloys, methods, or temperatures without scientific justification and provenance.
- Do not use an external repository to overwrite TRIP/TWIP labels or to treat repeated observations as independent samples.
