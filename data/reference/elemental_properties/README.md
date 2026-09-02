# Elemental-property reference area

## Production status: V1 usable with documented unresolved radii

`elemental_properties_v1.csv` is the controlled production table. It contains
property-level provenance and status for 15 HEA-relevant elements. See
`elemental_property_schema.md` for the contract and
`docs/elemental_property_sources.md` for source review and scientific choices.

Only `VALID` records may enter calculations. N, Si, and C metallic radii are
`NOT_AVAILABLE`; they remain blank rather than receiving a covalent, ionic, or
other incompatible substitute. A changed value, source, definition, or
convention requires a new immutable version.
