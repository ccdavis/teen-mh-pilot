"""State youth survey county panel: (1) LTE onset event study at county level (WA, ME, MN with pre-2011 data); (2) NTIA CBSA adoption dose 2011-2019;
(3) descriptive trends by state. Outcome: sad_hopeless (YRBS wording) where available; MN considered_suicide 1998-2019."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; pd.set_option("display.width", 220)
p = pd.read_csv(ROOT/"data/compiled/state_surveys/state_survey_county_panel.csv", low_memory=False); p = p[(p.geography_type=="county")&p.geography_fips.notna()].copy(); p["fips"] = p.geography_fips.astype(int)
p = p[p.value_pct.notna()]
# one series per county-year-item-sex: pool grades (mean of grade rows) for 'all' rows; keep HS-type grades only where mixed
hs = p[p.grade_or_age.astype(str).isin(["9","10","11","12","9-12","6-12","8","10","12","all"])]
S = hs.groupby(["state","fips","year","item","sex"]).agg(value=("value_pct","mean"), n=("n","sum"), k=("value_pct","size")).reset_index()
S.to_csv(T/"state_survey_county_series.csv", index=False)
print(S[S.sex=="all"].groupby(["state","item"]).agg(counties=("fips","nunique"), years=("year","nunique"), y0=("year","min"), y1=("year","max")).to_string())
xw = pd.read_csv(ROOT/"data/compiled/lte/county_cbsa_2013.csv", dtype=str); xw["fips"] = xw.fips.astype(int); xw["cbsa"] = xw.cbsa_code.astype(int)  # 2013 county-to-CBSA crosswalk written by scripts/download/lte/build_lte_launches.py
on = pd.read_csv(ROOT/"data/compiled/lte/lte_onset_by_cbsa.csv"); od = pd.to_datetime(on.first_launch_date, format="mixed", errors="coerce"); on["onset_year"] = od.dt.year + (od.dt.month>6).astype(int)
cty = xw[["fips","cbsa"]].drop_duplicates("fips").merge(on[["cbsa_code","onset_year"]].rename(columns={"cbsa_code":"cbsa"}), on="cbsa", how="left")
S = S.merge(cty, on="fips", how="left"); S["metro"] = S.cbsa.notna()
# (1) event study: sad_hopeless (WA, ME) + MN considered_suicide (as MN has no YRBS sadness), sex=all; treated = year >= onset_year; non-metro & undated = never treated (rural counties: LTE came ~2013-14, so this is a bound)
def es(d, label, min_pre=2):
    d = d.copy(); d["k"] = (d.year - d.onset_year).clip(-6, 8); d.loc[d.onset_year.isna(), "k"] = -1; d["k"] = d.k.fillna(-1).astype(int); d["treated"] = (d.year >= d.onset_year).astype(int); d["sy"] = d.state+"_"+d.year.astype(str)
    m = pf.feols("value ~ treated | fips + sy", data=d, vcov={"CRV1":"fips"}); e = pf.feols("value ~ i(k, ref=-1) | fips + sy", data=d, vcov={"CRV1":"fips"}); t = e.tidy().reset_index(); t["k"] = t.Coefficient.astype(str).str.extract(r"(-?\d+)\]?$")[0].astype(float); t["series"] = label
    print(f"{label}: DiD={m.coef().iloc[0]:+.2f} (se {m.se().iloc[0]:.2f}) N={m._N} counties={d.fips.nunique()} dated-metro counties={d[d.onset_year.notna()].fips.nunique()}"); return t[["series","k","Estimate","Std. Error"]]
out = []
d1 = S[(S.item=="sad_hopeless")&(S.sex=="all")&(S.state.isin(["WA","ME"]))&(S.year<=2019)]; out.append(es(d1, "Sad/hopeless, WA+ME counties 2009-2019"))
d2 = S[(S.item=="considered_suicide")&(S.sex=="all")&(S.state.isin(["WA","ME","MN"]))&(S.year<=2019)]; out.append(es(d2, "Considered suicide, WA+ME+MN counties 1998-2019"))
d3 = S[(S.item=="considered_suicide")&(S.sex=="all")&(S.state=="MN")&(S.year<=2019)]; out.append(es(d3, "Considered suicide, MN counties 1998-2019"))
pd.concat(out).to_csv(T/"state_survey_lte_event.csv", index=False)
# (2) NTIA CBSA dose (teen-household smartphone internet), interpolated to survey years, 2011-2019
N = pd.read_csv(ROOT/"data/compiled/ntia/ntia_cbsa_year.csv"); N = N[(N.group=="hh_teen12_17")&(N.indicator=="person_uses_smartphone_internet")&(N.year!=2012)&(N.n_unweighted>=30)]
rows = []
for cb, d in N.groupby("cbsa"):
    d = d.set_index("year").reindex(range(2011, 2024)); d["share"] = d.share.interpolate(limit_direction="both"); d["cbsa"] = cb; rows.append(d.reset_index()[["cbsa","year","share"]])
ND = pd.concat(rows); ND["cbsa"] = ND.cbsa.astype(int)
Sd = S.merge(ND, on=["cbsa","year"], how="inner"); Sd = Sd[Sd.year.between(2011,2019)]; Sd["sy"] = Sd.state+"_"+Sd.year.astype(str)
print("\n(2) NTIA CBSA smartphone-internet dose (interpolated), county + state x year FE, 2011-2019:")
res = []
for it in ["sad_hopeless","considered_suicide"]:
    for sx in ["all","female","male"]:
        d = Sd[(Sd.item==it)&(Sd.sex==sx)]
        if d.fips.nunique() < 20: continue
        m = pf.feols("value ~ share | fips + sy", data=d, vcov={"CRV1":"cbsa"}); res.append(dict(item=it, sex=sx, coef_per10pp=m.coef().iloc[0]/10, se=m.se().iloc[0]/10, n=m._N, counties=d.fips.nunique(), cbsas=d.cbsa.nunique(), states=";".join(sorted(d.state.unique()))))
        print(f"  {it:18s} {sx:6s} per 10pp: {m.coef().iloc[0]/10:+.2f} (se {m.se().iloc[0]/10:.2f}) N={m._N} counties={d.fips.nunique()} cbsas={d.cbsa.nunique()} states={sorted(d.state.unique())}")
pd.DataFrame(res).to_csv(T/"state_survey_ntia_dose.csv", index=False)
# (3) trends by state: mean across counties, sad_hopeless and considered_suicide
tr = S[S.sex=="all"].groupby(["state","item","year"]).value.mean().reset_index(); tr.to_csv(T/"state_survey_trends.csv", index=False)
print(tr[tr.item.isin(["sad_hopeless","considered_suicide"])].pivot_table(index="year", columns=["item","state"], values="value").round(1).to_string())
