import hashlib

import pandas as pd
import pytest

from scripts.integrate_p023_recovery_v17 import (
    AUDIT,
    BOOK,
    BOOK_SHA256,
    CONDITION_BY_STATE,
    DIRECT_JOINT_IDS,
    DOI,
    EXACT_IDS,
    EXPECTED_LOCAL_EDS,
    EXPECTED_PHASES,
    MATERIAL,
    NOMINAL_COMPOSITION,
    NOMINAL_ELEMENTS,
    OUT,
    PAPER_ID,
    SERIES,
    SOURCE,
    SOURCE_SHA256,
    STATE_BY_CONDITION,
    STATE_ORDER,
    SUPPORT_ONLY_750_STATES,
    TABLE,
    TITLE,
    UNRESOLVED_IDS,
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
    assert len(rows) == 7
    return rows.set_index("ML_Condition_ID", drop=False)


def load_table(name: str) -> pd.DataFrame:
    return pd.read_csv(
        TABLE / f"p023_recovery_v17_{name}.csv",
        low_memory=False,
    )


def test_source_identity_duplicate_gate_and_immutable_v16_prefix(recovered):
    source, out = recovered
    assert duplicate_rows(source).empty
    assert not source.Paper_ID.eq(PAPER_ID).any()
    assert len(out) == len(source) + len(EXACT_IDS)
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    identity = load_table("study_identity").iloc[0]
    assert identity.Paper_ID == PAPER_ID
    assert identity.DOI == DOI
    assert identity.Title == TITLE
    assert identity.Journal == "Applied Materials Today"
    assert int(identity.Volume) == 13
    assert str(identity.Pages) == "198-206"
    assert int(identity.Year) == 2018
    assert identity.Data_Origin == "EXPERIMENTAL"
    assert identity.Source_Identity_Status == (
        "VERIFIED_PDF_AND_SCIENCEDIRECT_DOI_MATCH"
    )


def test_written_v17_roundtrip_preserves_every_v16_source_cell(recovered):
    source, _ = recovered
    written = pd.read_csv(OUT, low_memory=False)
    pd.testing.assert_frame_equal(
        written.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )


def test_one_material_parent_seven_conditions_and_no_family_merge(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert tuple(rows.index) == EXACT_IDS
    assert rows.Material_Parent_ID.nunique() == 1
    assert rows.Material_Parent_ID.eq(MATERIAL).all()
    assert rows.Study_Series_ID.eq(SERIES).all()
    assert rows.Leakage_Group_Strict.eq(SERIES).all()
    assert rows.Leakage_Group_Material.eq(MATERIAL).all()
    assert rows.P023_Source_Family_Status.eq(
        "NEW_SOURCE_NOT_MERGED_WITH_RELATED_NENE_MISHRA_STUDIES"
    ).all()
    assert not rows.Parent_ML_Condition_ID.str.startswith("P020").any()
    assert not rows.Parent_ML_Condition_ID.str.startswith("P021").any()
    assert not rows.Parent_ML_Condition_ID.str.startswith("P022").any()


def test_exactly_ten_supporting_phase_states_and_750_not_primary(recovered):
    _, out = recovered
    rows = primary_rows(out)
    states = load_table("processing_states")
    phases = load_table("phase_fractions")
    assert len(states) == len(phases) == 10
    assert tuple(states.Processing_State_ID) == STATE_ORDER
    assert tuple(phases.Processing_State_ID) == STATE_ORDER
    assert states.Independent_Experimental_ML_sample.eq(False).all()
    assert not rows.Processing_State_ID.isin(SUPPORT_ONLY_750_STATES).any()
    support_750 = states[states.Processing_State_ID.isin(SUPPORT_ONLY_750_STATES)]
    assert len(support_750) == 3
    assert support_750.Primary_Tensile_Condition_ID.isna().all()
    assert support_750.Primary_Tensile_Status.eq(
        "SUPPORTING_ONLY_NO_CONDITION_SPECIFIC_TENSILE_RESULT"
    ).all()


def test_all_seven_are_independent_n3_without_pseudo_replicates(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Observation_Role.eq("INDEPENDENT_CONDITION").all()
    assert rows.Independent_ML_sample.eq(True).all()
    assert rows.Independent_Experimental_ML_sample.eq(True).all()
    assert rows.Experimental_Target_Eligibility.eq(True).all()
    assert rows.Parent_Experiment_ID.eq(rows.ML_Condition_ID).all()
    assert rows.Parent_ML_Condition_ID.eq(rows.ML_Condition_ID).all()
    assert rows.Observation_ID.nunique() == 7
    assert rows.Physical_Batch_ID.isna().all()
    assert rows.Replicate_ID.isna().all()
    assert rows.Replicate_n.astype(float).eq(3).all()
    hierarchy = load_table("tensile_conditions")
    assert hierarchy.Pseudo_Replicate_Status.eq(
        "NO_PSEUDO_REPLICATES_CREATED"
    ).all()
    assert hierarchy.Replicate_Status.eq(
        "AGGREGATE_N3_PER_CONDITION_NO_INDIVIDUAL_ROWS"
    ).all()
    assert not hierarchy.ML_Condition_ID.str.contains("REP", case=False).any()


def test_nominal_chemistry_exact_without_normalization_or_bulk_substitution(
    recovered,
):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Original_Composition.eq(NOMINAL_COMPOSITION).all()
    assert rows.Nominal_Composition_at_pct.eq(NOMINAL_COMPOSITION).all()
    assert rows.Composition_basis.eq("at.% nominal").all()
    for element, expected in NOMINAL_ELEMENTS.items():
        assert rows[f"{element}_at%"].astype(float).eq(expected).all()
    assert rows.Normalized_Composition_at_pct.isna().all()
    assert rows.Composition_Normalization_Status.eq(
        "NOT_NORMALIZED_SOURCE_NOMINAL_ATPCT_AS_REPORTED"
    ).all()
    assert rows.Measured_Bulk_Composition.isna().all()
    assert rows.Measured_Composition_at_pct.isna().all()
    assert rows.Recovered_Bulk_Composition_at_pct.isna().all()
    assert rows.Composition_Status.eq(
        "NOMINAL_PLUS_LOCAL_EDS_NO_BULK_POSTMELT_CHEMISTRY"
    ).all()


def test_ascast_and_dpass_eds_are_numeric_local_only_not_bulk(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Local_EDS_Chemistry_Status.eq(
        "LOCAL_EDS_ELEMENTAL_DISTRIBUTION_TABLE_NOT_BULK_CHEMISTRY"
    ).all()
    chemistry = load_table("composition_local_eds")
    local = chemistry[chemistry.Chemistry_Scope.str.startswith("LOCAL_EDS")]
    assert len(local) == 2
    assert local.Bulk_Chemistry_Use_Status.eq(
        "LOCAL_ONLY_EXCLUDED_FROM_BULK_CHEMISTRY"
    ).all()
    for scope, key in [("LOCAL_EDS_AS_CAST", "AS_CAST"), ("LOCAL_EDS_D_PASS", "D_PASS")]:
        row = local[local.Chemistry_Scope.eq(scope)].iloc[0]
        for element, expected in EXPECTED_LOCAL_EDS[key].items():
            assert float(row[f"{element}_at_pct"]) == expected
    measured = chemistry[chemistry.Chemistry_Scope.eq("MEASURED_BULK_POSTMELT")]
    assert len(measured) == 1
    assert measured.Measured_Bulk_Composition.isna().all()


def test_casting_fsp_and_annealing_grid_are_preserved(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Cast_method.eq("Vacuum arc casting in cold-copper crucible").all()
    assert rows.Vacuum_Level_Raw.eq("~300 um vacuum").all()
    assert rows.Backfill_Atmosphere.eq("Ar to 1 atm").all()
    assert rows.Cast_Ingot_Dimensions_mm.eq("300 x 100 x 6").all()
    assert rows.FSP_Pass1_Rotation_rpm.astype(float).eq(350).all()
    assert rows.FSP_Pass2_Rotation_rpm.astype(float).eq(150).all()
    assert rows.FSP_Traverse_Speed_mm_min.astype(float).eq(50.8).all()
    assert rows.FSP_Plunge_Depth_mm.astype(float).eq(3.65).all()
    assert rows.FSP_Tilt_deg.astype(float).eq(2).all()
    assert rows.FSP_Backplate.eq("Cu").all()
    assert rows.FSP_Shielding.eq("Ar near tool/specimen interface").all()
    annealed = rows[rows.Processing_State_ID.ne("P023_STATE_DPASS")]
    assert set(annealed.Anneal_T_C_Raw.astype(float)) == {650.0, 850.0}
    assert set(annealed.Annealing_time_min.astype(float)) == {5.0, 15.0, 30.0}
    assert annealed.Post_Anneal_Quench.eq("Water quench").all()
    support = load_table("processing_states")
    annealed_support = support[support.Anneal_T_C.notna()]
    assert set(annealed_support.Anneal_T_C.astype(float)) == {650.0, 750.0, 850.0}
    assert set(annealed_support.Anneal_Time_min.astype(float)) == {5.0, 15.0, 30.0}


def test_room_temperature_rate_geometry_and_exact_kelvin_safeguard(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.Test_T_Raw.eq("room temperature").all()
    assert rows.Test_T_K.isna().all()
    assert rows.Test_T_C.isna().all()
    assert rows["Strain_rate_s-1"].astype(float).eq(1e-3).all()
    assert rows.Loading_Mode.eq("Uniaxial tension").all()
    assert rows.Gauge_length_mm.astype(float).eq(5).all()
    assert rows.Gauge_width_mm.astype(float).eq(1.25).all()
    assert rows.Specimen_thickness_mm.astype(float).eq(1).all()


def test_dpass_and_ascast_grain_sizes_without_annealed_digitization(recovered):
    _, out = recovered
    rows = primary_rows(out)
    dpass = rows.loc["P023_MC_DPASS_RT"]
    assert float(dpass.Grain_size_um) == 0.79
    assert float(dpass.Grain_size_SD_um) == 0.05
    assert rows.drop(index="P023_MC_DPASS_RT").Grain_size_um.isna().all()
    fsp = load_table("fsp_processing").iloc[0]
    assert float(fsp.AsCast_Grain_Size_um) == 120
    assert float(fsp.AsCast_Grain_Size_SD_um) == 12
    assert float(fsp.DPass_Grain_Size_um) == 0.79
    assert float(fsp.DPass_Grain_Size_SD_um) == 0.05
    assert rows.drop(index="P023_MC_DPASS_RT").Annealed_Grain_Size_Digitization_Status.eq(
        "NOT_DIGITIZED_FIG3G_QUALITATIVE_ONLY"
    ).all()
    assert rows.Al_Content_Curve_Digitization_Status.eq(
        "NOT_DIGITIZED_FIG3H_QUALITATIVE_TREND_ONLY"
    ).all()


def test_all_ten_pretest_phase_fractions_and_sd_match_exactly(recovered):
    _, out = recovered
    rows = primary_rows(out)
    phases = load_table("phase_fractions").set_index("Processing_State_ID")
    assert tuple(phases.index) == STATE_ORDER
    for state_id, expected in EXPECTED_PHASES.items():
        actual = phases.loc[
            state_id,
            ["Initial_FCC_fraction", "Initial_HCP_fraction", "Phase_Fraction_SD_pct"],
        ]
        assert tuple(float(value) for value in actual) == expected
    for condition_id, state_id in STATE_BY_CONDITION.items():
        row = rows.loc[condition_id]
        expected = EXPECTED_PHASES[state_id]
        assert (
            float(row.Initial_FCC_fraction),
            float(row.Initial_HCP_fraction),
            float(row.PreTest_Phase_Fraction_SD_pct),
        ) == expected


def test_initial_hcp_never_automatically_generates_trip(recovered):
    _, out = recovered
    rows = primary_rows(out)
    unresolved = rows.loc[list(UNRESOLVED_IDS)]
    assert unresolved.Initial_HCP_fraction.astype(float).gt(0).all()
    assert unresolved.Effective_TRIP.isna().all()
    assert unresolved.Initial_HCP_Target_Guardrail.eq(
        "PRETEST_HCP_IS_NOT_DEFORMATION_INDUCED_TRIP_EVIDENCE"
    ).all()


def test_650_15_direct_joint_target_postfractions_and_hcp_slip(recovered):
    _, out = recovered
    row = primary_rows(out).loc["P023_MC_650_15_RT"]
    assert float(row.Effective_TRIP) == 1
    assert float(row.Effective_TWIP) == 1
    assert float(row.Slip) == 1
    assert row.Target_Status == "VERIFIED_JOINT"
    assert row.TWIP_Phase == "HCP_EPSILON"
    assert (float(row.Initial_FCC_fraction), float(row.Initial_HCP_fraction)) == (
        0.30,
        0.70,
    )
    assert (float(row.PostTest_FCC_fraction), float(row.PostTest_HCP_fraction)) == (
        0.06,
        0.94,
    )
    assert row.Slip_Evidence_Type == "DIRECT_<C+A>_SLIP_IN_EPSILON_HCP"


def test_850_30_direct_joint_target_postfractions_and_hcp_slip(recovered):
    _, out = recovered
    row = primary_rows(out).loc["P023_MC_850_30_RT"]
    assert float(row.Effective_TRIP) == 1
    assert float(row.Effective_TWIP) == 1
    assert float(row.Slip) == 1
    assert row.Target_Status == "VERIFIED_JOINT"
    assert row.TWIP_Phase == "HCP_EPSILON"
    assert (float(row.Initial_FCC_fraction), float(row.Initial_HCP_fraction)) == (
        0.43,
        0.57,
    )
    assert (float(row.PostTest_FCC_fraction), float(row.PostTest_HCP_fraction)) == (
        0.10,
        0.90,
    )
    assert row.Slip_Evidence_Type == "DIRECT_<C+A>_SLIP_IN_EPSILON_HCP"


def test_other_five_targets_remain_na_and_no_zero_is_created(recovered):
    _, out = recovered
    rows = primary_rows(out)
    unresolved = rows.loc[list(UNRESOLVED_IDS)]
    assert unresolved[["Effective_TRIP", "Effective_TWIP", "Slip"]].isna().all().all()
    assert unresolved.Negative_Evidence_Status.eq("INSUFFICIENT_FOR_ZERO").all()
    assert not rows.Effective_TRIP.eq(0).any()
    assert not rows.Effective_TWIP.eq(0).any()
    assert rows.loc[list(DIRECT_JOINT_IDS), "Phase_Specific_TWIP_Safeguard"].eq(
        "HCP_EPSILON_TWIP_NOT_SILENTLY_RECODED_AS_FCC_TWIP"
    ).all()


def test_mechanical_recovery_preserves_engineering_true_and_leakage_semantics(
    recovered,
):
    _, out = recovered
    rows = primary_rows(out)
    m65015 = rows.loc["P023_MC_650_15_RT"]
    assert (
        float(m65015.Engineering_YS_MPa),
        float(m65015.Engineering_UTS_MPa),
        float(m65015.Engineering_Elongation_pct),
        float(m65015.SDI_MPa),
    ) == (610.0, 1120.0, 52.0, 425.0)
    assert m65015.SDI_Predictor_Eligibility == "OUTCOME_DERIVED_MECHANICAL_LEAKAGE"
    m65030 = rows.loc["P023_MC_650_30_RT"]
    assert float(m65030.True_Tensile_Strength_MPa) == 1630
    assert float(m65030.Uniform_elongation_pct) == 43
    assert pd.isna(m65030.Engineering_UTS_MPa)
    assert pd.isna(m65030.Engineering_Elongation_pct)
    assert m65030.Mechanical_Stress_Basis_Status == (
        "TRUE_TENSILE_STRENGTH_AND_UNIFORM_ELONGATION_NOT_ENGINEERING"
    )
    figure_only = rows.drop(index=["P023_MC_650_15_RT", "P023_MC_650_30_RT"])
    fields = [
        "Engineering_YS_MPa",
        "Engineering_UTS_MPa",
        "Engineering_Elongation_pct",
        "True_Tensile_Strength_MPa",
        "Uniform_elongation_pct",
        "SDI_MPa",
    ]
    assert figure_only[fields].isna().all().all()
    assert rows.Tensile_Curve_Digitization_Status.eq(
        "NOT_DIGITIZED_DIRECT_TEXT_VALUES_ONLY"
    ).all()


def test_curve_inferred_onset_is_not_a_direct_stage(recovered):
    _, out = recovered
    rows = primary_rows(out)
    row = rows.loc["P023_MC_650_15_RT"]
    assert float(row.TRIP_Onset_True_Stress_MPa) == 924
    assert float(row.TRIP_Onset_Engineering_Stress_Approx_MPa) == 840
    assert float(row.TRIP_Onset_Strain_Approx_pct) == 10
    assert float(row.WH_Rate_at_Slope_Change_MPa) == 2983
    assert row.TRIP_Onset_Evidence_Status == (
        "CURRENT_PAPER_CURVE_INFERRED_MECHANISM_ONSET"
    )
    assert row.TRIP_Onset_Predictor_Eligibility == (
        "MODEL_CURVE_INFERENCE_NOT_DIRECT_STAGE"
    )
    assert row.WH_Rate_Predictor_Eligibility == "MECHANICAL_OUTCOME_LEAKAGE"
    assert rows.Direct_Stage_Fabrication_Status.eq(
        "NO_DIRECT_EXPERIMENTAL_STAGE_CREATED_FROM_CURVE_INFERENCE"
    ).all()
    assert len(out[out.Paper_ID.eq(PAPER_ID)]) == 7
    assert not out[out.Paper_ID.eq(PAPER_ID)].Observation_Role.eq(
        "DIRECT_EXPERIMENTAL_STAGE"
    ).any()
    onset = load_table("wh_onset")
    assert len(onset) == 4
    assert onset.Direct_Stage_Status.eq(
        "NO_DIRECT_EXPERIMENTAL_STAGE_CREATED_FROM_CURVE_INFERENCE"
    ).all()


def test_posttest_phase_gnd_ipf_and_twins_are_leakage_only(recovered):
    _, out = recovered
    rows = primary_rows(out).loc[list(DIRECT_JOINT_IDS)]
    assert rows.PostTest_Evidence_Status.eq("POST_TEST_TARGET_EVIDENCE").all()
    assert rows.PostTest_Predictor_Eligibility.eq(
        "POST_TEST_TARGET_EVIDENCE_NOT_PRETEST_PREDICTOR"
    ).all()
    assert rows.PostTest_GND_Evidence_Status.eq(
        "POST_TEST_LEAKAGE_NO_NUMERIC_DENSITY_RECOVERED"
    ).all()
    assert rows.PostTest_IPF_Evidence_Status.eq(
        "POST_TEST_LEAKAGE_NOT_PRETEST_PREDICTOR"
    ).all()
    evidence = load_table("before_after_evidence")
    assert len(evidence) == 2
    assert evidence.Independent_ML_sample.eq(False).all()
    assert evidence.Predictor_Eligibility.eq(
        "POST_TEST_TARGET_EVIDENCE_NOT_PRETEST_PREDICTOR"
    ).all()
    assert evidence.TWIP_Phase.eq("HCP_EPSILON").all()


def test_precipitation_is_pretest_and_no_grain_or_al_curve_values_are_digitized(
    recovered,
):
    _ = recovered
    precip = load_table("precipitation_state").set_index("Processing_State_ID")
    assert "Fine Al-rich" in precip.loc["P023_STATE_650_15", "Precipitate_State"]
    assert "Large Al-rich grain-boundary" in precip.loc[
        "P023_STATE_850_15", "Precipitate_State"
    ]
    assert "Massive Al-rich" in precip.loc[
        "P023_STATE_850_30", "Precipitate_State"
    ]
    assert precip.PreTest_Status.eq("PRE_TEST_MICROSTRUCTURE").all()
    assert precip.Al_Content_Status.eq(
        "FIG3H_NOT_DIGITIZED_QUALITATIVE_TREND_ONLY"
    ).all()
    annealed = precip[precip.Anneal_T_C.notna()]
    assert annealed.Annealed_Grain_Size_Status.eq(
        "FIG3G_NOT_DIGITIZED_QUALITATIVE_GRAIN_GROWTH_ONLY"
    ).all()


def test_thermocalc_is_context_only_and_sfe_deltag_remain_na(recovered):
    _, out = recovered
    rows = primary_rows(out)
    assert rows.ThermoCalc_Software.eq("Thermo-Calc").all()
    assert rows.ThermoCalc_Database.eq("TCHEA2").all()
    assert rows.ThermoCalc_Observation_Safeguard.eq(
        "EQUILIBRIUM_PREDICTIONS_DO_NOT_OVERRIDE_EBSD_XRD_OBSERVATIONS"
    ).all()
    assert rows.SFE_mJ_m2.isna().all()
    assert rows.SFE_method.isna().all()
    assert rows.DeltaG_FCC_HCP_J_mol.isna().all()
    assert rows.DeltaG_method.isna().all()
    assert rows.SFE_Transfer_Safeguard.eq(
        "NO_IMPORT_FROM_CITED_FE_MN_SI_OR_RELATED_HEA_LITERATURE"
    ).all()
    assert rows.DeltaG_Transfer_Safeguard.eq(
        "NO_CALCULATION_OR_CROSS_PAPER_TRANSFER"
    ).all()
    thermo = load_table("thermocalc_context").iloc[0]
    assert thermo.Value == "TCHEA2"
    assert thermo.Measured_Phase_Fraction_Use == "NOT_USED_AS_MEASURED_PHASE_FRACTION"
    gaps = load_table("sfe_deltag_gaps")
    assert set(gaps.Feature) == {"SFE_numeric", "DeltaG_FCC_HCP"}
    assert gaps.Value.isna().all()


def test_every_new_master_field_and_support_table_value_has_provenance(recovered):
    _, out = recovered
    provenance = load_table("provenance")
    required = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
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
    assert set(provenance.Provenance_Layer) == {
        "MASTER_FIELD_MAPPING",
        "VERIFIED_WORKBOOK_LEDGER",
        "SUPPORT_TABLE_FIELD_MAPPING",
    }
    master = provenance[provenance.Provenance_Layer.eq("MASTER_FIELD_MAPPING")]
    assert master.ML_Condition_ID.isin(EXACT_IDS).all()
    assert master.Processing_State_ID.isin(CONDITION_BY_STATE).all()
    assert out[out.Paper_ID.eq(PAPER_ID)].P023_Recovery_Provenance_JSON.str.len().gt(2).all()
    expected_support = {
        f"p023_recovery_v17_{name}.csv"
        for name in {
            "study_identity",
            "composition_local_eds",
            "fsp_processing",
            "processing_states",
            "phase_fractions",
            "tensile_conditions",
            "mechanical_response",
            "precipitation_state",
            "before_after_evidence",
            "target_evidence",
            "wh_onset",
            "thermocalc_context",
            "sfe_deltag_gaps",
        }
    }
    support = provenance[provenance.Provenance_Layer.eq("SUPPORT_TABLE_FIELD_MAPPING")]
    assert expected_support <= set(support.Source_Table)


def test_programmatic_count_deltas_add_two_joint_positive_conditions(recovered):
    source, out = recovered
    before = counts(source)
    after = counts(out)
    assert tuple(after[index] - before[index] for index in range(4)) == (7, 2, 2, 2)
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    assert after_classes["trip_positive"] - before_classes["trip_positive"] == 2
    assert after_classes["twip_positive"] - before_classes["twip_positive"] == 2
    assert after_classes["joint_11"] - before_classes["joint_11"] == 2
    assert after_classes["trip_negative"] == before_classes["trip_negative"]
    assert after_classes["twip_negative"] == before_classes["twip_negative"]
    for state in ["joint_00", "joint_10", "joint_01"]:
        assert after_classes[state] == before_classes[state]


def test_audit_and_all_required_supporting_tables_exist(recovered):
    _ = recovered
    expected = {
        "study_identity",
        "composition_local_eds",
        "fsp_processing",
        "processing_states",
        "phase_fractions",
        "tensile_conditions",
        "mechanical_response",
        "precipitation_state",
        "before_after_evidence",
        "target_evidence",
        "wh_onset",
        "thermocalc_context",
        "sfe_deltag_gaps",
        "provenance",
        "decision_correction_ledger",
    }
    for name in expected:
        assert (TABLE / f"p023_recovery_v17_{name}.csv").is_file()
    text = AUDIT.read_text(encoding="utf-8")
    assert "# P023 recovery v17 audit" in text
    for letter in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["AA", "AB", "AC"]:
        assert f"## {letter}." in text
    assert "Global QC" in text
    assert "after paper collection pauses" in text


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
