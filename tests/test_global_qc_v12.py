from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
REPORTS = ROOT / "reports"
SOURCE = DATA / "master_19papers_recovery_v11.csv"
MASTER = DATA / "master_19papers_recovery_v12_qc.csv"
EXP = DATA / "experimental_condition_index_v12.csv"
COMP = DATA / "computational_condition_index_v12.csv"


def load(path):
    return pd.read_csv(path, low_memory=False)


def test_source_and_qc_master_are_row_and_cell_preserved():
    source, master = load(SOURCE), load(MASTER)
    assert len(source) == len(master) == 192
    pd.testing.assert_frame_equal(master[source.columns], source, check_dtype=False)
    assert master[source.columns].isna().equals(source.isna())
    assert set(master.columns) - set(source.columns) == {
        "QC_Row_Role", "QC_Experimental_Eligibility", "QC_Computational_Eligibility",
        "QC_Target_Eligibility", "QC_Duplicate_Status", "QC_Leakage_Risk",
        "QC_Leakage_Category", "QC_Source_Completeness", "QC_Review_Status",
    }


def test_replacement_aware_experimental_index_and_targets():
    exp = load(EXP)
    assert len(exp) == 51
    assert exp.ML_Condition_ID.notna().all() and exp.ML_Condition_ID.is_unique
    assert exp.Independent_ML_sample.eq(True).all()
    assert exp.Effective_TRIP.notna().sum() == 32
    assert exp.Effective_TWIP.notna().sum() == 30
    assert exp[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum() == 27
    assert not set(exp.Paper_ID) & {"P017", "P018", "P019"}


def test_stages_computational_and_legacy_never_enter_experimental_index():
    master, exp = load(MASTER), load(EXP)
    selected = set(exp.ML_Condition_ID)
    stages = master[master.QC_Row_Role.eq("EXPERIMENTAL_STAGE_CHILD")]
    assert stages.QC_Experimental_Eligibility.eq("NOT_ELIGIBLE").all()
    assert not set(stages.Observation_ID.dropna()) & set(exp.ML_Condition_ID)
    assert master.loc[master.QC_Row_Role.str.startswith("LEGACY"), "QC_Experimental_Eligibility"].eq("NOT_ELIGIBLE").all()
    assert selected == set(master.loc[master.QC_Row_Role.eq("EXPERIMENTAL_PRIMARY_CONDITION"), "ML_Condition_ID"])


def test_p017_exact_computational_domain_is_isolated():
    comp, exp, master = load(COMP), load(EXP), load(MASTER)
    assert len(comp) == 12 and set(comp.Paper_ID) == {"P017"}
    assert comp.Independent_Computational_Condition.eq(True).all()
    assert comp.Experimental_Target_Eligibility.eq("NOT_ELIGIBLE_FOR_EXPERIMENTAL_TARGET_POOL").all()
    assert not set(comp.Computational_Condition_ID) & set(exp.ML_Condition_ID)
    p17 = master[master.QC_Row_Role.eq("COMPUTATIONAL_PRIMARY_CONDITION")]
    assert p17.Effective_TRIP.isna().all() and p17.Effective_TWIP.isna().all()


def test_na_and_established_target_semantics_are_preserved():
    source, master = load(SOURCE), load(MASTER)
    for target in ["TRIP", "TWIP", "Original_TRIP", "Original_TWIP", "Effective_TRIP", "Effective_TWIP"]:
        pd.testing.assert_series_equal(master[target], source[target], check_dtype=False)
    # Processing mechanisms are kept separate from tensile targets.
    cr = master[master.ML_Condition_ID.eq("P014_MC_CR")].iloc[-1]
    assert cr.Processing_TRIP == 1 and cr.Processing_TWIP == 1
    assert pd.isna(cr.Effective_TRIP) and pd.isna(cr.Effective_TWIP)
    # Initial twins do not automatically establish TWIP.
    a9 = master[master.ML_Condition_ID.eq("P011_MC_A9_298K")].iloc[-1]
    assert pd.notna(a9.Initial_Twin_Type) and pd.isna(a9.Effective_TWIP)
    # P013 thermal/pre-existing HCP remains an initial-state field; its positive
    # target is retained only with separate deformation evidence.
    p13 = master[master.ML_Condition_ID.eq("P013_MC_ASCAST_RT")].iloc[-1]
    assert "thermal" in str(p13.Initial_HCP_Origin).lower() and p13.Effective_TRIP == 1
    assert pd.notna(p13.Nearest_SXRD_TRIP_Onset_Stress_MPa)


def test_no_imputation_normalization_or_new_metallurgical_descriptors():
    source, master = load(SOURCE), load(MASTER)
    forbidden = ["VEC", "Omega", "Mixing_Entropy", "Entropy_of_Mixing", "Enthalpy_of_Mixing",
                 "Atomic_Size_Mismatch", "Electronegativity_Descriptor", "Normalized_Composition"]
    assert not any(any(token.lower() in col.lower() for token in forbidden) for col in set(master.columns) - set(source.columns))
    pd.testing.assert_frame_equal(master[source.columns], source, check_dtype=False)


def test_method_specific_sfe_and_experimental_coverage():
    sfe = load(REPORTS / "SFE_METHOD_AUDIT_V12.csv")
    p17 = sfe[sfe.Paper_ID.eq("P017")]
    assert set(p17.loc[p17.SFE_Type.eq("Stable_SFE_gamma_sf"), "Value"]) == {-14, -27}
    assert set(p17.loc[p17.SFE_Type.eq("Unstable_SFE_gamma_usf"), "Value"]) == {579, 610}
    assert p17.Eligibility_Status.eq("NOT_EXPERIMENTAL_SFE").all()
    p15 = sfe[(sfe.Paper_ID.eq("P015")) & sfe.Value.isin([36.62, 10.97])]
    assert len(p15) >= 2 and p15.Eligibility_Status.eq("NOT_EXPERIMENTAL_SFE").all()
    assert not p15.Method.str.contains(r"\bTEM\b", case=False, regex=True).any()
    p8 = sfe[(sfe.Paper_ID.eq("P008")) & sfe.Value.eq(26)]
    assert len(p8) == 3 and p8.Eligibility_Status.eq("EXPERIMENTAL_COVERAGE_ELIGIBLE").all()
    p16 = sfe[(sfe.Paper_ID.eq("P016")) & sfe.SFE_Type.eq("ASSUMED_REFERENCE_INPUT")]
    assert len(p16) == 2 and p16.Eligibility_Status.eq("NOT_EXPERIMENTAL_SFE").all()
    summary = load(REPORTS / "FEATURE_COVERAGE_SUMMARY_V12.csv").set_index("Feature_Name")
    assert summary.loc["Experimental_SFE", "NonMissing_Count"] == 6
    assert summary.loc["Experimental_SFE", "Computational_Count"] == 0
    assert summary.loc["Loading_mode", "NonMissing_Count"] == 0
    assert summary.loc["GOS", "NonMissing_Count"] == 0


def test_leakage_classification_covers_post_test_and_mechanical_fields():
    leak = load(REPORTS / "FEATURE_LEAKAGE_CLASSIFICATION_V12.csv").set_index("Feature_Name")
    assert leak.loc["Original_Composition", "Leakage_Category"] == "PRE_TEST_SAFE"
    assert leak.loc["Test_T_K", "Leakage_Category"] == "TEST_CONDITION_SAFE"
    assert leak.loc["Postfracture_HCP_fraction", "Leakage_Category"] == "POST_TEST_MECHANISM_EVIDENCE"
    for field in ["YS_MPa", "UTS_MPa", "Elongation_pct", "Uniform_elongation_pct", "True_UTS_MPa", "Fracture_Mode"]:
        assert leak.loc[field, "Leakage_Category"] == "POST_TEST_MECHANICAL_OUTCOME"
        assert leak.loc[field, "Predictor_Eligibility"] == "PREDICTOR_ELIGIBILITY_UNRESOLVED"
    assert leak.loc["HDI_Hardening", "Leakage_Category"] == "MODEL_DERIVED_FROM_LOADING"
    assert leak.loc["SIS_PSR_GPa", "Leakage_Category"] == "COMPUTATIONAL_ONLY"


def test_provenance_gaps_and_source_unavailable_papers_are_reported_not_filled():
    source, master = load(SOURCE), load(MASTER)
    provenance = load(REPORTS / "PROVENANCE_COMPLETENESS_V12.csv")
    assert set(provenance.Provenance_Status) <= {"COMPLETE", "PARTIAL", "MISSING"}
    assert (provenance.Provenance_Status != "COMPLETE").any()
    papers = load(REPORTS / "PAPER_CONTRIBUTION_V12.csv").set_index("Paper_ID")
    for paper in ["P018", "P019"]:
        assert papers.loc[paper, "Source_Availability"] == "SOURCE_UNAVAILABLE_PENDING_REVIEW"
        assert papers.loc[paper, "Independent_Experimental_Conditions"] == 0
        assert papers.loc[paper, "Independent_Computational_Conditions"] == 0
        source_rows = source.Paper_ID.eq(paper)
        pd.testing.assert_frame_equal(
            master.loc[source_rows, source.columns].reset_index(drop=True),
            source.loc[source_rows].reset_index(drop=True),
            check_dtype=False,
        )


def test_global_report_states_the_preserved_source_width():
    source, master = load(SOURCE), load(MASTER)
    report = (REPORTS / "GLOBAL_DATASET_QC_V12.md").read_text(encoding="utf-8")
    assert len(source.columns) == 334
    assert len(master.columns) == len(source.columns) + 9 == 343
    assert "original 334-column scientific content is cell-preserved" in report


def test_legacy_mapping_prevents_double_counting():
    audit = load(REPORTS / "LEGACY_REPLACEMENT_AUDIT_V12.csv")
    exact = audit[audit.Exact_Row_Present.eq(True)]
    assert exact.Legacy_Row_Preserved.eq(True).all()
    assert exact.Independent_Count_Source.eq("EXACT_RECORD").all()
    assert exact.Double_Count_Risk.eq("CONTROLLED_EXCLUDED").all()


def test_computational_domain_audit_is_derived_and_passes():
    audit = load(REPORTS / "COMPUTATIONAL_DOMAIN_AUDIT_V12.csv")
    assert audit.Status.str.startswith("PASS").all()
    assert audit.set_index("Audit_Check").loc["P017_exact_computational_conditions", "Observed"] == 12
    for paper in ["P018", "P019"]:
        row = audit.set_index("Audit_Check").loc[f"{paper}_verified_promotions"]
        assert row.Observed == row.Expected == 0


def test_all_required_global_qc_reports_exist():
    names = [
        "INDEPENDENCE_AUDIT_V12.csv", "TARGET_INTEGRITY_AUDIT_V12.csv", "TARGET_COVERAGE_V12.csv",
        "PAPER_CONTRIBUTION_V12.csv", "FEATURE_COVERAGE_V12.csv", "FEATURE_COVERAGE_SUMMARY_V12.csv",
        "SFE_METHOD_AUDIT_V12.csv", "DELTAG_AUDIT_V12.csv", "COMPOSITION_AUDIT_V12.csv",
        "INITIAL_MICROSTRUCTURE_AUDIT_V12.csv", "FEATURE_LEAKAGE_CLASSIFICATION_V12.csv",
        "PROVENANCE_COMPLETENESS_V12.csv", "LEGACY_REPLACEMENT_AUDIT_V12.csv",
        "COMPUTATIONAL_DOMAIN_AUDIT_V12.csv", "EXPERIMENTAL_MISSINGNESS_V12.csv",
        "CONDITION_QC_TIER_V12.csv", "GLOBAL_QC_ISSUES_V12.csv", "DATASET_READINESS_V12.md",
        "GLOBAL_DATASET_QC_V12.md",
    ]
    for name in names:
        path = REPORTS / name
        assert path.exists() and path.stat().st_size > 0, name
