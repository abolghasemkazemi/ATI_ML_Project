import hashlib
from pathlib import Path

import pandas as pd
import pytest

from scripts.integrate_p021_recovery_v15 import (
    ARTICLE_NUMBER,
    AUDIT,
    BOOK,
    BOOK_SHA256,
    CHARACTERIZED_IDS,
    CRYO_ID,
    DOI,
    EXACT_IDS,
    EXPECTED_GRID,
    EXPECTED_MECHANICS,
    MATERIAL,
    MEANINGFUL_NA_FIELDS,
    NOMINAL_COMPOSITION,
    OUT,
    PAPER_ID,
    PROVENANCE_EXCLUDE,
    RT40_ID,
    RT_IDS,
    SERIES,
    SOURCE,
    SOURCE_SHA256,
    TABLE,
    TITLE,
    class_counts,
    counts,
    duplicate_rows,
    integrate,
    is_present,
)


@pytest.fixture(scope="module")
def recovered():
    book_hash = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    source, out = integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest() == book_hash == BOOK_SHA256
    assert (
        hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        == source_hash
        == SOURCE_SHA256
    )
    return source, out


def p021_rows(out: pd.DataFrame) -> pd.DataFrame:
    rows = out[out.Paper_ID.eq(PAPER_ID)].copy()
    assert len(rows) == 5
    return rows.set_index("ML_Condition_ID", drop=False)


def load_table(name: str) -> pd.DataFrame:
    return pd.read_csv(
        TABLE / f"p021_recovery_v15_{name}.csv",
        low_memory=False,
    )


def test_source_identity_duplicate_check_and_immutable_v14_prefix(recovered):
    source, out = recovered
    assert duplicate_rows(source).empty
    assert not source.Paper_ID.eq(PAPER_ID).any()
    assert len(out) == len(source) + 5
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    identity = load_table("study_identity").iloc[0]
    assert identity.Paper_ID == PAPER_ID
    assert identity.DOI == DOI
    assert identity.Title == TITLE
    assert identity.Journal == "Journal of Alloys and Compounds"
    assert int(identity.Volume) == 898
    assert str(identity.Article_Number) == ARTICLE_NUMBER
    assert int(identity.Year) == 2022
    assert identity.Data_Origin == "EXPERIMENTAL"
    assert identity.Source_Identity_Status == "VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH"


def test_exact_five_condition_hierarchy_without_pseudo_replicates(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert tuple(rows.index) == EXACT_IDS
    assert rows.Observation_Role.eq("INDEPENDENT_CONDITION").all()
    assert rows.Independent_ML_sample.eq(True).all()
    assert rows.Independent_Experimental_ML_sample.eq(True).all()
    assert rows.Experimental_Target_Eligibility.eq(True).all()
    assert rows.Parent_Experiment_ID.eq(rows.ML_Condition_ID).all()
    assert rows.Parent_ML_Condition_ID.eq(rows.ML_Condition_ID).all()
    assert rows.Observation_ID.nunique() == 5
    assert rows.Deformation_Stage_ID.isna().all()
    assert rows.Study_Series_ID.eq(SERIES).all()
    assert rows.Material_Parent_ID.eq(MATERIAL).all()
    assert rows.Leakage_Group_Strict.eq(SERIES).all()
    assert rows.Leakage_Group_Material.eq(MATERIAL).all()
    assert rows.Physical_Batch_ID.isna().all()
    assert rows.Replicate_ID.isna().all()
    hierarchy = load_table("hierarchy")
    assert len(hierarchy) == 5
    assert hierarchy.Pseudo_Replicate_Rows.eq(0).all()


def test_replicate_statement_remains_minimum_at_least_three(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert rows.Replicate_n.astype(float).eq(3).all()
    assert rows.Replicate_n_Status.eq(
        "MINIMUM_REPORTED_AT_LEAST_THREE"
    ).all()
    assert rows.Replicate_Scope.eq(
        "AVERAGE_MECHANICAL_VALUES_FROM_AT_LEAST_THREE_TENSILE_SPECIMENS"
    ).all()
    assert not rows.Condition_ID.str.contains("REP", case=False).any()


def test_nominal_composition_and_qualitative_eds_are_not_bulk_chemistry(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert rows.Original_Composition.eq(NOMINAL_COMPOSITION).all()
    assert rows.Nominal_Composition_at_pct.eq(NOMINAL_COMPOSITION).all()
    assert rows.Composition_basis.eq("at.% nominal").all()
    assert rows.Measured_Bulk_Composition.isna().all()
    assert rows.Measured_Composition_at_pct.isna().all()
    assert rows.Recovered_Bulk_Composition_at_pct.isna().all()
    assert rows.Composition_Status.eq(
        "NOMINAL_ONLY_EDS_QUALITATIVE_HOMOGENEITY_NO_QUANTITATIVE_POSTMELT_BULK_ANALYSIS"
    ).all()
    assert rows.EDS_Qualitative_Homogeneity.eq(
        "QUALITATIVE_HOMOGENIZATION_ONLY_NOT_QUANTITATIVE_BULK_CHEMISTRY"
    ).all()
    expected = {
        "Fe_at%": 50.0,
        "Mn_at%": 17.5,
        "Cr_at%": 12.5,
        "Co_at%": 10.0,
        "Ni_at%": 5.0,
        "Si_at%": 5.0,
    }
    for field, value in expected.items():
        assert rows[field].astype(float).eq(value).all()


def test_common_processing_and_exact_condition_grid(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert rows.Raw_Material_Purity.eq(">99.9%").all()
    assert rows.Melting_Route.eq("Vacuum arc melting under Ar").all()
    assert rows.Remelt_Count_Min.astype(float).eq(5).all()
    assert rows.Remelt_Count_Status.eq("AT_LEAST_FIVE").all()
    assert rows.Alloy_Mass_g_Approx.astype(float).eq(150).all()
    assert rows.Remolded_Ingot_Dimensions_mm.eq("65 x 40 x 10").all()
    assert rows.Homogenization_T_C_Raw.astype(float).eq(1150).all()
    assert rows.Homogenization_time_h.astype(float).eq(24).all()
    assert rows.Hot_Roll_T_C_Raw.astype(float).eq(1100).all()
    assert rows.Hot_Roll_Final_Thickness_mm.astype(float).eq(3).all()
    assert rows.Cold_rolling_reduction_pct.astype(float).eq(30).all()
    assert rows.Post_Anneal_Quench.eq("Water quench").all()
    assert rows.Specimen_Orientation.eq("Longitudinal / rolling direction").all()
    assert rows.Specimen_Standard.eq("ASTM E8/E8M sub-size").all()
    for condition_id, expected in EXPECTED_GRID.items():
        anneal_c, anneal_min, grain_um, test_k, test_raw = expected
        row = rows.loc[condition_id]
        assert float(row.Anneal_T_C_Raw) == anneal_c
        assert float(row.Annealing_time_min) == anneal_min
        assert float(row.Grain_size_um) == grain_um
        assert float(row.Test_T_K) == test_k
        assert row.Test_T_Raw == test_raw
        assert float(row["Strain_rate_s-1"]) == 1e-3
    assert rows.loc[list(RT_IDS), "Test_T_C"].astype(float).eq(25).all()
    assert pd.isna(rows.loc[CRYO_ID, "Test_T_C"])
    assert rows.loc[CRYO_ID, "Test_Atmosphere"] == "LIQUID_NITROGEN_ATMOSPHERE"


def test_initial_single_fcc_fraction_safeguards_and_grain_sizes(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert rows.Initial_Phase.eq("SINGLE_FCC").all()
    assert rows.Fully_Recrystallized.eq(True).all()
    assert rows.Initial_FCC_fraction.isna().all()
    assert rows.Recovered_Initial_FCC_fraction.isna().all()
    assert rows.Initial_HCP_fraction.astype(float).eq(0).all()
    assert rows.Initial_Alpha_BCT_fraction.astype(float).eq(0).all()
    assert rows.Initial_Secondary_Phase_Status.eq(
        "NO_OBVIOUS_PRECIPITATES_OR_OTHER_PHASES"
    ).all()
    assert rows.Grain_Size_Twin_Boundary_Exclusion.eq(True).all()
    assert set(rows.Grain_size_um.astype(float)) == {10.0, 19.5, 40.9, 149.6}
    assert rows.Lattice_parameter_nm.astype(float).eq(0.358).all()
    assert not rows.Initial_FCC_fraction.eq(1).any()


def test_annealing_twins_never_generate_tensile_twip(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert rows.PreTest_Twin_State.eq("ABUNDANT_ANNEALING_TWINS").all()
    assert rows.PreTest_Twin_Origin.eq("ANNEALING_PRETEST").all()
    assert rows.Initial_Twin_Target_Guardrail.eq(
        "ANNEALING_TWINS_DO_NOT_GENERATE_TENSILE_TWIP"
    ).all()
    unresolved = [EXACT_IDS[0], EXACT_IDS[1], EXACT_IDS[3], CRYO_ID]
    assert rows.loc[unresolved, "Effective_TWIP"].isna().all()


def test_77k_stacking_faults_are_pretest_state_not_twip(recovered):
    _, out = recovered
    rows = p021_rows(out)
    cryo = rows.loc[CRYO_ID]
    assert cryo.Initial_Stacking_Fault_State == "PROFUSE_PRETEST_STACKING_FAULTS"
    assert bool(cryo.PreTest_Cryogenic_Immersion)
    assert cryo.PreTest_State_Timing == "BEFORE_TENSILE_LOADING"
    assert pd.isna(cryo.Effective_TWIP)
    assert cryo.Negative_Evidence_Status == "INSUFFICIENT_FOR_ZERO"


def test_exact_mechanical_response_is_outcome_leakage(recovered):
    _, out = recovered
    rows = p021_rows(out)
    for condition_id, expected in EXPECTED_MECHANICS.items():
        row = rows.loc[condition_id]
        actual = (
            float(row.Engineering_YS_MPa),
            float(row.Engineering_UTS_MPa),
            float(row.Engineering_Elongation_pct),
        )
        assert actual == expected
        assert (
            float(row.YS_mean),
            float(row.UTS_mean),
            float(row.TE_mean),
        ) == expected
    assert rows.Mechanical_Predictor_Eligibility.eq(
        "MECHANICAL_OUTCOME_LEAKAGE"
    ).all()


def test_three_rt_grain_size_targets_remain_unresolved(recovered):
    _, out = recovered
    rows = p021_rows(out)
    unresolved = [EXACT_IDS[0], EXACT_IDS[1], EXACT_IDS[3]]
    assert rows.loc[
        unresolved, ["Effective_TRIP", "Effective_TWIP", "Slip"]
    ].isna().all().all()
    assert rows.loc[unresolved, "Negative_Evidence_Status"].eq(
        "INSUFFICIENT_FOR_ZERO"
    ).all()
    assert not rows.loc[unresolved, "Evidence_TRIP"].str.contains(
        "plateau.*TRIP=1", case=False, regex=True
    ).any()


def test_rt40_direct_trip_and_low_abundance_twip(recovered):
    _, out = recovered
    row = p021_rows(out).loc[RT40_ID]
    assert (int(row.Effective_TRIP), int(row.Effective_TWIP), int(row.Slip)) == (
        1,
        1,
        1,
    )
    assert row.TRIP_Parent_Phase == "FCC"
    assert row.TRIP_Product_Phase == "HCP_EPSILON"
    assert row.TWIP_Phase == "UNRESOLVED_PHASE_DIRECT_MECHANICAL_TWIN_TEXT"
    assert row.TWIP_Evidence_Abundance == "LOW"
    assert row.TWIP_Evidence_Strength == "MEDIUM_RELATIVE_TO_TRIP"
    assert row.TWIP_Evidence_Type == "DIRECT_TEM_TEXT_FEW_MECHANICAL_TWINS"
    assert float(row.Postfracture_HCP_fraction) == 0.149
    assert row.Postfracture_HCP_fraction_scope == (
        "EBSD_INDEXED_PIXELS_ONLY_EXCLUDES_NON_INDEXED_REGIONS"
    )


def test_77k_trip_positive_twip_na_and_hcp_fraction(recovered):
    _, out = recovered
    row = p021_rows(out).loc[CRYO_ID]
    assert int(row.Effective_TRIP) == 1
    assert pd.isna(row.Effective_TWIP)
    assert int(row.Slip) == 1
    assert row.TRIP_Evidence_Type == "DIRECT_XRD_EBSD_TEM_HCP_EPSILON"
    assert row.TWIP_Evidence_Type == "INSUFFICIENT_CONDITION_LEVEL_TWIN_EVIDENCE"
    assert row.Negative_Evidence_Status == "INSUFFICIENT_FOR_ZERO"
    assert float(row.Postfracture_HCP_fraction) == 0.562
    assert row.Postfracture_Predictor_Eligibility == "POST_TEST_TARGET_EVIDENCE"


def test_no_other_grain_condition_receives_hcp_fraction(recovered):
    _, out = recovered
    rows = p021_rows(out)
    unresolved = [EXACT_IDS[0], EXACT_IDS[1], EXACT_IDS[3]]
    assert rows.loc[unresolved, "Postfracture_HCP_fraction"].isna().all()
    assert rows.loc[unresolved, "HCP_fraction_at_condition"].isna().all()
    assert set(
        rows[rows.Postfracture_HCP_fraction.notna()].index
    ) == CHARACTERIZED_IDS


def test_alpha_bct_absence_is_separate_from_positive_trip(recovered):
    _, out = recovered
    rows = p021_rows(out)
    characterized = rows.loc[list(CHARACTERIZED_IDS)]
    assert characterized.Alpha_BCT_Transformation_Status.eq("NOT_DETECTED").all()
    assert characterized.Alpha_BCT_Target_Safeguard.eq(
        "ALPHA_BCT_ABSENCE_IS_SEPARATE_FROM_POSITIVE_FCC_TO_HCP_TRIP"
    ).all()
    assert characterized.Effective_TRIP.astype(float).eq(1).all()
    uncharacterized = rows.loc[
        [condition_id for condition_id in EXACT_IDS if condition_id not in CHARACTERIZED_IDS]
    ]
    assert uncharacterized.Alpha_BCT_Transformation_Status.isna().all()


def test_sfe_bound_remains_raw_and_numeric_sfe_is_na(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert rows.SFE_mJ_m2.isna().all()
    assert rows.SFE_method.isna().all()
    rt40 = rows.loc[RT40_ID]
    assert rt40.SFE_Raw_Bound == "<23 mJ/m2"
    assert (
        rt40.SFE_Bound_Status
        == "AUTHOR_INFERRED_UPPER_BOUND_NOT_DIRECT_MEASUREMENT"
    )
    assert rows.SFE_Predictor_Eligibility.eq(
        "NOT_SAFE_AS_DIRECT_NUMERIC_SFE"
    ).all()
    assert rows.loc[CRYO_ID, "SFE_Qualitative_Temperature_Status"] == (
        "FURTHER_REDUCTION_DISCUSSION_ONLY_NO_NUMERIC_VALUE"
    )
    physics = load_table("sfe_physics")
    sfe = physics[physics.Feature.eq("SFE")]
    assert sfe.Recovered_Value.isna().all()
    assert "<23" in set(sfe.Recovered_Value_Raw.dropna().astype(str))


def test_deltag_gap_and_hall_petch_leakage(recovered):
    _, out = recovered
    rows = p021_rows(out)
    assert rows.DeltaG_FCC_HCP_J_mol.isna().all()
    assert rows.DeltaG_method.isna().all()
    hall = load_table("hall_petch_support").set_index("Feature")
    assert float(hall.loc["Hall_Petch_sigma0", "Value"]) == 198
    assert float(hall.loc["Hall_Petch_k", "Value"]) == 368
    assert hall.Status.eq("CURRENT_PAPER_FIT_FROM_TENSILE_YIELD_RESPONSE").all()
    assert hall.Predictor_Eligibility.eq("MODEL_DERIVED_LEAKAGE").all()
    assert hall.Leakage_Classification.eq("MODEL_DERIVED_LEAKAGE").all()


def test_programmatic_count_changes_are_expected_scientific_additions(recovered):
    source, out = recovered
    before = counts(source)
    after = counts(out)
    assert tuple(after[index] - before[index] for index in range(4)) == (
        5,
        2,
        1,
        1,
    )
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    assert after_classes["trip_positive"] - before_classes["trip_positive"] == 2
    assert after_classes["twip_positive"] - before_classes["twip_positive"] == 1
    assert after_classes["joint_11"] - before_classes["joint_11"] == 1
    for key in ["trip_negative", "twip_negative", "joint_00", "joint_10", "joint_01"]:
        assert after_classes[key] == before_classes[key]


def test_every_new_master_scientific_value_and_meaningful_na_has_provenance(
    recovered,
):
    _, out = recovered
    rows = p021_rows(out)
    provenance = load_table("provenance")
    required = {
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
        "ML_Condition_ID",
        "Feature_Name",
        "Recovered_Value",
        "Units",
        "Evidence_Type",
        "Evidence_Location",
        "Method",
        "Confidence",
        "Recovery_Status",
        "Data_Origin",
    }
    assert required <= set(provenance)
    assert provenance[list(required)].notna().all().all()
    assert provenance.Paper_ID.eq(PAPER_ID).all()
    assert provenance.DOI.eq(DOI).all()
    assert provenance.Data_Origin.eq("EXPERIMENTAL").all()
    assert provenance.ML_Condition_ID.isin(EXACT_IDS).all()
    master = provenance[provenance.Provenance_Layer.eq("MASTER_FIELD_MAPPING")]
    for _, row in rows.iterrows():
        for feature, value in row.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            if is_present(value) or feature in MEANINGFUL_NA_FIELDS:
                match = master[
                    master.Observation_ID.eq(row.Observation_ID)
                    & master.Feature_Name.eq(feature)
                ]
                assert len(match), (row.Observation_ID, feature)
    assert rows.P021_Recovery_Provenance_JSON.str.len().gt(2).all()


def test_required_supporting_tables_and_a_to_z_audit_exist(recovered):
    _, out = recovered
    required_tables = {
        "study_identity",
        "hierarchy",
        "processing",
        "condition_grid",
        "initial_microstructure",
        "mechanical_response",
        "postfracture_evidence",
        "targets",
        "sfe_physics",
        "hall_petch_support",
        "provenance",
        "decision_correction_ledger",
    }
    for name in required_tables:
        path = TABLE / f"p021_recovery_v15_{name}.csv"
        assert path.exists() and path.stat().st_size > 0
    assert OUT.exists() and len(pd.read_csv(OUT, low_memory=False)) == len(out)
    audit = AUDIT.read_text(encoding="utf-8")
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        assert f"## {letter}." in audit
    assert "Global QC, feature coverage/schema statistics" in audit
    assert "No ML matrix, model, feature engineering" in audit


def test_no_feature_engineering_imputation_or_synthetic_records(recovered):
    _, out = recovered
    rows = p021_rows(out)
    forbidden = [
        "VEC_derived",
        "Atomic_size_mismatch_delta_pct",
        "Configurational_entropy_J_molK",
        "Mixing_enthalpy_kJ_mol",
        "Omega",
        "Electronegativity_mismatch",
        "Melting_temperature_weighted_K",
        "log10_strain_rate",
    ]
    for field in forbidden:
        if field in rows:
            assert rows[field].isna().all()
    assert not rows.Row_Type.str.contains(
        "synthetic|imputed|replicate specimen", case=False, regex=True
    ).any()
    assert rows.Observation_Role.eq("INDEPENDENT_CONDITION").all()
