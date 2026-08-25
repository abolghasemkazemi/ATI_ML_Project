"""Non-destructive scientific integrity checks and audit report generation."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ELEMENT_RE = re.compile(
    r"^(?:at\.?%[_ ]?)?([A-Z][a-z]?)_(?:at\.?%|atomic_percent)$", re.I
)


def composition_columns(df: pd.DataFrame) -> list[str]:
    """Find explicitly atomic-percent composition columns; never assume wt.% is at.%."""
    return [c for c in df.columns if ELEMENT_RE.match(str(c).strip())]


def composition_sum_flags(df: pd.DataFrame, tolerance: float = 1.0) -> pd.DataFrame:
    cols = composition_columns(df)
    if not cols:
        return pd.DataFrame(
            index=df.index,
            data={"Composition_Sum_at_pct": np.nan, "Composition_Sum_Flag": False},
        )
    values = df[cols].apply(pd.to_numeric, errors="coerce")
    sums = values.sum(axis=1, min_count=1)
    return pd.DataFrame(
        {
            "Composition_Sum_at_pct": sums,
            "Composition_Sum_Flag": sums.notna()
            & ~sums.between(100 - tolerance, 100 + tolerance),
        }
    )


def duplicate_condition_flags(df: pd.DataFrame) -> pd.Series:
    return df["Condition_ID"].notna() & df["Condition_ID"].duplicated(keep=False)


def paper_doi_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ids = df.get("Paper_ID", pd.Series(dtype="object"))
    for paper in sorted(ids.dropna().astype(str).unique()):
        dois = df.loc[ids.astype(str) == paper, "DOI"].dropna().astype(str).str.strip()
        unique = sorted(x for x in dois.unique() if x)
        rows.append(
            {
                "Paper_ID": paper,
                "DOI_values": " | ".join(unique),
                "DOI_count": len(unique),
                "Consistent": len(unique) <= 1,
            }
        )
    return pd.DataFrame(
        rows, columns=["Paper_ID", "DOI_values", "DOI_count", "Consistent"]
    )


def _find_columns(df: pd.DataFrame, fragments: tuple[str, ...]) -> list[str]:
    return [c for c in df if any(f in c.lower().replace(" ", "_") for f in fragments)]


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return row flags, long-form quality metrics, and Paper_ID/DOI audit."""
    required = ["Paper_ID", "DOI", "Condition_ID", "Experiment_Group_ID"]
    missing = [c for c in required if c not in df]
    if missing:
        raise ValueError(f"Dataset lacks traceability columns: {missing}")
    flags = pd.DataFrame(index=df.index)
    flags["Duplicate_Row"] = df.duplicated(keep=False)
    flags["Duplicate_Condition_ID"] = duplicate_condition_flags(df)
    flags["Duplicate_Paper_Condition"] = (
        df.duplicated(["Paper_ID", "Condition_ID"], keep=False)
        & df.Condition_ID.notna()
    )
    flags["Missing_Paper_ID"] = df.Paper_ID.isna()
    flags["Missing_DOI"] = df.DOI.isna()
    valid_paper = df.Paper_ID.astype("string").str.fullmatch(r"P(?:00[1-9]|01[0-9])")
    flags["Invalid_Paper_ID"] = ~valid_paper.fillna(False) & df.Paper_ID.notna()
    flags = pd.concat([flags, composition_sum_flags(df)], axis=1)
    impossible = pd.Series(False, index=df.index)
    for col in _find_columns(
        df, ("grain_size", "temperature", "elongation", "uts", "yield_strength", "_ys")
    ):
        impossible |= pd.to_numeric(df[col], errors="coerce").lt(0)
    for col in _find_columns(df, ("fraction",)):
        val = pd.to_numeric(df[col], errors="coerce")
        impossible |= val.notna() & ~val.between(0, 1)
    flags["Suspicious_Numerical_Value"] = impossible
    doi = paper_doi_audit(df)
    inconsistent = set(doi.loc[~doi.Consistent, "Paper_ID"])
    flags["Paper_DOI_Inconsistent"] = df.Paper_ID.isin(inconsistent)

    metrics: list[dict[str, object]] = []

    def add(section: str, metric: str, value: object, level: str = "row") -> None:
        metrics.append(
            {"Section": section, "Level": level, "Metric": metric, "Value": value}
        )

    add("dimensions", "total_rows", len(df))
    add("dimensions", "papers", df.Paper_ID.nunique())
    add("dimensions", "doi_values", df.DOI.nunique())
    add("dimensions", "unique_condition_id", df.Condition_ID.nunique())
    add("dimensions", "experiment_groups", df.Experiment_Group_ID.nunique(), "group")
    for col in df:
        add("missingness", col, round(df[col].isna().mean() * 100, 4))
    label_cols = _find_columns(df, ("trip", "twip", "slip", "mechanism"))
    for col in label_cols:
        if col.lower().endswith("class"):
            continue
        for value, count in df[col].value_counts(dropna=False).items():
            add("labels", f"{col}={value}", int(count))
        grouped_labels = (
            df.dropna(subset=["Experiment_Group_ID"])
            .groupby("Experiment_Group_ID")[col]
            .agg(lambda x: " | ".join(sorted(map(str, pd.unique(x.dropna())))) or "NA")
        )
        for value, count in grouped_labels.value_counts(dropna=False).items():
            add("labels", f"{col}={value}", int(count), "group")
    trip = next(iter(_find_columns(df, ("trip_label",))), None)
    twip = next(iter(_find_columns(df, ("twip_label",))), None)
    if trip and twip:
        for key, count in df.groupby([trip, twip], dropna=False).size().items():
            add("labels", f"TRIP/TWIP={key}", int(count))
        combinations = (
            df.dropna(subset=["Experiment_Group_ID"])
            .groupby("Experiment_Group_ID")[[trip, twip]]
            .agg(lambda x: " | ".join(sorted(map(str, pd.unique(x.dropna())))) or "NA")
        )
        for key, count in (
            combinations.groupby([trip, twip], dropna=False).size().items()
        ):
            add("labels", f"TRIP/TWIP={key}", int(count), "group")
    for col in flags.columns:
        if flags[col].dtype == bool:
            add("problems", col, int(flags[col].sum()))
    # Explicit row-role counts, preserving unknown as manual review.
    role_col = next(
        (c for c in ("Data_role", "Row_Type", "Data_Role") if c in df), None
    )
    if role_col:
        roles = df[role_col].astype("string").str.lower()
        comp = roles.str.contains("comput|model|simulation|md|dft|calphad", na=False)
        exp = roles.str.contains("experiment", na=False)
        add("row_role", "experimental_rows", int(exp.sum()))
        add("row_role", "computational_model_rows", int(comp.sum()))
        add("row_role", "unresolved_role_rows", int((~exp & ~comp).sum()))
        grouped = (
            pd.DataFrame({"group": df.Experiment_Group_ID, "exp": exp, "comp": comp})
            .dropna(subset=["group"])
            .groupby("group")
            .any()
        )
        add("row_role", "experimental_groups", int(grouped.exp.sum()), "group")
        add("row_role", "computational_model_groups", int(grouped.comp.sum()), "group")
    return flags, pd.DataFrame(metrics), doi


def write_audit(
    df: pd.DataFrame,
    flags: pd.DataFrame,
    metrics: pd.DataFrame,
    doi: pd.DataFrame,
    reports: Path,
) -> None:
    reports.mkdir(parents=True, exist_ok=True)
    tables = reports / "tables"
    tables.mkdir(exist_ok=True)
    metrics.to_csv(tables / "data_quality_report.csv", index=False)
    doi.to_csv(tables / "paper_doi_audit.csv", index=False)
    flag_counts = flags.select_dtypes("bool").sum().sort_values(ascending=False)
    missing = df.isna().mean().mul(100).sort_values(ascending=False)
    schema_path = tables / "schema_audit.csv"
    schema = (
        pd.read_csv(schema_path).to_markdown(index=False)
        if schema_path.exists()
        else "Not generated; run merge first."
    )
    text = f"""# Data audit: 19-paper pilot\n\n> Generated without changing, imputing, normalising, or deleting scientific values.\n\n## Scope\n\n- Rows: **{len(df)}**\n- Papers: **{df.Paper_ID.nunique()}**\n- DOI values: **{df.DOI.nunique()}**\n- Condition IDs: **{df.Condition_ID.nunique()}**\n- Independent experiment-group identifiers: **{df.Experiment_Group_ID.nunique()}**\n\n## Integrity flags\n\n{flag_counts.to_frame("Flagged rows").to_markdown()}\n\n## Missingness (%)\n\n{missing.to_frame("Missing percent").to_markdown()}\n\n## Schema inconsistencies\n\n{schema}\n\n## Manual review\n\nReview all schema differences, inconsistent DOI mappings, ambiguous mechanism labels, unresolved row roles, composition totals, and suspicious numerical values before modelling. Repeated rows sharing `Experiment_Group_ID` are correlated and must remain in the same validation fold. Computational/model rows must be analysed separately from independent experimental observations.\n"""
    (reports / "DATA_AUDIT.md").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=ROOT / "data/interim/master_19papers_raw.csv"
    )
    parser.add_argument("--reports", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    df = pd.read_csv(args.input, low_memory=False)
    flags, metrics, doi = validate(df)
    write_audit(df, flags, metrics, doi, args.reports)
    print(
        f"Audited {len(df)} rows; {flags.select_dtypes('bool').any(axis=1).sum()} rows carry at least one QC flag."
    )


if __name__ == "__main__":
    main()
