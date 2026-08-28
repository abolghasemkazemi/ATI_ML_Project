"""Integrate verified P021 evidence into extended recovery v15.

Dataset recovery only: the complete recovery-v14 input remains an immutable
prefix. Exactly five source-defined experimental tensile conditions are
appended. No pseudo-replicates, post-test child rows, feature engineering,
imputation, normalization, descriptor calculation, or model training occurs.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_extended_recovery_v14.csv"
BOOK = (
    ROOT
    / "data/interim/manual_recovery/P021_scientific_evidence_recovery_VERIFIED.xlsx"
)
OUT = ROOT / "data/processed/master_extended_recovery_v15.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P021_RECOVERY_V15_AUDIT.md"

PAPER_ID = "P021"
DOI = "10.1016/j.jallcom.2021.162765"
TITLE = (
    "Enhancement in mechanical properties through an FCC-to-HCP phase "
    "transformation in an Fe-17.5Mn-10Co-12.5Cr-5Ni-5Si (in at%) "
    "medium-entropy alloy"
)
JOURNAL = "Journal of Alloys and Compounds"
VOLUME = 898
ARTICLE_NUMBER = "162765"
YEAR = 2022
SERIES = "P021_SERIES01"
MATERIAL = "P021_MAT_FE50MN17p5CR12p5CO10NI5SI5"
NOMINAL_COMPOSITION = "Fe50Mn17.5Cr12.5Co10Ni5Si5"

SOURCE_SHA256 = "478e085b2fef3f7ea0c5cbad4e5bcead6f22f66e32528c5410e037d7d29aa5cf"
BOOK_SHA256 = "ad55be697812022b93ac3e91e73ccf268af94d93eb794e06e25dcf840ba08334"

EXACT_IDS = (
    "P021_MC_A900_5M_RT_G10",
    "P021_MC_A900_25M_RT_G19",
    "P021_MC_A1000_20M_RT_G41",
    "P021_MC_A1000_150M_RT_G150",
    "P021_MC_A1000_20M_77K_G41",
)
RT_IDS = EXACT_IDS[:4]
RT40_ID = "P021_MC_A1000_20M_RT_G41"
CRYO_ID = "P021_MC_A1000_20M_77K_G41"
CHARACTERIZED_IDS = {RT40_ID, CRYO_ID}

EXPECTED_GRID = {
    "P021_MC_A900_5M_RT_G10": (900.0, 5.0, 10.0, 298.0, "25 C"),
    "P021_MC_A900_25M_RT_G19": (900.0, 25.0, 19.5, 298.0, "25 C"),
    "P021_MC_A1000_20M_RT_G41": (1000.0, 20.0, 40.9, 298.0, "25 C"),
    "P021_MC_A1000_150M_RT_G150": (
        1000.0,
        150.0,
        149.6,
        298.0,
        "25 C",
    ),
    "P021_MC_A1000_20M_77K_G41": (
        1000.0,
        20.0,
        40.9,
        77.0,
        "liquid nitrogen / 77 K",
    ),
}

EXPECTED_MECHANICS = {
    "P021_MC_A900_5M_RT_G10": (310.0, 769.0, 63.0),
    "P021_MC_A900_25M_RT_G19": (292.0, 736.0, 64.0),
    "P021_MC_A1000_20M_RT_G41": (249.0, 688.0, 58.0),
    "P021_MC_A1000_150M_RT_G150": (228.0, 643.0, 59.0),
    "P021_MC_A1000_20M_77K_G41": (540.0, 1410.0, 51.0),
}

EXPECTED_TARGETS = {
    "P021_MC_A900_5M_RT_G10": (pd.NA, pd.NA, pd.NA),
    "P021_MC_A900_25M_RT_G19": (pd.NA, pd.NA, pd.NA),
    "P021_MC_A1000_20M_RT_G41": (1, 1, 1),
    "P021_MC_A1000_150M_RT_G150": (pd.NA, pd.NA, pd.NA),
    "P021_MC_A1000_20M_77K_G41": (1, pd.NA, 1),
}

REQUIRED_SHEETS = {
    "P021_Study_Identity",
    "P021_Conditions",
    "P021_Initial_Microstructure",
    "P021_Mechanical_Response",
    "P021_Postfracture_Evidence",
    "P021_Target_Evidence",
    "P021_Physics_SFE",
    "P021_HallPetch_Support",
    "P021_Integration_Decisions",
    "P021_Provenance",
}

NEW_COLUMNS = [
    "P021_Record_Role",
    "P021_Target_Status",
    "P021_Source_Identity_Status",
    "P021_QC_Status",
    "P021_Recovery_Provenance_JSON",
    "Article_Number",
    "Replicate_n_Status",
    "Remelt_Count_Min",
    "Remelt_Count_Status",
    "Alloy_Mass_g_Approx",
    "Remolded_Ingot_Dimensions_mm",
    "Homogenization_T_C_Raw",
    "Hot_Roll_T_C_Raw",
    "Hot_Roll_Final_Thickness_mm",
    "Anneal_T_C_Raw",
    "Post_Anneal_Quench",
    "Test_T_C",
    "Test_Atmosphere",
    "Specimen_Orientation",
    "Specimen_Standard",
    "Initial_Alpha_BCT_fraction",
    "Initial_Secondary_Phase_Status",
    "Fully_Recrystallized",
    "Grain_Size_Method",
    "Grain_Size_Twin_Boundary_Exclusion",
    "Initial_Stacking_Fault_State",
    "Initial_Stacking_Fault_State_Raw",
    "PreTest_Cryogenic_Immersion",
    "PreTest_State_Timing",
    "Postfracture_Evidence_Method",
    "Postfracture_HCP_fraction_scope",
    "Postfracture_Predictor_Eligibility",
    "Postfracture_Mechanical_Twin_Status",
    "Slip_StackingFault_Status",
    "Alpha_BCT_Transformation_Status",
    "Alpha_BCT_Transformation_Evidence",
    "Alpha_BCT_Target_Safeguard",
    "TWIP_Evidence_Abundance",
    "TWIP_Evidence_Strength",
    "SFE_Raw_Bound",
    "SFE_Bound_Status",
    "SFE_Predictor_Eligibility",
    "SFE_Qualitative_Temperature_Status",
]

MEANINGFUL_NA_FIELDS = {
    "Measured_Bulk_Composition",
    "Measured_Composition_at_pct",
    "Recovered_Bulk_Composition_at_pct",
    "Physical_Batch_ID",
    "Replicate_ID",
    "Initial_FCC_fraction",
    "Recovered_Initial_FCC_fraction",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
    "Postfracture_HCP_fraction",
    "HCP_fraction_at_condition",
    "SFE_mJ_m2",
    "SFE_method",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
}

PROVENANCE_EXCLUDE = {
    "P021_Recovery_Provenance_JSON",
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
    "Fe_at%": "at.%",
    "Mn_at%": "at.%",
    "Cr_at%": "at.%",
    "Co_at%": "at.%",
    "Ni_at%": "at.%",
    "Si_at%": "at.%",
    "Remelt_Count_Min": "count",
    "Alloy_Mass_g_Approx": "g",
    "Homogenization_T_C_Raw": "C",
    "Homogenization_T_K": "K",
    "Homogenization_time_h": "h",
    "Hot_Roll_T_C_Raw": "C",
    "Hot_rolling_T_K": "K",
    "Hot_Roll_Final_Thickness_mm": "mm",
    "Cold_rolling_reduction_pct": "%",
    "Anneal_T_C_Raw": "C",
    "Annealing_T_K": "K",
    "Annealing_time_min": "min",
    "Test_T_C": "C",
    "Test_T_K": "K",
    "Strain_rate_s-1": "s^-1",
    "Replicate_n": "minimum count",
    "Initial_FCC_fraction": "fraction",
    "Initial_HCP_fraction": "fraction",
    "Initial_Alpha_BCT_fraction": "fraction",
    "Recovered_Initial_FCC_fraction": "fraction",
    "Recovered_Initial_HCP_fraction": "fraction",
    "Grain_size_um": "um",
    "Lattice_parameter_nm": "nm",
    "YS_MPa": "MPa",
    "UTS_MPa": "MPa",
    "Elongation_pct": "%",
    "Engineering_YS_MPa": "MPa",
    "Engineering_UTS_MPa": "MPa",
    "Engineering_Elongation_pct": "%",
    "YS_mean": "MPa",
    "UTS_mean": "MPa",
    "TE_mean": "%",
    "Effective_TRIP": "binary",
    "Effective_TWIP": "binary",
    "Recovered_TRIP": "binary",
    "Recovered_TWIP": "binary",
    "Slip": "binary",
    "Postfracture_HCP_fraction": "fraction",
    "HCP_fraction_at_condition": "fraction",
    "SFE_mJ_m2": "mJ/m2",
    "SFE_Raw_Bound": "mJ/m2",
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


def c_to_k(value) -> float:
    """Represent a source-reported Celsius temperature in an existing K field."""
    return float(value) + 273.15


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
    """Apply all established replacement gates before counting conditions."""
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
    return (
        len(pool),
        int(pool.Effective_TRIP.notna().sum()),
        int(pool.Effective_TWIP.notna().sum()),
        int(
            pool[["Effective_TRIP", "Effective_TWIP"]]
            .notna()
            .all(axis=1)
            .sum()
        ),
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


def load_and_verify() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    assert file_hash(SOURCE) == SOURCE_SHA256, (
        "recovery-v14 source changed before P021 integration"
    )
    assert file_hash(BOOK) == BOOK_SHA256, "verified P021 workbook changed"
    source = pd.read_csv(SOURCE, low_memory=False)

    conflicting_id = source[
        source.Paper_ID.eq(PAPER_ID)
        & ~source.DOI.astype("string").str.strip().str.lower().eq(DOI.lower())
    ]
    assert conflicting_id.empty, "P021 Paper_ID exists with a different DOI"
    legacy = duplicate_rows(source)
    assert legacy.empty, (
        "P021 DOI already exists; stop for explicit replacement-aware mapping"
    )
    assert not source.Paper_ID.eq(PAPER_ID).any(), "P021 already exists in v14"

    sheets = pd.read_excel(BOOK, sheet_name=None, dtype=object)
    assert set(sheets) == REQUIRED_SHEETS
    for name, frame in sheets.items():
        if "Paper_ID" in frame:
            assert set(frame.Paper_ID.dropna()) == {PAPER_ID}, name
        if "DOI" in frame:
            assert set(frame.DOI.dropna()) == {DOI}, name

    identity = sheets["P021_Study_Identity"].iloc[0]
    assert identity.Paper_ID == PAPER_ID and identity.DOI == DOI
    assert identity.Title == TITLE and identity.Journal == JOURNAL
    assert int(identity.Volume) == VOLUME
    assert str(identity.Article_Number) == ARTICLE_NUMBER
    assert int(identity.Year) == YEAR
    assert identity.Data_Origin == "EXPERIMENTAL"
    assert identity.Study_Series_ID == SERIES
    assert identity.Material_Parent_ID == MATERIAL
    assert (
        identity.Source_Identity_Status
        == "VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH"
    )

    conditions = sheets["P021_Conditions"].set_index("ML_Condition_ID")
    assert len(conditions) == 5 and set(conditions.index) == set(EXACT_IDS)
    assert conditions.Independent_Experimental_ML_sample.eq(True).all()
    assert conditions.Study_Series_ID.eq(SERIES).all()
    assert conditions.Material_Parent_ID.eq(MATERIAL).all()
    assert conditions.Leakage_Group_Strict.eq(SERIES).all()
    assert conditions.Leakage_Group_Material.eq(MATERIAL).all()
    assert conditions.Physical_Batch_ID.isna().all()
    assert conditions.Replicate_ID.isna().all()
    assert conditions.Replicate_n.astype(float).eq(3).all()
    assert conditions.Replicate_n_Status.eq(
        "MINIMUM_REPORTED_AT_LEAST_THREE"
    ).all()
    assert conditions.Nominal_Composition.eq(NOMINAL_COMPOSITION).all()
    assert conditions.Measured_Bulk_Composition.isna().all()
    assert conditions["Strain_Rate_s-1"].astype(float).eq(1e-3).all()

    micro = sheets["P021_Initial_Microstructure"].set_index("ML_Condition_ID")
    mechanics = sheets["P021_Mechanical_Response"].set_index("ML_Condition_ID")
    targets = sheets["P021_Target_Evidence"].set_index("ML_Condition_ID")
    assert set(micro.index) == set(EXACT_IDS)
    assert set(mechanics.index) == set(EXACT_IDS)
    assert set(targets.index) == set(EXACT_IDS)

    for condition_id, expected in EXPECTED_GRID.items():
        anneal_c, anneal_min, grain_um, test_k, test_raw = expected
        condition = conditions.loc[condition_id]
        initial = micro.loc[condition_id]
        assert float(condition.Anneal_T_C) == anneal_c
        assert float(condition.Anneal_Time_min) == anneal_min
        assert float(condition.Test_T_K) == test_k
        assert condition.Test_T_Raw == test_raw
        assert float(initial.Grain_Size_um) == grain_um
        assert pd.isna(initial.Initial_FCC_fraction)
        assert float(initial.Initial_HCP_fraction) == 0.0
        assert float(initial.Initial_Alpha_BCT_fraction) == 0.0
        assert bool(initial.Fully_Recrystallized)
        assert initial.Initial_Phase_State == "SINGLE_FCC"
        assert initial.Twin_Origin == "ANNEALING_PRETEST"
        assert float(initial.Lattice_a_FCC_nm) == 0.358

    for condition_id, expected in EXPECTED_MECHANICS.items():
        values = mechanics.loc[
            condition_id,
            [
                "Engineering_YS_MPa",
                "Engineering_UTS_MPa",
                "Engineering_Elongation_pct",
            ],
        ].astype(float)
        assert tuple(values) == expected

    assert targets.loc[RT40_ID, "Effective_TRIP"] == 1
    assert targets.loc[RT40_ID, "Effective_TWIP"] == 1
    assert targets.loc[RT40_ID, "Slip"] == 1
    assert targets.loc[CRYO_ID, "Effective_TRIP"] == 1
    assert pd.isna(targets.loc[CRYO_ID, "Effective_TWIP"])
    assert targets.loc[CRYO_ID, "Slip"] == 1
    for condition_id in {EXACT_IDS[0], EXACT_IDS[1], EXACT_IDS[3]}:
        assert targets.loc[
            condition_id, ["Effective_TRIP", "Effective_TWIP", "Slip"]
        ].isna().all()

    post = sheets["P021_Postfracture_Evidence"].set_index("ML_Condition_ID")
    assert set(post.index) == CHARACTERIZED_IDS
    assert float(post.loc[RT40_ID, "HCP_Epsilon_Fraction"]) == 0.149
    assert float(post.loc[CRYO_ID, "HCP_Epsilon_Fraction"]) == 0.562
    assert post.Alpha_BCT_Status.str.startswith("NOT_DETECTED").all()

    physics = sheets["P021_Physics_SFE"]
    sfe_298 = physics[
        physics.Feature.eq("SFE") & physics.Temperature_K.astype(float).eq(298)
    ].iloc[0]
    assert pd.isna(sfe_298.Recovered_Value)
    assert str(sfe_298.Recovered_Value_Raw) == "<23"
    assert (
        sfe_298.Status
        == "AUTHOR_INFERRED_UPPER_BOUND_NOT_DIRECT_MEASUREMENT"
    )
    deltag = physics[physics.Feature.eq("DeltaG_FCC_to_HCP")].iloc[0]
    assert pd.isna(deltag.Recovered_Value)

    hall = sheets["P021_HallPetch_Support"].set_index("Feature")
    assert float(hall.loc["Hall_Petch_sigma0", "Value"]) == 198.0
    assert float(hall.loc["Hall_Petch_k", "Value"]) == 368.0
    assert hall.Predictor_Eligibility.eq("MODEL_DERIVED_LEAKAGE").all()
    return source, sheets


def _row_template(columns: list[str]) -> dict:
    return {column: pd.NA for column in columns}


def _observation_id(condition_id: str) -> str:
    return condition_id.replace("_MC_", "_OBS_")


def make_condition_rows(
    columns: list[str], sheets: dict[str, pd.DataFrame]
) -> list[dict]:
    conditions = sheets["P021_Conditions"].set_index("ML_Condition_ID")
    micro = sheets["P021_Initial_Microstructure"].set_index("ML_Condition_ID")
    mechanics = sheets["P021_Mechanical_Response"].set_index("ML_Condition_ID")
    targets = sheets["P021_Target_Evidence"].set_index("ML_Condition_ID")
    post = sheets["P021_Postfracture_Evidence"].set_index("ML_Condition_ID")
    rows: list[dict] = []

    for condition_id in EXACT_IDS:
        condition = conditions.loc[condition_id]
        initial = micro.loc[condition_id]
        mechanical = mechanics.loc[condition_id]
        target = targets.loc[condition_id]
        is_cryo = condition_id == CRYO_ID
        has_postfracture = condition_id in post.index
        observation_id = _observation_id(condition_id)

        row = _row_template(columns)
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Journal": JOURNAL,
                "Volume": VOLUME,
                "Article_Number": ARTICLE_NUMBER,
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
                "Replicate_n_Status": "MINIMUM_REPORTED_AT_LEAST_THREE",
                "Replicate_Scope": (
                    "AVERAGE_MECHANICAL_VALUES_FROM_AT_LEAST_THREE_"
                    "TENSILE_SPECIMENS"
                ),
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": MATERIAL,
                "Grouping_Confidence": "HIGH",
                "Grouping_Review_Required": False,
                "Grouping_Reason": (
                    "Verified source-defined anneal/grain-size/test-temperature "
                    "condition; five siblings remain in one strict study group"
                ),
                "P021_Record_Role": "RECOVERED_EXACT_PRIMARY_CONDITION",
                "P021_Target_Status": target.Target_Status,
                "P021_Source_Identity_Status": (
                    "VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH"
                ),
                "P021_QC_Status": (
                    "PENDING_GLOBAL_QC_SCHEMA_SPLIT_REFRESH_AFTER_COLLECTION"
                ),
                "Alloy_ID": NOMINAL_COMPOSITION,
                "Alloy_Family_Text": NOMINAL_COMPOSITION,
                "Alloy_Family_Use": (
                    "GROUPING_AUDIT_ONLY_NOT_SAMPLE_OR_BATCH_IDENTITY"
                ),
                "Original_Composition": NOMINAL_COMPOSITION,
                "Nominal_Composition_at_pct": NOMINAL_COMPOSITION,
                "Composition_basis": "at.% nominal",
                "Fe_at%": 50.0,
                "Mn_at%": 17.5,
                "Cr_at%": 12.5,
                "Co_at%": 10.0,
                "Ni_at%": 5.0,
                "Si_at%": 5.0,
                "Measured_Bulk_Composition": pd.NA,
                "Measured_Composition_at_pct": pd.NA,
                "Recovered_Bulk_Composition_at_pct": pd.NA,
                "Measured_Composition_Status": (
                    "NO_QUANTITATIVE_POSTMELT_BULK_ANALYSIS"
                ),
                "Composition_Status": condition.Composition_Status,
                "EDS_Qualitative_Homogeneity": (
                    "QUALITATIVE_HOMOGENIZATION_ONLY_NOT_QUANTITATIVE_"
                    "BULK_CHEMISTRY"
                ),
                "Raw_Material_Purity": ">99.9%",
                "Melting_Route": "Vacuum arc melting under Ar",
                "Cast_method": (
                    "Vacuum arc melting under Ar; flipped/remelted at least "
                    "five times; remolded rectangular ingot"
                ),
                "Remelt_Count_Min": 5,
                "Remelt_Count_Status": "AT_LEAST_FIVE",
                "Alloy_Mass_g_Approx": 150.0,
                "Remolded_Ingot_Dimensions_mm": "65 x 40 x 10",
                "Homogenization_T_C_Raw": 1150.0,
                "Homogenization_T_K": c_to_k(1150.0),
                "Homogenization_time_h": 24.0,
                "Hot_Roll_T_C_Raw": 1100.0,
                "Hot_rolling_T_K": c_to_k(1100.0),
                "Hot_Roll_Final_Thickness_mm": 3.0,
                "Cold_rolling_reduction_pct": 30.0,
                "Anneal_T_C_Raw": float(condition.Anneal_T_C),
                "Annealing_T_K": c_to_k(condition.Anneal_T_C),
                "Annealing_time_min": float(condition.Anneal_Time_min),
                "Cooling_route": "Water quench",
                "Post_Anneal_Quench": "Water quench",
                "Processing_route": (
                    "Vacuum arc melted under Ar from >99.9% raw materials; "
                    "flipped/remelted at least five times; approximately 150 g "
                    "alloy remolded to 65 x 40 x 10 mm; homogenized 1150 C/24 h; "
                    "hot rolled at 1100 C to 3 mm; cold rolled 30%; final "
                    f"anneal {float(condition.Anneal_T_C):g} C/"
                    f"{float(condition.Anneal_Time_min):g} min; water quenched"
                ),
                "Test_T_Raw": condition.Test_T_Raw,
                "Test_T_C": pd.NA if is_cryo else 25.0,
                "Test_T_K": float(condition.Test_T_K),
                "Test_Atmosphere": (
                    "LIQUID_NITROGEN_ATMOSPHERE" if is_cryo else pd.NA
                ),
                "Strain_rate_s-1": float(condition["Strain_Rate_s-1"]),
                "Loading_Mode": "Uniaxial tension",
                "Loading_Direction": "Longitudinal / rolling direction",
                "Specimen_Orientation": "Longitudinal / rolling direction",
                "Specimen_Standard": "ASTM E8/E8M sub-size",
                "Initial_Phase": "SINGLE_FCC",
                "Initial_Phase_State_Qualitative": "SINGLE_FCC",
                "Initial_Phase_Status": (
                    "FULLY_RECRYSTALLIZED_SINGLE_FCC_BEFORE_TENSILE_LOADING"
                ),
                "Initial_FCC_fraction": pd.NA,
                "Recovered_Initial_FCC_fraction": pd.NA,
                "Initial_HCP_fraction": 0.0,
                "Recovered_Initial_HCP_fraction": 0.0,
                "Recovered_Initial_HCP_status": (
                    "DIRECT_PRETEST_PHASE_ABSENCE"
                ),
                "Initial_HCP_Status": "DIRECT_PRETEST_PHASE_ABSENCE",
                "Initial_HCP_Origin": "ABSENT_BEFORE_TENSILE_LOADING",
                "Initial_Alpha_BCT_fraction": 0.0,
                "Initial_Secondary_Phase_Status": (
                    "NO_OBVIOUS_PRECIPITATES_OR_OTHER_PHASES"
                ),
                "Fully_Recrystallized": True,
                "Recrystallized_Status": "FULLY_RECRYSTALLIZED_QUALITATIVE",
                "Grain_size_um": float(initial.Grain_Size_um),
                "Grain_Size_Method": initial.Grain_Size_Method,
                "Grain_Size_Scope": (
                    "MATRIX_GRAINS_EXCLUDING_ANNEALING_TWIN_BOUNDARIES"
                ),
                "Grain_Size_Status": (
                    "DIRECT_EBSD_BSE_TWIN_BOUNDARIES_EXCLUDED"
                ),
                "Grain_Size_Twin_Boundary_Exclusion": True,
                "Initial_twin_boundary_status": "Abundant annealing twins",
                "Initial_Twin_Type": "ANNEALING_TWINS",
                "PreTest_Twin_State": "ABUNDANT_ANNEALING_TWINS",
                "PreTest_Twin_Origin": "ANNEALING_PRETEST",
                "Initial_Twin_Origin": "ANNEALING_PRETEST",
                "Initial_Twin_Target_Guardrail": (
                    "ANNEALING_TWINS_DO_NOT_GENERATE_TENSILE_TWIP"
                ),
                "Initial_TRIP_Target_Guardrail": (
                    "INITIAL_SINGLE_FCC_AND_HCP_ZERO_DO_NOT_ALONE_ASSIGN_TRIP"
                ),
                "Initial_Dislocation_State": initial.Initial_Dislocation_State,
                "Initial_Stacking_Fault_State": (
                    "PROFUSE_PRETEST_STACKING_FAULTS"
                    if is_cryo
                    else "NO_QUANTITATIVE_INITIAL_STACKING_FAULT_METRIC_REPORTED"
                ),
                "Initial_Stacking_Fault_State_Raw": (
                    initial.Initial_Stacking_Fault_State
                ),
                "PreTest_Cryogenic_Immersion": bool(
                    initial.PreTest_Cryogenic_Immersion
                ),
                "PreTest_State_Timing": "BEFORE_TENSILE_LOADING",
                "Lattice_parameter_nm": float(initial.Lattice_a_FCC_nm),
                "YS_MPa": float(mechanical.Engineering_YS_MPa),
                "UTS_MPa": float(mechanical.Engineering_UTS_MPa),
                "Elongation_pct": float(
                    mechanical.Engineering_Elongation_pct
                ),
                "Engineering_YS_MPa": float(mechanical.Engineering_YS_MPa),
                "Engineering_UTS_MPa": float(mechanical.Engineering_UTS_MPa),
                "Engineering_Elongation_pct": float(
                    mechanical.Engineering_Elongation_pct
                ),
                "YS_mean": float(mechanical.Engineering_YS_MPa),
                "UTS_mean": float(mechanical.Engineering_UTS_MPa),
                "TE_mean": float(mechanical.Engineering_Elongation_pct),
                "Mechanical_Value_Status": mechanical.Value_Status,
                "Mechanical_Predictor_Eligibility": (
                    "MECHANICAL_OUTCOME_LEAKAGE"
                ),
                "Original_TRIP": pd.NA,
                "Original_TWIP": pd.NA,
                "Recovered_TRIP": target.Effective_TRIP,
                "Recovered_TWIP": target.Effective_TWIP,
                "Effective_TRIP": target.Effective_TRIP,
                "Effective_TWIP": target.Effective_TWIP,
                "Slip": target.Slip,
                "Target_Status": target.Target_Status,
                "TRIP_Parent_Phase": "FCC",
                "TRIP_Product_Phase": "HCP_EPSILON",
                "TWIP_Phase": target.TWIP_Phase,
                "TRIP_Evidence_Type": target.TRIP_Evidence_Type,
                "TWIP_Evidence_Type": target.TWIP_Evidence_Type,
                "Negative_Evidence_Status": target.Negative_Evidence_Status,
                "Condition_Level_Target_Evidence": (
                    target.Condition_Level_Evidence
                ),
                "Target_Evidence_Confidence": target.Confidence,
                "Label_confidence": target.Confidence,
                "Evidence_TRIP": target.Condition_Level_Evidence,
                "Evidence_TWIP": target.Scientific_Justification,
                "TWIP_Evidence_Abundance": (
                    "LOW" if condition_id == RT40_ID else pd.NA
                ),
                "TWIP_Evidence_Strength": (
                    "MEDIUM_RELATIVE_TO_TRIP"
                    if condition_id == RT40_ID
                    else pd.NA
                ),
                "TWIP_Mode": (
                    "DIRECT_MECHANICAL_TWIN_OCCURRENCE_PHASE_UNRESOLVED"
                    if condition_id == RT40_ID
                    else pd.NA
                ),
                "Slip_Evidence_Type": (
                    "DIRECT_TEM_PARTIAL_DISLOCATION_STACKING_FAULT_ACTIVITY"
                    if condition_id in CHARACTERIZED_IDS
                    else pd.NA
                ),
                "SFE_mJ_m2": pd.NA,
                "SFE_method": pd.NA,
                "SFE_Value_Status": (
                    "NO_DIRECT_NUMERIC_ALLOY_SPECIFIC_SFE"
                ),
                "SFE_Data_Origin": (
                    "AUTHOR_INFERENCE_OR_QUALITATIVE_DISCUSSION_ONLY"
                ),
                "SFE_Raw_Bound": (
                    "<23 mJ/m2" if condition_id == RT40_ID else pd.NA
                ),
                "SFE_Bound_Status": (
                    "AUTHOR_INFERRED_UPPER_BOUND_NOT_DIRECT_MEASUREMENT"
                    if condition_id == RT40_ID
                    else pd.NA
                ),
                "SFE_Predictor_Eligibility": (
                    "NOT_SAFE_AS_DIRECT_NUMERIC_SFE"
                ),
                "SFE_Qualitative_Temperature_Status": (
                    "FURTHER_REDUCTION_DISCUSSION_ONLY_NO_NUMERIC_VALUE"
                    if is_cryo
                    else pd.NA
                ),
                "DeltaG_FCC_HCP_J_mol": pd.NA,
                "DeltaG_method": pd.NA,
                "DeltaG_Value_Status": "NOT_REPORTED_IN_CURRENT_PAPER",
                "DeltaG_Data_Origin": "UNRESOLVED_NO_P021_VALUE",
                "Characterization_methods": (
                    "BSE; EBSD; XRD; TEM/SAD"
                    if has_postfracture
                    else "BSE; EBSD; XRD"
                ),
                "Source_location": (
                    f"{condition.Evidence_Location}; "
                    f"{initial.Evidence_Location}; "
                    f"{mechanical.Evidence_Location}; "
                    f"{target.Condition_Level_Evidence}"
                ),
            }
        )

        if has_postfracture:
            evidence = post.loc[condition_id]
            hcp_fraction = float(evidence.HCP_Epsilon_Fraction)
            row.update(
                {
                    "Postfracture_Phase_State": (
                        "FCC_PLUS_EPSILON_HCP_AFTER_TENSILE_FRACTURE"
                    ),
                    "Postfracture_HCP_fraction": hcp_fraction,
                    "HCP_fraction_at_condition": hcp_fraction,
                    "Postfracture_HCP_fraction_Status": (
                        "DIRECT_EBSD_EXCLUDES_NON_INDEXED_REGIONS"
                    ),
                    "HCP_fraction_status": (
                        "POST_TEST_TARGET_EVIDENCE_EBSD_INDEXED_PIXELS_ONLY"
                    ),
                    "Postfracture_HCP_fraction_scope": (
                        "EBSD_INDEXED_PIXELS_ONLY_EXCLUDES_NON_INDEXED_REGIONS"
                    ),
                    "Postfracture_Predictor_Eligibility": (
                        "POST_TEST_TARGET_EVIDENCE"
                    ),
                    "Postfracture_Evidence_Method": evidence.Method,
                    "Postfracture_Mechanical_Twin_Status": (
                        evidence.Mechanical_Twin_Status
                    ),
                    "Slip_StackingFault_Status": (
                        evidence.Slip_StackingFault_Status
                    ),
                    "Alpha_BCT_Transformation_Status": "NOT_DETECTED",
                    "Alpha_BCT_Transformation_Evidence": (
                        evidence.Alpha_BCT_Status
                    ),
                    "Alpha_BCT_Target_Safeguard": (
                        "ALPHA_BCT_ABSENCE_IS_SEPARATE_FROM_POSITIVE_"
                        "FCC_TO_HCP_TRIP"
                    ),
                    "HCP_lath_or_lamella_note": evidence.Notes,
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
    "Article_Number",
    "Publication_Year",
    "Source_URL",
    "Data_Origin",
    "P021_Source_Identity_Status",
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
    "Replicate_n_Status",
    "Replicate_Scope",
    "Leakage_Group_Strict",
    "Leakage_Group_Material",
    "Grouping_Confidence",
    "Grouping_Review_Required",
    "Grouping_Reason",
    "P021_Record_Role",
    "P021_QC_Status",
}

COMPOSITION_FIELDS = {
    "Alloy_ID",
    "Alloy_Family_Text",
    "Alloy_Family_Use",
    "Original_Composition",
    "Nominal_Composition_at_pct",
    "Composition_basis",
    "Fe_at%",
    "Mn_at%",
    "Cr_at%",
    "Co_at%",
    "Ni_at%",
    "Si_at%",
    "Measured_Bulk_Composition",
    "Measured_Composition_at_pct",
    "Recovered_Bulk_Composition_at_pct",
    "Measured_Composition_Status",
    "Composition_Status",
    "EDS_Qualitative_Homogeneity",
}

PROCESSING_TEST_FIELDS = {
    "Raw_Material_Purity",
    "Melting_Route",
    "Cast_method",
    "Remelt_Count_Min",
    "Remelt_Count_Status",
    "Alloy_Mass_g_Approx",
    "Remolded_Ingot_Dimensions_mm",
    "Homogenization_T_C_Raw",
    "Homogenization_T_K",
    "Homogenization_time_h",
    "Hot_Roll_T_C_Raw",
    "Hot_rolling_T_K",
    "Hot_Roll_Final_Thickness_mm",
    "Cold_rolling_reduction_pct",
    "Anneal_T_C_Raw",
    "Annealing_T_K",
    "Annealing_time_min",
    "Cooling_route",
    "Post_Anneal_Quench",
    "Processing_route",
    "Test_T_Raw",
    "Test_T_C",
    "Test_T_K",
    "Test_Atmosphere",
    "Strain_rate_s-1",
    "Loading_Mode",
    "Loading_Direction",
    "Specimen_Orientation",
    "Specimen_Standard",
}

MICROSTRUCTURE_FIELDS = {
    "Initial_Phase",
    "Initial_Phase_State_Qualitative",
    "Initial_Phase_Status",
    "Initial_FCC_fraction",
    "Recovered_Initial_FCC_fraction",
    "Initial_HCP_fraction",
    "Recovered_Initial_HCP_fraction",
    "Recovered_Initial_HCP_status",
    "Initial_HCP_Status",
    "Initial_HCP_Origin",
    "Initial_Alpha_BCT_fraction",
    "Initial_Secondary_Phase_Status",
    "Fully_Recrystallized",
    "Recrystallized_Status",
    "Grain_size_um",
    "Grain_Size_Method",
    "Grain_Size_Scope",
    "Grain_Size_Status",
    "Grain_Size_Twin_Boundary_Exclusion",
    "Initial_twin_boundary_status",
    "Initial_Twin_Type",
    "PreTest_Twin_State",
    "PreTest_Twin_Origin",
    "Initial_Twin_Origin",
    "Initial_Twin_Target_Guardrail",
    "Initial_TRIP_Target_Guardrail",
    "Initial_Dislocation_State",
    "Initial_Stacking_Fault_State",
    "Initial_Stacking_Fault_State_Raw",
    "PreTest_Cryogenic_Immersion",
    "PreTest_State_Timing",
    "Lattice_parameter_nm",
}

MECHANICAL_FIELDS = {
    "YS_MPa",
    "UTS_MPa",
    "Elongation_pct",
    "Engineering_YS_MPa",
    "Engineering_UTS_MPa",
    "Engineering_Elongation_pct",
    "YS_mean",
    "UTS_mean",
    "TE_mean",
    "Mechanical_Value_Status",
    "Mechanical_Predictor_Eligibility",
}

TARGET_FIELDS = {
    "Recovered_TRIP",
    "Recovered_TWIP",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
    "Target_Status",
    "P021_Target_Status",
    "TRIP_Parent_Phase",
    "TRIP_Product_Phase",
    "TWIP_Phase",
    "TRIP_Evidence_Type",
    "TWIP_Evidence_Type",
    "Negative_Evidence_Status",
    "Condition_Level_Target_Evidence",
    "Target_Evidence_Confidence",
    "Label_confidence",
    "Evidence_TRIP",
    "Evidence_TWIP",
    "TWIP_Evidence_Abundance",
    "TWIP_Evidence_Strength",
    "TWIP_Mode",
    "Slip_Evidence_Type",
}

POSTFRACTURE_FIELDS = {
    "Postfracture_Phase_State",
    "Postfracture_HCP_fraction",
    "HCP_fraction_at_condition",
    "Postfracture_HCP_fraction_Status",
    "HCP_fraction_status",
    "Postfracture_HCP_fraction_scope",
    "Postfracture_Predictor_Eligibility",
    "Postfracture_Evidence_Method",
    "Postfracture_Mechanical_Twin_Status",
    "Slip_StackingFault_Status",
    "Alpha_BCT_Transformation_Status",
    "Alpha_BCT_Transformation_Evidence",
    "Alpha_BCT_Target_Safeguard",
    "HCP_lath_or_lamella_note",
}

PHYSICS_FIELDS = {
    "SFE_mJ_m2",
    "SFE_method",
    "SFE_Value_Status",
    "SFE_Data_Origin",
    "SFE_Raw_Bound",
    "SFE_Bound_Status",
    "SFE_Predictor_Eligibility",
    "SFE_Qualitative_Temperature_Status",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
    "DeltaG_Value_Status",
    "DeltaG_Data_Origin",
}


def _field_metadata(
    feature: str, record: dict
) -> tuple[str, str, str]:
    if feature in IDENTITY_FIELDS:
        return (
            "SOURCE_IDENTITY",
            "Verified article identity / whole paper",
            "Verified workbook and publisher DOI match",
        )
    if feature in HIERARCHY_FIELDS:
        return (
            "HIERARCHY_INTEGRATION",
            "P021_Conditions verified sheet",
            "Source-defined condition hierarchy and aggregate replicate scope",
        )
    if feature in COMPOSITION_FIELDS:
        return (
            "DIRECT_NOMINAL_TEXT_OR_VERIFIED_NA",
            "Abstract, Methods, and Fig.1",
            "Nominal alloy design; EDS/BSE qualitative homogeneity review",
        )
    if feature in PROCESSING_TEST_FIELDS:
        return (
            "DIRECT_METHOD_OR_SCHEMA_UNIT_REPRESENTATION",
            "Methods pp.2-3 and Figs.2,4",
            "Source methods; Celsius-to-Kelvin schema representation only",
        )
    if feature in MICROSTRUCTURE_FIELDS:
        return (
            "DIRECT_PRETEST_MICROSTRUCTURE",
            "Results pp.3,6 and Figs.2,3,7",
            "BSE, EBSD, XRD, and pre-test TEM interpretation",
        )
    if feature in MECHANICAL_FIELDS:
        return (
            "DIRECT_AGGREGATE_TENSILE_OUTCOME",
            "Fig.4 inset tables p.4",
            "Average engineering tensile response from at least three specimens",
        )
    if feature in POSTFRACTURE_FIELDS:
        return (
            "DIRECT_POST_TEST_TARGET_EVIDENCE",
            (
                "Figs.6a,7c pp.5-7"
                if record["ML_Condition_ID"] == RT40_ID
                else "Figs.5,6b,7b,7d pp.5-8"
            ),
            "Condition-specific XRD, EBSD, and TEM/SAD",
        )
    if feature in PHYSICS_FIELDS:
        return (
            "AUTHOR_INFERENCE_OR_VERIFIED_GAP",
            "Results pp.5-6 and whole-paper review",
            "Source interpretation; no numeric conversion or cross-paper transfer",
        )
    if feature in TARGET_FIELDS:
        return (
            "CONDITION_LEVEL_TARGET_DECISION",
            record.get("Source_location", "P021 target evidence sheet"),
            "Condition-specific EBSD/XRD/TEM evidence or conservative NA review",
        )
    return (
        "VERIFIED_MASTER_FIELD_MAPPING",
        record.get("Source_location", "Verified P021 workbook"),
        "Verified workbook-to-master mapping",
    )


def _na_status(feature: str) -> str:
    if feature in {
        "Measured_Bulk_Composition",
        "Measured_Composition_at_pct",
        "Recovered_Bulk_Composition_at_pct",
    }:
        return "VERIFIED_NA_NO_QUANTITATIVE_POSTMELT_BULK_ANALYSIS"
    if feature in {"Physical_Batch_ID", "Replicate_ID"}:
        return "VERIFIED_NA_NOT_SOURCE_SUPPORTED"
    if feature in {"Initial_FCC_fraction", "Recovered_Initial_FCC_fraction"}:
        return "VERIFIED_NA_EXACT_NUMERIC_FCC_FRACTION_NOT_REPORTED"
    if feature in {"Effective_TRIP", "Effective_TWIP", "Slip"}:
        return "VERIFIED_NA_INSUFFICIENT_CONDITION_LEVEL_TARGET_EVIDENCE"
    if feature in {"Postfracture_HCP_fraction", "HCP_fraction_at_condition"}:
        return "VERIFIED_NA_NO_CONDITION_SPECIFIC_POSTFRACTURE_FRACTION"
    if feature in {"SFE_mJ_m2", "SFE_method"}:
        return "VERIFIED_NA_NO_DIRECT_NUMERIC_ALLOY_SPECIFIC_SFE"
    if feature in {"DeltaG_FCC_HCP_J_mol", "DeltaG_method"}:
        return "VERIFIED_NA_NOT_REPORTED_NO_CROSS_PAPER_TRANSFER"
    return "VERIFIED_NA_NOT_SOURCE_SUPPORTED"


def _workbook_provenance_scopes(record_id: str, feature: str) -> list[str]:
    if record_id in EXACT_IDS:
        return [record_id]
    if record_id != MATERIAL:
        raise AssertionError(f"unknown P021 provenance record scope: {record_id}")
    if feature in {"SFE_numeric", "SFE_raw_bound"}:
        return [RT40_ID]
    return list(EXACT_IDS)


def _append_workbook_provenance(
    rows: list[dict], sheets: dict[str, pd.DataFrame]
) -> None:
    for source in sheets["P021_Provenance"].to_dict("records"):
        record_id = str(source["Record_ID"])
        for condition_id in _workbook_provenance_scopes(
            record_id, str(source["Feature_Name"])
        ):
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIAL,
                    "ML_Condition_ID": condition_id,
                    "Observation_ID": _observation_id(condition_id),
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


def _append_physics_provenance(
    rows: list[dict], sheets: dict[str, pd.DataFrame]
) -> None:
    for physics in sheets["P021_Physics_SFE"].to_dict("records"):
        if physics["Feature"] == "SFE" and float(physics["Temperature_K"]) == 298:
            scopes = [RT40_ID]
            feature_name = "SFE_Raw_Bound_298K"
            recovered = "<23 mJ/m2"
        elif physics["Feature"] == "SFE":
            scopes = [CRYO_ID]
            feature_name = "SFE_Qualitative_State_77K"
            recovered = physics["Recovered_Value_Raw"]
        else:
            scopes = list(EXACT_IDS)
            feature_name = "DeltaG_FCC_HCP_J_mol"
            recovered = "UNRESOLVED_NA"
        for condition_id in scopes:
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIAL,
                    "ML_Condition_ID": condition_id,
                    "Observation_ID": _observation_id(condition_id),
                    "Record_ID": f"{MATERIAL}_PHYSICS",
                    "Feature_Name": feature_name,
                    "Recovered_Value": recovered,
                    "Units": physics["Units"],
                    "Evidence_Type": physics["Status"],
                    "Evidence_Location": physics["Evidence_Location"],
                    "Method": physics["Method"],
                    "Confidence": physics["Confidence"],
                    "Recovery_Status": (
                        physics["Status"]
                        if is_present(physics["Recovered_Value_Raw"])
                        else "VERIFIED_NA_NOT_REPORTED"
                    ),
                    "Data_Origin": "EXPERIMENTAL",
                    "Source_URL": physics["Source_URL"],
                    "Predictor_Eligibility": physics["Predictor_Eligibility"],
                    "Provenance_Layer": "PHYSICS_SUPPORT_MAPPING",
                }
            )


def _append_hall_petch_provenance(
    rows: list[dict], sheets: dict[str, pd.DataFrame]
) -> None:
    for support in sheets["P021_HallPetch_Support"].to_dict("records"):
        units = (
            "MPa"
            if support["Feature"] == "Hall_Petch_sigma0"
            else "MPa um^0.5"
        )
        for condition_id in RT_IDS:
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIAL,
                    "ML_Condition_ID": condition_id,
                    "Observation_ID": _observation_id(condition_id),
                    "Record_ID": support["Support_Record_ID"],
                    "Feature_Name": support["Feature"],
                    "Recovered_Value": support["Value"],
                    "Units": units,
                    "Evidence_Type": support["Status"],
                    "Evidence_Location": support["Evidence_Location"],
                    "Method": (
                        "Current-paper Hall-Petch fit from tensile yield response"
                    ),
                    "Confidence": support["Confidence"],
                    "Recovery_Status": "VERIFIED_MODEL_DERIVED_SUPPORT",
                    "Data_Origin": "EXPERIMENTAL",
                    "Source_URL": support["Source_URL"],
                    "Predictor_Eligibility": support[
                        "Predictor_Eligibility"
                    ],
                    "Provenance_Layer": "HALL_PETCH_SUPPORT_MAPPING",
                }
            )


def build_provenance(
    condition_rows: list[dict], sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    rows: list[dict] = []
    for record in condition_rows:
        condition_id = record["ML_Condition_ID"]
        observation_id = record["Observation_ID"]
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            meaningful_na = feature in MEANINGFUL_NA_FIELDS
            if not is_present(value) and not meaningful_na:
                continue
            evidence_type, evidence_location, method = _field_metadata(
                feature, record
            )
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIAL,
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
                        "Target_Evidence_Confidence", "High"
                    ),
                    "Recovery_Status": (
                        "VERIFIED" if is_present(value) else _na_status(feature)
                    ),
                    "Data_Origin": "EXPERIMENTAL",
                    "Source_URL": f"https://doi.org/{DOI}",
                    "Predictor_Eligibility": (
                        record.get("Mechanical_Predictor_Eligibility")
                        if feature in MECHANICAL_FIELDS
                        else (
                            record.get("Postfracture_Predictor_Eligibility")
                            if feature in POSTFRACTURE_FIELDS
                            else (
                                record.get("SFE_Predictor_Eligibility")
                                if feature in PHYSICS_FIELDS
                                else "AUDIT_SCOPE_DEPENDENT"
                            )
                        )
                    ),
                    "Provenance_Layer": "MASTER_FIELD_MAPPING",
                }
            )

    _append_workbook_provenance(rows, sheets)
    _append_physics_provenance(rows, sheets)
    _append_hall_petch_provenance(rows, sheets)
    frame = pd.DataFrame(rows).drop_duplicates(ignore_index=True)
    required = [
        "Paper_ID",
        "DOI",
        "Study_Series_ID",
        "Material_Parent_ID",
        "ML_Condition_ID",
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
    condition_rows: list[dict], provenance: pd.DataFrame
) -> None:
    for row in condition_rows:
        condition_id = row["ML_Condition_ID"]
        selected = provenance[provenance.ML_Condition_ID.eq(condition_id)]
        row["P021_Recovery_Provenance_JSON"] = json.dumps(
            json_ready(selected.to_dict("records")),
            ensure_ascii=False,
            allow_nan=False,
        )


def hierarchy_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    conditions = sheets["P021_Conditions"].copy()
    frame = conditions[
        [
            "Paper_ID",
            "DOI",
            "Study_Series_ID",
            "Material_Parent_ID",
            "ML_Condition_ID",
            "Independent_Experimental_ML_sample",
            "Leakage_Group_Strict",
            "Leakage_Group_Material",
            "Physical_Batch_ID",
            "Replicate_ID",
            "Replicate_n",
            "Replicate_n_Status",
        ]
    ].copy()
    frame["Parent_Experiment_ID"] = frame.ML_Condition_ID
    frame["Parent_ML_Condition_ID"] = frame.ML_Condition_ID
    frame["Observation_ID"] = frame.ML_Condition_ID.map(_observation_id)
    frame["Observation_Role"] = "INDEPENDENT_CONDITION"
    frame["Pseudo_Replicate_Rows"] = 0
    frame["Counting_Status"] = (
        "FIVE_EXACT_INDEPENDENT_CONDITIONS_NO_REPLICATE_ROWS"
    )
    frame["New_Source_Status"] = (
        "NEW_PRIMARY_EXPERIMENTAL_PAPER_NO_V14_DOI_DUPLICATE"
    )
    return frame


def processing_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    conditions = sheets["P021_Conditions"].copy()
    frame = conditions[
        [
            "Paper_ID",
            "DOI",
            "ML_Condition_ID",
            "Raw_Material_Purity",
            "Melting_Route",
            "Remelt_Count_Min",
            "Remolded_Ingot_Dimensions_mm",
            "Homogenization_T_C",
            "Homogenization_Time_h",
            "Hot_Roll_T_C",
            "Hot_Roll_Final_Thickness_mm",
            "Cold_Roll_Reduction_pct",
            "Anneal_T_C",
            "Anneal_Time_min",
            "Post_Anneal_Quench",
            "Specimen_Orientation",
            "Specimen_Standard",
            "Evidence_Location",
            "Confidence",
            "Source_URL",
        ]
    ].copy()
    frame["Alloy_Mass_g_Approx"] = 150.0
    frame["Remelt_Count_Status"] = "AT_LEAST_FIVE"
    frame["Homogenization_T_K_Representation"] = (
        frame.Homogenization_T_C.astype(float) + 273.15
    )
    frame["Hot_Roll_T_K_Representation"] = (
        frame.Hot_Roll_T_C.astype(float) + 273.15
    )
    frame["Anneal_T_K_Representation"] = (
        frame.Anneal_T_C.astype(float) + 273.15
    )
    frame["EDS_Homogeneity_Use"] = (
        "QUALITATIVE_ONLY_NOT_QUANTITATIVE_BULK_CHEMISTRY"
    )
    return frame


def condition_grid_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    conditions = sheets["P021_Conditions"].copy()
    micro = sheets["P021_Initial_Microstructure"][
        ["ML_Condition_ID", "Grain_Size_um"]
    ]
    frame = conditions[
        [
            "Paper_ID",
            "DOI",
            "Study_Series_ID",
            "Material_Parent_ID",
            "ML_Condition_ID",
            "Anneal_T_C",
            "Anneal_Time_min",
            "Post_Anneal_Quench",
            "Test_T_Raw",
            "Test_T_K",
            "Strain_Rate_s-1",
            "Independent_Experimental_ML_sample",
        ]
    ].merge(micro, on="ML_Condition_ID", how="left", validate="one_to_one")
    frame["Condition_Grid_Status"] = "EXACT_SOURCE_DEFINED_CONDITION"
    return frame


def hall_petch_table(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    frame = sheets["P021_HallPetch_Support"].copy()
    frame.insert(2, "Study_Series_ID", SERIES)
    frame.insert(3, "Material_Parent_ID", MATERIAL)
    frame["Source_Units_Raw"] = frame.Units
    frame.loc[
        frame.Feature.eq("Hall_Petch_k"), "Units"
    ] = "MPa um^0.5"
    frame["Fit_Condition_Scope"] = "|".join(RT_IDS)
    frame["Leakage_Classification"] = "MODEL_DERIVED_LEAKAGE"
    return frame


def decision_ledger(
    sheets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    frame = sheets["P021_Integration_Decisions"].copy()
    frame.insert(0, "Paper_ID", PAPER_ID)
    frame.insert(1, "DOI", DOI)
    frame["Study_Series_ID"] = SERIES
    frame["Material_Parent_ID"] = MATERIAL
    frame["Data_Origin"] = "EXPERIMENTAL"
    frame["Legacy_Duplicate_Status"] = (
        "NEW_SOURCE_NO_P021_DOI_REPRESENTATION_IN_V14"
    )
    frame["Correction_Mode"] = (
        "NEW_ROWS_ONLY_NO_RECOVERY_V14_VALUE_OVERWRITE"
    )
    return frame


def validate(
    source: pd.DataFrame,
    out: pd.DataFrame,
    sheets: dict[str, pd.DataFrame],
    provenance: pd.DataFrame,
    condition_rows: list[dict],
) -> None:
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    assert duplicate_rows(source).empty
    p021 = out[out.Paper_ID.eq(PAPER_ID)].copy()
    assert len(out) - len(source) == 5
    assert len(p021) == 5
    assert tuple(p021.ML_Condition_ID) == EXACT_IDS
    assert p021.DOI.eq(DOI).all()
    assert p021.P021_Record_Role.eq(
        "RECOVERED_EXACT_PRIMARY_CONDITION"
    ).all()
    assert p021.Data_Origin.eq("EXPERIMENTAL").all()
    assert p021.Observation_Role.eq("INDEPENDENT_CONDITION").all()
    assert p021.Independent_ML_sample.eq(True).all()
    assert p021.Independent_Experimental_ML_sample.eq(True).all()
    assert p021.Experimental_Target_Eligibility.eq(True).all()
    assert p021.Parent_ML_Condition_ID.eq(p021.ML_Condition_ID).all()
    assert p021.Parent_Experiment_ID.eq(p021.ML_Condition_ID).all()
    assert p021.Observation_ID.nunique() == 5
    assert p021.Deformation_Stage_ID.isna().all()
    assert p021.Study_Series_ID.eq(SERIES).all()
    assert p021.Material_Parent_ID.eq(MATERIAL).all()
    assert p021.Leakage_Group_Strict.eq(SERIES).all()
    assert p021.Leakage_Group_Material.eq(MATERIAL).all()
    assert p021.Physical_Batch_ID.isna().all()
    assert p021.Replicate_ID.isna().all()
    assert p021.Replicate_n.astype(float).eq(3).all()
    assert p021.Replicate_n_Status.eq(
        "MINIMUM_REPORTED_AT_LEAST_THREE"
    ).all()

    assert p021.Original_Composition.eq(NOMINAL_COMPOSITION).all()
    assert p021.Nominal_Composition_at_pct.eq(NOMINAL_COMPOSITION).all()
    assert p021.Measured_Bulk_Composition.isna().all()
    assert p021.Measured_Composition_at_pct.isna().all()
    assert p021.Recovered_Bulk_Composition_at_pct.isna().all()
    assert p021.EDS_Qualitative_Homogeneity.eq(
        "QUALITATIVE_HOMOGENIZATION_ONLY_NOT_QUANTITATIVE_BULK_CHEMISTRY"
    ).all()
    expected_elements = {
        "Fe_at%": 50.0,
        "Mn_at%": 17.5,
        "Cr_at%": 12.5,
        "Co_at%": 10.0,
        "Ni_at%": 5.0,
        "Si_at%": 5.0,
    }
    for field, value in expected_elements.items():
        assert p021[field].astype(float).eq(value).all()

    assert p021.Remelt_Count_Min.astype(float).eq(5).all()
    assert p021.Remelt_Count_Status.eq("AT_LEAST_FIVE").all()
    assert p021.Alloy_Mass_g_Approx.astype(float).eq(150).all()
    assert p021.Homogenization_T_C_Raw.astype(float).eq(1150).all()
    assert p021.Homogenization_time_h.astype(float).eq(24).all()
    assert p021.Hot_Roll_T_C_Raw.astype(float).eq(1100).all()
    assert p021.Hot_Roll_Final_Thickness_mm.astype(float).eq(3).all()
    assert p021.Cold_rolling_reduction_pct.astype(float).eq(30).all()
    assert p021.Post_Anneal_Quench.eq("Water quench").all()
    assert p021["Strain_rate_s-1"].astype(float).eq(1e-3).all()
    assert p021.Specimen_Orientation.eq(
        "Longitudinal / rolling direction"
    ).all()
    assert p021.Specimen_Standard.eq("ASTM E8/E8M sub-size").all()

    indexed = p021.set_index("ML_Condition_ID")
    for condition_id, expected in EXPECTED_GRID.items():
        anneal_c, anneal_min, grain_um, test_k, test_raw = expected
        row = indexed.loc[condition_id]
        assert float(row.Anneal_T_C_Raw) == anneal_c
        assert float(row.Annealing_time_min) == anneal_min
        assert float(row.Grain_size_um) == grain_um
        assert float(row.Test_T_K) == test_k
        assert row.Test_T_Raw == test_raw
    assert indexed.loc[list(RT_IDS), "Test_T_C"].astype(float).eq(25).all()
    assert pd.isna(indexed.loc[CRYO_ID, "Test_T_C"])
    assert (
        indexed.loc[CRYO_ID, "Test_Atmosphere"]
        == "LIQUID_NITROGEN_ATMOSPHERE"
    )

    assert p021.Initial_Phase.eq("SINGLE_FCC").all()
    assert p021.Fully_Recrystallized.eq(True).all()
    assert p021.Initial_FCC_fraction.isna().all()
    assert p021.Recovered_Initial_FCC_fraction.isna().all()
    assert p021.Initial_HCP_fraction.astype(float).eq(0).all()
    assert p021.Initial_Alpha_BCT_fraction.astype(float).eq(0).all()
    assert p021.Initial_Secondary_Phase_Status.eq(
        "NO_OBVIOUS_PRECIPITATES_OR_OTHER_PHASES"
    ).all()
    assert p021.PreTest_Twin_Origin.eq("ANNEALING_PRETEST").all()
    assert p021.Initial_Twin_Target_Guardrail.eq(
        "ANNEALING_TWINS_DO_NOT_GENERATE_TENSILE_TWIP"
    ).all()
    assert p021.Grain_Size_Twin_Boundary_Exclusion.eq(True).all()
    assert p021.Lattice_parameter_nm.astype(float).eq(0.358).all()
    assert (
        indexed.loc[CRYO_ID, "Initial_Stacking_Fault_State"]
        == "PROFUSE_PRETEST_STACKING_FAULTS"
    )
    assert bool(indexed.loc[CRYO_ID, "PreTest_Cryogenic_Immersion"])
    assert p021.PreTest_State_Timing.eq("BEFORE_TENSILE_LOADING").all()

    for condition_id, expected in EXPECTED_MECHANICS.items():
        row = indexed.loc[condition_id]
        actual = (
            float(row.Engineering_YS_MPa),
            float(row.Engineering_UTS_MPa),
            float(row.Engineering_Elongation_pct),
        )
        assert actual == expected
        assert float(row.YS_MPa) == expected[0]
        assert float(row.UTS_MPa) == expected[1]
        assert float(row.Elongation_pct) == expected[2]
    assert p021.Mechanical_Predictor_Eligibility.eq(
        "MECHANICAL_OUTCOME_LEAKAGE"
    ).all()

    unresolved = [EXACT_IDS[0], EXACT_IDS[1], EXACT_IDS[3]]
    assert indexed.loc[
        unresolved, ["Effective_TRIP", "Effective_TWIP", "Slip"]
    ].isna().all().all()
    assert indexed.loc[unresolved, "Negative_Evidence_Status"].eq(
        "INSUFFICIENT_FOR_ZERO"
    ).all()
    assert float(indexed.loc[RT40_ID, "Effective_TRIP"]) == 1
    assert float(indexed.loc[RT40_ID, "Effective_TWIP"]) == 1
    assert float(indexed.loc[RT40_ID, "Slip"]) == 1
    assert (
        indexed.loc[RT40_ID, "TWIP_Phase"]
        == "UNRESOLVED_PHASE_DIRECT_MECHANICAL_TWIN_TEXT"
    )
    assert indexed.loc[RT40_ID, "TWIP_Evidence_Abundance"] == "LOW"
    assert (
        indexed.loc[RT40_ID, "TWIP_Evidence_Strength"]
        == "MEDIUM_RELATIVE_TO_TRIP"
    )
    assert float(indexed.loc[CRYO_ID, "Effective_TRIP"]) == 1
    assert pd.isna(indexed.loc[CRYO_ID, "Effective_TWIP"])
    assert float(indexed.loc[CRYO_ID, "Slip"]) == 1
    assert (
        indexed.loc[CRYO_ID, "Negative_Evidence_Status"]
        == "INSUFFICIENT_FOR_ZERO"
    )

    assert float(indexed.loc[RT40_ID, "Postfracture_HCP_fraction"]) == 0.149
    assert float(indexed.loc[CRYO_ID, "Postfracture_HCP_fraction"]) == 0.562
    assert indexed.loc[
        [RT40_ID, CRYO_ID], "Postfracture_HCP_fraction_scope"
    ].eq("EBSD_INDEXED_PIXELS_ONLY_EXCLUDES_NON_INDEXED_REGIONS").all()
    assert indexed.loc[
        unresolved, "Postfracture_HCP_fraction"
    ].isna().all()
    assert indexed.loc[
        unresolved, "HCP_fraction_at_condition"
    ].isna().all()
    assert indexed.loc[
        [RT40_ID, CRYO_ID], "Postfracture_Predictor_Eligibility"
    ].eq("POST_TEST_TARGET_EVIDENCE").all()
    assert indexed.loc[
        [RT40_ID, CRYO_ID], "Alpha_BCT_Transformation_Status"
    ].eq("NOT_DETECTED").all()
    assert indexed.loc[
        [RT40_ID, CRYO_ID], "Effective_TRIP"
    ].astype(float).eq(1).all()

    assert p021.SFE_mJ_m2.isna().all()
    assert p021.SFE_method.isna().all()
    assert indexed.loc[RT40_ID, "SFE_Raw_Bound"] == "<23 mJ/m2"
    assert (
        indexed.loc[RT40_ID, "SFE_Bound_Status"]
        == "AUTHOR_INFERRED_UPPER_BOUND_NOT_DIRECT_MEASUREMENT"
    )
    assert p021.SFE_Predictor_Eligibility.eq(
        "NOT_SAFE_AS_DIRECT_NUMERIC_SFE"
    ).all()
    assert (
        indexed.loc[CRYO_ID, "SFE_Qualitative_Temperature_Status"]
        == "FURTHER_REDUCTION_DISCUSSION_ONLY_NO_NUMERIC_VALUE"
    )
    assert p021.DeltaG_FCC_HCP_J_mol.isna().all()
    assert p021.DeltaG_method.isna().all()

    before = counts(source)
    after = counts(out)
    assert tuple(after[index] - before[index] for index in range(4)) == (
        5,
        2,
        1,
        1,
    )
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    expected_class_delta = {
        "trip_positive": 2,
        "trip_negative": 0,
        "twip_positive": 1,
        "twip_negative": 0,
        "joint_00": 0,
        "joint_10": 0,
        "joint_01": 0,
        "joint_11": 1,
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
    for record in condition_rows:
        observation_id = record["Observation_ID"]
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            if is_present(value) or feature in MEANINGFUL_NA_FIELDS:
                matching = master_provenance[
                    master_provenance.Observation_ID.eq(observation_id)
                    & master_provenance.Feature_Name.eq(feature)
                ]
                assert len(matching), (observation_id, feature)
    assert p021.P021_Recovery_Provenance_JSON.str.len().gt(2).all()

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
        if field in p021:
            assert p021[field].isna().all()
    assert file_hash(SOURCE) == SOURCE_SHA256
    assert file_hash(BOOK) == BOOK_SHA256


def write_audit(source: pd.DataFrame, out: pd.DataFrame) -> None:
    before = counts(source)
    after = counts(out)
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    p021 = out[out.Paper_ID.eq(PAPER_ID)].set_index("ML_Condition_ID")
    audit = f"""# P021 recovery v15 audit

## A. Source identity

- Paper_ID=P021; DOI {DOI}.
- Title: {TITLE}.
- {JOURNAL}, volume {VOLUME}, article {ARTICLE_NUMBER} ({YEAR}); Data_Origin=EXPERIMENTAL.
- The workbook identity is VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH. The workbook and recovery-v14 base are SHA-256 gated; integration rejects a DOI or identity mismatch.

## B. New-source/duplicate check

- The recovery-v14 DOI search returned {len(duplicate_rows(source))} matching rows and no P021 Paper_ID. P021 is therefore appended as a new source beyond P020.
- No mapping was made by row order. If a DOI representation appears in a changed base, the generator stops for explicit replacement-aware review.

## C. V15 total rows

- V15 contains {len(out)} rows: all {len(source)} recovery-v14 rows are preserved in their original order and source columns, followed by five P021 rows.

## D. Independent experimental count before/after

- Replacement-aware independent experimental conditions: {before[0]} before -> {after[0]} after.

## E. Exact P021 condition count

- Exactly five exact primary conditions exist: {", ".join(EXACT_IDS)}.
- Each is one independent condition-level record. Replicate_n=3 records the reported minimum of at least three specimens; no replicate or post-test child rows were created.

## F. Four RT grain-size conditions

- Four 298 K / 25 C conditions retain grain sizes 10.0, 19.5, 40.9, and 149.6 um with their exact annealing schedules and 1e-3 s^-1 rate.

## G. Cryogenic condition

- {CRYO_ID} reuses the 1000 C / 20 min, 40.9 um annealed state and is tested at 77 K in a liquid-nitrogen atmosphere at 1e-3 s^-1.

## H. Nominal chemistry / measured chemistry gap

- Nominal composition is {NOMINAL_COMPOSITION} at.%.
- Quantitative post-melt bulk chemistry remains NA. EDS/BSE evidence is stored only as qualitative homogenization and never converted into bulk composition.

## I. Common processing

- Source processing retains >99.9% raw-material purity; vacuum arc melting under Ar; at least five flips/remelts; approximately 150 g alloy; 65 x 40 x 10 mm remolded ingot; 1150 C/24 h homogenization; 1100 C hot rolling to 3 mm; 30% cold rolling; condition-specific final annealing; water quench; longitudinal ASTM E8/E8M sub-size tensile specimens.

## J. Fully recrystallized single-FCC initial states

- All five conditions are fully recrystallized and single FCC before tensile loading. Initial_HCP_fraction=0 and Initial_Alpha_BCT_fraction=0.
- Exact numeric Initial_FCC_fraction remains NA; no FCC=1.0 complement is fabricated. No obvious precipitates/secondary phases are reported.

## K. Annealing-twin safeguard

- All five retain abundant pre-test annealing twins with ANNEALING_TWINS_DO_NOT_GENERATE_TENSILE_TWIP. Only direct tensile deformation-twin evidence can establish TWIP.

## L. Grain sizes

- Exact grain sizes are 10.0, 19.5, 40.9, and 149.6 um. The 40.9 um state is used at both 298 K and 77 K. Annealing twin boundaries are excluded from the source grain-size calculation.

## M. Pre-test 77 K stacking faults

- The cryogenic row stores Initial_Stacking_Fault_State=PROFUSE_PRETEST_STACKING_FAULTS and timing BEFORE_TENSILE_LOADING. This pre-test state is neither post-test leakage nor TWIP evidence.

## N. Mechanical values

- A900/5 min RT: 310/769 MPa YS/UTS and 63% elongation.
- A900/25 min RT: 292/736 MPa and 64%.
- A1000/20 min RT: 249/688 MPa and 58%.
- A1000/150 min RT: 228/643 MPa and 59%.
- A1000/20 min 77 K: 540/1410 MPa and 51%.
- Values are exact source-reported averages from at least three specimens and remain MECHANICAL_OUTCOME_LEAKAGE.

## O. RT40 TRIP evidence

- {RT40_ID} is Effective_TRIP=1 and Slip=1. Initial HCP=0 is followed by 14.9% epsilon-HCP by post-fracture EBSD plus direct TEM/SAD epsilon-lath evidence, establishing FCC -> HCP epsilon TRIP.

## P. RT40 low-abundance TWIP evidence

- {RT40_ID} is Effective_TWIP=1 because the source explicitly reports few mechanical twins in the room-temperature-deformed TEM specimen.
- Abundance is LOW and evidence strength is MEDIUM relative to TRIP. TWIP_Phase=UNRESOLVED_PHASE_DIRECT_MECHANICAL_TWIN_TEXT; occurrence is not dominance and no FCC/HCP twin phase is invented.

## Q. 77 K TRIP evidence

- {CRYO_ID} is Effective_TRIP=1 and Slip=1 from strong post-deformation XRD, EBSD (56.2% epsilon-HCP), and TEM/SAD evidence of extensive epsilon laths on two non-coplanar systems.

## R. 77 K TWIP=NA decision

- Effective_TWIP remains NA with INSUFFICIENT_FOR_ZERO. Reduced/absent-twin discussion and pre-test stacking faults are not converted into TWIP=0 or TWIP=1.

## S. Post-fracture HCP fractions

- RT40=0.149 and 77K40=0.562. Both are POST_TEST_TARGET_EVIDENCE and explicitly scoped to indexed EBSD regions, excluding non-indexed regions.
- The 10.0, 19.5, and 149.6 um conditions remain NA; no phase fraction is extrapolated.

## T. Alpha-BCT pathway status

- Alpha_BCT_Transformation_Status=NOT_DETECTED only for the directly characterized RT40 and 77K40 tensile states.
- This is separate from FCC -> HCP TRIP and does not change either positive TRIP label.

## U. SFE inferred-bound handling

- Numeric SFE remains NA for every P021 condition. The raw <23 mJ/m2 statement is preserved only as AUTHOR_INFERRED_UPPER_BOUND_NOT_DIRECT_MEASUREMENT and NOT_SAFE_AS_DIRECT_NUMERIC_SFE.
- The 77 K discussion is qualitative further reduction only; no cryogenic numeric SFE is created.

## V. DeltaG gap

- No current-paper numerical alloy-specific DeltaG FCC -> HCP is reported. DeltaG and method remain NA; no calculation or cross-paper import occurs.

## W. Hall-Petch leakage handling

- Current-paper sigma0=198 MPa and k=368 MPa um^0.5 are preserved in the support table as CURRENT_PAPER_FIT_FROM_TENSILE_YIELD_RESPONSE and MODEL_DERIVED_LEAKAGE.
- They are not stored as safe pre-deformation predictors.

## X. Before/after usable target counts

- Usable TRIP/TWIP/joint counts: {before[1]}/{before[2]}/{before[3]} before -> {after[1]}/{after[2]}/{after[3]} after.
- TRIP positive/negative: {before_classes["trip_positive"]}/{before_classes["trip_negative"]} -> {after_classes["trip_positive"]}/{after_classes["trip_negative"]}.
- TWIP positive/negative: {before_classes["twip_positive"]}/{before_classes["twip_negative"]} -> {after_classes["twip_positive"]}/{after_classes["twip_negative"]}.
- Joint states before: 00={before_classes["joint_00"]}, 10={before_classes["joint_10"]}, 01={before_classes["joint_01"]}, 11={before_classes["joint_11"]}; after: 00={after_classes["joint_00"]}, 10={after_classes["joint_10"]}, 01={after_classes["joint_01"]}, 11={after_classes["joint_11"]}.
- Programmatic deltas are +5 independent, +2 usable TRIP, +1 usable TWIP, and +1 usable joint.

## Y. Remaining P021 gaps

- Quantitative post-melt bulk chemistry, physical-batch and individual-replicate identities/results, exact numeric initial FCC fractions, direct condition-specific post-test mechanism evidence for the 10.0/19.5/149.6 um RT states, condition-wide 77 K TWIP evidence, direct numeric SFE at either temperature, and alloy-specific DeltaG remain unresolved.

## Z. Later global refresh requirement

- Global QC, feature coverage/schema statistics, and grouped split artifacts remain intentionally unrefreshed while paper collection continues. They require a later non-destructive refresh after collection pauses.
- No ML matrix, model, feature engineering, imputation, normalization, composition reconciliation, alloy descriptor, digitized figure, resampling, synthetic record, or performance metric was created.
"""
    AUDIT.write_text(audit, encoding="utf-8")


def integrate() -> tuple[pd.DataFrame, pd.DataFrame]:
    source, sheets = load_and_verify()
    out = source.copy()
    for column in NEW_COLUMNS:
        if column not in out:
            out[column] = pd.NA

    condition_rows = make_condition_rows(list(out.columns), sheets)
    provenance = build_provenance(condition_rows, sheets)
    attach_provenance_json(condition_rows, provenance)
    out = pd.concat(
        [
            out.astype(object),
            pd.DataFrame(condition_rows, columns=out.columns).astype(object),
        ],
        ignore_index=True,
    )
    validate(source, out, sheets, provenance, condition_rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)

    exports = {
        "study_identity": sheets["P021_Study_Identity"],
        "hierarchy": hierarchy_table(sheets),
        "processing": processing_table(sheets),
        "condition_grid": condition_grid_table(sheets),
        "initial_microstructure": sheets["P021_Initial_Microstructure"],
        "mechanical_response": sheets["P021_Mechanical_Response"],
        "postfracture_evidence": sheets["P021_Postfracture_Evidence"],
        "targets": sheets["P021_Target_Evidence"],
        "sfe_physics": sheets["P021_Physics_SFE"],
        "hall_petch_support": hall_petch_table(sheets),
        "provenance": provenance,
        "decision_correction_ledger": decision_ledger(sheets),
    }
    for name, frame in exports.items():
        frame.to_csv(
            TABLE / f"p021_recovery_v15_{name}.csv",
            index=False,
        )
    write_audit(source, out)
    return source, out


if __name__ == "__main__":
    integrate()
