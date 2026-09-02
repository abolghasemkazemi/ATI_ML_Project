# Elemental-property layer

## Scope and current scientific status

`src/reference_data` supplies a fail-closed property record, lookup result,
status vocabulary, and versioned logical table. It is integrated with the MVP's
weight-to-atomic conversion, VEC, atomic-size mismatch, and electronegativity
difference calculations. Every property-dependent successful output embeds the
table identity/version and complete contributing records; unsuccessful outputs
retain available records and explain what is absent or incompatible.

No production elemental values were added. The repository's pre-existing
header-only external table is not evidence, and no authoritative property
dataset was otherwise available locally. Therefore the production reference
area remains deliberately unpopulated and production calculations remain
unresolved until source qualification is completed.

## Definitions and consistency gates

* **Atomic weight:** used in `x_i=(w_i/M_i)/sum(w_j/M_j)`. A usable record must
  identify whether `M_i` is a standard, conventional/abridged, isotope, or other
  mass quantity and provide its unit and source version. Missing or unverified
  weights stop conversion.
* **VEC:** `sum(x_i VEC_i)`. The repository has not yet adopted a production VEC
  dataset or counting convention. A future version must cite the scientific
  definition and explicitly describe transition-metal treatment. Group number
  is not an implicit fallback.
* **Atomic-size mismatch:**
  `100 sqrt(sum(x_i(1-r_i/r_bar)^2))`. All contributing radii must have the same
  definition/type, methodology, and unit. Metallic and covalent radii, or other
  definitions, are never silently mixed.
* **Electronegativity difference:**
  `sqrt(sum(x_i(chi_i-chi_bar)^2))`. Every value in one calculation must share
  one definition, scale (for example, Pauling only when sourced as such), and
  unit.

Ideal configurational entropy and element count remain composition-only
descriptors and do not consume elemental records.

## Status and provenance strategy

`VALID` permits calculation. `NOT_AVAILABLE` means that an element/property pair
is absent. `UNVERIFIED_SOURCE` means a record exists but has not passed the
scientific validation gate. `INCOMPATIBLE_DEFINITION` means complete validated
records cannot be combined because definitions/scales/units differ. Values from
non-`VALID` records are withheld from lookup results.

Each record stores element identity, value, unit, exact definition,
methodology/scale, source, version/date, access/reference locator, notes, and
validation status. Table version plus contributing record snapshots are emitted
with results so later table changes cannot hide what a calculation used.

## Adding properties or elements

1. Select an authoritative source appropriate to the intended definition.
2. Preserve its edition/release date and exact table/page/DOI/URL locator.
3. Add long-form records under a new version following the reference schema.
4. Independently check symbols, atomic numbers, values, units, definitions,
   scales/methods, and transcription; then set only reviewed records to `VALID`.
5. Add source-based validation tests and descriptor consistency tests. Synthetic
   tests may exercise software logic but must remain clearly labelled and outside
   `data/reference`.
6. Record the scientific decision and version in `PROJECT_GUIDE.md`.

## Limitations and unresolved choices

Authoritative atomic-weight edition/convention, radius family, VEC definition
(including transition metals), and electronegativity release/scale source still
require qualification. Mixing enthalpy, melting temperature, Omega, CALPHAD,
SFE, and other thermodynamic properties are outside this implementation. The
layer neither changes compositions/labels nor claims that a descriptor is
scientifically comparable across temperature, phase, or electronic state beyond
the metadata explicitly represented.
