# ATI ML Project

Machine Learning research project for ATI.

## Overview

This repository provides a reproducible layout for the ATI scientific
machine-learning research project. It separates immutable source data,
intermediate artifacts, research notebooks, reusable Python code, model
artifacts, evaluation outputs, figures, and research documentation.

The repository currently contains project scaffolding only. No data analysis,
feature engineering, model implementation, model training, or research results
are included at this stage.

## Project structure

```text
ATI_ML_Project/
├── configs/                 # Version-controlled experiment configuration
├── data/
│   ├── raw/                 # Original, immutable input data
│   ├── interim/             # Intermediate transformed data
│   ├── processed/           # Analysis-ready data
│   └── external/            # Data obtained from external sources
├── docs/
│   ├── methodology/         # Methodological decisions and protocols
│   ├── dataset_notes/       # Dataset provenance and data dictionaries
│   └── paper_notes/         # Manuscript and publication notes
├── figures/
│   ├── exploratory/         # Exploratory visualizations
│   ├── model_performance/   # Model evaluation visualizations
│   ├── explainability/      # Model interpretation visualizations
│   └── publication/         # Publication-ready figures
├── models/
│   ├── trained/             # Final serialized model artifacts
│   └── checkpoints/         # Training checkpoints
├── notebooks/
│   ├── 01_data_inspection/  # Initial data review
│   ├── 02_data_cleaning/    # Cleaning workflow
│   ├── 03_feature_engineering/
│   ├── 04_modeling/
│   └── 05_interpretability/
├── results/
│   ├── metrics/             # Evaluation metrics
│   ├── predictions/         # Model predictions
│   ├── tables/              # Generated result tables
│   └── logs/                # Experiment logs
├── scripts/                 # Reproducible command-line workflows
├── src/
│   ├── data/                # Data loading and processing code
│   ├── features/            # Feature generation code
│   ├── models/              # Model definitions and training code
│   ├── evaluation/          # Evaluation code
│   └── utils/               # Shared utilities
└── tests/                   # Automated tests
```

Empty directories contain `.gitkeep` placeholders so that the intended layout
is available in a fresh clone. Generated datasets, model artifacts, results,
and figures are excluded from version control by default.

## Environment setup

Use a dedicated virtual environment and install the intentionally small core
scientific Python stack:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Record the Python version and any dependency changes used for each experiment.
When the research workflow is implemented, configuration files, random seeds,
data provenance, and the exact commands required to reproduce each result
should be committed alongside the code.

## Data and artifact policy

- Treat files in `data/raw/` as immutable source material.
- Do not commit datasets, credentials, serialized models, generated results, or
  generated figures. The directory placeholders are explicitly retained.
- Document dataset provenance and access requirements in `docs/dataset_notes/`.
- Promote data from `interim` to `processed` only through reproducible scripts.
- Keep exploratory work in notebooks and move reusable logic into `src/`.
- Store experiment parameters in `configs/` and keep generated logs in
  `results/logs/`.

## Research status

Initial repository structure only; machine-learning analysis has not begun.
