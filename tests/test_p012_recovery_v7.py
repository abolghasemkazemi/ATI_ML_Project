import hashlib
import pandas as pd
from scripts.integrate_p012_recovery import BOOK, TABLE, counts, integrate


def exact(out):
    return out[out.P012_Record_Role.eq('RECOVERED_EXACT_CONDITION')].set_index('ML_Condition_ID')


def stages(out):
    return out[out.P012_Record_Role.eq('RECOVERED_STAGE_CHILD')].set_index('Observation_ID')


def test_v7_preserves_v6_and_verified_workbook():
    digest=hashlib.sha256(BOOK.read_bytes()).hexdigest(); before,out=integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==digest
    assert len(before)==137 and len(out)==163
    pd.testing.assert_frame_equal(out.iloc[:137][before.columns].reset_index(drop=True),before,check_dtype=False)


def test_six_conditions_and_strict_targets():
    before,out=integrate(); p=exact(out)
    assert len(p)==6 and p.Independent_ML_sample.eq(True).all()
    assert p.loc[['P012_MC_BASE_RT','P012_MC_MO_RT','P012_MC_C_RT'],'Effective_TRIP'].isna().all()
    assert p.loc[['P012_MC_BASE_RT','P012_MC_MO_RT','P012_MC_C_RT'],'Effective_TWIP'].eq(1).all()
    assert p.loc['P012_MC_BASE_77K','Effective_TRIP']==1 and pd.isna(p.loc['P012_MC_BASE_77K','Effective_TWIP'])
    assert p.loc['P012_MC_MO_77K','Effective_TRIP']==1 and pd.isna(p.loc['P012_MC_MO_77K','Effective_TWIP'])
    assert tuple(p.loc['P012_MC_C_77K',['Effective_TRIP','Effective_TWIP']])==(1,1)
    # Legacy hybrid extraction rows were never strict experimental samples; exact source-resolved rows add six.
    assert counts(out)[0]==counts(before)[0]+6


def test_stage_chronology_and_no_negative_promotion():
    _,out=integrate(); s=stages(out); p=exact(out)
    assert len(s)==20 and s.Independent_ML_sample.eq(False).all() and s.ML_Condition_ID.isna().all()
    assert s.loc[[i for i in s.index if '_RT_eps020' in i],'Effective_TRIP'].eq(0).all()
    assert p.loc[[i for i in p.index if i.endswith('_RT')],'Effective_TRIP'].isna().all()
    assert tuple(s.loc['P012_OBS_C_77_eps010',['Effective_TRIP','Effective_TWIP']])==(0,1)
    assert tuple(s.loc['P012_OBS_C_77_eps020',['Effective_TRIP','Effective_TWIP']])==(1,1)
    assert tuple(s.loc['P012_OBS_MO_77_eps010',['Effective_TRIP','Effective_TWIP']])==(0,0)
    assert tuple(s.loc['P012_OBS_MO_77_eps020',['Effective_TRIP','Effective_TWIP']])==(1,0)
    assert s.loc['P012_OBS_MO_77_eps050','HCP_fraction_at_condition']==.668
    assert s.loc['P012_OBS_C_77_eps050','HCP_fraction_at_condition']==.30


def test_composition_microstructure_physics_and_mechanics():
    _,out=integrate(); p=exact(out)
    c=p.loc['P012_MC_C_RT']; assert c['C_at%']==.6 and 'C0.5' in c.Nominal_Composition_at_pct
    assert p.Initial_Twin_Type.eq('ANNEALING_TWIN').all() and p.Initial_FCC_fraction.isna().all() and p.Initial_HCP_fraction.eq(0).all()
    assert set(p.XRD_Replicate_n)=={5} and p.Replicate_n.isna().all() and p.Replicate_ID.isna().all()
    assert p.loc[['P012_MC_BASE_77K','P012_MC_MO_77K'],['YS_MPa','UTS_MPa','Elongation_pct']].isna().all().all()
    physics=pd.read_csv(TABLE/'p012_recovery_v7_physics.csv')
    assert len(physics)==6 and set(physics.Value_Status)=={'CURRENT_PAPER_CALCULATED'} and physics.groupby('Material_Parent_ID').Temperature_K.nunique().eq(2).all()
    assert physics.SFE_Method.str.contains('Thermodynamic').all() and physics.DeltaG_Method.str.contains('Thermodynamic').all()


def test_provenance_mapping_and_supporting_tables():
    _,out=integrate(); prov=pd.read_csv(TABLE/'p012_recovery_v7_provenance.csv')
    required=['Paper_ID','DOI','Material_Parent_ID','ML_Condition_ID','Observation_ID','Feature_Name','Recovered_Value','Units','Evidence_Type','Evidence_Location','Confidence','Recovery_Status']
    # condition/stage provenance requires identities; standalone physics uses material+method/temperature table identity.
    assert prov[['Paper_ID','DOI','Material_Parent_ID','Feature_Name','Recovered_Value','Units','Evidence_Type','Evidence_Location','Confidence','Recovery_Status']].notna().all().all()
    assert set(stages(out).Initial_Twin_Type)=={'ANNEALING_TWIN'}
    for name in ['p012_recovery_v7_hierarchy.csv','p012_recovery_v7_stage_observations.csv','p012_recovery_v7_legacy_mapping.csv','p012_recovery_v7_decision_correction_ledger.csv']:
        assert (TABLE/name).exists()
