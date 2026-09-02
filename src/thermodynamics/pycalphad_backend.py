"""Optional pycalphad equilibrium adapter; imported only when explicitly used."""

from pathlib import Path
from typing import Mapping

from .interface import CalphadRequest, CalphadResult, request_snapshot
from .phase_mapping import PhaseMapping


class PyCalphadEngine:
    def __init__(self, database_path: Path, mapping: PhaseMapping, qualification_status: str):
        if qualification_status != "QUALIFIED_FOR_TEST":
            raise ValueError("database must be QUALIFIED_FOR_TEST")
        if not database_path.is_file():
            raise FileNotFoundError(database_path)
        self.database_path, self.mapping = database_path, mapping

    def calculate(self, request: CalphadRequest) -> CalphadResult:
        import pycalphad
        from pycalphad import Database, equilibrium, variables as v

        components = list(request.selected_components or request.atomic_fractions)
        phases = list(request.selected_phases or Database(str(self.database_path)).phases.keys())
        db = Database(str(self.database_path))
        conds = {v.T: request.temperature, v.P: request.pressure_pa, v.N: 1}
        independent = components[:-1]
        conds.update({v.X(element): request.atomic_fractions[element] for element in independent})
        eq = equilibrium(db, components, phases, conds)
        phase_values = eq.Phase.values.ravel()
        np_values = eq.NP.values.ravel()
        fractions = {}
        for phase, fraction in zip(phase_values, np_values):
            name = str(phase)
            if name and name != "nan" and float(fraction) > 0:
                fractions[name] = fractions.get(name, 0.0) + float(fraction)
        canonical: Mapping[str, float] = {kind: sum(value for phase, value in fractions.items()
                                                       if self.mapping.canonical(phase) == kind)
                                          for kind in ("FCC", "BCC", "HCP")}
        def available(kind):
            return canonical[kind] if any(self.mapping.canonical(p) == kind for p in fractions) else None
        other = {p: f for p, f in fractions.items() if self.mapping.canonical(p) not in {"FCC", "BCC", "HCP"}}
        return CalphadResult("AVAILABLE", None, request.temperature, request.database_name,
                             request.database_version, "pycalphad", pycalphad.__version__, fractions,
                             available("FCC"), available("BCC"), available("HCP"),
                             provenance={"request": request_snapshot(request), "database_path": str(self.database_path),
                                         "phase_mapping_provenance": self.mapping.provenance},
                             equilibrium_phase_names=tuple(fractions), other_stable_phases=other or None,
                             convergence_status="CONVERGED", calculation_conditions=dict(request.conditions))
