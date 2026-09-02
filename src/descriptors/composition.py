"""Composition conversion and descriptors backed by verified property records."""

from math import log, sqrt
from typing import Mapping, Optional

from src.inputs import Composition
from src.reference_data import ElementPropertyTable, LookupStatus

R = 8.31446261815324


def _property_failure(results, property_name):
    status = (LookupStatus.UNVERIFIED_SOURCE if any(r.status == LookupStatus.UNVERIFIED_SOURCE for r in results)
              else LookupStatus.NOT_AVAILABLE)
    missing = [r.element_symbol for r in results if r.status != LookupStatus.VALID]
    return status.value, f"no validated {property_name} for: {', '.join(missing)}"


def normalize_composition(composition: Composition, properties: Optional[ElementPropertyTable] = None) -> dict:
    original = {"elements": list(composition.elements), "fractions": list(composition.fractions),
                "basis": composition.basis, "source": composition.source}
    if composition.basis == "at.%":
        return {"original_composition": original,
                "atomic_fractions": {e: v / 100.0 for e, v in composition.reported().items()},
                "status": "VALID", "conversion_provenance": "at.% divided by 100; no basis conversion"}
    if properties is None:
        return {"original_composition": original, "atomic_fractions": None,
                "status": "NOT_AVAILABLE", "reason": "wt.% conversion requires validated atomic weights",
                "conversion_provenance": None}
    lookups = [properties.atomic_weight(e) for e in composition.elements]
    if any(r.status != LookupStatus.VALID for r in lookups):
        status, reason = _property_failure(lookups, "atomic weight")
        return {"original_composition": original, "atomic_fractions": None, "status": status,
                "reason": reason, "conversion_provenance": properties.provenance(lookups)}
    weights = {r.element_symbol: r.value for r in lookups}
    moles = {e: v / weights[e] for e, v in composition.reported().items()}
    total = sum(moles.values())
    return {"original_composition": original,
            "atomic_fractions": {e: n / total for e, n in moles.items()}, "status": "VALID",
            "conversion_provenance": {"formula": "x_i=(w_i/M_i)/sum(w_j/M_j)",
                                      **properties.provenance(lookups)}}


def calculate_descriptors(atomic_fractions: Optional[Mapping[str, float]],
                          properties: Optional[ElementPropertyTable]) -> dict:
    metadata = {
        "number_of_elements": ("N", "none", None),
        "vec": ("sum(x_i VEC_i)", "dimensionless", "vec"),
        "ideal_mixing_entropy": ("-R sum(x_i ln x_i)", "J mol^-1 K^-1", None),
        "atomic_size_mismatch": ("100 sqrt(sum(x_i(1-r_i/rbar)^2))", "%", "atomic_radius"),
        "electronegativity_difference": ("sqrt(sum(x_i(chi_i-chibar)^2))", "dimensionless", "electronegativity"),
    }
    if atomic_fractions is None:
        return {k: {"status": "NOT_AVAILABLE", "value": None, "formula": f, "unit": u,
                    "required_property": p, "reason": "atomic fractions unavailable"}
                for k, (f, u, p) in metadata.items()}
    out = {}
    for name, (formula, unit, prop) in metadata.items():
        record = {"status": "VALID", "value": None, "formula": formula, "unit": unit,
                  "required_property": prop, "provenance": "input composition" if prop is None else None}
        if name == "number_of_elements":
            record["value"] = len(atomic_fractions)
        elif name == "ideal_mixing_entropy":
            record["value"] = -R * sum(x * log(x) for x in atomic_fractions.values())
        elif properties is None:
            record.update(status="NOT_AVAILABLE", reason=f"no property table supplied for {prop}")
        else:
            lookups = [properties.lookup(e, prop) for e in atomic_fractions]
            if any(r.status != LookupStatus.VALID for r in lookups):
                status, reason = _property_failure(lookups, prop)
                record.update(status=status, reason=reason, provenance=properties.provenance(lookups))
            else:
                definitions = {r.record.definition for r in lookups}
                methods = {r.record.methodology_or_scale for r in lookups}
                units = {r.record.unit for r in lookups}
                if prop in {"atomic_radius", "electronegativity"} and (len(definitions) != 1 or len(methods) != 1 or len(units) != 1):
                    record.update(status="INCOMPATIBLE_DEFINITION",
                                  reason=f"{prop} definition, methodology/scale, and unit must match",
                                  provenance=properties.provenance(lookups))
                else:
                    vals = {r.element_symbol: r.value for r in lookups}
                    if name == "vec":
                        record["value"] = sum(atomic_fractions[e] * vals[e] for e in vals)
                    else:
                        mean = sum(atomic_fractions[e] * vals[e] for e in vals)
                        terms = ((1 - vals[e] / mean) if name == "atomic_size_mismatch" else
                                 (vals[e] - mean) for e in vals)
                        record["value"] = (100 if name == "atomic_size_mismatch" else 1) * sqrt(
                            sum(atomic_fractions[e] * term ** 2 for e, term in zip(vals, terms)))
                    record["provenance"] = properties.provenance(lookups)
        out[name] = record
    return out
