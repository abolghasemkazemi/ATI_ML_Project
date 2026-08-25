"""Generate non-modelling pilot audit figures from the processed dataset."""

from pathlib import Path
import argparse
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def make_figures(df: pd.DataFrame, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for col, name in [
        ("Paper_ID", "rows_by_paper"),
        ("TRIP", "trip_distribution"),
        ("TWIP", "twip_distribution"),
    ]:
        if col in df:
            ax = df[col].fillna("NA").astype(str).value_counts().plot.bar(title=col)
            ax.set_ylabel("Rows")
            plt.tight_layout()
            plt.savefig(output / f"{name}.png", dpi=150)
            plt.close()
    missing = df.isna().mean().sort_values(ascending=False).head(30)
    ax = missing.plot.bar(title="Top feature missingness")
    ax.set_ylabel("Fraction missing")
    plt.tight_layout()
    plt.savefig(output / "missingness.png", dpi=150)
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data/processed/master_19papers_features.xlsx",
    )
    p.add_argument("--output", type=Path, default=ROOT / "reports/figures")
    a = p.parse_args()
    make_figures(pd.read_excel(a.input), a.output)


if __name__ == "__main__":
    main()
