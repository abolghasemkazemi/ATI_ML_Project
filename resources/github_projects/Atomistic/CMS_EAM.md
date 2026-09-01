# CMS-EAM projects

- **Project name:** CMS-EAM projects
- **GitHub URL:** https://github.com/search?q=CMS-EAM&type=repositories
- **Category:** Atomistic
- **Main purpose:** Repository-discovery reference for concentration-dependent or composition-aware EAM projects.
- **Possible relevance for FeMnCoCrN HEA TRIP/TWIP machine learning project:** May support atomistic studies of composition-dependent defect energetics, but computational outputs must remain domain-separated from experiments.
- **Priority:** Medium

## Scientific role

**Reference only.** Composition-aware interatomic-potential approaches could eventually enable sampling of local chemical environments and defect energetics at scales inaccessible to DFT. This entry is currently a discovery query, so its role is to identify candidates for later potential validation.

## Possible ML usage

**Atomistic validation; SFE prediction; feature engineering.** Any resulting quantity must carry the repository version, calculation method, inputs, units, temperature, alloy scope, and computational/experimental domain.

## Relevance to FeMnCoCrN HEA TRIP/TWIP project

A validated Fe–Mn–Co–Cr–N potential could estimate distributions of fault energies, local stability, or transformation barriers rather than a single mean value. Those computational descriptors could probe how chemical disorder influences **SFE → FCC/HCP phase stability → TRIP/TWIP propensity** and could triangulate, not replace, experiments.

## Limitations

No particular potential, training set, element coverage, or accuracy is established here. Many EAM forms do not represent magnetism, interstitial N, charge effects, or phase energetics adequately. A potential fitted to elastic or liquid properties cannot be assumed valid for faults or FCC–HCP transformations; all outputs require benchmark and domain provenance.
