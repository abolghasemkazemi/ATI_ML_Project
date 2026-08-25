import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_hierarchical_identity_artifacts_preserve_science_and_rows():
    subprocess.run([sys.executable, "scripts/build_hierarchical_ids.py"], cwd=ROOT, check=True)
    source = pd.read_csv(ROOT / "data/interim/master_19papers_post_safe_qc.csv")
    result = pd.read_csv(ROOT / "data/interim/master_19papers_hierarchical_ids.csv")
    review = pd.read_csv(ROOT / "reports/tables/hierarchical_id_review.csv")
    plan = pd.read_csv(ROOT / "reports/tables/paper_manual_review_plan.csv")
    conflicts = pd.read_csv(ROOT / "reports/tables/group_conflict_resolution.csv")
    recovery = pd.read_csv(ROOT / "reports/tables/existing_paper_feature_recovery_plan.csv")

    assert len(source) == len(result) == len(review) == 98
    assert result["Observation_ID"].is_unique
    assert result["Observation_ID"].notna().all()
    assert result["Condition_ID"].equals(source["Condition_ID"])
    assert result["Experiment_Group_ID"].equals(source["Experiment_Group_ID"])
    assert result["Original_Experiment_Group_ID"].equals(source["Experiment_Group_ID"])
    assert result[["TRIP", "TWIP"]].equals(source[["TRIP", "TWIP"]])
    assert set(result["Data_Origin"]) <= {
        "EXPERIMENTAL", "MD", "DFT", "CALPHAD", "OTHER_COMPUTATIONAL", "HYBRID", "UNRESOLVED"
    }
    assert set(result["Observation_Role"]) <= {
        "INDEPENDENT_CONDITION", "REPEATED_STAGE", "SUMMARY",
        "COMPUTATIONAL_CONDITION", "OTHER", "UNRESOLVED",
    }
    repeated = result["Observation_Role"].eq("REPEATED_STAGE")
    assert result.loc[repeated, "Deformation_Stage_ID"].notna().all()
    assert result.loc[~repeated, "Deformation_Stage_ID"].isna().all()
    assert set(plan["Paper_ID"]) == {f"P{i:03d}" for i in range(1, 20)}
    assert set(recovery["Paper_ID"]) == {f"P{i:03d}" for i in range(1, 20)}
    assert len(conflicts) == 10
    assert (conflicts["Conflict_After_Regrouping"] == "NO").all()
    assert (conflicts["Conflict_Type"] == "SEQUENTIAL_MECHANISM_EVOLUTION").sum() == 3
    assert result.loc[result["Observation_Role"].eq("COMPUTATIONAL_CONDITION"), "ML_Condition_ID"].notna().all()
    experimental_conditions = result[
        result["Data_Origin"].isin(["EXPERIMENTAL", "HYBRID"])
        & result["Observation_Role"].isin(["INDEPENDENT_CONDITION", "REPEATED_STAGE"])
    ]
    assert experimental_conditions["ML_Condition_ID"].nunique() == 55


def test_all_preexisting_columns_are_value_identical():
    source = pd.read_csv(ROOT / "data/interim/master_19papers_post_safe_qc.csv")
    result = pd.read_csv(ROOT / "data/interim/master_19papers_hierarchical_ids.csv")
    pd.testing.assert_frame_equal(result[source.columns], source, check_dtype=False)
