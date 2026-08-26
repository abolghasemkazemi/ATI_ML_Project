"""Integrate verified P013 evidence into recovery_v8 without deriving values."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v7.csv"
BOOK = ROOT / "data/interim/manual_recovery/P013_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v8.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P013_RECOVERY_V8_AUDIT.md"
DOI = "10.1016/j.ijplas.2024.104048"
CID = "P013_MC_ASCAST_RT"
NEW = ["P013_Record_Role", "P013_Target_Status", "Test_T_Raw", "Composition_Status",
       "Surface_Preparation", "Specimen_Cutting", "SXRD_Mode", "Beam_Energy_keV",
       "Exposure_s", "Images_per_loading_step", "Beam_Size_um", "Initial_MnO_fraction",
       "Grain_Size_Scope", "HCP_Morphology", "EBSD_Phase_Fraction_Use_Status",
       "Initial_HCP_Status", "Initial_HCP_Origin", "Initial_FCC_lattice_a_A",
       "Initial_HCP_c_over_a", "Initial_HCP_c_over_a_uncertainty", "Approx_Stress_MPa",
       "HCP_fraction_status", "Nearest_SXRD_TRIP_Onset_Stress_MPa",
       "Tensile_TWIP_Onset_Stress_MPa", "Compression_Twinning_Onset_Stress_MPa",
       "Final_InSitu_True_Stress_Approx_MPa", "Final_InSitu_Engineering_Strain_Approx_pct",
       "Mechanism_Phase_Scope", "P013_Recovery_Provenance_JSON"]

def eligible(d):
    x = d[d.Data_Origin.eq("EXPERIMENTAL") & d.Observation_Role.eq("INDEPENDENT_CONDITION")]
    # Apply the established recovery-v7 gates before adding P013's exact-replacement gate.
    if "P012_Record_Role" in d and d.P012_Record_Role.eq("RECOVERED_EXACT_CONDITION").any():
        x=x[~(x.Paper_ID.eq("P012") & x.Condition_ID.isin([f"P012_C0{i}" for i in range(1,7)]))]
    if "P011_Record_Role" in d and d.P011_Record_Role.eq("RECOVERED_EXACT_CONDITION").any():
        x=x[~(x.Paper_ID.eq("P011") & x.Condition_ID.str.match(r"P011_C0[1-5]",na=False))]
    if "P008_Record_Role" in x:
        x=x[~x.P008_Record_Role.eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")]
    if "P013_Record_Role" in d and d.P013_Record_Role.eq("RECOVERED_EXACT_CONDITION").any():
        x=x[~(x.Paper_ID.eq("P013") & ~x.P013_Record_Role.eq("RECOVERED_EXACT_CONDITION"))]
    return x

def counts(d):
    x = eligible(d)
    return (len(x), x.Effective_TRIP.notna().sum(), x.Effective_TWIP.notna().sum(),
            x[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum())

def integrate():
    src = pd.read_csv(SOURCE, low_memory=False)
    sheets = pd.read_excel(BOOK, sheet_name=None)
    for frame in sheets.values():
        if "Paper_ID" in frame: assert set(frame.Paper_ID.dropna()) == {"P013"}
        if "DOI" in frame: assert set(frame.DOI.dropna()) == {DOI}
    c = sheets["P013_Study_Condition"].iloc[0]
    m = sheets["P013_Initial_Microstructure"].iloc[0]
    mech = sheets["P013_Mechanical_Response"].iloc[0]
    target = sheets["P013_Target_Evidence"].iloc[0]
    stages = sheets["P013_Landmark_Observations"]
    assert CID == c.ML_Condition_ID and len(stages) == 5
    out = src.copy()
    for col in NEW:
        if col not in out: out[col] = pd.NA
    legacy = src[src.Paper_ID.eq("P013")]
    assert len(legacy) == 5 and legacy.DOI.eq(DOI).all()
    old_trip, old_twip = legacy.iloc[0][["TRIP", "TWIP"]]
    base = {k: pd.NA for k in out.columns}
    base.update({
        "Paper_ID":"P013", "DOI":DOI, "Paper_Title":c.Paper_Title, "Condition_ID":CID,
        "Alloy_ID":c.Alloy_Label, "Original_Composition":c.Nominal_Composition_at_pct,
        "Nominal_Composition_at_pct":c.Nominal_Composition_at_pct, "Composition_basis":"at.% nominal",
        "Composition_Status":c.Composition_Status, "Fe_at%":50, "Mn_at%":30, "Co_at%":10, "Cr_at%":10,
        "Processing_route":c.Manufacturing_Route, "Cast_method":c.Manufacturing_Route,
        "Test_T_Raw":c.Test_T_Raw, "Test_T_K":pd.NA, "Strain_rate_s-1":c["Strain_Rate_s-1"],
        "Gauge_length_mm":c.Gauge_Length_mm, "Gauge_width_mm":c.Specimen_Width_mm,
        "Specimen_thickness_mm":c.Specimen_Thickness_mm, "Specimen_Cutting":c.Specimen_Cutting,
        "Surface_Preparation":c.Surface_Preparation, "SXRD_Mode":c.SXRD_Mode,
        "Beam_Energy_keV":c.Beam_Energy_keV, "Exposure_s":c.Exposure_s,
        "Images_per_loading_step":c.Images_per_loading_step, "Beam_Size_um":c.Beam_Size_um,
        "Grain_size_um":m.FCC_Grain_Size_mean_um, "Grain_size_SD_um":m.FCC_Grain_Size_sd_um,
        "Grain_Size_Scope":m.Grain_Size_Scope, "HCP_Morphology":m.HCP_Morphology,
        "Initial_HCP_fraction":m.Initial_HCP_fraction_bulk, "Initial_HCP_Status":m.Initial_HCP_fraction_method,
        "Initial_HCP_Origin":"THERMAL_PRE_EXISTING_MARTENSITE", "Initial_FCC_fraction":pd.NA,
        "Initial_MnO_fraction":m.Initial_MnO_fraction, "EBSD_Phase_Fraction_Use_Status":m.EBSD_Phase_Fraction_Use_Status,
        "Initial_Phase_State_Qualitative":m.Initial_Phase_State, "Initial_FCC_lattice_a_A":m.Initial_FCC_lattice_a_A,
        "HCP_lattice_a_XRD_A":m.Initial_HCP_lattice_a_A, "HCP_lattice_c_XRD_A":m.Initial_HCP_lattice_c_A,
        "Initial_HCP_c_over_a":m.Initial_HCP_c_over_a, "Initial_HCP_c_over_a_uncertainty":m.Initial_HCP_c_over_a_uncertainty,
        "SFE_mJ_m2":pd.NA, "DeltaG_FCC_HCP_J_mol":pd.NA, "YS_MPa":mech.Yield_Strength_MPa,
        "UTS_MPa":mech.UTS_MPa, "Elongation_pct":mech.Engineering_Fracture_Elongation_pct,
        "Nearest_SXRD_TRIP_Onset_Stress_MPa":mech.Nearest_SXRD_TRIP_Onset_Stress_MPa,
        "Tensile_TWIP_Onset_Stress_MPa":mech.Tensile_TWIP_Onset_Stress_MPa,
        "Compression_Twinning_Onset_Stress_MPa":mech.Compression_Twinning_Onset_Stress_MPa,
        "Final_InSitu_True_Stress_Approx_MPa":mech.Final_InSitu_True_Stress_Approx_MPa,
        "Final_InSitu_Engineering_Strain_Approx_pct":mech.Final_InSitu_Engineering_Strain_Approx_pct,
        "TRIP":pd.NA, "TWIP":pd.NA, "Original_TRIP":old_trip, "Original_TWIP":old_twip,
        "Recovered_TRIP":1, "Recovered_TWIP":1, "Effective_TRIP":1, "Effective_TWIP":1, "Slip":1,
        "Evidence_TRIP":target.TRIP_Evidence, "Evidence_TWIP":target.TWIP_Evidence,
        "Mechanism_Phase_Scope":target.Mechanism_Phase_Scope, "P013_Target_Status":target.Verification_Status,
        "Study_Series_ID":c.Study_Series_ID, "Material_Parent_ID":c.Material_Parent_ID,
        "Physical_Batch_ID":pd.NA, "Replicate_ID":pd.NA, "Replicate_n":pd.NA,
        "Leakage_Group_Strict":c.Leakage_Group_Strict, "Leakage_Group_Material":c.Leakage_Group_Material,
        "Parent_Experiment_ID":CID, "ML_Condition_ID":CID, "Parent_ML_Condition_ID":CID,
        "Observation_ID":"P013_OBS_CONDITION", "Data_Origin":"EXPERIMENTAL",
        "Observation_Role":"INDEPENDENT_CONDITION", "Independent_ML_sample":True,
        "Grouping_Confidence":"HIGH", "Grouping_Review_Required":0,
        "P013_Record_Role":"RECOVERED_EXACT_CONDITION", "Source_File":BOOK.name,
        "Source_Sheet":"P013_Study_Condition", "Source_location":c.Evidence_Location, "Label_confidence":"High"})
    rows = [base]
    for s in stages.to_dict("records"):
        r = {k: pd.NA for k in out.columns}
        for k in ["Paper_ID","DOI","Paper_Title","Study_Series_ID","Material_Parent_ID","Leakage_Group_Strict","Leakage_Group_Material"]: r[k]=base[k]
        r.update({"Condition_ID":s["Observation_ID"], "Observation_ID":s["Observation_ID"],
                  "Parent_ML_Condition_ID":CID, "Parent_Experiment_ID":CID, "ML_Condition_ID":pd.NA,
                  "Observation_Role":"REPEATED_STAGE", "Independent_ML_sample":False,
                  "Data_Origin":"EXPERIMENTAL", "Deformation_Stage_ID":s["Observation_ID"],
                  "Approx_Stress_MPa":s["Approx_Stress_MPa"], "HCP_fraction_at_condition":s["HCP_fraction"],
                  "HCP_fraction_status":s["HCP_fraction_status"], "Effective_TRIP":s["TRIP_at_observation"],
                  "Effective_TWIP":s["TWIP_at_observation"], "Recovered_TRIP":s["TRIP_at_observation"],
                  "Recovered_TWIP":s["TWIP_at_observation"], "Slip":s["Slip_at_observation"],
                  "Initial_HCP_c_over_a":s["HCP_c_over_a"], "Initial_HCP_c_over_a_uncertainty":s["HCP_c_over_a_uncertainty"],
                  "Initial_FCC_lattice_a_A":s["FCC_lattice_a_A"], "HCP_lattice_a_XRD_A":s["HCP_lattice_a_A"],
                  "HCP_lattice_c_XRD_A":s["HCP_lattice_c_A"], "Mechanism_Phase_Scope":target.Mechanism_Phase_Scope,
                  "Dominant_mechanism":s["Mechanism_Event"], "Initial_HCP_Origin":"THERMAL_PRE_EXISTING_MARTENSITE" if s["Observation_ID"]=="P013_OBS_0MPa" else pd.NA,
                  "P013_Record_Role":"RECOVERED_LANDMARK_CHILD", "Source_File":BOOK.name,
                  "Source_Sheet":"P013_Landmark_Observations", "Source_location":s["Evidence_Location"],
                  "Label_confidence":s["Confidence"], "Grouping_Confidence":"HIGH"})
        rows.append(r)
    # Provenance covers every non-empty workbook scientific cell, retaining sheet location and method/status context.
    prov=[]
    identities={"Paper_ID","DOI","ML_Condition_ID","Parent_ML_Condition_ID","Observation_ID","Source_URL"}
    for sheet, frame in sheets.items():
        for rec in frame.to_dict("records"):
            for feature,value in rec.items():
                if feature in identities or pd.isna(value): continue
                prov.append({"Paper_ID":"P013","DOI":DOI,"Material_Parent_ID":rec.get("Material_Parent_ID",c.Material_Parent_ID),
                    "ML_Condition_ID":rec.get("ML_Condition_ID",rec.get("Parent_ML_Condition_ID",CID)),
                    "Observation_ID":rec.get("Observation_ID",pd.NA),"Feature_Name":feature,"Recovered_Value":value,
                    "Units":"as named/reported","Evidence_Type":rec.get("Value_Status",rec.get("Verification_Status","VERIFIED_WORKBOOK")),
                    "Evidence_Location":rec.get("Evidence_Location",sheet),"Method":rec.get("Method_or_Source",rec.get("Initial_HCP_fraction_method","source-reported")),
                    "Confidence":rec.get("Confidence","High"),"Recovery_Status":"VERIFIED"})
    rows[0]["P013_Recovery_Provenance_JSON"] = json.dumps([p for p in prov if p["ML_Condition_ID"]==CID], default=str)
    out = pd.concat([out, pd.DataFrame(rows, columns=out.columns)], ignore_index=True)
    validate(src,out)
    out.to_csv(OUT,index=False)
    sheets["P013_Stage_Intervals"].to_csv(TABLE/"p013_recovery_v8_stage_intervals.csv",index=False)
    stages.to_csv(TABLE/"p013_recovery_v8_landmark_observations.csv",index=False)
    sheets["P013_Phase_Physics"].to_csv(TABLE/"p013_recovery_v8_phase_physics.csv",index=False)
    sheets["P013_Target_Evidence"].to_csv(TABLE/"p013_recovery_v8_target_evidence.csv",index=False)
    sheets["P013_Integration_Decisions"].to_csv(TABLE/"p013_recovery_v8_correction_decision_ledger.csv",index=False)
    pd.DataFrame(prov).to_csv(TABLE/"p013_recovery_v8_provenance.csv",index=False)
    pd.DataFrame([{"Legacy_Condition_ID":x,"Exact_ML_Condition_ID":CID,"Mapping_Status":"LEGACY_COLLAPSED; RETAINED; EXCLUDED_FROM_INDEPENDENT_COUNT","Original_TRIP":t,"Original_TWIP":w}
                  for x,t,w in legacy[["Condition_ID","TRIP","TWIP"]].itertuples(index=False)]).to_csv(TABLE/"p013_recovery_v8_legacy_mapping.csv",index=False)
    pd.DataFrame([{"Study_Series_ID":c.Study_Series_ID,"Material_Parent_ID":c.Material_Parent_ID,"ML_Condition_ID":CID,
                   "Independent_ML_sample":True,"Leakage_Group_Strict":c.Leakage_Group_Strict,"Leakage_Group_Material":c.Leakage_Group_Material,
                   "Physical_Batch_ID":pd.NA,"Replicate_ID":pd.NA,"Replicate_n":pd.NA}]).to_csv(TABLE/"p013_recovery_v8_hierarchy.csv",index=False)
    write_audit(src,out); return src,out

def validate(src,out):
    pd.testing.assert_frame_equal(out.iloc[:len(src)][src.columns].reset_index(drop=True),src,check_dtype=False)
    p=out[out.P013_Record_Role.eq("RECOVERED_EXACT_CONDITION")]; s=out[out.P013_Record_Role.eq("RECOVERED_LANDMARK_CHILD")]
    assert len(p)==1 and p.Independent_ML_sample.eq(True).all() and tuple(p.iloc[0][["Effective_TRIP","Effective_TWIP","Slip"]])==(1,1,1)
    assert len(s)==5 and s.Independent_ML_sample.eq(False).all() and s.ML_Condition_ID.isna().all()
    assert not out.Observation_ID.isin(["P013_STAGE_I","P013_STAGE_II","P013_STAGE_III","P013_STAGE_IV"]).any()
    assert pd.isna(p.iloc[0].Initial_FCC_fraction) and p.iloc[0].Initial_HCP_fraction==.33 and p.iloc[0].Initial_MnO_fraction==.01

def write_audit(src,out):
    b,a=counts(src),counts(out)
    AUDIT.write_text(f"""# P013 recovery v8 audit

## 1–7. Rows, hierarchy, mappings, and count impact
- Total recovery_v8 rows: **{len(out)}**; all **{len(src)}** recovery_v7 rows are byte-value/order preserved, including **5** P013 legacy rows.
- One exact independent condition (`{CID}`) and exactly five non-independent landmark children were appended. The four interval definitions exist only in the supporting table. All legacy rows are `LEGACY_COLLAPSED`, map scientifically to the exact condition, and are excluded from independent counting.
- Independent / usable TRIP / usable TWIP / usable joint counts: **{b[0]}/{b[1]}/{b[2]}/{b[3]} before → {a[0]}/{a[1]}/{a[2]}/{a[3]} after**.

## 8–17. Initial state, mechanics, chronology, and mechanism scope
- Canonical initial bulk HCP is **~0.33**, by transmission SXRD Rietveld; EBSD/OM phase fraction is rejected because polishing can induce surface TRIP. It is explicitly thermal/pre-existing HCP, distinct from deformation-induced growth to **~0.77** at fracture. FCC is NA rather than an unsupported 0.67 complement; MnO ~0.01 is separate.
- Gamma-FCC grain size is **40.2 +/- 10.7 um**; plate-like HCP remains qualitative. Measured engineering YS/UTS/elongation are **319 MPa / 726 MPa / 36%**. SXRD TRIP onset ~250 MPa and final true stress ~950 MPa remain distinct.
- Chronology is elastic observable-bulk Stage I; TRIP+slip Stage II; epsilon-HCP tensile TWIP from ~530 MPa Stage III; epsilon-HCP compression TWIP from ~655 MPa Stage IV. Stage negatives never become condition negatives. Mechanism scope is gamma-FCC to epsilon-HCP TRIP and epsilon-HCP TWIP, not gamma-FCC twinning.

## 18–22. Physics and remaining P013 gaps
- Phase-specific gamma-FCC dislocation density (~1.4e14 to ~8.2e14 m^-2), HCP slip modes, phase load partitioning, phase-average elastic properties, reflection-specific moduli, lattice parameters, and strengthening terms are retained in the phase-physics table. Reflection and phase-average moduli are not interchangeable.
- Lattice friction 179 MPa remains `SECONDARY_REFERENCE_INPUT`; calculated YS 321 +/- 31 MPa remains `CURRENT_PAPER_CALCULATED`, separate from measured 319 MPa and flagged for later leakage review.
- P013 SFE and DeltaG remain NA. Other gaps are measured bulk chemistry, exact RT Kelvin, physical batch, tensile replicate count/identity, numeric HCP lath size, and undigitized intermediate SXRD quantities.

## 23–28. Target availability, leakage, and overall blockers
- Effective condition targets are verified TRIP=1/TWIP=1/Slip=1; original legacy targets remain untouched. The exact condition adds one usable joint condition and children add none.
- Leakage audit: strict/material groups are explicit; all stages share their parent, intervals and ten-image loading acquisitions are metadata only, final/mechanical/mechanism physics remain outcome fields requiring predictor-eligibility review, and legacy/exact representations cannot double-count.
- Remaining P1/P2 blockers: small/imbalanced independent support, other-paper target review, computational/experimental separation, prediction-time leakage, sparse grain/phase/SFE/DeltaG coverage, empty traceable descriptor constants, and no final ML-ready target. No ML, feature engineering, derived descriptor, normalization, digitization, or fabrication occurred.
""",encoding="utf-8")

if __name__ == "__main__": integrate()
