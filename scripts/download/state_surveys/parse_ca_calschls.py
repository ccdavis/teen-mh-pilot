"""California Healthy Kids Survey county 'Main Report' PDFs (WestEd, CalSCHLS report search; downloaded by ca_calschls_download.py).
Extracts chronic sad/hopeless (table 'Chronic Sad or Hopeless Feelings, Past 12 Months', % Yes) and considered suicide ('Seriously
Considered Attempting Suicide, Past 12 Months', % Yes) by grade (7, 9, 11, NT) and, from the 'Social and Emotional Health by Gender' table,
by sex (Male / Female; the non-binary and 'something else' rows are not kept). Values are read by x-position against the Grade 7 / 9 / 11 /
NT column headers because a cell is blank (or a dash) when fewer than 10 students answered. Report windows are two school years
(2019/2021 = 2019-20 + 2020-21); `year` = the window's end year, as in parse_ca.py (kidsdata). Output: appended to ca_chks_county.csv, which
parse_ca.py writes from the kidsdata exports for 2013-2019: for 2019 and earlier, where both exist, the kidsdata row is kept and the report
value is written to data/compiled/state_surveys/ca_chks_source_overlap.csv for comparison. Run parse_ca.py first, then this script.
Candidate pages are located with pymupdf (fast text search); word positions on those pages come from pdfplumber."""
import re, glob, os, pandas as pd, pdfplumber, pymupdf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]; D = ROOT/"data/external/state_surveys/ca/calschls"; C = ROOT/"data/compiled/state_surveys"
WORD = {"sad_hopeless": "CHKS: during the past 12 months, did you ever feel so sad or hopeless almost every day for two weeks or more that you stopped doing some usual activities? (% yes)",
        "considered_suicide": "CHKS: during the past 12 months, did you ever seriously consider attempting suicide? (% yes)"}
TITLES = {"sad_hopeless": "chronicsadorhopelessfeelings,past12months", "considered_suicide": "seriouslyconsideredattemptingsuicide,past12months"}
GENDER = {"sad_hopeless": "experiencedchronicsadness/hopelessness", "considered_suicide": "consideredsuicide"}
GRADES = ["7", "9", "11", "NT"]
def squash(s): return re.sub(r"\s+", "", s).lower()
def lines_with_pos(page):
    """group words into lines by their top coordinate; return [(top, [(x0, x1, text), ...]), ...]"""
    rows = {}
    for w in page.extract_words():
        rows.setdefault(round(w["top"] / 3), []).append((w["x0"], w["x1"], w["text"]))
    return [(k * 3, sorted(v)) for k, v in sorted(rows.items())]
def grade_columns(line):
    """x-centre of each grade header on a line like 'Grade 7 Grade 9 Grade 11 NT' (words may be split or fused)"""
    if not squash(" ".join(t for _, _, t in line)).startswith("grade7"): return None
    cols, i = {}, 0
    while i < len(line):
        x0, x1, t = line[i]
        if t.lower() == "grade" and i + 1 < len(line): cols[line[i+1][2]] = (x0 + line[i+1][1]) / 2; i += 2; continue
        m = re.match(r"grade(\d+)$", t.lower())
        if m: cols[m.group(1)] = (x0 + x1) / 2
        elif t.upper() == "NT": cols["NT"] = (x0 + x1) / 2
        i += 1
    return cols if set(cols) == set(GRADES) else None
def assign(words, cols):
    """map numeric words to the nearest grade column (a blank or dash cell leaves that grade missing)"""
    out = {}
    for x0, x1, t in words:
        if not re.fullmatch(r"\d+", t): continue
        g = min(cols, key=lambda k: abs(cols[k] - (x0 + x1) / 2))
        if abs(cols[g] - (x0 + x1) / 2) < 30: out[g] = float(t)
    return out
rows = []
for f in sorted(glob.glob(str(D/"*_Sec_CHKS.pdf"))):
    m = re.match(r"(.+)_County_(\d{2})(\d{2})_Sec_CHKS\.pdf", os.path.basename(f))
    if not m: print("skip", f); continue
    county = m.group(1).replace("_", " ") + " County"; y0, y1 = 2000 + int(m.group(2)), 2000 + int(m.group(3)); win = f"{y0}-{str(y0+1)[2:]} and {y1-1}-{str(y1)[2:]}"
    doc = pymupdf.open(f); cand = []
    for i, pg in enumerate(doc):
        t = squash(pg.get_text())
        if (any(k in t for k in TITLES.values()) and "question" in t) or ("socialandemotionalhealthbygender" in t and any(k in t for k in GENDER.values())): cand.append(i)
    doc.close(); got = set()
    with pdfplumber.open(f) as pdf:
        for i in cand:
            L = lines_with_pos(pdf.pages[i]); cols = None; block = None; in_gender = False
            for top, line in L:
                s = squash(" ".join(w[2] for w in line))
                c = grade_columns(line)
                if c: cols = c; continue
                if "socialandemotionalhealthbygender" in s: in_gender = True; block = None; continue
                if in_gender:
                    if re.match(r"^(male|female)", s):
                        if block in GENDER and cols:
                            sx = "male" if s.startswith("male") else "female"
                            for g, v in assign(line[1:], cols).items(): rows.append(dict(county=county, year=y1, grade=g, sex=sx, item=block, value=v, window=win, file=os.path.basename(f))); got.add((block, sx))
                    elif re.match(r"^(nonbinary|somethingelse|transgender)", s): pass
                    elif re.match(r"^[a-z]", s):
                        block = next((it for it, k in GENDER.items() if s.startswith(k)), None)
                    continue
                hit = next((it for it, k in TITLES.items() if s.startswith(k)), None)
                if hit: block = hit; continue
                if block in TITLES and s.startswith("yes") and cols:
                    for g, v in assign(line[1:], cols).items(): rows.append(dict(county=county, year=y1, grade=g, sex="all", item=block, value=v, window=win, file=os.path.basename(f))); got.add((block, "all"))
                    block = None
    if ("sad_hopeless", "all") not in got or ("considered_suicide", "all") not in got: print("missing grade table:", os.path.basename(f), sorted(got))
R = pd.DataFrame(rows).drop_duplicates(["county", "year", "grade", "sex", "item"])
print(R.groupby(["item", "sex", "year"]).county.nunique().unstack(fill_value=0))
# merge with the kidsdata extract written by parse_ca.py
K = pd.read_csv(C/"ca_chks_county.csv", dtype={"geography_fips": str}); K = K[~K.note.str.contains("CalSCHLS county Main Report", na=False)]
fips = K[K.geography_type == "county"].drop_duplicates("geography_name").set_index("geography_name").geography_fips.to_dict()
R["geography_fips"] = R.county.map(fips)
if R.geography_fips.isna().any(): print("counties not in kidsdata (FIPS filled by combine.py):", sorted(R[R.geography_fips.isna()].county.unique()))
new = pd.DataFrame(dict(state="CA", geography_type="county", geography_name=R.county, geography_fips=R.geography_fips, year=R.year, grade_or_age=R.grade, sex=R.sex,
                        item=R.item, value_pct=R.value, n=None, source_url="https://calschls.org/reports-data/search-lea-reports/",
                        note=[f"{WORD[it]}; pooled school years {w}; CalSCHLS county Main Report {fn} (WestEd); percent rounded to integers" for it, w, fn in zip(R.item, R.window, R.file)]))
key = ["geography_name", "year", "grade_or_age", "sex", "item"]
both = new.merge(K[key + ["value_pct"]], on=key, suffixes=("_report", "_kidsdata"))
if len(both):
    d = (both.value_pct_report - both.value_pct_kidsdata).abs()
    print(f"overlap with kidsdata (2015-2019): {len(both)} cells; mean |diff| {d.mean():.2f} pp, within 1 pp: {(d <= 1).mean():.1%}, within 2 pp: {(d <= 2).mean():.1%}, max {d.max():.1f} pp")
    both[key + ["value_pct_kidsdata", "value_pct_report"]].to_csv(C/"ca_chks_source_overlap.csv", index=False)
keep = new.merge(K[key].assign(_k=1), on=key, how="left"); new = new[keep._k.isna().values]
out = pd.concat([K, new], ignore_index=True).sort_values(["geography_name", "item", "sex", "year", "grade_or_age"])
out.to_csv(C/"ca_chks_county.csv", index=False)
print("ca_chks_county.csv rows:", len(out)); print(out[out.geography_type == "county"].groupby(["item", "sex", "year"]).geography_name.nunique().unstack(fill_value=0))
