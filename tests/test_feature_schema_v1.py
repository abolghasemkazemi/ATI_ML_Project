from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/processed/master_19papers_recovery_v12_qc.csv"
SOURCE = ROOT / "data/processed/master_19papers_recovery_v11.csv"
EXP_INDEX = ROOT / "data/processed/experimental_condition_index_v12.csv"
COMP_INDEX = ROOT / "data/processed/computational_condition_index_v12.csv"
SCHEMA_DIR = ROOT / "data/schema"
REPORTS = ROOT / "reports"

SCHEMA = SCHEMA_DIR / "feature_schema_v1.csv"
SETS = SCHEMA_DIR / "feature_sets_v1.csv"
PRIORITY = SCHEMA_DIR / "feature_priority_v1.csv"
DOMAIN = SCHEMA_DIR / "domain_manifest_v1.csv"
COVERAGE = REPORTS / "FEATURE_SET_COVERAGE_V1.csv"
TARGET_AVAILABILITY = REPORTS / "TARGET_FEATURE_AVAILABILITY_V1.csv"
POLICY = REPORTS / "PREDICTION_TIME_LEAKAGE_POLICY_V1.md"
AUDIT = REPORTS / "FEATURE_SCHEMA_V1_AUDIT.md"

ALLOWED_CLASSES = {
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
}

SAFE_CLASSES = {"PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"}

FEATURE_SET_ORDER = [
    "M1_CHEMISTRY",
    "M2_CHEMISTRY_PLUS_TEST",
    "M3_PLUS_PROCESSING",
    "M4_PLUS_PHYSICS",
    "M5_PLUS_INITIAL_MICROSTRUCTURE",
]


def load(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def schema_index() -> pd.DataFrame:
    return load(SCHEMA).set_index("Column_Name")


def test_every_v12_master_column_has_one_frozen_schema_row():
    master, schema = load(MASTER), load(SCHEMA)
    assert len(master) == 192 and len(master.columns) == 343
    assert len(schema) == 343
    assert schema.Column_Name.notna().all() and schema.Column_Name.is_unique
    assert list(schema.Column_Name) == list(master.columns)
    assert set(schema.Prediction_Time_Class) <= ALLOWED_CLASSES
    assert not schema.Prediction_Time_Class.eq("UNRESOLVED_REVIEW").any()
    assert schema[
        [
            "Data_Type", "Scientific_Family", "Prediction_Time_Class", "Proposed_Model_Role",
            "Experimental_Domain_Eligibility", "Computational_Domain_Eligibility",
            "Known_Before_Deformation", "Direct_Source_or_Derived", "Method_Sensitive",
            "Temperature_Sensitive", "Phase_Sensitive", "Potential_Leakage", "Leakage_Reason",
            "Missingness_Concern", "Scope_Constraint", "Recommended_V1_Action", "Notes",
        ]
    ].notna().all().all()


def test_effective_original_and_direct_mechanism_fields_are_target_only():
    schema = schema_index()
    for field in [
        "Effective_TRIP", "Effective_TWIP", "TRIP", "TWIP", "Original_TRIP", "Original_TWIP",
        "Recovered_TRIP", "Recovered_TWIP", "Evidence_TRIP", "Evidence_TWIP",
        "Dominant_mechanism", "Slip", "Stacking_faulting",
    ]:
        assert schema.loc[field, "Prediction_Time_Class"] == "TARGET_ONLY"
        assert "PREDICTOR" not in schema.loc[field, "Proposed_Model_Role"]


def test_identifiers_and_grouping_keys_never_become_predictors():
    schema = schema_index()
    for field in ["Paper_ID", "DOI", "ML_Condition_ID", "Condition_ID", "Observation_ID"]:
        assert schema.loc[field, "Prediction_Time_Class"] == "IDENTIFIER_ONLY"
        assert "PREDICTOR" not in schema.loc[field, "Proposed_Model_Role"]
    for field in [
        "Leakage_Group_Strict", "Leakage_Group_Material", "Study_Series_ID",
        "Material_Parent_ID", "Physical_Batch_ID", "Replicate_ID", "Parent_ML_Condition_ID",
    ]:
        assert schema.loc[field, "Prediction_Time_Class"] == "GROUPING_ONLY"
        assert schema.loc[field, "Proposed_Model_Role"] == "SPLIT_AND_DEPENDENCE_CONTROL_ONLY"


def test_same_test_mechanics_true_properties_and_fracture_mode_are_blocked():
    schema = schema_index()
    fields = [
        "YS_MPa", "YS_error_MPa", "UTS_MPa", "UTS_error_MPa", "Elongation_pct",
        "Elongation_error_pct", "Uniform_elongation_pct", "Recovered_YS_MPa",
        "Recovered_UTS_MPa", "Recovered_Elongation_pct", "Recovered_Uniform_elongation_pct",
        "YS_mean", "UTS_mean", "TE_mean", "UE_mean", "Engineering_YS_MPa",
        "Engineering_UTS_MPa", "Engineering_Elongation_pct", "True_Yield_Stress_MPa",
        "True_UTS_MPa", "Fracture_Mode",
    ]
    for field in fields:
        assert schema.loc[field, "Prediction_Time_Class"] == "MECHANICAL_OUTCOME_LEAKAGE"
        assert schema.loc[field, "Recommended_V1_Action"] == "PERMANENTLY_BLOCK_FROM_PRIMARY_PREDICTORS"


def test_post_test_phase_twin_stage_and_kam_scope_are_blocked():
    schema = schema_index()
    for field in [
        "Postfracture_Phase_State", "Postfracture_HCP_fraction", "Postfracture_HCP_fraction_Status",
        "HCP_fraction_at_condition", "Deformation_Twin_thickness_nm", "Deformation_twin_width",
        "Deformation_twin_spacing", "FCC_fraction_at_stage", "TWIP_at_stage", "TRIP_at_stage",
        "Slip_at_stage", "GND_density_m-2", "Observed_Microstructure",
    ]:
        assert schema.loc[field, "Prediction_Time_Class"] == "POST_TEST_LEAKAGE"

    # KAM_mean_deg contains explicitly initial P014 values and post-test P011
    # stage values. Its conditional class therefore requires a strict row/scope
    # gate; post-test KAM is never eligible.
    assert schema.loc["KAM_mean_deg", "Prediction_Time_Class"] == "PREDICTOR_SAFE_CONDITIONAL"
    assert "P011 interrupted/fracture-stage KAM is post-test and excluded" in schema.loc["KAM_mean_deg", "Scope_Constraint"]
    master = load(MASTER)
    post_kam = master.KAM_mean_deg.notna() & master.QC_Row_Role.eq("EXPERIMENTAL_STAGE_CHILD")
    assert post_kam.any()
    assert master.loc[post_kam, "ML_Condition_ID"].isna().all()
    assert "post-test KAM/GOS" in POLICY.read_text(encoding="utf-8")


def test_hdi_back_stress_and_model_inferred_loading_fields_are_blocked():
    schema = schema_index()
    for field in [
        "HDI_at_stage", "HDI_Hardening", "Critical_twin_stress_MPa",
        "Critical_TRIP_stress_MPa", "Twin_onset_true_strain", "TRIP_onset_true_strain",
        "Adiabatic_temperature_K", "SFE_increase_dynamic_mJ_m2", "HC",
    ]:
        assert schema.loc[field, "Prediction_Time_Class"] == "MODEL_DERIVED_LEAKAGE"
    policy = POLICY.read_text(encoding="utf-8")
    assert "HDI/back stress" in policy
    assert "inferred onsets" in policy


def test_p017_native_targets_stress_regimes_and_gsfe_are_computational_only():
    schema = schema_index()
    for field in [
        "Paper_Native_TRIP", "Paper_Native_TWIP", "SIS_PSR_GPa", "UTS_PSR_GPa",
        "TWIP_induced_TRIP_Status", "TRIP_induced_TWIP_Status", "Initial_BCC_fraction_raw",
        "PostQuench_Initial_Structure",
    ]:
        assert schema.loc[field, "Prediction_Time_Class"] == "COMPUTATIONAL_ONLY"
        assert schema.loc[field, "Experimental_Domain_Eligibility"] == "NOT_ELIGIBLE_EXPERIMENTAL_DOMAIN"
    policy = POLICY.read_text(encoding="utf-8")
    assert "P017 GSFE is **COMPUTATIONAL_ONLY**" in policy
    domain = load(DOMAIN).set_index("Dataset_Domain")
    assert "P017 GSFE" in domain.loc["COMPUTATIONAL_PRIMARY", "Notes"]


def test_initial_grain_test_conditions_and_processing_route_can_be_pretest_predictors():
    schema = schema_index()
    for field in ["Grain_size_um", "Test_T_K", "Strain_rate_s-1", "Processing_route"]:
        assert schema.loc[field, "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
        assert schema.loc[field, "Known_Before_Deformation"] == "YES"
    assert schema.loc["Initial_FCC_fraction", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert schema.loc["Initial_HCP_fraction", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert "never establish tensile TRIP" in schema.loc["Initial_HCP_fraction", "Scope_Constraint"]


def test_nominal_measured_local_and_feedstock_chemistry_remain_distinct():
    schema = schema_index()
    assert schema.loc["Nominal_Composition_at_pct", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert schema.loc["Measured_Composition_at_pct", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    assert schema.loc["Recovered_Bulk_Composition_at_pct", "Prediction_Time_Class"] == "PREDICTOR_SAFE_DIRECT"
    for field in ["APT_local_composition", "EDS_local_composition", "Local_EDS_Composition_at_pct", "Feedstock_Composition_at_pct"]:
        assert schema.loc[field, "Prediction_Time_Class"] == "PREDICTOR_SAFE_CONDITIONAL"
    assert "not bulk composition" in schema.loc["APT_local_composition", "Scope_Constraint"]
    assert "not automatically specimen bulk" in schema.loc["Feedstock_Composition_at_pct", "Scope_Constraint"]
    policy = POLICY.read_text(encoding="utf-8")
    assert "if explicitly measured **bulk specimen/material chemistry** exists, prefer it" in policy
    assert "otherwise use explicitly nominal chemistry" in policy
    assert "does **not** merge the fields" in policy


def test_experimental_calculated_assumed_and_computational_sfe_are_not_collapsed():
    schema = schema_index()
    assert schema.loc["SFE_mJ_m2", "Prediction_Time_Class"] == "PREDICTOR_SAFE_CONDITIONAL"
    assert schema.loc["Recovered_ISFE_DFT_0K_mJ_m2", "Prediction_Time_Class"] == "PREDICTOR_SAFE_CONDITIONAL"
    assert schema.loc["Recovered_SFE_assumed_for_calculation_mJ_m2", "Prediction_Time_Class"] == "METADATA_ONLY"
    assert schema.loc["SFE_method", "Prediction_Time_Class"] == "PROVENANCE_ONLY"
    assert schema.loc["SFE_Data_Origin", "Prediction_Time_Class"] == "PROVENANCE_ONLY"
    assert "DFT intrinsic SFE at 0 K" in schema.loc["Recovered_ISFE_DFT_0K_mJ_m2", "Scope_Constraint"]
    assert "P016 assumed model input" in schema.loc["Recovered_SFE_assumed_for_calculation_mJ_m2", "Scope_Constraint"]
    policy = POLICY.read_text(encoding="utf-8")
    for phrase in ["thermodynamic/CALPHAD SFE", "DFT 0 K SFE", "MD SFE", "FCC stable gamma_sf", "BCC unstable gamma_usf"]:
        assert phrase in policy


def test_feature_set_manifest_is_cumulative_and_contains_only_safe_candidates():
    schema = schema_index()
    sets = load(SETS)
    assert list(sets.Feature_Set.drop_duplicates()) == FEATURE_SET_ORDER
    candidate_counts = []
    previous = set()
    for feature_set in FEATURE_SET_ORDER:
        block = sets[sets.Feature_Set.eq(feature_set)]
        candidates = set(block.loc[block.Eligibility_Status.ne("CONTROL_ONLY_NOT_MODEL_FEATURE"), "Column_Name"])
        controls = set(block.loc[block.Eligibility_Status.eq("CONTROL_ONLY_NOT_MODEL_FEATURE"), "Column_Name"])
        assert previous <= candidates
        assert candidates.isdisjoint(controls)
        assert set(schema.loc[list(candidates), "Prediction_Time_Class"]) <= SAFE_CLASSES
        assert not set(schema.loc[list(controls), "Proposed_Model_Role"]) & {"CANDIDATE_PREDICTOR", "CONDITIONAL_CANDIDATE_PREDICTOR"}
        candidate_counts.append(len(candidates))
        previous = candidates
    assert candidate_counts == [26, 31, 50, 70, 105]
    m1 = sets[sets.Feature_Set.eq("M1_CHEMISTRY")]
    assert {"Nominal_Composition_at_pct", "Measured_Composition_at_pct"} <= set(m1.Column_Name)
    assert m1.loc[m1.Column_Name.eq("Nominal_Composition_at_pct"), "Column_Name"].iloc[0] != m1.loc[m1.Column_Name.eq("Measured_Composition_at_pct"), "Column_Name"].iloc[0]


def test_feature_priority_covers_every_column_and_is_scientifically_gated():
    priority, schema = load(PRIORITY), schema_index()
    assert len(priority) == 343 and priority.Column_Name.is_unique
    assert set(priority.Feature_Priority) == {"CORE_V1", "OPTIONAL_V1", "EXPLORATORY_LATER", "NOT_ELIGIBLE"}
    p = priority.set_index("Column_Name")
    for field in ["Fe_at%", "Mn_at%", "Co_at%", "Cr_at%", "Test_T_K", "Strain_rate_s-1", "Processing_route", "Grain_size_um"]:
        assert p.loc[field, "Feature_Priority"] == "CORE_V1"
    for field in ["SFE_mJ_m2", "DeltaG_FCC_HCP_J_mol", "Recovered_ISFE_DFT_0K_mJ_m2"]:
        assert p.loc[field, "Feature_Priority"] == "EXPLORATORY_LATER"
    unsafe = schema[~schema.Prediction_Time_Class.isin(SAFE_CLASSES)].index
    assert p.loc[unsafe, "Feature_Priority"].eq("NOT_ELIGIBLE").all()


def test_m1_to_m5_coverage_is_descriptive_and_no_imputation_is_claimed():
    coverage = load(COVERAGE).set_index("Feature_Set")
    assert list(coverage.index) == FEATURE_SET_ORDER
    assert coverage.Independent_Experimental_Conditions.eq(51).all()
    assert coverage.Candidate_Feature_Count.tolist() == [26, 31, 50, 70, 105]
    assert coverage.Complete_Case_Count.tolist() == [40, 31, 31, 31, 26]
    assert coverage.Leakage_Free_Status.eq("PASS_FROZEN_PREDICTION_TIME_POLICY").all()
    assert coverage.Notes.str.contains("no imputation or transformation occurred", case=False).all()


def test_target_specific_availability_preserves_counts_and_joint_semantics():
    availability = load(TARGET_AVAILABILITY)
    assert len(availability) == 15
    assert set(availability.Feature_Set) == set(FEATURE_SET_ORDER)
    first = availability.groupby("Target", sort=False).first()
    assert first.loc["TRIP", ["Target_Usable_Conditions", "Target_Positive", "Target_Negative"]].tolist() == [32, 27, 5]
    assert first.loc["TWIP", ["Target_Usable_Conditions", "Target_Positive", "Target_Negative"]].tolist() == [30, 24, 6]
    assert first.loc["JOINT", ["Target_Usable_Conditions", "Target_Positive", "Target_Negative"]].tolist() == [27, 26, 1]
    assert availability.Notes.str.contains("No imputation", case=False).all()


def test_domain_manifest_preserves_51_experimental_and_12_computational_conditions():
    domain = load(DOMAIN).set_index("Dataset_Domain")
    assert set(domain.index) == {
        "EXPERIMENTAL_PRIMARY", "EXPERIMENTAL_STAGE_SUPPORT", "COMPUTATIONAL_PRIMARY",
        "COMPUTATIONAL_STAGE_SUPPORT", "LEGACY_PRESERVED", "PROVENANCE_SUPPORT",
    }
    assert domain.loc["EXPERIMENTAL_PRIMARY", "Current_Row_Count"] == 51
    assert domain.loc["COMPUTATIONAL_PRIMARY", "Current_Row_Count"] == 12
    assert "NEVER EXPERIMENTAL TRAINING ROWS" in domain.loc["COMPUTATIONAL_PRIMARY", "Training_Eligibility"]
    exp, comp = load(EXP_INDEX), load(COMP_INDEX)
    assert len(exp) == 51 and len(comp) == 12
    assert not set(exp.Paper_ID) & {"P017", "P018", "P019"}
    assert set(comp.Paper_ID) == {"P017"}


def test_source_scientific_dataset_is_unchanged_and_no_engineered_column_exists():
    source, master, schema = load(SOURCE), load(MASTER), load(SCHEMA)
    assert len(source) == len(master) == 192
    pd.testing.assert_frame_equal(master[source.columns], source, check_dtype=False)
    assert master[source.columns].isna().equals(source.isna())
    assert set(schema.Column_Name) == set(master.columns)
    assert not set(schema.Column_Name) - set(master.columns)
    added = set(master.columns) - set(source.columns)
    assert added == {
        "QC_Row_Role", "QC_Experimental_Eligibility", "QC_Computational_Eligibility",
        "QC_Target_Eligibility", "QC_Duplicate_Status", "QC_Leakage_Risk",
        "QC_Leakage_Category", "QC_Source_Completeness", "QC_Review_Status",
    }
    forbidden_new = [
        "VEC", "Omega", "Mixing_Entropy", "Mixing_Enthalpy", "Electronegativity_Mismatch",
        "Normalized_Composition", "Atomic_Size_Mismatch",
    ]
    assert not any(any(token.lower() in field.lower() for token in forbidden_new) for field in added)


def test_no_transformed_training_matrix_or_extra_schema_artifact_is_created():
    expected = {
        "feature_schema_v1.csv", "feature_sets_v1.csv", "feature_priority_v1.csv",
        "domain_manifest_v1.csv", "feature_schema_v2.csv",
    }
    files = {path.name for path in SCHEMA_DIR.iterdir() if path.is_file()}
    assert files == expected
    # V2 is a column-role manifest for the V17 QC refresh, not a transformed
    # training matrix. Pilot matrices remain isolated under data/modeling/.
    v2 = pd.read_csv(SCHEMA_DIR / "feature_schema_v2.csv", low_memory=False)
    assert {"Column_Name", "Schema_Role", "CORE_M2"} <= set(v2.columns)
    assert not any("matrix" in name.lower() for name in files)
    assert not any(any(token in name.lower() for token in ["matrix", "encoded", "imputed", "normalized", "train"]) for name in files)


def test_policy_and_audit_freeze_prediction_moment_examples_and_readiness():
    policy = POLICY.read_text(encoding="utf-8")
    assert "immediately before tensile loading begins" in policy.lower()
    assert "pre-deformation condition-level mechanism prediction" in policy.lower()
    for phrase in [
        "P015 post-fracture HCP", "P015 YS/UTS", "P014 HDI/back stress",
        "P013 strain-resolved SXRD", "P012 post-strain martensite/twin observations",
        "P017 MD conditions", "P011 initial phase fractions", "P012 initial grain size",
    ]:
        assert phrase in policy
    assert "M2_CHEMISTRY_PLUS_TEST is the recommended schema baseline" in policy
    assert "This is not authorization to train" in policy

    audit = AUDIT.read_text(encoding="utf-8")
    for letter in "ABCDEFGHIJKLMNOPQRSTUV":
        assert f"## {letter}." in audit or f"### {letter}." in audit
    assert "343 of 343 V12 master columns" in audit
    assert "Proceed only to grouped train/validation split design" in audit


def test_all_required_feature_schema_v1_outputs_exist():
    for path in [SCHEMA, SETS, PRIORITY, DOMAIN, POLICY, COVERAGE, TARGET_AVAILABILITY, AUDIT]:
        assert path.exists() and path.stat().st_size > 0, path
