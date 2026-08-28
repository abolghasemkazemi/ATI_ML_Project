"""Integrate verified P022 evidence into extended recovery v16.

Dataset recovery only. The complete recovery-v15 dataset remains an immutable
prefix. Five source-defined as-cast tensile conditions and three correlated
40%-strain EBSD observations are appended. No figure digitization, chemistry
normalization, imputation, feature engineering, pseudo-replication, descriptor
calculation, or model training occurs.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_extended_recovery_v15.csv"
BOOK = (
    ROOT
    / "data/interim/manual_recovery/P022_scientific_evidence_recovery_VERIFIED.xlsx"
)
OUT = ROOT / "data/processed/master_extended_recovery_v16.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P022_RECOVERY_V16_AUDIT.md"

PAPER_ID = "P022"
DOI = "10.1007/s10853-019-04064-9"
TITLE = (
    "Excellent room temperature ductility of as-cast TRIP "
    "high-entropy alloy via Mo and C alloying"
)
JOURNAL = "Journal of Materials Science"
VOLUME = 55
ISSUE = 5
PAGES = "2239-2244"
YEAR = 2020
SERIES = "P022_SERIES01"

SOURCE_SHA256 = "1050290af665540ed08b16202496e230e84895ca06315ef35972841bf82c4783"
BOOK_SHA256 = "3fe5b691b4ef09856a55cdd37534d6d4432425bf1a16caff6102d6d1645ee599"

MATERIALS = {
    "C0": "P022_MAT_C0",
    "C2": "P022_MAT_C2",
    "C4": "P022_MAT_C4",
    "C2Mo1": "P022_MAT_C2MO1",
    "C2Mo2": "P022_MAT_C2MO2",
}
FORMULAS = {
    "C0": "Fe50Mn30Co10Cr10",
    "C2": "Fe50Mn30Co10Cr10C2",
    "C4": "Fe50Mn30Co10Cr10C4",
    "C2Mo1": "Fe50Mn30Co10Cr10C2Mo1",
    "C2Mo2": "Fe50Mn30Co10Cr10C2Mo2",
}
CONDITION_BY_ALLOY = {
    "C0": "P022_MC_C0_ASCAST_RT",
    "C2": "P022_MC_C2_ASCAST_RT",
    "C4": "P022_MC_C4_ASCAST_RT",
    "C2Mo1": "P022_MC_C2MO1_ASCAST_RT",
    "C2Mo2": "P022_MC_C2MO2_ASCAST_RT",
}
EXACT_IDS = tuple(CONDITION_BY_ALLOY.values())
PRIMARY_OBSERVATION_IDS = {
    condition_id: condition_id.replace("_MC_", "_OBS_")
    for condition_id in EXACT_IDS
}
STAGE_IDS = (
    "P022_C2_EBSD_40",
    "P022_C2MO1_EBSD_40",
    "P022_C2MO2_EBSD_40",
)
STAGE_PARENT = {
    "P022_C2_EBSD_40": CONDITION_BY_ALLOY["C2"],
    "P022_C2MO1_EBSD_40": CONDITION_BY_ALLOY["C2Mo1"],
    "P022_C2MO2_EBSD_40": CONDITION_BY_ALLOY["C2Mo2"],
}
ALLOY_BY_CONDITION = {
    condition_id: alloy for alloy, condition_id in CONDITION_BY_ALLOY.items()
}
ALLOY_BY_MATERIAL = {
    material_id: alloy for alloy, material_id in MATERIALS.items()
}

EXPECTED_TARGETS = {
    CONDITION_BY_ALLOY["C0"]: (1, pd.NA, pd.NA),
    CONDITION_BY_ALLOY["C2"]: (pd.NA, 1, pd.NA),
    CONDITION_BY_ALLOY["C4"]: (pd.NA, pd.NA, pd.NA),
    CONDITION_BY_ALLOY["C2Mo1"]: (pd.NA, 1, pd.NA),
    CONDITION_BY_ALLOY["C2Mo2"]: (pd.NA, 1, pd.NA),
}
EXPECTED_MECHANICS = {
    CONDITION_BY_ALLOY["C0"]: (pd.NA, pd.NA, pd.NA),
    CONDITION_BY_ALLOY["C2"]: (pd.NA, 600.0, 67.4),
    CONDITION_BY_ALLOY["C4"]: (pd.NA, pd.NA, pd.NA),
    CONDITION_BY_ALLOY["C2Mo1"]: (pd.NA, 658.0, 89.8),
    CONDITION_BY_ALLOY["C2Mo2"]: (pd.NA, pd.NA, pd.NA),
}

REQUIRED_SHEETS = {
    "P022_Study_Identity",
    "P022_Material_Parents",
    "P022_Conditions",
    "P022_Initial_Microstructure",
    "P022_Mechanical_Response",
    "P022_Stage_Evidence",
    "P022_Target_Evidence",
    "P022_Physics_SFE",
    "P022_Integration_Decisions",
    "P022_Provenance",
}

NEW_COLUMNS = [
    "P022_Record_Role",
    "P022_Target_Status",
    "P022_Source_Identity_Status",
    "P022_QC_Status",
    "P022_Recovery_Provenance_JSON",
    "Original_Composition_Basis",
    "Normalized_Composition_at_pct",
    "Composition_Normalization_Status",
    "Atomic_Ratio_C_Addition_Raw",
    "Atomic_Ratio_Mo_Addition_Raw",
    "Processing_State",
    "Flat_Tensile_Specimen_Dimensions_mm",
    "Strain_Rate_Status",
    "Initial_Secondary_Phase",
    "Dendrite_Morphology",
    "Sigma_Phase_Evidence_Status",
    "Initial_HCP_Target_Guardrail",
    "Paper_Native_Mechanism_Attribution",
    "Author_Attributed_Target_Evidence_Grade",
    "TRIP_to_TWIP_Negative_Safeguard",
    "Twin_Boundary_Character",
    "Twin_Population_Qualitative",
    "Twin_Fraction_Status",
    "Figure3_Digitization_Status",
    "SFE_General_Threshold_Status",
    "SFE_Qualitative_Trend",
]

MEANINGFUL_NA_PRIMARY = {
    "Physical_Batch_ID",
    "Replicate_ID",
    "Replicate_n",
    "Nominal_Composition_at_pct",
    "Normalized_Composition_at_pct",
    "Measured_Bulk_Composition",
    "Measured_Composition_at_pct",
    "Recovered_Bulk_Composition_at_pct",
    "Fe_at%",
    "Mn_at%",
    "Co_at%",
    "Cr_at%",
    "C_at%",
    "Mo_at%",
    "Homogenization_T_K",
    "Homogenization_time_h",
    "Hot_rolling_T_K",
    "Hot_rolling_reduction_pct",
    "Cold_rolling_reduction_pct",
    "Annealing_T_K",
    "Annealing_time_min",
    "Test_T_K",
    "Test_T_C",
    "Strain_rate_s-1",
    "Gauge_length_mm",
    "Gauge_width_mm",
    "Specimen_thickness_mm",
    "Initial_FCC_fraction",
    "Recovered_Initial_FCC_fraction",
    "Initial_HCP_fraction",
    "Grain_size_um",
    "Engineering_YS_MPa",
    "Engineering_UTS_MPa",
    "Engineering_Elongation_pct",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
    "SFE_mJ_m2",
    "SFE_method",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
}
MEANINGFUL_NA_STAGE = {
    "ML_Condition_ID",
    "TRIP_Stage",
    "TRIP_at_stage",
    "Twin_fraction_or_Sigma3",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
}
PROVENANCE_EXCLUDE = {
    "P022_Recovery_Provenance_JSON",
    "QC_Row_Role",
    "QC_Experimental_Eligibility",
    "QC_Computational_Eligibility",
    "QC_Target_Eligibility",
    "QC_Duplicate_Status",
    "QC_Leakage_Risk",
    "QC_Leakage_Category",
    "QC_Source_Completeness",
    "QC_Review_Status",
}
UNIT_MAP = {
    "Atomic_Ratio_C_Addition_Raw": "atomic-ratio addition",
    "Atomic_Ratio_Mo_Addition_Raw": "atomic-ratio addition",
    "Remelt_Count_Min": "minimum count",
    "Test_T_K": "K",
    "Test_T_C": "C",
    "Strain_rate_s-1": "s^-1",
    "Gauge_length_mm": "mm",
    "Gauge_width_mm": "mm",
    "Specimen_thickness_mm": "mm",
    "Initial_FCC_fraction": "fraction",
    "Initial_HCP_fraction": "fraction",
    "Recovered_Initial_FCC_fraction": "fraction",
    "Recovered_Initial_HCP_fraction": "fraction",
    "Grain_size_um": "um",
    "Engineering_YS_MPa": "MPa",
    "Engineering_UTS_MPa": "MPa",
    "Engineering_Elongation_pct": "%",
    "YS_MPa": "MPa",
    "UTS_MPa": "MPa",
    "Elongation_pct": "%",
    "UTS_mean": "MPa",
    "TE_mean": "%",
    "Reported_Ultimate_Strength_MPa": "MPa",
    "Reported_Elongation_pct": "%",
    "Effective_TRIP": "binary",
    "Effective_TWIP": "binary",
    "Recovered_TRIP": "binary",
    "Recovered_TWIP": "binary",
    "Slip": "binary",
    "Local_Strain_pct": "%",
    "Tensile_Strain_pct": "%",
    "TWIP_Stage": "binary",
    "TWIP_at_stage": "binary",
    "TRIP_Stage": "binary",
    "TRIP_at_stage": "binary",
    "Twin_fraction_or_Sigma3": "fraction",
    "SFE_mJ_m2": "mJ/m2",
    "DeltaG_FCC_HCP_J_mol": "J/mol",
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def is_present(value) -> bool:
    return pd.notna(value) and str(value).strip() not in {
        "",
        "NA",
        "N/A",
        "nan",
        "None",
    }


def clean(value):
    return value if is_present(value) else pd.NA


def json_ready(value):
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def experimental_pool(data: pd.DataFrame) -> pd.DataFrame:
    """Apply established replacement gates before condition-level counting."""
    pool = data[
        data.Data_Origin.eq("EXPERIMENTAL")
        & data.Observation_Role.eq("INDEPENDENT_CONDITION")
    ].copy()
    for paper, column, pattern in [
        ("P012", "P012_Record_Role", r"P012_C0[1-6]"),
        ("P011", "P011_Record_Role", r"P011_C0[1-5]"),
    ]:
        if column in data and data[column].eq("RECOVERED_EXACT_CONDITION").any():
            pool = pool[
                ~(
                    pool.Paper_ID.eq(paper)
                    & pool.Condition_ID.str.match(pattern, na=False)
                )
            ]
    if "P008_Record_Role" in pool:
        pool = pool[
            ~pool.P008_Record_Role.eq(
                "LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT"
            )
        ]
    for paper, column in [
        ("P013", "P013_Record_Role"),
        ("P014", "P014_Record_Role"),
        ("P015", "P015_Record_Role"),
        ("P002", "P002_Record_Role"),
    ]:
        if column in data and data[column].eq("RECOVERED_EXACT_CONDITION").any():
            pool = pool[
                ~(
                    pool.Paper_ID.eq(paper)
                    & ~pool[column].eq("RECOVERED_EXACT_CONDITION")
                )
            ]
    return pool.copy()


def counts(data: pd.DataFrame) -> tuple[int, int, int, int]:
    pool = experimental_pool(data)
    joint = pool[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1)
    return (
        len(pool),
        int(pool.Effective_TRIP.notna().sum()),
        int(pool.Effective_TWIP.notna().sum()),
        int(joint.sum()),
    )


def class_counts(data: pd.DataFrame) -> dict[str, int]:
    pool = experimental_pool(data)
    joint = pool.dropna(subset=["Effective_TRIP", "Effective_TWIP"])
    states = (
        joint.Effective_TRIP.astype(int).astype(str)
        + joint.Effective_TWIP.astype(int).astype(str)
    ).value_counts()
    return {
        "trip_positive": int(pool.Effective_TRIP.eq(1).sum()),
        "trip_negative": int(pool.Effective_TRIP.eq(0).sum()),
        "twip_positive": int(pool.Effective_TWIP.eq(1).sum()),
        "twip_negative": int(pool.Effective_TWIP.eq(0).sum()),
        "joint_00": int(states.get("00", 0)),
        "joint_10": int(states.get("10", 0)),
        "joint_01": int(states.get("01", 0)),
        "joint_11": int(states.get("11", 0)),
    }


def duplicate_rows(data: pd.DataFrame) -> pd.DataFrame:
    normalized = data.DOI.astype("string").str.strip().str.lower()
    return data[normalized.eq(DOI.lower())].copy()


def _assert_expected_value(actual, expected) -> None:
    if pd.isna(expected):
        assert pd.isna(actual)
    else:
        assert float(actual) == float(expected)


def load_and_verify() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    assert file_hash(SOURCE) == SOURCE_SHA256, (
        "recovery-v15 source changed before P022 integration"
    )
    assert file_hash(BOOK) == BOOK_SHA256, "verified P022 workbook changed"
    source = pd.read_csv(SOURCE, low_memory=False)

    conflicting_id = source[
        source.Paper_ID.eq(PAPER_ID)
        & ~source.DOI.astype("string").str.strip().str.lower().eq(DOI.lower())
    ]
    assert conflicting_id.empty, "P022 Paper_ID exists with a different DOI"
    legacy = duplicate_rows(source)
    assert legacy.empty, (
        "P022 DOI already exists; stop for explicit replacement-aware mapping"
    )
    assert not source.Paper_ID.eq(PAPER_ID).any(), "P022 already exists in v15"

    sheets = pd.read_excel(BOOK, sheet_name=None, dtype=object)
    assert set(sheets) == REQUIRED_SHEETS
    for name, frame in sheets.items():
        if "Paper_ID" in frame:
            assert set(frame.Paper_ID.dropna()) == {PAPER_ID}, name
        if "DOI" in frame:
            assert set(frame.DOI.dropna()) == {DOI}, name

    identity = sheets["P022_Study_Identity"].iloc[0]
    assert identity.Paper_ID == PAPER_ID and identity.DOI == DOI
    assert identity.Title == TITLE
    assert identity.Journal == JOURNAL
    assert int(identity.Volume) == VOLUME
    assert int(identity.Issue) == ISSUE
    assert str(identity.Pages) == PAGES
    assert int(identity.Year) == YEAR
    assert identity.Data_Origin == "EXPERIMENTAL"
    assert identity.Study_Series_ID == SERIES
    assert (
        identity.Source_Identity_Status
        == "VERIFIED_PDF_AND_EXTERNAL_BIBLIOGRAPHIC_MATCH"
    )

    parents = sheets["P022_Material_Parents"].set_index("Alloy_Label")
    assert len(parents) == 5 and set(parents.index) == set(MATERIALS)
    for alloy, material_id in MATERIALS.items():
        parent = parents.loc[alloy]
        assert parent.Material_Parent_ID == material_id
        assert parent.Original_Composition_Formula == FORMULAS[alloy]
        assert parent.Original_Composition_Basis == "atomic ratio as reported"
        assert pd.isna(parent.Normalized_at_pct)
        assert pd.isna(parent.Measured_Bulk_Composition)
        assert (
            parent.Composition_Status
            == "NOMINAL_ORIGINAL_ATOMIC_RATIO_ONLY_NO_QUANTITATIVE_"
            "POSTMELT_BULK_CHEMISTRY_REPORTED"
        )

    conditions = sheets["P022_Conditions"].set_index("ML_Condition_ID")
    assert len(conditions) == 5 and set(conditions.index) == set(EXACT_IDS)
    assert conditions.Independent_Experimental_ML_sample.eq(True).all()
    assert conditions.Study_Series_ID.eq(SERIES).all()
    assert conditions.Leakage_Group_Strict.eq(SERIES).all()
    assert conditions.Physical_Batch_ID.isna().all()
    assert conditions.Replicate_n.isna().all()
    assert conditions.Test_T_Raw.eq("room temperature").all()
    assert conditions.Test_T_K.isna().all()
    assert conditions["Strain_Rate_s-1"].isna().all()
    assert conditions.Loading_Mode.eq("Uniaxial tension").all()
    assert conditions.Specimen_Dimensions_mm.eq("22 x 2.5 x 1.5").all()
    assert conditions.Processing_State.eq("AS_CAST").all()
    assert conditions.Remelt_Count_Min.astype(float).eq(5).all()
    for alloy, condition_id in CONDITION_BY_ALLOY.items():
        condition = conditions.loc[condition_id]
        assert condition.Material_Parent_ID == MATERIALS[alloy]
        assert condition.Leakage_Group_Material == MATERIALS[alloy]
        assert condition.Original_Composition_Formula == FORMULAS[alloy]

    micro = sheets["P022_Initial_Microstructure"].set_index("ML_Condition_ID")
    assert set(micro.index) == set(EXACT_IDS)
    c0 = micro.loc[CONDITION_BY_ALLOY["C0"]]
    assert c0.Initial_Phase_State == "FCC_PLUS_HCP"
    assert pd.isna(c0.Initial_FCC_fraction)
    assert pd.isna(c0.Initial_HCP_fraction)
    for alloy in ("C2", "C4", "C2Mo1", "C2Mo2"):
        row = micro.loc[CONDITION_BY_ALLOY[alloy]]
        assert pd.isna(row.Initial_FCC_fraction)
        assert float(row.Initial_HCP_fraction) == 0.0
    c4 = micro.loc[CONDITION_BY_ALLOY["C4"]]
    assert (
        c4.Initial_Secondary_Phase
        == "CARBIDES_IN_INTERDENDRITIC_REGION_DIRECT_SEM"
    )
    assert c4.Initial_Phase_State == "XRD_SINGLE_FCC_MATRIX"

    mechanics = sheets["P022_Mechanical_Response"].set_index("ML_Condition_ID")
    assert set(mechanics.index) == set(EXACT_IDS)
    for condition_id, expected in EXPECTED_MECHANICS.items():
        actual = mechanics.loc[
            condition_id,
            ["Engineering_YS_MPa", "Engineering_UTS_MPa", "Total_Elongation_pct"],
        ]
        for value, expected_value in zip(actual, expected):
            _assert_expected_value(value, expected_value)

    stages = sheets["P022_Stage_Evidence"]
    assert len(stages) == 3 and set(stages.Observation_ID) == set(STAGE_IDS)
    assert stages.Local_Strain_pct.astype(float).eq(40).all()
    assert stages.Method.eq("EBSD/IPF + misorientation").all()
    assert stages.TWIP_Stage.astype(float).eq(1).all()
    assert stages.TRIP_Stage.isna().all()
    assert stages.Independent_ML_sample.eq(False).all()
    assert stages.Observation_Role.eq("CORRELATED_STAGE_CHILD").all()
    for stage in stages.to_dict("records"):
        assert stage["Parent_ML_Condition_ID"] == STAGE_PARENT[stage["Observation_ID"]]

    targets = sheets["P022_Target_Evidence"].set_index("ML_Condition_ID")
    assert set(targets.index) == set(EXACT_IDS)
    for condition_id, expected in EXPECTED_TARGETS.items():
        actual = targets.loc[
            condition_id, ["Effective_TRIP", "Effective_TWIP", "Slip"]
        ]
        for value, expected_value in zip(actual, expected):
            _assert_expected_value(value, expected_value)
    assert (
        targets.loc[CONDITION_BY_ALLOY["C0"], "TRIP_Evidence_Type"]
        == "AUTHOR_CONDITION_ATTRIBUTION_CROSS_REFERENCED_TO_ESTABLISHED_BASE_ALLOY"
    )
    assert targets.Negative_Evidence_Status.eq("INSUFFICIENT_FOR_ZERO").all()

    physics = sheets["P022_Physics_SFE"]
    sfe = physics[physics.Feature.eq("SFE_numeric")].iloc[0]
    assert pd.isna(sfe.Recovered_Value)
    assert sfe.Status == "NOT_REPORTED_CURRENT_ALLOY_NUMERIC"
    delta_g = physics[physics.Feature.eq("DeltaG_FCC_HCP")].iloc[0]
    assert pd.isna(delta_g.Recovered_Value)
    return source, sheets


def _row_template(columns: list[str]) -> dict:
    return {column: pd.NA for column in columns}


def _sfe_trend(alloy: str) -> str:
    if alloy in {"C2", "C4"}:
        return "C_TENDS_TO_INCREASE_SFE_QUALITATIVE_DIRECTION_ONLY"
    if alloy == "C2Mo1":
        return (
            "C2MO1_MAY_HAVE_REDUCED_SFE_FROM_COMBINED_C_MO_EFFECT_"
            "QUALITATIVE_DIRECTION_ONLY"
        )
    if alloy == "C2Mo2":
        return (
            "C_INCREASE_AND_MO_REDUCTION_DISCUSSION_"
            "QUALITATIVE_DIRECTION_ONLY"
        )
    return "NO_CURRENT_ALLOY_NUMERIC_SFE_QUALITATIVE_REFERENCE_ONLY"


def _twin_population(alloy: str) -> object:
    if alloy == "C2Mo1":
        return "LARGEST_AMONG_C2_C2MO1_C2MO2_QUALITATIVE"
    if alloy in {"C2", "C2Mo2"}:
        return "LOWER_THAN_C2MO1_QUALITATIVE"
    return pd.NA


def _primary_source_location(alloy: str) -> str:
    if alloy in {"C2", "C2Mo1"}:
        return "Methods p.2; Figs.1-4 pp.2-5; abstract/results/conclusions"
    return "Methods p.2; Figs.1-4 pp.2-5"


def make_primary_rows(
    columns: list[str], sheets: dict[str, pd.DataFrame]
) -> list[dict]:
    parents = sheets["P022_Material_Parents"].set_index("Alloy_Label")
    conditions = sheets["P022_Conditions"].set_index("ML_Condition_ID")
    micro = sheets["P022_Initial_Microstructure"].set_index("ML_Condition_ID")
    mechanics = sheets["P022_Mechanical_Response"].set_index("ML_Condition_ID")
    targets = sheets["P022_Target_Evidence"].set_index("ML_Condition_ID")
    rows: list[dict] = []

    for condition_id in EXACT_IDS:
        alloy = ALLOY_BY_CONDITION[condition_id]
        parent = parents.loc[alloy]
        condition = conditions.loc[condition_id]
        initial = micro.loc[condition_id]
        mechanical = mechanics.loc[condition_id]
        target = targets.loc[condition_id]
        material_id = MATERIALS[alloy]
        observation_id = PRIMARY_OBSERVATION_IDS[condition_id]
        is_direct_twip = alloy in {"C2", "C2Mo1", "C2Mo2"}

        trip = clean(target.Effective_TRIP)
        twip = clean(target.Effective_TWIP)
        slip = clean(target.Slip)
        hcp = clean(initial.Initial_HCP_fraction)
        uts = clean(mechanical.Engineering_UTS_MPa)
        elongation = clean(mechanical.Total_Elongation_pct)

        row = _row_template(columns)
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Journal": JOURNAL,
                "Volume": VOLUME,
                "Issue": ISSUE,
                "Pages": PAGES,
                "Publication_Year": YEAR,
                "Source_URL": f"https://doi.org/{DOI}",
                "Condition_ID": condition_id,
                "Experiment_Group_ID": SERIES,
                "Parent_Experiment_ID": condition_id,
                "ML_Condition_ID": condition_id,
                "Parent_ML_Condition_ID": condition_id,
                "Observation_ID": observation_id,
                "Data_Origin": "EXPERIMENTAL",
                "Observation_Role": "INDEPENDENT_CONDITION",
                "Row_Type": "Primary as-cast experimental tensile condition",
                "Independent_ML_sample": True,
                "Independent_Experimental_ML_sample": True,
                "Experimental_Target_Eligibility": True,
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": material_id,
                "Physical_Batch_ID": pd.NA,
                "Replicate_ID": pd.NA,
                "Replicate_n": pd.NA,
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": material_id,
                "Grouping_Confidence": "HIGH",
                "Grouping_Review_Required": False,
                "Grouping_Reason": (
                    "Source-defined separately fabricated chemistry variant; "
                    "one primary room-temperature tensile condition"
                ),
                "P022_Record_Role": "RECOVERED_EXACT_PRIMARY_CONDITION",
                "P022_Target_Status": target.Target_Status,
                "P022_Source_Identity_Status": (
                    "VERIFIED_PDF_AND_EXTERNAL_BIBLIOGRAPHIC_MATCH"
                ),
                "P022_QC_Status": (
                    "PENDING_GLOBAL_QC_SCHEMA_SPLIT_REFRESH_AFTER_COLLECTION"
                ),
                "Alloy_ID": alloy,
                "Original_Composition": FORMULAS[alloy],
                "Original_Composition_Basis": "ATOMIC_RATIO_AS_REPORTED",
                "Composition_basis": "ATOMIC_RATIO_AS_REPORTED",
                "Nominal_Composition_at_pct": pd.NA,
                "Normalized_Composition_at_pct": pd.NA,
                "Composition_Normalization_Status": (
                    "NOT_NORMALIZED_RECOVERY_PRESERVES_ATOMIC_RATIO_FORMULA"
                ),
                "Atomic_Ratio_C_Addition_Raw": float(parent.C_Addition_Raw),
                "Atomic_Ratio_Mo_Addition_Raw": float(parent.Mo_Addition_Raw),
                "Fe_at%": pd.NA,
                "Mn_at%": pd.NA,
                "Co_at%": pd.NA,
                "Cr_at%": pd.NA,
                "C_at%": pd.NA,
                "Mo_at%": pd.NA,
                "Measured_Bulk_Composition": pd.NA,
                "Measured_Composition_at_pct": pd.NA,
                "Recovered_Bulk_Composition_at_pct": pd.NA,
                "Measured_Composition_Status": (
                    "NO_QUANTITATIVE_POSTMELT_BULK_CHEMISTRY_REPORTED"
                ),
                "Composition_Status": parent.Composition_Status,
                "Recovered_Composition_Status": parent.Composition_Status,
                "Processing_State": "AS_CAST",
                "Processing_State_ID": "AS_CAST",
                "Processing_route": (
                    "AS_CAST_ARC_MELTED_NO_REPORTED_HOMOGENIZATION_"
                    "ROLLING_OR_ANNEALING"
                ),
                "Raw_Material_Purity": ">99.9 wt.%",
                "Melting_Route": (
                    "Arc melting under Ti-gettered high-purity Ar in "
                    "water-cooled Cu crucible"
                ),
                "Cast_method": (
                    "Arc melting; Ti-gettered high-purity Ar; "
                    "water-cooled Cu crucible"
                ),
                "Casting_Route": "WATER_COOLED_CU_CRUCIBLE",
                "Remelt_Count_Min": 5,
                "Remelt_Count_Status": "AT_LEAST_FIVE",
                "Homogenization_T_K": pd.NA,
                "Homogenization_time_h": pd.NA,
                "Hot_rolling_T_K": pd.NA,
                "Hot_rolling_reduction_pct": pd.NA,
                "Cold_rolling_reduction_pct": pd.NA,
                "Annealing_T_K": pd.NA,
                "Annealing_time_min": pd.NA,
                "Cooling_route": "AS_CAST_IN_WATER_COOLED_CU_CRUCIBLE",
                "Test_T_Raw": "room temperature",
                "Test_T_K": pd.NA,
                "Test_T_C": pd.NA,
                "Test_T_Status": (
                    "SOURCE_TEXT_ROOM_TEMPERATURE_EXACT_NUMERIC_K_NOT_REPORTED"
                ),
                "Strain_rate_s-1": pd.NA,
                "Strain_Rate_Status": "NOT_REPORTED",
                "Loading_Mode": "Uniaxial tension",
                "Flat_Tensile_Specimen_Dimensions_mm": "22 x 2.5 x 1.5",
                "Gauge_length_mm": pd.NA,
                "Gauge_width_mm": pd.NA,
                "Specimen_thickness_mm": pd.NA,
                "Test_Metadata_Status": (
                    "ROOM_TEMPERATURE_RAW_ONLY_EXACT_K_AND_"
                    "TENSILE_STRAIN_RATE_NOT_REPORTED"
                ),
                "Initial_Phase": initial.Initial_Phase_State,
                "Initial_Phase_State_Qualitative": initial.Initial_Phase_State,
                "Initial_Phase_Status": "DIRECT_XRD_WITH_MICROSCOPY_CONTEXT",
                "Initial_FCC_fraction": pd.NA,
                "Recovered_Initial_FCC_fraction": pd.NA,
                "Initial_HCP_fraction": hcp,
                "Recovered_Initial_HCP_fraction": hcp,
                "Initial_HCP_Status": (
                    "PRE_EXISTING_AS_CAST_FCC_PLUS_HCP_FRACTIONS_NOT_REPORTED"
                    if alloy == "C0"
                    else "DIRECT_XRD_SINGLE_FCC_HCP_ABSENT"
                ),
                "Recovered_Initial_HCP_status": (
                    "QUALITATIVE_FCC_PLUS_HCP_NO_NUMERIC_FRACTION"
                    if alloy == "C0"
                    else "DIRECT_XRD_HCP_FRACTION_ZERO"
                ),
                "Initial_HCP_Origin": (
                    "PRE_EXISTING_AS_CAST"
                    if alloy == "C0"
                    else "NOT_PRESENT_BY_XRD"
                ),
                "Initial_TRIP_Target_Guardrail": (
                    "PRE_EXISTING_AS_CAST_HCP_DOES_NOT_GENERATE_"
                    "DEFORMATION_INDUCED_TRIP"
                ),
                "Initial_HCP_Target_Guardrail": (
                    "INITIAL_HCP_IS_NOT_DEFORMATION_INDUCED_TRIP_EVIDENCE"
                ),
                "Initial_Secondary_Phase": clean(initial.Initial_Secondary_Phase),
                "Initial_Secondary_Phase_Status": (
                    "CARBIDES_IN_INTERDENDRITIC_REGION_DIRECT_SEM"
                    if alloy == "C4"
                    else pd.NA
                ),
                "Dendrite_Morphology": initial.Dendrite_Morphology,
                "Grain_size_um": pd.NA,
                "Grain_Size_Status": initial.Grain_Size_Status,
                "Sigma_Phase_Evidence_Status": (
                    "PRIOR_WORK_POSSIBILITY_NOT_CURRENT_PAPER_MEASUREMENT"
                    if alloy == "C2Mo2"
                    else "NO_SIGMA_PHASE_VALUE_ASSIGNED"
                ),
                "C4_Carbide_XRD_Coexistence_Safeguard": (
                    "XRD_SINGLE_FCC_MATRIX_DOES_NOT_ERASE_DIRECT_SEM_CARBIDES"
                    if alloy == "C4"
                    else pd.NA
                ),
                "Engineering_YS_MPa": pd.NA,
                "Engineering_UTS_MPa": uts,
                "Engineering_Elongation_pct": elongation,
                "YS_MPa": pd.NA,
                "UTS_MPa": uts,
                "Elongation_pct": elongation,
                "YS_mean": pd.NA,
                "UTS_mean": uts,
                "TE_mean": elongation,
                "Reported_Ultimate_Strength_MPa": uts,
                "Reported_Elongation_pct": elongation,
                "Mechanical_Value_Status": mechanical.Value_Status,
                "Mechanical_Predictor_Eligibility": (
                    "MECHANICAL_OUTCOME_LEAKAGE"
                ),
                "Figure3_Digitization_Status": (
                    "NOT_DIGITIZED_TEXT_ONLY_VALUES_WHERE_EXPLICIT"
                ),
                "Strain_Basis_Status": (
                    "ENGINEERING_TENSILE_APPROXIMATE_DIRECT_TEXT"
                    if is_present(uts)
                    else "FIGURE_ONLY_NOT_DIGITIZED"
                ),
                "Original_TRIP": pd.NA,
                "Original_TWIP": pd.NA,
                "Recovered_TRIP": trip,
                "Recovered_TWIP": twip,
                "Effective_TRIP": trip,
                "Effective_TWIP": twip,
                "Slip": slip,
                "Target_Status": target.Target_Status,
                "Paper_Native_Mechanism_Attribution": clean(
                    target.Paper_Native_Mechanism_Attribution
                ),
                "TRIP_Evidence_Type": target.TRIP_Evidence_Type,
                "TWIP_Evidence_Type": target.TWIP_Evidence_Type,
                "Negative_Evidence_Status": target.Negative_Evidence_Status,
                "Condition_Level_Target_Evidence": (
                    target.Condition_Level_Evidence
                ),
                "Target_Evidence_Confidence": (
                    "MEDIUM"
                    if alloy == "C0"
                    else (
                        "HIGH_FOR_NA_DECISION"
                        if alloy == "C4"
                        else "HIGH"
                    )
                ),
                "Label_confidence": (
                    "MEDIUM"
                    if alloy == "C0"
                    else (
                        "HIGH_FOR_NA_DECISION"
                        if alloy == "C4"
                        else "HIGH"
                    )
                ),
                "Evidence_TRIP": (
                    target.Condition_Level_Evidence
                    if is_present(trip)
                    else target.TRIP_Evidence_Type
                ),
                "Evidence_TWIP": (
                    target.Condition_Level_Evidence
                    if is_present(twip)
                    else target.TWIP_Evidence_Type
                ),
                "Author_Attributed_Target_Evidence_Grade": (
                    "MEDIUM_AUTHOR_ATTRIBUTED_NOT_DIRECT_POSTTEST_PHASE_MAP"
                    if alloy == "C0"
                    else pd.NA
                ),
                "TRIP_to_TWIP_Negative_Safeguard": (
                    "MECHANISM_SHIFT_WORDING_DOES_NOT_GENERATE_TRIP_ZERO"
                ),
                "Twin_Boundary_Character": (
                    "APPROXIMATELY_60_DEGREE_<111>_"
                    "DEFORMATION_TWIN_BOUNDARIES"
                    if is_direct_twip
                    else pd.NA
                ),
                "Twin_Population_Qualitative": _twin_population(alloy),
                "Twin_Fraction_Status": (
                    "QUALITATIVE_POPULATION_ONLY_NO_FRACTION_DIGITIZED"
                    if is_direct_twip
                    else pd.NA
                ),
                "TWIP_Mode": (
                    "DEFORMATION_TWINNING_DIRECT_EBSD"
                    if is_direct_twip
                    else pd.NA
                ),
                "Characterization_methods": (
                    "XRD; OM/SEM; EBSD/IPF and misorientation at 40% strain"
                    if is_direct_twip
                    else "XRD; OM/SEM"
                ),
                "SFE_mJ_m2": pd.NA,
                "SFE_method": pd.NA,
                "SFE_Value_Status": "NOT_REPORTED_CURRENT_ALLOY_NUMERIC",
                "SFE_Data_Origin": "CURRENT_PAPER_GAP",
                "SFE_Predictor_Eligibility": (
                    "NOT_SAFE_AS_DIRECT_NUMERIC_SFE"
                ),
                "SFE_General_Threshold_Status": (
                    "SECONDARY_GENERAL_THRESHOLDS_NOT_ASSIGNED_TO_"
                    "P022_CONDITIONS"
                ),
                "SFE_Qualitative_Trend": _sfe_trend(alloy),
                "DeltaG_FCC_HCP_J_mol": pd.NA,
                "DeltaG_method": pd.NA,
                "DeltaG_Value_Status": "NOT_REPORTED",
                "DeltaG_Data_Origin": "CURRENT_PAPER_GAP",
                "Source_location": _primary_source_location(alloy),
                "Notes": target.Scientific_Justification,
            }
        )
        rows.append(row)
    return rows


def make_stage_rows(
    columns: list[str], sheets: dict[str, pd.DataFrame]
) -> list[dict]:
    stages = sheets["P022_Stage_Evidence"].set_index("Observation_ID")
    rows: list[dict] = []
    for observation_id in STAGE_IDS:
        stage = stages.loc[observation_id]
        parent_id = stage.Parent_ML_Condition_ID
        alloy = ALLOY_BY_CONDITION[parent_id]
        material_id = MATERIALS[alloy]
        row = _row_template(columns)
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Journal": JOURNAL,
                "Volume": VOLUME,
                "Issue": ISSUE,
                "Pages": PAGES,
                "Publication_Year": YEAR,
                "Source_URL": f"https://doi.org/{DOI}",
                "Condition_ID": observation_id,
                "Experiment_Group_ID": SERIES,
                "Parent_Experiment_ID": parent_id,
                "ML_Condition_ID": pd.NA,
                "Parent_ML_Condition_ID": parent_id,
                "Observation_ID": observation_id,
                "Deformation_Stage_ID": observation_id,
                "Data_Origin": "EXPERIMENTAL",
                "Observation_Role": "CORRELATED_STAGE_CHILD",
                "Row_Type": "Correlated 40%-strain EBSD twin observation",
                "Independent_ML_sample": False,
                "Independent_Experimental_ML_sample": False,
                "Experimental_Target_Eligibility": False,
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": material_id,
                "Physical_Batch_ID": pd.NA,
                "Replicate_ID": pd.NA,
                "Replicate_n": pd.NA,
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": material_id,
                "Grouping_Confidence": "HIGH",
                "Grouping_Review_Required": False,
                "Grouping_Reason": (
                    "40%-strain observation is correlated with its parent "
                    "tensile condition and cannot count independently"
                ),
                "P022_Record_Role": "RECOVERED_CORRELATED_40PCT_EBSD_STAGE",
                "P022_Target_Status": (
                    "STAGE_SPECIFIC_SUPPORT_NOT_CONDITION_LABEL"
                ),
                "P022_Source_Identity_Status": (
                    "VERIFIED_PDF_AND_EXTERNAL_BIBLIOGRAPHIC_MATCH"
                ),
                "P022_QC_Status": (
                    "PENDING_GLOBAL_QC_SCHEMA_SPLIT_REFRESH_AFTER_COLLECTION"
                ),
                "Alloy_ID": alloy,
                "Original_Composition": FORMULAS[alloy],
                "Original_Composition_Basis": "ATOMIC_RATIO_AS_REPORTED",
                "Composition_basis": "ATOMIC_RATIO_AS_REPORTED",
                "Nominal_Composition_at_pct": pd.NA,
                "Normalized_Composition_at_pct": pd.NA,
                "Composition_Normalization_Status": (
                    "NOT_NORMALIZED_RECOVERY_PRESERVES_ATOMIC_RATIO_FORMULA"
                ),
                "Atomic_Ratio_C_Addition_Raw": (
                    2.0 if alloy in {"C2", "C2Mo1", "C2Mo2"} else 0.0
                ),
                "Atomic_Ratio_Mo_Addition_Raw": (
                    1.0 if alloy == "C2Mo1" else (2.0 if alloy == "C2Mo2" else 0.0)
                ),
                "Processing_State": "AS_CAST",
                "Processing_State_ID": "AS_CAST",
                "Deformation_stage": "40% strain EBSD observation",
                "Stage_Label": "40% strain",
                "Local_Strain_pct": 40.0,
                "Tensile_Strain_pct": 40.0,
                "Stage_Method": "EBSD/IPF + misorientation",
                "Characterization_methods": "EBSD/IPF + misorientation",
                "TWIP_Stage": 1,
                "TWIP_at_stage": 1,
                "TRIP_Stage": pd.NA,
                "TRIP_at_stage": pd.NA,
                "Twin_Boundary_Character": (
                    "APPROXIMATELY_60_DEGREE_<111>_"
                    "DEFORMATION_TWIN_BOUNDARIES"
                ),
                "Twin_Population_Qualitative": _twin_population(alloy),
                "Twin_fraction_or_Sigma3": pd.NA,
                "Twin_Fraction_Status": (
                    "QUALITATIVE_POPULATION_ONLY_NO_FRACTION_DIGITIZED"
                ),
                "Stage_Evidence_Type": (
                    "DIRECT_EBSD_DEFORMATION_TWIN_BOUNDARIES_AT_40PCT"
                ),
                "Evidence_TWIP": stage.Twin_Evidence,
                "Target_Evidence_Confidence": "HIGH",
                "TRIP_to_TWIP_Negative_Safeguard": (
                    "STAGE_TWIP_EVIDENCE_DOES_NOT_GENERATE_TRIP_ZERO"
                ),
                "SFE_General_Threshold_Status": (
                    "SECONDARY_GENERAL_THRESHOLDS_NOT_ASSIGNED_TO_"
                    "P022_CONDITIONS"
                ),
                "Source_location": stage.Evidence_Location,
                "Notes": stage.Notes,
            }
        )
        rows.append(row)
    return rows


IDENTITY_FIELDS = {
    "Paper_ID",
    "DOI",
    "Paper_Title",
    "Journal",
    "Volume",
    "Issue",
    "Pages",
    "Publication_Year",
    "Source_URL",
    "Data_Origin",
    "P022_Source_Identity_Status",
}
HIERARCHY_FIELDS = {
    "Condition_ID",
    "Experiment_Group_ID",
    "Parent_Experiment_ID",
    "ML_Condition_ID",
    "Parent_ML_Condition_ID",
    "Observation_ID",
    "Deformation_Stage_ID",
    "Observation_Role",
    "Row_Type",
    "Independent_ML_sample",
    "Independent_Experimental_ML_sample",
    "Experimental_Target_Eligibility",
    "Study_Series_ID",
    "Material_Parent_ID",
    "Physical_Batch_ID",
    "Replicate_ID",
    "Replicate_n",
    "Leakage_Group_Strict",
    "Leakage_Group_Material",
    "Grouping_Confidence",
    "Grouping_Review_Required",
    "Grouping_Reason",
    "P022_Record_Role",
    "P022_QC_Status",
}
COMPOSITION_PROCESSING_FIELDS = {
    "Alloy_ID",
    "Original_Composition",
    "Original_Composition_Basis",
    "Composition_basis",
    "Nominal_Composition_at_pct",
    "Normalized_Composition_at_pct",
    "Composition_Normalization_Status",
    "Atomic_Ratio_C_Addition_Raw",
    "Atomic_Ratio_Mo_Addition_Raw",
    "Fe_at%",
    "Mn_at%",
    "Co_at%",
    "Cr_at%",
    "C_at%",
    "Mo_at%",
    "Measured_Bulk_Composition",
    "Measured_Composition_at_pct",
    "Recovered_Bulk_Composition_at_pct",
    "Measured_Composition_Status",
    "Composition_Status",
    "Recovered_Composition_Status",
    "Processing_State",
    "Processing_State_ID",
    "Processing_route",
    "Raw_Material_Purity",
    "Melting_Route",
    "Cast_method",
    "Casting_Route",
    "Remelt_Count_Min",
    "Remelt_Count_Status",
    "Homogenization_T_K",
    "Homogenization_time_h",
    "Hot_rolling_T_K",
    "Hot_rolling_reduction_pct",
    "Cold_rolling_reduction_pct",
    "Annealing_T_K",
    "Annealing_time_min",
    "Cooling_route",
    "Test_T_Raw",
    "Test_T_K",
    "Test_T_C",
    "Test_T_Status",
    "Strain_rate_s-1",
    "Strain_Rate_Status",
    "Loading_Mode",
    "Flat_Tensile_Specimen_Dimensions_mm",
    "Gauge_length_mm",
    "Gauge_width_mm",
    "Specimen_thickness_mm",
    "Test_Metadata_Status",
}
MICROSTRUCTURE_FIELDS = {
    "Initial_Phase",
    "Initial_Phase_State_Qualitative",
    "Initial_Phase_Status",
    "Initial_FCC_fraction",
    "Recovered_Initial_FCC_fraction",
    "Initial_HCP_fraction",
    "Recovered_Initial_HCP_fraction",
    "Initial_HCP_Status",
    "Recovered_Initial_HCP_status",
    "Initial_HCP_Origin",
    "Initial_TRIP_Target_Guardrail",
    "Initial_HCP_Target_Guardrail",
    "Initial_Secondary_Phase",
    "Initial_Secondary_Phase_Status",
    "Dendrite_Morphology",
    "Grain_size_um",
    "Grain_Size_Status",
    "Sigma_Phase_Evidence_Status",
    "C4_Carbide_XRD_Coexistence_Safeguard",
}
MECHANICAL_FIELDS = {
    "Engineering_YS_MPa",
    "Engineering_UTS_MPa",
    "Engineering_Elongation_pct",
    "YS_MPa",
    "UTS_MPa",
    "Elongation_pct",
    "YS_mean",
    "UTS_mean",
    "TE_mean",
    "Reported_Ultimate_Strength_MPa",
    "Reported_Elongation_pct",
    "Mechanical_Value_Status",
    "Mechanical_Predictor_Eligibility",
    "Figure3_Digitization_Status",
    "Strain_Basis_Status",
}
TARGET_STAGE_FIELDS = {
    "Original_TRIP",
    "Original_TWIP",
    "Recovered_TRIP",
    "Recovered_TWIP",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
    "Target_Status",
    "P022_Target_Status",
    "Paper_Native_Mechanism_Attribution",
    "TRIP_Evidence_Type",
    "TWIP_Evidence_Type",
    "Negative_Evidence_Status",
    "Condition_Level_Target_Evidence",
    "Target_Evidence_Confidence",
    "Label_confidence",
    "Evidence_TRIP",
    "Evidence_TWIP",
    "Author_Attributed_Target_Evidence_Grade",
    "TRIP_to_TWIP_Negative_Safeguard",
    "Twin_Boundary_Character",
    "Twin_Population_Qualitative",
    "Twin_Fraction_Status",
    "TWIP_Mode",
    "Deformation_stage",
    "Stage_Label",
    "Local_Strain_pct",
    "Tensile_Strain_pct",
    "Stage_Method",
    "TWIP_Stage",
    "TWIP_at_stage",
    "TRIP_Stage",
    "TRIP_at_stage",
    "Twin_fraction_or_Sigma3",
    "Stage_Evidence_Type",
}
PHYSICS_FIELDS = {
    "SFE_mJ_m2",
    "SFE_method",
    "SFE_Value_Status",
    "SFE_Data_Origin",
    "SFE_Predictor_Eligibility",
    "SFE_General_Threshold_Status",
    "SFE_Qualitative_Trend",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
    "DeltaG_Value_Status",
    "DeltaG_Data_Origin",
}


def _field_metadata(
    feature: str, record: dict
) -> tuple[str, str, str]:
    source_location = record.get(
        "Source_location", "Verified P022 scientific-evidence workbook"
    )
    if feature in IDENTITY_FIELDS:
        return (
            "SOURCE_IDENTITY",
            "Verified article identity / whole paper",
            "Verified PDF and bibliographic DOI identity",
        )
    if feature in HIERARCHY_FIELDS:
        return (
            "HIERARCHY_INTEGRATION",
            "Verified material-parent, condition, and stage sheets",
            "Source-defined hierarchy with correlated stage-child control",
        )
    if feature in COMPOSITION_PROCESSING_FIELDS:
        return (
            "DIRECT_TEXT_OR_VERIFIED_NA",
            "Materials and methods p.2; tensile condition p.3",
            "Source text without chemistry normalization or temperature/rate inference",
        )
    if feature in MICROSTRUCTURE_FIELDS:
        return (
            "DIRECT_XRD_OM_SEM_OR_VERIFIED_NA",
            "Figs.1-2 pp.2-3",
            "XRD plus OM/SEM with phase-scope safeguards",
        )
    if feature in MECHANICAL_FIELDS:
        return (
            "DIRECT_APPROX_TEXT_OR_VERIFIED_NA",
            source_location,
            "Engineering tensile response; Figure 3 not digitized",
        )
    if feature in TARGET_STAGE_FIELDS:
        return (
            "CONDITION_OR_STAGE_TARGET_EVIDENCE",
            source_location,
            (
                "EBSD/IPF plus misorientation at 40% strain"
                if record.get("Observation_Role") == "CORRELATED_STAGE_CHILD"
                else "Condition-level evidence grading from verified workbook"
            ),
        )
    if feature in PHYSICS_FIELDS:
        return (
            "QUALITATIVE_DIRECTION_OR_VERIFIED_GAP",
            "Introduction/results and whole-paper review",
            "No current-alloy numeric SFE or DeltaG; no cross-paper transfer",
        )
    return (
        "VERIFIED_MASTER_FIELD_MAPPING",
        source_location,
        "Verified workbook-to-master mapping",
    )


def _na_status(feature: str) -> str:
    if feature in {
        "Measured_Bulk_Composition",
        "Measured_Composition_at_pct",
        "Recovered_Bulk_Composition_at_pct",
    }:
        return "VERIFIED_NA_NO_QUANTITATIVE_POSTMELT_BULK_CHEMISTRY"
    if feature in {
        "Nominal_Composition_at_pct",
        "Normalized_Composition_at_pct",
        "Fe_at%",
        "Mn_at%",
        "Co_at%",
        "Cr_at%",
        "C_at%",
        "Mo_at%",
    }:
        return "VERIFIED_NA_ATOMIC_RATIO_FORMULA_NOT_NORMALIZED_TO_ATPCT"
    if feature in {"Physical_Batch_ID", "Replicate_ID", "Replicate_n"}:
        return "VERIFIED_NA_NOT_SOURCE_SUPPORTED_NO_PSEUDOREPLICATION"
    if feature in {
        "Homogenization_T_K",
        "Homogenization_time_h",
        "Hot_rolling_T_K",
        "Hot_rolling_reduction_pct",
        "Cold_rolling_reduction_pct",
        "Annealing_T_K",
        "Annealing_time_min",
    }:
        return "VERIFIED_NA_NO_POSTCAST_TREATMENT_REPORTED"
    if feature in {"Test_T_K", "Test_T_C"}:
        return "VERIFIED_NA_ROOM_TEMPERATURE_NOT_NUMERICALLY_REPORTED"
    if feature == "Strain_rate_s-1":
        return "VERIFIED_NA_TENSILE_STRAIN_RATE_NOT_REPORTED"
    if feature in {"Gauge_length_mm", "Gauge_width_mm", "Specimen_thickness_mm"}:
        return "VERIFIED_NA_SOURCE_DIMENSIONS_NOT_PROMOTED_TO_GAUGE_FIELDS"
    if feature in {"Initial_FCC_fraction", "Recovered_Initial_FCC_fraction"}:
        return "VERIFIED_NA_EXACT_NUMERIC_FCC_FRACTION_NOT_REPORTED"
    if feature == "Initial_HCP_fraction":
        return "VERIFIED_NA_C0_INITIAL_FCC_HCP_FRACTIONS_NOT_REPORTED"
    if feature == "Grain_size_um":
        return "VERIFIED_NA_NUMERIC_GRAIN_SIZE_NOT_REPORTED_NO_DIGITIZATION"
    if feature in {
        "Engineering_YS_MPa",
        "Engineering_UTS_MPa",
        "Engineering_Elongation_pct",
    }:
        return "VERIFIED_NA_NOT_EXPLICIT_DIRECT_TEXT_NO_FIGURE_DIGITIZATION"
    if feature in {"Effective_TRIP", "Effective_TWIP", "Slip"}:
        return "VERIFIED_NA_INSUFFICIENT_CONDITION_LEVEL_EVIDENCE"
    if feature in {"TRIP_Stage", "TRIP_at_stage"}:
        return "VERIFIED_NA_NO_STAGE_PHASE_TRANSFORMATION_ASSIGNMENT"
    if feature == "Twin_fraction_or_Sigma3":
        return "VERIFIED_NA_TWIN_FRACTION_NOT_DIGITIZED"
    if feature in {"SFE_mJ_m2", "SFE_method"}:
        return "VERIFIED_NA_NO_CURRENT_ALLOY_NUMERIC_SFE"
    if feature in {"DeltaG_FCC_HCP_J_mol", "DeltaG_method"}:
        return "VERIFIED_NA_NOT_REPORTED_NO_CROSS_PAPER_TRANSFER"
    return "VERIFIED_NA_NOT_SOURCE_SUPPORTED"


def _predictor_eligibility(feature: str, record: dict) -> str:
    if feature in MECHANICAL_FIELDS:
        return "MECHANICAL_OUTCOME_LEAKAGE"
    if feature in TARGET_STAGE_FIELDS:
        return (
            "POST_DEFORMATION_TARGET_EVIDENCE"
            if record.get("Observation_Role") == "CORRELATED_STAGE_CHILD"
            else "TARGET_OR_TARGET_EVIDENCE_NOT_PREDICTOR"
        )
    if feature in PHYSICS_FIELDS:
        return "NOT_SAFE_AS_DIRECT_NUMERIC_SFE_OR_DELTAG"
    return "AUDIT_SCOPE_DEPENDENT"


def _workbook_scopes(record_id: str) -> list[str]:
    if record_id == SERIES:
        return list(EXACT_IDS)
    if record_id in MATERIALS.values():
        alloy = ALLOY_BY_MATERIAL[record_id]
        return [CONDITION_BY_ALLOY[alloy]]
    if record_id in EXACT_IDS:
        return [record_id]
    if record_id == "P022_C4_PHASE":
        return [CONDITION_BY_ALLOY["C4"]]
    if record_id in {"P022_SFE_GENERIC_LOW", "P022_DELTAG"}:
        return list(EXACT_IDS)
    raise AssertionError(f"unknown P022 provenance record scope: {record_id}")


def _append_workbook_provenance(
    rows: list[dict], sheets: dict[str, pd.DataFrame]
) -> None:
    for source in sheets["P022_Provenance"].to_dict("records"):
        record_id = str(source["Record_ID"])
        for condition_id in _workbook_scopes(record_id):
            alloy = ALLOY_BY_CONDITION[condition_id]
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIALS[alloy],
                    "ML_Condition_ID": condition_id,
                    "Observation_ID": PRIMARY_OBSERVATION_IDS[condition_id],
                    "Record_ID": record_id,
                    "Feature_Name": source["Feature_Name"],
                    "Recovered_Value": (
                        source["Recovered_Value"]
                        if is_present(source["Recovered_Value"])
                        else "UNRESOLVED_NA"
                    ),
                    "Units": (
                        source["Units"]
                        if is_present(source["Units"])
                        else "not applicable"
                    ),
                    "Evidence_Type": source["Evidence_Type"],
                    "Evidence_Location": source["Evidence_Location"],
                    "Method": source["Method"],
                    "Confidence": source["Confidence"],
                    "Recovery_Status": source["Recovery_Status"],
                    "Data_Origin": "EXPERIMENTAL",
                    "Source_URL": source["Source_URL"],
                    "Predictor_Eligibility": "SOURCE_LEDGER_SCOPE_DEPENDENT",
                    "Provenance_Layer": "VERIFIED_WORKBOOK_LEDGER",
                }
            )


def sfe_physics_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P022_Physics_SFE"].copy()
    thresholds = pd.DataFrame(
        [
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Record_ID": "P022_SFE_THRESHOLD_TWIP_GENERAL",
                "Alloy_Label": "SECONDARY_GENERAL_NOT_P022_ALLOY_VALUE",
                "Feature": "SFE_general_TWIP_range",
                "Recovered_Value": pd.NA,
                "Recovered_Value_Raw": "15-45",
                "Units": "mJ/m2",
                "Method": "Secondary general literature threshold",
                "Status": "SECONDARY_GENERAL_THRESHOLD_NOT_CURRENT_ALLOY_VALUE",
                "Current_Paper_or_Secondary": "SECONDARY_GENERAL_THRESHOLD",
                "Predictor_Eligibility": "SUPPORT_ONLY_NOT_CONDITION_VALUE",
                "Evidence_Location": "Introduction p.2",
                "Confidence": "Medium",
                "Notes": (
                    "Preserved only as a general TWIP range; never assigned "
                    "to any P022 material."
                ),
                "Source_URL": f"https://doi.org/{DOI}",
            },
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Record_ID": "P022_SFE_THRESHOLD_TRIP_GENERAL",
                "Alloy_Label": "SECONDARY_GENERAL_NOT_P022_ALLOY_VALUE",
                "Feature": "SFE_general_TRIP_upper_threshold",
                "Recovered_Value": pd.NA,
                "Recovered_Value_Raw": "<15",
                "Units": "mJ/m2",
                "Method": "Secondary general literature threshold",
                "Status": "SECONDARY_GENERAL_THRESHOLD_NOT_CURRENT_ALLOY_VALUE",
                "Current_Paper_or_Secondary": "SECONDARY_GENERAL_THRESHOLD",
                "Predictor_Eligibility": "SUPPORT_ONLY_NOT_CONDITION_VALUE",
                "Evidence_Location": "Introduction p.2",
                "Confidence": "Medium",
                "Notes": (
                    "Preserved only as a general TRIP threshold; never assigned "
                    "to any P022 material."
                ),
                "Source_URL": f"https://doi.org/{DOI}",
            },
        ]
    )
    frame = pd.concat([frame, thresholds], ignore_index=True)
    frame.insert(2, "Study_Series_ID", SERIES)
    frame["Condition_Assignment_Status"] = (
        "NOT_ASSIGNED_TO_ANY_P022_CONDITION_AS_NUMERIC_SFE_OR_DELTAG"
    )
    return frame


def _append_physics_support_provenance(
    rows: list[dict], physics: pd.DataFrame
) -> None:
    feature_names = {
        "SFE_numeric": "SFE_numeric_current_alloy",
        "SFE_trend": "SFE_qualitative_direction",
        "DeltaG_FCC_HCP": "DeltaG_FCC_HCP_J_mol",
        "SFE_general_TWIP_range": "SFE_general_TWIP_range_15_45",
        "SFE_general_TRIP_upper_threshold": (
            "SFE_general_TRIP_upper_threshold_lt15"
        ),
    }
    for support in physics.to_dict("records"):
        for condition_id in EXACT_IDS:
            alloy = ALLOY_BY_CONDITION[condition_id]
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIALS[alloy],
                    "ML_Condition_ID": condition_id,
                    "Observation_ID": PRIMARY_OBSERVATION_IDS[condition_id],
                    "Record_ID": support["Record_ID"],
                    "Feature_Name": feature_names[str(support["Feature"])],
                    "Recovered_Value": (
                        support["Recovered_Value"]
                        if is_present(support["Recovered_Value"])
                        else (
                            support["Recovered_Value_Raw"]
                            if is_present(support["Recovered_Value_Raw"])
                            else "UNRESOLVED_NA"
                        )
                    ),
                    "Units": (
                        support["Units"]
                        if is_present(support["Units"])
                        else "not applicable"
                    ),
                    "Evidence_Type": support["Status"],
                    "Evidence_Location": support["Evidence_Location"],
                    "Method": support["Method"],
                    "Confidence": support["Confidence"],
                    "Recovery_Status": (
                        "VERIFIED_SUPPORT_ONLY_NOT_CONDITION_VALUE"
                        if "THRESHOLD" in str(support["Status"])
                        else support["Status"]
                    ),
                    "Data_Origin": "EXPERIMENTAL",
                    "Source_URL": support["Source_URL"],
                    "Predictor_Eligibility": (
                        support["Predictor_Eligibility"]
                        if is_present(support["Predictor_Eligibility"])
                        else "NOT_SAFE_AS_DIRECT_NUMERIC_SFE_OR_DELTAG"
                    ),
                    "Provenance_Layer": "PHYSICS_SAFEGUARD_MAPPING",
                }
            )


def build_provenance(
    new_rows: list[dict],
    sheets: dict[str, pd.DataFrame],
    physics: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict] = []
    for record in new_rows:
        observation_id = record["Observation_ID"]
        is_stage = record["Observation_Role"] == "CORRELATED_STAGE_CHILD"
        condition_id = (
            record["Parent_ML_Condition_ID"]
            if is_stage
            else record["ML_Condition_ID"]
        )
        meaningful_na = (
            MEANINGFUL_NA_STAGE if is_stage else MEANINGFUL_NA_PRIMARY
        )
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            if not is_present(value) and feature not in meaningful_na:
                continue
            evidence_type, evidence_location, method = _field_metadata(
                feature, record
            )
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": record["Material_Parent_ID"],
                    "ML_Condition_ID": condition_id,
                    "Observation_ID": observation_id,
                    "Record_ID": observation_id,
                    "Feature_Name": feature,
                    "Recovered_Value": (
                        value if is_present(value) else "UNRESOLVED_NA"
                    ),
                    "Units": UNIT_MAP.get(feature, "as reported"),
                    "Evidence_Type": evidence_type,
                    "Evidence_Location": evidence_location,
                    "Method": method,
                    "Confidence": record.get(
                        "Target_Evidence_Confidence",
                        record.get("Grouping_Confidence", "High"),
                    ),
                    "Recovery_Status": (
                        "VERIFIED" if is_present(value) else _na_status(feature)
                    ),
                    "Data_Origin": "EXPERIMENTAL",
                    "Source_URL": f"https://doi.org/{DOI}",
                    "Predictor_Eligibility": _predictor_eligibility(
                        feature, record
                    ),
                    "Provenance_Layer": "MASTER_FIELD_MAPPING",
                }
            )

    _append_workbook_provenance(rows, sheets)
    _append_physics_support_provenance(rows, physics)
    frame = pd.DataFrame(rows).drop_duplicates(ignore_index=True)
    required = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
        "ML_Condition_ID",
        "Observation_ID",
        "Feature_Name",
        "Recovered_Value",
        "Units",
        "Evidence_Type",
        "Evidence_Location",
        "Method",
        "Confidence",
        "Recovery_Status",
        "Data_Origin",
    ]
    assert frame[required].notna().all().all()
    assert frame.ML_Condition_ID.isin(EXACT_IDS).all()
    return frame


def attach_provenance_json(
    new_rows: list[dict], provenance: pd.DataFrame
) -> None:
    for row in new_rows:
        selected = provenance[
            provenance.Observation_ID.eq(row["Observation_ID"])
        ]
        row["P022_Recovery_Provenance_JSON"] = json.dumps(
            json_ready(selected.to_dict("records")),
            ensure_ascii=False,
            allow_nan=False,
        )


def material_parent_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    frame = sheets["P022_Material_Parents"].copy()
    frame["Original_Composition_Basis"] = "ATOMIC_RATIO_AS_REPORTED"
    frame["Normalized_at_pct"] = pd.NA
    frame["Measured_Bulk_Composition"] = pd.NA
    frame["Normalization_Status"] = (
        "NOT_NORMALIZED_RECOVERY_PRESERVES_ATOMIC_RATIO_FORMULA"
    )
    frame["Corresponding_ML_Condition_ID"] = frame.Alloy_Label.map(
        CONDITION_BY_ALLOY
    )
    return frame


def raw_composition_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    parents = material_parent_table(sheets)
    return parents[
        [
            "Paper_ID",
            "DOI",
            "Study_Series_ID",
            "Material_Parent_ID",
            "Corresponding_ML_Condition_ID",
            "Alloy_Label",
            "Original_Composition_Formula",
            "Original_Composition_Basis",
            "C_Addition_Raw",
            "Mo_Addition_Raw",
            "Normalized_at_pct",
            "Measured_Bulk_Composition",
            "Composition_Status",
            "Normalization_Status",
            "Scientific_Note",
            "Source_URL",
        ]
    ].copy()


def condition_hierarchy_table(
    primary_rows: list[dict], stage_rows: list[dict]
) -> pd.DataFrame:
    fields = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
        "Condition_ID",
        "ML_Condition_ID",
        "Parent_ML_Condition_ID",
        "Observation_ID",
        "Deformation_Stage_ID",
        "Observation_Role",
        "Independent_ML_sample",
        "Independent_Experimental_ML_sample",
        "Experimental_Target_Eligibility",
        "Leakage_Group_Strict",
        "Leakage_Group_Material",
        "Physical_Batch_ID",
        "Replicate_ID",
        "Replicate_n",
        "P022_Record_Role",
    ]
    frame = pd.DataFrame(
        [{field: row[field] for field in fields} for row in primary_rows + stage_rows]
    )
    frame["Pseudo_Replicate_Status"] = "NO_PSEUDO_REPLICATES_CREATED"
    frame["Counting_Status"] = frame.Observation_Role.map(
        {
            "INDEPENDENT_CONDITION": "COUNTS_AS_ONE_INDEPENDENT_CONDITION",
            "CORRELATED_STAGE_CHILD": "SUPPORT_ONLY_DOES_NOT_INCREASE_COUNT",
        }
    )
    return frame


def processing_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    frame = sheets["P022_Conditions"].copy()
    frame["Original_Composition_Basis"] = "ATOMIC_RATIO_AS_REPORTED"
    frame["Post_Cast_Treatment_Status"] = (
        "NO_HOMOGENIZATION_ROLLING_OR_ANNEALING_REPORTED"
    )
    frame["Exact_Test_T_K_Status"] = "NOT_NUMERICALLY_REPORTED"
    frame["Tensile_Strain_Rate_Status"] = "NOT_REPORTED"
    frame["Replicate_Status"] = "NOT_REPORTED_NO_PSEUDO_REPLICATES"
    return frame


def stage_observation_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    frame = sheets["P022_Stage_Evidence"].copy()
    frame["Study_Series_ID"] = SERIES
    frame["Material_Parent_ID"] = frame.Parent_ML_Condition_ID.map(
        lambda condition_id: MATERIALS[ALLOY_BY_CONDITION[condition_id]]
    )
    frame["Twin_Boundary_Character"] = (
        "APPROXIMATELY_60_DEGREE_<111>_DEFORMATION_TWIN_BOUNDARIES"
    )
    frame["Twin_Fraction"] = pd.NA
    frame["Twin_Fraction_Status"] = (
        "QUALITATIVE_POPULATION_ONLY_NO_FRACTION_DIGITIZED"
    )
    frame["Counting_Status"] = "CORRELATED_STAGE_CHILD_NOT_INDEPENDENT"
    return frame


def decision_ledger(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    frame = sheets["P022_Integration_Decisions"].copy()
    frame.insert(0, "Paper_ID", PAPER_ID)
    frame.insert(1, "DOI", DOI)
    frame["Study_Series_ID"] = SERIES
    frame["Data_Origin"] = "EXPERIMENTAL"
    frame["Legacy_Duplicate_Status"] = (
        "NEW_SOURCE_NO_P022_DOI_REPRESENTATION_IN_V15"
    )
    frame["Correction_Mode"] = (
        "NEW_ROWS_ONLY_NO_RECOVERY_V15_VALUE_OVERWRITE"
    )
    return frame


def validate(
    source: pd.DataFrame,
    out: pd.DataFrame,
    sheets: dict[str, pd.DataFrame],
    provenance: pd.DataFrame,
    new_rows: list[dict],
) -> None:
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    assert duplicate_rows(source).empty
    p022 = out[out.Paper_ID.eq(PAPER_ID)].copy()
    assert len(out) == len(source) + 8
    assert len(p022) == 8

    primary = p022[
        p022.Observation_Role.eq("INDEPENDENT_CONDITION")
    ].set_index("ML_Condition_ID", drop=False)
    stages = p022[
        p022.Observation_Role.eq("CORRELATED_STAGE_CHILD")
    ].set_index("Observation_ID", drop=False)
    assert tuple(primary.index) == EXACT_IDS
    assert tuple(stages.index) == STAGE_IDS
    assert len(primary) == 5 and len(stages) == 3
    assert primary.DOI.eq(DOI).all() and stages.DOI.eq(DOI).all()
    assert primary.Independent_ML_sample.eq(True).all()
    assert primary.Independent_Experimental_ML_sample.eq(True).all()
    assert primary.Experimental_Target_Eligibility.eq(True).all()
    assert stages.Independent_ML_sample.eq(False).all()
    assert stages.Independent_Experimental_ML_sample.eq(False).all()
    assert stages.Experimental_Target_Eligibility.eq(False).all()
    assert stages.ML_Condition_ID.isna().all()
    assert stages.Parent_ML_Condition_ID.notna().all()
    assert primary.Physical_Batch_ID.isna().all()
    assert primary.Replicate_ID.isna().all()
    assert primary.Replicate_n.isna().all()

    assert set(primary.Material_Parent_ID) == set(MATERIALS.values())
    assert primary.Study_Series_ID.eq(SERIES).all()
    assert primary.Leakage_Group_Strict.eq(SERIES).all()
    for condition_id in EXACT_IDS:
        alloy = ALLOY_BY_CONDITION[condition_id]
        row = primary.loc[condition_id]
        assert row.Material_Parent_ID == MATERIALS[alloy]
        assert row.Leakage_Group_Material == MATERIALS[alloy]
        assert row.Original_Composition == FORMULAS[alloy]
        assert row.Original_Composition_Basis == "ATOMIC_RATIO_AS_REPORTED"
        assert row.Composition_basis == "ATOMIC_RATIO_AS_REPORTED"

    normalized_fields = [
        "Nominal_Composition_at_pct",
        "Normalized_Composition_at_pct",
        "Fe_at%",
        "Mn_at%",
        "Co_at%",
        "Cr_at%",
        "C_at%",
        "Mo_at%",
    ]
    assert primary[normalized_fields].isna().all().all()
    assert primary.Composition_Normalization_Status.eq(
        "NOT_NORMALIZED_RECOVERY_PRESERVES_ATOMIC_RATIO_FORMULA"
    ).all()
    assert primary.Measured_Bulk_Composition.isna().all()
    assert primary.Measured_Composition_at_pct.isna().all()
    assert primary.Recovered_Bulk_Composition_at_pct.isna().all()

    assert primary.Processing_State.eq("AS_CAST").all()
    assert primary.Raw_Material_Purity.eq(">99.9 wt.%").all()
    assert primary.Remelt_Count_Min.astype(float).eq(5).all()
    assert primary.Remelt_Count_Status.eq("AT_LEAST_FIVE").all()
    assert primary.Homogenization_T_K.isna().all()
    assert primary.Hot_rolling_T_K.isna().all()
    assert primary.Annealing_T_K.isna().all()
    assert primary.Test_T_Raw.eq("room temperature").all()
    assert primary.Test_T_K.isna().all()
    assert primary["Strain_rate_s-1"].isna().all()
    assert primary.Strain_Rate_Status.eq("NOT_REPORTED").all()
    assert primary.Loading_Mode.eq("Uniaxial tension").all()
    assert primary.Flat_Tensile_Specimen_Dimensions_mm.eq(
        "22 x 2.5 x 1.5"
    ).all()

    c0 = primary.loc[CONDITION_BY_ALLOY["C0"]]
    assert c0.Initial_Phase == "FCC_PLUS_HCP"
    assert pd.isna(c0.Initial_FCC_fraction)
    assert pd.isna(c0.Initial_HCP_fraction)
    assert (
        c0.Initial_HCP_Target_Guardrail
        == "INITIAL_HCP_IS_NOT_DEFORMATION_INDUCED_TRIP_EVIDENCE"
    )
    for alloy in ("C2", "C4", "C2Mo1", "C2Mo2"):
        row = primary.loc[CONDITION_BY_ALLOY[alloy]]
        assert float(row.Initial_HCP_fraction) == 0
        assert pd.isna(row.Initial_FCC_fraction)
    c4 = primary.loc[CONDITION_BY_ALLOY["C4"]]
    assert c4.Initial_Phase == "XRD_SINGLE_FCC_MATRIX"
    assert (
        c4.Initial_Secondary_Phase
        == "CARBIDES_IN_INTERDENDRITIC_REGION_DIRECT_SEM"
    )
    assert (
        c4.C4_Carbide_XRD_Coexistence_Safeguard
        == "XRD_SINGLE_FCC_MATRIX_DOES_NOT_ERASE_DIRECT_SEM_CARBIDES"
    )
    c2mo2 = primary.loc[CONDITION_BY_ALLOY["C2Mo2"]]
    assert (
        c2mo2.Sigma_Phase_Evidence_Status
        == "PRIOR_WORK_POSSIBILITY_NOT_CURRENT_PAPER_MEASUREMENT"
    )
    assert primary.Grain_size_um.isna().all()

    for condition_id, expected in EXPECTED_MECHANICS.items():
        row = primary.loc[condition_id]
        for field, expected_value in zip(
            [
                "Engineering_YS_MPa",
                "Engineering_UTS_MPa",
                "Engineering_Elongation_pct",
            ],
            expected,
        ):
            _assert_expected_value(row[field], expected_value)
    assert primary.Mechanical_Predictor_Eligibility.eq(
        "MECHANICAL_OUTCOME_LEAKAGE"
    ).all()
    assert primary.Figure3_Digitization_Status.eq(
        "NOT_DIGITIZED_TEXT_ONLY_VALUES_WHERE_EXPLICIT"
    ).all()

    for condition_id, expected in EXPECTED_TARGETS.items():
        row = primary.loc[condition_id]
        for field, expected_value in zip(
            ["Effective_TRIP", "Effective_TWIP", "Slip"], expected
        ):
            _assert_expected_value(row[field], expected_value)
    assert float(c0.Effective_TRIP) == 1
    assert pd.isna(c0.Effective_TWIP)
    assert (
        c0.Author_Attributed_Target_Evidence_Grade
        == "MEDIUM_AUTHOR_ATTRIBUTED_NOT_DIRECT_POSTTEST_PHASE_MAP"
    )
    assert primary.loc[
        [
            CONDITION_BY_ALLOY["C2"],
            CONDITION_BY_ALLOY["C2Mo1"],
            CONDITION_BY_ALLOY["C2Mo2"],
        ],
        "Effective_TWIP",
    ].astype(float).eq(1).all()
    assert primary.loc[
        [
            CONDITION_BY_ALLOY["C2"],
            CONDITION_BY_ALLOY["C2Mo1"],
            CONDITION_BY_ALLOY["C2Mo2"],
        ],
        "Effective_TRIP",
    ].isna().all()
    assert primary.loc[
        CONDITION_BY_ALLOY["C4"], ["Effective_TRIP", "Effective_TWIP", "Slip"]
    ].isna().all()
    assert not primary.Effective_TRIP.eq(0).any()
    assert not primary.Effective_TWIP.eq(0).any()

    assert stages.Local_Strain_pct.astype(float).eq(40).all()
    assert stages.Stage_Method.eq("EBSD/IPF + misorientation").all()
    assert stages.TWIP_Stage.astype(float).eq(1).all()
    assert stages.TRIP_Stage.isna().all()
    assert stages.Twin_fraction_or_Sigma3.isna().all()
    assert stages.Twin_Fraction_Status.eq(
        "QUALITATIVE_POPULATION_ONLY_NO_FRACTION_DIGITIZED"
    ).all()
    assert (
        stages.loc["P022_C2MO1_EBSD_40", "Twin_Population_Qualitative"]
        == "LARGEST_AMONG_C2_C2MO1_C2MO2_QUALITATIVE"
    )
    assert stages.loc[
        ["P022_C2_EBSD_40", "P022_C2MO2_EBSD_40"],
        "Twin_Population_Qualitative",
    ].eq("LOWER_THAN_C2MO1_QUALITATIVE").all()

    assert primary.SFE_mJ_m2.isna().all()
    assert primary.SFE_method.isna().all()
    assert primary.SFE_General_Threshold_Status.eq(
        "SECONDARY_GENERAL_THRESHOLDS_NOT_ASSIGNED_TO_P022_CONDITIONS"
    ).all()
    assert primary.DeltaG_FCC_HCP_J_mol.isna().all()
    assert primary.DeltaG_method.isna().all()

    before = counts(source)
    after = counts(out)
    assert tuple(after[i] - before[i] for i in range(4)) == (5, 1, 3, 0)
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    expected_class_delta = {
        "trip_positive": 1,
        "trip_negative": 0,
        "twip_positive": 3,
        "twip_negative": 0,
        "joint_00": 0,
        "joint_10": 0,
        "joint_01": 0,
        "joint_11": 0,
    }
    assert {
        key: after_classes[key] - before_classes[key]
        for key in before_classes
    } == expected_class_delta

    required = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
        "ML_Condition_ID",
        "Observation_ID",
        "Feature_Name",
        "Recovered_Value",
        "Units",
        "Evidence_Type",
        "Evidence_Location",
        "Method",
        "Confidence",
        "Recovery_Status",
        "Data_Origin",
    ]
    assert provenance[required].notna().all().all()
    master_provenance = provenance[
        provenance.Provenance_Layer.eq("MASTER_FIELD_MAPPING")
    ]
    for record in new_rows:
        meaningful_na = (
            MEANINGFUL_NA_STAGE
            if record["Observation_Role"] == "CORRELATED_STAGE_CHILD"
            else MEANINGFUL_NA_PRIMARY
        )
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            if is_present(value) or feature in meaningful_na:
                matching = master_provenance[
                    master_provenance.Observation_ID.eq(
                        record["Observation_ID"]
                    )
                    & master_provenance.Feature_Name.eq(feature)
                ]
                assert len(matching), (record["Observation_ID"], feature)
    assert p022.P022_Recovery_Provenance_JSON.str.len().gt(2).all()

    forbidden_derived = [
        "VEC_derived",
        "Atomic_size_mismatch_delta_pct",
        "Configurational_entropy_J_molK",
        "Mixing_enthalpy_kJ_mol",
        "Omega",
        "Electronegativity_mismatch",
        "Melting_temperature_weighted_K",
        "log10_strain_rate",
    ]
    for field in forbidden_derived:
        if field in p022:
            assert p022[field].isna().all()
    assert file_hash(SOURCE) == SOURCE_SHA256
    assert file_hash(BOOK) == BOOK_SHA256


def write_audit(source: pd.DataFrame, out: pd.DataFrame) -> None:
    before = counts(source)
    after = counts(out)
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    audit = f"""# P022 recovery v16 audit

## A. Source identity

- Paper_ID=P022; DOI={DOI}.
- Title: {TITLE}.
- {JOURNAL}, volume {VOLUME}, issue {ISSUE}, pages {PAGES} ({YEAR}); Data_Origin=EXPERIMENTAL.
- The verified workbook identity matches the DOI and bibliographic record. Both workbook and recovery-v15 base are SHA-256 gated; integration rejects a mismatch.

## B. New-source/duplicate status

- Exact recovery-v15 DOI matches: {len(duplicate_rows(source))}. No P022 Paper_ID was present, so P022 is appended as a new source beyond P021.
- No composition-text or row-order mapping was used. A changed base containing this DOI causes the generator to stop for replacement-aware review.

## C. V16 row count

- V16 contains {len(out)} rows: the complete {len(source)}-row recovery-v15 prefix plus five primary conditions and three correlated stage children.

## D. Independent experimental count before/after

- Replacement-aware independent experimental conditions: {before[0]} before -> {after[0]} after.
- The three 40%-strain observations are non-independent and do not affect this count.

## E. Five exact P022 conditions

- Exactly five primary conditions exist: {", ".join(EXACT_IDS)}.
- Each is one independent as-cast tensile condition. Physical batch, replicate identity, and replicate count remain NA; no pseudo-replicates were created.

## F. Five material parents

- Material parents are {", ".join(MATERIALS.values())}, one for each separately fabricated chemistry variant.
- All share strict leakage group {SERIES}; each uses its corresponding material-parent leakage key.

## G. Composition/raw-formula handling

- Exact formulas remain {", ".join(FORMULAS.values())}.
- Original_Composition_Basis=ATOMIC_RATIO_AS_REPORTED. Quantitative post-melt bulk chemistry remains NA.

## H. No automatic at.% normalization

- No formula was normalized to 100 at.%, no normalized elemental concentrations were calculated, and all master at.% element fields remain NA.
- The C and Mo addition terms are retained only in dedicated atomic-ratio fields, not as normalized concentrations.

## I. Room-temperature/test-rate missingness

- Test_T_Raw remains room temperature for all five conditions. Exact Test_T_K and Test_T_C remain NA.
- Tensile strain rate remains NA/NOT_REPORTED. The source dimensions 22 x 2.5 x 1.5 mm are retained without promotion to gauge fields.

## J. Initial C0 FCC+HCP state

- C0 retains initial FCC+HCP with exact FCC and HCP fractions NA.
- Pre-existing as-cast HCP does not generate the C0 TRIP label; the label comes from author condition attribution.

## K. Single-FCC C2/C4/C2Mo1/C2Mo2 states

- C2, C4, C2Mo1, and C2Mo2 retain XRD single-FCC or single-FCC-matrix states with Initial_HCP_fraction=0.
- Exact numeric FCC fractions remain NA; no FCC=1 complement was fabricated.

## L. C4 carbide evidence

- C4 retains CARBIDES_IN_INTERDENDRITIC_REGION_DIRECT_SEM despite the XRD single-FCC-matrix description.
- The XRD matrix result is not treated as proof that carbides are absent.

## M. Morphology differences

- C0 retains a typical as-cast dendritic microstructure; C2 equiaxed/columnar dendrites; C4 dendritic/interdendritic carbide morphology; C2Mo1 more uniform and finer equiaxed dendrites; and C2Mo2 non-equiaxed/striped dendrites.
- No numeric grain size was digitized. Possible sigma precipitation discussed from prior work was not promoted to current-paper phase evidence.

## N. Direct 40%-strain TWIP evidence

- Exactly three correlated EBSD/IPF + misorientation observations exist at Local_Strain_pct=40.
- Each directly records approximately 60-degree <111> deformation-twin boundaries and TWIP_Stage=1. No twin-boundary fraction was digitized.

## O. C2/C2Mo1/C2Mo2 TWIP labels

- C2, C2Mo1, and C2Mo2 are Effective_TWIP=1 from direct 40%-strain EBSD evidence.
- C2Mo1 has the largest qualitative twin population; C2 and C2Mo2 are lower. TRIP remains NA for all three.

## P. C0 author-attributed TRIP evidence grade

- C0 is Effective_TRIP=1 with MEDIUM author-attributed evidence: the current paper explicitly treats C0 as its TRIP reference and contrasts alloyed TWIP response with the TRIP effect in C0.
- This is not graded as direct current-paper post-test phase mapping. C0 TWIP remains NA.

## Q. C4 unresolved target state

- C4 Effective_TRIP, Effective_TWIP, and Slip remain NA with INSUFFICIENT_FOR_ZERO.

## R. Negative-label safeguards

- P022 creates no new TRIP=0 or TWIP=0 labels.
- TRIP-to-TWIP wording, TWIP dominance, missing microscopy, and pre-existing HCP are never converted into strong mechanism negatives or positives outside their supported scope.

## S. Mechanical-property recovery

- C2 retains approximate direct-text UTS about 600 MPa and total elongation about 67.4%.
- C2Mo1 retains approximate direct-text UTS about 658 MPa and total elongation about 89.8%.
- YS and all C0/C4/C2Mo2 exact numeric mechanics remain NA. Figure 3 was not digitized, and the C2Mo2 elongation decrease was not converted into a final value. All recovered mechanics are MECHANICAL_OUTCOME_LEAKAGE.

## T. SFE gap

- No current-paper alloy-specific numeric SFE is stored for any condition.
- General 15-45 mJ/m2 TWIP and <15 mJ/m2 TRIP thresholds remain secondary support-only safeguards, never condition values. C/Mo effects remain QUALITATIVE_DIRECTION_ONLY.

## U. DeltaG gap

- DeltaG_FCC_HCP remains NA for all five materials. No value was calculated or transferred from another FeMnCoCr paper.

## V. Before/after usable target counts

- Usable TRIP/TWIP/joint counts: {before[1]}/{before[2]}/{before[3]} before -> {after[1]}/{after[2]}/{after[3]} after.
- TRIP positive/negative: {before_classes["trip_positive"]}/{before_classes["trip_negative"]} -> {after_classes["trip_positive"]}/{after_classes["trip_negative"]}.
- TWIP positive/negative: {before_classes["twip_positive"]}/{before_classes["twip_negative"]} -> {after_classes["twip_positive"]}/{after_classes["twip_negative"]}.
- Joint states before: 00={before_classes["joint_00"]}, 10={before_classes["joint_10"]}, 01={before_classes["joint_01"]}, 11={before_classes["joint_11"]}; after: 00={after_classes["joint_00"]}, 10={after_classes["joint_10"]}, 01={after_classes["joint_01"]}, 11={after_classes["joint_11"]}.
- Programmatically calculated deltas are +{after[0] - before[0]} independent, +{after[1] - before[1]} usable TRIP, +{after[2] - before[2]} usable TWIP, and +{after[3] - before[3]} usable joint.

## W. Remaining P022 gaps

- Quantitative post-melt bulk chemistry; physical-batch, replicate identity/count, and individual results; exact numeric test temperature and strain rate; exact FCC fractions; numeric grain sizes; C0 direct post-test phase evolution; C4 mechanism evidence; condition-wide TRIP evidence for C2/C2Mo1/C2Mo2; all condition-specific twin fractions; numeric alloy-specific SFE; and DeltaG remain unresolved.

## X. Later global refresh requirement

- Global QC, feature coverage/schema statistics, and grouped split artifacts remain intentionally unrefreshed during the active paper-collection batch.
- They require a non-destructive refresh after collection pauses and before any matrix construction. No ML matrix, model, feature engineering, imputation, normalization, descriptor calculation, figure digitization, resampling, or synthetic record was created.
"""
    AUDIT.write_text(audit, encoding="utf-8")


def integrate() -> tuple[pd.DataFrame, pd.DataFrame]:
    source, sheets = load_and_verify()
    out = source.copy()
    for column in NEW_COLUMNS + ["C4_Carbide_XRD_Coexistence_Safeguard"]:
        if column not in out:
            out[column] = pd.NA

    primary_rows = make_primary_rows(list(out.columns), sheets)
    stage_rows = make_stage_rows(list(out.columns), sheets)
    new_rows = primary_rows + stage_rows
    physics = sfe_physics_table(sheets)
    provenance = build_provenance(new_rows, sheets, physics)
    attach_provenance_json(new_rows, provenance)
    out = pd.concat(
        [
            out.astype(object),
            pd.DataFrame(new_rows, columns=out.columns).astype(object),
        ],
        ignore_index=True,
    )
    validate(source, out, sheets, provenance, new_rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)

    exports = {
        "study_identity": sheets["P022_Study_Identity"],
        "material_parents": material_parent_table(sheets),
        "condition_hierarchy": condition_hierarchy_table(
            primary_rows, stage_rows
        ),
        "raw_composition_formulas": raw_composition_table(sheets),
        "processing": processing_table(sheets),
        "initial_microstructure": sheets["P022_Initial_Microstructure"],
        "mechanical_response": sheets["P022_Mechanical_Response"],
        "40pct_twin_observations": stage_observation_table(sheets),
        "target_evidence": sheets["P022_Target_Evidence"],
        "sfe_physics_safeguards": physics,
        "provenance": provenance,
        "decision_correction_ledger": decision_ledger(sheets),
    }
    for name, frame in exports.items():
        frame.to_csv(
            TABLE / f"p022_recovery_v16_{name}.csv",
            index=False,
        )
    write_audit(source, out)
    return source, out


if __name__ == "__main__":
    integrate()
