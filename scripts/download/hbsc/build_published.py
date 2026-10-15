"""Build data/compiled/hbsc/hbsc_published_trends.csv from HBSC data-browser CSVs and
international-report PDF charts (2005/06, 2009/10, 2013/14, 2017/18)."""
import re, sys, os
import pandas as pd, pymupdf
sys.path.insert(0, os.path.dirname(__file__))
from chart_extract import find_charts, page_lines, norm_country, KNOWN

ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[2])
EXT = f"{ROOT}/data/external/hbsc"

ITEM_RX = [
    (r"pressured by school ?work|schoolwork pressure", "schoolwork_pressure"),
    (r"like school a lot|liking school", "like_school"),
    (r"high life satisfaction", "high_life_satisfaction"),
    (r"multiple health complaints", "multiple_complaints"),
    (r"feeling low", "feel_low_weekly"),
    (r"feeling nervous", "feel_nervous_weekly"),
    (r"problematic social media", "problematic_social_media"),
    (r"intens\w+ (online|electronic)|continuous online", "intense_social_media"),
]
CN = {"MKD": "North Macedonia", "TFYR Macedonia": "North Macedonia", "Czech Republic": "Czechia", "USA": "United States",
      "Belgium (Flanders)": "Belgium (Flemish)", "Belgium (Wallonia)": "Belgium (French)", "Kyrgyztan": "Kyrgyzstan",
      "HBSC average (gender)": "HBSC average", "HBSC average (total)": "HBSC average", "HBSC AVERAGE (GENDER)": "HBSC average",
      "HBSC AVERAGE (TOTAL)": "HBSC average", "HBSC AVERAGE PREVALENCE": "HBSC average", " Greenland": "Greenland",
      "Germany*": "Germany", "France*": "France", "Russian Federation*": "Russian Federation"}
def cn(c):
    c = c.strip(); return CN.get(c, c)

REPORTS = [
 dict(key="2005/06", year_end=2006, doc="hbsc_2005_06_inequalities.pdf",
      cite="Currie C et al. (eds) (2008). Inequalities in young people's health: HBSC international report from the 2005/2006 survey. WHO Regional Office for Europe.",
      pages=[58,59,66,67,80,81,84,85], upper="girl", lower="boy"),
 dict(key="2009/10", year_end=2010, doc="hbsc_2009_10_social_determinants.pdf",
      cite="Currie C et al. (eds) (2012). Social determinants of health and well-being among young people. HBSC international report from the 2009/2010 survey. WHO Regional Office for Europe.",
      pages=[65,66,73,74,91,92,95,96], upper="girl", lower="boy"),
 dict(key="2013/14", year_end=2014, doc="hbsc_2013_14_growing_up_unequal.pdf",
      cite="Inchley J et al. (eds) (2016). Growing up unequal: gender and socioeconomic differences in young people's health and well-being. HBSC international report from the 2013/2014 survey. WHO Regional Office for Europe.",
      pages=[67,68,75,76,91,92,95,96], upper="girl", lower="boy"),
 dict(key="2017/18", year_end=2018, doc="hbsc_2017_18_vol2_key_data.pdf",
      cite="Inchley J et al. (eds) (2020). Spotlight on adolescent health and well-being. Findings from the 2017/2018 HBSC survey in Europe and Canada. International report. Volume 2. Key data. WHO Regional Office for Europe.",
      pages=[45,46,49,50,61,62,69,70,73,74,129,130,131,132], upper="girl", lower="boy"),
]

def page_item(page):
    t = page.get_text()
    hits = [name for rx, name in ITEM_RX if re.search(rx, t, re.I)]
    # prefer the item that appears in a chart title line
    for rx, name in ITEM_RX:
        for l in page_lines(page):
            if re.search(r"1[135]-year-olds? who", l["text"]):
                # gather this and the next 2 lines' text
                pass
    return hits

def extract_report(rep):
    doc = pymupdf.open(f"{EXT}/{rep['doc']}")
    out = []
    for pn in rep["pages"]:
        page = doc[pn-1]
        lines = page_lines(page)
        # year header positions (2017/18 vol2 has 2014 & 2018 value columns)
        yearhdr = [(l["xc"], l["text"]) for l in lines if l["text"] in ("2014", "2018", "2022") and l["y1"] < 200]
        charts = find_charts(page)
        for ch in charts:
            if ch["title"] is None:  # family-affluence charts have no age title; skip
                continue
            # full title: title line + following lines within 30pt below and overlapping x
            tl = [l for l in lines if l["text"] == ch["title"]]
            title = ch["title"] or ""
            if tl:
                t0 = tl[0]
                for l in lines:
                    if (0 < l["y0"] - t0["y0"] < 32 and l["x0"] < t0["x1"] + 5 and l["x1"] > t0["x0"] - 5 and l is not t0
                            and not re.match(r"^[\d.*–\- ]+$", l["text"]) and norm_country(l["text"]) not in KNOWN):
                        title += " " + l["text"]
            item = None
            for rx, name in ITEM_RX:
                if re.search(rx, title, re.I):
                    item = name; break
            if item is None:  # fall back to page header text
                hdr = " ".join(l["text"] for l in lines if l["y1"] < 60)
                for rx, name in ITEM_RX:
                    if re.search(rx, hdr, re.I):
                        item = name; break
            m = re.search(r"(1[135])-year-old", title)
            age = int(m.group(1)) if m else None
            for name, yc, vals in ch["rows"]:
                if not vals:
                    continue
                # cluster values by x into columns
                vals = sorted(vals)
                cols = []
                if yearhdr:
                    for x, y, v in vals:
                        if cols and abs(x - cols[-1][-1][0]) < 9:
                            cols[-1].append((x, y, v))
                        else:
                            cols.append([(x, y, v)])
                else:
                    cols = [list(vals)]
                for col in cols:
                    xc = sum(c[0] for c in col) / len(col)
                    yr = None
                    if yearhdr:
                        yr = min(yearhdr, key=lambda h: abs(h[0] - xc - 5))[1]
                    col = sorted(col, key=lambda c: c[1])
                    if name == "HBSC average" or name.startswith("HBSC"):
                        pass
                    if len(col) == 1:
                        out.append(dict(country=cn(name), wave=rep["key"], age=age, item=item, sex="all" if "total" in name.lower() or "TOTAL" in name else "?",
                                        value=col[0][2], colyear=yr, page=pn, title=title, n=1))
                    elif len(col) == 2:
                        out.append(dict(country=cn(name), wave=rep["key"], age=age, item=item, sex=rep["upper"], value=col[0][2], colyear=yr, page=pn, title=title, n=2))
                        out.append(dict(country=cn(name), wave=rep["key"], age=age, item=item, sex=rep["lower"], value=col[1][2], colyear=yr, page=pn, title=title, n=2))
                    else:
                        out.append(dict(country=cn(name), wave=rep["key"], age=age, item=item, sex="??", value="|".join(c[2] for c in col), colyear=yr, page=pn, title=title, n=len(col)))
    df = pd.DataFrame(out)
    df["source_doc"] = rep["doc"]
    return df

BROWSER_ITEMS = {"sch_pressure": "schoolwork_pressure", "sch_satis": "like_school", "multihealth": "multiple_complaints",
                 "d_feellow": "feel_low_weekly", "d_nervous": "feel_nervous_weekly", "SMPdum": "problematic_social_media",
                 "EMC_intensive": "intense_social_media"}

def load_browser():
    d = pd.read_csv(f"{EXT}/data_browser_data.csv", dtype=str).dropna(how="all")
    d = d[d.HBSC_id.notna() & (d.HBSC_id != "HBSC_id")].copy()
    d["Country"] = d.Country.map(cn)
    d["age"] = d.Age_group.str.extract(r"(\d+)").astype(int)
    d["item"] = d.HBSC_id.map(BROWSER_ITEMS)
    return d

def validate(df):
    b = load_browser()
    b = b[b.item.notna()]
    long = pd.concat([
        b.rename(columns={"Girl": "bval"}).assign(sex="girl")[["Country", "Survey_year", "age", "item", "sex", "bval"]],
        b.rename(columns={"Boy": "bval"}).assign(sex="boy")[["Country", "Survey_year", "age", "item", "sex", "bval"]]])
    long["Survey_year"] = long.Survey_year.astype(int)
    x = df[(df.n == 2) & (~df.country.str.startswith("HBSC"))].copy()
    x["yr"] = x.colyear.fillna(x.wave.map({"2013/14": "2014", "2017/18": "2018"})).astype(float)
    x = x[x.yr.isin([2014, 2018])]
    m = x.merge(long, left_on=["country", "yr", "age", "item", "sex"], right_on=["Country", "Survey_year", "age", "item", "sex"], how="left")
    m["ok"] = pd.to_numeric(m.value, errors="coerce") == pd.to_numeric(m.bval, errors="coerce")
    print("\nVALIDATION vs data browser (as-mapped upper=girl, lower=boy):")
    print(m.groupby(["wave", "yr", "item"]).agg(n=("ok", "size"), matched=("bval", lambda s: s.notna().sum()), ok=("ok", "sum")).to_string())
    bad = m[m.bval.notna() & ~m.ok]
    print("mismatches sample:"); print(bad[["country", "wave", "yr", "age", "item", "sex", "value", "bval", "page"]].head(25).to_string())
    print("unmatched countries:", sorted(m[m.bval.isna()].country.unique()))


if __name__ == "__main__":
    dfs = [extract_report(r) for r in REPORTS]
    df = pd.concat(dfs, ignore_index=True)
    df.to_csv(f"{ROOT}/data/compiled/hbsc/_pdf_chart_raw.csv", index=False)
    print(df.groupby(["wave", "item", "age"]).size().to_string())
    print("\nproblem rows (n!=2 non-average):")
    print(df[(df.n != 2) & (~df.country.str.startswith("HBSC"))].to_string()[:3000])
    validate(df)
    print("\nmissing item/age:", df[df.item.isna() | df.age.isna()].groupby(["wave","page","title"]).size())

