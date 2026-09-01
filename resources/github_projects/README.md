# GitHub research project library

This directory is a lightweight, provenance-conscious index. Repositories are linked rather than cloned. Entries whose supplied project name did not identify a unique owner/repository use an explicit GitHub repository-discovery URL; resolve and review the exact repository before using its code or scientific outputs. A reference is not an endorsement, and no values, labels, samples, or datasets are imported here.

| Project | Category | Purpose | Scientific role | ML usage | Final priority |
| ------- | -------- | ------- | --------------- | -------- | -------------- |
| [Ahadzadeh2022/SFE](SFE/Ahadzadeh2022_SFE.md) | SFE | SFE calculation and analysis workflows. | Useful | SFE prediction; feature engineering; atomistic validation | High |
| [gsfe_workflow](SFE/gsfe_workflow.md) | SFE | Reproducible generalized stacking-fault-energy workflows. | Useful | SFE prediction; feature engineering; atomistic validation | High |
| [OpenCALPHAD examples](CALPHAD/OpenCALPHAD_examples.md) | CALPHAD | Equilibrium and Gibbs-energy calculation infrastructure. | Useful | CALPHAD descriptors; feature engineering; interpretation | High |
| [Gibbs energy prediction projects](CALPHAD/Gibbs_energy_prediction_projects.md) | CALPHAD | Discovery of Gibbs-energy calculation or prediction tools. | Reference only | CALPHAD descriptors; SFE context; interpretation | Medium |
| [HEA_Mechanisms](HEA/HEA_Mechanisms.md) | HEA | Discovery of HEA deformation-mechanism tools and data. | Reference only | Interpretation; feature engineering | Medium |
| [hea-bench](ML_materials/hea_bench.md) | ML_materials | Discovery of HEA benchmark datasets and models. | Reference only | Feature engineering; interpretation | Medium |
| [HEA corrosion ML projects](ML_materials/HEA_corrosion_ML.md) | ML_materials | ML approaches for an unrelated corrosion target. | Not relevant | Generic featurization/interpretation patterns only | Low |
| [HEA energy adsorption projects](ML_materials/HEA_adsorption_energy.md) | ML_materials | ML approaches for unrelated surface-adsorption targets. | Not relevant | Generic feature-code patterns only | Low |
| [CMS-EAM projects](Atomistic/CMS_EAM.md) | Atomistic | Discovery of composition-aware EAM approaches. | Reference only | Atomistic validation; SFE prediction; features | Medium |
| [atomman](Atomistic/atomman.md) | Atomistic | Atomistic system construction and defect analysis. | Useful | Atomistic validation; feature engineering; SFE prediction | High |
| [pafi](Atomistic/pafi.md) | Atomistic | Discovery of activated-process free-energy methods. | Reference only | Atomistic validation; interpretation | Medium |
| [Stress-field related projects](Atomistic/stress_field_projects.md) | Atomistic | Discovery of defect and elastic stress-field methods. | Reference only | Feature engineering; atomistic validation; interpretation | Medium |

## Use safeguards

- Review repository licenses, versions, methods, dependencies, and primary references before adoption.
- Keep computational outputs distinct from experimental observations.
- Do not transfer SFE, Gibbs energy, potential-derived, or other scientific values across alloys, methods, or temperatures without scientific justification and provenance.
- Do not use an external repository to overwrite TRIP/TWIP labels or to treat repeated observations as independent samples.


## Scientific role

The library distinguishes **Useful** implementation candidates from **Reference only** discovery or methodological context and **Not relevant** resources whose scientific targets do not match bulk deformation. No listed resource is currently **Essential**: the project can preserve and analyze its literature evidence without these repositories, and adoption requires method- and domain-specific validation.

## Possible ML usage

Candidate uses are limited to feature engineering, SFE prediction, CALPHAD thermodynamic descriptors, atomistic validation, and data interpretation. The table records the appropriate uses for each entry. Computational outputs must remain method-tagged and domain-separated; they are not extra experimental samples.

## Relevance to FeMnCoCrN HEA TRIP/TWIP project

The scientifically relevant pathway is **SFE → FCC/HCP phase stability → competition between deformation-induced martensitic transformation (TRIP) and deformation twinning (TWIP)**. SFE/GSFE resources address fault energetics, CALPHAD resources can describe thermodynamic phase stability, atomistic resources can test defect or kinetic mechanisms, and HEA/ML references can support cautious representation and interpretation. This pathway is a modelling hypothesis, not a universal deterministic threshold.

## Limitations

Repository code, pretrained models, scientific values, thresholds, labels, and benchmark scores cannot be transferred directly. FeMnCoCrN use requires exact repository/version resolution, license and dependency review, Fe–Mn–Co–Cr–N domain coverage, temperature and method provenance, uncertainty assessment, and validation against appropriate evidence. Search links identify candidate families only. No resource may overwrite observed phase states or TRIP/TWIP labels, collapse computational and experimental domains, or turn correlated observations into independent samples.
