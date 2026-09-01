# HEA deformation-mechanism data layout

This directory supports the generalized, physics-informed high-entropy alloy
(HEA) deformation-mechanism workflow:

`composition + processing -> CALPHAD/thermodynamics -> SFE -> microstructure -> ML -> mechanism`

## Directories

- `raw/`: immutable source material. Never overwrite, normalize, or impute a raw
  observation.
- `processed/`: versioned, provenance-linked derived and harmonized artifacts.
  Existing recovery datasets remain unchanged.
- `schemas/`: prospective dataset contracts, beginning with
  [`HEA_deformation_mechanism_schema.md`](schemas/HEA_deformation_mechanism_schema.md).
- `interim/`, `external/`, `schema/`, and `splits/`: established project
  locations retained for compatibility with the current recovery workflow.

The new schema is a design specification, not a populated dataset. It does not
authorize literature collection, label inference, imputation, descriptor
calculation, or model training. Experimental observations and computational
predictions must remain distinguishable and traceable to their sources.
