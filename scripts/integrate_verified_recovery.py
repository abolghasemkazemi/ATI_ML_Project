"""Integrate the reviewed P006/P007/P016 workbooks without altering source data.

The canonical columns are deliberately read-only.  Recovered values are written to
parallel ``Recovered_*`` columns and every populated cell is represented in the
recovery ledger with its source evidence.  Ambiguous P016 condition/stage mappings
remain in the grouping review rather than being guessed.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data/interim/master_19papers_hierarchical_ids.csv"
OUT = ROOT / "data/processed/master_19papers_recovery_v1.csv"
LEDGER = ROOT / "data/interim/scientific_data_recovery.csv"
TARGETS = ROOT / "reports/tables/target_evidence_review.csv"
GROUPS = ROOT / "reports/tables/grouping_pdf_review.csv"
AUDIT = ROOT / "reports/RECOVERY_P006_P007_P016_AUDIT.md"
MANUAL = ROOT / "data/interim/manual_recovery"

DOIS = {"P006": "10.1016/j.scriptamat.2019.02.018", "P007": "10.1016/j.actamat.2022.117974", "P016": "10.1016/j.actamat.2018.10.017"}


def txt(v):
    if pd.isna(v):
        return ""
    return str(v)


def load_inputs():
    books = {}
    for paper in DOIS:
        path = MANUAL / f"{paper}_scientific_evidence_recovery.xlsx"
        sheets = pd.read_excel(path, sheet_name=None)
        for frame in sheets.values():
            if "Paper_ID" in frame:
                assert set(frame["Paper_ID"].dropna()) == {paper}, f"Paper_ID mismatch in {path}"
            if "DOI" in frame:
                assert set(frame["DOI"].dropna().str.lower()) == {DOIS[paper]}, f"DOI mismatch in {path}"
        books[paper] = sheets
    return books


def evidence_lookup(books, paper, key, item):
    d = books[paper][f"{paper}_Evidence"]
    key_col = "Alloy_short_name" if paper == "P006" else "Condition"
    hit = d[(d[key_col] == key) & (d["Evidence_item"] == item)]
    assert len(hit) == 1
    return hit.iloc[0]


def add_recovery(rows, row, feature, value, units, ev_type, page, figure="", table="", section="", status="VERIFIED", note=""):
    if pd.isna(value) or value == "":
        return
    rows.append({
        "Paper_ID": row.Paper_ID, "ML_Condition_ID": row.ML_Condition_ID,
        "Observation_ID": row.Observation_ID, "Feature_Name": feature,
        "Original_Value": txt(getattr(row, feature, "")), "Recovered_Value": txt(value),
        "Units": units, "Evidence_Type": ev_type, "Evidence_Location": "; ".join(x for x in [txt(page), txt(figure), txt(table), txt(section)] if x),
        "Page": txt(page), "Figure": txt(figure), "Table": txt(table), "Section": txt(section),
        "Extraction_Method": "manual source review", "Confidence": "High",
        "Reviewer_Status": status, "Reviewer_Notes": note,
    })


def integrate():
    books = load_inputs()
    base = pd.read_csv(CANON)
    out = base.copy()
    recovered_cols = [
        "Grain_size_um", "ISFE_DFT_0K_mJ_m2", "DeltaG_FCC_HCP_300K_J_mol",
        "YS_MPa", "UTS_MPa", "Elongation_pct", "Uniform_elongation_pct",
        "Initial_FCC_fraction", "Initial_HCP_fraction", "TRIP", "TWIP",
        "Recrystallized_fraction", "SFE_assumed_for_calculation_mJ_m2",
    ]
    for c in recovered_cols:
        out[f"Recovered_{c}"] = pd.NA
    out["Recovery_Provenance_JSON"] = pd.NA
    records = []

    # P006 composition uniquely identifies each canonical condition.
    p6 = books["P006"]["P006_Conditions"]
    for _, src in p6.iterrows():
        matches = out[(out.Paper_ID == "P006") & (out["Ni_at%"] == src["Ni_at%"]) & (out["Fe_at%"] == src["Fe_at%"])]
        assert len(matches) == 1
        i = matches.index[0]; row = base.loc[i]
        specs = [
            ("Grain_size_um", src.Grain_size_um, "µm", "Average grain diameter"),
            ("ISFE_DFT_0K_mJ_m2", src.ISFE_DFT_0K_mJ_m2, "mJ/m²", "Intrinsic SFE (DFT, 0 K)"),
            ("DeltaG_FCC_HCP_300K_J_mol", src.DeltaG_FCC_HCP_300K_J_mol, "J/mol", "DeltaG FCC→HCP at 300 K"),
        ]
        for f, v, u, item in specs:
            ev = evidence_lookup(books, "P006", src.Alloy_short_name, item)
            add_recovery(records, row, f, v, u, ev.Evidence_type, ev.Page, ev.Figure_or_Table, status=ev.Status,
                         note=ev.Scientific_interpretation)
            out.at[i, f"Recovered_{f}"] = v
        for f, v in [("YS_MPa", src.YS_MPa), ("UTS_MPa", src.UTS_MPa), ("Elongation_pct", src.Elongation_pct)]:
            ev = evidence_lookup(books, "P006", src.Alloy_short_name, "Tensile properties")
            add_recovery(records, row, f, v, "MPa" if f != "Elongation_pct" else "%", ev.Evidence_type, ev.Page, ev.Figure_or_Table)
            out.at[i, f"Recovered_{f}"] = v
        for f in ["TRIP", "TWIP"]:
            v = src[f]
            if pd.notna(v):
                item = f"{f} evidence"
                if f == "TRIP" and v == 0: item = "TRIP negative evidence"
                ev = evidence_lookup(books, "P006", src.Alloy_short_name, item)
                add_recovery(records, row, f, int(v), "binary", ev.Evidence_type, ev.Page, ev.Figure_or_Table, status=ev.Status, note=ev.Scientific_interpretation)
                out.at[i, f"Recovered_{f}"] = int(v)

    # P007 annealing duration gives an exact one-to-one mapping.
    p7 = books["P007"]["P007_Conditions"]
    for _, src in p7.iterrows():
        minutes = src.Annealing_time_h * 60
        matches = out[(out.Paper_ID == "P007") & (out.Annealing_time_min == minutes)]
        assert len(matches) == 1
        i = matches.index[0]; row = base.loc[i]
        loc = src.Source_location
        specs = [("YS_MPa", src.YS_MPa, "MPa"), ("UTS_MPa", src.UTS_MPa, "MPa"),
                 ("Uniform_elongation_pct", src.Uniform_elongation_pct, "%"), ("Elongation_pct", src.Total_elongation_pct, "%"),
                 ("Initial_FCC_fraction", src.Initial_FCC_fraction, "fraction"), ("Initial_HCP_fraction", src.Initial_HCP_fraction, "fraction")]
        for f, v, u in specs:
            add_recovery(records, row, f, v, u, "source table/text/figure", loc, status="VERIFIED",
                         note=txt(src.Initial_HCP_status) if "Initial_HCP" in f else "")
            out.at[i, f"Recovered_{f}"] = v
        for f in ["TRIP", "TWIP"]:
            if pd.notna(src[f]):
                add_recovery(records, row, f, int(src[f]), "binary", "TEM + diffraction + text", loc,
                             status="VERIFIED_TARGET_EVIDENCE", note=src[f"{f}_evidence"])
                out.at[i, f"Recovered_{f}"] = int(src[f])
        if pd.notna(src.Recrystallized_fraction):
            add_recovery(records, row, "Recrystallized_fraction", src.Recrystallized_fraction, "fraction", "text + figure", loc,
                         status="APPROX_REPORTED", note=src.Recrystallized_fraction_status)
            out.at[i, "Recovered_Recrystallized_fraction"] = src.Recrystallized_fraction

    # Only the two 400 C P016 rows map exactly.  The assumed SFE is retained in a
    # dedicated field; it is never placed in canonical SFE_mJ_m2.
    p16 = books["P016"]["P016_Conditions"]
    for _, src in p16[p16.Heat_treatment_T_C.eq(400)].iterrows():
        matches = out[(out.Paper_ID == "P016") & (out.Annealing_T_K == 673) & (out.Annealing_time_min == src.Heat_treatment_time_min)]
        assert len(matches) == 1
        i = matches.index[0]; row = base.loc[i]
        add_recovery(records, row, "SFE_assumed_for_calculation_mJ_m2", src.SFE_mJ_m2, "mJ/m²", "assumption in critical-stress calculation", "pp. 26–28", section="Appendix", status="ASSUMED_NOT_MEASURED", note=src.SFE_status)
        out.at[i, "Recovered_SFE_assumed_for_calculation_mJ_m2"] = src.SFE_mJ_m2

    # Attach a compact per-observation pointer to the authoritative ledger.
    rec = pd.DataFrame(records)
    for obs, group in rec.groupby("Observation_ID"):
        i = out.index[out.Observation_ID == obs][0]
        out.at[i, "Recovery_Provenance_JSON"] = json.dumps([{"feature": r.Feature_Name, "status": r.Reviewer_Status, "page": r.Page, "figure": r.Figure} for r in group.itertuples()], ensure_ascii=False)

    # Preserve all legacy ledger rows and replace only the mapped feature slots.
    ledger = pd.read_csv(LEDGER, dtype=str, keep_default_na=False)
    for _, r in rec.iterrows():
        mask = (ledger.Paper_ID == r.Paper_ID) & (ledger.Observation_ID == r.Observation_ID) & (ledger.Feature_Name == r.Feature_Name)
        if mask.any(): ledger.loc[mask, :] = [txt(r[c]) for c in ledger.columns]
        else: ledger.loc[len(ledger)] = [txt(r[c]) for c in ledger.columns]
    ledger.to_csv(LEDGER, index=False, lineterminator="\r\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    update_reviews(base, books)
    write_audit(base, out, rec)
    return base, out, rec


def update_reviews(base, books):
    t = pd.read_csv(TARGETS, dtype=str, keep_default_na=False)
    verified = {
        ("P006", "P006_MC01"): ("0", "", "XRD before/after tensile: remained single FCC; no HCP detected.", "No explicit condition-specific deformation-twin evidence; unresolved."),
        ("P006", "P006_MC02"): ("0", "1", "Post-tensile XRD remained FCC.", "EBSD/IPF deformation nanotwins and ~60° misorientation."),
        ("P006", "P006_MC03"): ("1", "", "XRD and EBSD show deformation-induced FCC→HCP.", "No direct condition-specific twin evidence; recovered review conflicts with original TWIP=0."),
        ("P007", "P007_MC01"): ("1", "1", "20%-strain TEM shows deformation-induced ε.", "20%-strain TEM shows deformation twins."),
        ("P007", "P007_MC02"): ("1", "1", "20%-strain TEM shows deformation-induced ε.", "20%-strain TEM shows deformation twins."),
        ("P007", "P007_MC03"): ("", "", "No condition-specific direct assignment.", "No condition-specific direct assignment."),
        ("P007", "P007_MC04"): ("1", "0", "TEM shows deformation-induced ε and sequential reversion.", "Twins explicitly not observed at 20% strain."),
        ("P007", "P007_MC05"): ("1", "1", "10/20%-strain TEM shows multi-variant deformation ε.", "Rare deformation twins directly observed at 20% strain."),
    }
    for key, vals in verified.items():
        m = (t.Paper_ID == key[0]) & (t.ML_Condition_ID == key[1])
        trip, twip, te, we = vals
        t.loc[m, ["TRIP_Evidence", "TWIP_Evidence", "Evidence_Type", "Evidence_Location", "Page", "Figure_Table", "Verification_Status", "Notes"]] = [te, we, "source text + microscopy/diffraction", "reviewed recovery workbook", "see recovery ledger", "see recovery ledger", "UNRESOLVED" if not trip or not twip else "VERIFIED", f"Recovered TRIP={trip or 'NA'}; TWIP={twip or 'NA'}. Original labels remain read-only; differences are not overwritten."]
    t.to_csv(TARGETS, index=False, lineterminator="\r\n")

    g = pd.read_csv(GROUPS, dtype=str, keep_default_na=False)
    for i, r in g[g.Paper_ID.isin(DOIS)].iterrows():
        if r.Paper_ID in ("P006", "P007") and r.Review_Aspect == "condition identity":
            g.loc[i, ["Evidence_Type", "Evidence_Location", "Verification_Status", "Reviewer_Notes"]] = ["processing/test condition in source", "recovery Conditions/Provenance sheets", "VERIFIED_KEEP_SEPARATE", "Distinct composition or annealing duration verifies a distinct ML condition; current conservative parent remains unchanged."]
        else:
            g.loc[i, ["Verification_Status", "Reviewer_Notes"]] = ["MANUAL_MAPPING_REVIEW", "Source recovery does not prove specimen/replicate parent linkage; do not guess or regroup. P016 stage/annealed-condition evidence cannot be mapped uniquely to the three existing rows."]
    g.to_csv(GROUPS, index=False, lineterminator="\r\n")


def write_audit(base, out, rec):
    tracked = {"grain size": ["Grain_size_um"], "SFE": ["SFE_mJ_m2", "Recovered_ISFE_DFT_0K_mJ_m2", "Recovered_SFE_assumed_for_calculation_mJ_m2"],
               "DeltaG": ["DeltaG_FCC_HCP_J_mol", "Recovered_DeltaG_FCC_HCP_300K_J_mol"], "initial FCC fraction": ["Initial_FCC_fraction"],
               "initial HCP fraction": ["Initial_HCP_fraction"], "strain rate": ["Strain_rate_s-1"], "test temperature": ["Test_T_K"],
               "mechanical properties": ["YS_MPa", "UTS_MPa", "Elongation_pct", "Uniform_elongation_pct"]}
    lines = []
    for label, cols in tracked.items():
        before = base[cols[0]].isna().sum() if len(cols) == 1 else base[[c for c in cols if c in base]].isna().all(axis=1).sum()
        relevant = [c for c in cols if c in out]
        # Recovery columns supplement, rather than replace, their canonical counterpart.
        present = pd.Series(False, index=out.index)
        for c in relevant:
            present |= out[c].notna()
            rc = f"Recovered_{c}"
            if rc in out: present |= out[rc].notna()
        after = (~present).sum()
        lines.append(f"| {label} | {before} ({before/len(base):.2%}) | {after} ({after/len(base):.2%}) |")
    def usable(df, target):
        df = df[df.Observation_Role.isin(["INDEPENDENT_CONDITION", "REPEATED_STAGE"])]
        vals = df[target].copy()
        rv = df[f"Recovered_{target}"]
        vals = vals.where(vals.notna(), rv)
        return df.assign(_v=vals).query("Data_Origin != 'DFT' and Data_Origin != 'CALPHAD'").groupby("ML_Condition_ID")["_v"].apply(lambda x: x.notna().any()).sum()
    bt, bw = usable(out.assign(Recovered_TRIP=pd.NA, Recovered_TWIP=pd.NA), "TRIP"), usable(out.assign(Recovered_TRIP=pd.NA, Recovered_TWIP=pd.NA), "TWIP")
    at, aw = usable(out, "TRIP"), usable(out, "TWIP")
    # Current architecture has one row per reviewed P006/P007 condition; joint availability is intersection.
    def joint(df):
        df=df[df.Observation_Role.isin(["INDEPENDENT_CONDITION","REPEATED_STAGE"])]
        a=df.TRIP.where(df.TRIP.notna(),df.Recovered_TRIP); b=df.TWIP.where(df.TWIP.notna(),df.Recovered_TWIP)
        z=df.assign(_a=a,_b=b).groupby('ML_Condition_ID').agg({'_a':lambda x:x.notna().any(),'_b':lambda x:x.notna().any()}); return (z._a&z._b).sum()
    bj=joint(out.assign(Recovered_TRIP=pd.NA,Recovered_TWIP=pd.NA)); aj=joint(out)
    features = ", ".join(sorted(rec.Feature_Name.unique()))
    AUDIT.write_text(f"""# P006/P007/P016 Scientific Recovery Audit

## Scope and safeguards

All three workbook Paper_ID/DOI pairs matched the canonical records. The immutable workbooks were read only. The output retains all {len(base)} observations and every original column/value; recovered data occupy parallel columns and the evidence ledger. No ML model was trained.

## Recovery results

- **Recovered value cells:** {len(rec)} (including already-present values retained as explicit verified comparisons).
- **Features recovered:** {features}.
- **Target labels newly made usable:** P006/P006_MC01 TRIP=0; P007/P007_MC04 TWIP=0; P007/P007_MC05 TWIP=1.
- **Unresolved labels remaining in reviewed papers:** P006/P006_MC01 TWIP, P006/P006_MC03 TWIP, P007/P007_MC03 TRIP and TWIP, and condition-specific P016 labels not explicitly mapped by the recovery.
- **Grouping uncertainties resolved:** condition identity for 3 P006 composition conditions and 5 P007 annealing-duration conditions; they remain separate ML conditions.
- **Grouping uncertainties remaining:** specimen/replicate parent linkage for P006/P007 and mapping P016's five recovered conditions plus sequential strain stages onto only three existing observations. These are explicitly marked `MANUAL_MAPPING_REVIEW`.

P006's intrinsic SFE is stored only as **DFT, 0 K** and its DeltaG only as **Thermo-Calc, 300 K**. P007 initial epsilon is a quench-induced starting fraction, not TRIP. P016's 18 mJ/m² is stored only as an assumed calculation input, never as experimental SFE; its unmapped sequential stages remain in manual review.

## Missingness (98-row observation basis)

| Feature family | Before | After |
|---|---:|---:|
{chr(10).join(lines)}

Method-specific SFE availability in the table counts separately preserved DFT/assumed values; it does not claim experimental room-temperature SFE coverage. Mechanical-property missingness means all four tracked property fields are absent.

## Usable labelled ML-condition availability

| Target availability | Before | After |
|---|---:|---:|
| TRIP | {bt} | {at} |
| TWIP | {bw} | {aw} |
| joint TRIP/TWIP | {bj} | {aj} |

Counts are availability counts, not independent-sample or model-readiness claims. Existing labels take precedence; recovered values fill only missing availability for this audit and discrepancies remain review records.
""", encoding="utf-8")


if __name__ == "__main__":
    integrate()
