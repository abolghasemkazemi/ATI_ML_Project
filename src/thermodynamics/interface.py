"""Engine-neutral CALPHAD contract (Thermo-Calc, pycalphad, OpenCALPHAD)."""

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Protocol


@dataclass(frozen=True)
class CalphadRequest:
    atomic_fractions: Mapping[str, float]
    temperature: float
    database_name: Optional[str]
    database_version: Optional[str]


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
                             provenance={"request_preserved": True})
