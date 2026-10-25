"""Parse the Monitoring the Future data volumes ("Questionnaire Responses from the Nation's High School Seniors", 1996-2012 PDFs in
data/external/mtf/datavolumes/, fetched by fetch_datavolumes.py) into item-level percentage distributions for 12th graders.

Table format (identical 1996-2012, "Introduction to the Table Format and Conventions" in each volume): every questionnaire item is
printed as a question line ("E13: About how many hours do you spend in an average week on all your homework ..."), one line per
response category ("3. 5-9 hours 19.7 19.8 19.3 ...") with one weighted percentage per column, and a trailer line
("Item 7640 Subject B01 N 2073 952 1059 ...") giving the study's permanent item reference number, subject codes and the weighted
number answering per column. Columns are Total, Sex (M, F), Race (White, Black[, Hispanic from 2005]), Region (NE, NC, S, W), College
plans (Yes, No) and lifetime illicit drug use groups; the "N (Weighted No. of Cases):" header of each page gives the column count.
"-" means 0.0 and "*" means less than 0.05 percent (both stored as 0.0). The same item can appear on several questionnaire forms
(independent random sixths of the sample), so rows carry the form; the analysis pools forms weighting by N.

Outputs: data/extracts/mtf/datavolume_items_<year>.parquet (every item, gitignored cache) and
data/compiled/mtf/mtf_published_trends.csv (the items in TARGET_ITEMS: grade, year, form, item_ref, item_code, wording,
response_code, response_label, pct_total, pct_male, pct_female, n_total, n_male, n_female, source_url, pdf_page).

Usage: uv run python scripts/download/mtf/parse_datavolumes.py [--cache-only] [--years 1996 2012]
"""
import re, json, sys, pathlib, argparse
ROOT = pathlib.Path(__file__).resolve().parents[3]; RAW = ROOT/"data/external/mtf/datavolumes"; EXT = ROOT/"data/extracts/mtf"; OUT = ROOT/"data/compiled/mtf"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from fetch_datavolumes import CAPTURES
# item reference numbers (permanent across years; printed in the "Item NNNNN" trailer) and the series label used downstream
INTERNET_ITEMS = {29625: "social_network_freq", 31680: "internet_hours_week", 31990: "games_hours_week", 29930: "computer_hours_week"}  # Form 2 items A02Q, E08, E09, E07 (2009-2012 volumes)
TARGET_ITEMS = {
    1190: "happiness", 6840: "life_satisfaction", 12620: "satisfied_with_self", 12650: "lonely", 12660: "not_much_proud", 12680: "no_good_at_all",
    12690: "left_out", 12720: "cant_do_anything_right", 12750: "life_not_useful", 23700: "life_meaningless", 23710: "enjoy_life", 23720: "future_hopeless",
    23730: "good_to_be_alive", 20780: "sleep_7h", 20790: "less_sleep_than_should", 5820: "watch_tv_freq", 5920: "friends_informal_freq", 7640: "homework_hours",
    620: "evenings_out", 630: "dating_freq", 590: "work_hours", 10550: "tv_hours_weekday",
    # internet / social networking items (added to the 12th-grade forms in the 2000s; reference numbers confirmed from the 2009-2012 volumes)
    **INTERNET_ITEMS,
}
def page_texts(year):
    """Text of every page (cached as JSON in data/extracts/mtf/)."""
    EXT.mkdir(parents=True, exist_ok=True); c = EXT/f"datavolume_pages_{year}.json"
    if c.exists(): return json.load(open(c))
    import pdfplumber
    with pdfplumber.open(RAW/f"{year}dv.pdf") as pdf: pages = [(p.extract_text() or "") for p in pdf.pages]
    json.dump(pages, open(c, "w")); return pages
HDR = re.compile(r"^(DESCRIPTIVE RESULTS|\d+ MONITORING THE FUTURE|TOTAL SEX RACE|PLANS\?|QUESTIONNAIRE FORM|\d{4} M F |Only oin|% of Weighted Total|Hispanic|Her-|Few More|None Mari)")
NCASES = re.compile(r"^N \(Weighted No\. of Cases\):\s*(.*)$"); FORM = re.compile(r"QUESTIONNAIRE FORM (\d)(?:-(\d))?")
QLINE = re.compile(r"^([A-E]\d{2,3}[A-Z]{0,2}):\s*(.*)$")  # Form 1 uses three-digit question numbers (A001, B101F)
RLINE = re.compile(r"^(\d{1,2})\.\s+(.*)$"); TRAIL = re.compile(r"^Item (\d+) Subject (.*?) N ((?:[\d,]+\s*)+)$")
NUM = re.compile(r"^(?:\d+(?:\.\d+)?|-|\*)$")
def val(t): return 0.0 if t in ("-", "*") else float(t)
def parse_year(year):
    pages = page_texts(year); rows = []; form = None; ncol = None; cur = None; stem = None; resp = []
    def flush(trailer_ref, subj, ns, pg):
        if cur is None or not resp: return
        wording = (stem[1] + " " if stem and cur[0].startswith(stem[0]) and cur[0] != stem[0] else "") + cur[1]
        for code, lab, vals in resp:
            rows.append(dict(grade=12, year=year, form=form, item_ref=int(trailer_ref), item_code=cur[0], subject=subj, wording=re.sub(r"\s+", " ", wording).strip(),
                             response_code=int(code), response_label=lab.strip(), pct_total=vals[0], pct_male=vals[1], pct_female=vals[2],
                             n_total=ns[0] if ns else None, n_male=ns[1] if len(ns) > 1 else None, n_female=ns[2] if len(ns) > 2 else None, pdf_page=pg))
    for pi, text in enumerate(pages, start=1):
        if "DESCRIPTIVE RESULTS" not in text and "Item " not in text: continue
        for line in text.split("\n"):
            line = line.strip()
            if not line: continue
            m = FORM.search(line)
            if m and "QUESTIONNAIRE FORM" in line: form = int(m.group(1)) if not m.group(2) else 0; continue  # 0 = core items printed for forms 1-6 together
            m = NCASES.match(line)
            if m: ncol = len(m.group(1).split()); continue
            if HDR.match(line): continue
            m = TRAIL.match(line)
            if m:
                ns = [int(x.replace(",", "")) for x in m.group(3).split()]; flush(m.group(1), m.group(2).strip(), ns, pi); cur = None; resp = []; continue
            m = QLINE.match(line)
            if m:
                if cur is not None and not resp: stem = cur          # previous code line had no responses: it is a stem for sub-items
                cur = (m.group(1), m.group(2)); resp = []; continue
            m = RLINE.match(line)
            if m and cur is not None and ncol:
                toks = m.group(2).split()
                if len(toks) > ncol and all(NUM.match(t) for t in toks[-ncol:]):
                    resp.append((m.group(1), " ".join(toks[:-ncol]), [val(t) for t in toks[-ncol:]])); continue
            if cur is not None and not resp: cur = (cur[0], cur[1] + " " + line)   # wrapped question text
            elif cur is not None and resp and not RLINE.match(line) and len(line) < 60 and not re.search(r"\d+\.\d", line):
                c, lab, v = resp[-1]; resp[-1] = (c, lab + " " + line, v)            # wrapped response label
    return rows
if __name__ == "__main__":
    import pandas as pd
    ap = argparse.ArgumentParser(); ap.add_argument("--cache-only", action="store_true"); ap.add_argument("--years", nargs="*", type=int); a = ap.parse_args()
    years = a.years or sorted(CAPTURES); allrows = []
    for y in years:
        if a.cache_only: page_texts(y); print(y, "cached", flush=True); continue
        r = parse_year(y); df = pd.DataFrame(r); df.to_parquet(EXT/f"datavolume_items_{y}.parquet", index=False)
        print(f"{y}: {len(df):,} rows, {df.item_ref.nunique()} items, forms {sorted(df.form.dropna().unique())}, target items found: {sorted(set(df.item_ref) & set(TARGET_ITEMS))}", flush=True); allrows.append(df)
    if not a.cache_only:
        D = pd.concat(allrows); T = D[D.item_ref.isin(TARGET_ITEMS)].copy(); T["series"] = T.item_ref.map(TARGET_ITEMS)
        T["source_url"] = T.year.map(lambda y: f"https://web.archive.org/web/{CAPTURES[y][1]}/{CAPTURES[y][0]}")
        OUT.mkdir(parents=True, exist_ok=True); T.to_csv(OUT/"mtf_published_trends.csv", index=False)
        print(T.groupby(["series"]).year.agg(["min", "max", "nunique"]).to_string()); print("wrote", OUT/"mtf_published_trends.csv", len(T), "rows")
