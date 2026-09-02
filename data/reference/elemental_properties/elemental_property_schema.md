# Elemental-property schema

## Long-form record contract

One row represents one property for one element. These fields are mandatory
unless explicitly noted:

| Field | Meaning |
|---|---|
| `element_symbol` | Case-sensitive chemical symbol used by the source. |
| `atomic_number` | Integer atomic number; identity metadata, not a guessed value. |
| `property_name` | Controlled name: initially `atomic_weight`, `atomic_radius`, `vec`, or `electronegativity`. |
| `value` | Numeric computational representative; blank only for a non-`VALID` record. Never an imputation. |
| `unit` | Exact unit (`dimensionless` where appropriate). |
| `definition` | Exact scientific meaning of the property. For radius, this must state metallic, covalent, or another defined type. |
| `methodology_or_scale` | Measurement/evaluation methodology; electronegativity scale; or the adopted VEC counting convention. |
| `source` | Authoritative publication or issuing organization. |
| `source_version_date` | Edition, standard version, release, or publication date. |
| `access_reference` | DOI, stable URL, report/table locator, and access date as applicable. |
| `notes` | Optional qualifications, uncertainty, interval semantics, or applicability limits. |
| `uncertainty` | Source-reported symmetric standard uncertainty, when applicable. |
| `value_min`, `value_max` | Source-reported interval endpoints, when applicable. |
| `validation_status` | `VALID`, `NOT_AVAILABLE`, `INCOMPATIBLE_DEFINITION`, or `UNVERIFIED_SOURCE`. Only `VALID` numeric records may enter calculations. |

Atomic weight records must state whether the number is a standard atomic weight,
an abridged/conventional value, an isotope mass, or another explicitly defined
quantity. Interval-valued standard atomic weights cannot be collapsed to a
single number without an adopted, cited convention.

VEC records must share one documented electron-counting definition. In
particular, transition-metal group numbers may be used only if the adopted
scientific definition explicitly says so. Atomic-radius descriptor inputs must
share definition, methodology, and unit. Electronegativity inputs must share
scale, definition, and unit. Incompatible records remain individually traceable
but cannot produce a mixed descriptor.

## Table rules

The logical key is (`element_symbol`, `property_name`); duplicate keys are
invalid within a version. Every table has a stable identifier and version.
Review must verify identity, transcription, definition, unit, source locator,
and licensing before setting `VALID`. Unknown information is represented by an
absent/unverified record, never by zero, a periodic trend, or a silent fallback.
