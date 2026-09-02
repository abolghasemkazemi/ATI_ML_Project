"""Input contract for one reported alloy condition; no fields are inferred."""

from dataclasses import asdict, dataclass, field
from math import isfinite
from typing import Any, Mapping, Optional


def _optional_nonnegative(name: str, value: Optional[float]) -> None:
    if value is not None and (not isfinite(value) or value < 0):
        raise ValueError(f"{name} must be finite and non-negative when reported")


@dataclass(frozen=True)
class Composition:
    elements: tuple[str, ...]
    fractions: tuple[float, ...]
    basis: str
    source: str

    def __post_init__(self) -> None:
        if not self.elements or not self.fractions or not self.source.strip():
            raise ValueError("elements, fractions, and composition source are required")
        if self.basis not in {"at.%", "wt.%"}:
            raise ValueError("composition basis must be 'at.%' or 'wt.%'")
        if len(self.elements) != len(self.fractions):
            raise ValueError("elements and fractions must have equal lengths")
        canonical = [element.strip().casefold() for element in self.elements]
        if any(not element for element in canonical):
            raise ValueError("element symbols must not be empty")
        if len(canonical) != len(set(canonical)):
            raise ValueError("duplicate elements are not permitted")
        if any(not isfinite(value) or value <= 0 for value in self.fractions):
            raise ValueError("fractions must be finite and greater than zero")
        if abs(sum(self.fractions) - 100.0) > 1e-6:
            raise ValueError("reported composition must sum to 100 percent")

    def reported(self) -> dict[str, float]:
        return dict(zip(self.elements, self.fractions))


@dataclass(frozen=True)
class Processing:
    homogenization_temperature: Optional[float] = None
    homogenization_time: Optional[float] = None
    solution_treatment_temperature: Optional[float] = None
    solution_treatment_time: Optional[float] = None
    annealing_temperature: Optional[float] = None
    annealing_time: Optional[float] = None
    cold_rolling_reduction: Optional[float] = None
    cooling_condition: Optional[str] = None

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if name != "cooling_condition":
                _optional_nonnegative(name, value)
        if self.cold_rolling_reduction is not None and self.cold_rolling_reduction > 100:
            raise ValueError("cold_rolling_reduction cannot exceed 100 percent")


@dataclass(frozen=True)
class Deformation:
    test_temperature: float
    strain_rate: float
    loading_mode: str

    def __post_init__(self) -> None:
        if not isfinite(self.test_temperature) or self.test_temperature < 0:
            raise ValueError("test_temperature must be finite and non-negative")
        if not isfinite(self.strain_rate) or self.strain_rate <= 0:
            raise ValueError("strain_rate must be finite and greater than zero")
        if not self.loading_mode.strip():
            raise ValueError("loading_mode is required")


@dataclass(frozen=True)
class Microstructure:
    grain_size: Optional[float] = None
    initial_fcc_fraction: Optional[float] = None
    initial_hcp_fraction: Optional[float] = None
    initial_bcc_fraction: Optional[float] = None

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            _optional_nonnegative(name, value)
            if "fraction" in name and value is not None and value > 1:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class AlloyInput:
    composition: Composition
    processing: Processing
    deformation: Deformation
    provenance: Mapping[str, Any]
    microstructure: Optional[Microstructure] = None
    condition_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.provenance:
            raise ValueError("input provenance is required")
