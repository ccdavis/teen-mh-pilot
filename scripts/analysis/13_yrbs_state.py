"""YRBS state files: sad/hopeless, considered suicide, made a plan, attempted suicide and daily-plus social-media use by state x year x sex
(weighted), and state-level check vs ACS 12-17.

Two SADC releases are read: sadc_2023 (39 state sites, 1991-2023) and sadc_2025 (29 state sites, 1991-2025; a different set of states,
with different fixed-width column positions, see data/external/yrbs/README.md). For every site x year the newest release that has it is
used (`release` column), so 2025 and the five states only in the 2025 release (DE LA NY SD WV) come from sadc_2025 and the states that
did not take part in 2025 (AK AL AR CO FL GA IA ID MD NC NJ PA TX WY) keep their sadc_2023 rows. Items: sad (q26), consider (q27), plan (q28),
attempt (q29, any attempt), socmed (several times a day or more; 2023 q80 / 2025 q77, asked from 2023 only). Output yrbs_state_year_sex.csv
(one row per site x year x sex x item; p = weighted share, se from the effective sample size) is read by 16_policy_t2.py, 19_us_dose_rttt.py
(item sad only) and 33_yrbs_ban_did.py."""
import pandas as pd, numpy as np, pathlib, glob, pyfixest as pf
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; EXT = ROOT/"data/external/yrbs"
# column positions (0-based start, end) from the SADC SAS input programs; the raw items are 1-character strings
REL = {"sadc_2023": dict(cs=[(0,5),(113,121),(124,134),(158,161),(161,164),(164,167),(280,281),(281,282),(282,283),(283,284),(331,332)]),
       "sadc_2025": dict(cs=[(0,5),(113,121),(124,134),(158,161),(161,164),(164,167),(265,266),(266,267),(267,268),(268,269),(313,314)])}
names = ["sitecode","year","weight","age","sex","grade","q_sad","q_consider","q_plan","q_attempt","q_socmed"]
def extract(release):
    out = []
    for f in sorted(glob.glob(str(EXT/release/f"{release}_state_*.dat"))):
        for chunk in pd.read_fwf(f, colspecs=REL[release]["cs"], names=names, dtype={c: str for c in names if c != "weight"}, chunksize=300000):
            chunk = chunk[chunk.weight.notna() & chunk.sex.isin(["1","2"])]
            chunk["sad"] = chunk.q_sad.map({"1":1.0,"2":0.0}); chunk["consider"] = chunk.q_consider.map({"1":1.0,"2":0.0}); chunk["plan"] = chunk.q_plan.map({"1":1.0,"2":0.0})
            chunk["attempt"] = chunk.q_attempt.map({"1":0.0,"2":1.0,"3":1.0,"4":1.0,"5":1.0})
            chunk["socmed"] = chunk.q_socmed.map({"1":0.0,"2":0.0,"3":0.0,"4":0.0,"5":0.0,"6":1.0,"7":1.0,"8":1.0})
            for col in ["sad","consider","plan","attempt","socmed"]:
                c = chunk[chunk[col].notna()].assign(sw=lambda d: d.weight, sw2=lambda d: d.weight**2, swy=lambda d: d.weight*d[col], n=1)
                g = c.groupby(["sitecode","year","sex"])[["sw","sw2","swy","n"]].sum().reset_index(); g["item"] = col; out.append(g)
    d = pd.concat(out).groupby(["sitecode","year","sex","item"]).sum().reset_index(); d["release"] = release; d["year"] = d.year.astype(int)
    return d
d25 = extract("sadc_2025"); d23 = extract("sadc_2023")
d23["st"] = d23.sitecode.str[:2]; d25["st"] = d25.sitecode.str[:2]
have25 = set(zip(d25.st, d25.year))
d = pd.concat([d25, d23[~pd.Series(list(zip(d23.st, d23.year))).isin(have25).values]], ignore_index=True)
d["p"] = d.swy/d.sw; d["neff"] = d.sw**2/d.sw2
pc = d.p.clip(lower=0.5/d.n, upper=1-0.5/d.n); d["se"] = np.sqrt(pc*(1-pc)/d.neff)  # floor keeps SE > 0 when every respondent answered the same way
d["sexlab"] = d.sex.map({"1":"girls","2":"boys"}); d = d.drop(columns="st").sort_values(["item","sitecode","year","sex"]); d.to_csv(T/"yrbs_state_year_sex.csv", index=False)
print(d.groupby(["item","year"]).sitecode.nunique().unstack(0).to_string())
print("release by year:\n", d[d.item=="sad"].drop_duplicates(["sitecode","year"]).groupby(["year","release"]).size().unstack(fill_value=0).tail(6).to_string())
# state FIPS from postal code
fips = {"AL":1,"AK":2,"AZ":4,"AR":5,"CA":6,"CO":8,"CT":9,"DE":10,"DC":11,"FL":12,"GA":13,"HI":15,"ID":16,"IL":17,"IN":18,"IA":19,"KS":20,"KY":21,"LA":22,"ME":23,"MD":24,"MA":25,"MI":26,"MN":27,"MS":28,"MO":29,"MT":30,"NE":31,"NV":32,"NH":33,"NJ":34,"NM":35,"NY":36,"NC":37,"ND":38,"OH":39,"OK":40,"OR":41,"PA":42,"RI":44,"SC":45,"SD":46,"TN":47,"TX":48,"UT":49,"VT":50,"VA":51,"WA":53,"WV":54,"WI":55,"WY":56}
d["statefip"] = d.sitecode.str[:2].map(fips)
a = pd.read_csv(T/"acs_state_year_sex_1217.csv"); a["sexlab"] = a.sex.map({1:"boys",2:"girls"}); a["acs"] = 100*a.rate; a["acs_se"] = 100*a.se
for item in ["sad","consider"]:
    x = d[(d.item==item)&(d.year>=2008)].merge(a[["statefip","year","sexlab","acs","acs_se"]], on=["statefip","year","sexlab"]); x["y"] = 100*x.p; x["wt"] = 1/(100*x.se)**2
    print(f"\n{item}: state x year x sex panel n={len(x)}, states={x.statefip.nunique()}")
    for fe, lab in [("statefip + year", "state+year FE"), ("statefip^sexlab + year^sexlab", "state×sex + year×sex FE")]:
        m = pf.feols(f"y ~ acs | {fe}", data=x, weights="wt", vcov={"CRV1":"statefip"}); print(f"  {lab}: slope={m.coef().iloc[0]:.3f} se={m.se().iloc[0]:.3f}")
    x.to_csv(T/f"validation_state_yrbs_{item}_vs_acs.csv", index=False)
