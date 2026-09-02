# CALPHAD backend implementation and qualification audit

## Audit result and selected backend

The 2026-09-02 audit establishes **STATE C: no usable CALPHAD engine/database is currently available**. Thermo-Calc and its `tc_python` API are `NOT_AVAILABLE`; a legitimate Thermo-Calc licence remains `LICENSE_REQUIRED`. pycalphad is `NOT_AVAILABLE`. OpenCALPHAD is `NOT_AVAILABLE`. No `.tdb` or other qualified thermodynamic database was found in the repository or the searched system locations. The authoritative machine-readable result is `data/reference/thermodynamics/calphad_backend_registry.csv`.

Consequently, no backend is activated for production, no equilibrium calculation was run, and Fe40Mn30Co20Cr10 at.% was not submitted to a solver. It would be scientifically invalid to present a fixture result without both an installed engine and an alloy-qualified, traceable database. The existing safe `NOT_AVAILABLE` behavior remains the runtime default.

## Implemented adapter and detection layer

The engine-neutral request now retains composition and basis, temperature, pressure, selected components/phases, database identity/version, additional conditions, and caller provenance. Results distinguish absent phase outputs (`None`, serialized as `NOT_AVAILABLE` by consumers) from a calculated zero. They can retain phase names/fractions, canonical FCC/BCC/HCP fractions, other phases, Gibbs-related outputs when supported, convergence, and calculation provenance.

An optional pycalphad adapter is implemented but fails closed unless its database is explicitly `QUALIFIED_FOR_TEST` and exists. It does not ship or download a database. Backend discovery uses imports/PATH only and never claims licence availability. Database qualification requires traceable identity/version/source, required-element coverage, explicit FCC and BCC representations, and documented assessment scope. HCP coverage is recorded but is not invented as a universal requirement.

## Database inventory and qualification

No database was discovered, so the database classification is `NOT_AVAILABLE`. Supported and unsupported alloy spaces are therefore both unresolved: **no alloy composition is currently supported for CALPHAD production use**, including the preferred Fe-Mn-Co-Cr candidate. Existing literature references to commercial databases are contextual evidence, not accessible database files or licences, and were not promoted to production capability.

Future qualification must review database documentation or peer-reviewed assessment evidence—not just parse a TDB—to establish the intended multicomponent space, element interactions, and phase descriptions. A database with the requested elements and phase names but without relevant assessed higher-order systems is at most `PARTIALLY_QUALIFIED`.

## Explicit phase mapping

`PhaseMapping` binds exact database phase names to canonical `FCC`, `BCC`, or `HCP` labels together with database name/version and provenance. No global mapping is preloaded because `FCC_A1`, `BCC_A2`, and `HCP_A3` meanings must be verified against the selected database documentation. Unmapped stable phases remain named `other_stable_phases`; they are never silently discarded or coerced.

## Integration and validation status

There is no scientific integration result. `CALPHAD_Validation_Status` is **UNVALIDATED** because neither a calculation nor a traceable official example/published benchmark is available. Unit tests exercise detection, qualification gates, missing engine/database, unsupported elements, mapping, provenance, invalid combinations, and safe unavailable behavior. They are software validation only and do not validate thermodynamic predictions.

A future first calculation should use exactly one alloy only after database qualification, state a temperature tied either to a documented condition or explicitly to a general solver integration test, and compare against database documentation, an official example, or a published benchmark. Its output must remain a computational integration fixture, never experimental evidence or an ML training record.

## Temperature series and Gibbs-energy capability

The request contract supports repeated, explicit temperatures without generating a bulk dataset. A future orchestration layer may issue `T1 ... Tn` requests and preserve each independent condition/provenance record to study phase fractions and transition tendencies.

pycalphad can expose equilibrium thermodynamic quantities supported by its model/database, but this repository currently reports no Gibbs value because no calculation ran. Future FCC→HCP or FCC→BCC transformation-driving-force work must define, before computation: molar reference basis; composition constraint/partitioning assumption; temperature and pressure; magnetic/ordering state; phase models and metastable phase suppression; sign convention; and whether energies are evaluated at common bulk composition or phase-specific equilibrium compositions. Equilibrium phase Gibbs energies are not automatically martensitic transformation driving forces. Interfacial, elastic/strain, magnetic, defect, and kinetic contributions may also be required. SFE additionally needs a scientifically justified thermodynamic model and interfacial/structural terms; it is not calculated here.

## Current limitations and next requirements

1. Install a supported engine without bypassing licensing.
2. Obtain a legitimately accessible, versioned database with traceable source and licence.
3. Qualify Fe-Mn-Co-Cr (or a narrower documented alloy) and exact phase mappings from database documentation.
4. Run one condition, retain solver diagnostics, and validate it against a traceable benchmark before any production designation.
5. Keep CALPHAD descriptors separate from experimental observations and mechanism labels; do not infer SFE, Slip, TWIP, or TRIP from equilibrium output.
