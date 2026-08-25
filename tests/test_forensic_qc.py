import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_forensic_qc_preserves_rows_and_uncertain_targets():
    subprocess.run([sys.executable, "scripts/run_forensic_qc.py"], cwd=ROOT, check=True)
    before = read_rows(ROOT / "data/interim/master_19papers_raw_pre_qc.csv")
    after = read_rows(ROOT / "data/interim/master_19papers_post_safe_qc.csv")
    review = read_rows(ROOT / "reports/tables/mechanism_review.csv")

    assert len(before) == len(after) == 98
    assert len(review) == 62
    assert [(r["Paper_ID"], r["Condition_ID"], r["TRIP"], r["TWIP"]) for r in before] == [
        (r["Paper_ID"], r["Condition_ID"], r["TRIP"], r["TWIP"]) for r in after
    ]
    assert all(r["Can_Auto_Fix"] == "False" for r in review)


def test_review_tables_have_required_coverage():
    roles = read_rows(ROOT / "reports/tables/row_role_review.csv")
    groups = read_rows(ROOT / "reports/tables/experiment_group_review.csv")
    schema = read_rows(ROOT / "reports/tables/schema_forensic_review.csv")
    corrections = read_rows(ROOT / "reports/tables/qc_correction_log.csv")

    assert len(roles) == 98
    assert len(groups) == len({r["Experiment_Group_ID"] for r in roles})
    assert {r["Mapping_Status"] for r in schema} <= {
        "EXACT", "SAFE_ALIAS", "POSSIBLE_ALIAS", "NEW_SCIENTIFIC_FEATURE",
        "DUPLICATE_INFORMATION", "AMBIGUOUS", "UNMAPPED",
    }
    assert corrections and {r["Correction_Type"] for r in corrections} == {"EXACT_SCHEMA_ALIAS"}
