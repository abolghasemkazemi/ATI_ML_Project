"""Integrate the verified P008 workbook into recovery_v4 without inference."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v3.csv"
BOOK = ROOT / "data/interim/manual_recovery/P008_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v4.csv"
PROV = ROOT / "reports/tables/p008_recovery_v4_provenance.csv"
HIER = ROOT / "reports/tables/p008_recovery_v4_hierarchy.csv"
AUX = ROOT / "reports/tables/p008_recovery_v4_aux_n_series.csv"
CORR = ROOT / "reports/tables/p008_recovery_v4_corrections.csv"
AUDIT = ROOT / "reports/P008_RECOVERY_V4_AUDIT.md"

EXPECTED_DOI = "10.1016/j.ijplas.2021.102965"
EXPECTED_TITLE = "Multi-heterostructure and mechanical properties of N-doped FeMnCoCr high entropy alloy"

FIELDS = [
    "P008_Record_Role", "P008_Legacy_Mapping_Status", "P008_Source_State",
    "Recovered_Bulk_Composition_at_pct", "Recovered_Composition_Status",
    "Recovered_Processing_route", "Recovered_Test_T_Reported", "Recovered_Test_T_Status",
    "Recovered_Grain_size_scope", "Recovered_Grain_size_status",
    "Recovered_Initial_HCP_status", "Initial_BCC_alpha_martensite_fraction",
    "Initial_BCC_alpha_martensite_status", "Recovered_Recrystallized_fraction_status",
    "Recovered_YS_status", "Recovered_UTS_status", "Recovered_Uniform_elongation_status",
    "SFE_scope", "SFE_value_alloy_level_mJ_m2", "SFE_status", "SFE_source_provenance",
    "Alpha_lath_thickness", "Alpha_lath_spacing", "Recovery_twin_fraction",
    "Recovery_twin_thickness", "Recovery_twin_spacing_observed",
    "Recovery_twin_spacing_fraction_input_nm", "Deformation_twin_width",
    "Deformation_twin_spacing", "Precipitate_type", "APT_local_composition",
    "EDS_local_composition", "P008_Recovery_Provenance_JSON",
]


def _missing(v):
    return pd.isna(v) or v == ""


def integrate():
    source = pd.read_csv(SOURCE)
    sheets = pd.read_excel(BOOK, sheet_name=None)
    cond = sheets["P008_Conditions"]
    # Fail closed before touching output files.
    assert set(cond.Paper_ID) == {"P008"}, "P008 Paper_ID mismatch"
    assert set(cond.DOI) == {EXPECTED_DOI}, "P008 DOI mismatch"
    assert len(cond) == 6 and cond.Proposed_ML_Condition_ID.is_unique
    out = source.copy()
    for f in FIELDS:
        if f not in out:
            out[f] = pd.NA

    c01 = out.index[out.Condition_ID.eq("P008_C01")][0]
    out.at[c01, "P008_Record_Role"] = "LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT"
    out.at[c01, "P008_Legacy_Mapping_Status"] = "MANUAL_IDENTITY_REVIEW"

    provenance = []
    exact_rows = []
    for rec in cond.to_dict("records"):
        cid = rec["Proposed_ML_Condition_ID"]
        if cid == "P008_MC_N2p6_PC":
            i = out.index[out.Condition_ID.eq("P008_C02")][0]
            out.at[i, "ML_Condition_ID"] = cid
            out.at[i, "P008_Record_Role"] = "EXACT_CONDITION_LEGACY_MAPPED"
            out.at[i, "P008_Legacy_Mapping_Status"] = "VERIFIED_EXACT_MATCH"
        else:
            row = {c: pd.NA for c in out.columns}
            row.update({
                "Paper_ID": "P008", "DOI": EXPECTED_DOI, "Paper_Title": EXPECTED_TITLE,
                "Condition_ID": cid, "Observation_ID": f"P008_OBS_{cid.removeprefix('P008_MC_')}",
                "ML_Condition_ID": cid, "Parent_ML_Condition_ID": cid,
                "Data_Origin": "EXPERIMENTAL", "Observation_Role": "INDEPENDENT_CONDITION",
                "Row_Type": "Experimental", "Row_Role": "EXPERIMENTAL_INDEPENDENT",
                "P008_Record_Role": "EXACT_CONDITION_RECOVERED", "P008_Legacy_Mapping_Status": "NEW_EXACT_CONDITION",
                "Grouping_Review_Required": 0, "Grouping_Confidence": rec["Confidence"],
                "Source_File": BOOK.name, "Source_Sheet": "P008_Conditions",
            })
            exact_rows.append(row)
            i = len(out) + len(exact_rows) - 1
        # Applied after append below through a shared update dictionary.
        target = out.loc[i].to_dict() if i < len(out) else exact_rows[-1]
        updates = {
            "Study_Series_ID": "P008_SERIES01", "Material_Parent_ID": rec["Material_Parent_ID"],
            "Leakage_Group_Strict": "P008_SERIES01", "Leakage_Group_Material": rec["Material_Parent_ID"],
            "Physical_Batch_ID": pd.NA, "Replicate_ID": pd.NA,
            "P008_Source_State": rec["State"], "Recovered_Bulk_Composition_at_pct": rec["Bulk_Composition_at_pct"],
            "Recovered_Composition_Status": rec["Composition_Status"], "Recovered_Processing_route": rec["Upstream_Processing"],
            "Recovered_Test_T_Reported": rec["Test_T_Reported"], "Recovered_Test_T_Status": "ROOM_TEMPERATURE_REPORTED",
            "Recovered_Grain_size_um": rec["Grain_size_value_um"],
            "Recovered_Grain_size_scope": rec["Grain_size_scope"], "Recovered_Grain_size_status": rec["Grain_size_description"],
            "Recovered_Initial_HCP_fraction": rec["Initial_HCP_fraction"], "Recovered_Initial_HCP_status": rec["Initial_HCP_Status"],
            "Initial_BCC_alpha_martensite_fraction": rec["Initial_alpha_martensite_fraction"],
            "Initial_BCC_alpha_martensite_status": rec["Initial_alpha_Status"],
            "Recovered_Recrystallized_fraction": rec["Recrystallized_fraction"],
            "Recovered_Recrystallized_fraction_status": rec["Recrystallized_fraction_Status"],
            "Recovered_YS_MPa": rec["YS_MPa"], "Recovered_YS_status": rec["YS_Status"],
            "Recovered_UTS_MPa": rec["UTS_MPa"], "Recovered_UTS_status": rec["UTS_Status"],
            "Recovered_Uniform_elongation_pct": rec["Uniform_elongation_pct"],
            "Recovered_Uniform_elongation_status": rec["Uniform_elongation_Status"],
            "Recovered_TRIP": rec["TRIP"], "Recovered_TWIP": rec["TWIP"],
            "Effective_TRIP": rec["TRIP"], "Effective_TWIP": rec["TWIP"],
        }
        # Annealing applies only to PC/FC; raw RT is deliberately not converted to Test_T_K.
        if cid != "P008_MC_N2p6_PC":
            updates["Strain_rate_s-1"] = rec["Strain_rate_s-1"]
        if rec["State"] != "HOMO" and cid != "P008_MC_N2p6_PC":
            updates.update({"Cold_rolling_reduction_pct": rec["Cold_rolling_reduction_pct"],
                            "Annealing_T_K": rec["Annealing_T_C"] + 273.15,
                            "Annealing_time_min": rec["Annealing_time_min"]})
        if rec["Alloy_Label"] == "N2.6":
            updates.update({"SFE_scope": "ALLOY_LEVEL", "SFE_value_alloy_level_mJ_m2": 26,
                            "SFE_status": "CURRENT_STUDY_ALLOY_LEVEL", "SFE_source_provenance": "TEM; p. 13; state not specified"})
        else:
            updates.update({"SFE_scope": "ALLOY_LEVEL", "SFE_value_alloy_level_mJ_m2": 6.5,
                            "SFE_status": "SECONDARY_REFERENCE", "SFE_source_provenance": "Su et al. 2019 cited by P008; p. 13"})
        if i < len(out):
            for k, v in updates.items(): out.at[i, k] = v
        else:
            target.update(updates)
        exact_rows[-1] = target if i >= len(out) else exact_rows[-1] if exact_rows else target
        for k, v in updates.items():
            if not _missing(v):
                original = pd.NA
                if cid == "P008_MC_N2p6_PC" and k in source.columns:
                    original = source.loc[source.Condition_ID.eq("P008_C02"), k].iloc[0]
                provenance.append({"Paper_ID":"P008", "DOI":EXPECTED_DOI, "ML_Condition_ID":cid,
                    "Feature_Name":k, "Original_Value":original, "Recovered_Value":v,
                    "Units":"source/schema units", "Evidence_Type":"VERIFIED_WORKBOOK",
                    "Evidence_Location":rec["Evidence_Location"], "Page_Figure_Section":rec["Evidence_Location"],
                    "Extraction_Method":"Verified direct source extraction", "Confidence":rec["Confidence"],
                    "Recovery_Status":"VERIFIED"})

    out = pd.concat([out, pd.DataFrame(exact_rows, columns=out.columns)], ignore_index=True)
    # Store detailed N2.6-PC physics once, not duplicated across conditions.
    pc = out.index[out.ML_Condition_ID.eq("P008_MC_N2p6_PC")][0]
    physics = sheets["P008_Physics_Provenance"]
    fmap = {"Alpha_lath_thickness":"Alpha_lath_thickness", "Alpha_lath_spacing":"Alpha_lath_spacing",
            "Recovery_twin_fraction":"Recovery_twin_fraction", "Recovery_twin_thickness":"Recovery_twin_thickness",
            "Recovery_twin_spacing_observed":"Recovery_twin_spacing_observed",
            "Recovery_twin_spacing_used_in_fraction_calculation":"Recovery_twin_spacing_fraction_input_nm",
            "Deformation_twin_width":"Deformation_twin_width", "Deformation_twin_spacing":"Deformation_twin_spacing",
            "Precipitate_type":"Precipitate_type", "APT_local_composition":"APT_local_composition",
            "EDS_local_composition":"EDS_local_composition"}
    for p in physics.to_dict("records"):
        if p["Feature_Name"] in fmap and "N2.6-PC" in p["Scope"]:
            field = fmap[p["Feature_Name"]]; out.at[pc, field] = p["Value"]
            provenance.append({"Paper_ID":"P008","DOI":EXPECTED_DOI,"ML_Condition_ID":"P008_MC_N2p6_PC",
                "Feature_Name":field,"Original_Value":pd.NA,"Recovered_Value":p["Value"],"Units":p["Units"],
                "Evidence_Type":p["Evidence_Type"],"Evidence_Location":p["Evidence_Location"],
                "Page_Figure_Section":p["Evidence_Location"],"Extraction_Method":p["Extraction_Method"],
                "Confidence":p["Confidence"],"Recovery_Status":p["Value_Status"]})
    pjson = pd.DataFrame(provenance).query("ML_Condition_ID == 'P008_MC_N2p6_PC'").to_dict("records")
    out.at[pc, "P008_Recovery_Provenance_JSON"] = json.dumps(pjson, default=str)
    validate(source, out, pd.DataFrame(provenance), sheets)
    out.to_csv(OUT, index=False)
    pd.DataFrame(provenance).to_csv(PROV, index=False)
    sheets["P008_Aux_N_Series"].to_csv(AUX, index=False)
    sheets["Verification_Change_Log"].to_csv(CORR, index=False)
    write_audit(source, out)
    return source, out


def independent(df):
    excluded = (df["P008_Record_Role"].eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")
                if "P008_Record_Role" in df else pd.Series(False, index=df.index))
    return df[(df.Data_Origin.eq("EXPERIMENTAL")) & df.Observation_Role.eq("INDEPENDENT_CONDITION") & ~excluded]


def validate(source, out, prov, sheets):
    assert len(out) == len(source) + 5
    permitted = {"ML_Condition_ID", "Recovered_Grain_size_um", "Recovered_YS_MPa",
        "Recovered_UTS_MPa", "Recovered_Uniform_elongation_pct", "Recovered_Initial_HCP_fraction",
        "Recovered_TRIP", "Recovered_TWIP", "Recovered_Recrystallized_fraction",
        "Effective_TRIP", "Effective_TWIP", "Study_Series_ID", "Material_Parent_ID",
        "Physical_Batch_ID", "Replicate_ID", "Leakage_Group_Strict", "Leakage_Group_Material"}
    stable = [c for c in source.columns if c not in permitted]
    pd.testing.assert_frame_equal(out.loc[:len(source)-1, stable].reset_index(drop=True), source[stable], check_dtype=False)
    assert out.Observation_ID.is_unique
    p8 = out[out.Paper_ID.eq("P008")]
    exact = p8[p8.ML_Condition_ID.isin(sheets["P008_Conditions"].Proposed_ML_Condition_ID)]
    assert len(exact) == 6 and exact.ML_Condition_ID.nunique() == 6
    assert p8.loc[p8.Condition_ID.eq("P008_C01"), "P008_Legacy_Mapping_Status"].iloc[0] == "MANUAL_IDENTITY_REVIEW"
    pc = exact[exact.ML_Condition_ID.eq("P008_MC_N2p6_PC")].iloc[0]
    assert pc.Condition_ID == "P008_C02" and pd.isna(pc.Recovered_Initial_FCC_fraction)
    assert pc.Initial_BCC_alpha_martensite_fraction == .24 and pc.Recovered_Initial_HCP_fraction == 0
    expected = {"P008_MC_N0_PC":(1,1), "P008_MC_N0_FC":(1,pd.NA),
                "P008_MC_N2p6_PC":(0,1), "P008_MC_N2p6_FC":(0,1)}
    for cid, (t,w) in expected.items():
        r=exact[exact.ML_Condition_ID.eq(cid)].iloc[0]; assert r.Effective_TRIP == t
        assert (pd.isna(r.Effective_TWIP) if pd.isna(w) else r.Effective_TWIP == w)
    assert exact[exact.P008_Source_State.eq("HOMO")][["Effective_TRIP","Effective_TWIP"]].isna().all().all()
    assert exact.SFE_mJ_m2.isna().all()  # alloy-level evidence is not copied into condition field
    assert not set(sheets["P008_Aux_N_Series"].query("Primary_ML_Eligibility.str.startswith('AUXILIARY')", engine="python").Alloy_Label) & set(exact.P008_Source_State)
    assert prov[["Paper_ID","DOI","ML_Condition_ID","Feature_Name","Recovered_Value","Evidence_Type","Evidence_Location","Extraction_Method","Confidence","Recovery_Status"]].notna().all().all()


def write_audit(source, out):
    p8 = out[out.Paper_ID.eq("P008")]; ex = p8[p8.P008_Record_Role.str.startswith("EXACT", na=False)]
    before, after = independent(source), independent(out)
    counts=lambda d: (d.Effective_TRIP.notna().sum(), d.Effective_TWIP.notna().sum(), d[["Effective_TRIP","Effective_TWIP"]].notna().all(axis=1).sum())
    HIER.parent.mkdir(parents=True, exist_ok=True)
    ex[["Condition_ID","Observation_ID","ML_Condition_ID","Study_Series_ID","Material_Parent_ID","Physical_Batch_ID","Replicate_ID","Leakage_Group_Strict","Leakage_Group_Material","P008_Record_Role"]].to_csv(HIER,index=False)
    AUDIT.write_text(f"""# P008 recovery v4 audit

## Source identity and preservation

- Verified `Paper_ID=P008`, DOI `{EXPECTED_DOI}`, and the workbook's six-condition hierarchy for **{EXPECTED_TITLE}**. Integration fails closed on an ID/DOI mismatch.
- recovery_v3 rows: **{len(source)}**; recovery_v4 rows: **{len(out)}**; rows added: **5**. All {len(source)} prior rows and their scientific fields remain present and ordered.
- Both legacy rows remain. `P008_C02` maps exactly to `P008_MC_N2p6_PC`; `P008_C01` is `MANUAL_IDENTITY_REVIEW` and excluded from independent counting to prevent double counting with the new exact N0-HOMO record.

## Exact hierarchy and leakage

P008 has **6 exact independent conditions**, all in `P008_SERIES01`. N0 HOMO/PC/FC are siblings under `P008_MAT_N0`; N2.6 HOMO/PC/FC are siblings under `P008_MAT_N2p6`. `Physical_Batch_ID` and `Replicate_ID` remain unknown (NA). Strict splits use `P008_SERIES01`; material-level splits use the corresponding parent. Source/stage/auxiliary records add no independent conditions. See `reports/tables/p008_recovery_v4_hierarchy.csv`.

## Target evidence before and after

| Exact condition | Effective TRIP | Effective TWIP |
|---|---:|---:|
| N0-HOMO | NA | NA |
| N0-PC | 1 | 1 |
| N0-FC | 1 | NA |
| N2.6-HOMO | NA | NA |
| N2.6-PC | 0 | 1 |
| N2.6-FC | 0 | 1 |

The verified corrections are: N0-PC TWIP unresolved→1; N0-FC TRIP unresolved→1; N2.6-FC unresolved→0/1. HOMO remains unresolved. NA was never interpreted as negative.

## Recovered descriptors and phase correction

Condition-scoped processing, RT text/status, 1e-3 s^-1 strain rate, grain-size values/scopes, N0 EBSD HCP fractions, recrystallized fractions, and supported YS/UTS/uniform elongation were recovered. N2.6-PC stores ~0.24 pre-existing **BCC alpha** separately from HCP and leaves FCC NA; FCC was never computed as 1-HCP. Alpha-lath, recovery-twin, deformation-twin, Cr2N, and local APT/EDS evidence remain distinct fields; local chemistry does not replace bulk chemistry and recovery twins do not establish TWIP.

## SFE and unresolved evidence

N2.6 ≈26 mJ/m2 is stored with `ALLOY_LEVEL`/TEM/current-study scope and is absent from condition-specific `SFE_mJ_m2`. N0 6.5 mJ/m2 is marked `SECONDARY_REFERENCE`, not a P008 measurement. Supplementary Table S1 is unavailable, so missing HOMO/FC UTS and elongation remain NA. Exact RT Kelvin, exact FCC fractions, intermediate-N bulk chemistry/targets, physical batches, and replicates remain unresolved. No figures were digitized and no supplementary values were fabricated.

## Count impact

| Metric | recovery_v3 | recovery_v4 |
|---|---:|---:|
| Independent experimental ML conditions | {len(before)} | {len(after)} |
| Usable TRIP conditions | {counts(before)[0]} | {counts(after)[0]} |
| Usable TWIP conditions | {counts(before)[1]} | {counts(after)[1]} |
| Usable joint conditions | {counts(before)[2]} | {counts(after)[2]} |

P008 changes from two legacy independent rows to six exact conditions while retaining both legacy observations; the ambiguous legacy C01 is not counted twice. Auxiliary N0.5/N0.8/N1.1/N1.4/N1.8/N3.2 entries remain source-only in `reports/tables/p008_recovery_v4_aux_n_series.csv`.

## Provenance and correction ledger

Every populated recovered value is represented in `reports/tables/p008_recovery_v4_provenance.csv`; the six verified corrections are retained in `reports/tables/p008_recovery_v4_corrections.csv`. No ML, descriptors, feature engineering, figure digitization, or model selection was performed.
""", encoding="utf-8")


if __name__ == "__main__": integrate()
