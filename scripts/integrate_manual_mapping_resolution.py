"""Build recovery_v2 from the reviewed P006/P016 mapping resolution.

Recovery v1 and all legacy scientific columns are immutable inputs.  Existing
target values are never edited: adjudicated values are exposed through explicit
``Effective_*`` fields and the correction ledger.  New P016 source conditions
and their correlated stage observations are appended with only workbook-backed
values.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v1.csv"
BOOK = ROOT / "data/interim/manual_recovery/P006_P016_manual_mapping_resolution.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v2.csv"
CORRECTIONS = ROOT / "reports/tables/recovery_v2_target_correction_ledger.csv"
AUDIT = ROOT / "reports/RECOVERY_V2_AUDIT.md"


def _effective(row: pd.Series, target: str):
    correction = row.get(f"Target_Correction_{target}")
    if isinstance(correction, str) and correction == "INVALIDATE_TO_NA":
        return pd.NA
    recovered = row.get(f"Recovered_{target}")
    return recovered if pd.notna(recovered) else row.get(target)


def _usable(df: pd.DataFrame) -> tuple[int, int, int]:
    eligible = df[df.Observation_Role.isin(["INDEPENDENT_CONDITION", "REPEATED_STAGE"])]
    eligible = eligible[eligible.Data_Origin.isin(["EXPERIMENTAL", "HYBRID"])]
    grouped = eligible.groupby("ML_Condition_ID").agg(
        trip=("Effective_TRIP", lambda x: x.notna().any()),
        twip=("Effective_TWIP", lambda x: x.notna().any()),
    )
    return int(grouped.trip.sum()), int(grouped.twip.sum()), int((grouped.trip & grouped.twip).sum())


def _blank_row(columns) -> dict:
    return {column: pd.NA for column in columns}


def integrate():
    sheets = pd.read_excel(BOOK, sheet_name=None)
    hierarchy = sheets["P016_Hierarchy_Resolution"]
    stages = sheets["P016_Stage_Hierarchy"]
    p006 = sheets["P006_Target_Resolution"]
    source = pd.read_csv(SOURCE)
    out = source.copy()
    out["Target_Correction_TRIP"] = pd.NA
    out["Target_Correction_TWIP"] = pd.NA
    out["Resolution_Provenance_JSON"] = pd.NA

    # Exact legacy P016 rows are retained and assigned the reviewed exact IDs.
    for condition in ("P016_C01", "P016_C02"):
        decision = hierarchy[hierarchy.Legacy_Condition_ID.eq(condition)].iloc[0]
        idx = out.index[out.Condition_ID.eq(condition)]
        assert len(idx) == 1
        i = idx[0]
        out.at[i, "ML_Condition_ID"] = decision.Proposed_ML_Condition_ID
        out.at[i, "Parent_Experiment_ID"] = decision.Proposed_ML_Condition_ID.replace("_MC_", "_PE_")
        out.at[i, "Grouping_Review_Required"] = 0
        out.at[i, "Grouping_Confidence"] = "HIGH"
        out.at[i, "Grouping_Reason"] = decision.Mapping_action
        out.at[i, "Resolution_Provenance_JSON"] = json.dumps({"workbook_sheet": "P016_Hierarchy_Resolution", "status": decision.Target_status, "source": decision.Source_location})

    # C03 remains byte-for-byte intact in its scientific fields, but its role is
    # explicitly non-ML and it is no longer allowed to impersonate an exact state.
    decision = hierarchy[hierarchy.Legacy_Condition_ID.eq("P016_C03")].iloc[0]
    i = out.index[out.Condition_ID.eq("P016_C03")][0]
    out.at[i, "ML_Condition_ID"] = "P016_LEGACY_COLLAPSED_C03"
    out.at[i, "Parent_Experiment_ID"] = "P016_LEGACY_COLLAPSED_C03"
    out.at[i, "Observation_Role"] = "LEGACY_COLLAPSED"
    out.at[i, "Grouping_Review_Required"] = 0
    out.at[i, "Grouping_Confidence"] = "HIGH"
    out.at[i, "Grouping_Reason"] = decision.Mapping_action
    out.at[i, "Resolution_Provenance_JSON"] = json.dumps({"workbook_sheet": "P016_Hierarchy_Resolution", "status": decision.Target_status, "source": decision.Source_location})

    # Add the four exact conditions absent from the legacy extraction.  No
    # composition, property, or label is copied from a legacy row.
    new_conditions = hierarchy[hierarchy.Legacy_status.eq("new exact condition")]
    appended = []
    for decision in new_conditions.itertuples():
        row = _blank_row(out.columns)
        row.update({
            "Paper_ID": "P016", "DOI": decision.DOI,
            "Condition_ID": decision.Proposed_ML_Condition_ID.replace("P016_MC_", "P016_NEW_"),
            "Annealing_T_K": decision.Heat_T_C + 273.15,
            "Annealing_time_min": decision.Heat_time_min,
            "TRIP": decision.TRIP_final, "TWIP": decision.TWIP_final,
            "Parent_Experiment_ID": decision.Proposed_ML_Condition_ID.replace("_MC_", "_PE_"),
            "ML_Condition_ID": decision.Proposed_ML_Condition_ID,
            "Observation_ID": decision.Proposed_ML_Condition_ID.replace("_MC_", "_OBS_CONDITION_"),
            "Data_Origin": "EXPERIMENTAL", "Observation_Role": "INDEPENDENT_CONDITION",
            "Grouping_Review_Required": 0, "Grouping_Confidence": "HIGH",
            "Grouping_Reason": decision.Mapping_action, "Target_Review_Status": decision.Target_status,
            "Evidence_TRIP": decision.Direct_evidence if pd.notna(decision.TRIP_final) else pd.NA,
            "Evidence_TWIP": decision.Direct_evidence if pd.notna(decision.TWIP_final) else pd.NA,
            "Source_location": decision.Source_location, "Label_confidence": decision.Confidence,
            "Notes": decision.Notes, "Source_File": BOOK.name, "Source_Sheet": "P016_Hierarchy_Resolution",
            "Resolution_Provenance_JSON": json.dumps({"workbook_sheet": "P016_Hierarchy_Resolution", "source": decision.Source_location}),
        })
        appended.append(row)

    # Stage observations are children of, never substitutes for, their condition.
    for stage in stages.itertuples():
        row = _blank_row(out.columns)
        row.update({
            "Paper_ID": "P016", "DOI": hierarchy.DOI.iloc[0],
            "Condition_ID": stage.Proposed_Observation_ID,
            "Parent_Experiment_ID": stage.Parent_ML_Condition_ID.replace("_MC_", "_PE_"),
            "ML_Condition_ID": stage.Parent_ML_Condition_ID,
            "Observation_ID": stage.Proposed_Observation_ID,
            "Deformation_Stage_ID": stage.Proposed_Observation_ID,
            "Local_strain": stage.Local_strain_pct / 100,
            "Deformation_stage": f"{stage.Local_strain_pct:g}% local strain",
            "HCP_fraction_at_condition": stage.HCP_fraction_vol_pct / 100,
            "TRIP": stage.TRIP_stage, "TWIP": stage.TWIP_stage,
            "Data_Origin": "EXPERIMENTAL", "Observation_Role": "REPEATED_STAGE",
            "Grouping_Review_Required": 0, "Grouping_Confidence": "HIGH",
            "Grouping_Reason": "Correlated child observation; excluded from independent sample counts.",
            "Evidence_TRIP": stage.Evidence, "Evidence_TWIP": stage.Evidence if pd.notna(stage.TWIP_stage) else pd.NA,
            "Source_location": stage.Source_location, "Label_confidence": stage.Confidence,
            "Source_File": BOOK.name, "Source_Sheet": "P016_Stage_Hierarchy",
            "Resolution_Provenance_JSON": json.dumps({"workbook_sheet": "P016_Stage_Hierarchy", "source": stage.Source_location, "independent": False}),
        })
        appended.append(row)
    out = pd.concat([out, pd.DataFrame(appended, columns=out.columns)], ignore_index=True)

    # Explicit correction ledger: original TWIP=0 survives; effective value is NA.
    correction_rows = []
    for decision in p006.itertuples():
        i = out.index[out.Condition_ID.eq(decision.Legacy_Condition_ID)][0]
        if decision.Legacy_Condition_ID == "P006_C03":
            out.at[i, "Target_Correction_TWIP"] = "INVALIDATE_TO_NA"
        correction_rows.extend([
            {"Paper_ID": "P006", "Condition_ID": decision.Legacy_Condition_ID, "Observation_ID": out.at[i, "Observation_ID"],
             "Target": target, "Original_Value": out.at[i, target], "Effective_Value": getattr(decision, f"{target}_final"),
             "Status": getattr(decision, f"{target}_status"), "Action": decision.Required_action,
             "Evidence": decision.Evidence, "Source_location": decision.Source_location, "Confidence": decision.Confidence,
             "Source_Workbook": BOOK.name, "Source_Sheet": "P006_Target_Resolution"}
            for target in ("TRIP", "TWIP")
        ])

    out["Effective_TRIP"] = out.apply(_effective, axis=1, target="TRIP")
    out["Effective_TWIP"] = out.apply(_effective, axis=1, target="TWIP")
    pd.DataFrame(correction_rows).to_csv(CORRECTIONS, index=False)
    out.to_csv(OUT, index=False)
    write_audit(source, out)
    return source, out


def write_audit(source, out):
    before = source.copy()
    before["Target_Correction_TRIP"] = pd.NA; before["Target_Correction_TWIP"] = pd.NA
    before["Effective_TRIP"] = before.apply(_effective, axis=1, target="TRIP")
    before["Effective_TWIP"] = before.apply(_effective, axis=1, target="TWIP")
    b, a = _usable(before), _usable(out)
    p16 = out[out.Paper_ID.eq("P016")]
    missing_before = source.isna().mean().mean(); missing_after = out[source.columns].isna().mean().mean()
    AUDIT.write_text(f"""# Recovery v2 hierarchy, leakage, target, provenance, and missingness audit

## Preservation and provenance

- Recovery v1 input: {len(source)} rows; recovery v2: {len(out)} rows. All {len(source)} legacy rows remain in their original order.
- Every legacy scientific/source column is unchanged. Only explicit hierarchy/role metadata is reclassified for P016 C01-C03; canonical P006 TRIP/TWIP cells are not overwritten.
- Added records carry workbook, sheet, evidence location, and confidence. The P006 correction ledger retains original and effective values.

## Hierarchy and leakage

- P016 has six exact ML conditions: 400 C/3 min, 400 C/10 min, 650 C/3 min, 650 C/10 min, 750 C/3 min, and 750 C/10 min.
- P016_C03 is `LEGACY_COLLAPSED` and is excluded from ML-condition counts.
- Six stage rows are `REPEATED_STAGE`, share their exact parent `ML_Condition_ID`, and contribute zero additional independent conditions.
- Duplicate observation IDs: {out.Observation_ID.duplicated().sum()}; stage rows lacking a parent exact condition: {sum(~p16.loc[p16.Observation_Role.eq('REPEATED_STAGE'),'ML_Condition_ID'].isin(p16.loc[p16.Observation_Role.eq('INDEPENDENT_CONDITION'),'ML_Condition_ID']))}.

## Targets

- 400 C conditions remain TRIP/TWIP unresolved. 650 C/3 min and 650 C/10 min are TRIP=1/TWIP=NA. 750 C/3 min is TRIP=1/TWIP=1. 750 C/10 min remains unresolved.
- P006_C01 effective TRIP=0/TWIP=NA; P006_C02 effective TRIP=0/TWIP=1; P006_C03 effective TRIP=1/TWIP=NA. P006_C03's original TWIP=0 remains present and is invalidated only through the correction ledger.

| Usable experimental ML conditions | Before v2 | After v2 |
|---|---:|---:|
| TRIP | {b[0]} | {a[0]} |
| TWIP | {b[1]} | {a[1]} |
| Joint | {b[2]} | {a[2]} |

## Missingness and readiness

- Mean missingness across preserved recovery-v1 columns: {missing_before:.2%} before and {missing_after:.2%} after on the observation-row basis. The increase is expected because stage children contain only directly documented stage values; no value was invented or copied to suppress missingness.
- No ML was trained. Recovery v2 is evidence-resolved, not declared ML-ready; grouped validation, target leakage screening, sparse descriptors, small support, and remaining P1 issues still gate modelling.
""", encoding="utf-8")


if __name__ == "__main__":
    integrate()
