"""Published MTF year-by-year estimates from open-access papers (PubMed Central), for the years the data volumes do not cover.

Johnson, Staff, Patrick & Schulenberg (2017), "Adolescent adaptation before, during and in the aftermath of the Great Recession in
the USA", Int J Psychol 52(1):9-18, doi:10.1002/ijop.12389, PMC5583705. Table 1 gives, for MTF 8th and 10th graders 1991-2014,
OLS coefficients of each survey year (reference 2008) on self-esteem, depressed mood, risk taking, aggression, property crime, GPA,
time spent on homework (1 = 0 hours ... 7 = 25+ hours per week) and BA-degree expectations, and odds ratios of year on going out at
night for fun at least one evening per week, playing sports or exercising daily, volunteering at least monthly and working for pay.
"ns" cells (p >= .05, point estimate not reported) are stored as missing with ns = 1.

Output: data/compiled/mtf/mtf_johnson2017_year_effects.csv (year, outcome, estimate, ns, type, reference_year, source).
Usage: uv run python scripts/download/mtf/parse_published_papers.py
"""
import re, pathlib, urllib.request, xml.etree.ElementTree as ET, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]; RAW = ROOT/"data/external/mtf/pmc"; OUT = ROOT/"data/compiled/mtf"
URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=5583705&retmode=xml"
def fetch():
    RAW.mkdir(parents=True, exist_ok=True); f = RAW/"PMC5583705.xml"
    if not f.exists(): f.write_bytes(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "teen-mh-pilot/1.0"}), timeout=120).read())
    return f
if __name__ == "__main__":
    root = ET.parse(fetch()).getroot(); tw = root.find(".//table-wrap"); rows = [[" ".join(c.itertext()).strip() for c in tr] for tr in tw.findall(".//tr")]
    hdr = rows[0]; cols = ["Self-esteem", "Depressed mood", "Risk taking", "Aggression", "Property crime", "GPA", "Homework hours (1-7 scale)", "Expects BA degree",
                           "Goes out at night for fun (OR, 1+ evenings/week)", "Plays sports or exercises daily (OR)", "Volunteers at least monthly (OR)", "Works for pay (OR)"]
    out = []
    for r in rows[1:]:
        if not re.match(r"^\d{4}$", r[0]): continue
        y = int(r[0]); vals = r[1:1 + len(cols)]
        if len(vals) < len(cols): vals = vals + [""] * (len(cols) - len(vals))
        for c, v in zip(cols, vals):
            v = v.replace("−", "-").strip(); ns = v.lower() in ("ns", "")
            out.append(dict(year=y, grade="8 and 10 pooled", outcome=c, estimate=None if ns or "reference" in v else float(v), ns=int(ns), type="odds ratio vs 2008" if "(OR" in c else "OLS coefficient vs 2008",
                            reference_year=2008, source="Johnson et al. 2017, Int J Psychol, Table 1, https://pmc.ncbi.nlm.nih.gov/articles/PMC5583705/"))
    D = pd.DataFrame(out); OUT.mkdir(parents=True, exist_ok=True); D.to_csv(OUT/"mtf_johnson2017_year_effects.csv", index=False)
    print(D.pivot(index="year", columns="outcome", values="estimate")[cols[:2] + [cols[6], cols[8]]].to_string()); print("wrote", OUT/"mtf_johnson2017_year_effects.csv", len(D))
