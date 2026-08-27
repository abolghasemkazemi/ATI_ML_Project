# Dataset Readiness V12

## A. Controlled feature-schema design

**Yes, structurally, with gates.** The 51-condition experimental index is replacement-aware and domain-separated, and every existing field has a preliminary leakage category. Schema design must remain restricted to source-preserved fields and must not imply predictor eligibility.

## B. Final ML training

**No.** Target completeness, class balance, paper/material dependence, provenance gaps, source-unavailable papers, sparse physics descriptors, and unresolved leakage policy remain material blockers.

## C. Strongest first target

TRIP has the largest usable coverage (32/51), versus TWIP (30/51) and joint (27/51). This is only a relative support ranking—not evidence that TRIP is adequate for modelling.

## D–F. Blockers and risks

Scientific blockers: unresolved mechanism labels, incomplete verified source recovery, sparse measured chemistry/initial microstructure/experimental SFE/DeltaG, and heterogeneous mechanism evidence. Statistical blockers: small effective sample size, class imbalance, and paper/material-family dependence. Leakage risks: all post-loading mechanism and mechanical outcomes, stage observations, model-derived loading quantities, and computational-only descriptors.

## G. Work required before ML

Resolve prioritized source/target/provenance gaps; acquire P018/P019 full sources; freeze target semantics; define a pre-test/test-condition-only candidate schema; specify paper/material leakage groups and evaluation design; then reassess support and class balance without imputation or synthetic samples.
