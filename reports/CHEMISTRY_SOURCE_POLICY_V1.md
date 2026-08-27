# Chemistry Source Policy V1

## Status and scope

This policy is frozen for the next source-preserving matrix-construction stage. It is documentation only in Grouped Split Design V1: no unified chemistry column was created, no composition was parsed or reconciled, and no value was normalized, filled, or calculated.

## Future selection rule

For each independent experimental condition:

1. If explicitly measured **bulk specimen/material chemistry** is available with a valid source scope, method/provenance, and composition basis, prefer that measured bulk representation.
2. Otherwise, use explicitly reported nominal composition.
3. Retain `Composition_Source` as `MEASURED_BULK` or `NOMINAL` beside every later selected value.
4. Preserve the original measured, nominal, basis, uncertainty, method, and provenance fields; the selected representation must never overwrite them.
5. If neither valid bulk-measured nor nominal chemistry is available, retain missingness. Do not infer absent elements as zero.

"Valid measured bulk" means source evidence explicitly scoped to the specimen/material bulk rather than a local region or feedstock, with enough method and basis information to interpret the reported composition. A disagreement or ambiguous scope is a review flag, not permission to average, normalize, or silently choose a value.

## Prohibited substitutions

- Local EDS, local APT, TEM-local chemistry, scanned-region chemistry, precipitate chemistry, and grain-boundary chemistry do not substitute for bulk chemistry unless a later explicit scientific decision justifies that exact use.
- Feedstock chemistry is not automatically final specimen bulk chemistry.
- Nominal and measured values are not averaged.
- Cross-paper alloy families are not declared equivalent by similar text or apparent composition.
- Missing elements are not converted to zero, and totals are not normalized in this phase.

## Provenance required later

Any future source-preserving chemistry representation must retain `Paper_ID`, `ML_Condition_ID`, original composition text, composition basis, selected source class, measurement method/scope, uncertainty where reported, and source location. Conflict and selection decisions must be auditable condition by condition.

## Gate

The next task may implement this policy while constructing an untransformed, provenance-preserving condition table. It must still perform no imputation, encoding, normalization, alloy-descriptor calculation, resampling, or model training unless separately authorized and scientifically justified.
