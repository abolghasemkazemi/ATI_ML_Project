# OpenCALPHAD examples

- **Project name:** OpenCALPHAD examples
- **GitHub URL:** https://github.com/OpenCalphad/OpenCalphad
- **Category:** CALPHAD
- **Main purpose:** Open-source CALPHAD software with examples for thermodynamic equilibrium and Gibbs-energy calculations.
- **Possible relevance for FeMnCoCrN HEA TRIP/TWIP machine learning project:** Potential basis for provenance-controlled phase-stability descriptors, provided a suitable assessed database and alloy-specific calculation protocol are documented.
- **Priority:** High

## Scientific role

**Useful.** OpenCalphad can serve as calculation infrastructure for provenance-controlled equilibrium or Gibbs-energy descriptors. It is useful only when paired with an assessed database that covers the Fe–Mn–Co–Cr–N composition range and with a documented calculation protocol.

## Possible ML usage

**CALPHAD thermodynamic descriptors; feature engineering; data interpretation.** Any resulting quantity must carry the repository version, calculation method, inputs, units, temperature, alloy scope, and computational/experimental domain.

## Relevance to FeMnCoCrN HEA TRIP/TWIP project

Alloy- and temperature-specific phase Gibbs energies, FCC/HCP driving force, equilibrium phase fractions, or phase-boundary distances could complement SFE. Together they can quantify whether FCC is metastable and help represent **SFE → FCC/HCP phase stability → deformation-induced TRIP versus TWIP**, while test conditions and initial microstructure remain necessary predictors.

## Limitations

Examples and software do not supply a validated FeMnCoCrN thermodynamic description. Database coverage, magnetic models, interstitial sublattices, metastable phase handling, equilibrium assumptions, sign conventions, and extrapolation uncertainty must be checked. Equilibrium CALPHAD output cannot be equated with deformation kinetics or used to overwrite observed phases and labels.
