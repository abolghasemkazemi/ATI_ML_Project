# Target definition audit

> No target was changed by this audit. Questionable cases remain queued for source review.

## Operational definition

- **TRIP=1** must mean deformation-induced martensitic transformation observed or explicitly modelled for the specified mechanical condition; initial/pre-existing martensite, processing-induced transformation, and phase reversion alone do not qualify.
- **TWIP=1** must mean deformation twinning during the specified condition; initial, annealing, or pre-existing twins alone do not qualify.

## Questionable cases

- **P001 / P001_C01** — TRIP=1, TWIP=0; Stacking-faulting dominated; sluggish/suppressed martensitic transformation. Check Abstract; Methods; Table 1; Figs. 4-13.
- **P001 / P001_C02** — TRIP=1, TWIP=0; Stacking-faulting dominated; sluggish/suppressed martensitic transformation. Check Abstract; Methods; Table 1; Figs. 4-13.
- **P001 / P001_C03** — TRIP=1, TWIP=0; Stacking-faulting dominated; sluggish/suppressed martensitic transformation. Check Abstract; Methods; Table 1; Figs. 4-13.
- **P002 / P002_C03** — TRIP=0, TWIP=0; TRIP/TWIP hindered; limited dislocation slip dominates due to high non-recrystallized zone fraction. Check Abstract; Methods; Fig. 1-6; mechanical-property discussion.
- **P002 / P002_C04** — TRIP=NA, TWIP=NA; mechanism missing. Check Medium.
- **P002 / P002_C05** — TRIP=NA, TWIP=NA; mechanism missing. Check the original paper.
- **P003 / P003_C01** — TRIP=1, TWIP=1; quasi-static: martensitic transformation dominant; TRIP+TWIP+B-TRIP. Check Abstract; Methods; Figs. 1-7; Table 1; discussion.
- **P003 / P003_C02** — TRIP=NA, TWIP=NA; tested strain-rate condition; exact properties require digitization from Fig. 2/Table 1. Check Abstract; Methods; Figs. 1-7; Table 1; discussion.
- **P003 / P003_C03** — TRIP=NA, TWIP=NA; tested strain-rate condition; exact properties require digitization from Fig. 2/Table 1. Check Abstract; Methods; Figs. 1-7; Table 1; discussion.
- **P003 / P003_C04** — TRIP=1, TWIP=1; transition state; TRIP/TWIP mixed. Check Abstract; Methods; Figs. 1-7; Table 1; discussion.
- **P003 / P003_C05** — TRIP=NA, TWIP=NA; tested strain-rate condition; exact properties require digitization from Fig. 2/Table 1. Check Abstract; Methods; Figs. 1-7; Table 1; discussion.
- **P003 / P003_C06** — TRIP=NA, TWIP=NA; tested strain-rate condition; exact properties require digitization from Fig. 2/Table 1. Check Abstract; Methods; Figs. 1-7; Table 1; discussion.
- **P003 / P003_C07** — TRIP=1, TWIP=1; dynamic: low-strain TRIP then TWIP-dominant; reverse HCP→FCC. Check Abstract; Methods; Figs. 1-7; Table 1; discussion.
- **P004 / P004_C01** — TRIP=1, TWIP=0; planar slip + early TRIP; HCP forms. Check Yes.
- **P004 / P004_C02** — TRIP=1, TWIP=0; TRIP; HCP lath thickening; first WHR peak. Check Yes.
- **P004 / P004_C03** — TRIP=1, TWIP=1; TWIP initiation in untransformed FCC + partial HCP→FCC reversion. Check Yes.
- **P004 / P004_C04** — TRIP=1, TWIP=1; twin-twin interaction + grain fragmentation + partial reversion. Check Yes.
- **P004 / P004_C05** — TRIP=1, TWIP=1; TRIP + TWIP + reversion; HCP laths partially thicken but overall fraction decreases. Check Yes.
- **P004 / P004_C06** — TRIP=1, TWIP=1; HCP fraction rises again at final strain; new martensite variants mostly from grain boundaries. Check Yes.
- **P005 / P005_C01** — TRIP=0, TWIP=0; Planar dislocation slip; increased dislocation density; pile-ups at grain boundaries. Check Yes.
- **P005 / P005_C02** — TRIP=1, TWIP=1; High density stacking faults; extrinsic/intrinsic fault pairs; 3-layer twin embryos; 4/6/8-layer HCP lamellae. Check Yes.
- **P005 / P005_C03** — TRIP=1, TWIP=1; Numerous thin deformation twins; multiple twin systems in grains; HCP-twin overlap observed. Check Yes.
- **P006 / P006_C01** — TRIP=NA, TWIP=NA; Reference equiatomic alloy; label not forced. Check Figs. 1-3; abstract/conclusions.
- **P007 / P007_C03** — TRIP=NA, TWIP=NA; Mechanism transition; exact class to verify. Check Table 3; Figs. 3,5-10; conclusions.
- **P007 / P007_C04** — TRIP=1, TWIP=NA; Multi-variant ε + reverse transformation + sequential transformation. Check Table 3; Figs. 3,5-10; conclusions.
- **P007 / P007_C05** — TRIP=1, TWIP=NA; Multi-variant ε + reverse transformation + sequential transformation. Check Table 3; Figs. 3,5-10; conclusions.
- **P008 / P008_C01** — TRIP=1, TWIP=NA; Martensitic-transformation-dominant base alloy. Check Abstract + methods + mechanism comparison.
- **P008 / P008_C02** — TRIP=0, TWIP=1; Twinning-dominant; martensitic transformation suppressed. Check Abstract; methods; deformation microstructure section.
- **P010 / P010_C01** — TRIP=1, TWIP=1; TRIP with twin-like planar defects / mixed low-SFE deformation. Check Abstract; Figs. 1-5; Summary and Conclusions.
- **P010 / P010_C03** — TRIP=0, TWIP=0; Stable FCC / planar-slip-dominant relative to designed TRIP/TWIP alloys. Check Abstract; Figs. 1-5; Summary and Conclusions.
- **P009 / P009_C01** — TRIP=1, TWIP=0; TRIP. Check Wang et al. 2022, Fig. 5 and design/validation results.
- **P009 / P009_C02** — TRIP=0, TWIP=1; TWIP. Check Wang et al. 2022, Fig. 5 and design/validation results.
- **P009 / P009_C03** — TRIP=0, TWIP=1; TWIP. Check Wang et al. 2022, Fig. 5 and design/validation results.
- **P009 / P009_C04** — TRIP=0, TWIP=1; TWIP. Check Wang et al. 2022, Fig. 5 and design/validation results.
- **P009 / P009_C05** — TRIP=1, TWIP=0; TRIP. Check Wang et al. 2022, Fig. 5 and design/validation results.
- **P009 / P009_C06** — TRIP=1, TWIP=0; TRIP. Check Wang et al. 2022, Fig. 5 and design/validation results.
- **P009 / P009_C07** — TRIP=1, TWIP=0; TRIP. Check Wang et al. 2022, Fig. 5 and design/validation results.
- **P011 / P011_C05** — TRIP=1, TWIP=0; Enhanced TRIP; dislocation slip; no mechanical twinning. Check Abstract; tensile-temperature comparison.
- **P012 / P012_C02** — TRIP=1, TWIP=1; Cryogenic TRIP/TWIP; strain-induced martensite favored. Check Abstract; experimental sections; Table 2/strain-dependent results.
- **P012 / P012_C04** — TRIP=1, TWIP=1; Synergistic TWIP + TRIP; exceptional strength/ductility. Check Abstract; experimental sections; Table 2/strain-dependent results.
- **P013 / P013_C02** — TRIP=1, TWIP=1; Stage-resolved load accommodation from SXRD; TRIP/TWIP/slip contributions evolve with stress.. Check Abstract; Materials and methods; four-stage SXRD results.
- **P013 / P013_C03** — TRIP=1, TWIP=1; Stage-resolved load accommodation from SXRD; TRIP/TWIP/slip contributions evolve with stress.. Check Abstract; Materials and methods; four-stage SXRD results.
- **P013 / P013_C04** — TRIP=1, TWIP=1; Stage-resolved load accommodation from SXRD; TRIP/TWIP/slip contributions evolve with stress.. Check Abstract; Materials and methods; four-stage SXRD results.
- **P013 / P013_C05** — TRIP=1, TWIP=1; Stage-resolved load accommodation from SXRD; TRIP/TWIP/slip contributions evolve with stress.. Check Abstract; Materials and methods; four-stage SXRD results.
- **P014 / P014_C01** — TRIP=1, TWIP=1; Microstructure reference state. Check Processing; microstructure; tensile and strengthening/deformation-mechanism sections.
- **P014 / P014_C02** — TRIP=1, TWIP=1; Microstructure reference state. Check Processing; microstructure; tensile and strengthening/deformation-mechanism sections.
- **P014 / P014_C03** — TRIP=1, TWIP=1; FCC→HCP transformation + deformation twins + HDI strengthening/strain hardening. Check Processing; microstructure; tensile and strengthening/deformation-mechanism sections.
- **P014 / P014_C04** — TRIP=1, TWIP=1; FCC→HCP transformation + deformation twins + HDI strengthening/strain hardening. Check Processing; microstructure; tensile and strengthening/deformation-mechanism sections.
- **P014 / P014_C05** — TRIP=1, TWIP=1; FCC→HCP transformation + deformation twins + HDI strengthening/strain hardening. Check Processing; microstructure; tensile and strengthening/deformation-mechanism sections.
- **P015 / P015_C01** — TRIP=0, TWIP=1; TWIP-dominant; deformation bands/HDDWs and nanotwins. Check Abstract; Sections 2.1-2.4; mechanism model; conclusions.
- **P015 / P015_C02** — TRIP=1, TWIP=1; Synergistic TWIP + TRIP; secondary twins + ε-martensite. Check Abstract; Sections 2.1-2.4; mechanism model; conclusions.
- **P016 / P016_C01** — TRIP=NA, TWIP=NA; Nanograin/nanotwin strengthening; condition-specific TRIP/TWIP labels not forced. Check Acta Materialia 163 (2019) 40–54.
- **P016 / P016_C02** — TRIP=NA, TWIP=NA; Recovered parent grains + nanograins; hierarchical bimodal microstructure. Check Acta Materialia 163 (2019) 40–54.
- **P017 / P017_C01** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P017 / P017_C02** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P017 / P017_C03** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P017 / P017_C04** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P017 / P017_C05** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P017 / P017_C06** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P017 / P017_C07** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P017 / P017_C08** — TRIP=1, TWIP=1; Coupled TWIP-induced TRIP and TRIP-induced TWIP; stacking-fault/dislocation/twin evolution. Check International Journal of Plasticity 127 (2020) 102649.
- **P018 / P018_C01** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C02** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C03** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C04** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C05** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C06** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C07** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C08** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C09** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C10** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C11** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
- **P018 / P018_C12** — TRIP=1, TWIP=1; Grain-size/composition-dependent Shockley partials, stacking faults, twinning and transformation. Check International Journal of Mechanical Sciences 219 (2022) 107098.
