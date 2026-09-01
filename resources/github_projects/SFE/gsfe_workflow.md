# gsfe_workflow

- **Project name:** gsfe_workflow
- **GitHub URL:** https://github.com/ICAMS/gsfe_workflow
- **Category:** SFE
- **Main purpose:** Workflow automation for generalized stacking-fault-energy calculations.
- **Possible relevance for FeMnCoCrN HEA TRIP/TWIP machine learning project:** May support reproducible GSFE/SFE descriptor generation and method documentation for FeMnCoCrN, while remaining separate from experimental labels.
- **Priority:** High

## Scientific role

**Useful.** This workflow may automate reproducible generalized stacking-fault-energy calculations and preserve calculation inputs as provenance. It is useful infrastructure for generating intrinsic/extrinsic fault energies or barrier-shaped descriptors when a validated electronic-structure setup is available.

## Possible ML usage

**SFE prediction; feature engineering; atomistic validation.** Any resulting quantity must carry the repository version, calculation method, inputs, units, temperature, alloy scope, and computational/experimental domain.

## Relevance to FeMnCoCrN HEA TRIP/TWIP project

A FeMnCoCrN GSFE surface can provide more information than one scalar SFE, including unstable fault or twinning barriers. These descriptors may connect planar-fault energetics to FCC metastability and competition between epsilon-martensite formation and deformation twinning, supporting **SFE/GSFE → phase stability → TRIP/TWIP prediction** as a physics-informed hypothesis.

## Limitations

Workflow reproducibility is not physical validity. Results depend on supercell chemistry, local chemical configurations, magnetic treatment, N sites, temperature approximation, relaxation protocol, exchange-correlation choices, and convergence. A zero-kelvin or single-configuration GSFE cannot be treated as an experimental finite-temperature SFE or a universal TRIP/TWIP threshold.
