"""Washington Healthy Youth Survey county/ESD frequency reports (AskHYS.net).
2023/2025: Excel workbooks (sheet per grade, one row per response option).
2014-2021: multi-grade PDF 'Report of Participating Schools' (Grade 6/8/10/12 columns).
2012: single-grade PDFs (Your Students / Statewide columns). 2010: Word .doc converted to .txt (same layout as 2012)."""
import re, os, glob, sys, openpyxl, pdfplumber, pandas as pd
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[3]); D = f"{ROOT}/data/external/state_surveys/wa"; fails = []
idx = pd.read_csv(f"{D}/index.csv")
ITEMS = {
    "sad_hopeless": (r"feel so sad or hopeless almost\s+every day for two weeks", "yes"),
    "considered_suicide": (r"seriously consider(ed)? attempting\s+suicide", "yes"),
    "attempted_suicide": (r"how many times did you\s+actually attempt suicide", "not0"),
    "screen_time_3plus": (r"how many hours do you spend in front of a TV, computer", "3plus"),
    "social_media_daily": (r"how often do you (use|check) social media|asks about social media", "daily"),
}
WORD = {"sad_hopeless": "HYS: During the past 12 months, did you ever feel so sad or hopeless almost every day for two weeks or more in a row that you stopped doing some usual activities? (% yes)",
        "considered_suicide": "HYS: During the past 12 months, did you ever seriously consider attempting suicide? (% yes)",
        "attempted_suicide": "HYS: During the past 12 months, how many times did you actually attempt suicide? (% 1+ times = 100 - % '0 times')",
        "screen_time_3plus": "HYS: On an average school day, how many hours do you spend in front of a TV, computer, smart phone, or other electronic device watching shows or videos, playing games, accessing the Internet, or using social media? (% 3+ hours)",
        "social_media_daily": "HYS: social media use frequency (% about once a day or more often)"}
def pct(s): return float(s.replace("%", ""))
out = []
def add(y, gtype, gname, grade, item, val, n, src, note=""):
    out.append(dict(state="WA", geography_type=gtype, geography_name=gname, geography_fips=None, year=y, grade_or_age=str(grade), sex="all",
                    item=item, value_pct=round(val, 1), n=n, source_url=src, note=(WORD[item] + (" | " + note if note else ""))))
# ---------- Excel ----------
for _, r in idx[idx.report == "Excel"].iterrows():
    if not os.path.exists(r.file): continue
    from openpyxl.reader.excel import ExcelReader
    rd = ExcelReader(r.file, read_only=True); rd.read_properties = lambda: None; rd.read(); wb = rd.wb
    src = f"https://www.askhys.net/SurveyResults/GetReport?year={r.year}&reportLevel={r.askhys_id}&reportLable=Excel"
    for ws in wb.worksheets:
        gm = re.match(r"Grade (\d+)", ws.title)
        if not gm: continue
        grade = gm.group(1)
        q = {}
        for row in ws.iter_rows(values_only=True):
            if not (isinstance(row[0], int) and row[3]): continue
            var = str(row[1]).strip(); qt = str(row[3]).strip(); resp = str(row[5]).strip(); tot = row[6]; p = row[9]
            if not isinstance(p, (int, float)): continue
            q.setdefault((var, qt), []).append((resp, tot, p))
        for (var, qt), opts in q.items():
            for item, (pat, rule) in ITEMS.items():
                if not re.search(pat, qt, re.I): continue
                tot = opts[0][1]
                if rule == "yes":
                    v = [p for resp, _, p in opts if resp.lower() == "yes"]
                    if v: add(r.year, r.geo, r["name"], grade, item, v[0] * 100, tot, src)
                elif rule == "not0":
                    v = [p for resp, _, p in opts if resp.startswith("0 ")]
                    if v: add(r.year, r.geo, r["name"], grade, item, (1 - v[0]) * 100, tot, src)
                elif rule == "3plus":
                    v = sum(p for resp, _, p in opts if re.match(r"^(3|4|5)", resp))
                    add(r.year, r.geo, r["name"], grade, item, v * 100, tot, src, "sum of 3, 4, 5+ hours per day")
                elif rule == "daily":
                    v = sum(p for resp, _, p in opts if re.search(r"once a day|several times a day|once an hour|more than once an hour", resp, re.I))
                    add(r.year, r.geo, r["name"], grade, item, v * 100, tot, src, "sum of about once a day / several times a day / about once an hour / more than once an hour")
                break
# ---------- PDF / TXT ----------
def parse_text(text):
    """Return dict item -> list of (colvalues[list of (pct, n or None)]) parsed from a HYS frequency report text."""
    lines = [l.strip() for l in text.split("\n")]
    res = {}
    for i, l in enumerate(lines):
        if not re.match(r"^\d{1,3}\.", l): continue
        # gather question block: question lines until first response line 'a.'
        qlines = [l]; k = i + 1
        while k < len(lines) and not re.match(r"^[a-h]\.\s", lines[k]) and k < i + 10:
            qlines.append(lines[k]); k += 1
        qtext = " ".join(l for l in qlines if not re.match(r"^(Grade \d+( Grade \d+)*|% \(± CI\).*|Your Students.*|Statewide.*)$", l))
        ns = re.findall(r"\(n=([\d,]+)\)", qtext)
        resp = []
        while k < len(lines) and re.match(r"^[a-h]\.\s", lines[k]):
            resp.append(lines[k]); k += 1
        for item, (pat, rule) in ITEMS.items():
            if not re.search(pat, qtext, re.I): continue
            def vals(line):
                # tokens: 'xx.x%' or '**' (suppressed) or '--'
                toks = re.findall(r"(\d+\.\d%|\*\*|--|N/A)", re.sub(r"\(±[\d.]+\)", "", line))
                return [pct(t) if t.endswith("%") else None for t in toks]
            if rule == "yes":
                ln = [x for x in resp if re.match(r"^[a-h]\.\s+Yes\b", x, re.I)]
                if ln: res[item] = (vals(ln[0]), ns)
            elif rule == "not0":
                ln = [x for x in resp if re.match(r"^[a-h]\.\s+0 times", x, re.I)]
                if ln: res[item] = ([None if v is None else 100 - v for v in vals(ln[0])], ns)
            elif rule == "3plus":
                sel = [vals(x) for x in resp if re.match(r"^[a-h]\.\s+(3|4|5)", x)]
                if sel:
                    res[item] = ([None if any(s[c] is None for s in sel) else sum(s[c] for s in sel) for c in range(len(sel[0]))], ns)
            elif rule == "daily":
                sel = [vals(x) for x in resp if re.search(r"once a day|several times a day|once an hour|more than once an hour", x, re.I)]
                if sel:
                    res[item] = ([None if any(s[c] is None for s in sel) else sum(s[c] for s in sel) for c in range(len(sel[0]))], ns)
            break
    return res
def parse_txt2010(text):
    lines = [l.strip() for l in text.split("\n")]
    res = {}
    i = 0
    while i < len(lines):
        l = lines[i]
        if not re.match(r"^\d{1,3}\.\t", l): i += 1; continue
        qtext = l.split("\t", 1)[1]
        ns = []; k = i + 1
        while k < len(lines) and not re.match(r"^[a-h]\.\s", lines[k]) and k < i + 8:
            m = re.match(r"^\(n\s*=\s*([\d,]+)\)$", lines[k].replace("\xa0", " "))
            if m: ns.append(m.group(1))
            k += 1
        resp = []  # (label, [local, state])
        while k < len(lines) and not re.match(r"^\d{1,3}\.\t", lines[k]):
            if re.match(r"^[a-h]\.\s", lines[k]):
                lab = lines[k]; vals = []; k += 1
                while k < len(lines) and not re.match(r"^[a-h]\.\s", lines[k]) and not re.match(r"^\d{1,3}\.\t", lines[k]) and len(vals) < 2:
                    t = lines[k].replace("%", "").strip()
                    if re.match(r"^\d+\.\d$", t): vals.append(float(t))
                    elif t in ("**", "--", "NA", "N/A", "*"): vals.append(None)
                    k += 1
                resp.append((lab, vals))
            else: k += 1
        for item, (pat, rule) in ITEMS.items():
            if not re.search(pat, qtext, re.I): continue
            if rule == "yes":
                v = [x for lab, x in resp if re.match(r"^[a-h]\.\s+Yes\b", lab, re.I)]
                if v: res[item] = (v[0], ns)
            elif rule == "not0":
                v = [x for lab, x in resp if re.match(r"^[a-h]\.\s+0 times", lab, re.I)]
                if v: res[item] = ([None if a is None else 100 - a for a in v[0]], ns)
            elif rule == "3plus":
                sel = [x for lab, x in resp if re.match(r"^[a-h]\.\s+(3|4|5)", lab)]
                if sel: res[item] = ([None if any(x[c] is None for x in sel if c < len(x)) else sum(x[c] for x in sel if c < len(x)) for c in range(2)], ns)
            break
        i = k
    return res
for _, r in idx[idx.report != "Excel"].iterrows():
    f = r.file
    if r.year == 2010:
        f = f"{D}/doc2010/" + os.path.basename(f).replace(".pdf", ".txt")
    if not os.path.exists(f): print("missing", f); continue
    src = f"https://www.askhys.net/SurveyResults/GetReport?year={r.year}&reportLevel={r.askhys_id}&reportLable={r.report}"
    try:
        if f.endswith(".txt"):
            text = open(f, encoding="utf-8", errors="ignore").read()
        else:
            with pdfplumber.open(f) as pdf:
                text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    except Exception as e:
        fails.append((f, str(e))); continue
    res = parse_txt2010(text) if f.endswith(".txt") else parse_text(text)
    if r.report.startswith("Multi-grade"):
        grades = ["6", "8", "10", "12"] if "12" in r.report else ["6", "8", "10"]
    else:
        grades = [re.sub(r"\D", "", r.report)]  # single grade: first column = local, second = statewide
    for item, (v, ns) in res.items():
        for ci, grade in enumerate(grades):
            if ci < len(v) and v[ci] is not None:
                n = int(ns[ci].replace(",", "")) if ci < len(ns) else None
                add(r.year, r.geo, r["name"], grade, item, v[ci], n, src)
    if not res: print("no items", f)
df = pd.DataFrame(out).drop_duplicates(["geography_type", "geography_name", "year", "grade_or_age", "item"])
df.to_csv(f"{ROOT}/data/compiled/state_surveys/wa_hys_county.csv", index=False)
print(df.groupby(["item", "year"]).size().unstack(fill_value=0))
print(df[(df.geography_name=="King County")&(df.grade_or_age=="10")].pivot_table(index="item", columns="year", values="value_pct"))
if fails: raise SystemExit(f"{len(fails)} report files could not be read: " + "; ".join(f"{a}: {b}" for a, b in fails))
