import hashlib
import pandas as pd
from scripts.integrate_p015_recovery import BOOK, TABLE, counts, integrate

def parts(out):
    return out[out.P015_Record_Role.eq("RECOVERED_EXACT_CONDITION")].set_index("ML_Condition_ID")

def test_preservation_identity_hierarchy_and_no_pseudoreplicates():
    digest=hashlib.sha256(BOOK.read_bytes()).hexdigest(); before,out=integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==digest and (len(before),len(out))==(178,180)
    pd.testing.assert_frame_equal(out.iloc[:178][before.columns].reset_index(drop=True),before,check_dtype=False)
    p=parts(out); assert set(p.index)=={"P015_MC_298K","P015_MC_77K"}
    assert p.Independent_ML_sample.eq(True).all() and p.Replicate_n.eq(3).all() and p.Replicate_ID.isna().all() and p.Physical_Batch_ID.isna().all()
    assert counts(out)[0]==counts(before)[0]+2

def test_chemistry_processing_initial_state_rate_and_conflict():
    _,out=integrate(); p=parts(out)
    assert p.Measured_Composition_at_pct.isna().all() and p.Nominal_Composition_at_pct.eq("Fe50Mn20Cr20Ni10").all()
    assert list(p[["Fe_at%","Mn_at%","Cr_at%","Ni_at%"]].iloc[0])==[50,20,20,10]
    assert p.Mn_Charge_Adjustment.str.contains("NOT part").all() and p.Initial_HCP_fraction.eq(0).all() and p.Initial_FCC_fraction.isna().all()
    assert p.Grain_size_um.eq(100).all() and p.Grain_Size_Status.eq("APPROX_DIRECT_TEXT").all()
    assert p["Strain_rate_s-1"].eq(.001).all() and not ((out.Paper_ID.eq("P015"))&(out["Strain_rate_s-1"]==1000)).any()
    issues=pd.read_csv(TABLE/"p015_recovery_v10_source_consistency.csv")
    assert issues.Source_B.str.contains("1000",regex=False).any()

def test_targets_negative_phase_evidence_and_mechanics():
    _,out=integrate(); p=parts(out); a=p.loc["P015_MC_298K"]; c=p.loc["P015_MC_77K"]
    assert tuple(a[["Effective_TRIP","Effective_TWIP","Slip"]])==(0,1,1) and tuple(c[["Effective_TRIP","Effective_TWIP","Slip"]])==(1,1,1)
    assert a.Negative_Evidence_Quality=="EXPLICIT_INITIAL_TO_FINAL_PHASE_NEGATIVE" and a.Postfracture_HCP_fraction==0
    assert pd.isna(c.Postfracture_HCP_fraction) and c.Postfracture_HCP_fraction_Status=="HCP_DIRECTLY_PRESENT_BUT_NOT_NUMERICALLY_QUANTIFIED"
    assert tuple(a[["Engineering_YS_MPa","Engineering_UTS_MPa","Engineering_Elongation_pct"]])==(300,550,60)
    assert tuple(c[["Engineering_YS_MPa","Engineering_UTS_MPa","Engineering_Elongation_pct"]])==(608,850,35)
    assert tuple(a[["True_Yield_Stress_MPa","True_UTS_MPa","HC"]])==(300.25,888.61,1.96)
    assert tuple(c[["True_Yield_Stress_MPa","True_UTS_MPa","HC"]])==(690.33,1368.75,.983)
    assert tuple(a[["YS_MPa","UTS_MPa"]])==(300,550) and tuple(c[["YS_MPa","UTS_MPa"]])==(608,850)

def test_sfe_physics_deltag_onsets_and_no_duplicate_evidence():
    _,out=integrate(); p=parts(out); physics=pd.read_csv(TABLE/"p015_recovery_v10_sfe_critical_stress_physics.csv")
    assert p.loc["P015_MC_298K","SFE_mJ_m2"]==36.62 and p.loc["P015_MC_77K","SFE_mJ_m2"]==10.97
    assert p.SFE_Value_Status.eq("CURRENT_PAPER_MD_CALCULATED").all() and p.SFE_Data_Origin.eq("COMPUTATIONAL_MD").all() and p.DeltaG_FCC_HCP_J_mol.isna().all()
    def value(feature,temp): return float(physics[(physics.Feature==feature)&(physics.Temperature_K.astype(str)==str(temp))].iloc[0].Value)
    assert value("Twin_critical_normal_growth_stress",77)==440 and value("Twin_critical_normal_growth_stress",298)==658
    assert value("Epsilon_martensite_critical_normal_growth_stress",77)==742 and value("Epsilon_martensite_critical_normal_growth_stress",298)==745
    assert p.loc["P015_MC_298K","Critical_Stress_Model_Validity"]=="LIMITED_VALIDITY_AT_298K"
    onset=physics[physics.Feature.eq("TRIP_onset_strain")].iloc[0]; assert float(onset.Value)==12 and onset.Method=="MODEL_CURVE_INFERENCE"
    assert len(physics[physics.Feature.eq("SFE")])==2 and physics[physics.Feature.eq("Gamma_SF")].iloc[0].Value_Status=="MODEL_INPUT_FROM_CURRENT_MD_SFE"
    assert physics[physics.Feature.eq("Gamma_fcc_hcp_interface")].iloc[0].Value_Status=="SECONDARY_REFERENCE_INPUT"

def test_md_domain_legacy_mapping_and_provenance():
    _,out=integrate(); md=pd.read_csv(TABLE/"p015_recovery_v10_md_stages.csv")
    assert len(md)==8 and md.Data_Origin.eq("COMPUTATIONAL_MD").all() and md.Observation_Role.eq("CORRELATED_SIM_STAGE").all() and (~md.Independent_ML_sample).all()
    assert not out.Observation_ID.fillna("").str.startswith("P015_MD_").any()
    assert tuple(parts(out).loc["P015_MC_77K",["Effective_TRIP","Effective_TWIP"]])==(1,1)
    mapping=pd.read_csv(TABLE/"p015_recovery_v10_legacy_mapping.csv"); assert len(mapping)==2 and mapping.Exact_ML_Condition_ID.nunique()==2
    prov=pd.read_csv(TABLE/"p015_recovery_v10_provenance.csv")
    required={"Paper_ID","DOI","Material_Parent_ID","ML_Condition_ID","Feature_Name","Recovered_Value","Units","Evidence_Type","Evidence_Location","Method","Confidence","Recovery_Status"}
    assert required.issubset(prov.columns) and not prov[list(required)].isna().any().any()
