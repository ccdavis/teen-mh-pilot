"""Build the slim NSCH extract: children aged 6-17 from the 2016-2025 topical public-use files.
Run from the repository root after fetch_nsch.py:  uv run python scripts/download/nsch/extract_nsch.py
Input : data/external/nsch/<year>/nsch_<year>e_topical.dta (Stata; variable names lower-case; extended missing .m/.n/.l/.d -> NaN)
Output: data/extracts/nsch/nsch_6_17.parquet (one row per sampled child, all years stacked, raw codes kept, plus harmonised
        analysis variables documented in notes/nsch.md) and data/extracts/nsch/nsch_items.csv (variable, years present, label).
Item changes handled here (see notes/nsch.md): 2016-17 screen time is two items (K7Q60_R TV, K7Q91_R devices; 1 none ... 6 4+ h),
2018+ one item SCREENTIME (1 <1 h ... 5 4+ h); bullying BULLIED (2016-17, definitely/somewhat/not true) vs BULLIED_R (2018+, frequency);
school-engagement and flourishing items switched from a 3-point true scale (2016-17) to a 4-point always/never scale (2018+).
"""
import pathlib, re, numpy as np, pandas as pd, pyreadstat
ROOT = pathlib.Path(__file__).resolve().parents[3]; RAW = ROOT/"data/external/nsch"; OUT = ROOT/"data/extracts/nsch"; OUT.mkdir(parents=True, exist_ok=True)
YEARS = range(2016, 2026)
KEEP = """year hhid fipsst stratum fwc formtype sc_age_years sc_sex sc_race_r sc_hispanic_r fpl_i1 higrade a1_grade a1_menthealth a1_physhealth
k2q33a k2q33b k2q33c k2q32a k2q32b k2q32c k2q31a k2q31b k2q31c k2q34a k2q34b k2q30a k2q35a screentime k7q60_r k7q91_r hoursleep hoursleep05
bullied bullied_r bully k7q82_r k7q83_r k7q84_r k7q85_r k7q70_r k6q71_r k6q73_r physactiv k10q40_r k10q41_r k10q11 k10q12 k10q13 k10q14
k7q30 k7q31 k7q32 k7q33 makefriend k4q22_r treatneed metro_yn mpc_yn k2q01 sc_cshcn k7q02r_r family_r totkids_r hhlanguage bornusa tenure
sc_english outdoorswkday outdoorswkend grades bodyimage vape k8q35 k11q43r a1_age a1_relation currins ace1 ace3 ace4 ace5 ace6 ace7 ace8 ace9 ace10""".split()

def labels(year):
    t = (RAW/str(year)/f"nsch_{year}_topical.do").read_text(encoding="utf-8", errors="replace")
    return {m.group(1).lower(): m.group(2) for m in re.finditer(r'^label var (\S+)\s+"([^"]*)"', t, re.M)}

frames, items = [], []
for y in YEARS:
    f = RAW/str(y)/f"nsch_{y}e_topical.dta"
    lab = labels(y); cols = [c for c in KEEP if c in lab]
    df, meta = pyreadstat.read_dta(str(f), usecols=cols)
    df.columns = [c.lower() for c in df.columns]
    df["year"] = y; df["stratum"] = df["stratum"].astype(str); df["formtype"] = df["formtype"].astype(str); df["hhid"] = df["hhid"].astype(str)
    df = df[df.sc_age_years.between(6, 17)].copy()
    for c in KEEP:
        if c not in df: df[c] = np.nan
    frames.append(df[KEEP]); items += [dict(variable=c, year=y, label=lab[c]) for c in cols]
    print(f"{y}: file rows {meta.number_rows:,}, ages 6-17 kept {len(df):,}, weight sum {df.fwc.sum():,.0f}", flush=True)
d = pd.concat(frames, ignore_index=True)
# ---- harmonised analysis variables (NaN when the item is missing or not asked) ----
yn = lambda s: s.map({1: 1.0, 2: 0.0})
d["anx_ever"] = yn(d.k2q33a); d["dep_ever"] = yn(d.k2q32a); d["adhd_ever"] = yn(d.k2q31a); d["beh_ever"] = yn(d.k2q34a)
# "currently has": 1 if ever told and currently yes; 0 if never told or told but not current
for a, b, nm in [("k2q33a","k2q33b","anx_cur"),("k2q32a","k2q32b","dep_cur"),("k2q31a","k2q31b","adhd_cur"),("k2q34a","k2q34b","beh_cur")]:
    d[nm] = np.where(d[a]==2, 0.0, np.where((d[a]==1)&(d[b]==1), 1.0, np.where((d[a]==1)&(d[b]==2), 0.0, np.nan)))
for c, nm in [("k2q33c","anx_modsev"),("k2q32c","dep_modsev")]:   # current and moderate/severe
    cur = d[nm.split("_")[0]+"_cur"]; d[nm] = np.where(cur==0, 0.0, np.where((cur==1)&d[c].isin([2,3]), 1.0, np.where((cur==1)&(d[c]==1), 0.0, np.nan)))
# screen time: 2018+ SCREENTIME 1 <1h, 2 1h, 3 2h, 4 3h, 5 4+h  -> hours category label and numeric midpoint
scr_lab = {1:"<1 h", 2:"1 h", 3:"2 h", 4:"3 h", 5:"4+ h"}; scr_hrs = {1:0.5, 2:1, 3:2, 4:3, 5:4.5}
d["screen_cat"] = d.screentime.map(scr_lab); d["screen_hrs"] = d.screentime.map(scr_hrs); d["screen_4plus"] = (d.screentime==5).astype(float).where(d.screentime.notna())
d["screen_3plus"] = (d.screentime>=4).astype(float).where(d.screentime.notna())
# 2016-17: sum of the two items (each 1 none, 2 <1h, 3 1h, 4 2h, 5 3h, 6 4+h -> hours 0, .5, 1, 2, 3, 4.5), capped like Twenge & Campbell
h2 = {1:0, 2:0.5, 3:1, 4:2, 5:3, 6:4.5}
d["screen_hrs_1617"] = d.k7q60_r.map(h2) + d.k7q91_r.map(h2)
d["device_hrs_1617"] = d.k7q91_r.map(h2)
# sleep: HOURSLEEP (6-17) 1 <6h 2 6h 3 7h 4 8h 5 9h 6 10h 7 11+h
d["sleep_lt8"] = (d.hoursleep<=3).astype(float).where(d.hoursleep.notna()); d["sleep_hrs"] = d.hoursleep.map({1:5.5, 2:6, 3:7, 4:8, 5:9, 6:10, 7:11})
# bullying victimisation: 2018+ BULLIED_R 1 never ... 5 almost every day; monthly+ = 3,4,5; weekly+ = 4,5
d["bullied_monthly"] = (d.bullied_r>=3).astype(float).where(d.bullied_r.notna()); d["bullied_weekly"] = (d.bullied_r>=4).astype(float).where(d.bullied_r.notna())
d["bullied_any"] = (d.bullied_r>=2).astype(float).where(d.bullied_r.notna())
d["bullied_true_1617"] = (d.bullied<=2).astype(float).where(d.bullied.notna())   # definitely/somewhat true
d["bully_monthly"] = (d.bully>=3).astype(float).where(d.bully.notna())
# school engagement (2018+: 1 always 2 usually 3 sometimes 4 never): cares about school + does homework, "always/usually" both
d["engaged"] = ((d.k7q82_r<=2)&(d.k7q83_r<=2)).astype(float).where(d.k7q82_r.notna()&d.k7q83_r.notna()&(d.year>=2018))
d["missed_school_11plus"] = (d.k7q02r_r>=4).astype(float).where(d.k7q02r_r.notna())  # K7Q02R_R: 1 none, 2 1-3, 3 4-6, 4 7-10, 5 11+ (check); kept raw too
d["physact_daily"] = (d.physactiv==4).astype(float).where(d.physactiv.notna()); d["physact_0days"] = (d.physactiv==1).astype(float).where(d.physactiv.notna())
d["safe_nbhd"] = (d.k10q40_r<=2).astype(float).where(d.k10q40_r.notna()); d["safe_school"] = (d.k10q41_r<=2).astype(float).where(d.k10q41_r.notna())
d["sports"] = yn(d.k7q30); d["clubs"] = yn(d.k7q31)
d["friends_difficulty"] = (d.makefriend>=2).astype(float).where(d.makefriend.notna())
d["mh_treat_12m"] = (d.k4q22_r==1).astype(float).where(d.k4q22_r.notna()); d["mh_unmet"] = (d.k4q22_r==2).astype(float).where(d.k4q22_r.notna())
# covariates
d["girl"] = (d.sc_sex==2).astype(float).where(d.sc_sex.notna()); d["age"] = d.sc_age_years.astype(int); d["age12_17"] = (d.age>=12).astype(int)
d["agegrp"] = np.where(d.age>=12, "12-17", "6-11")
race = np.select([d.sc_hispanic_r==1, d.sc_race_r==1, d.sc_race_r==2, d.sc_race_r==4], ["Hispanic", "White NH", "Black NH", "Asian NH"], "Other/multi NH")
d["raceeth"] = pd.Series(race).where(d.sc_race_r.notna()|(d.sc_hispanic_r==1), np.nan).values
d["fpl"] = d.fpl_i1.clip(50, 400); d["fpl_cat"] = pd.cut(d.fpl, [0, 99, 199, 399, 400], labels=["<100", "100-199", "200-399", "400+"]).astype(str)
d["pared"] = d.higrade.map({1:"<HS", 2:"HS", 3:">HS"})
d["state"] = d.fipsst.astype(int); d["wt"] = d.fwc.astype(float); d["strat"] = d.year.astype(str)+"_"+d.fipsst.astype(int).astype(str)+"_"+d.stratum.astype(str)
d.to_parquet(OUT/"nsch_6_17.parquet", index=False)
it = pd.DataFrame(items); it = it.groupby("variable").agg(years=("year", lambda s: ",".join(map(str, sorted(s)))), label=("label", "last")).reset_index()
it.to_csv(OUT/"nsch_items.csv", index=False)
print("rows", len(d), "cols", d.shape[1], "->", OUT/"nsch_6_17.parquet")
print(d.groupby("year").agg(n=("wt","size"), n12_17=("age12_17","sum"), anx_cur=("anx_cur","mean"), dep_cur=("dep_cur","mean"), screen4=("screen_4plus","mean")).round(3).to_string())
