import math

import pytest

from src.descriptors import ElementPropertyTable, calculate_descriptors, normalize_composition
from src.inputs import AlloyInput, Composition, Deformation, Processing
from src.pipeline import run_pipeline
from src.reference_data import LookupStatus, PropertyRecord
from src.thermodynamics import CalphadRequest, UnavailableThermodynamicsEngine


def composition(basis="at.%"):
    return Composition(("A", "B"), (50.0, 50.0), basis, "test fixture (not scientific data)")


def property_record(element, name, value):
    return PropertyRecord(element, 1 if element == "A" else 2, name, value,
                          "synthetic unit", f"synthetic {name} definition",
                          f"synthetic {name} method", "test fixture", "1",
                          "tests/test_computational_mvp.py", LookupStatus.VALID,
                          "synthetic; not scientific data")


def test_composition_sum_validation_and_duplicates():
    with pytest.raises(ValueError, match="sum"):
        Composition(("A", "B"), (40.0, 50.0), "at.%", "fixture")
    with pytest.raises(ValueError, match="duplicate"):
        Composition(("A", "a"), (50.0, 50.0), "at.%", "fixture")


def test_at_percent_normalization_preserves_original():
    result = normalize_composition(composition())
    assert result["atomic_fractions"] == {"A": .5, "B": .5}
    assert result["original_composition"]["fractions"] == [50.0, 50.0]


def test_weight_percent_requires_atomic_weights_and_can_convert_with_provenance():
    unresolved = normalize_composition(composition("wt.%"))
    assert unresolved["status"] == "NOT_AVAILABLE"
    table = ElementPropertyTable([property_record("A", "atomic_weight", 1.0),
                                  property_record("B", "atomic_weight", 2.0)], "fixture", "1")
    result = normalize_composition(composition("wt.%"), table)
    assert result["atomic_fractions"] == pytest.approx({"A": 2 / 3, "B": 1 / 3})
    assert result["conversion_provenance"]["property_table"]["id"] == "fixture"


def test_descriptor_calculation_and_missing_properties():
    atomic = {"A": .5, "B": .5}
    missing = calculate_descriptors(atomic, None)
    assert missing["vec"]["status"] == "NOT_AVAILABLE"
    assert missing["ideal_mixing_entropy"]["status"] == "VALID"
    table = ElementPropertyTable([
        property_record(element, name, value)
        for element, values in {"A": (1.0, 1.0, 1.0), "B": (3.0, 2.0, 3.0)}.items()
        for name, value in zip(("vec", "atomic_radius", "electronegativity"), values)], "fixture", "1")
    values = calculate_descriptors(atomic, table)
    assert values["vec"]["value"] == 2.0
    assert values["electronegativity_difference"]["value"] == 1.0
    assert values["ideal_mixing_entropy"]["value"] == pytest.approx(8.31446261815324 * math.log(2))
    assert values["vec"]["provenance"]["property_table"]["id"] == "fixture"


def test_unavailable_calphad_engine_and_database():
    engine = UnavailableThermodynamicsEngine("engine absent")
    with_db = engine.calculate(CalphadRequest({"A": 1.0}, 300, "DB", "1"))
    assert with_db.status == "NOT_AVAILABLE" and with_db.reason == "engine absent"
    without_db = engine.calculate(CalphadRequest({"A": 1.0}, 300, None, None))
    assert without_db.status == "NOT_AVAILABLE" and "database" in without_db.reason


def test_pipeline_unavailable_sfe_and_provenance_preservation():
    alloy = AlloyInput(composition(), Processing(), Deformation(300, 1e-3, "tension"),
                       {"paper_id": "fixture-source"})
    result = run_pipeline(alloy)
    assert result["sfe"]["SFE_status"] == "NOT_AVAILABLE"
    assert result["sfe"]["SFE_experimental"] is None
    assert result["calphad"]["status"] == "NOT_AVAILABLE"
    assert result["provenance"] == {"paper_id": "fixture-source"}
    assert "prediction" not in result
