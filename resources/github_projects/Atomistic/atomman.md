# atomman

- **Project name:** atomman
- **GitHub URL:** https://github.com/usnistgov/atomman
- **Category:** Atomistic
- **Main purpose:** Python toolkit for atomistic calculations, defect construction, and simulation analysis.
- **Possible relevance for FeMnCoCrN HEA TRIP/TWIP machine learning project:** Could support reproducible fault, dislocation, and elastic calculations used as explicitly computational descriptors.
- **Priority:** High

## Scientific role

**Useful.** atomman is useful calculation and analysis infrastructure for constructing atomistic systems and evaluating defects, elasticity, and related properties. It can standardize input/output handling and provenance around a separately selected, validated interatomic potential.

## Possible ML usage

**Atomistic validation; feature engineering; SFE prediction.** Any resulting quantity must carry the repository version, calculation method, inputs, units, temperature, alloy scope, and computational/experimental domain.

## Relevance to FeMnCoCrN HEA TRIP/TWIP project

For FeMnCoCrN, reproducible fault, elastic, dislocation, or transformation calculations could generate method-tagged descriptors and test whether a proposed SFE trend is consistent with atomistic energetics. These results may strengthen interpretation of **SFE → phase stability → TRIP/TWIP prediction**, especially when compared against DFT or experiments.

## Limitations

A toolkit is not a FeMnCoCrN physical model and does not provide a validated potential by itself. Accuracy is limited by the potential, atomic configurations, boundary conditions, temperature, and calculation protocol. Atomistic outputs cannot be pooled silently with experimental observations or converted directly into TRIP/TWIP labels.
