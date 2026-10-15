"""GSHS 2022-23 rounds with the mobile-phone-hours item (GHA, IND, JAM, MAR, WLF): within-country dose-response of loneliness/suicidality on daily mobile hours, by sex."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
T = pathlib.Path("results/tables"); pd.set_option("display.width", 200)
g = pd.read_parquet("data/extracts/gshs/gshs_stacked.parquet"); g = g[g.net_ot_mobilehours.notna() & g.weight.notna() & g.female.isin([0,1])].copy()
# CDC coding for hours items: 1 = did not use / 0 h, 2 = <1 h, 3 = 1 h, 4 = 2 h, 5 = 3 h, 6 = 4 h, 7 = 5+ h  (verified against ot_b_mobilehours: 1 = 3+ h)
print(pd.crosstab(g.net_ot_mobilehours, g.net_ot_b_mobilehours))
g["hours3plus"] = (g.net_ot_b_mobilehours==1).astype(float).where(g.net_ot_b_mobilehours.isin([1,2])); g["hrs_cat"] = g.net_ot_mobilehours.astype(int)
g["ctry"] = g.iso3; g["age_c"] = g.age_yrs.fillna(g.raw_age.astype(float)); g["cl"] = g.iso3+"_"+g.psu.astype(str)
print(g.groupby(["iso3","year","female"]).agg(n=("weight","size"), p3=("hours3plus","mean"), lonely=("lonely","mean"), consider=("suicide_consider","mean")).round(3).to_string())
rows = []
for sx, lab in [(1,"girls"),(0,"boys")]:
    d = g[g.female==sx]
    for y in ["lonely","worried_sleep","suicide_consider","suicide_plan","suicide_attempt"]:
        dd = d[d[y].notna()&d.hours3plus.notna()]
        if len(dd) < 500: continue
        m = pf.feols(f"{y} ~ hours3plus + C(age_c) | ctry", data=dd, weights="weight", vcov={"CRV1":"cl"})
        m2 = pf.feols(f"{y} ~ C(hrs_cat) | ctry", data=dd[dd.hrs_cat.between(1,7)], weights="weight", vcov={"CRV1":"cl"})
        grad = {k: 100*v for k, v in m2.coef().items()}
        rows.append(dict(sex=lab, outcome=y, n=len(dd), mean=100*np.average(dd[y], weights=dd.weight), coef_3plus=100*m.coef()["hours3plus"], se=100*m.se()["hours3plus"], **{f"h{k}": round(v,1) for k,v in enumerate(list(grad.values()), start=2)}))
R = pd.DataFrame(rows); R.to_csv(T/"gshs_mobile_hours.csv", index=False); print(R.round(2).to_string())
