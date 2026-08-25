# QC before/after and final scientific diagnosis

## Before/after

| Measure | Before | After safe QC |
|---|---:|---:|
| Rows | 98 | 98 |
| TRIP missing | 10 | 10 |
| TWIP missing | 13 | 13 |
| Unresolved row roles | 0 | 0 |
| Source batches with noncanonical fields | 2 | 2 |
| Strict singleton independent experimental groups | 13 | 13 |
| Internally label-ambiguous groups | 10 | 10 |

Safe aliases recovered `Data_role`, `Composition_basis_original`, and `Image_modalities` into the canonical row type, composition basis, and characterization fields. New scientific fields were preserved, not collapsed. There are **336 condition/field-level manual-review tasks across 18 papers** in the ranked queue.

## Final scientific diagnosis

1. The **62** mechanism-flagged rows comprise: formatting/schema **0**, genuine missing **0**, scientifically ambiguous/text-without-defensible-label **27**, computational/model **22**, and repeated-stage/summary **13**. Categories are mutually exclusive primary diagnoses; the CSV retains row-level reasoning.
2. **0 mechanism flags** can be scientifically repaired without reading papers. Safe representation/schema-alias corrections elsewhere total **129** cells.
3. **62 mechanism flags** require source review.
4. **Yes, potentially.** Existing groups combine stage-resolved rows and, in some cases, changing temperature/condition, creating artificial *group-level* conflicts even when row labels may be scientifically valid.
5. **Yes, before ML.** Use a stable parent specimen/test ID plus condition sub-ID (alloy + processing + temperature + strain rate + specimen), and a separate stage ID. Keep all stages together for splitting but do not require identical labels.
6. Existing papers can realistically recover values explicitly queued from figures/tables/supplements, especially test conditions, processing parameters, phase fractions, grain size, and mechanical properties. SFE/DeltaG must retain method and temperature provenance.
7. Features marked UNKNOWN/NOT_REPORTED can only be distinguished after paper review; if genuinely unreported, complete method-matched SFE/DeltaG, initial phase fractions, and processing/test metadata require new papers or author data—not imputation.
8. Under the deliberately strict definition of a singleton, explicitly experimental independent group: TRIP **11**, TWIP **10**, joint **10**. These are conservative usable counts, not row counts; multirow parent experiments require redesigned IDs before they can be counted correctly.
9. Collect independent deformation experiments with explicit pre-test phase/twin state and post-/in-situ mechanism evidence, prioritising TWIP-negative/TRIP-negative controls, single-positive TRIP and TWIP conditions, and verified joint-positive cases across temperature, strain rate, grain size, and processing—with complete SFE method and phase-fraction provenance.
10. **Data collection and manual source review should occur first.** A Pilot ML run is not yet scientifically justified because target semantics and independence remain unresolved; no model was trained.

Fewer rows are not treated as improvement: all 98 rows are preserved, and uncertainty remains explicit.
