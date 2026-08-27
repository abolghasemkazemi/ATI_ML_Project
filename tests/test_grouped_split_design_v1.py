from __future__ import annotations

import ast
from collections import Counter
from hashlib import sha256
from pathlib import Path
import subprocess
import sys

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/grouped_split_design_v1.py"
MASTER = ROOT / "data/processed/master_19papers_recovery_v12_qc.csv"
EXP_INDEX = ROOT / "data/processed/experimental_condition_index_v12.csv"
COMP_INDEX = ROOT / "data/processed/computational_condition_index_v12.csv"
FEATURE_SCHEMA = ROOT / "data/schema/feature_schema_v1.csv"
FEATURE_SETS = ROOT / "data/schema/feature_sets_v1.csv"
FEATURE_PRIORITY = ROOT / "data/schema/feature_priority_v1.csv"
DOMAIN_MANIFEST = ROOT / "data/schema/domain_manifest_v1.csv"
FEATURE_COVERAGE = ROOT / "reports/FEATURE_SET_COVERAGE_V1.csv"
TARGET_FEATURE = ROOT / "reports/TARGET_FEATURE_AVAILABILITY_V1.csv"
LEAKAGE_POLICY = ROOT / "reports/PREDICTION_TIME_LEAKAGE_POLICY_V1.md"
FEATURE_AUDIT = ROOT / "reports/FEATURE_SCHEMA_V1_AUDIT.md"
GLOBAL_AUDIT = ROOT / "reports/GLOBAL_DATASET_QC_V12.md"

GROUP_DISTRIBUTION = ROOT / "reports/GROUP_TARGET_DISTRIBUTION_V1.csv"
CLASS_SUPPORT = ROOT / "reports/CLASS_SUPPORT_BY_GROUP_V1.csv"
GROUP_KEYS = ROOT / "reports/CONDITION_GROUPING_KEY_AUDIT_V1.csv"
M2_SUPPORT = ROOT / "reports/M2_COMPLETE_CASE_SUPPORT_V1.csv"
NEGATIVE_AUDIT = ROOT / "reports/NEGATIVE_CLASS_AUDIT_V1.csv"
POSITIVE_AUDIT = ROOT / "reports/POSITIVE_CLASS_FAMILY_AUDIT_V1.csv"
GENERALIZATION = ROOT / "reports/GENERALIZATION_FEASIBILITY_V1.csv"
CHEMISTRY_POLICY = ROOT / "reports/CHEMISTRY_SOURCE_POLICY_V1.md"
ARCHITECTURE = ROOT / "reports/VALIDATION_ARCHITECTURE_V1.md"
SPLIT_AUDIT = ROOT / "reports/SPLIT_DESIGN_V1_AUDIT.md"
CANDIDATES = ROOT / "data/splits/split_candidates_v1.csv"
MANIFEST = ROOT / "data/splits/split_manifest_v1.csv"
PROJECT_GUIDE = ROOT / "PROJECT_GUIDE.md"

INPUTS = (
    EXP_INDEX,
    MASTER,
    FEATURE_SCHEMA,
    FEATURE_SETS,
    FEATURE_PRIORITY,
    DOMAIN_MANIFEST,
    FEATURE_COVERAGE,
    TARGET_FEATURE,
    LEAKAGE_POLICY,
    FEATURE_AUDIT,
    GLOBAL_AUDIT,
)

OUTPUTS = (
    GROUP_DISTRIBUTION,
    CLASS_SUPPORT,
    GROUP_KEYS,
    M2_SUPPORT,
    NEGATIVE_AUDIT,
    POSITIVE_AUDIT,
    GENERALIZATION,
    CHEMISTRY_POLICY,
    ARCHITECTURE,
    SPLIT_AUDIT,
    CANDIDATES,
    MANIFEST,
)

FEATURE_SET_ORDER = [
    "M1_CHEMISTRY",
    "M2_CHEMISTRY_PLUS_TEST",
    "M3_PLUS_PROCESSING",
    "M4_PLUS_PHYSICS",
    "M5_PLUS_INITIAL_MICROSTRUCTURE",
]

FROZEN_DATASET_SHA256 = {
    EXP_INDEX: "2b4f9a3d1cc4e662c285b1621720d8a83819def9d74d58f76be1d1895c732467",
    MASTER: "4dec9a87c0c3f0f38a4ff676681ae0bacf09d247e7136770baf2d1eb27928406",
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def regenerate_and_prove_determinism():
    before = {path: file_hash(path) for path in INPUTS}
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
    assert {path: file_hash(path) for path in INPUTS} == before
    first_outputs = {path: file_hash(path) for path in OUTPUTS}
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
    assert {path: file_hash(path) for path in INPUTS} == before
    assert {path: file_hash(path) for path in OUTPUTS} == first_outputs


def primary_conditions() -> pd.DataFrame:
    master = load(MASTER)
    return master.loc[master.QC_Row_Role.eq("EXPERIMENTAL_PRIMARY_CONDITION")].copy()


def test_all_required_outputs_and_schemas_exist():
    for path in OUTPUTS:
        assert path.exists() and path.stat().st_size > 0, path

    group_required = {
        "Grouping_Level", "Group_ID", "Number_of_Conditions", "TRIP_Usable",
        "TRIP_Positive", "TRIP_Negative", "TWIP_Usable", "TWIP_Positive",
        "TWIP_Negative", "Joint_Usable", "Joint_00", "Joint_10", "Joint_01",
        "Joint_11", "Papers", "Material_Parents", "Notes",
    }
    assert group_required <= set(load(GROUP_DISTRIBUTION).columns)

    candidate_required = {
        "Target", "Split_ID", "Split_Strategy", "Grouping_Level",
        "Train_Condition_Count", "Validation_Condition_Count", "Train_Group_Count",
        "Validation_Group_Count", "Train_Positive", "Train_Negative",
        "Validation_Positive", "Validation_Negative", "Both_Classes_Train",
        "Both_Classes_Validation", "Group_Overlap", "Paper_Overlap", "Study_Overlap",
        "Material_Overlap", "Source_Alloy_Family_Overlap", "Strict_Leakage_Overlap", "Feature_Set",
        "Feature_Complete_Train", "Feature_Complete_Validation",
        "Scientific_Validity", "Statistical_Limitation", "Recommended_Status", "Notes",
        "Train_00", "Train_10", "Train_01", "Train_11",
        "Validation_00", "Validation_10", "Validation_01", "Validation_11",
    }
    assert candidate_required <= set(load(CANDIDATES).columns)
    assert set(load(MANIFEST).columns) == {
        "Target", "Split_ID", "ML_Condition_ID", "Assignment", "Group_ID",
        "Paper_ID", "Material_Parent_ID", "Target_Value", "Feature_Set",
    }


def test_source_datasets_are_byte_preserved_and_domain_counts_stay_frozen():
    # The session fixture separately proves the generator leaves every declared
    # input byte-identical. These frozen hashes guard the two scientific roster
    # inputs against changes outside the generator as well.
    assert {path: file_hash(path) for path in FROZEN_DATASET_SHA256} == FROZEN_DATASET_SHA256
    assert len(load(MASTER)) == 192
    assert len(load(EXP_INDEX)) == 51
    comp = load(COMP_INDEX)
    assert len(comp) == 12 and set(comp.Paper_ID) == {"P017"}


def test_atomic_roster_excludes_p017_stages_legacy_replacements_and_summaries():
    index, primary, master = load(EXP_INDEX), primary_conditions(), load(MASTER)
    assert len(index) == len(primary) == 51
    assert index.ML_Condition_ID.is_unique and primary.ML_Condition_ID.is_unique
    assert set(index.ML_Condition_ID) == set(primary.ML_Condition_ID)
    assert not set(index.Paper_ID) & {"P017", "P018", "P019"}
    assert primary.QC_Duplicate_Status.eq("NO_DOUBLE_COUNT").all()
    assert primary.Observation_Role.eq("INDEPENDENT_CONDITION").all()
    # Stage children intentionally inherit their parent's ML_Condition_ID, so role
    # filtering—not naïve ID disjointness—is the exclusion proof.
    assert set(master.loc[master.QC_Row_Role.eq("EXPERIMENTAL_STAGE_CHILD"), "ML_Condition_ID"].dropna()) & set(index.ML_Condition_ID)
    assert len(primary) < len(master.loc[master.QC_Row_Role.str.startswith("EXPERIMENTAL")])
    assert not set(load(MANIFEST).ML_Condition_ID) - set(index.ML_Condition_ID)


def test_target_counts_labels_and_joint_states_are_unchanged():
    index = load(EXP_INDEX)
    assert index.Effective_TRIP.notna().sum() == 32
    assert index.Effective_TRIP.value_counts().to_dict() == {1.0: 27, 0.0: 5}
    assert index.Effective_TWIP.notna().sum() == 30
    assert index.Effective_TWIP.value_counts().to_dict() == {1.0: 24, 0.0: 6}
    joint = index.dropna(subset=["Effective_TRIP", "Effective_TWIP"])
    states = joint.Effective_TRIP.astype(int).astype(str) + joint.Effective_TWIP.astype(int).astype(str)
    assert Counter(states) == Counter({"11": 17, "10": 5, "01": 4, "00": 1})
    assert len(joint) == 27


def test_grouping_hierarchy_is_complete_without_inventing_batches():
    keys = load(GROUP_KEYS)
    index = load(EXP_INDEX)
    assert len(keys) == 51 and keys.ML_Condition_ID.is_unique
    assert index.Physical_Batch_ID.isna().all()
    assert keys.Effective_Batch_Group.str.startswith("MATERIAL_FALLBACK::").all()
    assert keys.Safest_Group_ID.notna().all()
    assert keys.Alloy_Family_ID.notna().all()
    assert keys.Safest_Grouping_Level.eq("Leakage_Group_Strict_WITH_PAPER_FALLBACK").all()
    assert keys.Strict_Group_Source.value_counts().to_dict() == {
        "Leakage_Group_Strict": 32,
        "Paper_ID_FALLBACK": 19,
    }
    fallback = keys.Strict_Group_Source.eq("Paper_ID_FALLBACK")
    assert (keys.loc[fallback, "Safest_Group_ID"] == "PAPER_FALLBACK::" + keys.loc[fallback, "Paper_ID"]).all()
    exact_family = keys.Alloy_Family_ID.eq("SOURCE_COMPOSITION_TEXT::Fe50Mn30Co10Cr10")
    assert set(keys.loc[exact_family, "Paper_ID"]) == {"P003", "P011", "P013", "P014"}


def test_group_target_distribution_covers_all_conditions_at_every_level():
    groups = load(GROUP_DISTRIBUTION)
    expected = {
        "Paper_ID": 12,
        "Study_Series_ID": 12,
        "Material_Parent_ID": 17,
        "Physical_Batch_ID": 17,
        "Leakage_Group_Strict": 12,
        "Leakage_Group_Material": 17,
    }
    assert groups.groupby("Grouping_Level").size().to_dict() == expected
    for _, group in groups.groupby("Grouping_Level"):
        assert group.Number_of_Conditions.sum() == 51
        assert group.TRIP_Positive.sum() == 27 and group.TRIP_Negative.sum() == 5
        assert group.TWIP_Positive.sum() == 24 and group.TWIP_Negative.sum() == 6
        assert group[["Joint_00", "Joint_10", "Joint_01", "Joint_11"]].sum().tolist() == [1, 5, 4, 17]
    batch = groups.loc[groups.Grouping_Level.eq("Physical_Batch_ID")]
    assert batch.Notes.str.contains("No physical batch was inferred", case=False).all()


def test_class_support_flags_capture_full_and_m2_group_limits():
    support = load(CLASS_SUPPORT)
    strict = support.loc[support.Grouping_Level.eq("Leakage_Group_Strict")].set_index(["Target", "Population"])
    assert strict.loc[("T1_TRIP", "ALL_TARGET_USABLE"), ["Positive_Conditions", "Negative_Conditions"]].tolist() == [27, 5]
    assert strict.loc[("T2_TWIP", "ALL_TARGET_USABLE"), ["Positive_Conditions", "Negative_Conditions"]].tolist() == [24, 6]
    assert strict.loc[("T1_TRIP", "ALL_TARGET_USABLE"), "Groups_Containing_Negatives"] == 4
    assert strict.loc[("T2_TWIP", "ALL_TARGET_USABLE"), "Groups_Containing_Negatives"] == 4
    assert "LOW_GROUP_SUPPORT" in strict.loc[("T1_TRIP", "ALL_TARGET_USABLE"), "Flags"]
    assert "CLASS_GROUP_CONFOUNDING" in strict.loc[("T2_TWIP", "ALL_TARGET_USABLE"), "Flags"]
    t1_m2_flags = strict.loc[("T1_TRIP", "M2_CORE_COMPLETE"), "Flags"]
    assert "NEGATIVE_CLASS_TWO_GROUPS" in t1_m2_flags
    assert "CLASS_GROUP_CONFOUNDING" in t1_m2_flags


def test_m2_complete_cases_preserve_raw_availability_and_expose_trip_loss():
    support = load(M2_SUPPORT, dtype={"Class_Value": "string"}).set_index(["Target", "Class_Value"])
    assert support.loc[("T1_TRIP", "0"), ["Full_Usable_Conditions", "M2_Complete_Conditions"]].tolist() == [5, 2]
    assert support.loc[("T1_TRIP", "1"), "M2_Complete_Conditions"] == 17
    assert support.loc[("T1_TRIP", "0"), "M2_Complete_Paper_Count"] == 2
    assert support.loc[("T2_TWIP", "0"), ["Full_Usable_Conditions", "M2_Complete_Conditions"]].tolist() == [6, 6]
    assert support.loc[("T2_TWIP", "1"), "M2_Complete_Conditions"] == 14
    assert support.loc[("T2_TWIP", "0"), "M2_Complete_Paper_Count"] == 4
    assert support.loc[("T3_JOINT", "00"), "M2_Complete_Conditions"] == 1
    assert support.Notes.str.contains("No chemistry reconciliation", case=False).all()


def test_negative_audit_lists_exact_source_negatives_without_generating_labels():
    negative, index = load(NEGATIVE_AUDIT), load(EXP_INDEX).set_index("ML_Condition_ID")
    assert negative.Negative_Target.value_counts().to_dict() == {"TWIP": 6, "TRIP": 5}
    assert negative.Condition_Level_Negative.all()
    assert negative.Negative_Origin_Check.str.startswith("PASS_NO_LABEL_GENERATION_BY_SPLIT_TASK").all()
    assert not set(negative.Paper_ID) & {"P017", "P018", "P019"}
    for row in negative.itertuples():
        field = "Effective_TRIP" if row.Negative_Target == "TRIP" else "Effective_TWIP"
        assert index.loc[row.ML_Condition_ID, field] == 0
        assert row.TRIP_Label == index.loc[row.ML_Condition_ID, "Effective_TRIP"]
        assert row.TWIP_Label == index.loc[row.ML_Condition_ID, "Effective_TWIP"]
    p008 = negative.loc[negative.ML_Condition_ID.eq("P008_MC_N2p6_FC")].iloc[0]
    assert p008.Negative_Evidence_Strength == "LIMITED"
    assert "CONSOLIDATED_EVIDENCE_TEXT_GAP_RETAINED" in p008.Negative_Origin_Check
    strong_initial_final = set(negative.loc[negative.Initial_to_Final_Evidence.str.startswith("YES_"), "ML_Condition_ID"])
    assert {"P010_MC_AlloyII", "P015_MC_298K"} <= strong_initial_final


def test_positive_family_concentration_preserves_every_positive_once_per_level():
    audit = load(POSITIVE_AUDIT)
    for target, expected in (("T1_TRIP", 27), ("T2_TWIP", 24)):
        target_rows = audit.loc[audit.Target.eq(target)]
        assert set(target_rows.Concentration_Level) == {"PAPER", "STUDY_SERIES", "MATERIAL_PARENT", "ALLOY_FAMILY"}
        for _, level in target_rows.groupby("Concentration_Level"):
            assert level.Positive_Conditions.sum() == expected
            assert level.Total_Positive_Conditions.eq(expected).all()
            assert level.Positive_Share.sum() == pytest.approx(1.0, abs=0.001)
    assert audit.Notes.str.contains("No composition parsing", case=False).all()


def test_every_requested_binary_split_design_and_fold_count_is_audited():
    candidates = load(CANDIDATES)
    m2 = candidates.loc[candidates.Feature_Set.eq("M2_CHEMISTRY_PLUS_TEST")]
    expected = {
        "LEAVE_ONE_PAPER_OUT": 12,
        "LEAVE_ONE_STUDY_SERIES_OUT": 12,
        "LEAVE_ONE_MATERIAL_FAMILY_OUT": 17,
        "GROUP_K_FOLD_K2": 2,
        "GROUP_K_FOLD_K3": 3,
        "GROUP_K_FOLD_K4": 4,
        "GROUP_K_FOLD_K5": 5,
        "DETERMINISTIC_GROUPED_HOLDOUT": 3,
    }
    for target, usable in (("T1_TRIP", 32), ("T2_TWIP", 30)):
        target_rows = m2.loc[m2.Target.eq(target)]
        assert set(target_rows.Split_Strategy) == set(expected)
        for strategy, count in expected.items():
            block = target_rows.loc[target_rows.Split_Strategy.eq(strategy)]
            assert block.Split_ID.nunique() == count
            assert (block.Train_Condition_Count + block.Validation_Condition_Count).eq(usable).all()
            assert (block.Train_Positive + block.Train_Negative).eq(block.Train_Condition_Count).all()
            assert (block.Validation_Positive + block.Validation_Negative).eq(block.Validation_Condition_Count).all()


def test_lopo_and_one_material_designs_are_not_promoted_as_feasible():
    candidates = load(CANDIDATES)
    m2 = candidates.loc[candidates.Feature_Set.eq("M2_CHEMISTRY_PLUS_TEST")]
    for target in ("T1_TRIP", "T2_TWIP"):
        lopo = m2.loc[m2.Target.eq(target) & m2.Split_Strategy.eq("LEAVE_ONE_PAPER_OUT")]
        assert lopo.Design_Feasibility.eq("NOT_FEASIBLE").all()
        assert not lopo.Recommended_Status.isin(["VALID_STRONG", "VALID_LIMITED"]).any()
        material = m2.loc[m2.Target.eq(target) & m2.Split_Strategy.eq("LEAVE_ONE_MATERIAL_FAMILY_OUT")]
        assert material.Recommended_Status.eq("INVALID_GROUP_LEAKAGE").any()
        assert material.loc[material.Recommended_Status.eq("INVALID_GROUP_LEAKAGE"), "Strict_Leakage_Overlap"].gt(0).all()


def test_group_kfold_feasibility_is_target_and_m2_specific():
    candidates = load(CANDIDATES)
    m2 = candidates.loc[candidates.Feature_Set.eq("M2_CHEMISTRY_PLUS_TEST")]
    t1_k2 = m2.loc[m2.Target.eq("T1_TRIP") & m2.Split_Strategy.eq("GROUP_K_FOLD_K2")]
    assert t1_k2.Design_Feasibility.eq("TARGET_ROSTER_FEASIBLE; FEATURE_SET_NOT_FEASIBLE").all()
    assert t1_k2.Recommended_Status.eq("INVALID_CLASS_SUPPORT").all()
    assert (
        t1_k2.Feature_Complete_Train_Negative.eq(0)
        | t1_k2.Feature_Complete_Validation_Negative.eq(0)
    ).all()
    for k in (3, 4, 5):
        block = m2.loc[m2.Target.eq("T1_TRIP") & m2.Split_Strategy.eq(f"GROUP_K_FOLD_K{k}")]
        assert block.Design_Feasibility.eq("NOT_FEASIBLE").all()

    for k in (2, 4):
        block = m2.loc[m2.Target.eq("T2_TWIP") & m2.Split_Strategy.eq(f"GROUP_K_FOLD_K{k}")]
        assert block.Recommended_Status.eq("VALID_LIMITED").all()
        assert block.Both_Classes_Train.all() and block.Both_Classes_Validation.all()
        assert block.Feature_Complete_Train_Negative.gt(0).all()
        assert block.Feature_Complete_Validation_Negative.gt(0).all()
    for k in (3, 5):
        block = m2.loc[m2.Target.eq("T2_TWIP") & m2.Split_Strategy.eq(f"GROUP_K_FOLD_K{k}")]
        assert block.Design_Feasibility.eq("NOT_FEASIBLE").all()


def test_retained_grouped_holdouts_have_zero_leakage_and_m2_dual_class_support():
    candidates = load(CANDIDATES)
    holdouts = candidates.loc[
        candidates.Feature_Set.eq("M2_CHEMISTRY_PLUS_TEST")
        & candidates.Split_Strategy.eq("DETERMINISTIC_GROUPED_HOLDOUT")
        & candidates.Target.isin(["T1_TRIP", "T2_TWIP"])
    ]
    assert holdouts.groupby("Target").size().to_dict() == {"T1_TRIP": 3, "T2_TWIP": 3}
    assert holdouts.Recommended_Status.eq("VALID_LIMITED").all()
    assert holdouts.Both_Classes_Train.all() and holdouts.Both_Classes_Validation.all()
    assert holdouts[[
        "Group_Overlap", "Paper_Overlap", "Study_Overlap", "Material_Overlap",
        "Source_Alloy_Family_Overlap", "Strict_Leakage_Overlap",
    ]].eq(0).all().all()
    for field in (
        "Feature_Complete_Train_Positive", "Feature_Complete_Train_Negative",
        "Feature_Complete_Validation_Positive", "Feature_Complete_Validation_Negative",
    ):
        assert holdouts[field].gt(0).all()
    assert holdouts.groupby("Target").Validation_Group_IDs.nunique().eq(3).all()


def test_every_valid_manifest_partition_has_no_over_or_under_sampling():
    manifest, index = load(MANIFEST), load(EXP_INDEX).set_index("ML_Condition_ID")
    assert set(manifest.Assignment) == {"TRAIN", "VALIDATION"}
    assert "TEST" not in set(manifest.Assignment)
    assert not manifest.duplicated(["Target", "Split_ID", "Feature_Set", "ML_Condition_ID"]).any()
    for (target, _, _), block in manifest.groupby(["Target", "Split_ID", "Feature_Set"]):
        expected = 32 if target == "T1_TRIP" else 30
        field = "Effective_TRIP" if target == "T1_TRIP" else "Effective_TWIP"
        expected_ids = set(index.loc[index[field].notna()].index)
        assert len(block) == expected and block.ML_Condition_ID.is_unique
        assert set(block.ML_Condition_ID) == expected_ids
        assert set(block.loc[block.Assignment.eq("TRAIN"), "Group_ID"]).isdisjoint(
            set(block.loc[block.Assignment.eq("VALIDATION"), "Group_ID"])
        )
        assert block.Target_Value.tolist() == index.loc[block.ML_Condition_ID, field].astype(int).tolist()


def test_feature_complete_counts_are_recomputed_from_existing_raw_core_columns_only():
    candidates, manifest, primary = load(CANDIDATES), load(MANIFEST), primary_conditions().set_index("ML_Condition_ID")
    sets = load(FEATURE_SETS)
    valid_rows = candidates.loc[
        candidates.Target.isin(["T1_TRIP", "T2_TWIP"])
        & candidates.Recommended_Status.isin(["VALID_STRONG", "VALID_LIMITED"])
    ]
    for row in valid_rows.itertuples():
        assignment = manifest.loc[
            manifest.Target.eq(row.Target)
            & manifest.Split_ID.eq(row.Split_ID)
            & manifest.Feature_Set.eq(row.Feature_Set)
        ].set_index("ML_Condition_ID")
        fields = sets.loc[
            sets.Feature_Set.eq(row.Feature_Set)
            & sets.Eligibility_Status.eq("CANDIDATE_CORE_V1"),
            "Column_Name",
        ].tolist()
        aligned = primary.loc[assignment.index]
        complete = aligned[fields].notna().all(axis=1)
        values = assignment.Target_Value.astype(int)
        train = assignment.Assignment.eq("TRAIN")
        validation = assignment.Assignment.eq("VALIDATION")
        assert int((complete & train).sum()) == row.Feature_Complete_Train
        assert int((complete & validation).sum()) == row.Feature_Complete_Validation
        assert int((complete & train & values.eq(1)).sum()) == row.Feature_Complete_Train_Positive
        assert int((complete & train & values.eq(0)).sum()) == row.Feature_Complete_Train_Negative
        assert int((complete & validation & values.eq(1)).sum()) == row.Feature_Complete_Validation_Positive
        assert int((complete & validation & values.eq(0)).sum()) == row.Feature_Complete_Validation_Negative


def test_t3_four_class_is_invalid_and_multilabel_is_future_exploratory_only():
    candidates = load(CANDIDATES)
    t3a = candidates.loc[candidates.Target.eq("T3A_FOUR_CLASS")]
    assert len(t3a) == 12
    assert t3a.Recommended_Status.eq("INVALID_CLASS_SUPPORT").all()
    assert t3a.Statistical_Limitation.str.contains("T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE").all()
    assert ((t3a.Train_00 == 0) | (t3a.Validation_00 == 0)).all()
    for state, expected in (("00", 1), ("10", 5), ("01", 4), ("11", 17)):
        assert (t3a[f"Train_{state}"] + t3a[f"Validation_{state}"]).eq(expected).all()

    t3b = candidates.loc[candidates.Target.eq("T3B_MULTILABEL")]
    assert len(t3b) == 3
    assert t3b.Recommended_Status.eq("EXPLORATORY_ONLY").all()
    assert t3b.Both_Classes_Train.all() and t3b.Both_Classes_Validation.all()
    for field in (
        "Train_TRIP_Positive", "Train_TRIP_Negative", "Validation_TRIP_Positive",
        "Validation_TRIP_Negative", "Train_TWIP_Positive", "Train_TWIP_Negative",
        "Validation_TWIP_Positive", "Validation_TWIP_Negative",
    ):
        assert t3b[field].gt(0).all()
    assert not load(MANIFEST).Target.str.startswith("T3").any()


def test_random_row_split_and_three_way_split_are_explicitly_rejected():
    candidates, manifest = load(CANDIDATES), load(MANIFEST)
    assert not candidates.Split_Strategy.str.contains("RANDOM", case=False).any()
    assert set(manifest.Assignment) == {"TRAIN", "VALIDATION"}
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    for phrase in (
        "same paper", "material parent", "composition/alloy family", "processing family",
        "temperature series", "strain-rate series", "Exact stratification never overrides group independence",
        "No three-way train/validation/test partition",
    ):
        assert phrase in architecture


def test_no_model_training_resampling_transformation_or_performance_metric_exists():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = []
    called_attributes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            called_attributes.append(node.func.attr)
    assert not any(name.startswith("sklearn") for name in imported)
    assert not {"fit", "predict", "fit_transform", "resample"} & set(called_attributes)

    candidates = load(CANDIDATES)
    forbidden_metrics = {"accuracy", "auc", "roc_auc", "f1", "precision", "recall", "log_loss"}
    assert not forbidden_metrics & {column.lower() for column in candidates.columns}
    assert {path.name for path in (ROOT / "data/splits").iterdir() if path.is_file()} == {
        "split_candidates_v1.csv", "split_manifest_v1.csv"
    }
    assert not any(token in path.name.lower() for path in ROOT.rglob("*") if path.is_file() for token in ("smote_sample", "synthetic_alloy", "trained_model"))


def test_chemistry_policy_is_frozen_but_not_executed():
    policy = CHEMISTRY_POLICY.read_text(encoding="utf-8")
    for phrase in (
        "prefer that measured bulk representation", "Composition_Source", "MEASURED_BULK",
        "NOMINAL", "Local EDS", "local APT", "TEM-local chemistry",
        "do not substitute for bulk chemistry", "no unified chemistry column was created",
    ):
        assert phrase in policy
    assert "normalized" not in set(load(MASTER).columns.str.lower())
    assert not any("matrix" in path.name.lower() for path in (ROOT / "data/splits").iterdir())


def test_generalization_taxonomy_and_limitations_are_explicit():
    generalization = load(GENERALIZATION).set_index("Generalization_Level")
    assert list(generalization.index) == ["G1", "G2", "G3"]
    assert generalization.loc["G1", "T1_Feasibility"] == "EXPLORATORY_ONLY"
    assert generalization.loc["G2", "T1_Feasibility"] == "VALID_LIMITED"
    assert "LOPO_NOT_FEASIBLE" in generalization.loc["G3", "T1_Feasibility"]
    assert "LOPO_NOT_FEASIBLE" in generalization.loc["G3", "T2_Feasibility"]
    assert generalization.loc["G3", "T3_Four_Class_Feasibility"] == "T3_FOUR_CLASS_NOT_CURRENTLY_VALIDATABLE"


def test_project_guide_records_grouped_split_design_v1_without_authorizing_ml():
    guide = PROJECT_GUIDE.read_text(encoding="utf-8")
    for phrase in (
        "Grouped Split Design V1", "group independence", "T1", "T2", "T3",
        "G1", "G2", "G3", "M2", "measured bulk", "nominal",
        "no resampling", "No ML training",
    ):
        assert phrase.lower() in guide.lower()
    assert "LOG-0021" in guide and "DEC-0030" in guide
