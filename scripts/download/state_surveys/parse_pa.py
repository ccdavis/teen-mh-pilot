"""Pennsylvania Youth Survey county profile reports (Bach Harrison PDFs), 2019, 2023 and 2025 editions. Each report's 'Suicide risk' table
gives County y-4, County y-2, County y, State y for 5 items x grades 6/8/10/12/All; the 2023 and 2025 reports also have a 'Mental Health
Concerns' table (6 items; the column order differs between the 2023 and 2025 editions, so the order is read from the table header).
Where a county-year-item appears in two editions (2021 and 2023 are in both the 2023 and 2025 reports) the later edition is kept and the
overlap is written to data/compiled/state_surveys/pa_pays_report_overlap.csv so that revisions between editions are visible."""
import re, glob, os, pandas as pd, pdfplumber
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[3]); D = f"{ROOT}/data/external/state_surveys/pa"; fails = []
SUIC_W = {"sad_hopeless": "PAYS: During the past 12 months did you ever feel so sad or hopeless almost every day for two weeks or more in a row that you stopped doing some usual activities? (% yes)",
          "considered_suicide": "PAYS: During the past 12 months did you ever seriously consider attempting suicide? (% yes)",
          "planned_suicide": "PAYS: made a plan about how you would attempt suicide (% yes)",
          "attempted_suicide": "PAYS: did you actually attempt suicide (% yes / 1+ times; yes/no item from 2023)",
          "suicide_attempt_injury": "PAYS: attempt resulted in injury needing medical treatment (2023+: % of attempters)"}
MH_W = {"self_harm": "PAYS: self-harm (cutting, scraping, burning) 1+ times in past 12 months",
        "mental_health_good": "PAYS 2023+: My overall mental health in the past month has been good (% agree)",
        "depressed_sad_most_days": "PAYS: In the past 12 months have you felt depressed or sad MOST days, even if you feel OK sometimes? (% yes)",
        "life_not_worth_it": "PAYS: Sometimes I think that life is not worth it (% agree)",
        "no_good_at_all": "PAYS: At times I think I am no good at all (% agree)",
        "failure": "PAYS: All in all, I am inclined to think that I am a failure (% agree)"}
# key phrases that identify each column in the table header (position in the header line gives the column order)
SUIC_KEY = {"sad_hopeless": "So sad stopped doing usual activities", "considered_suicide": "Seriously considered suicide", "planned_suicide": "Planned suicide",
            "attempted_suicide": "Attempted suicide", "suicide_attempt_injury": "Needed medical treatment"}
MH_KEY = {"self_harm": "Self-harm", "mental_health_good": "Past month overall mental health", "depressed_sad_most_days": "Felt depressed or sad MOST days",
          "life_not_worth_it": "life is not", "no_good_at_all": "no good at all", "failure": "inclined to think that I"}
out = []
def fix_header(l):
    # pdfplumber interleaves rotated year labels with the word County: 'Co 2 u 0 n 2 t 5 y' = 'County 2025'
    return re.sub(r"Co (\d) u (\d) n (\d) t (\d) y", r"County \1\2\3\4", l)
def item_order(l, keys):
    pos = {it: l.find(k) for it, k in keys.items()}
    return [it for it, p in sorted(pos.items(), key=lambda kv: kv[1])] if all(p >= 0 for p in pos.values()) else None
def parse_table(lines, start, keys, y, county, src, wmap):
    # start = index of the header line that names the items; the 'Grade County yyyy ...' line follows within a few lines
    items = item_order(lines[start], keys)
    if not items: return False
    hdr = None
    for j in range(start, min(start + 6, len(lines))):
        if lines[j].startswith("Grade "):
            hdr = re.findall(r"(County|State)\s*(\d{4})", fix_header(lines[j])); k = j + 1; break
    if not hdr: return False
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
    m = re.match(r"pays_(\d{4})_(.+)\.pdf", os.path.basename(f)); y = int(m.group(1)); name = re.sub(r"^\d{4}\s+", "", m.group(2).replace("_", " "))
    if name.lower().startswith("state of"): continue
    county = re.sub(r"\s*(county )?profile report.*$", "", name, flags=re.I).strip()
    county = re.sub(r"\s+\d{4}$", "", county).title() + (" County" if "county" in name.lower() else "")
    src = "https://www.pa.gov/agencies/pccd/programs-and-services/juvenile-justice-and-delinquency-prevention/pays"
    try:
        with pdfplumber.open(f) as pdf: pages = [(p.extract_text() or "") for p in pdf.pages]
    except Exception as e: fails.append((f, str(e))); continue
    got_s = got_m = False
    for t in pages:
        lines = [l.strip() for l in t.split("\n")]
        for i, l in enumerate(lines):
            if l.startswith("So sad stopped doing usual activities Seriously considered suicide"):
                got_s |= parse_table(lines, i, SUIC_KEY, y, county, src, SUIC_W)
            if y >= 2023 and "Felt depressed or sad MOST days" in l and "Self-harm" in l:
                got_m |= parse_table(lines, i, MH_KEY, y, county, src, MH_W)
    if not got_s: print("no suicide-risk table", os.path.basename(f))
    if y >= 2023 and not got_m: print("no mental-health table", os.path.basename(f))
df = pd.DataFrame(out).drop_duplicates(["geography_type", "geography_name", "year", "grade_or_age", "item", "note"])
df["rep"] = df.note.str.extract(r"from (\d{4})").astype(int)
# overlap between editions: the same county-year-grade-item from two report years
key = ["geography_type", "geography_name", "year", "grade_or_age", "item"]
dup = df[df.duplicated(key, keep=False)].pivot_table(index=key, columns="rep", values="value_pct").reset_index()
reps = [c for c in dup.columns if isinstance(c, int)]
if len(reps) >= 2:
    pairs = [(a, b) for a in reps for b in reps if a < b]
    for a, b in pairs:
        both = dup[dup[a].notna() & dup[b].notna()]
        if len(both): d = (both[b] - both[a]).abs(); print(f"edition overlap {a} vs {b}: {len(both)} cells, {int((d < 0.05).sum())} identical, {int((d >= 0.05).sum())} differ (max |diff| {d.max():.1f} pp)")
    dup.columns = [c if not isinstance(c, int) else f"report_{c}" for c in dup.columns]
    dup.to_csv(f"{ROOT}/data/compiled/state_surveys/pa_pays_report_overlap.csv", index=False)
# where the same county-year-item appears in two reports keep the later report
df = df.sort_values("rep").drop_duplicates(key, keep="last").drop(columns="rep")
df.to_csv(f"{ROOT}/data/compiled/state_surveys/pa_pays_county.csv", index=False)
print(df[df.geography_type == "county"].groupby(["item", "year"]).geography_name.nunique().unstack(fill_value=0))
print(df[(df.item=="sad_hopeless")&(df.grade_or_age=="6-12")&(df.geography_type=="county")].pivot_table(index="geography_name", columns="year", values="value_pct").head(8))
if fails: raise SystemExit(f"{len(fails)} report files could not be read: " + "; ".join(f"{a}: {b}" for a, b in fails))
