"""Continuous county broadband coverage and the AT&T December-2010 mobile footprint against (1) the state youth-survey county x grade
panel (results/tables/state_survey_county_grade_series.csv, written by 23_state_surveys.py) and (2) NVSS county youth (10-19) suicide
from CDC WONDER. Usage (repository root): uv run python scripts/analysis/34_broadband_instruments.py

(1) Continuous dose, 2010-2021. County broadband shares from data/compiled/broadband/county_broadband_panel.csv (NTIA SBI / National
    Broadband Map 2010-2014, FCC Form 477 2014-2021) are linearly interpolated to each survey spring (year + 0.25; within half a year of
    the nearest round at the ends) and regressed on sad_hopeless and considered_suicide with the Phase 1 design: county x grade and
    state x year fixed effects, standard errors clustered by 2013 CBSA (county outside CBSAs), unweighted county x grade series.
    Coefficients are reported per +10 percentage points of county population covered, and as the percent change in the outcome mean
    per within-county standard deviation of the dose (the scale of Churchill & Johnson's "one standard deviation" state result).
(2) AT&T 2010 footprint. att = share of county population (2000 blocks) with any AT&T Mobility mobile-wireless coverage in the Dec-2010
    SBI release (data/compiled/broadband/county_att_mobile_2010.csv; Myers & Hooper 2026 use the same release). Minnesota's 1998-2019
    county series (waves 1998 2001 2004 2007 2010 2013 2016 2019) brackets the June 2007 - February 2011 AT&T iPhone exclusivity:
    event-style regressions of each item on att x wave (reference 2007, the last pre-iPhone wave), with county x grade and year fixed
    effects; pooled att x post-2007; Myers & Hooper's binary treated (>90%) vs control (<10%) contrast; a Verizon-footprint comparison;
    pre-trend slopes over 1998-2007; long differences 2007->2013 and 2007->2019 (and the 2001->2007 placebo) across counties; and a
    pooled differential-trend test for 2010-2019 across all six states (att x linear time, state x year FE). Maine (16 counties) only
    supports a cross-sectional gradient.
(3) County youth suicide. CDC WONDER county tables (ages 10-19, suicide X60-X84/Y87.0, pooled 1999-2002, 2003-07, 2008-12, 2013-17,
    2018-22; counts under 10 suppressed) from data/compiled/broadband/county_youth_suicide_periods.csv: change in the average annual
    rate per 100,000 between periods regressed on att and on 2010-2014 broadband growth, state fixed effects, population weights,
    counties with unsuppressed counts in both periods (zeros are reported, 1-9 are suppressed; a midpoint-imputed variant is shown).
Outputs results/tables/bb_*.csv (see the bottom of the file for the list).
"""
import pathlib, numpy as np, pandas as pd, pyfixest as pf, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; C = ROOT/"data/compiled/broadband"; pd.set_option("display.width", 230)
G = pd.read_csv(T/"state_survey_county_grade_series.csv"); G["fips"] = G.fips.astype(int); G["grade"] = G.grade.astype(str)
xw = pd.read_csv(ROOT/"data/compiled/lte/county_cbsa_2013.csv", dtype=str); xw["fips"] = xw.fips.astype(int); xw["cbsa"] = xw.cbsa_code.astype(int); xw = xw.drop_duplicates("fips")[["fips", "cbsa", "cbsa_type"]]
on = pd.read_csv(ROOT/"data/compiled/lte/lte_onset_by_cbsa.csv"); od = pd.to_datetime(on.first_launch_date, format="mixed", errors="coerce"); on["onset_year"] = od.dt.year + (od.dt.month > 6).astype(int)
G = G.merge(xw, on="fips", how="left"); G["unit"] = G.fips.astype(str) + "_" + G.grade; G["sy"] = G.state + "_" + G.year.astype(str); G["cl"] = G.cbsa.fillna(G.fips).astype(int).astype(str)
P = pd.read_csv(C/"county_broadband_panel.csv", dtype={"fips": str}); P["fips"] = P.fips.astype(int)
A = pd.read_csv(C/"county_att_mobile_2010.csv", dtype={"fips": str}); A["fips"] = A.fips.astype(int); A["att"] = A.att_share_dec2010; A["state_fips"] = A.fips // 1000
S = pd.read_csv(C/"county_youth_suicide_periods.csv", dtype={"fips": str}); S["fips"] = S.fips.astype(int)
def fe(formula, d, cl="cl", weights=None):
    cols = [c for c in set(__import__("re").findall(r"[A-Za-z_][A-Za-z0-9_]*", formula.replace("i(", " ").replace("ref=", " "))) if c in d.columns] + [cl] + ([weights] if weights else [])
    d = d.dropna(subset=cols); fes = [f.strip() for f in formula.split("|")[1].split("+")] if "|" in formula else []
    for f in fes: d = d[d.groupby(f)[cols[0]].transform("size") >= 2]  # drop singletons so the demeaner never sees an empty group
    return pf.feols(formula, data=d, vcov={"CRV1": cl}, weights=weights)
def row(m, term, **kw):
    t = m.tidy(); return dict(coef=t.loc[term, "Estimate"], se=t.loc[term, "Std. Error"], n=m._N, **kw)
# ---------------------------------------------------------------- panel summary
ps = P.groupby("round").agg(counties=("fips", "nunique"), **{c: (c, "mean") for c in ["wireline_any", "wireline_ge10", "wireline_ge25", "fixed_ge25", "mobile_any", "mobile_ge3", "anytech_ge10", "att_mobile_any"]}).reset_index()
pw = P.groupby("round").apply(lambda d: pd.Series({c + "_popw": np.average(d[c].fillna(0), weights=d.population.fillna(0)) if d[c].notna().any() else np.nan for c in ["wireline_any", "wireline_ge10", "wireline_ge25", "fixed_ge25", "mobile_any", "mobile_ge3"]}), include_groups=False).reset_index()
ps = ps.merge(pw, on="round"); ps["source"] = P.groupby("round").source.first().values; ps.round(4).to_csv(T/"bb_panel_summary.csv", index=False)
print("Broadband panel, unweighted county means by round:\n", ps[["round", "counties", "wireline_any", "wireline_ge10", "wireline_ge25", "fixed_ge25", "mobile_any", "mobile_ge3", "anytech_ge10"]].round(3).to_string(index=False))
# ---------------------------------------------------------------- (1) continuous dose
MEAS = ["wireline_any", "wireline_ge10", "wireline_ge25", "fixed_ge25", "mobile_any", "mobile_ge3", "anytech_ge10"]
def interp(meas, years=range(2010, 2022)):
    rows = []
    for fips, d in P[["fips", "year_frac", meas]].dropna().groupby("fips"):
        x, y = d.year_frac.values, d[meas].values
        if len(x) < 1: continue
        o = np.argsort(x); x, y = x[o], y[o]
        for yr in years:
            t = yr + 0.25
            if x.min() - 0.5 <= t <= x.max() + 0.5: rows.append((fips, yr, float(np.interp(t, x, y))))
    return pd.DataFrame(rows, columns=["fips", "year", "dose"])
D = {m: interp(m) for m in MEAS}
lte = pd.read_csv(T/"state_survey_lte_did.csv") if (T/"state_survey_lte_did.csv").exists() else None
res = []
for meas in MEAS:
  for ymax in [2021, 2019]:
    for item in ["sad_hopeless", "considered_suicide"]:
        for sx in ["all", "female", "male"]:
            d = G[(G.item == item) & (G.sex == sx) & G.year.between(2010, ymax)].merge(D[meas], on=["fips", "year"])
            if item == "sad_hopeless": d = d[~((d.state == "MN") & (d.year <= 2010))]  # MN's pre-2013 sadness item is a 30-day question (see notes/state_surveys.md)
            d = d[d.groupby("unit").value.transform("size") >= 2].copy()  # singleton county-grade units carry no within information
            if d.fips.nunique() < 20 or d.year.nunique() < 2: continue
            d["dose100"] = d.dose * 100; d["dose_w"] = d.dose100 - d.groupby("unit").dose100.transform("mean"); sdw = d.dose_w.std()
            if not sdw > 0.01: continue
            try: m = fe("value ~ dose100 | unit + sy", d)
            except BaseException as e: print(f"  skipped {meas} {item} {sx}: {type(e).__name__}"); continue
            c = m.coef().iloc[0]
            res.append(dict(measure=meas, item=item, sex=sx, sample=f"2010-{ymax}", coef_per10pp=10 * c, se_per10pp=10 * m.se().iloc[0], n=m._N, units=d.unit.nunique(), counties=d.fips.nunique(), clusters=d.cl.nunique(), states=";".join(sorted(d.state.unique())), y0=int(d.year.min()), y1=int(d.year.max()),
                            mean_outcome=d.value.mean(), dose_mean=d.dose100.mean(), dose_sd_between=d.groupby("fips").dose100.mean().std(), dose_sd_within=sdw, pct_per_within_sd=100 * c * sdw / d.value.mean(), ci_lo_per10pp=10 * (c - 1.96 * m.se().iloc[0]), ci_hi_per10pp=10 * (c + 1.96 * m.se().iloc[0])))
R1 = pd.DataFrame(res); R1.to_csv(T/"bb_dose_results.csv", index=False)
print("\n(1) Continuous dose per +10 pp of county population covered (county x grade + state x year FE, CBSA clusters):")
print(R1[["measure", "item", "sex", "sample", "coef_per10pp", "se_per10pp", "n", "counties", "states", "y0", "y1", "mean_outcome", "dose_sd_within", "pct_per_within_sd"]].round(2).to_string(index=False))
# ---------------------------------------------------------------- (2) AT&T Dec-2010 footprint
Acols = A[["fips", "att", "att_share_jun2010", "att_share_bg_dec2010", "verizon_share_dec2010", "mh_group", "population_2000"]]
mn = G[(G.state == "MN") & (G.sex == "all")].merge(Acols, on="fips"); mn["post"] = (mn.year >= 2010).astype(int); mn["vz"] = mn.verizon_share_dec2010
ev, dd, ld = [], [], []
ITEMS = {"considered_suicide": "Considered suicide (grade 9, 1998-2019)", "attempted_suicide": "Attempted suicide (grade 9, 1998-2019)", "sad_hopeless": "Sad all/most of last 30 days (grades 6/9/12, 1998-2010)",
         "hopeless_30d": "Discouraged or hopeless, last 30 days (1998-2010)", "nervous_30d": "Nervous, worried or upset, last 30 days (1998-2010)", "stress_high": "Under great stress or pressure, last 30 days (1998-2010)"}
for item, label in ITEMS.items():
    d = mn[mn.item == item].copy()
    if d.empty: continue
    e = fe("value ~ i(year, att, ref=2007) | unit + year", d); t = e.tidy().reset_index(); t["year"] = pd.to_numeric(t.Coefficient.str.extract(r"(19\d\d|20\d\d)")[0], errors="coerce"); t = t.dropna(subset=["year"]); t["year"] = t.year.astype(int)
    for _, r in t.iterrows(): ev.append(dict(item=item, label=label, year=r.year, coef=r.Estimate, se=r["Std. Error"], n=e._N, counties=d.fips.nunique()))
    ev.append(dict(item=item, label=label, year=2007, coef=0.0, se=0.0, n=e._N, counties=d.fips.nunique()))
    pre = d[d.year <= 2007].copy(); pre["tr"] = (pre.year - 2007) / 3
    mp = fe("value ~ att:tr | unit + year", pre); dd.append(row(mp, "att:tr", item=item, label=label, spec="pre-trend 1998-2007: att x waves (per 3-year wave)", counties=pre.fips.nunique(), y0=1998, y1=2007, mean_pre2007=d[d.year <= 2007].value.mean()))
    if d.year.max() >= 2010:
        m = fe("value ~ att:post | unit + year", d); dd.append(row(m, "att:post", item=item, label=label, spec="att share (0-1) x post-2007", counties=d.fips.nunique(), y0=int(d.year.min()), y1=int(d.year.max()), mean_pre2007=d[d.year <= 2007].value.mean()))
        db = d[d.mh_group != "intermediate"].copy(); db["treated"] = (db.mh_group == "treated").astype(int)
        m = fe("value ~ treated:post | unit + year", db); dd.append(row(m, "treated:post", item=item, label=label, spec="Myers-Hooper binary: treated (>90%) vs control (<10%) x post-2007", counties=db.fips.nunique(), y0=int(db.year.min()), y1=int(db.year.max()), mean_pre2007=db[db.year <= 2007].value.mean()))
        m = fe("value ~ vz:post | unit + year", d); dd.append(row(m, "vz:post", item=item, label=label, spec="comparison: Verizon share (0-1) x post-2007 (no iPhone until Feb 2011)", counties=d.fips.nunique(), y0=int(d.year.min()), y1=int(d.year.max()), mean_pre2007=d[d.year <= 2007].value.mean()))
        m = fe("value ~ att:post + vz:post | unit + year", d); dd.append(row(m, "att:post", item=item, label=label, spec="att x post, controlling Verizon x post", counties=d.fips.nunique(), y0=int(d.year.min()), y1=int(d.year.max()), mean_pre2007=d[d.year <= 2007].value.mean()))
    if item in ("considered_suicide", "attempted_suicide"):  # long differences across counties (grade 9)
        w = d.pivot_table(index="fips", columns="year", values="value").join(A.set_index("fips")[["att", "population_2000", "cbsa_type"]] if "cbsa_type" in A else A.set_index("fips")[["att", "population_2000"]]).join(xw.set_index("fips").cbsa_type)
        w["metro"] = (w.cbsa_type == "Metropolitan Statistical Area").astype(int); w["lpop"] = np.log(w.population_2000)
        for name, y1, y0 in [("2007->2013", 2013, 2007), ("2007->2019", 2019, 2007), ("2007->2010", 2010, 2007), ("placebo 2001->2007", 2007, 2001), ("placebo 1998->2004", 2004, 1998)]:
            x = w[[y0, y1, "att", "population_2000", "metro", "lpop"]].dropna().copy(); x["dy"] = x[y1] - x[y0]
            for wt, lab in [(None, "unweighted"), ("population_2000", "pop-2000 weighted")]:
                x = x[x.population_2000 > 0]; m = pf.feols("dy ~ att", data=x, vcov="HC1", weights=wt); ld.append(dict(item=item, window=name, controls="none", weights=lab, coef=m.coef()["att"], se=m.se()["att"], n=m._N, mean_change=x.dy.mean()))
                m = pf.feols("dy ~ att + metro + lpop", data=x, vcov="HC1", weights=wt); ld.append(dict(item=item, window=name, controls="metro + log pop", weights=lab, coef=m.coef()["att"], se=m.se()["att"], n=m._N, mean_change=x.dy.mean()))
            if name == "2007->2019" and item == "considered_suicide": x.reset_index()[["fips", "att", "dy", "population_2000", "metro"]].rename(columns={"dy": "change_2007_2019"}).to_csv(T/"bb_scatter_mn_considered.csv", index=False)
            if name == "2007->2013" and item == "considered_suicide": x.reset_index()[["fips", "att", "dy", "population_2000", "metro"]].rename(columns={"dy": "change_2007_2013"}).to_csv(T/"bb_scatter_mn_considered_2013.csv", index=False)
EV, DD, LD = pd.DataFrame(ev).sort_values(["item", "year"]), pd.DataFrame(dd), pd.DataFrame(ld)
EV.to_csv(T/"bb_att_event_mn.csv", index=False); DD.to_csv(T/"bb_att_did_mn.csv", index=False); LD.to_csv(T/"bb_att_longdiff_mn.csv", index=False)
print("\n(2) Minnesota: att (Dec-2010 AT&T share, 0-1) x wave, reference 2007, county x grade + year FE, CBSA/county clusters:")
print(EV.pivot_table(index="year", columns="item", values="coef").round(2).to_string()); print(EV.pivot_table(index="year", columns="item", values="se").round(2).to_string())
print(DD[["item", "spec", "coef", "se", "n", "counties", "mean_pre2007"]].round(2).to_string(index=False)); print(LD.round(2).to_string(index=False))
# differential trend 2010-2019 across the six states, and Maine / Washington gradients
tr = []
for item in ["sad_hopeless", "considered_suicide"]:
    for sx in ["all", "female", "male"]:
        d = G[(G.item == item) & (G.sex == sx) & G.year.between(2010, 2019)].merge(Acols, on="fips"); d = d[~((d.state == "MN") & (d.item == "sad_hopeless"))].copy(); d["t"] = (d.year - 2010) / 10
        if d.fips.nunique() < 20 or d.year.nunique() < 2: continue
        m = fe("value ~ att:t | unit + sy", d); tr.append(row(m, "att:t", item=item, sex=sx, states=";".join(sorted(d.state.unique())), counties=d.fips.nunique(), y0=int(d.year.min()), y1=int(d.year.max()), spec="pooled: att x (years since 2010)/10, county x grade + state x year FE"))
        for st, ds in d.groupby("state"):
            if ds.year.nunique() >= 3 and ds.fips.nunique() >= 15 and sx == "all":
                m = fe("value ~ att:t | unit + sy", ds); tr.append(row(m, "att:t", item=item, sex=sx, states=st, counties=ds.fips.nunique(), y0=int(ds.year.min()), y1=int(ds.year.max()), spec="single state: att x (years since 2010)/10"))
me = G[(G.state == "ME") & (G.sex == "all")].merge(Acols, on="fips")
for item in ["sad_hopeless", "considered_suicide"]:
    w = me[me.item == item].pivot_table(index="fips", columns="year", values="value").join(A.set_index("fips").att)
    for lab, y in [("level 2009", w[2009]), ("change 2009->2013", w[2013] - w[2009]), ("change 2009->2019", w[2019] - w[2009]), ("change 2009->2021", w[2021] - w[2009])]:
        x = pd.DataFrame({"y": y, "att": w.att}).dropna(); m = pf.feols("y ~ att", data=x, vcov="HC1"); tr.append(dict(coef=m.coef()["att"], se=m.se()["att"], n=m._N, item=item, sex="all", states="ME", counties=len(x), y0=2009, y1=2009, spec=f"Maine cross-section: {lab} on att (r = {x.corr().iloc[0,1]:.2f})"))
TR = pd.DataFrame(tr); TR.to_csv(T/"bb_att_trend_states.csv", index=False); print("\n(2b) Differential trends 2010-2019 and Maine gradients:\n", TR.round(2).to_string(index=False))
# AT&T footprint summary: relation to LTE onset and metro status
As = A.merge(xw, on="fips", how="left").merge(on[["cbsa_code", "onset_year"]].rename(columns={"cbsa_code": "cbsa"}), on="cbsa", how="left")
As["metro"] = As.cbsa_type.eq("Metropolitan Statistical Area"); As["lte_by_2012"] = As.onset_year.le(2012)
summ = [dict(stat="counties", value=len(As)), dict(stat="mean att share (unweighted)", value=As.att.mean()), dict(stat="mean att share (pop-2000 weighted)", value=np.average(As.att, weights=As.population_2000)),
        dict(stat="counties treated (>90% in block groups, Myers-Hooper)", value=(As.mh_group == "treated").sum()), dict(stat="counties control (<10%)", value=(As.mh_group == "control").sum()), dict(stat="counties intermediate", value=(As.mh_group == "intermediate").sum()),
        dict(stat="mean att share, metro counties", value=As[As.metro].att.mean()), dict(stat="mean att share, non-metro counties", value=As[~As.metro].att.mean()),
        dict(stat="mean att share, counties with LTE by school year 2012", value=As[As.lte_by_2012].att.mean()), dict(stat="mean att share, dated-LTE counties with LTE after 2012 or undated", value=As[~As.lte_by_2012].att.mean()),
        dict(stat="correlation att share vs Verizon share", value=As.att.corr(As.verizon_share_dec2010)), dict(stat="correlation att share vs LTE onset year (dated metros)", value=As.att.corr(As.onset_year)),
        dict(stat="share of 2000 population in treated counties", value=As.loc[As.mh_group == "treated", "population_2000"].sum() / As.population_2000.sum()), dict(stat="share of 2000 population in control counties", value=As.loc[As.mh_group == "control", "population_2000"].sum() / As.population_2000.sum()),
        dict(stat="MN counties: mean att share", value=As[As.state_fips == 27].att.mean()), dict(stat="MN counties treated / control / intermediate", value=f"{(As[(As.state_fips==27)].mh_group=='treated').sum()} / {(As[(As.state_fips==27)].mh_group=='control').sum()} / {(As[(As.state_fips==27)].mh_group=='intermediate').sum()}"),
        dict(stat="ME counties: mean att share", value=As[As.state_fips == 23].att.mean()), dict(stat="WA counties: mean att share", value=As[As.state_fips == 53].att.mean()),
        dict(stat="June-2010 release: mean att share (incomplete submissions)", value=As.att_share_jun2010.mean()), dict(stat="correlation att Dec-2010 vs June-2010 where June > 0", value=As[As.att_share_jun2010 > 0].att.corr(As[As.att_share_jun2010 > 0].att_share_jun2010))]
pd.DataFrame(summ).to_csv(T/"bb_att_summary.csv", index=False); print("\nAT&T footprint summary:\n", pd.DataFrame(summ).to_string(index=False))
# ---------------------------------------------------------------- (3) county youth suicide
Sw = S.pivot_table(index=["fips", "sex"], columns="period", values=["deaths", "population", "rate_per100k", "suppressed"])
dose = P.pivot_table(index="fips", columns="round", values=["wireline_any", "anytech_ge10", "mobile_any", "fixed_ge25", "wireline_ge25"])
def growth(meas, r0, r1):
    nm = f"d_{meas}_{r0.replace('-', '')}_{r1.replace('-', '')}"  # formulaic reads a hyphen as a minus sign
    try: return (dose[(meas, r1)] - dose[(meas, r0)]).rename(nm)
    except KeyError: return pd.Series(dtype=float, name=nm)
GR = pd.concat([growth("wireline_any", "2010-12", "2014-06"), growth("anytech_ge10", "2011-06", "2014-06"), growth("mobile_any", "2010-12", "2014-06"), growth("fixed_ge25", "2014-12", "2019-12"), growth("wireline_ge25", "2010-12", "2016-12")], axis=1)
sres, sdesc = [], []
WINDOWS = [("2003-2007", "2013-2017"), ("1999-2002", "2003-2007"), ("2008-2012", "2013-2017"), ("2013-2017", "2018-2022"), ("2003-2007", "2018-2022")]
for sex in ["all", "F", "M"]:
    for p0, p1 in WINDOWS:
        try: x = Sw.xs(sex, level="sex")
        except KeyError: continue
        if (("rate_per100k", p0) not in x.columns) or (("rate_per100k", p1) not in x.columns): continue
        for sample in ["large counties (>=50,000 youths/yr; suppressed set to 5)", "unsuppressed counties", "all counties (suppressed set to 5)"]:
            y = pd.DataFrame({"r0": x[("rate_per100k", p0)], "r1": x[("rate_per100k", p1)], "s0": x[("suppressed", p0)], "s1": x[("suppressed", p1)], "pop1": x[("population", p1)], "pop0": x[("population", p0)], "d0": x[("deaths", p0)], "d1": x[("deaths", p1)]})
            if sample.startswith("large"):  # 5-year summed population >= 250,000 (about 50,000 10-19-year-olds a year); a count under 10 is then rare and set to the midpoint 5
                y = y[(y.pop0 >= 250000) & (y.pop1 >= 250000)].copy(); y["r0"] = np.where(y.s0 == 1, 5 / y.pop0 * 1e5, y.r0); y["r1"] = np.where(y.s1 == 1, 5 / y.pop1 * 1e5, y.r1)
            elif sample.startswith("all"): y["r0"] = np.where(y.s0 == 1, 5 / y.pop0 * 1e5, y.r0); y["r1"] = np.where(y.s1 == 1, 5 / y.pop1 * 1e5, y.r1)
            else: y = y[(y.s0 == 0) & (y.s1 == 0)]
            y = y.join(A.set_index("fips")[["att", "mh_group", "state_fips", "population_2000"]]).join(xw.set_index("fips").cbsa_type).join(GR).dropna(subset=["att", "r0", "r1"]).copy()
            y["dy"] = y.r1 - y.r0; y["state"] = y.state_fips.astype(str); y["w"] = y.pop1 / 5; y["metro"] = y.cbsa_type.eq("Metropolitan Statistical Area").astype(int); y["lpop"] = np.log(y.pop1 / 5); impute = sample
            if len(y) < 50: continue
            regs = [("att", "AT&T Dec-2010 share (0-1)")] + [(c, c) for c in GR.columns if y[c].notna().sum() > 50]
            if sex == "all" and (p0, p1) == ("2003-2007", "2013-2017"): yb = y[y.mh_group != "intermediate"].copy(); yb["treated"] = (yb.mh_group == "treated").astype(int); regs.append(("treated", "treated (>90%) vs control (<10%)"))
            for reg, lab in regs:
                dta = yb if reg == "treated" else y; dta = dta.dropna(subset=[reg, "dy", "w", "state"]); dta = dta[dta.w > 0]
                for ctrl in ["", " + metro + lpop"]:
                    if ctrl and reg != "att" and not reg.startswith("d_mobile") and not reg.startswith("d_fixed_ge25"): continue
                    try: m = pf.feols(f"dy ~ {reg}{ctrl} | state", data=dta, vcov={"CRV1": "state"}, weights="w")
                    except BaseException as e: print(f"  skipped suicide fit {sex} {p0}->{p1} {reg}{ctrl} [{sample}]: {type(e).__name__}"); continue
                    sres.append(dict(sex=sex, window=f"{p0} -> {p1}", regressor=lab, sample=sample, controls="metro + log youth pop" if ctrl else "none", coef=m.coef()[reg], se=m.se()[reg], n=m._N, mean_rate_p0=np.average(dta.r0, weights=dta.w), mean_rate_p1=np.average(dta.r1, weights=dta.w), mean_change=np.average(dta.dy, weights=dta.w), share_us_pop=dta.pop1.sum() / x[("population", p1)].sum()))
            if sample.startswith("large") and sex == "all" and (p0, p1) == ("2003-2007", "2013-2017"): y.reset_index()[["fips", "att", "mh_group", "metro", "r0", "r1", "dy", "pop1"]].rename(columns={"r0": "rate_2003_2007", "r1": "rate_2013_2017", "dy": "change", "pop1": "population_2013_2017"}).to_csv(T/"bb_scatter_suicide.csv", index=False)
    # descriptive: population-weighted rate by period and Myers-Hooper group (unsuppressed counties; and all counties with midpoint imputation)
    x = Sw.xs(sex, level="sex") if sex in Sw.index.get_level_values("sex") else None
    if x is None: continue
    for per in [p for p in S.period.unique()]:
        if ("deaths", per) not in x.columns: continue
        z = pd.DataFrame({"deaths": x[("deaths", per)], "pop": x[("population", per)], "sup": x[("suppressed", per)]}).join(A.set_index("fips").mh_group).dropna(subset=["mh_group", "pop"])
        for grp, zz in z.groupby("mh_group"):
            u = zz[zz.sup == 0]; sdesc.append(dict(sex=sex, period=per, group=grp, basis="unsuppressed counties", counties=len(u), deaths=u.deaths.sum(), population=u["pop"].sum(), rate=u.deaths.sum() / u["pop"].sum() * 1e5))
            di = np.where(zz.sup == 1, 5, zz.deaths); sdesc.append(dict(sex=sex, period=per, group=grp, basis="all counties, suppressed counts set to 5", counties=len(zz), deaths=di.sum(), population=zz["pop"].sum(), rate=di.sum() / zz["pop"].sum() * 1e5))
SR, SD = pd.DataFrame(sres), pd.DataFrame(sdesc); SR.to_csv(T/"bb_suicide_results.csv", index=False); SD.to_csv(T/"bb_suicide_desc.csv", index=False)
# att variation inside each county sample (why the large-county sample is uninformative for AT&T)
Sw_all = Sw.xs("all", level="sex"); base = pd.DataFrame({"p0": Sw_all[("population", "2003-2007")], "p1": Sw_all[("population", "2013-2017")], "s0": Sw_all[("suppressed", "2003-2007")], "s1": Sw_all[("suppressed", "2013-2017")]}).join(A.set_index("fips").att).dropna(subset=["att"])
big = base[(base.p0 >= 250000) & (base.p1 >= 250000)]; uns = base[(base.s0 == 0) & (base.s1 == 0)]
pd.DataFrame([dict(sample="large counties (>=50,000 youths/yr)", counties=len(big), att_mean=big.att.mean(), att_sd=big.att.std(), share_att_above_0_9=(big.att > 0.9).mean()),
              dict(sample="unsuppressed counties", counties=len(uns), att_mean=uns.att.mean(), att_sd=uns.att.std(), share_att_above_0_9=(uns.att > 0.9).mean()),
              dict(sample="all counties", counties=len(A), att_mean=A.att.mean(), att_sd=A.att.std(), share_att_above_0_9=(A.att > 0.9).mean())]).to_csv(T/"bb_suicide_samples.csv", index=False)
# ---------------------------------------------------------------- (3b) state-level youth suicide, 1999-2023 (no suppression): the fallback the plan asked for
sf = C/"state_youth_suicide_year.csv"
if sf.exists():
    SY = pd.read_csv(sf, dtype={"state_fips": str}); SY = SY[(SY.suppressed == 0) & SY.deaths.notna()].copy(); SY["state_fips"] = SY.state_fips.astype(int)
    has157 = SY[SY.database == "D157"].groupby(["sex", "year"]).size().index  # bridged-race file (D76) to 2020; single-race file (D157) replaces it from 2018 where available
    SY = SY[(SY.database == "D76") & ~SY.set_index(["sex", "year"]).index.isin(has157) | (SY.database == "D157")]
    sa = A.groupby("state_fips").apply(lambda d: np.average(d.att, weights=d.population_2000), include_groups=False).rename("att_state")
    SY = SY.merge(sa, left_on="state_fips", right_index=True); SY["w"] = SY.population; st_res, st_ev = [], []
    nm = A.merge(xw, on="fips", how="left"); nm["nonmetro"] = ~nm.cbsa_type.eq("Metropolitan Statistical Area")
    nonmetro = nm.groupby("state_fips").apply(lambda d: np.average(d.nonmetro, weights=d.population_2000), include_groups=False).rename("nonmetro_state"); SY = SY.merge(nonmetro, left_on="state_fips", right_index=True)
    for sex in ["all", "F", "M"]:
        d = SY[SY.sex == sex].copy(); d["post"] = (d.year >= 2008).astype(int); d["t"] = (d.year - 2007) / 10
        if d.empty: continue
        m = pf.feols("rate_per100k ~ att_state:post | state_fips + year", data=d, vcov={"CRV1": "state_fips"}, weights="w")
        st_res.append(dict(sex=sex, spec="state AT&T share (0-1) x post-2007, 1999-2023, state + year FE, youth-population weights", coef=m.coef().iloc[0], se=m.se().iloc[0], n=m._N, states=d.state_fips.nunique(), y0=int(d.year.min()), y1=int(d.year.max()), mean_rate_pre=np.average(d[d.year <= 2007].rate_per100k, weights=d[d.year <= 2007].w)))
        m = pf.feols("rate_per100k ~ att_state:post + nonmetro_state:post | state_fips + year", data=d, vcov={"CRV1": "state_fips"}, weights="w")
        st_res.append(dict(sex=sex, spec="same, controlling the state's non-metro population share x post-2007", coef=m.coef()["att_state:post"], se=m.se()["att_state:post"], n=m._N, states=d.state_fips.nunique(), y0=int(d.year.min()), y1=int(d.year.max()), mean_rate_pre=np.average(d[d.year <= 2007].rate_per100k, weights=d[d.year <= 2007].w)))
        st_res.append(dict(sex=sex, spec="non-metro share x post-2007 in that model", coef=m.coef()["nonmetro_state:post"], se=m.se()["nonmetro_state:post"], n=m._N, states=d.state_fips.nunique(), y0=int(d.year.min()), y1=int(d.year.max()), mean_rate_pre=np.nan))
        d19 = d[d.year <= 2019]; m = pf.feols("rate_per100k ~ att_state:post | state_fips + year", data=d19, vcov={"CRV1": "state_fips"}, weights="w")
        st_res.append(dict(sex=sex, spec="same, 1999-2019 (before the pandemic years)", coef=m.coef().iloc[0], se=m.se().iloc[0], n=m._N, states=d19.state_fips.nunique(), y0=1999, y1=2019, mean_rate_pre=np.average(d[d.year <= 2007].rate_per100k, weights=d[d.year <= 2007].w)))
        pre = d[d.year <= 2007]; m = pf.feols("rate_per100k ~ att_state:t | state_fips + year", data=pre, vcov={"CRV1": "state_fips"}, weights="w")
        st_res.append(dict(sex=sex, spec="pre-trend 1999-2007: att_state x years/10", coef=m.coef().iloc[0], se=m.se().iloc[0], n=m._N, states=pre.state_fips.nunique(), y0=1999, y1=2007, mean_rate_pre=np.average(pre.rate_per100k, weights=pre.w)))
        e = pf.feols("rate_per100k ~ i(year, att_state, ref=2007) | state_fips + year", data=d, vcov={"CRV1": "state_fips"}, weights="w"); te = e.tidy().reset_index()
        te["year"] = pd.to_numeric(te.Coefficient.str.extract(r"(19\d\d|20\d\d)")[0], errors="coerce"); te = te.dropna(subset=["year"])
        for _, r in te.iterrows(): st_ev.append(dict(sex=sex, year=int(r.year), coef=r.Estimate, se=r["Std. Error"]))
        st_ev.append(dict(sex=sex, year=2007, coef=0.0, se=0.0))
        # long difference across states: mean rate 2013-17 minus 2003-07 on att_state
        w = d.groupby("state_fips").apply(lambda g: pd.Series({"r0": g[g.year.between(2003, 2007)].deaths.sum() / g[g.year.between(2003, 2007)].population.sum() * 1e5, "r1": g[g.year.between(2013, 2017)].deaths.sum() / g[g.year.between(2013, 2017)].population.sum() * 1e5, "rp": g[g.year.between(1999, 2002)].deaths.sum() / g[g.year.between(1999, 2002)].population.sum() * 1e5, "pop": g[g.year.between(2013, 2017)].population.sum() / 5, "att_state": g.att_state.iloc[0]}), include_groups=False).dropna()
        w["dy"] = w.r1 - w.r0; w["dpre"] = w.r0 - w.rp
        m = pf.feols("dy ~ att_state", data=w, vcov="HC1", weights="pop"); st_res.append(dict(sex=sex, spec="state long difference: rate 2013-17 minus 2003-07 on att_state (pop-weighted)", coef=m.coef()["att_state"], se=m.se()["att_state"], n=m._N, states=len(w), y0=2003, y1=2017, mean_rate_pre=np.average(w.r0, weights=w["pop"])))
        m = pf.feols("dpre ~ att_state", data=w, vcov="HC1", weights="pop"); st_res.append(dict(sex=sex, spec="placebo: rate 2003-07 minus 1999-2002 on att_state", coef=m.coef()["att_state"], se=m.se()["att_state"], n=m._N, states=len(w), y0=1999, y1=2007, mean_rate_pre=np.average(w.rp, weights=w["pop"])))
        if sex == "all": w.reset_index().rename(columns={"r0": "rate_2003_2007", "r1": "rate_2013_2017", "dy": "change"}).to_csv(T/"bb_scatter_suicide_state.csv", index=False)
    pd.DataFrame(st_res).to_csv(T/"bb_suicide_state_results.csv", index=False); pd.DataFrame(st_ev).to_csv(T/"bb_suicide_state_event.csv", index=False)
    print("\n(3b) State youth suicide 1999-2023 on the state's population-weighted AT&T Dec-2010 share:"); print(pd.DataFrame(st_res).round(2).to_string(index=False))
    print(pd.DataFrame(st_ev).pivot_table(index="year", columns="sex", values="coef").round(2).to_string())
else: print("\n(3b) state_youth_suicide_year.csv not found; state-level fallback skipped")
print("\n(3) County youth (10-19) suicide: change in average annual rate per 100k, state FE, population weights:")
print(SR[SR["sample"].str.startswith("large") & SR.regressor.isin(["AT&T Dec-2010 share (0-1)", "treated (>90%) vs control (<10%)", "d_mobile_any_201012_201406", "d_fixed_ge25_201412_201912", "d_anytech_ge10_201106_201406"])][["sex", "window", "regressor", "controls", "coef", "se", "n", "mean_rate_p0", "mean_rate_p1", "share_us_pop"]].round(2).to_string(index=False))
print(SR[(SR.window == "2003-2007 -> 2013-2017") & (SR.regressor == "AT&T Dec-2010 share (0-1)")][["sex", "sample", "controls", "coef", "se", "n", "share_us_pop"]].round(2).to_string(index=False))
print(SD[(SD.sex == "all")].pivot_table(index=["basis", "group"], columns="period", values="rate").round(2).to_string())
print("\nwrote: bb_panel_summary, bb_dose_results, bb_att_event_mn, bb_att_did_mn, bb_att_longdiff_mn, bb_att_trend_states, bb_att_summary, bb_suicide_results, bb_suicide_desc, bb_suicide_samples, bb_suicide_state_results, bb_suicide_state_event, bb_scatter_mn_considered(.csv/_2013), bb_scatter_suicide, bb_scatter_suicide_state")
