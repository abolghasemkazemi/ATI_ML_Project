# Ahadzadeh2022/SFE

- **Project name:** Ahadzadeh2022/SFE
- **GitHub URL:** https://github.com/Ahadzadeh2022/SFE
- **Category:** SFE
- **Main purpose:** Stacking-fault-energy calculations and related analysis workflows.
- **Possible relevance for FeMnCoCrN HEA TRIP/TWIP machine learning project:** A direct reference for SFE methodology and phase-stability descriptor provenance; values must not be transferred without alloy-, method-, and temperature-specific validation.
- **Priority:** High

## Scientific role

**Useful.** This is a potentially direct methodological reference for building or auditing stacking-fault-energy calculations. If its implementation, physical model, units, and dependencies pass review, its outputs could be retained as method-tagged computational features rather than mixed with measured SFE.

## Possible ML usage

**SFE prediction; feature engineering; atomistic validation.** Any resulting quantity must carry the repository version, calculation method, inputs, units, temperature, alloy scope, and computational/experimental domain.

## Relevance to FeMnCoCrN HEA TRIP/TWIP project

For FeMnCoCrN, a composition- and temperature-specific SFE estimate could describe the energetic competition among perfect slip, faulting, twinning, and FCC-to-HCP transformation. Used with initial phase state and thermodynamic driving force, it could therefore inform the chain **SFE → FCC/HCP phase stability → TRIP/TWIP propensity**. It does not itself establish a mechanism label.

## Limitations

The repository's values or settings cannot be transferred directly to FeMnCoCrN. Alloy chemistry (especially interstitial N), magnetic state, temperature, chemical order, fault definition, reference structure, and computational method can change SFE. Scientific use requires code/version, inputs, convergence, uncertainty, and alloy-specific validation; predicted SFE must remain computational and must not replace experimental evidence.
