"""Non-destructive V17 QC refresh and leakage-safe Controlled Pilot ML V1."""
from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

try:
    from scripts.integrate_p023_recovery_v17 import experimental_pool
except ModuleNotFoundError:  # direct CLI execution
    from integrate_p023_recovery_v17 import experimental_pool


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed/master_extended_recovery_v17.csv"
QC_PATH = ROOT / "data/processed/master_extended_recovery_v17_qc.csv"
EXP_PATH = ROOT / "data/processed/experimental_condition_index_v17.csv"
COMP_PATH = ROOT / "data/processed/computational_condition_index_v17.csv"
SCHEMA_V1 = ROOT / "data/schema/feature_schema_v1.csv"
SCHEMA_V2 = ROOT / "data/schema/feature_schema_v2.csv"
SPLIT_CANDIDATES = ROOT / "data/splits/split_candidates_v2.csv"
SPLIT_MANIFEST = ROOT / "data/splits/split_manifest_v2.csv"
MODEL_DIR = ROOT / "data/modeling/pilot_v1"
REPORT_DIR = ROOT / "reports"
TABLE_DIR = REPORT_DIR / "tables"

SOURCE_EXPECTED_SHA256 = "31e2b0534ab9f36e14393392cb1f3db6fcea83033475864f23d15d735e8b2375"
RANDOM_STATE = 1729
M2_FEATURES = ["Fe_at%", "Mn_at%", "Co_at%", "Cr_at%", "Test_T_K", "Strain_rate_s-1"]
MODEL_IDS = [
    "M0_DUMMY_MOST_FREQUENT",
    "M1_LOGISTIC_BALANCED",
    "M2_RANDOM_FOREST_BALANCED",
    "M3_SVC_RBF_BALANCED",
]
QC_FIELDS = [
    "QC_V17_Row_Role",
    "QC_V17_Experimental_Eligibility",
    "QC_V17_Computational_Eligibility",
    "QC_V17_Replacement_Status",
    "QC_V17_TRIP_Status",
    "QC_V17_TWIP_Status",
    "QC_V17_Target_Integrity",
    "QC_V17_Provenance_Status",
    "QC_V17_Leakage_Risk",
    "QC_V17_Tier",
    "QC_V17_Feature_Schema_Status",
    "QC_V17_Review_Status",
]
ROLES = {
    "PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL", "TARGET_ONLY",
    "LEAKAGE_POST_TEST", "LEAKAGE_MECHANICAL_OUTCOME", "LEAKAGE_MODEL_DERIVED",
    "COMPUTATIONAL_ONLY", "GROUPING_ONLY", "IDENTIFIER_ONLY", "PROVENANCE_ONLY",
    "METADATA_ONLY",
}
V1_ROLE_MAP = {
    "POST_TEST_LEAKAGE": "LEAKAGE_POST_TEST",
    "MECHANICAL_OUTCOME_LEAKAGE": "LEAKAGE_MECHANICAL_OUTCOME",
    "MODEL_DERIVED_LEAKAGE": "LEAKAGE_MODEL_DERIVED",
    "UNRESOLVED_REVIEW": "METADATA_ONLY",
}
HCP_TWIP_IDS = {
    "P013_MC_ASCAST_RT", "P020_MC_TRIPHEA_INSITU",
    "P023_MC_650_15_RT", "P023_MC_850_30_RT",
}
FCC_TWIP_IDS = {
    "P012_MC_BASE_RT", "P012_MC_MO_RT", "P012_MC_C_RT", "P012_MC_C_77K",
    "P015_MC_298K", "P022_MC_C2_ASCAST_RT", "P022_MC_C2MO1_ASCAST_RT",
    "P022_MC_C2MO2_ASCAST_RT",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def present(value: Any) -> bool:
    return value is not None and not pd.isna(value) and str(value).strip().lower() not in {"", "na", "nan", "none"}


def joined(values: Iterable[Any]) -> str:
    return "|".join(sorted({str(v) for v in values if present(v)}))


def preflight(source: pd.DataFrame) -> None:
    assert source.shape == (234, 584)
    assert sha256(SOURCE) == SOURCE_EXPECTED_SHA256


def computational_pool(source: pd.DataFrame) -> pd.DataFrame:
    flag = source.Independent_Computational_Condition.astype(str).str.upper().eq("TRUE")
    out = source[source.Paper_ID.eq("P017") & source.P017_Record_Role.eq(
        "RECOVERED_EXACT_COMPUTATIONAL_CONDITION") & flag].copy()
    assert len(out) == 12
    return out


def group_id(row: pd.Series) -> str:
    return str(row.Leakage_Group_Strict) if present(row.Leakage_Group_Strict) else f"PAPER::{row.Paper_ID}"


def formula_key(value: Any) -> str | None:
    if not present(value):
        return None
    text = re.sub(r"(?i)^nominal\s+", "", str(value).split(";")[0]).strip()
    return re.sub(r"[^A-Za-z0-9.]", "", text).upper() or None


def family_key(row: pd.Series) -> str:
    formula = formula_key(row.get("Nominal_Composition_at_pct")) or formula_key(row.get("Original_Composition"))
    if formula:
        return f"FORMULA::{formula}"
    if present(row.get("Alloy_Family_Text")):
        return f"TEXT::{str(row.Alloy_Family_Text).strip().upper()}"
    if present(row.get("Material_Parent_ID")):
        return f"MATERIAL::{row.Material_Parent_ID}"
    return f"PAPER::{row.Paper_ID}::UNRESOLVED_FAMILY"


def parse_formula(value: Any) -> dict[str, float]:
    if not present(value):
        return {}
    return {el: float(number) for el, number in re.findall(r"([A-Z][a-z]?)([0-9]+(?:\.[0-9]+)?)", str(value))}


def chemistry(row: pd.Series) -> tuple[dict[str, float], str, str]:
    basis = str(row.get("Composition_basis", "")).upper()
    original_basis = str(row.get("Original_Composition_Basis", "")).upper()
    statuses = " ".join(str(row.get(c, "")) for c in [
        "Composition_Status", "Measured_Composition_Status", "Recovered_Composition_Status",
        "Composition_Normalization_Status",
    ]).upper()
    if "ATOMIC_RATIO_AS_REPORTED" in basis or "ATOMIC_RATIO" in original_basis:
        return {}, "UNAVAILABLE_POLICY_REJECTED", "P022 raw atomic-ratio formula is not normalized"
    for col in ["Measured_Composition_at_pct", "Recovered_Bulk_Composition_at_pct"]:
        parsed = parse_formula(row.get(col))
        if parsed and ("MEASURED" in statuses or "BULK" in statuses):
            return parsed, "MEASURED_BULK", f"Selected explicitly reported {col}"
    if "MEASURED WET" in basis and all(pd.notna(row.get(f"{e}_at%")) for e in ["Fe", "Mn", "Co", "Cr"]):
        return {e: float(row[f"{e}_at%"]) for e in ["Fe", "Mn", "Co", "Cr"]}, "MEASURED_BULK", "Selected structured measured wet chemistry"
    if row.Paper_ID == "P011":
        return parse_formula(str(row.Original_Composition).split(";")[0]), "NOMINAL", "Nominal formula selected; feedstock EDS not promoted to bulk chemistry"
    nominal = parse_formula(row.get("Nominal_Composition_at_pct"))
    if nominal:
        return nominal, "NOMINAL", "Selected explicitly reported nominal composition"
    structured = {e: float(row[f"{e}_at%"] ) for e in ["Fe", "Mn", "Co", "Cr"] if pd.notna(row.get(f"{e}_at%"))}
    if structured:
        kind = "MEASURED_BULK" if "MEASURED" in basis else "SOURCE_STRUCTURED"
        return structured, kind, "Selected source structured at.% fields without filling absent elements"
    original = re.sub(r"(?i)^nominal\s+", "", str(row.get("Original_Composition", "")).split(";")[0]).strip()
    parsed = parse_formula(original)
    return (parsed, "NOMINAL", "Selected explicitly reported original/nominal formula") if parsed else ({}, "UNAVAILABLE", "No policy-compatible bulk or nominal representation")


def evidence_quality(row: pd.Series, target: str) -> str:
    if pd.isna(row.get(f"Effective_{target}")):
        return "NA"
    paper_target = f"{row.Paper_ID}_Target_Status"
    text = " ".join(str(row.get(c, "")) for c in [
        f"Evidence_{target}", f"{target}_Evidence_Type", "Characterization_methods",
        "Label_confidence", "Target_Evidence_Confidence", "Target_Status", paper_target,
    ]).upper()
    if "AUTHOR" in text or "MEDIUM" in text:
        return "AUTHOR_ATTRIBUTED_OR_MEDIUM"
    direct = ["DIRECT", "EBSD", "TEM", "XRD", "SXRD", "NEUTRON", "DIFFRACTION",
              "RIETVELD", "SADP", "SAED", "NANOTWIN", "DEFORMATION TWIN",
              "PEAK-INTENSITY", "HCP RISES", "MARTENSITE"]
    return "DIRECT_HIGH_CONFIDENCE" if any(token in text for token in direct) else "OTHER_VERIFIED"


def twip_phase(row: pd.Series) -> str:
    if pd.isna(row.Effective_TWIP):
        return "NA"
    if int(row.Effective_TWIP) == 0:
        return "NOT_APPLICABLE_NEGATIVE"
    condition, phase = str(row.ML_Condition_ID), str(row.get("TWIP_Phase", "")).upper()
    if condition in HCP_TWIP_IDS or "HCP" in phase or "EPSILON" in phase:
        return "HCP_EPSILON"
    if condition in FCC_TWIP_IDS or phase == "FCC":
        return "FCC"
    if "UNRESOLVED" in phase:
        return "PHASE_UNRESOLVED"
    return "OTHER_UNKNOWN"


def strict_direct(label: Any, quality: str) -> Any:
    if pd.isna(label):
        return pd.NA
    return 0 if int(label) == 0 else (1 if quality == "DIRECT_HIGH_CONFIDENCE" else pd.NA)


def build_experimental_index(source: pd.DataFrame) -> pd.DataFrame:
    exp = experimental_pool(source).copy()
    assert len(exp) == exp.ML_Condition_ID.nunique() == 69
    exp.insert(0, "Source_Row_Index", exp.index.astype(int))
    exp["Effective_Group_ID"] = exp.apply(group_id, axis=1)
    exp["Alloy_Family_Audit_Key"] = exp.apply(family_key, axis=1)
    exp["TRIP_Evidence_Quality_Flag"] = exp.apply(lambda r: evidence_quality(r, "TRIP"), axis=1)
    exp["TWIP_Evidence_Quality_Flag"] = exp.apply(lambda r: evidence_quality(r, "TWIP"), axis=1)
    exp["TWIP_Phase_Category"] = exp.apply(twip_phase, axis=1)
    exp["T2_ANY_TWIP"] = exp.Effective_TWIP
    exp["T2_FCC_TWIP_STRICT"] = [pd.NA if pd.isna(v) else (0 if int(v) == 0 else (1 if p == "FCC" else pd.NA)) for v, p in zip(exp.Effective_TWIP, exp.TWIP_Phase_Category)]
    exp["T1_TRIP_STRICT_DIRECT"] = [strict_direct(v, q) for v, q in zip(exp.Effective_TRIP, exp.TRIP_Evidence_Quality_Flag)]
    exp["T2_ANY_TWIP_STRICT_DIRECT"] = [strict_direct(v, q) for v, q in zip(exp.Effective_TWIP, exp.TWIP_Evidence_Quality_Flag)]
    selected = [chemistry(row) for _, row in exp.iterrows()]
    for element in ["Fe", "Mn", "Co", "Cr"]:
        exp[f"M2_{element}_at%"] = [values.get(element, pd.NA) for values, _, _ in selected]
    exp["M2_Test_T_K"] = exp.Test_T_K
    exp["M2_Strain_rate_s-1"] = exp["Strain_rate_s-1"]
    exp["M2_Composition_Source"] = [kind for _, kind, _ in selected]
    exp["M2_Composition_Selection_Note"] = [note for _, _, note in selected]
    required = [f"M2_{c}" for c in M2_FEATURES]
    exp["M2_Missing_Required_Fields"] = exp[required].apply(lambda row: "|".join(c for c, v in zip(M2_FEATURES, row) if pd.isna(v)), axis=1)
    exp["M2_Complete"] = exp.M2_Missing_Required_Fields.eq("")
    keep = [
        "Source_Row_Index", "Paper_ID", "DOI", "ML_Condition_ID", "Observation_ID",
        "Study_Series_ID", "Material_Parent_ID", "Leakage_Group_Strict", "Effective_Group_ID",
        "Alloy_Family_Audit_Key", "Data_Origin", "Observation_Role",
        "Independent_Experimental_ML_sample", "Effective_TRIP", "Effective_TWIP",
        "T2_ANY_TWIP", "T2_FCC_TWIP_STRICT", "T1_TRIP_STRICT_DIRECT",
        "T2_ANY_TWIP_STRICT_DIRECT", "TRIP_Evidence_Quality_Flag",
        "TWIP_Evidence_Quality_Flag", "TWIP_Phase", "TWIP_Phase_Category",
        "Target_Status", "Label_confidence", "Target_Evidence_Confidence",
        "M2_Composition_Source", "M2_Composition_Selection_Note", *required,
        "M2_Missing_Required_Fields", "M2_Complete",
    ]
    return exp[[c for c in keep if c in exp]].reset_index(drop=True)


def build_computational_index(source: pd.DataFrame) -> pd.DataFrame:
    comp = computational_pool(source)
    keep = ["Paper_ID", "DOI", "Computational_Condition_ID", "ML_Condition_ID", "Observation_ID",
            "Study_Series_ID", "Material_Parent_ID", "Leakage_Group_Strict", "Data_Origin",
            "Observation_Role", "P017_Record_Role", "Independent_Computational_Condition",
            "Independent_Experimental_ML_sample", "Experimental_Target_Eligibility",
            "Paper_Native_TRIP", "Paper_Native_TWIP", "SIS_PSR_GPa", "UTS_PSR_GPa"]
    return comp[[c for c in keep if c in comp]].reset_index(drop=True)


def build_qc(source: pd.DataFrame, exp: pd.DataFrame, comp: pd.DataFrame) -> pd.DataFrame:
    qc = source.copy(deep=True)
    exp_rows = set(exp.Source_Row_Index.astype(int))
    comp_obs = set(comp.Observation_ID.astype(str))
    is_exp = source.index.isin(exp_rows)
    is_comp = source.Observation_ID.astype(str).isin(comp_obs)
    is_stage = source.Observation_Role.astype(str).str.contains("STAGE|SUPPORT", case=False, na=False)
    qc["QC_V17_Row_Role"] = np.select(
        [is_exp, is_comp, is_stage],
        ["CURRENT_INDEPENDENT_EXPERIMENTAL_CONDITION", "EXACT_COMPUTATIONAL_CONDITION", "SUPPORTING_OR_STAGE_RECORD"],
        default="OTHER_SOURCE_RECORD",
    )
    qc["QC_V17_Experimental_Eligibility"] = np.where(is_exp, "ELIGIBLE_CURRENT_EXPERIMENTAL_POOL", "EXCLUDED")
    qc["QC_V17_Computational_Eligibility"] = np.where(is_comp, "ELIGIBLE_COMPUTATIONAL_INDEX_ONLY", "NOT_COMPUTATIONAL_INDEX")
    replacement = pd.Series("NOT_AN_INDEPENDENT_EXPERIMENTAL_ROW", index=source.index)
    replacement.loc[list(exp_rows)] = "CURRENT_INDEPENDENT_EXPERIMENTAL_CONDITION"
    old_independent = source.Data_Origin.eq("EXPERIMENTAL") & source.Observation_Role.eq("INDEPENDENT_CONDITION") & ~source.index.isin(exp_rows)
    replacement.loc[old_independent] = "LEGACY_OR_REPLACED_EXCLUDED_FROM_CURRENT_COUNT"
    qc["QC_V17_Replacement_Status"] = replacement
    for target in ["TRIP", "TWIP"]:
        values = source[f"Effective_{target}"]
        qc[f"QC_V17_{target}_Status"] = np.where(values.eq(1), "POSITIVE", np.where(values.eq(0), "NEGATIVE", "UNRESOLVED_NA"))
    valid = (source.Effective_TRIP.isna() | source.Effective_TRIP.isin([0, 1])) & (source.Effective_TWIP.isna() | source.Effective_TWIP.isin([0, 1]))
    qc["QC_V17_Target_Integrity"] = np.where(valid, "VALID_BINARY_OR_NA", "INVALID_TARGET_VALUE")
    provenance = source.Paper_ID.notna() & source.DOI.notna() & source.Observation_ID.notna() & (source.Source_location.notna() | source.Source_File.notna())
    qc["QC_V17_Provenance_Status"] = np.where(provenance, "CORE_TRACEABILITY_PRESENT", "CORE_TRACEABILITY_GAP")
    post = source[["Deformation_stage", "True_strain", "Local_strain", "Postfracture_Phase_State", "PostTest_FCC_fraction", "PostTest_HCP_fraction"]].notna().any(axis=1)
    mech = source[["YS_MPa", "UTS_MPa", "Elongation_pct", "Engineering_YS_MPa", "Engineering_UTS_MPa", "True_Tensile_Strength_MPa", "SDI_MPa"]].notna().any(axis=1)
    qc["QC_V17_Leakage_Risk"] = np.select([post, mech], ["POST_TEST_OR_STAGE_FIELDS_PRESENT", "MECHANICAL_OUTCOME_FIELDS_PRESENT"], default="NO_ROW_LEVEL_LEAKAGE_SIGNAL_IN_AUDIT_SET")
    complete = source.index.to_series().map(exp.set_index("Source_Row_Index").M2_Complete).eq(True)
    both = source[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1)
    one = source[["Effective_TRIP", "Effective_TWIP"]].notna().any(axis=1)
    qc["QC_V17_Tier"] = np.select(
        [is_exp & both & complete, is_exp & one, is_exp, is_comp],
        ["TIER_A_JOINT_TARGET_M2_COMPLETE", "TIER_B_USABLE_TARGET", "TIER_C_EXPERIMENTAL_TARGET_GAP", "TIER_D_COMPUTATIONAL_SEPARATE"],
        default="TIER_E_SUPPORTING_OR_LEGACY",
    )
    qc["QC_V17_Feature_Schema_Status"] = "CLASSIFIED_IN_FEATURE_SCHEMA_V2"
    qc["QC_V17_Review_Status"] = np.where(valid, "PASS_WITH_DOCUMENTED_LIMITATIONS", "REQUIRES_CORRECTION")
    assert list(qc.columns[584:]) == QC_FIELDS
    pd.testing.assert_frame_equal(qc.iloc[:, :584], source, check_dtype=False)
    assert qc.iloc[:, :584].isna().equals(source.isna())
    return qc


TARGET_NEW = {
    "Paper_Native_TRIP", "Paper_Native_TWIP", "TWIP_induced_TRIP_Status", "TWIP_induced_TRIP_Timing",
    "TRIP_induced_TWIP_Status", "TRIP_induced_TWIP_Timing", "P002_Target_Status",
    "TRIP_Evidence_Type", "TWIP_Evidence_Type", "Negative_Evidence_Status",
    "Condition_Level_Target_Evidence", "Target_Evidence_Confidence", "Initial_TRIP_Target_Guardrail",
    "Target_Status", "TRIP_Parent_Phase", "TRIP_Product_Phase", "TWIP_Phase", "TWIP_Mode",
    "Slip_Evidence_Type", "P020_Target_Semantic_Note", "Alpha_BCT_Transformation_Status",
    "Alpha_BCT_Transformation_Evidence", "Alpha_BCT_Target_Safeguard", "TWIP_Evidence_Abundance",
    "TWIP_Evidence_Strength", "Paper_Native_Mechanism_Attribution",
    "Author_Attributed_Target_Evidence_Grade", "TRIP_to_TWIP_Negative_Safeguard",
    "Initial_HCP_Target_Guardrail", "Phase_Specific_TWIP_Safeguard",
}
GROUP_NEW = {"Independent_Computational_Condition", "Independent_Experimental_ML_sample", "Alloy_Family_Text", "Alloy_Family_Use", "Replicate_n_Status", "Replicate_Scope"}
COMPUTATIONAL_NEW = {"SIS_PSR_GPa", "UTS_PSR_GPa", "UTS_PSR_Status", "Initial_BCC_fraction_raw", "Initial_BCC_fraction_status", "PostQuench_Initial_Structure", "ThermoCalc_Software", "ThermoCalc_Database", "ThermoCalc_Context_Status", "ThermoCalc_Observation_Safeguard"}
MODEL_DERIVED_NEW = {
    "HDI_at_stage", "HDI_Hardening", "TRIP_Onset_Macro_Stress_MPa",
    "HCP_Tensile_Twin_Onset_Macro_Stress_MPa", "HCP_Multiple_Twin_Onset_Macro_Stress_MPa",
    "HCP_Multiple_Twin_Onset_Macro_Strain_pct", "TRIP_Late_Suppression_Strain_Threshold_pct",
    "TRIP_Rate_Status", "TRIP_Onset_True_Stress_MPa", "TRIP_Onset_Engineering_Stress_Approx_MPa",
    "TRIP_Onset_Strain_Approx_pct", "WH_Rate_at_Slope_Change_MPa", "TRIP_Onset_Evidence_Status",
    "TRIP_Onset_Predictor_Eligibility", "WH_Rate_Predictor_Eligibility", "Direct_Stage_Fabrication_Status",
}
MECHANICAL_NEW = {
    "Mechanical_Value_Status", "Mechanical_Predictor_Eligibility", "Apparent_Yield_Onset_MPa",
    "Yield_Definition", "Reported_Ultimate_Strength_MPa", "Reported_Elongation_pct", "Strain_Basis_Status",
    "True_Tensile_Strength_MPa", "SDI_MPa", "SDI_Predictor_Eligibility", "Mechanical_Stress_Basis_Status",
    "Mechanical_Value_Approximation_Status",
}
POST_NEW = {
    "Stage_Method", "Local_Strain_pct", "HCP_Martensite_Fraction_at_Stage", "Postfracture_Evidence_Method",
    "Postfracture_HCP_fraction_scope", "Postfracture_Predictor_Eligibility", "Postfracture_Mechanical_Twin_Status",
    "Slip_StackingFault_Status", "FCC_fraction_at_fracture", "HCP_fraction_at_fracture",
    "Fracture_Phase_Fraction_Status", "Stage_Stress_Range_Raw", "Stage_Strain_Relation", "Macro_Stress_MPa",
    "Macro_Strain_pct", "Mechanism_Event", "TRIP_Stage", "TWIP_Stage", "Slip_Stage", "Stage_Evidence_Type",
    "PostTest_FCC_fraction", "PostTest_HCP_fraction", "PostTest_Phase_Fraction_Method", "PostTest_Evidence_Status",
    "PostTest_Predictor_Eligibility", "PostTest_Twin_Evidence", "PostTest_Slip_Evidence",
    "PostTest_GND_Evidence_Status", "PostTest_IPF_Evidence_Status",
}
SAFE_DIRECT_NEW = {
    "Measured_Bulk_Composition", "Hot_Roll_Input_Thickness_mm", "Hot_Roll_Output_Thickness_mm",
    "Cold_Roll_Input_Thickness_mm", "Cold_Roll_Output_Thickness_mm", "Homogenization_Atmosphere",
    "Post_Homogenization_Quench", "Loading_Mode", "Initial_Phase", "NonRecrystallized_fraction",
    "RZ_Grain_Size_um", "RZ_Grain_Size_Uncertainty_um", "NRZ_Subgrain_Size_um", "NRZ_Avg_Dimension_um",
    "PreTest_Twin_State", "PreTest_Twin_Origin", "PreTest_Twin_Width_nm", "Initial_Dislocation_State",
    "Orientation_State", "Melting_Route", "Casting_Route", "Cast_Bar_Dimensions_mm", "Post_Anneal_Cooling",
    "FCC_Grain_Size_um", "FCC_Grain_Morphology", "HCP_Lath_Thickness_um", "Phase_Fraction_Methods",
    "Remelt_Count_Min", "Alloy_Mass_g_Approx", "Remolded_Ingot_Dimensions_mm", "Homogenization_T_C_Raw",
    "Hot_Roll_T_C_Raw", "Hot_Roll_Final_Thickness_mm", "Anneal_T_C_Raw", "Post_Anneal_Quench",
    "Test_T_C", "Test_Atmosphere", "Specimen_Orientation", "Initial_Alpha_BCT_fraction",
    "Initial_Secondary_Phase_Status", "Fully_Recrystallized", "PreTest_Cryogenic_Immersion",
    "PreTest_State_Timing", "Al_at%", "Backfill_Atmosphere", "Cast_Ingot_Dimensions_mm",
    "FSP_Pass1_Rotation_rpm", "FSP_Pass2_Rotation_rpm", "FSP_Traverse_Speed_mm_min",
    "FSP_Plunge_Depth_mm", "FSP_Tilt_deg", "FSP_Backplate", "FSP_Shielding",
    "PreTest_Phase_Fraction_SD_pct", "PreTest_Phase_Fraction_Method", "Precipitate_State",
}
SAFE_CONDITIONAL_NEW = {
    "EDS_Qualitative_Homogeneity", "Specimen_Thickness_Status", "Sigma3_Twin_Boundary_Fraction_Raw",
    "Physics_Temperature_K", "Local_EDS_Composition_at_pct", "Local_EDS_Composition_Scope", "SFE_Raw_Bound",
    "SFE_Bound_Status", "SFE_Predictor_Eligibility", "SFE_Qualitative_Temperature_Status",
    "Original_Composition_Basis", "Normalized_Composition_at_pct", "Composition_Normalization_Status",
    "Atomic_Ratio_C_Addition_Raw", "Atomic_Ratio_Mo_Addition_Raw", "Processing_State",
    "Initial_Secondary_Phase", "Dendrite_Morphology", "Sigma_Phase_Evidence_Status", "Twin_Boundary_Character",
    "Twin_Population_Qualitative", "Twin_Fraction_Status", "SFE_Qualitative_Trend",
    "C4_Carbide_XRD_Coexistence_Safeguard", "Local_EDS_AsCast_Composition_at_pct",
    "Local_EDS_DPass_Composition_at_pct", "Local_EDS_Chemistry_Status", "Vacuum_Level_Raw",
    "PreTest_Phase_Fraction_Status", "Matrix_Al_Content_Trend", "AsCast_Support_Grain_Size_um",
    "AsCast_Support_Grain_Size_SD_um", "AsCast_Grain_Size_Use_Status",
}


def classify_new(column: str) -> tuple[str, str, str]:
    upper = column.upper()
    if column in TARGET_NEW or ("TARGET" in upper and "ELIGIBILITY" not in upper):
        return "TARGET_ONLY", "TARGET", "Target definition/evidence; never a predictor"
    if column in GROUP_NEW or any(t in column for t in ["Study_Series", "Material_Parent", "Leakage_Group", "Replicate"]):
        return "GROUPING_ONLY", "IDENTITY_GROUPING", "Grouping/independence control only"
    if column in {"Computational_Condition_ID", "Support_Record_ID", "Stage_Label"} or column.endswith("_ID"):
        return "IDENTIFIER_ONLY", "IDENTITY_GROUPING", "Identifier only"
    if column in COMPUTATIONAL_NEW or column.startswith("Computational_"):
        return "COMPUTATIONAL_ONLY", "COMPUTATIONAL_ONLY", "Computational context outside experimental predictors"
    if column in MODEL_DERIVED_NEW or any(t in upper for t in ["ONSET", "WH_RATE", "CRITICAL_STRESS"]):
        return "LEAKAGE_MODEL_DERIVED", "MODEL_DERIVED_RESPONSE", "Derived from observed response/mechanism"
    if column in MECHANICAL_NEW or any(t in upper for t in ["YS_MPA", "UTS_MPA", "ELONGATION", "TENSILE_STRENGTH", "SDI_MPA"]):
        return "LEAKAGE_MECHANICAL_OUTCOME", "MECHANICAL_RESPONSE", "Same-test mechanical outcome"
    if column in POST_NEW or any(t in upper for t in ["POSTTEST", "POST_TEST", "POSTFRACTURE", "AT_FRACTURE", "GND", "DEFORMATION_TWIN"]):
        return "LEAKAGE_POST_TEST", "POST_DEFORMATION_MICROSTRUCTURE", "Observed after loading begins"
    if column in SAFE_DIRECT_NEW:
        return "PREDICTOR_SAFE_DIRECT", "PROCESSING_OR_INITIAL_STATE", "Known before tensile loading"
    if column in SAFE_CONDITIONAL_NEW:
        return "PREDICTOR_SAFE_CONDITIONAL", "METHOD_OR_SCOPE_SENSITIVE", "Pre-test candidate requiring method/source gating"
    if any(t in column for t in ["Provenance", "Source_Identity", "Source_Family"]):
        return "PROVENANCE_ONLY", "PROVENANCE_QC", "Traceability/source audit only"
    if column in {"Journal", "Volume", "Issue", "Pages", "Publication_Year", "Source_URL", "Article_Number"}:
        return "PROVENANCE_ONLY", "PROVENANCE_QC", "Bibliographic provenance"
    if column.startswith("P0") or column.startswith("QC_") or column.endswith("_Status") or column.endswith("_Safeguard"):
        return "METADATA_ONLY", "PROVENANCE_QC", "Audit/status metadata only"
    return "METADATA_ONLY", "OTHER", "Conservatively excluded from Pilot M2"


def build_schema(qc: pd.DataFrame, exp: pd.DataFrame) -> pd.DataFrame:
    v1 = pd.read_csv(SCHEMA_V1, low_memory=False).set_index("Column_Name")
    indices = exp.Source_Row_Index.astype(int).tolist()
    rows = []
    for column in qc.columns:
        if column in v1.index:
            old = v1.loc[column]
            old_role = str(old.Prediction_Time_Class)
            role = V1_ROLE_MAP.get(old_role, old_role)
            family = str(old.Scientific_Family)
            reason = str(old.Leakage_Reason) if present(old.Leakage_Reason) else str(old.Notes)
            review = "V1_PRECEDENT_RECONFIRMED"
        else:
            role, family, reason = classify_new(column)
            old_role, review = "NOT_IN_V1", "EXPLICIT_V17_NEW_FIELD_REVIEW"
        assert role in ROLES, (column, role)
        series = qc.loc[indices, column]
        core = column in M2_FEATURES
        rows.append({
            "Column_Name": column, "Data_Type": str(qc[column].dtype), "Scientific_Family": family,
            "Schema_Role": role, "V1_Prediction_Time_Class": old_role,
            "Experimental_Coverage_n": int(series.notna().sum()),
            "Experimental_Coverage_pct": round(100 * series.notna().mean(), 3),
            "CORE_M2": core, "Pilot_M2_Action": "INCLUDE_COMPLETE_CASE_ONLY" if core else "EXCLUDE",
            "Source_Type": "CHEMISTRY_POLICY_SELECTED_ANALYSIS_REPRESENTATION" if core and column.endswith("_at%") else ("DIRECT_SOURCE_FIELD" if core else "SOURCE_OR_QC_METADATA"),
            "Preprocessing": "StandardScaler inside training fold for Logistic/SVC" if core else "Not used in Pilot M2",
            "Potential_Leakage": role.startswith("LEAKAGE_") or role == "TARGET_ONLY",
            "Scientific_Justification": reason, "V2_Review_Status": review,
        })
    schema = pd.DataFrame(rows)
    assert schema.Column_Name.tolist() == qc.columns.tolist() and len(schema) == 596
    return schema


TARGET_COLUMNS = {
    "T1_TRIP": "Effective_TRIP",
    "T2_ANY_TWIP": "T2_ANY_TWIP",
    "T2_FCC_TWIP_STRICT": "T2_FCC_TWIP_STRICT",
}
POOLS = {
    ("T1_TRIP", "ALL_VERIFIED_USABLE"): "Effective_TRIP",
    ("T1_TRIP", "STRICT_DIRECT_EVIDENCE_ONLY"): "T1_TRIP_STRICT_DIRECT",
    ("T2_ANY_TWIP", "ALL_VERIFIED_USABLE"): "T2_ANY_TWIP",
    ("T2_ANY_TWIP", "STRICT_DIRECT_EVIDENCE_ONLY"): "T2_ANY_TWIP_STRICT_DIRECT",
    ("T2_FCC_TWIP_STRICT", "ALL_VERIFIED_USABLE"): "T2_FCC_TWIP_STRICT",
}


def target_semantics(exp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in exp.iterrows():
        for target in TARGET_COLUMNS:
            source_col = "Effective_TRIP" if target == "T1_TRIP" else "Effective_TWIP"
            source_value = row[source_col]
            analysis_value = row.T2_FCC_TWIP_STRICT if target == "T2_FCC_TWIP_STRICT" else source_value
            quality = row.TRIP_Evidence_Quality_Flag if target == "T1_TRIP" else row.TWIP_Evidence_Quality_Flag
            if target == "T2_FCC_TWIP_STRICT" and source_value == 1 and pd.isna(analysis_value):
                decision = "EXCLUDED_NOT_CONVERTED_TO_ZERO_PHASE_INCOMPATIBLE_OR_UNRESOLVED"
            elif pd.isna(source_value):
                decision = "SOURCE_TARGET_NA_PRESERVED"
            else:
                decision = "SOURCE_LABEL_RETAINED"
            rows.append({
                "Paper_ID": row.Paper_ID, "ML_Condition_ID": row.ML_Condition_ID, "Target": target,
                "Source_Target_Field": source_col, "Source_Label": source_value,
                "Analysis_Label": analysis_value, "Evidence_Quality_Flag": quality,
                "TWIP_Phase_Source": row.get("TWIP_Phase"), "TWIP_Phase_Category": row.TWIP_Phase_Category,
                "Analysis_Decision": decision, "Master_Label_Changed": False,
            })
    return pd.DataFrame(rows)


def make_matrix(exp: pd.DataFrame, target: str, target_col: str) -> pd.DataFrame:
    data = exp[exp[target_col].notna() & exp.M2_Complete].copy()
    matrix = pd.DataFrame({
        "Paper_ID": data.Paper_ID, "ML_Condition_ID": data.ML_Condition_ID,
        "Group_ID": data.Effective_Group_ID, "Study_Series_ID": data.Study_Series_ID,
        "Material_Parent_ID": data.Material_Parent_ID, "Alloy_Family_Audit_Key": data.Alloy_Family_Audit_Key,
        "Target": target, "Target_Value": data[target_col].astype(int), "Target_Status": data.Target_Status,
        "Evidence_Quality_Flag": data.TRIP_Evidence_Quality_Flag if target == "T1_TRIP" else data.TWIP_Evidence_Quality_Flag,
        "TWIP_Phase_Category": data.TWIP_Phase_Category, "Composition_Source": data.M2_Composition_Source,
        "Fe_at%": pd.to_numeric(data["M2_Fe_at%"]), "Mn_at%": pd.to_numeric(data["M2_Mn_at%"]),
        "Co_at%": pd.to_numeric(data["M2_Co_at%"]), "Cr_at%": pd.to_numeric(data["M2_Cr_at%"]),
        "Test_T_K": pd.to_numeric(data.M2_Test_T_K), "Strain_rate_s-1": pd.to_numeric(data["M2_Strain_rate_s-1"]),
        "Complete_Case": True, "Imputation_Applied": False, "Resampling_Applied": False,
        "Synthetic_Sample": False,
    })
    assert matrix[M2_FEATURES].notna().all().all() and matrix.ML_Condition_ID.nunique() == len(matrix)
    return matrix.reset_index(drop=True)


def build_matrices(exp: pd.DataFrame) -> tuple[dict[tuple[str, str], pd.DataFrame], pd.DataFrame]:
    matrices = {key: make_matrix(exp, key[0], col) for key, col in POOLS.items()}
    paths = {
        ("T1_TRIP", "ALL_VERIFIED_USABLE"): MODEL_DIR / "TRIP_M2_complete_cases.csv",
        ("T2_ANY_TWIP", "ALL_VERIFIED_USABLE"): MODEL_DIR / "TWIP_ANY_M2_complete_cases.csv",
        ("T2_FCC_TWIP_STRICT", "ALL_VERIFIED_USABLE"): MODEL_DIR / "TWIP_FCC_STRICT_M2_complete_cases.csv",
    }
    for key, path in paths.items():
        matrices[key].to_csv(path, index=False)
    ledger = []
    for target, col in TARGET_COLUMNS.items():
        for _, row in exp.iterrows():
            source_value = row.Effective_TRIP if target == "T1_TRIP" else row.Effective_TWIP
            value, reasons = row[col], []
            if pd.isna(source_value): reasons.append("SOURCE_TARGET_NA")
            elif pd.isna(value): reasons.append("FCC_STRICT_PHASE_EXCLUSION_NOT_ZERO")
            if not row.M2_Complete: reasons.append("M2_INCOMPLETE")
            if row.M2_Composition_Source == "UNAVAILABLE_POLICY_REJECTED": reasons.append("CHEMISTRY_POLICY_REJECTED_RAW_ATOMIC_RATIO")
            ledger.append({
                "Paper_ID": row.Paper_ID, "ML_Condition_ID": row.ML_Condition_ID, "Target": target,
                "Exclusion_Reason": "|".join(reasons) if reasons else "INCLUDED",
                "Missing_Required_Fields": row.M2_Missing_Required_Fields, "Target_Status": row.Target_Status,
                "Group_ID": row.Effective_Group_ID, "Source_Target_Value": source_value,
                "Analysis_Target_Value": value, "M2_Composition_Source": row.M2_Composition_Source,
                "Included": pd.notna(value) and bool(row.M2_Complete), "NA_Converted_To_Zero": False,
            })
    out = pd.DataFrame(ledger)
    out.to_csv(MODEL_DIR / "M2_exclusion_ledger.csv", index=False)
    return matrices, out


def predictor_manifest(schema: pd.DataFrame, exp: pd.DataFrame) -> pd.DataFrame:
    lookup = schema.set_index("Column_Name")
    rows = []
    for feature in M2_FEATURES:
        role = lookup.loc[feature, "Schema_Role"]
        assert role in {"PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"}
        rows.append({
            "Feature_Name": feature, "Schema_Role": role,
            "Source_Type": "CHEMISTRY_POLICY_SELECTED_MEASURED_THEN_NOMINAL" if feature.endswith("_at%") else "DIRECT_SOURCE_NUMERIC",
            "Coverage": int(exp[f"M2_{feature}"].notna().sum()),
            "Coverage_pct": round(100 * exp[f"M2_{feature}"].notna().mean(), 3),
            "Data_Type": "numeric",
            "Preprocessing": "StandardScaler inside training fold for LogisticRegression/SVC; none for Dummy/RandomForest",
            "Scientific_Justification": "Policy-compatible elemental at.% known before loading" if feature.endswith("_at%") else "Direct tensile-test condition known before loading",
            "CORE_M2_Required": True,
        })
    return pd.DataFrame(rows)


def overlap(train: pd.DataFrame, test: pd.DataFrame, column: str) -> str:
    return joined(set(train[column].dropna().astype(str)) & set(test[column].dropna().astype(str)))


def split_row(data: pd.DataFrame, train_idx: np.ndarray, test_idx: np.ndarray, target: str,
              pool: str, design: str, strategy: str, k: int | None, fold: int) -> dict[str, Any]:
    train, test = data.iloc[train_idx], data.iloc[test_idx]
    tc, vc = train.Target_Value.value_counts(), test.Target_Value.value_counts()
    go = overlap(train, test, "Group_ID")
    both_train, both_test = set(train.Target_Value.astype(int)) == {0, 1}, set(test.Target_Value.astype(int)) == {0, 1}
    valid = bool(both_train and both_test and not go)
    return {
        "Target": target, "Evidence_Pool": pool, "Design_ID": design, "Strategy": strategy, "k": k, "Fold": fold,
        "Train_n": len(train), "Test_n": len(test), "Train_Positive_n": int(tc.get(1, 0)),
        "Train_Negative_n": int(tc.get(0, 0)), "Test_Positive_n": int(vc.get(1, 0)),
        "Test_Negative_n": int(vc.get(0, 0)), "Train_Group_n": train.Group_ID.nunique(),
        "Test_Group_n": test.Group_ID.nunique(), "Train_Groups": joined(train.Group_ID), "Test_Groups": joined(test.Group_ID),
        "Group_Overlap": go, "Group_Overlap_n": 0 if not go else len(go.split("|")),
        "Paper_Overlap": overlap(train, test, "Paper_ID"), "Paper_Overlap_n": 0 if not overlap(train, test, "Paper_ID") else len(overlap(train, test, "Paper_ID").split("|")),
        "Study_Series_Overlap": overlap(train, test, "Study_Series_ID"),
        "Material_Parent_Overlap": overlap(train, test, "Material_Parent_ID"),
        "Material_Family_Overlap": overlap(train, test, "Alloy_Family_Audit_Key"),
        "Both_Classes_Train": both_train, "Both_Classes_Test": both_test,
        "M2_Complete": bool(train[M2_FEATURES].notna().all().all() and test[M2_FEATURES].notna().all().all()),
        "Fold_Valid": valid, "Design_Feasible": False, "Selected": False,
        "Rejection_Reason": "" if valid else "CLASS_SUPPORT_OR_GROUP_SEPARATION_FAILURE",
    }


def candidate_designs(data: pd.DataFrame, target: str, pool: str) -> tuple[list[dict[str, Any]], dict[str, list[tuple[np.ndarray, np.ndarray]]]]:
    records, designs = [], {}
    groups, y = data.Group_ID.astype(str).to_numpy(), data.Target_Value.astype(int).to_numpy()
    unique = sorted(set(groups))
    for k in range(2, min(5, len(unique)) + 1):
        design = f"{target}__{pool}__GROUP_KFOLD_K{k}"
        splits = list(GroupKFold(n_splits=k).split(data[M2_FEATURES], y, groups))
        designs[design], start = splits, len(records)
        for fold, (train_idx, test_idx) in enumerate(splits, 1):
            records.append(split_row(data, train_idx, test_idx, target, pool, design, "GROUP_KFOLD", k, fold))
        feasible = all(r["Fold_Valid"] for r in records[start:])
        for r in records[start:]:
            r["Design_Feasible"] = feasible
            if not feasible and r["Fold_Valid"]: r["Rejection_Reason"] = "ANOTHER_FOLD_LACKS_CLASS_SUPPORT"
    feasible = sorted({r["Design_ID"] for r in records if r["Design_Feasible"]}, key=lambda v: int(re.search(r"K(\d+)$", v).group(1)))
    if feasible:
        chosen = feasible[-1]
        for r in records: r["Selected"] = r["Design_ID"] == chosen
        return records, designs
    holdouts = []
    for size in range(1, max(1, len(unique) // 2) + 1):
        for test_groups in itertools.combinations(unique, size):
            mask = np.isin(groups, test_groups); train_idx, test_idx = np.flatnonzero(~mask), np.flatnonzero(mask)
            design = f"{target}__{pool}__GROUPED_HOLDOUT_{hashlib.sha1('|'.join(test_groups).encode()).hexdigest()[:8]}"
            designs[design] = [(train_idx, test_idx)]
            r = split_row(data, train_idx, test_idx, target, pool, design, "DETERMINISTIC_GROUPED_HOLDOUT", None, 1)
            r["Design_Feasible"] = r["Fold_Valid"]; records.append(r)
            if r["Fold_Valid"]: holdouts.append((abs(len(test_idx) / len(data) - .25), design))
    if holdouts:
        chosen = sorted(holdouts)[0][1]
        for r in records: r["Selected"] = r["Design_ID"] == chosen
    return records, designs


def build_splits(matrices: dict[tuple[str, str], pd.DataFrame]):
    records, selected = [], {}
    for (target, pool), data in matrices.items():
        ng = data.loc[data.Target_Value.eq(0), "Group_ID"].nunique()
        pg = data.loc[data.Target_Value.eq(1), "Group_ID"].nunique()
        if data.Target_Value.nunique() < 2 or ng <= 1 or pg <= 1:
            reason = "ONLY_ONE_OR_ZERO_NEGATIVE_GROUPS" if ng <= 1 else "ONLY_ONE_OR_ZERO_POSITIVE_GROUPS" if pg <= 1 else "INSUFFICIENT_CLASS_OR_GROUP_SUPPORT"
            records.append({
                "Target": target, "Evidence_Pool": pool, "Design_ID": f"{target}__{pool}__UNSUPPORTED",
                "Strategy": "NOT_CURRENTLY_VALIDATABLE", "k": pd.NA, "Fold": pd.NA,
                **{c: 0 for c in ["Train_n", "Test_n", "Train_Positive_n", "Train_Negative_n", "Test_Positive_n", "Test_Negative_n", "Train_Group_n", "Test_Group_n"]},
                "Train_Groups": "", "Test_Groups": "", "Group_Overlap": "", "Group_Overlap_n": 0,
                "Paper_Overlap": "", "Paper_Overlap_n": 0, "Study_Series_Overlap": "", "Material_Parent_Overlap": "",
                "Material_Family_Overlap": "", "Both_Classes_Train": False, "Both_Classes_Test": False,
                "M2_Complete": True, "Fold_Valid": False, "Design_Feasible": False, "Selected": False,
                "Rejection_Reason": reason,
            })
            continue
        found, designs = candidate_designs(data, target, pool); records.extend(found)
        for design in {r["Design_ID"] for r in found if r["Selected"]}:
            selected[design] = (data, designs[design])
    candidates = pd.DataFrame(records)
    manifest = []
    for design, (data, splits) in selected.items():
        meta = candidates[candidates.Design_ID.eq(design)].iloc[0]
        for fold, (train_idx, test_idx) in enumerate(splits, 1):
            for assignment, indices in [("TRAIN", train_idx), ("TEST", test_idx)]:
                for pos in indices:
                    row = data.iloc[pos]
                    manifest.append({
                        "Target": meta.Target, "Evidence_Pool": meta.Evidence_Pool, "Design_ID": design,
                        "Strategy": meta.Strategy, "Fold": fold, "Assignment": assignment,
                        "Paper_ID": row.Paper_ID, "ML_Condition_ID": row.ML_Condition_ID, "Group_ID": row.Group_ID,
                        "Study_Series_ID": row.Study_Series_ID, "Material_Parent_ID": row.Material_Parent_ID,
                        "Alloy_Family_Audit_Key": row.Alloy_Family_Audit_Key, "Target_Value": int(row.Target_Value),
                        "M2_Complete": True,
                    })
    return candidates, pd.DataFrame(manifest), selected


def model_factory(model_id: str) -> Pipeline:
    if model_id == MODEL_IDS[0]:
        return Pipeline([("model", DummyClassifier(strategy="most_frequent"))])
    if model_id == MODEL_IDS[1]:
        return Pipeline([("scaler", StandardScaler()), ("model", LogisticRegression(class_weight="balanced", C=1.0, max_iter=5000, random_state=RANDOM_STATE))])
    if model_id == MODEL_IDS[2]:
        return Pipeline([("model", RandomForestClassifier(n_estimators=500, class_weight="balanced_subsample", random_state=RANDOM_STATE, n_jobs=1))])
    if model_id == MODEL_IDS[3]:
        return Pipeline([("scaler", StandardScaler()), ("model", SVC(kernel="rbf", C=1.0, gamma="scale", class_weight="balanced"))])
    raise KeyError(model_id)


def leakage_check(predictors: list[str], schema: pd.DataFrame) -> None:
    assert predictors == M2_FEATURES
    forbidden = ["paper", "doi", "group", "posttest", "post_test", "postfracture", "gnd", "kam", "twin", "trip", "twip", "yield", "uts", "elongation", "sdi", "onset", "provenance", "thermocalc", "computed"]
    assert all(not any(token in feature.lower() for token in forbidden) for feature in predictors)
    roles = schema.set_index("Column_Name").loc[predictors, "Schema_Role"]
    assert roles.isin(["PREDICTOR_SAFE_DIRECT", "PREDICTOR_SAFE_CONDITIONAL"]).all()
    assert not set(predictors) & {"VEC", "delta", "Omega", "entropy", "Atomic_size_misfit_pct"}


def scores(model: Pipeline, x: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(x)[:, list(model.classes_).index(1)]
    if hasattr(model, "decision_function"):
        return np.asarray(model.decision_function(x), float)
    return np.asarray(model.predict(x), float)


def metrics_for(y: np.ndarray, pred: np.ndarray, score: np.ndarray) -> dict[str, Any]:
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    both = len(set(y.astype(int))) == 2
    fraction = float(np.mean(pred == 1))
    return {
        "Accuracy": float(accuracy_score(y, pred)), "Balanced_Accuracy": float(balanced_accuracy_score(y, pred)),
        "MCC": float(matthews_corrcoef(y, pred)),
        "Precision_Class_1": float(precision_score(y, pred, pos_label=1, zero_division=0)),
        "Recall_Class_1": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "Precision_Class_0": float(precision_score(y, pred, pos_label=0, zero_division=0)),
        "Recall_Class_0": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "F1_Class_1": float(f1_score(y, pred, pos_label=1, zero_division=0)),
        "F1_Class_0": float(f1_score(y, pred, pos_label=0, zero_division=0)),
        "ROC_AUC": float(roc_auc_score(y, score)) if both else np.nan,
        "Average_Precision": float(average_precision_score(y, score)) if both else np.nan,
        "Predicted_Positive_Fraction": fraction, "Predicted_Negative_Count": int(np.sum(pred == 0)),
        "True_Negative_Count": int(tn), "False_Positive_Count": int(fp), "True_Positive_Count": int(tp),
        "False_Negative_Count": int(fn), "Positive_Class_Collapse": fraction == 1.0,
        "Failure_Flag": "POSITIVE_CLASS_COLLAPSE" if fraction == 1.0 else "NONE",
    }


def run_models(selected: dict[str, tuple[pd.DataFrame, list[tuple[np.ndarray, np.ndarray]]]],
               candidates: pd.DataFrame, schema: pd.DataFrame):
    leakage_check(M2_FEATURES, schema)
    metric_rows, prediction_rows, confusion_rows = [], [], []
    for design, (data, splits) in selected.items():
        meta = candidates[candidates.Design_ID.eq(design)].iloc[0]
        for fold, (train_idx, test_idx) in enumerate(splits, 1):
            train, test = data.iloc[train_idx], data.iloc[test_idx]
            x_train, x_test = train[M2_FEATURES], test[M2_FEATURES]
            y_train, y_test = train.Target_Value.astype(int).to_numpy(), test.Target_Value.astype(int).to_numpy()
            assert set(y_train) == set(y_test) == {0, 1} and not set(train.Group_ID) & set(test.Group_ID)
            for model_id in MODEL_IDS:
                leakage_check(M2_FEATURES, schema)
                model = model_factory(model_id); model.fit(x_train, y_train)
                pred, score = model.predict(x_test).astype(int), scores(model, x_test)
                values = metrics_for(y_test, pred, score)
                metric_rows.append({
                    "Record_Type": "FOLD", "Statistic": "FOLD", "Target": meta.Target,
                    "Evidence_Pool": meta.Evidence_Pool, "Design_ID": design, "Strategy": meta.Strategy,
                    "Fold": fold, "Model_ID": model_id, "Train_n": len(train), "Test_n": len(test),
                    "Train_Positive_n": int(np.sum(y_train == 1)), "Train_Negative_n": int(np.sum(y_train == 0)),
                    "Test_Positive_n": int(np.sum(y_test == 1)), "Test_Negative_n": int(np.sum(y_test == 0)),
                    "Predictor_n": 6, "Preprocessing_Fit_Within_Fold": True, "Imputation_Applied": False,
                    "Resampling_Applied": False, "Hyperparameter_Search": False, **values,
                    "Positive_Class_Collapse_Fold_n": int(values["Positive_Class_Collapse"]),
                    "Evaluated_Fold_n": 1, "All_Folds_Positive_Class_Collapse": bool(values["Positive_Class_Collapse"]),
                })
                confusion_rows.append({"Scope": "FOLD", "Target": meta.Target, "Evidence_Pool": meta.Evidence_Pool,
                                       "Design_ID": design, "Fold": fold, "Model_ID": model_id,
                                       "TN": values["True_Negative_Count"], "FP": values["False_Positive_Count"],
                                       "FN": values["False_Negative_Count"], "TP": values["True_Positive_Count"]})
                for (_, sample), truth, prediction, value in zip(test.iterrows(), y_test, pred, score):
                    prediction_rows.append({"Target": meta.Target, "Evidence_Pool": meta.Evidence_Pool,
                                            "Design_ID": design, "Fold": fold, "Model_ID": model_id,
                                            "Paper_ID": sample.Paper_ID, "ML_Condition_ID": sample.ML_Condition_ID,
                                            "Group_ID": sample.Group_ID, "True_Label": int(truth),
                                            "Predicted_Label": int(prediction), "Decision_Score_or_Probability": float(value)})
    folds = pd.DataFrame(metric_rows)
    aggregate, numeric = [], [
        "Accuracy", "Balanced_Accuracy", "MCC", "Precision_Class_1", "Recall_Class_1",
        "Precision_Class_0", "Recall_Class_0", "F1_Class_1", "F1_Class_0", "ROC_AUC",
        "Average_Precision", "Predicted_Positive_Fraction", "Predicted_Negative_Count",
        "True_Negative_Count", "False_Positive_Count", "True_Positive_Count", "False_Negative_Count",
    ]
    keys = ["Target", "Evidence_Pool", "Design_ID", "Strategy", "Model_ID"]
    for key, subset in folds.groupby(keys, dropna=False):
        for statistic, op in [("MEAN", "mean"), ("MEDIAN", "median"), ("MINIMUM", "min"), ("MAXIMUM", "max")]:
            row = {"Record_Type": "DESCRIPTIVE_AGGREGATE", "Statistic": statistic, **dict(zip(keys, key)), "Fold": pd.NA,
                   "Predictor_n": 6, "Preprocessing_Fit_Within_Fold": True, "Imputation_Applied": False,
                   "Resampling_Applied": False, "Hyperparameter_Search": False}
            for col in ["Train_n", "Test_n", "Train_Positive_n", "Train_Negative_n", "Test_Positive_n", "Test_Negative_n"] + numeric:
                row[col] = getattr(subset[col], op)()
            row["Positive_Class_Collapse"] = bool(subset.Positive_Class_Collapse.any())
            row["Positive_Class_Collapse_Fold_n"] = int(subset.Positive_Class_Collapse.sum())
            row["Evaluated_Fold_n"] = len(subset)
            row["All_Folds_Positive_Class_Collapse"] = bool(subset.Positive_Class_Collapse.all())
            row["Failure_Flag"] = "POSITIVE_CLASS_COLLAPSE_IN_AT_LEAST_ONE_FOLD" if subset.Positive_Class_Collapse.any() else "NONE"
            aggregate.append(row)
    metrics = pd.concat([folds, pd.DataFrame(aggregate)], ignore_index=True)
    predictions, confusions = pd.DataFrame(prediction_rows), pd.DataFrame(confusion_rows)
    if not predictions.empty:
        pooled = []
        for key, frame in predictions.groupby(["Target", "Evidence_Pool", "Design_ID", "Model_ID"]):
            tn, fp, fn, tp = confusion_matrix(frame.True_Label, frame.Predicted_Label, labels=[0, 1]).ravel()
            pooled.append({"Scope": "ALL_DISJOINT_GROUP_KFOLD_TEST_PARTITIONS", "Target": key[0],
                           "Evidence_Pool": key[1], "Design_ID": key[2], "Fold": pd.NA, "Model_ID": key[3],
                           "TN": tn, "FP": fp, "FN": fn, "TP": tp})
        confusions = pd.concat([confusions, pd.DataFrame(pooled)], ignore_index=True)
    return metrics, predictions, confusions


def negative_audit(exp: pd.DataFrame, matrices, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target, col in TARGET_COLUMNS.items():
        labeled, matrix = exp[exp[col].notna()], matrices[(target, "ALL_VERIFIED_USABLE")]
        source_neg, m2_neg = labeled[labeled[col].eq(0)], matrix[matrix.Target_Value.eq(0)]
        selected = candidates[(candidates.Target == target) & (candidates.Evidence_Pool == "ALL_VERIFIED_USABLE") & candidates.Selected]
        rows.append({
            "Target": target, "Source_Usable_n": len(labeled), "Source_Positive_n": int(labeled[col].eq(1).sum()),
            "Source_Negative_n": len(source_neg), "Source_Negative_Paper_n": source_neg.Paper_ID.nunique(),
            "Source_Negative_Strict_Group_n": source_neg.Effective_Group_ID.nunique(),
            "Source_Negative_Material_Family_n": source_neg.Alloy_Family_Audit_Key.nunique(),
            "M2_Usable_n": len(matrix), "M2_Positive_n": int(matrix.Target_Value.eq(1).sum()),
            "M2_Negative_n": len(m2_neg), "M2_Negative_Paper_n": m2_neg.Paper_ID.nunique(),
            "M2_Negative_Strict_Group_n": m2_neg.Group_ID.nunique(),
            "M2_Negative_Material_Family_n": m2_neg.Alloy_Family_Audit_Key.nunique(),
            "M2_Negative_Papers": joined(m2_neg.Paper_ID), "M2_Negative_Groups": joined(m2_neg.Group_ID),
            "Selected_Validation_Design": joined(selected.Design_ID),
            "Validation_Status": "VALID_GROUPED_PILOT" if not selected.empty else "PILOT_NOT_VALIDATABLE_UNDER_CURRENT_M2",
        })
    return pd.DataFrame(rows)


def evidence_sensitivity(matrices, candidates: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (target, pool), matrix in matrices.items():
        if pool not in {"ALL_VERIFIED_USABLE", "STRICT_DIRECT_EVIDENCE_ONLY"}: continue
        selected = candidates[(candidates.Target == target) & (candidates.Evidence_Pool == pool) & candidates.Selected]
        row = {"Target": target, "Evidence_Pool": pool, "M2_n": len(matrix),
               "Positive_n": int(matrix.Target_Value.eq(1).sum()), "Negative_n": int(matrix.Target_Value.eq(0).sum()),
               "Positive_Group_n": matrix[matrix.Target_Value.eq(1)].Group_ID.nunique(),
               "Negative_Group_n": matrix[matrix.Target_Value.eq(0)].Group_ID.nunique(),
               "Validation_Status": "VALID" if not selected.empty else "NOT_CURRENTLY_VALIDATABLE",
               "Selected_Design_ID": joined(selected.Design_ID)}
        for model in MODEL_IDS:
            mean = metrics[(metrics.Target == target) & (metrics.Evidence_Pool == pool) & (metrics.Model_ID == model) & (metrics.Statistic == "MEAN")]
            for metric in ["MCC", "Balanced_Accuracy", "Recall_Class_0"]:
                row[f"{model}_{metric}_mean"] = np.nan if mean.empty else mean.iloc[0][metric]
        rows.append(row)
    return pd.DataFrame(rows)


def write_qc_tables(source: pd.DataFrame, qc: pd.DataFrame, exp: pd.DataFrame, comp: pd.DataFrame, schema: pd.DataFrame) -> None:
    source_exp = source.loc[exp.Source_Row_Index.astype(int)].reset_index(drop=True)
    pd.DataFrame([
        {"Target": t, "Usable_n": int(source_exp[t].notna().sum()), "Positive_n": int(source_exp[t].eq(1).sum()),
         "Negative_n": int(source_exp[t].eq(0).sum()), "Unresolved_n": int(source_exp[t].isna().sum())}
        for t in ["Effective_TRIP", "Effective_TWIP"]
    ]).to_csv(REPORT_DIR / "TARGET_COVERAGE_V17.csv", index=False)
    pd.DataFrame([
        {"Target": t, "Invalid_n": int((~(source_exp[t].isna() | source_exp[t].isin([0, 1]))).sum()),
         "NA_is_preserved": True, "Source_target_mutated": False, "Status": "PASS"}
        for t in ["Effective_TRIP", "Effective_TWIP"]
    ]).to_csv(REPORT_DIR / "TARGET_INTEGRITY_AUDIT_V17.csv", index=False)
    qc.groupby(["Paper_ID", "QC_V17_Replacement_Status"], dropna=False).size().rename("Row_n").reset_index().to_csv(REPORT_DIR / "LEGACY_REPLACEMENT_AUDIT_V17.csv", index=False)
    pd.DataFrame([
        {"Feature_Name": f, "Present_n": int(exp[f"M2_{f}"].notna().sum()), "Missing_n": int(exp[f"M2_{f}"].isna().sum()),
         "Coverage_pct": round(100 * exp[f"M2_{f}"].notna().mean(), 3), "No_Imputation": True}
        for f in M2_FEATURES
    ]).to_csv(REPORT_DIR / "EXPERIMENTAL_MISSINGNESS_V17.csv", index=False)
    exp.groupby("M2_Composition_Source", dropna=False).size().rename("Condition_n").reset_index().to_csv(REPORT_DIR / "COMPOSITION_AUDIT_V17.csv", index=False)
    micro = ["Grain_size_um", "Recovered_Grain_size_um", "Initial_FCC_fraction", "Recovered_Initial_FCC_fraction", "Initial_HCP_fraction", "Recovered_Initial_HCP_fraction", "Initial_twin_boundary_status"]
    pd.DataFrame([{"Feature_Name": c, "Present_n": int(source_exp[c].notna().sum()), "Coverage_pct": round(100 * source_exp[c].notna().mean(), 3), "Prediction_Time_Status": "PRE_TEST_CANDIDATE_METHOD_GATED"} for c in micro]).to_csv(REPORT_DIR / "INITIAL_MICROSTRUCTURE_AUDIT_V17.csv", index=False)
    sfe_cols = ["Paper_ID", "ML_Condition_ID", "SFE_mJ_m2", "SFE_method", "SFE_status", "SFE_Data_Origin", "SFE_Predictor_Eligibility"]
    source_exp.loc[source_exp[sfe_cols[2:]].notna().any(axis=1), sfe_cols].to_csv(REPORT_DIR / "SFE_METHOD_AUDIT_V17.csv", index=False)
    dg_cols = ["Paper_ID", "ML_Condition_ID", "DeltaG_FCC_HCP_J_mol", "DeltaG_method", "DeltaG_Value_Status", "DeltaG_Data_Origin"]
    source_exp.loc[source_exp[dg_cols[2:]].notna().any(axis=1), dg_cols].to_csv(REPORT_DIR / "DELTAG_AUDIT_V17.csv", index=False)
    prov = source_exp[["Paper_ID", "ML_Condition_ID", "DOI", "Observation_ID"]].copy()
    prov["Evidence_Location_or_Source_File"] = source_exp.Source_location.notna() | source_exp.Source_File.notna()
    prov["Core_Provenance_Complete"] = prov[["Paper_ID", "DOI", "Observation_ID"]].notna().all(axis=1) & prov.Evidence_Location_or_Source_File
    prov.to_csv(REPORT_DIR / "PROVENANCE_COMPLETENESS_V17.csv", index=False)
    pd.DataFrame([{"Paper_ID": "P017", "Exact_Computational_n": len(comp), "Experimental_Training_n": 0,
                   "P018_Experimental_Training_n": 0, "P019_Experimental_Training_n": 0, "Status": "PASS_SEPARATE_DOMAINS"}]).to_csv(REPORT_DIR / "COMPUTATIONAL_DOMAIN_AUDIT_V17.csv", index=False)
    source_exp.groupby("Paper_ID").agg(
        Independent_Experimental_n=("ML_Condition_ID", "size"),
        TRIP_usable_n=("Effective_TRIP", lambda x: int(x.notna().sum())),
        TRIP_positive_n=("Effective_TRIP", lambda x: int(x.eq(1).sum())),
        TRIP_negative_n=("Effective_TRIP", lambda x: int(x.eq(0).sum())),
        TWIP_usable_n=("Effective_TWIP", lambda x: int(x.notna().sum())),
        TWIP_positive_n=("Effective_TWIP", lambda x: int(x.eq(1).sum())),
        TWIP_negative_n=("Effective_TWIP", lambda x: int(x.eq(0).sum())),
    ).reset_index().to_csv(REPORT_DIR / "PAPER_CONTRIBUTION_V17.csv", index=False)
    qc.loc[exp.Source_Row_Index.astype(int), ["Paper_ID", "ML_Condition_ID", "QC_V17_Tier", "QC_V17_Review_Status"]].to_csv(REPORT_DIR / "CONDITION_QC_TIER_V17.csv", index=False)
    pd.DataFrame([
        {"Priority": "P1", "Issue": "TRIP_NEGATIVE_GROUP_SCARCITY_AFTER_M2", "Status": "OPEN", "Scientific_Impact": "Prevents meaningful grouped TRIP validation"},
        {"Priority": "P1", "Issue": "TWIP_PHASE_HETEROGENEITY", "Status": "OPEN_CONTROLLED_BY_SENSITIVITY", "Scientific_Impact": "ANY-TWIP mixes FCC and HCP-epsilon semantics"},
        {"Priority": "P2", "Issue": "CORE_M2_MISSINGNESS", "Status": "OPEN_COMPLETE_CASE_EXCLUSION", "Scientific_Impact": "Reduces conditions and groups"},
        {"Priority": "P2", "Issue": "MATERIAL_FAMILY_CROSS_PAPER_OVERLAP", "Status": "AUDITED_NOT_FULLY_CONTROLLED", "Scientific_Impact": "Paper grouping may retain family similarity"},
    ]).to_csv(REPORT_DIR / "GLOBAL_QC_ISSUES_V17.csv", index=False)
    schema[["Column_Name", "Scientific_Family", "Schema_Role", "Experimental_Coverage_n", "Experimental_Coverage_pct", "CORE_M2", "Pilot_M2_Action"]].to_csv(REPORT_DIR / "FEATURE_COVERAGE_V17.csv", index=False)
    schema.groupby(["Scientific_Family", "Schema_Role"], dropna=False).agg(Field_n=("Column_Name", "size"), CORE_M2_n=("CORE_M2", "sum")).reset_index().to_csv(REPORT_DIR / "FEATURE_COVERAGE_SUMMARY_V17.csv", index=False)
    exp[["Paper_ID", "ML_Condition_ID", "M2_Composition_Source", "M2_Composition_Selection_Note", "M2_Fe_at%", "M2_Mn_at%", "M2_Co_at%", "M2_Cr_at%", "M2_Missing_Required_Fields"]].assign(
        Local_EDS_Promoted_to_Bulk=False, P022_Raw_Atomic_Ratio_Normalized=False, Missing_Element_Filled_with_Zero=False
    ).to_csv(REPORT_DIR / "CHEMISTRY_SOURCE_AUDIT_V17.csv", index=False)
    contribution = exp.groupby(["Study_Series_ID", "Material_Parent_ID", "Effective_Group_ID", "Alloy_Family_Audit_Key"], dropna=False).size().rename("Independent_Experimental_n").reset_index()
    contribution.to_csv(REPORT_DIR / "STUDY_MATERIAL_CONTRIBUTION_V17.csv", index=False)


def md_table(frame: pd.DataFrame, columns: list[str] | None = None) -> str:
    if columns: frame = frame[columns]
    if frame.empty: return "_No rows._"
    frame = frame.astype(object).where(frame.notna(), "NA")
    clean = lambda value: str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(map(clean, frame.columns)) + " |", "| " + " | ".join(["---"] * len(frame.columns)) + " |"]
    lines.extend("| " + " | ".join(clean(v) for v in row) + " |" for row in frame.to_numpy())
    return "\n".join(lines)


def value(frame: pd.DataFrame, model: str, metric: str) -> float:
    row = frame[(frame.Model_ID == model) & (frame.Statistic == "MEAN")]
    return float(row.iloc[0][metric]) if not row.empty else np.nan


def write_reports(source, qc, exp, comp, schema, matrices, candidates, negative, metrics, sensitivity):
    trip, twip, fcc = matrices[("T1_TRIP", "ALL_VERIFIED_USABLE")], matrices[("T2_ANY_TWIP", "ALL_VERIFIED_USABLE")], matrices[("T2_FCC_TWIP_STRICT", "ALL_VERIFIED_USABLE")]
    source_counts = f"TRIP {int(exp.Effective_TRIP.notna().sum())} ({int(exp.Effective_TRIP.eq(1).sum())}/{int(exp.Effective_TRIP.eq(0).sum())}); TWIP {int(exp.Effective_TWIP.notna().sum())} ({int(exp.Effective_TWIP.eq(1).sum())}/{int(exp.Effective_TWIP.eq(0).sum())}); joint {int(exp[['Effective_TRIP','Effective_TWIP']].notna().all(axis=1).sum())}"
    (REPORT_DIR / "GLOBAL_DATASET_QC_V17_REFRESH.md").write_text(f"""# Global Dataset QC V17 Refresh

V17 remains the immutable scientific source: **234 rows x 584 columns**. The **234 x 596** QC snapshot preserves every original cell, row/column order, and NA-mask, then appends twelve QC-only fields. Source SHA-256: `{sha256(SOURCE)}`.

The refreshed architecture contains **69 independent experimental conditions** and **12 exact P017 computational conditions**. P017/P018/P019 contribute zero experimental training rows. Target support is {source_counts}.

Replacement/duplicate, target-integrity, missingness, chemistry, initial microstructure, SFE, DeltaG, provenance, domain, contribution, tier/issue, and feature-coverage audits are versioned in `reports/`. Measured bulk chemistry is preferred when valid; otherwise explicit nominal/source chemistry may be selected in analysis metadata. Local EDS is never bulk, P022 atomic ratios are not normalized, missing elements remain missing, and only exact numeric test temperature is eligible.

The main limitations are complete-case attrition, one surviving TRIP-negative M2 group, TWIP phase heterogeneity, and audited cross-paper material-family overlap.
""", encoding="utf-8")
    roles = schema.Schema_Role.value_counts().rename_axis("Schema_Role").reset_index(name="Field_n")
    critical = schema[schema.Column_Name.isin(M2_FEATURES + ["TWIP_Phase", "Postfracture_HCP_fraction", "PostTest_FCC_fraction", "PostTest_HCP_fraction", "GND_density_m-2", "PostTest_Twin_Evidence", "TRIP_Onset_True_Stress_MPa", "WH_Rate_at_Slope_Change_MPa", "SDI_MPa", "Engineering_YS_MPa", "ThermoCalc_Software", "ThermoCalc_Database"])][["Column_Name", "Schema_Role", "CORE_M2", "Scientific_Justification"]]
    (REPORT_DIR / "FEATURE_SCHEMA_V2_AUDIT.md").write_text(f"""# Feature Schema V2 Audit

Feature Schema V2 classifies all **596** V17-QC fields with no unresolved role. V1 policy is retained and every post-V1/P020-P023 field receives explicit review.

{md_table(roles)}

Pilot M2 contains exactly six numeric predictors: `{', '.join(M2_FEATURES)}`. All are required; no imputation or inferred zero is allowed. Scaling occurs only inside Logistic/SVC training folds.

{md_table(critical)}

Mechanical outcomes, post-test phases/twins/GND/KAM, target evidence, onset/work-hardening, identifiers/groups/provenance, and computational context are excluded. Thermo-Calc remains model context; local EDS is never promoted to bulk chemistry.
""", encoding="utf-8")
    neg = negative[["Target", "Source_Negative_n", "Source_Negative_Paper_n", "Source_Negative_Strict_Group_n", "M2_Negative_n", "M2_Negative_Strict_Group_n", "M2_Negative_Material_Family_n", "Validation_Status"]]
    (REPORT_DIR / "VALIDATION_ARCHITECTURE_V2.md").write_text(f"""# Validation Architecture V2

The task is pre-deformation experimental Effective_TRIP/TWIP prediction using complete-case M2 only. P017 remains computational-only. `Leakage_Group_Strict` is primary with `PAPER::<Paper_ID>` fallback; reported partitions require both classes and zero strict-group overlap. Paper, study, material-parent, and formula/alloy-family overlap are audited but never predictors.

{md_table(neg)}

`T2_ANY_TWIP` preserves every usable label. `T2_FCC_TWIP_STRICT` excludes HCP/epsilon and unresolved-positive semantics as NA rather than zero. Direct-evidence filtering is analysis-only. One-or-zero positive/negative-group targets are declared not validatable before fitting. This pilot is not publication-level validation.
""", encoding="utf-8")
    selected = candidates[candidates.Selected][["Target", "Evidence_Pool", "Design_ID", "Strategy", "Fold", "Train_n", "Test_n", "Train_Positive_n", "Train_Negative_n", "Test_Positive_n", "Test_Negative_n", "Train_Group_n", "Test_Group_n", "Group_Overlap_n", "Paper_Overlap_n", "Material_Family_Overlap"]]
    rejected = candidates[~candidates.Design_Feasible].groupby(["Target", "Evidence_Pool", "Rejection_Reason"], dropna=False).size().rename("Candidate_Partition_n").reset_index()
    (REPORT_DIR / "SPLIT_DESIGN_V2_AUDIT.md").write_text(f"""# Split Design V2 Audit

## Selected partitions

{md_table(selected)}

Every selected fold contains both classes, is complete-case M2, and has zero strict-group/paper overlap. Material-family overlap is reported. No random-row split, forced LOPO, or forced k=5 exists.

## Rejected/unsupported candidates

{md_table(rejected)}
""", encoding="utf-8")
    primary = metrics[(metrics.Target == "T2_ANY_TWIP") & (metrics.Evidence_Pool == "ALL_VERIFIED_USABLE")]
    means = primary[primary.Statistic == "MEAN"][["Model_ID", "Balanced_Accuracy", "MCC", "Recall_Class_0", "Recall_Class_1", "Predicted_Positive_Fraction", "Positive_Class_Collapse_Fold_n", "Evaluated_Fold_n"]]
    folds = primary[primary.Record_Type == "FOLD"][["Fold", "Model_ID", "Test_Positive_n", "Test_Negative_n", "True_Negative_Count", "False_Positive_Count", "True_Positive_Count", "False_Negative_Count", "Balanced_Accuracy", "MCC", "Recall_Class_0", "Recall_Class_1", "Predicted_Positive_Fraction", "Failure_Flag"]]
    all_sens = sensitivity[(sensitivity.Target == "T2_ANY_TWIP") & (sensitivity.Evidence_Pool == "ALL_VERIFIED_USABLE")].iloc[0]
    strict_sens = sensitivity[(sensitivity.Target == "T2_ANY_TWIP") & (sensitivity.Evidence_Pool == "STRICT_DIRECT_EVIDENCE_ONLY")].iloc[0]
    logistic_all = all_sens["M1_LOGISTIC_BALANCED_MCC_mean"]
    logistic_strict = strict_sens["M1_LOGISTIC_BALANCED_MCC_mean"]
    collapse = means.apply(lambda r: f"{r.Model_ID} {int(r.Positive_Class_Collapse_Fold_n)}/{int(r.Evaluated_Fold_n)} folds", axis=1).str.cat(sep="; ")
    (REPORT_DIR / "PILOT_ML_V1_REPORT.md").write_text(f"""# Controlled Pilot ML V1 Report

> This is a pipeline-sanity pilot, not publication-ready performance or evidence of reliable generalization to new HEAs.

1. Independent experimental conditions: **69**.
2. Usable labels: **TRIP 37; ANY-TWIP 36; joint 30**.
3. M2 complete cases: **TRIP {len(trip)}; ANY-TWIP {len(twip)}; FCC-strict {len(fcc)}**.
4. M2 classes: TRIP {int(trip.Target_Value.eq(1).sum())}/{int(trip.Target_Value.eq(0).sum())}; ANY-TWIP {int(twip.Target_Value.eq(1).sum())}/{int(twip.Target_Value.eq(0).sum())}; FCC-strict {int(fcc.Target_Value.eq(1).sum())}/{int(fcc.Target_Value.eq(0).sum())} positive/negative.
5. Negative strict groups: TRIP {trip[trip.Target_Value.eq(0)].Group_ID.nunique()}; ANY-TWIP {twip[twip.Target_Value.eq(0)].Group_ID.nunique()}; FCC-strict {fcc[fcc.Target_Value.eq(0)].Group_ID.nunique()}.
6. Valid primary design: `T2_ANY_TWIP__ALL_VERIFIED_USABLE__GROUP_KFOLD_K3`; unsupported targets are not forced.
7. Only balanced Logistic Regression beats the dummy on both mean MCC and balanced accuracy.
8. Positive-only collapse: {collapse}.
9. Negative-class recall is reported below for every fold/model; primary means are Dummy 0.000, Logistic 0.333, Random Forest 0.000, and SVC 0.000.
10. Primary mean MCC is Dummy 0.000, Logistic 0.211, Random Forest 0.000, and SVC -0.149.
11. Fold results are highly variable; means do not hide fold rows or min/median/max aggregates.
12. TRIP is `PILOT_NOT_VALIDATABLE_UNDER_CURRENT_M2` because one negative group survives.
13. ANY-TWIP has a mean above-dummy Logistic result, but it collapses in multiple folds and does not establish robust learnability.
14. FCC-only TWIP is `NOT_CURRENTLY_VALIDATABLE` because only one positive strict group survives.
15. Direct-only filtering removes one medium/author-attributed positive but does not materially change Logistic mean MCC ({logistic_all:.3f} to {logistic_strict:.3f}); it does not resolve fold collapse or establish robustness.
16. Leakage assertions find zero forbidden predictors; preprocessing is fit inside each training fold.
17. The largest limitation is scarce, concentrated negative-group support after complete-case filtering.
18. Next collect direct condition-level TRIP/TWIP negatives with phase resolution, policy-valid Fe/Mn/Co/Cr chemistry, exact numeric test temperature/rate, distinct strict groups/material families, and before/after microscopy/diffraction. Add independent FCC-TWIP-positive groups for strict-phase validation.

## Primary mean diagnostics

{md_table(means)}

## Primary fold diagnostics and confusion counts

{md_table(folds)}

## Evidence sensitivity

{md_table(sensitivity[sensitivity.Target == 'T2_ANY_TWIP'])}

The only above-dummy mean result is group/evidence-sensitive. Random Forest and the dummy collapse to positive in every primary fold. The pilot answers pipeline feasibility and exposes data gaps; it does not select a publication model.
""", encoding="utf-8")


def validate(source, qc, exp, comp, schema, matrices, candidates, manifest, metrics, predictions):
    assert source.shape == (234, 584) and qc.shape == (234, 596)
    pd.testing.assert_frame_equal(qc[source.columns], source, check_dtype=False)
    assert qc[source.columns].isna().equals(source.isna())
    assert len(exp) == 69 and exp.Effective_TRIP.notna().sum() == 37 and exp.Effective_TWIP.notna().sum() == 36
    assert exp[["Effective_TRIP", "Effective_TWIP"]].notna().all(axis=1).sum() == 30
    assert len(comp) == 12 and comp.Paper_ID.eq("P017").all()
    assert not exp.Paper_ID.isin(["P017", "P018", "P019"]).any()
    assert schema.Column_Name.tolist() == qc.columns.tolist() and set(schema.Schema_Role) <= ROLES
    leakage_check(M2_FEATURES, schema)
    assert exp[exp.Paper_ID.eq("P022")].M2_Composition_Source.eq("UNAVAILABLE_POLICY_REJECTED").all()
    hcp = exp.ML_Condition_ID.isin(HCP_TWIP_IDS)
    assert exp.loc[hcp, "TWIP_Phase_Category"].eq("HCP_EPSILON").all() and exp.loc[hcp, "T2_FCC_TWIP_STRICT"].isna().all()
    for matrix in matrices.values():
        assert matrix[M2_FEATURES].notna().all().all() and matrix.Complete_Case.all()
        assert not matrix.Imputation_Applied.any() and not matrix.Resampling_Applied.any() and not matrix.Synthetic_Sample.any()
        assert matrix.ML_Condition_ID.nunique() == len(matrix)
    chosen = candidates[candidates.Selected]
    assert not chosen.empty and chosen.Fold_Valid.all() and chosen.Group_Overlap_n.eq(0).all()
    assert chosen.Both_Classes_Train.all() and chosen.Both_Classes_Test.all() and chosen.Strategy.ne("RANDOM_ROW_SPLIT").all()
    assert not manifest.empty and manifest.M2_Complete.all()
    fold_metrics = metrics[metrics.Record_Type.eq("FOLD")]
    assert set(fold_metrics.Model_ID) == set(MODEL_IDS)
    assert metrics.Imputation_Applied.eq(False).all() and metrics.Resampling_Applied.eq(False).all() and metrics.Hyperparameter_Search.eq(False).all()
    for keys, frame in predictions.groupby(["Target", "Evidence_Pool", "Design_ID", "Fold", "Model_ID"]):
        expected = metrics_for(frame.True_Label.to_numpy(), frame.Predicted_Label.to_numpy(), frame.Decision_Score_or_Probability.to_numpy())
        stored = fold_metrics[(fold_metrics.Target == keys[0]) & (fold_metrics.Evidence_Pool == keys[1]) &
                              (fold_metrics.Design_ID == keys[2]) & (fold_metrics.Fold == keys[3]) &
                              (fold_metrics.Model_ID == keys[4])].iloc[0]
        assert np.isclose(expected["Balanced_Accuracy"], stored.Balanced_Accuracy)
        assert np.isclose(expected["MCC"], stored.MCC)
    assert sha256(SOURCE) == SOURCE_EXPECTED_SHA256


def main() -> None:
    for directory in [MODEL_DIR, TABLE_DIR, REPORT_DIR, SPLIT_CANDIDATES.parent, SCHEMA_V2.parent]:
        directory.mkdir(parents=True, exist_ok=True)
    before = sha256(SOURCE)
    source = pd.read_csv(SOURCE, low_memory=False); preflight(source)
    exp, comp = build_experimental_index(source), build_computational_index(source)
    qc = build_qc(source, exp, comp)
    schema = build_schema(qc, exp)
    semantics = target_semantics(exp)
    matrices, exclusions = build_matrices(exp)
    predictors = predictor_manifest(schema, exp)
    candidates, manifest, selected = build_splits(matrices)
    metrics, predictions, confusions = run_models(selected, candidates, schema)
    negative = negative_audit(exp, matrices, candidates)
    sensitivity = evidence_sensitivity(matrices, candidates, metrics)

    qc.to_csv(QC_PATH, index=False); exp.to_csv(EXP_PATH, index=False); comp.to_csv(COMP_PATH, index=False)
    schema.to_csv(SCHEMA_V2, index=False); candidates.to_csv(SPLIT_CANDIDATES, index=False); manifest.to_csv(SPLIT_MANIFEST, index=False)
    predictors.to_csv(MODEL_DIR / "M2_predictor_manifest.csv", index=False)
    semantics.to_csv(TABLE_DIR / "pilot_v1_target_semantics_audit.csv", index=False)
    negative.to_csv(TABLE_DIR / "pilot_v1_negative_class_audit.csv", index=False)
    metrics.to_csv(TABLE_DIR / "pilot_v1_model_metrics.csv", index=False)
    predictions.to_csv(TABLE_DIR / "pilot_v1_predictions.csv", index=False)
    confusions.to_csv(TABLE_DIR / "pilot_v1_confusion_matrices.csv", index=False)
    sensitivity.to_csv(TABLE_DIR / "pilot_v1_evidence_sensitivity.csv", index=False)
    write_qc_tables(source, qc, exp, comp, schema)
    write_reports(source, qc, exp, comp, schema, matrices, candidates, negative, metrics, sensitivity)
    validate(source, qc, exp, comp, schema, matrices, candidates, manifest, metrics, predictions)
    assert sha256(SOURCE) == before
    print(json.dumps({
        "source_shape": list(source.shape), "qc_shape": list(qc.shape), "experimental_n": len(exp),
        "computational_n": len(comp), "trip_usable_n": int(exp.Effective_TRIP.notna().sum()),
        "twip_usable_n": int(exp.Effective_TWIP.notna().sum()),
        "trip_m2_n": len(matrices[("T1_TRIP", "ALL_VERIFIED_USABLE")]),
        "twip_m2_n": len(matrices[("T2_ANY_TWIP", "ALL_VERIFIED_USABLE")]),
        "fcc_twip_m2_n": len(matrices[("T2_FCC_TWIP_STRICT", "ALL_VERIFIED_USABLE")]),
        "strict_twip_m2_n": len(matrices[("T2_ANY_TWIP", "STRICT_DIRECT_EVIDENCE_ONLY")]),
        "selected_designs": sorted(selected), "model_fold_rows": int(metrics.Record_Type.eq("FOLD").sum()),
    }, indent=2))


if __name__ == "__main__":
    main()
