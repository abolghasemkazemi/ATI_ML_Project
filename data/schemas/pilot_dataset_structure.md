# Pilot dataset structure

## Scope

This document defines the empty intake and extraction infrastructure for a
validated pilot dataset in the General HEA Deformation Mechanism Prediction
Framework. It is a prospective contract, not a populated dataset. No paper,
extracted record, mechanism label, scientific value, calculation, or model is
created by this structure.

## 1. Dataset organization

The pilot uses four layers:

1. `data/raw/papers/` stores immutable, locally obtained source documents.
2. `data/manifests/paper_manifest.csv` is the paper-level intake and scope
   register. `extraction_status.csv` records workflow progress without storing
   scientific results.
3. Condition- and observation-level extraction workbooks will be created only
   after a paper is admitted and reviewed. Each must conform to the applicable
   project schema and retain raw representations.
4. `data/processed/` holds validated, versioned, provenance-linked outputs. A
   processed file never replaces its raw source or an earlier version.

`Paper_ID` is the stable source identifier. Each paper can describe multiple
alloys, processing routes, test conditions, specimens, replicates, or
deformation stages. Future records therefore require, at minimum,
`Study_Series_ID`, `Material_Parent_ID`, `Condition_ID`, and `Observation_ID` in
addition to `Paper_ID`. `Physical_Batch_ID`, `Replicate_ID`,
`Parent_Experiment_ID`, and `Deformation_Stage_ID` must be used when supported
by the source and remain missing when identity is not reported.

## 2. Relationship between raw papers and extracted records

A paper is a provenance container, not automatically one sample. One
`Paper_ID` can link to many condition records, while every extracted field must
link back to exactly one source paper and a source location. A condition is a
specific alloy/material state, processing history, initial microstructure, and
deformation-test configuration. Multiple observations may descend from the
same condition.

Repeated strain points, interrupted tests, in-situ frames, microscopy fields,
and multiple reported measurements from a shared specimen or parent experiment
are correlated observations. They retain separate `Observation_ID` values but
share their parent identifiers and are not counted as independent samples.
Reported replicate summaries likewise remain aggregate values; they never
generate pseudo-replicate rows. Independence may be asserted only with
source-supported specimen/batch/condition identity and documented review.

## 3. Data provenance tracking

Future extraction must preserve the original reported text or numeric value,
unit, basis, uncertainty, statistic type, and source location (page, section,
table, figure, or supplement). Harmonized values are additional fields linked
to the original; they do not overwrite it. Each value must record extraction
method, extractor, extraction date, review status, and any correction or
decision reference. Unknown information remains missing rather than inferred.

Paper DOI and `Paper_ID` provide source provenance. Condition and observation
identifiers provide experimental hierarchy. Computational fields additionally
require software, version, database or potential, method, input composition and
state, temperature/reference state, parameters, run identifier, and output
artifact. All transformations must be reproducible from an immutable input and
a versioned procedure.

## 4. Evidence-based labeling workflow

Mechanism labels are assigned at the eligible condition level, never merely at
paper level:

1. register the paper without assigning a label;
2. define the material, processing, initial-state, test-condition, and parent
   hierarchy;
3. extract the authors' claims and the underlying condition-specific evidence
   separately, with exact source locations;
4. classify evidence modality and strength, including phase identity and
   whether it is pre-, during-, or post-deformation;
5. adjudicate labels against the project's target definitions, retaining
   uncertainty and recording the reviewer decision; and
6. independently validate the condition, evidence, hierarchy, and label before
   dataset admission.

Absence of reporting is not evidence of mechanism absence. Initial martensite
does not establish TRIP, and annealing or initial twins do not establish TWIP.
Epsilon-TRIP, alpha-prime-TRIP, TWIP, Slip, and mixed behavior must not be
silently collapsed or relabeled. Conflicting, non-condition-specific, or weak
evidence remains unresolved. Repeated observations can strengthen evidence for
their parent condition but cannot increase independent sample support.

## 5. Experimental versus calculated descriptor separation

Experimental measurements and calculated descriptors occupy separate fields
and carry explicit origins. For example, an experimentally inferred SFE cannot
be overwritten by thermodynamic SFE, GSFE, DFT, MD, or CALPHAD output. Values
from different methods, temperatures, phases, databases, reference states, or
alloys remain separate records or method-qualified fields.

Calculated descriptors may enrich an experimentally labelled condition only
when their inputs and run provenance are recorded and their domain is
compatible. They never become experimental observations, mechanism evidence,
or substitute labels. A reported calculated value and a calculation performed
by this project must also remain distinguishable.

## 6. Version-control strategy

- Track schemas, empty manifests, validation code, and non-copyright
  documentation in Git.
- Do not commit paper PDFs or other restricted source files.
- Treat raw sources and raw extraction representations as immutable.
- Give each processed release an explicit version and record its schema,
  source-manifest snapshot, generation procedure, validation result, and
  creation date.
- Make corrections non-destructively through a new version plus a correction
  or decision ledger; never rewrite historical evidence or labels silently.
- Review manifest and schema diffs before release. Tag or checksum immutable
  inputs and generated artifacts where practical.
- Split and validate by parent study/condition groups. Never allow correlated
  observations from one parent to cross training and evaluation partitions.

The two pilot manifests contain headers only at infrastructure creation. Their
first populated revision must follow the literature-mining protocol and the
open P1/P2 scientific gates in `PROJECT_GUIDE.md`.
