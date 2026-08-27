# Feature Schema V1 Audit

Prediction moment: **immediately before tensile loading begins**. This is schema design and descriptive coverage only; no training, transformation, imputation, normalization, encoding, or derived-alloy calculation occurred.

## A. Total master columns classified

343 of 343 V12 master columns; no omissions or duplicates.

## B. Count by eligibility class

- `PREDICTOR_SAFE_DIRECT`: 48
- `PREDICTOR_SAFE_CONDITIONAL`: 57
- `METADATA_ONLY`: 10
- `GROUPING_ONLY`: 14
- `TARGET_ONLY`: 18
- `POST_TEST_LEAKAGE`: 30
- `MECHANICAL_OUTCOME_LEAKAGE`: 25
- `MODEL_DERIVED_LEAKAGE`: 9
- `COMPUTATIONAL_ONLY`: 19
- `PROVENANCE_ONLY`: 104
- `IDENTIFIER_ONLY`: 9
- `UNRESOLVED_REVIEW`: 0

## C. Safe direct predictors

48.

## D. Safe conditional predictors

57.

## E. Leakage fields

64, defined as POST_TEST_LEAKAGE + MECHANICAL_OUTCOME_LEAKAGE + MODEL_DERIVED_LEAKAGE. Target-only fields are separately blocked and are not double-counted here.

## F. Computational-only fields

19.

## G. Grouping/identifier fields

23 (14 grouping-only + 9 identifier-only).

## H. Provenance-only fields

104 provenance-only; 114 when metadata-only is included.

## I. Chemistry candidates

`Original_Composition`, `Composition_basis`, `Fe_at%`, `Mn_at%`, `Co_at%`, `Cr_at%`, `Ni_at%`, `N_at%`, `C_at%`, `Mo_at%`, `Si_at%`, `Ti_at%`, `V_at%`, `Other_elements`, `Recovered_Bulk_Composition_at_pct`, `APT_local_composition`, `EDS_local_composition`, `Nominal_Composition_at_pct`, `Cr_at%_uncertainty`, `Mn_at%_uncertainty`, `Fe_at%_uncertainty`, `Co_at%_uncertainty`, `Ni_at%_uncertainty`, `Feedstock_Composition_at_pct`, `Local_EDS_Composition_at_pct`, `Measured_Composition_at_pct`

Measured bulk, nominal, feedstock, and local representations remain separate. The measured-first/nominal-fallback policy is documented but not applied.

## J. Processing candidates

`Processing_route`, `Cast_method`, `Homogenization_T_K`, `Homogenization_time_h`, `Hot_rolling_T_K`, `Hot_rolling_reduction_pct`, `Cold_rolling_reduction_pct`, `Annealing_T_K`, `Annealing_time_min`, `Cooling_route`, `P008_Source_State`, `Recovered_Processing_route`, `Sintering_T_C`, `SPS_Pressure_MPa`, `SPS_Time_min`, `SPS_Vacuum_Pa`, `Cold_Roll_Pass_Reduction_mm`, `Remelting_n`, `Raw_Material_Purity`

## K. Test-condition candidates

`Test_T_K`, `Strain_rate_s-1`, `Recovered_Test_T_Reported`, `Loading_Direction`, `Test_T_Raw`

No dedicated usable loading-mode column exists; loading direction is sparse. Specimen dimensions remain metadata-only.

## L. Initial-microstructure candidates

`Grain_size_um`, `Grain_size_SD_um`, `Initial_FCC_fraction`, `Initial_HCP_fraction`, `Initial_twin_boundary_status`, `Recovered_Grain_size_um`, `Recovered_Initial_FCC_fraction`, `Recovered_Initial_HCP_fraction`, `Recovered_Recrystallized_fraction`, `Initial_BCC_alpha_martensite_fraction`, `Alpha_lath_thickness`, `Alpha_lath_spacing`, `Recovery_twin_fraction`, `Recovery_twin_thickness`, `Recovery_twin_spacing_observed`, `Recovery_twin_spacing_fraction_input_nm`, `Precipitate_type`, `Initial_Phase_State_Qualitative`, `Relative_Density_pct`, `Effective_Grain_Size_Including_TB_PhaseBoundary_um`, `Initial_Sigma3_TB_fraction`, `Initial_Twin_Type`, `Mn_Oxide_Area_Fraction`, `Detwinning`, `KAM_mean_deg`, `Grain_Size_Including_TB_as_HAB_um`, `Initial_MnO_fraction`, `HCP_Morphology`, `Initial_HCP_Origin`, `Recrystallized_fraction`, `Processing_TRIP`, `Processing_TWIP`, `Initial_Twin_Origin`, `Texture_Orientation_Status`, `Elemental_Segregation_Status`

All are constrained to explicitly pre-test state; initial twins/HCP never establish TWIP/TRIP.

## M. Physics candidates

`SFE_mJ_m2`, `SFE_error_mJ_m2`, `DeltaG_FCC_HCP_J_mol`, `Elastic_modulus_GPa`, `Shear_modulus_GPa`, `Poisson_ratio`, `Lattice_parameter_nm`, `CSRO_present`, `Recovered_ISFE_DFT_0K_mJ_m2`, `Recovered_DeltaG_FCC_HCP_300K_J_mol`, `SFE_value_alloy_level_mJ_m2`, `Magnetic_transition_T_K`, `Low_T_Magnetic_Behavior`, `Low_T_Magnetic_Behavior_T_K`, `FCC_lattice_a_XRD_A`, `HCP_lattice_a_XRD_A`, `HCP_lattice_c_XRD_A`, `Initial_FCC_lattice_a_A`, `Initial_HCP_c_over_a`, `Initial_HCP_c_over_a_uncertainty`

All method-sensitive physics candidates preserve temperature, structure, method, and domain distinctions. P017 GSFE is computational-only and is not a 343-column experimental candidate.

## N. Highest-risk leakage variables

`True_strain`, `Local_strain`, `Deformation_stage`, `TRIP`, `TWIP`, `Slip`, `Stacking_faulting`, `HCP_to_FCC_reversion`, `Dominant_mechanism`, `HCP_fraction_at_condition`, `Twin_fraction_or_Sigma3`, `Twin_thickness_nm`, `HCP_lath_or_lamella_note`, `YS_MPa`, `YS_error_MPa`, `UTS_MPa`, `UTS_error_MPa`, `Elongation_pct`, `Elongation_error_pct`, `Uniform_elongation_pct`, `Critical_twin_stress_MPa`, `Critical_TRIP_stress_MPa`, `Twin_onset_true_strain`, `TRIP_onset_true_strain`, `Adiabatic_temperature_K`, `SFE_increase_dynamic_mJ_m2`, `Evidence_TRIP`, `Evidence_TWIP`, `Recovered_YS_MPa`, `Recovered_UTS_MPa`, `Recovered_Elongation_pct`, `Recovered_Uniform_elongation_pct`, `Recovered_TRIP`, `Recovered_TWIP`, `Target_Correction_TRIP`, `Target_Correction_TWIP`, `Effective_TRIP`, `Effective_TWIP`, `YS_mean`, `YS_uncertainty`, `UTS_mean`, `UTS_uncertainty`, `TE_mean`, `TE_uncertainty`, `UE_mean`, `UE_uncertainty`, `Deformation_twin_width`, `Deformation_twin_spacing`, `HCP_lath_thickness_nm`, `Deformation_Twin_thickness_nm`, `P011_Negative_TWIP_Evidence`, `Original_TRIP`, `Original_TWIP`, `GND_density_m-2`, `Martensite_lath_thickness`, `Martensite_interspace_nm`, `Observed_Microstructure`, `Approx_Stress_MPa`, `HCP_fraction_status`, `Nearest_SXRD_TRIP_Onset_Stress_MPa`, `Tensile_TWIP_Onset_Stress_MPa`, `Compression_Twinning_Onset_Stress_MPa`, `Final_InSitu_True_Stress_Approx_MPa`, `Final_InSitu_Engineering_Strain_Approx_pct`, `Mechanism_Phase_Scope`, `Tensile_Strain_pct`, `FCC_fraction_at_stage`, `TWIP_at_stage`, `TRIP_at_stage`, `Slip_at_stage`, `HDI_at_stage`, `HDI_Hardening`, `Engineering_YS_MPa`, `Engineering_UTS_MPa`, `Engineering_Elongation_pct`, `True_Yield_Stress_MPa`, `True_UTS_MPa`, `HC`, `Postfracture_Phase_State`, `Postfracture_HCP_fraction`, `Postfracture_HCP_fraction_Status`, `Fracture_Mode`

These include direct targets/evidence in addition to the 64 post-test, mechanical-outcome, and model-derived fields.

### O. M1_CHEMISTRY coverage

Candidates: 26; CORE_V1 raw complete cases: 40/51; median/min/max raw candidate coverage: 9.80%/0.00%/82.35%. Bottleneck: Other_elements=0/51; N_at%=1/51; APT_local_composition=1/51; EDS_local_composition=1/51.
### P. M2_CHEMISTRY_PLUS_TEST coverage

Candidates: 31; CORE_V1 raw complete cases: 31/51; median/min/max raw candidate coverage: 11.76%/0.00%/92.16%. Bottleneck: Other_elements=0/51; N_at%=1/51; APT_local_composition=1/51; EDS_local_composition=1/51.
### Q. M3_PLUS_PROCESSING coverage

Candidates: 50; CORE_V1 raw complete cases: 31/51; median/min/max raw candidate coverage: 12.75%/0.00%/92.16%. Bottleneck: Other_elements=0/51; N_at%=1/51; APT_local_composition=1/51; EDS_local_composition=1/51.
### R. M4_PLUS_PHYSICS coverage

Candidates: 70; CORE_V1 raw complete cases: 31/51; median/min/max raw candidate coverage: 9.80%/0.00%/92.16%. Bottleneck: Other_elements=0/51; SFE_error_mJ_m2=0/51; Recovered_ISFE_DFT_0K_mJ_m2=0/51; Recovered_DeltaG_FCC_HCP_300K_J_mol=0/51.
### S. M5_PLUS_INITIAL_MICROSTRUCTURE coverage

Candidates: 105; CORE_V1 raw complete cases: 26/51; median/min/max raw candidate coverage: 9.80%/0.00%/92.16%. Bottleneck: Other_elements=0/51; SFE_error_mJ_m2=0/51; Recovered_ISFE_DFT_0K_mJ_m2=0/51; Recovered_DeltaG_FCC_HCP_300K_J_mol=0/51.

## T. Target-specific feature availability

- TRIP: usable 32, positive 27, negative 5; CORE_V1 complete cases by set: M1_CHEMISTRY=24, M2_CHEMISTRY_PLUS_TEST=19, M3_PLUS_PROCESSING=19, M4_PLUS_PHYSICS=19, M5_PLUS_INITIAL_MICROSTRUCTURE=16.
- TWIP: usable 30, positive 24, negative 6; CORE_V1 complete cases by set: M1_CHEMISTRY=25, M2_CHEMISTRY_PLUS_TEST=20, M3_PLUS_PROCESSING=20, M4_PLUS_PHYSICS=20, M5_PLUS_INITIAL_MICROSTRUCTURE=17.
- JOINT: usable 27, positive 26, negative 1; CORE_V1 complete cases by set: M1_CHEMISTRY=22, M2_CHEMISTRY_PLUS_TEST=17, M3_PLUS_PROCESSING=17, M4_PLUS_PHYSICS=17, M5_PLUS_INITIAL_MICROSTRUCTURE=14.

The joint positive definition is any of 10/01/11; the sole joint negative is 00. Complete cases are descriptive CORE_V1 raw-column intersections only.

## U. Unresolved schema fields

0. None. Conservative metadata/leakage/domain decisions block ambiguous non-candidates rather than leaving them silently eligible.

## V. Exact recommendation before ML

Proceed only to grouped train/validation split design, using M2_CHEMISTRY_PLUS_TEST as the initial schema baseline and all paper/study/material identifiers solely as grouping controls. First predeclare measured-bulk-versus-nominal representation and target-specific group allocation; keep M4 physics and sparse M5 details for later ablation. Do not construct a training matrix, train, impute, encode, normalize, synthesize, or calculate derived descriptors in this phase.
