import pandas as pd
import numpy as np
import pytest
from src.data.merge_datasets import load_batch, merge_batches
from src.data.validate_dataset import (
    composition_sum_flags,
    duplicate_condition_flags,
    paper_doi_audit,
)
from src.features.build_features import derive_features, R_GAS

BASE = {
    "Paper_ID": ["P001"],
    "DOI": ["10.x/a"],
    "Condition_ID": ["C1"],
    "Experiment_Group_ID": ["G1"],
    "Fe_at% ": [50],
    "Ni_at%": [50],
}


def test_dataset_loading_and_schema(tmp_path):
    path = tmp_path / "a.xlsx"
    pd.DataFrame(BASE).to_excel(path, index=False, sheet_name="Extraction")
    frame, sheet = load_batch(path)
    assert sheet == "Extraction" and "Fe_at%" in frame and len(frame) == 1


def test_schema_difference_is_preserved(tmp_path):
    a = tmp_path / "a.xlsx"
    b = tmp_path / "b.xlsx"
    pd.DataFrame(BASE).to_excel(a, index=False)
    later = {k: v for k, v in BASE.items()}
    later["New scientific note"] = ["retain me"]
    pd.DataFrame(later).to_excel(b, index=False)
    merged, audit = merge_batches([a, b])
    assert "retain me" in merged.loc[1, "Unmapped_Fields"] and bool(
        audit.loc[1, "Requires_Manual_Review"]
    )


def test_canonical_schema_requires_traceability(tmp_path):
    path = tmp_path / "bad.xlsx"
    pd.DataFrame({"Paper_ID": ["P001"]}).to_excel(path, index=False)
    with pytest.raises(ValueError):
        merge_batches([path])


def test_composition_sum_check_does_not_normalize():
    df = pd.DataFrame({"Fe_at%": [60, 50], "Ni_at%": [50, 50]})
    flags = composition_sum_flags(df)
    assert flags.Composition_Sum_at_pct.tolist() == [
        110,
        100,
    ] and flags.Composition_Sum_Flag.tolist() == [True, False]


def test_duplicate_condition_detection():
    assert duplicate_condition_flags(
        pd.DataFrame({"Condition_ID": ["C1", "C1", "C2", None]})
    ).tolist() == [True, True, False, False]


def test_paper_doi_consistency():
    audit = paper_doi_audit(
        pd.DataFrame({"Paper_ID": ["P001", "P001"], "DOI": ["a", "b"]})
    )
    assert audit.loc[0, "DOI_count"] == 2 and not bool(audit.loc[0, "Consistent"])


def test_derived_feature_formulas_and_missing_constants():
    df = pd.DataFrame({"Fe_at%": [50], "Ni_at%": [50], "Strain_rate_s-1": [0.001]})
    props = pd.DataFrame(
        {
            "Element": ["Fe", "Ni"],
            "Atomic_radius_pm": [1, 1],
            "VEC": [8, 10],
            "Electronegativity_Pauling": [1, 3],
            "Melting_temperature_K": [1000, 2000],
        }
    )
    h = pd.DataFrame(
        {"Element_A": ["Fe"], "Element_B": ["Ni"], "Mixing_enthalpy_kJ_mol": [-2]}
    )
    got = derive_features(df, props, h).iloc[0]
    assert got.VEC_derived == 9 and np.isclose(
        got.Configurational_entropy_J_molK, R_GAS * np.log(2)
    )
    assert got.Mixing_enthalpy_kJ_mol == -2 and got.log10_strain_rate == -3
    assert got.Atomic_size_mismatch_delta_pct == 0
