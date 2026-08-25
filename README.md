# ML-TRIP-TWIP: metastable-alloy mechanism data pipeline

## Scientific objective and status

This repository provides a reproducible, provenance-preserving pipeline for a
pilot literature dataset extracted from 19 papers (P001–P019). Its purpose is
to assess data quality and feasibility for predicting TRIP, TWIP, slip, and
related deformation mechanisms in metastable high-/medium-entropy alloys.

> **The 19-paper dataset is a pilot dataset for pipeline validation and
> feasibility assessment. It is not yet assumed to be sufficient for the final
> publication-grade ML model.** No final ML model is trained here.

## Layout

```text
data/raw/        immutable, manually supplied Excel extractions
data/interim/    canonical-schema merge, still close to literature extraction
data/processed/  traceable rows plus reproducibly derived features
data/external/   documented elemental/pair-property reference tables
notebooks/       audit and pilot-ML planning only
src/data/        merge and non-destructive validation
src/features/    explicit feature formulae
src/analysis/    audit figure generation
reports/         audit Markdown, tables, and figures
tests/           synthetic tests (no scientific-value fixtures)
```

Existing research-support directories are retained; generated data are ignored
by Git. The first workbook's extraction table is the master schema. Later
columns are mapped only on exact whitespace-cleaned names; extras are retained
per row in `Unmapped_Fields` and listed in `schema_audit.csv` for manual review.

## Reproduce the pipeline

Install `requirements.txt`, place the four named workbooks in `data/raw/`, then
run from the repository root:

```bash
python -m src.data.merge_datasets
python -m src.data.validate_dataset
python -m src.features.build_features
python -m src.analysis.dataset_audit
pytest
```

Outputs are `data/interim/master_19papers_raw.{xlsx,csv}`, QC tables and
`reports/DATA_AUDIT.md`, then
`data/processed/master_19papers_features.xlsx`. Missing values remain missing:
the scripts never replace NA with zero, infer labels, normalize composition,
or fabricate constants. Raw files remain untouched.

## Scientific safeguards

- `Paper_ID`, DOI, `Condition_ID`, `Experiment_Group_ID`, row role, and source
  workbook/sheet retain provenance. DOI consistency is audited per paper.
- Atomic-percent sums are flags, not corrections. Physically suspicious values
  and ambiguous schema/role information are sent to manual review.
- Experimental, CALPHAD, DFT, MD, and other computational rows remain
  distinguishable. Computational rows are not automatically counted as
  independent experimental evidence, and SFE methods/sources must remain
  separate. No empirical SFE estimate is made.
- Multiple strain stages sharing `Experiment_Group_ID` are correlated. Future
  validation must use `GroupKFold` or feasible `StratifiedGroupKFold` by that
  field, and Leave-One-Paper-Out by `Paper_ID`; random row splitting is
  prohibited.
- Element and binary-enthalpy constants require references. Any unavailable
  input propagates NA to the derived feature.

The audit notebook explores coverage and distributions only. The planning
notebook documents candidate features/targets, class balance, missing data, row
separation, and grouped validation without fitting a model.
