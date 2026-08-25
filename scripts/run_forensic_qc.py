"""Reproducible, conservative forensic QC for the 19-paper TRIP/TWIP data.

The script reads the immutable workbooks directly, freezes the existing merge,
and writes review artefacts plus a post-*safe*-QC CSV.  It intentionally does
not infer scientific labels, impute values, remove incomplete rows, or train a
model.  Heuristic classifications are explicitly marked for paper review.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import run_pipeline_stdlib as base

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
TABLES = ROOT / "reports/tables"

MECH_FIELDS = ["Paper_ID", "DOI", "Condition_ID", "Experiment_Group_ID", "Row_Type",
               "TRIP", "TWIP", "Slip", "Dominant_mechanism", "Evidence_TRIP",
               "Evidence_TWIP", "Deformation_stage", "Source_location", "Label_confidence"]
MECH_ADDED = ["Problem_Type", "Problem_Description", "Likely_Root_Cause",
              "Suggested_Action", "Can_Auto_Fix", "Requires_Paper_Review"]
FEATURES = ["Test_T_K", "Strain_rate_s-1", "Grain_size_um", "SFE_mJ_m2", "SFE_method",
            "DeltaG_FCC_HCP_J_mol", "Initial_FCC_fraction", "Initial_HCP_fraction",
            "YS_MPa", "UTS_MPa", "Elongation_pct"]
MISSING_FOCUS = ["Grain_size_um", "SFE_mJ_m2", "DeltaG_FCC_HCP_J_mol",
                 "Initial_FCC_fraction", "Initial_HCP_fraction", "Strain_rate_s-1",
                 "Test_T_K", "Homogenization_T_K", "Homogenization_time_h",
                 "Hot_rolling_T_K", "Hot_rolling_reduction_pct",
                 "Cold_rolling_reduction_pct", "Annealing_T_K", "Annealing_time_min"]


def write(path, rows, fields):
    base.write_csv(path, rows, fields)


def load_sources():
    loaded = []
    for name in base.FILES:
        path = base.RAW / name
        sheet, rows = base.extraction(path)
        loaded.append((path, sheet, rows))
    return loaded


def merge_source_rows(loaded):
    """Recreate the baseline merge while retaining source columns for analysis."""
    canonical = list(loaded[0][2][0])
    merged = []
    for path, sheet, rows in loaded:
        columns = list(rows[0])
        aliases = {a: b for a, b in base.ALIASES.items() if a in columns and b not in columns}
        extras = [c for c in columns if c not in canonical and c not in aliases]
        for source in rows:
            out = {c: source.get(c, "") for c in canonical}
            for old, new in aliases.items():
                out[new] = source.get(old, "")
            out["Unmapped_Fields"] = json.dumps(
                {c: source[c] for c in extras if source.get(c, "") != ""},
                ensure_ascii=False, sort_keys=True,
            ) if extras else ""
            out["Source_File"], out["Source_Sheet"] = path.name, sheet
            out["Schema_Mapping_Review"] = " | ".join(f"{a} -> {b}" for a, b in aliases.items())
            out["_source"] = source
            merged.append(out)
    return canonical, merged


def role(row):
    text = " ".join([row.get("Row_Type", ""), row.get("Dominant_mechanism", ""),
                     row.get("Notes", "")]).lower()
    stage = row.get("Deformation_stage", "").lower()
    if "molecular-dynamics" in text or re.search(r"\bmd\b", text):
        return "COMPUTATIONAL_MD", "Row type explicitly identifies molecular dynamics", "HIGH"
    if "experimental" in text and any(x in text for x in ("dft", "calphad", "thermodynamic", "md-derived", "magnetism")):
        return "HYBRID_EXPERIMENTAL_COMPUTATIONAL", "Row type explicitly combines experimental and computational evidence", "HIGH"
    if "multiscale computational" in text:
        return "COMPUTATIONAL_OTHER", "Row type explicitly identifies a multiscale computational/model condition", "HIGH"
    if "dft" in text:
        return "COMPUTATIONAL_DFT", "Row type explicitly identifies DFT", "HIGH"
    if "calphad" in text:
        return "COMPUTATIONAL_CALPHAD", "Row type explicitly identifies CALPHAD", "HIGH"
    if "reference comparator" in text or "descriptor" in text or "thermodynamic design" in stage:
        return "EXPERIMENTAL_SUMMARY", "Reference/design descriptor is not an independent tested condition", "MEDIUM"
    if any(x in text for x in ("interrupted strain", "local-strain", "in-situ strain-resolved")) or re.search(r"stage [ivx]+", stage):
        return "EXPERIMENTAL_REPEATED_STAGE", "Explicit local/interrupted/in-situ deformation-stage observation", "HIGH"
    if "experimental" in text or "tensile condition" in text or "processing/tensile" in text:
        return "EXPERIMENTAL_INDEPENDENT", "Row type explicitly identifies an experimental tensile condition", "HIGH"
    return "UNRESOLVED", "No source-supported experimental or computational role token", "LOW"


def mechanism_problem(row, assigned):
    missing = [x for x in ("TRIP", "TWIP") if not row.get(x, "").strip()]
    mechanism = row.get("Dominant_mechanism", "")
    ambiguous_syntax = ";" in mechanism or "/" in mechanism
    if not (missing or ambiguous_syntax):
        return None
    evidence = " ".join([row.get("Evidence_TRIP", ""), row.get("Evidence_TWIP", ""), mechanism]).lower()
    if assigned.startswith("COMPUTATIONAL"):
        return ("G", "Computational/model row is in the mechanism-flag set",
                "Computational evidence was audited with experimental labels",
                "Retain row; separate computational targets and review label semantics", "False", "True")
    if assigned == "EXPERIMENTAL_REPEATED_STAGE":
        return ("H", "Repeated deformation-stage observation has missing or compound mechanism syntax",
                "Stage-resolved observations share a parent experiment but mechanisms evolve with strain",
                "Retain stage row and verify stage-specific labels in the cited source", "False", "True")
    if assigned == "EXPERIMENTAL_SUMMARY":
        return ("I", "Reference/design/summary row is mixed with condition-level mechanism rows",
                "Row granularity does not support a condition-level binary target",
                "Retain as provenance; exclude from condition-level target analysis unless paper verifies it", "False", "True")
    if missing and any(x in evidence for x in ("not explicitly assigned", "not forced", "verify")):
        return ("E", "Binary label intentionally unresolved despite contextual mechanism text",
                "Available extraction text does not support an unambiguous condition-specific label",
                "Inspect the cited paper location; preserve NA meanwhile", "False", "True")
    if missing and evidence.strip():
        return ("B", "Binary label is missing while textual evidence is present",
                "Evidence was extracted without a defensible binary condition-level assignment",
                "Review evidence against target definition; do not infer from suggestive wording", "False", "True")
    if missing:
        return ("A", "Mechanism label and supporting evidence are missing",
                "Mechanism was not reported or has not yet been extracted",
                "Inspect paper figures/tables/text and retain NA until supported", "False", "True")
    return ("E", "Dominant mechanism uses compound '/' or ';' terminology",
            "Multiple co-active or stage-dependent mechanisms are represented in free text",
            "Keep binary labels; manually verify that each refers to deformation at this condition", "False", "True")


def schema_review(loaded, canonical):
    rows = []
    safe = {"Data_role": "Row_Type", "Composition_basis_original": "Composition_basis",
            "Image_modalities": "Characterization_methods"}
    meanings = {
        "ISFE_DFT_0K_mJ_m2": "Intrinsic stacking-fault energy calculated by DFT at 0 K",
        "USFE_mJ_m2": "Unstable stacking-fault energy", "UMFE_mJ_m2": "Unstable martensite-fault energy",
        "UTFE_mJ_m2": "Unstable twin-fault energy", "Precipitate_types": "Reported precipitate identity",
        "Initial_alpha_martensite_area_fraction": "Initial alpha-martensite area fraction",
        "HDI_strengthening_MPa": "Hetero-deformation-induced strengthening contribution",
        "Magnetic_state_descriptor": "Magnetic state description",
        "Magnetic_critical_temperature_K": "Magnetic critical temperature",
        "VEC": "Reported valence-electron concentration",
    }
    for path, sheet, source_rows in loaded:
        for field in source_rows[0]:
            if field in canonical:
                continue
            values = [r.get(field, "") for r in source_rows if r.get(field, "") != ""]
            if field in safe:
                status, target, rec, risk, manual = "SAFE_ALIAS", safe[field], f"Map exactly to {safe[field]}", "LOW", "False"
            elif field.startswith("Derived_"):
                status, target, rec, risk, manual = "DUPLICATE_INFORMATION", "", "Retain provenance; recompute only from documented inputs", "MEDIUM", "True"
            elif field in meanings or field in {"USFE_mJ_m2"}:
                status, target, rec, risk, manual = "NEW_SCIENTIFIC_FEATURE", "", "Add as a distinct provenance-preserving feature; do not collapse into SFE", "HIGH if collapsed", "True"
            else:
                status, target, rec, risk, manual = "UNMAPPED", "", "Retain without coercion pending scientific schema review", "UNKNOWN", "True"
            rows.append({"Source_Workbook": path.name, "Source_Sheet": sheet, "Original_Field": field,
                         "Canonical_Field_if_known": target, "Mapping_Status": status,
                         "Number_of_nonmissing_values": len(values),
                         "Example_values": " | ".join(dict.fromkeys(map(str, values[:3]))),
                         "Scientific_meaning": meanings.get(field, "Derived descriptor" if field.startswith("Derived_") else "See source extraction header"),
                         "Recommended_mapping": rec, "Risk_of_information_loss": risk,
                         "Requires_manual_review": manual})
    return rows


def numeric_status(field, value, row):
    try:
        number = float(value)
    except ValueError:
        return "NONNUMERIC", "Value is not unambiguously numeric", True
    if field in ("Initial_FCC_fraction", "Initial_HCP_fraction"):
        if 0 <= number <= 1:
            return "CONSISTENT", "Fraction represented on 0–1 scale", False
        if 1 < number <= 100:
            return "POSSIBLE_PERCENT", "Could be percent rather than fraction; do not convert without source confirmation", True
        return "OUT_OF_RANGE", "Outside both fraction and percent ranges", True
    if field == "Strain_rate_s-1" and number <= 0:
        return "OUT_OF_RANGE", "Strain rate must be positive", True
    if field in {"Test_T_K", "Grain_size_um", "YS_MPa", "UTS_MPa", "Elongation_pct"} and number < 0:
        return "OUT_OF_RANGE", "Negative physical value", True
    method = row.get("SFE_method", "") if field == "SFE_mJ_m2" else row.get("DeltaG_method", "") if field == "DeltaG_FCC_HCP_J_mol" else ""
    return "CONSISTENT", (f"Numeric value retained with method: {method}" if method else "Numeric value in canonical declared unit"), False


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    current = INTERIM / "master_19papers_raw.csv"
    frozen = INTERIM / "master_19papers_raw_pre_qc.csv"
    if not frozen.exists():
        shutil.copyfile(current, frozen)
    loaded = load_sources()
    canonical, rows = merge_source_rows(loaded)
    if len(rows) != 98:
        raise RuntimeError(f"Expected 98 source rows, found {len(rows)}")

    role_rows, roles = [], []
    for row in rows:
        assigned, reason, confidence = role(row); roles.append(assigned)
        role_rows.append({"Paper_ID": row["Paper_ID"], "Condition_ID": row["Condition_ID"],
                          "Experiment_Group_ID": row["Experiment_Group_ID"], "Original_Row_Type": row["Row_Type"],
                          "Assigned_Row_Role": assigned, "Reason": reason, "Confidence": confidence,
                          "Requires_manual_review": str(assigned == "UNRESOLVED")})
    write(TABLES / "row_role_review.csv", role_rows, list(role_rows[0]))

    mech = []
    for row, assigned in zip(rows, roles):
        problem = mechanism_problem(row, assigned)
        if problem:
            mech.append({**{k: row.get(k, "") for k in MECH_FIELDS}, **dict(zip(MECH_ADDED, problem))})
    write(TABLES / "mechanism_review.csv", mech, MECH_FIELDS + MECH_ADDED)

    schema = schema_review(loaded, canonical)
    write(TABLES / "schema_forensic_review.csv", schema, list(schema[0]))

    groups = defaultdict(list)
    for row, assigned in zip(rows, roles): groups[row["Experiment_Group_ID"]].append((row, assigned))
    group_rows = []
    ambiguous_groups = 0
    for gid, items in groups.items():
        rs = [x[0] for x in items]; rr = [x[1] for x in items]
        tvals = sorted({r["TRIP"] for r in rs if r["TRIP"] != ""}); wvals = sorted({r["TWIP"] for r in rs if r["TWIP"] != ""})
        conflict = len(tvals) > 1 or len(wvals) > 1
        varying_stage = len({r["Deformation_stage"] for r in rs if r["Deformation_stage"]}) > 1
        varying_temp = len({r["Test_T_K"] for r in rs if r["Test_T_K"]}) > 1
        if conflict: ambiguous_groups += 1
        why = []
        if conflict and varying_stage: why.append("labels vary with deformation stage")
        if conflict and varying_temp: why.append("labels vary with test temperature")
        if conflict and not why: why.append("group may be too coarse; processing/condition distinction needs paper review")
        independent = len(rs) == 1 and rr[0] == "EXPERIMENTAL_INDEPENDENT"
        group_rows.append({"Experiment_Group_ID": gid, "Paper_ID": " | ".join(sorted({r['Paper_ID'] for r in rs})),
            "number_of_rows": len(rs), "row_roles": " | ".join(sorted(set(rr))),
            "test_temperatures": " | ".join(sorted({r['Test_T_K'] for r in rs if r['Test_T_K']})),
            "strain_rates": " | ".join(sorted({r['Strain_rate_s-1'] for r in rs if r['Strain_rate_s-1']})),
            "compositions": " | ".join(sorted({r['Original_Composition'] or r['Alloy_ID'] for r in rs})),
            "processing_conditions": " | ".join(sorted({r['Processing_route'] for r in rs if r['Processing_route']})),
            "TRIP_values": " | ".join(tvals) or "NA", "TWIP_values": " | ".join(wvals) or "NA",
            "Deformation_stages": " | ".join(sorted({r['Deformation_stage'] for r in rs if r['Deformation_stage']})),
            "Is_independent_experimental_group": str(independent), "Internal_label_conflict": str(conflict),
            "Potential_data_leakage_risk": "HIGH" if len(rs) > 1 else "LOW",
            "Review_note": "; ".join(why) if why else ("Correlated rows must remain grouped" if len(rs)>1 else "No internal conflict")})
    write(TABLES / "experiment_group_review.csv", group_rows, list(group_rows[0]))

    feature_rows = []
    for row, assigned in zip(rows, roles):
        for field in FEATURES:
            value = row.get(field, "")
            if not value: continue
            if field == "SFE_method":
                status, note, manual = "METHOD_RECORDED", "Method retained; values from different methods must not be treated as interchangeable", False
            else:
                status, note, manual = numeric_status(field, value, row)
            feature_rows.append({"Paper_ID": row["Paper_ID"], "Condition_ID": row["Condition_ID"], "Row_Role": assigned,
                "Field": field, "Value": value, "Declared_unit": field.split("_",1)[1] if "_" in field else "text",
                "Consistency_Status": status, "Method_or_origin": row.get("SFE_method", "") if "SFE" in field else row.get("DeltaG_method", "") if "DeltaG" in field else assigned,
                "Temperature_association": row.get("Test_T_K", ""), "Condition_association": row["Condition_ID"],
                "Review_note": note, "Requires_manual_review": str(manual)})
    write(TABLES / "feature_consistency_review.csv", feature_rows, list(feature_rows[0]))

    missing_rows = []
    for row, assigned in zip(rows, roles):
        text = " ".join([row.get("Source_location", ""), row.get("Notes", ""), row.get("Evidence_TRIP", ""), row.get("Evidence_TWIP", "")]).lower()
        for field in MISSING_FOCUS:
            if row.get(field, "") != "": continue
            if assigned.startswith("COMPUTATIONAL") and field in {"YS_MPa", "UTS_MPa", "Elongation_pct"}:
                cause = "NOT_APPLICABLE"
            elif "supplement" in text: cause = "AVAILABLE_IN_SUPPLEMENT"
            elif "table" in text: cause = "AVAILABLE_IN_TABLE"
            elif any(x in text for x in ("figure", "fig.", "digitiz")): cause = "AVAILABLE_IN_FIGURE"
            else: cause = "UNKNOWN"
            missing_rows.append({"Paper_ID": row["Paper_ID"], "DOI": row["DOI"], "Condition_ID": row["Condition_ID"],
                "Field": field, "Missingness_Cause": cause,
                "Evidence_for_classification": "Explicit location cue in extracted provenance" if cause.startswith("AVAILABLE") else "Cannot distinguish not reported from not extracted without paper review",
                "Where_to_check": row.get("Source_location", "") or "Original paper methods/tables/figures/supplement",
                "Requires_manual_review": "True"})
    write(TABLES / "missingness_root_cause.csv", missing_rows, list(missing_rows[0]))

    # Existing merge already applies exact aliases and strips header whitespace.  Normalize
    # only cell whitespace and exact binary spellings; record every changed nonblank cell.
    corrections = []
    binary = {"0": "0", "0.0": "0", "1": "1", "1.0": "1"}
    post = []
    for row, assigned in zip(rows, roles):
        out = {k: row.get(k, "") for k in canonical + ["Unmapped_Fields", "Source_File", "Source_Sheet", "Schema_Mapping_Review"]}
        for field, old in list(out.items()):
            new = base.clean(old) if isinstance(old, str) and field != "Unmapped_Fields" else old
            reason = "Whitespace normalization"
            ctype = "FORMATTING"
            if field in {"TRIP", "TWIP", "Slip", "Stacking_faulting", "HCP_to_FCC_reversion"} and str(new) in binary:
                normalized = binary[str(new)]
                if normalized != old: reason, ctype = "Unambiguous binary representation", "BINARY_NORMALIZATION"
                new = normalized
            if new != old:
                corrections.append({"Paper_ID": row["Paper_ID"], "Condition_ID": row["Condition_ID"], "Field": field,
                    "Old_Value": old, "New_Value": new, "Reason": reason, "Correction_Type": ctype,
                    "Automatic_or_Manual": "Automatic", "Source": f"{row['Source_File']}::{row['Source_Sheet']}"})
            out[field] = new
        for original, canonical_name in base.ALIASES.items():
            source_value = row["_source"].get(original, "")
            if source_value != "":
                corrections.append({"Paper_ID": row["Paper_ID"], "Condition_ID": row["Condition_ID"],
                    "Field": canonical_name, "Old_Value": f"{original}={source_value}",
                    "New_Value": out[canonical_name], "Reason": f"Exact reviewed schema alias: {original} -> {canonical_name}",
                    "Correction_Type": "EXACT_SCHEMA_ALIAS", "Automatic_or_Manual": "Automatic",
                    "Source": f"{row['Source_File']}::{row['Source_Sheet']}"})
        review = mechanism_problem(row, assigned) is not None or assigned == "UNRESOLVED"
        out.update({"QC_Status": "SAFE_QC_COMPLETE_MANUAL_REVIEW_REMAINS" if review else "SAFE_QC_COMPLETE",
                    "Requires_Manual_Review": str(review), "Row_Role": assigned,
                    "Target_Review_Status": "REVIEW_REQUIRED" if mechanism_problem(row, assigned) else "NO_FLAG",
                    "Schema_Review_Status": "SOURCE_HAS_UNMAPPED_FIELDS" if row["Unmapped_Fields"] else "CANONICAL_OR_SAFE_ALIAS"})
        post.append(out)
    write(TABLES / "qc_correction_log.csv", corrections,
          ["Paper_ID", "Condition_ID", "Field", "Old_Value", "New_Value", "Reason", "Correction_Type", "Automatic_or_Manual", "Source"])
    post_fields = list(post[0])
    write(INTERIM / "master_19papers_post_safe_qc.csv", post, post_fields)

    questionable = [r for r, a in zip(rows, roles) if mechanism_problem(r, a) or
                    any(x in " ".join([r.get("Dominant_mechanism", ""), r.get("Evidence_TRIP", ""), r.get("Evidence_TWIP", ""), r.get("Deformation_stage", "")]).lower()
                        for x in ("initial twin", "annealing twin", "pre-existing", "cold rolling", "reference", "reversion", "not forced", "not explicitly assigned"))]
    target_lines = ["# Target definition audit", "", "> No target was changed by this audit. Questionable cases remain queued for source review.", "",
        "## Operational definition", "", "- **TRIP=1** must mean deformation-induced martensitic transformation observed or explicitly modelled for the specified mechanical condition; initial/pre-existing martensite, processing-induced transformation, and phase reversion alone do not qualify.",
        "- **TWIP=1** must mean deformation twinning during the specified condition; initial, annealing, or pre-existing twins alone do not qualify.", "", "## Questionable cases", ""]
    for r in questionable:
        target_lines.append(f"- **{r['Paper_ID']} / {r['Condition_ID']}** — TRIP={r['TRIP'] or 'NA'}, TWIP={r['TWIP'] or 'NA'}; {r['Dominant_mechanism'] or 'mechanism missing'}. Check {r['Source_location'] or 'the original paper' }.")
    (ROOT / "reports/TARGET_DEFINITION_AUDIT.md").write_text("\n".join(target_lines)+"\n", encoding="utf-8")

    # One actionable queue item per target/role case plus each major recoverable feature.
    queue = []
    for r, a in zip(rows, roles):
        if mechanism_problem(r, a) or a == "UNRESOLVED":
            queue.append({"Priority": "P1", "Paper_ID": r["Paper_ID"], "DOI": r["DOI"], "Condition_ID": r["Condition_ID"],
                "Field_or_Issue": "TRIP/TWIP target or row independence", "Current_Value": f"TRIP={r['TRIP'] or 'NA'}; TWIP={r['TWIP'] or 'NA'}; role={a}",
                "What_needs_verification": "Verify deformation-specific mechanism evidence and whether this is an independent, stage, summary, or computational observation",
                "Where_to_check": r["Source_location"] or "Methods/results and cited figure/table", "Expected_benefit": "Defensible target and leakage-safe grouping"})
    for m in missing_rows:
        if m["Missingness_Cause"] in {"AVAILABLE_IN_FIGURE", "AVAILABLE_IN_TABLE", "AVAILABLE_IN_SUPPLEMENT", "SCHEMA_MAPPING_FAILURE"}:
            queue.append({"Priority": "P2", "Paper_ID": m["Paper_ID"], "DOI": m["DOI"], "Condition_ID": m["Condition_ID"],
                "Field_or_Issue": m["Field"], "Current_Value": "NA", "What_needs_verification": "Extract value with unit, method, temperature, and condition provenance",
                "Where_to_check": m["Where_to_check"], "Expected_benefit": "Recover a major ML feature without adding a paper"})
    rank = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
    queue.sort(key=lambda x: (rank[x["Priority"]], x["Paper_ID"], x["Condition_ID"], x["Field_or_Issue"]))
    write(TABLES / "manual_review_queue.csv", queue, list(queue[0]))

    mc = Counter(r["Problem_Type"] for r in mech)
    unresolved = sum(x == "UNRESOLVED" for x in roles)
    exp_groups = [g for g in group_rows if g["Is_independent_experimental_group"] == "True"]
    usable_trip = sum(g["TRIP_values"] in {"0", "1"} for g in exp_groups)
    usable_twip = sum(g["TWIP_values"] in {"0", "1"} for g in exp_groups)
    usable_joint = sum(g["TRIP_values"] in {"0", "1"} and g["TWIP_values"] in {"0", "1"} for g in exp_groups)
    before = f"""# QC before/after and final scientific diagnosis

## Before/after

| Measure | Before | After safe QC |
|---|---:|---:|
| Rows | 98 | {len(post)} |
| TRIP missing | {sum(not r['TRIP'] for r in rows)} | {sum(not r['TRIP'] for r in post)} |
| TWIP missing | {sum(not r['TWIP'] for r in rows)} | {sum(not r['TWIP'] for r in post)} |
| Unresolved row roles | {unresolved} | {unresolved} |
| Source batches with noncanonical fields | {len({r['Source_Workbook'] for r in schema})} | {len({r['Source_Workbook'] for r in schema if r['Mapping_Status'] not in {'SAFE_ALIAS'}})} |
| Strict singleton independent experimental groups | {len(exp_groups)} | {len(exp_groups)} |
| Internally label-ambiguous groups | {ambiguous_groups} | {ambiguous_groups} |

Safe aliases recovered `Data_role`, `Composition_basis_original`, and `Image_modalities` into the canonical row type, composition basis, and characterization fields. New scientific fields were preserved, not collapsed. There are **{len(queue)} condition/field-level manual-review tasks across {len({q['Paper_ID'] for q in queue})} papers** in the ranked queue.

## Final scientific diagnosis

1. The **{len(mech)}** mechanism-flagged rows comprise: formatting/schema **{mc['J'] + mc['D']}**, genuine missing **{mc['A']}**, scientifically ambiguous/text-without-defensible-label **{mc['B'] + mc['C'] + mc['E'] + mc['F'] + mc['K']}**, computational/model **{mc['G']}**, and repeated-stage/summary **{mc['H'] + mc['I']}**. Categories are mutually exclusive primary diagnoses; the CSV retains row-level reasoning.
2. **{sum(r['Can_Auto_Fix']=='True' for r in mech)} mechanism flags** can be scientifically repaired without reading papers. Safe representation/schema-alias corrections elsewhere total **{len(corrections)}** cells.
3. **{sum(r['Requires_Paper_Review']=='True' for r in mech)} mechanism flags** require source review.
4. **Yes, potentially.** Existing groups combine stage-resolved rows and, in some cases, changing temperature/condition, creating artificial *group-level* conflicts even when row labels may be scientifically valid.
5. **Yes, before ML.** Use a stable parent specimen/test ID plus condition sub-ID (alloy + processing + temperature + strain rate + specimen), and a separate stage ID. Keep all stages together for splitting but do not require identical labels.
6. Existing papers can realistically recover values explicitly queued from figures/tables/supplements, especially test conditions, processing parameters, phase fractions, grain size, and mechanical properties. SFE/DeltaG must retain method and temperature provenance.
7. Features marked UNKNOWN/NOT_REPORTED can only be distinguished after paper review; if genuinely unreported, complete method-matched SFE/DeltaG, initial phase fractions, and processing/test metadata require new papers or author data—not imputation.
8. Under the deliberately strict definition of a singleton, explicitly experimental independent group: TRIP **{usable_trip}**, TWIP **{usable_twip}**, joint **{usable_joint}**. These are conservative usable counts, not row counts; multirow parent experiments require redesigned IDs before they can be counted correctly.
9. Collect independent deformation experiments with explicit pre-test phase/twin state and post-/in-situ mechanism evidence, prioritising TWIP-negative/TRIP-negative controls, single-positive TRIP and TWIP conditions, and verified joint-positive cases across temperature, strain rate, grain size, and processing—with complete SFE method and phase-fraction provenance.
10. **Data collection and manual source review should occur first.** A Pilot ML run is not yet scientifically justified because target semantics and independence remain unresolved; no model was trained.

Fewer rows are not treated as improvement: all 98 rows are preserved, and uncertainty remains explicit.
"""
    (ROOT / "reports/QC_BEFORE_AFTER.md").write_text(before, encoding="utf-8")
    print(f"Forensic QC complete: {len(rows)} rows; {len(mech)} mechanism flags; no model trained.")


if __name__ == "__main__":
    main()
