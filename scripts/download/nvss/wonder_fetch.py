"""Fetch U.S. suicide deaths (ICD-10 113 cause list GR113-124: *U03, X60-X84, Y87.0) by year, month, single-year age and sex from the CDC WONDER API.

Databases: D76 = Underlying Cause of Death 1999-2020 (bridged-race populations); D158 = Underlying Cause of Death 2018-2024, Single Race.
Endpoint: POST https://wonder.cdc.gov/controller/datarequest/<DB> with form fields request_xml=<xml>, accept_datause_restrictions=true.
The XML carries every form parameter of the interactive request page; this script fetches that page (after posting "I Agree"), reads the
default value of every field, and overrides the group-by (B_*), the cause-of-death selector (O_ucd/V_<DB>.V4), the age selector
(O_age/V_<DB>.V52) and display options. National data only (the API does not allow sub-national geography; national counts are not suppressed).

Usage: uv run python scripts/download/nvss/wonder_fetch.py [--only NAME ...] [--test]
Raw responses: data/external/nvss/wonder/<name>.xml ; parsed tables: data/compiled/nvss/<name>.csv ; form pages: data/external/nvss/wonder/form_<DB>.html
"""
import sys, re, html, time, pathlib, argparse, datetime as dt
import requests, pandas as pd
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
RAW = ROOT/"data/external/nvss/wonder"; OUT = ROOT/"data/compiled/nvss"
RAW.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://wonder.cdc.gov/controller/datarequest/"
UA = {"User-Agent": "curl/8.5.0"}  # wonder.cdc.gov (Akamai) returns 403 to other non-browser user agents
AGES_WIDE = [str(a) for a in range(10, 40)]          # 10-39: covers 12-17, 18-24, 25-34 plus margins (placebo 10-11, 35-39)
AGES_YOUTH = [str(a) for a in range(10, 35)]         # for the larger weekday x month tables

def form_defaults(session, db):
    """Post the data-use agreement, save the request form, return {name: [values]} of default values."""
    r = session.post(BASE + db, data={"stage": "about", "saved_id": "", "action-I Agree": "I Agree"}, headers=UA, timeout=120); r.raise_for_status()
    src = r.text; (RAW/f"form_{db}.html").write_text(src)
    d = {}
    for m in re.finditer(r"<input([^>]*)>", src, flags=re.I):
        a = m.group(1); name = re.search(r'name="([^"]*)"', a); val = re.search(r'value="([^"]*)"', a); typ = (re.search(r'type="([^"]*)"', a) or [None, "text"])[1].lower()
        if not name: continue
        n, v = name.group(1), html.unescape(val.group(1)) if val else ""
        if typ == "hidden": d.setdefault(n, []); d[n] = [v] if n not in d or not d[n] else d[n]
        elif typ in ("radio", "checkbox") and "checked" in a.lower(): d[n] = [v]
        elif typ == "text": d.setdefault(n, [v])
    for m in re.finditer(r"<select([^>]*)>(.*?)</select>", src, flags=re.I | re.S):
        a, body = m.group(1), m.group(2); name = re.search(r'name="([^"]*)"', a)
        if not name: continue
        opts = re.findall(r"<option([^>]*)>", body, flags=re.I)
        sel = [html.unescape(re.search(r'value="([^"]*)"', o).group(1)) for o in opts if "selected" in o.lower() and re.search(r'value="([^"]*)"', o)]
        if not sel and opts and "multiple" not in a.lower():
            v = re.search(r'value="([^"]*)"', opts[0]); sel = [html.unescape(v.group(1))] if v else []
        d[name.group(1)] = sel
    return d

def build_xml(params):
    def esc(s): return html.escape(str(s), quote=False)
    body = "".join(f"<parameter><name>{esc(k)}</name>{''.join(f'<value>{esc(v)}</value>' for v in vals)}</parameter>" for k, vals in sorted(params.items()))
    return f"<request-parameters>{body}</request-parameters>"

def make_query(defaults, db, groups, ages, years=None, weekday_only_known=False, show_zeros=True):
    """groups: list of up to 5 group-by codes (without the DB prefix, e.g. 'V1-level1'); ages: list of single-year ages (strings) or None."""
    p = {k: list(v) for k, v in defaults.items() if v is not None}
    # drop the interactive-only fields and finder display items we do not use
    for k in list(p):
        if k in ("query", "affiliate", "saved_id", "O_oc-sect1-request") or k.startswith("I_"): p.pop(k)
    p["accept_datause_restrictions"] = ["true"]; p["stage"] = ["request"]; p["action-Send"] = ["Send"]; p["O_javascript"] = ["on"]
    for i in range(1, 6): p[f"B_{i}"] = [f"{db}.{groups[i-1]}"] if i <= len(groups) else ["*None*"]
    p["M_1"] = [f"{db}.M1"]; p["M_2"] = [f"{db}.M2"]; p["M_3"] = [f"{db}.M3"]
    for k in ("M_9", "M_31", "M_32", "O_aar_enable", "O_aar_CI", "O_aar_SE", "O_aar_nonstd", "O_post_pops", "O_change_action-Send-Export Results"): p.pop(k, None)
    p["O_aar"] = ["aar_none"]; p["O_precision"] = ["3"]; p["O_rate_per"] = ["100000"]; p["O_timeout"] = ["900"]; p["O_title"] = [""]
    p["O_show_totals"] = ["false"]; p["O_show_zeros"] = ["true" if show_zeros else "false"]; p["O_show_suppressed"] = ["true"]
    # cause of death: ICD-10 113 cause list, intentional self-harm
    p["O_ucd"] = [f"{db}.V4"]; p[f"V_{db}.V4"] = ["GR113-124"]; p[f"F_{db}.V2"] = ["*All*"]; p[f"V_{db}.V2"] = [""]
    # ages
    if ages: p["O_age"] = [f"{db}.V52"]; p[f"V_{db}.V52"] = list(ages); p[f"V_{db}.V5"] = ["*All*"]; p[f"V_{db}.V51"] = ["*All*"]
    else: p["O_age"] = [f"{db}.V5"]; p[f"V_{db}.V5"] = ["*All*"]; p[f"V_{db}.V52"] = ["*All*"]; p[f"V_{db}.V51"] = ["*All*"]
    p[f"V_{db}.V6"] = ["00"]
    # years
    p[f"F_{db}.V1"] = [str(y) for y in years] if years else ["*All*"]; p[f"V_{db}.V1"] = [""]
    if weekday_only_known: p[f"V_{db}.V24"] = ["1", "2", "3", "4", "5", "6", "7"]
    # national geography
    for v in ("V9", "V10", "V27", "V30", "V31"):
        if f"F_{db}.{v}" in p: p[f"F_{db}.{v}"] = ["*All*"]; p[f"V_{db}.{v}"] = [""]
    return p

def parse_response(xml_text, group_labels):
    """Rows are <r><c l="label" r="rowspan"/>...<c v="value"/>...</r>; with show-all-labels="false" a label cell with rowspan r
    is omitted from the following r-1 rows, so group labels are carried forward column by column."""
    root = ET.fromstring(xml_text)
    rows = []; ng = len(group_labels); cur = [None] * ng; left = [0] * ng
    for r in root.iter("r"):
        cells = list(r)
        labcells = [c for c in cells if c.get("l") is not None]
        vals = [c.get("v") for c in cells if c.get("v") is not None]
        labs = []; k = 0
        for j in range(ng):
            if left[j] > 0: left[j] -= 1
            elif k < len(labcells): c = labcells[k]; k += 1; cur[j] = c.get("l"); left[j] = int(c.get("r", 1)) - 1
            labs.append(cur[j])
        rows.append(labs + vals)
    ncol = max((len(x) for x in rows), default=0)
    cols = group_labels + ["deaths", "population", "crude_rate"]
    cols = cols[:ncol] + [f"x{i}" for i in range(ncol - len(cols))] if ncol > len(cols) else cols[:ncol]
    df = pd.DataFrame(rows, columns=cols)
    caveats = [("".join(c.itertext())).strip() for c in root.iter("caveat")]
    msgs = [("".join(c.itertext())).strip() for c in root.iter("message")]
    return df, caveats, msgs

# WONDER suppresses cells of 1-9 deaths even in national queries when the table is grouped by single-year age (checked 2026-10-24:
# 5,603 of 15,840 year x month x single-age x sex cells were "Suppressed"). The main tables therefore FILTER on single-year ages
# (e.g. 12-17) without grouping by age, so WONDER returns the age-group total per cell; age-group x month x sex cells are all >= 10
# for the groups below. Weekday tables are pooled over a period for the same reason. The API requires >= 15 s between requests.
AGEGRPS = {"12-17": range(12, 18), "18-24": range(18, 25), "25-34": range(25, 35), "12-14": range(12, 15), "15-17": range(15, 18), "12-18": range(12, 19),
           "35-54": range(35, 55)}
WAIT = 16
def _ages(g): return [str(a) for a in AGEGRPS[g]]
QUERIES = {}
SCHOOL, SUMMER = (9, 10, 11, 12, 1, 2, 3, 4, 5), (6, 7, 8)
def _months(years, months): return [f"{y}/{m:02d}" for y in years for m in months]   # year/month finder codes (F_<db>.V1)
for db, pre, pool in (("D76", "d76", range(1999, 2020)), ("D158", "d158", range(2021, 2025))):
    QUERIES[f"{pre}_year_age_sex"] = (db, ["V1-level1", "V52", "V7"], ["year", "age", "sex"], AGES_WIDE, None, False)   # populations by single year of age
    for g in AGEGRPS:
        QUERIES[f"{pre}_month_sex_{g}"] = (db, ["V1-level1", "V1-level2", "V7"], ["year", "month", "sex"], _ages(g), None, False)
        QUERIES[f"{pre}_month_all_{g}"] = (db, ["V1-level1", "V1-level2"], ["year", "month"], _ages(g), None, False)      # both sexes: never suppressed
    for g in ("12-17", "18-24", "25-34"):
        QUERIES[f"{pre}_year_weekday_sex_{g}"] = (db, ["V1-level1", "V24", "V7"], ["year", "weekday", "sex"], _ages(g), None, True)
        # day of week pooled over the period's school months (Sep-May) and summer months (Jun-Aug); the Month group-by is
        # year-specific ("Jan., 1999") and such cells are heavily suppressed, so the pooling is done through the year/month filter
        QUERIES[f"{pre}_weekday_sex_{g}_school"] = (db, ["V24", "V7"], ["weekday", "sex"], _ages(g), _months(pool, SCHOOL), True)
        QUERIES[f"{pre}_weekday_sex_{g}_summer"] = (db, ["V24", "V7"], ["weekday", "sex"], _ages(g), _months(pool, SUMMER), True)
# exploratory single-age tables (kept as raw XML only; heavily suppressed)
QUERIES["d76_year_month_age_sex"] = ("D76", ["V1-level1", "V1-level2", "V52", "V7"], ["year", "month", "age", "sex"], AGES_WIDE, None, False)
QUERIES["d158_year_month_age_sex"] = ("D158", ["V1-level1", "V1-level2", "V52", "V7"], ["year", "month", "age", "sex"], AGES_WIDE, None, False)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", nargs="*"); ap.add_argument("--test", action="store_true"); ap.add_argument("--skip-existing", action="store_true"); a = ap.parse_args()
    s = requests.Session(); defaults = {}
    names = a.only or [n for n in QUERIES if not n.endswith("year_month_age_sex")]
    if a.test: names = ["d76_year_age_sex"]
    log = []; last = 0.0
    for name in names:
        if a.skip_existing and (OUT/f"{name}.csv").exists(): print(f"{name}: exists, skipped"); continue
        db, groups, labels, ages, years, wk = QUERIES[name]
        if db not in defaults:
            time.sleep(max(0, WAIT - (time.time() - last))); defaults[db] = form_defaults(s, db); last = time.time()
        if a.test: ages = [str(x) for x in range(12, 18)]; years = [2015, 2016]
        p = make_query(defaults[db], db, groups, ages, years, wk)
        xml = build_xml(p)
        time.sleep(max(0, WAIT - (time.time() - last))); t0 = time.time()
        r = s.post(BASE + db, data={"request_xml": xml, "accept_datause_restrictions": "true"}, headers=UA, timeout=960); last = time.time()
        (RAW/f"{name}.xml").write_text(r.text); (RAW/f"{name}_request.xml").write_text(xml)
        if r.status_code != 200 or "<data-table" not in r.text:
            msg = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", r.text))[:600]
            print(f"{name}: HTTP {r.status_code}, no data-table. {msg}"); log.append((name, r.status_code, 0, f"{time.time()-t0:.0f}s", "FAILED")); continue
        df, caveats, msgs = parse_response(r.text, labels)
        df.to_csv(OUT/f"{name}.csv", index=False)
        nsup = int((df.deaths == "Suppressed").sum()) if "deaths" in df else -1
        print(f"{name}: HTTP {r.status_code}, {len(df):,} rows, {time.time()-t0:.0f}s; deaths sum = {pd.to_numeric(df.deaths.astype(str).str.replace(',', ''), errors='coerce').sum():,.0f}; suppressed cells = {nsup}")
        for m in msgs[:4]: print("   message:", re.sub(r"\s+", " ", m)[:300])
        log.append((name, r.status_code, len(df), f"{time.time()-t0:.0f}s", (RAW/f"{name}.xml").stat().st_size))
    pd.DataFrame(log, columns=["query", "http", "rows", "seconds", "xml_bytes"]).assign(fetched=dt.date.today().isoformat()).to_csv(OUT/"wonder_fetch_log.csv", index=False, mode="a", header=not (OUT/"wonder_fetch_log.csv").exists())

if __name__ == "__main__": main()
