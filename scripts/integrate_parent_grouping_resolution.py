"""Integrate the reviewed P006/P007 hierarchy into recovery_v3.

The recovery-v2 rows and scientific values are retained.  The only existing
field updated is ML_Condition_ID for the eight reviewed condition rows; all new
identity levels and aggregate-property fields are additive.  P007 interrupted
test observations are appended as correlated children, never as ML samples.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v2.csv"
BOOK = ROOT / "data/interim/manual_recovery/P006_P007_parent_replicate_grouping_resolution.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v3.csv"
AUDIT = ROOT / "reports/P006_P007_GROUPING_RESOLUTION_AUDIT.md"
TABLE = ROOT / "reports/tables/p006_p007_recovery_v3_hierarchy.csv"

NEW_FIELDS = [
    "Study_Series_ID", "Material_Parent_ID", "Physical_Batch_ID", "Replicate_ID",
    "Leakage_Group_Strict", "Leakage_Group_Material", "Parent_Linkage_Status",
    "Aggregate_Property_Status", "Parent_ML_Condition_ID", "YS_mean",
    "YS_uncertainty", "UTS_mean", "UTS_uncertainty", "TE_mean",
    "TE_uncertainty", "UE_mean", "UE_uncertainty", "Replicate_n",
    "uncertainty_type",
]


def _blank(columns):
    return {c: pd.NA for c in columns}


def integrate() -> tuple[pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(SOURCE)
    sheets = pd.read_excel(BOOK, sheet_name=None)
    out = source.copy()
    for field in NEW_FIELDS:
        if field not in out:
            out[field] = pd.NA

    for sheet in ("P006_Parent_Grouping", "P007_Parent_Grouping"):
        for decision in sheets[sheet].itertuples(index=False):
            idx = out.index[out.Condition_ID.eq(decision.Legacy_Condition_ID)]
            assert len(idx) == 1
            i = idx[0]
            out.at[i, "ML_Condition_ID"] = decision.ML_Condition_ID
            out.at[i, "Study_Series_ID"] = decision.Study_Series_ID
            out.at[i, "Material_Parent_ID"] = decision.Material_Parent_ID
            out.at[i, "Leakage_Group_Strict"] = decision.Leakage_Group_Strict
            out.at[i, "Leakage_Group_Material"] = decision.Leakage_Group_Material
            out.at[i, "Parent_Linkage_Status"] = decision.Parent_linkage_status
            out.at[i, "Aggregate_Property_Status"] = decision.Mechanical_values_are_aggregate
            out.at[i, "Parent_ML_Condition_ID"] = decision.ML_Condition_ID
            # Batch/replicate IDs deliberately remain missing.

    aggregate = sheets["P007_Aggregate_Properties"]
    for prop in aggregate.itertuples(index=False):
        i = out.index[out.ML_Condition_ID.eq(prop.ML_Condition_ID)][0]
        values = {
            "YS_mean": prop.YS_MPa_mean, "YS_uncertainty": prop.YS_MPa_pm,
            "UTS_mean": prop.UTS_MPa_mean, "UTS_uncertainty": prop.UTS_MPa_pm,
            "TE_mean": prop.TE_pct_mean, "TE_uncertainty": prop.TE_pct_pm,
            "UE_mean": prop.UE_pct_mean, "UE_uncertainty": prop.UE_pct_pm,
            "Aggregate_Property_Status": prop.Aggregation_status,
            "uncertainty_type": "UNKNOWN_REPORTED_PM",
        }
        for field, value in values.items():
            out.at[i, field] = value

    appended = []
    for stage in sheets["P007_Stage_Linkage"].itertuples(index=False):
        parent = out[out.ML_Condition_ID.eq(stage.Parent_ML_Condition_ID)].iloc[0]
        row = _blank(out.columns)
        # Only identity, directly reported strain, and provenance-safe grouping
        # metadata are copied. No parent property/target is duplicated.
        row.update({
            "Paper_ID": "P007", "DOI": parent.DOI,
            "Condition_ID": stage.Stage_Observation_ID,
            "Observation_ID": stage.Stage_Observation_ID,
            "Deformation_Stage_ID": stage.Stage_Observation_ID,
            "Deformation_stage": f"{stage.Nominal_or_local_strain_pct:g}% reported strain",
            "ML_Condition_ID": stage.Parent_ML_Condition_ID,
            "Parent_ML_Condition_ID": stage.Parent_ML_Condition_ID,
            "Study_Series_ID": "P007_SERIES01", "Material_Parent_ID": "P007_MAT01",
            "Leakage_Group_Strict": "P007_SERIES01", "Leakage_Group_Material": "P007_MAT01",
            "Parent_Linkage_Status": stage.Parent_linkage_status,
            "Data_Origin": "EXPERIMENTAL", "Observation_Role": "REPEATED_STAGE",
            "Grouping_Confidence": stage.Confidence, "Grouping_Review_Required": 0,
            "Grouping_Reason": stage.Implementation_rule,
            "Source_File": BOOK.name, "Source_Sheet": "P007_Stage_Linkage",
            "Source_location": stage.Source_location,
        })
        appended.append(row)
    out = pd.concat([out, pd.DataFrame(appended, columns=out.columns)], ignore_index=True)
    validate(source, out)
    out.to_csv(OUT, index=False)
    selected = out[out.Paper_ID.isin(["P006", "P007"])][
        ["Paper_ID", "Condition_ID", "Observation_ID", "Observation_Role"] + NEW_FIELDS[:9]
    ]
    selected.to_csv(TABLE, index=False)
    write_audit(source, out)
    return source, out


def validate(source: pd.DataFrame, out: pd.DataFrame) -> None:
    assert len(out) == len(source) + 5
    permitted = {"ML_Condition_ID"}
    stable = [c for c in source.columns if c not in permitted]
    pd.testing.assert_frame_equal(out.loc[: len(source)-1, stable].reset_index(drop=True), source[stable], check_dtype=False)
    assert out.loc[: len(source)-1, "Condition_ID"].tolist() == source.Condition_ID.tolist()
    p6 = out[(out.Paper_ID.eq("P006")) & out.Condition_ID.str.match(r"P006_C0[1-3]", na=False)]
    p7 = out[(out.Paper_ID.eq("P007")) & out.Condition_ID.str.match(r"P007_C0[1-5]", na=False)]
    stages = out[(out.Paper_ID.eq("P007")) & out.Observation_Role.eq("REPEATED_STAGE")]
    assert p6.Material_Parent_ID.nunique() == 3 and set(p6.Study_Series_ID) == {"P006_SERIES01"}
    assert set(p7.Material_Parent_ID) == {"P007_MAT01"} and set(p7.Study_Series_ID) == {"P007_SERIES01"}
    assert p6.Physical_Batch_ID.isna().all() and p7.Physical_Batch_ID.isna().all()
    assert p6.Replicate_ID.isna().all() and p7.Replicate_ID.isna().all()
    assert p7.Replicate_n.isna().all()
    assert len(stages) == 5 and stages.Observation_ID.is_unique
    assert (stages.Parent_ML_Condition_ID == stages.ML_Condition_ID).all()
    assert set(stages.ML_Condition_ID) <= set(p7.ML_Condition_ID)
    assert not stages.Observation_Role.eq("INDEPENDENT_CONDITION").any()
    assert stages.Replicate_ID.isna().all() and stages.Physical_Batch_ID.isna().all()


def write_audit(source: pd.DataFrame, out: pd.DataFrame) -> None:
    p6 = out[(out.Paper_ID.eq("P006")) & out.Condition_ID.str.match(r"P006_C", na=False)]
    p7 = out[(out.Paper_ID.eq("P007")) & out.Condition_ID.str.match(r"P007_C", na=False)]
    stages = out[(out.Paper_ID.eq("P007")) & out.Observation_Role.eq("REPEATED_STAGE")]
    def table(df, cols): return df[cols].to_markdown(index=False)
    before = source[source.Paper_ID.isin(["P006", "P007"])].ML_Condition_ID.nunique()
    after = pd.concat([p6, p7]).ML_Condition_ID.nunique()
    AUDIT.write_text(f"""# P006/P007 grouping resolution audit

## Preservation

- recovery_v2 rows: **{len(source)}**; recovery_v3 rows: **{len(out)}**. All existing rows remain in their original order.
- Existing scientific/source cells are unchanged. Only the reviewed `ML_Condition_ID` metadata changes on eight parent rows; twenty additive hierarchy/property fields were introduced.
- Five workbook-backed P007 stage children were added. No ML was trained and no replicate or specimen was synthesized.

## 1. P006 final hierarchy

{table(p6, ['Condition_ID','Study_Series_ID','Material_Parent_ID','ML_Condition_ID','Leakage_Group_Strict','Physical_Batch_ID','Replicate_ID'])}

## 2. P007 final hierarchy

{table(p7, ['Condition_ID','Study_Series_ID','Material_Parent_ID','ML_Condition_ID','Leakage_Group_Strict','Physical_Batch_ID','Replicate_ID'])}

## 3–6. Group and unknown-ID counts

| Audit | P006 | P007 |
|---|---:|---:|
| Material parents | {p6.Material_Parent_ID.nunique()} | {p7.Material_Parent_ID.nunique()} |
| Study series | {p6.Study_Series_ID.nunique()} | {p7.Study_Series_ID.nunique()} |
| Parent conditions with unknown physical batch | {p6.Physical_Batch_ID.isna().sum()} | {p7.Physical_Batch_ID.isna().sum()} |
| Parent conditions with unknown replicate ID | {p6.Replicate_ID.isna().sum()} | {p7.Replicate_ID.isna().sum()} |

## 7. Aggregate-property handling

P007 Table 3 is represented by separate `YS_mean`, `YS_uncertainty`, `UTS_mean`, `UTS_uncertainty`, `TE_mean`, `TE_uncertainty`, `UE_mean`, and `UE_uncertainty` fields. All five rows have `uncertainty_type=UNKNOWN_REPORTED_PM`; all `Replicate_n` values remain NA. The ± values created **zero** synthetic replicate rows.

## 8. Stage-child handling

{table(stages, ['Observation_ID','Parent_ML_Condition_ID','ML_Condition_ID','Observation_Role','Leakage_Group_Strict'])}

All five are correlated `REPEATED_STAGE` children. Split assignment must use their parent `ML_Condition_ID` (or the stricter series group), so a child cannot cross folds independently of its parent.

## 9. Independent ML-condition counts before vs after

The P006/P007 identity strings comprised **{before}** unique legacy ML-condition IDs before resolution and **{after}** reviewed ML conditions after resolution (3 P006 + 5 P007). The five new stage rows add **0** independent ML conditions.

## 10. Leakage risks before vs after

Before: parent/material/study/batch/replicate concepts were not separately represented, P007 sibling conditions could be split without a shared material key, and the interrupted stages were absent. After: strict study groups, material parents, distinct ML conditions, explicit unknown batch/replicate fields, and child-to-parent linkage are separate. Residual risk is controlled—not erased—because physical batch and replicate metadata remain genuinely unknown.

## 11. Remaining unresolved P1 issues

P006/P007 parent-linkage is **resolved at the material/study hierarchy level** and can leave the P1 blocker list. Unknown `Physical_Batch_ID`, `Replicate_ID`, P007 Table 3 replicate count, and ± statistic type remain metadata limitations, not hierarchy blockers. Other P1 issues remain: P007 A600-5 target review, broader target ambiguity, computational-domain separation, small/imbalanced support, empty descriptor reference constants, feature-leakage eligibility, and final target selection. No ML was trained.
""", encoding="utf-8")


if __name__ == "__main__":
    integrate()
