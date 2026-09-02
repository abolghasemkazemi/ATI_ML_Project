# Computational MVP Full-Test Baseline Verification

## Scope

This audit determines whether the frozen-source hash failure and the recovery-test
setup errors reported after the computational MVP were caused by that MVP. The
requested upstream commit name was `e585b64`; that object is not present in this
checkout. The repository contains the same titled task commit as
`0c8ec2340f64feb47b89a4d82cfa7a7aa4341d8d` (`Build computational MVP for HEA
descriptor pipeline`), so this audit uses that commit and its first parent
`c6a162d` as the reproducible local before/after boundary.

No expected hash, frozen scientific source, dataset, label, recovered value,
manifest, or provenance record was changed during this audit. No model was
trained.

## Commit inspection and protected-file check

The MVP commit changes only:

- `PROJECT_GUIDE.md`;
- `docs/computational_mvp.md`;
- new Python modules under `src/descriptors/`, `src/inputs/`, `src/pipeline/`,
  `src/sfe/`, and `src/thermodynamics/`; and
- `tests/test_computational_mvp.py`.

`git diff --name-status 0c8ec23^ 0c8ec23 -- data/processed tests scripts`
reports only the added MVP test. In particular, the commit changes none of the
six data files involved in the observed hash-gate failures:

| Protected source | Expected SHA-256 | Committed/observed SHA-256 |
|---|---|---|
| `data/processed/master_19papers_recovery_v12_qc.csv` | `4dec9a87c0c3f0f38a4ff676681ae0bacf09d247e7136770baf2d1eb27928406` | `b2ac9358e31c2c6dbd49a75ff7cf850e67d673fa1fe7989743d525399a7c4e49` |
| `data/processed/experimental_condition_index_v12.csv` | `2b4f9a3d1cc4e662c285b1621720d8a83819def9d74d58f76be1d1895c732467` | `08eafa8f4d119ba664a5d8aa9e1d1a4392b9ef14a8ac97815b5f25defe2e444b` |
| `data/processed/master_19papers_recovery_v13.csv` | `73c09dbc6eb72d498fb0792cda417c2207e85c74bcc56531f758dff4e8f3c59e` | `5e5f63a840671784abb493fd492e0421a6b5318422fc41e83a509ed3798247b3` |
| `data/processed/master_extended_recovery_v14.csv` | `478e085b2fef3f7ea0c5cbad4e5bcead6f22f66e32528c5410e037d7d29aa5cf` | `136c836d8934b5fe07c1dcc003e2354c93c0f92470f96e586f60a2cbb420f0d1` |
| `data/processed/master_extended_recovery_v15.csv` | `1050290af665540ed08b16202496e230e84895ca06315ef35972841bf82c4783` | `ba4aab3bdb7469b72c5f38f50736f221c1e416dcc7d2f9cbc697914162950d44` |
| `data/processed/master_extended_recovery_v16.csv` | `32b455e3cd8a34dd2d0e404613fabf296e52a05f9662a26724c1c689f4a0688f` | `4bddf99125e77fa25d8cf51fb39097ac0b30502d9880f847a768bec97772726e` |

Git tree inspection gives the six files identical blob IDs on both sides of the
MVP boundary. This is stronger than a clean working-tree comparison: the exact
committed bytes used by each revision are the same.

## Before/after full-suite reproduction

Detached worktrees were created at the MVP commit and its immediate parent, and
`python -m pytest -q` was run independently in each worktree.

| Repository state | Result | Interpretation |
|---|---|---|
| Immediately before MVP (`c6a162d`) | 1 failed, 111 passed, 93 errors | Frozen hashes were already inconsistent; recovery fixtures stopped at their source-hash gates. |
| MVP commit (`0c8ec23`) | 1 failed, 117 passed, 93 errors | The six new MVP tests account exactly for the pass-count increase. Failure/error categories and counts are unchanged. |

The single failure is
`tests/test_grouped_split_design_v1.py::test_source_datasets_are_byte_preserved_and_domain_counts_stay_frozen`.
It reports mismatches for the V12 QC master and V12 experimental-condition
index shown above.

The 93 errors are setup-gate cascades, not 93 distinct scientific discrepancies:

| Recovery suite | Error count | Gate source |
|---|---:|---|
| P002 recovery V13 | 11 | V12 QC master |
| P020 recovery V14 | 16 | recovery V13 master |
| P021 recovery V15 | 20 | extended recovery V14 master |
| P022 recovery V16 | 22 | extended recovery V15 master |
| P023 recovery V17 | 24 | extended recovery V16 master |
| **Total** | **93** | **Five mismatched source-hash gates** |

Because each module-scoped recovery fixture aborts before integration, every test
depending on that fixture is reported as an error. The output does not establish
93 independently failing recovery assertions.

## Classification

| Failure category | Classification | Evidence |
|---|---|---|
| Grouped-split frozen-source hash assertion (one failure; V12 QC master and experimental index) | **PRE_EXISTING** | It reproduces immediately before the MVP with the same expected and observed hashes; neither protected file's Git blob changes in the MVP. |
| P002 recovery V13 setup errors (11) | **PRE_EXISTING** | The pre-MVP suite reaches the same V12 source-hash assertion and reports the same 11 errors; the MVP changes neither source nor gate. |
| P020/P021/P022/P023 recovery setup errors (16/20/22/24) | **PRE_EXISTING** | The pre-MVP suite reports the same cascade and counts; every gated recovery-source blob is identical across the commit boundary. |
| Computational MVP focused tests | **INTRODUCED_BY_MVP (passing, not a failure)** | The after state has exactly six additional passes and no additional failure/error category. |
| Root cause of why committed source bytes differ from historical expected hashes | **UNRESOLVED** | Establishing whether line-ending conversion, serialization, or another earlier change produced the mismatch requires a separate history/provenance audit. Updating expected hashes without that evidence is prohibited. |

No observed failing category is classified `INTRODUCED_BY_MVP`.

## Task 8 readiness and corrective action

**Task 8 can safely proceed with respect to computational-MVP regression:** the
controlled before/after comparison rules out the MVP as the source of these hash
and recovery-gate failures. This conclusion does not convert the repository's
full-test baseline to green and does not validate any frozen source whose hash is
currently inconsistent.

Task 8 must therefore:

1. preserve every frozen source and expected hash exactly as committed;
2. avoid interpreting the 93 gated tests as successful recovery validation;
3. keep the existing scientific, provenance, label, and sample-independence
   safeguards; and
4. record the known red baseline when reporting its own tests.

No corrective change is required in the computational MVP. A separate,
provenance-led audit is genuinely required to identify the origin of the six
expected-versus-committed byte-hash inconsistencies. That audit must compare
historical blobs and generation/checkout behavior and decide which repository
artifact is authoritative. It must not update expected hashes merely to obtain a
passing suite, and it must not alter scientific content without source-backed,
reviewed justification.
