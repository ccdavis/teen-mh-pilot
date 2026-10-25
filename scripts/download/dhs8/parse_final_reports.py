"""Parse the DHS-8 mental-health chapters of the final reports in data/external/dhs8/final_reports/ into compiled tables.

Tables parsed (one value per line in the PDF text; the parser reads the "Age" block and the Residence/Total rows of each table):
  severity tables  : percent distribution by GAD-7 / PHQ-9 score category, percentage "with symptoms" (the report's cutoff) and weighted n
  care tables      : ever told by a provider they had anxiety / depression, took medicine, (counseling), n, ever sought help, n with symptoms
  diagnosis tables : Kenya 2022, DRC 2023-24, Mali 2023-24, Madagascar 2021 (diagnosis-only surveys; women and men side by side)
  national cutoffs : Nepal Table 19.5 (TPO Nepal adolescent/adult cutoffs)
Outputs (data/compiled/dhs8/): dhs8_report_tables_long.csv (every parsed cell with table, page and URL), dhs8_mental_health_prevalence.csv
(wide: survey x sex x group with PHQ-9 >= 10, PHQ-9 >= 5, GAD-7 categories and the report's anxiety definition, diagnosis items, n),
dhs8_module_inventory.csv (which DHS surveys since 2019 carry PHQ-9 / GAD-7 / diagnosis items, who was asked, exposure items, access routes;
the keyword-page counts are computed from the PDFs, the rest is transcribed from the reports and the DHS/World Bank data dictionaries).
Validation: score categories must sum to 100 (+-0.4) and the report's "with symptoms" column must equal the sum of the categories above
its cutoff (+-0.25); any failure is printed and the row flagged.
Usage: uv run python scripts/download/dhs8/parse_final_reports.py
"""
import re, csv, json, pathlib, pymupdf, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]; EXT = ROOT/"data/external/dhs8"; OUT = ROOT/"data/compiled/dhs8"; OUT.mkdir(parents=True, exist_ok=True)
IDX = {r["survey"]: r for r in csv.DictReader(open(EXT/"final_reports/index.csv"))}

AGE = r"15[–-]19|20[–-]24|25[–-]29|30[–-]34|35[–-]39|40[–-]44|45[–-]49|15[–-]24|15[–-]29|20[–-]49|30[–-]39|40[–-]49|50[–-]54|55[–-]59"
LABELS = {"age": AGE, "residence": r"Urban|Rural|Urbana|Rural|Urbain|Urbaine|Rural", "total": r"Total|Ensemble"}
LABEL_RE = re.compile(r"^\s*(" + "|".join(LABELS.values()) + r")\s*$")
NUM_RE = re.compile(r"^\s*\(?(\*|\d{1,3}(?:[ ,]\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\)?\s*$")

def num(tok):
    tok = tok.strip().strip("()")
    if tok == "*": return None
    if re.fullmatch(r"\d{1,3}(?: \d{3})+", tok): return float(tok.replace(" ", ""))          # 3 050  (pt/fr thousands)
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+", tok): return float(tok.replace(",", ""))          # 3,050  (en thousands)
    return float(tok.replace(",", "."))                                                       # 12,9 -> 12.9

def page_texts(pdf):
    doc = pymupdf.open(pdf); return [p.get_text() for p in doc]

def parse_table(text, cols, start_pat=r"^\s*(Age|Age group|Grupo de idade|Âge|Groupe d.âges?)\s*$"):
    """From the table text, return {label: [values...]} for the age, residence and total rows with len(cols) numeric cells each."""
    lines = text.splitlines(); out = {}
    starts = [i for i, l in enumerate(lines) if re.match(start_pat, l)]
    if not starts: return out
    i = starts[0] + 1; group_seen = set()
    while i < len(lines):
        m = LABEL_RE.match(lines[i])
        if m:
            lab = re.sub(r"[–-]", "-", m.group(1)); vals = []; j = i + 1
            while j < len(lines) and len(vals) < len(cols):
                if lines[j].strip() == "": j += 1; continue
                if NUM_RE.match(lines[j]): vals.append(num(lines[j])); j += 1
                else: break
            if len(vals) == len(cols) and lab not in out: out[lab] = vals
            i = j
            if lab in ("Total", "Ensemble"): break
        else: i += 1
    return out

def find_table(pages, title_re, cols):
    """First page whose text matches the table title AND whose Age block parses (skips the list-of-tables and narrative mentions)."""
    for k, t in enumerate(pages):
        if re.search(title_re, t):
            rows = parse_table(t, cols)
            if "15-19" in rows: return k, rows
    return None, {}

# per-survey table specifications: (table id, sex, kind, title regex, columns)
GAD3 = ["gad_0_5", "gad_6_14", "gad_15_21", "total", "anx_report", "n"]
GAD4 = ["gad_0_4", "gad_5_9", "gad_10_14", "gad_15_21", "total", "anx_report", "n"]
PHQ5 = ["phq_0_4", "phq_5_9", "phq_10_14", "phq_15_19", "phq_20_27", "total", "dep_report", "n"]
CARE6 = ["told_anx", "told_dep", "took_med", "n", "sought_help", "n_sympt"]
NPCARE = ["told_anx", "told_dep", "took_med", "counsel", "n"]
DIAG8 = ["told_w", "n_w", "treat_w", "n_told_w", "told_m", "n_m", "treat_m", "n_told_m"]
SPECS = {
 "NP2022DHS": [("19.2.1","women","gad",r"Table 19\.2\.1\s+Severity of symptoms of anxiety: Women",GAD3), ("19.2.2","men","gad",r"Table 19\.2\.2\s+Severity of symptoms of anxiety: Men",GAD3),
               ("19.4.1","women","phq",r"Table 19\.4\.1\s+Severity of symptoms of depression: Women",PHQ5), ("19.4.2","men","phq",r"Table 19\.4\.2\s+Severity of symptoms of depression: Men",PHQ5),
               ("19.6.1","women","care",r"Table 19\.6\.1\s+Treatment for symptoms of anxiety or depression: Women",NPCARE), ("19.6.2","men","care",r"Table 19\.6\.2\s+Treatment for symptoms of anxiety or depression: Men",NPCARE),
               ("19.5","both","national",r"Table 19\.5\s+Symptoms of anxiety and depression among women and men",["anx_nat_w","dep_nat_w","n_w","anx_nat_m","dep_nat_m","n_m","anx_nat_t","dep_nat_t","n_t"])],
 "MZ2022DHS": [("19.4.1","women","gad",r"Quadro 19\.4\.1\s+Gravidade dos sintomas de ansiedade: Mulheres",GAD3), ("19.4.2","men","gad",r"Quadro 19\.4\.2\s+Gravidade dos sintomas de ansiedade: Homens",GAD3),
               ("19.6.1","women","phq",r"Quadro 19\.6\.1\s+Gravidade dos sintomas de depressão: Mulheres",PHQ5), ("19.6.2","men","phq",r"Quadro 19\.6\.2\s+Gravidade dos sintomas de depressão: Homens",PHQ5),
               ("19.7.1","women","care",r"Quadro 19\.7\.1\s+Procura de cuidados e tratamento para sintomas de ansiedade ou depressão: Mulheres",CARE6), ("19.7.2","men","care",r"Quadro 19\.7\.2\s+Procura de cuidados e tratamento para sintomas de ansiedade ou depressão: Homens",CARE6)],
 "BD2022DHS": [("15.2","women","gad",r"Table 15\.2\s+Severity of symptoms of anxiety",GAD3), ("15.4","women","phq",r"Table 15\.4\s+Severity of symptoms of depression",PHQ5),
               ("15.5","women","care",r"Table 15\.5\s+Care seeking and treatment for symptoms of anxiety or depression",CARE6)],
 "LS2023DHS": [("18.2.1","women","phq",r"Table 18\.2\.1\s+Severity of symptoms of depression: Women",PHQ5), ("18.2.2","men","phq",r"Table 18\.2\.2\s+Severity of symptoms of depression: Men",PHQ5),
               ("18.3.1","women","care",r"Table 18\.3\.1\s+Care seeking and treatment for symptoms of depression or anxiety: Women",CARE6), ("18.3.2","men","care",r"Table 18\.3\.2\s+Care seeking and treatment for symptoms of depression or anxiety: Men",CARE6)],
 "ZM2024DHS": [("18.2.1","women","gad",r"Table 18\.2\.1\s+Severity of symptoms of anxiety: Women",GAD4), ("18.2.2","men","gad",r"Table 18\.2\.2\s+Severity of symptoms of anxiety: Men",GAD4),
               ("18.4.1","women","phq",r"Table 18\.4\.1\s+Severity of symptoms of depression: Women",PHQ5), ("18.4.2","men","phq",r"Table 18\.4\.2\s+Severity of symptoms of depression: Men",PHQ5),
               ("18.5.1","women","care",r"Table 18\.5\.1\s+Care seeking and treatment for symptoms of anxiety or depression: Women",CARE6), ("18.5.2","men","care",r"Table 18\.5\.2\s+Care seeking and treatment for symptoms of anxiety or depression: Men",CARE6)],
 "KE2022DHS": [("14.6","both","diag",r"Table 14\.6\s+Depression diagnosis and treatment\s*\n",DIAG8)],
 "CD2023DHS": [("17.12","both","diag",r"Tableau 17\.12\s+Diagnostic et traitement de la dépression ou de l’anxiété",DIAG8)],
 "ML2023DHS": [("14.9","both","diag",r"Tableau 14\.9\s+Diagnostic et traitement de la dépression ou de l’anxiété",DIAG8)],
 "MD2021DHS": [("14.6","both","diag",r"Tableau 14\.6\s+Prise en charge de la dépression",DIAG8)],
}
MODULE_MIN_SCORE_LABEL = {"anx_report": {"GAD3": "GAD-7 >= 6", "GAD4": "GAD-7 >= 10"}}

long_rows = []; problems = []
for sid, specs in SPECS.items():
    meta = IDX[sid]; pages = page_texts(EXT/"final_reports"/meta["file"])
    for tid, sex, kind, title_re, cols in specs:
        k, rows = find_table(pages, title_re, cols)
        if k is None: problems.append(f"{sid} table {tid}: no page with this title and a parsable 15-19 row"); continue
        for lab, vals in rows.items():
            d = dict(zip(cols, vals))
            if kind in ("gad", "phq"):
                cats = [c for c in cols if c.startswith(("gad_", "phq_"))]; s = sum(d[c] for c in cats if d[c] is not None)
                if abs(s - 100) > 0.4: problems.append(f"{sid} {tid} {lab}: categories sum to {s:.1f}")
                cut = "dep_report" if kind == "phq" else "anx_report"
                above = [c for c in cats if int(c.split("_")[1]) >= (10 if kind == "phq" or len(cats) == 4 else 6)]
                if d[cut] is not None and abs(sum(d[c] for c in above) - d[cut]) > 0.25: problems.append(f"{sid} {tid} {lab}: '{cut}' {d[cut]} != sum of {above} = {sum(d[c] for c in above):.1f}")
            gtype = "age" if re.match(AGE, lab) else ("residence" if lab in ("Urban","Rural","Urbana","Urbain","Urbaine") else "total")
            lab2 = {"Urbana": "Urban", "Urbain": "Urban", "Urbaine": "Urban", "Ensemble": "Total"}.get(lab, lab)
            for c, v in d.items():
                if c == "total": continue
                long_rows.append(dict(survey=sid, country=meta["country"], year=meta["year"], sex=sex, group_type=gtype, group=lab2, measure=c, value=v, table=tid, pdf_page=k+1, report_page=None, source_url=meta["url"], file=meta["file"]))
L = pd.DataFrame(long_rows)
# printed page number = the "nnn  •  Chapter" header; derive per pdf page from the text
for sid in L.survey.unique():
    pages = page_texts(EXT/"final_reports"/IDX[sid]["file"])
    for k in L[L.survey == sid].pdf_page.unique():
        m = re.search(r"(\d{2,3})\s+•", pages[k-1][:200]) or re.search(r"•\s+(\d{2,3})", pages[k-1][:200])
        L.loc[(L.survey == sid) & (L.pdf_page == k), "report_page"] = int(m.group(1)) if m else None
L.to_csv(OUT/"dhs8_report_tables_long.csv", index=False)
print(f"parsed {len(L)} cells from {L.groupby(['survey','table']).ngroups} tables"); print("\n".join("PROBLEM: " + p for p in problems) or "all checks passed")

# wide prevalence table
W = L[L.sex.isin(["women", "men"])].pivot_table(index=["survey","country","year","sex","group_type","group"], columns="measure", values="value", aggfunc="first").reset_index()
def col(df, c): return df[c] if c in df else pd.Series([None]*len(df), index=df.index, dtype=float)
W["phq9_ge10"] = col(W, "dep_report"); W["phq9_ge5"] = (100 - col(W, "phq_0_4")).round(1)
W["gad7_ge5"] = (100 - col(W, "gad_0_4")).round(1); W["gad7_ge6"] = (col(W, "gad_6_14") + col(W, "gad_15_21")).round(1)
W["gad7_ge10"] = (col(W, "gad_10_14") + col(W, "gad_15_21")).round(1); W["gad7_ge15"] = col(W, "gad_15_21")
W["anxiety_report_def"] = W.apply(lambda r: ("GAD-7 >= 10" if pd.notna(r.get("gad_0_4")) else ("GAD-7 >= 6" if pd.notna(r.get("gad_0_5")) else None)), axis=1)
W["anxiety_report_pct"] = col(W, "anx_report")
W["n_weighted"] = col(W, "n")
# diagnosis-only tables (women/men side by side) -> rows per sex
D = L[L.sex == "both"]
for (sid, lab), g in D.groupby(["survey", "group"]):
    d = dict(zip(g.measure, g.value)); meta = IDX[sid]; gt = g.group_type.iloc[0]
    if "told_w" in d:
        for sx, suf in (("women", "w"), ("men", "m")):
            W = pd.concat([W, pd.DataFrame([dict(survey=sid, country=meta["country"], year=meta["year"], sex=sx, group_type=gt, group=lab, told_dep_or_anx=d[f"told_{suf}"], n_weighted=d[f"n_{suf}"], treated_among_told=d[f"treat_{suf}"])])], ignore_index=True)
    if "anx_nat_w" in d:
        for sx, suf in (("women", "w"), ("men", "m")):
            W.loc[(W.survey == sid) & (W.sex == sx) & (W.group == lab), ["anx_national_cutoff", "dep_national_cutoff"]] = [d[f"anx_nat_{suf}"], d[f"dep_nat_{suf}"]]
keep = ["survey","country","year","sex","group_type","group","n_weighted","phq9_ge10","phq9_ge5","phq_0_4","phq_5_9","phq_10_14","phq_15_19","phq_20_27","anxiety_report_def","anxiety_report_pct","gad7_ge5","gad7_ge6","gad7_ge10","gad7_ge15","gad_0_4","gad_0_5","gad_5_9","gad_6_14","gad_10_14","gad_15_21","told_anx","told_dep","told_dep_or_anx","took_med","counsel","sought_help","n_sympt","anx_national_cutoff","dep_national_cutoff","treated_among_told"]
for c in keep:
    if c not in W: W[c] = None
src = L.groupby(["survey","sex"]).apply(lambda g: "; ".join(sorted({f"Table {t} p.{int(p) if pd.notna(p) else '?'}" for t, p in zip(g.table, g.report_page)})), include_groups=False).rename("source_tables").reset_index()
W = W[keep].merge(src, on=["survey","sex"], how="left"); W["source_url"] = W.survey.map(lambda s: IDX[s]["url"])
W["group_order"] = W.group.map(lambda g: {"Total": 90, "Urban": 80, "Rural": 81}.get(g, int(g[:2]) if g[:2].isdigit() else 95)); W = W.sort_values(["survey","sex","group_order","group"]).drop(columns="group_order")
W.to_csv(OUT/"dhs8_mental_health_prevalence.csv", index=False, float_format="%.1f")
print(W[(W.group == "15-19")][["survey","sex","n_weighted","phq9_ge10","anxiety_report_def","anxiety_report_pct","gad7_ge10","told_dep_or_anx","told_dep"]].to_string(index=False))

# ---- module inventory: which DHS surveys with fieldwork from 2019 carry the module, who was asked, exposure items, access routes ----
# Transcribed from the final reports (chapter and tables above), the DHS-8 recode data dictionaries published by the World Bank Microdata
# Library (RECMTH / MRECMTH files: mth1-7 GAD-7 items, mth8-16 PHQ-9 items, mth19/mth20 diagnosis, mth22 PHQ score, mth24 GAD score;
# "NA -" labels mark items not fielded) and the IPUMS DHS sample files (scripts/extract/dhs_extract.py). phq_gad_pages counts PDF pages
# of the final report mentioning PHQ / GAD-7, computed here.
INV = [
 # survey, module, instruments, women universe, men asked, internet items (v171a/b), smartphone item (v169c), IPUMS DHS status, raw files, report chapter
 ("NP2022DHS","PHQ-9 + GAD-7","GAD-7, PHQ-9, diagnosis, care seeking","women 15-49 in the men's-survey household subsample (n = 7,442)","yes, men 15-49 in the same households (n = 4,913)","yes","yes","np2022ir: DEPRESSIONSCORE, GADSCORE, ANXIETYDIAG, INTERNETMO, CELLPHONESMART; no men's file","NPIR82FL / NPMR82FL (RECMTH, MRECMTH)","Ch. 19 Mental Health, Tables 19.2-19.7"),
 ("MZ2022DHS","PHQ-9 + GAD-7","GAD-7, PHQ-9, diagnosis, care seeking","all women 15-49 (n = 13,183)","yes, men 15-49 (n = 5,380)","yes (in the report; not yet in IPUMS DHS)","yes","mz2022ir: DEPRESSIONSCORE, GADSCORE, CELLPHONESMART; INTERNETMO/INTERNETEVYR not integrated; no men's file","MZIR81FL / MZMR81FL","Ch. 19 Saúde Mental, Quadros 19.4-19.8"),
 ("BD2022DHS","PHQ-9 + GAD-7","GAD-7, PHQ-9, diagnosis, care seeking","ever-married women 15-49 in the long-questionnaire households (n = 20,029)","no (no men's survey)","yes","yes","bd2022ir: DEPRESSIONSCORE, GADSCORE, ANXIETYDIAG, INTERNETMO, CELLPHONESMART","BDIR81FL","Ch. 15 Mental Health, Tables 15.2-15.6"),
 ("ZM2024DHS","PHQ-9 + GAD-7","GAD-7, PHQ-9, diagnosis, care seeking","all women 15-49 (n = 13,951)","yes, men 15-49 (n = 12,585)","yes","yes","not in IPUMS DHS (sample not yet released there)","ZMIR81FL / ZMMR81FL (RECMTH, MRECMTH)","Ch. 18 Mental Health, Tables 18.2-18.6"),
 ("LS2023DHS","PHQ-9 only","PHQ-9, diagnosis, care seeking (GAD-7 items marked NA in the recode)","women 15-49 in a household subsample (n = 3,297)","yes, men 15-49 (n = 3,215)","yes","yes","ls2023ir integrated without the mental-health variables","LSIR81FL / LSMR81FL (RECMTH, MRECMTH)","Ch. 18 Mental Health, Tables 18.2-18.3"),
 ("KE2022DHS","diagnosis only","ever told by a provider: depression or anxiety; treatment","women 15-49 in the men's-survey households","yes, men 15-49","no frequency item in IPUMS (v171a/b fielded)","yes","ke2022ir: DEPRESSIONDIAG, ANXIETYDIAG, CELLPHONESMART","KEIR8CFL / KEMR8CFL","Ch. 14 Chronic Conditions, Table 14.6"),
 ("MD2021DHS","diagnosis only","ever told: depression; treatment","women 15-49","yes, men 15-59","ever-use only (women); frequency (men)","no","mg2021ir: DEPRESSIONDIAG, DEPRESSIONTR, INTERNETEVYR; mg2021mr: DEPRESSIONDIAGMN, INTERNETMOMN","MDIR81FL / MDMR81FL","Ch. 14, Tableau 14.6"),
 ("ML2023DHS","diagnosis only","ever told: depression or anxiety; treatment","women 15-49","yes, men 15-49","yes","yes","not in IPUMS DHS","MLIR8AFL / MLMR8AFL","Ch. 14, Tableau 14.9"),
 ("CD2023DHS","diagnosis only","ever told: depression or anxiety; treatment","women 15-49","yes, men 15-49","yes","yes","not in IPUMS DHS","CDIR81FL / CDMR81FL","Ch. 17, Tableau 17.12"),
 ("JO2023DHS","none","-","-","-","yes","yes","jo2023ir (no mental-health variables)","JOIR82FL (no RECMTH file in the recode)","no mental-health chapter"),
 ("KH2021DHS","none","-","-","-","yes","yes","kh2021ir (no mental-health variables)","KHIR82FL","no mental-health chapter"),
]
others = sorted(set(IDX) - {r[0] for r in INV})
inv = pd.DataFrame(INV, columns=["survey","module","instruments","women_universe","men_asked","internet_items","smartphone_item","ipums_dhs_status","raw_recode_files","report_chapter"])
inv = pd.concat([inv, pd.DataFrame([dict(survey=s, module="none", instruments="-", women_universe="-", men_asked="-", internet_items="", smartphone_item="", ipums_dhs_status="", raw_recode_files="", report_chapter="no mental-health chapter") for s in others])], ignore_index=True)
pat = re.compile(r"PHQ|GAD-?7|QSP-9|TAG-7", re.I)
inv["phq_gad_pages"] = inv.survey.map(lambda s: sum(bool(pat.search(t)) for t in page_texts(EXT/"final_reports"/IDX[s]["file"])))
inv["country"] = inv.survey.map(lambda s: IDX[s]["country"]); inv["fieldwork_year"] = inv.survey.map(lambda s: IDX[s]["year"]); inv["final_report"] = inv.survey.map(lambda s: IDX[s]["url"])
inv["release_date"] = inv.survey.map(lambda s: IDX[s]["release"])
inv = inv[["survey","country","fieldwork_year","release_date","module","instruments","women_universe","men_asked","internet_items","smartphone_item","ipums_dhs_status","raw_recode_files","report_chapter","phq_gad_pages","final_report"]]
inv.to_csv(OUT/"dhs8_module_inventory.csv", index=False)
print(inv[["survey","module","men_asked","phq_gad_pages","ipums_dhs_status"]].to_string(index=False))
