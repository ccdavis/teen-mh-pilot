"""Pennsylvania Youth Survey county profile reports (Bach Harrison PDFs). Each report's 'Suicide risk' table gives
County y-4, County y-2, County y, State y for 5 items x grades 6/8/10/12/All; 2023 reports also have a 'Mental Health Concerns' table."""
import re, glob, os, pandas as pd, pdfplumber
D = "data/external/state_surveys/pa"
SUIC = ["sad_hopeless", "considered_suicide", "planned_suicide", "attempted_suicide", "suicide_attempt_injury"]
SUIC_W = {"sad_hopeless": "PAYS: During the past 12 months did you ever feel so sad or hopeless almost every day for two weeks or more in a row that you stopped doing some usual activities? (% yes)",
          "considered_suicide": "PAYS: During the past 12 months did you ever seriously consider attempting suicide? (% yes)",
          "planned_suicide": "PAYS: made a plan about how you would attempt suicide (% yes)",
          "attempted_suicide": "PAYS: did you actually attempt suicide (% yes / 1+ times)",
          "suicide_attempt_injury": "PAYS: attempt resulted in injury needing medical treatment (2023: % of attempters)"}
MH23 = ["self_harm", "mental_health_good", "depressed_sad_most_days", "life_not_worth_it", "no_good_at_all", "failure"]
MH23_W = {"self_harm": "PAYS: self-harm (cutting, scraping, burning) 1+ times in past 12 months",
          "mental_health_good": "PAYS 2023+: My overall mental health in the past month has been good (% agree)",
          "depressed_sad_most_days": "PAYS: In the past 12 months have you felt depressed or sad MOST days, even if you feel OK sometimes? (% yes)",
          "life_not_worth_it": "PAYS: Sometimes I think that life is not worth it (% agree)",
          "no_good_at_all": "PAYS: At times I think I am no good at all (% agree)",
          "failure": "PAYS: All in all, I am inclined to think that I am a failure (% agree)"}
out = []
def parse_table(lines, start, items, y, county, src, wmap):
    # header line: 'Grade County 2015 County 2017 County 2019 State 2019'
    hdr = None
    for j in range(start, min(start + 6, len(lines))):
        if lines[j].startswith("Grade "):
            hdr = re.findall(r"(County|State)\s*(\d{4})", lines[j].replace("Co 2 u 0 n 1 t 9 y", "County 2019").replace("Co 2 u 0 n 2 t 1 y", "County 2021").replace("Co 2 u 0 n 2 t 3 y", "County 2023"))
            k = j + 1; break
    if not hdr:
        return False
    ncol = len(hdr) // len(items) if len(hdr) >= 4 else 4
    cols = hdr[:ncol] if len(hdr) >= ncol else [("County", str(y - 4)), ("County", str(y - 2)), ("County", str(y)), ("State", str(y))]
    got = False
    for j in range(k, min(k + 8, len(lines))):
        gm = re.match(r"^(6th|8th|10th|12th|All)\s+(.*)$", lines[j])
        if not gm: continue
        grade = gm.group(1).replace("th", "").replace("All", "6-12")
        toks = gm.group(2).split()
        if len(toks) != len(items) * ncol: continue
        for ii, item in enumerate(items):
            for ci, (geo, yy) in enumerate(cols):
                v = toks[ii * ncol + ci]
                if v.lower() == "n/a": continue
                out.append(dict(state="PA", geography_type="county" if geo == "County" else "state", geography_name=county if geo == "County" else "Pennsylvania",
                                geography_fips=None, year=int(yy), grade_or_age=grade, sex="all", item=item, value_pct=float(v), n=None, source_url=src,
                                note=wmap[item] + f" | from {y} county profile report"))
                got = True
    return got
for f in sorted(glob.glob(f"{D}/pays_*.pdf")):
    m = re.match(r"pays_(\d{4})_(.+)\.pdf", os.path.basename(f)); y = int(m.group(1)); name = m.group(2).replace("_", " ")
    if name.lower().startswith("state of"): continue
    county = re.sub(r"\s*(county )?profile report.*$", "", name, flags=re.I).strip()
    county = re.sub(r"\s+\d{4}$", "", county).title() + (" County" if "county" in name.lower() else "")
    src = "https://www.pa.gov/agencies/pccd/programs-and-services/juvenile-justice-and-delinquency-prevention/pays"
    try:
        with pdfplumber.open(f) as pdf: pages = [(p.extract_text() or "") for p in pdf.pages]
    except Exception as e: print("fail", f, e); continue
    got = False
    for t in pages:
        lines = [l.strip() for l in t.split("\n")]
        for i, l in enumerate(lines):
            if l.startswith("So sad stopped doing usual activities Seriously considered suicide"):
                got |= parse_table(lines, i, SUIC, y, county, src, SUIC_W)
            if y >= 2023 and l.startswith("Self-harm (e.g. cutting, scraping, Past month overall mental health is Felt depressed"):
                got |= parse_table(lines, i, MH23, y, county, src, MH23_W)
    if not got: print("no items", os.path.basename(f))
df = pd.DataFrame(out).drop_duplicates(["geography_type", "geography_name", "year", "grade_or_age", "item", "note"])
# where the same county-year-item appears in two reports (e.g. 2019 in both the 2019 and 2023 reports) keep the later report
df["rep"] = df.note.str.extract(r"from (\d{4})").astype(int)
df = df.sort_values("rep").drop_duplicates(["geography_type", "geography_name", "year", "grade_or_age", "item"], keep="last").drop(columns="rep")
df.to_csv("data/compiled/state_surveys/pa_pays_county.csv", index=False)
print(df.groupby(["item", "year"]).size().unstack(fill_value=0))
print(df[(df.item=="sad_hopeless")&(df.grade_or_age=="10")].pivot_table(index="geography_name", columns="year", values="value_pct").head(8))
