import hashlib

import pandas as pd
import pytest

from scripts.integrate_p022_recovery_v16 import (
    AUDIT,
    BOOK,
    BOOK_SHA256,
    CONDITION_BY_ALLOY,
    DOI,
    EXACT_IDS,
    FORMULAS,
    MATERIALS,
    OUT,
    PAPER_ID,
    SERIES,
    SOURCE,
    SOURCE_SHA256,
    STAGE_IDS,
    TABLE,
    TITLE,
    class_counts,
    counts,
    duplicate_rows,
    integrate,
)


@pytest.fixture(scope="module")
def recovered():
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    book_hash = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    source, out = integrate()
    assert (
        hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        == source_hash
        == SOURCE_SHA256
    )
    assert (
        hashlib.sha256(BOOK.read_bytes()).hexdigest()
        == book_hash
        == BOOK_SHA256
    )
    return source, out


def primary_rows(out: pd.DataFrame) -> pd.DataFrame:
    rows = out[
        out.Paper_ID.eq(PAPER_ID)
        & out.Observation_Role.eq("INDEPENDENT_CONDITION")
    ].copy()
    assert len(rows) == 5
    return rows.set_index("ML_Condition_ID", drop=False)


def stage_rows(out: pd.DataFrame) -> pd.DataFrame:
    rows = out[
        out.Paper_ID.eq(PAPER_ID)
        & out.Observation_Role.eq("CORRELATED_STAGE_CHILD")
    ].copy()
    assert len(rows) == 3
    return rows.set_index("Observation_ID", drop=False)


def load_table(name: str) -> pd.DataFrame:
    return pd.read_csv(
        TABLE / f"p022_recovery_v16_{name}.csv",
        low_memory=False,
    )


def test_source_identity_duplicate_check_and_immutable_v15_prefix(recovered):
    source, out = recovered
    assert duplicate_rows(source).empty
    assert not source.Paper_ID.eq(PAPER_ID).any()
    assert len(out) == len(source) + 8
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    identity = load_table("study_identity").iloc[0]
    assert identity.Paper_ID == PAPER_ID
    assert identity.DOI == DOI
    assert identity.Title == TITLE
    assert identity.Journal == "Journal of Materials Science"
    assert int(identity.Volume) == 55
    assert int(identity.Issue) == 5
    assert str(identity.Pages) == "2239-2244"
    assert int(identity.Year) == 2020
    assert identity.Data_Origin == "EXPERIMENTAL"
    assert (
        identity.Source_Identity_Status
        == "VERIFIED_PDF_AND_EXTERNAL_BIBLIOGRAPHIC_MATCH"
    )


def test_written_v16_roundtrip_preserves_every_v15_source_cell(recovered):
    source, _ = recovered
    written = pd.read_csv(OUT, low_memory=False)
    pd.testing.assert_frame_equal(
        written.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )


def test_five_material_parents_and_five_primary_conditions(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert tuple(rows.index) == EXACT_IDS
    assert set(rows.Material_Parent_ID) == set(MATERIALS.values())
    assert rows.Study_Series_ID.eq(SERIES).all()
    assert rows.Leakage_Group_Strict.eq(SERIES).all()
    for alloy, condition_id in CONDITION_BY_ALLOY.items():
        row = rows.loc[condition_id]
        assert row.Material_Parent_ID == MATERIALS[alloy]
        assert row.Leakage_Group_Material == MATERIALS[alloy]
    parents = load_table("material_parents")
    assert len(parents) == 5
    assert set(parents.Material_Parent_ID) == set(MATERIALS.values())


def test_all_primary_rows_are_independent_without_pseudo_replicates(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Observation_Role.eq("INDEPENDENT_CONDITION").all()
    assert rows.Independent_ML_sample.eq(True).all()
    assert rows.Independent_Experimental_ML_sample.eq(True).all()
    assert rows.Experimental_Target_Eligibility.eq(True).all()
    assert rows.Parent_Experiment_ID.eq(rows.ML_Condition_ID).all()
    assert rows.Parent_ML_Condition_ID.eq(rows.ML_Condition_ID).all()
    assert rows.Observation_ID.nunique() == 5
    assert rows.Physical_Batch_ID.isna().all()
    assert rows.Replicate_ID.isna().all()
    assert rows.Replicate_n.isna().all()
    hierarchy = load_table("condition_hierarchy")
    assert hierarchy.Pseudo_Replicate_Status.eq(
        "NO_PSEUDO_REPLICATES_CREATED"
    ).all()
    assert not hierarchy.Condition_ID.str.contains("REP", case=False).any()


def test_raw_atomic_ratio_formulas_remain_exact_and_unnormalized(recovered):
    _, out = recovered
    rows = primary_rows(out)
    for alloy, condition_id in CONDITION_BY_ALLOY.items():
        row = rows.loc[condition_id]
        assert row.Original_Composition == FORMULAS[alloy]
        assert row.Original_Composition_Basis == "ATOMIC_RATIO_AS_REPORTED"
        assert row.Composition_basis == "ATOMIC_RATIO_AS_REPORTED"
    assert tuple(rows.Original_Composition) == tuple(FORMULAS.values())
    assert rows.Nominal_Composition_at_pct.isna().all()
    assert rows.Normalized_Composition_at_pct.isna().all()
    for field in ["Fe_at%", "Mn_at%", "Co_at%", "Cr_at%", "C_at%", "Mo_at%"]:
        assert rows[field].isna().all()
    assert rows.Composition_Normalization_Status.eq(
        "NOT_NORMALIZED_RECOVERY_PRESERVES_ATOMIC_RATIO_FORMULA"
    ).all()
    formulas = load_table("raw_composition_formulas")
    assert tuple(formulas.Original_Composition_Formula) == tuple(
        FORMULAS.values()
    )
    assert formulas.Normalized_at_pct.isna().all()


def test_measured_bulk_chemistry_remains_missing(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Measured_Bulk_Composition.isna().all()
    assert rows.Measured_Composition_at_pct.isna().all()
    assert rows.Recovered_Bulk_Composition_at_pct.isna().all()
    assert rows.Composition_Status.eq(
        "NOMINAL_ORIGINAL_ATOMIC_RATIO_ONLY_NO_QUANTITATIVE_"
        "POSTMELT_BULK_CHEMISTRY_REPORTED"
    ).all()


def test_as_cast_processing_and_missing_test_metadata(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Processing_State.eq("AS_CAST").all()
    assert rows.Raw_Material_Purity.eq(">99.9 wt.%").all()
    assert rows.Melting_Route.str.contains(
        "Ti-gettered high-purity Ar", regex=False
    ).all()
    assert rows.Melting_Route.str.contains(
        "water-cooled Cu crucible", regex=False
    ).all()
    assert rows.Remelt_Count_Min.astype(float).eq(5).all()
    assert rows.Remelt_Count_Status.eq("AT_LEAST_FIVE").all()
    assert rows.Homogenization_T_K.isna().all()
    assert rows.Hot_rolling_T_K.isna().all()
    assert rows.Annealing_T_K.isna().all()
    assert rows.Test_T_Raw.eq("room temperature").all()
    assert rows.Test_T_K.isna().all()
    assert rows.Test_T_C.isna().all()
    assert rows["Strain_rate_s-1"].isna().all()
    assert rows.Strain_Rate_Status.eq("NOT_REPORTED").all()
    assert rows.Loading_Mode.eq("Uniaxial tension").all()
    assert rows.Flat_Tensile_Specimen_Dimensions_mm.eq(
        "22 x 2.5 x 1.5"
    ).all()
    assert rows[["Gauge_length_mm", "Gauge_width_mm", "Specimen_thickness_mm"]].isna().all().all()


def test_c0_initial_fcc_hcp_does_not_itself_generate_trip(recovered):
    _, out = recovered
    row = primary_rows(out).loc[CONDITION_BY_ALLOY["C0"]]
    assert row.Initial_Phase == "FCC_PLUS_HCP"
    assert pd.isna(row.Initial_FCC_fraction)
    assert pd.isna(row.Initial_HCP_fraction)
    assert row.Initial_HCP_Origin == "PRE_EXISTING_AS_CAST"
    assert (
        row.Initial_HCP_Target_Guardrail
        == "INITIAL_HCP_IS_NOT_DEFORMATION_INDUCED_TRIP_EVIDENCE"
    )
    assert float(row.Effective_TRIP) == 1
    assert row.TRIP_Evidence_Type.startswith("AUTHOR_CONDITION_ATTRIBUTION")


def test_single_fcc_states_have_hcp_zero_without_fabricated_fcc_fraction(recovered):
    _, out = recovered
    rows = primary_rows(out)
    ids = [
        CONDITION_BY_ALLOY["C2"],
        CONDITION_BY_ALLOY["C4"],
        CONDITION_BY_ALLOY["C2Mo1"],
        CONDITION_BY_ALLOY["C2Mo2"],
    ]
    assert rows.loc[ids, "Initial_HCP_fraction"].astype(float).eq(0).all()
    assert rows.loc[ids, "Initial_FCC_fraction"].isna().all()
    assert not rows.Initial_FCC_fraction.eq(1).any()
    assert rows.Grain_size_um.isna().all()


def test_c4_carbides_and_c2mo2_sigma_safeguard(recovered):
    _, out = recovered
    rows = primary_rows(out)
    c4 = rows.loc[CONDITION_BY_ALLOY["C4"]]
    assert c4.Initial_Phase == "XRD_SINGLE_FCC_MATRIX"
    assert (
        c4.Initial_Secondary_Phase
        == "CARBIDES_IN_INTERDENDRITIC_REGION_DIRECT_SEM"
    )
    assert (
        c4.C4_Carbide_XRD_Coexistence_Safeguard
        == "XRD_SINGLE_FCC_MATRIX_DOES_NOT_ERASE_DIRECT_SEM_CARBIDES"
    )
    c2mo2 = rows.loc[CONDITION_BY_ALLOY["C2Mo2"]]
    assert (
        c2mo2.Sigma_Phase_Evidence_Status
        == "PRIOR_WORK_POSSIBILITY_NOT_CURRENT_PAPER_MEASUREMENT"
    )


def test_dendrite_morphologies_are_qualitative_only(recovered):
    _, out = recovered
    rows = primary_rows(out)
    expected_fragments = {
        "C0": "dendritic",
        "C2": "Equiaxed/columnar",
        "C4": "carbides",
        "C2Mo1": "More uniform and finer equiaxed",
        "C2Mo2": "Non-equiaxed / striped",
    }
    for alloy, fragment in expected_fragments.items():
        assert fragment.lower() in str(
            rows.loc[CONDITION_BY_ALLOY[alloy], "Dendrite_Morphology"]
        ).lower()
    assert rows.Grain_size_um.isna().all()


def test_c0_trip_is_medium_author_attributed_and_twip_unresolved(recovered):
    _, out = recovered
    row = primary_rows(out).loc[CONDITION_BY_ALLOY["C0"]]
    assert float(row.Effective_TRIP) == 1
    assert pd.isna(row.Effective_TWIP)
    assert pd.isna(row.Slip)
    assert row.Target_Evidence_Confidence == "MEDIUM"
    assert (
        row.Author_Attributed_Target_Evidence_Grade
        == "MEDIUM_AUTHOR_ATTRIBUTED_NOT_DIRECT_POSTTEST_PHASE_MAP"
    )
    assert (
        row.TRIP_Evidence_Type
        == "AUTHOR_CONDITION_ATTRIBUTION_CROSS_REFERENCED_TO_ESTABLISHED_BASE_ALLOY"
    )


def test_direct_twip_conditions_keep_trip_unresolved(recovered):
    _, out = recovered
    rows = primary_rows(out)
    ids = [
        CONDITION_BY_ALLOY["C2"],
        CONDITION_BY_ALLOY["C2Mo1"],
        CONDITION_BY_ALLOY["C2Mo2"],
    ]
    assert rows.loc[ids, "Effective_TWIP"].astype(float).eq(1).all()
    assert rows.loc[ids, "Effective_TRIP"].isna().all()
    assert rows.loc[ids, "Slip"].isna().all()
    assert rows.loc[ids, "Target_Evidence_Confidence"].eq("HIGH").all()
    assert rows.loc[ids, "Twin_Boundary_Character"].eq(
        "APPROXIMATELY_60_DEGREE_<111>_DEFORMATION_TWIN_BOUNDARIES"
    ).all()


def test_c4_targets_and_all_negative_labels_remain_unresolved(recovered):
    _, out = recovered
    rows = primary_rows(out)
    c4 = rows.loc[CONDITION_BY_ALLOY["C4"]]
    assert c4[["Effective_TRIP", "Effective_TWIP", "Slip"]].isna().all()
    assert c4.Negative_Evidence_Status == "INSUFFICIENT_FOR_ZERO"
    assert not rows.Effective_TRIP.eq(0).any()
    assert not rows.Effective_TWIP.eq(0).any()
    assert rows.TRIP_to_TWIP_Negative_Safeguard.eq(
        "MECHANISM_SHIFT_WORDING_DOES_NOT_GENERATE_TRIP_ZERO"
    ).all()


def test_exact_three_40pct_ebsd_children_are_non_independent(recovered):
    _, out = recovered
    rows = stage_rows(out)
    assert tuple(rows.index) == STAGE_IDS
    assert rows.Local_Strain_pct.astype(float).eq(40).all()
    assert rows.Stage_Method.eq("EBSD/IPF + misorientation").all()
    assert rows.TWIP_Stage.astype(float).eq(1).all()
    assert rows.TRIP_Stage.isna().all()
    assert rows.Observation_Role.eq("CORRELATED_STAGE_CHILD").all()
    assert rows.Independent_ML_sample.eq(False).all()
    assert rows.Independent_Experimental_ML_sample.eq(False).all()
    assert rows.Experimental_Target_Eligibility.eq(False).all()
    assert rows.ML_Condition_ID.isna().all()
    assert rows.Parent_ML_Condition_ID.notna().all()
    assert rows.Twin_fraction_or_Sigma3.isna().all()
    assert rows.Twin_Fraction_Status.eq(
        "QUALITATIVE_POPULATION_ONLY_NO_FRACTION_DIGITIZED"
    ).all()


def test_qualitative_twin_population_order_is_preserved(recovered):
    _, out = recovered
    rows = stage_rows(out)
    assert (
        rows.loc["P022_C2MO1_EBSD_40", "Twin_Population_Qualitative"]
        == "LARGEST_AMONG_C2_C2MO1_C2MO2_QUALITATIVE"
    )
    assert rows.loc[
        ["P022_C2_EBSD_40", "P022_C2MO2_EBSD_40"],
        "Twin_Population_Qualitative",
    ].eq("LOWER_THAN_C2MO1_QUALITATIVE").all()


def test_only_direct_text_mechanics_are_recovered_as_approximate_leakage(recovered):
    _, out = recovered
    rows = primary_rows(out)
    c2 = rows.loc[CONDITION_BY_ALLOY["C2"]]
    c2mo1 = rows.loc[CONDITION_BY_ALLOY["C2Mo1"]]
    assert (float(c2.Engineering_UTS_MPa), float(c2.Engineering_Elongation_pct)) == (
        600.0,
        67.4,
    )
    assert (
        float(c2mo1.Engineering_UTS_MPa),
        float(c2mo1.Engineering_Elongation_pct),
    ) == (658.0, 89.8)
    assert c2.Mechanical_Value_Status == "APPROX_DIRECT_TEXT"
    assert c2mo1.Mechanical_Value_Status == "APPROX_DIRECT_TEXT"
    other_ids = [
        CONDITION_BY_ALLOY["C0"],
        CONDITION_BY_ALLOY["C4"],
        CONDITION_BY_ALLOY["C2Mo2"],
    ]
    numeric = [
        "Engineering_YS_MPa",
        "Engineering_UTS_MPa",
        "Engineering_Elongation_pct",
    ]
    assert rows.loc[other_ids, numeric].isna().all().all()
    assert rows.Engineering_YS_MPa.isna().all()
    assert rows.Mechanical_Predictor_Eligibility.eq(
        "MECHANICAL_OUTCOME_LEAKAGE"
    ).all()
    assert rows.Figure3_Digitization_Status.eq(
        "NOT_DIGITIZED_TEXT_ONLY_VALUES_WHERE_EXPLICIT"
    ).all()
    assert not rows[numeric].eq(47.2).any().any()


def test_numeric_sfe_and_deltag_remain_missing_with_threshold_safeguards(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.SFE_mJ_m2.isna().all()
    assert rows.SFE_method.isna().all()
    assert rows.DeltaG_FCC_HCP_J_mol.isna().all()
    assert rows.DeltaG_method.isna().all()
    assert rows.SFE_General_Threshold_Status.eq(
        "SECONDARY_GENERAL_THRESHOLDS_NOT_ASSIGNED_TO_P022_CONDITIONS"
    ).all()
    assert (
        rows.loc[
            CONDITION_BY_ALLOY["C2Mo1"], "SFE_Qualitative_Trend"
        ]
        == "C2MO1_MAY_HAVE_REDUCED_SFE_FROM_COMBINED_C_MO_EFFECT_"
        "QUALITATIVE_DIRECTION_ONLY"
    )
    physics = load_table("sfe_physics_safeguards")
    threshold = physics[
        physics.Status.eq("SECONDARY_GENERAL_THRESHOLD_NOT_CURRENT_ALLOY_VALUE")
    ]
    assert set(threshold.Recovered_Value_Raw.astype(str)) == {"15-45", "<15"}
    assert threshold.Recovered_Value.isna().all()
    assert threshold.Predictor_Eligibility.eq(
        "SUPPORT_ONLY_NOT_CONDITION_VALUE"
    ).all()
    assert physics.Condition_Assignment_Status.eq(
        "NOT_ASSIGNED_TO_ANY_P022_CONDITION_AS_NUMERIC_SFE_OR_DELTAG"
    ).all()


def test_every_new_master_field_and_support_value_has_provenance(recovered):
    _, out = recovered
    provenance = load_table("provenance")
    required = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
        "ML_Condition_ID",
        "Observation_ID",
        "Feature_Name",
        "Recovered_Value",
        "Units",
        "Evidence_Type",
        "Evidence_Location",
        "Method",
        "Confidence",
        "Recovery_Status",
        "Data_Origin",
    ]
    assert provenance[required].notna().all().all()
    assert provenance.Paper_ID.eq(PAPER_ID).all()
    assert provenance.DOI.eq(DOI).all()
    assert provenance.ML_Condition_ID.isin(EXACT_IDS).all()
    assert set(provenance.Provenance_Layer) == {
        "MASTER_FIELD_MAPPING",
        "VERIFIED_WORKBOOK_LEDGER",
        "PHYSICS_SAFEGUARD_MAPPING",
    }
    assert out[out.Paper_ID.eq(PAPER_ID)].P022_Recovery_Provenance_JSON.str.len().gt(2).all()


def test_programmatic_target_count_deltas_and_no_new_joint_condition(recovered):
    source, out = recovered
    before = counts(source)
    after = counts(out)
    assert tuple(after[i] - before[i] for i in range(4)) == (5, 1, 3, 0)
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    assert after_classes["trip_positive"] - before_classes["trip_positive"] == 1
    assert after_classes["twip_positive"] - before_classes["twip_positive"] == 3
    assert after_classes["trip_negative"] == before_classes["trip_negative"]
    assert after_classes["twip_negative"] == before_classes["twip_negative"]
    for state in ["joint_00", "joint_10", "joint_01", "joint_11"]:
        assert after_classes[state] == before_classes[state]


def test_audit_and_all_required_supporting_tables_exist(recovered):
    _ = recovered
    expected = {
        "study_identity",
        "material_parents",
        "condition_hierarchy",
        "raw_composition_formulas",
        "processing",
        "initial_microstructure",
        "mechanical_response",
        "40pct_twin_observations",
        "target_evidence",
        "sfe_physics_safeguards",
        "provenance",
        "decision_correction_ledger",
    }
    for name in expected:
        assert (TABLE / f"p022_recovery_v16_{name}.csv").is_file()
    text = AUDIT.read_text(encoding="utf-8")
    assert "# P022 recovery v16 audit" in text
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWX":
        assert f"## {letter}." in text
    assert "Global QC" in text
    assert "after collection pauses" in text


def test_no_derived_features_imputation_or_model_matrix_are_created(recovered):
    _, out = recovered
    rows = out[out.Paper_ID.eq(PAPER_ID)]
    for field in [
        "VEC_derived",
        "Atomic_size_mismatch_delta_pct",
        "Configurational_entropy_J_molK",
        "Mixing_enthalpy_kJ_mol",
        "Omega",
        "Electronegativity_mismatch",
        "Melting_temperature_weighted_K",
        "log10_strain_rate",
    ]:
        if field in rows:
            assert rows[field].isna().all()
