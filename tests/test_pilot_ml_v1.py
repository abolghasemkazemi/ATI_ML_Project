"""Regression tests for V17 QC, schema/splits, and Controlled Pilot ML V1."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, matthews_corrcoef
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from scripts import pilot_ml_v1 as pilot


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_extended_recovery_v17.csv"
QC = ROOT / "data/processed/master_extended_recovery_v17_qc.csv"
EXP = ROOT / "data/processed/experimental_condition_index_v17.csv"
COMP = ROOT / "data/processed/computational_condition_index_v17.csv"
SCHEMA = ROOT / "data/schema/feature_schema_v2.csv"
CANDIDATES = ROOT / "data/splits/split_candidates_v2.csv"
MANIFEST = ROOT / "data/splits/split_manifest_v2.csv"
MODEL_DIR = ROOT / "data/modeling/pilot_v1"
TABLE_DIR = ROOT / "reports/tables"


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="session", autouse=True)
def generated():
    before = digest(SOURCE)
    pilot.main()
    assert digest(SOURCE) == before == pilot.SOURCE_EXPECTED_SHA256


def test_source_shape_cells_and_na_mask_are_preserved():
    source, qc = read(SOURCE), read(QC)
    assert source.shape == (234, 584) and qc.shape == (234, 596)
    assert qc.columns[:584].tolist() == source.columns.tolist()
    pd.testing.assert_frame_equal(qc.iloc[:, :584], source, check_dtype=False)
    assert qc.iloc[:, :584].isna().equals(source.isna())


def test_source_targets_are_unchanged_and_na_never_becomes_zero():
    source, qc, exp = read(SOURCE), read(QC), read(EXP)
    for target in ["Effective_TRIP", "Effective_TWIP"]:
        pd.testing.assert_series_equal(qc[target], source[target], check_dtype=False)
        selected = source.loc[exp.Source_Row_Index.astype(int), target].reset_index(drop=True)
        pd.testing.assert_series_equal(exp[target], selected, check_dtype=False, check_names=False)
        assert set(source[target].dropna().astype(int)) <= {0, 1}


def test_experimental_and_computational_domains_are_separate():
    exp, comp = read(EXP), read(COMP)
    assert len(exp) == exp.ML_Condition_ID.nunique() == 69
    assert exp.Data_Origin.eq("EXPERIMENTAL").all() and exp.Observation_Role.eq("INDEPENDENT_CONDITION").all()
    assert not exp.Paper_ID.isin(["P017", "P018", "P019"]).any()
    assert len(comp) == 12 and comp.Paper_ID.eq("P017").all()
    assert comp.P017_Record_Role.eq("RECOVERED_EXACT_COMPUTATIONAL_CONDITION").all()


def test_current_target_counts():
    exp = read(EXP)
    assert (exp.Effective_TRIP.notna().sum(), exp.Effective_TRIP.eq(1).sum(), exp.Effective_TRIP.eq(0).sum()) == (37, 33, 4)
    assert (exp.Effective_TWIP.notna().sum(), exp.Effective_TWIP.eq(1).sum(), exp.Effective_TWIP.eq(0).sum()) == (36, 31, 5)
    assert exp[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum() == 30


def test_hcp_twip_truth_is_tagged_and_excluded_not_zero_in_fcc_strict():
    exp = read(EXP).set_index("ML_Condition_ID")
    for condition in pilot.HCP_TWIP_IDS:
        assert exp.loc[condition, "Effective_TWIP"] == 1
        assert exp.loc[condition, "TWIP_Phase_Category"] == "HCP_EPSILON"
        assert pd.isna(exp.loc[condition, "T2_FCC_TWIP_STRICT"])
    semantics = read(TABLE_DIR / "pilot_v1_target_semantics_audit.csv")
    excluded = semantics[(semantics.Target == "T2_FCC_TWIP_STRICT") & semantics.ML_Condition_ID.isin(pilot.HCP_TWIP_IDS)]
    assert excluded.Analysis_Label.isna().all()
    assert excluded.Analysis_Decision.str.contains("NOT_CONVERTED_TO_ZERO").all()


def test_feature_schema_v2_covers_every_qc_field():
    qc, schema = read(QC), read(SCHEMA)
    assert len(schema) == len(qc.columns) == 596
    assert schema.Column_Name.tolist() == qc.columns.tolist()
    assert set(schema.Schema_Role) <= pilot.ROLES and schema.Schema_Role.notna().all()
    assert schema.iloc[343:].V2_Review_Status.notna().all()


@pytest.mark.parametrize("field,role", [
    ("TWIP_Phase", "TARGET_ONLY"),
    ("Postfracture_HCP_fraction", "LEAKAGE_POST_TEST"),
    ("PostTest_FCC_fraction", "LEAKAGE_POST_TEST"),
    ("PostTest_HCP_fraction", "LEAKAGE_POST_TEST"),
    ("GND_density_m-2", "LEAKAGE_POST_TEST"),
    ("PostTest_Twin_Evidence", "LEAKAGE_POST_TEST"),
    ("TRIP_Onset_True_Stress_MPa", "LEAKAGE_MODEL_DERIVED"),
    ("WH_Rate_at_Slope_Change_MPa", "LEAKAGE_MODEL_DERIVED"),
    ("SDI_MPa", "LEAKAGE_MECHANICAL_OUTCOME"),
    ("Engineering_YS_MPa", "LEAKAGE_MECHANICAL_OUTCOME"),
    ("Engineering_UTS_MPa", "LEAKAGE_MECHANICAL_OUTCOME"),
    ("Engineering_Elongation_pct", "LEAKAGE_MECHANICAL_OUTCOME"),
    ("ThermoCalc_Software", "COMPUTATIONAL_ONLY"),
    ("ThermoCalc_Database", "COMPUTATIONAL_ONLY"),
])
def test_critical_feature_roles(field, role):
    assert read(SCHEMA).set_index("Column_Name").loc[field, "Schema_Role"] == role


def test_exact_six_leakage_safe_predictors_and_no_new_descriptors():
    manifest = read(MODEL_DIR / "M2_predictor_manifest.csv")
    assert manifest.Feature_Name.tolist() == pilot.M2_FEATURES and len(manifest) == 6
    assert manifest.Schema_Role.isin(["PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"]).all()
    forbidden = ["paper", "doi", "group", "post", "gnd", "kam", "trip", "twip", "twin", "yield", "uts", "elongation", "sdi", "onset", "thermocalc"]
    assert all(not any(token in name.lower() for token in forbidden) for name in manifest.Feature_Name)
    assert not set(manifest.Feature_Name) & {"VEC", "delta", "Omega", "entropy", "Atomic_size_misfit_pct"}


def test_chemistry_source_safeguards():
    exp = read(EXP).set_index("ML_Condition_ID")
    assert exp.loc["P023_MC_650_15_RT", "M2_Composition_Source"] == "NOMINAL"
    p022 = exp[exp.Paper_ID == "P022"]
    assert p022.M2_Composition_Source.eq("UNAVAILABLE_POLICY_REJECTED").all()
    assert p022[["M2_Fe_at%", "M2_Mn_at%", "M2_Co_at%", "M2_Cr_at%"]].isna().all().all()
    assert pd.isna(exp.loc["P015_MC_298K", "M2_Co_at%"])
    assert exp.loc["P011_MC_A10_298K", "M2_Fe_at%"] == 50
    audit = read(ROOT / "reports/CHEMISTRY_SOURCE_AUDIT_V17.csv")
    assert not audit.Local_EDS_Promoted_to_Bulk.any()
    assert not audit.P022_Raw_Atomic_Ratio_Normalized.any()
    assert not audit.Missing_Element_Filled_with_Zero.any()


@pytest.mark.parametrize("name,n,pos,neg", [
    ("TRIP_M2_complete_cases.csv", 18, 17, 1),
    ("TWIP_ANY_M2_complete_cases.csv", 18, 13, 5),
    ("TWIP_FCC_STRICT_M2_complete_cases.csv", 9, 4, 5),
])
def test_complete_case_matrices_no_imputation_resampling_or_synthetic(name, n, pos, neg):
    matrix = read(MODEL_DIR / name)
    assert (len(matrix), matrix.Target_Value.eq(1).sum(), matrix.Target_Value.eq(0).sum()) == (n, pos, neg)
    assert matrix[pilot.M2_FEATURES].notna().all().all() and matrix.Complete_Case.all()
    assert not matrix.Imputation_Applied.any() and not matrix.Resampling_Applied.any() and not matrix.Synthetic_Sample.any()
    assert matrix.ML_Condition_ID.nunique() == len(matrix)
    assert not matrix.Paper_ID.isin(["P017", "P018", "P019"]).any()


def test_exclusion_ledger_preserves_na_and_documents_policy_rejection():
    ledger = read(MODEL_DIR / "M2_exclusion_ledger.csv")
    assert len(ledger) == 69 * 3 and not ledger.NA_Converted_To_Zero.any()
    assert ledger[ledger.Paper_ID == "P022"].Exclusion_Reason.str.contains("CHEMISTRY_POLICY_REJECTED").all()
    hcp = ledger[(ledger.Target == "T2_FCC_TWIP_STRICT") & ledger.ML_Condition_ID.isin(pilot.HCP_TWIP_IDS)]
    assert hcp.Analysis_Target_Value.isna().all() and hcp.Exclusion_Reason.str.contains("NOT_ZERO").all()


def test_selected_splits_are_supported_groupkfold_k3():
    selected = read(CANDIDATES).query("Selected")
    assert set(selected.Target) == {"T2_ANY_TWIP"}
    assert set(selected.Evidence_Pool) == {"ALL_VERIFIED_USABLE", "STRICT_DIRECT_EVIDENCE_ONLY"}
    assert selected.k.eq(3).all() and selected.groupby("Evidence_Pool").size().eq(3).all()
    assert selected.Strategy.eq("GROUP_KFOLD").all()
    assert selected.Group_Overlap_n.eq(0).all() and selected.Paper_Overlap_n.eq(0).all()
    assert selected.Both_Classes_Train.all() and selected.Both_Classes_Test.all() and selected.M2_Complete.all()


def test_unsupported_trip_and_fcc_strict_are_not_forced():
    candidates = read(CANDIDATES)
    trip = candidates[(candidates.Target == "T1_TRIP") & (candidates.Evidence_Pool == "ALL_VERIFIED_USABLE")]
    fcc = candidates[(candidates.Target == "T2_FCC_TWIP_STRICT") & (candidates.Evidence_Pool == "ALL_VERIFIED_USABLE")]
    assert not trip.Selected.any() and trip.Rejection_Reason.eq("ONLY_ONE_OR_ZERO_NEGATIVE_GROUPS").all()
    assert not fcc.Selected.any() and fcc.Rejection_Reason.eq("ONLY_ONE_OR_ZERO_POSITIVE_GROUPS").all()


def test_manifest_has_zero_group_overlap_and_both_classes():
    manifest = read(MANIFEST)
    for _, frame in manifest.groupby(["Design_ID", "Fold"]):
        train, test = frame[frame.Assignment == "TRAIN"], frame[frame.Assignment == "TEST"]
        assert not set(train.Group_ID) & set(test.Group_ID)
        assert set(train.Target_Value.astype(int)) == set(test.Target_Value.astype(int)) == {0, 1}
        assert train.M2_Complete.all() and test.M2_Complete.all()


def test_exact_predeclared_models_and_internal_pipelines():
    dummy, logistic, forest, svm = [pilot.model_factory(m) for m in pilot.MODEL_IDS]
    assert isinstance(dummy, Pipeline) and isinstance(dummy[-1], DummyClassifier) and dummy[-1].strategy == "most_frequent"
    assert isinstance(logistic[0], StandardScaler) and isinstance(logistic[-1], LogisticRegression)
    assert logistic[-1].class_weight == "balanced" and logistic[-1].C == 1 and logistic[-1].max_iter >= 5000
    assert isinstance(forest[-1], RandomForestClassifier) and forest[-1].n_estimators == 500
    assert forest[-1].class_weight == "balanced_subsample" and forest[-1].random_state == pilot.RANDOM_STATE
    assert isinstance(svm[0], StandardScaler) and isinstance(svm[-1], SVC)
    assert svm[-1].kernel == "rbf" and svm[-1].C == 1 and svm[-1].class_weight == "balanced"


def test_model_table_has_dummy_all_models_and_no_forbidden_operations():
    metrics = read(TABLE_DIR / "pilot_v1_model_metrics.csv")
    folds = metrics[metrics.Record_Type == "FOLD"]
    assert set(folds.Model_ID) == set(pilot.MODEL_IDS)
    for _, frame in folds.groupby(["Target", "Evidence_Pool", "Fold"]):
        assert set(frame.Model_ID) == set(pilot.MODEL_IDS)
    assert metrics.Preprocessing_Fit_Within_Fold.all()
    assert not metrics.Imputation_Applied.any() and not metrics.Resampling_Applied.any() and not metrics.Hyperparameter_Search.any()


def test_confusions_balanced_accuracy_and_mcc_are_reproducible():
    predictions, metrics, confusions = read(TABLE_DIR / "pilot_v1_predictions.csv"), read(TABLE_DIR / "pilot_v1_model_metrics.csv"), read(TABLE_DIR / "pilot_v1_confusion_matrices.csv")
    for key, frame in predictions.groupby(["Target", "Evidence_Pool", "Design_ID", "Fold", "Model_ID"]):
        tn, fp, fn, tp = confusion_matrix(frame.True_Label, frame.Predicted_Label, labels=[0, 1]).ravel()
        mask = ((metrics.Record_Type == "FOLD") & (metrics.Target == key[0]) & (metrics.Evidence_Pool == key[1]) & (metrics.Design_ID == key[2]) & (metrics.Fold == key[3]) & (metrics.Model_ID == key[4]))
        stored = metrics[mask].iloc[0]
        cmask = ((confusions.Scope == "FOLD") & (confusions.Target == key[0]) & (confusions.Evidence_Pool == key[1]) & (confusions.Design_ID == key[2]) & (confusions.Fold == key[3]) & (confusions.Model_ID == key[4]))
        c = confusions[cmask].iloc[0]
        assert [c.TN, c.FP, c.FN, c.TP] == [tn, fp, fn, tp]
        assert np.isclose(stored.Balanced_Accuracy, balanced_accuracy_score(frame.True_Label, frame.Predicted_Label))
        assert np.isclose(stored.MCC, matthews_corrcoef(frame.True_Label, frame.Predicted_Label))


def test_positive_class_collapse_flag_and_counts():
    folds = read(TABLE_DIR / "pilot_v1_model_metrics.csv").query("Record_Type == 'FOLD'")
    expected = folds.Predicted_Positive_Fraction.eq(1)
    assert folds.Positive_Class_Collapse.astype(bool).equals(expected)
    assert folds.loc[expected, "Failure_Flag"].eq("POSITIVE_CLASS_COLLAPSE").all()
    assert folds.loc[expected, "Predicted_Negative_Count"].eq(0).all()
    primary_dummy = folds[(folds.Model_ID == pilot.MODEL_IDS[0]) & (folds.Evidence_Pool == "ALL_VERIFIED_USABLE")]
    assert primary_dummy.Positive_Class_Collapse.all()


def test_negative_group_audit_and_evidence_sensitivity():
    audit = read(TABLE_DIR / "pilot_v1_negative_class_audit.csv").set_index("Target")
    assert audit.loc["T1_TRIP", "M2_Negative_Strict_Group_n"] == 1
    assert audit.loc["T1_TRIP", "Validation_Status"] == "PILOT_NOT_VALIDATABLE_UNDER_CURRENT_M2"
    assert audit.loc["T2_ANY_TWIP", "M2_Negative_n"] == 5
    assert audit.loc["T2_ANY_TWIP", "M2_Negative_Strict_Group_n"] == 3
    sensitivity = read(TABLE_DIR / "pilot_v1_evidence_sensitivity.csv")
    direct = sensitivity[(sensitivity.Target == "T2_ANY_TWIP") & (sensitivity.Evidence_Pool == "STRICT_DIRECT_EVIDENCE_ONLY")].iloc[0]
    assert (direct.M2_n, direct.Positive_n, direct.Negative_n) == (17, 12, 5)
    assert direct.Validation_Status == "VALID"


def test_required_outputs_exist():
    paths = [QC, EXP, COMP, SCHEMA, CANDIDATES, MANIFEST,
             MODEL_DIR / "TRIP_M2_complete_cases.csv", MODEL_DIR / "TWIP_ANY_M2_complete_cases.csv",
             MODEL_DIR / "TWIP_FCC_STRICT_M2_complete_cases.csv", MODEL_DIR / "M2_exclusion_ledger.csv",
             MODEL_DIR / "M2_predictor_manifest.csv", TABLE_DIR / "pilot_v1_model_metrics.csv",
             TABLE_DIR / "pilot_v1_predictions.csv", TABLE_DIR / "pilot_v1_confusion_matrices.csv",
             TABLE_DIR / "pilot_v1_target_semantics_audit.csv", TABLE_DIR / "pilot_v1_negative_class_audit.csv",
             TABLE_DIR / "pilot_v1_evidence_sensitivity.csv", ROOT / "reports/GLOBAL_DATASET_QC_V17_REFRESH.md",
             ROOT / "reports/FEATURE_SCHEMA_V2_AUDIT.md", ROOT / "reports/VALIDATION_ARCHITECTURE_V2.md",
             ROOT / "reports/SPLIT_DESIGN_V2_AUDIT.md", ROOT / "reports/PILOT_ML_V1_REPORT.md"]
    assert all(path.exists() and path.stat().st_size for path in paths)


def test_outputs_are_deterministic_and_source_remains_immutable():
    outputs = [TABLE_DIR / "pilot_v1_model_metrics.csv", TABLE_DIR / "pilot_v1_predictions.csv",
               TABLE_DIR / "pilot_v1_confusion_matrices.csv", CANDIDATES, MANIFEST]
    before, source_before = {path: digest(path) for path in outputs}, digest(SOURCE)
    pilot.main()
    assert {path: digest(path) for path in outputs} == before
    assert digest(SOURCE) == source_before == pilot.SOURCE_EXPECTED_SHA256
