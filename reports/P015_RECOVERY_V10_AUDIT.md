# P015 recovery v10 audit

## A–D. Rows, hierarchy, mappings, and target impact
- recovery_v10 has **180 rows**; all **178 recovery_v9 rows are byte-value/order preserved**, including both P015 legacy rows. Two exact experimental conditions were added: `P015_MC_298K` and `P015_MC_77K`.
- Legacy C01/C02 map by DOI, nominal chemistry, temperature, strain rate, initial phase, mechanics, SFE, and targets—not row order—to 298 K/77 K respectively. Legacy records remain preserved and replacement-excluded. Independent / usable TRIP / usable TWIP / usable joint: **49/30/28/25 before → 51/32/30/27 after**.
- Effective targets are 298 K **0/1** and 77 K **1/1** (TRIP/TWIP), with Slip=1. Original targets remain separate.

## E. Strong negative-label improvement and phase evidence
- The 298 K TRIP=0 is high-quality initial-to-final evidence: initial XRD/EBSD single FCC (HCP=0), then post-fracture XRD only FCC and EBSD stable single FCC/no HCP. At 77 K weak HCP XRD peaks, minor EBSD HCP grains, and TEM/HR-TEM/SAED/IFFT lath epsilon martensite establish TRIP=1. No exact post-fracture 77 K HCP fraction is fabricated.
- Initial FCC fraction remains NA because no numeric fraction was reported; initial HCP=0 is direct phase-absence evidence. Grain size is approximately 100 um (`APPROX_DIRECT_TEXT`), orientation random, and EDS reports no obvious segregation without becoming bulk chemistry.

## F. SFE and critical-stress physics
- Temperature-specific SFE improves to 36.62 (298 K) and 10.97 mJ/m2 (77 K), both current-paper LAMMPS MD calculations using the Daramola potential—not experiments. Gamma_SF=10.97 is a reuse of the 77 K SFE model input, not another observation; interface energy 8 mJ/m2 remains a secondary reference input.
- Model twin thresholds are 658 MPa (298 K) / 440 MPa (77 K), and martensite thresholds 745/742 MPa. They remain calculated thresholds. The 298 K predictions carry `LIMITED_VALIDITY_AT_298K` and cannot override experimental targets. At 77 K, TWIP near plastic onset and TRIP near 12% strain are `MODEL_CURVE_INFERENCE`, not direct stages. DeltaG remains NA.

## G–H. Mechanical properties and source conflict
- Engineering YS/UTS/elongation are 300/550 MPa/60% at 298 K and 608/850 MPa/35% at 77 K. Separate Table 1 true YS/UTS/HC are 300.25/888.61/1.960 and 690.33/1368.75/0.983; no reconciliation or overwrite occurred.
- Methods/body quasi-static rate 1e-3 s^-1 is canonical. The contradictory 1000 s^-1 captions (Figs.4,7,9) are retained in the source-consistency table only; no such experimental condition exists. Replicate_n=3 is aggregate metadata, with no three pseudo-rows, Replicate_ID NA, and batch NA.

## I–J. Computational domain, fracture/evidence, and decisions
- Eight MD snapshots remain only in the supporting MD table as `COMPUTATIONAL_MD`, `CORRELATED_SIM_STAGE`, non-independent; none enters the master or overrides experimental TWIP=1 at 77 K. Comparative higher 77 K KAM remains qualitative. Fracture is ductile-dimpled at 298 K and mixed dimples/cleavage at 77 K.
- The mapping and decision/correction ledger records no target conflict: legacy 0/1 and 1/1 agree with verified effective targets while exact rows strengthen provenance.

## K–L. Remaining gaps and blockers
- P015 gaps: no post-melt quantitative bulk chemistry, physical-batch or individual-replicate identity/results, exact initial FCC fraction, numeric 77 K post-fracture HCP fraction, numeric KAM means, alloy-specific DeltaG, direct experimental onset stages, or experimental SFE.
- Global P1/P2 blockers remain small/imbalanced independent support, unresolved labels in other papers, strict experimental/computational separation, sparse grain size/SFE/DeltaG/initial phase descriptors, predictor-leakage review, and empty traceable descriptor-reference constants. No ML, feature engineering, alloy-descriptor calculation, figure digitization, or scientific-value fabrication occurred.
