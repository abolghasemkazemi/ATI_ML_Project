# Hierarchical grouping audit

## Scope and counting rules

This audit preserves all 98 source rows and their TRIP/TWIP values. `HYBRID` rows with an experimental condition count as experimental observations; pure MD/CALPHAD/other-computational rows count as computational. Summary rows are not independent conditions. Parent-level labels are reported only when all labelled independent conditions in that parent agree; no majority label is forced.

## Independence census

| Measure | Count |
|---|---:|
| A. Total observations | 98 |
| B. Experimental observations | 72 |
| C. Computational observations | 26 |
| D. Unique experimental Parent_Experiment_ID | 55 |
| E. Independent experimental conditions | 52 |
| F. Repeated deformation-stage observations | 19 |
| G. Summary rows | 1 |
| H. Unresolved rows | 0 |

## TRIP and TWIP distributions

### Observation level

| Label | 0 | 1 | unresolved |
|---|---:|---:|---:|
| TRIP | 17 | 71 | 10 |
| TWIP | 19 | 66 | 13 |
### Independent Condition level

| Label | 0 | 1 | unresolved |
|---|---:|---:|---:|
| TRIP | 11 | 33 | 8 |
| TWIP | 11 | 30 | 11 |
### Parent Experiment level

| Label | 0 | 1 | unresolved |
|---|---:|---:|---:|
| TRIP | 11 | 33 | 8 |
| TWIP | 11 | 30 | 11 |

## Conflict result

- Previously conflicting original groups: **10** (P001_G01, P002_G01, P004_G01, P005_G01, P006_G01, P011_A10, P012_Fe38.3Mn40Co10Cr10Mo1.7, P012_Fe39.5Mn40Co10Cr10C0.5, P012_Fe40Mn40Co10Cr10, P015_G01).
- Conflicts that disappear under the hierarchy: **10**.
- Remaining parent-level conflicts: **0**. No remaining conflict is treated as a label error; stage evolution is excluded from independent-condition conflict tests.
- Genuinely scientifically ambiguous grouping rows: **11** rows across **3** papers.

## Required original-paper review

- **Grouping:** P006, P007, P016.
- **TRIP/TWIP labels:** P001, P002, P003, P004, P005, P006, P007, P008, P010, P011, P012, P013, P014, P015, P016, P017, P018.

### Recoverable-feature review by paper

- **grain size:** P002, P006, P008, P009, P010, P011, P012, P013, P014, P015, P016, P017, P019
- **SFE:** P002, P004, P006, P007, P008, P009, P010, P011, P012, P013, P014, P016, P017, P018, P019
- **initial FCC fraction:** P008, P009, P010, P011, P012, P013, P014, P016, P017, P018, P019
- **initial HCP fraction:** P007, P008, P009, P010, P011, P012, P013, P014, P015, P016, P017, P018, P019
- **strain rate:** P002, P005, P009, P014, P018, P019
- **test temperature:** P002, P018
- **processing information:** none

## Currently usable independent experimental conditions

- **TRIP:** 44
- **TWIP:** 41
- **Joint TRIP/TWIP:** 41

These counts include experimental conditions in `HYBRID` studies but exclude repeated stages, summaries, and purely computational conditions. They are availability counts, not a claim that all predictors are complete.
