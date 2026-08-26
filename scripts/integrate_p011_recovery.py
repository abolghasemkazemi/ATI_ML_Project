"""Integrate verified P011 evidence into recovery_v6 without derived data."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/processed/master_19papers_recovery_v5.csv'
BOOK=ROOT/'data/interim/manual_recovery/P011_scientific_evidence_recovery_VERIFIED.xlsx'
OUT=ROOT/'data/processed/master_19papers_recovery_v6.csv'
PROV=ROOT/'reports/tables/p011_recovery_v6_provenance.csv'
CORR=ROOT/'reports/tables/p011_recovery_v6_corrections.csv'
STATES=ROOT/'reports/tables/p011_recovery_v6_source_states.csv'
SFE=ROOT/'reports/tables/p011_recovery_v6_sfe.csv'
EXTRA=ROOT/'reports/tables/p011_recovery_v6_extra_descriptors.csv'
MAPPING=ROOT/'reports/tables/p011_recovery_v6_legacy_mapping.csv'
AUDIT=ROOT/'reports/P011_RECOVERY_V6_AUDIT.md'
DOI='10.1016/j.jallcom.2023.170225'

FIELDS=['Independent_ML_sample','Processing_State_ID','Source_Material_ID','Sintering_T_C',
 'Relative_Density_pct','Effective_Grain_Size_Including_TB_PhaseBoundary_um','Initial_Sigma3_TB_fraction',
 'Initial_Twin_Type','Mn_Oxide_Area_Fraction','SPS_Pressure_MPa','SPS_Time_min','SPS_Vacuum_Pa',
 'Detwinning','Feedstock_Composition_at_pct','Feedstock_Composition_Method','Feedstock_Composition_Scope',
 'Local_EDS_Composition_at_pct','Local_EDS_Composition_Scope','FCC_lattice_a_XRD_A','HCP_lattice_a_XRD_A',
 'HCP_lattice_c_XRD_A','KAM_mean_deg','HCP_lath_thickness_nm','Deformation_Twin_thickness_nm',
 'P011_Record_Role','P011_Target_Status','P011_Negative_TWIP_Evidence','P011_Recovery_Provenance_JSON']

def independent(df):
    d=df[df.Data_Origin.eq('EXPERIMENTAL') & df.Observation_Role.eq('INDEPENDENT_CONDITION')]
    # Once exact P011 replacements exist, its five legacy extraction rows are not counted again.
    if 'P011_Record_Role' in df and df.P011_Record_Role.eq('RECOVERED_EXACT_CONDITION').any():
        d=d[~(d.Paper_ID.eq('P011') & d.Condition_ID.isin([f'P011_C0{i}' for i in range(1,6)]))]
    if 'P008_Record_Role' in d: d=d[~d.P008_Record_Role.eq('LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT')]
    return d

def counts(df):
    d=independent(df)
    return len(d),d.Effective_TRIP.notna().sum(),d.Effective_TWIP.notna().sum(),d[['Effective_TRIP','Effective_TWIP']].notna().all(axis=1).sum()

def integrate():
    src=pd.read_csv(SOURCE,low_memory=False); sh=pd.read_excel(BOOK,sheet_name=None)
    assert all(set(x.Paper_ID)=={'P011'} for x in sh.values() if 'Paper_ID' in x)
    assert all(set(x.DOI)=={DOI} for x in sh.values() if 'DOI' in x)
    cond=sh['P011_ML_Conditions']; stages=sh['P011_Stage_Observations']; states=sh['P011_Source_States']
    assert len(cond)==4 and len(stages)==6 and len(states)==4
    out=src.copy()
    for f in FIELDS:
        if f not in out: out[f]=pd.NA
    feed=sh['P011_Study_Feedstock'].iloc[0]; targets=sh['P011_Target_Evidence'].set_index('ML_Condition_ID')
    state=states.set_index('Processing_State_ID'); prov=[]; rows=[]
    def pv(cid,oid,f,v,u,etype,loc,conf):
        if pd.notna(v): prov.append(dict(Paper_ID='P011',DOI=DOI,ML_Condition_ID=cid,Observation_ID=oid,
          Feature_Name=f,Recovered_Value=v,Units=u,Evidence_Type=etype,Evidence_Location=loc,Confidence=conf,Recovery_Status='VERIFIED'))
    for c in cond.to_dict('records'):
        st=state.loc[c['Processing_State_ID']]; cid=c['ML_Condition_ID']; oid=cid.replace('_MC_','_OBS_')+'_condition'
        r={k:pd.NA for k in out.columns}; r.update({
          'Paper_ID':'P011','DOI':DOI,'Paper_Title':feed.Paper_Title,'Condition_ID':cid,'Alloy_ID':c['Alloy_Label'],
          'Original_Composition':feed.Nominal_Composition_at_pct,'Composition_basis':'at.% nominal; feedstock EDS retained separately',
          'Fe_at%':49.2,'Mn_at%':31.4,'Co_at%':9.4,'Cr_at%':10.0,'Processing_route':f"commercial gas-atomized pre-alloy powder; SPS {c['Sintering_T_C']} C/30 min, 45 MPa, vacuum 7e-3 Pa",
          'Annealing_T_K':c['Sintering_T_C']+273.15,'Test_T_K':c['Test_T_K'],'Strain_rate_s-1':c['Strain_rate_s-1'],
          'Gauge_length_mm':10,'Gauge_width_mm':2,'Specimen_thickness_mm':1,'Grain_size_um':c['Grain_Size_um'],
          'Initial_FCC_fraction':c['Initial_FCC_fraction'],'Initial_HCP_fraction':c['Initial_HCP_fraction'],
          'Initial_twin_boundary_status':'ANNEALING_TWIN','YS_MPa':c['YS_MPa'],'UTS_MPa':c['UTS_MPa'],
          'Uniform_elongation_pct':c['Uniform_Elongation_pct'],'TRIP':pd.NA,'TWIP':pd.NA,'Recovered_TRIP':c['TRIP'],
          'Recovered_TWIP':c['TWIP'],'Effective_TRIP':c['TRIP'],'Effective_TWIP':c['TWIP'],'Slip':c['Slip'],
          'Detwinning':c['Detwinning'],'Dominant_mechanism':c['Dominant_Mechanism'],'Evidence_TRIP':targets.loc[cid,'TRIP_Evidence'],
          'Evidence_TWIP':targets.loc[cid,'TWIP_Evidence'],'Source_location':c['Evidence_Location'],'Label_confidence':c['Confidence'],
          'Study_Series_ID':'P011_SERIES01','Source_Material_ID':'P011_FEEDSTOCK_GA01','Material_Parent_ID':'P011_MAT_FE50MN30CO10CR10',
          'Physical_Batch_ID':pd.NA,'Replicate_ID':pd.NA,'Replicate_n':3,'Leakage_Group_Strict':'P011_SERIES01',
          'Leakage_Group_Material':'P011_MAT_FE50MN30CO10CR10','Parent_Experiment_ID':cid,'ML_Condition_ID':cid,
          'Parent_ML_Condition_ID':cid,'Observation_ID':oid,'Data_Origin':'EXPERIMENTAL','Observation_Role':'INDEPENDENT_CONDITION',
          'Independent_ML_sample':True,'Grouping_Confidence':'HIGH','Grouping_Review_Required':0,'Processing_State_ID':c['Processing_State_ID'],
          'Sintering_T_C':c['Sintering_T_C'],'Relative_Density_pct':st.Relative_Density_pct,
          'Effective_Grain_Size_Including_TB_PhaseBoundary_um':st.Effective_Grain_Size_Including_TB_PhaseBoundary_um,
          'Initial_Sigma3_TB_fraction':st.Initial_Sigma3_TB_fraction,'Initial_Twin_Type':'ANNEALING_TWIN',
          'Mn_Oxide_Area_Fraction':st.Mn_Oxide_Area_Fraction,'SPS_Pressure_MPa':45,'SPS_Time_min':30,'SPS_Vacuum_Pa':.007,
          'Feedstock_Composition_at_pct':feed.Feedstock_Actual_Composition_at_pct,'Feedstock_Composition_Method':'EDS',
          'Feedstock_Composition_Scope':'FEEDSTOCK','FCC_lattice_a_XRD_A':st.FCC_lattice_a_A,'HCP_lattice_a_XRD_A':st.HCP_lattice_a_A,
          'HCP_lattice_c_XRD_A':st.HCP_lattice_c_A,'P011_Record_Role':'RECOVERED_EXACT_CONDITION','P011_Target_Status':c['Target_Status'],
          'P011_Negative_TWIP_Evidence':targets.loc[cid,'Negative_Evidence_Quality'] if c['TWIP']==0 else pd.NA,
          'Source_File':BOOK.name,'Source_Sheet':'P011_ML_Conditions'})
        if c['Processing_State_ID']=='P011_PS_A10':
            r['Local_EDS_Composition_at_pct']='Fe49.5Mn29.6Co10.5Cr10.4'; r['Local_EDS_Composition_Scope']='LOCAL_OR_SCANNED_REGION_EDS'
        for f,u in [('Test_T_K','K'),('Strain_rate_s-1','s^-1'),('Initial_FCC_fraction','fraction'),('Initial_HCP_fraction','fraction'),('Grain_size_um','um'),('Effective_Grain_Size_Including_TB_PhaseBoundary_um','um'),('Relative_Density_pct','%'),('YS_MPa','MPa'),('UTS_MPa','MPa'),('Uniform_elongation_pct','%'),('Effective_TRIP','binary'),('Effective_TWIP','binary'),('Slip','binary'),('Detwinning','binary'),('Initial_Sigma3_TB_fraction','fraction'),('Initial_Twin_Type','categorical'),('Mn_Oxide_Area_Fraction','fraction'),('Feedstock_Composition_at_pct','at.%'),('Local_EDS_Composition_at_pct','at.%'),('FCC_lattice_a_XRD_A','A'),('HCP_lattice_a_XRD_A','A'),('HCP_lattice_c_XRD_A','A')]:
            pv(cid,oid,f,r[f],u,'VERIFIED_WORKBOOK',c['Evidence_Location'],c['Confidence'])
        r['P011_Recovery_Provenance_JSON']=json.dumps([x for x in prov if x['ML_Condition_ID']==cid],default=str); rows.append(r)
    parents={r['ML_Condition_ID']:r for r in rows}
    for s in stages.to_dict('records'):
        p=parents[s['Parent_ML_Condition_ID']]; r={k:pd.NA for k in out.columns}
        for k in ['Paper_ID','DOI','Paper_Title','Alloy_ID','Study_Series_ID','Source_Material_ID','Material_Parent_ID','Leakage_Group_Strict','Leakage_Group_Material','Processing_State_ID']: r[k]=p[k]
        r.update({'Condition_ID':s['Observation_ID'],'Observation_ID':s['Observation_ID'],'ML_Condition_ID':pd.NA,
          'Parent_ML_Condition_ID':s['Parent_ML_Condition_ID'],'Parent_Experiment_ID':s['Parent_ML_Condition_ID'],
          'Observation_Role':'REPEATED_STAGE','Independent_ML_sample':False,'Data_Origin':'EXPERIMENTAL','Test_T_K':s['Test_T_K'],
          'Deformation_stage':s['Stage_Name'],'HCP_fraction_at_condition':s['HCP_fraction'],'Twin_fraction_or_Sigma3':s['Sigma3_TB_fraction'],
          'Recovered_TRIP':s['TRIP_at_stage'],'Recovered_TWIP':s['TWIP_at_stage'],'Effective_TRIP':s['TRIP_at_stage'],
          'Effective_TWIP':s['TWIP_at_stage'],'Slip':s['Slip_at_stage'],'Detwinning':s['Detwinning_at_stage'],
          'KAM_mean_deg':s['KAM_mean_deg'],'HCP_lath_thickness_nm':s['HCP_lath_thickness_nm'],
          'Deformation_Twin_thickness_nm':s['Deformation_Twin_thickness_nm'],'Initial_Twin_Type':'ANNEALING_TWIN',
          'Source_location':s['Evidence_Location'],'Label_confidence':s['Confidence'],'Deformation_Stage_ID':s['Observation_ID'],
          'Grouping_Confidence':'HIGH','P011_Record_Role':'RECOVERED_STAGE_CHILD','Source_File':BOOK.name,'Source_Sheet':'P011_Stage_Observations'})
        for f,u in [('HCP_fraction_at_condition','fraction'),('Twin_fraction_or_Sigma3','fraction'),('KAM_mean_deg','degree'),('HCP_lath_thickness_nm','nm'),('Deformation_Twin_thickness_nm','nm'),('Effective_TRIP','binary'),('Effective_TWIP','binary')]: pv(s['Parent_ML_Condition_ID'],s['Observation_ID'],f,r[f],u,s['Evidence_Type'],s['Evidence_Location'],s['Confidence'])
        rows.append(r)
    out=pd.concat([out,pd.DataFrame(rows,columns=out.columns)],ignore_index=True)
    validate(src,out); OUT.write_text(out.to_csv(index=False),encoding='utf-8'); pd.DataFrame(prov).to_csv(PROV,index=False)
    states.to_csv(STATES,index=False); sh['P011_Physics_SFE'].to_csv(SFE,index=False); sh['P011_Extra_Descriptors'].to_csv(EXTRA,index=False)
    mapping=pd.DataFrame([['P011_C01','P011_PS_A8',pd.NA,'SOURCE_STATE_ONLY; LEGACY_TARGETS_UNSUPPORTED'],['P011_C02','P011_PS_A9','P011_MC_A9_298K','EXACT_REPLACEMENT'],['P011_C03','P011_PS_A10','P011_MC_A10_298K','EXACT_REPLACEMENT'],['P011_C04','P011_PS_A11','P011_MC_A11_298K','EXACT_REPLACEMENT'],['P011_C05','P011_PS_A10','P011_MC_A10_77K','EXACT_REPLACEMENT']],columns=['Legacy_Condition_ID','Processing_State_ID','Exact_ML_Condition_ID','Mapping_Status']); mapping.to_csv(MAPPING,index=False)
    sh['P011_Integration_Decisions'].to_csv(CORR,index=False); write_audit(src,out,mapping); return src,out

def validate(src,out):
    pd.testing.assert_frame_equal(out.iloc[:len(src)][src.columns].reset_index(drop=True),src,check_dtype=False)
    p=out[out.P011_Record_Role.eq('RECOVERED_EXACT_CONDITION')].set_index('ML_Condition_ID'); s=out[out.P011_Record_Role.eq('RECOVERED_STAGE_CHILD')]
    assert len(p)==4 and len(s)==6 and s.Independent_ML_sample.eq(False).all()
    assert tuple(p.loc['P011_MC_A10_298K',['Effective_TRIP','Effective_TWIP']])==(1,1)
    assert tuple(p.loc['P011_MC_A10_77K',['Effective_TRIP','Effective_TWIP']])==(1,0)
    assert p.loc[['P011_MC_A9_298K','P011_MC_A11_298K'],['Effective_TRIP','Effective_TWIP']].isna().all().all()
    assert p.loc['P011_MC_A9_298K',['UTS_MPa','Uniform_elongation_pct']].isna().all()
    assert s[s.Observation_ID.str.contains('eps15')].HCP_fraction_at_condition.isna().all()
    assert set(s.Leakage_Group_Strict)=={'P011_SERIES01'} and p.Replicate_ID.isna().all()

def write_audit(src,out,mapping):
    b,a=counts(src),counts(out)
    AUDIT.write_text(f'''# P011 recovery v6 audit

## Preservation, hierarchy, and leakage
- recovery_v6 total rows: **{len(out)}**; all **{len(src)}** recovery_v5 rows are byte-value-equivalent in their original columns and order.
- Four source processing states (A8/A9/A10/A11) are preserved in `{STATES.relative_to(ROOT)}`. A8 is not a primary condition.
- Exactly four primary independent conditions were appended: `P011_MC_A9_298K`, `P011_MC_A10_298K`, `P011_MC_A11_298K`, and `P011_MC_A10_77K`.
- Six repeated-stage children were appended; all are non-independent and inherit `P011_SERIES01` / `P011_MAT_FE50MN30CO10CR10` leakage groups.
- Five legacy rows remain unchanged. Scientific matching maps C02-C05 exactly to replacements; C01 maps only to A8 and is excluded from independent use. Thus neither legacy rows nor n=3 aggregate tensile metadata are double-counted.

## Counts
| Metric | recovery_v5 | recovery_v6 |
|---|---:|---:|
| Independent experimental conditions | {b[0]} | {a[0]} |
| Usable TRIP | {b[1]} | {a[1]} |
| Usable TWIP | {b[2]} | {a[2]} |
| Usable joint | {b[3]} | {a[3]} |

## Recovered evidence
- Feedstock EDS is Fe49.2Mn31.4Co9.4Cr10.0 at.% at `FEEDSTOCK` scope. A10 Fe49.5Mn29.6Co10.5Cr10.4 is separately `LOCAL_OR_SCANNED_REGION_EDS`.
- Relative densities, initial EBSD phase fractions, primary and alternative grain-size definitions, annealing Sigma3 boundary fractions, Mn-oxide fractions, and initial XRD lattice parameters are preserved by processing state. Initial annealing twins never establish TWIP.
- Mechanics: A9 YS 300.5 MPa (UTS/UE unresolved); A10-298 287.1/745.7 MPa and 28.1% UE; A11-298 257.3/708.9 MPa and 31.0% UE; A10-77 489.7/1107.3 MPa and 25.5% UE.
- Effective targets: A10-298=1/1; A10-77=1/0 with explicit direct negative TWIP evidence; A9/A11 remain NA/NA. Slip and detwinning remain separate mechanism fields.
- Initial versus fracture HCP and XRD versus fracture TEM lattice parameters remain distinct. No exact 15% HCP value was digitized. Sigma3 is not treated as deformation-twin volume fraction.
- SFE is method-separated in `{SFE.relative_to(ROOT)}`: current-paper thermodynamic 18.4 (298 K) and -14.4 (77 K), versus secondary ab-initio ranges 14–22 and -9–-2 mJ/m2. No value is duplicated per SPS state or called experimental.

## Unresolved fields and blockers
A9 exact UTS/UE, both 15% HCP fractions, A9/A11 condition-specific targets, A8 EBSD phase fractions/tensile condition, physical-batch and individual replicate identities remain unresolved. Remaining project P1/P2 blockers include broader target review, feature-leakage eligibility, computational/experimental domain separation, sparse descriptors/reference constants, small support, and final-target selection. No ML, feature engineering, derived descriptors, figure digitization, pseudo-replicates, or fabricated values were produced.
''',encoding='utf-8')

if __name__=='__main__': integrate()
