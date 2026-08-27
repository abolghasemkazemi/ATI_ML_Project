"""Integrate verified P020 evidence into extended recovery v14.

This is a source-recovery operation only.  The complete recovery-v13 input is
an immutable prefix.  One independent P020 experimental condition and six
correlated in-situ observations are appended without feature engineering,
imputation, composition normalization, resampling, or model training.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v13.csv"
BOOK = ROOT / "data/interim/manual_recovery/P020_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_extended_recovery_v14.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P020_RECOVERY_V14_AUDIT.md"

PAPER_ID = "P020"
DOI = "10.1080/21663831.2018.1523239"
TITLE = (
    "Deformation mechanisms and work-hardening behavior of transformation-induced "
    "plasticity high entropy alloys by in-situ neutron diffraction"
)
JOURNAL = "Materials Research Letters"
SERIES = "P020_SERIES01"
MATERIAL = "P020_MAT_FE50MN30CO10CR10"
PRIMARY_ID = "P020_MC_TRIPHEA_INSITU"
SOURCE_SHA256 = "73c09dbc6eb72d498fb0792cda417c2207e85c74bcc56531f758dff4e8f3c59e"
BOOK_SHA256 = "5884187804c37f70bd926cfdf23de2bf71b0cc04133e03fb9dec18ecc097e20e"

STAGE_IDS = {
    "P020_STAGE_I_ELASTIC",
    "P020_STAGE_TRIP_ONSET",
    "P020_STAGE_HCP_TENSILE_TWIN",
    "P020_STAGE_MULTI_TWIN",
    "P020_STAGE_LATE_TRIP_SUPPRESSION",
    "P020_STAGE_FRACTURE",
}

REQUIRED_SHEETS = {
    "P020_Study_Identity",
    "P020_Condition",
    "P020_Initial_Microstructure",
    "P020_Mechanical_Response",
    "P020_Target_Evidence",
    "P020_Stage_Evidence",
    "P020_Phase_Evolution",
    "P020_InSitu_Method",
    "P020_Integration_Decisions",
    "P020_Provenance",
}

NEW_COLUMNS = [
    "P020_Record_Role",
    "P020_Target_Status",
    "P020_Source_Identity_Status",
    "P020_QC_Status",
    "P020_Supplement_Status",
    "P020_Recovery_Provenance_JSON",
    "Journal",
    "Volume",
    "Issue",
    "Pages",
    "Publication_Year",
    "Source_URL",
    "Alloy_Family_Text",
    "Alloy_Family_Use",
    "Melting_Route",
    "Casting_Route",
    "Cast_Bar_Dimensions_mm",
    "Rolling_T_Raw",
    "Post_Anneal_Cooling",
    "Test_Metadata_Status",
    "Initial_TRIP_Target_Guardrail",
    "FCC_Grain_Size_um",
    "FCC_Grain_Morphology",
    "HCP_Lath_Thickness_um",
    "HCP_Morphology",
    "Phase_Fraction_Methods",
    "Apparent_Yield_Onset_MPa",
    "Yield_Definition",
    "Reported_Ultimate_Strength_MPa",
    "Reported_Elongation_pct",
    "Strain_Basis_Status",
    "Target_Status",
    "TRIP_Parent_Phase",
    "TRIP_Product_Phase",
    "TWIP_Phase",
    "TWIP_Mode",
    "Slip_Evidence_Type",
    "TRIP_Onset_Macro_Stress_MPa",
    "HCP_Tensile_Twin_Onset_Macro_Stress_MPa",
    "HCP_Multiple_Twin_Onset_Macro_Stress_MPa",
    "HCP_Multiple_Twin_Onset_Macro_Strain_pct",
    "TRIP_Late_Suppression_Strain_Threshold_pct",
    "TRIP_Rate_Status",
    "FCC_fraction_at_fracture",
    "HCP_fraction_at_fracture",
    "Fracture_Phase_Fraction_Status",
    "Instrument",
    "Facility",
    "Diffraction_Type",
    "Detector_Directions",
    "Detector_Banks",
    "Phase_Quantification_Method",
    "Peak_Analysis_Method",
    "Neutron_Measured_Quantities",
    "Stage_Label",
    "Stage_Stress_Range_Raw",
    "Stage_Strain_Relation",
    "Macro_Stress_MPa",
    "Macro_Strain_pct",
    "Mechanism_Event",
    "TRIP_Stage",
    "TWIP_Stage",
    "Slip_Stage",
    "Stage_Evidence_Type",
    "P020_Target_Semantic_Note",
]

MEANINGFUL_NA_FIELDS = {
    "Measured_Bulk_Composition",
    "Measured_Composition_at_pct",
    "Recovered_Bulk_Composition_at_pct",
    "Physical_Batch_ID",
    "Replicate_ID",
    "Replicate_n",
    "Test_T_K",
    "Strain_rate_s-1",
    "Gauge_length_mm",
    "Gauge_width_mm",
    "Specimen_thickness_mm",
    "SFE_mJ_m2",
    "SFE_method",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
    "HCP_fraction_at_fracture",
}

PROVENANCE_EXCLUDE = {
    "P020_Recovery_Provenance_JSON",
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
    "Co_at%": "at.%",
    "Cr_at%": "at.%",
    "Homogenization_T_K": "K",
    "Homogenization_time_h": "h",
    "Cold_rolling_reduction_pct": "%",
    "Annealing_T_K": "K",
    "Annealing_time_min": "min",
    "Test_T_K": "K",
    "Strain_rate_s-1": "s^-1",
    "Gauge_length_mm": "mm",
    "Gauge_width_mm": "mm",
    "Specimen_thickness_mm": "mm",
    "Initial_FCC_fraction": "fraction",
    "Initial_HCP_fraction": "fraction",
    "Recovered_Initial_FCC_fraction": "fraction",
    "Recovered_Initial_HCP_fraction": "fraction",
    "Grain_size_um": "um",
    "FCC_Grain_Size_um": "um",
    "HCP_Lath_Thickness_um": "um",
    "Apparent_Yield_Onset_MPa": "MPa",
    "Reported_Ultimate_Strength_MPa": "MPa",
    "Reported_Elongation_pct": "%",
    "Effective_TRIP": "binary",
    "Effective_TWIP": "binary",
    "Recovered_TRIP": "binary",
    "Recovered_TWIP": "binary",
    "Slip": "binary",
    "TRIP_Onset_Macro_Stress_MPa": "MPa",
    "HCP_Tensile_Twin_Onset_Macro_Stress_MPa": "MPa",
    "HCP_Multiple_Twin_Onset_Macro_Stress_MPa": "MPa",
    "HCP_Multiple_Twin_Onset_Macro_Strain_pct": "%",
    "TRIP_Late_Suppression_Strain_Threshold_pct": "%",
    "FCC_fraction_at_fracture": "fraction",
    "HCP_fraction_at_fracture": "fraction",
    "Macro_Stress_MPa": "MPa",
    "Macro_Strain_pct": "%",
    "TRIP_Stage": "binary",
    "TWIP_Stage": "binary",
    "Slip_Stage": "binary",
    "TRIP_at_stage": "binary",
    "TWIP_at_stage": "binary",
    "Slip_at_stage": "binary",
    "SFE_mJ_m2": "mJ/m2",
    "DeltaG_FCC_HCP_J_mol": "J/mol",
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def is_present(value) -> bool:
    return pd.notna(value) and str(value).strip() not in {"", "NA", "N/A", "nan", "None"}


def c_to_k(value) -> float:
    """Represent a source-reported Celsius temperature in an existing K field."""
    return float(value) + 273.15


def json_ready(value):
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def experimental_pool(data: pd.DataFrame) -> pd.DataFrame:
    """Apply all established replacement gates before counting conditions."""
    out = data[
        data.Data_Origin.eq("EXPERIMENTAL")
        & data.Observation_Role.eq("INDEPENDENT_CONDITION")
    ].copy()
    for paper, column, pattern in [
        ("P012", "P012_Record_Role", r"P012_C0[1-6]"),
        ("P011", "P011_Record_Role", r"P011_C0[1-5]"),
    ]:
        if column in data and data[column].eq("RECOVERED_EXACT_CONDITION").any():
            out = out[~(out.Paper_ID.eq(paper) & out.Condition_ID.str.match(pattern, na=False))]
    if "P008_Record_Role" in out:
        out = out[
            ~out.P008_Record_Role.eq(
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
            out = out[
                ~(out.Paper_ID.eq(paper) & ~out[column].eq("RECOVERED_EXACT_CONDITION"))
            ]
    return out.copy()


def counts(data: pd.DataFrame) -> tuple[int, int, int, int]:
    pool = experimental_pool(data)
    return (
        len(pool),
        int(pool.Effective_TRIP.notna().sum()),
        int(pool.Effective_TWIP.notna().sum()),
        int(pool[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum()),
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


def load_and_verify() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    assert file_hash(SOURCE) == SOURCE_SHA256, "recovery-v13 source changed before P020 integration"
    assert file_hash(BOOK) == BOOK_SHA256, "verified P020 workbook changed"
    source = pd.read_csv(SOURCE, low_memory=False)
    assert not source.Paper_ID.eq(PAPER_ID).any(), "P020 already exists in recovery v13"
    assert not source.DOI.eq(DOI).any(), "P020 DOI already exists in recovery v13"

    sheets = pd.read_excel(BOOK, sheet_name=None, dtype=object)
    assert set(sheets) == REQUIRED_SHEETS
    for frame in sheets.values():
        if "Paper_ID" in frame:
            assert set(frame.Paper_ID.dropna()) == {PAPER_ID}
        if "DOI" in frame:
            assert set(frame.DOI.dropna()) == {DOI}

    identity = sheets["P020_Study_Identity"].iloc[0]
    assert identity.Paper_ID == PAPER_ID and identity.DOI == DOI
    assert identity.Title == TITLE and identity.Journal == JOURNAL
    assert int(identity.Volume) == 6 and int(identity.Issue) == 11
    assert str(identity.Pages) == "620-626" and int(identity.Year) == 2018
    assert identity.Data_Origin == "EXPERIMENTAL"
    assert identity.Source_Identity_Status == "VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH"

    condition = sheets["P020_Condition"]
    assert len(condition) == 1 and condition.iloc[0].ML_Condition_ID == PRIMARY_ID
    assert condition.iloc[0].Study_Series_ID == SERIES
    assert condition.iloc[0].Material_Parent_ID == MATERIAL
    assert bool(condition.iloc[0].Independent_Experimental_ML_sample)
    assert condition.iloc[0].Nominal_Composition == "Fe50Mn30Co10Cr10"
    assert pd.isna(condition.iloc[0].Measured_Bulk_Composition)
    assert pd.isna(condition.iloc[0].Test_T_K)
    assert pd.isna(condition.iloc[0]["Strain_Rate_s-1"])

    micro = sheets["P020_Initial_Microstructure"].iloc[0]
    assert float(micro.Initial_FCC_fraction) == 0.79
    assert float(micro.Initial_HCP_fraction) == 0.21
    target = sheets["P020_Target_Evidence"].iloc[0]
    assert (int(target.Effective_TRIP), int(target.Effective_TWIP), int(target.Slip)) == (1, 1, 1)
    assert target.TWIP_Phase == "HCP"

    stages = sheets["P020_Stage_Evidence"]
    assert len(stages) == 6 and set(stages.Observation_ID) == STAGE_IDS
    assert stages.Independent_ML_sample.eq(False).all()
    phase = sheets["P020_Phase_Evolution"].set_index("Phase_Record_ID")
    assert float(phase.loc["P020_PHASE_FRACTURE", "FCC_Fraction"]) == 0.17
    assert pd.isna(phase.loc["P020_PHASE_FRACTURE", "HCP_Fraction"])
    return source, sheets


def _row_template(columns: list[str]) -> dict:
    return {column: pd.NA for column in columns}


def make_primary_row(columns: list[str], sheets: dict[str, pd.DataFrame]) -> dict:
    identity = sheets["P020_Study_Identity"].iloc[0]
    condition = sheets["P020_Condition"].iloc[0]
    micro = sheets["P020_Initial_Microstructure"].iloc[0]
    mechanics = sheets["P020_Mechanical_Response"].iloc[0]
    target = sheets["P020_Target_Evidence"].iloc[0]
    method = sheets["P020_InSitu_Method"].iloc[0]
    evidence_url = f"https://doi.org/{DOI}"
    row = _row_template(columns)
    row.update(
        {
            "Paper_ID": PAPER_ID,
            "DOI": DOI,
            "Paper_Title": TITLE,
            "Journal": identity.Journal,
            "Volume": int(identity.Volume),
            "Issue": int(identity.Issue),
            "Pages": identity.Pages,
            "Publication_Year": int(identity.Year),
            "Source_URL": evidence_url,
            "Condition_ID": PRIMARY_ID,
            "Experiment_Group_ID": SERIES,
            "Parent_Experiment_ID": PRIMARY_ID,
            "ML_Condition_ID": PRIMARY_ID,
            "Parent_ML_Condition_ID": PRIMARY_ID,
            "Observation_ID": "P020_OBS_PRIMARY",
            "Data_Origin": "EXPERIMENTAL",
            "Observation_Role": "INDEPENDENT_CONDITION",
            "Row_Type": "Primary experimental in-situ tensile condition",
            "Independent_ML_sample": True,
            "Independent_Experimental_ML_sample": True,
            "Experimental_Target_Eligibility": True,
            "Study_Series_ID": SERIES,
            "Material_Parent_ID": MATERIAL,
            "Physical_Batch_ID": pd.NA,
            "Replicate_ID": pd.NA,
            "Replicate_n": pd.NA,
            "Leakage_Group_Strict": SERIES,
            "Leakage_Group_Material": MATERIAL,
            "Grouping_Confidence": "HIGH",
            "Grouping_Review_Required": False,
            "Grouping_Reason": "New verified paper, one source-defined tensile condition and correlated in-situ stages",
            "P020_Record_Role": "RECOVERED_EXACT_PRIMARY_CONDITION",
            "P020_Target_Status": "VERIFIED_JOINT",
            "P020_Source_Identity_Status": "VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH",
            "P020_QC_Status": "PENDING_GLOBAL_QC_SCHEMA_SPLIT_REFRESH",
            "P020_Supplement_Status": "NOT_INCLUDED_TEST_METADATA_NOT_INFERRED",
            "Alloy_ID": "Fe50Mn30Co10Cr10",
            "Alloy_Family_Text": "Fe50Mn30Co10Cr10",
            "Alloy_Family_Use": "GROUPING_AUDIT_ONLY_NOT_PREDICTOR_NOT_SAMPLE_IDENTITY",
            "Original_Composition": "Fe50Mn30Co10Cr10",
            "Nominal_Composition_at_pct": "Fe50Mn30Co10Cr10",
            "Composition_basis": "at.% nominal",
            "Fe_at%": 50.0,
            "Mn_at%": 30.0,
            "Co_at%": 10.0,
            "Cr_at%": 10.0,
            "Measured_Bulk_Composition": pd.NA,
            "Measured_Composition_at_pct": pd.NA,
            "Recovered_Bulk_Composition_at_pct": pd.NA,
            "Composition_Status": "NOMINAL_ONLY_NO_QUANTITATIVE_POSTMELT_BULK_CHEMISTRY_REPORTED",
            "Raw_Material_Purity": ">99.9 wt.%",
            "Melting_Route": "Vacuum arc melting",
            "Casting_Route": "Drop casting",
            "Cast_method": "Vacuum arc melting; drop casting",
            "Cast_Bar_Dimensions_mm": "12.7 x 12.7 x 75",
            "Homogenization_T_K": c_to_k(condition.Homogenization_T_C),
            "Homogenization_time_h": float(condition.Homogenization_Time_h),
            "Homogenization_Atmosphere": "vacuum",
            "Rolling_T_Raw": "room-temperature rolling",
            "Cold_rolling_reduction_pct": float(condition.Rolling_Reduction_pct),
            "Annealing_T_K": c_to_k(condition.Anneal_T_C),
            "Annealing_time_min": float(condition.Anneal_Time_h) * 60.0,
            "Cooling_route": "Air cooling",
            "Post_Anneal_Cooling": "air cooling",
            "Processing_route": (
                "Vacuum arc melting from >99.9 wt.% raw metals; drop cast to 12.7 x 12.7 x 75 mm; "
                "homogenized at 1150 C for 4 h in vacuum; room-temperature rolled 75%; "
                "annealed at 950 C for 1 h; air cooled"
            ),
            "Test_T_Raw": "NOT_EXPLICITLY_REPORTED_IN_MAIN_ARTICLE",
            "Test_T_K": pd.NA,
            "Strain_rate_s-1": pd.NA,
            "Gauge_length_mm": pd.NA,
            "Gauge_width_mm": pd.NA,
            "Specimen_thickness_mm": pd.NA,
            "Loading_Mode": "Uniaxial tension during real-time in-situ neutron diffraction",
            "Test_Metadata_Status": "SUPPLEMENT_REFERENCED_NOT_AVAILABLE_NO_INFERENCE",
            "Initial_Phase": "DUAL_PHASE_FCC_PLUS_HCP",
            "Initial_Phase_State_Qualitative": "DUAL_PHASE_FCC_PLUS_HCP",
            "Initial_Phase_Status": "DIRECT_EBSD_AND_NEUTRON_DIFFRACTION_AGREEMENT",
            "Initial_FCC_fraction": float(micro.Initial_FCC_fraction),
            "Initial_HCP_fraction": float(micro.Initial_HCP_fraction),
            "Recovered_Initial_FCC_fraction": float(micro.Initial_FCC_fraction),
            "Recovered_Initial_HCP_fraction": float(micro.Initial_HCP_fraction),
            "Recovered_Initial_HCP_status": "DIRECT_EBSD_AND_NEUTRON_DIFFRACTION",
            "Initial_HCP_Status": "DIRECT_PRETEST_EBSD_AND_NEUTRON_DIFFRACTION",
            "Initial_HCP_Origin": "PRE_EXISTING_BEFORE_TENSILE_LOADING",
            "Initial_TRIP_Target_Guardrail": "PRE_EXISTING_HCP_DOES_NOT_ESTABLISH_TRIP_DYNAMIC_FCC_LOSS_REQUIRED",
            "Grain_size_um": float(micro.FCC_Grain_Size_um),
            "FCC_Grain_Size_um": float(micro.FCC_Grain_Size_um),
            "Grain_Size_Scope": "FCC_AVERAGE",
            "Grain_Size_Status": "APPROX_DIRECT_TEXT",
            "FCC_Grain_Morphology": micro.FCC_Grain_Morphology,
            "HCP_Lath_Thickness_um": float(micro.HCP_Lath_Thickness_um),
            "HCP_Morphology": micro.HCP_Morphology,
            "HCP_lath_or_lamella_note": "Lath-shaped HCP; average HCP lath thickness approximately 4 um",
            "Phase_Fraction_Methods": micro.Phase_Fraction_Methods,
            "Apparent_Yield_Onset_MPa": float(mechanics.Apparent_Yield_Onset_MPa),
            "Yield_Definition": "OBSERVABLE_DEVIATION_FROM_ELASTIC_REGIME",
            "Reported_Ultimate_Strength_MPa": float(mechanics.Reported_Ultimate_Strength_MPa),
            "Reported_Elongation_pct": float(mechanics.Reported_Elongation_pct),
            "Strain_Basis_Status": mechanics.Strain_Basis_Status,
            "Mechanical_Value_Status": "DIRECT_SOURCE_RAW_BASIS",
            "Mechanical_Predictor_Eligibility": "MECHANICAL_OUTCOME_LEAKAGE",
            "Original_TRIP": pd.NA,
            "Original_TWIP": pd.NA,
            "Recovered_TRIP": 1,
            "Recovered_TWIP": 1,
            "Effective_TRIP": 1,
            "Effective_TWIP": 1,
            "Slip": 1,
            "Target_Status": "VERIFIED_JOINT",
            "TRIP_Parent_Phase": "FCC",
            "TRIP_Product_Phase": "HCP",
            "TWIP_Phase": "HCP",
            "TWIP_Mode": "HCP_TENSILE_AND_COMPRESSION_TWINNING",
            "TRIP_Evidence_Type": "DIRECT_REALTIME_NEUTRON_PHASE_FRACTION_EVOLUTION",
            "TWIP_Evidence_Type": "DIRECT_REALTIME_NEUTRON_GRAIN_REORIENTATION",
            "Slip_Evidence_Type": target.Slip_Evidence_Type,
            "Evidence_TRIP": (
                "Real-time neutron/Rietveld phase fractions show continuous FCC loss from 0.79 "
                "during tensile loading to approximately 0.17 remaining at fracture."
            ),
            "Evidence_TWIP": (
                "Real-time neutron grain-family intensity splitting and LD/TD reorientation show "
                "HCP {10.2} tensile twinning near 400 MPa and later compression/multiple HCP twinning."
            ),
            "Condition_Level_Target_Evidence": target.Condition_Level_Evidence,
            "Target_Evidence_Confidence": "High",
            "Label_confidence": "High",
            "P020_Target_Semantic_Note": (
                "TWIP is deformation twinning in HCP, not FCC; initial 0.21 HCP is pre-existing "
                "and TRIP is assigned from dynamic FCC loss."
            ),
            "TRIP_Onset_Macro_Stress_MPa": 200.0,
            "HCP_Tensile_Twin_Onset_Macro_Stress_MPa": 400.0,
            "HCP_Multiple_Twin_Onset_Macro_Stress_MPa": 730.0,
            "HCP_Multiple_Twin_Onset_Macro_Strain_pct": 15.0,
            "TRIP_Late_Suppression_Strain_Threshold_pct": 25.0,
            "TRIP_Rate_Status": "SLOWS_ABOVE_APPROX_25_PERCENT_STRAIN_BUT_REMAINS_ACTIVE_TO_FRACTURE",
            "Tensile_TWIP_Onset_Stress_MPa": 400.0,
            "Compression_Twinning_Onset_Stress_MPa": 730.0,
            "Mechanism_Phase_Scope": "TRIP: FCC_TO_HCP; TWIP: HCP_TENSILE_AND_COMPRESSION; SLIP: FCC_AND_HCP",
            "FCC_fraction_at_fracture": 0.17,
            "HCP_fraction_at_fracture": pd.NA,
            "Fracture_Phase_Fraction_Status": "DIRECT_FCC_ONLY_HCP_COMPLEMENT_NOT_DERIVED",
            "SFE_mJ_m2": pd.NA,
            "SFE_method": pd.NA,
            "SFE_Value_Status": "NOT_REPORTED_IN_P020_MAIN_ARTICLE_NO_CROSS_PAPER_TRANSFER",
            "SFE_Data_Origin": "UNRESOLVED_NO_P020_VALUE",
            "DeltaG_FCC_HCP_J_mol": pd.NA,
            "DeltaG_method": pd.NA,
            "DeltaG_Value_Status": "NOT_REPORTED_IN_P020_MAIN_ARTICLE_NO_CROSS_PAPER_TRANSFER",
            "DeltaG_Data_Origin": "UNRESOLVED_NO_P020_VALUE",
            "Characterization_methods": method.Diffraction_Type,
            "Instrument": method.Instrument,
            "Facility": method.Facility,
            "Diffraction_Type": method.Diffraction_Type,
            "Detector_Directions": "Loading direction (LD) and transverse direction (TD)",
            "Detector_Banks": "-90 degrees and +90 degrees",
            "Phase_Quantification_Method": "Rietveld refinement",
            "Peak_Analysis_Method": "Single-peak fitting",
            "Neutron_Measured_Quantities": method.Measured_Quantities,
            "Source_location": "Experimental section and Figs.1-4, pp.621-625",
        }
    )
    return row


def _stage_twin_mode(observation_id: str, twip_phase) -> object:
    if not is_present(twip_phase):
        return pd.NA
    if observation_id == "P020_STAGE_HCP_TENSILE_TWIN":
        return "HCP_{10.2}_TENSILE_TWINNING"
    if observation_id == "P020_STAGE_MULTI_TWIN":
        return "HCP_COMPRESSION_AND_MULTIPLE_TWINNING"
    return "HCP_TENSILE_AND_COMPRESSION_TWINNING"


def make_stage_rows(columns: list[str], sheets: dict[str, pd.DataFrame]) -> list[dict]:
    rows: list[dict] = []
    phase = sheets["P020_Phase_Evolution"].set_index("Phase_Record_ID")
    for stage in sheets["P020_Stage_Evidence"].to_dict("records"):
        obs = stage["Observation_ID"]
        row = _row_template(columns)
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Journal": JOURNAL,
                "Volume": 6,
                "Issue": 11,
                "Pages": "620-626",
                "Publication_Year": 2018,
                "Source_URL": f"https://doi.org/{DOI}",
                "Condition_ID": obs,
                "Experiment_Group_ID": SERIES,
                "Parent_Experiment_ID": PRIMARY_ID,
                "ML_Condition_ID": pd.NA,
                "Parent_ML_Condition_ID": PRIMARY_ID,
                "Observation_ID": obs,
                "Deformation_Stage_ID": obs,
                "Data_Origin": "EXPERIMENTAL",
                "Observation_Role": stage["Observation_Role"],
                "Row_Type": "Correlated real-time in-situ neutron observation",
                "Independent_ML_sample": False,
                "Independent_Experimental_ML_sample": False,
                "Experimental_Target_Eligibility": False,
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": MATERIAL,
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": MATERIAL,
                "Grouping_Confidence": "HIGH",
                "Grouping_Review_Required": False,
                "Grouping_Reason": "Correlated observation from parent in-situ tensile condition",
                "P020_Record_Role": (
                    "RECOVERED_CORRELATED_POST_TEST_ENDPOINT"
                    if stage["Observation_Role"] == "CORRELATED_POST_TEST_ENDPOINT"
                    else "RECOVERED_CORRELATED_IN_SITU_STAGE"
                ),
                "P020_Target_Status": "STAGE_SPECIFIC_SUPPORT_NOT_CONDITION_LABEL",
                "P020_Source_Identity_Status": "VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH",
                "P020_QC_Status": "PENDING_GLOBAL_QC_SCHEMA_SPLIT_REFRESH",
                "Alloy_ID": "Fe50Mn30Co10Cr10",
                "Alloy_Family_Text": "Fe50Mn30Co10Cr10",
                "Alloy_Family_Use": "GROUPING_AUDIT_ONLY_NOT_PREDICTOR_NOT_SAMPLE_IDENTITY",
                "Original_Composition": "Fe50Mn30Co10Cr10",
                "Composition_basis": "at.% nominal",
                "Target_Status": "STAGE_SPECIFIC_SUPPORT_NOT_CONDITION_LABEL",
                "Stage_Label": stage["Stage"],
                "Macro_Stress_MPa": stage["Macro_Stress_MPa"],
                "Macro_Strain_pct": stage["Macro_Strain_pct"],
                "Mechanism_Event": stage["Mechanism_Event"],
                "TRIP_Stage": int(stage["TRIP_Stage"]),
                "TWIP_Stage": int(stage["TWIP_Stage"]),
                "Slip_Stage": int(stage["Slip_Stage"]),
                "TRIP_at_stage": int(stage["TRIP_Stage"]),
                "TWIP_at_stage": int(stage["TWIP_Stage"]),
                "Slip_at_stage": int(stage["Slip_Stage"]),
                "TWIP_Phase": stage["TWIP_Phase"],
                "TWIP_Mode": _stage_twin_mode(obs, stage["TWIP_Phase"]),
                "Stage_Evidence_Type": stage["Evidence_Type"],
                "Stage_Method": "Real-time in-situ time-of-flight neutron diffraction",
                "Characterization_methods": "Real-time in-situ time-of-flight neutron diffraction",
                "Source_location": stage["Evidence_Location"],
                "Target_Evidence_Confidence": stage["Confidence"],
                "P020_Target_Semantic_Note": stage["Notes"],
            }
        )
        if obs == "P020_STAGE_I_ELASTIC":
            row["Stage_Stress_Range_Raw"] = "0 to approximately 200 MPa"
            row["P020_Target_Semantic_Note"] = (
                "Pre-yield stage-specific zeros only; never condition-level negatives."
            )
        elif obs == "P020_STAGE_MULTI_TWIN":
            row["Stage_Strain_Relation"] = "approximately 15% strain"
        elif obs == "P020_STAGE_LATE_TRIP_SUPPRESSION":
            row["Stage_Strain_Relation"] = "> approximately 25% strain"
            row["TRIP_Rate_Status"] = "RATE_DECREASED_TRIP_REMAINS_ACTIVE"
        elif obs == "P020_STAGE_FRACTURE":
            row["Stage_Strain_Relation"] = "reported elongation approximately 34%; source basis preserved"
            row["FCC_fraction_at_fracture"] = float(
                phase.loc["P020_PHASE_FRACTURE", "FCC_Fraction"]
            )
            row["HCP_fraction_at_fracture"] = pd.NA
            row["Fracture_Phase_Fraction_Status"] = "DIRECT_FCC_ONLY_HCP_COMPLEMENT_NOT_DERIVED"
        rows.append(row)
    return rows


def _field_domain(field: str) -> tuple[str, str, str]:
    identity = {
        "Paper_ID", "DOI", "Paper_Title", "Journal", "Volume", "Issue", "Pages",
        "Publication_Year", "Source_URL", "Data_Origin", "P020_Source_Identity_Status",
    }
    hierarchy = {
        "Condition_ID", "Experiment_Group_ID", "Parent_Experiment_ID", "ML_Condition_ID",
        "Parent_ML_Condition_ID", "Observation_ID", "Deformation_Stage_ID", "Observation_Role",
        "Row_Type", "Independent_ML_sample", "Independent_Experimental_ML_sample",
        "Experimental_Target_Eligibility", "Study_Series_ID", "Material_Parent_ID",
        "Physical_Batch_ID", "Replicate_ID", "Replicate_n", "Leakage_Group_Strict",
        "Leakage_Group_Material", "Grouping_Confidence", "Grouping_Review_Required",
        "Grouping_Reason", "P020_Record_Role", "P020_QC_Status",
    }
    composition_processing = {
        "Alloy_ID", "Alloy_Family_Text", "Alloy_Family_Use", "Original_Composition",
        "Nominal_Composition_at_pct", "Composition_basis", "Fe_at%", "Mn_at%", "Co_at%",
        "Cr_at%", "Measured_Bulk_Composition", "Measured_Composition_at_pct",
        "Recovered_Bulk_Composition_at_pct", "Composition_Status", "Raw_Material_Purity",
        "Melting_Route", "Casting_Route", "Cast_method", "Cast_Bar_Dimensions_mm",
        "Homogenization_T_K", "Homogenization_time_h", "Homogenization_Atmosphere",
        "Rolling_T_Raw", "Cold_rolling_reduction_pct", "Annealing_T_K",
        "Annealing_time_min", "Cooling_route", "Post_Anneal_Cooling", "Processing_route",
        "Test_T_Raw", "Test_T_K", "Strain_rate_s-1", "Gauge_length_mm", "Gauge_width_mm",
        "Specimen_thickness_mm", "Loading_Mode", "Test_Metadata_Status",
        "P020_Supplement_Status",
    }
    microstructure = {
        "Initial_Phase", "Initial_Phase_State_Qualitative", "Initial_Phase_Status",
        "Initial_FCC_fraction", "Initial_HCP_fraction", "Recovered_Initial_FCC_fraction",
        "Recovered_Initial_HCP_fraction", "Recovered_Initial_HCP_status", "Initial_HCP_Status",
        "Initial_HCP_Origin", "Initial_TRIP_Target_Guardrail", "Grain_size_um",
        "FCC_Grain_Size_um", "Grain_Size_Scope", "Grain_Size_Status",
        "FCC_Grain_Morphology", "HCP_Lath_Thickness_um", "HCP_Morphology",
        "HCP_lath_or_lamella_note", "Phase_Fraction_Methods",
    }
    mechanics = {
        "Apparent_Yield_Onset_MPa", "Yield_Definition", "Reported_Ultimate_Strength_MPa",
        "Reported_Elongation_pct", "Strain_Basis_Status", "Mechanical_Value_Status",
        "Mechanical_Predictor_Eligibility",
    }
    method = {
        "Characterization_methods", "Instrument", "Facility", "Diffraction_Type",
        "Detector_Directions", "Detector_Banks", "Phase_Quantification_Method",
        "Peak_Analysis_Method", "Neutron_Measured_Quantities",
    }
    physics = {
        "SFE_mJ_m2", "SFE_method", "SFE_Value_Status", "SFE_Data_Origin",
        "DeltaG_FCC_HCP_J_mol", "DeltaG_method", "DeltaG_Value_Status", "DeltaG_Data_Origin",
    }
    if field in identity:
        return "SOURCE_IDENTITY", "Whole verified article", "Verified workbook and publisher DOI identity"
    if field in hierarchy:
        return "HIERARCHY_INTEGRATION", "Verified condition/stage sheets", "Source-defined condition hierarchy"
    if field in composition_processing:
        return "DIRECT_TEXT_OR_VERIFIED_NA", "Experimental section, pp.621-622", "Source text; C-to-K representation only where required by existing field"
    if field in microstructure:
        return "DIRECT_EBSD_AND_NEUTRON", "Experimental section and Fig.1, pp.621-622", "EBSD and neutron diffraction"
    if field in mechanics:
        return "DIRECT_SOURCE_RAW_BASIS", "Results and Fig.2, p.622", "Tensile loading; source stress/strain basis preserved"
    if field in method:
        return "DIRECT_METHOD_METADATA", "Experimental section, pp.621-622", "Real-time in-situ time-of-flight neutron diffraction"
    if field in physics:
        return "VERIFIED_ABSENCE_IN_MAIN_ARTICLE", "Whole uploaded main article", "Source review; no cross-paper transfer"
    return "DIRECT_CONDITION_OR_STAGE_EVIDENCE", "Figs.2-4 and text, pp.622-625", "Real-time in-situ neutron diffraction and source interpretation"


def _na_status(field: str) -> str:
    if field == "HCP_fraction_at_fracture":
        return "VERIFIED_NA_NOT_SOURCE_REPORTED_NO_COMPLEMENT_DERIVATION"
    if field in {"SFE_mJ_m2", "SFE_method", "DeltaG_FCC_HCP_J_mol", "DeltaG_method"}:
        return "VERIFIED_NA_NOT_REPORTED_NO_CROSS_PAPER_TRANSFER"
    if field in {"Test_T_K", "Strain_rate_s-1", "Gauge_length_mm", "Gauge_width_mm", "Specimen_thickness_mm"}:
        return "VERIFIED_NA_PENDING_MISSING_SUPPLEMENT"
    if field in {"Measured_Bulk_Composition", "Measured_Composition_at_pct", "Recovered_Bulk_Composition_at_pct"}:
        return "VERIFIED_NA_NO_QUANTITATIVE_POSTMELT_BULK_CHEMISTRY"
    return "VERIFIED_NA_NOT_SOURCE_SUPPORTED"


def build_provenance(new_rows: list[dict], sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict] = []
    for record in new_rows:
        record_id = record["Observation_ID"]
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            meaningful_na = (
                record_id == "P020_OBS_PRIMARY" and feature in MEANINGFUL_NA_FIELDS
            ) or (
                record_id == "P020_STAGE_FRACTURE"
                and feature == "HCP_fraction_at_fracture"
            )
            if not is_present(value) and not meaningful_na:
                continue
            evidence_type, evidence_location, method = _field_domain(feature)
            recovery_status = "VERIFIED" if is_present(value) else _na_status(feature)
            rows.append(
                {
                    "Paper_ID": PAPER_ID,
                    "DOI": DOI,
                    "Study_Series_ID": SERIES,
                    "Material_Parent_ID": MATERIAL,
                    "ML_Condition_ID": record.get("ML_Condition_ID", pd.NA),
                    "Observation_ID": record_id,
                    "Record_ID": record_id,
                    "Feature_Name": feature,
                    "Recovered_Value": value if is_present(value) else "UNRESOLVED_NA",
                    "Units": UNIT_MAP.get(feature, "as reported"),
                    "Evidence_Type": evidence_type,
                    "Evidence_Location": record.get("Source_location", evidence_location),
                    "Method": method,
                    "Confidence": record.get("Target_Evidence_Confidence", "High"),
                    "Recovery_Status": recovery_status,
                    "Data_Origin": "EXPERIMENTAL",
                    "Source_URL": f"https://doi.org/{DOI}",
                    "Provenance_Layer": "MASTER_FIELD_MAPPING",
                }
            )

    # Preserve the workbook's explicit source ledger as a second, unmodified evidence layer.
    for source in sheets["P020_Provenance"].to_dict("records"):
        record_id = str(source["Record_ID"])
        if record_id == MATERIAL:
            ml_id = pd.NA
            obs_id = pd.NA
        elif record_id == PRIMARY_ID:
            ml_id = PRIMARY_ID
            obs_id = "P020_OBS_PRIMARY"
        else:
            ml_id = pd.NA
            obs_id = record_id
        rows.append(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": MATERIAL,
                "ML_Condition_ID": ml_id,
                "Observation_ID": obs_id,
                "Record_ID": record_id,
                "Feature_Name": source["Feature_Name"],
                "Recovered_Value": (
                    source["Recovered_Value"]
                    if is_present(source["Recovered_Value"])
                    else "UNRESOLVED_NA"
                ),
                "Units": source["Units"],
                "Evidence_Type": source["Evidence_Type"],
                "Evidence_Location": source["Evidence_Location"],
                "Method": source["Method"],
                "Confidence": source["Confidence"],
                "Recovery_Status": source["Recovery_Status"],
                "Data_Origin": "EXPERIMENTAL",
                "Source_URL": source["Source_URL"],
                "Provenance_Layer": "VERIFIED_WORKBOOK_LEDGER",
            }
        )
    frame = pd.DataFrame(rows).drop_duplicates(ignore_index=True)
    required = {
        "Paper_ID", "DOI", "Study_Series_ID", "Material_Parent_ID", "Feature_Name",
        "Recovered_Value", "Units", "Evidence_Type", "Evidence_Location", "Method",
        "Confidence", "Recovery_Status", "Data_Origin",
    }
    assert frame[list(required)].notna().all().all()
    return frame


def attach_provenance_json(new_rows: list[dict], provenance: pd.DataFrame) -> None:
    for row in new_rows:
        record_id = row["Observation_ID"]
        selected = provenance[
            provenance.Observation_ID.eq(record_id)
            | (provenance.Record_ID.eq(MATERIAL) & (record_id == "P020_OBS_PRIMARY"))
        ]
        row["P020_Recovery_Provenance_JSON"] = json.dumps(
            json_ready(selected.to_dict("records")),
            ensure_ascii=False,
            allow_nan=False,
        )


def scientific_safeguards() -> pd.DataFrame:
    rules = [
        ("S001", "INITIAL_HCP_NOT_TRIP", "Initial 0.21 HCP is pre-existing; assign TRIP only from dynamic FCC loss."),
        ("S002", "PHASE_SPECIFIC_TWIP", "P020 TWIP is HCP tensile/compression twinning, never FCC twinning."),
        ("S003", "STAGE_NON_INDEPENDENCE", "All six in-situ observations are correlated children of one condition."),
        ("S004", "STAGE_ZERO_SCOPE", "Stage-I pre-yield zeros never become condition-level mechanism negatives."),
        ("S005", "MISSING_SUPPLEMENT_NO_INFERENCE", "Test temperature, rate, geometry, and replicate count remain NA."),
        ("S006", "APPARENT_YIELD_DEFINITION", "Approximately 200 MPa is observable elastic-deviation onset, not 0.2% offset YS."),
        ("S007", "FRACTURE_COMPLEMENT_NOT_DERIVED", "Direct FCC approximately 0.17 is retained; exact HCP 0.83 is not fabricated."),
        ("S008", "NO_CROSS_PAPER_PHYSICS", "P020 SFE and DeltaG remain NA; no Fe50Mn30Co10Cr10 value is transferred."),
        ("S009", "COMMON_COMPOSITION_NOT_SAME_SAMPLE", "P020 remains separate from P003/P011/P013/P014 despite nominal text."),
        ("S010", "MECHANICAL_OUTCOME_LEAKAGE", "Yield onset, strength, and elongation are post-loading outcomes."),
        ("S011", "TRIP_RATE_SUPPRESSION_NOT_ABSENCE", "Slower transformation above approximately 25% strain remains TRIP-positive."),
        ("S012", "NO_MODEL_OR_FEATURE_ENGINEERING", "Recovery v14 creates no model, metric, imputation, normalization, or descriptor."),
    ]
    return pd.DataFrame(
        [
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Safeguard_ID": safeguard_id,
                "Safeguard": name,
                "Rule": rule,
                "Status": "ENFORCED",
                "Data_Origin": "EXPERIMENTAL",
                "Source_URL": f"https://doi.org/{DOI}",
            }
            for safeguard_id, name, rule in rules
        ]
    )


def integration_ledger(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = sheets["P020_Integration_Decisions"].copy()
    frame.insert(0, "Paper_ID", PAPER_ID)
    frame.insert(1, "DOI", DOI)
    frame["Study_Series_ID"] = SERIES
    frame["Material_Parent_ID"] = MATERIAL
    frame["ML_Condition_ID"] = PRIMARY_ID
    frame["Data_Origin"] = "EXPERIMENTAL"
    frame["Legacy_Mapping_Status"] = "NEW_PAPER_NO_LEGACY_P020_REPRESENTATION_IN_V13"
    return frame


def processing_table(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    source = sheets["P020_Condition"].copy()
    source["Homogenization_T_K_Representation"] = source.Homogenization_T_C.astype(float) + 273.15
    source["Anneal_T_K_Representation"] = source.Anneal_T_C.astype(float) + 273.15
    source["Anneal_Time_min_Representation"] = source.Anneal_Time_h.astype(float) * 60.0
    source["Test_T_Raw_Canonical"] = "NOT_EXPLICITLY_REPORTED_IN_MAIN_ARTICLE"
    source["Supplement_Status"] = "NOT_INCLUDED_TEST_METADATA_NOT_INFERRED"
    return source


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
    p020 = out[out.Paper_ID.eq(PAPER_ID)]
    primary = p020[p020.P020_Record_Role.eq("RECOVERED_EXACT_PRIMARY_CONDITION")]
    stages = p020[p020.P020_Record_Role.str.contains("CORRELATED", na=False)]
    assert len(source) == 207 and len(out) == 214
    assert len(primary) == 1 and primary.iloc[0].ML_Condition_ID == PRIMARY_ID
    assert set(stages.Observation_ID) == STAGE_IDS and len(stages) == 6
    assert primary.Independent_ML_sample.eq(True).all()
    assert primary.Independent_Experimental_ML_sample.eq(True).all()
    assert stages.Independent_ML_sample.eq(False).all()
    assert stages.Independent_Experimental_ML_sample.eq(False).all()
    assert stages.ML_Condition_ID.isna().all()
    assert stages.Parent_ML_Condition_ID.eq(PRIMARY_ID).all()
    assert stages[["Effective_TRIP", "Effective_TWIP"]].isna().all().all()
    assert primary.Paper_ID.eq(PAPER_ID).all() and primary.DOI.eq(DOI).all()
    assert primary.Study_Series_ID.eq(SERIES).all()
    assert primary.Material_Parent_ID.eq(MATERIAL).all()
    assert primary.Leakage_Group_Strict.eq(SERIES).all()
    assert primary.Leakage_Group_Material.eq(MATERIAL).all()
    assert primary.Physical_Batch_ID.isna().all()
    assert primary.Replicate_ID.isna().all() and primary.Replicate_n.isna().all()
    assert primary.Measured_Bulk_Composition.isna().all()
    assert primary.Measured_Composition_at_pct.isna().all()
    assert primary.Original_Composition.eq("Fe50Mn30Co10Cr10").all()
    assert primary.Initial_FCC_fraction.eq(0.79).all()
    assert primary.Initial_HCP_fraction.eq(0.21).all()
    assert primary.Initial_TRIP_Target_Guardrail.str.contains("DYNAMIC_FCC_LOSS_REQUIRED").all()
    assert primary.FCC_Grain_Size_um.eq(40).all()
    assert primary.HCP_Lath_Thickness_um.eq(4).all()
    assert primary.Effective_TRIP.eq(1).all()
    assert primary.Effective_TWIP.eq(1).all()
    assert primary.Slip.eq(1).all()
    assert primary.TWIP_Phase.eq("HCP").all()
    assert primary.TWIP_Mode.eq("HCP_TENSILE_AND_COMPRESSION_TWINNING").all()
    assert primary.TWIP_Evidence_Type.eq("DIRECT_REALTIME_NEUTRON_GRAIN_REORIENTATION").all()
    assert primary.Test_T_Raw.eq("NOT_EXPLICITLY_REPORTED_IN_MAIN_ARTICLE").all()
    assert primary.Test_T_K.isna().all() and primary["Strain_rate_s-1"].isna().all()
    assert primary.SFE_mJ_m2.isna().all() and primary.DeltaG_FCC_HCP_J_mol.isna().all()
    assert primary.Apparent_Yield_Onset_MPa.eq(200).all()
    assert primary.Yield_Definition.eq("OBSERVABLE_DEVIATION_FROM_ELASTIC_REGIME").all()
    assert primary.Reported_Ultimate_Strength_MPa.eq(1046).all()
    assert primary.Reported_Elongation_pct.eq(34).all()
    assert primary.UTS_MPa.isna().all() and primary.Elongation_pct.isna().all()
    assert primary.FCC_fraction_at_fracture.eq(0.17).all()
    assert primary.HCP_fraction_at_fracture.isna().all()

    indexed = stages.set_index("Observation_ID")
    assert indexed.loc["P020_STAGE_I_ELASTIC", ["TRIP_Stage", "TWIP_Stage", "Slip_Stage"]].astype(int).tolist() == [0, 0, 0]
    assert indexed.loc["P020_STAGE_TRIP_ONSET", "Macro_Stress_MPa"] == 200
    assert indexed.loc["P020_STAGE_HCP_TENSILE_TWIN", "Macro_Stress_MPa"] == 400
    assert indexed.loc["P020_STAGE_HCP_TENSILE_TWIN", "TWIP_Phase"] == "HCP"
    assert indexed.loc["P020_STAGE_MULTI_TWIN", "Macro_Stress_MPa"] == 730
    assert indexed.loc["P020_STAGE_MULTI_TWIN", "Macro_Strain_pct"] == 15
    assert indexed.loc["P020_STAGE_LATE_TRIP_SUPPRESSION", "TRIP_Stage"] == 1
    assert indexed.loc["P020_STAGE_LATE_TRIP_SUPPRESSION", "TRIP_Rate_Status"] == "RATE_DECREASED_TRIP_REMAINS_ACTIVE"
    assert indexed.loc["P020_STAGE_FRACTURE", "FCC_fraction_at_fracture"] == 0.17
    assert pd.isna(indexed.loc["P020_STAGE_FRACTURE", "HCP_fraction_at_fracture"])

    assert counts(source) == (51, 31, 29, 26)
    assert counts(out) == (52, 32, 30, 27)
    assert class_counts(source) == {
        "trip_positive": 27, "trip_negative": 4, "twip_positive": 24,
        "twip_negative": 5, "joint_00": 0, "joint_10": 5,
        "joint_01": 4, "joint_11": 17,
    }
    assert class_counts(out) == {
        "trip_positive": 28, "trip_negative": 4, "twip_positive": 25,
        "twip_negative": 5, "joint_00": 0, "joint_10": 5,
        "joint_01": 4, "joint_11": 18,
    }
    assert not out[out.Paper_ID.eq("P013")].Study_Series_ID.eq(SERIES).any()
    assert not out[out.Paper_ID.eq("P013")].Material_Parent_ID.eq(MATERIAL).any()

    required = {
        "Paper_ID", "DOI", "Study_Series_ID", "Material_Parent_ID", "Feature_Name",
        "Recovered_Value", "Units", "Evidence_Type", "Evidence_Location", "Method",
        "Confidence", "Recovery_Status", "Data_Origin",
    }
    assert provenance[list(required)].notna().all().all()
    master_prov = provenance[provenance.Provenance_Layer.eq("MASTER_FIELD_MAPPING")]
    for record in new_rows:
        record_id = record["Observation_ID"]
        for feature, value in record.items():
            if feature in PROVENANCE_EXCLUDE:
                continue
            meaningful_na = (
                record_id == "P020_OBS_PRIMARY" and feature in MEANINGFUL_NA_FIELDS
            ) or (
                record_id == "P020_STAGE_FRACTURE"
                and feature == "HCP_fraction_at_fracture"
            )
            if is_present(value) or meaningful_na:
                assert len(
                    master_prov[
                        master_prov.Record_ID.eq(record_id)
                        & master_prov.Feature_Name.eq(feature)
                    ]
                ), (record_id, feature)
    hcp_fracture = provenance[provenance.Feature_Name.eq("HCP_fraction_at_fracture")]
    assert hcp_fracture.Recovered_Value.eq("UNRESOLVED_NA").all()
    assert not provenance[
        provenance.Feature_Name.eq("HCP_fraction_at_fracture")
    ].Recovered_Value.astype(str).eq("0.83").any()
    assert primary.P020_Recovery_Provenance_JSON.str.len().gt(2).all()
    assert stages.P020_Recovery_Provenance_JSON.str.len().gt(2).all()
    assert file_hash(SOURCE) == SOURCE_SHA256 and file_hash(BOOK) == BOOK_SHA256


def write_audit(source: pd.DataFrame, out: pd.DataFrame) -> None:
    before = counts(source)
    after = counts(out)
    before_classes = class_counts(source)
    after_classes = class_counts(out)
    AUDIT.write_text(
        f"""# P020 recovery v14 audit

## A. Source identity

- `Paper_ID=P020`; DOI `{DOI}`; title **{TITLE}**.
- Materials Research Letters 6(11), 620-626 (2018). The verified workbook status is `VERIFIED_PDF_AND_PUBLISHER_DOI_MATCH`; both workbook and V13 base were SHA-256 gated.

## B. New-vs-existing source status

- P020 is a new primary experimental source beyond P001-P019. No P020 `Paper_ID` or DOI exists in recovery V13.
- Nominal `Fe50Mn30Co10Cr10` also occurs in P003/P011/P013/P014, but common composition text is not physical-sample identity. P020 has its own preparation, `{SERIES}`, `{MATERIAL}`, and condition; it is not merged into P013 or another paper.

## C-E. V14 size, independence, and exact condition

- Recovery V14 contains **{len(out)} rows**: all **{len(source)}** V13 rows unchanged, one exact P020 primary condition, and six correlated in-situ observations.
- Replacement-aware independent experimental conditions: **{before[0]} before -> {after[0]} after**. The increase is programmatically confirmed only after proving that P020/DOI were absent from V13.
- Exact P020 condition: `{PRIMARY_ID}` under `{SERIES}` / `{MATERIAL}`. Physical batch, replicate identity, and replicate count remain NA.

## F-G. Composition and processing

- Nominal chemistry is `Fe50Mn30Co10Cr10` at.% with status `NOMINAL_ONLY_NO_QUANTITATIVE_POSTMELT_BULK_CHEMISTRY_REPORTED`. Measured bulk chemistry remains NA; no composition or chemistry is transferred from another Fe50Mn30Co10Cr10 paper.
- Processing retains >99.9 wt.% raw-metal purity, vacuum arc melting, drop casting to 12.7 x 12.7 x 75 mm, 1150 C/4 h/vacuum homogenization, room-temperature rolling at 75% reduction, and 950 C/1 h annealing followed by air cooling.

## H. Missing supplement and test conditions

- The main article refers detailed tensile metadata to a supplement that is not present. `Test_T_Raw=NOT_EXPLICITLY_REPORTED_IN_MAIN_ARTICLE`; numeric test temperature, strain rate, specimen geometry, and replicate count remain NA. Room temperature and 1e-3 s^-1 were not imported or inferred.

## I-K. Initial dual-phase microstructure

- EBSD and neutron diffraction independently report initial FCC=0.79 and HCP=0.21. The pre-existing HCP does not generate TRIP; condition-level TRIP is based on dynamic FCC loss during tensile loading.
- FCC grains are equiaxed with average size approximately 40 um. HCP is lath-shaped with average lath thickness approximately 4 um.

## L-O. Condition targets, phase semantics, and slip

- `{PRIMARY_ID}` is verified TRIP=1, TWIP=1, Slip=1 (`VERIFIED_JOINT`).
- TRIP is FCC-to-HCP transformation measured through continuous real-time FCC loss beginning near 200 MPa and persisting to fracture.
- TWIP is explicitly **HCP-phase** `{{10.2}}` tensile twinning followed by compression/multiple HCP twinning. `TWIP_Phase=HCP` and `TWIP_Mode=HCP_TENSILE_AND_COMPRESSION_TWINNING`; it is not labelled as FCC twinning.
- Slip accompanies FCC TRIP and later HCP twinning. Phase-specific meaning is preserved rather than globally redefining the TWIP target.

## P-Q. Stage transitions and fracture phase fraction

- Six observations are non-independent children: elastic 0-to-approximately-200 MPa; TRIP/slip onset near 200 MPa; HCP tensile twinning near 400 MPa; compression/multiple HCP twinning plus slip near 730 MPa and approximately 15% strain; slower-but-persistent TRIP above approximately 25% strain; and the fracture endpoint.
- Stage-I zeros are pre-yield stage values only and are never condition-level negatives. Slower transformation is not absence: the late stage remains TRIP=1.
- Direct remaining FCC at fracture is approximately 0.17. Exact HCP=0.83 is not calculated or stored; the HCP fracture fraction remains NA.

## R. Mechanical response and leakage

- Approximately 200 MPa is stored only as `Apparent_Yield_Onset_MPa` with definition `OBSERVABLE_DEVIATION_FROM_ELASTIC_REGIME`, not conventional 0.2% offset YS.
- Source-reported ultimate strength is 1046 MPa and reported elongation is 34%. The figure's macro true-stress/true-strain context and the text's raw word “elongation” are preserved; no engineering/true conversion is made.
- All response values are `MECHANICAL_OUTCOME_LEAKAGE` for pre-deformation models.

## S-T. SFE and DeltaG gaps

- P020 SFE remains NA. P020 DeltaG remains NA. No 6.5 mJ/m2 or other value is imported, calculated, or transferred from P003/P011/P013/P014.

## U. P020/P013 non-duplication safeguard

- P020 and P013 share nominal composition text but not study, preparation, condition, or material identity. Separate paper/study/material/leakage identifiers are enforced. `Alloy_Family_Text` is grouping-audit metadata only and not an ML predictor.

## V. Usable target counts

- Usable TRIP/TWIP/joint counts: **{before[1]}/{before[2]}/{before[3]} before -> {after[1]}/{after[2]}/{after[3]} after**.
- Binary class support changes TRIP {before_classes['trip_positive']}/{before_classes['trip_negative']} to {after_classes['trip_positive']}/{after_classes['trip_negative']} positive/negative and TWIP {before_classes['twip_positive']}/{before_classes['twip_negative']} to {after_classes['twip_positive']}/{after_classes['twip_negative']}.
- Joint states change only by one verified `11`: before `00={before_classes['joint_00']}, 10={before_classes['joint_10']}, 01={before_classes['joint_01']}, 11={before_classes['joint_11']}`; after `00={after_classes['joint_00']}, 10={after_classes['joint_10']}, 01={after_classes['joint_01']}, 11={after_classes['joint_11']}`.

## W. Remaining P020 gaps

- Missing quantitative post-melt bulk chemistry, supplement-defined test temperature/rate/geometry/replicates, physical-batch identity, any P020 numeric SFE or DeltaG, and an explicitly reported HCP fracture fraction remain NA.

## X. Downstream refresh status

- V13/V12 Global QC, Feature Schema coverage statistics, feature coverage, and Grouped Split Design statistics do not include P020 and require a later non-destructive refresh. They are deliberately not refreshed while additional papers are being collected.
- No ML model was trained. No matrix, feature engineering, imputation, normalization, composition reconciliation, derived alloy descriptor, resampling, synthetic record, digitized curve, or performance metric was created.
""",
        encoding="utf-8",
    )


def integrate() -> tuple[pd.DataFrame, pd.DataFrame]:
    source, sheets = load_and_verify()
    out = source.copy()
    for column in NEW_COLUMNS:
        if column not in out:
            out[column] = pd.NA

    primary = make_primary_row(list(out.columns), sheets)
    stages = make_stage_rows(list(out.columns), sheets)
    new_rows = [primary] + stages
    provenance = build_provenance(new_rows, sheets)
    attach_provenance_json(new_rows, provenance)
    out = pd.concat(
        [out.astype(object), pd.DataFrame(new_rows, columns=out.columns).astype(object)],
        ignore_index=True,
    )
    validate(source, out, sheets, provenance, new_rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)

    condition = sheets["P020_Condition"].copy()
    hierarchy = condition[
        [
            "Paper_ID", "DOI", "Study_Series_ID", "Material_Parent_ID",
            "ML_Condition_ID", "Independent_Experimental_ML_sample",
            "Leakage_Group_Strict", "Leakage_Group_Material", "Physical_Batch_ID",
            "Replicate_n",
        ]
    ].copy()
    hierarchy["Replicate_ID"] = pd.NA
    hierarchy["Observation_Count"] = 6
    hierarchy["Counting_Status"] = "ONE_NEW_INDEPENDENT_CONDITION_SIX_NONINDEPENDENT_CHILDREN"
    hierarchy["New_Source_Status"] = "NEW_PRIMARY_EXPERIMENTAL_PAPER_BEYOND_P019"

    exports = {
        "study_identity": sheets["P020_Study_Identity"],
        "hierarchy": hierarchy,
        "processing": processing_table(sheets),
        "initial_microstructure": sheets["P020_Initial_Microstructure"],
        "mechanical_response": sheets["P020_Mechanical_Response"],
        "target_evidence": sheets["P020_Target_Evidence"],
        "phase_evolution": sheets["P020_Phase_Evolution"],
        "in_situ_stage_evidence": sheets["P020_Stage_Evidence"],
        "neutron_method_metadata": sheets["P020_InSitu_Method"],
        "provenance": provenance,
        "scientific_safeguards": scientific_safeguards(),
        "integration_decision_ledger": integration_ledger(sheets),
    }
    for name, frame in exports.items():
        frame.to_csv(TABLE / f"p020_recovery_v14_{name}.csv", index=False)
    write_audit(source, out)
    return source, out


if __name__ == "__main__":
    integrate()
