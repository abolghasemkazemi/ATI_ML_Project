"""Integrate verified P017 MD evidence into recovery v11 (dataset construction only)."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v10.csv"
BOOK = ROOT / "data/interim/manual_recovery/P017_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v11.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P017_RECOVERY_V11_AUDIT.md"
DOI = "10.1016/j.ijplas.2019.102649"

NEW = ["Computational_Condition_ID", "Independent_Computational_Condition",
 "Independent_Experimental_ML_sample", "Experimental_Target_Eligibility", "Paper_Native_TRIP",
 "Paper_Native_TWIP", "TWIP_induced_TRIP_Status", "TWIP_induced_TRIP_Timing",
 "TRIP_induced_TWIP_Status", "TRIP_induced_TWIP_Timing", "SIS_PSR_GPa", "UTS_PSR_GPa",
 "UTS_PSR_Status", "Initial_BCC_fraction_raw", "Initial_BCC_fraction_status",
 "PostQuench_Initial_Structure", "P017_Record_Role", "P017_Legacy_Mapping_Status",
 "P017_Recovery_Provenance_JSON"]

def experimental_pool(d):
    """Apply the established strict recovery role gate (computational rows never qualify)."""
    x=d[d.Data_Origin.eq("EXPERIMENTAL") & d.Observation_Role.eq("INDEPENDENT_CONDITION")]
    if "P008_Record_Role" in x: x=x[~x.P008_Record_Role.eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")]
    for paper,col in [("P011","P011_Record_Role"),("P012","P012_Record_Role"),("P013","P013_Record_Role"),("P014","P014_Record_Role"),("P015","P015_Record_Role")]:
        if col in d and d[col].eq("RECOVERED_EXACT_CONDITION").any():
            x=x[~(x.Paper_ID.eq(paper)&~x[col].eq("RECOVERED_EXACT_CONDITION"))]
    return x

def counts(d):
    x=experimental_pool(d)
    return (len(x), x.Effective_TRIP.notna().sum(), x.Effective_TWIP.notna().sum(),
            x[["Effective_TRIP","Effective_TWIP"]].notna().all(axis=1).sum())

def make_provenance(sheets):
    rows=[]
    for sheet,frame in sheets.items():
        for rec in frame.to_dict("records"):
            record=rec.get("Computational_Condition_ID", rec.get("Mechanism_Record_ID", rec.get("Record_ID", "P017_SERIES01")))
            material=rec.get("Material_Parent_ID", pd.NA)
            for feature,value in rec.items():
                if feature in {"Paper_ID","DOI","Source_URL"} or pd.isna(value): continue
                rows.append({"Paper_ID":"P017","DOI":DOI,"Material_Parent_ID":material,
                  "Computational_Condition_ID":rec.get("Computational_Condition_ID",rec.get("Parent_Computational_Condition_ID",pd.NA)),
                  "Mechanism_Record_ID":rec.get("Mechanism_Record_ID",pd.NA),"Record_ID":record,
                  "Feature_Name":feature,"Recovered_Value":value,"Units":rec.get("Units",rec.get("Units_or_Type","as reported")),
                  "Evidence_Type":rec.get("Evidence_Type","VERIFIED_WORKBOOK"),"Evidence_Location":rec.get("Evidence_Location",sheet),
                  "Method":rec.get("Method","source-reported"),"Confidence":rec.get("Confidence","High"),
                  "Recovery_Status":rec.get("Recovery_Status","VERIFIED"),"Data_Origin":rec.get("Data_Origin","COMPUTATIONAL_MD")})
    return pd.DataFrame(rows)

def integrate():
    src=pd.read_csv(SOURCE,low_memory=False); sheets=pd.read_excel(BOOK,sheet_name=None,dtype=object)
    for f in sheets.values():
        if "Paper_ID" in f: assert set(f.Paper_ID.dropna())=={"P017"}
        if "DOI" in f: assert set(f.DOI.dropna())=={DOI}
    study=sheets["P017_Study_Method"].iloc[0]; mats=sheets["P017_Material_Parents"].set_index("Material_Parent_ID")
    cond=sheets["P017_Computational_Conditions"]
    assert len(cond)==12 and cond.Computational_Condition_ID.nunique()==12
    out=src.copy()
    for c in NEW:
        if c not in out: out[c]=pd.NA
    prov=make_provenance(sheets); rows=[]
    for c in cond.to_dict("records"):
        m=mats.loc[c["Material_Parent_ID"]]; row={k:pd.NA for k in out.columns}
        row.update({"Paper_ID":"P017","DOI":DOI,"Paper_Title":study.Paper_Title,
          "Condition_ID":c["Computational_Condition_ID"],"Computational_Condition_ID":c["Computational_Condition_ID"],
          "Alloy_ID":c["Alloy_Label"],"Original_Composition":m.Original_Composition_Value,
          "Composition_basis":m.Original_Composition_Basis,"Test_T_K":c["Temperature_K"],
          "Strain_rate_s-1":c["Strain_Rate_s-1"],"True_strain":c["Max_Strain"],
          "Initial_FCC_fraction":pd.NA,"Initial_HCP_fraction":pd.NA,"Initial_BCC_fraction_raw":m.Initial_BCC_fraction,
          "Initial_BCC_fraction_status":m.Initial_BCC_fraction_status,"PostQuench_Initial_Structure":m.PostQuench_Initial_Structure,
          "TRIP":pd.NA,"TWIP":pd.NA,"Effective_TRIP":pd.NA,"Effective_TWIP":pd.NA,
          "Paper_Native_TRIP":c["Paper_Native_TRIP"],"Paper_Native_TWIP":c["Paper_Native_TWIP"],
          "TWIP_induced_TRIP_Status":c["TWIP_induced_TRIP_Status"],"TWIP_induced_TRIP_Timing":c["TWIP_induced_TRIP_Timing"],
          "TRIP_induced_TWIP_Status":c["TRIP_induced_TWIP_Status"],"TRIP_induced_TWIP_Timing":c["TRIP_induced_TWIP_Timing"],
          "SIS_PSR_GPa":c["SIS_PSR_GPa"],"UTS_PSR_GPa":c["UTS_PSR_GPa"],"UTS_PSR_Status":c["UTS_PSR_Status"],
          "YS_MPa":pd.NA,"UTS_MPa":pd.NA,"Experimental_Target_Eligibility":c["Experimental_Target_Eligibility"],
          "Study_Series_ID":c["Study_Series_ID"],"Material_Parent_ID":c["Material_Parent_ID"],
          "Leakage_Group_Strict":c["Leakage_Group_Strict"],"Leakage_Group_Material":c["Leakage_Group_Material"],
          "Parent_Experiment_ID":c["Computational_Condition_ID"],"Parent_ML_Condition_ID":c["Computational_Condition_ID"],
          "ML_Condition_ID":c["Computational_Condition_ID"],"Observation_ID":"P017_OBS_"+c["Computational_Condition_ID"].removeprefix("P017_SIM_"),
          "Data_Origin":"COMPUTATIONAL_MD","Observation_Role":"COMPUTATIONAL_CONDITION",
          "Independent_ML_sample":False,"Independent_Computational_Condition":True,
          "Independent_Experimental_ML_sample":False,"Grouping_Confidence":"HIGH","Grouping_Review_Required":0,
          "P017_Record_Role":"RECOVERED_EXACT_COMPUTATIONAL_CONDITION","Source_File":BOOK.name,
          "Source_Sheet":"P017_Computational_Conditions","Source_location":c["Evidence_Location"],"Label_confidence":c["Confidence"]})
        cp=prov[prov.Computational_Condition_ID.eq(c["Computational_Condition_ID"])].to_dict("records")
        row["P017_Recovery_Provenance_JSON"]=json.dumps(cp,default=str); rows.append(row)
    out=pd.concat([out,pd.DataFrame(rows,columns=out.columns)],ignore_index=True)
    legacy=src[src.Paper_ID.eq("P017")].copy(); mapping=[]
    for _,r in legacy.iterrows():
        hit=cond[(cond.Alloy_Label.eq(r.Alloy_ID))&(cond.Temperature_K.astype(float).eq(r.Test_T_K))&(cond["Strain_Rate_s-1"].astype(float).eq(r["Strain_rate_s-1"]))]
        mapping.append({"Legacy_Condition_ID":r.Condition_ID,"Exact_Computational_Condition_ID":hit.Computational_Condition_ID.iloc[0] if len(hit)==1 else pd.NA,
          "Mapping_Status":"EXACT_CONDITION_MATCH_LEGACY_RETAINED_EXCLUDED_FROM_DOUBLE_COUNT" if len(hit)==1 else "LEGACY_COLLAPSED_COMPUTATIONAL",
          "Match_Basis":"DOI; alloy x; temperature; strain rate; verified condition grid (not row order)"})
    validate(src,out); out.to_csv(OUT,index=False); TABLE.mkdir(parents=True,exist_ok=True)
    exports={"study_method":sheets["P017_Study_Method"],"material_parents":sheets["P017_Material_Parents"],
      "computational_conditions":cond,"gsfe_sfe":sheets["P017_GSFE_SFE"],"coupled_mechanism_landmarks":sheets["P017_Mechanism_Landmarks"],
      "dislocation_physics":sheets["P017_Dislocation_Physics"],"source_safeguards":sheets["P017_Source_Safeguards"],
      "provenance":prov,"legacy_mapping":pd.DataFrame(mapping),"decision_correction_ledger":sheets["P017_Integration_Decisions"]}
    for name,frame in exports.items(): frame.to_csv(TABLE/f"p017_recovery_v11_{name}.csv",index=False)
    write_audit(src,out,pd.DataFrame(mapping)); return src,out

def validate(src,out):
    pd.testing.assert_frame_equal(out.iloc[:len(src)][src.columns].reset_index(drop=True),src,check_dtype=False)
    p=out[out.P017_Record_Role.eq("RECOVERED_EXACT_COMPUTATIONAL_CONDITION")]
    assert len(p)==12 and p.Data_Origin.eq("COMPUTATIONAL_MD").all()
    assert p.Independent_Computational_Condition.eq(True).all() and p.Independent_Experimental_ML_sample.eq(False).all()
    assert p.Effective_TRIP.isna().all() and p.Effective_TWIP.isna().all() and counts(src)==counts(out)

def write_audit(src,out,mapping):
    p=out[out.P017_Record_Role.eq("RECOVERED_EXACT_COMPUTATIONAL_CONDITION")]; b=counts(src); a=counts(out)
    tw=int(p.Paper_Native_TWIP.astype(int).sum()); ti=int(p.TWIP_induced_TRIP_Status.eq("Observed").sum()); it=int(p.TRIP_induced_TWIP_Status.eq("Observed").sum())
    AUDIT.write_text(f"""# P017 recovery v11 audit

## 1–8. Rows, hierarchy, counts, and domain separation
- recovery_v11 total rows: **{len(out)}**. All **{len(src)} recovery_v10 rows** are value/order preserved; **{len(src[src.Paper_ID.eq('P017')])} P017 legacy rows** remain. Twelve exact P017 computational conditions were identified and appended; exact independent computational count is **{len(p)}**.
- Independent experimental conditions before/after: **{b[0]} → {a[0]}**. P017 contributes zero. Independent P017 computational conditions: **12**. Every exact row is `COMPUTATIONAL_MD`, `COMPUTATIONAL_CONDITION`, experimental-independent false, and target-ineligible; experimental splitting/class balance cannot include it.

## 9–17. Composition, state, grids, stresses, and native mechanisms
- Two parents retain molar-ratio formulas `Al0.5Cr1Co1Fe1Cu1Ni1` and `Al1.5Cr1Co1Fe1Cu1Ni1`; measured bulk chemistry and at.% normalization remain NA. Post-quench tensile states are BCC-dominant, never FCC. Al0.5 exact BCC fraction is NA; Al1.5 retains raw `>0.95` with approximate direct-text status, never numeric 0.95.
- At 1e10 s^-1 the temperature grid is 300/700/1000/1300 K for each alloy; at 300 K the rate grid is 1e10/1e9/1e8 s^-1. These extreme MD rates remain outside the experimental distribution.
- SIS-PSR / UTS-PSR (GPa), in workbook order: **{list(zip(p.SIS_PSR_GPa.tolist(),p.UTS_PSR_GPa.where(p.UTS_PSR_GPa.notna(),None).tolist()))}**. Dedicated fields are used; experimental YS/UTS remain NA.
- Paper-native TRIP: **12 positive / 0 negative**. Paper-native TWIP: **{tw} positive / {12-tw} negative**. These reversible BCC↔FCC(HCP/SF) and BCC-nanotwinning labels do not populate experimental targets. TWIP-induced TRIP is observed in **{ti}** conditions; TRIP-induced TWIP in **{it}**.

## 18–23. PTM, GSFE, correlated sequences, and dislocations
- PTM HCP means `HCP_or_SF_atomic_fraction`, not automatically bulk epsilon martensite; no dense curve or atomic snapshot time series was digitized and no fraction was merged with EBSD/XRD.
- Structure-specific 0 K EAM values remain separate: FCC stable gamma_sf = **-14/-27 mJ m-2** (Al0.5/Al1.5); BCC unstable gamma_usf = **610/579 mJ m-2**. All are `CURRENT_PAPER_MD_CALCULATED`, `NOT_EXPERIMENTAL_SFE`.
- GSFE provenance retains 20 unit cells/direction; FCC x[11-2], y[111], z[1-10], a/6<112> on (111); BCC x[111], y[1-10], z[11-2], a/2<111> on a (110)-type plane; lateral x/z PBC.
- Five high-value Fig.20/21/24/25 sequences remain correlated, non-independent supporting records. They include Fig.20 TRIP-induced TWIP, the ISF→ESF and SF-interaction BCC-nucleation landmarks, Fig.24 TWIP-induced TRIP, and Fig.25 bidirectional coupling.
- Phase-specific Shockley partial, BCC perfect-dislocation, temperature/annihilation, Al1.5 defect-network, and rate/stress-transformation fluctuation findings are retained only as atomistic descriptors, never automatic pre-test predictors.

## 24–30. Legacy, leakage, target stability, and gaps
- Legacy mapping: **{mapping.Mapping_Status.value_counts().to_dict()}**. Matching used DOI/alloy/temperature/rate, never row order. Legacy rows are retained; exact matches cannot double-count, and 600 K legacy representations absent from the verified grid are marked collapsed computational.
- Experimental usable TRIP/TWIP/joint counts before/after: **{b[1]}/{b[2]}/{b[3]} → {a[1]}/{a[2]}/{a[3]}** (unchanged). No P017 row enters experimental class balance or train/test splitting.
- Remaining P017 gaps: exact Al0.5 initial BCC fraction, experimental bulk chemistry, physical batch/replicate concepts (not applicable to MD), numeric undigitized phase/dislocation curves, and experimental-equivalent targets/SFE remain unavailable by design.
- Remaining global P1/P2 blockers: small/imbalanced independent experimental support, unresolved labels in other papers, enforced computational separation, sparse grain size/SFE/DeltaG/initial-phase descriptors, and predictor-leakage review. No ML, feature engineering, descriptor calculation, experimental fabrication, or curve digitization occurred.
""",encoding="utf-8")

if __name__=="__main__": integrate()
