"""Elemental-property records and fail-closed lookup operations."""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable, Optional


class LookupStatus(str, Enum):
    VALID = "VALID"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    INCOMPATIBLE_DEFINITION = "INCOMPATIBLE_DEFINITION"
    UNVERIFIED_SOURCE = "UNVERIFIED_SOURCE"


@dataclass(frozen=True)
class PropertyRecord:
    element_symbol: str
    atomic_number: int
    property_name: str
    value: float
    unit: str
    definition: str
    methodology_or_scale: str
    source: str
    source_version_date: str
    access_reference: str
    validation_status: LookupStatus
    notes: str = ""

    def __post_init__(self):
        required = (self.element_symbol, self.property_name, self.unit, self.definition,
                    self.methodology_or_scale, self.source, self.source_version_date,
                    self.access_reference)
        if not all(isinstance(item, str) and item.strip() for item in required):
            raise ValueError("property records require complete definition and provenance text")
        if self.atomic_number < 1 or not isinstance(self.value, (int, float)):
            raise ValueError("atomic_number and numeric value must be valid")


@dataclass(frozen=True)
class LookupResult:
    element_symbol: str
    property_name: str
    status: LookupStatus
    value: Optional[float]
    record: Optional[PropertyRecord]
    reason: Optional[str] = None


class ElementPropertyTable:
    """An immutable logical table; only records marked VALID are calculation-ready."""

    def __init__(self, records: Iterable[PropertyRecord], table_id: str, version: str):
        if not table_id.strip() or not version.strip():
            raise ValueError("table_id and version are required")
        self.table_id, self.version = table_id, version
        self._records = {}
        for record in records:
            key = (record.element_symbol, record.property_name)
            if key in self._records:
                raise ValueError(f"duplicate property record: {key}")
            self._records[key] = record

    def lookup(self, element_symbol: str, property_name: str) -> LookupResult:
        record = self._records.get((element_symbol, property_name))
        if record is None:
            return LookupResult(element_symbol, property_name, LookupStatus.NOT_AVAILABLE, None, None,
                                "element/property pair is absent from the table")
        if record.validation_status != LookupStatus.VALID:
            return LookupResult(element_symbol, property_name, LookupStatus.UNVERIFIED_SOURCE, None,
                                record, "property record is not validated for calculation")
        return LookupResult(element_symbol, property_name, LookupStatus.VALID, record.value, record)

    def atomic_weight(self, element_symbol: str) -> LookupResult:
        return self.lookup(element_symbol, "atomic_weight")

    def vec(self, element_symbol: str) -> LookupResult:
        return self.lookup(element_symbol, "vec")

    def atomic_radius(self, element_symbol: str) -> LookupResult:
        return self.lookup(element_symbol, "atomic_radius")

    def electronegativity(self, element_symbol: str) -> LookupResult:
        return self.lookup(element_symbol, "electronegativity")

    def provenance(self, results) -> dict:
        return {"property_table": {"id": self.table_id, "version": self.version},
                "property_records": [asdict(r.record) if r.record else {
                    "element_symbol": r.element_symbol, "property_name": r.property_name,
                    "validation_status": r.status.value, "reason": r.reason} for r in results]}
