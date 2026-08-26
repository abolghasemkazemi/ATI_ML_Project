import hashlib
import pandas as pd
from scripts.integrate_p017_recovery import BOOK, DOI, TABLE, counts, integrate

def exact(out): return out[out.P017_Record_Role.eq("RECOVERED_EXACT_COMPUTATIONAL_CONDITION")].set_index("Computational_Condition_ID")

def test_preservation_identity_domain_and_counts():
    digest=hashlib.sha256(BOOK.read_bytes()).hexdigest(); before,out=integrate(); p=exact(out)
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==digest and (len(before),len(out))==(180,192)
    pd.testing.assert_frame_equal(out.iloc[:180][before.columns].reset_index(drop=True),before,check_dtype=False)
    assert len(p)==12 and p.DOI.eq(DOI).all() and p.Data_Origin.eq("COMPUTATIONAL_MD").all()
    assert p.Independent_Computational_Condition.eq(True).all() and (~p.Independent_Experimental_ML_sample).all()
    assert counts(before)==counts(out) and p.Effective_TRIP.isna().all() and p.Effective_TWIP.isna().all()

def test_parents_composition_initial_state_and_grids():
    _,out=integrate(); p=exact(out)
    assert set(p.Material_Parent_ID)=={"P017_MAT_AL0p5","P017_MAT_AL1p5"}
    assert set(p.Original_Composition)=={"Al0.5Cr1Co1Fe1Cu1Ni1","Al1.5Cr1Co1Fe1Cu1Ni1"}
    assert p.Composition_basis.eq("Molar-ratio formula").all() and p[["Fe_at%","Cr_at%","Co_at%","Ni_at%"]].isna().all().all()
    assert p.PostQuench_Initial_Structure.str.startswith("BCC-dominant").all() and p.Initial_FCC_fraction.isna().all()
    a=p[p.Material_Parent_ID.eq("P017_MAT_AL1p5")]; assert a.Initial_BCC_fraction_raw.eq(">0.95").all() and not (a.Initial_BCC_fraction_raw==.95).any()
    for mat in set(p.Material_Parent_ID):
        q=p[p.Material_Parent_ID.eq(mat)]
        assert set(q[q["Strain_rate_s-1"].eq(1e10)].Test_T_K)=={300,700,1000,1300}
        assert set(q[q.Test_T_K.eq(300)]["Strain_rate_s-1"])=={1e8,1e9,1e10}

def test_stresses_native_targets_and_coupling():
    _,out=integrate(); p=exact(out)
    expected={"P017_SIM_A05_300K_SR1E10":(5,None),"P017_SIM_A05_300K_SR1E9":(3.7,4.2),"P017_SIM_A05_300K_SR1E8":(3.6,4.0),
      "P017_SIM_A15_300K_SR1E10":(2.1,3.6),"P017_SIM_A15_700K_SR1E10":(1.5,2.5),"P017_SIM_A15_1000K_SR1E10":(1.3,2.5),
      "P017_SIM_A15_1300K_SR1E10":(1.1,1.4),"P017_SIM_A15_300K_SR1E9":(2,2.6),"P017_SIM_A15_300K_SR1E8":(2,3)}
    for k,(sis,uts) in expected.items():
        assert p.loc[k,"SIS_PSR_GPa"]==sis and (pd.isna(p.loc[k,"UTS_PSR_GPa"]) if uts is None else p.loc[k,"UTS_PSR_GPa"]==uts)
    assert p.YS_MPa.isna().all() and p.UTS_MPa.isna().all() and p.Paper_Native_TRIP.eq(1).all()
    assert p.Paper_Native_TWIP.value_counts().to_dict()=={1:8,0:4}
    assert p.TWIP_induced_TRIP_Status.eq("Observed").sum()==3 and p.TRIP_induced_TWIP_Status.eq("Observed").sum()==8
    assert p.Experimental_Target_Eligibility.eq("NOT_ELIGIBLE_FOR_EXPERIMENTAL_TARGET_POOL").all()

def test_gsfe_landmarks_safeguards_legacy_and_provenance():
    _,out=integrate(); gs=pd.read_csv(TABLE/"p017_recovery_v11_gsfe_sfe.csv")
    assert gs[gs.Feature.eq("Stable_SFE_gamma_sf")].Value_mJ_m2.tolist()==[-14,-27]
    assert gs[gs.Feature.eq("Unstable_SFE_gamma_usf")].Value_mJ_m2.tolist()==[610,579]
    assert gs.Value_Status.eq("CURRENT_PAPER_MD_CALCULATED").all() and gs.Experimental_Equivalence.eq("NOT_EXPERIMENTAL_SFE").all() and gs.Temperature_K.eq(0).all()
    lm=pd.read_csv(TABLE/"p017_recovery_v11_coupled_mechanism_landmarks.csv"); assert len(lm)==5 and (~lm.Independent_Computational_Condition).all() and (~lm.Independent_Experimental_ML_sample).all()
    assert lm.Evidence_Location.str.contains("Fig.20").any() and lm.Evidence_Location.str.contains("Fig.24").any() and lm.Evidence_Location.str.contains("Fig.25").any()
    safe=pd.read_csv(TABLE/"p017_recovery_v11_source_safeguards.csv"); assert safe.Scientific_Rationale.str.contains("stacking faults",case=False).any()
    mapping=pd.read_csv(TABLE/"p017_recovery_v11_legacy_mapping.csv"); assert len(mapping)==8 and mapping.Mapping_Status.value_counts().to_dict()=={"EXACT_CONDITION_MATCH_LEGACY_RETAINED_EXCLUDED_FROM_DOUBLE_COUNT":4,"LEGACY_COLLAPSED_COMPUTATIONAL":4}
    prov=pd.read_csv(TABLE/"p017_recovery_v11_provenance.csv"); req={"Paper_ID","DOI","Material_Parent_ID","Computational_Condition_ID","Mechanism_Record_ID","Feature_Name","Recovered_Value","Units","Evidence_Type","Evidence_Location","Method","Confidence","Recovery_Status","Data_Origin"}
    assert req<=set(prov) and len(prov)>0 and prov[list(req-{"Material_Parent_ID","Computational_Condition_ID","Mechanism_Record_ID"})].notna().all().all()
    assert exact(out).P017_Recovery_Provenance_JSON.str.len().gt(2).all()
