"""Freeze Feature Schema V1 and the pre-deformation leakage policy.

This is schema/audit generation only.  It reads the immutable V12 QC master and
condition indexes, classifies the existing 343 columns, and writes manifests and
descriptive coverage reports.  It never writes a scientific dataset, fills a
missing value, transforms a feature, or trains a model.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = ROOT / "data/processed/master_19papers_recovery_v12_qc.csv"
EXPERIMENTAL_INDEX_PATH = ROOT / "data/processed/experimental_condition_index_v12.csv"
COMPUTATIONAL_INDEX_PATH = ROOT / "data/processed/computational_condition_index_v12.csv"
SCHEMA_DIR = ROOT / "data/schema"
REPORTS_DIR = ROOT / "reports"

SCHEMA_PATH = SCHEMA_DIR / "feature_schema_v1.csv"
FEATURE_SETS_PATH = SCHEMA_DIR / "feature_sets_v1.csv"
PRIORITY_PATH = SCHEMA_DIR / "feature_priority_v1.csv"
DOMAIN_PATH = SCHEMA_DIR / "domain_manifest_v1.csv"
COVERAGE_PATH = REPORTS_DIR / "FEATURE_SET_COVERAGE_V1.csv"
TARGET_AVAILABILITY_PATH = REPORTS_DIR / "TARGET_FEATURE_AVAILABILITY_V1.csv"
POLICY_PATH = REPORTS_DIR / "PREDICTION_TIME_LEAKAGE_POLICY_V1.md"
AUDIT_PATH = REPORTS_DIR / "FEATURE_SCHEMA_V1_AUDIT.md"

PREDICTION_MOMENT = "Immediately before tensile loading begins"

ELIGIBILITY_CLASSES = (
    "PREDICTOR_SAFE_DIRECT",
    "PREDICTOR_SAFE_CONDITIONAL",
    "METADATA_ONLY",
    "GROUPING_ONLY",
    "TARGET_ONLY",
    "POST_TEST_LEAKAGE",
    "MECHANICAL_OUTCOME_LEAKAGE",
    "MODEL_DERIVED_LEAKAGE",
    "COMPUTATIONAL_ONLY",
    "PROVENANCE_ONLY",
    "IDENTIFIER_ONLY",
    "UNRESOLVED_REVIEW",
)

SCIENTIFIC_FAMILIES = (
    "CHEMISTRY",
    "PROCESSING",
    "TEST_CONDITIONS",
    "INITIAL_MICROSTRUCTURE",
    "PHYSICS_THERMODYNAMICS",
    "IDENTITY_GROUPING",
    "TARGET",
    "MECHANICAL_RESPONSE",
    "POST_DEFORMATION_MICROSTRUCTURE",
    "MODEL_DERIVED_RESPONSE",
    "COMPUTATIONAL_ONLY",
    "PROVENANCE_QC",
    "OTHER",
)

SCHEMA_COLUMNS = [
    "Column_Name",
    "Data_Type",
    "Scientific_Family",
    "Prediction_Time_Class",
    "Proposed_Model_Role",
    "Experimental_Domain_Eligibility",
    "Computational_Domain_Eligibility",
    "Known_Before_Deformation",
    "Direct_Source_or_Derived",
    "Method_Sensitive",
    "Temperature_Sensitive",
    "Phase_Sensitive",
    "Potential_Leakage",
    "Leakage_Reason",
    "Missingness_Concern",
    "Scope_Constraint",
    "Recommended_V1_Action",
    "Notes",
]


def names(value: str) -> set[str]:
    """Make exact column-name sets readable without weakening header checks."""
    return set(value.split())


CLASS_COLUMNS = {
    "PREDICTOR_SAFE_DIRECT": names(
        """
        Fe_at% Mn_at% Co_at% Cr_at% Ni_at% N_at% C_at% Mo_at% Si_at% Ti_at% V_at%
        Processing_route Cast_method Homogenization_T_K Homogenization_time_h Hot_rolling_T_K
        Hot_rolling_reduction_pct Cold_rolling_reduction_pct Annealing_T_K Annealing_time_min
        Cooling_route Test_T_K Strain_rate_s-1 Grain_size_um Initial_FCC_fraction
        Initial_HCP_fraction Recovered_Grain_size_um Recovered_Initial_FCC_fraction
        Recovered_Initial_HCP_fraction Recovered_Recrystallized_fraction
        Recovered_Bulk_Composition_at_pct Recovered_Processing_route Nominal_Composition_at_pct
        Sintering_T_C Relative_Density_pct Effective_Grain_Size_Including_TB_PhaseBoundary_um
        Initial_Sigma3_TB_fraction Mn_Oxide_Area_Fraction SPS_Pressure_MPa SPS_Time_min SPS_Vacuum_Pa
        Measured_Composition_at_pct Grain_Size_Including_TB_as_HAB_um Loading_Direction
        Initial_MnO_fraction Cold_Roll_Pass_Reduction_mm Remelting_n Recrystallized_fraction
        """
    ),
    "PREDICTOR_SAFE_CONDITIONAL": names(
        """
        Original_Composition Composition_basis Other_elements Grain_size_SD_um
        Initial_twin_boundary_status SFE_mJ_m2 SFE_error_mJ_m2 DeltaG_FCC_HCP_J_mol
        Elastic_modulus_GPa Shear_modulus_GPa Poisson_ratio Lattice_parameter_nm CSRO_present
        Recovered_ISFE_DFT_0K_mJ_m2 Recovered_DeltaG_FCC_HCP_300K_J_mol
        P008_Source_State Recovered_Test_T_Reported Initial_BCC_alpha_martensite_fraction
        SFE_value_alloy_level_mJ_m2 Alpha_lath_thickness Alpha_lath_spacing
        Recovery_twin_fraction Recovery_twin_thickness Recovery_twin_spacing_observed
        Recovery_twin_spacing_fraction_input_nm Precipitate_type APT_local_composition
        EDS_local_composition Cr_at%_uncertainty Mn_at%_uncertainty Fe_at%_uncertainty
        Co_at%_uncertainty Ni_at%_uncertainty Initial_Phase_State_Qualitative
        Initial_Twin_Type
        Magnetic_transition_T_K Low_T_Magnetic_Behavior Low_T_Magnetic_Behavior_T_K
        Detwinning Feedstock_Composition_at_pct Local_EDS_Composition_at_pct
        FCC_lattice_a_XRD_A HCP_lattice_a_XRD_A HCP_lattice_c_XRD_A KAM_mean_deg
        Test_T_Raw HCP_Morphology Initial_HCP_Origin Initial_FCC_lattice_a_A
        Initial_HCP_c_over_a Initial_HCP_c_over_a_uncertainty Processing_TRIP Processing_TWIP
        Initial_Twin_Origin Raw_Material_Purity Texture_Orientation_Status
        Elemental_Segregation_Status
        """
    ),
    "METADATA_ONLY": names(
        """
        Paper_Title Row_Type Gauge_length_mm Gauge_width_mm Specimen_thickness_mm
        Atomic_size_misfit_pct Image_usable_for_descriptors
        Recovered_SFE_assumed_for_calculation_mJ_m2 Gauge_Cross_Section_mm
        Mn_Charge_Adjustment
        """
    ),
    "GROUPING_ONLY": names(
        """
        Experiment_Group_ID Original_Experiment_Group_ID Parent_Experiment_ID Study_Series_ID
        Material_Parent_ID Physical_Batch_ID Replicate_ID Leakage_Group_Strict
        Leakage_Group_Material Parent_ML_Condition_ID Replicate_n Independent_ML_sample
        Source_Material_ID Independent_Experimental_ML_sample
        """
    ),
    "TARGET_ONLY": names(
        """
        TRIP TWIP Slip Stacking_faulting HCP_to_FCC_reversion Dominant_mechanism
        Evidence_TRIP Evidence_TWIP Recovered_TRIP Recovered_TWIP Target_Correction_TRIP
        Target_Correction_TWIP Effective_TRIP Effective_TWIP P011_Negative_TWIP_Evidence
        Original_TRIP Original_TWIP Mechanism_Phase_Scope
        """
    ),
    "POST_TEST_LEAKAGE": names(
        """
        True_strain Local_strain Deformation_stage HCP_fraction_at_condition
        Twin_fraction_or_Sigma3 Twin_thickness_nm HCP_lath_or_lamella_note
        Deformation_twin_width Deformation_twin_spacing HCP_lath_thickness_nm
        Deformation_Twin_thickness_nm GND_density_m-2 Martensite_lath_thickness
        Martensite_interspace_nm Observed_Microstructure Approx_Stress_MPa HCP_fraction_status
        Nearest_SXRD_TRIP_Onset_Stress_MPa Tensile_TWIP_Onset_Stress_MPa
        Compression_Twinning_Onset_Stress_MPa Final_InSitu_True_Stress_Approx_MPa
        Final_InSitu_Engineering_Strain_Approx_pct Tensile_Strain_pct FCC_fraction_at_stage
        TWIP_at_stage TRIP_at_stage Slip_at_stage Postfracture_Phase_State
        Postfracture_HCP_fraction Postfracture_HCP_fraction_Status
        """
    ),
    "MECHANICAL_OUTCOME_LEAKAGE": names(
        """
        YS_MPa YS_error_MPa UTS_MPa UTS_error_MPa Elongation_pct Elongation_error_pct
        Uniform_elongation_pct Recovered_YS_MPa Recovered_UTS_MPa Recovered_Elongation_pct
        Recovered_Uniform_elongation_pct YS_mean YS_uncertainty UTS_mean UTS_uncertainty
        TE_mean TE_uncertainty UE_mean UE_uncertainty Engineering_YS_MPa Engineering_UTS_MPa
        Engineering_Elongation_pct True_Yield_Stress_MPa True_UTS_MPa Fracture_Mode
        """
    ),
    "MODEL_DERIVED_LEAKAGE": names(
        """
        Critical_twin_stress_MPa Critical_TRIP_stress_MPa Twin_onset_true_strain
        TRIP_onset_true_strain Adiabatic_temperature_K SFE_increase_dynamic_mJ_m2
        HDI_at_stage HDI_Hardening HC
        """
    ),
    "COMPUTATIONAL_ONLY": names(
        """
        Computational_Magnetic_States PM_Model AFM_Model Computational_SFE_Scope
        SFE_Relative_Trend Finite_T_SFE_Excitations_Status Independent_Computational_Condition
        Paper_Native_TRIP Paper_Native_TWIP TWIP_induced_TRIP_Status TWIP_induced_TRIP_Timing
        TRIP_induced_TWIP_Status TRIP_induced_TWIP_Timing SIS_PSR_GPa UTS_PSR_GPa
        UTS_PSR_Status Initial_BCC_fraction_raw Initial_BCC_fraction_status
        PostQuench_Initial_Structure
        """
    ),
    "PROVENANCE_ONLY": names(
        """
        SFE_method DeltaG_method Characterization_methods Source_location Label_confidence Notes
        Unmapped_Fields Source_File Source_Sheet Schema_Mapping_Review QC_Status
        Requires_Manual_Review Row_Role Target_Review_Status Schema_Review_Status Data_Origin
        Observation_Role Grouping_Review_Required Grouping_Confidence Grouping_Reason
        Recovery_Provenance_JSON Resolution_Provenance_JSON Parent_Linkage_Status
        Aggregate_Property_Status uncertainty_type P008_Record_Role P008_Legacy_Mapping_Status
        Recovered_Composition_Status Recovered_Test_T_Status Recovered_Grain_size_scope
        Recovered_Grain_size_status Recovered_Initial_HCP_status
        Initial_BCC_alpha_martensite_status Recovered_Recrystallized_fraction_status
        Recovered_YS_status Recovered_UTS_status Recovered_Uniform_elongation_status
        SFE_scope SFE_status SFE_source_provenance P008_Recovery_Provenance_JSON
        Measured_Composition_Status Initial_Phase_Status Magnetic_transition_Status P010_Record_Role
        P010_Recovery_Provenance_JSON Feedstock_Composition_Method Feedstock_Composition_Scope
        Local_EDS_Composition_Scope P011_Record_Role P011_Target_Status
        P011_Recovery_Provenance_JSON P012_Record_Role Measured_Composition_Method
        XRD_Replicate_n XRD_Replicate_Scope P012_Target_Status P012_Recovery_Provenance_JSON
        P013_Record_Role P013_Target_Status Composition_Status Surface_Preparation
        Specimen_Cutting SXRD_Mode Beam_Energy_keV Exposure_s Images_per_loading_step
        Beam_Size_um Grain_Size_Scope EBSD_Phase_Fraction_Use_Status Initial_HCP_Status
        P013_Recovery_Provenance_JSON P014_Record_Role P014_Target_Status
        P014_Legacy_Mapping_Status Cold_Roll_Reduction_Status Test_T_Status KAM_Status
        Recrystallized_Status Initial_Twin_Target_Safety P014_Recovery_Provenance_JSON
        P015_Record_Role P015_Target_Status P015_Legacy_Mapping_Status Grain_Size_Status
        True_Property_Status Negative_Evidence_Quality SFE_Value_Status SFE_Data_Origin
        Critical_Stress_Model_Validity P015_Recovery_Provenance_JSON
        Experimental_Target_Eligibility P017_Record_Role P017_Legacy_Mapping_Status
        P017_Recovery_Provenance_JSON QC_Row_Role QC_Experimental_Eligibility
        QC_Computational_Eligibility QC_Target_Eligibility QC_Duplicate_Status
        QC_Leakage_Risk QC_Leakage_Category QC_Source_Completeness QC_Review_Status
        """
    ),
    "IDENTIFIER_ONLY": names(
        """
        Paper_ID DOI Condition_ID Alloy_ID ML_Condition_ID Observation_ID
        Deformation_Stage_ID Processing_State_ID Computational_Condition_ID
        """
    ),
    "UNRESOLVED_REVIEW": set(),
}


SAFE_FAMILY_COLUMNS = {
    "CHEMISTRY": names(
        """
        Original_Composition Composition_basis Fe_at% Mn_at% Co_at% Cr_at% Ni_at% N_at%
        C_at% Mo_at% Si_at% Ti_at% V_at% Other_elements Recovered_Bulk_Composition_at_pct
        Nominal_Composition_at_pct APT_local_composition EDS_local_composition
        Cr_at%_uncertainty Mn_at%_uncertainty Fe_at%_uncertainty Co_at%_uncertainty
        Ni_at%_uncertainty Feedstock_Composition_at_pct Local_EDS_Composition_at_pct
        Measured_Composition_at_pct
        """
    ),
    "PROCESSING": names(
        """
        Processing_route Cast_method Homogenization_T_K Homogenization_time_h Hot_rolling_T_K
        Hot_rolling_reduction_pct Cold_rolling_reduction_pct Annealing_T_K Annealing_time_min
        Cooling_route Recovered_Processing_route P008_Source_State Sintering_T_C
        SPS_Pressure_MPa SPS_Time_min SPS_Vacuum_Pa Detwinning Cold_Roll_Pass_Reduction_mm
        Remelting_n Processing_TRIP Processing_TWIP Raw_Material_Purity
        """
    ),
    "TEST_CONDITIONS": names(
        """
        Test_T_K Strain_rate_s-1 Recovered_Test_T_Reported Loading_Direction Test_T_Raw
        """
    ),
    "INITIAL_MICROSTRUCTURE": names(
        """
        Grain_size_um Grain_size_SD_um Initial_FCC_fraction Initial_HCP_fraction
        Initial_twin_boundary_status Recovered_Grain_size_um Recovered_Initial_FCC_fraction
        Recovered_Initial_HCP_fraction Recovered_Recrystallized_fraction
        Initial_BCC_alpha_martensite_fraction Alpha_lath_thickness Alpha_lath_spacing
        Recovery_twin_fraction Recovery_twin_thickness Recovery_twin_spacing_observed
        Recovery_twin_spacing_fraction_input_nm Precipitate_type Initial_Phase_State_Qualitative
        Relative_Density_pct Effective_Grain_Size_Including_TB_PhaseBoundary_um
        Initial_Sigma3_TB_fraction Initial_Twin_Type Mn_Oxide_Area_Fraction Detwinning
        KAM_mean_deg Grain_Size_Including_TB_as_HAB_um Initial_MnO_fraction HCP_Morphology
        Initial_HCP_Origin Recrystallized_fraction Initial_Twin_Origin
        Texture_Orientation_Status Elemental_Segregation_Status Processing_TRIP Processing_TWIP
        """
    ),
    "PHYSICS_THERMODYNAMICS": names(
        """
        SFE_mJ_m2 SFE_error_mJ_m2 DeltaG_FCC_HCP_J_mol Elastic_modulus_GPa
        Shear_modulus_GPa Poisson_ratio Lattice_parameter_nm CSRO_present
        Recovered_ISFE_DFT_0K_mJ_m2 Recovered_DeltaG_FCC_HCP_300K_J_mol
        SFE_value_alloy_level_mJ_m2 Magnetic_transition_T_K Low_T_Magnetic_Behavior
        Low_T_Magnetic_Behavior_T_K FCC_lattice_a_XRD_A HCP_lattice_a_XRD_A
        HCP_lattice_c_XRD_A Initial_FCC_lattice_a_A Initial_HCP_c_over_a
        Initial_HCP_c_over_a_uncertainty
        """
    ),
}

# A field can be relevant to two scientific concepts (for example detwinning is
# processing plus initial state).  The primary family is frozen here.
PRIMARY_FAMILY_OVERRIDES = {
    "Detwinning": "INITIAL_MICROSTRUCTURE",
    "Processing_TRIP": "INITIAL_MICROSTRUCTURE",
    "Processing_TWIP": "INITIAL_MICROSTRUCTURE",
}

METADATA_FAMILIES = {
    "Paper_Title": "PROVENANCE_QC",
    "Row_Type": "PROVENANCE_QC",
    "Gauge_length_mm": "TEST_CONDITIONS",
    "Gauge_width_mm": "TEST_CONDITIONS",
    "Specimen_thickness_mm": "TEST_CONDITIONS",
    "Gauge_Cross_Section_mm": "TEST_CONDITIONS",
    "Atomic_size_misfit_pct": "PHYSICS_THERMODYNAMICS",
    "Recovered_SFE_assumed_for_calculation_mJ_m2": "PHYSICS_THERMODYNAMICS",
    "Mn_Charge_Adjustment": "PROCESSING",
    "Image_usable_for_descriptors": "PROVENANCE_QC",
}

PROVENANCE_FAMILY_OVERRIDES = {
    "SFE_method": "PHYSICS_THERMODYNAMICS",
    "DeltaG_method": "PHYSICS_THERMODYNAMICS",
    "SFE_scope": "PHYSICS_THERMODYNAMICS",
    "SFE_status": "PHYSICS_THERMODYNAMICS",
    "SFE_source_provenance": "PHYSICS_THERMODYNAMICS",
    "SFE_Value_Status": "PHYSICS_THERMODYNAMICS",
    "SFE_Data_Origin": "PHYSICS_THERMODYNAMICS",
    "Magnetic_transition_Status": "PHYSICS_THERMODYNAMICS",
    "Recovered_Composition_Status": "CHEMISTRY",
    "Measured_Composition_Status": "CHEMISTRY",
    "Measured_Composition_Method": "CHEMISTRY",
    "Feedstock_Composition_Method": "CHEMISTRY",
    "Feedstock_Composition_Scope": "CHEMISTRY",
    "Local_EDS_Composition_Scope": "CHEMISTRY",
    "Composition_Status": "CHEMISTRY",
    "Recovered_Test_T_Status": "TEST_CONDITIONS",
    "Test_T_Status": "TEST_CONDITIONS",
    "Cold_Roll_Reduction_Status": "PROCESSING",
    "Recovered_Grain_size_scope": "INITIAL_MICROSTRUCTURE",
    "Recovered_Grain_size_status": "INITIAL_MICROSTRUCTURE",
    "Recovered_Initial_HCP_status": "INITIAL_MICROSTRUCTURE",
    "Initial_BCC_alpha_martensite_status": "INITIAL_MICROSTRUCTURE",
    "Recovered_Recrystallized_fraction_status": "INITIAL_MICROSTRUCTURE",
    "Grain_Size_Scope": "INITIAL_MICROSTRUCTURE",
    "EBSD_Phase_Fraction_Use_Status": "INITIAL_MICROSTRUCTURE",
    "Initial_HCP_Status": "INITIAL_MICROSTRUCTURE",
    "KAM_Status": "INITIAL_MICROSTRUCTURE",
    "Recrystallized_Status": "INITIAL_MICROSTRUCTURE",
    "Initial_Twin_Target_Safety": "INITIAL_MICROSTRUCTURE",
    "Grain_Size_Status": "INITIAL_MICROSTRUCTURE",
    "P011_Target_Status": "TARGET",
    "P012_Target_Status": "TARGET",
    "P013_Target_Status": "TARGET",
    "P014_Target_Status": "TARGET",
    "P015_Target_Status": "TARGET",
    "Negative_Evidence_Quality": "TARGET",
    "True_Property_Status": "MECHANICAL_RESPONSE",
    "Critical_Stress_Model_Validity": "MODEL_DERIVED_RESPONSE",
}

CORE_V1_COLUMNS = names(
    """
    Fe_at% Mn_at% Co_at% Cr_at% Test_T_K Strain_rate_s-1 Processing_route Grain_size_um
    """
)

FEATURE_SET_ORDER = (
    "M1_CHEMISTRY",
    "M2_CHEMISTRY_PLUS_TEST",
    "M3_PLUS_PROCESSING",
    "M4_PLUS_PHYSICS",
    "M5_PLUS_INITIAL_MICROSTRUCTURE",
)

FEATURE_SET_ADDITION = {
    "M1_CHEMISTRY": "CHEMISTRY",
    "M2_CHEMISTRY_PLUS_TEST": "TEST_CONDITIONS",
    "M3_PLUS_PROCESSING": "PROCESSING",
    "M4_PLUS_PHYSICS": "PHYSICS_THERMODYNAMICS",
    "M5_PLUS_INITIAL_MICROSTRUCTURE": "INITIAL_MICROSTRUCTURE",
}

FEATURE_SET_CONTROLS = {
    "CHEMISTRY": names(
        """
        Recovered_Composition_Status Measured_Composition_Status Measured_Composition_Method
        Feedstock_Composition_Method Feedstock_Composition_Scope Local_EDS_Composition_Scope
        Composition_Status
        """
    ),
    "TEST_CONDITIONS": names("Recovered_Test_T_Status Test_T_Status"),
    "PROCESSING": names("Cold_Roll_Reduction_Status"),
    "PHYSICS_THERMODYNAMICS": names(
        """
        SFE_method DeltaG_method SFE_scope SFE_status SFE_source_provenance
        Magnetic_transition_Status SFE_Value_Status SFE_Data_Origin
        """
    ),
    "INITIAL_MICROSTRUCTURE": names(
        """
        Recovered_Grain_size_scope Recovered_Grain_size_status Recovered_Initial_HCP_status
        Initial_BCC_alpha_martensite_status Recovered_Recrystallized_fraction_status
        Grain_Size_Scope EBSD_Phase_Fraction_Use_Status Initial_HCP_Status KAM_Status
        Recrystallized_Status Initial_Twin_Target_Safety Grain_Size_Status
        """
    ),
}


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def nonmissing(series: pd.Series) -> pd.Series:
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        text = series.astype("string").str.strip()
        return series.notna() & ~text.isin(["", "NA", "N/A", "nan", "None"])
    return series.notna()


def infer_data_type(series: pd.Series) -> str:
    values = series.dropna()
    if pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    if pd.api.types.is_numeric_dtype(series):
        if len(values) and values.isin([0, 1]).all():
            return "BINARY_NUMERIC"
        if len(values) and ((values % 1) == 0).all():
            return "INTEGER_NUMERIC"
        return "CONTINUOUS_NUMERIC"
    return "TEXT"


def class_lookup(master_columns: list[str]) -> dict[str, str]:
    assigned: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}
    for eligibility_class, fields in CLASS_COLUMNS.items():
        for field in fields:
            if field in assigned:
                duplicates.setdefault(field, [assigned[field]]).append(eligibility_class)
            assigned[field] = eligibility_class
    assert not duplicates, f"Duplicate eligibility assignments: {duplicates}"
    missing = set(master_columns) - set(assigned)
    extra = set(assigned) - set(master_columns)
    assert not missing, f"Unclassified V12 master columns: {sorted(missing)}"
    assert not extra, f"Schema catalog contains non-master columns: {sorted(extra)}"
    assert set(assigned.values()) <= set(ELIGIBILITY_CLASSES)
    return assigned


def safe_family_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}
    for family, fields in SAFE_FAMILY_COLUMNS.items():
        for field in fields:
            if field in lookup and PRIMARY_FAMILY_OVERRIDES.get(field) != family:
                duplicates.setdefault(field, [lookup[field]]).append(family)
            lookup[field] = PRIMARY_FAMILY_OVERRIDES.get(field, family)
    # Explicit overlaps are allowed only when the frozen override resolves them.
    for field, family in PRIMARY_FAMILY_OVERRIDES.items():
        lookup[field] = family
        duplicates.pop(field, None)
    assert not duplicates, f"Unresolved safe-family overlaps: {duplicates}"
    safe_fields = CLASS_COLUMNS["PREDICTOR_SAFE_DIRECT"] | CLASS_COLUMNS["PREDICTOR_SAFE_CONDITIONAL"]
    assert set(lookup) == safe_fields, (
        f"Safe family mismatch; missing={sorted(safe_fields-set(lookup))}, "
        f"extra={sorted(set(lookup)-safe_fields)}"
    )
    return lookup


def scientific_family(field: str, eligibility_class: str, safe_families: dict[str, str]) -> str:
    if field in safe_families:
        return safe_families[field]
    if eligibility_class in {"GROUPING_ONLY", "IDENTIFIER_ONLY"}:
        return "IDENTITY_GROUPING"
    if eligibility_class == "TARGET_ONLY":
        return "TARGET"
    if eligibility_class == "MECHANICAL_OUTCOME_LEAKAGE":
        return "MECHANICAL_RESPONSE"
    if eligibility_class == "POST_TEST_LEAKAGE":
        if field in {
            "Approx_Stress_MPa", "Nearest_SXRD_TRIP_Onset_Stress_MPa",
            "Tensile_TWIP_Onset_Stress_MPa", "Compression_Twinning_Onset_Stress_MPa",
            "Final_InSitu_True_Stress_Approx_MPa", "Final_InSitu_Engineering_Strain_Approx_pct",
            "Tensile_Strain_pct",
        }:
            return "MECHANICAL_RESPONSE"
        return "POST_DEFORMATION_MICROSTRUCTURE"
    if eligibility_class == "MODEL_DERIVED_LEAKAGE":
        return "MODEL_DERIVED_RESPONSE"
    if eligibility_class == "COMPUTATIONAL_ONLY":
        return "COMPUTATIONAL_ONLY"
    if eligibility_class == "METADATA_ONLY":
        return METADATA_FAMILIES[field]
    if eligibility_class == "PROVENANCE_ONLY":
        return PROVENANCE_FAMILY_OVERRIDES.get(field, "PROVENANCE_QC")
    return "OTHER"


def model_role(eligibility_class: str) -> str:
    return {
        "PREDICTOR_SAFE_DIRECT": "CANDIDATE_PREDICTOR",
        "PREDICTOR_SAFE_CONDITIONAL": "CONDITIONAL_CANDIDATE_PREDICTOR",
        "METADATA_ONLY": "AUDIT_OR_DESCRIPTIVE_ONLY",
        "GROUPING_ONLY": "SPLIT_AND_DEPENDENCE_CONTROL_ONLY",
        "TARGET_ONLY": "TARGET_OR_TARGET_EVIDENCE_ONLY",
        "POST_TEST_LEAKAGE": "PERMANENTLY_BLOCK_FROM_PRIMARY_PREDICTORS",
        "MECHANICAL_OUTCOME_LEAKAGE": "PERMANENTLY_BLOCK_FROM_PRIMARY_PREDICTORS",
        "MODEL_DERIVED_LEAKAGE": "PERMANENTLY_BLOCK_FROM_PRIMARY_PREDICTORS",
        "COMPUTATIONAL_ONLY": "COMPUTATIONAL_DOMAIN_ONLY",
        "PROVENANCE_ONLY": "AUDIT_OR_ELIGIBILITY_CONTROL_ONLY",
        "IDENTIFIER_ONLY": "IDENTITY_CONTROL_ONLY",
        "UNRESOLVED_REVIEW": "BLOCK_PENDING_SCIENTIFIC_REVIEW",
    }[eligibility_class]


def experimental_eligibility(field: str, eligibility_class: str) -> str:
    if eligibility_class == "PREDICTOR_SAFE_DIRECT":
        return "ELIGIBLE_SOURCE_FIELD"
    if eligibility_class == "PREDICTOR_SAFE_CONDITIONAL":
        if field in {
            "Recovered_ISFE_DFT_0K_mJ_m2", "SFE_mJ_m2", "SFE_value_alloy_level_mJ_m2",
        }:
            return "CONDITIONAL_METHOD_GATED_OR_FUTURE_ABLATION_ONLY"
        return "CONDITIONAL_SCOPE_CONTROL_REQUIRED"
    return {
        "TARGET_ONLY": "TARGET_POOL_ONLY",
        "GROUPING_ONLY": "SPLIT_CONTROL_ONLY",
        "PROVENANCE_ONLY": "AUDIT_CONTROL_ONLY",
        "METADATA_ONLY": "NOT_ELIGIBLE_AS_ORDINARY_PREDICTOR",
        "IDENTIFIER_ONLY": "NOT_ELIGIBLE_AS_PREDICTOR",
        "COMPUTATIONAL_ONLY": "NOT_ELIGIBLE_EXPERIMENTAL_DOMAIN",
        "UNRESOLVED_REVIEW": "NOT_ELIGIBLE_PENDING_REVIEW",
    }.get(eligibility_class, "NOT_ELIGIBLE_LEAKAGE")


def computational_eligibility(field: str, eligibility_class: str) -> str:
    if eligibility_class == "COMPUTATIONAL_ONLY":
        return "ELIGIBLE_COMPUTATIONAL_DOMAIN_ONLY"
    if field == "Recovered_ISFE_DFT_0K_mJ_m2":
        return "ELIGIBLE_METHOD_SPECIFIC_PHYSICS_ABLATION_ONLY"
    if eligibility_class in {"PROVENANCE_ONLY", "GROUPING_ONLY", "IDENTIFIER_ONLY"}:
        return "DOMAIN_CONTROL_ONLY"
    return "NOT_DEFINED_FOR_CURRENT_P017_FEATURE_SPACE"


def known_before(eligibility_class: str) -> str:
    if eligibility_class in {"PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"}:
        return "YES" if eligibility_class == "PREDICTOR_SAFE_DIRECT" else "CONDITIONAL_ON_SCOPE"
    if eligibility_class in {"POST_TEST_LEAKAGE", "MECHANICAL_OUTCOME_LEAKAGE", "MODEL_DERIVED_LEAKAGE", "TARGET_ONLY"}:
        return "NO"
    if eligibility_class == "COMPUTATIONAL_ONLY":
        return "COMPUTATIONAL_DOMAIN_ONLY"
    return "NOT_APPLICABLE_TO_MODEL_ROLE"


def source_kind(field: str, eligibility_class: str) -> str:
    if field.startswith("QC_"):
        return "REPOSITORY_QC_DERIVED"
    if field in {"Effective_TRIP", "Effective_TWIP", "Target_Correction_TRIP", "Target_Correction_TWIP"}:
        return "REVIEW_DERIVED_TARGET_WITH_ORIGINAL_PRESERVED"
    if eligibility_class == "MODEL_DERIVED_LEAKAGE":
        return "SOURCE_REPORTED_OR_FITTED_LOADING_DERIVATION"
    if eligibility_class == "COMPUTATIONAL_ONLY":
        return "SOURCE_REPORTED_COMPUTATIONAL"
    if field in {"Atomic_size_misfit_pct", "Cold_rolling_reduction_pct", "Cold_Roll_Reduction_Status"}:
        return "SOURCE_REPORTED_OR_EXPLICIT_SOURCE_DERIVATION"
    if field in {
        "SFE_mJ_m2", "DeltaG_FCC_HCP_J_mol", "Recovered_ISFE_DFT_0K_mJ_m2",
        "Recovered_DeltaG_FCC_HCP_300K_J_mol", "SFE_value_alloy_level_mJ_m2",
        "Recovered_SFE_assumed_for_calculation_mJ_m2",
    }:
        return "SOURCE_REPORTED_METHOD_SPECIFIC_VALUE"
    if eligibility_class in {"PROVENANCE_ONLY", "METADATA_ONLY", "GROUPING_ONLY", "IDENTIFIER_ONLY"}:
        return "SOURCE_OR_REPOSITORY_BOOKKEEPING"
    return "DIRECT_SOURCE_FIELD"


def sensitivity_flags(field: str, family: str) -> tuple[str, str, str]:
    method_tokens = (
        "SFE", "DeltaG", "lattice", "XRD", "EBSD", "EDS", "APT", "KAM", "GOS",
        "Grain", "fraction", "Composition", "Twin", "Martensite", "HCP", "FCC",
    )
    temperature_tokens = (
        "SFE", "DeltaG", "Magnetic", "Test_T", "temperature", "Phase", "HCP", "FCC",
    )
    phase_tokens = (
        "SFE", "DeltaG", "lattice", "Phase", "HCP", "FCC", "BCC", "Twin", "Martensite",
        "CSRO", "GND", "KAM", "Recrystall", "Precipitate",
    )
    method = "YES" if family in {"PHYSICS_THERMODYNAMICS", "INITIAL_MICROSTRUCTURE"} or any(t.lower() in field.lower() for t in method_tokens) else "NO"
    temperature = "YES" if any(t.lower() in field.lower() for t in temperature_tokens) else "NO"
    phase = "YES" if family in {"PHYSICS_THERMODYNAMICS", "INITIAL_MICROSTRUCTURE", "POST_DEFORMATION_MICROSTRUCTURE"} or any(t.lower() in field.lower() for t in phase_tokens) else "NO"
    return method, temperature, phase


def leakage_fields(eligibility_class: str) -> tuple[str, str]:
    reasons = {
        "PREDICTOR_SAFE_DIRECT": ("NO", "Direct source-supported information available before loading."),
        "PREDICTOR_SAFE_CONDITIONAL": ("CONDITIONAL", "Safe only after method, scope, timing, or availability control."),
        "METADATA_ONLY": ("YES_IF_MODELED", "Metadata can encode paper, workflow, or extraction artifacts rather than material behavior."),
        "GROUPING_ONLY": ("YES_IF_MODELED", "A grouping key would expose dependence or study/material identity."),
        "TARGET_ONLY": ("YES", "The field is a target, direct target state, or target evidence."),
        "POST_TEST_LEAKAGE": ("YES", "The field is observed only after tensile deformation starts or after fracture."),
        "MECHANICAL_OUTCOME_LEAKAGE": ("YES", "The field is an outcome of the same tensile test whose mechanisms are predicted."),
        "MODEL_DERIVED_LEAKAGE": ("YES", "The field is derived or inferred from loading response or fitted mechanical behavior."),
        "COMPUTATIONAL_ONLY": ("YES_FOR_EXPERIMENTAL_MODEL", "The descriptor is confined to a non-equivalent computational domain."),
        "PROVENANCE_ONLY": ("YES_IF_MODELED", "Source, method, review, or QC bookkeeping can encode study and label-acquisition artifacts."),
        "IDENTIFIER_ONLY": ("YES_IF_MODELED", "The identifier can memorize paper, material, condition, or observation identity."),
        "UNRESOLVED_REVIEW": ("YES", "Prediction-time scope has not been established; blocked by default."),
    }
    return reasons[eligibility_class]


def missingness_concern(count: int, denominator: int, eligibility_class: str) -> str:
    pct = 100 * count / denominator if denominator else 0
    if eligibility_class not in {"PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"}:
        return f"NOT_MODEL_APPLICABLE; experimental nonmissing {count}/{denominator}"
    if count == 0:
        level = "NO_EXPERIMENTAL_COVERAGE"
    elif pct < 20:
        level = "SEVERE"
    elif pct < 50:
        level = "HIGH"
    elif pct < 80:
        level = "MODERATE"
    else:
        level = "LOW"
    return f"{level}; experimental nonmissing {count}/{denominator} ({pct:.2f}%)"


def scope_constraint(field: str, family: str, eligibility_class: str) -> str:
    overrides = {
        "Original_Composition": "May combine nominal and measured text; retain basis and never silently parse or normalize.",
        "Composition_basis": "Interpretation control; measured and nominal chemistry must remain distinguishable.",
        "Recovered_Bulk_Composition_at_pct": "Use only when explicitly specimen/material bulk; never substitute local or feedstock chemistry.",
        "Nominal_Composition_at_pct": "Nominal chemistry only; do not overwrite with measured chemistry.",
        "Measured_Composition_at_pct": "Measured bulk chemistry; retain method and do not normalize in V1.",
        "Feedstock_Composition_at_pct": "Feedstock scope only; not automatically specimen bulk chemistry.",
        "APT_local_composition": "Local APT chemistry only; not bulk composition.",
        "EDS_local_composition": "Local EDS chemistry only; not bulk composition.",
        "Local_EDS_Composition_at_pct": "Local/scanned-region EDS only; not bulk composition.",
        "Processing_TRIP": "Pre-tensile processing-induced phase state only; never use as the tensile TRIP target.",
        "Processing_TWIP": "Pre-tensile processing-induced twin state only; never use as the tensile TWIP target.",
        "Initial_twin_boundary_status": "Initial/annealing twins may be predictors but never establish deformation TWIP.",
        "Initial_Sigma3_TB_fraction": "Initial annealing-twin state only; never establish deformation TWIP.",
        "Initial_HCP_fraction": "Pre-existing/thermal/processing HCP only; never establish tensile TRIP.",
        "Recovered_Initial_HCP_fraction": "Pre-test HCP only; never promote processing or thermal martensite to a tensile target.",
        "Initial_BCC_alpha_martensite_fraction": "Pre-test BCC alpha state; keep separate from HCP and tensile TRIP.",
        "KAM_mean_deg": "Eligible only for rows explicitly measured before tensile loading (current P014 initial states); P011 interrupted/fracture-stage KAM is post-test and excluded.",
        "SFE_mJ_m2": "Require row-level method, structure, temperature, paper/current-reference, and experimental/computational scope.",
        "Recovered_ISFE_DFT_0K_mJ_m2": "DFT intrinsic SFE at 0 K; future physics ablation only, never generic experimental SFE.",
        "SFE_value_alloy_level_mJ_m2": "Alloy-level value; do not duplicate across conditions without a predeclared scope rule.",
        "Recovered_SFE_assumed_for_calculation_mJ_m2": "P016 assumed model input; not a direct material measurement.",
        "DeltaG_FCC_HCP_J_mol": "Require alloy, paper, calculation method, and temperature match; never transfer across papers/alloys.",
        "Recovered_DeltaG_FCC_HCP_300K_J_mol": "Thermo-Calc value at 300 K only; never transfer across temperature, alloy, or paper.",
        "Atomic_size_misfit_pct": "Existing source field retained only; no V1 calculation or ordinary predictor use.",
        "Test_T_Raw": "Raw reported temperature text; no RT-to-K conversion is performed in this task.",
        "Recovered_Test_T_Reported": "Raw reported temperature; no numeric inference or standardization in V1.",
        "Mn_Charge_Adjustment": "Melting-charge compensation metadata only; not final specimen chemistry.",
        "Leakage_Group_Strict": "Split/group control only; all dependent rows must remain within one fold.",
        "Leakage_Group_Material": "Material-family split/group control only; never a predictor.",
        "Paper_ID": "May be used to design paper-held-out splits; never an ordinary predictor.",
        "DOI": "Source identity only; never an ordinary predictor.",
        "ML_Condition_ID": "Condition identity only; never an ordinary predictor.",
        "Postfracture_HCP_fraction": "P015 post-fracture target evidence; permanently forbidden as a pre-deformation predictor.",
        "HDI_Hardening": "P014 loading-unloading-reloading-derived HDI quantity; permanently blocked.",
        "Paper_Native_TRIP": "P017 paper-native computational target; not experimental FCC-to-HCP TRIP.",
        "Paper_Native_TWIP": "P017 paper-native computational target; not experimental deformation TWIP.",
        "SIS_PSR_GPa": "P017 computational stress-regime metric; not experimental YS.",
        "UTS_PSR_GPa": "P017 computational stress-regime metric; not experimental UTS.",
    }
    if field in overrides:
        return overrides[field]
    if eligibility_class in {"POST_TEST_LEAKAGE", "MECHANICAL_OUTCOME_LEAKAGE", "MODEL_DERIVED_LEAKAGE"}:
        return "Permanently excluded from primary pre-deformation TRIP/TWIP predictor matrices."
    if eligibility_class == "TARGET_ONLY":
        return "Retain for target definition/evidence only; never include in predictors."
    if eligibility_class == "COMPUTATIONAL_ONLY":
        return "Retain outside the experimental feature matrix; do not use P017 to increase experimental sample count."
    if eligibility_class in {"GROUPING_ONLY", "IDENTIFIER_ONLY"}:
        return "Use only for identity, dependence control, or grouped split design."
    if eligibility_class in {"PROVENANCE_ONLY", "METADATA_ONLY"}:
        return "Retain for audit, descriptive context, and eligibility control; never use as an ordinary predictor."
    if family == "CHEMISTRY":
        return "Retain source basis and scope; measured bulk is preferred over nominal only under the documented future policy."
    if family == "PROCESSING":
        return "Must describe processing completed before the tensile test; route text is not encoded in this task."
    if family == "TEST_CONDITIONS":
        return "Must be a planned condition known before loading; no missing temperature/rate is inferred."
    if family == "INITIAL_MICROSTRUCTURE":
        return "Must be explicitly pre-test; preserve method, phase, and initial-versus-deformed scope."
    if family == "PHYSICS_THERMODYNAMICS":
        return "Require method, phase/structure, temperature, and source-domain matching; no cross-paper transfer."
    return "Blocked unless later source review establishes prediction-time scope."


def recommended_action(eligibility_class: str) -> str:
    return {
        "PREDICTOR_SAFE_DIRECT": "RETAIN_AS_UNTRANSFORMED_CANDIDATE",
        "PREDICTOR_SAFE_CONDITIONAL": "RETAIN_CONDITIONALLY; REQUIRE_SCOPE_GATE",
        "METADATA_ONLY": "RETAIN; BLOCK_AS_ORDINARY_PREDICTOR",
        "GROUPING_ONLY": "RETAIN_FOR_SPLIT_DESIGN_ONLY",
        "TARGET_ONLY": "RETAIN_FOR_TARGET_OR_EVIDENCE_ONLY",
        "POST_TEST_LEAKAGE": "PERMANENTLY_BLOCK_FROM_PRIMARY_PREDICTORS",
        "MECHANICAL_OUTCOME_LEAKAGE": "PERMANENTLY_BLOCK_FROM_PRIMARY_PREDICTORS",
        "MODEL_DERIVED_LEAKAGE": "PERMANENTLY_BLOCK_FROM_PRIMARY_PREDICTORS",
        "COMPUTATIONAL_ONLY": "KEEP_IN_SEPARATE_COMPUTATIONAL_DOMAIN",
        "PROVENANCE_ONLY": "RETAIN_FOR_AUDIT_OR_ELIGIBILITY_CONTROL_ONLY",
        "IDENTIFIER_ONLY": "RETAIN_FOR_IDENTITY_CONTROL_ONLY",
        "UNRESOLVED_REVIEW": "BLOCK_PENDING_REVIEW",
    }[eligibility_class]


def schema_note(field: str, family: str, eligibility_class: str) -> str:
    special = {
        "SFE_mJ_m2": "Mixed current source field; experimental, thermodynamic, DFT/MD, assumed, and reference values are not interchangeable.",
        "Recovered_ISFE_DFT_0K_mJ_m2": "Distinct DFT 0 K field; not collapsed into experimental SFE.",
        "Effective_TRIP": "Primary preserved experimental TRIP target candidate; final task selection is not made in V1.",
        "Effective_TWIP": "Primary preserved experimental TWIP target candidate; final task selection is not made in V1.",
        "Postfracture_Phase_State": "P015 post-fracture state is target evidence, not a predictor.",
        "Engineering_YS_MPa": "P015 same-test engineering yield outcome; retained for interpretation only.",
        "Engineering_UTS_MPa": "P015 same-test engineering ultimate strength outcome; retained for interpretation only.",
        "Nearest_SXRD_TRIP_Onset_Stress_MPa": "P013 strain-resolved SXRD target/stage evidence only.",
        "Paper_Native_TRIP": "P017 native computational label remains separate from Effective_TRIP.",
        "Paper_Native_TWIP": "P017 native computational label remains separate from Effective_TWIP.",
    }
    if field in special:
        return special[field]
    if eligibility_class == "PREDICTOR_SAFE_DIRECT":
        return "No transformation, normalization, encoding, or imputation is performed in Feature Schema V1."
    if eligibility_class == "PREDICTOR_SAFE_CONDITIONAL":
        return "Candidate status does not authorize pooling heterogeneous methods or filling missing values."
    return f"Primary V1 family: {family}; classification is frozen for pre-deformation prediction."


def build_schema(master: pd.DataFrame, experimental_rows: pd.DataFrame) -> pd.DataFrame:
    classes = class_lookup(list(master.columns))
    safe_families = safe_family_lookup()
    rows = []
    for field in master.columns:
        eligibility_class = classes[field]
        family = scientific_family(field, eligibility_class, safe_families)
        assert family in SCIENTIFIC_FAMILIES
        count = int(nonmissing(experimental_rows[field]).sum())
        method, temperature, phase = sensitivity_flags(field, family)
        potential, reason = leakage_fields(eligibility_class)
        rows.append(
            {
                "Column_Name": field,
                "Data_Type": infer_data_type(master[field]),
                "Scientific_Family": family,
                "Prediction_Time_Class": eligibility_class,
                "Proposed_Model_Role": model_role(eligibility_class),
                "Experimental_Domain_Eligibility": experimental_eligibility(field, eligibility_class),
                "Computational_Domain_Eligibility": computational_eligibility(field, eligibility_class),
                "Known_Before_Deformation": known_before(eligibility_class),
                "Direct_Source_or_Derived": source_kind(field, eligibility_class),
                "Method_Sensitive": method,
                "Temperature_Sensitive": temperature,
                "Phase_Sensitive": phase,
                "Potential_Leakage": potential,
                "Leakage_Reason": reason,
                "Missingness_Concern": missingness_concern(count, len(experimental_rows), eligibility_class),
                "Scope_Constraint": scope_constraint(field, family, eligibility_class),
                "Recommended_V1_Action": recommended_action(eligibility_class),
                "Notes": schema_note(field, family, eligibility_class),
            }
        )
    return pd.DataFrame(rows, columns=SCHEMA_COLUMNS)


def priority_for(field: str, family: str, eligibility_class: str, count: int) -> tuple[str, str]:
    if eligibility_class not in {"PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"}:
        return "NOT_ELIGIBLE", {
            "TARGET_ONLY": "Target or target evidence cannot be an input.",
            "POST_TEST_LEAKAGE": "Unavailable at the frozen prediction moment.",
            "MECHANICAL_OUTCOME_LEAKAGE": "Same-test mechanical outcome would leak the response.",
            "MODEL_DERIVED_LEAKAGE": "Derived from loading response or fitted mechanics.",
            "COMPUTATIONAL_ONLY": "Not equivalent to the experimental predictor domain.",
            "GROUPING_ONLY": "Reserved for dependence-aware splitting.",
            "IDENTIFIER_ONLY": "Identity fields may memorize study or condition.",
            "PROVENANCE_ONLY": "Reserved for audit/method/QC control.",
            "METADATA_ONLY": "Descriptive metadata has no approved V1 predictor role.",
            "UNRESOLVED_REVIEW": "Blocked until scientific scope is resolved.",
        }[eligibility_class]
    if field in CORE_V1_COLUMNS:
        reasons = {
            "Fe_at%": "Central alloy chemistry with broad direct coverage; missing remains NA.",
            "Mn_at%": "Mechanism-relevant matrix chemistry with broad direct coverage; missing remains NA.",
            "Co_at%": "Central multicomponent chemistry with broad direct coverage; missing remains NA.",
            "Cr_at%": "Central multicomponent chemistry with broad direct coverage; missing remains NA.",
            "Test_T_K": "Planned temperature is mechanism-defining and available before loading.",
            "Strain_rate_s-1": "Planned rate is mechanism-defining and available before loading.",
            "Processing_route": "Processing history is scientifically essential and broadly reported; raw text remains unencoded.",
            "Grain_size_um": "Initial grain size is mechanistically relevant with useful direct coverage; method/scope remain controlled.",
        }
        return "CORE_V1", reasons[field]
    if family == "PHYSICS_THERMODYNAMICS":
        return "EXPLORATORY_LATER", "Physics descriptor is method/temperature/phase sensitive and too sparse or heterogeneous for the initial baseline."
    if field in {
        "APT_local_composition", "EDS_local_composition", "Local_EDS_Composition_at_pct",
        "Feedstock_Composition_at_pct", "Cr_at%_uncertainty", "Mn_at%_uncertainty",
        "Fe_at%_uncertainty", "Co_at%_uncertainty", "Ni_at%_uncertainty",
        "Alpha_lath_thickness", "Alpha_lath_spacing", "Recovery_twin_fraction",
        "Recovery_twin_thickness", "Recovery_twin_spacing_observed",
        "Recovery_twin_spacing_fraction_input_nm", "Precipitate_type", "KAM_mean_deg",
        "Recrystallized_fraction", "Recovered_Recrystallized_fraction",
    }:
        return "EXPLORATORY_LATER", "Scientifically relevant but local/scope-specific, sparse, or method-heterogeneous; reserve for controlled ablation."
    return "OPTIONAL_V1", "Pre-test and scientifically relevant, but representation, applicability, coverage, or method heterogeneity prevents CORE_V1 status."


def build_priority(schema: pd.DataFrame, experimental_rows: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, item in schema.iterrows():
        field = item.Column_Name
        count = int(nonmissing(experimental_rows[field]).sum())
        priority, reason = priority_for(field, item.Scientific_Family, item.Prediction_Time_Class, count)
        rows.append(
            {
                "Column_Name": field,
                "Scientific_Family": item.Scientific_Family,
                "Prediction_Time_Class": item.Prediction_Time_Class,
                "Feature_Priority": priority,
                "Coverage_Count_51": count,
                "Coverage_Percent_51": round(100 * count / len(experimental_rows), 2),
                "Scientific_Reason": reason,
                "Recommended_Use": {
                    "CORE_V1": "BASELINE_CANDIDATE_AFTER_SPLIT_DESIGN_AND_REPRESENTATION_POLICY",
                    "OPTIONAL_V1": "OPTIONAL_CANDIDATE_WITH_SCOPE_CONTROL",
                    "EXPLORATORY_LATER": "ABLATION_OR_FUTURE_PHYSICS_STUDY_ONLY",
                    "NOT_ELIGIBLE": "BLOCK_FROM_PRIMARY_PREDICTOR_MATRIX",
                }[priority],
                "Notes": "Priority is scientific and coverage-aware; no numeric threshold alone determined this class.",
            }
        )
    return pd.DataFrame(rows)


def feature_set_members(schema: pd.DataFrame) -> dict[str, tuple[list[str], list[str]]]:
    schema_by_name = schema.set_index("Column_Name")
    master_order = {name: i for i, name in enumerate(schema.Column_Name)}
    cumulative_candidates: set[str] = set()
    cumulative_controls: set[str] = set()
    result: dict[str, tuple[list[str], list[str]]] = {}
    for feature_set in FEATURE_SET_ORDER:
        family = FEATURE_SET_ADDITION[feature_set]
        family_candidates = set(
            schema.loc[
                schema.Scientific_Family.eq(family)
                & schema.Prediction_Time_Class.isin({"PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"}),
                "Column_Name",
            ]
        )
        cumulative_candidates.update(family_candidates)
        cumulative_controls.update(FEATURE_SET_CONTROLS[family])
        assert cumulative_controls <= set(schema_by_name.index)
        candidates = sorted(cumulative_candidates, key=master_order.get)
        controls = sorted(cumulative_controls - cumulative_candidates, key=master_order.get)
        result[feature_set] = (candidates, controls)
    return result


def build_feature_sets(
    schema: pd.DataFrame, priority: pd.DataFrame, experimental_rows: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, tuple[list[str], list[str]]]]:
    members = feature_set_members(schema)
    schema_map = schema.set_index("Column_Name")
    priority_map = priority.set_index("Column_Name")
    rows = []
    for feature_set, (candidates, controls) in members.items():
        for field in candidates + controls:
            item = schema_map.loc[field]
            prio = priority_map.loc[field, "Feature_Priority"]
            count = int(nonmissing(experimental_rows[field]).sum())
            is_control = field in controls
            rows.append(
                {
                    "Feature_Set": feature_set,
                    "Feature_Family": item.Scientific_Family,
                    "Column_Name": field,
                    "Eligibility_Status": "CONTROL_ONLY_NOT_MODEL_FEATURE" if is_control else {
                        "CORE_V1": "CANDIDATE_CORE_V1",
                        "OPTIONAL_V1": "CANDIDATE_OPTIONAL_V1",
                        "EXPLORATORY_LATER": "CANDIDATE_EXPLORATORY_LATER",
                    }[prio],
                    "Reason": (
                        "Required source/method/scope control; retained in the manifest but excluded from candidate and complete-case counts."
                        if is_control else priority_map.loc[field, "Scientific_Reason"]
                    ),
                    "Coverage_Count_51": count,
                    "Coverage_Percent_51": round(100 * count / len(experimental_rows), 2),
                    "Method_Constraint": item.Scope_Constraint,
                    "Leakage_Status": (
                        "CONTROL_ONLY_NEVER_MODEL_FEATURE" if is_control
                        else "LEAKAGE_FREE_DIRECT" if item.Prediction_Time_Class == "PREDICTOR_SAFE_DIRECT"
                        else "LEAKAGE_FREE_ONLY_WITH_SCOPE_GATE"
                    ),
                    "Notes": "Raw source column only; no imputation, encoding, normalization, conflict resolution, or derived descriptor was produced.",
                }
            )
    return pd.DataFrame(rows), members


def lowest_coverage(columns: list[str], experimental_rows: pd.DataFrame, limit: int = 4) -> str:
    if not columns:
        return "NONE"
    order = {field: i for i, field in enumerate(experimental_rows.columns)}
    ranked = sorted(
        ((int(nonmissing(experimental_rows[field]).sum()), order[field], field) for field in columns),
        key=lambda item: (item[0], item[1]),
    )
    return "; ".join(f"{field}={count}/51" for count, _, field in ranked[:limit])


def build_coverage(
    members: dict[str, tuple[list[str], list[str]]],
    priority: pd.DataFrame,
    experimental_rows: pd.DataFrame,
) -> pd.DataFrame:
    priority_map = priority.set_index("Column_Name")
    rows = []
    for feature_set in FEATURE_SET_ORDER:
        candidates, controls = members[feature_set]
        counts = [int(nonmissing(experimental_rows[field]).sum()) for field in candidates]
        core = [field for field in candidates if priority_map.loc[field, "Feature_Priority"] == "CORE_V1"]
        complete = int(experimental_rows[core].notna().all(axis=1).sum()) if core else len(experimental_rows)
        rows.append(
            {
                "Feature_Set": feature_set,
                "Independent_Experimental_Conditions": len(experimental_rows),
                "Candidate_Feature_Count": len(candidates),
                "Complete_Case_Count": complete,
                "Median_Feature_Coverage": round(100 * float(pd.Series(counts).median()) / len(experimental_rows), 2),
                "Minimum_Feature_Coverage": round(100 * min(counts) / len(experimental_rows), 2),
                "Maximum_Feature_Coverage": round(100 * max(counts) / len(experimental_rows), 2),
                "Major_Missingness_Bottleneck": lowest_coverage(candidates, experimental_rows),
                "Leakage_Free_Status": "PASS_FROZEN_PREDICTION_TIME_POLICY",
                "Notes": (
                    "Complete_Case_Count is the raw intersection of cumulative CORE_V1 columns only: "
                    + ", ".join(core)
                    + ". Candidate count and coverage statistics include all direct/conditional candidates but exclude "
                    + f"{len(controls)} method/provenance controls. Alternative chemistry or grain fields were not merged; no imputation or transformation occurred."
                ),
            }
        )
    return pd.DataFrame(rows)


def target_definition(experimental_rows: pd.DataFrame, target: str) -> tuple[pd.Series, int, int, str]:
    if target == "TRIP":
        usable = experimental_rows.Effective_TRIP.notna()
        positive = int(experimental_rows.loc[usable, "Effective_TRIP"].eq(1).sum())
        negative = int(experimental_rows.loc[usable, "Effective_TRIP"].eq(0).sum())
        note = "Effective_TRIP usable conditions; binary 1/0 counts."
    elif target == "TWIP":
        usable = experimental_rows.Effective_TWIP.notna()
        positive = int(experimental_rows.loc[usable, "Effective_TWIP"].eq(1).sum())
        negative = int(experimental_rows.loc[usable, "Effective_TWIP"].eq(0).sum())
        note = "Effective_TWIP usable conditions; binary 1/0 counts."
    else:
        usable = experimental_rows[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1)
        subset = experimental_rows.loc[usable, ["Effective_TRIP", "Effective_TWIP"]]
        positive = int(subset.eq(1).any(axis=1).sum())
        negative = int(subset.eq(0).all(axis=1).sum())
        note = "Joint usable conditions; positive means any mechanism (10/01/11), negative means state 00."
    return usable, positive, negative, note


def build_target_availability(
    members: dict[str, tuple[list[str], list[str]]],
    priority: pd.DataFrame,
    experimental_rows: pd.DataFrame,
) -> pd.DataFrame:
    priority_map = priority.set_index("Column_Name")
    rows = []
    for target in ("TRIP", "TWIP", "JOINT"):
        usable, positive, negative, target_note = target_definition(experimental_rows, target)
        subset = experimental_rows.loc[usable]
        for feature_set in FEATURE_SET_ORDER:
            candidates, _ = members[feature_set]
            core = [field for field in candidates if priority_map.loc[field, "Feature_Priority"] == "CORE_V1"]
            complete = int(subset[core].notna().all(axis=1).sum()) if core else len(subset)
            ranked = sorted(
                ((int(nonmissing(subset[field]).sum()), field) for field in candidates),
                key=lambda item: (item[0], item[1]),
            )
            major = "; ".join(f"{field}={count}/{len(subset)}" for count, field in ranked[:5])
            rows.append(
                {
                    "Target": target,
                    "Feature_Set": feature_set,
                    "Target_Usable_Conditions": len(subset),
                    "Target_Positive": positive,
                    "Target_Negative": negative,
                    "Complete_Case_Count": complete,
                    "Major_Missing_Features": major,
                    "Notes": (
                        target_note
                        + " Complete cases use cumulative CORE_V1 raw columns only; optional/exploratory fields and controls are reported but not required. No imputation."
                    ),
                }
            )
    return pd.DataFrame(rows)


def build_domain_manifest(master: pd.DataFrame) -> pd.DataFrame:
    role = master.QC_Row_Role.astype("string")
    domains = [
        {
            "Dataset_Domain": "EXPERIMENTAL_PRIMARY",
            "Current_Row_Count": int(role.eq("EXPERIMENTAL_PRIMARY_CONDITION").sum()),
            "Source_Row_Roles": "EXPERIMENTAL_PRIMARY_CONDITION",
            "Training_Eligibility": "ELIGIBLE_FOR_FUTURE_EXPERIMENTAL_SPLIT_DESIGN; NOT_YET_TRAINING_AUTHORIZATION",
            "Target_Eligibility": "Effective_TRIP/Effective_TWIP only when nonmissing and evidence-reviewed",
            "Grouping_Role": "Group by paper/study/material/strict leakage keys before any split",
            "Scientific_Role": "One replacement-aware independent pre-deformation tensile condition",
            "Notes": "Current count is 51; P017/P018/P019 contribute zero rows.",
        },
        {
            "Dataset_Domain": "EXPERIMENTAL_STAGE_SUPPORT",
            "Current_Row_Count": int(role.eq("EXPERIMENTAL_STAGE_CHILD").sum()),
            "Source_Row_Roles": "EXPERIMENTAL_STAGE_CHILD",
            "Training_Eligibility": "NOT_INDEPENDENT; FORBIDDEN_AS_PRIMARY_TRAINING_ROWS",
            "Target_Eligibility": "TARGET_OR_STAGE_EVIDENCE_ONLY; no stage negative promoted to condition negative",
            "Grouping_Role": "Must remain with parent condition; cannot cross folds",
            "Scientific_Role": "Strain-resolved, interrupted, in-situ, or other repeated deformation evidence",
            "Notes": "All stage variables are post-loading relative to the frozen prediction moment.",
        },
        {
            "Dataset_Domain": "COMPUTATIONAL_PRIMARY",
            "Current_Row_Count": int(role.eq("COMPUTATIONAL_PRIMARY_CONDITION").sum()),
            "Source_Row_Roles": "COMPUTATIONAL_PRIMARY_CONDITION",
            "Training_Eligibility": "COMPUTATIONAL-DOMAIN TASKS ONLY; NEVER EXPERIMENTAL TRAINING ROWS",
            "Target_Eligibility": "Paper-native computational labels only; not Effective_TRIP/Effective_TWIP",
            "Grouping_Role": "Group by computational material/trajectory identity",
            "Scientific_Role": "Twelve exact P017 MD conditions",
            "Notes": "P017 GSFE, SIS/UTS-PSR, PTM, native mechanisms, MD rates, and dislocation evolution remain computational-only.",
        },
        {
            "Dataset_Domain": "COMPUTATIONAL_STAGE_SUPPORT",
            "Current_Row_Count": int(role.eq("COMPUTATIONAL_STAGE_CHILD").sum()),
            "Source_Row_Roles": "COMPUTATIONAL_STAGE_CHILD or trajectory snapshots retained outside the V12 primary index",
            "Training_Eligibility": "NOT_INDEPENDENT; SUPPORTING COMPUTATIONAL EVIDENCE ONLY",
            "Target_Eligibility": "NOT EXPERIMENTAL TARGETS",
            "Grouping_Role": "Must remain with parent computational trajectory",
            "Scientific_Role": "Longitudinal MD snapshots or stage-specific computational evidence",
            "Notes": "The V12 master currently has no row classified COMPUTATIONAL_STAGE_CHILD; source support tables remain separate.",
        },
        {
            "Dataset_Domain": "LEGACY_PRESERVED",
            "Current_Row_Count": int(role.str.startswith("LEGACY", na=False).sum()),
            "Source_Row_Roles": "LEGACY_COLLAPSED; LEGACY_COMPUTATIONAL; LEGACY_EXACT_REPLACED",
            "Training_Eligibility": "NOT_PRIMARY; exact replacements govern independent counting",
            "Target_Eligibility": "Original values preserved for audit; not promoted over reviewed exact targets",
            "Grouping_Role": "Identity/replacement audit only",
            "Scientific_Role": "Non-destructive preservation of earlier representations",
            "Notes": "Legacy preservation does not authorize double counting.",
        },
        {
            "Dataset_Domain": "PROVENANCE_SUPPORT",
            "Current_Row_Count": int(role.isin(["OTHER_REVIEW", "SUMMARY_SUPPORT", "METHOD_SUPPORT"]).sum()),
            "Source_Row_Roles": "OTHER_REVIEW; SUMMARY_SUPPORT; METHOD_SUPPORT",
            "Training_Eligibility": "NOT_PRIMARY_TRAINING_DATA",
            "Target_Eligibility": "SOURCE/METHOD REVIEW ONLY",
            "Grouping_Role": "Audit support; never a predictor",
            "Scientific_Role": "Source state, summaries, methods, and unresolved provenance support",
            "Notes": "QC tiers, confidence, evidence locations, and review status remain non-predictive.",
        },
    ]
    return pd.DataFrame(domains)


def format_list(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "None."


def write_policy(schema: pd.DataFrame) -> None:
    text = f"""# Prediction-Time Leakage Policy V1

## Frozen prediction task and moment

**Task:** pre-deformation condition-level mechanism prediction.

**Prediction moment:** **{PREDICTION_MOMENT.lower()}**.

Given alloy/material information, processing history, initial microstructure, and planned tensile-test conditions known before loading, a future model may predict whether the condition subsequently exhibits TRIP and/or TWIP. Information first observed after loading starts is unavailable at this moment and is forbidden as a primary predictor.

This document freezes eligibility only. It does not choose a final target, train a model, select an algorithm, run cross-validation, impute, encode, normalize, calculate a descriptor, or produce a transformed matrix.

## Preserved target definitions

- **T1 — binary TRIP:** `Effective_TRIP`.
- **T2 — binary TWIP:** `Effective_TWIP`.
- **T3 — joint multilabel:** `Effective_TRIP` and `Effective_TWIP`, with 00 = neither, 10 = TRIP only, 01 = TWIP only, and 11 = both.

`TRIP`, `TWIP`, `Original_TRIP`, `Original_TWIP`, recovered/correction fields, evidence fields, and direct mechanism-state variables are target/evidence fields, never predictors. V1 does not select T1, T2, or T3 as the final ML task.

## Allowed at prediction time

- Source-supported nominal or measured **bulk chemistry**, with basis and scope preserved.
- **Processing history** completed before the tensile test.
- Explicitly pre-test **initial microstructure**, including pre-existing phases or annealing/processing twins when their temporal scope is documented.
- Planned **test temperature, strain rate, loading mode, and loading/orientation** when explicitly reported.
- Eligible pre-test **physics/thermodynamic descriptors** only under method, phase, temperature, paper, and domain controls.

Safe-direct status does not imply completeness or authorize encoding. Safe-conditional status requires its recorded scope gate before inclusion.

## Permanently forbidden primary predictors

- Same-test mechanics: YS, UTS, engineering/true properties, elongation, uniform elongation, hardening response, fracture strain/mode, and their uncertainties.
- Post-deformation or post-fracture phases, twins, post-test KAM/GOS, dislocation density, morphology, and mechanism observations.
- Strain-stage, interrupted-test, in-situ SXRD/EBSD/TEM, stage phase fraction, stage twin fraction, stage KAM, or other observations collected after loading starts.
- TRIP/TWIP labels, target evidence, target confidence/status, or any direct mechanism-state outcome.
- HDI/back stress, strengthening contributions, critical stresses, inferred onsets, adiabatic/dynamic loading quantities, or other fitted/loading-response-derived fields.
- Paper/material/condition identifiers, grouping keys, provenance, QC tiers/status, source location, evidence confidence, and review metadata as ordinary predictors.
- P017 computational rows or paper-native labels in an experimental feature matrix.

These fields remain in the source for interpretation, target adjudication, mechanism–property studies, and audit. Retention never implies predictor eligibility.

## Chemistry policy

Measured bulk and nominal chemistry remain separate source representations. The frozen future conflict policy is:

1. if explicitly measured **bulk specimen/material chemistry** exists, prefer it;
2. otherwise use explicitly nominal chemistry;
3. retain basis, source, and method;
4. never treat local EDS/APT/TEM or feedstock chemistry as specimen bulk without an explicit scope decision;
5. never treat extra melting-charge compensation as final bulk chemistry.

This preference is documentation only. V1 does **not** merge the fields, parse composition strings, normalize at.%, infer an absent element as zero, or calculate elemental/alloy descriptors.

## Processing and test-condition policy

Melting/casting, powder metallurgy/SPS, homogenization, rolling, annealing, quenching/solution treatment, and processing-state information may be pre-test predictors when source-supported. Processing-induced martensite or twins can describe the initial tensile state but never become tensile TRIP/TWIP targets. Processing deformation is distinct from tensile deformation.

Planned temperature, strain rate, loading mode, and orientation are direct safe concepts. This V12 dataset has no dedicated usable loading-mode column and only partial loading-direction coverage. Specimen dimensions are metadata-only in V1 because no core scientific rationale has yet been frozen.

## Initial-microstructure policy

Explicitly pre-test FCC/HCP/BCC/other phases, grain size, recrystallized fraction, initial KAM/GOS, twins, precipitates, and phase-measurement method remain available. XRD and EBSD phase fractions are not assumed interchangeable. Initial annealing twins never establish TWIP. Pre-existing or processing-induced martensite/HCP never establishes tensile TRIP. Generic or post-test phase/twin fields remain blocked.

## Physics and thermodynamic policy

SFE and DeltaG require method-specific provenance and condition scope. Experimental SFE, thermodynamic/CALPHAD SFE, DFT 0 K SFE, MD SFE, FCC stable gamma_sf, and BCC unstable gamma_usf are never collapsed into one feature. `SFE_mJ_m2` is conditional because its rows span heterogeneous methods; the source method/origin fields are eligibility controls, not ordinary predictors.

- Direct experimental SFE may be eligible when measured before testing and condition-relevant.
- Current-paper thermodynamic/CALPHAD SFE is conditional.
- DFT/MD SFE is future physics-ablation-only and is not automatically experimental SFE.
- P017 GSFE is **COMPUTATIONAL_ONLY**.
- P016's assumed 18 mJ/m2 input is metadata/model input, not a material measurement.
- Reference constants remain metadata or conditional future inputs; they are not silently transferred.
- DeltaG is method-, alloy-, paper-, phase-, and temperature-specific and is never transferred across papers/alloys.

No SFE or DeltaG is imputed.

## Computational-domain policy

The twelve exact P017 conditions remain `COMPUTATIONAL_PRIMARY`; they contribute zero experimental conditions. P017 paper-native TRIP/TWIP, SIS-PSR, UTS-PSR, PTM descriptors, extreme MD strain rates, GSFE, and dislocation evolution are computational-only. Native computational labels are not experimental targets, and P017 cannot increase the experimental training count.

## Concrete current-paper decisions

- **P015 post-fracture HCP/phase state:** forbidden post-test predictor; target evidence only.
- **P015 YS/UTS, including engineering and true values:** forbidden same-test mechanical outcomes.
- **P014 HDI/back stress:** forbidden model/loading-derived predictor.
- **P013 strain-resolved SXRD and onset/landmark values:** stage/target evidence only.
- **P012 post-strain martensite/twin observations:** target evidence only.
- **P017 MD conditions and GSFE/stress-regime fields:** computational domain only.
- **P011 initial phase fractions:** potential pre-test predictors with phase/method scope.
- **P012 initial grain size:** pre-test predictor with grain-definition/method scope.

## Frozen feature-family progression

- **M1_CHEMISTRY:** untransformed pre-test chemistry source columns only; measured-first/nominal-fallback policy documented but not applied.
- **M2_CHEMISTRY_PLUS_TEST:** M1 plus planned test temperature, strain rate, and usable orientation/loading fields.
- **M3_PLUS_PROCESSING:** M2 plus eligible pre-test processing fields; route text remains unencoded.
- **M4_PLUS_PHYSICS:** M3 plus method-gated SFE, DeltaG, phase-stability, and related physics candidates; no generic SFE merge and no imputation.
- **M5_PLUS_INITIAL_MICROSTRUCTURE:** M4 plus explicitly pre-test phases, grain/twin/recrystallization/KAM/precipitate descriptors; no post-test field.

`feature_sets_v1.csv` lists raw candidate columns plus non-model method/scope controls. `feature_priority_v1.csv` distinguishes CORE_V1, OPTIONAL_V1, EXPLORATORY_LATER, and NOT_ELIGIBLE. No transformed training matrix exists.

## Readiness decision

1. **Ready for train/validation split design?** Yes—Feature Schema V1 is frozen enough to design grouped splits, because all 343 columns have a primary class and unsafe fields are blocked. This is not authorization to train.
2. **Initial baseline feature family:** M2_CHEMISTRY_PLUS_TEST is the recommended schema baseline for split design because it adds the planned mechanism-driving temperature/rate context without the sparse physics and detailed-microstructure families. Raw chemistry representation/conflict handling must be finalized before matrix construction.
3. **Too sparse for the baseline:** experimental SFE, DeltaG, detailed phase-stability descriptors, KAM/GOS, recrystallized fraction, local/measured chemistry, and several minor-element fields.
4. **Ablation-only:** method-specific DFT/MD/thermodynamic physics, magnetic/computational descriptors, local chemistry, and sparse detailed initial-microstructure descriptors.
5. **Permanently blocked:** targets/evidence, mechanical outcomes, post-test/stage observations, fitted/loading-derived quantities, identifiers/groups as features, provenance/QC as features, and P017-native computational fields in experimental models.

## Next gate

Design paper/study/material-aware train/validation splits using `Leakage_Group_Strict`, `Leakage_Group_Material`, `Study_Series_ID`, `Material_Parent_ID`, and paper identity strictly as grouping controls. Reconcile target-specific split feasibility and the documented measured-versus-nominal representation policy before constructing any predictor matrix. Do not train, impute, encode, normalize, synthesize, or calculate derived descriptors at this gate.
"""
    POLICY_PATH.write_text(text, encoding="utf-8")


def write_audit(
    schema: pd.DataFrame,
    feature_sets: pd.DataFrame,
    coverage: pd.DataFrame,
    target_availability: pd.DataFrame,
) -> None:
    counts = Counter(schema.Prediction_Time_Class)
    leakage_count = sum(counts[name] for name in (
        "POST_TEST_LEAKAGE", "MECHANICAL_OUTCOME_LEAKAGE", "MODEL_DERIVED_LEAKAGE"
    ))
    grouping_identifier = counts["GROUPING_ONLY"] + counts["IDENTIFIER_ONLY"]
    provenance_metadata = counts["PROVENANCE_ONLY"] + counts["METADATA_ONLY"]
    candidates = schema[schema.Prediction_Time_Class.isin({"PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"})]
    by_family = {
        family: candidates.loc[candidates.Scientific_Family.eq(family), "Column_Name"].tolist()
        for family in SAFE_FAMILY_COLUMNS
    }
    class_lines = "\n".join(f"- `{name}`: {counts[name]}" for name in ELIGIBILITY_CLASSES)
    coverage_lines = []
    for letter, (_, row) in zip("OPQRS", coverage.iterrows()):
        coverage_lines.append(
            f"### {letter}. {row.Feature_Set} coverage\n\n"
            f"Candidates: {int(row.Candidate_Feature_Count)}; CORE_V1 raw complete cases: "
            f"{int(row.Complete_Case_Count)}/51; median/min/max raw candidate coverage: "
            f"{row.Median_Feature_Coverage:.2f}%/{row.Minimum_Feature_Coverage:.2f}%/"
            f"{row.Maximum_Feature_Coverage:.2f}%. Bottleneck: {row.Major_Missingness_Bottleneck}."
        )
    target_lines = []
    for target in ("TRIP", "TWIP", "JOINT"):
        subset = target_availability[target_availability.Target.eq(target)]
        first = subset.iloc[0]
        cc = ", ".join(f"{r.Feature_Set}={int(r.Complete_Case_Count)}" for _, r in subset.iterrows())
        target_lines.append(
            f"- {target}: usable {int(first.Target_Usable_Conditions)}, positive {int(first.Target_Positive)}, "
            f"negative {int(first.Target_Negative)}; CORE_V1 complete cases by set: {cc}."
        )
    unresolved = schema.loc[schema.Prediction_Time_Class.eq("UNRESOLVED_REVIEW"), "Column_Name"].tolist()
    high_risk = schema.loc[
        schema.Prediction_Time_Class.isin({
            "TARGET_ONLY", "POST_TEST_LEAKAGE", "MECHANICAL_OUTCOME_LEAKAGE", "MODEL_DERIVED_LEAKAGE"
        }),
        "Column_Name",
    ].tolist()
    text = f"""# Feature Schema V1 Audit

Prediction moment: **{PREDICTION_MOMENT.lower()}**. This is schema design and descriptive coverage only; no training, transformation, imputation, normalization, encoding, or derived-alloy calculation occurred.

## A. Total master columns classified

{len(schema)} of {len(schema)} V12 master columns; no omissions or duplicates.

## B. Count by eligibility class

{class_lines}

## C. Safe direct predictors

{counts['PREDICTOR_SAFE_DIRECT']}.

## D. Safe conditional predictors

{counts['PREDICTOR_SAFE_CONDITIONAL']}.

## E. Leakage fields

{leakage_count}, defined as POST_TEST_LEAKAGE + MECHANICAL_OUTCOME_LEAKAGE + MODEL_DERIVED_LEAKAGE. Target-only fields are separately blocked and are not double-counted here.

## F. Computational-only fields

{counts['COMPUTATIONAL_ONLY']}.

## G. Grouping/identifier fields

{grouping_identifier} ({counts['GROUPING_ONLY']} grouping-only + {counts['IDENTIFIER_ONLY']} identifier-only).

## H. Provenance-only fields

{counts['PROVENANCE_ONLY']} provenance-only; {provenance_metadata} when metadata-only is included.

## I. Chemistry candidates

{format_list(by_family['CHEMISTRY'])}

Measured bulk, nominal, feedstock, and local representations remain separate. The measured-first/nominal-fallback policy is documented but not applied.

## J. Processing candidates

{format_list(by_family['PROCESSING'])}

## K. Test-condition candidates

{format_list(by_family['TEST_CONDITIONS'])}

No dedicated usable loading-mode column exists; loading direction is sparse. Specimen dimensions remain metadata-only.

## L. Initial-microstructure candidates

{format_list(by_family['INITIAL_MICROSTRUCTURE'])}

All are constrained to explicitly pre-test state; initial twins/HCP never establish TWIP/TRIP.

## M. Physics candidates

{format_list(by_family['PHYSICS_THERMODYNAMICS'])}

All method-sensitive physics candidates preserve temperature, structure, method, and domain distinctions. P017 GSFE is computational-only and is not a 343-column experimental candidate.

## N. Highest-risk leakage variables

{format_list(high_risk)}

These include direct targets/evidence in addition to the {leakage_count} post-test, mechanical-outcome, and model-derived fields.

{chr(10).join(coverage_lines)}

## T. Target-specific feature availability

{chr(10).join(target_lines)}

The joint positive definition is any of 10/01/11; the sole joint negative is 00. Complete cases are descriptive CORE_V1 raw-column intersections only.

## U. Unresolved schema fields

{len(unresolved)}. {format_list(unresolved)} Conservative metadata/leakage/domain decisions block ambiguous non-candidates rather than leaving them silently eligible.

## V. Exact recommendation before ML

Proceed only to grouped train/validation split design, using M2_CHEMISTRY_PLUS_TEST as the initial schema baseline and all paper/study/material identifiers solely as grouping controls. First predeclare measured-bulk-versus-nominal representation and target-specific group allocation; keep M4 physics and sparse M5 details for later ablation. Do not construct a training matrix, train, impute, encode, normalize, synthesize, or calculate derived descriptors in this phase.
"""
    AUDIT_PATH.write_text(text, encoding="utf-8")


def validate(
    master: pd.DataFrame,
    experimental_index: pd.DataFrame,
    computational_index: pd.DataFrame,
    experimental_rows: pd.DataFrame,
    schema: pd.DataFrame,
    feature_sets: pd.DataFrame,
    priority: pd.DataFrame,
    domain: pd.DataFrame,
    coverage: pd.DataFrame,
    target_availability: pd.DataFrame,
    source_hashes: dict[Path, str],
) -> None:
    assert len(master) == 192 and len(master.columns) == 343
    assert len(experimental_index) == len(experimental_rows) == 51
    assert len(computational_index) == 12 and set(computational_index.Paper_ID) == {"P017"}
    assert not set(experimental_index.Paper_ID) & {"P017", "P018", "P019"}
    assert experimental_rows.Effective_TRIP.notna().sum() == 32
    assert experimental_rows.Effective_TWIP.notna().sum() == 30
    assert experimental_rows[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum() == 27
    assert len(schema) == 343 and schema.Column_Name.is_unique
    assert list(schema.Column_Name) == list(master.columns)
    assert list(schema.columns) == SCHEMA_COLUMNS
    assert set(schema.Prediction_Time_Class) <= set(ELIGIBILITY_CLASSES)
    assert set(schema.Scientific_Family) <= set(SCIENTIFIC_FAMILIES)
    indexed = schema.set_index("Column_Name")
    assert indexed.loc["Effective_TRIP", "Prediction_Time_Class"] == "TARGET_ONLY"
    assert indexed.loc["Effective_TWIP", "Prediction_Time_Class"] == "TARGET_ONLY"
    assert indexed.loc["Leakage_Group_Strict", "Prediction_Time_Class"] == "GROUPING_ONLY"
    assert indexed.loc["Leakage_Group_Material", "Prediction_Time_Class"] == "GROUPING_ONLY"
    assert indexed.loc["YS_MPa", "Prediction_Time_Class"] == "MECHANICAL_OUTCOME_LEAKAGE"
    assert indexed.loc["Postfracture_HCP_fraction", "Prediction_Time_Class"] == "POST_TEST_LEAKAGE"
    assert indexed.loc["HDI_Hardening", "Prediction_Time_Class"] == "MODEL_DERIVED_LEAKAGE"
    assert indexed.loc["Paper_Native_TRIP", "Prediction_Time_Class"] == "COMPUTATIONAL_ONLY"
    assert indexed.loc["SIS_PSR_GPa", "Prediction_Time_Class"] == "COMPUTATIONAL_ONLY"
    assert indexed.loc["Test_T_K", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert indexed.loc["Strain_rate_s-1", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert indexed.loc["Processing_route", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert indexed.loc["Grain_size_um", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert len(priority) == 343 and priority.Column_Name.is_unique
    assert set(priority.Feature_Priority) <= {"CORE_V1", "OPTIONAL_V1", "EXPLORATORY_LATER", "NOT_ELIGIBLE"}
    assert set(feature_sets.Feature_Set) == set(FEATURE_SET_ORDER)
    assert len(domain) == 6 and set(domain.Dataset_Domain) == {
        "EXPERIMENTAL_PRIMARY", "EXPERIMENTAL_STAGE_SUPPORT", "COMPUTATIONAL_PRIMARY",
        "COMPUTATIONAL_STAGE_SUPPORT", "LEGACY_PRESERVED", "PROVENANCE_SUPPORT",
    }
    assert len(coverage) == 5 and coverage.Independent_Experimental_Conditions.eq(51).all()
    assert len(target_availability) == 15
    usable = target_availability.groupby("Target").Target_Usable_Conditions.first().to_dict()
    assert usable == {"JOINT": 27, "TRIP": 32, "TWIP": 30}
    assert not any(
        token in field.lower()
        for field in set(schema.Column_Name) - set(master.columns)
        for token in ("vec", "omega", "mixing_entropy", "mixing_enthalpy", "electronegativity", "normalized")
    )
    expected_outputs = {SCHEMA_PATH.name, FEATURE_SETS_PATH.name, PRIORITY_PATH.name, DOMAIN_PATH.name}
    assert {path.name for path in SCHEMA_DIR.glob("*") if path.is_file()} <= expected_outputs
    for path, digest in source_hashes.items():
        assert file_digest(path) == digest, f"Source artifact changed during schema generation: {path}"
    for path in (
        SCHEMA_PATH, FEATURE_SETS_PATH, PRIORITY_PATH, DOMAIN_PATH, COVERAGE_PATH,
        TARGET_AVAILABILITY_PATH, POLICY_PATH, AUDIT_PATH,
    ):
        assert path.exists() and path.stat().st_size > 0


def run() -> None:
    source_paths = (MASTER_PATH, EXPERIMENTAL_INDEX_PATH, COMPUTATIONAL_INDEX_PATH)
    source_hashes = {path: file_digest(path) for path in source_paths}
    master = pd.read_csv(MASTER_PATH, low_memory=False)
    experimental_index = pd.read_csv(EXPERIMENTAL_INDEX_PATH, low_memory=False)
    computational_index = pd.read_csv(COMPUTATIONAL_INDEX_PATH, low_memory=False)
    experimental_rows = master[master.QC_Row_Role.eq("EXPERIMENTAL_PRIMARY_CONDITION")].copy()

    assert set(experimental_rows.ML_Condition_ID) == set(experimental_index.ML_Condition_ID)
    experimental_rows = experimental_rows.set_index("ML_Condition_ID").loc[
        experimental_index.ML_Condition_ID
    ].reset_index()

    schema = build_schema(master, experimental_rows)
    priority = build_priority(schema, experimental_rows)
    feature_sets, members = build_feature_sets(schema, priority, experimental_rows)
    coverage = build_coverage(members, priority, experimental_rows)
    target_availability = build_target_availability(members, priority, experimental_rows)
    domain = build_domain_manifest(master)

    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    schema.to_csv(SCHEMA_PATH, index=False)
    feature_sets.to_csv(FEATURE_SETS_PATH, index=False)
    priority.to_csv(PRIORITY_PATH, index=False)
    domain.to_csv(DOMAIN_PATH, index=False)
    coverage.to_csv(COVERAGE_PATH, index=False)
    target_availability.to_csv(TARGET_AVAILABILITY_PATH, index=False)
    write_policy(schema)
    write_audit(schema, feature_sets, coverage, target_availability)

    validate(
        master, experimental_index, computational_index, experimental_rows, schema,
        feature_sets, priority, domain, coverage, target_availability, source_hashes,
    )


if __name__ == "__main__":
    run()
