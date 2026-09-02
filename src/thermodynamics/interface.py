"""Engine-neutral CALPHAD contract (Thermo-Calc, pycalphad, OpenCALPHAD)."""

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Protocol, Sequence


@dataclass(frozen=True)
class CalphadRequest:
    atomic_fractions: Mapping[str, float]
    temperature: float
    database_name: Optional[str]
    database_version: Optional[str]
    composition_basis: str = "atomic_fraction"
    pressure_pa: float = 101325.0
    selected_components: Optional[Sequence[str]] = None
    selected_phases: Optional[Sequence[str]] = None
    conditions: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CalphadResult:
    status: str
    reason: Optional[str]
    calculation_temperature: float
    database_name: Optional[str]
    database_version: Optional[str]
    engine_name: str
    engine_version: Optional[str]
    equilibrium_phase_fractions: Optional[Mapping[str, float]] = None
    fcc_fraction: Optional[float] = None
    bcc_fraction: Optional[float] = None
    hcp_fraction: Optional[float] = None
    gibbs_energies: Optional[Mapping[str, float]] = None
    phase_stability_descriptors: Optional[Mapping[str, Any]] = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    equilibrium_phase_names: Optional[Sequence[str]] = None
    other_stable_phases: Optional[Mapping[str, float]] = None
    convergence_status: Optional[str] = None
    calculation_conditions: Mapping[str, Any] = field(default_factory=dict)


class ThermodynamicsEngine(Protocol):
    def calculate(self, request: CalphadRequest) -> CalphadResult: ...


class UnavailableThermodynamicsEngine:
    def __init__(self, reason: str, name: str = "NOT_CONFIGURED", version: Optional[str] = None):
        self.reason, self.name, self.version = reason, name, version

    def calculate(self, request: CalphadRequest) -> CalphadResult:
        reason = self.reason
        if not request.database_name or not request.database_version:
            reason = "qualified CALPHAD database name and version are required"
        return CalphadResult("NOT_AVAILABLE", reason, request.temperature, request.database_name,
                             request.database_version, self.name, self.version,
                             provenance={"request_preserved": True,
                                         "request": request_snapshot(request)},
                             convergence_status="NOT_RUN",
                             calculation_conditions=request.conditions)


def request_snapshot(request: CalphadRequest) -> Mapping[str, Any]:
    """Return a serialization-friendly, lossless calculation-input record."""
    return {
        "composition": dict(request.atomic_fractions),
        "composition_basis": request.composition_basis,
        "temperature_k": request.temperature,
        "pressure_pa": request.pressure_pa,
        "selected_components": list(request.selected_components or request.atomic_fractions),
        "selected_phases": None if request.selected_phases is None else list(request.selected_phases),
        "database_name": request.database_name,
        "database_version": request.database_version,
        "conditions": dict(request.conditions),
        "provenance": dict(request.provenance),
    }
