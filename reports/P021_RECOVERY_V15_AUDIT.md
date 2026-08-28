# P021 recovery v15 audit

## A. Source identity

- Paper_ID=P021; DOI 10.1016/j.jallcom.2021.162765.
- Title: Enhancement in mechanical properties through an FCC-to-HCP phase transformation in an Fe-17.5Mn-10Co-12.5Cr-5Ni-5Si (in at%) medium-entropy alloy.
- Journal of Alloys and Compounds, volume 898, article 162765 (2022); Data_Origin=EXPERIMENTAL.
- The workbook identity is VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH. The workbook and recovery-v14 base are SHA-256 gated; integration rejects a DOI or identity mismatch.

## B. New-source/duplicate check

- The recovery-v14 DOI search returned 0 matching rows and no P021 Paper_ID. P021 is therefore appended as a new source beyond P020.
- No mapping was made by row order. If a DOI representation appears in a changed base, the generator stops for explicit replacement-aware review.

## C. V15 total rows

- V15 contains 219 rows: all 214 recovery-v14 rows are preserved in their original order and source columns, followed by five P021 rows.

## D. Independent experimental count before/after

- Replacement-aware independent experimental conditions: 52 before -> 57 after.

## E. Exact P021 condition count

- Exactly five exact primary conditions exist: P021_MC_A900_5M_RT_G10, P021_MC_A900_25M_RT_G19, P021_MC_A1000_20M_RT_G41, P021_MC_A1000_150M_RT_G150, P021_MC_A1000_20M_77K_G41.
- Each is one independent condition-level record. Replicate_n=3 records the reported minimum of at least three specimens; no replicate or post-test child rows were created.

## F. Four RT grain-size conditions

- Four 298 K / 25 C conditions retain grain sizes 10.0, 19.5, 40.9, and 149.6 um with their exact annealing schedules and 1e-3 s^-1 rate.

## G. Cryogenic condition

- P021_MC_A1000_20M_77K_G41 reuses the 1000 C / 20 min, 40.9 um annealed state and is tested at 77 K in a liquid-nitrogen atmosphere at 1e-3 s^-1.

## H. Nominal chemistry / measured chemistry gap

- Nominal composition is Fe50Mn17.5Cr12.5Co10Ni5Si5 at.%.
- Quantitative post-melt bulk chemistry remains NA. EDS/BSE evidence is stored only as qualitative homogenization and never converted into bulk composition.

## I. Common processing

- Source processing retains >99.9% raw-material purity; vacuum arc melting under Ar; at least five flips/remelts; approximately 150 g alloy; 65 x 40 x 10 mm remolded ingot; 1150 C/24 h homogenization; 1100 C hot rolling to 3 mm; 30% cold rolling; condition-specific final annealing; water quench; longitudinal ASTM E8/E8M sub-size tensile specimens.

## J. Fully recrystallized single-FCC initial states

- All five conditions are fully recrystallized and single FCC before tensile loading. Initial_HCP_fraction=0 and Initial_Alpha_BCT_fraction=0.
- Exact numeric Initial_FCC_fraction remains NA; no FCC=1.0 complement is fabricated. No obvious precipitates/secondary phases are reported.

## K. Annealing-twin safeguard

- All five retain abundant pre-test annealing twins with ANNEALING_TWINS_DO_NOT_GENERATE_TENSILE_TWIP. Only direct tensile deformation-twin evidence can establish TWIP.

## L. Grain sizes

- Exact grain sizes are 10.0, 19.5, 40.9, and 149.6 um. The 40.9 um state is used at both 298 K and 77 K. Annealing twin boundaries are excluded from the source grain-size calculation.

## M. Pre-test 77 K stacking faults

- The cryogenic row stores Initial_Stacking_Fault_State=PROFUSE_PRETEST_STACKING_FAULTS and timing BEFORE_TENSILE_LOADING. This pre-test state is neither post-test leakage nor TWIP evidence.

## N. Mechanical values

- A900/5 min RT: 310/769 MPa YS/UTS and 63% elongation.
- A900/25 min RT: 292/736 MPa and 64%.
- A1000/20 min RT: 249/688 MPa and 58%.
- A1000/150 min RT: 228/643 MPa and 59%.
- A1000/20 min 77 K: 540/1410 MPa and 51%.
- Values are exact source-reported averages from at least three specimens and remain MECHANICAL_OUTCOME_LEAKAGE.

## O. RT40 TRIP evidence

- P021_MC_A1000_20M_RT_G41 is Effective_TRIP=1 and Slip=1. Initial HCP=0 is followed by 14.9% epsilon-HCP by post-fracture EBSD plus direct TEM/SAD epsilon-lath evidence, establishing FCC -> HCP epsilon TRIP.

## P. RT40 low-abundance TWIP evidence

- P021_MC_A1000_20M_RT_G41 is Effective_TWIP=1 because the source explicitly reports few mechanical twins in the room-temperature-deformed TEM specimen.
- Abundance is LOW and evidence strength is MEDIUM relative to TRIP. TWIP_Phase=UNRESOLVED_PHASE_DIRECT_MECHANICAL_TWIN_TEXT; occurrence is not dominance and no FCC/HCP twin phase is invented.

## Q. 77 K TRIP evidence

- P021_MC_A1000_20M_77K_G41 is Effective_TRIP=1 and Slip=1 from strong post-deformation XRD, EBSD (56.2% epsilon-HCP), and TEM/SAD evidence of extensive epsilon laths on two non-coplanar systems.

## R. 77 K TWIP=NA decision

- Effective_TWIP remains NA with INSUFFICIENT_FOR_ZERO. Reduced/absent-twin discussion and pre-test stacking faults are not converted into TWIP=0 or TWIP=1.

## S. Post-fracture HCP fractions

- RT40=0.149 and 77K40=0.562. Both are POST_TEST_TARGET_EVIDENCE and explicitly scoped to indexed EBSD regions, excluding non-indexed regions.
- The 10.0, 19.5, and 149.6 um conditions remain NA; no phase fraction is extrapolated.

## T. Alpha-BCT pathway status

- Alpha_BCT_Transformation_Status=NOT_DETECTED only for the directly characterized RT40 and 77K40 tensile states.
- This is separate from FCC -> HCP TRIP and does not change either positive TRIP label.

## U. SFE inferred-bound handling

- Numeric SFE remains NA for every P021 condition. The raw <23 mJ/m2 statement is preserved only as AUTHOR_INFERRED_UPPER_BOUND_NOT_DIRECT_MEASUREMENT and NOT_SAFE_AS_DIRECT_NUMERIC_SFE.
- The 77 K discussion is qualitative further reduction only; no cryogenic numeric SFE is created.

## V. DeltaG gap

- No current-paper numerical alloy-specific DeltaG FCC -> HCP is reported. DeltaG and method remain NA; no calculation or cross-paper import occurs.

## W. Hall-Petch leakage handling

- Current-paper sigma0=198 MPa and k=368 MPa um^0.5 are preserved in the support table as CURRENT_PAPER_FIT_FROM_TENSILE_YIELD_RESPONSE and MODEL_DERIVED_LEAKAGE.
- They are not stored as safe pre-deformation predictors.

## X. Before/after usable target counts

- Usable TRIP/TWIP/joint counts: 32/30/27 before -> 34/31/28 after.
- TRIP positive/negative: 28/4 -> 30/4.
- TWIP positive/negative: 25/5 -> 26/5.
- Joint states before: 00=0, 10=5, 01=4, 11=18; after: 00=0, 10=5, 01=4, 11=19.
- Programmatic deltas are +5 independent, +2 usable TRIP, +1 usable TWIP, and +1 usable joint.

## Y. Remaining P021 gaps

- Quantitative post-melt bulk chemistry, physical-batch and individual-replicate identities/results, exact numeric initial FCC fractions, direct condition-specific post-test mechanism evidence for the 10.0/19.5/149.6 um RT states, condition-wide 77 K TWIP evidence, direct numeric SFE at either temperature, and alloy-specific DeltaG remain unresolved.

## Z. Later global refresh requirement

- Global QC, feature coverage/schema statistics, and grouped split artifacts remain intentionally unrefreshed while paper collection continues. They require a later non-destructive refresh after collection pauses.
- No ML matrix, model, feature engineering, imputation, normalization, composition reconciliation, alloy descriptor, digitized figure, resampling, synthetic record, or performance metric was created.
