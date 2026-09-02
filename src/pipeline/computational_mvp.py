"""Unified descriptor-only MVP. Deliberately contains no mechanism prediction."""

from dataclasses import asdict
from typing import Optional

from src.descriptors import ElementPropertyTable, calculate_descriptors, normalize_composition
from src.inputs import AlloyInput
from src.sfe import SFEResult, unavailable_sfe
from src.thermodynamics import CalphadRequest, ThermodynamicsEngine, UnavailableThermodynamicsEngine


def run_pipeline(alloy: AlloyInput, properties: Optional[ElementPropertyTable] = None,
                 thermodynamics: Optional[ThermodynamicsEngine] = None,
                 database_name: Optional[str] = None, database_version: Optional[str] = None,
                 sfe: Optional[SFEResult] = None) -> dict:
    normalized = normalize_composition(alloy.composition, properties)
    descriptors = calculate_descriptors(normalized["atomic_fractions"], properties)
    engine = thermodynamics or UnavailableThermodynamicsEngine("no qualified CALPHAD engine configured")
    if normalized["atomic_fractions"] is None:
        calphad = {"status": "NOT_AVAILABLE", "reason": "atomic composition unresolved"}
    else:
        calphad = asdict(engine.calculate(CalphadRequest(normalized["atomic_fractions"],
                         alloy.deformation.test_temperature, database_name, database_version)))
    sfe_record = asdict(sfe or unavailable_sfe("no qualified SFE source or calculation configured",
                                               temperature=alloy.deformation.test_temperature))
    unresolved = []
    if normalized["status"] != "VALID": unresolved.append("normalized_input.atomic_fractions")
    unresolved.extend(f"composition_descriptors.{k}" for k, v in descriptors.items() if v["status"] != "VALID")
    if calphad["status"] != "AVAILABLE": unresolved.append("calphad")
    if sfe_record["SFE_status"] != "AVAILABLE": unresolved.append("sfe")
    processing = asdict(alloy.processing)
    unresolved.extend(f"processing_descriptors.{k}" for k, v in processing.items() if v is None)
    if alloy.microstructure is None: unresolved.append("microstructure")
    return {"normalized_input": normalized, "composition_descriptors": descriptors,
            "processing_descriptors": processing, "deformation_conditions": asdict(alloy.deformation),
            "microstructure": asdict(alloy.microstructure) if alloy.microstructure else None,
            "calphad": calphad, "sfe": sfe_record, "provenance": dict(alloy.provenance),
            "condition_id": alloy.condition_id, "missing_unresolved_fields": unresolved}
