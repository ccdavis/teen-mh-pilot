"""State youth survey county panel: (1) LTE onset event study at county level (WA, ME, MN with pre-2011 data); (2) NTIA CBSA adoption
dose 2011-2019; (3) descriptive trends by state. Outcome: sad_hopeless (YRBS wording) where available; MN considered_suicide 1998-2019.

Unit of analysis for (1) and (2): county x grade series. For each state, item and sex, only the grade categories the state reports in
every survey year are kept, and a state's all-grade aggregate row is used instead of single grades when it reports one every year
(Washington grades 8/10/12; Maine's 9-12 and Pennsylvania's 6-12 aggregates; Minnesota grade 9, the only grade asked both before and
after its 2013 redesign; California 7/9/11; Illinois 8/10/12). Changes in which grades a state surveys therefore cannot show up as
changes in distress. Fixed effects: county x grade and state x year. Event time is binned: the three years before onset form the
reference (the surveys are biennial or triennial, so no single pre-onset year is observed for every onset cohort); k <= -6 and k >= 8
are endpoint bins. SE clustered by 2013 CBSA (by county for counties outside any CBSA).

Outputs (results/tables/): state_survey_county_grade_series.csv (the unit panel), state_survey_county_series.csv (county means over
the kept grades; read by 24_county_screen_dose.py), state_survey_lte_event.csv, state_survey_lte_did.csv, state_survey_ntia_dose.csv,
state_survey_trends.csv.
"""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; pd.set_option("display.width", 220)
p = pd.read_csv(ROOT/"data/compiled/state_surveys/state_survey_county_panel.csv", low_memory=False); p = p[(p.geography_type=="county")&p.geography_fips.notna()].copy(); p["fips"] = p.geography_fips.astype(int)
p = p[p.value_pct.notna()]; p["grade"] = p.grade_or_age.astype(str)
# grade categories reported in every survey year of the state (per item and sex); an all-grade aggregate wins when it is always there
AGG = {"9-12", "6-12"}; NOT_GRADES = {"Non_Traditional", "all", "nan"}
def kept_grades(d):
    per = d.groupby("grade").year.nunique(); every = set(per[per == d.year.nunique()].index) - NOT_GRADES
    return (every & AGG) or every
keep = []
for (st, it, sx), d in p.groupby(["state", "item", "sex"]):
    g = kept_grades(d); keep.append(d[d.grade.isin(g)])
    if sx == "all": print(f"  {st} {it:22s} grades kept: {sorted(g)}")
G = pd.concat(keep).groupby(["state","fips","year","item","sex","grade"]).agg(value=("value_pct","mean"), n=("n","sum")).reset_index()
G.to_csv(T/"state_survey_county_grade_series.csv", index=False)
S = G.groupby(["state","fips","year","item","sex"]).agg(value=("value","mean"), n=("n","sum"), k=("value","size")).reset_index()
S.to_csv(T/"state_survey_county_series.csv", index=False)
print(S[S.sex=="all"].groupby(["state","item"]).agg(counties=("fips","nunique"), years=("year","nunique"), y0=("year","min"), y1=("year","max")).to_string())
xw = pd.read_csv(ROOT/"data/compiled/lte/county_cbsa_2013.csv", dtype=str); xw["fips"] = xw.fips.astype(int); xw["cbsa"] = xw.cbsa_code.astype(int)  # 2013 county-to-CBSA crosswalk written by scripts/download/lte/build_lte_launches.py
on = pd.read_csv(ROOT/"data/compiled/lte/lte_onset_by_cbsa.csv"); od = pd.to_datetime(on.first_launch_date, format="mixed", errors="coerce"); on["onset_year"] = od.dt.year + (od.dt.month>6).astype(int)
cty = xw[["fips","cbsa"]].drop_duplicates("fips").merge(on[["cbsa_code","onset_year"]].rename(columns={"cbsa_code":"cbsa"}), on="cbsa", how="left")
G = G.merge(cty, on="fips", how="left"); G["metro"] = G.cbsa.notna()
G["unit"] = G.fips.astype(str) + "_" + G.grade; G["sy"] = G.state + "_" + G.year.astype(str); G["cl"] = G.cbsa.fillna(G.fips).astype(int).astype(str)
# (1) event study: sad_hopeless (WA, ME) + MN considered_suicide (as MN has no YRBS sadness), sex=all; treated = year >= onset_year;
#     non-metro & undated = never treated (rural counties: LTE came ~2013-14, so this is a bound)
def es(d, label):
    d = d.copy(); d["k"] = (d.year - d.onset_year).clip(-6, 8); d.loc[d.onset_year.isna(), "k"] = -1; d["k"] = d.k.fillna(-1).astype(int)
    d["kb"] = d.k.where(~d.k.between(-3, -1), -1)  # reference bin = the three years before onset
    d["treated"] = (d.year >= d.onset_year).astype(int)
    cov = d[d.onset_year.notna()].groupby("onset_year").k.apply(lambda s: sorted(s.unique())); print(f"  {label}: event years observed per onset cohort:", dict(cov))
    m = pf.feols("value ~ treated | unit + sy", data=d, vcov={"CRV1":"cl"}); e = pf.feols("value ~ i(kb, ref=-1) | unit + sy", data=d, vcov={"CRV1":"cl"})
    t = e.tidy().reset_index(); t["k"] = t.Coefficient.astype(str).str.extract(r"(-?\d+)\]?$")[0].astype(float); t["series"] = label
    did = dict(series=label, did=m.coef().iloc[0], se=m.se().iloc[0], n=m._N, units=d.unit.nunique(), counties=d.fips.nunique(), dated_counties=d[d.onset_year.notna()].fips.nunique(), clusters=d.cl.nunique(), y0=int(d.year.min()), y1=int(d.year.max()))
    print(f"{label}: DiD={did['did']:+.2f} (se {did['se']:.2f}) N={did['n']} county-grade units={did['units']} counties={did['counties']} dated-metro counties={did['dated_counties']} clusters={did['clusters']}")
    return t[["series","k","Estimate","Std. Error"]], did
out, dids = [], []
d1 = G[(G.item=="sad_hopeless")&(G.sex=="all")&(G.state.isin(["WA","ME"]))&(G.year<=2019)]; t, dd = es(d1, "Sad/hopeless, WA+ME counties 2009-2019"); out.append(t); dids.append(dd)
d2 = G[(G.item=="considered_suicide")&(G.sex=="all")&(G.state.isin(["WA","ME","MN"]))&(G.year<=2019)]; t, dd = es(d2, "Considered suicide, WA+ME+MN counties 1998-2019"); out.append(t); dids.append(dd)
d3 = G[(G.item=="considered_suicide")&(G.sex=="all")&(G.state=="MN")&(G.year<=2019)]; t, dd = es(d3, "Considered suicide, MN counties 1998-2019"); out.append(t); dids.append(dd)
pd.concat(out).to_csv(T/"state_survey_lte_event.csv", index=False); pd.DataFrame(dids).to_csv(T/"state_survey_lte_did.csv", index=False)
# (2) NTIA CBSA dose (teen-household smartphone internet), interpolated to survey years, 2011-2019
N = pd.read_csv(ROOT/"data/compiled/ntia/ntia_cbsa_year.csv"); N = N[(N.group=="hh_teen12_17")&(N.indicator=="person_uses_smartphone_internet")&(N.year!=2012)&(N.n_unweighted>=30)]
rows = []
for cb, d in N.groupby("cbsa"):
    d = d.set_index("year").reindex(range(2011, 2024)); d["share"] = d.share.interpolate(limit_direction="both"); d["cbsa"] = cb; rows.append(d.reset_index()[["cbsa","year","share"]])
ND = pd.concat(rows); ND["cbsa"] = ND.cbsa.astype(int)
Gd = G.merge(ND, on=["cbsa","year"], how="inner"); Gd = Gd[Gd.year.between(2011,2019)]
print("\n(2) NTIA CBSA smartphone-internet dose (interpolated), county x grade + state x year FE, 2011-2019:")
res = []
for it in ["sad_hopeless","considered_suicide"]:
    for sx in ["all","female","male"]:
        d = Gd[(Gd.item==it)&(Gd.sex==sx)]
        if d.fips.nunique() < 20: continue
        m = pf.feols("value ~ share | unit + sy", data=d, vcov={"CRV1":"cbsa"}); res.append(dict(item=it, sex=sx, coef_per10pp=m.coef().iloc[0]/10, se=m.se().iloc[0]/10, n=m._N, counties=d.fips.nunique(), cbsas=d.cbsa.nunique(), states=";".join(sorted(d.state.unique()))))
        print(f"  {it:18s} {sx:6s} per 10pp: {m.coef().iloc[0]/10:+.2f} (se {m.se().iloc[0]/10:.2f}) N={m._N} counties={d.fips.nunique()} cbsas={d.cbsa.nunique()} states={sorted(d.state.unique())}")
pd.DataFrame(res).to_csv(T/"state_survey_ntia_dose.csv", index=False)
# (3) trends by state: mean across counties (over the kept grades), sad_hopeless and considered_suicide
tr = S[S.sex=="all"].groupby(["state","item","year"]).value.mean().reset_index(); tr.to_csv(T/"state_survey_trends.csv", index=False)
print(tr[tr.item.isin(["sad_hopeless","considered_suicide"])].pivot_table(index="year", columns=["item","state"], values="value").round(1).to_string())
