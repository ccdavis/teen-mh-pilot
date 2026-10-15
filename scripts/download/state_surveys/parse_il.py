"""Illinois Youth Survey county frequency reports (PDF, 2018-2024; grades 8/10/12 columns as '% N')."""
import re, glob, os, pandas as pd, pdfplumber
ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[3]); D = f"{ROOT}/data/external/state_surveys/il"; fails = []
WORD = {"sad_hopeless": "IYS: During the past 12 months did you ever feel so sad or hopeless almost every day for two weeks or more in a row that you stopped doing some usual activities (% yes)",
        "considered_suicide": "IYS: During the past 12 months did you ever seriously consider attempting suicide (% yes; asked of grades 10/12 only)"}
out = []
for f in sorted(glob.glob(f"{D}/iys_*.pdf")):
    m = re.match(r"iys_(\d{4})_(.+)\.pdf", os.path.basename(f)); y = int(m.group(1)); county = m.group(2).replace("_", " ")
    county = re.sub(r" \d$", "", county)
    try:
        with pdfplumber.open(f) as pdf: pages = [(p.extract_text() or "") for p in pdf.pages]
    except Exception as e: fails.append((f, str(e))); continue
    got = False
    for t in pages:
        if "sad or hopeless" not in t: continue
        lines = [l.strip() for l in t.split("\n")]
        grades = None
        for i, l in enumerate(lines):
            gm = re.fullmatch(r"((?:6th|8th|10th|12th)(?: (?:6th|8th|10th|12th))*)", l)
            if gm and i + 1 < len(lines) and lines[i + 1].startswith("%"):
                grades = [g.replace("th", "") for g in gm.group(1).split()]
            if grades is None: continue
            def take(vals_line, item):
                toks = re.findall(r"(\d+%|N/A)\s*(\d[\d,]*|N/A)?", vals_line)
                for gi, (p, n) in enumerate(toks[:len(grades)]):
                    if p == "N/A": continue
                    out.append(dict(state="IL", geography_type="county", geography_name=county + " County" if "Chicago" not in county else county, geography_fips=None,
                                    year=y, grade_or_age=grades[gi], sex="all", item=item, value_pct=float(p[:-1]),
                                    n=int(n.replace(",", "")) if n and n != "N/A" else None,
                                    source_url="https://iys.cprd.illinois.edu/results/county", note=WORD[item] + " | percent rounded to integer in source; N = number answering yes"))
            if l.startswith("Seriously consider attempting suicide"):
                take(l, "considered_suicide"); got = True
            if l.startswith("Feel so sad or hopeless"):
                vl = l if re.search(r"\d+%", l) else lines[i + 1]
                take(vl, "sad_hopeless"); got = True
    if not got: print("no items", os.path.basename(f))
df = pd.DataFrame(out).drop_duplicates(["geography_name", "year", "grade_or_age", "item"])
df.to_csv(f"{ROOT}/data/compiled/state_surveys/il_iys_county.csv", index=False)
print(df.groupby(["item", "year"]).size().unstack(fill_value=0))
print(df[df.item=="sad_hopeless"].pivot_table(index="geography_name", columns=["year"], values="value_pct", aggfunc="mean").head(8))
if fails: raise SystemExit(f"{len(fails)} report files could not be read: " + "; ".join(f"{a}: {b}" for a, b in fails))
