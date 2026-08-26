# P011 recovery v6 audit

## Preservation, hierarchy, and leakage
- recovery_v6 total rows: **137**; all **127** recovery_v5 rows are byte-value-equivalent in their original columns and order.
- Four source processing states (A8/A9/A10/A11) are preserved in `reports/tables/p011_recovery_v6_source_states.csv`. A8 is not a primary condition.
- Exactly four primary independent conditions were appended: `P011_MC_A9_298K`, `P011_MC_A10_298K`, `P011_MC_A11_298K`, and `P011_MC_A10_77K`.
- Six repeated-stage children were appended; all are non-independent and inherit `P011_SERIES01` / `P011_MAT_FE50MN30CO10CR10` leakage groups.
- Five legacy rows remain unchanged. Scientific matching maps C02-C05 exactly to replacements; C01 maps only to A8 and is excluded from independent use. Thus neither legacy rows nor n=3 aggregate tensile metadata are double-counted.

## Counts
| Metric | recovery_v5 | recovery_v6 |
|---|---:|---:|
| Independent experimental conditions | 43 | 42 |
| Usable TRIP | 33 | 30 |
| Usable TWIP | 30 | 27 |
| Usable joint | 30 | 27 |

## Recovered evidence
- Feedstock EDS is Fe49.2Mn31.4Co9.4Cr10.0 at.% at `FEEDSTOCK` scope. A10 Fe49.5Mn29.6Co10.5Cr10.4 is separately `LOCAL_OR_SCANNED_REGION_EDS`.
- Relative densities, initial EBSD phase fractions, primary and alternative grain-size definitions, annealing Sigma3 boundary fractions, Mn-oxide fractions, and initial XRD lattice parameters are preserved by processing state. Initial annealing twins never establish TWIP.
- Mechanics: A9 YS 300.5 MPa (UTS/UE unresolved); A10-298 287.1/745.7 MPa and 28.1% UE; A11-298 257.3/708.9 MPa and 31.0% UE; A10-77 489.7/1107.3 MPa and 25.5% UE.
- Effective targets: A10-298=1/1; A10-77=1/0 with explicit direct negative TWIP evidence; A9/A11 remain NA/NA. Slip and detwinning remain separate mechanism fields.
- Initial versus fracture HCP and XRD versus fracture TEM lattice parameters remain distinct. No exact 15% HCP value was digitized. Sigma3 is not treated as deformation-twin volume fraction.
- SFE is method-separated in `reports/tables/p011_recovery_v6_sfe.csv`: current-paper thermodynamic 18.4 (298 K) and -14.4 (77 K), versus secondary ab-initio ranges 14–22 and -9–-2 mJ/m2. No value is duplicated per SPS state or called experimental.

## Unresolved fields and blockers
A9 exact UTS/UE, both 15% HCP fractions, A9/A11 condition-specific targets, A8 EBSD phase fractions/tensile condition, physical-batch and individual replicate identities remain unresolved. Remaining project P1/P2 blockers include broader target review, feature-leakage eligibility, computational/experimental domain separation, sparse descriptors/reference constants, small support, and final-target selection. No ML, feature engineering, derived descriptors, figure digitization, pseudo-replicates, or fabricated values were produced.
