# Computational input and descriptor MVP

## Implemented capabilities

The MVP validates one alloy condition without changing any repository dataset.
Its immutable reported-composition record accepts `at.%` or `wt.%`, requires an
explicit source, rejects duplicate elements and invalid totals, and retains
processing, deformation, optional initial microstructure, and provenance.
Missing optional observations remain `None`; the pipeline does not guess them.

Atomic-percent input is represented as atomic fractions without a basis
conversion. Weight-percent input is converted only when the caller supplies a
versioned, sourced atomic-weight table; both reported and converted compositions
and the conversion formula/source are retained. Otherwise conversion is
`UNRESOLVED`.

The descriptor interface provides number of elements, VEC, ideal configurational
mixing entropy, atomic-size mismatch, and electronegativity difference. Each
result carries its formula, unit, required property, status, and provenance.
Only element count and ideal entropy can currently be evaluated from qualified
atomic fractions alone. Other descriptors resolve only with caller-supplied,
traceable elemental properties.

## Unresolved dependencies and requirements

The repository's elemental-property table remains header-only. Before production
use it needs reviewed sources and versions for atomic weight, valence electron
count convention, atomic radius definition, and electronegativity scale. No
elemental values were added by this MVP.

The engine-neutral CALPHAD contract anticipates Thermo-Calc, pycalphad, and
OpenCALPHAD. A calculation requires a qualified engine plus an alloy-system-
appropriate database with recorded name/version. Outputs accommodate equilibrium
phase fractions (including FCC/BCC/HCP where supported), Gibbs energies,
phase-stability descriptors, temperature, and engine/database provenance. With
no engine or database it returns `NOT_AVAILABLE`; it never emits placeholder
thermodynamic values.

The SFE record separates experimental and calculated values and records method,
temperature, source, uncertainty, status, and provenance. Future implementations
may ingest literature experimental SFE, thermodynamic calculations, GSFE/atomistic
results, or a scientifically justified prediction, but must retain those methods
and origins separately. The MVP performs no SFE calculation and returns
`NOT_AVAILABLE` unless a caller supplies a provenance-complete result.

## Scientific boundary

The unified record contains normalized input, descriptor records, processing,
deformation and optional microstructure, CALPHAD/SFE status, provenance, and an
explicit unresolved-field list. It neither imputes scientific values nor derives
TRIP/TWIP/Slip labels or predictions from SFE or any threshold. No ML training is
implemented. Existing raw, interim, and processed datasets and labels are outside
this pipeline and remain untouched.
