"""GSHS 2022-23 rounds with the mobile-phone-hours item (GHA, IND, JAM, MAR, WLF): within-country dose-response of loneliness/suicidality on daily mobile hours, by sex."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
T = ROOT/"results/tables"; pd.set_option("display.width", 200)
g = pd.read_parquet(ROOT/"data/extracts/gshs/gshs_stacked.parquet"); g = g[g.net_ot_mobilehours.notna() & g.weight.notna() & g.female.isin([0,1])].copy()
# ot_mobilehours value labels (same in all five rounds): 1 = did not have a mobile phone in the past 7 days, 2 = less than 1 h/day, 3 = 1-2 h, 4 = 3-4 h,
# 5 = 5-6 h, 6 = 7-8 h, 7 = more than 8 h. The CDC dichotomy ot_b_mobilehours (1 = 3+ h/day) is defined among phone users only (codes 2-7).
print(pd.crosstab(g.net_ot_mobilehours, g.net_ot_b_mobilehours))
# hours3plus = 3+ h/day (codes 4-7) vs everyone else, including students without a phone (code 1), so the contrast covers all students
g["hrs_cat"] = g.net_ot_mobilehours.astype(int); g["hours3plus"] = (g.hrs_cat >= 4).astype(float).where(g.hrs_cat.between(1,7))
g["ctry"] = g.iso3; g["age_c"] = g.age_yrs.fillna(g.raw_age.astype(float)); g["cl"] = g.iso3+"_"+g.psu.astype(str)
print(g.groupby(["iso3","year","female"]).agg(n=("weight","size"), p3=("hours3plus","mean"), lonely=("lonely","mean"), consider=("suicide_consider","mean")).round(3).to_string())
rows = []
for sx, lab in [(1,"girls"),(0,"boys")]:
    d = g[g.female==sx]
    for y in ["lonely","worried_sleep","suicide_consider","suicide_plan","suicide_attempt"]:
        dd = d[d[y].notna()&d.hours3plus.notna()]
        if len(dd) < 500: continue
        m = pf.feols(f"{y} ~ hours3plus + C(age_c) | ctry", data=dd, weights="weight", vcov={"CRV1":"cl"})
        m2 = pf.feols(f"{y} ~ i(hrs_cat, ref=2) | ctry", data=dd[dd.hrs_cat.between(1,7)], weights="weight", vcov={"CRV1":"cl"})  # gradient relative to under 1 h/day; h1 = no phone
        grad = {int(float(k.split("::")[1])): 100*v for k, v in m2.coef().items() if k.startswith("hrs_cat::")}  # key = hours code (1 no phone, 3 = 1-2 h, 4 = 3-4 h, 5 = 5-6 h, 6 = 7-8 h, 7 = 8+ h), reference = code 2 (<1 h)
        rows.append(dict(sex=lab, outcome=y, n=len(dd), mean=100*np.average(dd[y], weights=dd.weight), coef_3plus=100*m.coef()["hours3plus"], se=100*m.se()["hours3plus"], **{f"h{k}": round(v,1) for k,v in sorted(grad.items())}))
R = pd.DataFrame(rows); R.to_csv(T/"gshs_mobile_hours.csv", index=False); print(R.round(2).to_string())
