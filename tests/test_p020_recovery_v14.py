import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from scripts.integrate_p020_recovery_v14 import (
    AUDIT,
    BOOK,
    BOOK_SHA256,
    DOI,
    MATERIAL,
    MEANINGFUL_NA_FIELDS,
    OUT,
    PAPER_ID,
    PRIMARY_ID,
    PROVENANCE_EXCLUDE,
    SERIES,
    SOURCE,
    SOURCE_SHA256,
    STAGE_IDS,
    TABLE,
    class_counts,
    counts,
    experimental_pool,
    integrate,
    is_present,
)


@pytest.fixture(scope="module")
def recovered():
    before_book = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    before_source = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    source, out = integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest() == before_book == BOOK_SHA256
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before_source == SOURCE_SHA256
    return source, out


def primary(out: pd.DataFrame) -> pd.Series:
    rows = out[out.P020_Record_Role.eq("RECOVERED_EXACT_PRIMARY_CONDITION")]
    assert len(rows) == 1
    return rows.iloc[0]


def stages(out: pd.DataFrame) -> pd.DataFrame:
    return out[
        out.P020_Record_Role.fillna("").str.contains("RECOVERED_CORRELATED")
    ].set_index("Observation_ID")


def load_table(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLE / f"p020_recovery_v14_{name}.csv", low_memory=False)


def test_exact_source_identity_new_paper_and_immutable_v13_prefix(recovered):
    source, out = recovered
    assert (len(source), len(out)) == (207, 214)
    assert not source.Paper_ID.eq(PAPER_ID).any()
    assert not source.DOI.eq(DOI).any()
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    identity = load_table("study_identity").iloc[0]
    assert identity.Paper_ID == PAPER_ID and identity.DOI == DOI
    assert identity.Source_Identity_Status == "VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH"
    assert identity.Journal == "Materials Research Letters"
    assert int(identity.Volume) == 6 and int(identity.Issue) == 11
    assert str(identity.Pages) == "620-626" and int(identity.Year) == 2018


def test_one_primary_condition_and_six_nonindependent_stages(recovered):
    _, out = recovered
    p = primary(out)
    s = stages(out)
    assert p.ML_Condition_ID == PRIMARY_ID
    assert p.Study_Series_ID == SERIES and p.Material_Parent_ID == MATERIAL
    assert p.Leakage_Group_Strict == SERIES and p.Leakage_Group_Material == MATERIAL
    assert p.Independent_ML_sample is True and p.Independent_Experimental_ML_sample is True
    assert p.Data_Origin == "EXPERIMENTAL" and p.Observation_Role == "INDEPENDENT_CONDITION"
    assert pd.isna(p.Physical_Batch_ID) and pd.isna(p.Replicate_ID) and pd.isna(p.Replicate_n)
    assert set(s.index) == STAGE_IDS and len(s) == 6
    assert (~s.Independent_ML_sample.astype(bool)).all()
    assert (~s.Independent_Experimental_ML_sample.astype(bool)).all()
    assert s.ML_Condition_ID.isna().all() and s.Parent_ML_Condition_ID.eq(PRIMARY_ID).all()
    assert s[["Effective_TRIP", "Effective_TWIP"]].isna().all().all()
    hierarchy = load_table("hierarchy").iloc[0]
    assert hierarchy.Counting_Status == "ONE_NEW_INDEPENDENT_CONDITION_SIX_NONINDEPENDENT_CHILDREN"


def test_p020_not_merged_with_p013_or_same_composition_sources(recovered):
    _, out = recovered
    p = primary(out)
    p013 = out[out.Paper_ID.eq("P013")]
    assert p.Paper_ID == "P020" and p.Material_Parent_ID.startswith("P020_")
    assert not p013.Study_Series_ID.eq(SERIES).any()
    assert not p013.Material_Parent_ID.eq(MATERIAL).any()
    assert p.Alloy_Family_Text == "Fe50Mn30Co10Cr10"
    assert p.Alloy_Family_Use == "GROUPING_AUDIT_ONLY_NOT_PREDICTOR_NOT_SAMPLE_IDENTITY"
    safeguards = load_table("scientific_safeguards")
    assert safeguards.Safeguard.eq("COMMON_COMPOSITION_NOT_SAME_SAMPLE").any()


def test_nominal_chemistry_processing_and_no_cross_paper_bulk_transfer(recovered):
    _, out = recovered
    p = primary(out)
    assert p.Original_Composition == "Fe50Mn30Co10Cr10"
    assert p.Nominal_Composition_at_pct == "Fe50Mn30Co10Cr10"
    assert p.Composition_basis == "at.% nominal"
    assert (p["Fe_at%"], p["Mn_at%"], p["Co_at%"], p["Cr_at%"]) == (50, 30, 10, 10)
    assert pd.isna(p["Ni_at%"])
    assert pd.isna(p.Measured_Bulk_Composition)
    assert pd.isna(p.Measured_Composition_at_pct)
    assert p.Composition_Status == "NOMINAL_ONLY_NO_QUANTITATIVE_POSTMELT_BULK_CHEMISTRY_REPORTED"
    assert p.Raw_Material_Purity == ">99.9 wt.%"
    assert p.Melting_Route == "Vacuum arc melting" and p.Casting_Route == "Drop casting"
    assert p.Cast_Bar_Dimensions_mm == "12.7 x 12.7 x 75"
    assert p.Homogenization_T_K == pytest.approx(1423.15)
    assert p.Homogenization_time_h == 4 and p.Homogenization_Atmosphere == "vacuum"
    assert p.Rolling_T_Raw == "room-temperature rolling"
    assert p.Cold_rolling_reduction_pct == 75
    assert p.Annealing_T_K == pytest.approx(1223.15)
    assert p.Annealing_time_min == 60 and p.Post_Anneal_Cooling == "air cooling"


def test_missing_supplement_values_remain_na_without_room_temperature_or_rate_inference(recovered):
    _, out = recovered
    p = primary(out)
    assert p.Test_T_Raw == "NOT_EXPLICITLY_REPORTED_IN_MAIN_ARTICLE"
    assert pd.isna(p.Test_T_K) and pd.isna(p["Strain_rate_s-1"])
    assert pd.isna(p.Gauge_length_mm) and pd.isna(p.Gauge_width_mm)
    assert pd.isna(p.Specimen_thickness_mm) and pd.isna(p.Replicate_n)
    assert p.P020_Supplement_Status == "NOT_INCLUDED_TEST_METADATA_NOT_INFERRED"
    assert p.Test_Metadata_Status == "SUPPLEMENT_REFERENCED_NOT_AVAILABLE_NO_INFERENCE"
    assert "room temperature" not in str(p.Test_T_Raw).lower()
    assert p.Loading_Mode == "Uniaxial tension during real-time in-situ neutron diffraction"


def test_initial_dual_phase_microstructure_and_trip_guardrail(recovered):
    _, out = recovered
    p = primary(out)
    assert p.Initial_Phase == "DUAL_PHASE_FCC_PLUS_HCP"
    assert p.Initial_FCC_fraction == 0.79 and p.Initial_HCP_fraction == 0.21
    assert p.Recovered_Initial_FCC_fraction == 0.79
    assert p.Recovered_Initial_HCP_fraction == 0.21
    assert p.FCC_Grain_Size_um == 40 and p.Grain_Size_Scope == "FCC_AVERAGE"
    assert p.HCP_Lath_Thickness_um == 4
    assert p.FCC_Grain_Morphology == "Equiaxed FCC grains"
    assert p.HCP_Morphology == "Lath-shaped HCP grains"
    assert p.Initial_HCP_Origin == "PRE_EXISTING_BEFORE_TENSILE_LOADING"
    assert p.Initial_TRIP_Target_Guardrail == "PRE_EXISTING_HCP_DOES_NOT_ESTABLISH_TRIP_DYNAMIC_FCC_LOSS_REQUIRED"
    target = load_table("target_evidence").iloc[0]
    assert "decreases continuously" in target.Condition_Level_Evidence


def test_joint_targets_hcp_twip_semantics_and_phase_specific_slip(recovered):
    _, out = recovered
    p = primary(out)
    assert (p.Effective_TRIP, p.Effective_TWIP, p.Slip) == (1, 1, 1)
    assert p.Target_Status == "VERIFIED_JOINT" and p.P020_Target_Status == "VERIFIED_JOINT"
    assert p.TRIP_Parent_Phase == "FCC" and p.TRIP_Product_Phase == "HCP"
    assert p.TWIP_Phase == "HCP"
    assert p.TWIP_Mode == "HCP_TENSILE_AND_COMPRESSION_TWINNING"
    assert p.TWIP_Evidence_Type == "DIRECT_REALTIME_NEUTRON_GRAIN_REORIENTATION"
    assert "not FCC" in p.P020_Target_Semantic_Note
    assert p.Mechanism_Phase_Scope == "TRIP: FCC_TO_HCP; TWIP: HCP_TENSILE_AND_COMPRESSION; SLIP: FCC_AND_HCP"
    assert "HCP" in p.Evidence_TWIP and "FCC loss" in p.Evidence_TRIP


def test_in_situ_stage_landmarks_and_stage_zero_scope(recovered):
    _, out = recovered
    s = stages(out)
    assert s.loc["P020_STAGE_I_ELASTIC", ["TRIP_Stage", "TWIP_Stage", "Slip_Stage"]].astype(int).tolist() == [0, 0, 0]
    assert "never condition-level negatives" in s.loc["P020_STAGE_I_ELASTIC", "P020_Target_Semantic_Note"]
    assert s.loc["P020_STAGE_TRIP_ONSET", "Macro_Stress_MPa"] == 200
    assert s.loc["P020_STAGE_TRIP_ONSET", ["TRIP_Stage", "TWIP_Stage", "Slip_Stage"]].astype(int).tolist() == [1, 0, 1]
    assert s.loc["P020_STAGE_HCP_TENSILE_TWIN", "Macro_Stress_MPa"] == 400
    assert s.loc["P020_STAGE_HCP_TENSILE_TWIN", "TWIP_Phase"] == "HCP"
    assert s.loc["P020_STAGE_HCP_TENSILE_TWIN", "TWIP_Mode"] == "HCP_{10.2}_TENSILE_TWINNING"
    assert s.loc["P020_STAGE_MULTI_TWIN", "Macro_Stress_MPa"] == 730
    assert s.loc["P020_STAGE_MULTI_TWIN", "Macro_Strain_pct"] == 15
    assert s.loc["P020_STAGE_MULTI_TWIN", "TWIP_Mode"] == "HCP_COMPRESSION_AND_MULTIPLE_TWINNING"


def test_late_trip_suppression_remains_positive_and_fracture_complement_not_fabricated(recovered):
    _, out = recovered
    p = primary(out)
    s = stages(out)
    late = s.loc["P020_STAGE_LATE_TRIP_SUPPRESSION"]
    assert late.Macro_Strain_pct == 25 and late.TRIP_Stage == 1
    assert late.TRIP_Rate_Status == "RATE_DECREASED_TRIP_REMAINS_ACTIVE"
    assert "> approximately 25% strain" == late.Stage_Strain_Relation
    fracture = s.loc["P020_STAGE_FRACTURE"]
    assert fracture.FCC_fraction_at_fracture == 0.17
    assert pd.isna(fracture.HCP_fraction_at_fracture)
    assert p.FCC_fraction_at_fracture == 0.17 and pd.isna(p.HCP_fraction_at_fracture)
    phase = load_table("phase_evolution").set_index("Phase_Record_ID")
    assert phase.loc["P020_PHASE_FRACTURE", "FCC_Fraction"] == 0.17
    assert pd.isna(phase.loc["P020_PHASE_FRACTURE", "HCP_Fraction"])
    assert not out.HCP_fraction_at_fracture.eq(0.83).any()


def test_mechanical_response_preserves_definition_and_raw_basis(recovered):
    _, out = recovered
    p = primary(out)
    assert p.Apparent_Yield_Onset_MPa == 200
    assert p.Yield_Definition == "OBSERVABLE_DEVIATION_FROM_ELASTIC_REGIME"
    assert pd.isna(p.YS_MPa)
    assert p.Reported_Ultimate_Strength_MPa == 1046
    assert p.Reported_Elongation_pct == 34
    assert pd.isna(p.UTS_MPa) and pd.isna(p.Elongation_pct)
    assert "macro true stress/true strain" in p.Strain_Basis_Status
    assert p.Mechanical_Predictor_Eligibility == "MECHANICAL_OUTCOME_LEAKAGE"
    mechanics = load_table("mechanical_response").iloc[0]
    assert mechanics.Reported_Ultimate_Strength_MPa == 1046
    assert mechanics.Reported_Elongation_pct == 34


def test_neutron_method_metadata_is_preserved(recovered):
    _, out = recovered
    p = primary(out)
    assert p.Instrument == "VULCAN"
    assert p.Facility == "Spallation Neutron Source, ORNL"
    assert p.Diffraction_Type == "Real-time in-situ time-of-flight neutron diffraction"
    assert p.Detector_Directions == "Loading direction (LD) and transverse direction (TD)"
    assert p.Detector_Banks == "-90 degrees and +90 degrees"
    assert p.Phase_Quantification_Method == "Rietveld refinement"
    assert p.Peak_Analysis_Method == "Single-peak fitting"
    method = load_table("neutron_method_metadata").iloc[0]
    assert method.Instrument == "VULCAN" and "Rietveld" in method.Phase_Quantification


def test_sfe_and_deltag_remain_na_without_cross_paper_transfer(recovered):
    _, out = recovered
    p = primary(out)
    assert pd.isna(p.SFE_mJ_m2) and pd.isna(p.SFE_method)
    assert pd.isna(p.DeltaG_FCC_HCP_J_mol) and pd.isna(p.DeltaG_method)
    assert p.SFE_Value_Status == "NOT_REPORTED_IN_P020_MAIN_ARTICLE_NO_CROSS_PAPER_TRANSFER"
    assert p.DeltaG_Value_Status == "NOT_REPORTED_IN_P020_MAIN_ARTICLE_NO_CROSS_PAPER_TRANSFER"
    prov = load_table("provenance")
    p020_physics = prov[prov.Feature_Name.isin(["SFE_mJ_m2", "SFE_method", "DeltaG_FCC_HCP_J_mol", "DeltaG_method"])]
    assert p020_physics.Recovered_Value.eq("UNRESOLVED_NA").all()
    assert p020_physics.Recovery_Status.str.contains("NO_CROSS_PAPER_TRANSFER").all()
    assert not p020_physics.Recovered_Value.astype(str).eq("6.5").any()


def test_replacement_aware_counts_change_only_by_one_verified_joint_condition(recovered):
    source, out = recovered
    assert counts(source) == (51, 31, 29, 26)
    assert counts(out) == (52, 32, 30, 27)
    assert class_counts(source) == {
        "trip_positive": 27, "trip_negative": 4, "twip_positive": 24,
        "twip_negative": 5, "joint_00": 0, "joint_10": 5,
        "joint_01": 4, "joint_11": 17,
    }
    assert class_counts(out) == {
        "trip_positive": 28, "trip_negative": 4, "twip_positive": 25,
        "twip_negative": 5, "joint_00": 0, "joint_10": 5,
        "joint_01": 4, "joint_11": 18,
    }
    pool = experimental_pool(out)
    assert len(pool) == 52 and pool.ML_Condition_ID.is_unique
    assert int(pool.ML_Condition_ID.eq(PRIMARY_ID).sum()) == 1


def test_every_new_master_value_and_meaningful_na_has_provenance(recovered):
    source, out = recovered
    prov = load_table("provenance")
    required = {
        "Paper_ID", "DOI", "Study_Series_ID", "Material_Parent_ID",
        "ML_Condition_ID", "Observation_ID", "Feature_Name", "Recovered_Value",
        "Units", "Evidence_Type", "Evidence_Location", "Method", "Confidence",
        "Recovery_Status", "Data_Origin",
    }
    assert required <= set(prov)
    nonnullable = required - {"ML_Condition_ID", "Observation_ID"}
    assert prov[list(nonnullable)].notna().all().all()
    master = prov[prov.Provenance_Layer.eq("MASTER_FIELD_MAPPING")]
    for _, record in out.iloc[len(source):].iterrows():
        record_id = record.Observation_ID
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            meaningful_na = (
                record_id == "P020_OBS_PRIMARY" and feature in MEANINGFUL_NA_FIELDS
            ) or (
                record_id == "P020_STAGE_FRACTURE"
                and feature == "HCP_fraction_at_fracture"
            )
            if is_present(value) or meaningful_na:
                hit = master[
                    master.Record_ID.eq(record_id)
                    & master.Feature_Name.eq(feature)
                ]
                assert len(hit), (record_id, feature)
    for text in out.iloc[len(source):].P020_Recovery_Provenance_JSON:
        assert "NaN" not in text and len(json.loads(text)) > 0


def test_no_modelling_feature_engineering_imputation_or_synthetic_records(recovered):
    source, out = recovered
    script = (Path(__file__).parents[1] / "scripts/integrate_p020_recovery_v14.py").read_text(encoding="utf-8").lower()
    for token in [
        "import sklearn", "import xgboost", "accuracy_score(", "roc_auc_score(",
        "fit_resample(", "smote(", ".fit(", "standardscaler", "onehotencoder",
    ]:
        assert token not in script
    assert len(out) == len(source) + 7
    assert not out.P020_Record_Role.fillna("").str.contains(
        "SYNTHETIC|SMOTE|OVERSAMPLE|UNDERSAMPLE|REPLICATE_ROW",
        case=False,
        regex=True,
    ).any()
    added = set(out.columns) - set(source.columns)
    assert not added & {
        "VEC", "Omega", "Mixing_Entropy", "Entropy_of_Mixing",
        "Enthalpy_of_Mixing", "Normalized_Composition",
    }
    assert not any(
        path.is_file()
        for path in (Path(__file__).parents[1] / "models/trained").glob("*.*")
        if path.name != ".gitkeep"
    )


def test_required_supporting_tables_audit_and_deferred_refresh(recovered):
    _, _ = recovered
    names = {
        "study_identity", "hierarchy", "processing", "initial_microstructure",
        "mechanical_response", "target_evidence", "phase_evolution",
        "in_situ_stage_evidence", "neutron_method_metadata", "provenance",
        "scientific_safeguards", "integration_decision_ledger",
    }
    for name in names:
        path = TABLE / f"p020_recovery_v14_{name}.csv"
        assert path.exists() and path.stat().st_size > 0
    text = AUDIT.read_text(encoding="utf-8")
    assert "51 before -> 52 after" in text
    assert "31/29/26 before -> 32/30/27 after" in text
    assert "Global QC" in text and "Feature Schema" in text and "Grouped Split Design" in text
    assert "deliberately not refreshed" in text
    assert "No ML model was trained" in text
    assert OUT.exists() and OUT.stat().st_size > 0
