"""Merge the four immutable literature-extraction workbooks.

The first workbook defines the canonical schema.  Later columns are matched only
by an exact, whitespace-normalised name.  Unmatched values are serialised in
``Unmapped_Fields`` and reported rather than discarded or guessed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
FILES = [
    "TRIP_TWIP_First5_FULL_EXTRACTION.xlsx",
    "TRIP_TWIP_P006_P010_FULL_EXTRACTION.xlsx",
    "TRIP_TWIP_P011_P015_FULL_EXTRACTION.xlsx",
    "TRIP_TWIP_P016_P019_FULL_EXTRACTION.xlsx",
]
IDENTIFIERS = {
    "paper_id",
    "doi",
    "condition_id",
    "experiment_group_id",
    "row_type",
    "data_role",
}


def clean_column(value: object) -> str:
    """Normalise harmless Excel whitespace without changing scientific meaning."""
    return " ".join(str(value).strip().split())


def choose_extraction_sheet(path: Path) -> str:
    """Choose the sheet containing the most expected identifiers, then most rows."""
    book = pd.ExcelFile(path)
    scores: list[tuple[int, int, str]] = []
    for sheet in book.sheet_names:
        preview = pd.read_excel(path, sheet_name=sheet, nrows=5)
        cols = {clean_column(c).lower() for c in preview.columns}
        scores.append((len(cols & IDENTIFIERS), len(preview), sheet))
    score, _, selected = max(scores)
    if score == 0:
        raise ValueError(f"No scientific extraction sheet identifiable in {path.name}")
    return selected


def load_batch(path: Path, sheet: str | None = None) -> tuple[pd.DataFrame, str]:
    """Load one batch without replacing or coercing missing values."""
    selected = sheet or choose_extraction_sheet(path)
    frame = pd.read_excel(path, sheet_name=selected)
    frame.columns = [clean_column(c) for c in frame.columns]
    if len(frame.columns) != len(set(frame.columns)):
        raise ValueError(
            f"Duplicate column names after whitespace cleanup in {path.name}"
        )
    return frame, selected


def merge_batches(paths: Iterable[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return canonical merged rows and a schema-difference audit."""
    paths = list(paths)
    if not paths:
        raise ValueError("At least one workbook is required")
    first, first_sheet = load_batch(paths[0])
    canonical = list(first.columns)
    required = {"Paper_ID", "DOI", "Condition_ID", "Experiment_Group_ID"}
    missing_required = required - set(canonical)
    if missing_required:
        raise ValueError(
            f"Canonical schema lacks required columns: {sorted(missing_required)}"
        )
    frames: list[pd.DataFrame] = []
    audit: list[dict[str, object]] = []
    for i, path in enumerate(paths):
        frame, sheet = (first.copy(), first_sheet) if i == 0 else load_batch(path)
        missing = [c for c in canonical if c not in frame.columns]
        extra = [c for c in frame.columns if c not in canonical]
        out = frame.reindex(columns=canonical).copy()
        if extra:
            out["Unmapped_Fields"] = frame[extra].apply(
                lambda row: json.dumps(
                    {k: v for k, v in row.items() if pd.notna(v)}, default=str
                ),
                axis=1,
            )
        else:
            out["Unmapped_Fields"] = pd.NA
        out["Source_File"] = path.name
        out["Source_Sheet"] = sheet
        frames.append(out)
        audit.append(
            {
                "Source_File": path.name,
                "Source_Sheet": sheet,
                "Missing_Canonical_Columns": " | ".join(missing),
                "Extra_Unmapped_Columns": " | ".join(extra),
                "Requires_Manual_Review": bool(missing or extra),
            }
        )
    return pd.concat(frames, ignore_index=True), pd.DataFrame(audit)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "interim")
    parser.add_argument("--reports-dir", type=Path, default=ROOT / "reports" / "tables")
    args = parser.parse_args()
    paths = [args.raw_dir / name for name in FILES]
    absent = [str(p) for p in paths if not p.exists()]
    if absent:
        raise FileNotFoundError(
            "Place all four raw workbooks in data/raw. Missing: " + ", ".join(absent)
        )
    merged, schema = merge_batches(paths)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    merged.to_excel(args.output_dir / "master_19papers_raw.xlsx", index=False)
    merged.to_csv(args.output_dir / "master_19papers_raw.csv", index=False)
    schema.to_csv(args.reports_dir / "schema_audit.csv", index=False)
    print(
        f"Merged {len(merged)} rows; {schema.Requires_Manual_Review.sum()} batch(es) require schema review."
    )


if __name__ == "__main__":
    main()
