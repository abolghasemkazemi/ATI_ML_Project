"""Build source-paper recovery queues without changing canonical data.

The generated recovery ledger is deliberately separate from the canonical CSV.
Running this script recreates blank recovery fields; it never applies recovered
values to a scientific dataset.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data/interim/master_19papers_hierarchical_ids.csv"
PAPERS = ROOT / "data/raw/papers"
TABLES = ROOT / "reports/tables"

TARGET_REVIEW_PAPERS = {f"P{i:03d}" for i in range(1, 9)} | {
    f"P{i:03d}" for i in range(10, 19)
}
GROUPING_PAPERS = {"P006", "P007", "P016"}

# Display name, canonical fields, units, importance (1-5), ambiguity risk (1-5).
FEATURES = [
    ("grain size", ["Grain_size_um"], "as reported (currently µm field)", 5, 3),
    ("SFE", ["SFE_mJ_m2"], "as reported (currently mJ m^-2 field)", 5, 5),
    ("SFE method", ["SFE_method"], "method/text", 5, 4),
    ("initial FCC fraction", ["Initial_FCC_fraction"], "as reported", 5, 5),
    ("initial HCP fraction", ["Initial_HCP_fraction"], "as reported", 5, 5),
    ("DeltaG / transformation driving force", ["DeltaG_FCC_HCP_J_mol"], "as reported (currently J mol^-1 field)", 5, 5),
    ("strain rate", ["Strain_rate_s-1"], "as reported (currently s^-1 field)", 5, 3),
    ("test temperature", ["Test_T_K"], "as reported (currently K field)", 5, 2),
    ("processing history", ["Processing_route", "Cast_method", "Homogenization_T_K", "Homogenization_time_h", "Hot_rolling_T_K", "Hot_rolling_reduction_pct", "Cold_rolling_reduction_pct", "Annealing_T_K", "Annealing_time_min", "Cooling_route"], "mixed; preserve each reported unit", 5, 5),
    ("mechanical properties", ["YS_MPa", "UTS_MPa", "Elongation_pct", "Uniform_elongation_pct"], "mixed; preserve each reported unit", 3, 4),
    ("TRIP evidence", ["Evidence_TRIP"], "text/evidence", 5, 5),
    ("TWIP evidence", ["Evidence_TWIP"], "text/evidence", 5, 5),
    ("phase-transformation evidence", ["HCP_fraction_at_condition", "HCP_lath_or_lamella_note", "Characterization_methods"], "mixed; preserve each reported unit", 5, 5),
    ("specimen identity", [], "identifier/text", 5, 5),
    ("replicate identity", [], "identifier/text", 5, 5),
    ("condition-to-test-series linkage", ["Parent_Experiment_ID"], "identifier/text", 5, 5),
]


def clean(values):
    return [str(v).strip() for v in values if str(v).strip()]


def joined_original(row, fields):
    values = [(field, str(row[field]).strip()) for field in fields if str(row.get(field, "")).strip()]
    return " | ".join(f"{field}={value}" for field, value in values)


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_manifest(data, verify_pdfs=False):
    rows = []
    for pid, group in data.groupby("Paper_ID", sort=True):
        dois, titles = sorted(set(clean(group["DOI"]))), sorted(set(clean(group["Paper_Title"])))
        pdf_name = f"{pid}.pdf"
        available = (PAPERS / pdf_name).is_file()
        rows.append({
            "Paper_ID": pid,
            "DOI": dois[0] if len(dois) == 1 else "",
            "Title": titles[0] if len(titles) == 1 else "",
            "PDF_Filename": pdf_name,
            "PDF_Available": "YES" if available else "NO",
            "PDF_Verified": "PENDING" if available else "NO",
            "DOI_Match": "NOT_CHECKED",
            "Title_Match": "NOT_CHECKED",
            "Review_Status": "READY_FOR_MANUAL_VERIFICATION" if available else "PDF_REQUIRED",
            "Notes": "" if (len(dois) == 1 and len(titles) == 1) else "Title unavailable in repository" if not titles else "Conflicting repository metadata; manual review required",
        })
    return rows


def condition_rows(data):
    return [(key, group) for key, group in data.groupby(["Paper_ID", "ML_Condition_ID"], sort=True)]


def build_recovery(data):
    rows = []
    for _, row in data.sort_values("Observation_ID").iterrows():
        for name, fields, units, _, _ in FEATURES:
            rows.append({
                "Paper_ID": row.Paper_ID, "ML_Condition_ID": row.ML_Condition_ID,
                "Observation_ID": row.Observation_ID, "Feature_Name": name,
                "Original_Value": joined_original(row, fields), "Recovered_Value": "",
                "Units": units, "Evidence_Type": "", "Evidence_Location": "",
                "Page": "", "Figure": "", "Table": "", "Section": "",
                "Extraction_Method": "", "Confidence": "",
                "Reviewer_Status": "PENDING_SOURCE_REVIEW", "Reviewer_Notes": "",
            })
    return rows


def unique_values(group, field):
    values = sorted(set(clean(group[field])))
    return " | ".join(values)


def build_target_review(data):
    rows = []
    for (pid, condition), group in condition_rows(data):
        if pid not in TARGET_REVIEW_PAPERS:
            continue
        rows.append({
            "Paper_ID": pid, "ML_Condition_ID": condition,
            "TRIP_Current": unique_values(group, "TRIP"), "TWIP_Current": unique_values(group, "TWIP"),
            "TRIP_Evidence": unique_values(group, "Evidence_TRIP"), "TWIP_Evidence": unique_values(group, "Evidence_TWIP"),
            "Evidence_Type": "", "Evidence_Location": unique_values(group, "Source_location"),
            "Page": "", "Figure_Table": "", "Verification_Status": "PENDING_PDF_REVIEW",
            "Notes": "Current labels are read-only; verification must not silently relabel them.",
        })
    return rows


def build_grouping_review(data):
    aspects = ["specimen identity", "replicate identity", "condition identity", "test-series linkage", "deformation-stage linkage"]
    rows = []
    for (pid, condition), group in condition_rows(data):
        if pid not in GROUPING_PAPERS:
            continue
        for aspect in aspects:
            rows.append({
                "Paper_ID": pid, "ML_Condition_ID": condition,
                "Observation_IDs": " | ".join(group.Observation_ID), "Review_Aspect": aspect,
                "Current_Parent_Experiment_ID": unique_values(group, "Parent_Experiment_ID"),
                "Current_Grouping_Confidence": unique_values(group, "Grouping_Confidence"),
                "Evidence_Type": "", "Evidence_Location": "", "Page": "",
                "Figure_Table": "", "Verification_Status": "PENDING_PDF_REVIEW",
                "Reviewer_Notes": "Do not regroup automatically; retain the current hierarchy until evidence is reviewed.",
            })
    return rows


def build_feature_priority(data):
    conditions = condition_rows(data)
    rows = []
    for name, fields, _, importance, ambiguity in FEATURES:
        missing_conditions, papers = 0, set()
        for (pid, _), group in conditions:
            present = any(clean(group[field]) for field in fields) if fields else False
            if not present:
                missing_conditions += 1
                papers.add(pid)
        total = len(conditions)
        missing_pct = 100 * missing_conditions / total
        # Importance dominates; breadth and missingness matter, while ambiguity is a review cost.
        score = round(importance * 20 + (missing_conditions / total) * 15 + (len(papers) / 19) * 10 - ambiguity * 2, 2)
        rows.append({
            "Feature_Name": name, "Priority_Rank": 0, "Priority_Score": score,
            "Scientific_Importance_1_5": importance, "Missing_ML_Conditions": missing_conditions,
            "Total_ML_Conditions": total, "Missingness_Percent": f"{missing_pct:.2f}",
            "ML_Conditions_Potentially_Recoverable": missing_conditions, "Papers_Requiring_Review": len(papers),
            "Risk_of_Ambiguity_1_5": ambiguity,
            "Scoring_Rationale": "20×importance + 15×condition missing fraction + 10×paper breadth fraction − 2×ambiguity; recoverability is a review opportunity, not a claim the PDF reports the value.",
        })
    rows.sort(key=lambda r: (-r["Priority_Score"], r["Feature_Name"]))
    for rank, row in enumerate(rows, 1): row["Priority_Rank"] = rank
    return rows


def build_paper_queue(data):
    rows = []
    for pid, group in data.groupby("Paper_ID", sort=True):
        target = int(pid in TARGET_REVIEW_PAPERS)
        grouping = int(pid in GROUPING_PAPERS)
        major_missing = 0
        for _, fields, _, importance, _ in FEATURES[:10]:
            if importance >= 5 and not (fields and any(clean(group[f]) for f in fields)):
                major_missing += 1
        trip = set(clean(group.TRIP)); twip = set(clean(group.TWIP))
        negative = int("0.0" in trip or "0" in trip or "0.0" in twip or "0" in twip)
        joint = int(("1.0" in trip or "1" in trip) and ("1.0" in twip or "1" in twip))
        single = int(("1.0" in trip or "1" in trip) != ("1.0" in twip or "1" in twip))
        score = 30*target + 30*grouping + min(major_missing, 6)*5 + 10*negative + 8*single + 6*joint
        reasons = []
        if target: reasons.append("unresolved/condition-specific TRIP/TWIP evidence review")
        if grouping: reasons.append("P1 grouping identity/linkage review")
        if major_missing: reasons.append(f"{major_missing} major feature groups absent")
        if negative: reasons.append("negative-class evidence importance")
        if single: reasons.append("single-positive mechanism case")
        if joint: reasons.append("joint-positive mechanism case")
        rows.append({"Paper_ID": pid, "Priority_Rank": 0, "Priority_Score": score,
                     "Target_Evidence_Review": "YES" if target else "NO", "Grouping_Review": "YES" if grouping else "NO",
                     "Recoverable_Major_Feature_Gaps": major_missing, "Negative_Class_Importance": "YES" if negative else "NO",
                     "Single_Positive_Case": "YES" if single else "NO", "Joint_Positive_Case": "YES" if joint else "NO",
                     "Priority_Rationale": "; ".join(reasons)})
    rows.sort(key=lambda r: (-r["Priority_Score"], r["Paper_ID"]))
    for rank, row in enumerate(rows, 1): row["Priority_Rank"] = rank
    return rows


def validate_verified_recovery(rows):
    """Reject verified recovered values without explicit source provenance."""
    required = ["Recovered_Value", "Evidence_Type", "Evidence_Location", "Extraction_Method", "Confidence"]
    for number, row in enumerate(rows, 2):
        if row.get("Reviewer_Status") == "VERIFIED" and any(not str(row.get(k, "")).strip() for k in required):
            raise ValueError(f"Recovery row {number}: VERIFIED requires {', '.join(required)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-pdfs", action="store_true", help="record PDF presence; DOI/title matching remains manual")
    args = parser.parse_args()
    data = pd.read_csv(CANONICAL, dtype=str, keep_default_na=False)
    write_csv(PAPERS / "paper_manifest.csv", ["Paper_ID","DOI","Title","PDF_Filename","PDF_Available","PDF_Verified","DOI_Match","Title_Match","Review_Status","Notes"], build_manifest(data, args.verify_pdfs))
    recovery = build_recovery(data)
    validate_verified_recovery(recovery)
    write_csv(ROOT / "data/interim/scientific_data_recovery.csv", list(recovery[0]), recovery)
    target = build_target_review(data); write_csv(TABLES / "target_evidence_review.csv", list(target[0]), target)
    grouping = build_grouping_review(data); write_csv(TABLES / "grouping_pdf_review.csv", list(grouping[0]), grouping)
    priority = build_feature_priority(data); write_csv(TABLES / "feature_recovery_priority.csv", list(priority[0]), priority)
    queue = build_paper_queue(data); write_csv(TABLES / "paper_review_queue.csv", list(queue[0]), queue)
    print(f"Prepared {len(recovery)} blank recovery records for {data.Paper_ID.nunique()} papers; canonical data unchanged.")


if __name__ == "__main__":
    main()
