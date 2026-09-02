"""Method-separated SFE record; experimental values are never substituted."""

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class SFEResult:
    SFE_experimental: Optional[float]
    SFE_calculated: Optional[float]
    SFE_method: Optional[str]
    SFE_temperature: Optional[float]
    SFE_source: Optional[str]
    SFE_uncertainty: Optional[float]
    SFE_status: str
    reason: Optional[str] = None
    provenance: Optional[Mapping[str, Any]] = None


def unavailable_sfe(reason: str, method: Optional[str] = None, temperature: Optional[float] = None) -> SFEResult:
    return SFEResult(None, None, method, temperature, None, None, "NOT_AVAILABLE", reason,
                     {"values_imputed": False})
