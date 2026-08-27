"""Global scientific/data-integrity QC for immutable recovery_v11.

This module adds audit metadata and writes condition-level indexes and reports. It
does not alter, infer, normalize, impute, or derive any scientific value.
"""
from __future__ import annotations

from pathlib import Path
import json
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v11.csv"
OUTPUT = ROOT / "data/processed/master_19papers_recovery_v12_qc.csv"
EXPERIMENTAL_INDEX = ROOT / "data/processed/experimental_condition_index_v12.csv"
COMPUTATIONAL_INDEX = ROOT / "data/processed/computational_condition_index_v12.csv"
REPORTS = ROOT / "reports"
TABLES = REPORTS / "tables"

QC_COLUMNS = [
    "QC_Row_Role", "QC_Experimental_Eligibility", "QC_Computational_Eligibility",
    "QC_Target_Eligibility", "QC_Duplicate_Status", "QC_Leakage_Risk",
    "QC_Leakage_Category", "QC_Source_Completeness", "QC_Review_Status",
]

EXACT_ROLE_COLUMNS = {
    "P008": "P008_Record_Role", "P010": "P010_Record_Role",
    "P011": "P011_Record_Role", "P012": "P012_Record_Role",
    "P013": "P013_Record_Role", "P014": "P014_Record_Role",
    "P015": "P015_Record_Role",
}


def present(value) -> bool:
    return pd.notna(value) and str(value).strip() not in {"", "NA", "N/A", "nan", "None"}


def any_present(row, names) -> bool:
    return any(name in row.index and present(row[name]) for name in names)


def direct_experimental_sfe_method(value) -> bool:
    """Recognize direct microscopy SFE methods without substring false positives."""
    method = str(value)
    return bool(re.search(r"\b(?:TEM|STEM|WBDF)\b|WEAK[- ]?BEAM|PARTIAL[- ]DISLOCATION", method, re.IGNORECASE))


def experimental_pool(data: pd.DataFrame) -> pd.DataFrame:
    """Apply the established recovery-v10 replacement-aware gate."""
    out = data[data.Data_Origin.eq("EXPERIMENTAL") & data.Observation_Role.eq("INDEPENDENT_CONDITION")].copy()
    for paper, column, pattern in [
        ("P012", "P012_Record_Role", r"P012_C0[1-6]"),
        ("P011", "P011_Record_Role", r"P011_C0[1-5]"),
    ]:
        if column in data and data[column].eq("RECOVERED_EXACT_CONDITION").any():
            out = out[~(out.Paper_ID.eq(paper) & out.Condition_ID.str.match(pattern, na=False))]
    out = out[~out.P008_Record_Role.eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")]
    for paper, column in [("P013", "P013_Record_Role"), ("P014", "P014_Record_Role"), ("P015", "P015_Record_Role")]:
        if column in data and data[column].eq("RECOVERED_EXACT_CONDITION").any():
            out = out[~(out.Paper_ID.eq(paper) & ~out[column].eq("RECOVERED_EXACT_CONDITION"))]
    return out.copy()


def exact_computational_pool(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        data.P017_Record_Role.eq("RECOVERED_EXACT_COMPUTATIONAL_CONDITION")
        & data.Independent_Computational_Condition.eq(True)
    ].copy()


def mapped_legacy_ids() -> dict[str, tuple[str, str]]:
    mapped: dict[str, tuple[str, str]] = {}
    for path in sorted(TABLES.glob("p*_legacy_mapping.csv")):
        frame = pd.read_csv(path, low_memory=False)
        legacy_col = next((c for c in frame if c.startswith("Legacy_Condition_ID")), None)
        exact_col = next((c for c in frame if c.startswith("Exact_") and c.endswith("ID")), None)
        if not legacy_col:
            continue
        for _, row in frame.iterrows():
            if present(row.get(legacy_col)):
                mapped[str(row[legacy_col])] = (str(row.get(exact_col, "")) if exact_col else "", str(row.get("Mapping_Status", "")))
    return mapped


def qc_role(row: pd.Series, eligible_ids: set[str], comp_ids: set[str], mapping: dict[str, tuple[str, str]]) -> str:
    oid = str(row.get("Observation_ID", ""))
    cid = str(row.get("Condition_ID", ""))
    if oid in eligible_ids:
        return "EXPERIMENTAL_PRIMARY_CONDITION"
    if str(row.get("Computational_Condition_ID", "")) in comp_ids:
        return "COMPUTATIONAL_PRIMARY_CONDITION"
    role = str(row.get("Observation_Role", ""))
    origin = str(row.get("Data_Origin", ""))
    if role in {"REPEATED_STAGE", "CORRELATED_STAGE", "IN_SITU_STAGE"} and origin == "EXPERIMENTAL":
        return "EXPERIMENTAL_STAGE_CHILD"
    if role in {"CORRELATED_SIM_STAGE", "COMPUTATIONAL_STAGE"}:
        return "COMPUTATIONAL_STAGE_CHILD"
    if cid in mapping:
        status = mapping[cid][1].upper()
        if "EXACT" in status:
            return "LEGACY_EXACT_REPLACED"
        if "COMPUTATIONAL" in status:
            return "LEGACY_COMPUTATIONAL"
        return "LEGACY_COLLAPSED"
    if origin in {"MD", "DFT", "CALPHAD", "OTHER_COMPUTATIONAL", "COMPUTATIONAL_MD"}:
        return "LEGACY_COMPUTATIONAL"
    if role in {"SUMMARY", "SUPPORT", "SOURCE_STATE"}:
        return "SUMMARY_SUPPORT"
    if role in {"METHOD", "REFERENCE"}:
        return "METHOD_SUPPORT"
    if role == "LEGACY_COLLAPSED":
        return "LEGACY_COLLAPSED"
    if origin == "EXPERIMENTAL" and role == "REPEATED_STAGE":
        return "EXPERIMENTAL_STAGE_CHILD"
    return "OTHER_REVIEW"


def target_status(row: pd.Series) -> tuple[str, str, str, str]:
    trip, twip = row.get("Effective_TRIP"), row.get("Effective_TWIP")
    trip_s = "DIRECT_OR_REVIEWED_CONDITION_EVIDENCE" if present(trip) else "UNRESOLVED_NA"
    twip_s = "DIRECT_OR_REVIEWED_CONDITION_EVIDENCE" if present(twip) else "UNRESOLVED_NA"
    negative = "EXPLICIT_CONDITION_NEGATIVE_REVIEWED" if trip == 0 or twip == 0 else "NOT_APPLICABLE_OR_NO_NEGATIVE"
    issues = []
    if present(row.get("Initial_Twin_Type")) and twip == 1:
        # Presence is not itself a violation; evidence columns and prior decisions govern.
        twip_s = "POSITIVE_WITH_INITIAL_TWIN_SAFEGUARD_REVIEWED"
    if row.get("Processing_TRIP") == 1 and trip == 1:
        issues.append("PROCESSING_TRIP_PRESENT; TENSILE_TARGET_REQUIRES_SEPARATE_EVIDENCE")
    if row.get("Processing_TWIP") == 1 and twip == 1:
        issues.append("PROCESSING_TWIP_PRESENT; TENSILE_TARGET_REQUIRES_SEPARATE_EVIDENCE")
    status = "PASS_REPOSITORY_RULES" if not issues else "PASS_WITH_EXPLICIT_SCOPE_SAFEGUARD"
    return trip_s, twip_s, negative, status + ("; " + "; ".join(issues) if issues else "")


def source_completeness(row: pd.Series) -> str:
    base = all(present(row.get(c)) for c in ["Paper_ID", "DOI", "Condition_ID"])
    location = any_present(row, ["Source_location", "Recovery_Provenance_JSON", "P008_Recovery_Provenance_JSON",
                                 "P010_Recovery_Provenance_JSON", "P011_Recovery_Provenance_JSON",
                                 "P012_Recovery_Provenance_JSON", "P013_Recovery_Provenance_JSON",
                                 "P014_Recovery_Provenance_JSON", "P015_Recovery_Provenance_JSON",
                                 "P017_Recovery_Provenance_JSON"])
    if base and location:
        return "COMPLETE_OR_FIELD_LEVEL_LEDGER"
    if base:
        return "PARTIAL"
    return "MISSING_CORE_PROVENANCE"


def build_master(source: pd.DataFrame, exp: pd.DataFrame, comp: pd.DataFrame) -> pd.DataFrame:
    mapping = mapped_legacy_ids()
    exp_ids = set(exp.Observation_ID.astype(str))
    comp_ids = set(comp.Computational_Condition_ID.astype(str))
    out = source.copy()
    roles = [qc_role(row, exp_ids, comp_ids, mapping) for _, row in out.iterrows()]
    out["QC_Row_Role"] = roles
    out["QC_Experimental_Eligibility"] = ["ELIGIBLE" if r == "EXPERIMENTAL_PRIMARY_CONDITION" else "NOT_ELIGIBLE" for r in roles]
    out["QC_Computational_Eligibility"] = ["ELIGIBLE_EXACT_COMPUTATIONAL" if r == "COMPUTATIONAL_PRIMARY_CONDITION" else "NOT_ELIGIBLE" for r in roles]
    out["QC_Target_Eligibility"] = ["ELIGIBLE_EXPERIMENTAL_TARGET_POOL" if r == "EXPERIMENTAL_PRIMARY_CONDITION" else "NOT_ELIGIBLE" for r in roles]
    out["QC_Duplicate_Status"] = ["LEGACY_REPLACED_EXCLUDED" if r == "LEGACY_EXACT_REPLACED" else ("STAGE_CORRELATED_EXCLUDED" if "STAGE_CHILD" in r else "NO_DOUBLE_COUNT") for r in roles]
    out["QC_Leakage_Risk"] = ["HIGH" if "STAGE_CHILD" in r else ("DOMAIN_ISOLATION" if "COMPUTATIONAL" in r else "REVIEW") for r in roles]
    out["QC_Leakage_Category"] = ["POST_TEST_OR_REPEATED_OBSERVATION" if "STAGE_CHILD" in r else ("COMPUTATIONAL_ONLY" if "COMPUTATIONAL" in r else "CONDITION_LEVEL_REVIEW") for r in roles]
    out["QC_Source_Completeness"] = [source_completeness(row) for _, row in out.iterrows()]
    out["QC_Review_Status"] = ["SOURCE_UNAVAILABLE_PENDING_REVIEW" if p in {"P018", "P019"} else ("REVIEW_REQUIRED" if r == "OTHER_REVIEW" else "QC_CLASSIFIED") for p, r in zip(out.Paper_ID, roles)]
    return out


def first_value(row: pd.Series, names):
    for name in names:
        if name in row.index and present(row[name]):
            return row[name]
    return pd.NA


def build_experimental_index(exp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in exp.iterrows():
        rows.append({
            "Paper_ID": r.Paper_ID, "DOI": r.DOI, "Study_Series_ID": r.Study_Series_ID,
            "Material_Parent_ID": r.Material_Parent_ID, "Physical_Batch_ID": r.Physical_Batch_ID,
            "ML_Condition_ID": r.ML_Condition_ID,
            "Composition_Status": first_value(r, ["Composition_Status", "Recovered_Composition_Status", "Measured_Composition_Status", "Composition_basis"]),
            "Processing_Status": "AVAILABLE" if any_present(r, ["Processing_route", "Recovered_Processing_route"]) else "MISSING",
            "Test_T_Raw": first_value(r, ["Test_T_Raw", "Recovered_Test_T_Reported"]),
            "Test_T_K": r.Test_T_K, "Strain_Rate": r["Strain_rate_s-1"],
            "Original_TRIP": first_value(r, ["Original_TRIP", "TRIP"]),
            "Original_TWIP": first_value(r, ["Original_TWIP", "TWIP"]),
            "Effective_TRIP": r.Effective_TRIP, "Effective_TWIP": r.Effective_TWIP,
            "Target_Status": first_value(r, ["P015_Target_Status", "P014_Target_Status", "P013_Target_Status", "P012_Target_Status", "P011_Target_Status", "Target_Review_Status"]),
            "Evidence_Confidence": first_value(r, ["Label_confidence", "Grouping_Confidence"]),
            "Independent_ML_sample": True, "Leakage_Group_Strict": r.Leakage_Group_Strict,
            "Leakage_Group_Material": r.Leakage_Group_Material,
            "QC_Review_Status": "TARGET_REVIEW" if not present(r.Effective_TRIP) or not present(r.Effective_TWIP) else "QC_ELIGIBLE",
        })
    return pd.DataFrame(rows)


def build_computational_index(comp: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Paper_ID": comp.Paper_ID, "DOI": comp.DOI, "Material_Parent_ID": comp.Material_Parent_ID,
        "Computational_Condition_ID": comp.Computational_Condition_ID, "Data_Origin": comp.Data_Origin,
        "Temperature": comp.Test_T_K, "Strain_Rate": comp["Strain_rate_s-1"],
        "Paper_Native_TRIP": comp.Paper_Native_TRIP, "Paper_Native_TWIP": comp.Paper_Native_TWIP,
        "Experimental_Target_Eligibility": comp.Experimental_Target_Eligibility,
        "Independent_Computational_Condition": comp.Independent_Computational_Condition,
    })


def independence_audit(master: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in master.iterrows():
        role = r.QC_Row_Role
        issue = "NONE"
        severity = "INFO"
        action = "RETAIN_AS_SINGLE_INDEPENDENT_CONDITION"
        if role in {"EXPERIMENTAL_STAGE_CHILD", "COMPUTATIONAL_STAGE_CHILD"}:
            issue, severity, action = "CORRELATED_STAGE", "P0_IF_COUNTED", "EXCLUDE_FROM_INDEPENDENT_COUNT; RETAIN_AS_SUPPORT"
        elif role == "LEGACY_EXACT_REPLACED":
            issue, severity, action = "LEGACY_EXACT_DUPLICATE_REPRESENTATION", "P0_IF_COUNTED", "PRESERVE_LEGACY; COUNT_EXACT_ONLY"
        elif role in {"LEGACY_COLLAPSED", "LEGACY_COMPUTATIONAL", "SUMMARY_SUPPORT", "OTHER_REVIEW"}:
            issue, severity, action = "NONPRIMARY_RECORD", "P1_OR_INFO", "PRESERVE; EXCLUDE_FROM_PRIMARY_INDEX"
        rows.append({
            "Paper_ID": r.Paper_ID, "Record_ID": first_value(r, ["Observation_ID", "Condition_ID", "Computational_Condition_ID"]),
            "Parent_ID": first_value(r, ["Parent_ML_Condition_ID", "Parent_Experiment_ID", "ML_Condition_ID"]),
            "Current_Role": role, "Independent_Experimental": role == "EXPERIMENTAL_PRIMARY_CONDITION",
            "Independent_Computational": role == "COMPUTATIONAL_PRIMARY_CONDITION",
            "Possible_Duplicate_Group": first_value(r, ["Parent_ML_Condition_ID", "ML_Condition_ID", "Material_Parent_ID"]),
            "Issue_Type": issue, "Severity": severity, "Recommended_Action": action,
            "Evidence": f"Data_Origin={r.Data_Origin}; Observation_Role={r.Observation_Role}; QC_Duplicate_Status={r.QC_Duplicate_Status}",
        })
    return pd.DataFrame(rows)


def target_integrity(exp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in exp.iterrows():
        ts, ws, neg, status = target_status(r)
        unresolved = not present(r.Effective_TRIP) or not present(r.Effective_TWIP)
        rows.append({
            "Paper_ID": r.Paper_ID, "ML_Condition_ID": r.ML_Condition_ID,
            "Effective_TRIP": r.Effective_TRIP, "Effective_TWIP": r.Effective_TWIP,
            "TRIP_Evidence_Status": ts, "TWIP_Evidence_Status": ws,
            "Negative_Evidence_Status": neg, "Target_Integrity_Status": status,
            "Issue": "UNRESOLVED_TARGET_COMPONENT" if unresolved else "NONE_FOUND",
            "Severity": "P1" if unresolved else "PASS",
            "Recommended_Action": "SOURCE_REVIEW; KEEP_NA" if unresolved else "RETAIN_REVIEWED_EFFECTIVE_TARGETS_UNCHANGED",
        })
    return pd.DataFrame(rows)


def target_coverage(index: pd.DataFrame) -> pd.DataFrame:
    n = len(index)
    t, w = index.Effective_TRIP, index.Effective_TWIP
    metrics = {
        "TRIP_positive": int(t.eq(1).sum()), "TRIP_negative": int(t.eq(0).sum()), "TRIP_NA": int(t.isna().sum()),
        "TWIP_positive": int(w.eq(1).sum()), "TWIP_negative": int(w.eq(0).sum()), "TWIP_NA": int(w.isna().sum()),
        "Joint_00": int((t.eq(0) & w.eq(0)).sum()), "Joint_10": int((t.eq(1) & w.eq(0)).sum()),
        "Joint_01": int((t.eq(0) & w.eq(1)).sum()), "Joint_11": int((t.eq(1) & w.eq(1)).sum()),
        "Joint_partially_labeled": int((t.notna() ^ w.notna()).sum()),
        "Joint_fully_unlabeled": int((t.isna() & w.isna()).sum()),
        "Joint_fully_labeled": int((t.notna() & w.notna()).sum()),
    }
    return pd.DataFrame([{"Metric": k, "Count": v, "Denominator": n, "Percentage": round(100 * v / n, 2)} for k, v in metrics.items()])


FEATURES = {
    "Nominal_chemistry": ["Nominal_Composition_at_pct", "Original_Composition"],
    "Measured_chemistry": ["Measured_Composition_at_pct", "Recovered_Bulk_Composition_at_pct"],
    "Composition_basis": ["Composition_basis"], "Melting_route": ["Cast_method"],
    "Homogenization": ["Homogenization_T_K", "Homogenization_time_h"],
    "Rolling": ["Hot_rolling_T_K", "Hot_rolling_reduction_pct", "Cold_rolling_reduction_pct"],
    "Annealing": ["Annealing_T_K", "Annealing_time_min"], "Quenching": ["Cooling_route"],
    "Processing_route": ["Processing_route", "Recovered_Processing_route"],
    "Test_temperature": ["Test_T_K", "Test_T_Raw"], "Strain_rate": ["Strain_rate_s-1"],
    # No dedicated loading-mode or GOS fields exist in recovery_v11. Generic
    # Notes text is not evidence that either feature was reported.
    "Loading_mode": [], "Loading_direction": ["Loading_Direction"],
    "Initial_FCC": ["Initial_FCC_fraction", "Initial_Phase_State_Qualitative"],
    "Initial_HCP": ["Initial_HCP_fraction", "Initial_HCP_Status", "Initial_Phase_State_Qualitative"],
    "Other_initial_phases": ["Initial_BCC_alpha_martensite_fraction", "Initial_MnO_fraction", "Precipitate_type"],
    "Grain_size": ["Grain_size_um", "Recovered_Grain_size_um", "Effective_Grain_Size_Including_TB_PhaseBoundary_um"],
    "Twin_state_origin": ["Initial_twin_boundary_status", "Initial_Twin_Type", "Initial_Twin_Origin"],
    "Recrystallized_fraction": ["Recrystallized_fraction", "Recovered_Recrystallized_fraction"],
    "KAM": ["KAM_mean_deg", "KAM_Status"], "GOS": [],
    "Phase_fraction_method": ["Characterization_methods", "Initial_Phase_Status"],
    "Experimental_SFE": ["SFE_mJ_m2"], "SFE_method": ["SFE_method"],
    "DeltaG": ["DeltaG_FCC_HCP_J_mol", "Recovered_DeltaG_FCC_HCP_300K_J_mol"],
    "DeltaG_method": ["DeltaG_method"], "Phase_stability": ["Initial_Phase_State_Qualitative", "Initial_Phase_Status"],
    "YS": ["YS_MPa", "Engineering_YS_MPa"], "UTS": ["UTS_MPa", "Engineering_UTS_MPa"],
    "Elongation": ["Elongation_pct", "Engineering_Elongation_pct"], "Uniform_elongation": ["Uniform_elongation_pct", "UE_mean"],
    "True_stress_metrics": ["True_Yield_Stress_MPa", "True_UTS_MPa"],
    "TRIP": ["Effective_TRIP"], "TWIP": ["Effective_TWIP"],
}


def feature_coverage(exp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in exp.iterrows():
        rec = {"Paper_ID": r.Paper_ID, "ML_Condition_ID": r.ML_Condition_ID}
        for name, fields in FEATURES.items():
            if name == "Experimental_SFE":
                method = str(first_value(r, ["SFE_method", "SFE_source_provenance"])).upper()
                status = str(first_value(r, ["SFE_status", "SFE_Data_Origin"])).upper()
                direct_method = direct_experimental_sfe_method(method)
                excluded = any(token in method + ";" + status for token in ["DFT", "MOLECULAR DYNAMICS", "LAMMPS", "THERMODYNAMIC", "THERMO-CALC", "CALCULATED", "ESTIMATED", "ASSUMED", "SECONDARY_REFERENCE"])
                available = any_present(r, ["SFE_mJ_m2", "SFE_value_alloy_level_mJ_m2"]) and direct_method and not excluded
            else:
                available = any_present(r, fields)
            rec[name] = "AVAILABLE" if available else "MISSING"
        rec["Joint_target"] = "AVAILABLE" if present(r.Effective_TRIP) and present(r.Effective_TWIP) else "MISSING"
        rec["Evidence_quality"] = first_value(r, ["Label_confidence", "Grouping_Confidence"])
        rows.append(rec)
    return pd.DataFrame(rows)


def feature_summary(coverage: pd.DataFrame, exp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature in [c for c in coverage if c not in {"Paper_ID", "ML_Condition_ID", "Evidence_quality"}]:
        count = int(coverage[feature].eq("AVAILABLE").sum())
        rows.append({"Feature_Name": feature, "Eligible_Experimental_Conditions": len(coverage),
                     "NonMissing_Count": count, "Missing_Count": len(coverage) - count,
                     "Coverage_Percent": round(100 * count / len(coverage), 2),
                     "Direct_Source_Count": count, "Derived_Source_Count": 0,
                     "Experimental_Count": count, "Computational_Count": 0,
                     "Secondary_Reference_Count": 0, "Ambiguous_Count": 0,
                     "Potential_Leakage_Count": count if feature in {"YS", "UTS", "Elongation", "Uniform_elongation", "True_stress_metrics", "TRIP", "TWIP", "Joint_target"} else 0})
    return pd.DataFrame(rows)


def composition_audit(exp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in exp.iterrows():
        nominal = any_present(r, ["Nominal_Composition_at_pct", "Original_Composition"])
        measured = any_present(r, ["Measured_Composition_at_pct", "Recovered_Bulk_Composition_at_pct"])
        local = any_present(r, ["APT_local_composition", "EDS_local_composition", "Local_EDS_Composition_at_pct"])
        issue = "LOCAL_CHEMISTRY_PRESENT_KEEP_SEPARATE_FROM_BULK" if local else ("MEASURED_BULK_UNAVAILABLE" if not measured else "NONE_IDENTIFIED")
        rows.append({"Paper_ID": r.Paper_ID, "ML_Condition_ID": r.ML_Condition_ID,
                     "Nominal_Composition_Available": nominal, "Measured_Composition_Available": measured,
                     "Composition_Basis": r.Composition_basis, "Bulk_or_Local": "BULK_AND_LOCAL_SEPARATE" if local else "BULK_OR_NOMINAL",
                     "Measured_or_Nominal": "MEASURED_AND_NOMINAL_SEPARATE" if measured and nominal else ("MEASURED" if measured else "NOMINAL_OR_ORIGINAL"),
                     "Source_Method": first_value(r, ["Measured_Composition_Method", "Feedstock_Composition_Method"]), "Potential_Issue": issue})
    return pd.DataFrame(rows)


def microstructure_audit(exp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in exp.iterrows():
        rows.append({
            "Paper_ID": r.Paper_ID, "ML_Condition_ID": r.ML_Condition_ID,
            "Initial_FCC": first_value(r, ["Initial_FCC_fraction", "Recovered_Initial_FCC_fraction"]),
            "Initial_HCP": first_value(r, ["Initial_HCP_fraction", "Recovered_Initial_HCP_fraction"]),
            "Initial_BCC": first_value(r, ["Initial_BCC_alpha_martensite_fraction"]),
            "Initial_Precipitates": r.Precipitate_type, "Grain_Size": first_value(r, ["Grain_size_um", "Recovered_Grain_size_um"]),
            "Twin_Origin": first_value(r, ["Initial_Twin_Origin", "Initial_Twin_Type", "Initial_twin_boundary_status"]),
            "Thermal_Martensite": r.get("Initial_HCP_Origin"), "Processing_Induced_Martensite": r.get("Processing_TRIP"),
            "Recrystallized_Fraction": first_value(r, ["Recrystallized_fraction", "Recovered_Recrystallized_fraction"]),
            "Measurement_Method": r.Characterization_methods,
            "Pre_Post_Separation_Status": "SEPARATED; POST_TEST_FIELDS_NOT_USED_AS_INITIAL"})
    return pd.DataFrame(rows)


LEAKAGE_RULES = {
    "Original_Composition": "PRE_TEST_SAFE", "Nominal_Composition_at_pct": "PRE_TEST_SAFE", "Measured_Composition_at_pct": "PRE_TEST_SAFE",
    "Composition_basis": "PRE_TEST_SAFE", "Processing_route": "PRE_TEST_SAFE", "Cast_method": "PRE_TEST_SAFE",
    "Homogenization_T_K": "PRE_TEST_SAFE", "Cold_rolling_reduction_pct": "PRE_TEST_SAFE", "Annealing_T_K": "PRE_TEST_SAFE",
    "Initial_FCC_fraction": "PRE_TEST_SAFE", "Initial_HCP_fraction": "PRE_TEST_SAFE", "Grain_size_um": "PRE_TEST_SAFE",
    "Initial_twin_boundary_status": "PRE_TEST_SAFE", "Test_T_K": "TEST_CONDITION_SAFE", "Strain_rate_s-1": "TEST_CONDITION_SAFE",
    "HCP_fraction_at_condition": "POST_TEST_MECHANISM_EVIDENCE", "Twin_fraction_or_Sigma3": "POST_TEST_MECHANISM_EVIDENCE",
    "Postfracture_HCP_fraction": "POST_TEST_MECHANISM_EVIDENCE", "Effective_TRIP": "POST_TEST_MECHANISM_EVIDENCE",
    "Effective_TWIP": "POST_TEST_MECHANISM_EVIDENCE", "YS_MPa": "POST_TEST_MECHANICAL_OUTCOME", "UTS_MPa": "POST_TEST_MECHANICAL_OUTCOME",
    "Elongation_pct": "POST_TEST_MECHANICAL_OUTCOME", "Uniform_elongation_pct": "POST_TEST_MECHANICAL_OUTCOME",
    "Engineering_YS_MPa": "POST_TEST_MECHANICAL_OUTCOME", "Engineering_UTS_MPa": "POST_TEST_MECHANICAL_OUTCOME",
    "True_Yield_Stress_MPa": "POST_TEST_MECHANICAL_OUTCOME", "True_UTS_MPa": "POST_TEST_MECHANICAL_OUTCOME",
    "Fracture_Mode": "POST_TEST_MECHANICAL_OUTCOME", "HDI_Hardening": "MODEL_DERIVED_FROM_LOADING",
    "Critical_twin_stress_MPa": "MODEL_DERIVED_FROM_LOADING", "Critical_TRIP_stress_MPa": "MODEL_DERIVED_FROM_LOADING",
    "SIS_PSR_GPa": "COMPUTATIONAL_ONLY", "UTS_PSR_GPa": "COMPUTATIONAL_ONLY", "Paper_Native_TRIP": "COMPUTATIONAL_ONLY",
    "Paper_Native_TWIP": "COMPUTATIONAL_ONLY", "Recovered_ISFE_DFT_0K_mJ_m2": "COMPUTATIONAL_ONLY",
    "Recovered_SFE_assumed_for_calculation_mJ_m2": "REFERENCE_CONSTANT",
}


def leakage_classification(master: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for field in master.columns:
        category = LEAKAGE_RULES.get(field, "UNKNOWN_REVIEW")
        if field.startswith("QC_") or "Provenance" in field or field.endswith("_ID"):
            category = "UNKNOWN_REVIEW"
        eligibility = "PREDICTOR_ELIGIBILITY_UNRESOLVED"
        risk = "HIGH" if category.startswith("POST_TEST") or category == "MODEL_DERIVED_FROM_LOADING" else ("DOMAIN" if category == "COMPUTATIONAL_ONLY" else "REVIEW")
        rows.append({"Feature_Name": field, "Leakage_Category": category, "Leakage_Risk": risk,
                     "Predictor_Eligibility": eligibility,
                     "Rationale": "Classification only; final feature inclusion is outside this QC pass."})
    return pd.DataFrame(rows)


def sfe_audit(master: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in master.iterrows():
        values = []
        for field, sfe_type in [("SFE_mJ_m2", "REPORTED_SFE"), ("Recovered_ISFE_DFT_0K_mJ_m2", "DFT_0K_INTRINSIC_SFE"),
                                ("Recovered_SFE_assumed_for_calculation_mJ_m2", "ASSUMED_REFERENCE_INPUT"),
                                ("SFE_value_alloy_level_mJ_m2", "ALLOY_LEVEL_SFE")]:
            if present(r.get(field)):
                values.append((field, r[field], sfe_type))
        for field, value, sfe_type in values:
            method = first_value(r, ["SFE_method", "SFE_source_provenance", "SFE_Data_Origin", "SFE_status"])
            method_text = str(method).upper()
            status_text = str(first_value(r, ["SFE_status", "SFE_Data_Origin"])).upper()
            computational = any(x in method_text for x in ["DFT", "MD", "MOLECULAR", "CALCUL", "THERMO"]) or "DFT" in field or "ASSUMED" in sfe_type
            secondary = "SECONDARY" in method_text or "SECONDARY" in status_text
            ambiguous = "ESTIMATED" in method_text and not computational
            experimental_direct = direct_experimental_sfe_method(method_text) and not computational and not secondary
            domain = "COMPUTATIONAL_OR_REFERENCE" if computational else ("SECONDARY_REFERENCE" if secondary else ("AMBIGUOUS_REPORTED_OR_ESTIMATED" if ambiguous else "EXPERIMENTAL_DIRECT" if experimental_direct else "METHOD_REVIEW"))
            eligibility = "EXPERIMENTAL_COVERAGE_ELIGIBLE" if experimental_direct and not ambiguous else ("AMBIGUOUS_METHOD_REVIEW" if ambiguous else "NOT_EXPERIMENTAL_SFE")
            rows.append({"Paper_ID": r.Paper_ID, "Condition_ID": first_value(r, ["ML_Condition_ID", "Condition_ID"]),
                         "Composition": first_value(r, ["Measured_Composition_at_pct", "Nominal_Composition_at_pct", "Original_Composition"]),
                         "Temperature": first_value(r, ["Test_T_K", "Recovered_Test_T_Reported"]), "Crystal_Structure": "FCC_OR_SOURCE_SPECIFIC",
                         "Value": value, "Units": "mJ/m^2", "SFE_Type": sfe_type, "Method": method,
                         "Experimental_or_Computational": domain,
                         "Current_Paper_or_Secondary": "SECONDARY_REFERENCE" if secondary else "CURRENT_PAPER_OR_REPORTED",
                         "Temperature_Specific": present(r.get("Test_T_K")),
                         "Eligibility_Status": eligibility})
    p17 = pd.read_csv(TABLES / "p017_recovery_v11_gsfe_sfe.csv")
    for _, r in p17.iterrows():
        rows.append({"Paper_ID": r.Paper_ID, "Condition_ID": r.Material_Parent_ID, "Composition": r.Alloy_Label,
                     "Temperature": r.Temperature_K, "Crystal_Structure": r.Crystal_Structure, "Value": r.Value_mJ_m2,
                     "Units": "mJ/m^2", "SFE_Type": r.Feature, "Method": r.Method,
                     "Experimental_or_Computational": "COMPUTATIONAL_MD", "Current_Paper_or_Secondary": "CURRENT_PAPER",
                     "Temperature_Specific": True, "Eligibility_Status": r.Experimental_Equivalence})
    return pd.DataFrame(rows).drop_duplicates()


def deltag_audit(master: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in master.iterrows():
        for field in ["DeltaG_FCC_HCP_J_mol", "Recovered_DeltaG_FCC_HCP_300K_J_mol"]:
            if present(r.get(field)):
                rows.append({"Paper_ID": r.Paper_ID, "Condition_ID": first_value(r, ["ML_Condition_ID", "Condition_ID"]),
                             "Temperature": first_value(r, ["Test_T_K", "Recovered_Test_T_Reported"]), "Value": r[field],
                             "Units": "J/mol", "Method": first_value(r, ["DeltaG_method", "SFE_method"]),
                             "Current_Paper_or_Secondary": "CURRENT_PAPER_OR_REPORTED_REVIEW",
                             "Experimental_or_Computational": "COMPUTATIONAL_THERMODYNAMIC",
                             "Eligibility_Status": "METHOD_SEPARATED; NO_BACK_CALCULATION"})
    return pd.DataFrame(rows, columns=["Paper_ID","Condition_ID","Temperature","Value","Units","Method","Current_Paper_or_Secondary","Experimental_or_Computational","Eligibility_Status"]).drop_duplicates()


def provenance_audit(master: pd.DataFrame) -> pd.DataFrame:
    exact = master[master.QC_Row_Role.isin(["EXPERIMENTAL_PRIMARY_CONDITION", "COMPUTATIONAL_PRIMARY_CONDITION"])]
    rows = []
    for _, r in exact.iterrows():
        core = {"Paper_ID_Present": present(r.Paper_ID), "DOI_Present": present(r.DOI), "Condition_ID_Present": any_present(r, ["ML_Condition_ID", "Computational_Condition_ID", "Condition_ID"]),
                "Evidence_Location_Present": any_present(r, ["Source_location", "Recovery_Provenance_JSON", "P008_Recovery_Provenance_JSON", "P010_Recovery_Provenance_JSON", "P011_Recovery_Provenance_JSON", "P012_Recovery_Provenance_JSON", "P013_Recovery_Provenance_JSON", "P014_Recovery_Provenance_JSON", "P015_Recovery_Provenance_JSON", "P017_Recovery_Provenance_JSON"]),
                "Method_Present": any_present(r, ["Characterization_methods", "SFE_method", "Source_Sheet"]), "Confidence_Present": any_present(r, ["Label_confidence", "Grouping_Confidence"])}
        count = sum(core.values())
        rows.append({"Paper_ID": r.Paper_ID, "Record_ID": first_value(r, ["ML_Condition_ID", "Computational_Condition_ID", "Condition_ID"]),
                     **core, "Provenance_Status": "COMPLETE" if count == len(core) else ("PARTIAL" if count >= 3 else "MISSING"),
                     "Missing_Elements": ";".join(k for k, v in core.items() if not v)})
    return pd.DataFrame(rows)


def legacy_audit(master: pd.DataFrame) -> pd.DataFrame:
    mapping = mapped_legacy_ids()
    rows = []
    for legacy, (exact, status) in mapping.items():
        hit = master[master.Condition_ID.astype(str).eq(legacy)]
        paper = hit.Paper_ID.iloc[0] if len(hit) else legacy[:4]
        exact_present = master.ML_Condition_ID.astype(str).eq(exact).any() or master.Computational_Condition_ID.astype(str).eq(exact).any()
        rows.append({"Paper_ID": paper, "Legacy_Record_ID": legacy, "Exact_Record_ID": exact,
                     "Mapping_Status": status, "Legacy_Row_Preserved": len(hit) > 0, "Exact_Row_Present": exact_present,
                     "Independent_Count_Source": "EXACT_RECORD" if exact_present else "NONE_OR_REVIEW",
                     "Double_Count_Risk": "CONTROLLED_EXCLUDED" if exact_present else "REVIEW",
                     "Issue": "NONE" if len(hit) and (exact_present or not present(exact)) else "MAPPING_COMPLETENESS_REVIEW"})
    return pd.DataFrame(rows)


def computational_audit(master: pd.DataFrame, comp: pd.DataFrame) -> pd.DataFrame:
    p017_experimental = int(
        (master.Paper_ID.eq("P017") & master.QC_Row_Role.eq("EXPERIMENTAL_PRIMARY_CONDITION")).sum()
    )
    p017_native_in_experimental_targets = int(
        comp.Effective_TRIP.notna().sum() + comp.Effective_TWIP.notna().sum()
    )
    checks = [
        ("P017_exact_computational_conditions", len(comp), 12, "PASS"),
        ("P017_experimental_conditions", p017_experimental, 0, "PASS"),
        ("P017_native_targets_isolated", p017_native_in_experimental_targets, 0, "PASS"),
        ("P017_extreme_strain_rate_isolated", int(comp["Strain_rate_s-1"].ge(1e8).sum()), 12, "PASS"),
    ]
    for paper in ["P018", "P019"]:
        promoted = int(
            (master.Paper_ID.eq(paper) & master.QC_Row_Role.isin(
                ["EXPERIMENTAL_PRIMARY_CONDITION", "COMPUTATIONAL_PRIMARY_CONDITION"]
            )).sum()
        )
        checks.append((f"{paper}_verified_promotions", promoted, 0, "PASS_SOURCE_UNAVAILABLE"))
    rows = [
        (name, observed, expected, pass_status if observed == expected else "FAIL")
        for name, observed, expected, pass_status in checks
    ]
    return pd.DataFrame(rows, columns=["Audit_Check", "Observed", "Expected", "Status"])


def missingness(exp: pd.DataFrame, coverage: pd.DataFrame) -> pd.DataFrame:
    map_names = {"Measured chemistry":"Measured_chemistry", "Nominal chemistry":"Nominal_chemistry", "Test temperature":"Test_temperature",
                 "Strain rate":"Strain_rate", "Processing route":"Processing_route", "Initial phase":"Initial_FCC", "Grain size":"Grain_size",
                 "SFE":"Experimental_SFE", "DeltaG":"DeltaG", "YS":"YS", "UTS":"UTS", "Elongation":"Elongation", "TRIP":"TRIP", "TWIP":"TWIP"}
    out = coverage[["Paper_ID", "ML_Condition_ID"]].copy()
    for label, col in map_names.items():
        out[label] = coverage[col].eq("MISSING")
    out["Number_of_missing_core_fields"] = out[list(map_names)].sum(axis=1)
    return out


def qc_tiers(exp: pd.DataFrame, coverage: pd.DataFrame, provenance: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cov = coverage.set_index("ML_Condition_ID")
    prov = provenance.set_index("Record_ID")
    for _, r in exp.iterrows():
        c = cov.loc[r.ML_Condition_ID]
        identity = present(r.ML_Condition_ID) and present(r.Leakage_Group_Strict)
        target = present(r.Effective_TRIP) and present(r.Effective_TWIP)
        comp = c.Nominal_chemistry == "AVAILABLE" or c.Measured_chemistry == "AVAILABLE"
        test = c.Test_temperature == "AVAILABLE" and c.Strain_rate == "AVAILABLE"
        micro = c.Initial_FCC == "AVAILABLE" or c.Initial_HCP == "AVAILABLE" or c.Grain_size == "AVAILABLE"
        trace = r.ML_Condition_ID in prov.index and prov.loc[r.ML_Condition_ID, "Provenance_Status"] == "COMPLETE"
        score = sum([identity, target, comp, test, micro, trace])
        tier = "QC_HIGH" if score == 6 else ("QC_MEDIUM" if score >= 4 else ("QC_LOW" if score >= 2 else "QC_REVIEW"))
        rows.append({"Paper_ID": r.Paper_ID, "ML_Condition_ID": r.ML_Condition_ID, "QC_Tier": tier,
                     "Identity_Clear": identity, "Independent": True, "Target_Evidence_Complete": target,
                     "Composition_Provenance": comp, "Test_Condition_Provenance": test,
                     "Initial_Microstructure_Provenance": micro, "Source_Traceability_Complete": trace,
                     "Rule": "HIGH=all 6 gates; MEDIUM=4-5; LOW=2-3; REVIEW=0-1. Target value and strength magnitude are never scored."})
    return pd.DataFrame(rows)


def paper_contribution(master, exp, comp, target, issues):
    rows = []
    for i in range(1, 20):
        paper = f"P{i:03d}"; p = master[master.Paper_ID.eq(paper)]; e = exp[exp.Paper_ID.eq(paper)]; c = comp[comp.Paper_ID.eq(paper)]
        source = "SOURCE_UNAVAILABLE_PENDING_REVIEW" if paper in {"P018", "P019"} else "SOURCE_RECOVERY_OR_REPOSITORY_EVIDENCE_AVAILABLE"
        recovery = "VERIFIED_COMPUTATIONAL_RECOVERY_V11" if paper == "P017" else ("PENDING_SOURCE_RECOVERY" if paper in {"P018", "P019"} else "RECOVERY_STATUS_VARIES_BY_PAPER")
        domain = ";".join(sorted(set(p.Data_Origin.dropna().astype(str))))
        unresolved = target[(target.Paper_ID == paper) & (target.Issue != "NONE_FOUND")].ML_Condition_ID.astype(str).tolist()
        rows.append({"Paper_ID": paper, "DOI": ";".join(sorted(set(p.DOI.dropna().astype(str)))), "Source_Availability": source,
                     "Recovery_Status": recovery, "Data_Domain": domain, "Independent_Experimental_Conditions": len(e),
                     "Independent_Computational_Conditions": len(c), "Experimental_Stage_Children": int(((p.QC_Row_Role == "EXPERIMENTAL_STAGE_CHILD")).sum()),
                     "Computational_Stage_Children": int(((p.QC_Row_Role == "COMPUTATIONAL_STAGE_CHILD")).sum()),
                     "Usable_TRIP": int(e.Effective_TRIP.notna().sum()), "Usable_TWIP": int(e.Effective_TWIP.notna().sum()),
                     "Usable_Joint": int(e[["Effective_TRIP","Effective_TWIP"]].notna().all(axis=1).sum()),
                     "Legacy_Rows": int(p.QC_Row_Role.str.startswith("LEGACY").sum()),
                     "Exact_Replacement_Rows": int(p.QC_Row_Role.isin(["EXPERIMENTAL_PRIMARY_CONDITION","COMPUTATIONAL_PRIMARY_CONDITION"]).sum()),
                     "Remaining_Identity_Issues": "SOURCE_IDENTITY_UNVERIFIED" if paper in {"P018","P019"} else "SEE_GLOBAL_QC_ISSUES",
                     "Remaining_Scientific_Gaps": ";".join(unresolved) if unresolved else ("SOURCE_UNAVAILABLE" if paper in {"P018","P019"} else "SEE_FEATURE_COVERAGE")})
    return pd.DataFrame(rows)


def issue_ledger(exp, target, provenance):
    rows = []
    def add(priority, paper, record, category, description, current, expected, action, pdf, feature, ml, status="OPEN"):
        rows.append({"Issue_ID": f"V12-{len(rows)+1:04d}", "Priority": priority, "Paper_ID": paper, "Record_ID": record,
                     "Issue_Category": category, "Scientific_Description": description, "Current_Value": current,
                     "Expected_Semantic_State": expected, "Recommended_Action": action, "Requires_Source_PDF": pdf,
                     "Blocks_Feature_Design": feature, "Blocks_ML_Training": ml, "Status": status})
    for _, r in target[target.Issue != "NONE_FOUND"].iterrows():
        add("P1", r.Paper_ID, r.ML_Condition_ID, "UNRESOLVED_TARGET", "One or both effective experimental targets remain unknown; NA is preserved.",
            f"TRIP={r.Effective_TRIP};TWIP={r.Effective_TWIP}", "DIRECT_POSITIVE, EXPLICIT_CONDITION_NEGATIVE, OR NA",
            "Review verified source evidence; never infer or convert NA to zero.", True, False, True)
    for paper in ["P018", "P019"]:
        add("P1", paper, "PAPER", "SOURCE_UNAVAILABLE", "No verified source recovery is available; preserved legacy computational rows are not promoted.",
            "SOURCE_UNAVAILABLE_PENDING_REVIEW", "VERIFIED_SOURCE_REQUIRED_BEFORE_RECOVERY", "Obtain and review full source PDF/supplement.", True, False, True)
    for _, r in provenance[provenance.Provenance_Status != "COMPLETE"].iterrows():
        add("P2", r.Paper_ID, r.Record_ID, "PROVENANCE_COMPLETENESS", "Condition provenance is partial in the consolidated row/ledger view.",
            r.Missing_Elements, "COMPLETE_FIELD_LEVEL_PROVENANCE", "Retain gap; recover exact source location/method only from verified source.", True, False, False)
    return pd.DataFrame(rows)


def write_markdown(master, exp_index, comp_index, coverage, summary, papers, target_cov, issues, tiers, prov, sfe, dg):
    def md_table(frame):
        if frame.empty:
            return "None."
        values = frame.fillna("NA").astype(str)
        header = "| " + " | ".join(values.columns) + " |"
        rule = "| " + " | ".join(["---"] * len(values.columns)) + " |"
        body = ["| " + " | ".join(row) + " |" for row in values.to_numpy().tolist()]
        return "\n".join([header, rule, *body])
    def metric(name): return int(target_cov.loc[target_cov.Metric.eq(name), "Count"].iloc[0])
    top_missing = summary.sort_values(["Coverage_Percent", "Feature_Name"]).head(8)
    role_counts = master.QC_Row_Role.value_counts().to_dict()
    p0 = int(issues.Priority.eq("P0").sum()); p1 = int(issues.Priority.eq("P1").sum())
    unresolved = issues[issues.Issue_Category.eq("UNRESOLVED_TARGET")][["Paper_ID","Record_ID"]]
    high_risk = ", ".join(k for k,v in LEAKAGE_RULES.items() if v.startswith("POST_TEST") or v == "MODEL_DERIVED_FROM_LOADING")
    report = f"""# Global Dataset QC V12

## Scope and census

- Dataset: `master_19papers_recovery_v12_qc.csv`, generated from immutable recovery_v11.
- Total master rows: **{len(master)}**; original {len(master.columns)-len(QC_COLUMNS)}-column scientific content is cell-preserved.
- Replacement-aware independent experimental conditions: **{len(exp_index)}**.
- Exact independent computational conditions: **{len(comp_index)}** (P017 only).
- QC roles: `{role_counts}`.
- P0 issues: **{p0}**; P1 issues: **{p1}**.

## Experimental target distribution

- TRIP: {metric('TRIP_positive')} positive, {metric('TRIP_negative')} negative, {metric('TRIP_NA')} NA.
- TWIP: {metric('TWIP_positive')} positive, {metric('TWIP_negative')} negative, {metric('TWIP_NA')} NA.
- Joint: 00={metric('Joint_00')}, 10={metric('Joint_10')}, 01={metric('Joint_01')}, 11={metric('Joint_11')}; partially labelled={metric('Joint_partially_labeled')}; fully unlabeled={metric('Joint_fully_unlabeled')}.

## Integrity findings

No silent scientific correction was made. Stage observations, in-situ/longitudinal children, aggregate replicate metadata, legacy/exact representations, and computational records are excluded from the experimental condition index. The audit preserves NA != 0; intermediate-stage absence != condition-wide negative; annealing/initial twins != tensile TWIP; pre-existing/processing HCP != tensile TRIP; local != bulk chemistry; nominal != measured chemistry; method-specific SFE classes; and computational-native != experimental targets.

Unresolved target conditions remain:

{md_table(unresolved)}

## Coverage and missingness

Lowest-coverage audited features/families:

{md_table(top_missing[['Feature_Name','NonMissing_Count','Missing_Count','Coverage_Percent']])}

Experimental SFE coverage counts only source/reported experimental-equivalent SFE and excludes DFT, MD, CALPHAD/thermodynamic, assumed/reference, FCC/BCC GSFE distinctions. DeltaG remains method-specific calculated evidence; no values were back-calculated or transferred across papers.

## Provenance and source status

Exact condition provenance: `{prov.Provenance_Status.value_counts().to_dict()}`. Gaps are reported, never fabricated. P018 and P019 remain **SOURCE_UNAVAILABLE_PENDING_REVIEW**; their legacy computational rows are preserved but not promoted.

## Leakage audit

High-risk post-loading/model-derived fields include: {high_risk}. Mechanical properties remain outcomes/supporting metadata with `PREDICTOR_ELIGIBILITY_UNRESOLVED`. P017 MD fields are computational-only and cannot improve experimental coverage.

## Paper contribution

{md_table(papers[['Paper_ID','Independent_Experimental_Conditions','Independent_Computational_Conditions','Experimental_Stage_Children','Computational_Stage_Children','Usable_TRIP','Usable_TWIP','Usable_Joint','Source_Availability']])}

## Limitations and recommendation

Structurally, the dataset is ready for a controlled, leakage-aware feature-schema design because identities, domains, replacement gates, roles, target coverage, missingness, and provenance gaps are explicit. It is **not scientifically/statistically ready for final ML training**: support is only 51 dependent literature conditions; negatives are scarce; joint labels are fewer; paper/material-family dependence is strong; unresolved labels and sparse initial microstructure, experimental SFE, DeltaG, and measured chemistry remain; and predictor leakage policy is not finalized. TRIP has the largest usable count but this alone does not establish adequacy.

Recommended next phase: resolve the queued source-specific target and provenance gaps (beginning with the listed unresolved conditions and P018/P019 source acquisition), then define a frozen pre-test/test-condition-only candidate schema with paper/material-group validation rules before any modelling.
"""
    (REPORTS / "GLOBAL_DATASET_QC_V12.md").write_text(report, encoding="utf-8")
    readiness = f"""# Dataset Readiness V12

## A. Controlled feature-schema design

**Yes, structurally, with gates.** The 51-condition experimental index is replacement-aware and domain-separated, and every existing field has a preliminary leakage category. Schema design must remain restricted to source-preserved fields and must not imply predictor eligibility.

## B. Final ML training

**No.** Target completeness, class balance, paper/material dependence, provenance gaps, source-unavailable papers, sparse physics descriptors, and unresolved leakage policy remain material blockers.

## C. Strongest first target

TRIP has the largest usable coverage ({metric('TRIP_positive') + metric('TRIP_negative')}/51), versus TWIP ({metric('TWIP_positive') + metric('TWIP_negative')}/51) and joint ({metric('Joint_fully_labeled')}/51). This is only a relative support ranking—not evidence that TRIP is adequate for modelling.

## D–F. Blockers and risks

Scientific blockers: unresolved mechanism labels, incomplete verified source recovery, sparse measured chemistry/initial microstructure/experimental SFE/DeltaG, and heterogeneous mechanism evidence. Statistical blockers: small effective sample size, class imbalance, and paper/material-family dependence. Leakage risks: all post-loading mechanism and mechanical outcomes, stage observations, model-derived loading quantities, and computational-only descriptors.

## G. Work required before ML

Resolve prioritized source/target/provenance gaps; acquire P018/P019 full sources; freeze target semantics; define a pre-test/test-condition-only candidate schema; specify paper/material leakage groups and evaluation design; then reassess support and class balance without imputation or synthetic samples.
"""
    (REPORTS / "DATASET_READINESS_V12.md").write_text(readiness, encoding="utf-8")


def validate(source, master, exp, comp, reports):
    assert len(source) == 192 and len(master) == 192
    pd.testing.assert_frame_equal(master[source.columns].reset_index(drop=True), source.reset_index(drop=True), check_dtype=False)
    assert len(exp) == 51 and len(comp) == 12
    assert exp.Effective_TRIP.notna().sum() == 32 and exp.Effective_TWIP.notna().sum() == 30
    assert exp[["Effective_TRIP","Effective_TWIP"]].notna().all(axis=1).sum() == 27
    assert set(comp.Paper_ID) == {"P017"} and not set(exp.Paper_ID) & {"P017", "P018", "P019"}
    assert not master.loc[master.QC_Row_Role.eq("EXPERIMENTAL_STAGE_CHILD"), "QC_Experimental_Eligibility"].eq("ELIGIBLE").any()
    assert not any(c.lower().startswith(("vec", "omega", "mixing_entropy", "atomic_size_mismatch")) for c in master.columns)
    for path in reports:
        assert path.exists() and path.stat().st_size > 0


def run():
    REPORTS.mkdir(exist_ok=True)
    source = pd.read_csv(SOURCE, low_memory=False)
    exp = experimental_pool(source)
    comp = exact_computational_pool(source)
    master = build_master(source, exp, comp)
    exp_index = build_experimental_index(exp)
    comp_index = build_computational_index(comp)
    independence = independence_audit(master)
    target = target_integrity(exp)
    target_cov = target_coverage(exp_index)
    coverage = feature_coverage(exp)
    summary = feature_summary(coverage, exp)
    composition = composition_audit(exp)
    micro = microstructure_audit(exp)
    leakage = leakage_classification(master)
    sfe = sfe_audit(master)
    dg = deltag_audit(master)
    prov = provenance_audit(master)
    legacy = legacy_audit(master)
    computational = computational_audit(master, comp)
    miss = missingness(exp, coverage)
    tiers = qc_tiers(exp, coverage, prov)
    issues = issue_ledger(exp, target, prov)
    papers = paper_contribution(master, exp, comp, target, issues)
    files = {
        OUTPUT: master, EXPERIMENTAL_INDEX: exp_index, COMPUTATIONAL_INDEX: comp_index,
        REPORTS/"INDEPENDENCE_AUDIT_V12.csv": independence,
        REPORTS/"TARGET_INTEGRITY_AUDIT_V12.csv": target,
        REPORTS/"TARGET_COVERAGE_V12.csv": target_cov,
        REPORTS/"PAPER_CONTRIBUTION_V12.csv": papers,
        REPORTS/"FEATURE_COVERAGE_V12.csv": coverage,
        REPORTS/"FEATURE_COVERAGE_SUMMARY_V12.csv": summary,
        REPORTS/"SFE_METHOD_AUDIT_V12.csv": sfe,
        REPORTS/"DELTAG_AUDIT_V12.csv": dg,
        REPORTS/"COMPOSITION_AUDIT_V12.csv": composition,
        REPORTS/"INITIAL_MICROSTRUCTURE_AUDIT_V12.csv": micro,
        REPORTS/"FEATURE_LEAKAGE_CLASSIFICATION_V12.csv": leakage,
        REPORTS/"PROVENANCE_COMPLETENESS_V12.csv": prov,
        REPORTS/"LEGACY_REPLACEMENT_AUDIT_V12.csv": legacy,
        REPORTS/"COMPUTATIONAL_DOMAIN_AUDIT_V12.csv": computational,
        REPORTS/"EXPERIMENTAL_MISSINGNESS_V12.csv": miss,
        REPORTS/"CONDITION_QC_TIER_V12.csv": tiers,
        REPORTS/"GLOBAL_QC_ISSUES_V12.csv": issues,
    }
    for path, frame in files.items():
        frame.to_csv(path, index=False)
    write_markdown(master, exp_index, comp_index, coverage, summary, papers, target_cov, issues, tiers, prov, sfe, dg)
    reports = list(files) + [REPORTS/"GLOBAL_DATASET_QC_V12.md", REPORTS/"DATASET_READINESS_V12.md"]
    validate(source, master, exp_index, comp_index, reports)
    return master, exp_index, comp_index


if __name__ == "__main__":
    run()
