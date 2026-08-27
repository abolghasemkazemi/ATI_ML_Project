"""Integrate verified P002 evidence into recovery v13 (dataset recovery only).

The V12-QC input is immutable.  This module appends evidence-rich exact P002
conditions and correlated/supporting records, while retaining every V12-QC row
and every pre-existing column value.  It performs no global-QC refresh, feature
engineering, imputation, composition normalization, resampling, or modelling.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_19papers_recovery_v12_qc.csv"
BOOK = ROOT / "data/interim/manual_recovery/P002_scientific_evidence_recovery_VERIFIED.xlsx"
OUT = ROOT / "data/processed/master_19papers_recovery_v13.csv"
TABLE = ROOT / "reports/tables"
AUDIT = ROOT / "reports/P002_RECOVERY_V13_AUDIT.md"

PAPER_ID = "P002"
DOI = "10.1016/j.msea.2020.140441"
CORRIGENDUM_DOI = "10.1016/j.msea.2021.142419"
TITLE = (
    "A TWIP-TRIP quinary high-entropy alloy: Tuning phase stability and "
    "microstructure for enhanced mechanical properties"
)
SERIES = "P002_SERIES01"
MATERIAL = "P002_MAT_FE40MN10CO20CR20NI10"
SOURCE_SHA256 = "4dec9a87c0c3f0f38a4ff676681ae0bacf09d247e7136770baf2d1eb27928406"
BOOK_SHA256 = "ff5722ac5f8b3406405adfca36b40b72e542de27aff0e30e33a84528b3baa21c"

EXACT_IDS = {"P002_MC_A600_RT", "P002_MC_A700_RT", "P002_MC_A800_RT"}

NEW_COLUMNS = [
    "P002_Record_Role",
    "P002_Target_Status",
    "P002_Legacy_Mapping_Status",
    "P002_Mapped_Exact_ML_Condition_ID",
    "P002_Source_Identity_Status",
    "Corrigendum_DOI",
    "Corrigendum_Applied",
    "Corrected_TRIP_Comparison",
    "Measured_Bulk_Composition",
    "EDS_Qualitative_Homogeneity",
    "Hot_Roll_Input_Thickness_mm",
    "Hot_Roll_Output_Thickness_mm",
    "Cold_Roll_Input_Thickness_mm",
    "Cold_Roll_Output_Thickness_mm",
    "Homogenization_Atmosphere",
    "Post_Homogenization_Quench",
    "Loading_Mode",
    "Specimen_Thickness_Status",
    "Replicate_Scope",
    "Initial_Phase",
    "NonRecrystallized_fraction",
    "RZ_Grain_Size_um",
    "RZ_Grain_Size_Uncertainty_um",
    "NRZ_Subgrain_Size_um",
    "NRZ_Avg_Dimension_um",
    "PreTest_Twin_State",
    "PreTest_Twin_Origin",
    "PreTest_Twin_Width_nm",
    "Sigma3_Twin_Boundary_Fraction_Raw",
    "Initial_Dislocation_State",
    "Orientation_State",
    "Initial_Twin_Target_Guardrail",
    "Mechanical_Value_Status",
    "Mechanical_Predictor_Eligibility",
    "TRIP_Evidence_Type",
    "TWIP_Evidence_Type",
    "Negative_Evidence_Status",
    "Condition_Level_Target_Evidence",
    "Target_Evidence_Confidence",
    "Stage_Method",
    "Local_Strain_pct",
    "HCP_Martensite_Fraction_at_Stage",
    "DeltaG_Value_Status",
    "DeltaG_Data_Origin",
    "Physics_Temperature_K",
    "Support_Record_ID",
    "P002_Recovery_Provenance_JSON",
]

REQUIRED_SHEETS = {
    "P002_Study_Identity",
    "P002_Conditions",
    "P002_Initial_Microstructure",
    "P002_Mechanical_Response",
    "P002_HallPetch_Support",
    "P002_Stage_Evidence",
    "P002_Target_Evidence",
    "P002_Physics",
    "P002_Corrigendum",
    "P002_Integration_Decisions",
    "P002_Provenance",
}

LEGACY_PRIMARY_MAP = {
    "P002_C01": "P002_MC_A800_RT",
    "P002_C02": "P002_MC_A700_RT",
    "P002_C03": "P002_MC_A600_RT",
}

EXACT_SCIENTIFIC_FIELDS = [
    "Original_Composition",
    "Composition_basis",
    "Fe_at%",
    "Mn_at%",
    "Co_at%",
    "Cr_at%",
    "Ni_at%",
    "Measured_Bulk_Composition",
    "Composition_Status",
    "EDS_Qualitative_Homogeneity",
    "Processing_route",
    "Cast_method",
    "Raw_Material_Purity",
    "Hot_rolling_T_K",
    "Hot_rolling_reduction_pct",
    "Hot_Roll_Input_Thickness_mm",
    "Hot_Roll_Output_Thickness_mm",
    "Homogenization_T_K",
    "Homogenization_time_h",
    "Homogenization_Atmosphere",
    "Post_Homogenization_Quench",
    "Cold_rolling_reduction_pct",
    "Cold_Roll_Input_Thickness_mm",
    "Cold_Roll_Output_Thickness_mm",
    "Annealing_T_K",
    "Annealing_time_min",
    "Cooling_route",
    "Test_T_Raw",
    "Test_T_K",
    "Strain_rate_s-1",
    "Loading_Mode",
    "Gauge_length_mm",
    "Gauge_width_mm",
    "Specimen_thickness_mm",
    "Replicate_n",
    "Initial_Phase",
    "Initial_FCC_fraction",
    "Initial_HCP_fraction",
    "Initial_HCP_Status",
    "Recrystallized_fraction",
    "NonRecrystallized_fraction",
    "RZ_Grain_Size_um",
    "RZ_Grain_Size_Uncertainty_um",
    "NRZ_Subgrain_Size_um",
    "NRZ_Avg_Dimension_um",
    "PreTest_Twin_State",
    "PreTest_Twin_Origin",
    "PreTest_Twin_Width_nm",
    "Sigma3_Twin_Boundary_Fraction_Raw",
    "Initial_Dislocation_State",
    "Orientation_State",
    "YS_MPa",
    "UTS_MPa",
    "Elongation_pct",
    "Original_TRIP",
    "Original_TWIP",
    "Effective_TRIP",
    "Effective_TWIP",
    "Slip",
    "TRIP_Evidence_Type",
    "TWIP_Evidence_Type",
    "Negative_Evidence_Status",
    "SFE_mJ_m2",
    "SFE_method",
    "SFE_Value_Status",
    "DeltaG_FCC_HCP_J_mol",
    "DeltaG_method",
    "DeltaG_Value_Status",
    "Physics_Temperature_K",
]

MEANINGFUL_NA_FIELDS = {
    "Measured_Bulk_Composition",
    "Test_T_K",
    "Initial_FCC_fraction",
    "UTS_MPa",
    "Elongation_pct",
    "Effective_TRIP",
    "Effective_TWIP",
}

STAGE_SCIENTIFIC_FIELDS = [
    "Local_Strain_pct",
    "Stage_Method",
    "HCP_Martensite_Fraction_at_Stage",
    "TRIP_at_stage",
    "TWIP_at_stage",
    "Slip_at_stage",
    "Observed_Microstructure",
]

SUPPORT_SCIENTIFIC_FIELDS = ["Processing_route", "Grain_size_um", "Grain_size_SD_um", "YS_MPa"]

UNIT_MAP = {
    "Fe_at%": "at.%",
    "Mn_at%": "at.%",
    "Co_at%": "at.%",
    "Cr_at%": "at.%",
    "Ni_at%": "at.%",
    "Hot_rolling_T_K": "K",
    "Homogenization_T_K": "K",
    "Annealing_T_K": "K",
    "Test_T_K": "K",
    "Physics_Temperature_K": "K",
    "Hot_rolling_reduction_pct": "%",
    "Cold_rolling_reduction_pct": "%",
    "Annealing_time_min": "min",
    "Homogenization_time_h": "h",
    "Hot_Roll_Input_Thickness_mm": "mm",
    "Hot_Roll_Output_Thickness_mm": "mm",
    "Cold_Roll_Input_Thickness_mm": "mm",
    "Cold_Roll_Output_Thickness_mm": "mm",
    "Gauge_length_mm": "mm",
    "Gauge_width_mm": "mm",
    "Specimen_thickness_mm": "mm",
    "Strain_rate_s-1": "s^-1",
    "Initial_FCC_fraction": "fraction",
    "Initial_HCP_fraction": "fraction",
    "Recrystallized_fraction": "fraction",
    "NonRecrystallized_fraction": "fraction",
    "RZ_Grain_Size_um": "um",
    "RZ_Grain_Size_Uncertainty_um": "um",
    "NRZ_Subgrain_Size_um": "um",
    "NRZ_Avg_Dimension_um": "um",
    "PreTest_Twin_Width_nm": "nm",
    "YS_MPa": "MPa",
    "UTS_MPa": "MPa",
    "Elongation_pct": "%",
    "Original_TRIP": "binary",
    "Original_TWIP": "binary",
    "Effective_TRIP": "binary",
    "Effective_TWIP": "binary",
    "Slip": "binary",
    "Local_Strain_pct": "%",
    "HCP_Martensite_Fraction_at_Stage": "fraction",
    "TRIP_at_stage": "binary",
    "TWIP_at_stage": "binary",
    "Slip_at_stage": "binary",
    "SFE_mJ_m2": "mJ/m2",
    "DeltaG_FCC_HCP_J_mol": "J/mol",
    "Grain_size_um": "um",
    "Grain_size_SD_um": "um",
    "Replicate_n": "count",
}


def file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def is_present(value) -> bool:
    return pd.notna(value) and str(value).strip() not in {"", "NA", "N/A", "nan", "None"}


def c_to_k(value) -> float:
    """Deterministic unit representation; the reported Celsius value remains in tables."""
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
    """Apply all established replacement gates plus the exact P002 V13 gate."""
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
        out = out[~out.P008_Record_Role.eq("LEGACY_PRESERVED_EXCLUDED_FROM_INDEPENDENT_COUNT")]
    for paper, column in [
        ("P013", "P013_Record_Role"),
        ("P014", "P014_Record_Role"),
        ("P015", "P015_Record_Role"),
        ("P002", "P002_Record_Role"),
    ]:
        if column in data and data[column].eq("RECOVERED_EXACT_CONDITION").any():
            out = out[~(out.Paper_ID.eq(paper) & ~out[column].eq("RECOVERED_EXACT_CONDITION"))]
    return out.copy()


def counts(data: pd.DataFrame) -> tuple[int, int, int, int]:
    pool = experimental_pool(data)
    return (
        len(pool),
        int(pool.Effective_TRIP.notna().sum()),
        int(pool.Effective_TWIP.notna().sum()),
        int(pool[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum()),
    )


def load_and_verify() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    assert file_hash(SOURCE) == SOURCE_SHA256, "V12-QC source changed before P002 integration"
    assert file_hash(BOOK) == BOOK_SHA256, "verified P002 workbook changed"
    source = pd.read_csv(SOURCE, low_memory=False)
    sheets = pd.read_excel(BOOK, sheet_name=None, dtype=object)
    assert set(sheets) == REQUIRED_SHEETS
    for frame in sheets.values():
        if "Paper_ID" in frame:
            assert set(frame.Paper_ID.dropna()) == {PAPER_ID}
        if "DOI" in frame:
            assert set(frame.DOI.dropna()) == {DOI}
    identity = sheets["P002_Study_Identity"].iloc[0]
    assert identity.Paper_ID == PAPER_ID
    assert identity.DOI == DOI
    assert identity.Title == TITLE
    assert identity.Corrigendum_DOI == CORRIGENDUM_DOI
    assert identity.Source_Identity_Status == "VERIFIED_PDF_AND_EXTERNAL_DOI_MATCH"
    assert bool(identity.Corrigendum_Applied)
    corr = sheets["P002_Corrigendum"].iloc[0]
    assert corr.Original_DOI == DOI and corr.Corrigendum_DOI == CORRIGENDUM_DOI
    assert corr.Corrected_Text_Semantic == "800C condition has more pronounced TRIP than 700C condition"
    assert corr.Status == "APPLIED"
    return source, sheets


def verify_legacy_mapping(source: pd.DataFrame, conditions: pd.DataFrame) -> pd.DataFrame:
    legacy = source[source.Paper_ID.eq(PAPER_ID)].copy()
    assert len(legacy) == 5 and legacy.DOI.eq(DOI).all()
    primary = legacy[legacy.Condition_ID.isin(LEGACY_PRIMARY_MAP)]
    assert len(primary) == 3
    indexed = conditions.set_index("ML_Condition_ID")
    rows: list[dict] = []
    for legacy_id, exact_id in LEGACY_PRIMARY_MAP.items():
        old = primary.set_index("Condition_ID").loc[legacy_id]
        new = indexed.loc[exact_id]
        # Match by scientific identity, never by row position.
        assert old.Original_Composition == new.Nominal_Composition
        assert abs(float(old.Annealing_T_K) - c_to_k(new.Anneal_T_C)) <= 0.2
        assert float(old["Strain_rate_s-1"]) == float(new["Engineering_Strain_Rate_s-1"])
        mechanical = {
            "P002_MC_A800_RT": (375.0, 785.0, 77.5),
            "P002_MC_A700_RT": (589.0, 865.0, 69.1),
            "P002_MC_A600_RT": (1060.0, None, None),
        }[exact_id]
        assert float(old.YS_MPa) == mechanical[0]
        if mechanical[1] is not None:
            assert float(old.UTS_MPa) == mechanical[1]
            assert float(old.Elongation_pct) == mechanical[2]
        rows.append(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Legacy_Condition_ID": legacy_id,
                "Legacy_ML_Condition_ID": old.ML_Condition_ID,
                "Exact_ML_Condition_ID": exact_id,
                "Mapping_Status": "EXACT_IDENTITY_MATCH_LEGACY_RETAINED_EXCLUDED_FROM_INDEPENDENT_COUNT",
                "Match_Basis": (
                    "DOI; nominal composition; annealing temperature; room-temperature representation; "
                    "strain rate; mechanical values; historical targets (not row order)"
                ),
                "Original_TRIP": old.TRIP,
                "Original_TWIP": old.TWIP,
                "Verified_Effective_TRIP": 1 if exact_id != "P002_MC_A600_RT" else pd.NA,
                "Verified_Effective_TWIP": 1 if exact_id != "P002_MC_A600_RT" else pd.NA,
                "Conflict_Status": (
                    "LEGACY_ZERO_CONFLICTS_WITH_VERIFIED_INSUFFICIENT_NEGATIVE_EVIDENCE"
                    if exact_id == "P002_MC_A600_RT"
                    else "NO_TARGET_CONFLICT"
                ),
                "Counting_Rule": "COUNT_EXACT_REPLACEMENT_ONLY",
            }
        )
    rows.extend(
        [
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Legacy_Condition_ID": "P002_C04",
                "Legacy_ML_Condition_ID": "P002_MC04",
                "Exact_ML_Condition_ID": pd.NA,
                "Mapping_Status": "LEGACY_REFERENCE_COMPARATOR_RETAINED_SUPPORT_ONLY",
                "Match_Basis": "DOI; equiatomic reference-comparator identity",
                "Original_TRIP": pd.NA,
                "Original_TWIP": pd.NA,
                "Verified_Effective_TRIP": pd.NA,
                "Verified_Effective_TWIP": pd.NA,
                "Conflict_Status": "NOT_A_PRIMARY_P002_MATERIAL_CONDITION",
                "Counting_Rule": "NEVER_COUNT_AS_INDEPENDENT",
            },
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Legacy_Condition_ID": "P002_C05",
                "Legacy_ML_Condition_ID": "P002_MC05",
                "Exact_ML_Condition_ID": pd.NA,
                "Mapping_Status": "LEGACY_CALPHAD_DESCRIPTOR_RETAINED_SUPPORT_ONLY",
                "Match_Basis": "DOI; nominal composition; Thermo-Calc TCFE7; DeltaG=-292 J/mol",
                "Original_TRIP": pd.NA,
                "Original_TWIP": pd.NA,
                "Verified_Effective_TRIP": pd.NA,
                "Verified_Effective_TWIP": pd.NA,
                "Conflict_Status": "COMPUTATIONAL_SUPPORT_NOT_EXPERIMENTAL_TARGET_ROW",
                "Counting_Rule": "NEVER_COUNT_AS_INDEPENDENT_EXPERIMENTAL",
            },
        ]
    )
    return pd.DataFrame(rows)


def physics_table(frame: pd.DataFrame) -> pd.DataFrame:
    lattice = {
        "Paper_ID": PAPER_ID,
        "DOI": DOI,
        "Material_Parent_ID": MATERIAL,
        "Temperature_K": 300,
        "Feature": "Lattice_constant_a",
        "Value": 0.3587,
        "Units": "nm",
        "Method": "Current-paper value used to derive planar packing density",
        "Status": "CURRENT_PAPER_DERIVED_MODEL_INPUT",
        "Condition_Scope": "MODEL_INPUT",
        "Current_Paper_or_Secondary": "CURRENT_PAPER",
        "Predictor_Timing": "MODEL_DERIVED_METADATA",
        "Evidence_Location": "Sec.4.2 p.8; Eq.2",
        "Confidence": "High",
        "Notes": "Preserved with the 2.98e-5 mol/m2 planar-density derivation; not an independent measurement.",
        "Source_URL": f"https://doi.org/{DOI}",
    }
    return pd.concat([frame.copy(), pd.DataFrame([lattice])], ignore_index=True)


def build_processing_table(conditions: pd.DataFrame) -> pd.DataFrame:
    out = conditions.copy()
    out.insert(out.columns.get_loc("Hot_Roll_Reduction_pct") + 1, "Hot_Roll_Input_Thickness_mm", 10.0)
    out.insert(out.columns.get_loc("Hot_Roll_Input_Thickness_mm") + 1, "Hot_Roll_Output_Thickness_mm", 5.0)
    out.insert(out.columns.get_loc("Cold_Roll_Reduction_pct") + 1, "Cold_Roll_Input_Thickness_mm", 5.0)
    out.insert(out.columns.get_loc("Cold_Roll_Input_Thickness_mm") + 1, "Cold_Roll_Output_Thickness_mm", 1.5)
    out["Specimen_Thickness_Status"] = "APPROX_DIRECT_TEXT"
    return out


def base_provenance(frame: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    for rec in frame.to_dict("records"):
        record = rec["Record_ID"]
        recovered = "UNRESOLVED_NA" if pd.isna(rec["Recovered_Value"]) else rec["Recovered_Value"]
        rows.append(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Corrigendum_DOI": CORRIGENDUM_DOI,
                "Material_Parent_ID": MATERIAL,
                "ML_Condition_ID": record if str(record).startswith("P002_MC_") else pd.NA,
                "Record_ID": record,
                "Feature_Name": rec["Feature_Name"],
                "Recovered_Value": recovered,
                "Units": rec["Units"],
                "Evidence_Type": rec["Evidence_Type"],
                "Evidence_Location": rec["Evidence_Location"],
                "Method": rec["Method"],
                "Confidence": rec["Confidence"],
                "Recovery_Status": rec["Recovery_Status"],
                "Source_URL": rec["Source_URL"],
            }
        )
    return rows


def add_master_provenance(
    rows: list[dict],
    record: dict,
    record_id: str,
    scientific_fields: list[str],
    evidence_type: str,
    evidence_location: str,
    method: str,
    confidence: str,
) -> None:
    for feature in scientific_fields:
        value = record.get(feature, pd.NA)
        if not is_present(value) and feature not in MEANINGFUL_NA_FIELDS:
            continue
        status = "VERIFIED_NA" if not is_present(value) else "VERIFIED"
        rows.append(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Corrigendum_DOI": CORRIGENDUM_DOI,
                "Material_Parent_ID": MATERIAL,
                "ML_Condition_ID": record.get("ML_Condition_ID", pd.NA),
                "Record_ID": record_id,
                "Feature_Name": feature,
                "Recovered_Value": "UNRESOLVED_NA" if status == "VERIFIED_NA" else value,
                "Units": UNIT_MAP.get(feature, "as reported"),
                "Evidence_Type": evidence_type,
                "Evidence_Location": evidence_location,
                "Method": method,
                "Confidence": confidence,
                "Recovery_Status": status,
                "Source_URL": f"https://doi.org/{DOI}",
            }
        )


def make_exact_rows(
    out_columns: list[str],
    sheets: dict[str, pd.DataFrame],
    mapping: pd.DataFrame,
) -> list[dict]:
    conditions = sheets["P002_Conditions"].set_index("ML_Condition_ID")
    micro = sheets["P002_Initial_Microstructure"].set_index("ML_Condition_ID")
    mechanics = sheets["P002_Mechanical_Response"].set_index("ML_Condition_ID")
    targets = sheets["P002_Target_Evidence"].set_index("ML_Condition_ID")
    original = mapping.dropna(subset=["Exact_ML_Condition_ID"]).set_index("Exact_ML_Condition_ID")
    rows: list[dict] = []
    for mc in ["P002_MC_A600_RT", "P002_MC_A700_RT", "P002_MC_A800_RT"]:
        c = conditions.loc[mc]
        m = micro.loc[mc]
        mech = mechanics.loc[mc]
        target = targets.loc[mc]
        old = original.loc[mc]
        label = c.Condition_Label
        state = mc.split("_")[2]
        route = (
            "Vacuum induction melting/casting from >99.8 wt% raw metals; hot rolled at 900 C "
            "from 10 to 5 mm (50%); homogenized at 1200 C for 2 h in Ar; water quenched; "
            "cold rolled from 5 to 1.5 mm (70%); "
            f"annealed at {int(c.Anneal_T_C)} C for 30 min; water quenched"
        )
        row = {column: pd.NA for column in out_columns}
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Condition_ID": mc,
                "Experiment_Group_ID": SERIES,
                "Original_Experiment_Group_ID": "P002_G01",
                "Row_Type": "Processing/tensile condition",
                "Alloy_ID": "Fe40Mn10Co20Cr20Ni10",
                "Original_Composition": c.Nominal_Composition,
                "Nominal_Composition_at_pct": c.Nominal_Composition,
                "Composition_basis": "at.% nominal",
                "Fe_at%": 40,
                "Mn_at%": 10,
                "Co_at%": 20,
                "Cr_at%": 20,
                "Ni_at%": 10,
                "Measured_Bulk_Composition": pd.NA,
                "Measured_Composition_at_pct": pd.NA,
                "Recovered_Bulk_Composition_at_pct": pd.NA,
                "Composition_Status": c.Composition_Status,
                "Measured_Composition_Status": c.Composition_Status,
                "Recovered_Composition_Status": c.Composition_Status,
                "EDS_Qualitative_Homogeneity": m.EDS_Homogeneity,
                "Processing_route": route,
                "Recovered_Processing_route": route,
                "Cast_method": "Vacuum induction melting / casting",
                "Raw_Material_Purity": c.Raw_Material_Purity,
                "Hot_rolling_T_K": c_to_k(c.Hot_Roll_T_C),
                "Hot_rolling_reduction_pct": c.Hot_Roll_Reduction_pct,
                "Hot_Roll_Input_Thickness_mm": 10.0,
                "Hot_Roll_Output_Thickness_mm": 5.0,
                "Homogenization_T_K": c_to_k(c.Homogenization_T_C),
                "Homogenization_time_h": c.Homogenization_Time_h,
                "Homogenization_Atmosphere": c.Homogenization_Atmosphere,
                "Post_Homogenization_Quench": c.Post_Homogenization_Quench,
                "Cold_rolling_reduction_pct": c.Cold_Roll_Reduction_pct,
                "Cold_Roll_Input_Thickness_mm": 5.0,
                "Cold_Roll_Output_Thickness_mm": 1.5,
                "Annealing_T_K": c_to_k(c.Anneal_T_C),
                "Annealing_time_min": c.Anneal_Time_min,
                "Cooling_route": c.Post_Anneal_Quench,
                "Test_T_Raw": c.Test_T_Raw,
                "Test_T_K": pd.NA,
                "Test_T_Status": "DIRECT_TEXT_ROOM_TEMPERATURE_EXACT_K_NOT_REPORTED",
                "Recovered_Test_T_Reported": c.Test_T_Raw,
                "Recovered_Test_T_Status": "DIRECT_TEXT_ROOM_TEMPERATURE_EXACT_K_NOT_REPORTED",
                "Strain_rate_s-1": c["Engineering_Strain_Rate_s-1"],
                "Loading_Mode": c.Loading_Mode,
                "Gauge_length_mm": c.Gauge_Length_mm,
                "Gauge_width_mm": c.Gauge_Width_mm,
                "Specimen_thickness_mm": c.Specimen_Thickness_mm,
                "Specimen_Thickness_Status": "APPROX_DIRECT_TEXT",
                "Replicate_n": c.Replicate_n,
                "Replicate_ID": pd.NA,
                "Physical_Batch_ID": pd.NA,
                "Replicate_Scope": "THREE_TENSILE_SPECIMENS_PER_ANNEALING_TEMPERATURE_NO_INDIVIDUAL_ROWS",
                "Aggregate_Property_Status": "AGGREGATE_REPRESENTATIVE_RESPONSE_NO_PSEUDO_REPLICATES",
                "Initial_Phase": m.Initial_Phase,
                "Initial_Phase_State_Qualitative": m.Initial_Phase,
                "Initial_Phase_Status": m.Initial_HCP_Status,
                "Initial_FCC_fraction": pd.NA,
                "Recovered_Initial_FCC_fraction": pd.NA,
                "Initial_HCP_fraction": m.Initial_HCP_fraction,
                "Recovered_Initial_HCP_fraction": m.Initial_HCP_fraction,
                "Initial_HCP_Status": m.Initial_HCP_Status,
                "Recovered_Initial_HCP_status": m.Initial_HCP_Status,
                "Recrystallized_fraction": m.Recrystallized_Fraction,
                "Recovered_Recrystallized_fraction": m.Recrystallized_Fraction,
                "Recrystallized_Status": "DIRECT_TEXT_APPROXIMATE" if mc != "P002_MC_A800_RT" else "DIRECT_TEXT_FULLY_RECRYSTALLIZED",
                "Recovered_Recrystallized_fraction_status": "DIRECT_TEXT_APPROXIMATE" if mc != "P002_MC_A800_RT" else "DIRECT_TEXT_FULLY_RECRYSTALLIZED",
                "NonRecrystallized_fraction": m.NonRecrystallized_Fraction,
                "RZ_Grain_Size_um": m.RZ_Grain_Size_um,
                "RZ_Grain_Size_Uncertainty_um": m.RZ_Grain_Size_Uncertainty_um,
                "NRZ_Subgrain_Size_um": m.NRZ_Subgrain_Size_um,
                "NRZ_Avg_Dimension_um": m.NRZ_Avg_Dimension_um,
                "Grain_size_um": m.RZ_Grain_Size_um if mc == "P002_MC_A800_RT" else pd.NA,
                "Grain_size_SD_um": m.RZ_Grain_Size_Uncertainty_um if mc == "P002_MC_A800_RT" else pd.NA,
                "Recovered_Grain_size_um": m.RZ_Grain_Size_um if mc == "P002_MC_A800_RT" else pd.NA,
                "Recovered_Grain_size_scope": "FULLY_RECRYSTALLIZED_AVERAGE" if mc == "P002_MC_A800_RT" else "RZ_SPECIFIC_SEPARATE_FIELD",
                "Recovered_Grain_size_status": "DIRECT_TEXT_WITH_SD" if mc == "P002_MC_A800_RT" else "GENERAL_GRAIN_SIZE_NOT_POPULATED_FROM_RZ_ONLY_VALUE",
                "Initial_twin_boundary_status": m.PreTest_Twin_State,
                "PreTest_Twin_State": m.PreTest_Twin_State,
                "PreTest_Twin_Origin": m.PreTest_Twin_Origin,
                "Initial_Twin_Origin": m.PreTest_Twin_Origin,
                "PreTest_Twin_Width_nm": m.Twin_Width_nm,
                "Sigma3_Twin_Boundary_Fraction_Raw": m.Sigma3_Twin_Boundary_Fraction_Raw,
                "Initial_Dislocation_State": m.Initial_Dislocation_State,
                "Orientation_State": m.Orientation_State,
                "Texture_Orientation_Status": m.Orientation_State,
                "Initial_Twin_Target_Safety": "PRETEST_TWINS_DO_NOT_ESTABLISH_TENSILE_TWIP",
                "Initial_Twin_Target_Guardrail": m.Scientific_Guardrail,
                "Engineering_YS_MPa": mech.Engineering_YS_MPa,
                "Engineering_UTS_MPa": mech.Engineering_UTS_MPa,
                "Engineering_Elongation_pct": mech.Total_Elongation_pct,
                "YS_MPa": mech.Engineering_YS_MPa,
                "UTS_MPa": mech.Engineering_UTS_MPa,
                "Elongation_pct": mech.Total_Elongation_pct,
                "YS_mean": mech.Engineering_YS_MPa,
                "UTS_mean": mech.Engineering_UTS_MPa,
                "TE_mean": mech.Total_Elongation_pct,
                "Mechanical_Value_Status": mech.Value_Status,
                "Mechanical_Predictor_Eligibility": mech.Predictor_Eligibility,
                "TRIP": pd.NA,
                "TWIP": pd.NA,
                "Original_TRIP": old.Original_TRIP,
                "Original_TWIP": old.Original_TWIP,
                "Recovered_TRIP": target.Effective_TRIP,
                "Recovered_TWIP": target.Effective_TWIP,
                "Effective_TRIP": target.Effective_TRIP,
                "Effective_TWIP": target.Effective_TWIP,
                "Slip": target.Slip,
                "P002_Target_Status": target.Target_Status,
                "Target_Review_Status": target.Target_Status,
                "TRIP_Evidence_Type": target.TRIP_Evidence_Type,
                "TWIP_Evidence_Type": target.TWIP_Evidence_Type,
                "Negative_Evidence_Status": target.Negative_Evidence_Status,
                "Condition_Level_Target_Evidence": target.Condition_Level_Evidence,
                "Target_Evidence_Confidence": target.Confidence,
                "Evidence_TRIP": target.TRIP_Evidence_Type,
                "Evidence_TWIP": target.TWIP_Evidence_Type,
                "SFE_mJ_m2": 14,
                "SFE_method": "Thermodynamic estimate using DeltaG, strain energy, FCC/HCP interface energy and planar packing density",
                "SFE_Value_Status": "CURRENT_PAPER_THERMODYNAMIC_ESTIMATE",
                "SFE_Data_Origin": "THERMODYNAMIC_ESTIMATE_NOT_EXPERIMENTAL",
                "SFE_scope": "ALLOY_LEVEL_TEMPERATURE_SPECIFIC_300K",
                "SFE_status": "CURRENT_PAPER_THERMODYNAMIC_ESTIMATE_NOT_EXPERIMENTAL",
                "SFE_source_provenance": "P002 Sec.4.2 Eq.2; current-paper thermodynamic estimate at 300 K",
                "DeltaG_FCC_HCP_J_mol": -292,
                "Recovered_DeltaG_FCC_HCP_300K_J_mol": -292,
                "DeltaG_method": "Thermo-Calc TCFE7",
                "DeltaG_Value_Status": "CURRENT_PAPER_CALCULATED",
                "DeltaG_Data_Origin": "CALPHAD",
                "Physics_Temperature_K": 300,
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": MATERIAL,
                "Processing_State_ID": f"P002_PS_{state}",
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": MATERIAL,
                "Parent_Experiment_ID": mc,
                "Parent_ML_Condition_ID": mc,
                "ML_Condition_ID": mc,
                "Observation_ID": f"P002_OBS_{state}_RT",
                "Data_Origin": "EXPERIMENTAL",
                "Observation_Role": "INDEPENDENT_CONDITION",
                "Row_Role": "EXPERIMENTAL_INDEPENDENT",
                "Independent_ML_sample": True,
                "Independent_Experimental_ML_sample": True,
                "Grouping_Confidence": "HIGH",
                "Grouping_Review_Required": 0,
                "Grouping_Reason": "Three processing-defined conditions share one P002 study series and material parent.",
                "P002_Record_Role": "RECOVERED_EXACT_CONDITION",
                "P002_Source_Identity_Status": "VERIFIED_PDF_AND_EXTERNAL_DOI_MATCH",
                "Corrigendum_DOI": CORRIGENDUM_DOI,
                "Corrigendum_Applied": True,
                "Corrected_TRIP_Comparison": "A800_TRIP_MORE_PRONOUNCED_THAN_A700",
                "Source_File": BOOK.name,
                "Source_Sheet": "P002_Conditions; P002_Initial_Microstructure; P002_Mechanical_Response; P002_Target_Evidence; P002_Physics",
                "Source_location": "; ".join(
                    [str(c.Evidence_Location), str(m.Evidence_Location), str(mech.Evidence_Location), "Sec.4.2 p.8"]
                ),
                "Label_confidence": target.Confidence,
                "Notes": f"{label}. {target.Scientific_Justification}",
            }
        )
        rows.append(row)
    return rows


def make_stage_rows(out_columns: list[str], stages: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    for stage in stages.to_dict("records"):
        row = {column: pd.NA for column in out_columns}
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Condition_ID": stage["Observation_ID"],
                "Row_Type": "Correlated deformation-stage evidence",
                "Alloy_ID": "Fe40Mn10Co20Cr20Ni10",
                "Original_Composition": "Fe40Mn10Co20Cr20Ni10",
                "Composition_basis": "at.% nominal",
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": MATERIAL,
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": MATERIAL,
                "Parent_Experiment_ID": stage["Parent_ML_Condition_ID"],
                "Parent_ML_Condition_ID": stage["Parent_ML_Condition_ID"],
                "ML_Condition_ID": pd.NA,
                "Observation_ID": stage["Observation_ID"],
                "Deformation_Stage_ID": stage["Observation_ID"],
                "Data_Origin": "EXPERIMENTAL",
                "Observation_Role": stage["Observation_Role"],
                "Independent_ML_sample": False,
                "Independent_Experimental_ML_sample": False,
                "Local_Strain_pct": stage["Local_Strain_pct"],
                "Tensile_Strain_pct": stage["Local_Strain_pct"],
                "Stage_Method": stage["Method"],
                "Characterization_methods": stage["Method"],
                "HCP_Martensite_Fraction_at_Stage": stage["HCP_Martensite_Fraction"],
                "TRIP_at_stage": stage["TRIP_Stage"],
                "TWIP_at_stage": stage["TWIP_Stage"],
                "Slip_at_stage": stage["Slip_Stage"],
                "Observed_Microstructure": stage["Notes"],
                "P002_Record_Role": "RECOVERED_CORRELATED_STAGE_OR_POST_TEST_EVIDENCE",
                "P002_Source_Identity_Status": "VERIFIED_PDF_AND_EXTERNAL_DOI_MATCH",
                "Corrigendum_DOI": CORRIGENDUM_DOI,
                "Corrigendum_Applied": True,
                "Corrected_TRIP_Comparison": "A800_TRIP_MORE_PRONOUNCED_THAN_A700",
                "Source_File": BOOK.name,
                "Source_Sheet": "P002_Stage_Evidence",
                "Source_location": stage["Evidence_Location"],
                "Label_confidence": stage["Confidence"],
                "Notes": stage["Notes"],
            }
        )
        rows.append(row)
    return rows


def make_support_rows(out_columns: list[str], support: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    # A800 is the same material condition as the exact primary row and therefore
    # remains in the support table only; it is not appended as a duplicate row.
    for rec in support[~support.Support_Record_ID.eq("P002_HP_A800")].to_dict("records"):
        row = {column: pd.NA for column in out_columns}
        row.update(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Paper_Title": TITLE,
                "Condition_ID": rec["Support_Record_ID"],
                "Support_Record_ID": rec["Support_Record_ID"],
                "Row_Type": "Hall-Petch supporting state",
                "Alloy_ID": "Fe40Mn10Co20Cr20Ni10",
                "Original_Composition": "Fe40Mn10Co20Cr20Ni10",
                "Composition_basis": "at.% nominal",
                "Processing_route": rec["Processing_State"],
                "Grain_size_um": rec["Grain_Size_um"],
                "Grain_size_SD_um": rec["Grain_Size_Uncertainty_um"],
                "YS_MPa": rec["YS_MPa"],
                "Mechanical_Predictor_Eligibility": "MECHANICAL_OUTCOME_LEAKAGE",
                "Study_Series_ID": SERIES,
                "Material_Parent_ID": MATERIAL,
                "Leakage_Group_Strict": SERIES,
                "Leakage_Group_Material": MATERIAL,
                "ML_Condition_ID": pd.NA,
                "Observation_ID": rec["Support_Record_ID"],
                "Data_Origin": "EXPERIMENTAL",
                "Observation_Role": "SUPPORT",
                "Independent_ML_sample": False,
                "Independent_Experimental_ML_sample": False,
                "P002_Record_Role": "HALL_PETCH_SUPPORT_ONLY",
                "P002_Source_Identity_Status": "VERIFIED_PDF_AND_EXTERNAL_DOI_MATCH",
                "Source_File": BOOK.name,
                "Source_Sheet": "P002_HallPetch_Support",
                "Source_location": rec["Evidence_Location"],
                "Label_confidence": rec["Confidence"],
                "Notes": rec["Notes"],
            }
        )
        rows.append(row)
    return rows


def decision_correction_ledger(
    decisions: pd.DataFrame, corrigendum: pd.DataFrame
) -> pd.DataFrame:
    rows: list[dict] = []
    for rec in decisions.to_dict("records"):
        rows.append(
            {
                "Ledger_ID": rec["Decision_ID"],
                "Ledger_Type": "INTEGRATION_DECISION",
                "Scope": PAPER_ID,
                "Legacy_Value": pd.NA,
                "Verified_Value": rec["Decision"],
                "Action": rec["Implementation_Rule"],
                "Scientific_Rationale": rec["Scientific_Rationale"],
                "Evidence_Location": rec["Evidence_Location"],
                "DOI": DOI,
                "Corrigendum_DOI": CORRIGENDUM_DOI if rec["Decision_ID"] == "D005" else pd.NA,
                "Status": rec["Status"],
            }
        )
    rows.extend(
        [
            {
                "Ledger_ID": "C001",
                "Ledger_Type": "LEGACY_TARGET_CORRECTION",
                "Scope": "P002_C03 -> P002_MC_A600_RT / Effective_TRIP",
                "Legacy_Value": 0,
                "Verified_Value": "UNRESOLVED_NA",
                "Action": "Retain legacy 0 unchanged; preserve as Original_TRIP; exact Effective_TRIP remains NA",
                "Scientific_Rationale": "Hindered/suppressed plus missing direct post-test characterization is insufficient for a verified zero.",
                "Evidence_Location": "Sec.4.2 p.8; verified source review",
                "DOI": DOI,
                "Corrigendum_DOI": pd.NA,
                "Status": "APPLIED_NON_DESTRUCTIVELY",
            },
            {
                "Ledger_ID": "C002",
                "Ledger_Type": "LEGACY_TARGET_CORRECTION",
                "Scope": "P002_C03 -> P002_MC_A600_RT / Effective_TWIP",
                "Legacy_Value": 0,
                "Verified_Value": "UNRESOLVED_NA",
                "Action": "Retain legacy 0 unchanged; preserve as Original_TWIP; exact Effective_TWIP remains NA",
                "Scientific_Rationale": "Pre-test twins and hindered activation do not establish condition-wide post-test TWIP absence.",
                "Evidence_Location": "Sec.3.1; Sec.4.2 p.8; verified source review",
                "DOI": DOI,
                "Corrigendum_DOI": pd.NA,
                "Status": "APPLIED_NON_DESTRUCTIVELY",
            },
            {
                "Ledger_ID": "C003",
                "Ledger_Type": "LEGACY_NUMERIC_SCOPE_CORRECTION",
                "Scope": "P002_C01/P002_C02/P002_C03 -> exact replacement Test_T_K",
                "Legacy_Value": "298 K",
                "Verified_Value": "Test_T_Raw=room temperature; Test_T_K=NA",
                "Action": "Retain legacy values unchanged; do not propagate inferred 298 K to exact rows",
                "Scientific_Rationale": "The source text reports room temperature without an exact numeric Kelvin value.",
                "Evidence_Location": "Sec.2.3",
                "DOI": DOI,
                "Corrigendum_DOI": pd.NA,
                "Status": "APPLIED_NON_DESTRUCTIVELY",
            },
            {
                "Ledger_ID": "C004",
                "Ledger_Type": "LEGACY_NUMERIC_SCOPE_CORRECTION",
                "Scope": "P002_C01/P002_C02/P002_C03 -> exact replacement Initial_FCC_fraction",
                "Legacy_Value": 1,
                "Verified_Value": "NA with qualitative Single FCC",
                "Action": "Retain legacy values unchanged; exact numeric FCC fraction is not propagated",
                "Scientific_Rationale": "Single-FCC EBSD establishes phase identity and HCP absence, but not an exact numeric FCC fraction.",
                "Evidence_Location": "Sec.3.1; Figs.1-5",
                "DOI": DOI,
                "Corrigendum_DOI": pd.NA,
                "Status": "APPLIED_NON_DESTRUCTIVELY",
            },
        ]
    )
    corr = corrigendum.iloc[0]
    rows.append(
        {
            "Ledger_ID": "C005",
            "Ledger_Type": "OFFICIAL_CORRIGENDUM",
            "Scope": corr.Affected_Section,
            "Legacy_Value": corr.Original_Text_Semantic,
            "Verified_Value": corr.Corrected_Text_Semantic,
            "Action": corr.Recovery_Action,
            "Scientific_Rationale": corr.Scientific_Impact,
            "Evidence_Location": corr.Evidence_Location,
            "DOI": DOI,
            "Corrigendum_DOI": CORRIGENDUM_DOI,
            "Status": corr.Status,
        }
    )
    return pd.DataFrame(rows)


def add_legacy_metadata(out: pd.DataFrame, mapping: pd.DataFrame) -> None:
    indexed = mapping.set_index("Legacy_Condition_ID")
    for legacy_id, rec in indexed.iterrows():
        mask = out.Condition_ID.eq(legacy_id)
        assert int(mask.sum()) == 1
        out.loc[mask, "P002_Legacy_Mapping_Status"] = rec.Mapping_Status
        out.loc[mask, "P002_Mapped_Exact_ML_Condition_ID"] = rec.Exact_ML_Condition_ID
        if legacy_id in LEGACY_PRIMARY_MAP:
            role = "LEGACY_EXACT_REPRESENTATION_RETAINED_EXCLUDED_FROM_INDEPENDENT_COUNT"
        elif legacy_id == "P002_C04":
            role = "LEGACY_REFERENCE_COMPARATOR_RETAINED"
        else:
            role = "LEGACY_CALPHAD_DESCRIPTOR_RETAINED"
        out.loc[mask, "P002_Record_Role"] = role


def attach_provenance(
    all_rows: list[dict],
    exact_rows: list[dict],
    stage_rows: list[dict],
    support_rows: list[dict],
    sheets: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    provenance = base_provenance(sheets["P002_Provenance"])
    for row in exact_rows:
        add_master_provenance(
            provenance,
            row,
            str(row["ML_Condition_ID"]),
            EXACT_SCIENTIFIC_FIELDS,
            "MASTER_FIELD_MAPPING_FROM_VERIFIED_P002_EVIDENCE",
            str(row["Source_location"]),
            "Source-reported; Celsius-to-K fields use explicit C + 273.15 unit representation",
            str(row["Target_Evidence_Confidence"]),
        )
    stage_lookup = sheets["P002_Stage_Evidence"].set_index("Observation_ID")
    for row in stage_rows:
        source = stage_lookup.loc[row["Observation_ID"]]
        add_master_provenance(
            provenance,
            row,
            str(row["Observation_ID"]),
            STAGE_SCIENTIFIC_FIELDS,
            "CORRELATED_STAGE_OR_POST_TEST_EVIDENCE",
            str(source.Evidence_Location),
            str(source.Method),
            str(source.Confidence),
        )
    support_lookup = sheets["P002_HallPetch_Support"].set_index("Support_Record_ID")
    for row in support_rows:
        source = support_lookup.loc[row["Support_Record_ID"]]
        add_master_provenance(
            provenance,
            row,
            str(row["Support_Record_ID"]),
            SUPPORT_SCIENTIFIC_FIELDS,
            "HALL_PETCH_SUPPORT_DIRECT_TABLE",
            str(source.Evidence_Location),
            "Source-reported Hall-Petch input state",
            str(source.Confidence),
        )
    # Explicit task-specified source values that are not standalone workbook rows.
    for feature, value, units, location, method in [
        ("Hot_Roll_Input_Thickness_mm", 10.0, "mm", "Sec.2.1 p.2", "direct processing dimension"),
        ("Hot_Roll_Output_Thickness_mm", 5.0, "mm", "Sec.2.1 p.2", "direct processing dimension"),
        ("Cold_Roll_Input_Thickness_mm", 5.0, "mm", "Sec.2.1 p.2", "direct processing dimension"),
        ("Cold_Roll_Output_Thickness_mm", 1.5, "mm", "Sec.2.1 p.2", "direct processing dimension"),
        ("Lattice_constant_a", 0.3587, "nm", "Sec.4.2 p.8; Eq.2", "current-paper model derivation input"),
    ]:
        provenance.append(
            {
                "Paper_ID": PAPER_ID,
                "DOI": DOI,
                "Corrigendum_DOI": CORRIGENDUM_DOI,
                "Material_Parent_ID": MATERIAL,
                "ML_Condition_ID": pd.NA,
                "Record_ID": MATERIAL,
                "Feature_Name": feature,
                "Recovered_Value": value,
                "Units": units,
                "Evidence_Type": "DIRECT_TEXT_OR_CURRENT_PAPER_DERIVATION_INPUT",
                "Evidence_Location": location,
                "Method": method,
                "Confidence": "High",
                "Recovery_Status": "VERIFIED",
                "Source_URL": f"https://doi.org/{DOI}",
            }
        )
    corr = sheets["P002_Corrigendum"].iloc[0]
    provenance.append(
        {
            "Paper_ID": PAPER_ID,
            "DOI": DOI,
            "Corrigendum_DOI": CORRIGENDUM_DOI,
            "Material_Parent_ID": MATERIAL,
            "ML_Condition_ID": pd.NA,
            "Record_ID": "P002_CORRIGENDUM",
            "Feature_Name": "Corrected_TRIP_Comparison",
            "Recovered_Value": "A800_TRIP_MORE_PRONOUNCED_THAN_A700",
            "Units": "semantic comparison",
            "Evidence_Type": "OFFICIAL_CORRIGENDUM",
            "Evidence_Location": corr.Evidence_Location,
            "Method": "official published correction",
            "Confidence": "High",
            "Recovery_Status": "VERIFIED_CORRIGENDUM_APPLIED",
            "Source_URL": corr.Corrigendum_URL,
        }
    )
    frame = pd.DataFrame(provenance).drop_duplicates(ignore_index=True)
    required = [
        "Paper_ID",
        "DOI",
        "Material_Parent_ID",
        "Feature_Name",
        "Recovered_Value",
        "Units",
        "Evidence_Type",
        "Evidence_Location",
        "Method",
        "Confidence",
        "Recovery_Status",
    ]
    assert frame[required].notna().all().all()
    for row in all_rows:
        record_id = (
            row.get("ML_Condition_ID")
            if is_present(row.get("ML_Condition_ID"))
            else row.get("Observation_ID", row.get("Support_Record_ID"))
        )
        selected = frame[frame.Record_ID.eq(record_id)]
        if row.get("P002_Record_Role") == "RECOVERED_EXACT_CONDITION":
            selected = pd.concat(
                [selected, frame[frame.Record_ID.eq(MATERIAL)]], ignore_index=True
            ).drop_duplicates()
        row["P002_Recovery_Provenance_JSON"] = json.dumps(
            json_ready(selected.to_dict("records")), ensure_ascii=False, allow_nan=False
        )
    return frame


def validate(
    source: pd.DataFrame,
    out: pd.DataFrame,
    sheets: dict[str, pd.DataFrame],
    mapping: pd.DataFrame,
    provenance: pd.DataFrame,
) -> None:
    pd.testing.assert_frame_equal(
        out.iloc[: len(source)][source.columns].reset_index(drop=True),
        source.reset_index(drop=True),
        check_dtype=False,
    )
    assert source[source.Paper_ID.eq(PAPER_ID)].shape[0] == 5
    exact = out[out.P002_Record_Role.eq("RECOVERED_EXACT_CONDITION")]
    stages = out[out.P002_Record_Role.eq("RECOVERED_CORRELATED_STAGE_OR_POST_TEST_EVIDENCE")]
    support = out[out.P002_Record_Role.eq("HALL_PETCH_SUPPORT_ONLY")]
    assert len(out) == len(source) + 3 + 10 + 2 == 207
    assert set(exact.ML_Condition_ID) == EXACT_IDS and len(exact) == 3
    assert exact.Independent_ML_sample.eq(True).all()
    assert exact.Independent_Experimental_ML_sample.eq(True).all()
    assert exact.Replicate_n.eq(3).all() and exact.Replicate_ID.isna().all()
    assert exact.Physical_Batch_ID.isna().all()
    assert len(stages) == 10 and stages.Independent_ML_sample.eq(False).all()
    assert stages.Independent_Experimental_ML_sample.eq(False).all()
    assert len(support) == 2 and support.Independent_ML_sample.eq(False).all()
    assert not out.Support_Record_ID.eq("P002_HP_A800").any()
    assert exact.Measured_Bulk_Composition.isna().all()
    assert exact.Measured_Composition_at_pct.isna().all()
    assert exact.Initial_FCC_fraction.isna().all()
    assert exact.Initial_HCP_fraction.eq(0).all()
    assert exact.Initial_Phase.eq("Single FCC").all()
    assert exact.Test_T_Raw.eq("room temperature").all() and exact.Test_T_K.isna().all()
    assert exact.Initial_Twin_Target_Safety.eq("PRETEST_TWINS_DO_NOT_ESTABLISH_TENSILE_TWIP").all()
    indexed = exact.set_index("ML_Condition_ID")
    assert indexed.loc["P002_MC_A700_RT", "Effective_TRIP"] == 1
    assert indexed.loc["P002_MC_A700_RT", "Effective_TWIP"] == 1
    assert indexed.loc["P002_MC_A800_RT", "Effective_TRIP"] == 1
    assert indexed.loc["P002_MC_A800_RT", "Effective_TWIP"] == 1
    assert pd.isna(indexed.loc["P002_MC_A600_RT", "Effective_TRIP"])
    assert pd.isna(indexed.loc["P002_MC_A600_RT", "Effective_TWIP"])
    assert indexed.loc["P002_MC_A600_RT", "Negative_Evidence_Status"] == "INSUFFICIENT_FOR_ZERO"
    assert indexed.loc["P002_MC_A800_RT", "TWIP_Evidence_Type"] == "AUTHOR_CONDITION_ATTRIBUTION_SUPPORTED_BY_STUDY_CONCLUSION"
    assert indexed.loc["P002_MC_A700_RT", "TWIP_Evidence_Type"] == "DIRECT_TEM_DEFORMATION_TWIN_BUNDLES"
    assert indexed.loc["P002_MC_A800_RT", "Target_Evidence_Confidence"] == "High_TRIP_Medium_TWIP"
    assert indexed.loc["P002_MC_A700_RT", "Target_Evidence_Confidence"] == "High"
    hcp = stages.set_index("Observation_ID").HCP_Martensite_Fraction_at_Stage
    assert hcp.loc["P002_A800_EBSD_45"] == 0.057 and hcp.loc["P002_A800_EBSD_65"] == 0.163
    assert hcp.loc["P002_A700_EBSD_10"] == 0.007
    assert hcp.loc["P002_A700_EBSD_45"] == 0.038 and hcp.loc["P002_A700_EBSD_65"] == 0.072
    assert pd.isna(hcp.loc["P002_A800_EBSD_10"])
    physics = physics_table(sheets["P002_Physics"]).set_index("Feature")
    assert physics.loc["SFE_gamma_SF_estimated", "Value"] == 14
    assert physics.loc["SFE_gamma_SF_estimated", "Status"] == "CURRENT_PAPER_THERMODYNAMIC_ESTIMATE"
    assert physics.loc["DeltaG_FCC_to_HCP", "Value"] == -292
    assert physics.loc["DeltaG_FCC_to_HCP", "Method"] == "CALPHAD Thermo-Calc TCFE7"
    assert physics.loc["Planar_packing_density", "Value"] == 2.98e-5
    assert physics.loc["Lattice_constant_a", "Value"] == 0.3587
    assert physics.loc["Lattice_friction_stress_sigma0", "Status"] == "CURRENT_PAPER_MODEL_DERIVED_FROM_MECHANICAL_RESPONSE"
    assert physics.loc["Hall_Petch_coefficient_k", "Status"] == "CURRENT_PAPER_MODEL_DERIVED_FROM_MECHANICAL_RESPONSE"
    assert mapping.Mapping_Status.str.contains("RETAINED").all()
    assert counts(source) == (51, 32, 30, 27)
    assert counts(out) == (51, 31, 29, 26)
    assert exact.Effective_TRIP.eq(1).sum() == 2 and exact.Effective_TRIP.eq(0).sum() == 0
    assert exact.Effective_TWIP.eq(1).sum() == 2 and exact.Effective_TWIP.eq(0).sum() == 0
    assert provenance.Feature_Name.eq("Corrected_TRIP_Comparison").any()
    assert exact.P002_Recovery_Provenance_JSON.str.len().gt(2).all()
    assert file_hash(SOURCE) == SOURCE_SHA256 and file_hash(BOOK) == BOOK_SHA256


def write_audit(source: pd.DataFrame, out: pd.DataFrame, mapping: pd.DataFrame) -> None:
    before = counts(source)
    after = counts(out)
    AUDIT.write_text(
        f"""# P002 recovery v13 audit

## 1. Scope, source identity, and immutable base

- This is source-specific P002 dataset recovery only. The verified source is **{TITLE}**, DOI **{DOI}**; the official corrigendum DOI is **{CORRIGENDUM_DOI}**.
- Source identity status is `VERIFIED_PDF_AND_EXTERNAL_DOI_MATCH`. The input workbook and the 192-row V12-QC base were hash-checked before integration.
- Recovery V13 has **{len(out)} rows**. Every V12-QC row, source-column value, missingness state, and row order is preserved. V13 appends new fields and records; it does not revise the V12-QC cells in place.

## 2. Corrigendum handling

- The original self-comparison typo is not used. V13 applies the official statement: **the 800 C condition shows more pronounced TRIP than the 700 C condition**.
- Numerical EBSD fractions are unchanged. Corrigendum DOI, affected section, original/corrected semantics, and action are retained in the corrigendum and provenance tables.

## 3. Legacy mapping and replacement-aware counts

- All **5** legacy P002 rows remain. `P002_C01`, `P002_C02`, and `P002_C03` map scientifically—not by row order—to A800, A700, and A600 using DOI, composition, annealing temperature, room-temperature representation, strain rate, mechanics, and historical targets.
- `P002_C04` remains a reference-comparator support row. `P002_C05` remains a CALPHAD descriptor support row. Neither is promoted.
- Three exact primary conditions were appended: `P002_MC_A600_RT`, `P002_MC_A700_RT`, and `P002_MC_A800_RT`. Exact replacements alone supply P002's independent count, preventing legacy/exact double counting.
- Replacement-aware independent / usable TRIP / usable TWIP / usable joint counts: **{before[0]}/{before[1]}/{before[2]}/{before[3]} before -> {after[0]}/{after[1]}/{after[2]}/{after[3]} after**. The independent count remains 51; removing the unsupported A600 `0/0` from effective labels reduces each usable binary target and the joint target by one.
- Legacy A600 `0/0` is retained unchanged and copied only to `Original_TRIP`/`Original_TWIP` on the exact replacement. Verified `Effective_TRIP`/`Effective_TWIP` remain `NA/NA`; the conflict is explicit in both mapping and correction ledgers.

## 4. Hierarchy, independence, and replicates

- All exact conditions use study series `{SERIES}`, material parent `{MATERIAL}`, strict leakage group `{SERIES}`, and material leakage group `{MATERIAL}`.
- `Physical_Batch_ID` and `Replicate_ID` remain NA because the source does not identify them. `Replicate_n=3` is aggregate metadata for each annealing temperature; no individual or pseudo-replicate rows were created.
- Ten correlated stage/post-test observations and two non-independent Hall-Petch support states were appended. They cannot increase the independent experimental count. The A800 Hall-Petch input is the same condition as `P002_MC_A800_RT` and remains table-only rather than becoming a duplicate master row.

## 5. Chemistry and processing

- Chemistry is nominal `Fe40Mn10Co20Cr20Ni10` at.% only. `Measured_Bulk_Composition` and `Measured_Composition_at_pct` remain NA with status `NOMINAL_ONLY_EDS_QUALITATIVE_HOMOGENEITY_NO_QUANTITATIVE_BULK_ANALYSIS`.
- EDS/STEM-EDS homogeneity is retained only as qualitative spatial evidence; it is never converted to quantitative bulk chemistry.
- Processing preserves vacuum induction melting/casting from >99.8 wt% raw metals; hot rolling at 900 C, 50%, 10 to 5 mm; homogenization at 1200 C for 2 h in Ar followed by water quench; cold rolling 70%, 5 to 1.5 mm; and 600/700/800 C, 30 min, water-quenched final anneals.
- Tensile testing is uniaxial at source-text `room temperature`, 1e-3 s^-1, gauge 10 x 2.5 x approximately 1.25 mm. Exact numeric `Test_T_K` remains NA.

## 6. Initial microstructure and twin-origin safeguard

- All three exact conditions are qualitatively single FCC with direct initial HCP absence (`Initial_HCP_fraction=0`). Exact numeric FCC fractions remain NA.
- A800 is fully recrystallized (1.0/0), average grain size 4.7 +/- 0.3 um, randomized, with abundant annealing twins and very low dislocation density.
- A700 retains approximately 0.92/0.08 recrystallized/non-recrystallized fractions, approximately 3.6 um RZ grain size, 12 um NRZ dimension, 0.95 um subgrains, 220 nm mean pre-test twin width, and raw scoped wording `~27.5 vol% in RZ` for Sigma3 boundaries.
- A600 retains approximately 0.13/0.87 recrystallized/non-recrystallized fractions, approximately 1.8 um RZ grain size, 0.40 um NRZ subgrains, dislocation tangles, and pre-existing nanoscale twins.
- Annealing and retained processing twins are initial-state descriptors only. They never generate tensile `Effective_TWIP=1` without separate deformation evidence.

## 7. Mechanical outcomes and target evidence

- Post-test mechanical outcomes are leakage-sensitive metadata: A800 375/785 MPa and 77.5%; A700 589/865 MPa and 69.1%; A600 approximately 1060 MPa YS with UTS/elongation NA. Figure 6 was not digitized.
- A800 is TRIP=1 from direct EBSD/XRD deformation-induced FCC-to-HCP evidence. TWIP=1 is retained at **medium** directness as `AUTHOR_CONDITION_ATTRIBUTION_SUPPORTED_BY_STUDY_CONCLUSION`; it is not represented as direct A800 TEM evidence. Slip=1.
- A700 is TRIP=1/TWIP=1/Slip=1 with high-confidence direct EBSD plus near-fracture TEM/SAED/HR-STEM evidence for HCP martensite, deformation-twin bundles, dislocation structures, and stacking faults.
- A600 is TRIP=NA/TWIP=NA/Slip=1 with `Negative_Evidence_Status=INSUFFICIENT_FOR_ZERO`. “Hindered/suppressed” and absent dedicated post-test characterization are not converted to negatives.

## 8. Correlated stage evidence

- A800 EBSD keeps HCP fractions 5.7% at 45% local strain and 16.3% at 65%; the 10% observation is “barely observed” with no fabricated fraction. XRD 0/45/~95% observations remain correlated children, with the zero explicitly scoped to pre-deformation phase evidence.
- A700 EBSD keeps 0.7/3.8/7.2% HCP at 10/45/65% local strain. The near-fracture TEM/SAED/HR-STEM record is correlated post-test evidence, not another ML sample.

## 9. Physics, thermodynamics, and Hall-Petch scope

- `DeltaG_FCC_to_HCP=-292 J/mol` at 300 K is `CURRENT_PAPER_CALCULATED` by Thermo-Calc TCFE7. It is not transferred to other papers/alloys.
- SFE approximately 14 mJ/m2 at 300 K is `CURRENT_PAPER_THERMODYNAMIC_ESTIMATE`, not experimental SFE. The method-specific record retains DeltaG, 22.2 J/mol transformation strain energy, 15 mJ/m2 coherent interface energy, 2.98e-5 mol/m2 planar density, and the 0.3587 nm lattice constant used in the derivation. Reference/model inputs remain distinct from current-paper measurements.
- Hall-Petch inputs retain as-homogenized 128 +/- 18 um / 188 MPa, A900 16 +/- 0.6 um / 253 MPa, and A800 4.7 +/- 0.3 um / 375 MPa. Derived sigma0 approximately 139 MPa and k approximately 504 MPa um^0.5 are `CURRENT_PAPER_MODEL_DERIVED_FROM_MECHANICAL_RESPONSE`, leakage-sensitive, and not primary predictors.

## 10. Provenance, gaps, and downstream status

- Field-level provenance includes Paper_ID, DOI, corrigendum DOI, material parent, applicable ML/record identity, feature, value, units, evidence type/location, method, confidence, and recovery status. Meaningful NA decisions are recorded as `VERIFIED_NA`.
- Remaining P002 gaps are quantitative post-melt bulk chemistry, exact test temperature in K, physical-batch/replicate identities and individual results, exact initial FCC fractions, A600 UTS/elongation and direct post-test TRIP/TWIP characterization, a numeric A800 10% HCP fraction, direct A800 post-test twin imaging, and some state-specific uncertainty values.
- Remaining global blockers include sparse independent negatives (now one fewer effective P002 negative for each binary target), incomplete targets, missing physical batches, paper/material dependence, unavailable P018/P019 sources, sparse measured chemistry/initial-state/experimental-SFE coverage, and prediction-time leakage controls.
- Existing V12 Global QC, Feature Schema V1 coverage statistics, feature coverage reports, and Grouped Split Design V1 are preserved but **stale with respect to V13**. They must be refreshed before matrix construction; this task deliberately does not rerun them or reuse the old split roster as current.
- No ML training occurred. No feature engineering occurred. No chemistry reconciliation/normalization, imputation, descriptor calculation, resampling, synthetic data, pseudo-replication, or performance metric occurred.
""",
        encoding="utf-8",
    )


def integrate() -> tuple[pd.DataFrame, pd.DataFrame]:
    source, sheets = load_and_verify()
    conditions = sheets["P002_Conditions"]
    assert set(conditions.ML_Condition_ID) == EXACT_IDS and len(conditions) == 3
    assert conditions.Independent_Experimental_ML_sample.eq(True).all()
    mapping = verify_legacy_mapping(source, conditions)

    out = source.copy()
    for column in NEW_COLUMNS:
        if column not in out:
            out[column] = pd.NA
    add_legacy_metadata(out, mapping)

    exact_rows = make_exact_rows(list(out.columns), sheets, mapping)
    stage_rows = make_stage_rows(list(out.columns), sheets["P002_Stage_Evidence"])
    support_rows = make_support_rows(list(out.columns), sheets["P002_HallPetch_Support"])
    new_rows = exact_rows + stage_rows + support_rows
    provenance = attach_provenance(new_rows, exact_rows, stage_rows, support_rows, sheets)
    # Object alignment preserves the exact source values while avoiding pandas'
    # deprecated all-NA dtype inference during heterogeneous recovery-row append.
    out = pd.concat(
        [out.astype(object), pd.DataFrame(new_rows, columns=out.columns).astype(object)],
        ignore_index=True,
    )

    validate(source, out, sheets, mapping, provenance)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    TABLE.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)

    hierarchy = conditions[
        [
            "Paper_ID",
            "DOI",
            "Study_Series_ID",
            "Material_Parent_ID",
            "ML_Condition_ID",
            "Independent_Experimental_ML_sample",
            "Leakage_Group_Strict",
            "Leakage_Group_Material",
        ]
    ].copy()
    hierarchy["Physical_Batch_ID"] = pd.NA
    hierarchy["Replicate_ID"] = pd.NA
    hierarchy["Replicate_n"] = 3
    hierarchy["Replacement_Aware_Role"] = "EXACT_REPLACEMENT_COUNT_SOURCE"

    exports = {
        "hierarchy": hierarchy,
        "processing": build_processing_table(conditions),
        "initial_microstructure": sheets["P002_Initial_Microstructure"],
        "mechanical_response": sheets["P002_Mechanical_Response"],
        "stage_evidence": sheets["P002_Stage_Evidence"],
        "target_evidence": sheets["P002_Target_Evidence"],
        "physics_thermodynamics": physics_table(sheets["P002_Physics"]),
        "hall_petch_support": sheets["P002_HallPetch_Support"],
        "corrigendum": sheets["P002_Corrigendum"],
        "provenance": provenance,
        "legacy_mapping": mapping,
        "decision_correction_ledger": decision_correction_ledger(
            sheets["P002_Integration_Decisions"], sheets["P002_Corrigendum"]
        ),
    }
    for name, frame in exports.items():
        frame.to_csv(TABLE / f"p002_recovery_v13_{name}.csv", index=False)
    write_audit(source, out, mapping)
    return source, out


if __name__ == "__main__":
    integrate()
