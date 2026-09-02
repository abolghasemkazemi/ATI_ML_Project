"""Elemental-property records, CSV loading, and fail-closed lookups."""

import csv
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
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
    value: Optional[float]
    unit: str
    definition: str
    methodology_or_scale: str
    source: str
    source_version_date: str
    access_reference: str
    validation_status: LookupStatus
    notes: str = ""
    uncertainty: str = ""
    value_min: Optional[float] = None
    value_max: Optional[float] = None

    def __post_init__(self):
        required = (self.element_symbol, self.property_name, self.unit, self.definition,
                    self.methodology_or_scale, self.source, self.source_version_date,
                    self.access_reference)
        if not all(isinstance(item, str) and item.strip() for item in required):
            raise ValueError("property records require complete definition and provenance text")
        if self.atomic_number < 1:
            raise ValueError("atomic_number must be valid")
        if self.validation_status == LookupStatus.VALID and not isinstance(self.value, (int, float)):
            raise ValueError("VALID property records require a numeric value")
        if self.value is not None and not isinstance(self.value, (int, float)):
            raise ValueError("property value must be numeric or absent")


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

    @classmethod
    def from_csv(cls, path, table_id="elemental_properties", version=None):
        """Load the controlled long-form CSV without inventing missing values."""
        path = Path(path)
        records = []
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                def optional_float(name):
                    return float(row[name]) if row.get(name, "").strip() else None
                records.append(PropertyRecord(
                    element_symbol=row["element_symbol"], atomic_number=int(row["atomic_number"]),
                    property_name=row["property_name"], value=optional_float("value"),
                    unit=row["unit"], definition=row["definition"],
                    methodology_or_scale=row["methodology_or_scale"], source=row["source"],
                    source_version_date=row["source_version_date"],
                    access_reference=row["access_reference"],
                    validation_status=LookupStatus(row["validation_status"]), notes=row.get("notes", ""),
                    uncertainty=row.get("uncertainty", ""), value_min=optional_float("value_min"),
                    value_max=optional_float("value_max")))
        return cls(records, table_id, version or path.stem.rsplit("_", 1)[-1])

    def lookup(self, element_symbol: str, property_name: str) -> LookupResult:
        record = self._records.get((element_symbol, property_name))
        if record is None:
            return LookupResult(element_symbol, property_name, LookupStatus.NOT_AVAILABLE, None, None,
                                "element/property pair is absent from the table")
        if record.validation_status != LookupStatus.VALID:
            return LookupResult(element_symbol, property_name, record.validation_status, None,
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
