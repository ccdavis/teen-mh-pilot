"""Assemble data/compiled/hbsc/hbsc_published_trends.csv."""
import sys, os, re
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from build_published import REPORTS, load_browser, cn, EXT, ROOT, BROWSER_ITEMS
import parse_2001, parse_1998, parse_1994

OUT = f"{ROOT}/data/compiled/hbsc/hbsc_published_trends.csv"
COLS = ["country","wave","year_end","age","sex","item","value_pct","source_doc","source_page_or_table","note"]
DOCS = {r["key"]: r for r in REPORTS}
BROWSER_DOC = "HBSC Data Browser (data-browser.hbsc.org), file wp-content/uploads/csvs/data.csv (downloaded 2026-09-16)"

def browser_rows():
    b = load_browser()
    b["item"] = b.HBSC_id.map({**BROWSER_ITEMS, "lifesat_mean": "life_satisfaction_mean_0_10"})
    b = b[b.item.notna()].copy()
    b["Country"] = b.Country.str.strip().map(cn)
    b["Country"] = b.Country.replace({"HBSC AVERAGE (GENDER)": "HBSC average", "HBSC AVERAGE (TOTAL)": "HBSC average"})
    rows = []
    wave = {"2014": "2013/14", "2018": "2017/18", "2022": "2021/22"}
    for _, r in b.iterrows():
        base = dict(country=r["Country"], wave=wave[r["Survey_year"]], year_end=int(r["Survey_year"]), age=int(r["age"]), item=r["item"],
                    source_doc=BROWSER_DOC, source_page_or_table=f"HBSC_id={r["HBSC_id"]}; Age_group={r["Age_group"]}; Survey_year={r["Survey_year"]}")
        note = "mean Cantril ladder score (0-10), not a percentage" if r["item"].startswith("life_satisfaction_mean") else ""
        if pd.notna(r["Girl"]) and str(r["Girl"]).strip() != "":
            rows.append({**base, "sex": "girl", "value_pct": float(r["Girl"]), "note": note})
        if pd.notna(r["Boy"]) and str(r["Boy"]).strip() != "":
            rows.append({**base, "sex": "boy", "value_pct": float(r["Boy"]), "note": note})
        if pd.notna(r["Age_group_total"]) and str(r["Age_group_total"]).strip() != "":
            rows.append({**base, "sex": "all", "value_pct": float(r["Age_group_total"]), "note": (note + "; " if note else "") + "browser field Age_group_total"})
        elif pd.notna(r["sort_gender"]) and str(r["sort_gender"]).strip() != "" and r["Country"] != "HBSC average":
            rows.append({**base, "sex": "all", "value_pct": float(r["sort_gender"]), "note": (note + "; " if note else "") + "browser field sort_gender (both sexes combined; used by the browser for sorting)"})
    df = pd.DataFrame(rows)
    df["src"] = "browser"
    return df

def pdf_rows():
    raw = pd.read_csv(f"{ROOT}/data/compiled/hbsc/_pdf_chart_raw.csv", dtype=str)
    raw = raw[raw.sex.isin(["girl", "boy", "all"])].copy()
    raw["value"] = pd.to_numeric(raw.value.replace("–", pd.NA), errors="coerce")
    raw = raw[raw.value.notna()]
    raw["colyear"] = raw.colyear.where(raw.colyear.notna(), raw.wave.map({k: str(v["year_end"]) for k, v in DOCS.items()}))
    rows = []
    for _, r in raw.iterrows():
        rep = DOCS[r["wave"]]
        wave = {"2006": "2005/06", "2010": "2009/10", "2014": "2013/14", "2018": "2017/18"}[r["colyear"]]
        note = ""
        if r["wave"] == "2017/18" and r["colyear"] == "2014":
            note = "2014 value as re-published in the 2017/18 report (trend column)"
        rows.append(dict(country=r["country"], wave=wave, year_end=int(r["colyear"]), age=int(float(r["age"])), sex=r["sex"], item=r["item"],
                         value_pct=float(r["value"]), source_doc=rep["doc"], source_page_or_table=f"p.{r["page"]} (PDF page index; chart '{r["title"]}')",
                         note=note, src="pdf_" + r["wave"]))
    return pd.DataFrame(rows)

def main():
    b = browser_rows()
    p = pdf_rows()
    p2001 = parse_2001.parse(); p2001["src"] = "pdf_2001/02"; p2001["note"] = ""
    p1998 = parse_1998.parse(); p1998["src"] = "pdf_1997/98"
    p1998["note"] = p1998.item.map({
        "feel_low_at_least_weekly": "1997/98 definition: feeling low at least once a week (not 'more than once a week'); not directly comparable to feel_low_weekly",
        "like_school": "liking school a lot",
        "schoolwork_pressure_a_lot": "1997/98 figure reports 'pressured A LOT' only (not some/a lot); not comparable to schoolwork_pressure"})
    # primary PDF rows: 2005/06 and 2009/10 everything; 2013/14 high_life_satisfaction (not in browser); 2017/18 nothing (browser has it)
    prim = p[(p.src.isin(["pdf_2005/06", "pdf_2009/10"])) | ((p.src == "pdf_2013/14") & (p.item == "high_life_satisfaction"))]
    cross = p[~p.index.isin(prim.index)]
    p1994 = parse_1994.parse(); p1994["src"] = "pdf_1993/94"
    p1994["note"] = "1993/94 Fig. 6.10 'felt low or depressed once a week or more'; values read by OCR (RapidOCR) from rendered page (min token confidence " + p1994.ocr_conf.round(2).astype(str) + "); not directly comparable to feel_low_weekly"
    p1994 = p1994.drop(columns=["ocr_conf"])
    final = pd.concat([b, prim, p2001, p1998, p1994], ignore_index=True)
    final["note"] = final.note.fillna("")
    # definitions
    defs = {"schoolwork_pressure": "feel pressured by schoolwork 'some' or 'a lot' (%)",
            "multiple_complaints": "2+ of 8 HBSC-SCL health complaints more than once a week in last 6 months (%)",
            "high_life_satisfaction": "Cantril ladder score >= 6 (%)",
            "like_school": "like school 'a lot' (%)",
            "feel_low_weekly": "feeling low more than once a week (%)",
            "feel_nervous_weekly": "feeling nervous more than once a week (%)",
            "problematic_social_media": "Social Media Disorder Scale, 6+ of 9 items (%)",
            "intense_social_media": "continuous/intense online contact: 'almost all the time throughout the day' with at least one friend category (%)"}
    final["note"] = final.apply(lambda r: (defs.get(r["item"], "") + ("; " + r["note"] if r["note"] else "")) if r["item"] in defs else r["note"], axis=1)
    final = final.sort_values(["item", "year_end", "country", "age", "sex"]).reset_index(drop=True)
    dup = final.duplicated(["country", "wave", "age", "sex", "item"], keep=False)
    print("duplicate keys:", dup.sum())
    if dup.sum():
        print(final[dup].sort_values(["country","wave","age","sex","item"]).head(20).to_string())
    final = final.drop_duplicates(["country", "wave", "age", "sex", "item"], keep="first")
    final[COLS].to_csv(OUT, index=False)
    cross[COLS].to_csv(f"{ROOT}/data/compiled/hbsc/hbsc_published_trends_pdf_crosscheck.csv", index=False)
    print("rows:", len(final), "->", OUT)
    cov = final[(final.country != "HBSC average") & (final.sex != "all")].groupby(["item", "wave"]).country.nunique().unstack().fillna(0).astype(int)
    print(cov.to_string())
    return final, cov

if __name__ == "__main__":
    main()
