"""Integrate verified P023 evidence into extended recovery v17.

Dataset recovery only. The complete recovery-v16 dataset remains an immutable
prefix. Exactly seven source-defined primary tensile conditions are appended.
The three 750 C processing states, before/after deformation evidence, and the
work-hardening-derived onset remain supporting records and never become extra
experimental samples or direct interrupted-test stages. No curve digitization,
composition normalization, imputation, feature engineering, pseudo-replication,
descriptor calculation, or model training occurs.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_extended_recovery_v16.csv"
BOOK = (
    ROOT
    / "data/interim/manual_recovery/P023_scientific_evidence_recovery_VERIFIED.xlsx"
)
OUT = ROOT / "data/processed/master_extended_recovery_v17.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P023_RECOVERY_V17_AUDIT.md"

PAPER_ID = "P023"
DOI = "10.1016/j.apmt.2018.09.002"
TITLE = (
    "Unexpected strength–ductility response in an annealed, metastable, "
    "high-entropy alloy"
)
JOURNAL = "Applied Materials Today"
VOLUME = 13
PAGES = "198-206"
YEAR = 2018
SERIES = "P023_SERIES01"
MATERIAL = "P023_MAT_FE39MN20CO20CR15SI5AL1"
SOURCE_SHA256 = "32b455e3cd8a34dd2d0e404613fabf296e52a05f9662a26724c1c689f4a0688f"
BOOK_SHA256 = "77f2a62819e95426a5847396910eaa6663362d26282fc9213c605510d4a247a1"

NOMINAL_COMPOSITION = "Fe39Mn20Co20Cr15Si5Al1"
NOMINAL_ELEMENTS = {
    "Fe": 39.0,
    "Mn": 20.0,
    "Co": 20.0,
    "Cr": 15.0,
    "Si": 5.0,
    "Al": 1.0,
}
EXPECTED_LOCAL_EDS = {
    "AS_CAST": {
        "Fe": 40.2,
        "Mn": 19.7,
        "Co": 20.5,
        "Cr": 14.4,
        "Si": 4.6,
        "Al": 0.7,
    },
    "D_PASS": {
        "Fe": 39.0,
        "Mn": 19.8,
        "Co": 20.0,
        "Cr": 15.9,
        "Si": 4.3,
        "Al": 1.03,
    },
}

STATE_ORDER = (
    "P023_STATE_DPASS",
    "P023_STATE_650_5",
    "P023_STATE_650_15",
    "P023_STATE_650_30",
    "P023_STATE_750_5",
    "P023_STATE_750_15",
    "P023_STATE_750_30",
    "P023_STATE_850_5",
    "P023_STATE_850_15",
    "P023_STATE_850_30",
)
CONDITION_BY_STATE = {
    "P023_STATE_DPASS": "P023_MC_DPASS_RT",
    "P023_STATE_650_5": "P023_MC_650_5_RT",
    "P023_STATE_650_15": "P023_MC_650_15_RT",
    "P023_STATE_650_30": "P023_MC_650_30_RT",
    "P023_STATE_850_5": "P023_MC_850_5_RT",
    "P023_STATE_850_15": "P023_MC_850_15_RT",
    "P023_STATE_850_30": "P023_MC_850_30_RT",
}
EXACT_IDS = tuple(CONDITION_BY_STATE.values())
STATE_BY_CONDITION = {
    condition_id: state_id for state_id, condition_id in CONDITION_BY_STATE.items()
}
PRIMARY_OBSERVATION_IDS = {
    condition_id: condition_id.replace("_MC_", "_OBS_")
    for condition_id in EXACT_IDS
}
SUPPORT_ONLY_750_STATES = (
    "P023_STATE_750_5",
    "P023_STATE_750_15",
    "P023_STATE_750_30",
)
DIRECT_JOINT_IDS = (
    "P023_MC_650_15_RT",
    "P023_MC_850_30_RT",
)
UNRESOLVED_IDS = tuple(
    condition_id for condition_id in EXACT_IDS if condition_id not in DIRECT_JOINT_IDS
)
DEFORMATION_RECORD_BY_CONDITION = {
    "P023_MC_650_15_RT": "P023_65015_BEFORE_AFTER",
    "P023_MC_850_30_RT": "P023_85030_BEFORE_AFTER",
}

EXPECTED_PHASES = {
    "P023_STATE_DPASS": (0.83, 0.17, 3.9),
    "P023_STATE_650_5": (0.86, 0.14, 4.2),
    "P023_STATE_650_15": (0.30, 0.70, 3.5),
    "P023_STATE_650_30": (0.55, 0.45, 2.2),
    "P023_STATE_750_5": (0.79, 0.21, 0.4),
    "P023_STATE_750_15": (0.72, 0.28, 4.1),
    "P023_STATE_750_30": (0.88, 0.12, 1.0),
    "P023_STATE_850_5": (0.95, 0.05, 0.2),
    "P023_STATE_850_15": (0.97, 0.03, 2.3),
    "P023_STATE_850_30": (0.43, 0.57, 4.3),
}
EXPECTED_TARGETS = {
    condition_id: (
        (1, 1, 1) if condition_id in DIRECT_JOINT_IDS else (pd.NA, pd.NA, pd.NA)
    )
    for condition_id in EXACT_IDS
}
EXPECTED_POSTTEST = {
    "P023_MC_650_15_RT": (0.30, 0.70, 0.06, 0.94),
    "P023_MC_850_30_RT": (0.43, 0.57, 0.10, 0.90),
}

REQUIRED_SHEETS = {
    "P023_Study_Identity",
    "P023_Composition_Processing",
    "P023_Processing_States",
    "P023_Tensile_Conditions",
    "P023_Mechanical_Response",
    "P023_Deformation_Evidence",
    "P023_Target_Evidence",
    "P023_Physics_Onset",
    "P023_Integration_Decisions",
    "P023_Provenance",
}

NEW_COLUMNS = [
    "P023_Record_Role",
    "P023_Target_Status",
    "P023_Source_Identity_Status",
    "P023_Source_Family_Status",
    "P023_QC_Status",
    "P023_Recovery_Provenance_JSON",
    "Al_at%",
    "Local_EDS_AsCast_Composition_at_pct",
    "Local_EDS_DPass_Composition_at_pct",
    "Local_EDS_Chemistry_Status",
    "Vacuum_Level_Raw",
    "Backfill_Atmosphere",
    "Cast_Ingot_Dimensions_mm",
    "FSP_Pass1_Rotation_rpm",
    "FSP_Pass2_Rotation_rpm",
    "FSP_Traverse_Speed_mm_min",
    "FSP_Plunge_Depth_mm",
    "FSP_Tilt_deg",
    "FSP_Backplate",
    "FSP_Shielding",
    "PreTest_Phase_Fraction_SD_pct",
    "PreTest_Phase_Fraction_Method",
    "PreTest_Phase_Fraction_Status",
    "Precipitate_State",
    "Matrix_Al_Content_Trend",
    "AsCast_Support_Grain_Size_um",
    "AsCast_Support_Grain_Size_SD_um",
    "AsCast_Grain_Size_Use_Status",
    "Annealed_Grain_Size_Digitization_Status",
    "Al_Content_Curve_Digitization_Status",
    "Tensile_Curve_Digitization_Status",
    "True_Tensile_Strength_MPa",
    "SDI_MPa",
    "SDI_Predictor_Eligibility",
    "Mechanical_Stress_Basis_Status",
    "Mechanical_Value_Approximation_Status",
    "PostTest_FCC_fraction",
    "PostTest_HCP_fraction",
    "PostTest_Phase_Fraction_Method",
    "PostTest_Evidence_Status",
    "PostTest_Predictor_Eligibility",
    "PostTest_Twin_Evidence",
    "PostTest_Slip_Evidence",
    "PostTest_GND_Evidence_Status",
    "PostTest_IPF_Evidence_Status",
    "TRIP_Onset_True_Stress_MPa",
    "TRIP_Onset_Engineering_Stress_Approx_MPa",
    "TRIP_Onset_Strain_Approx_pct",
    "WH_Rate_at_Slope_Change_MPa",
    "TRIP_Onset_Evidence_Status",
    "TRIP_Onset_Predictor_Eligibility",
    "WH_Rate_Predictor_Eligibility",
    "Direct_Stage_Fabrication_Status",
    "ThermoCalc_Software",
    "ThermoCalc_Database",
    "ThermoCalc_Context_Status",
    "ThermoCalc_Observation_Safeguard",
    "SFE_Transfer_Safeguard",
    "DeltaG_Transfer_Safeguard",
    "Phase_Specific_TWIP_Safeguard",
]

MEANINGFUL_NA_PRIMARY = {
    "Issue",
    "Physical_Batch_ID",
    "Replicate_ID",
    "Measured_Bulk_Composition",
    "Measured_Composition_at_pct",
    "Recovered_Bulk_Composition_at_pct",
    "Normalized_Composition_at_pct",
    "Test_T_K",
    "Test_T_C",
    "SFE_mJ_m2",
    "SFE_method",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
    "Engineering_YS_MPa",
    "Engineering_UTS_MPa",
    "Engineering_Elongation_pct",
    "True_Tensile_Strength_MPa",
    "Uniform_elongation_pct",
    "SDI_MPa",
    "PostTest_FCC_fraction",
    "PostTest_HCP_fraction",
    "TRIP_Onset_True_Stress_MPa",
    "TRIP_Onset_Engineering_Stress_Approx_MPa",
    "TRIP_Onset_Strain_Approx_pct",
    "WH_Rate_at_Slope_Change_MPa",
}
PROVENANCE_EXCLUDE = {
    "P023_Recovery_Provenance_JSON",
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
SUPPORT_MEANINGFUL_NA = {
    "Measured_Bulk_Composition",
    "Test_T_K",
    "Physical_Batch_ID",
    "Replicate_ID",
    "SFE_numeric",
    "DeltaG_FCC_HCP",
    "Precipitate_State",
    "Engineering_YS_MPa",
    "Engineering_UTS_MPa",
    "Total_Elongation_pct",
    "True_Tensile_Strength_MPa",
    "Uniform_Elongation_pct",
    "SDI_MPa",
}

UNIT_MAP = {
    "Fe_at%": "at.%",
    "Mn_at%": "at.%",
    "Co_at%": "at.%",
    "Cr_at%": "at.%",
    "Si_at%": "at.%",
    "Al_at%": "at.%",
    "Annealing_T_K": "K",
    "Anneal_T_C_Raw": "C",
    "Annealing_time_min": "min",
    "Test_T_K": "K",
    "Test_T_C": "C",
    "Strain_rate_s-1": "s^-1",
    "Gauge_length_mm": "mm",
    "Gauge_width_mm": "mm",
    "Specimen_thickness_mm": "mm",
    "FSP_Pass1_Rotation_rpm": "rpm",
    "FSP_Pass2_Rotation_rpm": "rpm",
    "FSP_Traverse_Speed_mm_min": "mm/min",
    "FSP_Plunge_Depth_mm": "mm",
    "FSP_Tilt_deg": "degree",
    "Initial_FCC_fraction": "fraction",
    "Initial_HCP_fraction": "fraction",
    "Recovered_Initial_FCC_fraction": "fraction",
    "Recovered_Initial_HCP_fraction": "fraction",
    "PreTest_Phase_Fraction_SD_pct": "percentage points",
    "Grain_size_um": "um",
    "Grain_size_SD_um": "um",
    "Recovered_Grain_size_um": "um",
    "AsCast_Support_Grain_Size_um": "um",
    "AsCast_Support_Grain_Size_SD_um": "um",
    "Engineering_YS_MPa": "MPa",
    "Engineering_UTS_MPa": "MPa",
    "Engineering_Elongation_pct": "%",
    "True_UTS_MPa": "MPa",
    "True_Tensile_Strength_MPa": "MPa",
    "Uniform_elongation_pct": "%",
    "SDI_MPa": "MPa",
    "Effective_TRIP": "binary",
    "Effective_TWIP": "binary",
    "Recovered_TRIP": "binary",
    "Recovered_TWIP": "binary",
    "Slip": "binary",
    "PostTest_FCC_fraction": "fraction",
    "PostTest_HCP_fraction": "fraction",
    "TRIP_Onset_True_Stress_MPa": "MPa",
    "TRIP_Onset_Engineering_Stress_Approx_MPa": "MPa",
    "TRIP_Onset_Strain_Approx_pct": "%",
    "WH_Rate_at_Slope_Change_MPa": "MPa",
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


def parse_composition_string(value: str) -> dict[str, float]:
    pairs = re.findall(r"([A-Z][a-z]?)([0-9]+(?:\.[0-9]+)?)", str(value))
    assert pairs, f"cannot parse composition string: {value!r}"
    return {element: float(number) for element, number in pairs}


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
        "recovery-v16 source changed before P023 integration"
    )
    assert file_hash(BOOK) == BOOK_SHA256, "verified P023 workbook changed"
    source = pd.read_csv(SOURCE, low_memory=False)

    conflicting_id = source[
        source.Paper_ID.eq(PAPER_ID)
        & ~source.DOI.astype("string").str.strip().str.lower().eq(DOI.lower())
    ]
    assert conflicting_id.empty, "P023 Paper_ID exists with a different DOI"
    assert duplicate_rows(source).empty, (
        "P023 DOI already exists; stop for explicit replacement-aware review"
    )
    assert not source.Paper_ID.eq(PAPER_ID).any(), "P023 already exists in v16"

    sheets = pd.read_excel(BOOK, sheet_name=None, dtype=object)
    assert set(sheets) == REQUIRED_SHEETS
    for name, frame in sheets.items():
        if "Paper_ID" in frame:
            assert set(frame.Paper_ID.dropna()) == {PAPER_ID}, name
        if "DOI" in frame:
            assert set(frame.DOI.dropna()) == {DOI}, name

    identity = sheets["P023_Study_Identity"].iloc[0]
    assert identity.Paper_ID == PAPER_ID and identity.DOI == DOI
    assert identity.Title == TITLE
    assert identity.Journal == JOURNAL
    assert int(identity.Volume) == VOLUME
    assert str(identity.Pages) == PAGES
    assert int(identity.Year) == YEAR
    assert identity.Data_Origin == "EXPERIMENTAL"
    assert identity.Study_Series_ID == SERIES
    assert identity.Material_Parent_ID == MATERIAL
    assert (
        identity.Source_Identity_Status
        == "VERIFIED_PDF_AND_SCIENCEDIRECT_DOI_MATCH"
    )

    composition = sheets["P023_Composition_Processing"].iloc[0]
    assert composition.Material_Parent_ID == MATERIAL
    assert composition.Nominal_Composition == NOMINAL_COMPOSITION
    assert composition.Composition_Basis == "at.%"
    assert pd.isna(composition.Measured_Bulk_Composition)
    assert (
        composition.Composition_Status
        == "NOMINAL_PLUS_LOCAL_EDS_NO_BULK_POSTMELT_CHEMISTRY"
    )
    assert parse_composition_string(
        composition.AsCast_EDS_Composition_atpct
    ) == EXPECTED_LOCAL_EDS["AS_CAST"]
    assert parse_composition_string(
        composition.DPass_EDS_Composition_atpct
    ) == EXPECTED_LOCAL_EDS["D_PASS"]
    assert (
        composition.EDS_Scope
        == "LOCAL_EDS_ELEMENTAL_DISTRIBUTION_TABLE_NOT_BULK_CHEMISTRY"
    )
    assert composition.Casting_Route == "Vacuum arc casting in cold-copper crucible"
    assert composition.Vacuum_Level_Raw == "~300 um vacuum"
    assert composition.Backfill_Atmosphere == "Ar to 1 atm"
    assert composition.Ingot_Dimensions_mm == "300 x 100 x 6"
    assert float(composition.FSP_Pass1_rpm) == 350
    assert float(composition.FSP_Pass2_rpm) == 150
    assert float(composition.FSP_Traverse_mm_min) == 50.8
    assert float(composition.FSP_Plunge_mm) == 3.65
    assert float(composition.FSP_Tilt_deg) == 2
    assert composition.FSP_Backplate == "Cu"

    states = sheets["P023_Processing_States"].set_index(
        "Processing_State_ID", drop=False
    )
    assert tuple(states.index) == STATE_ORDER
    assert len(states) == 10
    assert states.Independent_Experimental_ML_sample.eq(False).all()
    assert states.Phase_Fraction_Method.eq(
        "XRD_PLUS_EBSD_REPORTED_SUMMARY"
    ).all()
    for state_id, expected in EXPECTED_PHASES.items():
        actual = states.loc[
            state_id,
            ["Initial_FCC_fraction", "Initial_HCP_fraction", "Phase_Fraction_SD_pct"],
        ]
        for value, expected_value in zip(actual, expected):
            _assert_expected_value(value, expected_value)
    dpass = states.loc["P023_STATE_DPASS"]
    assert float(dpass.Grain_Size_um) == 0.79
    assert float(dpass.Grain_Size_Uncertainty_um) == 0.05
    assert states.loc[list(SUPPORT_ONLY_750_STATES), "Grain_Size_um"].isna().all()

    tensile = sheets["P023_Tensile_Conditions"].set_index(
        "ML_Condition_ID", drop=False
    )
    assert tuple(tensile.index) == EXACT_IDS
    assert len(tensile) == 7
    assert tensile.Independent_Experimental_ML_sample.eq(True).all()
    assert tensile.Study_Series_ID.eq(SERIES).all()
    assert tensile.Material_Parent_ID.eq(MATERIAL).all()
    assert tensile.Leakage_Group_Strict.eq(SERIES).all()
    assert tensile.Leakage_Group_Material.eq(MATERIAL).all()
    assert tensile.Physical_Batch_ID.isna().all()
    assert tensile.Replicate_ID.isna().all()
    assert tensile.Replicate_n.astype(float).eq(3).all()
    assert tensile.Test_T_Raw.eq("room temperature").all()
    assert tensile.Test_T_K.isna().all()
    assert tensile["Strain_Rate_s-1"].astype(float).eq(1e-3).all()
    assert tensile.Loading_Mode.eq("Uniaxial tension").all()
    assert tensile.Gauge_Length_mm.astype(float).eq(5).all()
    assert tensile.Gauge_Width_mm.astype(float).eq(1.25).all()
    assert tensile.Thickness_mm.astype(float).eq(1).all()
    assert not tensile.Processing_State_ID.isin(SUPPORT_ONLY_750_STATES).any()
    for condition_id, state_id in STATE_BY_CONDITION.items():
        assert tensile.loc[condition_id, "Processing_State_ID"] == state_id

    mechanics = sheets["P023_Mechanical_Response"].set_index(
        "ML_Condition_ID", drop=False
    )
    assert tuple(mechanics.index) == EXACT_IDS
    m65015 = mechanics.loc["P023_MC_650_15_RT"]
    assert float(m65015.Engineering_YS_MPa) == 610
    assert float(m65015.Engineering_UTS_MPa) == 1120
    assert float(m65015.Total_Elongation_pct) == 52
    assert float(m65015.SDI_MPa) == 425
    m65030 = mechanics.loc["P023_MC_650_30_RT"]
    assert float(m65030.True_Tensile_Strength_MPa) == 1630
    assert float(m65030.Uniform_Elongation_pct) == 43
    assert pd.isna(m65030.Engineering_UTS_MPa)
    assert pd.isna(m65030.Total_Elongation_pct)

    deformation = sheets["P023_Deformation_Evidence"].set_index(
        "Parent_ML_Condition_ID", drop=False
    )
    assert tuple(deformation.index) == DIRECT_JOINT_IDS
    assert deformation.Independent_ML_sample.eq(False).all()
    assert deformation.Observation_Role.eq("CORRELATED_POST_TEST_EVIDENCE").all()
    for condition_id, expected in EXPECTED_POSTTEST.items():
        actual = deformation.loc[
            condition_id,
            ["Pre_FCC_fraction", "Pre_HCP_fraction", "Post_FCC_fraction", "Post_HCP_fraction"],
        ]
        for value, expected_value in zip(actual, expected):
            _assert_expected_value(value, expected_value)
        assert deformation.loc[condition_id, "TWIP_Phase"] == "HCP_EPSILON"

    targets = sheets["P023_Target_Evidence"].set_index(
        "ML_Condition_ID", drop=False
    )
    assert tuple(targets.index) == EXACT_IDS
    for condition_id, expected in EXPECTED_TARGETS.items():
        actual = targets.loc[
            condition_id, ["Effective_TRIP", "Effective_TWIP", "Slip"]
        ]
        for value, expected_value in zip(actual, expected):
            _assert_expected_value(value, expected_value)
    assert targets.loc[list(DIRECT_JOINT_IDS), "Target_Status"].eq(
        "VERIFIED_JOINT"
    ).all()
    assert targets.loc[list(DIRECT_JOINT_IDS), "TWIP_Phase"].eq(
        "HCP_EPSILON"
    ).all()
    assert targets.loc[list(UNRESOLVED_IDS), "Negative_Evidence_Status"].eq(
        "INSUFFICIENT_FOR_ZERO"
    ).all()
    assert not targets.Effective_TRIP.eq(0).any()
    assert not targets.Effective_TWIP.eq(0).any()

    physics = sheets["P023_Physics_Onset"]
    values = physics.set_index("Feature")["Value"]
    assert float(values["TRIP_Onset_True_Stress"]) == 924
    assert float(values["TRIP_Onset_Engineering_Stress_Approx"]) == 840
    assert float(values["TRIP_Onset_Strain_Approx"]) == 10
    assert float(values["WH_Rate_at_Slope_Change"]) == 2983
    assert values["ThermoCalc_Database"] == "TCHEA2"
    assert pd.isna(values["SFE_numeric"])
    assert pd.isna(values["DeltaG_FCC_HCP"])
    onset = physics[physics.Feature.str.startswith("TRIP_Onset")]
    assert onset.Status.eq("CURRENT_PAPER_CURVE_INFERRED_MECHANISM_ONSET").all()
    assert onset.Predictor_Eligibility.eq(
        "MODEL_CURVE_INFERENCE_NOT_DIRECT_STAGE"
    ).all()
    return source, sheets


def _row_template(columns: list[str]) -> dict:
    return {column: pd.NA for column in columns}


def _annealing_route(state: pd.Series) -> str:
    base = (
        "Vacuum arc cast in cold-copper crucible; double-pass friction-stir "
        "processing at 350 then 150 rpm, 50.8 mm/min traverse, 3.65 mm plunge, "
        "2 degree tilt, Cu backing plate, and Ar shielding"
    )
    if pd.isna(state.Anneal_T_C):
        return base
    return (
        f"{base}; annealed {int(state.Anneal_T_C)} C/"
        f"{int(state.Anneal_Time_min)} min; water quenched"
    )


def _grain_status(state_id: str) -> str:
    if state_id == "P023_STATE_DPASS":
        return "DIRECT_REPORTED_DPASS_GRAIN_SIZE"
    return "ANNEALED_GRAIN_SIZE_NOT_DIGITIZED_FROM_FIG3G"


def make_primary_rows(
    columns: list[str], sheets: dict[str, pd.DataFrame]
) -> list[dict]:
    identity = sheets["P023_Study_Identity"].iloc[0]
    composition = sheets["P023_Composition_Processing"].iloc[0]
    states = sheets["P023_Processing_States"].set_index("Processing_State_ID")
    tensile = sheets["P023_Tensile_Conditions"].set_index("ML_Condition_ID")
    mechanics = sheets["P023_Mechanical_Response"].set_index("ML_Condition_ID")
    targets = sheets["P023_Target_Evidence"].set_index("ML_Condition_ID")
    deformation = sheets["P023_Deformation_Evidence"].set_index(
        "Parent_ML_Condition_ID"
    )
    physics = sheets["P023_Physics_Onset"].set_index("Feature")
    rows: list[dict] = []

    for condition_id in EXACT_IDS:
        condition = tensile.loc[condition_id]
        state_id = condition.Processing_State_ID
        state = states.loc[state_id]
        mechanical = mechanics.loc[condition_id]
        target = targets.loc[condition_id]
        direct = condition_id in DIRECT_JOINT_IDS
        post = deformation.loc[condition_id] if direct else None
        observation_id = PRIMARY_OBSERVATION_IDS[condition_id]
        annealed = is_present(state.Anneal_T_C)

        trip = clean(target.Effective_TRIP)
        twip = clean(target.Effective_TWIP)
        slip = clean(target.Slip)
        engineering_ys = clean(mechanical.Engineering_YS_MPa)
        engineering_uts = clean(mechanical.Engineering_UTS_MPa)
        total_elongation = clean(mechanical.Total_Elongation_pct)
        true_strength = clean(mechanical.True_Tensile_Strength_MPa)
        uniform_elongation = clean(mechanical.Uniform_Elongation_pct)
        sdi = clean(mechanical.SDI_MPa)

        row = _row_template(columns)
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Journal": JOURNAL,
                "Volume": VOLUME,
                "Issue": pd.NA,
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
                "Row_Type": "Primary experimental tensile condition",
                "Independent_ML_sample": True,
                "Independent_Experimental_ML_sample": True,
                "Experimental_Target_Eligibility": True,
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": MATERIAL,
                "Physical_Batch_ID": pd.NA,
                "Replicate_ID": pd.NA,
                "Replicate_n": 3,
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": MATERIAL,
                "Grouping_Confidence": "HIGH",
                "Grouping_Review_Required": False,
                "Grouping_Reason": (
                    "Source-defined FSP/annealing processing state with one "
                    "room-temperature tensile condition; three tested specimens "
                    "retained only as aggregate metadata"
                ),
                "P023_Record_Role": "RECOVERED_EXACT_PRIMARY_CONDITION",
                "P023_Target_Status": target.Target_Status,
                "P023_Source_Identity_Status": identity.Source_Identity_Status,
                "P023_Source_Family_Status": (
                    "NEW_SOURCE_NOT_MERGED_WITH_RELATED_NENE_MISHRA_STUDIES"
                ),
                "P023_QC_Status": (
                    "PENDING_GLOBAL_QC_SCHEMA_SPLIT_REFRESH_AFTER_COLLECTION"
                ),
                "Alloy_ID": NOMINAL_COMPOSITION,
                "Alloy_Family_Text": NOMINAL_COMPOSITION,
                "Alloy_Family_Use": "GROUPING_AUDIT_ONLY_NOT_SOURCE_OR_BATCH_IDENTITY",
                "Original_Composition": NOMINAL_COMPOSITION,
                "Original_Composition_Basis": "NOMINAL_AT_PERCENT_AS_REPORTED",
                "Composition_basis": "at.% nominal",
                "Nominal_Composition_at_pct": NOMINAL_COMPOSITION,
                "Normalized_Composition_at_pct": pd.NA,
                "Composition_Normalization_Status": (
                    "NOT_NORMALIZED_SOURCE_NOMINAL_ATPCT_AS_REPORTED"
                ),
                "Fe_at%": NOMINAL_ELEMENTS["Fe"],
                "Mn_at%": NOMINAL_ELEMENTS["Mn"],
                "Co_at%": NOMINAL_ELEMENTS["Co"],
                "Cr_at%": NOMINAL_ELEMENTS["Cr"],
                "Si_at%": NOMINAL_ELEMENTS["Si"],
                "Al_at%": NOMINAL_ELEMENTS["Al"],
                "Other_elements": "Al1 at.%",
                "Measured_Bulk_Composition": pd.NA,
                "Measured_Composition_at_pct": pd.NA,
                "Recovered_Bulk_Composition_at_pct": pd.NA,
                "Measured_Composition_Status": (
                    "NO_BULK_POSTMELT_CHEMISTRY_LOCAL_EDS_ONLY"
                ),
                "Composition_Status": composition.Composition_Status,
                "Recovered_Composition_Status": composition.Composition_Status,
                "Local_EDS_AsCast_Composition_at_pct": (
                    composition.AsCast_EDS_Composition_atpct
                ),
                "Local_EDS_DPass_Composition_at_pct": (
                    composition.DPass_EDS_Composition_atpct
                ),
                "Local_EDS_Chemistry_Status": composition.EDS_Scope,
                "Local_EDS_Composition_at_pct": json.dumps(
                    EXPECTED_LOCAL_EDS, sort_keys=True
                ),
                "Local_EDS_Composition_Scope": composition.EDS_Scope,
                "Processing_State_ID": state_id,
                "Processing_State": state.Processing_State,
                "Processing_route": _annealing_route(state),
                "Melting_Route": composition.Casting_Route,
                "Cast_method": composition.Casting_Route,
                "Casting_Route": "VACUUM_ARC_CAST_COLD_COPPER_CRUCIBLE",
                "Vacuum_Level_Raw": composition.Vacuum_Level_Raw,
                "Backfill_Atmosphere": composition.Backfill_Atmosphere,
                "Cast_Ingot_Dimensions_mm": composition.Ingot_Dimensions_mm,
                "FSP_Pass1_Rotation_rpm": float(composition.FSP_Pass1_rpm),
                "FSP_Pass2_Rotation_rpm": float(composition.FSP_Pass2_rpm),
                "FSP_Traverse_Speed_mm_min": float(
                    composition.FSP_Traverse_mm_min
                ),
                "FSP_Plunge_Depth_mm": float(composition.FSP_Plunge_mm),
                "FSP_Tilt_deg": float(composition.FSP_Tilt_deg),
                "FSP_Backplate": composition.FSP_Backplate,
                "FSP_Shielding": composition.FSP_Shielding,
                "Anneal_T_C_Raw": clean(state.Anneal_T_C),
                "Annealing_T_K": (
                    float(state.Anneal_T_C) + 273.15 if annealed else pd.NA
                ),
                "Annealing_time_min": clean(state.Anneal_Time_min),
                "Post_Anneal_Quench": clean(state.Post_Anneal_Quench),
                "Cooling_route": clean(state.Post_Anneal_Quench),
                "Test_T_Raw": "room temperature",
                "Test_T_K": pd.NA,
                "Test_T_C": pd.NA,
                "Test_T_Status": (
                    "SOURCE_TEXT_ROOM_TEMPERATURE_EXACT_NUMERIC_K_NOT_REPORTED"
                ),
                "Strain_rate_s-1": 1e-3,
                "Strain_Rate_Status": "DIRECT_REPORTED_INITIAL_STRAIN_RATE",
                "Loading_Mode": "Uniaxial tension",
                "Gauge_length_mm": 5.0,
                "Gauge_width_mm": 1.25,
                "Specimen_thickness_mm": 1.0,
                "Test_Metadata_Status": (
                    "ROOM_TEMPERATURE_RAW_ONLY_WITH_DIRECT_RATE_AND_GAUGE_GEOMETRY"
                ),
                "Replicate_Scope": (
                    "THREE_TENSILE_SPECIMENS_PER_CONDITION_AGGREGATE_COUNT_ONLY"
                ),
                "Initial_Phase": "FCC_PLUS_HCP_PRETEST",
                "Initial_Phase_State_Qualitative": "FCC_PLUS_HCP_PRETEST",
                "Initial_Phase_Status": (
                    "DIRECT_PRETENSILE_FIG2C_EBSD_XRD_PHASE_FRACTIONS"
                ),
                "Initial_FCC_fraction": float(state.Initial_FCC_fraction),
                "Recovered_Initial_FCC_fraction": float(
                    state.Initial_FCC_fraction
                ),
                "Initial_HCP_fraction": float(state.Initial_HCP_fraction),
                "Recovered_Initial_HCP_fraction": float(
                    state.Initial_HCP_fraction
                ),
                "Initial_HCP_Status": (
                    "DIRECT_PRETEST_PHASE_FRACTION_FIG2C"
                ),
                "Recovered_Initial_HCP_status": (
                    "DIRECT_PRETEST_PHASE_FRACTION_FIG2C"
                ),
                "Initial_HCP_Origin": (
                    "PRETEST_FSP_ANNEALING_WATER_QUENCH_PROCESSING_STATE"
                ),
                "Initial_TRIP_Target_Guardrail": (
                    "INITIAL_HCP_DOES_NOT_GENERATE_TENSILE_TRIP"
                ),
                "Initial_HCP_Target_Guardrail": (
                    "PRETEST_HCP_IS_NOT_DEFORMATION_INDUCED_TRIP_EVIDENCE"
                ),
                "PreTest_Phase_Fraction_SD_pct": float(
                    state.Phase_Fraction_SD_pct
                ),
                "PreTest_Phase_Fraction_Method": state.Phase_Fraction_Method,
                "PreTest_Phase_Fraction_Status": (
                    "PRE_TENSILE_PROCESSING_STATE_NOT_POSTTEST_TARGET_EVIDENCE"
                ),
                "Phase_Fraction_Methods": state.Phase_Fraction_Method,
                "Grain_size_um": (
                    float(state.Grain_Size_um)
                    if is_present(state.Grain_Size_um)
                    else pd.NA
                ),
                "Grain_size_SD_um": (
                    float(state.Grain_Size_Uncertainty_um)
                    if is_present(state.Grain_Size_Uncertainty_um)
                    else pd.NA
                ),
                "Recovered_Grain_size_um": (
                    float(state.Grain_Size_um)
                    if is_present(state.Grain_Size_um)
                    else pd.NA
                ),
                "Recovered_Grain_size_scope": (
                    "D_PASS_PRETEST_GRAIN_SIZE"
                    if state_id == "P023_STATE_DPASS"
                    else "ANNEALED_GRAIN_SIZE_NOT_RECOVERED"
                ),
                "Grain_Size_Status": _grain_status(state_id),
                "Precipitate_type": clean(state.Precipitate_State),
                "Precipitate_State": clean(state.Precipitate_State),
                "Matrix_Al_Content_Trend": (
                    "DECREASES_WITH_ANNEALING_TIME_QUALITATIVE_FIG3H_NO_DIGITIZATION"
                    if annealed
                    else pd.NA
                ),
                "AsCast_Support_Grain_Size_um": 120.0,
                "AsCast_Support_Grain_Size_SD_um": 12.0,
                "AsCast_Grain_Size_Use_Status": (
                    "SUPPORTING_AS_CAST_MATERIAL_STATE_NOT_PRIMARY_TENSILE_CONDITION"
                ),
                "Annealed_Grain_Size_Digitization_Status": (
                    "NOT_APPLICABLE_DPASS_DIRECT_REPORTED"
                    if not annealed
                    else "NOT_DIGITIZED_FIG3G_QUALITATIVE_ONLY"
                ),
                "Al_Content_Curve_Digitization_Status": (
                    "NOT_DIGITIZED_FIG3H_QUALITATIVE_TREND_ONLY"
                ),
                "Engineering_YS_MPa": engineering_ys,
                "Engineering_UTS_MPa": engineering_uts,
                "Engineering_Elongation_pct": total_elongation,
                "YS_MPa": engineering_ys,
                "UTS_MPa": engineering_uts,
                "Elongation_pct": total_elongation,
                "Reported_Ultimate_Strength_MPa": engineering_uts,
                "Reported_Elongation_pct": total_elongation,
                "True_UTS_MPa": true_strength,
                "True_Tensile_Strength_MPa": true_strength,
                "Uniform_elongation_pct": uniform_elongation,
                "SDI_MPa": sdi,
                "Mechanical_Value_Status": mechanical.Value_Status,
                "Mechanical_Predictor_Eligibility": (
                    "MECHANICAL_OUTCOME_LEAKAGE"
                ),
                "SDI_Predictor_Eligibility": (
                    "OUTCOME_DERIVED_MECHANICAL_LEAKAGE"
                ),
                "Mechanical_Stress_Basis_Status": (
                    "ENGINEERING_YS_UTS_TOTAL_ELONGATION"
                    if condition_id == "P023_MC_650_15_RT"
                    else (
                        "TRUE_TENSILE_STRENGTH_AND_UNIFORM_ELONGATION_NOT_ENGINEERING"
                        if condition_id == "P023_MC_650_30_RT"
                        else "CURVE_ONLY_EXACT_VALUES_NOT_DIGITIZED"
                    )
                ),
                "Mechanical_Value_Approximation_Status": (
                    "UNIFORM_ELONGATION_APPROXIMATE"
                    if condition_id == "P023_MC_650_30_RT"
                    else "EXACT_DIRECT_TEXT_OR_NOT_RECOVERED"
                ),
                "Tensile_Curve_Digitization_Status": (
                    "NOT_DIGITIZED_DIRECT_TEXT_VALUES_ONLY"
                ),
                "Original_TRIP": pd.NA,
                "Original_TWIP": pd.NA,
                "Recovered_TRIP": trip,
                "Recovered_TWIP": twip,
                "Effective_TRIP": trip,
                "Effective_TWIP": twip,
                "Slip": slip,
                "Target_Status": target.Target_Status,
                "TRIP_Parent_Phase": "FCC",
                "TRIP_Product_Phase": "HCP_EPSILON",
                "TWIP_Phase": clean(target.TWIP_Phase),
                "TWIP_Mode": (
                    "DEFORMATION_TWINNING_IN_EPSILON_HCP" if direct else pd.NA
                ),
                "TRIP_Evidence_Type": target.TRIP_Evidence_Type,
                "TWIP_Evidence_Type": target.TWIP_Evidence_Type,
                "Slip_Evidence_Type": (
                    "DIRECT_<C+A>_SLIP_IN_EPSILON_HCP" if direct else pd.NA
                ),
                "Negative_Evidence_Status": target.Negative_Evidence_Status,
                "Condition_Level_Target_Evidence": (
                    target.Condition_Level_Evidence
                ),
                "Target_Evidence_Confidence": target.Confidence,
                "Label_confidence": target.Confidence,
                "Evidence_TRIP": target.Condition_Level_Evidence,
                "Evidence_TWIP": target.Condition_Level_Evidence,
                "Phase_Specific_TWIP_Safeguard": (
                    "HCP_EPSILON_TWIP_NOT_SILENTLY_RECODED_AS_FCC_TWIP"
                ),
                "PostTest_FCC_fraction": (
                    float(post.Post_FCC_fraction) if direct else pd.NA
                ),
                "PostTest_HCP_fraction": (
                    float(post.Post_HCP_fraction) if direct else pd.NA
                ),
                "PostTest_Phase_Fraction_Method": (
                    post.Method if direct else pd.NA
                ),
                "PostTest_Evidence_Status": (
                    "POST_TEST_TARGET_EVIDENCE" if direct else "NOT_RECOVERED_FOR_CONDITION"
                ),
                "PostTest_Predictor_Eligibility": (
                    "POST_TEST_TARGET_EVIDENCE_NOT_PRETEST_PREDICTOR"
                    if direct
                    else "NO_POSTTEST_VALUE_RECOVERED"
                ),
                "PostTest_Twin_Evidence": (
                    post.TWIP_Evidence if direct else pd.NA
                ),
                "PostTest_Slip_Evidence": (
                    post.Slip_Evidence if direct else pd.NA
                ),
                "PostTest_GND_Evidence_Status": (
                    "POST_TEST_LEAKAGE_NO_NUMERIC_DENSITY_RECOVERED"
                    if direct
                    else pd.NA
                ),
                "PostTest_IPF_Evidence_Status": (
                    "POST_TEST_LEAKAGE_NOT_PRETEST_PREDICTOR"
                    if direct
                    else pd.NA
                ),
                "TRIP_Onset_True_Stress_MPa": (
                    float(physics.loc["TRIP_Onset_True_Stress", "Value"])
                    if condition_id == "P023_MC_650_15_RT"
                    else pd.NA
                ),
                "TRIP_Onset_Engineering_Stress_Approx_MPa": (
                    float(
                        physics.loc[
                            "TRIP_Onset_Engineering_Stress_Approx", "Value"
                        ]
                    )
                    if condition_id == "P023_MC_650_15_RT"
                    else pd.NA
                ),
                "TRIP_Onset_Strain_Approx_pct": (
                    float(physics.loc["TRIP_Onset_Strain_Approx", "Value"])
                    if condition_id == "P023_MC_650_15_RT"
                    else pd.NA
                ),
                "WH_Rate_at_Slope_Change_MPa": (
                    float(physics.loc["WH_Rate_at_Slope_Change", "Value"])
                    if condition_id == "P023_MC_650_15_RT"
                    else pd.NA
                ),
                "TRIP_Onset_Evidence_Status": (
                    "CURRENT_PAPER_CURVE_INFERRED_MECHANISM_ONSET"
                    if condition_id == "P023_MC_650_15_RT"
                    else "NOT_RECOVERED_FOR_CONDITION"
                ),
                "TRIP_Onset_Predictor_Eligibility": (
                    "MODEL_CURVE_INFERENCE_NOT_DIRECT_STAGE"
                    if condition_id == "P023_MC_650_15_RT"
                    else "NOT_APPLICABLE"
                ),
                "WH_Rate_Predictor_Eligibility": (
                    "MECHANICAL_OUTCOME_LEAKAGE"
                    if condition_id == "P023_MC_650_15_RT"
                    else "NOT_APPLICABLE"
                ),
                "Direct_Stage_Fabrication_Status": (
                    "NO_DIRECT_EXPERIMENTAL_STAGE_CREATED_FROM_CURVE_INFERENCE"
                ),
                "ThermoCalc_Software": "Thermo-Calc",
                "ThermoCalc_Database": "TCHEA2",
                "ThermoCalc_Context_Status": (
                    "CURRENT_PAPER_THERMODYNAMIC_MODEL_CONTEXT"
                ),
                "ThermoCalc_Observation_Safeguard": (
                    "EQUILIBRIUM_PREDICTIONS_DO_NOT_OVERRIDE_EBSD_XRD_OBSERVATIONS"
                ),
                "SFE_mJ_m2": pd.NA,
                "SFE_method": pd.NA,
                "SFE_Value_Status": "NOT_REPORTED_CURRENT_ALLOY_NUMERIC",
                "SFE_Data_Origin": "CURRENT_PAPER_GAP",
                "SFE_Predictor_Eligibility": "NO_NUMERIC_CURRENT_ALLOY_VALUE",
                "SFE_Transfer_Safeguard": (
                    "NO_IMPORT_FROM_CITED_FE_MN_SI_OR_RELATED_HEA_LITERATURE"
                ),
                "DeltaG_FCC_HCP_J_mol": pd.NA,
                "DeltaG_method": pd.NA,
                "DeltaG_Value_Status": "NOT_REPORTED",
                "DeltaG_Data_Origin": "CURRENT_PAPER_GAP",
                "DeltaG_Transfer_Safeguard": (
                    "NO_CALCULATION_OR_CROSS_PAPER_TRANSFER"
                ),
                "Source_location": (
                    f"{condition.Evidence_Location}; {state.Evidence_Location}; "
                    f"{mechanical.Evidence_Location}; {target.Condition_Level_Evidence}"
                ),
                "Characterization_methods": (
                    "Pre-test XRD+EBSD; post-test EBSD phase/IPF/GND"
                    if direct
                    else "Pre-test XRD+EBSD; tensile/work-hardening curves not digitized"
                ),
                "Notes": target.Scientific_Justification,
            }
        )
        rows.append(row)
    return rows


def study_identity_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Study_Identity"].copy()
    frame["Source_Family_Status"] = (
        "NEW_SOURCE_NOT_MERGED_WITH_RELATED_NENE_MISHRA_STUDIES"
    )
    frame["Duplicate_DOI_Status"] = "ABSENT_FROM_RECOVERY_V16"
    frame["Evidence_Type"] = "DIRECT_PDF_PLUS_PUBLISHER_MATCH"
    frame["Evidence_Location"] = "p.1 and publisher DOI record"
    frame["Method"] = "Verified source identity review"
    frame["Confidence"] = "High"
    frame["Recovery_Status"] = "VERIFIED"
    return frame


def composition_local_eds_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    source = sheets["P023_Composition_Processing"].iloc[0]
    rows: list[dict] = []
    common = {
        "Paper_ID": PAPER_ID,
        "DOI": DOI,
        "Study_Series_ID": SERIES,
        "Material_Parent_ID": MATERIAL,
        "Composition_Basis": "at.%",
        "Source_URL": f"https://doi.org/{DOI}",
        "Data_Origin": "EXPERIMENTAL",
    }
    rows.append(
        {
            **common,
            "Chemistry_Record_ID": "P023_NOMINAL_COMPOSITION",
            "Processing_State_ID": pd.NA,
            "Chemistry_Scope": "NOMINAL_ALLOY_DESIGN",
            "Composition_String": NOMINAL_COMPOSITION,
            **{f"{element}_at_pct": value for element, value in NOMINAL_ELEMENTS.items()},
            "Measured_Bulk_Composition": pd.NA,
            "Bulk_Chemistry_Use_Status": "NOMINAL_NOT_MEASURED_BULK",
            "Composition_Status": source.Composition_Status,
            "Normalization_Status": "NOT_NORMALIZED_AS_REPORTED",
            "Evidence_Type": "DIRECT_NOMINAL_TEXT",
            "Evidence_Location": "Sec.2.1",
            "Method": "Nominal alloy design",
            "Confidence": "High",
            "Recovery_Status": "VERIFIED",
        }
    )
    rows.append(
        {
            **common,
            "Chemistry_Record_ID": "P023_MEASURED_BULK_GAP",
            "Processing_State_ID": pd.NA,
            "Chemistry_Scope": "MEASURED_BULK_POSTMELT",
            "Composition_String": pd.NA,
            **{f"{element}_at_pct": pd.NA for element in NOMINAL_ELEMENTS},
            "Measured_Bulk_Composition": pd.NA,
            "Bulk_Chemistry_Use_Status": "NOT_REPORTED",
            "Composition_Status": source.Composition_Status,
            "Normalization_Status": "NOT_APPLICABLE_NO_MEASURED_BULK_VALUE",
            "Evidence_Type": "NOT_REPORTED",
            "Evidence_Location": "Whole paper",
            "Method": "Source review",
            "Confidence": "High",
            "Recovery_Status": "VERIFIED_NA",
        }
    )
    for scope, state_id, text_field in [
        ("LOCAL_EDS_AS_CAST", "P023_STATE_ASCAST_SUPPORT", "AsCast_EDS_Composition_atpct"),
        ("LOCAL_EDS_D_PASS", "P023_STATE_DPASS", "DPass_EDS_Composition_atpct"),
    ]:
        values = parse_composition_string(getattr(source, text_field))
        rows.append(
            {
                **common,
                "Chemistry_Record_ID": f"P023_{scope}",
                "Processing_State_ID": state_id,
                "Chemistry_Scope": scope,
                "Composition_String": getattr(source, text_field),
                **{
                    f"{element}_at_pct": values[element]
                    for element in NOMINAL_ELEMENTS
                },
                "Measured_Bulk_Composition": pd.NA,
                "Bulk_Chemistry_Use_Status": (
                    "LOCAL_ONLY_EXCLUDED_FROM_BULK_CHEMISTRY"
                ),
                "Composition_Status": source.Composition_Status,
                "Normalization_Status": "NOT_NORMALIZED_LOCAL_EDS_AS_REPORTED",
                "Evidence_Type": "DIRECT_LOCAL_EDS_ELEMENTAL_DISTRIBUTION",
                "Evidence_Location": "Fig.1e",
                "Method": "Local EDS elemental-distribution measurement",
                "Confidence": "High",
                "Recovery_Status": "VERIFIED_LOCAL_ONLY",
            }
        )
    return pd.DataFrame(rows)


def fsp_processing_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    source = sheets["P023_Composition_Processing"].iloc[0]
    return pd.DataFrame(
        [
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": MATERIAL,
                "Processing_Record_ID": "P023_CAST_FSP_ROUTE",
                "Casting_Route": source.Casting_Route,
                "Vacuum_Level_Raw": source.Vacuum_Level_Raw,
                "Backfill_Atmosphere": source.Backfill_Atmosphere,
                "Ingot_Dimensions_mm": source.Ingot_Dimensions_mm,
                "FSP_Pass1_rpm": float(source.FSP_Pass1_rpm),
                "FSP_Pass2_rpm": float(source.FSP_Pass2_rpm),
                "FSP_Traverse_mm_min": float(source.FSP_Traverse_mm_min),
                "FSP_Plunge_mm": float(source.FSP_Plunge_mm),
                "FSP_Tilt_deg": float(source.FSP_Tilt_deg),
                "FSP_Backplate": source.FSP_Backplate,
                "FSP_Shielding": source.FSP_Shielding,
                "AsCast_Grain_Size_um": 120.0,
                "AsCast_Grain_Size_SD_um": 12.0,
                "AsCast_Grain_Size_Status": (
                    "SUPPORTING_MATERIAL_STATE_NOT_PRIMARY_TENSILE_CONDITION"
                ),
                "DPass_Grain_Size_um": 0.79,
                "DPass_Grain_Size_SD_um": 0.05,
                "DPass_Grain_Size_Status": "DIRECT_REPORTED_PRIMARY_DPASS_STATE",
                "Evidence_Type": "DIRECT_TEXT_AND_REPORTED_GRAIN_SIZE",
                "Evidence_Location": (
                    "Sec.2.1; Fig.1e pp.2-3; casting/FSP grain-size evidence "
                    "from verified recovery specification"
                ),
                "Method": "Casting/FSP source review; reported grain-size results",
                "Confidence": "High",
                "Recovery_Status": "VERIFIED",
                "Data_Origin": "EXPERIMENTAL",
                "Source_URL": f"https://doi.org/{DOI}",
            }
        ]
    )


def processing_states_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Processing_States"].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["Primary_Tensile_Condition_ID"] = frame.Processing_State_ID.map(
        CONDITION_BY_STATE
    )
    frame["Supporting_Record_Status"] = "SUPPORTING_PRETEST_PROCESSING_STATE"
    frame["Primary_Tensile_Status"] = frame.Primary_Tensile_Condition_ID.map(
        lambda value: (
            "HAS_PRIMARY_TENSILE_CONDITION"
            if is_present(value)
            else "SUPPORTING_ONLY_NO_CONDITION_SPECIFIC_TENSILE_RESULT"
        )
    )
    frame["Counting_Status"] = "DOES_NOT_COUNT_SEPARATELY_FROM_PRIMARY_CONDITION"
    frame["Evidence_Type"] = "DIRECT_FIG2C_PRETEST_PHASE_FRACTION"
    frame["Method"] = "EBSD/XRD reported summary"
    frame["Recovery_Status"] = "VERIFIED_PRETEST_STATE"
    frame["Data_Origin"] = "EXPERIMENTAL"
    return frame


def phase_fractions_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    states = processing_states_table(sheets)
    fields = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
        "Processing_State_ID",
        "Processing_State",
        "Primary_Tensile_Condition_ID",
        "Anneal_T_C",
        "Anneal_Time_min",
        "Post_Anneal_Quench",
        "Initial_FCC_fraction",
        "Initial_HCP_fraction",
        "Phase_Fraction_SD_pct",
        "Phase_Fraction_Method",
        "Independent_Experimental_ML_sample",
        "Supporting_Record_Status",
        "Primary_Tensile_Status",
        "Counting_Status",
        "Evidence_Type",
        "Evidence_Location",
        "Method",
        "Confidence",
        "Recovery_Status",
        "Data_Origin",
        "Notes",
        "Source_URL",
    ]
    return states[fields].copy()


def tensile_conditions_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Tensile_Conditions"].copy()
    frame["Observation_ID"] = frame.ML_Condition_ID.map(PRIMARY_OBSERVATION_IDS)
    frame["Observation_Role"] = "INDEPENDENT_CONDITION"
    frame["Independent_ML_sample"] = True
    frame["Experimental_Target_Eligibility"] = True
    frame["Pseudo_Replicate_Status"] = "NO_PSEUDO_REPLICATES_CREATED"
    frame["Replicate_Status"] = (
        "AGGREGATE_N3_PER_CONDITION_NO_INDIVIDUAL_ROWS"
    )
    frame["Counting_Status"] = "COUNTS_AS_ONE_INDEPENDENT_CONDITION"
    frame["Evidence_Type"] = "DIRECT_TENSILE_METHODS_TEXT"
    frame["Method"] = "Source-defined tensile condition hierarchy"
    frame["Recovery_Status"] = "VERIFIED_PRIMARY_CONDITION"
    frame["Data_Origin"] = "EXPERIMENTAL"
    return frame


def mechanical_response_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Mechanical_Response"].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["Processing_State_ID"] = frame.ML_Condition_ID.map(STATE_BY_CONDITION)
    frame["Stress_Basis_Safeguard"] = frame.ML_Condition_ID.map(
        lambda condition_id: (
            "ENGINEERING_YS_UTS_TOTAL_ELONGATION"
            if condition_id == "P023_MC_650_15_RT"
            else (
                "TRUE_TENSILE_STRENGTH_AND_UNIFORM_ELONGATION_NOT_CONVERTED_TO_ENGINEERING"
                if condition_id == "P023_MC_650_30_RT"
                else "FIGURE_ONLY_NOT_DIGITIZED"
            )
        )
    )
    frame["SDI_Leakage_Status"] = frame.SDI_MPa.map(
        lambda value: (
            "OUTCOME_DERIVED_MECHANICAL_LEAKAGE"
            if is_present(value)
            else "NOT_RECOVERED"
        )
    )
    frame["Curve_Digitization_Status"] = (
        "NOT_DIGITIZED_DIRECT_TEXT_VALUES_ONLY"
    )
    frame["Evidence_Type"] = frame.Value_Status.map(
        lambda status: (
            "DIRECT_TEXT"
            if str(status).startswith("DIRECT_TEXT")
            else "VERIFIED_NA_FIGURE_ONLY_NOT_DIGITIZED"
        )
    )
    frame["Method"] = "Tensile response; no curve digitization"
    frame["Recovery_Status"] = "VERIFIED_OR_VERIFIED_NA"
    frame["Data_Origin"] = "EXPERIMENTAL"
    return frame


def precipitation_state_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    states = processing_states_table(sheets)
    frame = states[
        [
            "Paper_ID",
            "DOI",
            "Study_Series_ID",
            "Material_Parent_ID",
            "Processing_State_ID",
            "Processing_State",
            "Primary_Tensile_Condition_ID",
            "Anneal_T_C",
            "Anneal_Time_min",
            "Precipitate_State",
            "Independent_Experimental_ML_sample",
            "Evidence_Location",
            "Confidence",
            "Notes",
            "Source_URL",
        ]
    ].copy()
    frame["Matrix_Al_Content_Trend"] = frame.Anneal_T_C.map(
        lambda value: (
            "DECREASES_WITH_ANNEALING_TIME_QUALITATIVE_ONLY"
            if is_present(value)
            else pd.NA
        )
    )
    frame["Annealed_Grain_Size_Status"] = frame.Anneal_T_C.map(
        lambda value: (
            "FIG3G_NOT_DIGITIZED_QUALITATIVE_GRAIN_GROWTH_ONLY"
            if is_present(value)
            else "D_PASS_DIRECT_GRAIN_SIZE_REPORTED_SEPARATELY"
        )
    )
    frame["Al_Content_Status"] = (
        "FIG3H_NOT_DIGITIZED_QUALITATIVE_TREND_ONLY"
    )
    frame["PreTest_Status"] = "PRE_TEST_MICROSTRUCTURE"
    frame["Counting_Status"] = "SUPPORT_ONLY_NOT_AN_INDEPENDENT_CONDITION"
    frame["Evidence_Type"] = "DIRECT_QUALITATIVE_MICROSTRUCTURE_OR_VERIFIED_NA"
    frame["Evidence_Location"] = "Sec.3.2; Fig.3g-h"
    frame["Method"] = "Pre-test microscopy/EDS interpretation; no curve digitization"
    frame["Recovery_Status"] = "VERIFIED_QUALITATIVE_OR_VERIFIED_NA"
    frame["Data_Origin"] = "EXPERIMENTAL"
    return frame


def before_after_evidence_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    frame = sheets["P023_Deformation_Evidence"].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["ML_Condition_ID"] = frame.Parent_ML_Condition_ID
    frame["Processing_State_ID"] = frame.ML_Condition_ID.map(STATE_BY_CONDITION)
    frame["Predictor_Eligibility"] = (
        "POST_TEST_TARGET_EVIDENCE_NOT_PRETEST_PREDICTOR"
    )
    frame["Counting_Status"] = "CORRELATED_SUPPORT_ONLY_NO_NEW_SAMPLE"
    frame["Initial_HCP_Target_Guardrail"] = (
        "PRETEST_HCP_ALONE_DOES_NOT_ESTABLISH_TENSILE_TRIP"
    )
    frame["Phase_Specific_TWIP_Safeguard"] = (
        "HCP_EPSILON_TWIP_NOT_FCC_DEFORMATION_TWINNING"
    )
    frame["Evidence_Type"] = "DIRECT_BEFORE_AFTER_EBSD_PHASE_AND_TWIN_EVIDENCE"
    frame["Recovery_Status"] = "VERIFIED_POST_TEST_TARGET_EVIDENCE"
    frame["Data_Origin"] = "EXPERIMENTAL"
    return frame


def target_evidence_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Target_Evidence"].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["Processing_State_ID"] = frame.ML_Condition_ID.map(STATE_BY_CONDITION)
    frame["Initial_HCP_Target_Guardrail"] = (
        "PRETEST_HCP_ALONE_DOES_NOT_ESTABLISH_TENSILE_TRIP"
    )
    frame["WH_Curve_Label_Safeguard"] = (
        "WORK_HARDENING_CURVE_SHAPE_ALONE_DOES_NOT_ASSIGN_BINARY_TARGET"
    )
    frame["Evidence_Type"] = "CONDITION_LEVEL_TARGET_EVIDENCE_REVIEW"
    frame["Method"] = "Direct evidence grading under project target definitions"
    frame["Recovery_Status"] = "VERIFIED_TARGET_DECISION"
    frame["Data_Origin"] = "EXPERIMENTAL"
    return frame


def wh_onset_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    features = {
        "TRIP_Onset_True_Stress",
        "TRIP_Onset_Engineering_Stress_Approx",
        "TRIP_Onset_Strain_Approx",
        "WH_Rate_at_Slope_Change",
    }
    frame = sheets["P023_Physics_Onset"]
    frame = frame[frame.Feature.isin(features)].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["Processing_State_ID"] = frame.ML_Condition_ID.map(STATE_BY_CONDITION)
    frame["Direct_Stage_Status"] = (
        "NO_DIRECT_EXPERIMENTAL_STAGE_CREATED_FROM_CURVE_INFERENCE"
    )
    frame["Evidence_Type"] = frame.Feature.map(
        lambda feature: (
            "CURRENT_PAPER_MECHANICAL_RESPONSE_DERIVED"
            if feature == "WH_Rate_at_Slope_Change"
            else "CURRENT_PAPER_CURVE_INFERRED_MECHANISM_ONSET"
        )
    )
    frame["Recovery_Status"] = "VERIFIED_CURVE_INFERENCE_NOT_DIRECT_STAGE"
    frame["Data_Origin"] = "EXPERIMENTAL"
    return frame


def thermocalc_context_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Physics_Onset"]
    frame = frame[frame.Feature.eq("ThermoCalc_Database")].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["ML_Condition_ID"] = pd.NA
    frame["Processing_State_ID"] = pd.NA
    frame["Software"] = "Thermo-Calc"
    frame["Observation_Safeguard"] = (
        "MODEL_PREDICTIONS_DO_NOT_OVERRIDE_EBSD_XRD_OBSERVATIONS"
    )
    frame["Measured_Phase_Fraction_Use"] = (
        "NOT_USED_AS_MEASURED_PHASE_FRACTION"
    )
    frame["Evidence_Type"] = "CURRENT_PAPER_THERMODYNAMIC_MODEL_CONTEXT"
    frame["Recovery_Status"] = "VERIFIED_MODEL_CONTEXT_ONLY"
    frame["Data_Origin"] = "EXPERIMENTAL_WITH_CALPHAD_CONTEXT"
    return frame


def sfe_deltag_gaps_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Physics_Onset"]
    frame = frame[frame.Feature.isin({"SFE_numeric", "DeltaG_FCC_HCP"})].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["ML_Condition_ID"] = pd.NA
    frame["Processing_State_ID"] = pd.NA
    frame["Cross_Paper_Transfer_Status"] = frame.Feature.map(
        {
            "SFE_numeric": "NO_IMPORT_FROM_CITED_FE_MN_SI_OR_RELATED_HEA_LITERATURE",
            "DeltaG_FCC_HCP": "NO_CALCULATION_OR_CROSS_PAPER_TRANSFER",
        }
    )
    frame["Evidence_Type"] = "CURRENT_PAPER_NUMERIC_GAP"
    frame["Recovery_Status"] = "VERIFIED_NA"
    frame["Data_Origin"] = "EXPERIMENTAL_CURRENT_PAPER_GAP"
    return frame


def decision_ledger(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P023_Integration_Decisions"].copy()
    frame.insert(0, "Paper_ID", PAPER_ID)
    frame.insert(1, "DOI", DOI)
    frame["Study_Series_ID"] = SERIES
    frame["Material_Parent_ID"] = MATERIAL
    frame["Data_Origin"] = "EXPERIMENTAL"
    frame["Legacy_Duplicate_Status"] = (
        "NEW_SOURCE_NO_P023_DOI_REPRESENTATION_IN_V16"
    )
    frame["Source_Family_Status"] = (
        "NOT_MERGED_WITH_RELATED_NENE_MISHRA_STUDIES"
    )
    frame["Correction_Mode"] = "NEW_ROWS_ONLY_NO_RECOVERY_V16_VALUE_OVERWRITE"
    return frame


def build_support_exports(
    sheets: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]:
    return {
        "study_identity": study_identity_table(sheets),
        "composition_local_eds": composition_local_eds_table(sheets),
        "fsp_processing": fsp_processing_table(sheets),
        "processing_states": processing_states_table(sheets),
        "phase_fractions": phase_fractions_table(sheets),
        "tensile_conditions": tensile_conditions_table(sheets),
        "mechanical_response": mechanical_response_table(sheets),
        "precipitation_state": precipitation_state_table(sheets),
        "before_after_evidence": before_after_evidence_table(sheets),
        "target_evidence": target_evidence_table(sheets),
        "wh_onset": wh_onset_table(sheets),
        "thermocalc_context": thermocalc_context_table(sheets),
        "sfe_deltag_gaps": sfe_deltag_gaps_table(sheets),
        "decision_correction_ledger": decision_ledger(sheets),
    }


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
    "P023_Source_Identity_Status",
    "P023_Source_Family_Status",
}
HIERARCHY_FIELDS = {
    "Condition_ID",
    "Experiment_Group_ID",
    "Parent_Experiment_ID",
    "ML_Condition_ID",
    "Parent_ML_Condition_ID",
    "Observation_ID",
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
    "Replicate_Scope",
    "Leakage_Group_Strict",
    "Leakage_Group_Material",
    "Grouping_Confidence",
    "Grouping_Review_Required",
    "Grouping_Reason",
    "P023_Record_Role",
    "P023_QC_Status",
}
COMPOSITION_FIELDS = {
    "Alloy_ID",
    "Alloy_Family_Text",
    "Alloy_Family_Use",
    "Original_Composition",
    "Original_Composition_Basis",
    "Composition_basis",
    "Nominal_Composition_at_pct",
    "Normalized_Composition_at_pct",
    "Composition_Normalization_Status",
    "Fe_at%",
    "Mn_at%",
    "Co_at%",
    "Cr_at%",
    "Si_at%",
    "Al_at%",
    "Other_elements",
    "Measured_Bulk_Composition",
    "Measured_Composition_at_pct",
    "Recovered_Bulk_Composition_at_pct",
    "Measured_Composition_Status",
    "Composition_Status",
    "Recovered_Composition_Status",
    "Local_EDS_AsCast_Composition_at_pct",
    "Local_EDS_DPass_Composition_at_pct",
    "Local_EDS_Chemistry_Status",
    "Local_EDS_Composition_at_pct",
    "Local_EDS_Composition_Scope",
}
PROCESSING_TEST_FIELDS = {
    "Processing_State_ID",
    "Processing_State",
    "Processing_route",
    "Melting_Route",
    "Cast_method",
    "Casting_Route",
    "Vacuum_Level_Raw",
    "Backfill_Atmosphere",
    "Cast_Ingot_Dimensions_mm",
    "FSP_Pass1_Rotation_rpm",
    "FSP_Pass2_Rotation_rpm",
    "FSP_Traverse_Speed_mm_min",
    "FSP_Plunge_Depth_mm",
    "FSP_Tilt_deg",
    "FSP_Backplate",
    "FSP_Shielding",
    "Anneal_T_C_Raw",
    "Annealing_T_K",
    "Annealing_time_min",
    "Post_Anneal_Quench",
    "Cooling_route",
    "Test_T_Raw",
    "Test_T_K",
    "Test_T_C",
    "Test_T_Status",
    "Strain_rate_s-1",
    "Strain_Rate_Status",
    "Loading_Mode",
    "Gauge_length_mm",
    "Gauge_width_mm",
    "Specimen_thickness_mm",
    "Test_Metadata_Status",
}
INITIAL_FIELDS = {
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
    "PreTest_Phase_Fraction_SD_pct",
    "PreTest_Phase_Fraction_Method",
    "PreTest_Phase_Fraction_Status",
    "Phase_Fraction_Methods",
    "Grain_size_um",
    "Grain_size_SD_um",
    "Recovered_Grain_size_um",
    "Recovered_Grain_size_scope",
    "Grain_Size_Status",
    "Precipitate_type",
    "Precipitate_State",
    "Matrix_Al_Content_Trend",
    "AsCast_Support_Grain_Size_um",
    "AsCast_Support_Grain_Size_SD_um",
    "AsCast_Grain_Size_Use_Status",
    "Annealed_Grain_Size_Digitization_Status",
    "Al_Content_Curve_Digitization_Status",
}
MECHANICAL_FIELDS = {
    "Engineering_YS_MPa",
    "Engineering_UTS_MPa",
    "Engineering_Elongation_pct",
    "YS_MPa",
    "UTS_MPa",
    "Elongation_pct",
    "Reported_Ultimate_Strength_MPa",
    "Reported_Elongation_pct",
    "True_UTS_MPa",
    "True_Tensile_Strength_MPa",
    "Uniform_elongation_pct",
    "SDI_MPa",
    "Mechanical_Value_Status",
    "Mechanical_Predictor_Eligibility",
    "SDI_Predictor_Eligibility",
    "Mechanical_Stress_Basis_Status",
    "Mechanical_Value_Approximation_Status",
    "Tensile_Curve_Digitization_Status",
}
TARGET_FIELDS = {
    "Original_TRIP",
    "Original_TWIP",
    "Recovered_TRIP",
    "Recovered_TWIP",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
    "Target_Status",
    "P023_Target_Status",
    "TRIP_Parent_Phase",
    "TRIP_Product_Phase",
    "TWIP_Phase",
    "TWIP_Mode",
    "TRIP_Evidence_Type",
    "TWIP_Evidence_Type",
    "Slip_Evidence_Type",
    "Negative_Evidence_Status",
    "Condition_Level_Target_Evidence",
    "Target_Evidence_Confidence",
    "Label_confidence",
    "Evidence_TRIP",
    "Evidence_TWIP",
    "Phase_Specific_TWIP_Safeguard",
}
POSTTEST_FIELDS = {
    "PostTest_FCC_fraction",
    "PostTest_HCP_fraction",
    "PostTest_Phase_Fraction_Method",
    "PostTest_Evidence_Status",
    "PostTest_Predictor_Eligibility",
    "PostTest_Twin_Evidence",
    "PostTest_Slip_Evidence",
    "PostTest_GND_Evidence_Status",
    "PostTest_IPF_Evidence_Status",
}
ONSET_FIELDS = {
    "TRIP_Onset_True_Stress_MPa",
    "TRIP_Onset_Engineering_Stress_Approx_MPa",
    "TRIP_Onset_Strain_Approx_pct",
    "WH_Rate_at_Slope_Change_MPa",
    "TRIP_Onset_Evidence_Status",
    "TRIP_Onset_Predictor_Eligibility",
    "WH_Rate_Predictor_Eligibility",
    "Direct_Stage_Fabrication_Status",
}
THERMO_PHYSICS_FIELDS = {
    "ThermoCalc_Software",
    "ThermoCalc_Database",
    "ThermoCalc_Context_Status",
    "ThermoCalc_Observation_Safeguard",
    "SFE_mJ_m2",
    "SFE_method",
    "SFE_Value_Status",
    "SFE_Data_Origin",
    "SFE_Predictor_Eligibility",
    "SFE_Transfer_Safeguard",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
    "DeltaG_Value_Status",
    "DeltaG_Data_Origin",
    "DeltaG_Transfer_Safeguard",
}


def _units(feature: str) -> str:
    if feature in UNIT_MAP:
        return UNIT_MAP[feature]
    if feature == "Phase_Fraction_SD_pct":
        return "percentage points"
    if feature.endswith("_fraction"):
        return "fraction"
    if feature.endswith("_at_pct"):
        return "at.%"
    if feature.endswith("_rpm"):
        return "rpm"
    if feature.endswith("_mm_min"):
        return "mm/min"
    if feature.endswith("_um"):
        return "um"
    if feature.endswith("_mm"):
        return "mm"
    if feature.endswith("_MPa"):
        return "MPa"
    if feature.endswith("_pct"):
        return "%"
    if feature.endswith("_T_C") or feature == "Anneal_T_C":
        return "C"
    if feature.endswith("_T_K"):
        return "K"
    return "as reported"


def _master_field_metadata(
    feature: str, record: dict
) -> tuple[str, str, str]:
    source_location = record.get(
        "Source_location", "Verified P023 scientific-evidence workbook"
    )
    if feature in IDENTITY_FIELDS:
        return (
            "SOURCE_IDENTITY",
            "p.1 and publisher DOI record",
            "Verified PDF and publisher DOI identity",
        )
    if feature in HIERARCHY_FIELDS:
        return (
            "HIERARCHY_INTEGRATION",
            "P023 tensile-condition and processing-state sheets",
            "Source-defined condition hierarchy and aggregate replicate scope",
        )
    if feature in COMPOSITION_FIELDS:
        return (
            "DIRECT_NOMINAL_OR_LOCAL_EDS_OR_VERIFIED_NA",
            "Sec.2.1; Fig.1e pp.2-3",
            "Nominal composition and scope-separated local EDS review",
        )
    if feature in PROCESSING_TEST_FIELDS:
        return (
            "DIRECT_PROCESSING_OR_TENSILE_METHODS_TEXT",
            "Sec.2.1 and Sec.2.3",
            "Casting/FSP/annealing and tensile-method mapping",
        )
    if feature in INITIAL_FIELDS:
        return (
            "DIRECT_PRETEST_EBSD_XRD_OR_QUALITATIVE_MICROSTRUCTURE",
            "Figs.1-3; Sec.3.1-3.2",
            "Pre-test processing-state evidence; no curve digitization",
        )
    if feature in MECHANICAL_FIELDS:
        return (
            "DIRECT_TEXT_OR_VERIFIED_NA_NO_CURVE_DIGITIZATION",
            source_location,
            "Tensile-response review with stress/strain basis preserved",
        )
    if feature in TARGET_FIELDS:
        return (
            "CONDITION_LEVEL_TARGET_EVIDENCE",
            source_location,
            "Direct before/after phase evidence or conservative NA decision",
        )
    if feature in POSTTEST_FIELDS:
        return (
            "DIRECT_POST_TEST_TARGET_EVIDENCE_OR_VERIFIED_NA",
            source_location,
            "EBSD phase/IPF/GND evidence kept outside pre-test predictors",
        )
    if feature in ONSET_FIELDS:
        return (
            "CURRENT_PAPER_CURVE_INFERRED_OR_MECHANICAL_RESPONSE_DERIVED",
            "Sec.3.3-4; Fig.4c pp.4,6",
            "Work-hardening slope analysis; no direct stage created",
        )
    if feature in THERMO_PHYSICS_FIELDS:
        return (
            "THERMODYNAMIC_MODEL_CONTEXT_OR_VERIFIED_CURRENT_PAPER_GAP",
            "Fig.1a; Fig.5f; whole-paper review",
            "Thermo-Calc context without observation override or cross-paper transfer",
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
        return "VERIFIED_NA_NO_BULK_POSTMELT_CHEMISTRY_LOCAL_EDS_ONLY"
    if feature == "Normalized_Composition_at_pct":
        return "VERIFIED_NA_NO_COMPOSITION_NORMALIZATION"
    if feature in {"Physical_Batch_ID", "Replicate_ID"}:
        return "VERIFIED_NA_NOT_SOURCE_SUPPORTED_NO_PSEUDOREPLICATION"
    if feature in {"Test_T_K", "Test_T_C"}:
        return "VERIFIED_NA_ROOM_TEMPERATURE_NOT_NUMERICALLY_REPORTED"
    if feature in {"Effective_TRIP", "Effective_TWIP", "Slip"}:
        return "VERIFIED_NA_INSUFFICIENT_CONDITION_SPECIFIC_DIRECT_EVIDENCE"
    if feature in MECHANICAL_FIELDS:
        return "VERIFIED_NA_NOT_EXPLICIT_TEXT_NO_CURVE_DIGITIZATION"
    if feature in POSTTEST_FIELDS:
        return "VERIFIED_NA_NO_CONDITION_SPECIFIC_POSTTEST_VALUE_RECOVERED"
    if feature in ONSET_FIELDS:
        return "VERIFIED_NA_NO_CONDITION_SPECIFIC_ONSET_RECOVERED"
    if feature in {"SFE_mJ_m2", "SFE_method"}:
        return "VERIFIED_NA_NO_CURRENT_PAPER_ALLOY_SPECIFIC_NUMERIC_SFE"
    if feature in {"DeltaG_FCC_HCP_J_mol", "DeltaG_method"}:
        return "VERIFIED_NA_NOT_REPORTED_NO_CALCULATION_OR_TRANSFER"
    return "VERIFIED_NA_NOT_SOURCE_SUPPORTED"


def _predictor_eligibility(feature: str) -> str:
    if feature in MECHANICAL_FIELDS:
        return "MECHANICAL_OUTCOME_LEAKAGE"
    if feature in TARGET_FIELDS:
        return "TARGET_OR_TARGET_EVIDENCE_NOT_PREDICTOR"
    if feature in POSTTEST_FIELDS:
        return "POST_TEST_TARGET_EVIDENCE_NOT_PRETEST_PREDICTOR"
    if feature in ONSET_FIELDS:
        return "MODEL_CURVE_INFERENCE_OR_MECHANICAL_OUTCOME_NOT_PREDICTOR"
    if feature in THERMO_PHYSICS_FIELDS:
        return "CONDITIONAL_CONTEXT_OR_GAP_NOT_DIRECT_NUMERIC_PREDICTOR"
    if feature in IDENTITY_FIELDS or feature in HIERARCHY_FIELDS:
        return "IDENTITY_GROUPING_OR_AUDIT_CONTROL"
    if feature in COMPOSITION_FIELDS and "Local_EDS" in feature:
        return "LOCAL_CHEMISTRY_NOT_BULK_COMPOSITION"
    return "AUDIT_SCOPE_DEPENDENT"


def _provenance_scopes(record_id: str) -> list[str | None]:
    if record_id in {SERIES, MATERIAL, "P023_SFE", "P023_DELTAG"}:
        return list(EXACT_IDS)
    if record_id in STATE_ORDER:
        return [CONDITION_BY_STATE.get(record_id)]
    if record_id in EXACT_IDS:
        return [record_id]
    if record_id in DEFORMATION_RECORD_BY_CONDITION.values():
        reverse = {
            evidence_id: condition_id
            for condition_id, evidence_id in DEFORMATION_RECORD_BY_CONDITION.items()
        }
        return [reverse[record_id]]
    if record_id in {"P023_65015_TRIP_ONSET", "P023_65015_WH"}:
        return ["P023_MC_650_15_RT"]
    raise AssertionError(f"unknown P023 provenance record scope: {record_id}")


def _append_workbook_provenance(
    rows: list[dict], sheets: dict[str, pd.DataFrame]
) -> None:
    for source in sheets["P023_Provenance"].to_dict("records"):
        record_id = str(source["Record_ID"])
        for condition_id in _provenance_scopes(record_id):
            state_id = (
                STATE_BY_CONDITION[condition_id]
                if condition_id in STATE_BY_CONDITION
                else (record_id if record_id in STATE_ORDER else pd.NA)
            )
            observation_id = (
                PRIMARY_OBSERVATION_IDS[condition_id]
                if condition_id in PRIMARY_OBSERVATION_IDS
                else record_id
            )
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIAL,
                    "ML_Condition_ID": condition_id if condition_id else pd.NA,
                    "Processing_State_ID": state_id,
                    "Observation_ID": observation_id,
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
                    "Source_Table": "P023_Provenance",
                }
            )


SUPPORT_PROVENANCE_SKIP = {
    "Paper_ID",
    "DOI",
    "Study_Series_ID",
    "Material_Parent_ID",
    "ML_Condition_ID",
    "Parent_ML_Condition_ID",
    "Primary_Tensile_Condition_ID",
    "Processing_State_ID",
    "Observation_ID",
    "Evidence_Record_ID",
    "Chemistry_Record_ID",
    "Processing_Record_ID",
    "Record_ID",
    "Decision_ID",
    "Evidence_Type",
    "Evidence_Location",
    "Method",
    "Confidence",
    "Recovery_Status",
    "Data_Origin",
    "Source_URL",
    "Notes",
    "Scientific_Justification",
}


def _support_record_id(table_name: str, row: pd.Series, index: int) -> str:
    for field in [
        "Evidence_Record_ID",
        "Chemistry_Record_ID",
        "Processing_Record_ID",
        "Record_ID",
        "ML_Condition_ID",
        "Processing_State_ID",
        "Decision_ID",
    ]:
        value = row.get(field, pd.NA)
        if is_present(value):
            return str(value)
    return f"P023_{table_name.upper()}_{index + 1:03d}"


def _support_condition_id(row: pd.Series) -> object:
    for field in [
        "ML_Condition_ID",
        "Parent_ML_Condition_ID",
        "Primary_Tensile_Condition_ID",
    ]:
        value = row.get(field, pd.NA)
        if is_present(value) and str(value) in EXACT_IDS:
            return str(value)
    state_id = row.get("Processing_State_ID", pd.NA)
    if is_present(state_id):
        return CONDITION_BY_STATE.get(str(state_id), pd.NA)
    return pd.NA


def _support_evidence_type(table_name: str, row: pd.Series) -> str:
    value = row.get("Evidence_Type", pd.NA)
    if is_present(value):
        return str(value)
    return {
        "study_identity": "SOURCE_IDENTITY",
        "composition_local_eds": "SCOPE_SEPARATED_CHEMISTRY",
        "fsp_processing": "CASTING_FSP_PROCESSING",
        "processing_states": "PRETEST_PROCESSING_STATE",
        "phase_fractions": "PRETEST_PHASE_FRACTION",
        "tensile_conditions": "TENSILE_CONDITION_HIERARCHY",
        "mechanical_response": "MECHANICAL_RESPONSE",
        "precipitation_state": "PRETEST_PRECIPITATION_STATE",
        "before_after_evidence": "POSTTEST_TARGET_EVIDENCE",
        "target_evidence": "TARGET_DECISION",
        "wh_onset": "CURVE_INFERRED_ONSET",
        "thermocalc_context": "THERMODYNAMIC_MODEL_CONTEXT",
        "sfe_deltag_gaps": "CURRENT_PAPER_NUMERIC_GAP",
    }[table_name]


def _support_predictor_eligibility(table_name: str) -> str:
    if table_name == "mechanical_response":
        return "MECHANICAL_OUTCOME_LEAKAGE"
    if table_name in {"before_after_evidence", "target_evidence"}:
        return "TARGET_OR_POSTTEST_EVIDENCE_NOT_PREDICTOR"
    if table_name == "wh_onset":
        return "MODEL_CURVE_INFERENCE_OR_MECHANICAL_OUTCOME_NOT_PREDICTOR"
    if table_name == "thermocalc_context":
        return "CONDITIONAL_MODEL_CONTEXT_ONLY"
    if table_name == "sfe_deltag_gaps":
        return "NO_CURRENT_PAPER_NUMERIC_VALUE"
    if table_name == "composition_local_eds":
        return "SCOPE_DEPENDENT_LOCAL_EDS_NEVER_BULK"
    return "AUDIT_SCOPE_DEPENDENT"


def _append_support_provenance(
    rows: list[dict], exports: dict[str, pd.DataFrame]
) -> None:
    for table_name, frame in exports.items():
        if table_name == "decision_correction_ledger":
            continue
        for index, row in frame.reset_index(drop=True).iterrows():
            record_id = _support_record_id(table_name, row, index)
            condition_id = _support_condition_id(row)
            state_id = row.get("Processing_State_ID", pd.NA)
            observation_id = (
                PRIMARY_OBSERVATION_IDS[str(condition_id)]
                if is_present(condition_id) and str(condition_id) in EXACT_IDS
                else record_id
            )
            evidence_location = row.get(
                "Evidence_Location", "Verified P023 recovery evidence"
            )
            if not is_present(evidence_location):
                evidence_location = "Verified P023 recovery evidence"
            method = row.get("Method", "Verified support-table mapping")
            if not is_present(method):
                method = "Verified support-table mapping"
            confidence = row.get("Confidence", "High")
            if not is_present(confidence):
                confidence = "High"
            for feature, value in row.items():
                if feature in SUPPORT_PROVENANCE_SKIP:
                    continue
                if not is_present(value) and feature not in SUPPORT_MEANINGFUL_NA:
                    continue
                rows.append(
                    {
                        "Paper_ID": PAPER_ID,
                        "DOI": DOI,
                        "Study_Series_ID": SERIES,
                        "Material_Parent_ID": MATERIAL,
                        "ML_Condition_ID": condition_id,
                        "Processing_State_ID": state_id,
                        "Observation_ID": observation_id,
                        "Record_ID": record_id,
                        "Feature_Name": feature,
                        "Recovered_Value": (
                            value if is_present(value) else "UNRESOLVED_NA"
                        ),
                        "Units": _units(feature),
                        "Evidence_Type": _support_evidence_type(table_name, row),
                        "Evidence_Location": evidence_location,
                        "Method": method,
                        "Confidence": confidence,
                        "Recovery_Status": (
                            "VERIFIED"
                            if is_present(value)
                            else "VERIFIED_NA_NOT_SOURCE_SUPPORTED"
                        ),
                        "Data_Origin": row.get("Data_Origin", "EXPERIMENTAL"),
                        "Source_URL": f"https://doi.org/{DOI}",
                        "Predictor_Eligibility": _support_predictor_eligibility(
                            table_name
                        ),
                        "Provenance_Layer": "SUPPORT_TABLE_FIELD_MAPPING",
                        "Source_Table": (
                            f"p023_recovery_v17_{table_name}.csv"
                        ),
                    }
                )


def build_provenance(
    new_rows: list[dict],
    sheets: dict[str, pd.DataFrame],
    support_exports: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: list[dict] = []
    for record in new_rows:
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            if not is_present(value) and feature not in MEANINGFUL_NA_PRIMARY:
                continue
            evidence_type, evidence_location, method = _master_field_metadata(
                feature, record
            )
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIAL,
                    "ML_Condition_ID": record["ML_Condition_ID"],
                    "Processing_State_ID": record["Processing_State_ID"],
                    "Observation_ID": record["Observation_ID"],
                    "Record_ID": record["Observation_ID"],
                    "Feature_Name": feature,
                    "Recovered_Value": (
                        value if is_present(value) else "UNRESOLVED_NA"
                    ),
                    "Units": _units(feature),
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
                    "Predictor_Eligibility": _predictor_eligibility(feature),
                    "Provenance_Layer": "MASTER_FIELD_MAPPING",
                    "Source_Table": "master_extended_recovery_v17.csv",
                }
            )
    _append_workbook_provenance(rows, sheets)
    _append_support_provenance(rows, support_exports)
    frame = pd.DataFrame(rows).drop_duplicates(ignore_index=True)
    required = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
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
    assert frame.Paper_ID.eq(PAPER_ID).all()
    assert frame.DOI.eq(DOI).all()
    master = frame[frame.Provenance_Layer.eq("MASTER_FIELD_MAPPING")]
    assert master.ML_Condition_ID.isin(EXACT_IDS).all()
    assert master.Processing_State_ID.isin(CONDITION_BY_STATE).all()
    return frame


def attach_provenance_json(
    new_rows: list[dict], provenance: pd.DataFrame
) -> None:
    for row in new_rows:
        selected = provenance[
            provenance.ML_Condition_ID.eq(row["ML_Condition_ID"])
            & provenance.Provenance_Layer.isin(
                {"MASTER_FIELD_MAPPING", "VERIFIED_WORKBOOK_LEDGER"}
            )
        ]
        row["P023_Recovery_Provenance_JSON"] = json.dumps(
            json_ready(selected.to_dict("records")),
            ensure_ascii=False,
            allow_nan=False,
        )


def validate(
    source: pd.DataFrame,
    out: pd.DataFrame,
    sheets: dict[str, pd.DataFrame],
    provenance: pd.DataFrame,
    support_exports: dict[str, pd.DataFrame],
    new_rows: list[dict],
) -> None:
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    assert duplicate_rows(source).empty
    p023 = out[out.Paper_ID.eq(PAPER_ID)].copy()
    assert len(out) == len(source) + len(EXACT_IDS)
    assert len(p023) == len(EXACT_IDS) == 7
    assert p023.Observation_Role.eq("INDEPENDENT_CONDITION").all()
    primary = p023.set_index("ML_Condition_ID", drop=False)
    assert tuple(primary.index) == EXACT_IDS
    assert primary.DOI.eq(DOI).all()
    assert primary.Study_Series_ID.eq(SERIES).all()
    assert primary.Material_Parent_ID.eq(MATERIAL).all()
    assert primary.Material_Parent_ID.nunique() == 1
    assert primary.Leakage_Group_Strict.eq(SERIES).all()
    assert primary.Leakage_Group_Material.eq(MATERIAL).all()
    assert primary.Independent_ML_sample.eq(True).all()
    assert primary.Independent_Experimental_ML_sample.eq(True).all()
    assert primary.Experimental_Target_Eligibility.eq(True).all()
    assert primary.Parent_Experiment_ID.eq(primary.ML_Condition_ID).all()
    assert primary.Parent_ML_Condition_ID.eq(primary.ML_Condition_ID).all()
    assert primary.Observation_ID.nunique() == 7
    assert primary.Physical_Batch_ID.isna().all()
    assert primary.Replicate_ID.isna().all()
    assert primary.Replicate_n.astype(float).eq(3).all()
    assert not primary.Processing_State_ID.isin(SUPPORT_ONLY_750_STATES).any()
    assert not primary.Condition_ID.str.contains("REP", case=False).any()

    assert primary.Original_Composition.eq(NOMINAL_COMPOSITION).all()
    assert primary.Nominal_Composition_at_pct.eq(NOMINAL_COMPOSITION).all()
    assert primary.Original_Composition_Basis.eq(
        "NOMINAL_AT_PERCENT_AS_REPORTED"
    ).all()
    assert primary.Composition_basis.eq("at.% nominal").all()
    for element, expected in NOMINAL_ELEMENTS.items():
        assert primary[f"{element}_at%"].astype(float).eq(expected).all()
    assert primary.Normalized_Composition_at_pct.isna().all()
    assert primary.Measured_Bulk_Composition.isna().all()
    assert primary.Measured_Composition_at_pct.isna().all()
    assert primary.Recovered_Bulk_Composition_at_pct.isna().all()
    assert primary.Composition_Status.eq(
        "NOMINAL_PLUS_LOCAL_EDS_NO_BULK_POSTMELT_CHEMISTRY"
    ).all()
    assert primary.Local_EDS_Chemistry_Status.eq(
        "LOCAL_EDS_ELEMENTAL_DISTRIBUTION_TABLE_NOT_BULK_CHEMISTRY"
    ).all()
    assert primary.Local_EDS_AsCast_Composition_at_pct.eq(
        "Fe40.2 Mn19.7 Co20.5 Cr14.4 Si4.6 Al0.7"
    ).all()
    assert primary.Local_EDS_DPass_Composition_at_pct.eq(
        "Fe39.0 Mn19.8 Co20.0 Cr15.9 Si4.3 Al1.03"
    ).all()

    assert primary.Cast_method.eq(
        "Vacuum arc casting in cold-copper crucible"
    ).all()
    assert primary.Vacuum_Level_Raw.eq("~300 um vacuum").all()
    assert primary.Backfill_Atmosphere.eq("Ar to 1 atm").all()
    assert primary.Cast_Ingot_Dimensions_mm.eq("300 x 100 x 6").all()
    assert primary.FSP_Pass1_Rotation_rpm.astype(float).eq(350).all()
    assert primary.FSP_Pass2_Rotation_rpm.astype(float).eq(150).all()
    assert primary.FSP_Traverse_Speed_mm_min.astype(float).eq(50.8).all()
    assert primary.FSP_Plunge_Depth_mm.astype(float).eq(3.65).all()
    assert primary.FSP_Tilt_deg.astype(float).eq(2).all()
    assert primary.FSP_Backplate.eq("Cu").all()
    assert primary.FSP_Shielding.eq("Ar near tool/specimen interface").all()

    assert primary.Test_T_Raw.eq("room temperature").all()
    assert primary.Test_T_K.isna().all()
    assert primary.Test_T_C.isna().all()
    assert primary["Strain_rate_s-1"].astype(float).eq(1e-3).all()
    assert primary.Loading_Mode.eq("Uniaxial tension").all()
    assert primary.Gauge_length_mm.astype(float).eq(5).all()
    assert primary.Gauge_width_mm.astype(float).eq(1.25).all()
    assert primary.Specimen_thickness_mm.astype(float).eq(1).all()

    for condition_id, state_id in STATE_BY_CONDITION.items():
        row = primary.loc[condition_id]
        expected_fcc, expected_hcp, expected_sd = EXPECTED_PHASES[state_id]
        assert float(row.Initial_FCC_fraction) == expected_fcc
        assert float(row.Initial_HCP_fraction) == expected_hcp
        assert float(row.PreTest_Phase_Fraction_SD_pct) == expected_sd
        assert (
            row.PreTest_Phase_Fraction_Method
            == "XRD_PLUS_EBSD_REPORTED_SUMMARY"
        )
        assert (
            row.Initial_HCP_Target_Guardrail
            == "PRETEST_HCP_IS_NOT_DEFORMATION_INDUCED_TRIP_EVIDENCE"
        )
    dpass = primary.loc["P023_MC_DPASS_RT"]
    assert float(dpass.Grain_size_um) == 0.79
    assert float(dpass.Grain_size_SD_um) == 0.05
    assert primary.drop(index="P023_MC_DPASS_RT").Grain_size_um.isna().all()
    assert primary.AsCast_Support_Grain_Size_um.astype(float).eq(120).all()
    assert primary.AsCast_Support_Grain_Size_SD_um.astype(float).eq(12).all()

    for condition_id, expected in EXPECTED_TARGETS.items():
        row = primary.loc[condition_id]
        for field, expected_value in zip(
            ["Effective_TRIP", "Effective_TWIP", "Slip"], expected
        ):
            _assert_expected_value(row[field], expected_value)
    assert primary.loc[list(DIRECT_JOINT_IDS), "Effective_TRIP"].astype(float).eq(
        1
    ).all()
    assert primary.loc[list(DIRECT_JOINT_IDS), "Effective_TWIP"].astype(float).eq(
        1
    ).all()
    assert primary.loc[list(DIRECT_JOINT_IDS), "Slip"].astype(float).eq(1).all()
    assert primary.loc[list(DIRECT_JOINT_IDS), "TWIP_Phase"].eq(
        "HCP_EPSILON"
    ).all()
    assert primary.loc[list(UNRESOLVED_IDS), [
        "Effective_TRIP",
        "Effective_TWIP",
        "Slip",
    ]].isna().all().all()
    assert primary.loc[list(UNRESOLVED_IDS), "Negative_Evidence_Status"].eq(
        "INSUFFICIENT_FOR_ZERO"
    ).all()
    assert not primary.Effective_TRIP.eq(0).any()
    assert not primary.Effective_TWIP.eq(0).any()
    assert primary.Phase_Specific_TWIP_Safeguard.eq(
        "HCP_EPSILON_TWIP_NOT_SILENTLY_RECODED_AS_FCC_TWIP"
    ).all()

    for condition_id, expected in EXPECTED_POSTTEST.items():
        row = primary.loc[condition_id]
        assert float(row.Initial_FCC_fraction) == expected[0]
        assert float(row.Initial_HCP_fraction) == expected[1]
        assert float(row.PostTest_FCC_fraction) == expected[2]
        assert float(row.PostTest_HCP_fraction) == expected[3]
        assert row.PostTest_Evidence_Status == "POST_TEST_TARGET_EVIDENCE"
        assert (
            row.PostTest_Predictor_Eligibility
            == "POST_TEST_TARGET_EVIDENCE_NOT_PRETEST_PREDICTOR"
        )

    m65015 = primary.loc["P023_MC_650_15_RT"]
    assert float(m65015.Engineering_YS_MPa) == 610
    assert float(m65015.Engineering_UTS_MPa) == 1120
    assert float(m65015.Engineering_Elongation_pct) == 52
    assert float(m65015.SDI_MPa) == 425
    assert m65015.SDI_Predictor_Eligibility == (
        "OUTCOME_DERIVED_MECHANICAL_LEAKAGE"
    )
    m65030 = primary.loc["P023_MC_650_30_RT"]
    assert float(m65030.True_Tensile_Strength_MPa) == 1630
    assert float(m65030.True_UTS_MPa) == 1630
    assert float(m65030.Uniform_elongation_pct) == 43
    assert pd.isna(m65030.Engineering_UTS_MPa)
    assert pd.isna(m65030.Engineering_Elongation_pct)
    figure_only_ids = [
        "P023_MC_DPASS_RT",
        "P023_MC_650_5_RT",
        "P023_MC_850_5_RT",
        "P023_MC_850_15_RT",
        "P023_MC_850_30_RT",
    ]
    exact_mechanical_fields = [
        "Engineering_YS_MPa",
        "Engineering_UTS_MPa",
        "Engineering_Elongation_pct",
        "True_Tensile_Strength_MPa",
        "Uniform_elongation_pct",
        "SDI_MPa",
    ]
    assert primary.loc[figure_only_ids, exact_mechanical_fields].isna().all().all()
    assert primary.Mechanical_Predictor_Eligibility.eq(
        "MECHANICAL_OUTCOME_LEAKAGE"
    ).all()

    assert float(m65015.TRIP_Onset_True_Stress_MPa) == 924
    assert float(m65015.TRIP_Onset_Engineering_Stress_Approx_MPa) == 840
    assert float(m65015.TRIP_Onset_Strain_Approx_pct) == 10
    assert float(m65015.WH_Rate_at_Slope_Change_MPa) == 2983
    assert (
        m65015.TRIP_Onset_Evidence_Status
        == "CURRENT_PAPER_CURVE_INFERRED_MECHANISM_ONSET"
    )
    assert (
        m65015.TRIP_Onset_Predictor_Eligibility
        == "MODEL_CURVE_INFERENCE_NOT_DIRECT_STAGE"
    )
    assert primary.Direct_Stage_Fabrication_Status.eq(
        "NO_DIRECT_EXPERIMENTAL_STAGE_CREATED_FROM_CURVE_INFERENCE"
    ).all()
    assert not p023.Observation_Role.eq("DIRECT_EXPERIMENTAL_STAGE").any()
    assert len(p023) == 7

    assert primary.ThermoCalc_Software.eq("Thermo-Calc").all()
    assert primary.ThermoCalc_Database.eq("TCHEA2").all()
    assert primary.ThermoCalc_Observation_Safeguard.eq(
        "EQUILIBRIUM_PREDICTIONS_DO_NOT_OVERRIDE_EBSD_XRD_OBSERVATIONS"
    ).all()
    assert primary.SFE_mJ_m2.isna().all()
    assert primary.SFE_method.isna().all()
    assert primary.DeltaG_FCC_HCP_J_mol.isna().all()
    assert primary.DeltaG_method.isna().all()

    states = support_exports["processing_states"]
    phases = support_exports["phase_fractions"]
    hierarchy = support_exports["tensile_conditions"]
    assert len(states) == len(phases) == 10
    assert tuple(states.Processing_State_ID) == STATE_ORDER
    assert tuple(phases.Processing_State_ID) == STATE_ORDER
    assert len(hierarchy) == 7
    assert tuple(hierarchy.ML_Condition_ID) == EXACT_IDS
    support_750 = states[states.Processing_State_ID.isin(SUPPORT_ONLY_750_STATES)]
    assert len(support_750) == 3
    assert support_750.Primary_Tensile_Condition_ID.isna().all()
    assert support_750.Primary_Tensile_Status.eq(
        "SUPPORTING_ONLY_NO_CONDITION_SPECIFIC_TENSILE_RESULT"
    ).all()
    assert states.Independent_Experimental_ML_sample.eq(False).all()
    assert hierarchy.Independent_Experimental_ML_sample.eq(True).all()
    assert hierarchy.Replicate_n.astype(float).eq(3).all()
    assert hierarchy.Pseudo_Replicate_Status.eq(
        "NO_PSEUDO_REPLICATES_CREATED"
    ).all()

    before = counts(source)
    after = counts(out)
    assert tuple(after[index] - before[index] for index in range(4)) == (
        7,
        2,
        2,
        2,
    )
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    expected_class_delta = {
        "trip_positive": 2,
        "trip_negative": 0,
        "twip_positive": 2,
        "twip_negative": 0,
        "joint_00": 0,
        "joint_10": 0,
        "joint_01": 0,
        "joint_11": 2,
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
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            if not is_present(value) and feature not in MEANINGFUL_NA_PRIMARY:
                continue
            matching = master_provenance[
                master_provenance.Observation_ID.eq(record["Observation_ID"])
                & master_provenance.Feature_Name.eq(feature)
            ]
            assert len(matching), (record["Observation_ID"], feature)
    assert p023.P023_Recovery_Provenance_JSON.str.len().gt(2).all()
    expected_support_sources = {
        f"p023_recovery_v17_{name}.csv"
        for name in support_exports
        if name != "decision_correction_ledger"
    }
    actual_support_sources = set(
        provenance.loc[
            provenance.Provenance_Layer.eq("SUPPORT_TABLE_FIELD_MAPPING"),
            "Source_Table",
        ]
    )
    assert expected_support_sources <= actual_support_sources

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
        if field in p023:
            assert p023[field].isna().all()
    assert file_hash(SOURCE) == SOURCE_SHA256
    assert file_hash(BOOK) == BOOK_SHA256


def write_audit(source: pd.DataFrame, out: pd.DataFrame) -> None:
    before = counts(source)
    after = counts(out)
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    states = ", ".join(STATE_ORDER)
    conditions = ", ".join(EXACT_IDS)
    audit = f"""# P023 recovery v17 audit

## A. Source identity

- Paper_ID=P023; DOI={DOI}.
- Title: {TITLE}.
- {JOURNAL}, volume {VOLUME}, pages {PAGES} ({YEAR}); Data_Origin=EXPERIMENTAL.
- The verified workbook identity matches the PDF/publisher DOI record. Both workbook and recovery-v16 base are SHA-256 gated; integration rejects a mismatch.

## B. Duplicate/source-family status

- Exact recovery-v16 DOI matches: {len(duplicate_rows(source))}; P023 Paper_ID matches: {int(source.Paper_ID.eq(PAPER_ID).sum())}.
- P023 is appended as a new source beyond P022 under {SERIES}. It is not merged with related Nene/Mishra papers on the basis of authors, FSP route, or alloy family; such relationships remain audit-only context.

## C. V17 row count

- V17 contains {len(out)} rows: the complete {len(source)}-row recovery-v16 prefix plus exactly seven primary P023 tensile conditions.
- No 750 C support state, replicate, before/after evidence row, or curve-inferred stage was appended to the master.

## D. Experimental count before/after

- Replacement-aware independent experimental conditions: {before[0]} before -> {after[0]} after.
- The +{after[0] - before[0]} change is exactly the seven requested primary P023 conditions.

## E. Seven exact tensile conditions

- {conditions}.
- Each is an independent source-defined room-temperature tensile condition under one strict study/material leakage group.

## F. Ten supporting processing states

- Exactly ten pre-test processing-state phase records are retained: {states}.
- P023_STATE_750_5, P023_STATE_750_15, and P023_STATE_750_30 are supporting-only because the paper does not provide condition-specific tensile results for them.

## G. Nominal chemistry

- Nominal chemistry is exactly {NOMINAL_COMPOSITION} at.%: Fe39, Mn20, Co20, Cr15, Si5, Al1.
- Values are source-reported nominal fractions; no normalization or derived composition descriptor was calculated.

## H. Local EDS vs bulk-chemistry safeguard

- Measured bulk/post-melt chemistry remains NA.
- As-cast local EDS is Fe40.2 Mn19.7 Co20.5 Cr14.4 Si4.6 Al0.7 at.%; D-pass local EDS is Fe39.0 Mn19.8 Co20.0 Cr15.9 Si4.3 Al1.03 at.%.
- Both are stored as LOCAL_EDS_ELEMENTAL_DISTRIBUTION_TABLE_NOT_BULK_CHEMISTRY and never overwrite nominal or bulk chemistry.

## I. FSP processing

- Vacuum arc casting in a cold-copper crucible retains raw vacuum notation `~300 um vacuum`, Ar backfill to 1 atm, and 300 x 100 x 6 mm ingot dimensions.
- Double-pass FSP retains 350/150 rpm, 50.8 mm/min traverse, 3.65 mm plunge, 2 degree tilt, Cu backing plate, and Ar shielding near the tool/specimen interface.

## J. Annealing grid

- D-pass specimens were annealed at 650, 750, and 850 C for 5, 15, and 30 min and water quenched.
- Only D-pass, 650-X, and 850-X states with reported tensile conditions enter the seven-row master addition; 750-X remains support-only.

## K. Pre-test phase fractions

- Exact FCC/HCP/SD percentage-point records are: D-pass 0.83/0.17/3.9; 650-5 0.86/0.14/4.2; 650-15 0.30/0.70/3.5; 650-30 0.55/0.45/2.2; 750-5 0.79/0.21/0.4; 750-15 0.72/0.28/4.1; 750-30 0.88/0.12/1.0; 850-5 0.95/0.05/0.2; 850-15 0.97/0.03/2.3; 850-30 0.43/0.57/4.3.
- All are PRE_TENSILE_PROCESSING_STATE evidence from the Fig.2c EBSD/XRD summary. Initial HCP never establishes tensile TRIP.

## L. Precipitation handling

- 650-X fine/controlled precipitation, 650-15 fine Al-rich precipitates, 850-X stronger precipitation/grain growth, 850-15 large Al-rich grain-boundary precipitates, and 850-30 massive Al-rich precipitation/grain growth are retained as pre-test microstructure.
- Fig.3g annealed grain sizes and Fig.3h matrix-Al values were not digitized. Only the qualitative decrease in matrix Al with annealing time is retained.

## M. D-pass grain size

- D-pass grain size is 0.79 +/- 0.05 um. As-cast 120 +/- 12 um is retained only as supporting material-state information.
- No annealed numeric grain size was created from Fig.3g.

## N. Room-temperature/strain-rate metadata

- Test_T_Raw=room temperature; exact Test_T_K and Test_T_C remain NA.
- Initial strain rate is 1e-3 s^-1, loading is uniaxial tension, and gauge length/width/thickness are 5/1.25/1 mm.

## O. Replicate handling

- Replicate_n=3 records the source statement that three specimens were tested per condition.
- Physical_Batch_ID and Replicate_ID remain NA. No pseudo-replicate or individual result row was created.

## P. 650-15 direct TRIP

- P023_MC_650_15_RT is Effective_TRIP=1 because direct before/after EBSD shows FCC 0.30 -> 0.06 and HCP epsilon 0.70 -> 0.94 during tensile deformation.
- The pre-test HCP=0.70 alone is not TRIP evidence; the tensile phase change is.

## Q. 650-15 HCP-TWIP/slip

- P023_MC_650_15_RT is Effective_TWIP=1 and Slip=1 from directly reported epsilon-HCP twinning and <c+a> slip.
- TWIP_Phase=HCP_EPSILON; it is not recoded as FCC deformation twinning.

## R. 850-30 direct TRIP

- P023_MC_850_30_RT is Effective_TRIP=1 because direct before/after EBSD shows FCC 0.43 -> 0.10 and HCP epsilon 0.57 -> 0.90 during tensile deformation.

## S. 850-30 HCP-TWIP/slip

- P023_MC_850_30_RT is Effective_TWIP=1 and Slip=1 from directly reported epsilon-phase twinning and <c+a> slip.
- TWIP_Phase=HCP_EPSILON.

## T. Five unresolved targets

- {", ".join(UNRESOLVED_IDS)} retain Effective_TRIP/Effective_TWIP/Slip=NA and Negative_Evidence_Status=INSUFFICIENT_FOR_ZERO.
- Work-hardening/stress-strain curve shape, missing microscopy, and initial HCP create neither positive nor negative labels.

## U. WH-derived TRIP onset classification

- For 650-15, the reported 924 MPa true-stress onset, approximately 840 MPa engineering stress, approximately 10% associated strain/elongation, and 2983 MPa WH rate are retained.
- The onset is CURRENT_PAPER_CURVE_INFERRED_MECHANISM_ONSET / MODEL_CURVE_INFERENCE_NOT_DIRECT_STAGE; the WH rate is mechanical-response-derived leakage. No direct interrupted-test stage was fabricated.

## V. Post-test leakage handling

- The 650-15 and 850-30 post-test phase fractions, twins, IPF/GND/dislocation evidence, and slip observations are POST_TEST_TARGET_EVIDENCE.
- They are excluded from pre-test predictor semantics and remain supporting/target evidence only.

## W. HCP-vs-FCC TWIP semantics

- Both direct P023 TWIP positives are explicitly HCP_EPSILON twinning.
- This task preserves source truth without globally redefining TWIP target semantics; later schema/QC refresh must retain the phase tag.

## X. Thermo-Calc context

- Thermo-Calc with database TCHEA2 is retained as current-paper thermodynamic/model context only.
- Equilibrium phase-stability predictions are not measured phase fractions and do not override EBSD/XRD observations.

## Y. SFE gap

- No current-paper alloy-specific numeric SFE is reported. SFE_mJ_m2 remains NA and no cited Fe-Mn-Si/HEA value was imported.

## Z. DeltaG gap

- No current-paper numeric FCC->HCP DeltaG is reported. DeltaG_FCC_HCP_J_mol remains NA; no value was calculated or transferred.

## AA. Before/after usable target counts

- Usable TRIP/TWIP/joint counts: {before[1]}/{before[2]}/{before[3]} before -> {after[1]}/{after[2]}/{after[3]} after.
- TRIP positive/negative: {before_classes["trip_positive"]}/{before_classes["trip_negative"]} -> {after_classes["trip_positive"]}/{after_classes["trip_negative"]}; TWIP positive/negative: {before_classes["twip_positive"]}/{before_classes["twip_negative"]} -> {after_classes["twip_positive"]}/{after_classes["twip_negative"]}.
- Joint states before: 00={before_classes["joint_00"]}, 10={before_classes["joint_10"]}, 01={before_classes["joint_01"]}, 11={before_classes["joint_11"]}; after: 00={after_classes["joint_00"]}, 10={after_classes["joint_10"]}, 01={after_classes["joint_01"]}, 11={after_classes["joint_11"]}.
- Programmatic deltas are +{after[0] - before[0]} independent, +{after[1] - before[1]} usable TRIP, +{after[2] - before[2]} usable TWIP, and +{after[3] - before[3]} usable joint.

## AB. Remaining P023 gaps

- Quantitative measured bulk chemistry; physical-batch and individual-replicate identities/results; exact numeric room temperature; annealed numeric grain sizes; digitized matrix-Al values; exact mechanics for D-pass/650-5/850-5/850-15/850-30; direct condition-specific target evidence for the five unresolved conditions; numeric SFE; and DeltaG remain unresolved.

## AC. Later global refresh requirement

- Yes: Global QC, feature coverage/schema statistics, and grouped split artifacts require a non-destructive refresh after paper collection pauses and before matrix construction.
- They were intentionally not refreshed in this recovery-only task. No ML matrix, model, feature engineering, imputation, normalization, descriptor calculation, curve digitization, resampling, or synthetic record was created.
"""
    AUDIT.write_text(audit, encoding="utf-8")


def integrate() -> tuple[pd.DataFrame, pd.DataFrame]:
    source, sheets = load_and_verify()
    out = source.copy()
    for column in NEW_COLUMNS:
        if column not in out:
            out[column] = pd.NA

    primary_rows = make_primary_rows(list(out.columns), sheets)
    support_exports = build_support_exports(sheets)
    provenance = build_provenance(primary_rows, sheets, support_exports)
    attach_provenance_json(primary_rows, provenance)
    out = pd.concat(
        [
            out.astype(object),
            pd.DataFrame(primary_rows, columns=out.columns).astype(object),
        ],
        ignore_index=True,
    )
    validate(
        source,
        out,
        sheets,
        provenance,
        support_exports,
        primary_rows,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    for name, frame in support_exports.items():
        frame.to_csv(TABLE / f"p023_recovery_v17_{name}.csv", index=False)
    provenance.to_csv(TABLE / "p023_recovery_v17_provenance.csv", index=False)
    write_audit(source, out)
    return source, out


if __name__ == "__main__":
    integrate()
