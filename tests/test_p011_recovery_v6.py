import hashlib
import pandas as pd
from scripts.integrate_p011_recovery import BOOK, CORR, EXTRA, MAPPING, PROV, SFE, STATES, counts, integrate


def test_v6_preserves_v5_and_verified_input():
    digest=hashlib.sha256(BOOK.read_bytes()).hexdigest(); before,out=integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==digest
    assert len(before)==127 and len(out)==137
    pd.testing.assert_frame_equal(out.iloc[:127][before.columns].reset_index(drop=True),before,check_dtype=False)


def test_exact_conditions_targets_and_a8_exclusion():
    before,out=integrate(); p=out[out.P011_Record_Role.eq('RECOVERED_EXACT_CONDITION')].set_index('ML_Condition_ID')
    assert len(p)==4 and p.Independent_ML_sample.eq(True).all()
    assert tuple(p.loc['P011_MC_A10_298K',['Effective_TRIP','Effective_TWIP']])==(1,1)
    assert tuple(p.loc['P011_MC_A10_77K',['Effective_TRIP','Effective_TWIP']])==(1,0)
    assert p.loc[['P011_MC_A9_298K','P011_MC_A11_298K'],['Effective_TRIP','Effective_TWIP']].isna().all().all()
    assert p.loc['P011_MC_A10_77K','P011_Negative_TWIP_Evidence']=='EXPLICIT_NEGATIVE_DIRECT_TEM'
    assert 'P011_MC_A8_298K' not in p.index and counts(out)[0]==counts(before)[0]-5+4


def test_stages_replicates_and_microstructure_semantics():
    _,out=integrate(); s=out[out.P011_Record_Role.eq('RECOVERED_STAGE_CHILD')].set_index('Observation_ID')
    p=out[out.P011_Record_Role.eq('RECOVERED_EXACT_CONDITION')]
    assert len(s)==6 and s.Independent_ML_sample.eq(False).all() and s.ML_Condition_ID.isna().all()
    assert set(s.Leakage_Group_Strict)=={'P011_SERIES01'} and set(s.Leakage_Group_Material)=={'P011_MAT_FE50MN30CO10CR10'}
    assert s.loc[['P011_OBS_A10_298_eps15','P011_OBS_A10_77_eps15'],'HCP_fraction_at_condition'].isna().all()
    assert s.loc['P011_OBS_A10_298_eps0','HCP_fraction_at_condition']==.047
    assert s.loc['P011_OBS_A10_298_fracture','HCP_fraction_at_condition']==.421
    assert p.Replicate_n.eq(3).all() and p.Replicate_ID.isna().all() and len(p)==4
    assert p.Initial_Twin_Type.eq('ANNEALING_TWIN').all()


def test_composition_sfe_mechanics_and_provenance_separation():
    _,out=integrate(); p=out[out.P011_Record_Role.eq('RECOVERED_EXACT_CONDITION')].set_index('ML_Condition_ID')
    assert p.Feedstock_Composition_Scope.eq('FEEDSTOCK').all()
    assert p.loc['P011_MC_A10_298K','Local_EDS_Composition_Scope']=='LOCAL_OR_SCANNED_REGION_EDS'
    assert p.loc['P011_MC_A10_298K','Feedstock_Composition_at_pct'] != p.loc['P011_MC_A10_298K','Local_EDS_Composition_at_pct']
    assert p.loc['P011_MC_A9_298K',['UTS_MPa','Uniform_elongation_pct']].isna().all()
    sfe=pd.read_csv(SFE); assert set(sfe.Value_Status)=={'CURRENT_PAPER_CALCULATED','SECONDARY_LITERATURE_RANGE'}
    assert set(sfe.Source_or_Reference_Status)=={'CURRENT_PAPER_CALCULATION_BASED_ON_PREVIOUS_METHOD','SECONDARY_REFERENCE'}
    prov=pd.read_csv(PROV); required=['Paper_ID','DOI','ML_Condition_ID','Observation_ID','Feature_Name','Recovered_Value','Units','Evidence_Type','Evidence_Location','Confidence','Recovery_Status']
    assert prov[required].notna().all().all()
    extra=pd.read_csv(EXTRA); assert set(extra[extra.Feature.str.contains('lattice')].Status)=={'DIRECT_TEM_SAED'}
    assert all(x.exists() for x in [CORR,MAPPING,STATES,EXTRA])
