from pathlib import Path

import pytest

from src.thermodynamics import (CalphadRequest, DatabaseQualification, PhaseMapping,
                                PyCalphadEngine, UnavailableThermodynamicsEngine,
                                detect_backends, discover_databases, map_phase,
                                qualify_database)


def database(**overrides):
    values = dict(name="TRACEABLE", version="1", source="official documentation",
                  supported_elements=("FE", "MN", "CO", "CR"),
                  supported_phases=("FCC_A1", "BCC_A2", "HCP_A3"),
                  assessed_systems=("Fe-Mn-Co-Cr",), status="candidate", limitations="fixture metadata")
    values.update(overrides)
    return DatabaseQualification(**values)


def test_backend_detection_returns_all_engines():
    capabilities = detect_backends()
    assert set(capabilities) == {"pycalphad", "OpenCALPHAD", "Thermo-Calc", "Thermo-Calc Python API"}
    assert all(item.availability in {"AVAILABLE", "NOT_AVAILABLE"} for item in capabilities.values())


def test_missing_database_discovery(tmp_path):
    assert discover_databases((tmp_path, tmp_path / "absent")) == ()
    (tmp_path / "example.TDB").write_text("test-only, not a database")
    assert discover_databases((tmp_path,)) == ((tmp_path / "example.TDB").resolve(),)


def test_database_qualification_and_unsupported_element():
    assert qualify_database(None, ("FE",)) == "NOT_AVAILABLE"
    assert qualify_database(database(), ("FE", "MN", "CO", "CR")) == "QUALIFIED_FOR_TEST"
    assert qualify_database(database(assessed_systems=()), ("FE", "MN")) == "PARTIALLY_QUALIFIED"
    assert qualify_database(database(), ("NI",)) == "UNQUALIFIED"
    assert qualify_database(database(supported_phases=("FCC_A1",)), ("FE",)) == "UNQUALIFIED"


def test_phase_mapping_is_explicit_and_database_scoped():
    mapping = PhaseMapping("TRACEABLE", "1", {"FCC_A1": "FCC"}, "official phase documentation")
    assert map_phase("FCC_A1", mapping) == "FCC"
    assert map_phase("BCC_A2", mapping) is None
    assert mapping.provenance == "official phase documentation"


def test_unavailable_result_preserves_full_request_provenance():
    request = CalphadRequest({"FE": 0.4, "MN": 0.6}, 1000, "DB", "1",
                             pressure_pa=100000, selected_phases=("FCC_A1",),
                             conditions={"purpose": "software fixture"}, provenance={"source": "test"})
    result = UnavailableThermodynamicsEngine("no engine").calculate(request)
    assert result.status == "NOT_AVAILABLE"
    assert result.fcc_fraction is None and result.equilibrium_phase_fractions is None
    assert result.provenance["request"]["composition"] == {"FE": 0.4, "MN": 0.6}
    assert result.provenance["request"]["provenance"] == {"source": "test"}
    assert result.convergence_status == "NOT_RUN"


def test_invalid_database_backend_combinations_fail_closed(tmp_path):
    mapping = PhaseMapping("DB", "1", {}, "fixture")
    with pytest.raises(ValueError, match="QUALIFIED"):
        PyCalphadEngine(tmp_path / "missing.tdb", mapping, "UNQUALIFIED")
    with pytest.raises(FileNotFoundError):
        PyCalphadEngine(tmp_path / "missing.tdb", mapping, "QUALIFIED_FOR_TEST")
