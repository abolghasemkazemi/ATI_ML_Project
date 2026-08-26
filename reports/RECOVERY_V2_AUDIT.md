# Recovery v2 hierarchy, leakage, target, provenance, and missingness audit

## Preservation and provenance

- Recovery v1 input: 98 rows; recovery v2: 108 rows. All 98 legacy rows remain in their original order.
- Every legacy scientific/source column is unchanged. Only explicit hierarchy/role metadata is reclassified for P016 C01-C03; canonical P006 TRIP/TWIP cells are not overwritten.
- Added records carry workbook, sheet, evidence location, and confidence. The P006 correction ledger retains original and effective values.

## Hierarchy and leakage

- P016 has six exact ML conditions: 400 C/3 min, 400 C/10 min, 650 C/3 min, 650 C/10 min, 750 C/3 min, and 750 C/10 min.
- P016_C03 is `LEGACY_COLLAPSED` and is excluded from ML-condition counts.
- Six stage rows are `REPEATED_STAGE`, share their exact parent `ML_Condition_ID`, and contribute zero additional independent conditions.
- Duplicate observation IDs: 0; stage rows lacking a parent exact condition: 0.

## Targets

- 400 C conditions remain TRIP/TWIP unresolved. 650 C/3 min and 650 C/10 min are TRIP=1/TWIP=NA. 750 C/3 min is TRIP=1/TWIP=1. 750 C/10 min remains unresolved.
- P006_C01 effective TRIP=0/TWIP=NA; P006_C02 effective TRIP=0/TWIP=1; P006_C03 effective TRIP=1/TWIP=NA. P006_C03's original TWIP=0 remains present and is invalidated only through the correction ledger.

| Usable experimental ML conditions | Before v2 | After v2 |
|---|---:|---:|
| TRIP | 48 | 50 |
| TWIP | 46 | 45 |
| Joint | 46 | 45 |

## Missingness and readiness

- Mean missingness across preserved recovery-v1 columns: 55.46% before and 57.92% after on the observation-row basis. The increase is expected because stage children contain only directly documented stage values; no value was invented or copied to suppress missingness.
- No ML was trained. Recovery v2 is evidence-resolved, not declared ML-ready; grouped validation, target leakage screening, sparse descriptors, small support, and remaining P1 issues still gate modelling.
