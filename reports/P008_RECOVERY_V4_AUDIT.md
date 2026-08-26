# P008 recovery v4 audit

## Source identity and preservation

- Verified `Paper_ID=P008`, DOI `10.1016/j.ijplas.2021.102965`, and the workbook's six-condition hierarchy for **Multi-heterostructure and mechanical properties of N-doped FeMnCoCr high entropy alloy**. Integration fails closed on an ID/DOI mismatch.
- recovery_v3 rows: **113**; recovery_v4 rows: **118**; rows added: **5**. All 113 prior rows and their scientific fields remain present and ordered.
- Both legacy rows remain. `P008_C02` maps exactly to `P008_MC_N2p6_PC`; `P008_C01` is `MANUAL_IDENTITY_REVIEW` and excluded from independent counting to prevent double counting with the new exact N0-HOMO record.

## Exact hierarchy and leakage

P008 has **6 exact independent conditions**, all in `P008_SERIES01`. N0 HOMO/PC/FC are siblings under `P008_MAT_N0`; N2.6 HOMO/PC/FC are siblings under `P008_MAT_N2p6`. `Physical_Batch_ID` and `Replicate_ID` remain unknown (NA). Strict splits use `P008_SERIES01`; material-level splits use the corresponding parent. Source/stage/auxiliary records add no independent conditions. See `reports/tables/p008_recovery_v4_hierarchy.csv`.

## Target evidence before and after

| Exact condition | Effective TRIP | Effective TWIP |
|---|---:|---:|
| N0-HOMO | NA | NA |
| N0-PC | 1 | 1 |
| N0-FC | 1 | NA |
| N2.6-HOMO | NA | NA |
| N2.6-PC | 0 | 1 |
| N2.6-FC | 0 | 1 |

The verified corrections are: N0-PC TWIP unresolved→1; N0-FC TRIP unresolved→1; N2.6-FC unresolved→0/1. HOMO remains unresolved. NA was never interpreted as negative.

## Recovered descriptors and phase correction

Condition-scoped processing, RT text/status, 1e-3 s^-1 strain rate, grain-size values/scopes, N0 EBSD HCP fractions, recrystallized fractions, and supported YS/UTS/uniform elongation were recovered. N2.6-PC stores ~0.24 pre-existing **BCC alpha** separately from HCP and leaves FCC NA; FCC was never computed as 1-HCP. Alpha-lath, recovery-twin, deformation-twin, Cr2N, and local APT/EDS evidence remain distinct fields; local chemistry does not replace bulk chemistry and recovery twins do not establish TWIP.

## SFE and unresolved evidence

N2.6 ≈26 mJ/m2 is stored with `ALLOY_LEVEL`/TEM/current-study scope and is absent from condition-specific `SFE_mJ_m2`. N0 6.5 mJ/m2 is marked `SECONDARY_REFERENCE`, not a P008 measurement. Supplementary Table S1 is unavailable, so missing HOMO/FC UTS and elongation remain NA. Exact RT Kelvin, exact FCC fractions, intermediate-N bulk chemistry/targets, physical batches, and replicates remain unresolved. No figures were digitized and no supplementary values were fabricated.

## Count impact

| Metric | recovery_v3 | recovery_v4 |
|---|---:|---:|
| Independent experimental ML conditions | 36 | 40 |
| Usable TRIP conditions | 28 | 30 |
| Usable TWIP conditions | 25 | 27 |
| Usable joint conditions | 25 | 27 |

P008 changes from two legacy independent rows to six exact conditions while retaining both legacy observations; the ambiguous legacy C01 is not counted twice. Auxiliary N0.5/N0.8/N1.1/N1.4/N1.8/N3.2 entries remain source-only in `reports/tables/p008_recovery_v4_aux_n_series.csv`.

## Provenance and correction ledger

Every populated recovered value is represented in `reports/tables/p008_recovery_v4_provenance.csv`; the six verified corrections are retained in `reports/tables/p008_recovery_v4_corrections.csv`. No ML, descriptors, feature engineering, figure digitization, or model selection was performed.
