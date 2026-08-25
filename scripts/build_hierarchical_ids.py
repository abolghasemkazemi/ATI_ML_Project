"""Build the conservative observation hierarchy and its audit artifacts.

This script deliberately consumes the post-safe-QC table: scientific target
values are copied, never derived or edited.  The small set of paper-specific
decisions below is an auditable identity crosswalk, not a scientific relabeling.
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/interim/master_19papers_post_safe_qc.csv"
OUTPUT = ROOT / "data/interim/master_19papers_hierarchical_ids.csv"
REVIEW = ROOT / "reports/tables/hierarchical_id_review.csv"
PLAN = ROOT / "reports/tables/paper_manual_review_plan.csv"
AUDIT = ROOT / "reports/HIERARCHICAL_GROUPING_AUDIT.md"

STAGE_PAPERS = {"P001", "P004", "P005", "P013"}
GROUPING_REVIEW_PAPERS = {"P006", "P007", "P016"}
PURE_MD_PAPERS = {"P017", "P018"}
HYBRID_PAPERS = {"P006", "P009", "P010", "P012", "P015"}


def origin(row):
    if row.Paper_ID in PURE_MD_PAPERS:
        return "MD"
    if row.Paper_ID == "P019":
        return "OTHER_COMPUTATIONAL"
    if row.Paper_ID == "P002" and row.Condition_ID == "P002_C05":
        return "CALPHAD"
    if row.Paper_ID in HYBRID_PAPERS:
        return "HYBRID"
    return "EXPERIMENTAL"


def role(row):
    old = row.Row_Role
    if old == "EXPERIMENTAL_REPEATED_STAGE":
        return "REPEATED_STAGE"
    if old == "EXPERIMENTAL_SUMMARY":
        return "SUMMARY" if row.Condition_ID == "P002_C04" else "COMPUTATIONAL_CONDITION"
    if old.startswith("COMPUTATIONAL_"):
        return "COMPUTATIONAL_CONDITION"
    return "INDEPENDENT_CONDITION"


def parent(row):
    # Only explicitly documented strain series share a parent. Every other
    # condition gets its own conservative parent, preventing leakage.
    if row.Paper_ID == "P001" and row.Condition_ID in {"P001_C01", "P001_C04", "P001_C05", "P001_C06", "P001_C07", "P001_C08"}:
        return "P001_PE01"
    if row.Paper_ID in {"P004", "P005", "P013"}:
        return f"{row.Paper_ID}_PE01"
    return row.Condition_ID.replace("_C", "_PE")


def reason(row):
    if row.Paper_ID == "P001" and row.Condition_ID >= "P001_C04":
        return "Extracted processing text explicitly links this local-strain stage to P001_C01."
    if row.Paper_ID in {"P004", "P005", "P013"}:
        return "Rows are explicitly identified as stages of one interrupted or in-situ tensile series."
    if row.Paper_ID in GROUPING_REVIEW_PAPERS:
        return "Condition is kept separate; extracted fields do not fully identify specimen/test-series relationships."
    if role(row) == "COMPUTATIONAL_CONDITION":
        return "Computational condition is isolated from every experimental parent."
    if role(row) == "SUMMARY":
        return "Reference summary is retained but excluded from independent-condition counts."
    return "Distinct extracted condition retained as a conservative leakage-safe parent."


def label_distribution(frame, unit):
    rows = []
    for label in ["TRIP", "TWIP"]:
        if unit == "observation":
            values = frame[label]
        else:
            key = "Condition_ID" if unit == "independent condition" else "Parent_Experiment_ID"
            values = frame.groupby(key, dropna=True)[label].apply(
                lambda x: x.dropna().iloc[0] if len(x.dropna()) and x.dropna().nunique() == 1 else pd.NA
            )
        counts = values.astype("Int64").value_counts(dropna=False)
        rows.append((label, int(counts.get(0, 0)), int(counts.get(1, 0)), int(values.isna().sum())))
    return rows


def main():
    source = pd.read_csv(SOURCE)
    out = source.copy()
    # Retain the legacy field byte-for-byte and add its explicitly named alias.
    insert_at = out.columns.get_loc("Experiment_Group_ID") + 1
    out.insert(insert_at, "Original_Experiment_Group_ID", out["Experiment_Group_ID"])
    out["Parent_Experiment_ID"] = [parent(r) for r in out.itertuples()]
    out["Observation_ID"] = [f"OBS{i:03d}" for i in range(1, len(out) + 1)]
    out["Deformation_Stage_ID"] = pd.NA
    stage_counter = {}
    for i, r in out.iterrows():
        if role(r) == "REPEATED_STAGE":
            key = r.Parent_Experiment_ID
            stage_counter[key] = stage_counter.get(key, 0) + 1
            out.at[i, "Deformation_Stage_ID"] = f"{key}_DS{stage_counter[key]:02d}"
    out["Data_Origin"] = [origin(r) for r in out.itertuples()]
    out["Observation_Role"] = [role(r) for r in out.itertuples()]
    out["Grouping_Review_Required"] = out.Paper_ID.isin(GROUPING_REVIEW_PAPERS).astype(int)
    out["Grouping_Reason"] = [reason(r) for r in out.itertuples()]
    out["Confidence"] = out.Grouping_Review_Required.map({0: "HIGH", 1: "LOW"})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)

    review_cols = ["Paper_ID", "DOI", "Original_Experiment_Group_ID", "Parent_Experiment_ID",
                   "Condition_ID", "Observation_ID", "Deformation_Stage_ID", "Data_Origin",
                   "Observation_Role", "Grouping_Review_Required", "Grouping_Reason", "Confidence"]
    out[review_cols].to_csv(REVIEW, index=False)

    target_review = source.Target_Review_Status.eq("REVIEW_REQUIRED")
    feature_map = {
        "grain size": "Grain_size_um", "SFE": "SFE_mJ_m2",
        "initial FCC fraction": "Initial_FCC_fraction", "initial HCP fraction": "Initial_HCP_fraction",
        "strain rate": "Strain_rate_s-1", "test temperature": "Test_T_K",
        "processing information": "Processing_route",
    }
    plan_rows = []
    for pid, g in out.groupby("Paper_ID", sort=True):
        idx = g.index
        missing = [name for name, col in feature_map.items() if source.loc[idx, col].isna().any()]
        target = bool(target_review.loc[idx].any())
        grouping = bool(g.Grouping_Review_Required.any())
        checks = []
        if grouping:
            checks.append("specimen identity and condition-to-test-series linkage")
        if target:
            checks.append("condition-specific TRIP/TWIP evidence")
        if missing:
            checks.append("recoverable " + ", ".join(missing))
        plan_rows.append({
            "Paper_ID": pid, "DOI": g.DOI.iloc[0], "Number_of_rows": len(g),
            "Number_of_parent_experiments": g.Parent_Experiment_ID.nunique(),
            "Number_of_conditions": g.Condition_ID.nunique(),
            "Number_of_repeated_stage_rows": int(g.Observation_Role.eq("REPEATED_STAGE").sum()),
            "Target_label_review_needed": int(target), "Grouping_review_needed": int(grouping),
            "Missing_feature_review_needed": int(bool(missing)),
            "Priority": "P1" if target or grouping else ("P2" if missing else "P4"),
            "Specific_items_to_check_in_original_paper": "; ".join(checks) or "No urgent review",
        })
    pd.DataFrame(plan_rows).to_csv(PLAN, index=False)

    experimental = out[out.Observation_Role.isin(["INDEPENDENT_CONDITION", "REPEATED_STAGE", "SUMMARY"])]
    independent = out[out.Observation_Role.eq("INDEPENDENT_CONDITION")]
    computational = out[out.Observation_Role.eq("COMPUTATIONAL_CONDITION")]
    old_conflicts = set()
    for label in ["TRIP", "TWIP"]:
        old_conflicts |= {k for k, g in out.dropna(subset=[label]).groupby("Original_Experiment_Group_ID") if g[label].nunique() > 1}
    new_conflicts = set()
    for label in ["TRIP", "TWIP"]:
        new_conflicts |= {k for k, g in independent.dropna(subset=[label]).groupby("Parent_Experiment_ID") if g[label].nunique() > 1}
    grouping_papers = ", ".join(sorted(GROUPING_REVIEW_PAPERS))
    target_papers = ", ".join(sorted(out.loc[target_review, "Paper_ID"].unique()))
    feature_lines = []
    for name, col in feature_map.items():
        pids = sorted(out.loc[source[col].isna(), "Paper_ID"].unique())
        feature_lines.append(f"- **{name}:** {', '.join(pids) if pids else 'none'}")

    dist_lines = []
    for level, frame in [("observation", out), ("independent condition", independent),
                         ("parent experiment", independent)]:
        dist_lines.append(f"### {level.title()} level\n\n| Label | 0 | 1 | unresolved |\n|---|---:|---:|---:|")
        dist_lines += [f"| {lab} | {zero} | {one} | {na} |" for lab, zero, one, na in label_distribution(frame, level)]

    usable = independent[independent.Data_Origin.isin(["EXPERIMENTAL", "HYBRID"])]
    trip_usable = int(usable.TRIP.notna().sum())
    twip_usable = int(usable.TWIP.notna().sum())
    joint_usable = int(usable[["TRIP", "TWIP"]].notna().all(axis=1).sum())
    AUDIT.write_text(f"""# Hierarchical grouping audit

## Scope and counting rules

This audit preserves all {len(out)} source rows and their TRIP/TWIP values. `HYBRID` rows with an experimental condition count as experimental observations; pure MD/CALPHAD/other-computational rows count as computational. Summary rows are not independent conditions. Parent-level labels are reported only when all labelled independent conditions in that parent agree; no majority label is forced.

## Independence census

| Measure | Count |
|---|---:|
| A. Total observations | {len(out)} |
| B. Experimental observations | {len(experimental)} |
| C. Computational observations | {len(computational)} |
| D. Unique experimental Parent_Experiment_ID | {experimental[experimental.Observation_Role.ne('SUMMARY')].Parent_Experiment_ID.nunique()} |
| E. Independent experimental conditions | {len(independent)} |
| F. Repeated deformation-stage observations | {out.Observation_Role.eq('REPEATED_STAGE').sum()} |
| G. Summary rows | {out.Observation_Role.eq('SUMMARY').sum()} |
| H. Unresolved rows | {(out.Observation_Role.eq('UNRESOLVED') | out.Data_Origin.eq('UNRESOLVED')).sum()} |

## TRIP and TWIP distributions

{chr(10).join(dist_lines)}

## Conflict result

- Previously conflicting original groups: **{len(old_conflicts)}** ({', '.join(sorted(old_conflicts))}).
- Conflicts that disappear under the hierarchy: **{len(old_conflicts - new_conflicts)}**.
- Remaining parent-level conflicts: **{len(new_conflicts)}**. No remaining conflict is treated as a label error; stage evolution is excluded from independent-condition conflict tests.
- Genuinely scientifically ambiguous grouping rows: **{out.Grouping_Review_Required.sum()}** rows across **{len(GROUPING_REVIEW_PAPERS)}** papers.

## Required original-paper review

- **Grouping:** {grouping_papers}.
- **TRIP/TWIP labels:** {target_papers}.

### Recoverable-feature review by paper

{chr(10).join(feature_lines)}

## Currently usable independent experimental conditions

- **TRIP:** {trip_usable}
- **TWIP:** {twip_usable}
- **Joint TRIP/TWIP:** {joint_usable}

These counts include experimental conditions in `HYBRID` studies but exclude repeated stages, summaries, and purely computational conditions. They are availability counts, not a claim that all predictors are complete.
""", encoding="utf-8")


if __name__ == "__main__":
    main()
