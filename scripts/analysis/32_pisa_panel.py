"""PISA 2012-2022 panel: school loneliness, belonging and life satisfaction against in-school and out-of-school digital hours.
Reads data/extracts/pisa_panel/pisa_panel_student.parquet (scripts/download/pisa_panel/build_panel.py) and writes results/tables/pisa_panel_*.csv:
  _samples        students, countries and item coverage per wave
  _country_wave   weighted country x wave x sex means (lonely, belong, life satisfaction, digital hours, ESCS)
  _trends         mean of country means by wave x sex x OECD/partner, all-available and balanced country sets
  _fe             two-way (country + wave) fixed-effects regressions of country-sex-wave means on digital-hours means, by sex, +/- ESCS
  _longdiff(_fit) country long differences 2012->2018 (loneliness, belonging) and 2015->2018, 2018->2022 (life satisfaction) and their fitted slopes
  _h3_2015(_desc) 2015 student-level test: well-being on test anxiety x in-school (>1 h) and x out-of-school (>4 h) weekday internet use, by sex
  _dose(_slope)   life satisfaction and loneliness by out-of-school hours band and wave, weighted means and country-FE contrasts; linear slopes by wave
  _policy2018     2018 within-country comparison of schools with/without a written digital-device-use policy (SC156Q01HA)
Student weights (W_FSTUWT) throughout; student-level models have country fixed effects and school-clustered SEs; cell-level models cluster by country.
"""
import pandas as pd, numpy as np, pyfixest as pf, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; T.mkdir(parents=True, exist_ok=True); pd.set_option("display.width", 230)
p = pd.read_parquet(ROOT/"data/extracts/pisa_panel/pisa_panel_student.parquet")
p = p[p.wt.notna() & (p.wt > 0) & p.girl.notna()].copy(); p["CNT"] = p.CNT.astype(str); p["sch"] = p.sch.astype(str)
p["girl"] = p.girl.astype(int); p["sex"] = np.where(p.girl == 1, "girls", "boys")
BANDS = ["none", "<=1 h", "1-2 h", "2-4 h", "4-6 h", ">6 h"]
def wavg(x, w):
    m = x.notna() & w.notna(); return float(np.average(x[m], weights=w[m])) if m.any() and w[m].sum() > 0 else np.nan
def by_sex(d):
    yield "all", d
    yield "girls", d[d.girl == 1]
    yield "boys", d[d.girl == 0]

# ---- 1. samples -------------------------------------------------------------------------------------------------------
S = p.groupby("year").apply(lambda g: pd.Series(dict(students=len(g), countries=g.CNT.nunique(), schools=g.sch.nunique(), ict_countries=g[g.ict_country == 1].CNT.nunique(),
    n_lonely=g.lonely.notna().sum(), n_lifesat=g.lifesat.notna().sum(), countries_lifesat=g[g.lifesat.notna()].CNT.nunique(), n_hours=g.hrs_out.notna().sum(), n_anxtest=g.anxtest.notna().sum(),
    share_girls=round(g.girl.mean(), 3), lonely=round(100 * wavg(g.lonely, g.wt), 1), belong=round(100 * wavg(g.belong, g.wt), 1), lifesat=round(wavg(g.lifesat, g.wt), 2), hrs_school=round(wavg(g.hrs_school, g.wt), 2), hrs_out=round(wavg(g.hrs_out, g.wt), 2))), include_groups=False).reset_index()
S.to_csv(T/"pisa_panel_samples.csv", index=False); print(S.to_string(index=False))

# ---- 2. country x wave x sex means ------------------------------------------------------------------------------------------
MEAS = ["lonely", "outsider", "belong", "awkward", "lifesat", "lifesat_low", "hrs_school", "hrs_out", "hrs_wkend", "sch_1h", "out_2h", "out_4h", "first_net_lt10", "socnet_daily", "chat_school_daily", "escs"]
rows = []
for (y, c), g in p.groupby(["year", "CNT"], observed=True):
    for sx, gg in by_sex(g):
        r = dict(year=y, CNT=c, sex=sx, oecd=int(gg.oecd.iloc[0]), ict_country=int(gg.ict_country.iloc[0]), n=len(gg), n_lonely=int(gg.lonely.notna().sum()), n_lifesat=int(gg.lifesat.notna().sum()), n_hours=int(gg.hrs_out.notna().sum()))
        for m in MEAS:
            v = wavg(gg[m], gg.wt); r[m] = 100 * v if m not in ("lifesat", "hrs_school", "hrs_out", "hrs_wkend", "escs") else v
        rows.append(r)
CW = pd.DataFrame(rows); CW.to_csv(T/"pisa_panel_country_wave.csv", index=False)
# an item counts as asked in a country-wave if at least half the students answered it
CW["has_lonely"] = CW.n_lonely > 0.5 * CW.n; CW["has_lifesat"] = CW.n_lifesat > 0.5 * CW.n; CW["has_hours"] = CW.n_hours > 0.5 * CW.n
print("country-waves:", len(CW[CW.sex == "all"]), "| with lonely:", CW[(CW.sex == "all") & CW.has_lonely].groupby("year").size().to_dict(), "| with life satisfaction:", CW[(CW.sex == "all") & CW.has_lifesat].groupby("year").size().to_dict(), "| with hours:", CW[(CW.sex == "all") & CW.has_hours].groupby("year").size().to_dict())

# ---- 3. trends: mean of country means, all-available and balanced sets ------------------------------------------------------------
def balanced(flag, years):
    ok = CW[(CW.sex == "all") & CW[flag] & CW.year.isin(years)].groupby("CNT").year.nunique(); return set(ok[ok == len(years)].index)
SETS = {"lonely": ("has_lonely", [2012, 2015, 2018, 2022]), "belong": ("has_lonely", [2012, 2015, 2018, 2022]), "outsider": ("has_lonely", [2012, 2015, 2018, 2022]), "lifesat": ("has_lifesat", [2015, 2018, 2022]), "lifesat_low": ("has_lifesat", [2015, 2018, 2022]),
        "hrs_school": ("has_hours", [2012, 2015, 2018]), "hrs_out": ("has_hours", [2012, 2015, 2018]), "sch_1h": ("has_hours", [2012, 2015, 2018]), "out_4h": ("has_hours", [2012, 2015, 2018]), "first_net_lt10": ("has_hours", [2012, 2015, 2018]), "socnet_daily": ("has_hours", [2012, 2015, 2018])}
rows = []
for m, (flag, yrs) in SETS.items():
    bal = balanced(flag, yrs)
    for setname, cset in [("all available", None), ("balanced", bal)]:
        d = CW[CW[flag] & CW[m].notna()] if cset is None else CW[CW[flag] & CW[m].notna() & CW.CNT.isin(cset)]
        for (y, sx), g in d.groupby(["year", "sex"]):
            for grp, gg in [("all", g), ("OECD", g[g.oecd == 1]), ("partner", g[g.oecd == 0])]:
                if len(gg): rows.append(dict(measure=m, set=setname, year=y, sex=sx, group=grp, value=gg[m].mean(), n_countries=len(gg), countries=" ".join(sorted(gg.CNT)) if setname == "balanced" and grp == "all" and sx == "all" else ""))
TR = pd.DataFrame(rows); TR.to_csv(T/"pisa_panel_trends.csv", index=False)
print("\nbalanced-set trends (mean of country means):"); print(TR[(TR.set == "balanced") & (TR.group == "all")].pivot_table(index=["measure", "sex"], columns="year", values="value").round(2).to_string())

# ---- 4. two-way FE panel on country-sex-wave cells --------------------------------------------------------------------------------------
rows = []
for sample, yrs in [("2012-2018", [2012, 2015, 2018]), ("2012-2022", [2012, 2015, 2018, 2022])]:
    for sx in ["all", "girls", "boys"]:
        cells = CW[(CW.sex == sx) & CW.has_hours & CW.has_lonely & CW.year.isin(yrs) & (CW.ict_country == 1)].copy()
        keep = cells.groupby("CNT").year.nunique(); cells = cells[cells.CNT.isin(keep[keep >= 2].index)]
        for y in ["lonely", "belong", "lifesat", "lifesat_low"]:
            d = cells[cells[y].notna()] if y not in ("lifesat", "lifesat_low") else cells[cells[y].notna() & cells.has_lifesat]
            if y in ("lifesat", "lifesat_low"):
                k2 = d.groupby("CNT").year.nunique(); d = d[d.CNT.isin(k2[k2 >= 2].index)]
            if d.CNT.nunique() < 10: continue
            for spec, xs in [("hours", ["hrs_school", "hrs_out"]), ("shares", ["sch_1h", "out_4h"])]:
                for ctrl in ["none", "escs"]:
                    f = f"{y} ~ {' + '.join(xs)}{' + escs' if ctrl == 'escs' else ''} | CNT + year"
                    m = pf.feols(f, data=d, vcov={"CRV1": "CNT"})
                    sc = 10 if spec == "shares" else 1   # shares are in pp: report per 10 pp of students
                    rows.append(dict(outcome=y, sex=sx, sample=sample, spec=spec, controls=ctrl, coef_school=sc * m.coef()[xs[0]], se_school=sc * m.se()[xs[0]], coef_out=sc * m.coef()[xs[1]], se_out=sc * m.se()[xs[1]],
                                     n_cells=m._N, n_countries=d.CNT.nunique(), waves=d.year.nunique(), mean_y=d[y].mean(), mean_school=d[xs[0]].mean(), mean_out=d[xs[1]].mean()))
FE = pd.DataFrame(rows); FE.to_csv(T/"pisa_panel_fe.csv", index=False)
print("\ntwo-way FE (country + wave) of country means; hours spec, with ESCS:"); print(FE[(FE.spec == "hours") & (FE.controls == "escs")][["outcome", "sex", "sample", "coef_school", "se_school", "coef_out", "se_out", "n_cells", "n_countries"]].round(3).to_string(index=False))

# ---- 5. long differences --------------------------------------------------------------------------------------------------------------
def longdiff(y0, y1, flag, meas):
    a = CW[(CW.year == y0) & CW[flag] & CW.has_hours & (CW.ict_country == 1)].set_index(["CNT", "sex"]); b = CW[(CW.year == y1) & CW[flag] & CW.has_hours & (CW.ict_country == 1)].set_index(["CNT", "sex"])
    both = a.index.intersection(b.index); d = (b.loc[both, meas] - a.loc[both, meas]).add_prefix("d_"); d["oecd"] = a.loc[both, "oecd"]; d["period"] = f"{y0}->{y1}"
    for m in meas: d[f"{m}_{y0}"] = a.loc[both, m]; d[f"{m}_{y1}"] = b.loc[both, m]
    return d.reset_index()
LD = pd.concat([longdiff(2012, 2018, "has_lonely", ["lonely", "belong", "hrs_school", "hrs_out", "sch_1h", "out_4h"]), longdiff(2015, 2018, "has_lifesat", ["lifesat", "lifesat_low", "lonely", "hrs_school", "hrs_out", "sch_1h", "out_4h"]),
                longdiff(2018, 2022, "has_lifesat", ["lifesat", "lifesat_low", "lonely", "hrs_school", "hrs_out", "sch_1h", "out_4h"])], ignore_index=True)
LD.to_csv(T/"pisa_panel_longdiff.csv", index=False)
rows = []
for per, g in LD.groupby("period"):
    for y in ["d_lonely", "d_belong", "d_lifesat", "d_lifesat_low"]:
        if y not in g or g[y].isna().all(): continue
        for x in ["d_hrs_school", "d_hrs_out"]:
            for sx in ["all", "girls", "boys"]:
                d = g[(g.sex == sx) & g[y].notna() & g[x].notna()]
                if len(d) < 8: continue
                m = pf.feols(f"{y} ~ {x}", data=d, vcov="hetero"); r = np.corrcoef(d[x], d[y])[0, 1]
                rows.append(dict(period=per, outcome=y[2:], regressor=x[2:], sex=sx, slope=m.coef()[x], se=m.se()[x], r=r, n=len(d), mean_dy=d[y].mean(), mean_dx=d[x].mean()))
LDF = pd.DataFrame(rows); LDF.to_csv(T/"pisa_panel_longdiff_fit.csv", index=False)
print("\nlong-difference slopes:"); print(LDF[LDF.sex != "all"].round(3).to_string(index=False) if len(LDF) else "(none)")

# ---- 6. 2015 student-level H3 test: anxiety x in-school vs out-of-school internet use --------------------------------------------------------
d15 = p[(p.year == 2015) & (p.ict_country == 1) & p.anxtest.notna() & p.hrs_school.notna() & p.hrs_out.notna() & p.escs.notna() & p.grade.notna()].copy()
d15["anx"] = (d15.anxtest - d15.anxtest.mean()) / d15.anxtest.std()
d15["hi_anx"] = (d15.anxtest > d15.groupby("CNT").anxtest.transform("median")).astype(float)
d15["belong_idx100"] = 100 * d15.belong_idx
print(f"\n2015 H3 sample: {len(d15):,} students, {d15.CNT.nunique()} ICT-module systems, {d15.sch.nunique():,} schools")
rows = []
OUTS = [("lonely", "Lonely at school (agree)", 100), ("belong", "Belongs at school (agree)", 100), ("lifesat", "Life satisfaction (0-10)", 1), ("lifesat_low", "Life satisfaction 0-4", 100), ("belong_idx100", "Belonging index (hundredths of SD)", 1)]
for y, lab, sc in OUTS:
    for sx, dd in by_sex(d15):
        dd = dd[dd[y].notna()]
        if len(dd) < 5000: continue
        for anxvar, aname in [("anx", "ANXTEST (SD units)"), ("hi_anx", "above country median")]:
            m = pf.feols(f"{y} ~ {anxvar} + sch_1h + out_4h + {anxvar}:sch_1h + {anxvar}:out_4h + escs + C(grade)" + (" + girl" if sx == "all" else "") + " | CNT", data=dd, weights="wt", vcov={"CRV1": "sch"})
            c, s = m.coef(), m.se()
            rows.append(dict(outcome=lab, y=y, sex=sx, anxiety=aname, anx=sc * c[anxvar], se_anx=sc * s[anxvar], sch_1h=sc * c["sch_1h"], se_sch=sc * s["sch_1h"], out_4h=sc * c["out_4h"], se_out=sc * s["out_4h"],
                             anx_x_sch=sc * c[f"{anxvar}:sch_1h"], se_anx_x_sch=sc * s[f"{anxvar}:sch_1h"], anx_x_out=sc * c[f"{anxvar}:out_4h"], se_anx_x_out=sc * s[f"{anxvar}:out_4h"], n=m._N, countries=dd.CNT.nunique(), mean_y=sc * wavg(dd[y], dd.wt), unit="pp" if sc == 100 else ("points" if y == "lifesat" else "hundredths SD")))
        # continuous hours version (per hour/day)
        m = pf.feols(f"{y} ~ anx + hrs_school + hrs_out + anx:hrs_school + anx:hrs_out + escs + C(grade)" + (" + girl" if sx == "all" else "") + " | CNT", data=dd, weights="wt", vcov={"CRV1": "sch"})
        c, s = m.coef(), m.se()
        rows.append(dict(outcome=lab, y=y, sex=sx, anxiety="ANXTEST (SD units), hours continuous", anx=sc * c["anx"], se_anx=sc * s["anx"], sch_1h=sc * c["hrs_school"], se_sch=sc * s["hrs_school"], out_4h=sc * c["hrs_out"], se_out=sc * s["hrs_out"],
                         anx_x_sch=sc * c["anx:hrs_school"], se_anx_x_sch=sc * s["anx:hrs_school"], anx_x_out=sc * c["anx:hrs_out"], se_anx_x_out=sc * s["anx:hrs_out"], n=m._N, countries=dd.CNT.nunique(), mean_y=sc * wavg(dd[y], dd.wt), unit="pp" if sc == 100 else ("points" if y == "lifesat" else "hundredths SD")))
H3 = pd.DataFrame(rows); H3.to_csv(T/"pisa_panel_h3_2015.csv", index=False)
print("\n2015 H3 (ANXTEST SD units, binary use):"); print(H3[H3.anxiety == "ANXTEST (SD units)"][["outcome", "sex", "anx", "se_anx", "sch_1h", "se_sch", "out_4h", "se_out", "anx_x_sch", "se_anx_x_sch", "anx_x_out", "se_anx_x_out", "n"]].round(2).to_string(index=False))
rows = []
for sx, dd in by_sex(d15):
    for hi, g in dd.groupby("hi_anx"):
        rows.append(dict(sex=sx, hi_anx=int(hi), n=len(g), sch_1h=100 * wavg(g.sch_1h, g.wt), out_4h=100 * wavg(g.out_4h, g.wt), hrs_school=wavg(g.hrs_school, g.wt), hrs_out=wavg(g.hrs_out, g.wt), lonely=100 * wavg(g.lonely, g.wt), belong=100 * wavg(g.belong, g.wt), lifesat=wavg(g.lifesat, g.wt), anxtest=wavg(g.anxtest, g.wt)))
pd.DataFrame(rows).to_csv(T/"pisa_panel_h3_desc.csv", index=False)

# ---- 7. dose-response by wave ---------------------------------------------------------------------------------------------------------------
rows, srows = [], []
for y in [2012, 2015, 2018, 2022]:
    d = p[(p.year == y) & (p.ict_country == 1) & p.band_out.notna() & p.escs.notna() & p.grade.notna()].copy(); d["band_out"] = d.band_out.astype(str)
    for b in BANDS: d[f"b_{BANDS.index(b)}"] = (d.band_out == b).astype(float)
    for sx, dd in by_sex(d):
        for outc, sc in [("lifesat", 1), ("lonely", 100), ("lifesat_low", 100)]:
            ddd = dd[dd[outc].notna()]
            if len(ddd) < 5000: continue
            X = " + ".join(f"b_{i}" for i in range(len(BANDS)) if i != 2)   # reference band: 1-2 h
            m = pf.feols(f"{outc} ~ {X} + escs + C(grade)" + (" + girl" if sx == "all" else "") + " | CNT", data=ddd, weights="wt", vcov={"CRV1": "sch"})
            for i, b in enumerate(BANDS):
                g = ddd[ddd.band_out == b]
                rows.append(dict(year=y, sex=sx, outcome=outc, band=b, share=100 * g.wt.sum() / ddd.wt.sum(), mean=sc * wavg(g[outc], g.wt), n=len(g), coef=0.0 if i == 2 else sc * m.coef()[f"b_{i}"], se=0.0 if i == 2 else sc * m.se()[f"b_{i}"], countries=ddd.CNT.nunique()))
            ml = pf.feols(f"{outc} ~ hrs_out + hrs_school + escs + C(grade)" + (" + girl" if sx == "all" else "") + " | CNT", data=ddd, weights="wt", vcov={"CRV1": "sch"})
            srows.append(dict(year=y, sex=sx, outcome=outc, slope_out=sc * ml.coef()["hrs_out"], se_out=sc * ml.se()["hrs_out"], slope_school=sc * ml.coef()["hrs_school"], se_school=sc * ml.se()["hrs_school"], n=ml._N, countries=ddd.CNT.nunique(), mean=sc * wavg(ddd[outc], ddd.wt), mean_hrs_out=wavg(ddd.hrs_out, ddd.wt)))
DO = pd.DataFrame(rows); DO.to_csv(T/"pisa_panel_dose.csv", index=False); DS = pd.DataFrame(srows)
# did the gradient steepen? pooled 2015+2018 on countries with the ICT module in both waves, slope x wave interaction (same item both waves)
both = set(CW[(CW.year == 2015) & (CW.sex == "all") & CW.has_hours].CNT) & set(CW[(CW.year == 2018) & (CW.sex == "all") & CW.has_hours].CNT)
d = p[p.year.isin([2015, 2018]) & p.CNT.isin(both) & p.hrs_out.notna() & p.hrs_school.notna() & p.escs.notna() & p.grade.notna()].copy(); d["y18"] = (d.year == 2018).astype(float); d["cy"] = d.CNT + "_" + d.year.astype(str)
irows = []
for sx, dd in by_sex(d):
    for outc, sc in [("lifesat", 1), ("lonely", 100), ("lifesat_low", 100)]:
        ddd = dd[dd[outc].notna()]
        if ddd.year.nunique() < 2: continue
        m = pf.feols(f"{outc} ~ hrs_out + hrs_out:y18 + hrs_school + hrs_school:y18 + escs + C(grade)" + (" + girl" if sx == "all" else "") + " | cy", data=ddd, weights="wt", vcov={"CRV1": "sch"})
        irows.append(dict(sex=sx, outcome=outc, slope_out_2015=sc * m.coef()["hrs_out"], se_2015=sc * m.se()["hrs_out"], change_2018=sc * m.coef()["hrs_out:y18"], se_change=sc * m.se()["hrs_out:y18"], slope_school_2015=sc * m.coef()["hrs_school"], se_school_2015=sc * m.se()["hrs_school"], change_school_2018=sc * m.coef()["hrs_school:y18"], se_change_school=sc * m.se()["hrs_school:y18"], n=m._N, countries=len(both)))
DS.to_csv(T/"pisa_panel_dose_slope.csv", index=False); pd.DataFrame(irows).to_csv(T/"pisa_panel_dose_steepen.csv", index=False)
print("\ndose-response slopes per hour/day outside school (country FE, ESCS, grade):"); print(DS[DS.sex != "all"].round(3).to_string(index=False)); print(pd.DataFrame(irows).round(3).to_string(index=False))

# ---- 8. 2018 school digital-device policy statement (SC156Q01HA) --------------------------------------------------------------------------
d18 = p[(p.year == 2018) & p.sch_policy.notna() & p.escs.notna() & p.grade.notna()].copy(); d18["private"] = d18.private.fillna(0.0)
print(f"\n2018 policy sample: {len(d18):,} students, {d18.CNT.nunique()} systems, share in schools with a written digital-device policy: {wavg(d18.sch_policy, d18.wt) if len(d18) else float('nan'):.3f}")
rows = []
for y, lab, sc in [("chat_school_daily", "Chats online at school (almost) every day (ICT module)", 100), ("sch_1h", "Internet >1 h/weekday at school (ICT module)", 100), ("hrs_school", "Internet hours/weekday at school (ICT module)", 1), ("out_4h", "Internet >4 h/weekday outside school (placebo)", 100),
                   ("lonely", "Lonely at school (agree)", 100), ("belong", "Belongs at school (agree)", 100), ("lifesat", "Life satisfaction (0-10)", 1), ("lifesat_low", "Life satisfaction 0-4", 100), ("belong_idx", "Belonging index (hundredths of SD)", 100)]:
    for sx, dd in by_sex(d18):
        dd = dd[dd[y].notna()]
        if len(dd) < 5000: continue
        m = pf.feols(f"{y} ~ sch_policy + escs + private + C(grade)" + (" + girl" if sx == "all" else "") + " | CNT", data=dd, weights="wt", vcov={"CRV1": "sch"})
        rows.append(dict(outcome=lab, y=y, sex=sx, coef=sc * m.coef()["sch_policy"], se=sc * m.se()["sch_policy"], n=m._N, countries=dd.CNT.nunique(), mean=sc * wavg(dd[y], dd.wt), share_policy=100 * wavg(dd.sch_policy, dd.wt),
                         n_schools=dd.sch.nunique(), unit="pp" if sc == 100 and y != "belong_idx" else ("points" if sc == 1 and y == "lifesat" else ("hours" if y == "hrs_school" else "hundredths SD"))))
PO = pd.DataFrame(rows); PO.to_csv(T/"pisa_panel_policy2018.csv", index=False)
print(PO.pivot_table(index="outcome", columns="sex", values=["coef", "se"], sort=False).round(2).to_string() if len(PO) else "(no 2018 policy rows)")
