# Elemental-property reference area

## Production status: PENDING

- The verified elemental-property infrastructure, schema, validation rules, and
  interfaces are established.
- The production elemental-property table remains **PENDING** until
  authoritative reference values are supplied and verified.

The scientific property layer must not be marked complete while this directory
contains no authoritative production values. Synthetic records used by tests
validate software behavior only and do not change this production status.

This directory is the controlled home for elemental properties used by the HEA
descriptor pipeline. **It intentionally contains no numerical property table at
this revision:** no authoritative, citable elemental-property dataset was
available in the repository when the layer was established. The legacy
`data/external/element_properties.csv` is header-only and is not a validated
source.

Before a value can be used, add it in a versioned long-form table conforming to
`elemental_property_schema.md`, retain the source's exact definition and unit,
and mark it `VALID` only after source and transcription review. Missing and
unverified records fail closed; they are never imputed. Synthetic records belong
only in tests and must not be copied here.

Recommended filenames are `elemental_properties_vNN.csv` plus an immutable
source manifest or snapshot/checksum where licensing permits. A changed value,
definition, or source requires a new table version rather than an in-place
historical rewrite.
