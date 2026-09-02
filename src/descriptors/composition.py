"""Composition conversion and descriptors with explicit property provenance.

Formulas for atomic fractions x_i: VEC=sum(x_i*VEC_i);
S_config=-R*sum(x_i*ln(x_i)); delta=100*sqrt(sum(x_i*(1-r_i/rbar)^2));
Delta_chi=sqrt(sum(x_i*(chi_i-chibar)^2)). Required properties are respectively
valence electron count, atomic radius, and electronegativity. Entropy is J/mol/K,
delta is percent, VEC/electronegativity difference are dimensionless.
"""

from dataclasses import dataclass
from math import log, sqrt
from typing import Mapping, Optional

from src.inputs import Composition

R = 8.31446261815324  # exact SI definition-derived molar gas constant


@dataclass(frozen=True)
class ElementPropertyTable:
    values: Mapping[str, Mapping[str, float]]
    source: str
    version: str


def normalize_composition(composition: Composition, properties: Optional[ElementPropertyTable] = None) -> dict:
    original = {"elements": list(composition.elements), "fractions": list(composition.fractions),
                "basis": composition.basis, "source": composition.source}
    if composition.basis == "at.%":
        atomic = {e: v / 100.0 for e, v in composition.reported().items()}
        return {"original_composition": original, "atomic_fractions": atomic,
                "status": "AVAILABLE", "conversion_provenance": "at.% divided by 100; no basis conversion"}
    if properties is None:
        return {"original_composition": original, "atomic_fractions": None, "status": "UNRESOLVED",
                "reason": "wt.% conversion requires a validated atomic_weight property table",
                "conversion_provenance": None}
    missing = [e for e in composition.elements if "atomic_weight" not in properties.values.get(e, {})]
    if missing:
        return {"original_composition": original, "atomic_fractions": None, "status": "UNRESOLVED",
                "reason": f"missing atomic_weight for: {', '.join(missing)}", "conversion_provenance": None}
    moles = {e: v / properties.values[e]["atomic_weight"] for e, v in composition.reported().items()}
    total = sum(moles.values())
    return {"original_composition": original, "atomic_fractions": {e: n / total for e, n in moles.items()},
            "status": "AVAILABLE", "conversion_provenance": {"formula": "x_i=(w_i/M_i)/sum(w_j/M_j)",
            "property_source": properties.source, "property_version": properties.version}}


def calculate_descriptors(atomic_fractions: Optional[Mapping[str, float]], properties: Optional[ElementPropertyTable]) -> dict:
    metadata = {
        "number_of_elements": ("N", "none", "composition"),
        "vec": ("sum(x_i VEC_i)", "dimensionless", "vec"),
        "ideal_mixing_entropy": ("-R sum(x_i ln x_i)", "J mol^-1 K^-1", None),
        "atomic_size_mismatch": ("100 sqrt(sum(x_i(1-r_i/rbar)^2))", "%", "atomic_radius"),
        "electronegativity_difference": ("sqrt(sum(x_i(chi_i-chibar)^2))", "dimensionless", "electronegativity"),
    }
    if atomic_fractions is None:
        return {k: {"status": "UNRESOLVED", "value": None, "formula": f, "unit": u,
                    "required_property": p, "reason": "atomic fractions unavailable"} for k, (f, u, p) in metadata.items()}
    out = {}
    for name, (formula, unit, prop) in metadata.items():
        record = {"status": "AVAILABLE", "value": None, "formula": formula, "unit": unit,
                  "required_property": prop, "provenance": "input composition" if prop is None else None}
        if name == "number_of_elements": record["value"] = len(atomic_fractions)
        elif name == "ideal_mixing_entropy": record["value"] = -R * sum(x * log(x) for x in atomic_fractions.values())
        else:
            missing = list(atomic_fractions) if properties is None else [e for e in atomic_fractions if prop not in properties.values.get(e, {})]
            if missing:
                record.update(status="UNRESOLVED", reason=f"missing {prop} for: {', '.join(missing)}")
            else:
                vals = {e: properties.values[e][prop] for e in atomic_fractions}
                if name == "vec": record["value"] = sum(atomic_fractions[e] * vals[e] for e in vals)
                else:
                    mean = sum(atomic_fractions[e] * vals[e] for e in vals)
                    record["value"] = (100 if name == "atomic_size_mismatch" else 1) * sqrt(sum(atomic_fractions[e] * ((1 - vals[e] / mean) if name == "atomic_size_mismatch" else (vals[e] - mean)) ** 2 for e in vals))
                record["provenance"] = {"property_source": properties.source, "property_version": properties.version}
        out[name] = record
    return out
