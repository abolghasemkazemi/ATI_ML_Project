"""Build recovery_v5 by appending verified P010 conditions and stage evidence."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v4.csv"
BOOK = ROOT / "data/interim/manual_recovery/P010_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v5.csv"
PROV = ROOT / "reports/tables/p010_recovery_v5_provenance.csv"
CORR = ROOT / "reports/tables/p010_recovery_v5_corrections.csv"
AUDIT = ROOT / "reports/P010_RECOVERY_V5_AUDIT.md"
DOI = "10.1103/PhysRevMaterials.4.033601"
TITLE = "Role of magnetic ordering for the design of quinary TWIP-TRIP high entropy alloys"

NEW_FIELDS = [
    "Independent_ML_sample", "Nominal_Composition_at_pct", "Measured_Composition_Status",
    "Cr_at%_uncertainty", "Mn_at%_uncertainty", "Fe_at%_uncertainty",
    "Co_at%_uncertainty", "Ni_at%_uncertainty", "Recovered_Test_T_Reported",
    "Recovered_Test_T_Status", "Initial_Phase_State_Qualitative", "Initial_Phase_Status",
    "Magnetic_transition_T_K", "Magnetic_transition_Status", "Low_T_Magnetic_Behavior",
    "Low_T_Magnetic_Behavior_T_K", "Computational_Magnetic_States", "PM_Model",
    "AFM_Model", "Computational_SFE_Scope", "SFE_Relative_Trend", "Finite_T_SFE_Excitations_Status",
    "P010_Record_Role", "P010_Recovery_Provenance_JSON",
]


def independent(df):
    excluded = (df.P008_Record_Role.eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")
                if "P008_Record_Role" in df else pd.Series(False, index=df.index))
    return df[df.Data_Origin.eq("EXPERIMENTAL") & df.Observation_Role.eq("INDEPENDENT_CONDITION") & ~excluded]


def counts(df):
    d = independent(df)
    return (len(d), d.Effective_TRIP.notna().sum(), d.Effective_TWIP.notna().sum(),
            d[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum())


def integrate():
    source = pd.read_csv(SOURCE, low_memory=False)
    sheets = pd.read_excel(BOOK, sheet_name=None)
    cond, stages = sheets["P010_Conditions"], sheets["P010_Stage_Observations"]
    assert set(cond.Paper_ID) == {"P010"} and set(cond.DOI) == {DOI}
    assert len(cond) == 3 and len(stages) == 6
    out = source.copy()
    for field in NEW_FIELDS:
        if field not in out:
            out[field] = pd.NA
    provenance, rows = [], []

    def add_prov(cid, oid, feature, value, units, evidence, location, confidence, status="VERIFIED"):
        if pd.notna(value):
            provenance.append({"Paper_ID":"P010", "DOI":DOI, "ML_Condition_ID":cid,
                "Observation_ID":oid, "Feature_Name":feature, "Recovered_Value":value,
                "Units":units, "Evidence_Type":evidence, "Evidence_Location":location,
                "Confidence":confidence, "Recovery_Status":status})

    physics = sheets["P010_Physics_Magnetism"]
    trends = {"Alloy I":"close to reference in PM and AFM", "Alloy II":"close to reference in PM; higher than reference in AFM",
              "Alloy III":"slightly higher than reference in PM and AFM; below Cantor alloy"}
    for c in cond.to_dict("records"):
        cid = c["Proposed_ML_Condition_ID"]; alloy = c["Alloy_Label"]
        row = {k:pd.NA for k in out.columns}
        row.update({"Paper_ID":"P010", "DOI":DOI, "Paper_Title":TITLE, "Condition_ID":cid,
            "Alloy_ID":alloy, "Original_Composition":c["Measured_Composition_at_pct"],
            "Composition_basis":"at.% measured wet chemistry", "Nominal_Composition_at_pct":c["Nominal_Composition_at_pct"],
            "Measured_Composition_Status":c["Composition_Status"], "Cr_at%":c["Cr_at_pct"], "Mn_at%":c["Mn_at_pct"],
            "Fe_at%":c["Fe_at_pct"], "Co_at%":c["Co_at_pct"], "Ni_at%":c["Ni_at_pct"],
            "Cr_at%_uncertainty":c["Cr_err"], "Mn_at%_uncertainty":c["Mn_err"], "Fe_at%_uncertainty":c["Fe_err"],
            "Co_at%_uncertainty":c["Co_err"], "Ni_at%_uncertainty":c["Ni_err"],
            "Processing_route":c["Processing_Route"], "Cast_method":"vacuum induction casting",
            "Hot_rolling_T_K":c["Hot_rolling_T_C"] + 273.15, "Hot_rolling_reduction_pct":c["Hot_rolling_reduction_pct"],
            "Homogenization_T_K":c["Homogenization_T_C"] + 273.15, "Homogenization_time_h":c["Homogenization_time_h"],
            "Cooling_route":c["Cooling_Route"], "Test_T_K":pd.NA, "Recovered_Test_T_Reported":c["Test_T_reported"],
            "Recovered_Test_T_Status":c["Test_T_Status"], "Strain_rate_s-1":c["Strain_rate_s-1"],
            "Gauge_length_mm":c["Gauge_length_mm"], "Gauge_width_mm":c["Gauge_width_mm"],
            "Specimen_thickness_mm":c["Thickness_mm"], "Initial_Phase_State_Qualitative":c["Initial_Phase_State"],
            "Initial_Phase_Status":c["Initial_Phase_Status"], "Initial_FCC_fraction":pd.NA, "Initial_HCP_fraction":pd.NA,
            "SFE_mJ_m2":pd.NA, "SFE_method":"ab-initio EMTO / CPA / AIM1", "Computational_SFE_Scope":"PM or AFM",
            "SFE_Relative_Trend":trends[alloy], "Finite_T_SFE_Excitations_Status":"NOT_EXPLICITLY_INCLUDED_IN_SCREENING",
            "Magnetic_transition_T_K":c["Magnetic_transition_T_K"], "Magnetic_transition_Status":c["Magnetic_transition_Status"],
            "Low_T_Magnetic_Behavior":"antiferromagnet-like M-H behavior", "Low_T_Magnetic_Behavior_T_K":5,
            "Computational_Magnetic_States":"PM; AFM", "PM_Model":"DLM + CPA", "AFM_Model":"ordered magnetic configuration used in calculations",
            "TRIP":pd.NA, "TWIP":pd.NA, "Recovered_TRIP":c["TRIP"], "Recovered_TWIP":c["TWIP"],
            "Effective_TRIP":c["TRIP"], "Effective_TWIP":c["TWIP"], "Slip":c["Slip"],
            "Dominant_mechanism":c["Dominant_Mechanism"], "Evidence_TRIP":sheets["P010_Target_Evidence"].set_index("ML_Condition_ID").loc[cid,"TRIP_Evidence"],
            "Evidence_TWIP":sheets["P010_Target_Evidence"].set_index("ML_Condition_ID").loc[cid,"TWIP_Evidence"],
            "Source_location":c["Evidence_Location"], "Label_confidence":c["Confidence"],
            "Study_Series_ID":"P010_SERIES01", "Material_Parent_ID":c["Material_Parent_ID"],
            "Physical_Batch_ID":pd.NA, "Replicate_ID":pd.NA, "Leakage_Group_Strict":"P010_SERIES01",
            "Leakage_Group_Material":c["Material_Parent_ID"], "Parent_Experiment_ID":cid, "ML_Condition_ID":cid,
            "Parent_ML_Condition_ID":cid, "Observation_ID":f"P010_OBS_{alloy.replace(' ','')}_condition",
            "Data_Origin":"EXPERIMENTAL", "Observation_Role":"INDEPENDENT_CONDITION", "Independent_ML_sample":True,
            "Grouping_Confidence":"HIGH", "Grouping_Review_Required":0, "P010_Record_Role":"RECOVERED_EXACT_CONDITION",
            "Source_File":BOOK.name, "Source_Sheet":"P010_Conditions"})
        oid=row["Observation_ID"]
        for f,u in [("Cr_at%","at.%"),("Mn_at%","at.%"),("Fe_at%","at.%"),("Co_at%","at.%"),("Ni_at%","at.%"),
                    ("Effective_TRIP","binary"),("Effective_TWIP","binary"),("Magnetic_transition_T_K","K"),
                    ("Recovered_Test_T_Reported","source text"),("Initial_Phase_State_Qualitative","categorical"),("SFE_Relative_Trend","qualitative")]:
            add_prov(cid,oid,f,row[f],u,"VERIFIED_WORKBOOK",c["Evidence_Location"],c["Confidence"])
        for el in ["Cr","Mn","Fe","Co","Ni"]: add_prov(cid,oid,f"{el}_at%_uncertainty",row[f"{el}_at%_uncertainty"],"at.%","WET_CHEMISTRY_REPORTED_PM","Table I",c["Confidence"])
        row["P010_Recovery_Provenance_JSON"] = json.dumps([p for p in provenance if p["ML_Condition_ID"]==cid], default=str)
        rows.append(row)

    parents={r["ML_Condition_ID"]:r for r in rows}
    for s in stages.to_dict("records"):
        cid=s["Parent_ML_Condition_ID"]; p=parents[cid]; row={k:pd.NA for k in out.columns}
        row.update({k:p[k] for k in ["Paper_ID","DOI","Paper_Title","Alloy_ID","Study_Series_ID","Material_Parent_ID","Leakage_Group_Strict","Leakage_Group_Material"]})
        row.update({"Condition_ID":s["Observation_ID"], "Observation_ID":s["Observation_ID"], "ML_Condition_ID":pd.NA,
            "Parent_ML_Condition_ID":cid, "Parent_Experiment_ID":cid, "Observation_Role":"REPEATED_STAGE",
            "Independent_ML_sample":False, "Data_Origin":"EXPERIMENTAL", "Local_strain":s["Local_strain_pct"]/100,
            "Deformation_stage":f"approximately {s['Local_strain_pct']}% local strain", "HCP_fraction_at_condition":s["HCP_fraction"],
            "Twin_fraction_or_Sigma3":s["Twin_fraction"], "Recovered_TRIP":s["TRIP_at_stage"], "Recovered_TWIP":s["TWIP_at_stage"],
            "Effective_TRIP":s["TRIP_at_stage"], "Effective_TWIP":s["TWIP_at_stage"], "Slip":s["Slip_at_stage"],
            "Dominant_mechanism":s["Dominant_or_observed_behavior"], "Source_location":s["Evidence_Location"],
            "Label_confidence":s["Confidence"], "P010_Record_Role":"RECOVERED_STAGE_CHILD", "Source_File":BOOK.name,
            "Source_Sheet":"P010_Stage_Observations", "Deformation_Stage_ID":s["Observation_ID"], "Grouping_Confidence":"HIGH"})
        for f,u in [("Local_strain","fraction"),("HCP_fraction_at_condition","fraction"),("Twin_fraction_or_Sigma3","fraction"),
                    ("Effective_TRIP","binary"),("Effective_TWIP","binary")]:
            add_prov(cid,s["Observation_ID"],f,row[f],u,s["Evidence_Type"],s["Evidence_Location"],s["Confidence"])
        rows.append(row)

    out=pd.concat([out,pd.DataFrame(rows,columns=out.columns)],ignore_index=True)
    validate(source,out)
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(out.to_csv(index=False),encoding="utf-8")
    pd.DataFrame(provenance).to_csv(PROV,index=False)
    corrections=pd.DataFrame([
        ["P010_MC_AlloyIII","TRIP",0,1,"1.4 vol.% deformation-induced HCP at ~80% local strain"],
        ["P010_MC_AlloyIII","TWIP",0,1,"23.4% twins plus TEM/STEM/SADP confirmation"],
        ["P010_MC_AlloyIII","Dominant_mechanism","Stable FCC / planar-slip-dominant","TWIP-dominant + minor TRIP + slip","effective interpretation"],
        ["P010_OBS_AlloyI_eps20","TWIP",pd.NA,pd.NA,"twin-like contrast insufficient; verified at 60%"],
        ["P010_MC_AlloyII","TRIP",0,0,"explicit high-strain negative phase evidence"],
        ["P010","Initial phase fractions",pd.NA,pd.NA,"qualitative identity does not justify fractions"],
        ["P010","Absolute SFE",pd.NA,pd.NA,"supplemental method-specific values unavailable"],
    ],columns=["Record_ID","Feature_Name","Original_Value","Effective_Value","Reason"])
    corrections.to_csv(CORR,index=False)
    write_audit(source,out)
    return source,out


def validate(source,out):
    pd.testing.assert_frame_equal(out.iloc[:len(source)][source.columns].reset_index(drop=True),source,check_dtype=False)
    p=out[out.P010_Record_Role.eq("RECOVERED_EXACT_CONDITION")]
    s=out[out.P010_Record_Role.eq("RECOVERED_STAGE_CHILD")]
    assert len(p)==3 and p.ML_Condition_ID.nunique()==3 and len(s)==6
    assert (~s.Independent_ML_sample.astype(bool)).all() and set(s.Leakage_Group_Strict)=={"P010_SERIES01"}
    expected={"P010_MC_AlloyI":(1,1),"P010_MC_AlloyII":(0,1),"P010_MC_AlloyIII":(1,1)}
    for cid,x in expected.items(): assert tuple(p.set_index("ML_Condition_ID").loc[cid,["Effective_TRIP","Effective_TWIP"]])==x
    assert p[["TRIP","TWIP"]].isna().all().all() and p[["Initial_FCC_fraction","Initial_HCP_fraction","SFE_mJ_m2"]].isna().all().all()
    legacy=out[out.Condition_ID.eq("P010_C03")].iloc[0]; assert (legacy.TRIP,legacy.TWIP)==(0,0)
    hi=s.set_index("Observation_ID"); assert hi.loc["P010_OBS_AlloyIII_eps80","HCP_fraction_at_condition"]==.014
    assert hi.loc["P010_OBS_AlloyIII_eps80","Twin_fraction_or_Sigma3"]==.234


def write_audit(source,out):
    b,a=counts(source),counts(out)
    AUDIT.write_text(f"""# P010 recovery v5 audit

## Preservation and hierarchy
- recovery_v5 total row count: **{len(out)}** ({len(source)} unchanged recovery_v4 rows plus 3 exact conditions and 6 correlated stages).
- P010 uses `P010_SERIES01`, three alloy-specific material parents, **3 independent conditions**, and **6 `REPEATED_STAGE` non-independent children**. Every child retains its parent's strict and material leakage groups.
- Physical batch and replicate IDs remain NA. Measured wet chemistry and element-wise uncertainty are stored separately from nominal chemistry and were not normalized.

## Targets and counts
| Metric | recovery_v4 | recovery_v5 |
|---|---:|---:|
| Independent experimental conditions | {b[0]} | {a[0]} |
| TRIP usable | {b[1]} | {a[1]} |
| TWIP usable | {b[2]} | {a[2]} |
| Joint usable | {b[3]} | {a[3]} |

P010 effective targets are Alloy I 1/1, Alloy II 0/1, and Alloy III 1/1. The legacy Alloy III 0/0 remains untouched; the effective correction adds two positive usable targets and changes its effective interpretation to TWIP-dominant + minor TRIP + slip. Stage fractions remain outcome evidence, not independent conditions.

## Scientific recovery and gaps
- Approximate magnetization transitions (160/190/80 K) retain `APPROX_EXPERIMENTAL_MAGNETIZATION_TRANSITION`; 5 K antiferromagnet-like behavior is separate and is not a room-temperature AFM label. Tensile temperature remains raw `ROOM_TEMPERATURE_REPORTED`, not an exact Kelvin value.
- Absolute SFE, YS, UTS, elongation, grain size, and exact initial FCC/HCP fractions remain NA. Computational PM/AFM methods and qualitative relative SFE trends are separate from experimental finite-temperature SFE.
- Remaining blockers: Supplemental Figs. S2/S4 and method-specific supplemental SFE values; exact condition grain sizes; source-supported batch/replicate identities. No NA was converted to zero except Alloy II stage HCP/TRIP, supported by explicit negative high-strain evidence.

## Provenance and leakage checks
`reports/tables/p010_recovery_v5_provenance.csv` records paper, DOI, condition, observation, feature, value, units, evidence type/location, confidence, and status. `reports/tables/p010_recovery_v5_corrections.csv` records all requested corrections and non-inference rules. No ML, feature engineering, descriptor calculation, figure digitization, normalization, or fabrication was performed.
""",encoding="utf-8")


if __name__ == "__main__": integrate()
