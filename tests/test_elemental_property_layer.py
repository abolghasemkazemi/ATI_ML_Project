"""Software tests use synthetic values; they are not scientific reference data."""

import pytest

from src.descriptors import calculate_descriptors, normalize_composition
from src.inputs import Composition
from src.reference_data import ElementPropertyTable, LookupStatus, PropertyRecord


def rec(element, prop, value, definition=None, method=None, status=LookupStatus.VALID):
    return PropertyRecord(element, 1 if element == "A" else 2, prop, value,
                          "g mol^-1" if prop == "atomic_weight" else "dimensionless",
                          definition or f"synthetic {prop} definition",
                          method or f"synthetic {prop} method", "synthetic unit-test source",
                          "fixture-v1", "tests/test_elemental_property_layer.py", status,
                          "SYNTHETIC; not scientific data")


def table(records):
    return ElementPropertyTable(records, "synthetic-test-only", "1")


def test_atomic_weight_lookup_success_missing_and_unsupported_element():
    props = table([rec("A", "atomic_weight", 1.0)])
    assert props.atomic_weight("A").status == LookupStatus.VALID
    assert props.atomic_weight("A").value == 1.0
    assert props.atomic_weight("B").status == LookupStatus.NOT_AVAILABLE
    assert props.atomic_weight("Xx").status == LookupStatus.NOT_AVAILABLE


def test_weight_percent_conversion_and_provenance_retention():
    props = table([rec("A", "atomic_weight", 1.0), rec("B", "atomic_weight", 2.0)])
    result = normalize_composition(Composition(("A", "B"), (50, 50), "wt.%", "synthetic fixture"), props)
    assert result["status"] == "VALID"
    assert result["atomic_fractions"] == pytest.approx({"A": 2 / 3, "B": 1 / 3})
    assert result["conversion_provenance"]["property_table"] == {"id": "synthetic-test-only", "version": "1"}
    assert result["conversion_provenance"]["property_records"][0]["source"] == "synthetic unit-test source"


def test_missing_and_unverified_atomic_weight_fail_closed():
    composition = Composition(("A", "B"), (50, 50), "wt.%", "synthetic fixture")
    assert normalize_composition(composition, table([rec("A", "atomic_weight", 1)]))["status"] == "NOT_AVAILABLE"
    props = table([rec("A", "atomic_weight", 1),
                   rec("B", "atomic_weight", 2, status=LookupStatus.UNVERIFIED_SOURCE)])
    assert normalize_composition(composition, props)["status"] == "UNVERIFIED_SOURCE"


def test_vec_lookup_and_descriptor():
    props = table([rec("A", "vec", 1), rec("B", "vec", 3)])
    assert props.vec("A").value == 1
    result = calculate_descriptors({"A": .5, "B": .5}, props)["vec"]
    assert result["status"] == "VALID" and result["value"] == 2
    assert len(result["provenance"]["property_records"]) == 2


def test_consistent_and_incompatible_radius_definitions():
    consistent = table([rec("A", "atomic_radius", 1, "synthetic metallic radius", "synthetic method"),
                        rec("B", "atomic_radius", 2, "synthetic metallic radius", "synthetic method")])
    assert calculate_descriptors({"A": .5, "B": .5}, consistent)["atomic_size_mismatch"]["status"] == "VALID"
    mixed = table([rec("A", "atomic_radius", 1, "synthetic metallic radius", "synthetic method"),
                   rec("B", "atomic_radius", 2, "synthetic covalent radius", "synthetic method")])
    result = calculate_descriptors({"A": .5, "B": .5}, mixed)["atomic_size_mismatch"]
    assert result["status"] == "INCOMPATIBLE_DEFINITION" and result["value"] is None


def test_consistent_and_incompatible_electronegativity_scales():
    consistent = table([rec("A", "electronegativity", 1, method="synthetic scale S"),
                        rec("B", "electronegativity", 3, method="synthetic scale S")])
    assert calculate_descriptors({"A": .5, "B": .5}, consistent)["electronegativity_difference"]["value"] == 1
    mixed = table([rec("A", "electronegativity", 1, method="synthetic scale S"),
                   rec("B", "electronegativity", 3, method="synthetic scale T")])
    result = calculate_descriptors({"A": .5, "B": .5}, mixed)["electronegativity_difference"]
    assert result["status"] == "INCOMPATIBLE_DEFINITION" and result["value"] is None
