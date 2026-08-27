# P020 recovery v14 audit

## A. Source identity

- `Paper_ID=P020`; DOI `10.1080/21663831.2018.1523239`; title **Deformation mechanisms and work-hardening behavior of transformation-induced plasticity high entropy alloys by in-situ neutron diffraction**.
- Materials Research Letters 6(11), 620-626 (2018). The verified workbook status is `VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH`; both workbook and V13 base were SHA-256 gated.

## B. New-vs-existing source status

- P020 is a new primary experimental source beyond P001-P019. No P020 `Paper_ID` or DOI exists in recovery V13.
- Nominal `Fe50Mn30Co10Cr10` also occurs in P003/P011/P013/P014, but common composition text is not physical-sample identity. P020 has its own preparation, `P020_SERIES01`, `P020_MAT_FE50MN30CO10CR10`, and condition; it is not merged into P013 or another paper.

## C-E. V14 size, independence, and exact condition

- Recovery V14 contains **214 rows**: all **207** V13 rows unchanged, one exact P020 primary condition, and six correlated in-situ observations.
- Replacement-aware independent experimental conditions: **51 before -> 52 after**. The increase is programmatically confirmed only after proving that P020/DOI were absent from V13.
- Exact P020 condition: `P020_MC_TRIPHEA_INSITU` under `P020_SERIES01` / `P020_MAT_FE50MN30CO10CR10`. Physical batch, replicate identity, and replicate count remain NA.

## F-G. Composition and processing

- Nominal chemistry is `Fe50Mn30Co10Cr10` at.% with status `NOMINAL_ONLY_NO_QUANTITATIVE_POSTMELT_BULK_CHEMISTRY_REPORTED`. Measured bulk chemistry remains NA; no composition or chemistry is transferred from another Fe50Mn30Co10Cr10 paper.
- Processing retains >99.9 wt.% raw-metal purity, vacuum arc melting, drop casting to 12.7 x 12.7 x 75 mm, 1150 C/4 h/vacuum homogenization, room-temperature rolling at 75% reduction, and 950 C/1 h annealing followed by air cooling.

## H. Missing supplement and test conditions

- The main article refers detailed tensile metadata to a supplement that is not present. `Test_T_Raw=NOT_EXPLICITLY_REPORTED_IN_MAIN_ARTICLE`; numeric test temperature, strain rate, specimen geometry, and replicate count remain NA. Room temperature and 1e-3 s^-1 were not imported or inferred.

## I-K. Initial dual-phase microstructure

- EBSD and neutron diffraction independently report initial FCC=0.79 and HCP=0.21. The pre-existing HCP does not generate TRIP; condition-level TRIP is based on dynamic FCC loss during tensile loading.
- FCC grains are equiaxed with average size approximately 40 um. HCP is lath-shaped with average lath thickness approximately 4 um.

## L-O. Condition targets, phase semantics, and slip

- `P020_MC_TRIPHEA_INSITU` is verified TRIP=1, TWIP=1, Slip=1 (`VERIFIED_JOINT`).
- TRIP is FCC-to-HCP transformation measured through continuous real-time FCC loss beginning near 200 MPa and persisting to fracture.
- TWIP is explicitly **HCP-phase** `{10.2}` tensile twinning followed by compression/multiple HCP twinning. `TWIP_Phase=HCP` and `TWIP_Mode=HCP_TENSILE_AND_COMPRESSION_TWINNING`; it is not labelled as FCC twinning.
- Slip accompanies FCC TRIP and later HCP twinning. Phase-specific meaning is preserved rather than globally redefining the TWIP target.

## P-Q. Stage transitions and fracture phase fraction

- Six observations are non-independent children: elastic 0-to-approximately-200 MPa; TRIP/slip onset near 200 MPa; HCP tensile twinning near 400 MPa; compression/multiple HCP twinning plus slip near 730 MPa and approximately 15% strain; slower-but-persistent TRIP above approximately 25% strain; and the fracture endpoint.
- Stage-I zeros are pre-yield stage values only and are never condition-level negatives. Slower transformation is not absence: the late stage remains TRIP=1.
- Direct remaining FCC at fracture is approximately 0.17. Exact HCP=0.83 is not calculated or stored; the HCP fracture fraction remains NA.

## R. Mechanical response and leakage

- Approximately 200 MPa is stored only as `Apparent_Yield_Onset_MPa` with definition `OBSERVABLE_DEVIATION_FROM_ELASTIC_REGIME`, not conventional 0.2% offset YS.
- Source-reported ultimate strength is 1046 MPa and reported elongation is 34%. The figure's macro true-stress/true-strain context and the text's raw word “elongation” are preserved; no engineering/true conversion is made.
- All response values are `MECHANICAL_OUTCOME_LEAKAGE` for pre-deformation models.

## S-T. SFE and DeltaG gaps

- P020 SFE remains NA. P020 DeltaG remains NA. No 6.5 mJ/m2 or other value is imported, calculated, or transferred from P003/P011/P013/P014.

## U. P020/P013 non-duplication safeguard

- P020 and P013 share nominal composition text but not study, preparation, condition, or material identity. Separate paper/study/material/leakage identifiers are enforced. `Alloy_Family_Text` is grouping-audit metadata only and not an ML predictor.

## V. Usable target counts

- Usable TRIP/TWIP/joint counts: **31/29/26 before -> 32/30/27 after**.
- Binary class support changes TRIP 27/4 to 28/4 positive/negative and TWIP 24/5 to 25/5.
- Joint states change only by one verified `11`: before `00=0, 10=5, 01=4, 11=17`; after `00=0, 10=5, 01=4, 11=18`.

## W. Remaining P020 gaps

- Missing quantitative post-melt bulk chemistry, supplement-defined test temperature/rate/geometry/replicates, physical-batch identity, any P020 numeric SFE or DeltaG, and an explicitly reported HCP fracture fraction remain NA.

## X. Downstream refresh status

- V13/V12 Global QC, Feature Schema coverage statistics, feature coverage, and Grouped Split Design statistics do not include P020 and require a later non-destructive refresh. They are deliberately not refreshed while additional papers are being collected.
- No ML model was trained. No matrix, feature engineering, imputation, normalization, composition reconciliation, derived alloy descriptor, resampling, synthetic record, digitized curve, or performance metric was created.
