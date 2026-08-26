import hashlib
import pandas as pd
from scripts.integrate_p013_recovery import BOOK, TABLE, counts, integrate


def parts(out):
    return (out[out.P013_Record_Role.eq('RECOVERED_EXACT_CONDITION')].set_index('ML_Condition_ID'),
            out[out.P013_Record_Role.eq('RECOVERED_LANDMARK_CHILD')].set_index('Observation_ID'))


def test_v8_preserves_v7_and_workbook():
    digest=hashlib.sha256(BOOK.read_bytes()).hexdigest(); before,out=integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest()==digest
    assert (len(before),len(out))==(163,169)
    pd.testing.assert_frame_equal(out.iloc[:163][before.columns].reset_index(drop=True),before,check_dtype=False)


def test_one_condition_five_nonindependent_landmarks_and_counts():
    before,out=integrate(); p,s=parts(out)
    assert list(p.index)==['P013_MC_ASCAST_RT'] and tuple(p.iloc[0][['Effective_TRIP','Effective_TWIP','Slip']])==(1,1,1)
    assert len(s)==5 and s.Independent_ML_sample.eq(False).all() and s.ML_Condition_ID.isna().all()
    assert counts(out)[0]==counts(before)[0]+1
    assert not out.Observation_ID.isin([f'P013_STAGE_{x}' for x in ['I','II','III','IV']]).any()


def test_microstructure_mechanics_and_no_fabrication():
    _,out=integrate(); p,s=parts(out); r=p.iloc[0]
    assert r.Initial_HCP_fraction==.33 and r.Initial_HCP_Origin=='THERMAL_PRE_EXISTING_MARTENSITE'
    assert pd.isna(r.Initial_FCC_fraction) and r.Initial_MnO_fraction==.01
    assert r.EBSD_Phase_Fraction_Use_Status=='DO_NOT_USE_EBSD_HCP_FRACTION_AS_BULK_VALUE'
    assert (r.Grain_size_um,r.Grain_size_SD_um)==(40.2,10.7) and 'γ-FCC' in r.Grain_Size_Scope
    assert (r.YS_MPa,r.Nearest_SXRD_TRIP_Onset_Stress_MPa)==(319,250)
    assert (r.UTS_MPa,r.Final_InSitu_True_Stress_Approx_MPa)==(726,950)
    assert pd.isna(r.SFE_mJ_m2) and pd.isna(r.DeltaG_FCC_HCP_J_mol)
    assert s.loc['P013_OBS_FRACTURE','HCP_fraction_at_condition']==.77
    assert pd.isna(s.loc['P013_OBS_TRIP_ONSET','HCP_fraction_at_condition'])


def test_stage_chronology_phase_scope_and_physics_separation():
    _,out=integrate(); p,s=parts(out)
    assert tuple(s.loc['P013_OBS_TRIP_ONSET',['Effective_TRIP','Effective_TWIP','Slip']])==(1,0,1)
    assert tuple(s.loc['P013_OBS_TENSILE_TWIP_ONSET',['Approx_Stress_MPa','Effective_TWIP']])==(530,1)
    assert s.loc['P013_OBS_COMPRESSION_TWIP_ONSET','Approx_Stress_MPa']==655
    assert 'ε-HCP tensile/compression twinning' in p.iloc[0].Mechanism_Phase_Scope
    physics=pd.read_csv(TABLE/'p013_recovery_v8_phase_physics.csv')
    assert {'Phase_Young_Modulus','Reflection_Young_Modulus'}.issubset(set(physics.Feature))
    sigma=physics[(physics.Feature=='Lattice_friction_stress_sigma0') & (physics.Value.astype(str)=='179')]
    assert len(sigma)==1 and sigma.iloc[0].Value_Status=='SECONDARY_REFERENCE_INPUT'
    calc=physics[physics.Feature.eq('Predicted_yield_strength')]
    assert len(calc)==1 and float(calc.iloc[0].Value)==321 and float(calc.iloc[0].Uncertainty)==31
    dis=physics[physics.Feature.isin(['Dislocation_density_initial','Dislocation_density_final'])]
    assert set(dis.Scope)=={'γ-FCC'} and set(dis.Value.astype(float))=={1.4e14,8.2e14}


def test_legacy_supporting_tables_and_complete_provenance():
    _,out=integrate(); mapping=pd.read_csv(TABLE/'p013_recovery_v8_legacy_mapping.csv')
    assert len(mapping)==5 and mapping.Exact_ML_Condition_ID.eq('P013_MC_ASCAST_RT').all()
    prov=pd.read_csv(TABLE/'p013_recovery_v8_provenance.csv')
    required=['Paper_ID','DOI','Material_Parent_ID','ML_Condition_ID','Feature_Name','Recovered_Value','Units','Evidence_Type','Evidence_Location','Method','Confidence','Recovery_Status']
    assert prov[required].notna().all().all()
    for name in ['hierarchy','stage_intervals','landmark_observations','phase_physics','target_evidence','provenance','legacy_mapping','correction_decision_ledger']:
        assert (TABLE/f'p013_recovery_v8_{name}.csv').exists()
