"""Database-specific phase mappings; mappings must never be inferred silently."""

from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class PhaseMapping:
    database_name: str
    database_version: str
    mapping: Mapping[str, str]
    provenance: str

    def canonical(self, database_phase: str) -> Optional[str]:
        return self.mapping.get(database_phase)


def map_phase(database_phase: str, mapping: PhaseMapping) -> Optional[str]:
    return mapping.canonical(database_phase)
