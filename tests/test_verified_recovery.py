import hashlib
from pathlib import Path

import pandas as pd

from scripts.integrate_verified_recovery import CANON, DOIS, LEDGER, MANUAL, OUT, integrate


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_verified_recovery_is_non_destructive_and_provenanced():
    workbook_hashes = {p: digest(MANUAL / f"{p}_scientific_evidence_recovery.xlsx") for p in DOIS}
    before, after, recovered = integrate()
    assert len(before) == len(after) == 98
    pd.testing.assert_frame_equal(after[before.columns], before, check_dtype=False)
    assert after.Observation_ID.tolist() == before.Observation_ID.tolist()
    assert workbook_hashes == {p: digest(MANUAL / f"{p}_scientific_evidence_recovery.xlsx") for p in DOIS}
    required = ["Recovered_Value", "Page", "Evidence_Type", "Confidence", "Reviewer_Status"]
    assert recovered[required].fillna("").ne("").all().all()
    assert after.loc[after.Paper_ID.eq("P016"), "Recovered_SFE_mJ_m2"].isna().all() if "Recovered_SFE_mJ_m2" in after else True
    assert after.loc[after.Paper_ID.eq("P016"), "Recovered_SFE_assumed_for_calculation_mJ_m2"].notna().sum() == 2


def test_unresolved_targets_are_not_negative_and_special_values_are_separate():
    out = pd.read_csv(OUT)
    p7_5 = out[out.ML_Condition_ID.eq("P007_MC03")].iloc[0]
    assert pd.isna(p7_5.Recovered_TRIP) and pd.isna(p7_5.Recovered_TWIP)
    p6 = out[out.Paper_ID.eq("P006")]
    assert p6.Recovered_ISFE_DFT_0K_mJ_m2.notna().all()
    assert p6.SFE_mJ_m2.isna().all()
    assert p6.Recovered_DeltaG_FCC_HCP_300K_J_mol.tolist() == [87, -34, -276]


def test_ledger_and_identifiers_cover_every_integrated_value():
    out = pd.read_csv(OUT)
    ledger = pd.read_csv(LEDGER, dtype=str, keep_default_na=False)
    for row in out.itertuples():
        for col in out.columns:
            if col.startswith("Recovered_") and pd.notna(getattr(row, col)):
                feature = col.removeprefix("Recovered_")
                hit = ledger[(ledger.Observation_ID == row.Observation_ID) & (ledger.Feature_Name == feature)]
                assert len(hit) == 1
                assert hit.iloc[0].Reviewer_Status != ""
                assert hit.iloc[0].Page != ""
