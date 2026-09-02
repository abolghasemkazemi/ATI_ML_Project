"""Fail-closed CALPHAD discovery and database qualification utilities."""

from dataclasses import dataclass
from importlib import metadata, util
from pathlib import Path
import shutil
from typing import Iterable, Mapping, Optional, Sequence


@dataclass(frozen=True)
class BackendCapability:
    engine: str
    version: Optional[str]
    availability: str
    provenance: str


@dataclass(frozen=True)
class DatabaseQualification:
    name: str
    version: Optional[str]
    source: Optional[str]
    supported_elements: Sequence[str]
    supported_phases: Sequence[str]
    assessed_systems: Sequence[str]
    status: str
    limitations: str


def detect_backends() -> Mapping[str, BackendCapability]:
    """Detect executables/APIs without starting a solver or probing a licence."""
    py = util.find_spec("pycalphad")
    tc = util.find_spec("tc_python")
    oc_path = shutil.which("oc") or shutil.which("opencalphad")
    tc_path = shutil.which("Thermo-Calc") or shutil.which("thermocalc")
    return {
        "pycalphad": BackendCapability("pycalphad", _version("pycalphad") if py else None,
                                        "AVAILABLE" if py else "NOT_AVAILABLE", "Python import discovery"),
        "OpenCALPHAD": BackendCapability("OpenCALPHAD", None,
                                          "AVAILABLE" if oc_path else "NOT_AVAILABLE",
                                          f"PATH executable discovery: {oc_path or 'none'}"),
        "Thermo-Calc": BackendCapability("Thermo-Calc", None,
                                          "AVAILABLE" if tc_path else "NOT_AVAILABLE",
                                          f"PATH executable discovery: {tc_path or 'none'}"),
        "Thermo-Calc Python API": BackendCapability("Thermo-Calc Python API", _version("tc_python") if tc else None,
                                                     "AVAILABLE" if tc else "NOT_AVAILABLE",
                                                     "Python import discovery"),
    }


def discover_databases(roots: Iterable[Path]) -> Sequence[Path]:
    return tuple(sorted({path.resolve() for root in roots if root.exists()
                         for path in root.rglob("*") if path.is_file() and path.suffix.lower() == ".tdb"}))


def qualify_database(database: Optional[DatabaseQualification], required_elements: Iterable[str]) -> str:
    """Apply traceability, element, phase, and assessed-space gates.

    Merely parsing element/phase names is deliberately insufficient for qualification.
    """
    if database is None:
        return "NOT_AVAILABLE"
    required = {e.upper() for e in required_elements}
    covered = {e.upper() for e in database.supported_elements}
    phases = {p.upper() for p in database.supported_phases}
    traceable = bool(database.name and database.version and database.source)
    structural = any("FCC" in p for p in phases) and any("BCC" in p for p in phases)
    assessed = bool(database.assessed_systems)
    if traceable and required <= covered and structural and assessed:
        return "QUALIFIED_FOR_TEST"
    if traceable and required <= covered and structural:
        return "PARTIALLY_QUALIFIED"
    return "UNQUALIFIED"


def _version(package: str) -> Optional[str]:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return None
