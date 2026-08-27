"""Design and audit leakage-safe grouped train/validation splits V1.

This module performs split design and descriptive feasibility analysis only.  Its
atomic roster is the replacement-aware 51-row experimental condition index.  It
does not construct a predictor matrix, reconcile chemistry, fill missing values,
transform features, resample conditions, train a model, or calculate a model
performance metric.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations
from math import ceil, floor
from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
SCHEMA = DATA / "schema"
SPLITS = DATA / "splits"
REPORTS = ROOT / "reports"

EXPERIMENTAL_INDEX_PATH = PROCESSED / "experimental_condition_index_v12.csv"
COMPUTATIONAL_INDEX_PATH = PROCESSED / "computational_condition_index_v12.csv"
MASTER_PATH = PROCESSED / "master_19papers_recovery_v12_qc.csv"
RECOVERY_SOURCE_PATH = PROCESSED / "master_19papers_recovery_v11.csv"

FEATURE_SCHEMA_PATH = SCHEMA / "feature_schema_v1.csv"
FEATURE_SETS_PATH = SCHEMA / "feature_sets_v1.csv"
FEATURE_PRIORITY_PATH = SCHEMA / "feature_priority_v1.csv"
DOMAIN_MANIFEST_PATH = SCHEMA / "domain_manifest_v1.csv"
FEATURE_COVERAGE_PATH = REPORTS / "FEATURE_SET_COVERAGE_V1.csv"
TARGET_FEATURE_PATH = REPORTS / "TARGET_FEATURE_AVAILABILITY_V1.csv"
LEAKAGE_POLICY_PATH = REPORTS / "PREDICTION_TIME_LEAKAGE_POLICY_V1.md"
FEATURE_AUDIT_PATH = REPORTS / "FEATURE_SCHEMA_V1_AUDIT.md"
GLOBAL_QC_AUDIT_PATH = REPORTS / "GLOBAL_DATASET_QC_V12.md"

GROUP_DISTRIBUTION_PATH = REPORTS / "GROUP_TARGET_DISTRIBUTION_V1.csv"
CLASS_SUPPORT_PATH = REPORTS / "CLASS_SUPPORT_BY_GROUP_V1.csv"
GROUPING_KEY_PATH = REPORTS / "CONDITION_GROUPING_KEY_AUDIT_V1.csv"
M2_SUPPORT_PATH = REPORTS / "M2_COMPLETE_CASE_SUPPORT_V1.csv"
NEGATIVE_AUDIT_PATH = REPORTS / "NEGATIVE_CLASS_AUDIT_V1.csv"
POSITIVE_FAMILY_PATH = REPORTS / "POSITIVE_CLASS_FAMILY_AUDIT_V1.csv"
GENERALIZATION_PATH = REPORTS / "GENERALIZATION_FEASIBILITY_V1.csv"
CHEMISTRY_POLICY_PATH = REPORTS / "CHEMISTRY_SOURCE_POLICY_V1.md"
ARCHITECTURE_PATH = REPORTS / "VALIDATION_ARCHITECTURE_V1.md"
DESIGN_AUDIT_PATH = REPORTS / "SPLIT_DESIGN_V1_AUDIT.md"
SPLIT_CANDIDATES_PATH = SPLITS / "split_candidates_v1.csv"
SPLIT_MANIFEST_PATH = SPLITS / "split_manifest_v1.csv"

INPUT_PATHS = (
    EXPERIMENTAL_INDEX_PATH,
    MASTER_PATH,
    FEATURE_SCHEMA_PATH,
    FEATURE_SETS_PATH,
    FEATURE_PRIORITY_PATH,
    DOMAIN_MANIFEST_PATH,
    FEATURE_COVERAGE_PATH,
    TARGET_FEATURE_PATH,
    LEAKAGE_POLICY_PATH,
    FEATURE_AUDIT_PATH,
    GLOBAL_QC_AUDIT_PATH,
)

FEATURE_SET_ORDER = (
    "M1_CHEMISTRY",
    "M2_CHEMISTRY_PLUS_TEST",
    "M3_PLUS_PROCESSING",
    "M4_PLUS_PHYSICS",
    "M5_PLUS_INITIAL_MICROSTRUCTURE",
)

QUALITY_FLAGS = {
    "VALID_STRONG",
    "VALID_LIMITED",
    "EXPLORATORY_ONLY",
    "INVALID_GROUP_LEAKAGE",
    "INVALID_CLASS_SUPPORT",
    "INVALID_SAMPLE_SUPPORT",
}

GROUP_LEVELS = (
    ("Paper_ID", "Paper_ID"),
    ("Study_Series_ID", "Effective_Study_Group"),
    ("Material_Parent_ID", "Effective_Material_Group"),
    ("Physical_Batch_ID", "Effective_Batch_Group"),
    ("Leakage_Group_Strict", "Effective_Strict_Group"),
    ("Leakage_Group_Material", "Effective_Leakage_Material_Group"),
)

CANDIDATE_COLUMNS = [
    "Target",
    "Split_ID",
    "Split_Strategy",
    "Grouping_Level",
    "Train_Condition_Count",
    "Validation_Condition_Count",
    "Train_Group_Count",
    "Validation_Group_Count",
    "Train_Positive",
    "Train_Negative",
    "Validation_Positive",
    "Validation_Negative",
    "Both_Classes_Train",
    "Both_Classes_Validation",
    "Group_Overlap",
    "Paper_Overlap",
    "Study_Overlap",
    "Material_Overlap",
    "Source_Alloy_Family_Overlap",
    "Strict_Leakage_Overlap",
    "Feature_Set",
    "Feature_Complete_Train",
    "Feature_Complete_Validation",
    "Scientific_Validity",
    "Statistical_Limitation",
    "Recommended_Status",
    "Notes",
    "Number_of_Folds",
    "Fold_Number",
    "Design_Feasibility",
    "Validation_Group_IDs",
    "Feature_Complete_Train_Positive",
    "Feature_Complete_Train_Negative",
    "Feature_Complete_Validation_Positive",
    "Feature_Complete_Validation_Negative",
    "Train_TRIP_Positive",
    "Train_TRIP_Negative",
    "Validation_TRIP_Positive",
    "Validation_TRIP_Negative",
    "Train_TWIP_Positive",
    "Train_TWIP_Negative",
    "Validation_TWIP_Positive",
    "Validation_TWIP_Negative",
    "Train_00",
    "Train_10",
    "Train_01",
    "Train_11",
    "Validation_00",
    "Validation_10",
    "Validation_01",
    "Validation_11",
]


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def present(value) -> bool:
    if pd.isna(value):
        return False
    return str(value).strip() not in {"", "NA", "N/A", "nan", "None", "<NA>"}


def present_mask(series: pd.Series) -> pd.Series:
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        text = series.astype("string").str.strip()
        return series.notna() & ~text.isin(["", "NA", "N/A", "nan", "None", "<NA>"])
    return series.notna()


def joined(values, empty: str = "NONE_REPORTED") -> str:
    cleaned = sorted({str(value).strip() for value in values if present(value)})
    return "|".join(cleaned) if cleaned else empty


def safe_token(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_")


def state_series(frame: pd.DataFrame) -> pd.Series:
    complete = frame[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1)
    result = pd.Series(pd.NA, index=frame.index, dtype="string")
    result.loc[complete] = (
        frame.loc[complete, "Effective_TRIP"].astype(int).astype(str)
        + frame.loc[complete, "Effective_TWIP"].astype(int).astype(str)
    )
    return result


def complete_mask(frame: pd.DataFrame, fields: list[str]) -> pd.Series:
    result = pd.Series(True, index=frame.index)
    for field in fields:
        result &= present_mask(frame[field])
    return result


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]], dict[Path, str]]:
    before = {path: digest(path) for path in INPUT_PATHS}
    index = pd.read_csv(EXPERIMENTAL_INDEX_PATH)
    master = pd.read_csv(MASTER_PATH, low_memory=False)
    schema = pd.read_csv(FEATURE_SCHEMA_PATH)
    feature_sets = pd.read_csv(FEATURE_SETS_PATH)
    priority = pd.read_csv(FEATURE_PRIORITY_PATH)
    domain = pd.read_csv(DOMAIN_MANIFEST_PATH)
    coverage = pd.read_csv(FEATURE_COVERAGE_PATH)
    target_coverage = pd.read_csv(TARGET_FEATURE_PATH)

    assert len(index) == 51 and index.ML_Condition_ID.is_unique
    assert index.Independent_ML_sample.astype(str).str.lower().eq("true").all()
    assert not set(index.Paper_ID) & {"P017", "P018", "P019"}
    primary = master.loc[master.QC_Row_Role.eq("EXPERIMENTAL_PRIMARY_CONDITION")].copy()
    assert len(primary) == 51 and primary.ML_Condition_ID.is_unique
    assert set(primary.ML_Condition_ID) == set(index.ML_Condition_ID)

    conditions = index[["Paper_ID", "ML_Condition_ID"]].merge(
        primary, on=["Paper_ID", "ML_Condition_ID"], how="left", validate="one_to_one"
    )
    assert len(conditions) == 51 and conditions.Observation_ID.notna().all()
    index_by_id = index.set_index("ML_Condition_ID")
    conditions_by_id = conditions.set_index("ML_Condition_ID")
    for field in (
        "Paper_ID",
        "Study_Series_ID",
        "Material_Parent_ID",
        "Physical_Batch_ID",
        "Leakage_Group_Strict",
        "Leakage_Group_Material",
        "Effective_TRIP",
        "Effective_TWIP",
    ):
        left = index_by_id[field]
        right = conditions_by_id[field]
        assert left.fillna("__NA__").astype(str).equals(right.fillna("__NA__").astype(str)), field

    assert len(schema) == 343 and schema.Column_Name.is_unique
    assert set(schema.Column_Name) == set(master.columns)
    assert set(priority.Column_Name) == set(master.columns)
    assert list(coverage.Feature_Set) == list(FEATURE_SET_ORDER)
    assert coverage.Complete_Case_Count.tolist() == [40, 31, 31, 31, 26]
    first = target_coverage.groupby("Target", sort=False).first()
    assert first.loc["TRIP", ["Target_Usable_Conditions", "Target_Positive", "Target_Negative"]].tolist() == [32, 27, 5]
    assert first.loc["TWIP", ["Target_Usable_Conditions", "Target_Positive", "Target_Negative"]].tolist() == [30, 24, 6]
    assert first.loc["JOINT", "Target_Usable_Conditions"] == 27
    assert domain.set_index("Dataset_Domain").loc["EXPERIMENTAL_PRIMARY", "Current_Row_Count"] == 51
    assert domain.set_index("Dataset_Domain").loc["COMPUTATIONAL_PRIMARY", "Current_Row_Count"] == 12

    policy = LEAKAGE_POLICY_PATH.read_text(encoding="utf-8")
    feature_audit = FEATURE_AUDIT_PATH.read_text(encoding="utf-8")
    qc_audit = GLOBAL_QC_AUDIT_PATH.read_text(encoding="utf-8")
    assert "immediately before tensile loading begins" in policy.lower()
    assert "M2_CHEMISTRY_PLUS_TEST is the recommended schema baseline" in policy
    assert "Proceed only to grouped train/validation split design" in feature_audit
    assert "TRIP: 27 positive, 5 negative, 19 NA" in qc_audit
    assert "TWIP: 24 positive, 6 negative, 21 NA" in qc_audit

    core_by_set: dict[str, list[str]] = {}
    master_order = {name: order for order, name in enumerate(master.columns)}
    for feature_set in FEATURE_SET_ORDER:
        fields = feature_sets.loc[
            feature_sets.Feature_Set.eq(feature_set)
            & feature_sets.Eligibility_Status.eq("CANDIDATE_CORE_V1"),
            "Column_Name",
        ].tolist()
        core_by_set[feature_set] = sorted(set(fields), key=master_order.get)
    assert core_by_set["M1_CHEMISTRY"] == ["Fe_at%", "Mn_at%", "Co_at%", "Cr_at%"]
    assert core_by_set["M2_CHEMISTRY_PLUS_TEST"] == [
        "Fe_at%", "Mn_at%", "Co_at%", "Cr_at%", "Test_T_K", "Strain_rate_s-1"
    ]

    conditions["Condition_Order"] = range(len(conditions))
    conditions["Effective_Study_Group"] = [
        value if present(value) else f"PAPER_FALLBACK::{paper}"
        for value, paper in zip(conditions.Study_Series_ID, conditions.Paper_ID)
    ]
    conditions["Effective_Material_Group"] = [
        leakage if present(leakage) else material if present(material) else f"PAPER_FALLBACK::{paper}"
        for leakage, material, paper in zip(
            conditions.Leakage_Group_Material, conditions.Material_Parent_ID, conditions.Paper_ID
        )
    ]
    conditions["Effective_Leakage_Material_Group"] = conditions["Effective_Material_Group"]
    conditions["Effective_Strict_Group"] = [
        leakage if present(leakage) else study if present(study) else f"PAPER_FALLBACK::{paper}"
        for leakage, study, paper in zip(
            conditions.Leakage_Group_Strict, conditions.Study_Series_ID, conditions.Paper_ID
        )
    ]
    conditions["Effective_Batch_Group"] = [
        batch if present(batch) else f"MATERIAL_FALLBACK::{material}"
        for batch, material in zip(conditions.Physical_Batch_ID, conditions.Effective_Material_Group)
    ]
    conditions["Strict_Group_Source"] = [
        "Leakage_Group_Strict" if present(leakage)
        else "Study_Series_ID" if present(study)
        else "Paper_ID_FALLBACK"
        for leakage, study in zip(conditions.Leakage_Group_Strict, conditions.Study_Series_ID)
    ]
    conditions["Alloy_Family_ID"] = [
        f"SOURCE_COMPOSITION_TEXT::{composition}" if present(composition)
        else f"SOURCE_NOMINAL_TEXT::{nominal}" if present(nominal)
        else f"MATERIAL_PARENT::{material}" if present(material)
        else f"SOURCE_ALLOY_ID::{alloy}" if present(alloy)
        else f"PAPER_FALLBACK::{paper}"
        for composition, nominal, material, alloy, paper in zip(
            conditions.Original_Composition,
            conditions.Nominal_Composition_at_pct,
            conditions.Material_Parent_ID,
            conditions.Alloy_ID,
            conditions.Paper_ID,
        )
    ]
    conditions["Joint_State"] = state_series(conditions)
    conditions["M2_Complete"] = complete_mask(conditions, core_by_set["M2_CHEMISTRY_PLUS_TEST"])
    return conditions, master, core_by_set, before


def build_grouping_key_audit(conditions: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "Paper_ID", "ML_Condition_ID", "Study_Series_ID", "Material_Parent_ID",
        "Physical_Batch_ID", "Leakage_Group_Strict", "Leakage_Group_Material",
        "Effective_Study_Group", "Effective_Material_Group", "Effective_Batch_Group",
        "Effective_Strict_Group", "Effective_Leakage_Material_Group", "Strict_Group_Source",
        "Alloy_Family_ID",
    ]
    out = conditions[columns].copy()
    out["Safest_Grouping_Level"] = "Leakage_Group_Strict_WITH_PAPER_FALLBACK"
    out["Safest_Group_ID"] = conditions.Effective_Strict_Group
    out["Fallback_Reason"] = [
        "EXPLICIT_STRICT_GROUP_AVAILABLE" if source == "Leakage_Group_Strict"
        else "STUDY_SERIES_USED_AS_STRICT_GROUP" if source == "Study_Series_ID"
        else "STRICT_STUDY_AND_MATERIAL_KEYS_MISSING; CONSERVATIVE_PAPER_FALLBACK"
        for source in conditions.Strict_Group_Source
    ]
    out["Notes"] = (
        "Fallback identifiers are split-control surrogates only; they do not assert physical batch identity "
        "or alter source hierarchy fields. Paper_ID is the universally observed outer boundary."
    )
    return out


def group_counts(group: pd.DataFrame) -> dict[str, int]:
    trip = group.Effective_TRIP
    twip = group.Effective_TWIP
    joint = group.Joint_State
    return {
        "Number_of_Conditions": len(group),
        "TRIP_Usable": int(trip.notna().sum()),
        "TRIP_Positive": int(trip.eq(1).sum()),
        "TRIP_Negative": int(trip.eq(0).sum()),
        "TWIP_Usable": int(twip.notna().sum()),
        "TWIP_Positive": int(twip.eq(1).sum()),
        "TWIP_Negative": int(twip.eq(0).sum()),
        "Joint_Usable": int(joint.notna().sum()),
        "Joint_00": int(joint.eq("00").sum()),
        "Joint_10": int(joint.eq("10").sum()),
        "Joint_01": int(joint.eq("01").sum()),
        "Joint_11": int(joint.eq("11").sum()),
    }


def build_group_distribution(conditions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for level, field in GROUP_LEVELS:
        raw_missing_field = level if level in conditions.columns else None
        for group_id, group in conditions.groupby(field, sort=True, dropna=False):
            row = {"Grouping_Level": level, "Group_ID": group_id, **group_counts(group)}
            row["Papers"] = joined(group.Paper_ID)
            row["Material_Parents"] = joined(group.Material_Parent_ID)
            missing = int(group[raw_missing_field].isna().sum()) if raw_missing_field else 0
            if level == "Physical_Batch_ID":
                note = (
                    f"{missing}/{len(group)} source batch IDs missing; conservative material/paper fallback used. "
                    "No physical batch was inferred."
                )
            elif str(group_id).startswith(("PAPER_FALLBACK::", "MATERIAL_FALLBACK::")):
                note = (
                    f"{missing}/{len(group)} source {level} values missing; fallback prevents within-paper/material splitting "
                    "without asserting a new scientific identity."
                )
            else:
                note = "Explicit source/reviewed hierarchy identifier."
            row["Notes"] = note
            rows.append(row)
    return pd.DataFrame(rows)


def target_subset(conditions: pd.DataFrame, target: str) -> tuple[pd.DataFrame, str]:
    field = "Effective_TRIP" if target == "T1_TRIP" else "Effective_TWIP"
    result = conditions.loc[conditions[field].notna()].copy()
    result["Target_Value_Internal"] = result[field].astype(int)
    return result, field


def support_flags(grouped: pd.core.groupby.DataFrameGroupBy, negative_groups: int, negative_count: int) -> str:
    flags = []
    if negative_groups == 1:
        flags.append("NEGATIVE_CLASS_SINGLE_GROUP")
    if negative_groups == 2:
        flags.append("NEGATIVE_CLASS_TWO_GROUPS")
    if negative_groups < 5 or negative_count < 10:
        flags.append("LOW_GROUP_SUPPORT")
    if negative_count:
        stats = []
        for _, group in grouped:
            negatives = int(group.Target_Value_Internal.eq(0).sum())
            positives = int(group.Target_Value_Internal.eq(1).sum())
            stats.append((negatives, positives))
        if any(negatives / negative_count >= 0.5 and positives == 0 for negatives, positives in stats):
            flags.append("CLASS_GROUP_CONFOUNDING")
    return "|".join(flags) if flags else "NONE"


def build_class_support(conditions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target in ("T1_TRIP", "T2_TWIP"):
        usable, _ = target_subset(conditions, target)
        populations = {
            "ALL_TARGET_USABLE": usable,
            "M2_CORE_COMPLETE": usable.loc[usable.M2_Complete],
        }
        for population, frame in populations.items():
            pos = frame.loc[frame.Target_Value_Internal.eq(1)]
            neg = frame.loc[frame.Target_Value_Internal.eq(0)]
            for level, field in GROUP_LEVELS:
                grouped = frame.groupby(field, sort=True, dropna=False)
                neg_group_sizes = neg.groupby(field).size()
                largest = int(neg_group_sizes.max()) if len(neg_group_sizes) else 0
                neg_groups = int(neg[field].nunique())
                rows.append(
                    {
                        "Target": target,
                        "Population": population,
                        "Grouping_Level": level,
                        "Positive_Conditions": len(pos),
                        "Negative_Conditions": len(neg),
                        "Total_Groups": int(frame[field].nunique()),
                        "Groups_Containing_Positives": int(pos[field].nunique()),
                        "Groups_Containing_Negatives": neg_groups,
                        "Material_Parents_Containing_Positives": int(pos.Effective_Material_Group.nunique()),
                        "Material_Parents_Containing_Negatives": int(neg.Effective_Material_Group.nunique()),
                        "Papers_Containing_Positives": int(pos.Paper_ID.nunique()),
                        "Papers_Containing_Negatives": int(neg.Paper_ID.nunique()),
                        "Largest_Negative_Group_Count": largest,
                        "Largest_Negative_Group_Share": round(largest / len(neg), 4) if len(neg) else 0.0,
                        "Flags": support_flags(grouped, neg_groups, len(neg)),
                        "Notes": (
                            "LOW_GROUP_SUPPORT is emitted when the negative class has fewer than five groups or ten conditions. "
                            "CLASS_GROUP_CONFOUNDING requires a class-pure group containing at least half of all negatives. "
                            "Effective fallback groups never invent batch identity."
                        ),
                    }
                )
    return pd.DataFrame(rows)


def build_m2_support(conditions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    definitions = {
        "T1_TRIP": (conditions.Effective_TRIP.notna(), conditions.Effective_TRIP.astype("Int64").astype("string")),
        "T2_TWIP": (conditions.Effective_TWIP.notna(), conditions.Effective_TWIP.astype("Int64").astype("string")),
        "T3_JOINT": (conditions.Joint_State.notna(), conditions.Joint_State),
    }
    for target, (usable, classes) in definitions.items():
        for class_value in sorted(classes.loc[usable].dropna().unique()):
            full = conditions.loc[usable & classes.eq(class_value)]
            complete = full.loc[full.M2_Complete]
            rows.append(
                {
                    "Target": target,
                    "Class_Value": class_value,
                    "Full_Usable_Conditions": len(full),
                    "M2_Complete_Conditions": len(complete),
                    "M2_Complete_Paper_Count": int(complete.Paper_ID.nunique()),
                    "M2_Complete_Papers": joined(complete.Paper_ID),
                    "M2_Complete_Study_Series_Count": int(complete.Effective_Study_Group.nunique()),
                    "M2_Complete_Study_Series": joined(complete.Effective_Study_Group),
                    "M2_Complete_Material_Parent_Count": int(complete.Effective_Material_Group.nunique()),
                    "M2_Complete_Material_Parents": joined(complete.Effective_Material_Group),
                    "Support_Flag": (
                        "NEGATIVE_CLASS_TWO_GROUPS" if target == "T1_TRIP" and class_value == "0" and complete.Effective_Strict_Group.nunique() == 2
                        else "LOW_GROUP_SUPPORT" if target in {"T1_TRIP", "T2_TWIP"} and class_value == "0" and complete.Effective_Strict_Group.nunique() < 5
                        else "LOW_CLASS_SUPPORT" if len(complete) < 5
                        else "LIMITED_BUT_DISTRIBUTED"
                    ),
                    "Notes": (
                        "M2 completeness is the raw intersection of Fe_at%, Mn_at%, Co_at%, Cr_at%, Test_T_K, and "
                        "Strain_rate_s-1. No chemistry reconciliation, missing-value filling, or matrix construction occurred."
                    ),
                }
            )
    return pd.DataFrame(rows)


def negative_evidence(row: pd.Series, target: str) -> tuple[str, str, str, str]:
    evidence = row.Evidence_TRIP if target == "TRIP" else row.Evidence_TWIP
    text = str(evidence).strip() if present(evidence) else ""
    lower = text.lower()
    initial_final = "NOT_RECORDED_AS_INITIAL_TO_FINAL_IN_CONSOLIDATED_MASTER"

    if target == "TRIP" and present(row.Negative_Evidence_Quality):
        initial_final = "YES_EXPLICIT_INITIAL_TO_FINAL_PHASE_EVIDENCE"
        return str(row.Negative_Evidence_Quality), "STRONG", initial_final, text or str(row.Postfracture_Phase_State)
    if target == "TWIP" and present(row.P011_Negative_TWIP_Evidence):
        return str(row.P011_Negative_TWIP_Evidence), "STRONG", initial_final, text
    if "initial single fcc" in lower and ("remains single fcc" in lower or "no hcp" in lower):
        initial_final = "YES_EXPLICIT_INITIAL_TO_FINAL_PHASE_EVIDENCE"
        return "DIRECT_INITIAL_TO_FINAL_PHASE_ABSENCE", "STRONG", initial_final, text
    if "without activation" in lower or "only deformation-induced phase transformation" in lower:
        return "DIRECT_CONDITION_WIDE_ABSENCE_STATEMENT", "STRONG", initial_final, text
    if "suppressed" in lower or "away from martensitic transformation" in lower:
        return "DIRECT_OR_COMPARATIVE_MECHANISM_SUPPRESSION", "MODERATE", initial_final, text
    if "short annealing times" in lower or "where activated" in lower:
        return "REVIEWED_CONDITION_LABEL_WITH_COMPARATIVE_OR_NONSPECIFIC_SUMMARY", "LIMITED", initial_final, text
    if not text:
        return "REVIEWED_EFFECTIVE_TARGET; EVIDENCE_TEXT_NOT_CARRIED_IN_CONSOLIDATED_FIELD", "LIMITED", initial_final, "NOT_CARRIED_IN_CONSOLIDATED_FIELD"
    return "REVIEWED_CONDITION_LEVEL_SOURCE_EVIDENCE", "MODERATE", initial_final, text


def build_negative_audit(conditions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in conditions.iterrows():
        for target, field in (("TRIP", "Effective_TRIP"), ("TWIP", "Effective_TWIP")):
            if row[field] != 0:
                continue
            evidence_type, strength, initial_final, evidence_text = negative_evidence(row, target)
            rows.append(
                {
                    "Paper_ID": row.Paper_ID,
                    "ML_Condition_ID": row.ML_Condition_ID,
                    "Material_Parent_ID": row.Material_Parent_ID,
                    "Test_T": row.Test_T_K,
                    "Strain_Rate": row["Strain_rate_s-1"],
                    "TRIP_Label": row.Effective_TRIP,
                    "TWIP_Label": row.Effective_TWIP,
                    "Negative_Target": target,
                    "Negative_Evidence_Type": evidence_type,
                    "Negative_Evidence_Strength": strength,
                    "Condition_Level_Negative": True,
                    "Initial_to_Final_Evidence": initial_final,
                    "Paper_Group": row.Paper_ID,
                    "Material_Group": row.Effective_Material_Group,
                    "Evidence_Text": evidence_text,
                    "Evidence_Location": row.Source_location,
                    "Negative_Origin_Check": (
                        "PASS_NO_LABEL_GENERATION_BY_SPLIT_TASK; INDEPENDENT_EXPERIMENTAL_CONDITION; NOT_STAGE; "
                        "NOT_LEGACY; NOT_COMPUTATIONAL; NOT_INITIAL_PHASE_ABSENCE_ALONE; "
                        + ("CONSOLIDATED_EVIDENCE_TEXT_GAP_RETAINED" if not present(evidence_text) or evidence_text == "NOT_CARRIED_IN_CONSOLIDATED_FIELD" else "SOURCE_EVIDENCE_TEXT_RETAINED")
                    ),
                    "Notes": (
                        "Target is copied unchanged from Effective_TRIP/Effective_TWIP. Strength audits the evidence text "
                        "available in the consolidated master and does not relabel the condition."
                    ),
                }
            )
    return pd.DataFrame(rows)


def build_positive_family_audit(conditions: pd.DataFrame) -> pd.DataFrame:
    levels = (
        ("PAPER", "Paper_ID"),
        ("STUDY_SERIES", "Effective_Study_Group"),
        ("MATERIAL_PARENT", "Effective_Material_Group"),
        ("ALLOY_FAMILY", "Alloy_Family_ID"),
    )
    rows = []
    for target, field in (("T1_TRIP", "Effective_TRIP"), ("T2_TWIP", "Effective_TWIP")):
        positives = conditions.loc[conditions[field].eq(1)]
        total = len(positives)
        for level, group_field in levels:
            for group_id, group in positives.groupby(group_field, sort=True):
                rows.append(
                    {
                        "Target": target,
                        "Concentration_Level": level,
                        "Group_ID": group_id,
                        "Positive_Conditions": len(group),
                        "Total_Positive_Conditions": total,
                        "Positive_Share": round(len(group) / total, 4),
                        "Papers": joined(group.Paper_ID),
                        "Study_Series": joined(group.Effective_Study_Group),
                        "Material_Parents": joined(group.Effective_Material_Group),
                        "Alloy_Families": joined(group.Alloy_Family_ID),
                        "Generalization_Interpretation": {
                            "PAPER": "G3_UNSEEN_STUDY_OR_PAPER_IF_HELD_OUT",
                            "STUDY_SERIES": "G3_UNSEEN_STUDY_IF_HELD_OUT",
                            "MATERIAL_PARENT": "G2_UNSEEN_MATERIAL_ONLY_IF_STRICT_STUDY_BOUNDARY_IS_ALSO_PRESERVED",
                            "ALLOY_FAMILY": "SOURCE_IDENTIFIER_FAMILY_ONLY; CROSS_PAPER_CHEMISTRY_EQUIVALENCE_NOT_RECONCILED",
                        }[level],
                        "Notes": (
                            "Alloy family uses exact unparsed Original_Composition text when available, then exact nominal text, "
                            "then an existing Material_Parent_ID or source Alloy_ID, otherwise a paper fallback. Exact-text "
                            "matching is an audit control only; no composition parsing or chemistry reconciliation occurred."
                        ),
                    }
                )
    return pd.DataFrame(rows)


def overlap_count(train: pd.DataFrame, validation: pd.DataFrame, field: str) -> int:
    return len(set(train[field].astype(str)) & set(validation[field].astype(str)))


def joint_counts(frame: pd.DataFrame) -> dict[str, int]:
    return {state: int(frame.Joint_State.eq(state).sum()) for state in ("00", "10", "01", "11")}


def build_partition(
    frame: pd.DataFrame,
    target: str,
    split_id: str,
    strategy: str,
    grouping_label: str,
    grouping_field: str,
    validation_ids: set[str],
    number_of_folds: int,
    fold_number: int,
    design_id: str,
    construction_note: str,
) -> dict:
    validation = frame.loc[frame.ML_Condition_ID.isin(validation_ids)].copy()
    train = frame.loc[~frame.ML_Condition_ID.isin(validation_ids)].copy()
    assert len(train) + len(validation) == len(frame)
    assert set(train.ML_Condition_ID).isdisjoint(validation.ML_Condition_ID)

    if target in {"T1_TRIP", "T2_TWIP"}:
        train_pos = int(train.Target_Value_Internal.eq(1).sum())
        train_neg = int(train.Target_Value_Internal.eq(0).sum())
        val_pos = int(validation.Target_Value_Internal.eq(1).sum())
        val_neg = int(validation.Target_Value_Internal.eq(0).sum())
        both_train = train_pos > 0 and train_neg > 0
        both_val = val_pos > 0 and val_neg > 0
    else:
        train_pos = int(train.Joint_State.isin(["10", "01", "11"]).sum())
        train_neg = int(train.Joint_State.eq("00").sum())
        val_pos = int(validation.Joint_State.isin(["10", "01", "11"]).sum())
        val_neg = int(validation.Joint_State.eq("00").sum())
        if target == "T3B_MULTILABEL":
            both_train = train.Effective_TRIP.nunique() == 2 and train.Effective_TWIP.nunique() == 2
            both_val = validation.Effective_TRIP.nunique() == 2 and validation.Effective_TWIP.nunique() == 2
        else:
            both_train = train.Joint_State.nunique() == 4
            both_val = validation.Joint_State.nunique() == 4

    train_states, val_states = joint_counts(train), joint_counts(validation)
    return {
        "Target": target,
        "Split_ID": split_id,
        "Split_Strategy": strategy,
        "Grouping_Level": grouping_label,
        "Train_Condition_Count": len(train),
        "Validation_Condition_Count": len(validation),
        "Train_Group_Count": int(train[grouping_field].nunique()),
        "Validation_Group_Count": int(validation[grouping_field].nunique()),
        "Train_Positive": train_pos,
        "Train_Negative": train_neg,
        "Validation_Positive": val_pos,
        "Validation_Negative": val_neg,
        "Both_Classes_Train": bool(both_train),
        "Both_Classes_Validation": bool(both_val),
        "Group_Overlap": overlap_count(train, validation, grouping_field),
        "Paper_Overlap": overlap_count(train, validation, "Paper_ID"),
        "Study_Overlap": overlap_count(train, validation, "Effective_Study_Group"),
        "Material_Overlap": overlap_count(train, validation, "Effective_Material_Group"),
        "Source_Alloy_Family_Overlap": overlap_count(train, validation, "Alloy_Family_ID"),
        "Strict_Leakage_Overlap": overlap_count(train, validation, "Effective_Strict_Group"),
        "Number_of_Folds": number_of_folds,
        "Fold_Number": fold_number,
        "Validation_Group_IDs": joined(validation[grouping_field], empty="NONE"),
        "Train_TRIP_Positive": int(train.Effective_TRIP.eq(1).sum()),
        "Train_TRIP_Negative": int(train.Effective_TRIP.eq(0).sum()),
        "Validation_TRIP_Positive": int(validation.Effective_TRIP.eq(1).sum()),
        "Validation_TRIP_Negative": int(validation.Effective_TRIP.eq(0).sum()),
        "Train_TWIP_Positive": int(train.Effective_TWIP.eq(1).sum()),
        "Train_TWIP_Negative": int(train.Effective_TWIP.eq(0).sum()),
        "Validation_TWIP_Positive": int(validation.Effective_TWIP.eq(1).sum()),
        "Validation_TWIP_Negative": int(validation.Effective_TWIP.eq(0).sum()),
        **{f"Train_{state}": train_states[state] for state in train_states},
        **{f"Validation_{state}": val_states[state] for state in val_states},
        "_Train_IDs": set(train.ML_Condition_ID),
        "_Validation_IDs": set(validation.ML_Condition_ID),
        "_Frame": frame,
        "_Grouping_Field": grouping_field,
        "_Design_ID": design_id,
        "_Construction_Note": construction_note,
    }


def independent_support(partition: dict) -> bool:
    return (
        partition["Both_Classes_Train"]
        and partition["Both_Classes_Validation"]
        and partition["Paper_Overlap"] == 0
        and partition["Study_Overlap"] == 0
        and partition["Material_Overlap"] == 0
        and partition["Strict_Leakage_Overlap"] == 0
        and partition["Train_Condition_Count"] >= 4
        and partition["Validation_Condition_Count"] >= 2
    )


def finalize_design(partitions: list[dict], force_exploratory: bool = False) -> None:
    design_feasible = all(independent_support(partition) for partition in partitions)
    for partition in partitions:
        overlap = any(
            partition[field] > 0
            for field in ("Paper_Overlap", "Study_Overlap", "Material_Overlap", "Strict_Leakage_Overlap")
        )
        if overlap:
            status = "INVALID_GROUP_LEAKAGE"
        elif not partition["Both_Classes_Train"] or not partition["Both_Classes_Validation"]:
            status = "INVALID_CLASS_SUPPORT"
        elif partition["Train_Condition_Count"] < 4 or partition["Validation_Condition_Count"] < 2:
            status = "INVALID_SAMPLE_SUPPORT"
        elif force_exploratory or not design_feasible:
            status = "EXPLORATORY_ONLY"
        else:
            status = "VALID_LIMITED"
        partition["Recommended_Status"] = status
        partition["Design_Feasibility"] = "FEASIBLE" if design_feasible and not force_exploratory else "NOT_FEASIBLE" if not design_feasible else "EXPLORATORY_ONLY"
        partition["Scientific_Validity"] = (
            "ZERO_PAPER_STUDY_MATERIAL_STRICT_AND_EXACT_SOURCE_FAMILY_OVERLAP"
            if not overlap and partition["Source_Alloy_Family_Overlap"] == 0
            else "ZERO_PROVENANCE_GROUP_OVERLAP; EXACT_SOURCE_ALLOY_FAMILY_OVERLAP_LIMITS_G2"
            if not overlap
            else "FORBIDDEN_RELATED_GROUPS_CROSS_TRAIN_VALIDATION"
        )
        limitation = []
        if partition["Target"] == "T1_TRIP":
            limitation.append("Only 5 TRIP negatives across 4 strict groups; M2 retains 2 negatives across 2 strict groups")
        elif partition["Target"] == "T2_TWIP":
            limitation.append("Only 6 TWIP negatives across 4 strict groups; one paper contributes 3 negatives")
        elif partition["Target"] == "T3A_FOUR_CLASS":
            limitation.append("State 00 is a singleton and cannot occur independently on both sides")
        else:
            limitation.append("Output-wise binary support does not solve the singleton 00 joint-state limitation")
        if status == "INVALID_CLASS_SUPPORT":
            limitation.append("At least one required class is absent from training or validation")
        if status == "INVALID_GROUP_LEAKAGE":
            limitation.append("Strict/paper/material relatedness crosses the partition")
        partition["Statistical_Limitation"] = "; ".join(limitation)
        partition["Notes"] = (
            partition["_Construction_Note"]
            + "; group independence takes precedence over exact stratification; no row-random split, resampling, or model fitting."
        )


def leave_one_group_design(
    frame: pd.DataFrame,
    target: str,
    strategy: str,
    grouping_label: str,
    grouping_field: str,
    prefix: str,
) -> list[dict]:
    groups = sorted(frame[grouping_field].astype(str).unique())
    partitions = []
    for fold_number, group_id in enumerate(groups, start=1):
        validation_ids = set(frame.loc[frame[grouping_field].astype(str).eq(group_id), "ML_Condition_ID"])
        partitions.append(
            build_partition(
                frame, target, f"{prefix}_F{fold_number:02d}_{safe_token(group_id)}", strategy,
                grouping_label, grouping_field, validation_ids, len(groups), fold_number,
                f"{target}:{strategy}:{grouping_label}",
                f"Deterministic leave-one-group-out fold holding {group_id}",
            )
        )
    finalize_design(partitions)
    return partitions


def deterministic_group_kfold_assignments(frame: pd.DataFrame, grouping_field: str, k: int) -> list[set[str]]:
    sizes = frame.groupby(grouping_field).size().to_dict()
    ordered_groups = sorted(sizes, key=lambda group: (-sizes[group], str(group)))
    folds = [{"size": 0, "groups": []} for _ in range(k)]
    for group in ordered_groups:
        fold_index = min(range(k), key=lambda idx: (folds[idx]["size"], len(folds[idx]["groups"]), idx))
        folds[fold_index]["groups"].append(group)
        folds[fold_index]["size"] += sizes[group]
    return [
        set(frame.loc[frame[grouping_field].isin(fold["groups"]), "ML_Condition_ID"])
        for fold in folds
    ]


def group_kfold_design(frame: pd.DataFrame, target: str, k: int, prefix: str) -> list[dict]:
    validation_sets = deterministic_group_kfold_assignments(frame, "Effective_Strict_Group", k)
    partitions = []
    for fold_number, validation_ids in enumerate(validation_sets, start=1):
        partitions.append(
            build_partition(
                frame, target, f"{prefix}_K{k}_F{fold_number:02d}", f"GROUP_K_FOLD_K{k}",
                "Leakage_Group_Strict_WITH_PAPER_FALLBACK", "Effective_Strict_Group",
                validation_ids, k, fold_number, f"{target}:GROUP_K_FOLD_K{k}",
                "Label-blind deterministic greedy group allocation by descending target-usable group size and lexical group ID",
            )
        )
    finalize_design(partitions)
    return partitions


def binary_class_support(frame: pd.DataFrame) -> bool:
    return frame.Target_Value_Internal.nunique() == 2


def deterministic_holdout_search(
    frame: pd.DataFrame,
    target: str,
    prefix: str,
    m2_fields: list[str],
    retain: int = 3,
) -> list[dict]:
    groups = sorted(frame.Effective_Strict_Group.unique())
    minimum = ceil(0.18 * len(frame))
    maximum = floor(0.35 * len(frame))
    target_size = round(0.25 * len(frame))
    candidates = []
    for group_count in (2, 3):
        for held_groups in combinations(groups, group_count):
            validation = frame.loc[frame.Effective_Strict_Group.isin(held_groups)]
            train = frame.loc[~frame.Effective_Strict_Group.isin(held_groups)]
            if not minimum <= len(validation) <= maximum:
                continue
            if not binary_class_support(train) or not binary_class_support(validation):
                continue
            if set(train.Alloy_Family_ID) & set(validation.Alloy_Family_ID):
                continue
            train_m2 = train.loc[complete_mask(train, m2_fields)]
            validation_m2 = validation.loc[complete_mask(validation, m2_fields)]
            if not binary_class_support(train_m2) or not binary_class_support(validation_m2):
                continue
            negative_groups = tuple(sorted(validation.loc[validation.Target_Value_Internal.eq(0), "Effective_Strict_Group"].unique()))
            rank = (abs(len(validation) - target_size), -group_count, held_groups)
            candidates.append((rank, held_groups, negative_groups, set(validation.ML_Condition_ID)))
    candidates.sort(key=lambda item: item[0])

    selected = []
    seen_negative_group_sets = set()
    for _, held_groups, negative_groups, validation_ids in candidates:
        if negative_groups in seen_negative_group_sets:
            continue
        seen_negative_group_sets.add(negative_groups)
        selected.append((held_groups, validation_ids))
        if len(selected) == retain:
            break
    assert len(selected) == retain, f"Only {len(selected)} deterministic {target} holdouts met predeclared gates"

    partitions = []
    for number, (held_groups, validation_ids) in enumerate(selected, start=1):
        split_id = f"{prefix}_GH_STRICT_{number:02d}"
        partition = build_partition(
            frame, target, split_id, "DETERMINISTIC_GROUPED_HOLDOUT",
            "Leakage_Group_Strict_WITH_PAPER_FALLBACK", "Effective_Strict_Group",
            validation_ids, 1, 1, split_id,
            (
                "Exhaustive lexical search over two/three strict validation groups; validation size constrained to 18-35%; "
                "both full-target and raw M2-complete subsets retain both classes; exact unparsed source-alloy families "
                "are disjoint; distinct negative-group sets retained; "
                f"held groups={joined(held_groups)}"
            ),
        )
        finalize_design([partition])
        partitions.append(partition)
    return partitions


def t3_multilabel_holdouts(joint: pd.DataFrame, retain: int = 3) -> list[dict]:
    groups = sorted(joint.Effective_Strict_Group.unique())
    minimum, maximum = ceil(0.18 * len(joint)), floor(0.35 * len(joint))
    target_size = round(0.25 * len(joint))
    candidates = []
    for group_count in (2, 3):
        for held_groups in combinations(groups, group_count):
            validation = joint.loc[joint.Effective_Strict_Group.isin(held_groups)]
            train = joint.loc[~joint.Effective_Strict_Group.isin(held_groups)]
            support = (
                train.Effective_TRIP.nunique() == 2 and validation.Effective_TRIP.nunique() == 2
                and train.Effective_TWIP.nunique() == 2 and validation.Effective_TWIP.nunique() == 2
            )
            if support and minimum <= len(validation) <= maximum:
                candidates.append(((abs(len(validation) - target_size), -group_count, held_groups), held_groups, set(validation.ML_Condition_ID)))
    candidates.sort(key=lambda item: item[0])
    selected = candidates[:retain]
    assert len(selected) == retain
    partitions = []
    for number, (_, held_groups, validation_ids) in enumerate(selected, start=1):
        split_id = f"T3B_GH_STRICT_{number:02d}"
        partition = build_partition(
            joint, "T3B_MULTILABEL", split_id, "DETERMINISTIC_GROUPED_HOLDOUT_FUTURE_MULTILABEL",
            "Leakage_Group_Strict_WITH_PAPER_FALLBACK", "Effective_Strict_Group", validation_ids,
            1, 1, split_id,
            f"Future-only output-wise binary-support holdout; held groups={joined(held_groups)}",
        )
        finalize_design([partition], force_exploratory=True)
        partitions.append(partition)
    return partitions


def build_all_partitions(conditions: pd.DataFrame, core_by_set: dict[str, list[str]]) -> list[dict]:
    partitions: list[dict] = []
    for target, prefix in (("T1_TRIP", "T1"), ("T2_TWIP", "T2")):
        frame, _ = target_subset(conditions, target)
        partitions.extend(leave_one_group_design(frame, target, "LEAVE_ONE_PAPER_OUT", "Paper_ID", "Paper_ID", f"{prefix}_LOPO"))
        partitions.extend(
            leave_one_group_design(
                frame, target, "LEAVE_ONE_STUDY_SERIES_OUT", "Study_Series_ID_WITH_PAPER_FALLBACK",
                "Effective_Study_Group", f"{prefix}_LOSO",
            )
        )
        partitions.extend(
            leave_one_group_design(
                frame, target, "LEAVE_ONE_MATERIAL_FAMILY_OUT",
                "Leakage_Group_Material_WITH_CONSERVATIVE_FALLBACK", "Effective_Material_Group",
                f"{prefix}_LOMFO",
            )
        )
        for k in (2, 3, 4, 5):
            partitions.extend(group_kfold_design(frame, target, k, f"{prefix}_GKF"))
        partitions.extend(
            deterministic_holdout_search(
                frame, target, prefix, core_by_set["M2_CHEMISTRY_PLUS_TEST"], retain=3
            )
        )

    joint = conditions.loc[conditions.Joint_State.notna()].copy()
    t3a = leave_one_group_design(
        joint, "T3A_FOUR_CLASS", "LEAVE_ONE_PAPER_OUT_FOUR_CLASS_DIAGNOSTIC", "Paper_ID", "Paper_ID", "T3A_LOPO"
    )
    # Four-class validity requires all four states on both sides; the singleton 00
    # makes every fold invalid regardless of the ordinary binary compatibility fields.
    for partition in t3a:
        partition["Recommended_Status"] = "INVALID_CLASS_SUPPORT"
        partition["Design_Feasibility"] = "NOT_FEASIBLE"
        partition["Statistical_Limitation"] = "T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE; state 00 is a singleton"
    partitions.extend(t3a)
    partitions.extend(t3_multilabel_holdouts(joint))
    return partitions


def feature_expansion(partitions: list[dict], core_by_set: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    for partition in partitions:
        feature_sets = FEATURE_SET_ORDER if partition["Target"] in {"T1_TRIP", "T2_TWIP"} else ("M2_CHEMISTRY_PLUS_TEST",)
        frame = partition["_Frame"]
        train = frame.loc[frame.ML_Condition_ID.isin(partition["_Train_IDs"])]
        validation = frame.loc[frame.ML_Condition_ID.isin(partition["_Validation_IDs"])]
        for feature_set in feature_sets:
            fields = core_by_set[feature_set]
            train_complete = complete_mask(train, fields)
            validation_complete = complete_mask(validation, fields)
            row = {key: value for key, value in partition.items() if not key.startswith("_")}
            row["Feature_Set"] = feature_set
            row["Feature_Complete_Train"] = int(train_complete.sum())
            row["Feature_Complete_Validation"] = int(validation_complete.sum())
            if partition["Target"] in {"T1_TRIP", "T2_TWIP"}:
                row["Feature_Complete_Train_Positive"] = int((train_complete & train.Target_Value_Internal.eq(1)).sum())
                row["Feature_Complete_Train_Negative"] = int((train_complete & train.Target_Value_Internal.eq(0)).sum())
                row["Feature_Complete_Validation_Positive"] = int((validation_complete & validation.Target_Value_Internal.eq(1)).sum())
                row["Feature_Complete_Validation_Negative"] = int((validation_complete & validation.Target_Value_Internal.eq(0)).sum())
                complete_both_train = row["Feature_Complete_Train_Positive"] > 0 and row["Feature_Complete_Train_Negative"] > 0
                complete_both_validation = row["Feature_Complete_Validation_Positive"] > 0 and row["Feature_Complete_Validation_Negative"] > 0
                if row["Recommended_Status"] in {"VALID_STRONG", "VALID_LIMITED"} and not (
                    complete_both_train and complete_both_validation
                ):
                    row["Recommended_Status"] = "INVALID_CLASS_SUPPORT"
                    row["Design_Feasibility"] = "TARGET_ROSTER_FEASIBLE; FEATURE_SET_NOT_FEASIBLE"
                    row["Statistical_Limitation"] += (
                        f"; {feature_set} complete cases do not retain both target classes in training and validation"
                    )
            else:
                row["Feature_Complete_Train_Positive"] = int((train_complete & train.Joint_State.isin(["10", "01", "11"])).sum())
                row["Feature_Complete_Train_Negative"] = int((train_complete & train.Joint_State.eq("00")).sum())
                row["Feature_Complete_Validation_Positive"] = int((validation_complete & validation.Joint_State.isin(["10", "01", "11"])).sum())
                row["Feature_Complete_Validation_Negative"] = int((validation_complete & validation.Joint_State.eq("00")).sum())
            rows.append(row)
    result = pd.DataFrame(rows)
    return result.reindex(columns=CANDIDATE_COLUMNS)


def build_manifest(partitions: list[dict], candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    valid_pairs = set(
        candidates.loc[
            candidates.Target.isin(["T1_TRIP", "T2_TWIP"])
            & candidates.Recommended_Status.isin(["VALID_STRONG", "VALID_LIMITED"]),
            ["Target", "Split_ID", "Feature_Set"],
        ].itertuples(index=False, name=None)
    )
    valid = [partition for partition in partitions if partition["Target"] in {"T1_TRIP", "T2_TWIP"}]
    for partition in valid:
        frame = partition["_Frame"].sort_values("Condition_Order")
        for feature_set in FEATURE_SET_ORDER:
            if (partition["Target"], partition["Split_ID"], feature_set) not in valid_pairs:
                continue
            for _, condition in frame.iterrows():
                target_field = "Effective_TRIP" if partition["Target"] == "T1_TRIP" else "Effective_TWIP"
                rows.append(
                    {
                        "Target": partition["Target"],
                        "Split_ID": partition["Split_ID"],
                        "ML_Condition_ID": condition.ML_Condition_ID,
                        "Assignment": "VALIDATION" if condition.ML_Condition_ID in partition["_Validation_IDs"] else "TRAIN",
                        "Group_ID": condition.Effective_Strict_Group,
                        "Paper_ID": condition.Paper_ID,
                        "Material_Parent_ID": condition.Material_Parent_ID,
                        "Target_Value": int(condition[target_field]),
                        "Feature_Set": feature_set,
                    }
                )
    return pd.DataFrame(rows)


def build_generalization(conditions: pd.DataFrame) -> pd.DataFrame:
    support = {}
    for target in ("T1_TRIP", "T2_TWIP"):
        frame, _ = target_subset(conditions, target)
        material_sizes = frame.groupby("Alloy_Family_ID").size()
        support[target] = {
            "related": int((material_sizes >= 2).sum()),
            "pos_material": int(frame.loc[frame.Target_Value_Internal.eq(1), "Alloy_Family_ID"].nunique()),
            "neg_material": int(frame.loc[frame.Target_Value_Internal.eq(0), "Alloy_Family_ID"].nunique()),
            "pos_paper": int(frame.loc[frame.Target_Value_Internal.eq(1), "Paper_ID"].nunique()),
            "neg_paper": int(frame.loc[frame.Target_Value_Internal.eq(0), "Paper_ID"].nunique()),
        }
    return pd.DataFrame(
        [
            {
                "Generalization_Level": "G1",
                "Definition": "NEW CONDITION, RELATED MATERIAL",
                "Grouping_Proxy": "Condition holdout with intentional material-family overlap",
                "T1_Support": f"{support['T1_TRIP']['related']} material groups contain >=2 usable T1 conditions",
                "T1_Feasibility": "EXPLORATORY_ONLY",
                "T2_Support": f"{support['T2_TWIP']['related']} material groups contain >=2 usable T2 conditions",
                "T2_Feasibility": "EXPLORATORY_ONLY",
                "T3_Multilabel_Feasibility": "EXPLORATORY_ONLY",
                "T3_Four_Class_Feasibility": "INVALID_CLASS_SUPPORT",
                "Limitations": "Intentional related-material overlap estimates interpolation, not leakage-safe unseen-family generalization.",
                "Recommended_Use": "Secondary descriptive sensitivity only; never the primary validation claim.",
            },
            {
                "Generalization_Level": "G2",
                "Definition": "UNSEEN MATERIAL PARENT / ALLOY VARIANT",
                "Grouping_Proxy": "Exact unparsed source-alloy-family separation nested inside strict study/paper holdout",
                "T1_Support": f"positive/negative exact-source alloy families={support['T1_TRIP']['pos_material']}/{support['T1_TRIP']['neg_material']}",
                "T1_Feasibility": "VALID_LIMITED",
                "T2_Support": f"positive/negative exact-source alloy families={support['T2_TWIP']['pos_material']}/{support['T2_TWIP']['neg_material']}",
                "T2_Feasibility": "VALID_LIMITED",
                "T3_Multilabel_Feasibility": "EXPLORATORY_ONLY",
                "T3_Four_Class_Feasibility": "INVALID_CLASS_SUPPORT",
                "Limitations": "A pure one-material-out split often leaks the same study; exact source-text matching catches only obvious family equality, while chemically equivalent differently written families remain unresolved.",
                "Recommended_Use": "Use the retained strict grouped holdouts with zero exact-source alloy-family overlap; do not claim chemically reconciled family separation.",
            },
            {
                "Generalization_Level": "G3",
                "Definition": "UNSEEN STUDY / PAPER FAMILY",
                "Grouping_Proxy": "Leakage_Group_Strict with Paper_ID fallback",
                "T1_Support": f"positive/negative papers={support['T1_TRIP']['pos_paper']}/{support['T1_TRIP']['neg_paper']}",
                "T1_Feasibility": "VALID_LIMITED_MULTI_PAPER_HOLDOUT; LOPO_NOT_FEASIBLE",
                "T2_Support": f"positive/negative papers={support['T2_TWIP']['pos_paper']}/{support['T2_TWIP']['neg_paper']}",
                "T2_Feasibility": "VALID_LIMITED_GROUPKFOLD_OR_MULTI_PAPER_HOLDOUT; LOPO_NOT_FEASIBLE",
                "T3_Multilabel_Feasibility": "EXPLORATORY_ONLY_OUTPUT_WISE",
                "T3_Four_Class_Feasibility": "T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE",
                "Limitations": "Only four papers support each negative target; many single-paper validation folds contain one class only.",
                "Recommended_Use": "Primary concept, but use multi-paper grouped partitions with explicit class-support reporting rather than claim universal LOPO feasibility.",
            },
        ]
    )


def design_summary(partitions: list[dict]) -> pd.DataFrame:
    rows = []
    grouped: dict[str, list[dict]] = {}
    for partition in partitions:
        grouped.setdefault(partition["_Design_ID"], []).append(partition)
    for design_id, group in grouped.items():
        first = group[0]
        rows.append(
            {
                "Target": first["Target"],
                "Design": first["Split_Strategy"],
                "Grouping": first["Grouping_Level"],
                "Folds_or_Candidates": len(group),
                "Validation_Positive_Range": f"{min(p['Validation_Positive'] for p in group)}-{max(p['Validation_Positive'] for p in group)}",
                "Validation_Negative_Range": f"{min(p['Validation_Negative'] for p in group)}-{max(p['Validation_Negative'] for p in group)}",
                "All_Folds_Both_Classes": all(p["Both_Classes_Validation"] for p in group),
                "All_Folds_Zero_Strict_Overlap": all(p["Strict_Leakage_Overlap"] == 0 for p in group),
                "All_Folds_Zero_Exact_Source_Family_Overlap": all(p["Source_Alloy_Family_Overlap"] == 0 for p in group),
                "Feasibility": first["Design_Feasibility"],
                "Quality": joined(p["Recommended_Status"] for p in group).replace("|", ", "),
            }
        )
    return pd.DataFrame(rows)


def valid_strategy_names(partitions: list[dict], target: str) -> list[str]:
    return sorted({
        partition["Split_Strategy"] for partition in partitions
        if partition["Target"] == target and partition["Recommended_Status"] in {"VALID_STRONG", "VALID_LIMITED"}
    })


def valid_candidate_strategy_names(
    candidates: pd.DataFrame, target: str, feature_set: str = "M2_CHEMISTRY_PLUS_TEST"
) -> list[str]:
    return sorted(set(candidates.loc[
        candidates.Target.eq(target)
        & candidates.Feature_Set.eq(feature_set)
        & candidates.Recommended_Status.isin(["VALID_STRONG", "VALID_LIMITED"]),
        "Split_Strategy",
    ]))


def strategy_feasible(partitions: list[dict], target: str, strategy: str) -> bool:
    designs = {}
    for partition in partitions:
        if partition["Target"] == target and partition["Split_Strategy"] == strategy:
            designs.setdefault(partition["_Design_ID"], []).append(partition)
    return bool(designs) and any(all(p["Recommended_Status"] in {"VALID_STRONG", "VALID_LIMITED"} for p in group) for group in designs.values())


def write_chemistry_policy() -> None:
    CHEMISTRY_POLICY_PATH.write_text(
        """# Chemistry Source Policy V1

## Status and scope

This policy is frozen for the next source-preserving matrix-construction stage. It is documentation only in Grouped Split Design V1: no unified chemistry column was created, no composition was parsed or reconciled, and no value was normalized, filled, or calculated.

## Future selection rule

For each independent experimental condition:

1. If explicitly measured **bulk specimen/material chemistry** is available with a valid source scope, method/provenance, and composition basis, prefer that measured bulk representation.
2. Otherwise, use explicitly reported nominal composition.
3. Retain `Composition_Source` as `MEASURED_BULK` or `NOMINAL` beside every later selected value.
4. Preserve the original measured, nominal, basis, uncertainty, method, and provenance fields; the selected representation must never overwrite them.
5. If neither valid bulk-measured nor nominal chemistry is available, retain missingness. Do not infer absent elements as zero.

"Valid measured bulk" means source evidence explicitly scoped to the specimen/material bulk rather than a local region or feedstock, with enough method and basis information to interpret the reported composition. A disagreement or ambiguous scope is a review flag, not permission to average, normalize, or silently choose a value.

## Prohibited substitutions

- Local EDS, local APT, TEM-local chemistry, scanned-region chemistry, precipitate chemistry, and grain-boundary chemistry do not substitute for bulk chemistry unless a later explicit scientific decision justifies that exact use.
- Feedstock chemistry is not automatically final specimen bulk chemistry.
- Nominal and measured values are not averaged.
- Cross-paper alloy families are not declared equivalent by similar text or apparent composition.
- Missing elements are not converted to zero, and totals are not normalized in this phase.

## Provenance required later

Any future source-preserving chemistry representation must retain `Paper_ID`, `ML_Condition_ID`, original composition text, composition basis, selected source class, measurement method/scope, uncertainty where reported, and source location. Conflict and selection decisions must be auditable condition by condition.

## Gate

The next task may implement this policy while constructing an untransformed, provenance-preserving condition table. It must still perform no imputation, encoding, normalization, alloy-descriptor calculation, resampling, or model training unless separately authorized and scientifically justified.
""",
        encoding="utf-8",
    )


def write_architecture(
    conditions: pd.DataFrame,
    partitions: list[dict],
    class_support: pd.DataFrame,
    m2_support: pd.DataFrame,
) -> None:
    summary = design_summary(partitions)
    binary_summary = summary.loc[summary.Target.isin(["T1_TRIP", "T2_TWIP"])]
    t1_valid = valid_strategy_names(partitions, "T1_TRIP")
    t2_valid = valid_strategy_names(partitions, "T2_TWIP")
    text = f"""# Validation Architecture V1

## Outcome

Leakage-safe grouped train/validation partitions are feasible, but only as **limited** validation designs. No candidate qualifies as `VALID_STRONG`. The atomic unit is one replacement-aware independent experimental ML condition: 51 total, with 32 usable for T1 and 30 for T2. Stage children, legacy replacements, summaries, computational records, P017 MD conditions, and replicate-count metadata are excluded.

The recommended grouping control is **`Leakage_Group_Strict` with a conservative `Paper_ID` fallback**. Nineteen conditions lack explicit study/material leakage keys; all such same-paper conditions remain together. All 51 physical-batch IDs are missing, so no batch identity is inferred. In this dataset the effective strict groups coincide with paper boundaries.

An additional exact-source alloy-family audit uses unparsed source composition text (falling back to nominal text, material parent, source Alloy_ID, then paper). It identifies the exact `Fe50Mn30Co10Cr10` text across P003/P011/P013/P014. This is not chemistry reconciliation: it catches obvious equality only. GroupKFold remains a G3 unseen-paper design even when that exact family appears on both sides; the retained deterministic holdouts require zero exact-source family overlap for limited G2 use.

## Group support

- T1/TRIP: 27 positive and 5 negative conditions; negatives occur in 4 papers/effective strict groups.
- T2/TWIP: 24 positive and 6 negative conditions; negatives occur in 4 papers/effective strict groups. P001 supplies 3 of the 6 negatives.
- M2 complete T1: 17 positive and 2 negative conditions; the two negatives occur in only 2 strict groups.
- M2 complete T2: 14 positive and all 6 negative conditions; negatives remain in 4 strict groups.

The negative-class evidence audit copies every effective label unchanged. It grades only the consolidated evidence text: direct initial-to-final or explicit absence is strong, suppression/comparative wording is moderate, and nonspecific or uncopied evidence summaries are limited. One P008 negative retains an explicit consolidated-text gap; Split Design V1 generates no label from that gap and does not silently upgrade its evidence strength.

## Strategy feasibility

{binary_summary.to_markdown(index=False)}

`FEASIBLE` means every fold has both classes in training and validation and has zero selected grouping-key, paper, study, reviewed material-parent, and strict-group overlap. The separate exact-source-family column determines whether a feasible G3 fold can also support a limited G2 interpretation. GroupKFold construction is label-blind and deterministic: groups are ordered by descending target-usable size and lexical ID, then assigned to the smallest fold. No seeds or label-driven seed search are used.

## Recommended T1 architecture

Primary: **the retained deterministic strict-grouped holdout family**, beginning with `T1_GH_STRICT_01`. The exhaustive, predeclared search retains three partitions with 18-35% validation size, two or three strict validation groups, both full-target classes on both sides, both raw M2-complete classes on both sides, and zero exact-source alloy-family overlap. This is `VALID_LIMITED`, not a performance-estimation guarantee: M2 has only one TRIP-negative complete case on each side of any admissible partition.

Standard label-blind GroupKFold k=2 is class-supported on the full 32-condition T1 roster, but it is **not M2-complete-case compatible**: one fold's M2 validation subset has no negative, while the complementary fold's M2 training subset has no negative. GroupKFold k=3, 4, and 5 fail full-roster class support in at least one validation fold. LOPO and leave-one-study-series-out are not complete binary-validation designs because most held-out groups are positive-only. Alternative retained grouped holdouts are the secondary robustness analysis.

## Recommended T2 architecture

Primary for G3 unseen-paper evaluation: **strict GroupKFold with k=2**. Both folds retain both classes, zero provenance-group overlap, and M2-complete positive/negative support. Exact-source alloy-family overlap means this is not a pure G2 design. Strict GroupKFold k=4 is also G3-feasible but secondary because each validation fold depends on only one negative-supporting paper. The retained deterministic grouped holdouts have zero exact-source family overlap and provide the limited G2 robustness view. GroupKFold k=3 and k=5 are not feasible because at least one validation fold lacks a negative.

## LOPO, repeated holdout, and nested CV

LOPO is **not feasible as a standalone binary cross-validation architecture** for either T1 or T2: many validation papers contain only positives, and P001's T2 fold contains only negatives. Per-paper folds may later be reported as exploratory stress tests, but they cannot replace a class-supported primary design.

Multiple deterministic grouped holdouts are justified for sensitivity to scarce group allocation. Stochastic "repeated holdout" and arbitrary seed hunting are not justified. Nested CV would be statistically excessive: it would repeatedly subdivide only 5/6 negatives and 4 negative-supporting strict groups, while M2 T1 has just 2 complete negatives.

## T3

T3A four-class prediction is **`T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE`**. State 00 has one independent condition, so it cannot occur in both training and validation. No class is merged or hidden.

T3B multilabel evaluation can be considered later only as `EXPLORATORY_ONLY`, using strict grouped partitions that preserve both binary outputs on both sides. This does not make four-state evaluation valid and does not provide independent validation support for state 00.

## Random row split rejection

Ordinary random row-level splitting is rejected. Conditions from the same paper, material parent, composition/alloy family, processing family, temperature series, or strain-rate series can share unmeasured study-specific information. Splitting those siblings across sides would allow memorization of related alloys or experimental practice and produce optimistic generalization estimates. Exact stratification never overrides group independence.

## No test split and no modelling

No three-way train/validation/test partition is created. With current support, reserving a third independent set would further fragment the minority classes. This architecture contains no algorithm selection, feature transformation, resampling, training, prediction, or performance metric.
"""
    ARCHITECTURE_PATH.write_text(text, encoding="utf-8")


def write_design_audit(
    conditions: pd.DataFrame,
    partitions: list[dict],
    candidates: pd.DataFrame,
    m2_support: pd.DataFrame,
    input_hashes: dict[Path, str],
) -> None:
    strict = {}
    for target in ("T1_TRIP", "T2_TWIP"):
        frame, _ = target_subset(conditions, target)
        strict[target] = (
            int(frame.loc[frame.Target_Value_Internal.eq(1), "Effective_Strict_Group"].nunique()),
            int(frame.loc[frame.Target_Value_Internal.eq(0), "Effective_Strict_Group"].nunique()),
        )
    valid_counts = {
        target: candidates.loc[
            candidates.Target.eq(target)
            & candidates.Feature_Set.eq("M2_CHEMISTRY_PLUS_TEST")
            & candidates.Recommended_Status.isin(["VALID_STRONG", "VALID_LIMITED"]),
            "Split_ID",
        ].nunique()
        for target in ("T1_TRIP", "T2_TWIP")
    }
    t1_m2 = m2_support.loc[m2_support.Target.eq("T1_TRIP")].set_index("Class_Value")
    t2_m2 = m2_support.loc[m2_support.Target.eq("T2_TWIP")].set_index("Class_Value")
    provenance = "\n".join(f"- `{path.relative_to(ROOT).as_posix()}`: `{value}`" for path, value in input_hashes.items())
    text = f"""# Grouped Split Design V1 Audit

This is split design and feasibility analysis only. No model, transformed matrix, imputation, normalization, encoding, descriptor calculation, resampling, synthetic sample, or performance metric was produced.

## A. Independent experimental conditions

**51** replacement-aware independent experimental ML conditions.

## B. T1 usable

**32**: 27 positive, 5 negative.

## C. T2 usable

**30**: 24 positive, 6 negative.

## D. Joint usable

**27**: 00=1, 10=5, 01=4, 11=17.

## E. Target-positive groups

At the recommended strict-with-paper-fallback level: T1={strict['T1_TRIP'][0]}, T2={strict['T2_TWIP'][0]}.

## F. Target-negative groups

At the recommended strict-with-paper-fallback level: T1={strict['T1_TRIP'][1]}, T2={strict['T2_TWIP'][1]}. These are four papers for each target.

## G. Valid T1 split candidates

**{valid_counts['T1_TRIP']}** unique M2-compatible train/validation partitions, all `VALID_LIMITED`; valid strategies: {', '.join(valid_candidate_strategy_names(candidates, 'T1_TRIP'))}.

## H. Valid T2 split candidates

**{valid_counts['T2_TWIP']}** unique M2-compatible train/validation partitions, all `VALID_LIMITED`; valid strategies: {', '.join(valid_candidate_strategy_names(candidates, 'T2_TWIP'))}.

## I. LOPO feasibility for T1

**NOT_FEASIBLE** as a complete binary validation design; positive-only held-out papers lack validation negatives.

## J. LOPO feasibility for T2

**NOT_FEASIBLE** as a complete binary validation design; most papers are positive-only and P001 is negative-only.

## K. GroupKFold feasibility for T1

**TARGET-ROSTER FEASIBLE but M2-INCOMPATIBLE for k=2**; k=3, 4, and 5 are not target-roster feasible under the deterministic label-blind strict-group allocation. GroupKFold is therefore not the recommended T1 M2 design.

## L. GroupKFold feasibility for T2

**FEASIBLE_LIMITED for k=2 and k=4**; k=3 and k=5 are not feasible because a validation fold lacks negatives.

## M. Recommended grouping level

`Leakage_Group_Strict` with conservative `Paper_ID` fallback. It is the safest fully covered key and currently coincides with paper boundaries. Physical batch is unavailable for all 51 conditions and is never inferred.

## N. Recommended T1 validation design

Deterministic strict grouped holdout family; primary candidate `T1_GH_STRICT_01`, with the other retained candidates as allocation sensitivity checks.

## O. Recommended T2 validation design

Strict GroupKFold k=2 as primary; strict GroupKFold k=4 and deterministic grouped holdouts as secondary robustness designs.

## P. M2 complete-case class support

T1: {int(t1_m2.loc['1','M2_Complete_Conditions'])} positive and {int(t1_m2.loc['0','M2_Complete_Conditions'])} negative complete cases; negatives occur in {int(t1_m2.loc['0','M2_Complete_Paper_Count'])} papers/strict groups. T2: {int(t2_m2.loc['1','M2_Complete_Conditions'])} positive and {int(t2_m2.loc['0','M2_Complete_Conditions'])} negative complete cases; negatives occur in {int(t2_m2.loc['0','M2_Complete_Paper_Count'])} papers/strict groups. M2 therefore removes 3/5 T1 negatives but 0/6 T2 negatives.

## Q. Joint four-class feasibility

**`T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE`** because state 00 is a singleton and cannot be independently present on both sides.

## R. Multilabel future feasibility

**EXPLORATORY_ONLY / potentially supportable output-wise** using T1/T2-compatible strict grouped partitions. This does not validate four-state discrimination or state 00.

## S. Generalization levels currently supportable

G1 is exploratory interpolation only; G2 is valid-limited only for retained strict holdouts with zero exact unparsed source-alloy-family overlap; G3 is valid-limited through multi-paper grouped partitions, not universal LOPO. Exact-text separation is not chemically reconciled equivalence.

## T. Principal statistical limitation

Only 5 TRIP and 6 TWIP negatives occur in four strict groups each; M2 reduces TRIP negatives to two groups, and joint state 00 has one condition.

## U. Principal scientific limitation

Conditions are strongly paper/study/material dependent, 19 conditions need paper fallback hierarchy, all physical batches are unknown, and exact `Fe50Mn30Co10Cr10` source text spans P003/P011/P013/P014. Differently written but chemically equivalent cross-paper families remain unresolved because chemistry has not been reconciled.

## V. Exact next step

Predeclare `T1_GH_STRICT_01` for an exploratory T1 baseline and the complete T2 GroupKFold-k=2 design, then construct a source-preserving **untransformed** M2 condition table under `CHEMISTRY_SOURCE_POLICY_V1.md`, retaining `Composition_Source` and missingness. Do not train until that table and its split intersections pass a new provenance/leakage audit; targeted acquisition of independent negative material families remains the scientific priority.

## Input provenance (SHA-256)

{provenance}

## Frozen safeguards

- Random row splitting is rejected.
- Group independence wins over exact stratification.
- P017 and every computational/stage/legacy/summary row are excluded.
- No class is merged; all labels and source scientific values are unchanged.
- No oversampling, undersampling, SMOTE, synthetic alloy, imputation, chemistry reconciliation, or model training occurred.
"""
    DESIGN_AUDIT_PATH.write_text(text, encoding="utf-8")


def validate(
    conditions: pd.DataFrame,
    master: pd.DataFrame,
    group_distribution: pd.DataFrame,
    class_support: pd.DataFrame,
    negative_audit: pd.DataFrame,
    partitions: list[dict],
    candidates: pd.DataFrame,
    manifest: pd.DataFrame,
    before: dict[Path, str],
) -> None:
    assert all(digest(path) == value for path, value in before.items())
    assert len(master) == 192 and len(conditions) == 51
    comp = pd.read_csv(COMPUTATIONAL_INDEX_PATH)
    assert len(comp) == 12 and set(comp.Paper_ID) == {"P017"}
    assert not set(conditions.Paper_ID) & {"P017", "P018", "P019"}
    assert conditions.QC_Row_Role.eq("EXPERIMENTAL_PRIMARY_CONDITION").all()
    assert conditions.QC_Duplicate_Status.eq("NO_DOUBLE_COUNT").all()
    assert int(conditions.Effective_TRIP.eq(1).sum()) == 27
    assert int(conditions.Effective_TRIP.eq(0).sum()) == 5
    assert int(conditions.Effective_TWIP.eq(1).sum()) == 24
    assert int(conditions.Effective_TWIP.eq(0).sum()) == 6
    assert Counter(conditions.Joint_State.dropna()) == Counter({"11": 17, "10": 5, "01": 4, "00": 1})
    assert conditions.Physical_Batch_ID.isna().all()
    assert set(candidates.Recommended_Status) <= QUALITY_FLAGS
    assert not candidates.Split_Strategy.str.contains("RANDOM", case=False).any()
    valid = candidates.Recommended_Status.isin(["VALID_STRONG", "VALID_LIMITED"])
    for field in ("Group_Overlap", "Paper_Overlap", "Study_Overlap", "Material_Overlap", "Strict_Leakage_Overlap"):
        assert candidates.loc[valid, field].eq(0).all()
    retained_holdouts = valid & candidates.Split_Strategy.eq("DETERMINISTIC_GROUPED_HOLDOUT") & candidates.Target.isin(["T1_TRIP", "T2_TWIP"])
    assert candidates.loc[retained_holdouts, "Source_Alloy_Family_Overlap"].eq(0).all()
    assert candidates.loc[candidates.Recommended_Status.eq("INVALID_GROUP_LEAKAGE"), "Strict_Leakage_Overlap"].gt(0).any()
    assert candidates.loc[candidates.Target.eq("T3A_FOUR_CLASS"), "Recommended_Status"].eq("INVALID_CLASS_SUPPORT").all()
    assert ((candidates.loc[candidates.Target.eq("T3A_FOUR_CLASS"), "Train_00"] == 0) | (candidates.loc[candidates.Target.eq("T3A_FOUR_CLASS"), "Validation_00"] == 0)).all()
    assert len(negative_audit.loc[negative_audit.Negative_Target.eq("TRIP")]) == 5
    assert len(negative_audit.loc[negative_audit.Negative_Target.eq("TWIP")]) == 6
    assert negative_audit.Condition_Level_Negative.all()
    assert negative_audit.Negative_Origin_Check.str.startswith("PASS_").all()
    for level in group_distribution.Grouping_Level.unique():
        assert group_distribution.loc[group_distribution.Grouping_Level.eq(level), "Number_of_Conditions"].sum() == 51
    all_support = class_support.loc[
        class_support.Population.eq("ALL_TARGET_USABLE")
        & class_support.Grouping_Level.eq("Leakage_Group_Strict")
    ].set_index("Target")
    assert all_support.loc["T1_TRIP", ["Positive_Conditions", "Negative_Conditions"]].tolist() == [27, 5]
    assert all_support.loc["T2_TWIP", ["Positive_Conditions", "Negative_Conditions"]].tolist() == [24, 6]

    assert not manifest.empty
    for (target, split_id, feature_set), group in manifest.groupby(["Target", "Split_ID", "Feature_Set"]):
        expected = 32 if target == "T1_TRIP" else 30
        assert len(group) == expected
        assert group.ML_Condition_ID.is_unique
        assert set(group.Assignment) == {"TRAIN", "VALIDATION"}
        target_field = "Effective_TRIP" if target == "T1_TRIP" else "Effective_TWIP"
        source = conditions.set_index("ML_Condition_ID").loc[group.ML_Condition_ID, target_field].astype(int).tolist()
        assert group.Target_Value.tolist() == source
        train_groups = set(group.loc[group.Assignment.eq("TRAIN"), "Group_ID"])
        validation_groups = set(group.loc[group.Assignment.eq("VALIDATION"), "Group_ID"])
        assert train_groups.isdisjoint(validation_groups)
    assert not manifest.duplicated(["Target", "Split_ID", "Feature_Set", "ML_Condition_ID"]).any()

    valid_pairs = set(candidates.loc[
        candidates.Target.isin(["T1_TRIP", "T2_TWIP"])
        & candidates.Recommended_Status.isin(["VALID_STRONG", "VALID_LIMITED"]),
        ["Target", "Split_ID", "Feature_Set"],
    ].itertuples(index=False, name=None))
    manifest_pairs = set(manifest[["Target", "Split_ID", "Feature_Set"]].itertuples(index=False, name=None))
    assert manifest_pairs == valid_pairs
    assert strategy_feasible(partitions, "T1_TRIP", "DETERMINISTIC_GROUPED_HOLDOUT")
    assert strategy_feasible(partitions, "T1_TRIP", "GROUP_K_FOLD_K2")
    assert not any(strategy_feasible(partitions, "T1_TRIP", f"GROUP_K_FOLD_K{k}") for k in (3, 4, 5))
    t1_k2_m2 = candidates.loc[
        candidates.Target.eq("T1_TRIP")
        & candidates.Split_Strategy.eq("GROUP_K_FOLD_K2")
        & candidates.Feature_Set.eq("M2_CHEMISTRY_PLUS_TEST")
    ]
    assert t1_k2_m2.Recommended_Status.eq("INVALID_CLASS_SUPPORT").all()
    assert strategy_feasible(partitions, "T2_TWIP", "GROUP_K_FOLD_K2")
    assert not strategy_feasible(partitions, "T2_TWIP", "GROUP_K_FOLD_K3")
    assert strategy_feasible(partitions, "T2_TWIP", "GROUP_K_FOLD_K4")
    assert not strategy_feasible(partitions, "T2_TWIP", "GROUP_K_FOLD_K5")
    assert not strategy_feasible(partitions, "T1_TRIP", "LEAVE_ONE_PAPER_OUT")
    assert not strategy_feasible(partitions, "T2_TWIP", "LEAVE_ONE_PAPER_OUT")

    script = Path(__file__).read_text(encoding="utf-8").lower()
    forbidden_code_tokens = ("import " + "sklearn", "from " + "sklearn", ".fit" + "(")
    assert not any(token in script for token in forbidden_code_tokens)
    assert not any(token in candidates.columns.str.lower().tolist() for token in ["accuracy", "auc", "f1", "precision", "recall"])


def run() -> None:
    conditions, master, core_by_set, before = load_inputs()
    group_keys = build_grouping_key_audit(conditions)
    group_distribution = build_group_distribution(conditions)
    class_support = build_class_support(conditions)
    m2_support = build_m2_support(conditions)
    negative_audit = build_negative_audit(conditions)
    positive_family = build_positive_family_audit(conditions)
    generalization = build_generalization(conditions)
    partitions = build_all_partitions(conditions, core_by_set)
    candidates = feature_expansion(partitions, core_by_set)
    manifest = build_manifest(partitions, candidates)

    SPLITS.mkdir(parents=True, exist_ok=True)
    group_keys.to_csv(GROUPING_KEY_PATH, index=False)
    group_distribution.to_csv(GROUP_DISTRIBUTION_PATH, index=False)
    class_support.to_csv(CLASS_SUPPORT_PATH, index=False)
    m2_support.to_csv(M2_SUPPORT_PATH, index=False)
    negative_audit.to_csv(NEGATIVE_AUDIT_PATH, index=False)
    positive_family.to_csv(POSITIVE_FAMILY_PATH, index=False)
    generalization.to_csv(GENERALIZATION_PATH, index=False)
    candidates.to_csv(SPLIT_CANDIDATES_PATH, index=False)
    manifest.to_csv(SPLIT_MANIFEST_PATH, index=False)
    write_chemistry_policy()
    write_architecture(conditions, partitions, class_support, m2_support)
    write_design_audit(conditions, partitions, candidates, m2_support, before)

    validate(
        conditions, master, group_distribution, class_support, negative_audit,
        partitions, candidates, manifest, before,
    )
    print("Grouped Split Design V1 generated and validated: no ML, transformation, resampling, or source-data change.")


if __name__ == "__main__":
    run()
