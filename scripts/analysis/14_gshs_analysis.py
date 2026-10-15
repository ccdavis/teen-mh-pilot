"""Pilot step 8: GSHS country-round rates (13-17) by sex, merged with WDI internet users % and mobile subs; country + year FE regressions by sex."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"
g = pd.read_parquet(ROOT/"data/extracts/gshs/gshs_stacked.parquet")
g = g[g.weight.notna() & (g.weight > 0)]
items = ["lonely","worried_sleep","suicide_consider","suicide_plan","suicide_attempt","no_close_friends"]
rows = []
for (iso, yr, fem), s in g.groupby(["iso3","year","female"]):
    if fem not in (0,1): continue
    for it in items:
        x = s[s[it].notna()]
        if len(x) < 100: continue
        w = x.weight; p = np.average(x[it], weights=w); neff = w.sum()**2/(w**2).sum()
        rows.append(dict(iso3=iso, year=int(yr), sex="girls" if fem==1 else "boys", item=it, rate=100*p, se=100*np.sqrt(p*(1-p)/neff), n=len(x)))
R = pd.DataFrame(rows)
W = pd.read_csv(ROOT/"data/compiled/wdi/wdi_ict_2000_2024.csv")
R = R.merge(W[["iso3","year","internet_users_pct","mobile_subs_per100","gdp_pc_ppp"]], on=["iso3","year"], how="left")
R["log_gdp"] = np.log(R.gdp_pc_ppp); R.to_csv(T/"gshs_country_round_rates.csv", index=False)
print("country-rounds:", R.groupby(["iso3","year"]).ngroups, " countries with 2+ rounds:", (R.groupby("iso3").year.nunique()>=2).sum())
print(R.groupby("item").rate.describe()[["count","mean","std"]].round(1).to_string())
multi = R[R.groupby("iso3").year.transform("nunique") >= 2]
out = []
for it in items:
    for sex in ["girls","boys"]:
        d = multi[(multi.item==it)&(multi.sex==sex)&multi.internet_users_pct.notna()&multi.log_gdp.notna()].copy()
        d = d[d.groupby("iso3").year.transform("nunique") >= 2]; d["wt"] = 1/d.se**2  # countries still observed twice after dropping rounds without WDI values
        if d.iso3.nunique() < 5: continue
        m = pf.feols("rate ~ internet_users_pct + log_gdp | iso3 + year", data=d, weights="wt", vcov={"CRV1":"iso3"})
        out.append(dict(item=it, sex=sex, n_rounds=m._N, n_countries=d.iso3.nunique(), coef_per10pp=10*m.coef()["internet_users_pct"], se_per10pp=10*m.se()["internet_users_pct"]))
O = pd.DataFrame(out); O.to_csv(T/"gshs_fe_internet.csv", index=False); print(O.round(3).to_string())
