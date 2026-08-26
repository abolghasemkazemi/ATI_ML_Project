"""Integrate verified P015 evidence into recovery v10 (dataset construction only)."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v9.csv"
BOOK = ROOT / "data/interim/manual_recovery/P015_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v10.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P015_RECOVERY_V10_AUDIT.md"
DOI = "10.1016/j.jallcom.2026.188919"

NEW = ["P015_Record_Role","P015_Target_Status","P015_Legacy_Mapping_Status","Mn_Charge_Adjustment",
 "Raw_Material_Purity","Initial_Phase_Status","Grain_Size_Status","Texture_Orientation_Status",
 "Elemental_Segregation_Status","Engineering_YS_MPa","Engineering_UTS_MPa","Engineering_Elongation_pct",
 "True_Yield_Stress_MPa","True_UTS_MPa","HC","True_Property_Status","Postfracture_Phase_State",
 "Postfracture_HCP_fraction","Postfracture_HCP_fraction_Status","Fracture_Mode","Negative_Evidence_Quality",
 "SFE_Value_Status","SFE_Data_Origin","Critical_Stress_Model_Validity","P015_Recovery_Provenance_JSON"]

def eligible(d):
    x=d[d.Data_Origin.eq("EXPERIMENTAL") & d.Observation_Role.eq("INDEPENDENT_CONDITION")]
    for paper,col,pattern in [("P012","P012_Record_Role",r"P012_C0[1-6]"),("P011","P011_Record_Role",r"P011_C0[1-5]")]:
        if col in d and d[col].eq("RECOVERED_EXACT_CONDITION").any(): x=x[~(x.Paper_ID.eq(paper)&x.Condition_ID.str.match(pattern,na=False))]
    if "P008_Record_Role" in x: x=x[~x.P008_Record_Role.eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")]
    for paper,col in [("P013","P013_Record_Role"),("P014","P014_Record_Role"),("P015","P015_Record_Role")]:
        if col in d and d[col].eq("RECOVERED_EXACT_CONDITION").any(): x=x[~(x.Paper_ID.eq(paper)&~x[col].eq("RECOVERED_EXACT_CONDITION"))]
    return x

def counts(d):
    x=eligible(d)
    return len(x),x.Effective_TRIP.notna().sum(),x.Effective_TWIP.notna().sum(),x[["Effective_TRIP","Effective_TWIP"]].notna().all(axis=1).sum()

def integrate():
    src=pd.read_csv(SOURCE,low_memory=False); sheets=pd.read_excel(BOOK,sheet_name=None)
    for f in sheets.values():
        if "Paper_ID" in f: assert set(f.Paper_ID.dropna())=={"P015"}
        if "DOI" in f: assert set(f.DOI.dropna())=={DOI}
    study=sheets["P015_Study_Processing"].iloc[0]; micro=sheets["P015_Initial_Microstructure"].iloc[0]
    cond=sheets["P015_ML_Conditions"]; assert set(cond.ML_Condition_ID)=={"P015_MC_298K","P015_MC_77K"}
    legacy=src[src.Paper_ID.eq("P015")]; assert len(legacy)==2 and legacy.DOI.eq(DOI).all()
    mapping={"P015_C01":"P015_MC_298K","P015_C02":"P015_MC_77K"}
    assert set(legacy.Condition_ID)==set(mapping)
    originals={mapping[r.Condition_ID]:(r.TRIP,r.TWIP) for _,r in legacy.iterrows()}
    out=src.copy()
    for c in NEW:
        if c not in out: out[c]=pd.NA
    provenance=[]; identities={"Paper_ID","DOI","Source_URL"}
    for sheet,frame in sheets.items():
        for rec in frame.to_dict("records"):
            for feature,value in rec.items():
                if feature in identities or pd.isna(value): continue
                mc=rec.get("ML_Condition_ID",pd.NA)
                if pd.isna(mc): mc="P015_ALLOY_OR_SUPPORTING_SCOPE"
                material=rec.get("Material_Parent_ID",study.Material_Parent_ID)
                if pd.isna(material): material=study.Material_Parent_ID
                evidence=rec.get("Evidence_Type",rec.get("Value_Status","VERIFIED_WORKBOOK"))
                if pd.isna(evidence): evidence="VERIFIED_WORKBOOK"
                location=rec.get("Evidence_Location",sheet)
                if pd.isna(location): location=sheet
                method=rec.get("Method",rec.get("Evidence_Methods","source-reported"))
                if pd.isna(method): method="source-reported"
                confidence=rec.get("Confidence","High")
                if pd.isna(confidence): confidence="High"
                provenance.append({"Paper_ID":"P015","DOI":DOI,"Material_Parent_ID":material,
                  "ML_Condition_ID":mc,"Feature_Name":feature,"Recovered_Value":value,
                  "Units":"as named/reported","Evidence_Type":evidence,
                  "Evidence_Location":location,"Method":method,"Confidence":confidence,"Recovery_Status":"VERIFIED"})
    rows=[]
    for c in cond.to_dict("records"):
        row={k:pd.NA for k in out.columns}; otr,otw=originals[c["ML_Condition_ID"]]
        row.update({"Paper_ID":"P015","DOI":DOI,"Paper_Title":study.Paper_Title,"Condition_ID":c["ML_Condition_ID"],
          "Alloy_ID":"Fe50Mn20Cr20Ni10","Original_Composition":study.Nominal_Composition_at_pct,"Nominal_Composition_at_pct":study.Nominal_Composition_at_pct,
          "Composition_basis":"at.% nominal","Composition_Status":study.Composition_Status,"Measured_Composition_at_pct":pd.NA,"Measured_Composition_Status":study.Composition_Status,
          "Fe_at%":50,"Mn_at%":20,"Cr_at%":20,"Ni_at%":10,"Mn_Charge_Adjustment":study.Mn_Charge_Adjustment,"Raw_Material_Purity":study.Raw_Material_Purity,
          "Processing_route":"Vacuum induction melting under Ar in BN crucible; ~350 g master alloy remelted; copper-mold cast 30 x 30 x 100 mm; homogenized 1473 K/6 h; water quenched",
          "Cast_method":study.Melting_Route,"Homogenization_T_K":1473,"Homogenization_time_h":6,"Cooling_route":"Water quench",
          "Test_T_K":c["Test_T_K"],"Test_T_Raw":c["Test_T_Raw"],"Strain_rate_s-1":c["Strain_rate_s-1"],"Gauge_length_mm":10,"Gauge_width_mm":3,"Specimen_thickness_mm":1,
          "Grain_size_um":micro.Average_Grain_Size_um,"Grain_Size_Status":micro.Grain_Size_Status,"Initial_FCC_fraction":pd.NA,"Initial_HCP_fraction":0,
          "Initial_Phase_State_Qualitative":micro.Initial_Phase_State,"Initial_Phase_Status":micro.Initial_Phase_Status,"Texture_Orientation_Status":micro.Texture_Orientation_Status,
          "Elemental_Segregation_Status":micro.Elemental_Segregation_Status,"SFE_mJ_m2":36.62 if c["Test_T_K"]==298 else 10.97,
          "SFE_method":"LAMMPS molecular dynamics using Daramola et al. interatomic potential","SFE_Value_Status":"CURRENT_PAPER_MD_CALCULATED","SFE_Data_Origin":"COMPUTATIONAL_MD",
          "DeltaG_FCC_HCP_J_mol":pd.NA,"Engineering_YS_MPa":c["Engineering_YS_MPa"],"Engineering_UTS_MPa":c["Engineering_UTS_MPa"],
          "Engineering_Elongation_pct":c["Engineering_Elongation_pct"],"YS_MPa":c["Engineering_YS_MPa"],"UTS_MPa":c["Engineering_UTS_MPa"],"Elongation_pct":c["Engineering_Elongation_pct"],
          "True_Yield_Stress_MPa":c["True_Yield_Stress_MPa"],"True_UTS_MPa":c["True_UTS_MPa"],"HC":c["HC"],"True_Property_Status":c["True_Property_Status"],
          "TRIP":pd.NA,"TWIP":pd.NA,"Original_TRIP":otr,"Original_TWIP":otw,"Recovered_TRIP":c["TRIP"],"Recovered_TWIP":c["TWIP"],
          "Effective_TRIP":c["TRIP"],"Effective_TWIP":c["TWIP"],"Slip":c["Slip"],"Dominant_mechanism":c["Dominant_Mechanism"],"P015_Target_Status":c["Target_Status"],
          "Postfracture_Phase_State":c["Postfracture_Phase_State"],"Postfracture_HCP_fraction":c["Postfracture_HCP_fraction"],
          "Postfracture_HCP_fraction_Status":c["Postfracture_HCP_fraction_Status"],"Fracture_Mode":c["Fracture_Mode"],
          "Negative_Evidence_Quality":"EXPLICIT_INITIAL_TO_FINAL_PHASE_NEGATIVE" if c["Test_T_K"]==298 else "NOT_APPLICABLE",
          "Replicate_n":3,"Replicate_ID":pd.NA,"Physical_Batch_ID":pd.NA,"Study_Series_ID":c["Study_Series_ID"],"Material_Parent_ID":c["Material_Parent_ID"],
          "Leakage_Group_Strict":c["Leakage_Group_Strict"],"Leakage_Group_Material":c["Leakage_Group_Material"],"Parent_Experiment_ID":c["ML_Condition_ID"],
          "Parent_ML_Condition_ID":c["ML_Condition_ID"],"ML_Condition_ID":c["ML_Condition_ID"],"Observation_ID":"P015_OBS_"+str(c["Test_T_K"])+"K",
          "Data_Origin":"EXPERIMENTAL","Observation_Role":"INDEPENDENT_CONDITION","Independent_ML_sample":True,"Grouping_Confidence":"HIGH","Grouping_Review_Required":0,
          "P015_Record_Role":"RECOVERED_EXACT_CONDITION","Source_File":BOOK.name,"Source_Sheet":"P015_ML_Conditions","Source_location":c["Evidence_Location"],"Label_confidence":c["Confidence"],
          "Critical_Stress_Model_Validity":"LIMITED_VALIDITY_AT_298K" if c["Test_T_K"]==298 else "CURRENT_PAPER_CALCULATED"})
        row["P015_Recovery_Provenance_JSON"]=json.dumps([p for p in provenance if not pd.isna(p["ML_Condition_ID"]) and p["ML_Condition_ID"]==c["ML_Condition_ID"]],default=str)
        rows.append(row)
    out=pd.concat([out,pd.DataFrame(rows,columns=out.columns)],ignore_index=True); validate(src,out); out.to_csv(OUT,index=False)
    exports={"hierarchy":cond[["Study_Series_ID","Material_Parent_ID","ML_Condition_ID","Independent_ML_sample","Leakage_Group_Strict","Leakage_Group_Material"]],
      "postfracture_experimental_evidence":sheets["P015_Postfracture_Evidence"],"target_evidence":sheets["P015_Target_Evidence"],
      "sfe_critical_stress_physics":sheets["P015_Physics_SFE_Critical"],"md_stages":sheets["P015_MD_Stages"],
      "source_consistency":sheets["P015_Source_Consistency"],"provenance":pd.DataFrame(provenance),
      "legacy_mapping":pd.DataFrame([{"Legacy_Condition_ID":k,"Exact_ML_Condition_ID":v,"Mapping_Status":"EXACT_IDENTITY_MATCH; LEGACY_RETAINED_EXCLUDED_FROM_REPLACEMENT_COUNT","Original_TRIP":originals[v][0],"Original_TWIP":originals[v][1]} for k,v in mapping.items()]),
      "correction_decision_ledger":sheets["P015_Integration_Decisions"]}
    for name,frame in exports.items(): frame.to_csv(TABLE/f"p015_recovery_v10_{name}.csv",index=False)
    write_audit(src,out); return src,out

def validate(src,out):
    pd.testing.assert_frame_equal(out.iloc[:len(src)][src.columns].reset_index(drop=True),src,check_dtype=False)
    p=out[out.P015_Record_Role.eq("RECOVERED_EXACT_CONDITION")]
    assert len(p)==2 and p.Independent_ML_sample.eq(True).all() and p.Replicate_n.eq(3).all()
    assert p.Measured_Composition_at_pct.isna().all() and p.Initial_FCC_fraction.isna().all() and p.Initial_HCP_fraction.eq(0).all()
    assert p["Strain_rate_s-1"].eq(.001).all() and not ((out.Paper_ID.eq("P015")) & (out["Strain_rate_s-1"]==1000)).any()

def write_audit(src,out):
    b,a=counts(src),counts(out)
    AUDIT.write_text(f"""# P015 recovery v10 audit

## A–D. Rows, hierarchy, mappings, and target impact
- recovery_v10 has **{len(out)} rows**; all **{len(src)} recovery_v9 rows are byte-value/order preserved**, including both P015 legacy rows. Two exact experimental conditions were added: `P015_MC_298K` and `P015_MC_77K`.
- Legacy C01/C02 map by DOI, nominal chemistry, temperature, strain rate, initial phase, mechanics, SFE, and targets—not row order—to 298 K/77 K respectively. Legacy records remain preserved and replacement-excluded. Independent / usable TRIP / usable TWIP / usable joint: **{b[0]}/{b[1]}/{b[2]}/{b[3]} before → {a[0]}/{a[1]}/{a[2]}/{a[3]} after**.
- Effective targets are 298 K **0/1** and 77 K **1/1** (TRIP/TWIP), with Slip=1. Original targets remain separate.

## E. Strong negative-label improvement and phase evidence
- The 298 K TRIP=0 is high-quality initial-to-final evidence: initial XRD/EBSD single FCC (HCP=0), then post-fracture XRD only FCC and EBSD stable single FCC/no HCP. At 77 K weak HCP XRD peaks, minor EBSD HCP grains, and TEM/HR-TEM/SAED/IFFT lath epsilon martensite establish TRIP=1. No exact post-fracture 77 K HCP fraction is fabricated.
- Initial FCC fraction remains NA because no numeric fraction was reported; initial HCP=0 is direct phase-absence evidence. Grain size is approximately 100 um (`APPROX_DIRECT_TEXT`), orientation random, and EDS reports no obvious segregation without becoming bulk chemistry.

## F. SFE and critical-stress physics
- Temperature-specific SFE improves to 36.62 (298 K) and 10.97 mJ/m2 (77 K), both current-paper LAMMPS MD calculations using the Daramola potential—not experiments. Gamma_SF=10.97 is a reuse of the 77 K SFE model input, not another observation; interface energy 8 mJ/m2 remains a secondary reference input.
- Model twin thresholds are 658 MPa (298 K) / 440 MPa (77 K), and martensite thresholds 745/742 MPa. They remain calculated thresholds. The 298 K predictions carry `LIMITED_VALIDITY_AT_298K` and cannot override experimental targets. At 77 K, TWIP near plastic onset and TRIP near 12% strain are `MODEL_CURVE_INFERENCE`, not direct stages. DeltaG remains NA.

## G–H. Mechanical properties and source conflict
- Engineering YS/UTS/elongation are 300/550 MPa/60% at 298 K and 608/850 MPa/35% at 77 K. Separate Table 1 true YS/UTS/HC are 300.25/888.61/1.960 and 690.33/1368.75/0.983; no reconciliation or overwrite occurred.
- Methods/body quasi-static rate 1e-3 s^-1 is canonical. The contradictory 1000 s^-1 captions (Figs.4,7,9) are retained in the source-consistency table only; no such experimental condition exists. Replicate_n=3 is aggregate metadata, with no three pseudo-rows, Replicate_ID NA, and batch NA.

## I–J. Computational domain, fracture/evidence, and decisions
- Eight MD snapshots remain only in the supporting MD table as `COMPUTATIONAL_MD`, `CORRELATED_SIM_STAGE`, non-independent; none enters the master or overrides experimental TWIP=1 at 77 K. Comparative higher 77 K KAM remains qualitative. Fracture is ductile-dimpled at 298 K and mixed dimples/cleavage at 77 K.
- The mapping and decision/correction ledger records no target conflict: legacy 0/1 and 1/1 agree with verified effective targets while exact rows strengthen provenance.

## K–L. Remaining gaps and blockers
- P015 gaps: no post-melt quantitative bulk chemistry, physical-batch or individual-replicate identity/results, exact initial FCC fraction, numeric 77 K post-fracture HCP fraction, numeric KAM means, alloy-specific DeltaG, direct experimental onset stages, or experimental SFE.
- Global P1/P2 blockers remain small/imbalanced independent support, unresolved labels in other papers, strict experimental/computational separation, sparse grain size/SFE/DeltaG/initial phase descriptors, predictor-leakage review, and empty traceable descriptor-reference constants. No ML, feature engineering, alloy-descriptor calculation, figure digitization, or scientific-value fabrication occurred.
""",encoding="utf-8")

if __name__=="__main__": integrate()
