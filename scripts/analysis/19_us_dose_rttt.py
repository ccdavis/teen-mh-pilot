"""US follow-ups: (a) NTIA state smartphone-internet dose vs YRBS state sad/hopeless and ACS, state+year FE by sex; (b) Race to the Top event-time plot (YRBS girls/boys, NSDUH, ACS)."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
T = pathlib.Path("results/tables"); pd.set_option("display.width", 220)
fips = {"AL":1,"AK":2,"AZ":4,"AR":5,"CA":6,"CO":8,"CT":9,"DE":10,"DC":11,"FL":12,"GA":13,"HI":15,"ID":16,"IL":17,"IN":18,"IA":19,"KS":20,"KY":21,"LA":22,"ME":23,"MD":24,"MA":25,"MI":26,"MN":27,"MS":28,"MO":29,"MT":30,"NE":31,"NV":32,"NH":33,"NJ":34,"NM":35,"NY":36,"NC":37,"ND":38,"OH":39,"OK":40,"OR":41,"PA":42,"RI":44,"SC":45,"SD":46,"TN":47,"TX":48,"UT":49,"VT":50,"VA":51,"WA":53,"WV":54,"WI":55,"WY":56}
N = pd.read_csv("data/compiled/ntia/ntia_state_year.csv"); N = N[(N.group=="hh_teen12_17")&(N.indicator.isin(["person_uses_smartphone_internet","person_internet_any","hh_mobile_data_plan"]))&(N.year!=2012)]
D = N.pivot_table(index=["state","year"], columns="indicator", values="share").reset_index().rename(columns={"state":"statefip","person_uses_smartphone_internet":"smart","person_internet_any":"inet","hh_mobile_data_plan":"dataplan"})
# interpolate to odd years 2009-2019 within state (waves 2009,2010,2011,2013,2015,2017,2019)
rows = []
for sf, d in D.groupby("statefip"):
    d = d.set_index("year").reindex(range(2009, 2024)); d[["smart","inet","dataplan"]] = d[["smart","inet","dataplan"]].interpolate(limit_direction="both"); d["statefip"] = sf; rows.append(d.reset_index())
D = pd.concat(rows); D.to_csv(T/"ntia_state_dose_interp.csv", index=False)
yr = pd.read_csv(T/"yrbs_state_year_sex.csv"); yr = yr[yr.item=="sad"]; yr["statefip"] = yr.sitecode.astype(str).str[:2].map(fips); yr = yr[yr.statefip.notna()]; yr["statefip"] = yr.statefip.astype(int); yr["y"] = 100*yr.p; yr["wt"] = 1/(100*yr.se)**2
x = yr.merge(D, on=["statefip","year"]); x = x[x.year.between(2011,2019)]
print("(a) YRBS sad/hopeless on NTIA teen-household smartphone-internet share (interpolated), state+year FE, 2011-2019:")
for sx in ["girls","boys"]:
    d = x[x.sexlab==sx]
    for v in ["smart","dataplan"]:
        m = pf.feols(f"y ~ {v} | statefip + year", data=d, weights="wt", vcov={"CRV1":"statefip"}); print(f"  {sx:5s} {v:8s} coef per +100pp = {m.coef().iloc[0]:+.2f} (se {m.se().iloc[0]:.2f}) per 10pp = {m.coef().iloc[0]/10:+.2f}  N={m._N} states={d.statefip.nunique()}")
a = pd.read_csv(T/"acs_state_year_sex_1217.csv"); a["y"] = 100*a.rate; a["wt"] = 1/(100*a.se)**2; a["sexlab"] = a.sex.map({1:"boys",2:"girls"}); xa = a.merge(D, on=["statefip","year"]); xa = xa[xa.year.between(2011,2019)]
for sx in ["girls","boys"]:
    m = pf.feols("y ~ smart | statefip + year", data=xa[xa.sexlab==sx], weights="wt", vcov={"CRV1":"statefip"}); print(f"  ACS {sx:5s} smart coef per 10pp = {m.coef().iloc[0]/10:+.3f} (se {m.se().iloc[0]/10:.3f})")
# (b) RTTT event time
P = pd.read_csv(T/"state_year_policy_fips.csv"); win = P[P.rttt_winner==1].groupby("statefip").year.min().rename("award"); 
def es(df, y, wt, label):
    d = df.merge(win, on="statefip", how="left"); d["k"] = (d.year - d.award).clip(-6, 8); d.loc[d.award.isna(), "k"] = -1; d["k"] = d.k.astype(int)
    d = d[d.year.between(2005, 2019)]
    m = pf.feols(f"{y} ~ i(k, ref=-1) | statefip + year", data=d, weights=wt, vcov={"CRV1":"statefip"}); t = m.tidy().reset_index(); t["k"] = t.Coefficient.astype(str).str.extract(r"(-?\d+)\]?$")[0].astype(float); t["series"] = label; return t[["series","k","Estimate","Std. Error"]]
out = [es(yr[yr.sexlab=="girls"], "y", "wt", "YRBS sad/hopeless girls"), es(yr[yr.sexlab=="boys"], "y", "wt", "YRBS sad/hopeless boys"), es(a[a.sexlab=="girls"], "y", "wt", "ACS girls"), es(a[a.sexlab=="boys"], "y", "wt", "ACS boys")]
ns = pd.read_csv(T/"validation_state_nsduh_vs_acs.csv"); ns["year"] = (ns.year+0.5).astype(int); ns["wt"] = 1/ns.nsduh_se**2; out.append(es(ns, "nsduh", "wt", "NSDUH youth MDE"))
E = pd.concat(out); E.to_csv(T/"rttt_event_time.csv", index=False); print("\n(b) RTTT event-time (ref = year before award):"); print(E.pivot(index="k", columns="series", values="Estimate").round(2).to_string())
