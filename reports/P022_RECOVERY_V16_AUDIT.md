# P022 recovery v16 audit

## A. Source identity

- Paper_ID=P022; DOI=10.1007/s10853-019-04064-9.
- Title: Excellent room temperature ductility of as-cast TRIP high-entropy alloy via Mo and C alloying.
- Journal of Materials Science, volume 55, issue 5, pages 2239-2244 (2020); Data_Origin=EXPERIMENTAL.
- The verified workbook identity matches the DOI and bibliographic record. Both workbook and recovery-v15 base are SHA-256 gated; integration rejects a mismatch.

## B. New-source/duplicate status

- Exact recovery-v15 DOI matches: 0. No P022 Paper_ID was present, so P022 is appended as a new source beyond P021.
- No composition-text or row-order mapping was used. A changed base containing this DOI causes the generator to stop for replacement-aware review.

## C. V16 row count

- V16 contains 227 rows: the complete 219-row recovery-v15 prefix plus five primary conditions and three correlated stage children.

## D. Independent experimental count before/after

- Replacement-aware independent experimental conditions: 57 before -> 62 after.
- The three 40%-strain observations are non-independent and do not affect this count.

## E. Five exact P022 conditions

- Exactly five primary conditions exist: P022_MC_C0_ASCAST_RT, P022_MC_C2_ASCAST_RT, P022_MC_C4_ASCAST_RT, P022_MC_C2MO1_ASCAST_RT, P022_MC_C2MO2_ASCAST_RT.
- Each is one independent as-cast tensile condition. Physical batch, replicate identity, and replicate count remain NA; no pseudo-replicates were created.

## F. Five material parents

- Material parents are P022_MAT_C0, P022_MAT_C2, P022_MAT_C4, P022_MAT_C2MO1, P022_MAT_C2MO2, one for each separately fabricated chemistry variant.
- All share strict leakage group P022_SERIES01; each uses its corresponding material-parent leakage key.

## G. Composition/raw-formula handling

- Exact formulas remain Fe50Mn30Co10Cr10, Fe50Mn30Co10Cr10C2, Fe50Mn30Co10Cr10C4, Fe50Mn30Co10Cr10C2Mo1, Fe50Mn30Co10Cr10C2Mo2.
- Original_Composition_Basis=ATOMIC_RATIO_AS_REPORTED. Quantitative post-melt bulk chemistry remains NA.

## H. No automatic at.% normalization

- No formula was normalized to 100 at.%, no normalized elemental concentrations were calculated, and all master at.% element fields remain NA.
- The C and Mo addition terms are retained only in dedicated atomic-ratio fields, not as normalized concentrations.

## I. Room-temperature/test-rate missingness

- Test_T_Raw remains room temperature for all five conditions. Exact Test_T_K and Test_T_C remain NA.
- Tensile strain rate remains NA/NOT_REPORTED. The source dimensions 22 x 2.5 x 1.5 mm are retained without promotion to gauge fields.

## J. Initial C0 FCC+HCP state

- C0 retains initial FCC+HCP with exact FCC and HCP fractions NA.
- Pre-existing as-cast HCP does not generate the C0 TRIP label; the label comes from author condition attribution.

## K. Single-FCC C2/C4/C2Mo1/C2Mo2 states

- C2, C4, C2Mo1, and C2Mo2 retain XRD single-FCC or single-FCC-matrix states with Initial_HCP_fraction=0.
- Exact numeric FCC fractions remain NA; no FCC=1 complement was fabricated.

## L. C4 carbide evidence

- C4 retains CARBIDES_IN_INTERDENDRITIC_REGION_DIRECT_SEM despite the XRD single-FCC-matrix description.
- The XRD matrix result is not treated as proof that carbides are absent.

## M. Morphology differences

- C0 retains a typical as-cast dendritic microstructure; C2 equiaxed/columnar dendrites; C4 dendritic/interdendritic carbide morphology; C2Mo1 more uniform and finer equiaxed dendrites; and C2Mo2 non-equiaxed/striped dendrites.
- No numeric grain size was digitized. Possible sigma precipitation discussed from prior work was not promoted to current-paper phase evidence.

## N. Direct 40%-strain TWIP evidence

- Exactly three correlated EBSD/IPF + misorientation observations exist at Local_Strain_pct=40.
- Each directly records approximately 60-degree <111> deformation-twin boundaries and TWIP_Stage=1. No twin-boundary fraction was digitized.

## O. C2/C2Mo1/C2Mo2 TWIP labels

- C2, C2Mo1, and C2Mo2 are Effective_TWIP=1 from direct 40%-strain EBSD evidence.
- C2Mo1 has the largest qualitative twin population; C2 and C2Mo2 are lower. TRIP remains NA for all three.

## P. C0 author-attributed TRIP evidence grade

- C0 is Effective_TRIP=1 with MEDIUM author-attributed evidence: the current paper explicitly treats C0 as its TRIP reference and contrasts alloyed TWIP response with the TRIP effect in C0.
- This is not graded as direct current-paper post-test phase mapping. C0 TWIP remains NA.

## Q. C4 unresolved target state

- C4 Effective_TRIP, Effective_TWIP, and Slip remain NA with INSUFFICIENT_FOR_ZERO.

## R. Negative-label safeguards

- P022 creates no new TRIP=0 or TWIP=0 labels.
- TRIP-to-TWIP wording, TWIP dominance, missing microscopy, and pre-existing HCP are never converted into strong mechanism negatives or positives outside their supported scope.

## S. Mechanical-property recovery

- C2 retains approximate direct-text UTS about 600 MPa and total elongation about 67.4%.
- C2Mo1 retains approximate direct-text UTS about 658 MPa and total elongation about 89.8%.
- YS and all C0/C4/C2Mo2 exact numeric mechanics remain NA. Figure 3 was not digitized, and the C2Mo2 elongation decrease was not converted into a final value. All recovered mechanics are MECHANICAL_OUTCOME_LEAKAGE.

## T. SFE gap

- No current-paper alloy-specific numeric SFE is stored for any condition.
- General 15-45 mJ/m2 TWIP and <15 mJ/m2 TRIP thresholds remain secondary support-only safeguards, never condition values. C/Mo effects remain QUALITATIVE_DIRECTION_ONLY.

## U. DeltaG gap

- DeltaG_FCC_HCP remains NA for all five materials. No value was calculated or transferred from another FeMnCoCr paper.

## V. Before/after usable target counts

- Usable TRIP/TWIP/joint counts: 34/31/28 before -> 35/34/28 after.
- TRIP positive/negative: 30/4 -> 31/4.
- TWIP positive/negative: 26/5 -> 29/5.
- Joint states before: 00=0, 10=5, 01=4, 11=19; after: 00=0, 10=5, 01=4, 11=19.
- Programmatically calculated deltas are +5 independent, +1 usable TRIP, +3 usable TWIP, and +0 usable joint.

## W. Remaining P022 gaps

- Quantitative post-melt bulk chemistry; physical-batch, replicate identity/count, and individual results; exact numeric test temperature and strain rate; exact FCC fractions; numeric grain sizes; C0 direct post-test phase evolution; C4 mechanism evidence; condition-wide TRIP evidence for C2/C2Mo1/C2Mo2; all condition-specific twin fractions; numeric alloy-specific SFE; and DeltaG remain unresolved.

## X. Later global refresh requirement

- Global QC, feature coverage/schema statistics, and grouped split artifacts remain intentionally unrefreshed during the active paper-collection batch.
- They require a non-destructive refresh after collection pauses and before any matrix construction. No ML matrix, model, feature engineering, imputation, normalization, descriptor calculation, figure digitization, resampling, or synthetic record was created.
