# Elemental-property sources and production decisions (V1)

## Scope and review outcome

`elemental_properties_v1.csv` is a long-form, property-level provenance table for
Fe, Mn, Co, Cr, Ni, N, Al, Cu, Ti, V, Nb, Mo, W, Si, and C. Each element has one
record for each required property. A record is calculation-ready only when its
own status is `VALID`; row completeness is never inferred from another property.
V1 is usable for atomic-weight conversion, VEC, and Pauling-electronegativity
calculations for all 15 elements. The metallic-radius subset is usable for Fe,
Mn, Co, Cr, Ni, Al, Cu, Ti, V, Nb, Mo, and W. N, Si, and C radii remain
`NOT_AVAILABLE`, so an alloy containing any of these elements fails closed for
atomic-size mismatch rather than mixing radius definitions.

## Atomic weights

The source is the CIAAW **Abridged Standard Atomic Weights 2021** table
(published in 2022; DOI `10.1515/pac-2019-0603`). The CSV preserves a symmetric
standard uncertainty in `uncertainty`, or the official lower and upper endpoints
in `value_min` and `value_max`. For N, Si, and C, whose standard atomic weights
are intervals, `value` is CIAAW's published conventional abridged value (14.007,
28.085, and 12.011 respectively). This explicit deterministic convention is used
in `x_i=(w_i/M_i)/sum_j(w_j/M_j)`; the interval is not silently replaced or lost.
The conversion does not propagate natural-material isotope-abundance variation,
so applications needing sample-specific isotope composition must supply a new,
method-qualified table version.

## VEC

V1 adopts the HEA descriptor convention used by Guo et al., *Journal of Applied
Physics* 109, 103505 (2011), DOI `10.1063/1.3587228`. Transition-metal elemental
VEC is the group valence count; main-group elemental VEC is the outer-shell
`s+p` valence count. Alloy VEC is `sum_i(x_i VEC_i)`. Group number is therefore
used only where the adopted convention defines that transition-metal count; it
is not a generic periodic-table fallback. These integers are convention-defined
descriptor inputs, not measurements.

## Electronegativity

All V1 values use the **Pauling scale** as tabulated in the 97th edition
(2016–2017) of the *CRC Handbook of Chemistry and Physics*, DOI
`10.1201/9781315380476`. No Mulliken, Allen, Allred–Rochow, or other scale enters
the production table. The descriptor is the composition-weighted standard
deviation `sqrt(sum_i x_i(chi_i-chibar)^2)`.

## Radius decision

The production size descriptor uses one metallic-radius compilation: Table 3 of
Miracle and Senkov, “A critical review of high entropy alloys and related
concepts,” *Acta Materialia* 122 (2017) 448–511, DOI
`10.1016/j.actamat.2016.08.081`. Source values in nm were converted exactly to pm
by multiplication by 1000. This HEA-specific review supports the choice and a
single table avoids combining metallic, covalent, ionic, or unrelated empirical
radii. Compatible entries were validated for the 12 metallic elements listed
above. No compatible entry was established for N, Si, or C; their blank values
and `NOT_AVAILABLE` statuses are deliberate.

## Limitations

These scalar descriptors ignore oxidation state, coordination, phase, magnetic
state, temperature, pressure, and local chemical environment. A conventional
atomic weight is not necessarily a sample-specific molar mass. VEC is a
literature convention rather than a direct electronic-structure calculation.
Pauling electronegativity and tabulated metallic radii are elemental heuristics.
The table supplies no binary mixing enthalpies, CALPHAD output, SFE, or mechanism
labels. Source URLs/DOIs are locators; redistribution of underlying publications
is not implied.
