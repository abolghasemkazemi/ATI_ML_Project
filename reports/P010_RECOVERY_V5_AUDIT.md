# P010 recovery v5 audit

## Preservation and hierarchy
- recovery_v5 total row count: **127** (118 unchanged recovery_v4 rows plus 3 exact conditions and 6 correlated stages).
- P010 uses `P010_SERIES01`, three alloy-specific material parents, **3 independent conditions**, and **6 `REPEATED_STAGE` non-independent children**. Every child retains its parent's strict and material leakage groups.
- Physical batch and replicate IDs remain NA. Measured wet chemistry and element-wise uncertainty are stored separately from nominal chemistry and were not normalized.

## Targets and counts
| Metric | recovery_v4 | recovery_v5 |
|---|---:|---:|
| Independent experimental conditions | 40 | 43 |
| TRIP usable | 30 | 33 |
| TWIP usable | 27 | 30 |
| Joint usable | 27 | 30 |

P010 effective targets are Alloy I 1/1, Alloy II 0/1, and Alloy III 1/1. The legacy Alloy III 0/0 remains untouched; the effective correction adds two positive usable targets and changes its effective interpretation to TWIP-dominant + minor TRIP + slip. Stage fractions remain outcome evidence, not independent conditions.

## Scientific recovery and gaps
- Approximate magnetization transitions (160/190/80 K) retain `APPROX_EXPERIMENTAL_MAGNETIZATION_TRANSITION`; 5 K antiferromagnet-like behavior is separate and is not a room-temperature AFM label. Tensile temperature remains raw `ROOM_TEMPERATURE_REPORTED`, not an exact Kelvin value.
- Absolute SFE, YS, UTS, elongation, grain size, and exact initial FCC/HCP fractions remain NA. Computational PM/AFM methods and qualitative relative SFE trends are separate from experimental finite-temperature SFE.
- Remaining blockers: Supplemental Figs. S2/S4 and method-specific supplemental SFE values; exact condition grain sizes; source-supported batch/replicate identities. No NA was converted to zero except Alloy II stage HCP/TRIP, supported by explicit negative high-strain evidence.

## Provenance and leakage checks
`reports/tables/p010_recovery_v5_provenance.csv` records paper, DOI, condition, observation, feature, value, units, evidence type/location, confidence, and status. `reports/tables/p010_recovery_v5_corrections.csv` records all requested corrections and non-inference rules. No ML, feature engineering, descriptor calculation, figure digitization, normalization, or fabrication was performed.
