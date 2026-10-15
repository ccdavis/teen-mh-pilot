"""GSHS country-round panel with ITU exposures: mobile-broadband subs per 100, 3G and 4G population coverage; country + year FE, by sex."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; pd.set_option("display.width", 220)
R = pd.read_csv(T/"gshs_country_round_rates.csv")
I = pd.read_csv(ROOT/"data/compiled/itu/itu_country_year.csv"); I = I[~I.source.astype(str).str.startswith("GSMA")]
W = I.pivot_table(index=["iso3","year"], columns="indicator", values="value").reset_index()
# fill missing 4G coverage with 0 before 2012 where the country has a 3G series that year (LTE not yet deployed); keep reported values and leave others NaN
W["pop_covered_4g_pct"] = W.pop_covered_4g_pct.mask((W.year < 2012) & W.pop_covered_4g_pct.isna() & W.pop_covered_3g_pct.notna(), 0.0)
R = R.merge(W[["iso3","year","mbb_subs_per100","pop_covered_3g_pct","pop_covered_4g_pct","internet_users_pct"]].rename(columns={"internet_users_pct":"itu_internet"}), on=["iso3","year"], how="left")
multi = R[R.groupby("iso3").year.transform("nunique") >= 2]
out = []
for x in ["mbb_subs_per100","pop_covered_3g_pct","pop_covered_4g_pct","itu_internet"]:
    for it in ["lonely","worried_sleep","suicide_consider","suicide_plan","suicide_attempt"]:
        for sex in ["girls","boys"]:
            d = multi[(multi.item==it)&(multi.sex==sex)&multi[x].notna()].copy(); d = d[d.groupby("iso3").year.transform("nunique")>=2]; d["wt"] = 1/d.se**2
            if d.iso3.nunique() < 8: continue
            m = pf.feols(f"rate ~ {x} | iso3 + year", data=d, weights="wt", vcov={"CRV1":"iso3"})
            out.append(dict(exposure=x, item=it, sex=sex, n_rounds=len(d), n_countries=d.iso3.nunique(), coef_per10=10*m.coef()[x], se_per10=10*m.se()[x], dose_mean=d[x].mean(), dose_within_sd=d.groupby("iso3")[x].transform(lambda s: s-s.mean()).std()))
O = pd.DataFrame(out); O.to_csv(T/"gshs_fe_itu.csv", index=False)
print(O.pivot_table(index=["exposure","item"], columns="sex", values=["coef_per10","se_per10"]).round(2).to_string()); print(O.groupby("exposure")[["n_rounds","n_countries","dose_within_sd"]].first().round(1).to_string())
