"""Dependency-free execution fallback for the four-workbook audit pipeline.

This runner exists so the immutable extraction can still be audited when the
scientific Python stack cannot be installed.  It reads the OOXML worksheets
with the standard library, preserves later-batch extras as JSON, and writes
CSV/Markdown deliverables.  It does not train a model or infer scientific data.
"""

from __future__ import annotations

import csv
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
FILES = [
    "TRIP_TWIP_First5_FULL_EXTRACTION.xlsx",
    "TRIP_TWIP_P006_P010_FULL_EXTRACTION.xlsx",
    "TRIP_TWIP_P011_P015_FULL_EXTRACTION.xlsx",
    "TRIP_TWIP_P016_P019_FULL_EXTRACTION.xlsx",
]
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ALIASES = {
    "Data_role": "Row_Type",
    "Composition_basis_original": "Composition_basis",
    "Image_modalities": "Characterization_methods",
}
CANDIDATES = [
    "Fe_at%", "Mn_at%", "Co_at%", "Cr_at%", "Ni_at%", "N_at%", "C_at%",
    "Mo_at%", "Si_at%", "Ti_at%", "V_at%", "Homogenization_T_K",
    "Homogenization_time_h", "Hot_rolling_T_K", "Hot_rolling_reduction_pct",
    "Cold_rolling_reduction_pct", "Annealing_T_K", "Annealing_time_min",
    "Test_T_K", "Strain_rate_s-1", "True_strain", "Grain_size_um",
    "Initial_FCC_fraction", "Initial_HCP_fraction", "SFE_mJ_m2",
    "DeltaG_FCC_HCP_J_mol", "Elastic_modulus_GPa", "Shear_modulus_GPa",
    "Poisson_ratio", "Lattice_parameter_nm", "Atomic_size_misfit_pct",
    "YS_MPa", "UTS_MPa", "Elongation_pct", "Uniform_elongation_pct",
    "log10_strain_rate",
]


def clean(value):
    return " ".join(str(value).strip().split())


def _col_number(ref):
    n = 0
    for char in re.match(r"[A-Z]+", ref).group():
        n = n * 26 + ord(char) - 64
    return n


def workbook_sheets(path):
    """Return ``[(sheet_name, rows)]`` from an xlsx using OOXML only."""
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(t.text or "" for t in x.iter(f"{{{NS}}}t")) for x in root]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {x.attrib["Id"]: x.attrib["Target"] for x in relationships}
        answer = []
        for sheet in workbook.find(f"{{{NS}}}sheets"):
            target = targets[sheet.attrib[f"{{{RNS}}}id"]].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(archive.read(target))
            rows = []
            for xmlrow in root.iter(f"{{{NS}}}row"):
                row = {}
                for cell in xmlrow.findall(f"{{{NS}}}c"):
                    number = _col_number(cell.attrib["r"])
                    value = cell.find(f"{{{NS}}}v")
                    inline = cell.find(f"{{{NS}}}is")
                    if cell.attrib.get("t") == "s" and value is not None:
                        parsed = strings[int(value.text)]
                    elif cell.attrib.get("t") == "inlineStr" and inline is not None:
                        parsed = "".join(t.text or "" for t in inline.iter(f"{{{NS}}}t"))
                    else:
                        parsed = value.text if value is not None else ""
                    row[number] = parsed
                rows.append(row)
            answer.append((sheet.attrib["name"], rows))
        return answer


def extraction(path):
    options = []
    for name, rows in workbook_sheets(path):
        header = [clean(v) for v in (rows[0].values() if rows else [])]
        score = len({"Paper_ID", "DOI", "Condition_ID", "Experiment_Group_ID"} & set(header))
        options.append((score, len(rows), name, rows))
    score, _, name, rows = max(options)
    if score < 4:
        raise ValueError(f"No traceable extraction sheet in {path.name}")
    positions = {n: clean(v) for n, v in rows[0].items()}
    return name, [{positions[k]: row.get(k, "") for k in positions} for row in rows[1:]]


def numeric(value):
    try:
        return float(value) if str(value).strip() else None
    except (TypeError, ValueError):
        return None


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def main():
    paths = [RAW / name for name in FILES]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing workbooks: " + ", ".join(missing))
    loaded = [(p, *extraction(p)) for p in paths]
    canonical = list(loaded[0][2][0])
    merged, schema = [], []
    for path, sheet, rows in loaded:
        columns = list(rows[0])
        mapped_aliases = {a: b for a, b in ALIASES.items() if a in columns and b not in columns}
        extras = [c for c in columns if c not in canonical and c not in mapped_aliases]
        absent = [c for c in canonical if c not in columns and c not in mapped_aliases.values()]
        for source in rows:
            out = {c: source.get(c, "") for c in canonical}
            for old, new in mapped_aliases.items():
                out[new] = source.get(old, "")
            out["Unmapped_Fields"] = json.dumps(
                {c: source[c] for c in extras if source.get(c, "") != ""},
                ensure_ascii=False, sort_keys=True,
            ) if extras else ""
            out["Source_File"], out["Source_Sheet"] = path.name, sheet
            out["Schema_Mapping_Review"] = " | ".join(f"{a} -> {b}" for a, b in mapped_aliases.items())
            rate = numeric(out.get("Strain_rate_s-1"))
            out["log10_strain_rate"] = math.log10(rate) if rate is not None and rate > 0 else ""
            merged.append(out)
        schema.append({
            "Source_File": path.name, "Source_Sheet": sheet,
            "Rows": len(rows), "Missing_Canonical_Columns": " | ".join(absent),
            "Mapped_Aliases_Manual_Review": " | ".join(f"{a} -> {b}" for a, b in mapped_aliases.items()),
            "Extra_Unmapped_Columns": " | ".join(extras),
            "Requires_Manual_Review": bool(absent or extras or mapped_aliases),
        })
    fields = canonical + ["Unmapped_Fields", "Source_File", "Source_Sheet", "Schema_Mapping_Review", "log10_strain_rate"]
    write_csv(ROOT / "data/interim/master_19papers_raw.csv", merged, fields[:-1])
    write_csv(ROOT / "data/processed/master_19papers_features.csv", merged, fields)
    tables = ROOT / "reports/tables"
    write_csv(tables / "schema_audit.csv", schema, list(schema[0]))

    by_paper = defaultdict(set)
    for row in merged:
        if row["Paper_ID"]: by_paper[row["Paper_ID"]].add(row["DOI"].strip())
    doi_rows = [{"Paper_ID": p, "DOI_values": " | ".join(sorted(x for x in values if x)),
                 "DOI_count": len({x for x in values if x}),
                 "Consistent": len({x for x in values if x}) <= 1} for p, values in sorted(by_paper.items())]
    write_csv(tables / "paper_doi_audit.csv", doi_rows, list(doi_rows[0]))

    condition_counts = Counter(r["Condition_ID"] for r in merged if r["Condition_ID"])
    duplicate_conditions = sum(n for n in condition_counts.values() if n > 1)
    comp_bad = 0; suspicious = 0
    for row in merged:
        vals = [numeric(row.get(c)) for c in canonical if re.match(r"^[A-Z][a-z]?_at%$", c)]
        vals = [v for v in vals if v is not None]
        if vals and not 99 <= sum(vals) <= 101: comp_bad += 1
        for c in canonical:
            v = numeric(row.get(c))
            if v is not None and ((any(x in c.lower() for x in ("temperature", "grain_size", "elongation", "uts", "ys_mpa")) and v < 0)
                                  or ("fraction" in c.lower() and not 0 <= v <= 1)):
                suspicious += 1; break
    roles = [r["Row_Type"].strip().lower() for r in merged]
    is_comp = [bool(re.search(r"comput|model|simulation|\bmd\b|dft|calphad", x)) for x in roles]
    is_exp = ["experiment" in x for x in roles]
    groups = defaultdict(lambda: [False, False])
    for r, exp, comp in zip(merged, is_exp, is_comp):
        if r["Experiment_Group_ID"]:
            groups[r["Experiment_Group_ID"]][0] |= exp; groups[r["Experiment_Group_ID"]][1] |= comp
    ambiguous = sum(1 for r in merged if not r["TRIP"] or not r["TWIP"] or ";" in r["Dominant_mechanism"] or "/" in r["Dominant_mechanism"])
    metrics = []
    def add(section, level, metric, value): metrics.append({"Section":section,"Level":level,"Metric":metric,"Value":value})
    for metric, value in [("total_rows",len(merged)),("papers",len(by_paper)),("doi_values",len({r['DOI'].strip() for r in merged if r['DOI'].strip()})),
                          ("unique_condition_id",len(condition_counts)),("experiment_groups",len(groups))]: add("dimensions","row",metric,value)
    add("row_role","group","independent_experimental_groups",sum(v[0] and not v[1] for v in groups.values()))
    add("row_role","group","computational_model_groups",sum(v[1] for v in groups.values()))
    add("row_role","row","experimental_rows",sum(is_exp)); add("row_role","row","computational_model_rows",sum(is_comp)); add("row_role","row","unresolved_role_rows",sum(not a and not b for a,b in zip(is_exp,is_comp)))
    for label in ("TRIP", "TWIP"):
        for value, count in sorted(Counter(r[label] or "NA" for r in merged).items()): add("labels","row",f"{label}={value}",count)
    for pair, count in sorted(Counter((r["TRIP"] or "NA",r["TWIP"] or "NA") for r in merged).items()): add("labels","row",f"TRIP/TWIP={pair[0]}/{pair[1]}",count)
    experimental_groups = defaultdict(list)
    for row, exp, comp in zip(merged,is_exp,is_comp):
        if exp and not comp and row["Experiment_Group_ID"]: experimental_groups[row["Experiment_Group_ID"]].append(row)
    for label in ("TRIP","TWIP"):
        counter=Counter()
        for rows in experimental_groups.values():
            vals={r[label] for r in rows if r[label]}
            counter[next(iter(vals)) if len(vals)==1 else ("NA" if not vals else "AMBIGUOUS")]+=1
        for value,count in sorted(counter.items()): add("labels","independent_experimental_group",f"{label}={value}",count)
    combo=Counter()
    for rows in experimental_groups.values():
        t={r['TRIP'] for r in rows if r['TRIP']}; w={r['TWIP'] for r in rows if r['TWIP']}
        combo[(next(iter(t)) if len(t)==1 else 'NA/AMBIGUOUS',next(iter(w)) if len(w)==1 else 'NA/AMBIGUOUS')]+=1
    for pair,count in sorted(combo.items()): add("labels","independent_experimental_group",f"TRIP/TWIP={pair[0]}/{pair[1]}",count)
    for c in CANDIDATES:
        pct=100*sum(r.get(c,"")=="" for r in merged)/len(merged); add("candidate_feature_missingness","row",c,round(pct,4))
    for metric,value in [("composition_sum_flagged_rows",comp_bad),("duplicate_condition_rows",duplicate_conditions),("doi_conflicting_papers",sum(not r['Consistent'] for r in doi_rows)),
                         ("ambiguous_or_missing_mechanism_rows",ambiguous),("suspicious_numerical_rows",suspicious),("schema_batches_requiring_review",sum(x['Requires_Manual_Review'] for x in schema))]: add("problems","row",metric,value)
    write_csv(tables / "data_quality_report.csv", metrics, ["Section","Level","Metric","Value"])

    ranked=sorted(((100*sum(r.get(c,"")!="" for r in merged)/len(merged),c) for c in CANDIDATES),reverse=True)
    exp_n=sum(v[0] and not v[1] for v in groups.values())
    target_counts={x:Counter(r[x] or 'NA' for r in merged) for x in ('TRIP','TWIP')}
    report = f"""# Data audit: 19-paper pre-Pilot dataset

> Generated non-destructively from the four supplied workbooks. No missing scientific value was imputed, estimated, normalised, or replaced by zero. No model was trained.

## Execution environment

The required pandas/openpyxl dependencies could not be installed because the package proxy returned HTTP 403. The standard-library OOXML fallback therefore generated the merged CSV, processed-feature CSV, QC CSV tables, and this report. The `.xlsx` merged/processed copies and matplotlib figures could not be generated in this environment; no substitute outputs or values are claimed for them.

## Dataset dimensions and separation

- **{len(merged)} rows**, **{len(by_paper)} papers**, **{len({r['DOI'].strip() for r in merged if r['DOI'].strip()})} unique DOI values**, **{len(condition_counts)} unique Condition_ID values**, and **{len(groups)} Experiment_Group_ID values**.
- **{exp_n} independent experimental groups**; **{sum(v[1] for v in groups.values())} computational/model groups**. There are **{sum(not a and not b for a,b in zip(is_exp,is_comp))} unresolved-role rows**, which must be reviewed rather than assumed experimental.

## Labels

- Row-level TRIP: {dict(target_counts['TRIP'])}
- Row-level TWIP: {dict(target_counts['TWIP'])}
- Full row- and scientifically valid independent-experimental-group balances are in `reports/tables/data_quality_report.csv`. A group is reported as ambiguous where its rows disagree; computational groups are excluded from experimental group balance.

## QC findings

- Composition sums outside 100 +/- 1 at.%: **{comp_bad} rows**.
- Rows participating in a duplicated Condition_ID: **{duplicate_conditions}**.
- Papers with conflicting nonblank DOI values: **{sum(not r['Consistent'] for r in doi_rows)}**.
- Rows with missing or syntactically ambiguous TRIP/TWIP/mechanism labels: **{ambiguous}**.
- Rows with suspicious range/negative numeric values: **{suspicious}**.
- Batches needing schema review: **{sum(x['Requires_Manual_Review'] for x in schema)} of 4**. Exact differences, reviewed aliases, and preserved extras are listed in `schema_audit.csv`; per-row extras remain JSON in `Unmapped_Fields`.

## Candidate feature availability (ranked)

| Rank | Candidate feature | Available (%) | Missing (%) |
|---:|---|---:|---:|
""" + "\n".join(f"| {i} | {c} | {p:.2f} | {100-p:.2f} |" for i,(p,c) in enumerate(ranked,1)) + f"""

## Pre-Pilot assessment

### A. Sufficiency

The dataset is sufficient for a **limited, uncertainty-aware feasibility test of the pipeline**, but not for a meaningful performance claim or final model: only {exp_n} independent experimental groups are available, observations are clustered by paper/group, role resolution is incomplete, and many scientifically important predictors are sparse. Any later Pilot must use grouped and leave-one-paper-out validation and report uncertainty.

### B. Best-supported target

Of the requested targets, **TRIP binary is presently the most supportable feasibility target**, subject to manual label/role review. TWIP binary has less usable group-level support; multilabel and four-class targets fragment the small independent-group sample further. This is a data-support assessment, not a trained-model result.

### C-D. Features

Use only high-coverage composition components and documented test/processing variables shown near the top of the ranked table. Treat zero composition entries as reported zeros, not missing-value replacements. Sparse SFE, DeltaG, phase-fraction, grain-size, elastic, geometric, and onset-stress descriptors should not be primary Pilot inputs unless collection improves. Only `log10_strain_rate` was derived: the committed elemental and binary-enthalpy reference tables contain no constants, so VEC, mismatch, entropy/enthalpy, melting-temperature, and Omega features were deliberately not calculated.

### E. Collection priorities

Collect additional independent experimental alloy-condition groups, prioritising underrepresented TWIP-positive and joint TRIP/TWIP classes; explicitly record row role and group boundaries; resolve DOI and label ambiguities; and extract complete composition basis, test temperature/rate, processing/annealing history, grain size, initial phase fractions, SFE with method/temperature, DeltaG, and mechanical properties. Add referenced elemental/pair constants before enabling further derived features.
"""
    (ROOT / "reports/DATA_AUDIT.md").write_text(report, encoding="utf-8")
    print(f"Merged and audited {len(merged)} rows from {len(by_paper)} papers; no model trained.")


if __name__ == "__main__":
    main()
