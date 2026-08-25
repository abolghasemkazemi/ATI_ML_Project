"""Add transparent composition-derived features without filling missing science."""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from src.data.validate_dataset import composition_columns, ELEMENT_RE

ROOT = Path(__file__).resolve().parents[2]
R_GAS = 8.31446261815324


def derive_features(
    df: pd.DataFrame, properties: pd.DataFrame, enthalpies: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Calculate features only where every required composition/property is known.

    Formulae (only for at.% totals within 100 +/- 1, without normalisation):
    weighted mean ``sum(x_i p_i)``; delta/EN mismatch
    ``sqrt(sum(x_i(1-p_i/p_bar)^2))``; ``S_mix=-R sum(x_i ln x_i)``;
    ``H_mix=4 sum(i<j, H_ij x_i x_j)``; and ``Omega=T_m S_mix/abs(H_mix)``
    (H converted from kJ/mol to J/mol). No SFE is estimated.
    """
    out = df.copy()
    props = properties.set_index("Element") if not properties.empty else pd.DataFrame()
    cols = composition_columns(df)
    elements = {c: ELEMENT_RE.match(c).group(1).title() for c in cols}

    def row_values(row):
        raw = {
            e: pd.to_numeric(pd.Series([row[c]]), errors="coerce").iloc[0]
            for c, e in elements.items()
        }
        raw = {e: v for e, v in raw.items() if pd.notna(v) and v > 0}
        total = sum(raw.values())
        # Do not renormalise incomplete or suspicious literature compositions.
        # A one-at.% tolerance mirrors QC; anything else propagates missing.
        return (
            {e: v / 100.0 for e, v in raw.items()} if abs(total - 100.0) <= 1.0 else {}
        )

    fractions = df.apply(row_values, axis=1)

    def weighted(xs, prop):
        if (
            not xs
            or prop not in props
            or any(e not in props.index or pd.isna(props.at[e, prop]) for e in xs)
        ):
            return np.nan
        return sum(x * float(props.at[e, prop]) for e, x in xs.items())

    out["VEC_derived"] = fractions.map(lambda x: weighted(x, "VEC"))
    out["Melting_temperature_weighted_K"] = fractions.map(
        lambda x: weighted(x, "Melting_temperature_K")
    )

    def mismatch(xs, prop, ratio=True):
        mean = weighted(xs, prop)
        if pd.isna(mean):
            return np.nan
        return (
            100
            * np.sqrt(
                sum(
                    x * (1 - float(props.at[e, prop]) / mean) ** 2
                    for e, x in xs.items()
                )
            )
            if ratio
            else np.sqrt(
                sum(x * (float(props.at[e, prop]) - mean) ** 2 for e, x in xs.items())
            )
        )

    out["Atomic_size_mismatch_delta_pct"] = fractions.map(
        lambda x: mismatch(x, "Atomic_radius_pm")
    )
    out["Electronegativity_mismatch"] = fractions.map(
        lambda x: mismatch(x, "Electronegativity_Pauling", False)
    )
    out["Configurational_entropy_J_molK"] = fractions.map(
        lambda x: -R_GAS * sum(v * np.log(v) for v in x.values()) if x else np.nan
    )
    lookup = {}
    if enthalpies is not None and not enthalpies.empty:
        lookup = {
            tuple(
                sorted((str(r.Element_A), str(r.Element_B)))
            ): r.Mixing_enthalpy_kJ_mol
            for _, r in enthalpies.iterrows()
            if pd.notna(r.Mixing_enthalpy_kJ_mol)
        }

    def hmix(xs):
        pairs = [(a, b) for i, a in enumerate(xs) for b in list(xs)[i + 1 :]]
        if not pairs or any(tuple(sorted(p)) not in lookup for p in pairs):
            return np.nan
        return 4 * sum(
            float(lookup[tuple(sorted((a, b)))]) * xs[a] * xs[b] for a, b in pairs
        )

    out["Mixing_enthalpy_kJ_mol"] = fractions.map(hmix)
    denom = out["Mixing_enthalpy_kJ_mol"].abs() * 1000
    out["Omega"] = (
        out["Melting_temperature_weighted_K"]
        * out["Configurational_entropy_J_molK"]
        / denom
    ).where(denom > 0)
    rate_col = next(
        (c for c in df if "strain" in c.lower() and "rate" in c.lower()), None
    )
    rate = (
        pd.to_numeric(df[rate_col], errors="coerce")
        if rate_col
        else pd.Series(np.nan, index=df.index)
    )
    out["log10_strain_rate"] = np.where(rate > 0, np.log10(rate), np.nan)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--input", type=Path, default=ROOT / "data/interim/master_19papers_raw.xlsx"
    )
    p.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/processed/master_19papers_features.xlsx",
    )
    a = p.parse_args()
    df = pd.read_excel(a.input)
    props = pd.read_csv(ROOT / "data/external/element_properties.csv")
    h = pd.read_csv(ROOT / "data/external/binary_mixing_enthalpies.csv")
    result = derive_features(df, props, h)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_excel(a.output, index=False)
    print(f"Wrote {len(result)} traceable rows to {a.output}")


if __name__ == "__main__":
    main()
