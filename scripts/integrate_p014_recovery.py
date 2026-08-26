"""Integrate verified P014 evidence into recovery v9 (dataset construction only)."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v8.csv"
BOOK = ROOT / "data/interim/manual_recovery/P014_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v9.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P014_RECOVERY_V9_AUDIT.md"
DOI = "10.3390/ma17235893"

NEW = ["P014_Record_Role", "P014_Target_Status", "P014_Legacy_Mapping_Status",
       "Cold_Roll_Reduction_Status", "Cold_Roll_Pass_Reduction_mm", "Remelting_n",
       "Test_T_Status", "Initial_Phase_Status", "KAM_Status", "Recrystallized_fraction",
       "Recrystallized_Status", "Processing_TRIP", "Processing_TWIP",
       "Initial_Twin_Origin", "Initial_Twin_Target_Safety", "Tensile_Strain_pct",
       "FCC_fraction_at_stage", "TWIP_at_stage", "TRIP_at_stage", "Slip_at_stage",
       "HDI_at_stage", "HDI_Hardening", "P014_Recovery_Provenance_JSON"]

def eligible(d):
    x=d[d.Data_Origin.eq("EXPERIMENTAL") & d.Observation_Role.eq("INDEPENDENT_CONDITION")]
    for paper,col,pattern in [("P012","P012_Record_Role",r"P012_C0[1-6]"),
                              ("P011","P011_Record_Role",r"P011_C0[1-5]")]:
        if col in d and d[col].eq("RECOVERED_EXACT_CONDITION").any():
            x=x[~(x.Paper_ID.eq(paper)&x.Condition_ID.str.match(pattern,na=False))]
    if "P008_Record_Role" in x: x=x[~x.P008_Record_Role.eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")]
    if "P013_Record_Role" in d and d.P013_Record_Role.eq("RECOVERED_EXACT_CONDITION").any():
        x=x[~(x.Paper_ID.eq("P013") & ~x.P013_Record_Role.eq("RECOVERED_EXACT_CONDITION"))]
    if "P014_Record_Role" in d and d.P014_Record_Role.eq("RECOVERED_EXACT_CONDITION").any():
        x=x[~(x.Paper_ID.eq("P014") & ~x.P014_Record_Role.eq("RECOVERED_EXACT_CONDITION"))]
    return x

def counts(d):
    x=eligible(d)
    return len(x),x.Effective_TRIP.notna().sum(),x.Effective_TWIP.notna().sum(),x[["Effective_TRIP","Effective_TWIP"]].notna().all(axis=1).sum()

def integrate():
    src=pd.read_csv(SOURCE,low_memory=False); sheets=pd.read_excel(BOOK,sheet_name=None)
    for f in sheets.values():
        if "Paper_ID" in f: assert set(f.Paper_ID.dropna())=={"P014"}
        if "DOI" in f: assert set(f.DOI.dropna())=={DOI}
    study=sheets["P014_Study_Processing"].iloc[0]; states=sheets["P014_Processing_States"].set_index("Processing_State_ID")
    cond=sheets["P014_ML_Conditions"]; stages=sheets["P014_A600_Stages"]
    assert len(cond)==5 and len(stages)==4
    out=src.copy()
    for c in NEW:
        if c not in out: out[c]=pd.NA
    legacy=src[src.Paper_ID.eq("P014")].copy(); assert len(legacy)==5 and legacy.DOI.eq(DOI).all()
    # Explicit source-identity mapping (processing state and annealing temperature), never row order.
    legacy_map={"P014_C01":"P014_MC_ASCAST", "P014_C02":"P014_MC_CR", "P014_C03":"P014_MC_A600",
                "P014_C04":"P014_MC_A650", "P014_C05":"P014_MC_A700"}
    assert set(legacy.Condition_ID)==set(legacy_map) and set(cond.ML_Condition_ID)==set(legacy_map.values())
    original={mc:legacy.set_index("Condition_ID").loc[cid,["TRIP","TWIP"]].tolist() for cid,mc in legacy_map.items()}
    provenance=[]; identities={"Paper_ID","DOI","Source_URL"}
    for sheet,frame in sheets.items():
        for rec in frame.to_dict("records"):
            for feature,value in rec.items():
                if feature in identities or pd.isna(value): continue
                provenance.append({"Paper_ID":"P014","DOI":DOI,"Material_Parent_ID":rec.get("Material_Parent_ID",study.Material_Parent_ID),
                    "Processing_State_ID":rec.get("Processing_State_ID",pd.NA),"ML_Condition_ID":rec.get("ML_Condition_ID",rec.get("Parent_ML_Condition_ID",pd.NA)),
                    "Observation_ID":rec.get("Observation_ID",pd.NA),"Feature_Name":feature,"Recovered_Value":value,
                    "Units":"as named/reported","Evidence_Type":rec.get("Value_Status",rec.get("Target_Status","VERIFIED_WORKBOOK")),
                    "Evidence_Location":rec.get("Evidence_Location",sheet),"Method":rec.get("Method_or_Formula",rec.get("KAM_Status","source-reported")),
                    "Confidence":rec.get("Confidence","High"),"Recovery_Status":"VERIFIED"})
    rows=[]
    for c in cond.to_dict("records"):
        s=states.loc[c["Processing_State_ID"]]; row={k:pd.NA for k in out.columns}; otr,otw=original[c["ML_Condition_ID"]]
        route="Vacuum levitation melting under Ar; remelted 5 times; blocks cut; cold rolled at room temperature from ~5 to ~2.75 mm (~0.05 mm/pass)"
        row.update({"Paper_ID":"P014","DOI":DOI,"Paper_Title":study.Paper_Title,"Condition_ID":c["ML_Condition_ID"],
          "Alloy_ID":"Fe50Mn30Co10Cr10","Original_Composition":study.Nominal_Composition_at_pct,"Nominal_Composition_at_pct":study.Nominal_Composition_at_pct,
          "Composition_basis":"at.% nominal","Composition_Status":study.Composition_Status,"Measured_Composition_at_pct":pd.NA,"Measured_Composition_Status":study.Composition_Status,
          "Fe_at%":50,"Mn_at%":30,"Co_at%":10,"Cr_at%":10,"Processing_route":route,"Cast_method":study.Melting_Route,
          "Cold_rolling_reduction_pct":study.Cold_Roll_Reduction_pct,"Cold_Roll_Reduction_Status":study.Cold_Roll_Reduction_Status,
          "Cold_Roll_Pass_Reduction_mm":study.Cold_Roll_Pass_Reduction_mm,"Remelting_n":study.Remelting_N,
          "Annealing_T_K":pd.NA if pd.isna(c["Anneal_T_C"]) else c["Anneal_T_C"]+273.15,"Annealing_time_min":pd.NA if pd.isna(c["Anneal_T_C"]) else study.Anneal_Time_min,
          "Cooling_route":pd.NA if pd.isna(c["Anneal_T_C"]) else study.Quench,"Test_T_Raw":c["Test_T_Raw"],"Test_T_K":pd.NA,"Test_T_Status":study.Test_T_Status,
          "Strain_rate_s-1":c["Strain_rate_s-1"],"Gauge_length_mm":40,"Gauge_width_mm":8,"Specimen_thickness_mm":1,"Loading_Direction":study.Tensile_Loading_Direction,
          "Grain_size_um":c["Grain_Size_um"],"Grain_size_SD_um":c["Grain_Size_sd_um"],"Initial_FCC_fraction":c["Initial_FCC_fraction"],
          "Initial_HCP_fraction":c["Initial_HCP_fraction"],"Initial_Phase_Status":c["Initial_Phase_Status"],"KAM_mean_deg":c["KAM_mean_deg"],"KAM_Status":s.KAM_Status,
          "Recrystallized_fraction":c["Recrystallized_fraction"],"Recrystallized_Status":s.Recrystallized_Status,
          "Initial_twin_boundary_status":s.Initial_Twin_Descriptor,"Initial_Twin_Origin":s.Initial_Twin_Origin,"Initial_Twin_Target_Safety":s.Initial_Twin_Target_Safety,
          "Processing_TRIP":s.Processing_TRIP,"Processing_TWIP":s.Processing_TWIP,"SFE_mJ_m2":pd.NA,"DeltaG_FCC_HCP_J_mol":pd.NA,
          "YS_MPa":c["YS_MPa"],"YS_error_MPa":c["YS_pm_MPa"],"UTS_MPa":c["UTS_MPa"],"UTS_error_MPa":c["UTS_pm_MPa"],
          "Elongation_pct":c["Fracture_Elongation_pct"],"Elongation_error_pct":c["FE_pm_pct"],"YS_mean":c["YS_MPa"],"YS_uncertainty":c["YS_pm_MPa"],
          "UTS_mean":c["UTS_MPa"],"UTS_uncertainty":c["UTS_pm_MPa"],"TE_mean":c["Fracture_Elongation_pct"],"TE_uncertainty":c["FE_pm_pct"],
          "Replicate_n":c["Tensile_Replicate_n"],"Replicate_ID":pd.NA,"Physical_Batch_ID":pd.NA,"uncertainty_type":c["Uncertainty_Type"],
          "TRIP":pd.NA,"TWIP":pd.NA,"Original_TRIP":otr,"Original_TWIP":otw,"Recovered_TRIP":c["TRIP"],"Recovered_TWIP":c["TWIP"],
          "Effective_TRIP":c["TRIP"],"Effective_TWIP":c["TWIP"],"Slip":c["Slip"],"HDI_Hardening":c["HDI_Hardening"],"P014_Target_Status":c["Target_Status"],
          "Study_Series_ID":c["Study_Series_ID"],"Material_Parent_ID":c["Material_Parent_ID"],"Processing_State_ID":c["Processing_State_ID"],
          "Leakage_Group_Strict":c["Leakage_Group_Strict"],"Leakage_Group_Material":c["Leakage_Group_Material"],"Parent_Experiment_ID":c["ML_Condition_ID"],
          "ML_Condition_ID":c["ML_Condition_ID"],"Parent_ML_Condition_ID":c["ML_Condition_ID"],"Observation_ID":"P014_OBS_CONDITION_"+c["State_Label"].upper().replace("-",""),
          "Data_Origin":"EXPERIMENTAL","Observation_Role":"INDEPENDENT_CONDITION","Independent_ML_sample":True,"Grouping_Confidence":"HIGH","Grouping_Review_Required":0,
          "P014_Record_Role":"RECOVERED_EXACT_CONDITION","Source_File":BOOK.name,"Source_Sheet":"P014_ML_Conditions","Source_location":c["Evidence_Location"],"Label_confidence":c["Confidence"]})
        row["P014_Recovery_Provenance_JSON"]=json.dumps([p for p in provenance if not pd.isna(p["ML_Condition_ID"]) and p["ML_Condition_ID"]==c["ML_Condition_ID"]],default=str)
        rows.append(row)
    for s in stages.to_dict("records"):
        row={k:pd.NA for k in out.columns}; row.update({"Paper_ID":"P014","DOI":DOI,"Paper_Title":study.Paper_Title,"Condition_ID":s["Observation_ID"],
          "Study_Series_ID":study.Study_Series_ID,"Material_Parent_ID":study.Material_Parent_ID,"Processing_State_ID":"P014_PS_A600",
          "Leakage_Group_Strict":study.Study_Series_ID,"Leakage_Group_Material":study.Material_Parent_ID,"Parent_Experiment_ID":"P014_MC_A600",
          "Parent_ML_Condition_ID":"P014_MC_A600","ML_Condition_ID":pd.NA,"Observation_ID":s["Observation_ID"],"Deformation_Stage_ID":s["Observation_ID"],
          "Observation_Role":"REPEATED_STAGE","Independent_ML_sample":False,"Data_Origin":"EXPERIMENTAL","Tensile_Strain_pct":s["Tensile_Strain_pct"],
          "FCC_fraction_at_stage":s["FCC_fraction"],"HCP_fraction_at_condition":s["HCP_fraction"],"TRIP_at_stage":s["TRIP_at_stage"],"TWIP_at_stage":s["TWIP_at_stage"],
          "Slip_at_stage":s["Slip_at_stage"],"HDI_at_stage":s["HDI_at_stage"],"Recovered_TRIP":s["TRIP_at_stage"],"Recovered_TWIP":s["TWIP_at_stage"],
          "Effective_TRIP":s["TRIP_at_stage"],"Effective_TWIP":s["TWIP_at_stage"],"Slip":s["Slip_at_stage"],"Observed_Microstructure":s["Microstructural_Observations"],
          "P014_Record_Role":"RECOVERED_A600_STAGE_CHILD","Source_File":BOOK.name,"Source_Sheet":"P014_A600_Stages","Source_location":s["Evidence_Location"],"Label_confidence":s["Confidence"]})
        rows.append(row)
    out=pd.concat([out,pd.DataFrame(rows,columns=out.columns)],ignore_index=True); validate(src,out); out.to_csv(OUT,index=False)
    hdi=sheets["P014_HDI_Strengthening"].copy()
    hdi["ML_Use_Status"]=hdi.Feature.map(lambda x: "POTENTIAL_TARGET_LEAKAGE_FEATURE" if x=="HDI_strength_contribution" else "REVIEW_BY_STATED_USE_RULE")
    exports={"hierarchy":cond[["Study_Series_ID","Material_Parent_ID","Processing_State_ID","ML_Condition_ID","Independent_ML_sample","Leakage_Group_Strict","Leakage_Group_Material"]],
      "processing_states":sheets["P014_Processing_States"],"a600_stages":stages,"target_evidence":sheets["P014_Target_Evidence"],
      "hdi_strengthening":hdi,"source_consistency_issues":sheets["P014_Source_Consistency"],
      "provenance":pd.DataFrame(provenance),"legacy_mapping":pd.DataFrame([{"Legacy_Condition_ID":cid,"Exact_ML_Condition_ID":mc,"Mapping_Status":"EXACT_IDENTITY_MATCH; LEGACY_RETAINED_EXCLUDED_FROM_INDEPENDENT_COUNT","Original_TRIP":original[mc][0],"Original_TWIP":original[mc][1]} for cid,mc in legacy_map.items()]),
      "correction_decision_ledger":sheets["P014_Integration_Decisions"]}
    for name,frame in exports.items(): frame.to_csv(TABLE/f"p014_recovery_v9_{name}.csv",index=False)
    write_audit(src,out); return src,out

def validate(src,out):
    pd.testing.assert_frame_equal(out.iloc[:len(src)][src.columns].reset_index(drop=True),src,check_dtype=False)
    p=out[out.P014_Record_Role.eq("RECOVERED_EXACT_CONDITION")]; s=out[out.P014_Record_Role.eq("RECOVERED_A600_STAGE_CHILD")]
    assert len(p)==5 and p.Independent_ML_sample.eq(True).all() and len(s)==4 and s.Independent_ML_sample.eq(False).all()
    assert p.Replicate_n.eq(3).all() and p.Replicate_ID.isna().all() and p.Test_T_K.isna().all() and p.Measured_Composition_at_pct.isna().all()

def write_audit(src,out):
    b,a=counts(src),counts(out)
    AUDIT.write_text(f"""# P014 recovery v9 audit

## 1–7. Preservation, hierarchy, mappings, and counts
- recovery_v9 has **{len(out)} rows**. All **{len(src)} recovery_v8 rows** are retained unchanged and all **5 P014 legacy rows** remain present.
- Exactly five primary conditions (`P014_MC_ASCAST`, `P014_MC_CR`, `P014_MC_A600`, `P014_MC_A650`, `P014_MC_A700`) and four correlated A600 children were added. Children are non-independent; tensile n=3 is aggregate metadata and creates no pseudo-replicates.
- Legacy rows map by DOI, processing state and annealing temperature to the five exact conditions. Exact rows replace them only for counting, preventing double counting.
- Independent / usable TRIP / usable TWIP / usable joint: **{b[0]}/{b[1]}/{b[2]}/{b[3]} before → {a[0]}/{a[1]}/{a[2]}/{a[3]} after**.

## 8–18. Chemistry, processing, initial state, and tensile properties
- Chemistry is nominal Fe50Mn30Co10Cr10 at.% only; measured chemistry is NA. Processing preserves vacuum levitation melting under Ar, five melts, block cutting, room-temperature rolling from about 5 to 2.75 mm at about 0.05 mm/pass, and 600/650/700 C, 10 min, water-quenched anneals. The 45% reduction is explicitly `DERIVED_FROM_REPORTED_5_TO_2.75_MM_THICKNESS`.
- CR processing TRIP/TWIP is 1/1 but its later tensile targets remain NA/NA. Pre-test/annealing twins never establish tensile TWIP.
- EBSD initial FCC/HCP is 0.795/0.205, 0.739/0.261, 1/0, 0.999/0.001, and 1/0. A650 retains `TRACE_EBSD_HCP_CONFLICTS_WITH_SINGLE_FCC_TEXT_XRD` rather than erasing the modality conflict.
- Grain sizes +/- uncertainty are 28.03+/-5.12, 0.71+/-0.18, 0.79+/-0.30, 1.10+/-0.57, and 1.16+/-0.60 um. KAM values 0.04/0.80/0.85/0.39/0.30 deg retain direct EBSD-label status. GOS recrystallized fractions are A600 0.102, A650 0.658, A700 0.747; none is fabricated for as-cast/CR.
- Test temperature is raw `Not explicitly specified` and numeric Test_T_K is NA. Table 1 YS/UTS/fracture elongation means and +/- values are separate, `UNKNOWN_REPORTED_PM`, with n=3 and no individual replicate rows.

## 19–25. Targets, chronology, HDI, and gaps
- Only A600 is verified condition-level TRIP=1/TWIP=1 (also Slip=1 and HDI=1). As-cast, CR, A650 and A700 remain NA/NA.
- A600 chronology is initial 0 HCP with pre-existing twins but no TWIP target; 15% HCP=0.184, TRIP=1/TWIP=NA; 30% HCP=0.604 and fracture HCP=0.651, both TRIP=1/TWIP=1 with direct deformation-twin evidence. Early slip+TRIP evolves to TWIP/HDI/dislocation interaction while TRIP tends toward saturation.
- The HDI contribution 631.2 MPa is retained in the strengthening table as `CURRENT_PAPER_FIT_INTERCEPT/REPORTED_CONTRIBUTION` and a `POTENTIAL_TARGET_LEAKAGE_FEATURE`; the 689 MPa YS comparison is outcome-derived. M=3.06 and alpha=0.2 are model inputs; G=76 GPa and k=226 MPa/um^0.5 are reference inputs, not P014 measurements.
- P014 numeric SFE and DeltaG remain NA. Remaining P014 gaps are explicit tensile temperature, measured bulk chemistry, batch/replicate identities, individual replicate values, and the +/- statistic definition.

## 26–31. Completeness and remaining blockers
- Five conditions now have processing, phase, grain size, KAM, mechanics and uncertainty metadata; three annealed states add direct GOS fractions. This is descriptor recovery, not feature engineering.
- Remaining overall P1/P2 blockers are unresolved labels in P014 and other papers, small/imbalanced independent support, predictor leakage eligibility (especially post-loading HDI), computational/experimental separation, sparse descriptors/reference constants, and no final ML-ready target. No ML, derived alloy descriptors, plot digitization, or fabrication occurred.
""",encoding="utf-8")

if __name__=="__main__": integrate()
