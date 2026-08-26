import hashlib
import pandas as pd
from scripts.integrate_p014_recovery import BOOK, TABLE, counts, integrate

def parts(out):
    return (out[out.P014_Record_Role.eq("RECOVERED_EXACT_CONDITION")].set_index("ML_Condition_ID"),
            out[out.P014_Record_Role.eq("RECOVERED_A600_STAGE_CHILD")].set_index("Observation_ID"))

def test_v9_preserves_v8_and_workbook():
    digest=hashlib.sha256(BOOK.read_bytes()).hexdigest(); before,out=integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==digest and (len(before),len(out))==(169,178)
    pd.testing.assert_frame_equal(out.iloc[:169][before.columns].reset_index(drop=True),before,check_dtype=False)

def test_hierarchy_replicates_temperature_chemistry_and_counts():
    before,out=integrate(); p,s=parts(out)
    assert list(p.index)==["P014_MC_ASCAST","P014_MC_CR","P014_MC_A600","P014_MC_A650","P014_MC_A700"]
    assert p.Independent_ML_sample.eq(True).all() and len(s)==4 and s.Independent_ML_sample.eq(False).all() and s.ML_Condition_ID.isna().all()
    assert p.Replicate_n.eq(3).all() and p.Replicate_ID.isna().all() and p.uncertainty_type.eq("UNKNOWN_REPORTED_PM").all()
    assert p.Test_T_K.isna().all() and p.Test_T_Raw.eq("Not explicitly specified").all()
    assert p.Measured_Composition_at_pct.isna().all() and p.Composition_Status.eq("NOMINAL_ONLY_NO_BULK_CHEMICAL_ANALYSIS_REPORTED").all()
    assert counts(out)[0]==counts(before)[0]  # five exact replacements for five legacy representations

def test_targets_processing_twin_safety_and_stages():
    _,out=integrate(); p,s=parts(out)
    assert tuple(p.loc["P014_MC_CR",["Processing_TRIP","Processing_TWIP"]])==(1,1)
    assert p.loc["P014_MC_CR",["Effective_TRIP","Effective_TWIP"]].isna().all()
    assert tuple(p.loc["P014_MC_A600",["Effective_TRIP","Effective_TWIP","Slip","HDI_Hardening"]])==(1,1,1,1)
    assert p.loc[["P014_MC_ASCAST","P014_MC_A650","P014_MC_A700"],["Effective_TRIP","Effective_TWIP"]].isna().all().all()
    assert s.loc["P014_OBS_A600_eps0",["Effective_TRIP","Effective_TWIP"]].isna().all()
    assert s.loc["P014_OBS_A600_eps15","Effective_TRIP"]==1 and pd.isna(s.loc["P014_OBS_A600_eps15","Effective_TWIP"])
    assert tuple(s.loc["P014_OBS_A600_eps30",["Effective_TRIP","Effective_TWIP"]])==(1,1)
    assert tuple(s.loc["P014_OBS_A600_FRACTURE",["Effective_TRIP","Effective_TWIP"]])==(1,1)
    assert s.loc[["P014_OBS_A600_eps0","P014_OBS_A600_eps15","P014_OBS_A600_eps30","P014_OBS_A600_FRACTURE"],"HCP_fraction_at_condition"].tolist()==[0,.184,.604,.651]
    assert pd.isna(s.loc["P014_OBS_A600_FRACTURE","Tensile_Strain_pct"])

def test_state_descriptors_conflict_and_missing_physics():
    _,out=integrate(); p,_=parts(out)
    assert p.loc["P014_MC_A650","Initial_HCP_fraction"]==.001
    assert p.loc["P014_MC_A650","Initial_Phase_Status"]=="TRACE_EBSD_HCP_CONFLICTS_WITH_SINGLE_FCC_TEXT_XRD"
    expected={"P014_MC_ASCAST":(28.03,5.12,.04),"P014_MC_CR":(.71,.18,.8),"P014_MC_A600":(.79,.3,.85),"P014_MC_A650":(1.1,.57,.39),"P014_MC_A700":(1.16,.6,.3)}
    for k,v in expected.items(): assert tuple(p.loc[k,["Grain_size_um","Grain_size_SD_um","KAM_mean_deg"]])==v
    assert tuple(p.loc[["P014_MC_A600","P014_MC_A650","P014_MC_A700"],"Recrystallized_fraction"])==(.102,.658,.747)
    assert p.KAM_Status.eq("DIRECT_EBSD_FIGURE_LABEL").all() and p.SFE_mJ_m2.isna().all() and p.DeltaG_FCC_HCP_J_mol.isna().all()

def test_supporting_tables_provenance_hdi_and_legacy_mapping():
    integrate(); h=pd.read_csv(TABLE/"p014_recovery_v9_hdi_strengthening.csv")
    x=h[h.Feature.eq("HDI_strength_contribution")].iloc[0]
    assert x.Value==631.2 and x.Value_Status=="CURRENT_PAPER_FIT_INTERCEPT/REPORTED_CONTRIBUTION" and x.ML_Use_Status=="POTENTIAL_TARGET_LEAKAGE_FEATURE"
    assert h[h.Feature.eq("Shear_modulus_G")].iloc[0].Value_Status=="SECONDARY_REFERENCE_INPUT"
    assert h[h.Feature.eq("Hall_Petch_k")].iloc[0].Value_Status=="SECONDARY_REFERENCE_INPUT"
    mapping=pd.read_csv(TABLE/"p014_recovery_v9_legacy_mapping.csv"); assert len(mapping)==5 and mapping.Exact_ML_Condition_ID.nunique()==5
    prov=pd.read_csv(TABLE/"p014_recovery_v9_provenance.csv")
    req=["Paper_ID","DOI","Material_Parent_ID","Feature_Name","Recovered_Value","Units","Evidence_Type","Evidence_Location","Method","Confidence","Recovery_Status"]
    assert prov[req].notna().all().all()
    for name in ["hierarchy","processing_states","a600_stages","target_evidence","hdi_strengthening","source_consistency_issues","provenance","legacy_mapping","correction_decision_ledger"]:
        assert (TABLE/f"p014_recovery_v9_{name}.csv").exists()
