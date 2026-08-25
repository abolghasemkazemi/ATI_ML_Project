"""Generate the conservative, stage-aware identity audit for the 19-paper data.

The source table is immutable input.  This module adds identities and review
metadata only; it never edits extracted scientific fields or target values.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/interim/master_19papers_post_safe_qc.csv"
OUTPUT = ROOT / "data/interim/master_19papers_hierarchical_ids.csv"
TABLES = ROOT / "reports/tables"
AUDIT = ROOT / "reports/HIERARCHICAL_GROUPING_AUDIT.md"

GROUPING_REVIEW_PAPERS = {"P006", "P007", "P016"}
PURE_MD_PAPERS = {"P017", "P018"}
HYBRID_PAPERS = {"P006", "P009", "P010", "P012", "P015"}
STAGE_SERIES = {"P001", "P004", "P005", "P013"}


def data_origin(row):
    if row.Paper_ID in PURE_MD_PAPERS:
        return "MD"
    if row.Paper_ID == "P019":
        return "OTHER_COMPUTATIONAL"
    if row.Paper_ID == "P002" and row.Condition_ID == "P002_C05":
        return "CALPHAD"
    if row.Paper_ID in HYBRID_PAPERS:
        return "HYBRID"
    return "EXPERIMENTAL"


def observation_role(row):
    if row.Row_Role == "EXPERIMENTAL_REPEATED_STAGE":
        return "REPEATED_STAGE"
    if row.Row_Role == "EXPERIMENTAL_SUMMARY":
        return "SUMMARY" if row.Condition_ID == "P002_C04" else "COMPUTATIONAL_CONDITION"
    if row.Row_Role.startswith("COMPUTATIONAL_"):
        return "COMPUTATIONAL_CONDITION"
    return "INDEPENDENT_CONDITION"


def parent_id(row):
    if row.Paper_ID == "P001" and row.Condition_ID in {
        "P001_C01", "P001_C04", "P001_C05", "P001_C06", "P001_C07", "P001_C08"
    }:
        return "P001_PE01"
    if row.Paper_ID in {"P004", "P005", "P013"}:
        return f"{row.Paper_ID}_PE01"
    return row.Condition_ID.replace("_C", "_PE")


def ml_condition_id(row, parent):
    # A strain series is one test condition; stage is represented separately.
    if row.Paper_ID == "P001" and row.Condition_ID in {
        "P001_C01", "P001_C04", "P001_C05", "P001_C06", "P001_C07", "P001_C08"
    }:
        return "P001_MC01"
    if row.Paper_ID in {"P004", "P005", "P013"}:
        return f"{row.Paper_ID}_MC01"
    return parent.replace("_PE", "_MC")


def grouping_reason(row, role):
    if row.Paper_ID == "P001" and row.Condition_ID in {"P001_C04", "P001_C05", "P001_C06", "P001_C07", "P001_C08"}:
        return "Processing text explicitly links the local-strain observation to test condition P001_C01."
    if row.Paper_ID in {"P004", "P005", "P013"}:
        return "Extracted stage metadata identifies observations from one interrupted or in-situ tensile series."
    if row.Paper_ID in GROUPING_REVIEW_PAPERS:
        return "Specimen identity and condition-to-test-series linkage are absent from the extraction; verify them in the paper."
    if role == "COMPUTATIONAL_CONDITION":
        return "Computational condition is isolated from experimental parents and experimental condition counts."
    if role == "SUMMARY":
        return "Reference summary is retained but is not an independent condition."
    return "Distinct extracted condition retained as a conservative parent; no cross-row specimen linkage is documented."


def build_hierarchy(source):
    out = source.copy()
    out.insert(out.columns.get_loc("Experiment_Group_ID") + 1,
               "Original_Experiment_Group_ID", out["Experiment_Group_ID"])
    out["Parent_Experiment_ID"] = [parent_id(r) for r in out.itertuples()]
    out["ML_Condition_ID"] = [ml_condition_id(r, p) for r, p in zip(out.itertuples(), out.Parent_Experiment_ID)]
    out["Observation_ID"] = [f"OBS{i:03d}" for i in range(1, len(out) + 1)]
    out["Data_Origin"] = [data_origin(r) for r in out.itertuples()]
    out["Observation_Role"] = [observation_role(r) for r in out.itertuples()]
    out["Deformation_Stage_ID"] = pd.NA
    counters = {}
    for i, row in out[out.Observation_Role.eq("REPEATED_STAGE")].iterrows():
        key = row.ML_Condition_ID
        counters[key] = counters.get(key, 0) + 1
        out.at[i, "Deformation_Stage_ID"] = f"{key}_DS{counters[key]:02d}"
    out["Grouping_Review_Required"] = out.Paper_ID.isin(GROUPING_REVIEW_PAPERS).astype(int)
    out["Grouping_Confidence"] = out.Grouping_Review_Required.map({0: "HIGH", 1: "LOW"})
    out["Grouping_Reason"] = [grouping_reason(r, role) for r, role in zip(out.itertuples(), out.Observation_Role)]
    return out


def collapse_labels(group):
    """Condition result without majority voting; preserve sequential activation."""
    result = {}
    for target in ("TRIP", "TWIP"):
        values = set(group[target].dropna().astype(int))
        result[target] = next(iter(values)) if len(values) == 1 else (1 if values == {0, 1} and group.Observation_Role.eq("REPEATED_STAGE").any() else pd.NA)
    return pd.Series(result)


def conflict_table(out):
    rows = []
    for old_id, group in out.groupby("Original_Experiment_Group_ID", sort=True):
        conflict_targets = [t for t in ("TRIP", "TWIP") if group[t].dropna().nunique() > 1]
        if not conflict_targets:
            continue
        sequential = group.Observation_Role.eq("REPEATED_STAGE").any() and group.ML_Condition_ID.nunique() < len(group)
        after = any(sg[t].dropna().nunique() > 1 and not sg.Observation_Role.eq("REPEATED_STAGE").any()
                    for _, sg in group.groupby("ML_Condition_ID") for t in conflict_targets)
        kind = "SEQUENTIAL_MECHANISM_EVOLUTION" if sequential else "ARTIFICIAL_GROUPING_CONFLICT"
        explanation = ("The old group pooled deformation stages; changing stage-specific labels are retained as sequential activation."
                       if sequential else "The old group pooled distinct compositions, processing states, temperatures, rates, or computational conditions; the new ML conditions do not conflict.")
        rows.append({
            "Paper_ID": group.Paper_ID.iloc[0], "Original_Experiment_Group_ID": old_id,
            "New_Parent_Experiment_ID": "|".join(group.Parent_Experiment_ID.unique()),
            "ML_Condition_ID": "|".join(group.ML_Condition_ID.unique()),
            "Original_Conflict": "+".join(conflict_targets),
            "Conflict_After_Regrouping": "YES" if after else "NO",
            "Conflict_Type": kind, "Explanation": explanation,
            "Paper_Review_Required": 1 if group.Paper_ID.iloc[0] in GROUPING_REVIEW_PAPERS else 0,
        })
    return pd.DataFrame(rows)


FEATURES = {
    "Grain_size": ["Grain_size_um"], "SFE": ["SFE_mJ_m2"], "SFE_method": ["SFE_method"],
    "Initial_FCC_fraction": ["Initial_FCC_fraction"], "Initial_HCP_fraction": ["Initial_HCP_fraction"],
    "DeltaG": ["DeltaG_FCC_HCP_J_mol"], "Strain_rate": ["Strain_rate_s-1"],
    "Test_temperature": ["Test_T_K"],
    "Processing_information": ["Processing_route", "Homogenization_T_K", "Annealing_T_K"],
    "Mechanical_properties": ["YS_MPa", "UTS_MPa", "Elongation_pct"],
    "TRIP_evidence": ["Evidence_TRIP"], "TWIP_evidence": ["Evidence_TWIP"],
}


def recovery_plan(source):
    rows = []
    for pid, group in source.groupby("Paper_ID", sort=True):
        row = {"Paper_ID": pid, "DOI": group.DOI.iloc[0]}
        for name, cols in FEATURES.items():
            row[name] = "ALREADY_AVAILABLE" if any(group[c].notna().any() for c in cols) else "REQUIRES_PAPER_REVIEW"
        rows.append(row)
    return pd.DataFrame(rows)


def manual_plan(source, out):
    rows = []
    for pid, group in out.groupby("Paper_ID", sort=True):
        original = source.loc[group.index]
        target = original.Target_Review_Status.eq("REVIEW_REQUIRED").any()
        grouping = group.Grouping_Review_Required.any()
        missing = any(original[c].isna().any() for cols in FEATURES.values() for c in cols)
        checks = []
        if target: checks.append("condition-specific TRIP/TWIP evidence and negative-label basis")
        if grouping: checks.append("specimen identity, replicate identity, and test-series linkage")
        if missing: checks.append("tables/figures/supplement for missing major descriptors")
        experimental_conditions = group[group.Observation_Role.isin(["INDEPENDENT_CONDITION", "REPEATED_STAGE"]) & group.Data_Origin.isin(["EXPERIMENTAL", "HYBRID"])]
        rows.append({"Paper_ID": pid, "DOI": group.DOI.iloc[0], "Number_of_observations": len(group),
                     "Number_of_parent_experiments": group.Parent_Experiment_ID.nunique(),
                     "Number_of_ML_conditions": experimental_conditions.ML_Condition_ID.nunique(),
                     "Number_of_repeated_stage_observations": group.Observation_Role.eq("REPEATED_STAGE").sum(),
                     "Target_review_needed": int(target), "Grouping_review_needed": int(grouping),
                     "Missing_feature_review_needed": int(missing),
                     "Priority": "P1" if target or grouping else ("P2" if missing else "P4"),
                     "Specific_items_to_check_in_original_paper": "; ".join(checks) or "No urgent issue"})
    return pd.DataFrame(rows)


def write_report(source, out, conflicts, recovery):
    experimental = out[out.Data_Origin.isin(["EXPERIMENTAL", "HYBRID"]) & ~out.Observation_Role.eq("COMPUTATIONAL_CONDITION")]
    comp = out[out.Observation_Role.eq("COMPUTATIONAL_CONDITION")]
    condition_rows = experimental[experimental.Observation_Role.isin(["INDEPENDENT_CONDITION", "REPEATED_STAGE"])]
    conditions = condition_rows.groupby("ML_Condition_ID").apply(collapse_labels, include_groups=False)
    parents = condition_rows.groupby("Parent_Experiment_ID").apply(collapse_labels, include_groups=False)
    def dist(frame):
        return [(t, int((frame[t] == 0).sum()), int((frame[t] == 1).sum()), int(frame[t].isna().sum())) for t in ("TRIP", "TWIP")]
    obs_dist = dist(out)
    cond_dist = dist(conditions)
    par_dist = dist(parents)
    sequential = conflicts.Conflict_Type.eq("SEQUENTIAL_MECHANISM_EVOLUTION")
    target_papers = sorted(out.loc[source.Target_Review_Status.eq("REVIEW_REQUIRED"), "Paper_ID"].unique())
    feature_papers = {name: sorted(recovery.loc[recovery[name].eq("REQUIRES_PAPER_REVIEW"), "Paper_ID"]) for name in FEATURES}
    def table(rows): return "\n".join(f"| {t} | {z} | {o} | {n} |" for t,z,o,n in rows)
    AUDIT.write_text(f"""# Hierarchical grouping audit

## Findings and redesign

The legacy `Experiment_Group_ID` was too coarse: it pooled different processing/test conditions and, in three groups, multiple deformation stages. Consequently, ten old groups appeared target-conflicted even when the rows described either distinct conditions or time-ordered mechanism activation. The redesign keeps paper provenance, assigns a conservative specimen/test parent, separates condition identity from row identity, and uses a stage ID only for linked deformation observations. No scientific value or TRIP/TWIP label was changed.

## Independence census

| Measure | Count |
|---|---:|
| Total observations | {len(out)} |
| Experimental observations (including experimental observations in hybrid studies) | {len(experimental)} |
| Computational observations (including computational roles in hybrid papers) | {len(comp)} |
| Hybrid-origin observations | {out.Data_Origin.eq('HYBRID').sum()} |
| Unresolved-origin observations | {out.Data_Origin.eq('UNRESOLVED').sum()} |
| Unique Parent_Experiment_ID (all origins) | {out.Parent_Experiment_ID.nunique()} |
| Unique experimental ML_Condition_ID | {condition_rows.ML_Condition_ID.nunique()} |
| Repeated deformation-stage observations | {out.Observation_Role.eq('REPEATED_STAGE').sum()} |
| Summary rows | {out.Observation_Role.eq('SUMMARY').sum()} |
| Unresolved grouping cases | {out.Grouping_Review_Required.sum()} |

## Target distributions

Mixed 0/1 stage series are represented as activation-positive at condition/parent level **and explicitly enumerated below**, rather than majority-voted or called conflicts.

### A. Observation level
| Target | 0 | 1 | unresolved |\n|---|---:|---:|---:|\n{table(obs_dist)}

### B. Independent experimental ML-condition level
| Target | 0 | 1 | unresolved |\n|---|---:|---:|---:|\n{table(cond_dist)}

### C. Experimental parent-experiment level
| Target | 0 | 1 | unresolved |\n|---|---:|---:|---:|\n{table(par_dist)}

Sequential stage-dependent groups are: **{', '.join(conflicts.loc[sequential, 'Original_Experiment_Group_ID'])}**.

## Previous conflict resolution

- Previous conflicting groups: **{len(conflicts)}**.
- Artificial grouping conflicts resolved: **{(~sequential).sum()}**.
- Legitimate sequential-mechanism cases: **{sequential.sum()}**.
- Genuinely ambiguous target conflicts after regrouping: **{conflicts.Conflict_After_Regrouping.eq('YES').sum()}**.
- Conflict groups requiring original-paper grouping review: **{conflicts.Paper_Review_Required.sum()}**.

The row-level grouping uncertainty is separate: **{out.Grouping_Review_Required.sum()} observations** in **P006, P007, and P016** need specimen/test linkage verification.

## Manual paper review

- Target labels/evidence: **{', '.join(target_papers)}**.
- Grouping: **P006, P007, P016**.
- Potential major-feature recovery (absence means only “not present in current extraction,” not “not reported”):
""" + "\n".join(f"  - {name}: {', '.join(pids) if pids else 'none'}" for name,pids in feature_papers.items()) + f"""

## Usable condition counts and readiness

- Revised independent experimental ML conditions: **{len(conditions)}**.
- TRIP-usable (nonmissing condition result): **{conditions.TRIP.notna().sum()}**.
- TWIP-usable: **{conditions.TWIP.notna().sum()}**.
- Joint TRIP/TWIP-usable: **{conditions[['TRIP','TWIP']].notna().all(axis=1).sum()}**.

These are label-availability counts, not proof of feature completeness or final eligibility. Pure computational rows are excluded; hybrid-paper rows count only where their observation role is experimental.

- **Final ML: NO.** Target evidence, 11 low-confidence grouping rows, sparse major descriptors, and small/imbalanced independent support remain unresolved.
- **Pilot ML: NO at present.** P1 label/grouping review should precede even exploratory performance estimates; pipeline-only dry runs remain acceptable but are not scientific ML results.
- **Targeted data expansion: YES.** Expansion should add genuinely independent, provenance-rich experimental conditions after existing-paper P1/P2 recovery, without resampling or synthetic data.
""", encoding="utf-8")


def main():
    source = pd.read_csv(SOURCE)
    out = build_hierarchy(source)
    TABLES.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)
    review_cols = ["Paper_ID", "DOI", "Original_Experiment_Group_ID", "Parent_Experiment_ID", "Condition_ID",
                   "ML_Condition_ID", "Observation_ID", "Deformation_Stage_ID", "Data_Origin", "Observation_Role",
                   "Grouping_Confidence", "Grouping_Review_Required", "Grouping_Reason"]
    out[review_cols].to_csv(TABLES / "hierarchical_id_review.csv", index=False)
    conflicts = conflict_table(out)
    conflicts.to_csv(TABLES / "group_conflict_resolution.csv", index=False)
    manual_plan(source, out).to_csv(TABLES / "paper_manual_review_plan.csv", index=False)
    recovery = recovery_plan(source)
    recovery.to_csv(TABLES / "existing_paper_feature_recovery_plan.csv", index=False)
    write_report(source, out, conflicts, recovery)


if __name__ == "__main__":
    main()
