import csv
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from scripts.prepare_pdf_recovery import validate_verified_recovery


ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_recovery_workflow_is_complete_and_non_destructive():
    before = pd.read_csv(ROOT / "data/interim/master_19papers_hierarchical_ids.csv")
    subprocess.run([sys.executable, "scripts/prepare_pdf_recovery.py"], cwd=ROOT, check=True)
    after = pd.read_csv(ROOT / "data/interim/master_19papers_hierarchical_ids.csv")
    pd.testing.assert_frame_equal(before, after)
    source = pd.read_csv(ROOT / "data/interim/master_19papers_post_safe_qc.csv")
    assert len(after) == len(source) == 98
    pd.testing.assert_frame_equal(after[source.columns], source, check_dtype=False)
    manifest = rows(ROOT / "data/raw/papers/paper_manifest.csv")
    assert [r["Paper_ID"] for r in manifest] == [f"P{i:03d}" for i in range(1, 20)]
    assert len({r["Paper_ID"] for r in manifest}) == 19
    recovery = rows(ROOT / "data/interim/scientific_data_recovery.csv")
    assert recovery and all(not r["Recovered_Value"] for r in recovery)
    assert all(r["Reviewer_Status"] == "PENDING_SOURCE_REVIEW" for r in recovery)
    assert {r["Observation_ID"] for r in recovery} == set(after.Observation_ID)
    assert {r["Feature_Name"] for r in recovery} >= {"grain size", "SFE", "TRIP evidence", "replicate identity"}


def test_verified_recovery_requires_evidence_and_cannot_be_silent():
    incomplete = {"Recovered_Value": "1", "Reviewer_Status": "VERIFIED", "Evidence_Type": "", "Evidence_Location": "p. 1", "Extraction_Method": "manual", "Confidence": "HIGH"}
    with pytest.raises(ValueError, match="VERIFIED requires"):
        validate_verified_recovery([incomplete])
    complete = dict(incomplete, Evidence_Type="table")
    validate_verified_recovery([complete])


def test_review_queues_cover_required_scopes_and_pdf_is_ignored():
    target = rows(ROOT / "reports/tables/target_evidence_review.csv")
    grouping = rows(ROOT / "reports/tables/grouping_pdf_review.csv")
    queue = rows(ROOT / "reports/tables/paper_review_queue.csv")
    assert {r["Paper_ID"] for r in target} == ({f"P{i:03d}" for i in range(1, 9)} | {f"P{i:03d}" for i in range(10, 19)})
    assert {r["Paper_ID"] for r in grouping} == {"P006", "P007", "P016"}
    assert len(queue) == 19 and sorted(int(r["Priority_Rank"]) for r in queue) == list(range(1, 20))
    check = subprocess.run(["git", "check-ignore", "data/raw/papers/test.pdf"], cwd=ROOT, capture_output=True, text=True)
    assert check.returncode == 0
