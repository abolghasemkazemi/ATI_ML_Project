# P002 recovery v13 audit

## 1. Scope, source identity, and immutable base

- This is source-specific P002 dataset recovery only. The verified source is **A TWIP-TRIP quinary high-entropy alloy: Tuning phase stability and microstructure for enhanced mechanical properties**, DOI **10.1016/j.msea.2020.140441**; the official corrigendum DOI is **10.1016/j.msea.2021.142419**.
- Source identity status is `VERIFIED_PDF_AND_EXTERNAL_DOI_MATCH`. The input workbook and the 192-row V12-QC base were hash-checked before integration.
- Recovery V13 has **207 rows**. Every V12-QC row, source-column value, missingness state, and row order is preserved. V13 appends new fields and records; it does not revise the V12-QC cells in place.

## 2. Corrigendum handling

- The original self-comparison typo is not used. V13 applies the official statement: **the 800 C condition shows more pronounced TRIP than the 700 C condition**.
- Numerical EBSD fractions are unchanged. Corrigendum DOI, affected section, original/corrected semantics, and action are retained in the corrigendum and provenance tables.

## 3. Legacy mapping and replacement-aware counts

- All **5** legacy P002 rows remain. `P002_C01`, `P002_C02`, and `P002_C03` map scientifically—not by row order—to A800, A700, and A600 using DOI, composition, annealing temperature, room-temperature representation, strain rate, mechanics, and historical targets.
- `P002_C04` remains a reference-comparator support row. `P002_C05` remains a CALPHAD descriptor support row. Neither is promoted.
- Three exact primary conditions were appended: `P002_MC_A600_RT`, `P002_MC_A700_RT`, and `P002_MC_A800_RT`. Exact replacements alone supply P002's independent count, preventing legacy/exact double counting.
- Replacement-aware independent / usable TRIP / usable TWIP / usable joint counts: **51/32/30/27 before -> 51/31/29/26 after**. The independent count remains 51; removing the unsupported A600 `0/0` from effective labels reduces each usable binary target and the joint target by one.
- Legacy A600 `0/0` is retained unchanged and copied only to `Original_TRIP`/`Original_TWIP` on the exact replacement. Verified `Effective_TRIP`/`Effective_TWIP` remain `NA/NA`; the conflict is explicit in both mapping and correction ledgers.

## 4. Hierarchy, independence, and replicates

- All exact conditions use study series `P002_SERIES01`, material parent `P002_MAT_FE40MN10CO20CR20NI10`, strict leakage group `P002_SERIES01`, and material leakage group `P002_MAT_FE40MN10CO20CR20NI10`.
- `Physical_Batch_ID` and `Replicate_ID` remain NA because the source does not identify them. `Replicate_n=3` is aggregate metadata for each annealing temperature; no individual or pseudo-replicate rows were created.
- Ten correlated stage/post-test observations and two non-independent Hall-Petch support states were appended. They cannot increase the independent experimental count. The A800 Hall-Petch input is the same condition as `P002_MC_A800_RT` and remains table-only rather than becoming a duplicate master row.

## 5. Chemistry and processing

- Chemistry is nominal `Fe40Mn10Co20Cr20Ni10` at.% only. `Measured_Bulk_Composition` and `Measured_Composition_at_pct` remain NA with status `NOMINAL_ONLY_EDS_QUALITATIVE_HOMOGENEITY_NO_QUANTITATIVE_BULK_ANALYSIS`.
- EDS/STEM-EDS homogeneity is retained only as qualitative spatial evidence; it is never converted to quantitative bulk chemistry.
- Processing preserves vacuum induction melting/casting from >99.8 wt% raw metals; hot rolling at 900 C, 50%, 10 to 5 mm; homogenization at 1200 C for 2 h in Ar followed by water quench; cold rolling 70%, 5 to 1.5 mm; and 600/700/800 C, 30 min, water-quenched final anneals.
- Tensile testing is uniaxial at source-text `room temperature`, 1e-3 s^-1, gauge 10 x 2.5 x approximately 1.25 mm. Exact numeric `Test_T_K` remains NA.

## 6. Initial microstructure and twin-origin safeguard

- All three exact conditions are qualitatively single FCC with direct initial HCP absence (`Initial_HCP_fraction=0`). Exact numeric FCC fractions remain NA.
- A800 is fully recrystallized (1.0/0), average grain size 4.7 +/- 0.3 um, randomized, with abundant annealing twins and very low dislocation density.
- A700 retains approximately 0.92/0.08 recrystallized/non-recrystallized fractions, approximately 3.6 um RZ grain size, 12 um NRZ dimension, 0.95 um subgrains, 220 nm mean pre-test twin width, and raw scoped wording `~27.5 vol% in RZ` for Sigma3 boundaries.
- A600 retains approximately 0.13/0.87 recrystallized/non-recrystallized fractions, approximately 1.8 um RZ grain size, 0.40 um NRZ subgrains, dislocation tangles, and pre-existing nanoscale twins.
- Annealing and retained processing twins are initial-state descriptors only. They never generate tensile `Effective_TWIP=1` without separate deformation evidence.

## 7. Mechanical outcomes and target evidence

- Post-test mechanical outcomes are leakage-sensitive metadata: A800 375/785 MPa and 77.5%; A700 589/865 MPa and 69.1%; A600 approximately 1060 MPa YS with UTS/elongation NA. Figure 6 was not digitized.
- A800 is TRIP=1 from direct EBSD/XRD deformation-induced FCC-to-HCP evidence. TWIP=1 is retained at **medium** directness as `AUTHOR_CONDITION_ATTRIBUTION_SUPPORTED_BY_STUDY_CONCLUSION`; it is not represented as direct A800 TEM evidence. Slip=1.
- A700 is TRIP=1/TWIP=1/Slip=1 with high-confidence direct EBSD plus near-fracture TEM/SAED/HR-STEM evidence for HCP martensite, deformation-twin bundles, dislocation structures, and stacking faults.
- A600 is TRIP=NA/TWIP=NA/Slip=1 with `Negative_Evidence_Status=INSUFFICIENT_FOR_ZERO`. “Hindered/suppressed” and absent dedicated post-test characterization are not converted to negatives.

## 8. Correlated stage evidence

- A800 EBSD keeps HCP fractions 5.7% at 45% local strain and 16.3% at 65%; the 10% observation is “barely observed” with no fabricated fraction. XRD 0/45/~95% observations remain correlated children, with the zero explicitly scoped to pre-deformation phase evidence.
- A700 EBSD keeps 0.7/3.8/7.2% HCP at 10/45/65% local strain. The near-fracture TEM/SAED/HR-STEM record is correlated post-test evidence, not another ML sample.

## 9. Physics, thermodynamics, and Hall-Petch scope

- `DeltaG_FCC_to_HCP=-292 J/mol` at 300 K is `CURRENT_PAPER_CALCULATED` by Thermo-Calc TCFE7. It is not transferred to other papers/alloys.
- SFE approximately 14 mJ/m2 at 300 K is `CURRENT_PAPER_THERMODYNAMIC_ESTIMATE`, not experimental SFE. The method-specific record retains DeltaG, 22.2 J/mol transformation strain energy, 15 mJ/m2 coherent interface energy, 2.98e-5 mol/m2 planar density, and the 0.3587 nm lattice constant used in the derivation. Reference/model inputs remain distinct from current-paper measurements.
- Hall-Petch inputs retain as-homogenized 128 +/- 18 um / 188 MPa, A900 16 +/- 0.6 um / 253 MPa, and A800 4.7 +/- 0.3 um / 375 MPa. Derived sigma0 approximately 139 MPa and k approximately 504 MPa um^0.5 are `CURRENT_PAPER_MODEL_DERIVED_FROM_MECHANICAL_RESPONSE`, leakage-sensitive, and not primary predictors.

## 10. Provenance, gaps, and downstream status

- Field-level provenance includes Paper_ID, DOI, corrigendum DOI, material parent, applicable ML/record identity, feature, value, units, evidence type/location, method, confidence, and recovery status. Meaningful NA decisions are recorded as `VERIFIED_NA`.
- Remaining P002 gaps are quantitative post-melt bulk chemistry, exact test temperature in K, physical-batch/replicate identities and individual results, exact initial FCC fractions, A600 UTS/elongation and direct post-test TRIP/TWIP characterization, a numeric A800 10% HCP fraction, direct A800 post-test twin imaging, and some state-specific uncertainty values.
- Remaining global blockers include sparse independent negatives (now one fewer effective P002 negative for each binary target), incomplete targets, missing physical batches, paper/material dependence, unavailable P018/P019 sources, sparse measured chemistry/initial-state/experimental-SFE coverage, and prediction-time leakage controls.
- Existing V12 Global QC, Feature Schema V1 coverage statistics, feature coverage reports, and Grouped Split Design V1 are preserved but **stale with respect to V13**. They must be refreshed before matrix construction; this task deliberately does not rerun them or reuse the old split roster as current.
- No ML training occurred. No feature engineering occurred. No chemistry reconciliation/normalization, imputation, descriptor calculation, resampling, synthetic data, pseudo-replication, or performance metric occurred.
