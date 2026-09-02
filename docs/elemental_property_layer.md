# Elemental-property layer

## Production status

Version 1 is **scientifically usable with explicit scope limitations**. The
production table is
`data/reference/elemental_properties/elemental_properties_v1.csv`; its complete
source review and methodological decisions are in
`docs/elemental_property_sources.md`. It contains 60 property-level records for
15 project-relevant elements. Atomic weights, Guo-convention VEC, and Pauling
electronegativity are validated for every element. A single HEA metallic-radius
dataset is validated for 12 elements; N, Si, and C radius records remain
`NOT_AVAILABLE`. Thus the layer remains partially pending only for size mismatch
in alloys containing those unresolved elements (and for elements outside V1).

## Runtime behavior

`ElementPropertyTable.from_csv` loads numeric values, interval endpoints,
uncertainties, definitions, source versions, locators, notes, and individual
validation statuses. `run_pipeline` loads V1 by default; callers may inject a
different versioned table. Only `VALID` values calculate. Missing and unresolved
records retain their exact status and provenance and produce no descriptor.

The supported formulas are:

* wt.% to at.%: `x_i=(w_i/M_i)/sum_j(w_j/M_j)`;
* VEC: `sum_i(x_i VEC_i)`;
* ideal entropy: `-R sum_i(x_i ln x_i)` with `R=8.31446261815324 J mol^-1 K^-1`;
* atomic-size mismatch: `100 sqrt(sum_i x_i(1-r_i/rbar)^2)`;
* electronegativity difference: `sqrt(sum_i x_i(chi_i-chibar)^2)`.

Radius calculations require identical definition, methodology, and unit across
all participating elements. Electronegativity calculations likewise require an
identical definition, scale, and unit. No fallback or cross-definition mixture
is allowed.

## Scientific integration fixture

`tests/fixtures/fe40mn30co20cr10_descriptors_v1.json` records the sole production
integration example, Fe40Mn30Co20Cr10 at.%. It is a test fixture, not literature
evidence and not part of any scientific dataset. All six requested composition
descriptors are supported by `VALID` V1 records. The pipeline intentionally does
not calculate CALPHAD, SFE, or Slip/TWIP/TRIP from this example.
