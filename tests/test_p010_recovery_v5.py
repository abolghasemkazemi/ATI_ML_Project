import hashlib
import pandas as pd
from scripts.integrate_p010_recovery import BOOK, CORR, integrate, counts


def test_v5_preserves_v4_and_verified_input():
    digest=hashlib.sha256(BOOK.read_bytes()).hexdigest(); before,after=integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==digest
    assert len(before)==118 and len(after)==127
    pd.testing.assert_frame_equal(after.iloc[:118][before.columns].reset_index(drop=True),before,check_dtype=False)


def test_p010_hierarchy_targets_and_legacy_correction():
    before,out=integrate(); p=out[out.P010_Record_Role.eq("RECOVERED_EXACT_CONDITION")].set_index("ML_Condition_ID")
    s=out[out.P010_Record_Role.eq("RECOVERED_STAGE_CHILD")]
    assert len(p)==3 and len(s)==6 and s.Independent_ML_sample.eq(False).all()
    assert tuple(p.loc["P010_MC_AlloyI",["Effective_TRIP","Effective_TWIP"]])==(1,1)
    assert tuple(p.loc["P010_MC_AlloyII",["Effective_TRIP","Effective_TWIP"]])==(0,1)
    assert tuple(p.loc["P010_MC_AlloyIII",["Effective_TRIP","Effective_TWIP"]])==(1,1)
    legacy=out[out.Condition_ID.eq("P010_C03")].iloc[0]; assert (legacy.TRIP,legacy.TWIP)==(0,0)
    assert counts(out)[0]==counts(before)[0]+3 and CORR.exists()


def test_stage_fractions_missingness_temperature_and_leakage():
    _,out=integrate(); s=out[out.P010_Record_Role.eq("RECOVERED_STAGE_CHILD")].set_index("Observation_ID")
    assert tuple(s.loc["P010_OBS_AlloyIII_eps80",["HCP_fraction_at_condition","Twin_fraction_or_Sigma3"]])==(.014,.234)
    assert tuple(s.loc["P010_OBS_AlloyI_eps60",["HCP_fraction_at_condition","Twin_fraction_or_Sigma3"]])==(.36,.045)
    p=out[out.P010_Record_Role.eq("RECOVERED_EXACT_CONDITION")]
    assert p[["Initial_FCC_fraction","Initial_HCP_fraction","SFE_mJ_m2","YS_MPa","UTS_MPa","Elongation_pct","Grain_size_um","Test_T_K"]].isna().all().all()
    assert set(p.Magnetic_transition_T_K)=={80,160,190} and set(p.Recovered_Test_T_Status)=={"ROOM_TEMPERATURE_REPORTED"}
    for _,r in s.iterrows():
        parent=p[p.ML_Condition_ID.eq(r.Parent_ML_Condition_ID)].iloc[0]
        assert (r.Leakage_Group_Strict,r.Leakage_Group_Material)==(parent.Leakage_Group_Strict,parent.Leakage_Group_Material)


def test_provenance_required_fields_complete_and_no_unjustified_zero():
    _,out=integrate(); prov=pd.read_csv("reports/tables/p010_recovery_v5_provenance.csv")
    required=["Paper_ID","DOI","ML_Condition_ID","Observation_ID","Feature_Name","Recovered_Value","Units","Evidence_Type","Evidence_Location","Confidence","Recovery_Status"]
    assert prov[required].notna().all().all()
    s=out[out.P010_Record_Role.eq("RECOVERED_STAGE_CHILD")]
    zero=s[(s.Effective_TRIP.eq(0)) | (s.HCP_fraction_at_condition.eq(0))]
    assert set(zero.Observation_ID)=={"P010_OBS_AlloyII_eps70"}
