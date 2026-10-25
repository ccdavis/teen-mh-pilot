"""County youth (10-19) suicide deaths and population by pooled period from CDC WONDER's web interface, driven with Playwright.
The WONDER API refuses sub-national geography, but the request form allows county tables (counts under 10 are suppressed per row).
Usage (repository root): uv run python scripts/download/broadband/wonder_county_suicide.py [--only D76|D157] [--pause 20]
Databases: D76 = Underlying Cause of Death 1999-2020 (https://wonder.cdc.gov/ucd-icd10.html), used for the periods 2003-07, 2008-12,
2013-17; D157 = Underlying Cause of Death 2018-2023, single race (https://wonder.cdc.gov/ucd-icd10-expanded.html), used for 2018-22.
Each query: Group by County (and Sex), ages 10-14 + 15-19 (five-year groups), Injury Intent = Suicide (WONDER's intent grouping is
*U03, X60-X84, Y87.0), years of the period, all states, measures deaths / population / crude rate, "show suppressed" and "show zero"
on, export as tab-separated text. The I Agree button on the landing page is clicked once per query (the agreement is re-shown per
session). Ten queries in total (1999-2002 is pulled for all sexes only, as a pre-trend period).
--compile parses the saved exports into data/compiled/broadband/county_youth_suicide_periods.csv (fips, period, sex, deaths, population,
rate_per100k = deaths / summed annual population x 100,000 (an average annual rate), suppressed flag, database), with a pause between them; outputs go to data/external/broadband/wonder/<db>_<period>_<all|sex>.txt.
"""
import argparse, io, pathlib, re, sys, time
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]; OUT = ROOT/"data/external/broadband/wonder"; OUT.mkdir(parents=True, exist_ok=True)
DBS = {"D76": ("https://wonder.cdc.gov/ucd-icd10.html", ["1999-2002", "2003-2007", "2008-2012", "2013-2017"]), "D157": ("https://wonder.cdc.gov/ucd-icd10-expanded.html", ["2018-2022"])}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
def codes(pg):
    """Variable codes from the labels of the first group-by select (they differ between databases: D76.V9-level2 vs D157.V9-level2 ...)."""
    opts = pg.evaluate("() => Array.from(document.querySelector('select[name=B_1]').options).map(o => [o.value, o.text.trim()])")
    want = {"County": "county", "Sex": "sex", "Gender": "sex", "Five-Year Age Groups": "age5", "Injury Intent": "intent", "Year": "year"}
    c = {}
    for v, t in opts:
        if t in want and want[t] not in c: c[want[t]] = v
    c["year"] = c["year"].replace("-level1", ""); c["county"] = c["county"]; return c
def run_query(pg, db, url, years, by_sex, dest, log, state_year=False):
    pg.goto(url, timeout=120000, wait_until="domcontentloaded")
    pg.locator("input[name='action-I Agree']").first.click(); pg.wait_for_selector("select[name=B_1]", timeout=120000)
    c = codes(pg); log(f"  codes {c}")
    if state_year:  # state x year (x sex) table: no suppression at this level
        pg.select_option("select[name=B_1]", c["county"].replace("level2", "level1")); pg.select_option("select[name=B_2]", c["year"] + "-level1"); pg.select_option("select[name=B_3]", c["sex"] if by_sex else "*None*")
    else: pg.select_option("select[name=B_1]", c["county"]); pg.select_option("select[name=B_2]", c["sex"] if by_sex else "*None*")
    for m in ("M_1", "M_2", "M_3"): pg.check(f"input[type=checkbox][name={m}]")
    pg.check(f"input[type=radio][name=O_age][value='{c['age5']}']"); pg.select_option(f"select[name='V_{c['age5']}']", ["10-14", "15-19"])
    pg.check(f"input[type=radio][name=O_ucd][value='{c['intent']}']"); pg.select_option(f"select[name='V_{c['intent']}']", ["2"])
    avail = pg.evaluate(f"() => Array.from(document.querySelector(\"select[name='F_{c['year']}']\").options).map(o => o.value)"); pg.select_option(f"select[name='F_{c['year']}']", [str(y) for y in years if str(y) in avail])
    pg.check("input[type=checkbox][name=O_show_suppressed]"); pg.check("input[type=checkbox][name=O_show_zeros]"); pg.uncheck("input[type=checkbox][name=O_show_totals]")
    tm = pg.evaluate("() => Array.from(document.querySelector('select[name=O_timeout]').options).map(o => o.value)"); pg.select_option("select[name=O_timeout]", tm[-1])
    if state_year:  # the export never arrives for this grouping; read the rendered results table instead and write the same TSV layout
        pg.locator("input[name='action-Send']").first.click()
        pg.wait_for_function("() => document.body && /\\(\\d\\d\\)\\t\\d{4}\\t/.test(document.body.innerText)", timeout=600000); time.sleep(4)  # wait for the rendered results rows
        body = pg.evaluate("() => document.body.innerText"); rows = []; st = sc = yr = None
        for line in body.splitlines():  # D76 repeats the state label on every row; the 2018+ database prints it once per state and adds a CI line under each row
            tok = [x.strip() for x in line.split("\t")]
            m = re.match(r"^(.+?) \((\d\d)\)$", tok[0])
            if m: st, sc = m.groups(); tok = tok[1:]
            if tok and re.fullmatch(r"\d{4}", tok[0]): yr = tok[0]; tok = tok[1:]
            sx = sxc = None
            if tok and re.match(r"^(Female|Male)", tok[0]): sx = tok[0].split(" ")[0]; sxc = sx[0]; tok = tok[1:]
            if st and yr and len(tok) >= 3 and re.fullmatch(r"[\d,]+|Suppressed", tok[0]) and re.fullmatch(r"[\d,]+|Not Applicable", tok[1]): rows.append((st, sc, yr, sx, sxc, tok[0], tok[1], tok[2]))
        hdr = ["State", "State Code", "Year", "Year Code"] + (["Sex", "Sex Code"] if by_sex else []) + ["Deaths", "Population", "Crude Rate"]
        with open(dest, "w") as fh:
            fh.write("\t".join(f'"{h}"' for h in hdr) + "\n")
            for st, sc, yr, sx, sxc, de, po, cr in rows: fh.write("\t".join([f'"{st}"', f'"{sc}"', f'"{yr}"', f'"{yr}"'] + ([f'"{sx}"', f'"{sxc or (sx or "")[:1]}"'] if by_sex else []) + [de.replace(",", ""), po.replace(",", ""), cr]) + "\n")
            fh.write('"---"\n' + body[body.find("Messages:"):][:3000])
        txt = dest.read_text(errors="replace"); n = len(rows)
    else:
        pg.check("input[type=checkbox][name='O_change_action-Send-Export Results']"); pg.select_option("select[name='O_export-format']", "tsv")
        with pg.expect_download(timeout=1500000) as dl: pg.locator("input[name='action-Send']").first.click()
        dl.value.save_as(dest); txt = dest.read_text(errors="replace"); n = txt.count("\n")
    sup = txt.count("Suppressed"); log(f"  saved {dest.name}: {n} lines, {sup} 'Suppressed' tokens, {dest.stat().st_size} bytes")
    if "Error" in txt[:2000] or n < 100: log("  WARNING: output looks wrong; first 600 chars:\n" + txt[:600])

def compile_state_year():
    rows = []
    for f in sorted(OUT.glob("D*_stateyear_*.txt")):
        db, _, per, kind = f.stem.split("_"); lines = f.read_text(errors="replace").splitlines(); end = next((i for i, l in enumerate(lines) if l.strip() == '"---"'), len(lines))
        d = pd.read_csv(io.StringIO("\n".join(lines[:end])), sep="\t", dtype=str); d = d[d["State Code"].fillna("").str.fullmatch(r"\d{2}") & d["Year Code"].fillna("").str.fullmatch(r"\d{4}")]
        d["sex"] = d["Sex Code"] if "Sex Code" in d else "all"; d["suppressed"] = (d.Deaths.str.strip() == "Suppressed").astype(int)
        rows.append(pd.DataFrame({"state_fips": d["State Code"], "state": d.State, "year": d["Year Code"].astype(int), "sex": d.sex, "deaths": pd.to_numeric(d.Deaths, errors="coerce"), "population": pd.to_numeric(d.Population, errors="coerce"), "suppressed": d.suppressed, "database": db}))
    if not rows: return None
    c = pd.concat(rows); c["rate_per100k"] = (c.deaths / c.population * 1e5).round(3); c = c.sort_values(["sex", "state_fips", "year", "database"])
    out = ROOT/"data/compiled/broadband/state_youth_suicide_year.csv"; c.to_csv(out, index=False); print(c.groupby(["database", "sex"]).agg(states=("state_fips", "nunique"), years=("year", "nunique"), suppressed=("suppressed", "sum"), deaths=("deaths", "sum")).to_string()); return c
def compile_outputs():
    compile_state_year(); rows = []
    for f in sorted(OUT.glob("D*_*.txt")):
        if "stateyear" in f.stem: continue
        db, per, kind = f.stem.split("_"); lines = f.read_text(errors="replace").splitlines(); end = next((i for i, l in enumerate(lines) if l.strip() == '"---"'), len(lines))
        d = pd.read_csv(io.StringIO("\n".join(lines[:end])), sep="\t", dtype=str)
        d = d[d["County Code"].fillna("").str.fullmatch(r"\d{5}")]
        d["sex"] = d["Sex Code"] if "Sex Code" in d else "all"
        d["suppressed"] = (d.Deaths.str.strip() == "Suppressed").astype(int); d["deaths"] = pd.to_numeric(d.Deaths, errors="coerce"); d["population"] = pd.to_numeric(d.Population, errors="coerce")
        d["rate_per100k"] = d.deaths / d.population * 1e5
        rows.append(pd.DataFrame({"fips": d["County Code"], "period": per, "sex": d.sex, "deaths": d.deaths, "population": d.population, "rate_per100k": d.rate_per100k.round(3), "suppressed": d.suppressed, "database": db, "county": d.County}))
    c = pd.concat(rows).sort_values(["period", "sex", "fips"]); out = ROOT/"data/compiled/broadband/county_youth_suicide_periods.csv"; out.parent.mkdir(parents=True, exist_ok=True); c.to_csv(out, index=False)
    print(c.groupby(["period", "sex"]).agg(counties=("fips", "size"), unsuppressed=("suppressed", lambda s: int((s == 0).sum())), deaths=("deaths", "sum"), pop=("population", "sum")).to_string()); return c

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=list(DBS)); ap.add_argument("--pause", type=float, default=20); ap.add_argument("--periods", help="comma list, e.g. 2003-2007")
    ap.add_argument("--no-sex", action="store_true", help="skip the by-sex queries"); ap.add_argument("--force", action="store_true"); ap.add_argument("--compile", action="store_true", help="only parse the saved exports into the compiled CSV")
    ap.add_argument("--state-year", action="store_true", help="instead of county periods, pull state x year (x sex) tables for all years of each database (the no-suppression fallback)")
    a = ap.parse_args(); log = lambda s: print(s, flush=True)
    if a.compile: compile_outputs(); sys.exit()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(user_agent=UA, accept_downloads=True)
        for db, (url, periods) in DBS.items():
            if a.only and db != a.only: continue
            if a.state_year: periods = ["1999-2020" if db == "D76" else "2018-2024"]
            for per in (a.periods.split(",") if a.periods else periods):
                y0, y1 = map(int, per.split("-"))
                for by_sex in ([False] if (a.no_sex or (per == '1999-2002' and not a.state_year)) else [False, True]):
                    dest = OUT/f"{db}_{'stateyear_' if a.state_year else ''}{per}_{'sex' if by_sex else 'all'}.txt"
                    if dest.exists() and dest.stat().st_size > 10000 and not a.force: log(f"ok {dest.name}"); continue
                    log(f"query {db} {per} {'by sex' if by_sex else 'all'} ...")
                    pg = ctx.new_page()
                    try: run_query(pg, db, url, range(y0, y1 + 1), by_sex, dest, log, state_year=a.state_year)
                    except Exception as e: log(f"  FAILED {db} {per} by_sex={by_sex}: {e}"); pg.screenshot(path=str(OUT/f"fail_{db}_{per}_{int(by_sex)}.png"))
                    pg.close(); time.sleep(a.pause)
        b.close()
    compile_outputs()
