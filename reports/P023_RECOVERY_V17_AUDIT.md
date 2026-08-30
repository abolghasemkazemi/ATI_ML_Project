# P023 recovery v17 audit

## A. Source identity

- Paper_ID=P023; DOI=10.1016/j.apmt.2018.09.002.
- Title: Unexpected strength–ductility response in an annealed, metastable, high-entropy alloy.
- Applied Materials Today, volume 13, pages 198-206 (2018); Data_Origin=EXPERIMENTAL.
- The verified workbook identity matches the PDF/publisher DOI record. Both workbook and recovery-v16 base are SHA-256 gated; integration rejects a mismatch.

## B. Duplicate/source-family status

- Exact recovery-v16 DOI matches: 0; P023 Paper_ID matches: 0.
- P023 is appended as a new source beyond P022 under P023_SERIES01. It is not merged with related Nene/Mishra papers on the basis of authors, FSP route, or alloy family; such relationships remain audit-only context.

## C. V17 row count

- V17 contains 234 rows: the complete 227-row recovery-v16 prefix plus exactly seven primary P023 tensile conditions.
- No 750 C support state, replicate, before/after evidence row, or curve-inferred stage was appended to the master.

## D. Experimental count before/after

- Replacement-aware independent experimental conditions: 62 before -> 69 after.
- The +7 change is exactly the seven requested primary P023 conditions.

## E. Seven exact tensile conditions

- P023_MC_DPASS_RT, P023_MC_650_5_RT, P023_MC_650_15_RT, P023_MC_650_30_RT, P023_MC_850_5_RT, P023_MC_850_15_RT, P023_MC_850_30_RT.
- Each is an independent source-defined room-temperature tensile condition under one strict study/material leakage group.

## F. Ten supporting processing states

- Exactly ten pre-test processing-state phase records are retained: P023_STATE_DPASS, P023_STATE_650_5, P023_STATE_650_15, P023_STATE_650_30, P023_STATE_750_5, P023_STATE_750_15, P023_STATE_750_30, P023_STATE_850_5, P023_STATE_850_15, P023_STATE_850_30.
- P023_STATE_750_5, P023_STATE_750_15, and P023_STATE_750_30 are supporting-only because the paper does not provide condition-specific tensile results for them.

## G. Nominal chemistry

- Nominal chemistry is exactly Fe39Mn20Co20Cr15Si5Al1 at.%: Fe39, Mn20, Co20, Cr15, Si5, Al1.
- Values are source-reported nominal fractions; no normalization or derived composition descriptor was calculated.

## H. Local EDS vs bulk-chemistry safeguard

- Measured bulk/post-melt chemistry remains NA.
- As-cast local EDS is Fe40.2 Mn19.7 Co20.5 Cr14.4 Si4.6 Al0.7 at.%; D-pass local EDS is Fe39.0 Mn19.8 Co20.0 Cr15.9 Si4.3 Al1.03 at.%.
- Both are stored as LOCAL_EDS_ELEMENTAL_DISTRIBUTION_TABLE_NOT_BULK_CHEMISTRY and never overwrite nominal or bulk chemistry.

## I. FSP processing

- Vacuum arc casting in a cold-copper crucible retains raw vacuum notation `~300 um vacuum`, Ar backfill to 1 atm, and 300 x 100 x 6 mm ingot dimensions.
- Double-pass FSP retains 350/150 rpm, 50.8 mm/min traverse, 3.65 mm plunge, 2 degree tilt, Cu backing plate, and Ar shielding near the tool/specimen interface.

## J. Annealing grid

- D-pass specimens were annealed at 650, 750, and 850 C for 5, 15, and 30 min and water quenched.
- Only D-pass, 650-X, and 850-X states with reported tensile conditions enter the seven-row master addition; 750-X remains support-only.

## K. Pre-test phase fractions

- Exact FCC/HCP/SD percentage-point records are: D-pass 0.83/0.17/3.9; 650-5 0.86/0.14/4.2; 650-15 0.30/0.70/3.5; 650-30 0.55/0.45/2.2; 750-5 0.79/0.21/0.4; 750-15 0.72/0.28/4.1; 750-30 0.88/0.12/1.0; 850-5 0.95/0.05/0.2; 850-15 0.97/0.03/2.3; 850-30 0.43/0.57/4.3.
- All are PRE_TENSILE_PROCESSING_STATE evidence from the Fig.2c EBSD/XRD summary. Initial HCP never establishes tensile TRIP.

## L. Precipitation handling

- 650-X fine/controlled precipitation, 650-15 fine Al-rich precipitates, 850-X stronger precipitation/grain growth, 850-15 large Al-rich grain-boundary precipitates, and 850-30 massive Al-rich precipitation/grain growth are retained as pre-test microstructure.
- Fig.3g annealed grain sizes and Fig.3h matrix-Al values were not digitized. Only the qualitative decrease in matrix Al with annealing time is retained.

## M. D-pass grain size

- D-pass grain size is 0.79 +/- 0.05 um. As-cast 120 +/- 12 um is retained only as supporting material-state information.
- No annealed numeric grain size was created from Fig.3g.

## N. Room-temperature/strain-rate metadata

- Test_T_Raw=room temperature; exact Test_T_K and Test_T_C remain NA.
- Initial strain rate is 1e-3 s^-1, loading is uniaxial tension, and gauge length/width/thickness are 5/1.25/1 mm.

## O. Replicate handling

- Replicate_n=3 records the source statement that three specimens were tested per condition.
- Physical_Batch_ID and Replicate_ID remain NA. No pseudo-replicate or individual result row was created.

## P. 650-15 direct TRIP

- P023_MC_650_15_RT is Effective_TRIP=1 because direct before/after EBSD shows FCC 0.30 -> 0.06 and HCP epsilon 0.70 -> 0.94 during tensile deformation.
- The pre-test HCP=0.70 alone is not TRIP evidence; the tensile phase change is.

## Q. 650-15 HCP-TWIP/slip

- P023_MC_650_15_RT is Effective_TWIP=1 and Slip=1 from directly reported epsilon-HCP twinning and <c+a> slip.
- TWIP_Phase=HCP_EPSILON; it is not recoded as FCC deformation twinning.

## R. 850-30 direct TRIP

- P023_MC_850_30_RT is Effective_TRIP=1 because direct before/after EBSD shows FCC 0.43 -> 0.10 and HCP epsilon 0.57 -> 0.90 during tensile deformation.

## S. 850-30 HCP-TWIP/slip

- P023_MC_850_30_RT is Effective_TWIP=1 and Slip=1 from directly reported epsilon-phase twinning and <c+a> slip.
- TWIP_Phase=HCP_EPSILON.

## T. Five unresolved targets

- P023_MC_DPASS_RT, P023_MC_650_5_RT, P023_MC_650_30_RT, P023_MC_850_5_RT, P023_MC_850_15_RT retain Effective_TRIP/Effective_TWIP/Slip=NA and Negative_Evidence_Status=INSUFFICIENT_FOR_ZERO.
- Work-hardening/stress-strain curve shape, missing microscopy, and initial HCP create neither positive nor negative labels.

## U. WH-derived TRIP onset classification

- For 650-15, the reported 924 MPa true-stress onset, approximately 840 MPa engineering stress, approximately 10% associated strain/elongation, and 2983 MPa WH rate are retained.
- The onset is CURRENT_PAPER_CURVE_INFERRED_MECHANISM_ONSET / MODEL_CURVE_INFERENCE_NOT_DIRECT_STAGE; the WH rate is mechanical-response-derived leakage. No direct interrupted-test stage was fabricated.

## V. Post-test leakage handling

- The 650-15 and 850-30 post-test phase fractions, twins, IPF/GND/dislocation evidence, and slip observations are POST_TEST_TARGET_EVIDENCE.
- They are excluded from pre-test predictor semantics and remain supporting/target evidence only.

## W. HCP-vs-FCC TWIP semantics

- Both direct P023 TWIP positives are explicitly HCP_EPSILON twinning.
- This task preserves source truth without globally redefining TWIP target semantics; later schema/QC refresh must retain the phase tag.

## X. Thermo-Calc context

- Thermo-Calc with database TCHEA2 is retained as current-paper thermodynamic/model context only.
- Equilibrium phase-stability predictions are not measured phase fractions and do not override EBSD/XRD observations.

## Y. SFE gap

- No current-paper alloy-specific numeric SFE is reported. SFE_mJ_m2 remains NA and no cited Fe-Mn-Si/HEA value was imported.

## Z. DeltaG gap

- No current-paper numeric FCC->HCP DeltaG is reported. DeltaG_FCC_HCP_J_mol remains NA; no value was calculated or transferred.

## AA. Before/after usable target counts

- Usable TRIP/TWIP/joint counts: 35/34/28 before -> 37/36/30 after.
- TRIP positive/negative: 31/4 -> 33/4; TWIP positive/negative: 29/5 -> 31/5.
- Joint states before: 00=0, 10=5, 01=4, 11=19; after: 00=0, 10=5, 01=4, 11=21.
- Programmatic deltas are +7 independent, +2 usable TRIP, +2 usable TWIP, and +2 usable joint.

## AB. Remaining P023 gaps

- Quantitative measured bulk chemistry; physical-batch and individual-replicate identities/results; exact numeric room temperature; annealed numeric grain sizes; digitized matrix-Al values; exact mechanics for D-pass/650-5/850-5/850-15/850-30; direct condition-specific target evidence for the five unresolved conditions; numeric SFE; and DeltaG remain unresolved.

## AC. Later global refresh requirement

- Yes: Global QC, feature coverage/schema statistics, and grouped split artifacts require a non-destructive refresh after paper collection pauses and before matrix construction.
- They were intentionally not refreshed in this recovery-only task. No ML matrix, model, feature engineering, imputation, normalization, descriptor calculation, curve digitization, resampling, or synthetic record was created.
