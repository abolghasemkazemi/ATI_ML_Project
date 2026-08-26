import hashlib

import pandas as pd

from scripts.integrate_parent_grouping_resolution import BOOK, integrate


def test_recovery_v3_preserves_rows_and_scientific_values():
    digest = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    before, after = integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest() == digest
    assert len(before) == 108 and len(after) == 113
    stable = [c for c in before.columns if c != "ML_Condition_ID"]
    pd.testing.assert_frame_equal(after.loc[:107, stable].reset_index(drop=True), before[stable], check_dtype=False)


def test_p006_p007_grouping_and_unknown_identifiers():
    _, out = integrate()
    parents = out[out.Condition_ID.isin([f"P006_C0{i}" for i in range(1, 4)] + [f"P007_C0{i}" for i in range(1, 6)])]
    p6, p7 = parents[parents.Paper_ID.eq("P006")], parents[parents.Paper_ID.eq("P007")]
    assert set(p6.Material_Parent_ID) == {"P006_MAT_Ni20Fe20", "P006_MAT_Ni15Fe15", "P006_MAT_Ni15Fe10"}
    assert set(p7.Material_Parent_ID) == {"P007_MAT01"}
    assert set(p6.Leakage_Group_Strict) == {"P006_SERIES01"}
    assert set(p7.Leakage_Group_Strict) == {"P007_SERIES01"}
    assert parents.Physical_Batch_ID.isna().all()
    assert parents.Replicate_ID.isna().all()


def test_stage_and_aggregate_rows_cannot_create_pseudoreplication():
    _, out = integrate()
    stages = out[(out.Paper_ID.eq("P007")) & out.Observation_Role.eq("REPEATED_STAGE")]
    assert set(stages.Observation_ID) == {"P007_OBS_A6001_eps20", "P007_OBS_A6002_eps20", "P007_OBS_A60010_eps20", "P007_OBS_A60072_eps10", "P007_OBS_A60072_eps20"}
    assert (stages.Parent_ML_Condition_ID == stages.ML_Condition_ID).all()
    assert stages.Replicate_ID.isna().all()
    parents = out[out.Condition_ID.isin([f"P007_C0{i}" for i in range(1, 6)])]
    assert parents.Replicate_n.isna().all()
    assert set(parents.uncertainty_type) == {"UNKNOWN_REPORTED_PM"}
    assert len(parents) == 5  # ± values did not expand into rows
