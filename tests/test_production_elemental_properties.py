import csv
import json
import math
from pathlib import Path

import pytest

from src.descriptors import calculate_descriptors, normalize_composition
from src.inputs import Composition
from src.pipeline.computational_mvp import load_production_properties
from src.reference_data import LookupStatus


CSV_PATH = Path("data/reference/elemental_properties/elemental_properties_v1.csv")
REQUIRED = {"Fe", "Mn", "Co", "Cr", "Ni", "N", "Al", "Cu", "Ti", "V", "Nb", "Mo", "W", "Si", "C"}
PROPERTIES = {"atomic_weight", "vec", "electronegativity", "atomic_radius"}


def rows():
    with CSV_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_production_schema_coverage_and_property_level_provenance():
    data = rows()
    assert len(data) == len(REQUIRED) * len(PROPERTIES)
    assert {(r["element_symbol"], r["property_name"]) for r in data} == {
        (e, p) for e in REQUIRED for p in PROPERTIES}
    for row in data:
        assert row["source"] and row["source_version_date"] and row["access_reference"]
        assert row["definition"] and row["methodology_or_scale"]
        assert row["validation_status"] in {s.value for s in LookupStatus}
        assert row["value"] or row["validation_status"] != "VALID"


def test_atomic_weight_intervals_and_conversion():
    table = load_production_properties()
    nitrogen = table.atomic_weight("N").record
    assert (nitrogen.value, nitrogen.value_min, nitrogen.value_max) == (14.007, 14.00643, 14.00728)
    result = normalize_composition(
        Composition(("Fe", "Ni"), (50.0, 50.0), "wt.%", "production conversion test"), table)
    expected_fe = (50 / 55.845) / ((50 / 55.845) + (50 / 58.6934))
    assert result["status"] == "VALID"
    assert result["atomic_fractions"]["Fe"] == pytest.approx(expected_fe)
    assert result["conversion_provenance"]["property_records"][0]["uncertainty"]


def test_vec_radius_and_electronegativity_conventions_are_consistent():
    data = rows()
    vec = [r for r in data if r["property_name"] == "vec"]
    chi = [r for r in data if r["property_name"] == "electronegativity"]
    radii = [r for r in data if r["property_name"] == "atomic_radius" and r["validation_status"] == "VALID"]
    assert len({r["methodology_or_scale"] for r in vec}) == 1
    assert len({r["methodology_or_scale"] for r in chi}) == 1
    assert {r["methodology_or_scale"] for r in chi} == {"Pauling scale"}
    assert len({(r["definition"], r["methodology_or_scale"], r["unit"]) for r in radii}) == 1


def test_unresolved_radius_fails_closed_without_losing_status():
    table = load_production_properties()
    assert table.atomic_radius("N").status == LookupStatus.NOT_AVAILABLE
    result = calculate_descriptors({"Fe": 0.99, "N": 0.01}, table)["atomic_size_mismatch"]
    assert result["status"] == "NOT_AVAILABLE" and result["value"] is None
    unresolved = next(r for r in result["provenance"]["property_records"] if r["element_symbol"] == "N")
    assert unresolved["validation_status"] == LookupStatus.NOT_AVAILABLE


def test_fe40mn30co20cr10_integration_fixture():
    fixture = json.loads(Path("tests/fixtures/fe40mn30co20cr10_descriptors_v1.json").read_text())
    fractions = fixture["expected"]["normalized_atomic_fractions"]
    result = calculate_descriptors(fractions, load_production_properties())
    assert result["number_of_elements"]["value"] == 4
    assert result["ideal_mixing_entropy"]["value"] == pytest.approx(fixture["expected"]["ideal_mixing_entropy_J_mol_K"])
    assert result["vec"]["value"] == pytest.approx(7.7)
    assert result["atomic_size_mismatch"]["value"] == pytest.approx(fixture["expected"]["atomic_size_mismatch_percent"])
    assert result["electronegativity_difference"]["value"] == pytest.approx(
        fixture["expected"]["electronegativity_difference_pauling"])
    assert all(result[name]["status"] == "VALID" for name in result)
