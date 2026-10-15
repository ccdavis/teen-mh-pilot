"""Maine Integrated Youth Health Survey: county high-school detailed tables (grades 9-12).
2015-2023: SAS HTML output saved as .xls (pandas.read_html); 2009-2013 and PDF-only counties: pdfplumber text.
Each question page: title, question text (+code), 'Percentage of students who answered Yes', then Total/Female/Male x (% CI N) by age, grade, ..."""
import re, glob, os, pandas as pd, pdfplumber
D = "data/external/state_surveys/me"
ITEMS = [(r"feel so sad or hopeless almost every day for two weeks", "sad_hopeless", "MIYHS HS: During the past 12 months, did you ever feel so sad or hopeless almost every day for two weeks or more in a row that you stopped doing some usual activities? (% yes)"),
         (r"seriously consider attempting suicide", "considered_suicide", "MIYHS HS: During the past 12 months, did you ever seriously consider attempting suicide? (% yes)"),
         (r"how many times did you actually attempt suicide", "attempted_suicide", "MIYHS HS: During the past 12 months, how many times did you actually attempt suicide? (% 1 or more times)"),
         (r"(bothered by|felt) .*down, depressed,? or hopeless", "depressed_2wk", "MIYHS HS: PHQ-style feeling down, depressed or hopeless item (see report)"),
         (r"average school day.*(hours|time).*(TV|screen|video|computer)", "screen_time_3plus", "MIYHS HS: screen-time item (% 3+ hours; see report)")]
def item_for(q):
    for pat, code, note in ITEMS:
        if re.search(pat, q, re.I): return code, note
    return None, None
def pnum(s):
    s = str(s).strip()
    if s in ("*", "nan", "", "None", "^"): return None
    try: return float(s.replace("%", "").replace(",", ""))
    except: return None
out = []
def add(y, county, grade, sex, code, note, v, n, src, extra=""):
    if v is None: return
    out.append(dict(state="ME", geography_type="county", geography_name=county, geography_fips=None, year=y, grade_or_age=grade, sex=sex,
                    item=code, value_pct=v, n=n, source_url=src, note=note + (" | " + extra if extra else "")))
files = sorted(glob.glob(f"{D}/miyhs_*.xls")) + sorted(glob.glob(f"{D}/miyhs_*.pdf"))
done = set()
for f in files:
    m = re.match(r"miyhs_(\d{4})_(?:All_)?(.+?)_County", os.path.basename(f))
    if not m: continue
    y, county = int(m.group(1)), m.group(2).replace("_", " ") + " County"
    if (y, county) in done: continue   # prefer xls over pdf for the same county-year
    src = "https://www.maine.gov/miyhs/" + f"{y}-results"
    got = False
    if f.endswith(".xls"):
        try: tabs = pd.read_html(f)
        except Exception as e: print("fail", f, e); continue
        for i, t in enumerate(tabs):
            if t.shape[1] != 1 or t.shape[0] < 3: continue
            q = " ".join(str(x) for x in t.iloc[:, 0])
            code, note = item_for(q)
            if not code or "answered" not in q: continue
            if i + 1 >= len(tabs): continue
            d = tabs[i + 1]
            if d.shape[1] < 10: continue
            d.columns = ["row", "t_p", "t_ci", "t_n", "f_p", "f_ci", "f_n", "m_p", "m_ci", "m_n"][:d.shape[1]] + list(d.columns[10:])
            for _, r in d.iterrows():
                lab = str(r["row"]).strip()
                gm = re.match(r"^(Total|Grade (\d+))$", lab)
                if not gm: continue
                grade = "9-12" if lab == "Total" else gm.group(2)
                for sex, pc, nc in (("all", "t_p", "t_n"), ("female", "f_p", "f_n"), ("male", "m_p", "m_n")):
                    v = pnum(r[pc]); n = pnum(r[nc])
                    add(y, county, grade, sex, code, note, v, int(n) if n else None, src, "N = weighted number answering yes")
                    got = True
    else:
        try:
            with pdfplumber.open(f) as pdf: pages = [(p.extract_text() or "") for p in pdf.pages]
        except Exception as e: print("fail", f, e); continue
        for t in pages:
            if "answered 'Yes'" not in t and "answered “Yes”" not in t and "1 or more" not in t: continue
            head = t.split("Total Female Male")[0] if "Total Female Male" in t else t[:600]
            code, note = item_for(head.replace("\n", " "))
            if not code: continue
            for line in t.split("\n"):
                gm = re.match(r"^(Total|Grade (\d+)) (.*)$", line.strip())
                if not gm: continue
                grade = "9-12" if gm.group(1) == "Total" else gm.group(2)
                toks = re.findall(r"(\d+\.\d%|\*|\^)\s*(?:\([^)]*\))?\s*([\d,]+|\*|\^)?", gm.group(3))
                for (p, n), sex in zip(toks[:3], ("all", "female", "male")):
                    add(y, county, grade, sex, code, note, pnum(p), int(n.replace(",", "")) if n and n.replace(",", "").isdigit() else None, src, "N = weighted number answering yes")
                    got = True
    if got: done.add((y, county))
    else: print("no items", os.path.basename(f))

# ---------- core reports (2013; PDF-only counties in 2021/2023): 'Suicide & Depression' page with County Y, County Y-2, Maine Y, Maine Y-2 ----------
CORE = [(r"feel so sad or hopeless", "sad_hopeless"), (r"seriously consider", "considered_suicide"), (r"actually attempt(ed)? suicide", "attempted_suicide")]
have = {(r["geography_name"], r["year"], r["item"]) for r in out if r["grade_or_age"] == "9-12" and r["sex"] == "all"}
for f in sorted(glob.glob(f"{D}/miyhs_*High_School_Report.pdf")):
    m = re.match(r"miyhs_(\d{4})_(.+?)_County", os.path.basename(f)); y = int(m.group(1)); county = m.group(2).replace("_", " ") + " County"
    src = f"https://www.maine.gov/miyhs/{y}-results"
    try:
        with pdfplumber.open(f) as pdf: pages = [(p.extract_text() or "") for p in pdf.pages]
    except Exception as e: print("fail", f, e); continue
    for t in pages:
        if "Suicide & Depression" not in t: continue
        txt = t.replace("\n", " ")
        for pat, code in CORE:
            note = dict((c, n) for _, c, n in ITEMS)[code]
            # question fragment ... then the first line holding 2+ percentages: County y, County y-2, Maine y, Maine y-2
            mm = re.search(pat + r".{0,400}?(\d+\.\d%|\^|\*)\s+(\d+\.\d%|\^|\*)\s+(\d+\.\d%|\^|\*)\s+(\d+\.\d%|\^|\*)", txt, re.I | re.S)
            if not mm: continue
            for yy, tok in ((y, mm.group(1)), (y - 2, mm.group(2))):
                v = pnum(tok)
                if v is None or (county, yy, code) in have: continue
                add(yy, county, "9-12", "all", code, note, v, None, src, f"from {y} county core report (weighted)")
                have.add((county, yy, code))

df = pd.DataFrame(out).drop_duplicates(["geography_name", "year", "grade_or_age", "sex", "item"])
df.to_csv("data/compiled/state_surveys/me_miyhs_county.csv", index=False)
print(df.groupby(["item", "year"]).size().unstack(fill_value=0))
print(df[(df.grade_or_age=="9-12")&(df.sex=="all")&(df.item=="sad_hopeless")].pivot_table(index="geography_name", columns="year", values="value_pct"))
