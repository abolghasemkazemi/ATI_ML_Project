"""Integrate the verified P012 workbook as recovery_v7 (dataset construction only)."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/processed/master_19papers_recovery_v6.csv'
BOOK=ROOT/'data/interim/manual_recovery/P012_scientific_evidence_recovery_VERIFIED.xlsx'
OUT=ROOT/'data/processed/master_19papers_recovery_v7.csv'
TABLE=ROOT/'reports/tables'
AUDIT=ROOT/'reports/P012_RECOVERY_V7_AUDIT.md'
DOI='10.1016/j.jallcom.2022.165108'
LEGACY={'P012_C01':'P012_MC_BASE_RT','P012_C02':'P012_MC_BASE_77K','P012_C03':'P012_MC_C_RT',
        'P012_C04':'P012_MC_C_77K','P012_C05':'P012_MC_MO_RT','P012_C06':'P012_MC_MO_77K'}
NEW=['Original_TRIP','Original_TWIP','P012_Record_Role','Nominal_Composition_at_pct','Measured_Composition_at_pct',
 'Measured_Composition_Method','Measured_Composition_Status','Grain_Size_Including_TB_as_HAB_um','Initial_Sigma3_TB_fraction',
 'Initial_Twin_Type','FCC_lattice_a_XRD_A','XRD_Replicate_n','XRD_Replicate_Scope','Gauge_Cross_Section_mm',
 'Loading_Direction','GND_density_m-2','Martensite_lath_thickness','Martensite_interspace_nm',
 'Deformation_Twin_thickness_nm','Observed_Microstructure','P012_Target_Status','P012_Recovery_Provenance_JSON']

def eligible(d):
    x=d[d.Data_Origin.eq('EXPERIMENTAL') & d.Observation_Role.eq('INDEPENDENT_CONDITION')]
    if 'P012_Record_Role' in d and d.P012_Record_Role.eq('RECOVERED_EXACT_CONDITION').any():
        x=x[~(x.Paper_ID.eq('P012') & x.Condition_ID.isin(LEGACY))]
    if 'P012_Record_Role' in x: x=x[~x.P012_Record_Role.eq('LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT')]
    for col,val in [('P011_Record_Role','RECOVERED_EXACT_CONDITION'),('P008_Record_Role','LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT')]:
        if col in x and col=='P011_Record_Role' and x[col].eq(val).any(): x=x[~(x.Paper_ID.eq('P011')&x.Condition_ID.str.match(r'P011_C0[1-5]',na=False))]
        elif col in x: x=x[~x[col].eq(val)]
    return x

def counts(d):
    x=eligible(d); return len(x),x.Effective_TRIP.notna().sum(),x.Effective_TWIP.notna().sum(),x[['Effective_TRIP','Effective_TWIP']].notna().all(axis=1).sum()

def integrate():
    src=pd.read_csv(SOURCE,low_memory=False); sh=pd.read_excel(BOOK,sheet_name=None)
    for d in sh.values():
        if 'Paper_ID' in d: assert set(d.Paper_ID)=={'P012'}
        if 'DOI' in d: assert set(d.DOI)=={DOI}
    cond=sh['P012_ML_Conditions']; stages=sh['P012_Stage_Observations']; chem=sh['P012_Study_Chemistry']; micro=sh['P012_Initial_Microstructure']
    assert len(cond)==6 and len(stages)==20
    out=src.copy()
    for f in NEW:
        if f not in out: out[f]=pd.NA
    prov=[]; rows=[]; ci=chem.set_index('Material_Parent_ID'); mi=micro.set_index('Material_Parent_ID'); te=sh['P012_Target_Evidence'].set_index('ML_Condition_ID')
    legacy=src[src.Paper_ID.eq('P012')].set_index('Condition_ID')
    reverse={v:k for k,v in LEGACY.items()}
    def pv(cid,oid,f,v,u,loc,kind='VERIFIED_WORKBOOK',material=None):
        if pd.notna(v): prov.append({'Paper_ID':'P012','DOI':DOI,'Material_Parent_ID':material if material is not None else rows[-1].get('Material_Parent_ID'),'ML_Condition_ID':cid,'Observation_ID':oid,'Feature_Name':f,'Recovered_Value':v,'Units':u,'Evidence_Type':kind,'Evidence_Location':loc,'Confidence':'High','Recovery_Status':'VERIFIED'})
    for c in cond.to_dict('records'):
        cid=c['ML_Condition_ID']; ch=ci.loc[c['Material_Parent_ID']]; m=mi.loc[c['Material_Parent_ID']]; lid=reverse[cid]; old=legacy.loc[lid]
        oid=cid.replace('_MC_','_OBS_')+'_condition'; r={k:pd.NA for k in out.columns}
        r.update({'Paper_ID':'P012','DOI':DOI,'Paper_Title':ch.Paper_Title,'Condition_ID':cid,'Alloy_ID':c['Alloy_Label'],
         'Original_Composition':ch.Measured_Composition_at_pct,'Composition_basis':'at.% measured (nominal retained separately)',
         'Fe_at%':ch.Fe_at_pct,'Mn_at%':ch.Mn_at_pct,'Co_at%':ch.Co_at_pct,'Cr_at%':ch.Cr_at_pct,'Mo_at%':ch.Mo_at_pct,'C_at%':ch.C_at_pct,
         'Nominal_Composition_at_pct':ch.Nominal_Composition_at_pct,'Measured_Composition_at_pct':ch.Measured_Composition_at_pct,
         'Measured_Composition_Method':ch.Composition_Method,'Measured_Composition_Status':ch.Composition_Status,
         'Processing_route':'arc melted under high-purity Ar; remelted 5 times; hot rolled 1170 K/60%; homogenized 1473 K/1 h in Ar; water quenched; subsequent hot/cold rolling; final cold reduction 90%; solution annealed 1420 K/2 h; water quenched',
         'Cast_method':'arc melting under high-purity Ar; remelted five times','Homogenization_T_K':1473,'Homogenization_time_h':1,
         'Hot_rolling_T_K':1170,'Hot_rolling_reduction_pct':60,'Cold_rolling_reduction_pct':90,'Annealing_T_K':1420,'Annealing_time_min':120,'Cooling_route':'water quench',
         'Test_T_K':c['Test_T_K'],'Strain_rate_s-1':.001,'Gauge_length_mm':9,'Gauge_width_mm':3.4,'Specimen_thickness_mm':2,
         'Gauge_Cross_Section_mm':'3.4 x 2','Loading_Direction':'parallel to rolling direction','Grain_size_um':m.Grain_Size_Excluding_TB_um,
         'Grain_Size_Including_TB_as_HAB_um':m.Grain_Size_Including_TB_as_HAB_um,'Initial_FCC_fraction':pd.NA,'Initial_HCP_fraction':0,
         'Initial_Phase_State_Qualitative':'single-phase FCC','Initial_Phase_Status':m.Initial_Phase_Status,'Initial_twin_boundary_status':'ANNEALING_TWIN',
         'Initial_Sigma3_TB_fraction':m.Initial_Sigma3_TB_fraction,'Initial_Twin_Type':'ANNEALING_TWIN','FCC_lattice_a_XRD_A':m.FCC_lattice_parameter_A,
         'XRD_Replicate_n':5,'XRD_Replicate_Scope':'LATTICE_PARAMETER_ONLY; NOT_TENSILE_REPLICATES','SFE_mJ_m2':c['SFE_mJ_m2'],
         'SFE_method':'Thermodynamic Olson-Cohen-type calculation; CURRENT_PAPER_CALCULATED','DeltaG_FCC_HCP_J_mol':c['DeltaG_fcc_hcp_J_mol'],
         'DeltaG_method':'Thermodynamic software; CURRENT_PAPER_CALCULATED','YS_MPa':c['YS_MPa'],'UTS_MPa':c['UTS_MPa'],'Elongation_pct':c['Total_Elongation_pct'],
         'TRIP':pd.NA,'TWIP':pd.NA,'Original_TRIP':old.TRIP,'Original_TWIP':old.TWIP,'Recovered_TRIP':c['TRIP'],'Recovered_TWIP':c['TWIP'],
         'Effective_TRIP':c['TRIP'],'Effective_TWIP':c['TWIP'],'Slip':c['Slip'],'Dominant_mechanism':c['Dominant_Mechanism'],
         'Evidence_TRIP':te.loc[cid,'TRIP_Evidence'],'Evidence_TWIP':te.loc[cid,'TWIP_Evidence'],'Source_location':c['Evidence_Location'],'Label_confidence':'High',
         'Study_Series_ID':'P012_SERIES01','Material_Parent_ID':c['Material_Parent_ID'],'Physical_Batch_ID':pd.NA,'Replicate_ID':pd.NA,
         'Replicate_n':pd.NA,'Leakage_Group_Strict':'P012_SERIES01','Leakage_Group_Material':c['Material_Parent_ID'],'Parent_Experiment_ID':cid,
         'ML_Condition_ID':cid,'Parent_ML_Condition_ID':cid,'Observation_ID':oid,'Data_Origin':'EXPERIMENTAL','Observation_Role':'INDEPENDENT_CONDITION',
         'Independent_ML_sample':True,'Grouping_Confidence':'HIGH','Grouping_Review_Required':0,'P012_Record_Role':'RECOVERED_EXACT_CONDITION',
         'P012_Target_Status':c['Target_Status'],'Source_File':BOOK.name,'Source_Sheet':'P012_ML_Conditions'})
        rows.append(r)
        units={'Fe_at%':'at.%','Mn_at%':'at.%','Co_at%':'at.%','Cr_at%':'at.%','Mo_at%':'at.%','C_at%':'at.%','SFE_mJ_m2':'mJ/m2','DeltaG_FCC_HCP_J_mol':'J/mol','YS_MPa':'MPa','UTS_MPa':'MPa','Elongation_pct':'%','Initial_HCP_fraction':'fraction','Initial_Sigma3_TB_fraction':'fraction','Grain_size_um':'um','Grain_Size_Including_TB_as_HAB_um':'um','FCC_lattice_a_XRD_A':'A','Effective_TRIP':'binary','Effective_TWIP':'binary','Slip':'binary'}
        for f,u in units.items(): pv(cid,oid,f,r[f],u,c['Evidence_Location'])
        r['P012_Recovery_Provenance_JSON']=json.dumps([p for p in prov if p['Observation_ID']==oid],default=str)
    parent={r['ML_Condition_ID']:r for r in rows}
    for s in stages.to_dict('records'):
        p=parent[s['Parent_ML_Condition_ID']]; r={k:pd.NA for k in out.columns}
        for k in ['Paper_ID','DOI','Paper_Title','Alloy_ID','Study_Series_ID','Material_Parent_ID','Leakage_Group_Strict','Leakage_Group_Material']: r[k]=p[k]
        r.update({'Condition_ID':s['Observation_ID'],'Observation_ID':s['Observation_ID'],'Parent_ML_Condition_ID':s['Parent_ML_Condition_ID'],'Parent_Experiment_ID':s['Parent_ML_Condition_ID'],
         'ML_Condition_ID':pd.NA,'Observation_Role':'REPEATED_STAGE','Independent_ML_sample':False,'Data_Origin':'EXPERIMENTAL','Test_T_K':s['Test_T_K'],'True_strain':s['True_Strain'],
         'Deformation_stage':f"true strain {s['True_Strain']}",'Recovered_TRIP':s['TRIP_at_stage'],'Recovered_TWIP':s['TWIP_at_stage'],'Effective_TRIP':s['TRIP_at_stage'],
         'Effective_TWIP':s['TWIP_at_stage'],'Slip':s['Slip_at_stage'],'HCP_fraction_at_condition':s['HCP_fraction'],'Twin_fraction_or_Sigma3':s['Twin_fraction'],
         'GND_density_m-2':s['GND_density_m-2'],'Martensite_lath_thickness':s['Martensite_lath_thickness'],'Martensite_interspace_nm':s['Martensite_interspace_nm'],
         'Deformation_Twin_thickness_nm':s['Deformation_twin_thickness_nm'],'Observed_Microstructure':s['Observed_Microstructure'],'Source_location':s['Evidence_Location'],
         'Label_confidence':s['Confidence'],'Deformation_Stage_ID':s['Observation_ID'],'Grouping_Confidence':'HIGH','Initial_Twin_Type':'ANNEALING_TWIN',
         'P012_Record_Role':'RECOVERED_STAGE_CHILD','Source_File':BOOK.name,'Source_Sheet':'P012_Stage_Observations'})
        rows.append(r)
        for f,u in [('Effective_TRIP','binary'),('Effective_TWIP','binary'),('Slip','binary'),('HCP_fraction_at_condition','fraction'),('Twin_fraction_or_Sigma3','fraction'),('GND_density_m-2','m^-2'),('Martensite_lath_thickness','reported mixed scale'),('Martensite_interspace_nm','nm'),('Deformation_Twin_thickness_nm','nm'),('Observed_Microstructure','text')]: pv(s['Parent_ML_Condition_ID'],s['Observation_ID'],f,r[f],u,s['Evidence_Location'],'DIRECT_STAGE_OBSERVATION',p['Material_Parent_ID'])
    out=pd.concat([out,pd.DataFrame(rows,columns=out.columns)],ignore_index=True)
    validate(src,out); out.to_csv(OUT,index=False)
    # Complete physics provenance records (kept method/temperature-specific in its supporting table).
    physics=sh['P012_Physics_SFE_DeltaG']; physics.to_csv(TABLE/'p012_recovery_v7_physics.csv',index=False)
    for q in physics.to_dict('records'):
        for f,u in [('SFE_mJ_m2','mJ/m2'),('DeltaG_fcc_to_hcp_J_mol','J/mol'),('Interfacial_Energy_mJ_m2','mJ/m2'),('Molar_Surface_Density_mol_m2','mol/m2')]:
            prov.append({'Paper_ID':'P012','DOI':DOI,'Material_Parent_ID':q['Material_Parent_ID'],'ML_Condition_ID':pd.NA,'Observation_ID':pd.NA,'Feature_Name':f,'Recovered_Value':q[f],'Units':u,'Evidence_Type':q['Value_Status'],'Evidence_Location':q['Evidence_Location'],'Confidence':q['Confidence'],'Recovery_Status':'VERIFIED'})
    pd.DataFrame(prov).to_csv(TABLE/'p012_recovery_v7_provenance.csv',index=False)
    hierarchy=cond[['Study_Series_ID','Material_Parent_ID','ML_Condition_ID','Independent_ML_sample','Leakage_Group_Strict','Leakage_Group_Material','Physical_Batch_ID','Replicate_ID']]
    hierarchy.to_csv(TABLE/'p012_recovery_v7_hierarchy.csv',index=False); stages.to_csv(TABLE/'p012_recovery_v7_stage_observations.csv',index=False)
    mapping=pd.DataFrame([{'Legacy_Condition_ID':k,'Exact_ML_Condition_ID':v,'Mapping_Status':'EXACT_REPLACEMENT; LEGACY_RETAINED_EXCLUDED_FROM_INDEPENDENT_COUNT','Original_TRIP':legacy.loc[k,'TRIP'],'Original_TWIP':legacy.loc[k,'TWIP']} for k,v in LEGACY.items()])
    mapping.to_csv(TABLE/'p012_recovery_v7_legacy_mapping.csv',index=False); sh['P012_Integration_Decisions'].to_csv(TABLE/'p012_recovery_v7_decision_correction_ledger.csv',index=False)
    write_audit(src,out,mapping); return src,out

def validate(src,out):
    pd.testing.assert_frame_equal(out.iloc[:len(src)][src.columns].reset_index(drop=True),src,check_dtype=False)
    p=out[out.P012_Record_Role.eq('RECOVERED_EXACT_CONDITION')].set_index('ML_Condition_ID'); s=out[out.P012_Record_Role.eq('RECOVERED_STAGE_CHILD')].set_index('Observation_ID')
    assert len(p)==6 and p.Independent_ML_sample.eq(True).all() and len(s)==20 and s.Independent_ML_sample.eq(False).all() and s.ML_Condition_ID.isna().all()
    assert p.loc[[x for x in p.index if x.endswith('_RT')],'Effective_TRIP'].isna().all() and p.loc[[x for x in p.index if x.endswith('_RT')],'Effective_TWIP'].eq(1).all()
    assert tuple(p.loc['P012_MC_BASE_77K',['Effective_TRIP','Effective_TWIP']].isna())==(False,True)
    assert tuple(p.loc['P012_MC_MO_77K',['Effective_TRIP','Effective_TWIP']].isna())==(False,True)
    assert tuple(p.loc['P012_MC_C_77K',['Effective_TRIP','Effective_TWIP']])==(1,1)
    assert s.loc[[x for x in s.index if '_RT_eps020' in x],'Effective_TRIP'].eq(0).all()
    assert tuple(s.loc['P012_OBS_C_77_eps010',['Effective_TRIP','Effective_TWIP']])==(0,1) and tuple(s.loc['P012_OBS_C_77_eps020',['Effective_TRIP','Effective_TWIP']])==(1,1)
    assert tuple(s.loc['P012_OBS_MO_77_eps010',['Effective_TRIP','Effective_TWIP']])==(0,0) and tuple(s.loc['P012_OBS_MO_77_eps020',['Effective_TRIP','Effective_TWIP']])==(1,0)
    assert p.loc[['P012_MC_BASE_77K','P012_MC_MO_77K'],['YS_MPa','UTS_MPa','Elongation_pct']].isna().all().all()

def write_audit(src,out,mapping):
    b,a=counts(src),counts(out)
    AUDIT.write_text(f'''# P012 recovery v7 audit

## 1–6. Preservation and hierarchy
- recovery_v7 total rows: **{len(out)}**. All **{len(src)}** recovery_v6 rows and all six P012 legacy rows are retained unchanged in their original columns and order.
- Exactly six recovered P012 independent experimental conditions and **20** non-independent repeated-stage observations were added. The three material parents share strict leakage group `P012_SERIES01`; material leakage uses the parent IDs. Batch and tensile replicate IDs remain NA.
- All six legacy rows map exactly by composition and temperature, not row order, to the six replacements in `{(TABLE/'p012_recovery_v7_legacy_mapping.csv').relative_to(ROOT)}` and are excluded from duplicate independent counting.

## 7–14. Recovered descriptors
- Measured chemistry is primary and unnormalised; nominal chemistry is separate. In particular measured carbon **0.6 at.%** is distinct from nominal **0.5 at.%**.
- The solution-annealed initial state is qualitatively single-phase FCC; exact FCC fraction remains NA and direct HCP absence is 0.
- Initial Sigma3 fractions 0.381/0.528/0.567 are explicitly `ANNEALING_TWIN` and never target evidence. Grain size excluding twins (54/40/34 um) and including twins as HABs (28/26/23 um) remain separate.
- Six temperature-specific calculated SFE and DeltaG records retain their thermodynamic methods, status, interfacial energy, molar surface density, and provenance. They are not experimental measurements.
- RT mechanics are Base 140/398/98, Mo 191/484/~80, C 213/581/~80 (YS/UTS/TE). C-77 K is 510/1022/~110; Base/Mo cryogenic values remain NA and Fig.4 was not digitized.

## 15–17. Targets and chronology
- RT targets are TRIP NA/TWIP 1; Base-77 K and Mo-77 K are TRIP 1/TWIP NA; C-77 K is TRIP 1/TWIP 1. Slip is 1 for all six.
- Stage negatives remain stage-specific and never promote condition negatives. Carbon-77 K chronology explicitly preserves Slip+TWIP at 0.1 followed by TWIP+TRIP from 0.2 onward.

## 18–21. Count impact
| Metric | recovery_v6 | recovery_v7 |
|---|---:|---:|
| Independent experimental conditions | {b[0]} | {a[0]} |
| Usable TRIP | {b[1]} | {a[1]} |
| Usable TWIP | {b[2]} | {a[2]} |
| Usable joint labels | {b[3]} | {a[3]} |

## 22–24. Leakage, gaps, blockers
- Stages inherit the strict/material parent grouping and cannot become independent samples. XRD n=5 is lattice-parameter reliability only and creates neither tensile replicates nor rows.
- Missing P012 fields: physical batch, tensile replicate identity/count, exact Base/Mo 77 K mechanical properties, exact initial FCC fraction, and numerical lattice friction stress. The Mo early-stage Results/caption ambiguity is retained in the stage note.
- Remaining P1/P2 blockers: small/imbalanced independent support, unresolved target reviews in other papers, computational/experimental separation, prediction-time feature leakage, sparse grain/phase/SFE/DeltaG coverage, empty traceable descriptor constants, and no final ML-ready target. No ML, feature engineering, derived descriptor, normalization, pseudo-replication, figure digitization, or fabrication occurred.
''',encoding='utf-8')

if __name__=='__main__': integrate()
