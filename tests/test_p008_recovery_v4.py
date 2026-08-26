import hashlib

import pandas as pd

from scripts.integrate_p008_recovery import BOOK, integrate, independent


def test_v4_preserves_v3_and_verified_workbook():
    digest = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    before, after = integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest() == digest
    assert len(before) == 113 and len(after) == 118
    assert after.loc[:112, "Condition_ID"].tolist() == before.Condition_ID.tolist()
    original = [c for c in before if not c.startswith("Recovered_") and c not in {
        "ML_Condition_ID", "Effective_TRIP", "Effective_TWIP", "Study_Series_ID",
        "Material_Parent_ID", "Physical_Batch_ID", "Replicate_ID",
        "Leakage_Group_Strict", "Leakage_Group_Material"}]
    pd.testing.assert_frame_equal(after.loc[:112, original].reset_index(drop=True), before[original], check_dtype=False)


def test_exact_hierarchy_mapping_and_no_double_counting():
    _, out = integrate()
    p8 = out[out.Paper_ID.eq("P008")]
    exact = p8[p8.P008_Record_Role.str.startswith("EXACT", na=False)]
    assert len(exact) == 6 and exact.ML_Condition_ID.nunique() == 6
    assert set(exact.Study_Series_ID) == {"P008_SERIES01"}
    assert set(exact.Material_Parent_ID) == {"P008_MAT_N0", "P008_MAT_N2p6"}
    assert exact.Physical_Batch_ID.isna().all() and exact.Replicate_ID.isna().all()
    assert p8.loc[p8.Condition_ID.eq("P008_C02"), "ML_Condition_ID"].iloc[0] == "P008_MC_N2p6_PC"
    c01 = p8[p8.Condition_ID.eq("P008_C01")].iloc[0]
    assert c01.P008_Legacy_Mapping_Status == "MANUAL_IDENTITY_REVIEW"
    assert len(independent(out)) == len(independent(pd.read_csv("data/processed/master_19papers_recovery_v3.csv"))) + 4


def test_phase_target_sfe_and_auxiliary_semantics():
    _, out = integrate()
    exact = out[out.P008_Record_Role.str.startswith("EXACT", na=False)].set_index("ML_Condition_ID")
    pc = exact.loc["P008_MC_N2p6_PC"]
    assert pd.isna(pc.Recovered_Initial_FCC_fraction)
    assert pc.Initial_BCC_alpha_martensite_fraction == .24
    assert pc.Recovered_Initial_HCP_fraction == 0
    assert (exact.loc["P008_MC_N0_PC", ["Effective_TRIP", "Effective_TWIP"]] == [1, 1]).all()
    assert exact.loc["P008_MC_N0_FC", "Effective_TRIP"] == 1 and pd.isna(exact.loc["P008_MC_N0_FC", "Effective_TWIP"])
    assert (exact.loc["P008_MC_N2p6_PC", ["Effective_TRIP", "Effective_TWIP"]] == [0, 1]).all()
    assert (exact.loc["P008_MC_N2p6_FC", ["Effective_TRIP", "Effective_TWIP"]] == [0, 1]).all()
    assert exact.loc[["P008_MC_N0_HOMO", "P008_MC_N2p6_HOMO"], ["Effective_TRIP", "Effective_TWIP"]].isna().all().all()
    assert exact.SFE_mJ_m2.isna().all()
    assert set(exact[exact.Material_Parent_ID.eq("P008_MAT_N2p6")].SFE_scope) == {"ALLOY_LEVEL"}
    aux = pd.read_csv("reports/tables/p008_recovery_v4_aux_n_series.csv")
    assert len(aux) == 8
    assert not set(aux.query("Primary_ML_Eligibility.str.startswith('AUXILIARY')", engine="python").Alloy_Label) & set(out.ML_Condition_ID.dropna())


def test_provenance_and_special_microstructures_are_separate():
    _, out = integrate()
    prov = pd.read_csv("reports/tables/p008_recovery_v4_provenance.csv")
    required = ["Paper_ID", "DOI", "ML_Condition_ID", "Feature_Name", "Recovered_Value",
                "Evidence_Type", "Evidence_Location", "Extraction_Method", "Confidence", "Recovery_Status"]
    assert prov[required].notna().all().all()
    assert set(prov.ML_Condition_ID) == {"P008_MC_N0_HOMO", "P008_MC_N0_PC", "P008_MC_N0_FC",
        "P008_MC_N2p6_HOMO", "P008_MC_N2p6_PC", "P008_MC_N2p6_FC"}
    pc = out[out.ML_Condition_ID.eq("P008_MC_N2p6_PC")].iloc[0]
    assert pc.Recovery_twin_fraction == .095
    assert pc.Deformation_twin_width == "~3"
    assert pc.Precipitate_type == "Cr2N"
    assert pc.APT_local_composition != pc.Recovered_Bulk_Composition_at_pct
