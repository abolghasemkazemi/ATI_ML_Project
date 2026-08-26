import hashlib

import pandas as pd

from scripts.integrate_manual_mapping_resolution import BOOK, OUT, SOURCE, integrate


def test_recovery_v2_preserves_legacy_and_applies_resolution():
    digest = hashlib.sha256(BOOK.read_bytes()).hexdigest()
    before, after = integrate()
    assert hashlib.sha256(BOOK.read_bytes()).hexdigest() == digest
    assert len(before) == 98 and len(after) == 108
    # Scientific/source legacy fields are unchanged; only reviewed hierarchy metadata may differ.
    permitted = {"Parent_Experiment_ID", "ML_Condition_ID", "Observation_Role", "Grouping_Review_Required", "Grouping_Confidence", "Grouping_Reason"}
    stable = [c for c in before.columns if c not in permitted]
    pd.testing.assert_frame_equal(after.loc[:97, stable].reset_index(drop=True), before[stable], check_dtype=False)
    p16 = after[after.Paper_ID.eq("P016")]
    exact = p16[p16.Observation_Role.eq("INDEPENDENT_CONDITION")]
    assert set(exact.ML_Condition_ID) == {f"P016_MC_{t}" for t in ["400C_3min", "400C_10min", "650C_3min", "650C_10min", "750C_3min", "750C_10min"]}
    assert p16.Observation_Role.eq("LEGACY_COLLAPSED").sum() == 1
    assert p16.Observation_Role.eq("REPEATED_STAGE").sum() == 6


def test_targets_corrections_and_stage_independence():
    out = pd.read_csv(OUT)
    expected = {"P006_C01": (0, None), "P006_C02": (0, 1), "P006_C03": (1, None)}
    for cid, (trip, twip) in expected.items():
        row = out[out.Condition_ID.eq(cid)].iloc[0]
        assert row.Effective_TRIP == trip
        assert (pd.isna(row.Effective_TWIP) if twip is None else row.Effective_TWIP == twip)
    c3 = out[out.Condition_ID.eq("P006_C03")].iloc[0]
    assert c3.TWIP == 0 and c3.Target_Correction_TWIP == "INVALIDATE_TO_NA"
    stages = out[(out.Paper_ID.eq("P016")) & out.Observation_Role.eq("REPEATED_STAGE")]
    conditions = set(out[out.Observation_Role.eq("INDEPENDENT_CONDITION")].ML_Condition_ID)
    assert set(stages.ML_Condition_ID) <= conditions
    assert stages.Observation_ID.is_unique
