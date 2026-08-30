# Global Dataset QC V17 Refresh

V17 remains the immutable scientific source: **234 rows x 584 columns**. The **234 x 596** QC snapshot preserves every original cell, row/column order, and NA-mask, then appends twelve QC-only fields. Source SHA-256: `31e2b0534ab9f36e14393392cb1f3db6fcea83033475864f23d15d735e8b2375`.

The refreshed architecture contains **69 independent experimental conditions** and **12 exact P017 computational conditions**. P017/P018/P019 contribute zero experimental training rows. Target support is TRIP 37 (33/4); TWIP 36 (31/5); joint 30.

Replacement/duplicate, target-integrity, missingness, chemistry, initial microstructure, SFE, DeltaG, provenance, domain, contribution, tier/issue, and feature-coverage audits are versioned in `reports/`. Measured bulk chemistry is preferred when valid; otherwise explicit nominal/source chemistry may be selected in analysis metadata. Local EDS is never bulk, P022 atomic ratios are not normalized, missing elements remain missing, and only exact numeric test temperature is eligible.

The main limitations are complete-case attrition, one surviving TRIP-negative M2 group, TWIP phase heterogeneity, and audited cross-paper material-family overlap.
