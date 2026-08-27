import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from scripts.integrate_p002_recovery_v13 import (
    AUDIT,
    BOOK,
    BOOK_SHA256,
    CORRIGENDUM_DOI,
    DOI,
    EXACT_IDS,
    EXACT_SCIENTIFIC_FIELDS,
    MATERIAL,
    MEANINGFUL_NA_FIELDS,
    OUT,
    SERIES,
    SOURCE,
    SOURCE_SHA256,
    STAGE_SCIENTIFIC_FIELDS,
    SUPPORT_SCIENTIFIC_FIELDS,
    TABLE,
    counts,
    experimental_pool,
    integrate,
)


@pytest.fixture(scope="module")
def recovered():
    before_book = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    before_source = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    source, out = integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest() == before_book == BOOK_SHA256
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == before_source == SOURCE_SHA256
    return source, out


def exact(out):
    return out[out.P002_Record_Role.eq("RECOVERED_EXACT_CONDITION")].set_index("ML_Condition_ID")


def load_table(name):
    return pd.read_csv(TABLE / f"p002_recovery_v13_{name}.csv", low_memory=False)


def test_source_identity_corrigendum_and_immutable_prefix(recovered):
    source, out = recovered
    assert (len(source), len(out)) == (192, 207)
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    corr = load_table("corrigendum").iloc[0]
    assert corr.Paper_ID == "P002" and corr.Original_DOI == DOI
    assert corr.Corrigendum_DOI == CORRIGENDUM_DOI and corr.Status == "APPLIED"
    assert corr.Corrected_Text_Semantic == "800C condition has more pronounced TRIP than 700C condition"
    assert "self-comparison typo" in corr.Original_Text_Semantic
    stage = load_table("stage_evidence")
    assert stage.set_index("Observation_ID").loc["P002_A800_EBSD_45", "HCP_Martensite_Fraction"] == 0.057
    assert stage.set_index("Observation_ID").loc["P002_A700_EBSD_45", "HCP_Martensite_Fraction"] == 0.038


def test_three_exact_conditions_hierarchy_independence_and_replicates(recovered):
    _, out = recovered
    p = exact(out)
    assert set(p.index) == EXACT_IDS and len(p) == 3
    assert p.Paper_ID.eq("P002").all() and p.DOI.eq(DOI).all()
    assert p.Study_Series_ID.eq(SERIES).all() and p.Material_Parent_ID.eq(MATERIAL).all()
    assert p.Leakage_Group_Strict.eq(SERIES).all() and p.Leakage_Group_Material.eq(MATERIAL).all()
    assert p.Independent_ML_sample.eq(True).all()
    assert p.Independent_Experimental_ML_sample.eq(True).all()
    assert p.Replicate_n.eq(3).all() and p.Replicate_ID.isna().all()
    assert p.Physical_Batch_ID.isna().all()
    assert not out.Replicate_ID.notna().loc[out.P002_Record_Role.notna()].any()
    assert len(out[out.P002_Record_Role.eq("RECOVERED_CORRELATED_STAGE_OR_POST_TEST_EVIDENCE")]) == 10
    assert len(out[out.P002_Record_Role.eq("HALL_PETCH_SUPPORT_ONLY")]) == 2


def test_nominal_chemistry_processing_and_room_temperature_scope(recovered):
    _, out = recovered
    p = exact(out)
    status = "NOMINAL_ONLY_EDS_QUALITATIVE_HOMOGENEITY_NO_QUANTITATIVE_BULK_ANALYSIS"
    assert p.Original_Composition.eq("Fe40Mn10Co20Cr20Ni10").all()
    assert p.Composition_Status.eq(status).all()
    assert p.Measured_Bulk_Composition.isna().all()
    assert p.Measured_Composition_at_pct.isna().all()
    assert p.Recovered_Bulk_Composition_at_pct.isna().all()
    assert p.EDS_Qualitative_Homogeneity.dropna().str.contains("qualitative", case=False).all()
    assert not p.EDS_Qualitative_Homogeneity.fillna("").str.contains(r"\d+\s*(?:at|wt)\.?%", case=False, regex=True).any()
    assert p.Hot_rolling_reduction_pct.eq(50).all() and p.Cold_rolling_reduction_pct.eq(70).all()
    assert p.Hot_Roll_Input_Thickness_mm.eq(10).all() and p.Hot_Roll_Output_Thickness_mm.eq(5).all()
    assert p.Cold_Roll_Input_Thickness_mm.eq(5).all() and p.Cold_Roll_Output_Thickness_mm.eq(1.5).all()
    assert p.Homogenization_time_h.eq(2).all() and p.Homogenization_Atmosphere.eq("Ar").all()
    assert p.Test_T_Raw.eq("room temperature").all() and p.Test_T_K.isna().all()
    assert p["Strain_rate_s-1"].eq(1e-3).all()
    assert p.Loading_Mode.eq("Uniaxial tension").all()
    assert p.Gauge_length_mm.eq(10).all() and p.Gauge_width_mm.eq(2.5).all()
    assert p.Specimen_thickness_mm.eq(1.25).all()


def test_initial_microstructure_and_initial_twin_guardrail(recovered):
    _, out = recovered
    p = exact(out)
    assert p.Initial_Phase.eq("Single FCC").all()
    assert p.Initial_FCC_fraction.isna().all()
    assert p.Initial_HCP_fraction.eq(0).all()
    assert p.Initial_HCP_Status.str.startswith("DIRECT_EBSD_PHASE_ABSENCE").all()
    assert p.Initial_Twin_Target_Safety.eq("PRETEST_TWINS_DO_NOT_ESTABLISH_TENSILE_TWIP").all()
    assert p.loc["P002_MC_A800_RT", "Recrystallized_fraction"] == 1
    assert p.loc["P002_MC_A800_RT", "NonRecrystallized_fraction"] == 0
    assert p.loc["P002_MC_A800_RT", "RZ_Grain_Size_um"] == 4.7
    assert p.loc["P002_MC_A800_RT", "RZ_Grain_Size_Uncertainty_um"] == 0.3
    assert p.loc["P002_MC_A700_RT", "Recrystallized_fraction"] == 0.92
    assert p.loc["P002_MC_A700_RT", "NonRecrystallized_fraction"] == 0.08
    assert p.loc["P002_MC_A700_RT", "RZ_Grain_Size_um"] == 3.6
    assert p.loc["P002_MC_A700_RT", "NRZ_Subgrain_Size_um"] == 0.95
    assert p.loc["P002_MC_A700_RT", "NRZ_Avg_Dimension_um"] == 12
    assert p.loc["P002_MC_A700_RT", "PreTest_Twin_Width_nm"] == 220
    assert p.loc["P002_MC_A700_RT", "Sigma3_Twin_Boundary_Fraction_Raw"] == "~27.5 vol% in RZ"
    assert p.loc["P002_MC_A600_RT", "Recrystallized_fraction"] == 0.13
    assert p.loc["P002_MC_A600_RT", "NonRecrystallized_fraction"] == 0.87
    assert p.loc["P002_MC_A600_RT", "RZ_Grain_Size_um"] == 1.8
    assert p.loc["P002_MC_A600_RT", "NRZ_Subgrain_Size_um"] == 0.4
    # A600 has pre-test twins yet remains TWIP=NA: the initial state did not create a target.
    assert "TWIN" in p.loc["P002_MC_A600_RT", "PreTest_Twin_Origin"]
    assert pd.isna(p.loc["P002_MC_A600_RT", "Effective_TWIP"])


def test_targets_evidence_grades_and_a600_insufficient_negative(recovered):
    _, out = recovered
    p = exact(out)
    assert (p.loc["P002_MC_A700_RT", ["Effective_TRIP", "Effective_TWIP", "Slip"]].astype(float) == 1).all()
    assert (p.loc["P002_MC_A800_RT", ["Effective_TRIP", "Effective_TWIP", "Slip"]].astype(float) == 1).all()
    assert p.loc["P002_MC_A700_RT", "TWIP_Evidence_Type"] == "DIRECT_TEM_DEFORMATION_TWIN_BUNDLES"
    assert p.loc["P002_MC_A800_RT", "TWIP_Evidence_Type"] == "AUTHOR_CONDITION_ATTRIBUTION_SUPPORTED_BY_STUDY_CONCLUSION"
    assert p.loc["P002_MC_A700_RT", "Target_Evidence_Confidence"] == "High"
    assert p.loc["P002_MC_A800_RT", "Target_Evidence_Confidence"] == "High_TRIP_Medium_TWIP"
    assert p.loc["P002_MC_A800_RT", "TWIP_Evidence_Type"] != "DIRECT_TEM_DEFORMATION_TWIN_BUNDLES"
    a600 = p.loc["P002_MC_A600_RT"]
    assert a600.Original_TRIP == 0 and a600.Original_TWIP == 0
    assert pd.isna(a600.Effective_TRIP) and pd.isna(a600.Effective_TWIP)
    assert a600.Negative_Evidence_Status == "INSUFFICIENT_FOR_ZERO" and float(a600.Slip) == 1
    assert pd.isna(a600.UTS_MPa) and pd.isna(a600.Elongation_pct)
    assert a600.YS_MPa == 1060 and a600.Mechanical_Value_Status == "PARTIAL_DIRECT_TEXT"
    ledger = load_table("decision_correction_ledger").set_index("Ledger_ID")
    assert ledger.loc["C001", "Legacy_Value"] == "0"
    assert ledger.loc["C001", "Verified_Value"] == "UNRESOLVED_NA"
    assert ledger.loc["C002", "Verified_Value"] == "UNRESOLVED_NA"
    assert ledger.loc["C005", "Corrigendum_DOI"] == CORRIGENDUM_DOI


def test_correlated_stage_values_are_preserved_without_independent_inflation(recovered):
    _, out = recovered
    s = out[out.P002_Record_Role.eq("RECOVERED_CORRELATED_STAGE_OR_POST_TEST_EVIDENCE")].set_index("Observation_ID")
    assert (~s.Independent_ML_sample).all() and (~s.Independent_Experimental_ML_sample).all()
    assert s.ML_Condition_ID.isna().all()
    assert s.loc["P002_A800_EBSD_45", "HCP_Martensite_Fraction_at_Stage"] == 0.057
    assert s.loc["P002_A800_EBSD_65", "HCP_Martensite_Fraction_at_Stage"] == 0.163
    assert pd.isna(s.loc["P002_A800_EBSD_10", "HCP_Martensite_Fraction_at_Stage"])
    assert s.loc["P002_A700_EBSD_10", "HCP_Martensite_Fraction_at_Stage"] == 0.007
    assert s.loc["P002_A700_EBSD_45", "HCP_Martensite_Fraction_at_Stage"] == 0.038
    assert s.loc["P002_A700_EBSD_65", "HCP_Martensite_Fraction_at_Stage"] == 0.072
    assert s.loc["P002_A700_TEM_FRACTURE", "Observation_Role"] == "CORRELATED_POST_TEST_EVIDENCE"
    assert s.loc["P002_A700_TEM_FRACTURE", "TWIP_at_stage"] == 1
    assert s[["Effective_TRIP", "Effective_TWIP"]].isna().all().all()


def test_method_specific_physics_and_hall_petch_leakage_scope(recovered):
    _, out = recovered
    p = exact(out)
    assert p.SFE_mJ_m2.eq(14).all()
    assert p.SFE_Value_Status.eq("CURRENT_PAPER_THERMODYNAMIC_ESTIMATE").all()
    assert p.SFE_Data_Origin.eq("THERMODYNAMIC_ESTIMATE_NOT_EXPERIMENTAL").all()
    assert p.DeltaG_FCC_HCP_J_mol.eq(-292).all()
    assert p.DeltaG_method.eq("Thermo-Calc TCFE7").all()
    assert p.DeltaG_Value_Status.eq("CURRENT_PAPER_CALCULATED").all()
    assert p.Physics_Temperature_K.eq(300).all()
    physics = load_table("physics_thermodynamics").set_index("Feature")
    assert physics.loc["Transformation_strain_energy", "Value"] == 22.2
    assert physics.loc["Transformation_strain_energy", "Status"] == "REFERENCE_MODEL_INPUT"
    assert physics.loc["FCC_HCP_interfacial_energy", "Value"] == 15
    assert physics.loc["Planar_packing_density", "Value"] == pytest.approx(2.98e-5)
    assert physics.loc["Lattice_constant_a", "Value"] == 0.3587
    assert physics.loc["Lattice_friction_stress_sigma0", "Value"] == 139
    assert physics.loc["Hall_Petch_coefficient_k", "Value"] == 504
    assert physics.loc["Lattice_friction_stress_sigma0", "Predictor_Timing"] == "MODEL_DERIVED_LEAKAGE"
    hall = load_table("hall_petch_support").set_index("Support_Record_ID")
    assert set(hall.index) == {"P002_HP_HOMOG", "P002_HP_A900", "P002_HP_A800"}
    assert hall.loc["P002_HP_A800", "Role"] == "HALL_PETCH_SUPPORT_DUPLICATES_PRIMARY_MECHANICS"
    assert not out.Support_Record_ID.eq("P002_HP_A800").any()


def test_legacy_mapping_and_replacement_aware_count_changes(recovered):
    source, out = recovered
    mapping = load_table("legacy_mapping").set_index("Legacy_Condition_ID")
    assert len(mapping) == 5
    assert mapping.loc["P002_C01", "Exact_ML_Condition_ID"] == "P002_MC_A800_RT"
    assert mapping.loc["P002_C02", "Exact_ML_Condition_ID"] == "P002_MC_A700_RT"
    assert mapping.loc["P002_C03", "Exact_ML_Condition_ID"] == "P002_MC_A600_RT"
    assert "not row order" in mapping.loc["P002_C01", "Match_Basis"]
    assert mapping.loc["P002_C03", "Conflict_Status"] == "LEGACY_ZERO_CONFLICTS_WITH_VERIFIED_INSUFFICIENT_NEGATIVE_EVIDENCE"
    assert counts(source) == (51, 32, 30, 27)
    assert counts(out) == (51, 31, 29, 26)
    pool = experimental_pool(out)
    assert pool.ML_Condition_ID.is_unique and len(pool) == 51
    assert not set(pool.Condition_ID) & {"P002_C01", "P002_C02", "P002_C03"}
    joint = pool.dropna(subset=["Effective_TRIP", "Effective_TWIP"])
    states = (
        joint.Effective_TRIP.astype(int).astype(str)
        + joint.Effective_TWIP.astype(int).astype(str)
    ).value_counts().to_dict()
    assert states == {"11": 17, "10": 5, "01": 4}


def test_every_new_master_scientific_value_has_field_provenance(recovered):
    _, out = recovered
    prov = load_table("provenance")
    required = {
        "Paper_ID",
        "DOI",
        "Material_Parent_ID",
        "ML_Condition_ID",
        "Record_ID",
        "Feature_Name",
        "Recovered_Value",
        "Units",
        "Evidence_Type",
        "Evidence_Location",
        "Method",
        "Confidence",
        "Recovery_Status",
    }
    assert required <= set(prov)
    nonnullable = required - {"ML_Condition_ID"}
    assert prov[list(nonnullable)].notna().all().all()
    for mc, row in exact(out).iterrows():
        for field in EXACT_SCIENTIFIC_FIELDS:
            if pd.notna(row[field]) or field in MEANINGFUL_NA_FIELDS:
                hit = prov[prov.Record_ID.eq(mc) & prov.Feature_Name.eq(field)]
                assert len(hit), (mc, field)
                assert hit.Recovered_Value.notna().all()
    stages = out[out.P002_Record_Role.eq("RECOVERED_CORRELATED_STAGE_OR_POST_TEST_EVIDENCE")]
    for _, row in stages.iterrows():
        for field in STAGE_SCIENTIFIC_FIELDS:
            if pd.notna(row[field]):
                assert len(prov[prov.Record_ID.eq(row.Observation_ID) & prov.Feature_Name.eq(field)])
    support = out[out.P002_Record_Role.eq("HALL_PETCH_SUPPORT_ONLY")]
    for _, row in support.iterrows():
        for field in SUPPORT_SCIENTIFIC_FIELDS:
            if pd.notna(row[field]):
                assert len(prov[prov.Record_ID.eq(row.Support_Record_ID) & prov.Feature_Name.eq(field)])
    for text in exact(out).P002_Recovery_Provenance_JSON:
        assert "NaN" not in text
        assert len(json.loads(text)) > 0


def test_no_forbidden_transformation_resampling_or_model_output(recovered):
    source, out = recovered
    added = set(out.columns) - set(source.columns)
    forbidden_descriptors = {
        "VEC",
        "Omega",
        "Mixing_Entropy",
        "Entropy_of_Mixing",
        "Enthalpy_of_Mixing",
        "Electronegativity_Descriptor",
        "Normalized_Composition",
    }
    assert not added & forbidden_descriptors
    assert len(out) == len(source) + 15
    assert not out.P002_Record_Role.fillna("").str.contains("SYNTHETIC|SMOTE|OVERSAMPLE|UNDERSAMPLE", case=False, regex=True).any()
    script = (Path(__file__).parents[1] / "scripts/integrate_p002_recovery_v13.py").read_text(encoding="utf-8").lower()
    for token in ["import sklearn", "import xgboost", "accuracy_score(", "roc_auc_score(", "fit_resample(", "smote("]:
        assert token not in script
    assert not any(path.is_file() for path in (Path(__file__).parents[1] / "models/trained").glob("*.*") if path.name != ".gitkeep")


def test_audit_requires_downstream_refresh_without_performing_it(recovered):
    _, _ = recovered
    text = AUDIT.read_text(encoding="utf-8")
    assert "Global QC" in text and "Feature Schema V1" in text and "Grouped Split Design V1" in text
    assert "stale with respect to V13" in text
    assert "must be refreshed before matrix construction" in text
    assert "No ML" in text and "no feature engineering" in text.lower()
    assert OUT.exists() and OUT.stat().st_size > 0
