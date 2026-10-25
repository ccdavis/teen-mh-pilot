"""NVSS/CDC WONDER monthly suicide mortality 1999-2024: school-calendar seasonality at ages 12-17 vs 18-24/25-34, the summer-vs-school-month
decomposition of the post-2010 rise (H1 vs H2/H3 test), the 2020 school-closure anomaly, and the day-of-week pattern.

Inputs (scripts/download/nvss/wonder_fetch.py): data/compiled/nvss/d76_*.csv (1999-2020, bridged-race populations) and d158_*.csv
(2018-2024, single-race populations); deaths = ICD-10 113 cause list GR113-124 (*U03, X60-X84, Y87.0), national, by month and sex,
filtered to single-year ages so that no cell is suppressed. Populations are July 1 estimates by single year of age (WONDER gives no
population for month or weekday tables); exposure = population x days in month / days in year (person-years).
Outputs: results/tables/nvss_*.csv (every number cited by scripts/report/parts/nvss.py)."""
import pathlib, calendar, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[2]; COMP = ROOT/"data/compiled/nvss"; T = ROOT/"results/tables"; T.mkdir(parents=True, exist_ok=True)
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
MON = {m: i for i, m in enumerate(["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."], 1)}
SUMMER = {6, 7, 8}; GROUPS = ["12-17", "18-24", "25-34", "12-14", "15-17", "12-18", "35-54"]; MAIN = ["12-17", "18-24", "25-34"]
PERIODS = {"1999-2003": (1999, 2003), "2005-2009": (2005, 2009), "2008-2010": (2008, 2010), "2011-2014": (2011, 2014), "2015-2019": (2015, 2019),
           "2020": (2020, 2020), "2021-2024": (2021, 2024), "1999-2019": (1999, 2019)}
def num(s): return pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")
def month_num(s): return s.astype(str).str.split(",").str[0].str.strip().map(MON)
def mask_small(df, cols=("deaths",)):
    """WONDER data-use rule: never present counts of 1-9. Internal totals use derived values; published tables blank them."""
    df = df.copy()
    for c in [c for c in df.columns if any(c == k or c.startswith(k + "_") for k in cols)]:
        small = df[c].between(1, 9); df.loc[small, c] = np.nan
        for rc in ("rate" + c[len(c.split("_")[0]):], "crude_rate", "pct_vs_trend", "pct_vs_2019level"):   # a rate or % alongside a masked count would reveal it
            if rc in df.columns: df.loc[small, rc] = np.nan
    return df
def rng(g): a, b = g.split("-"); return range(int(a), int(b) + 1)

# ---------- 1. populations by age group x year x sex (single-year ages summed) ----------
pops = []
for db in ("d76", "d158"):
    p = pd.read_csv(COMP/f"{db}_year_age_sex.csv"); p["year"] = num(p.year).astype(int); p["age_n"] = num(p.age.str.extract(r"(\d+)")[0]); p["population"] = num(p.population); p["deaths_annual"] = num(p.deaths)
    p["sex"] = p.sex.str[0]
    for g in GROUPS:
        s = p[p.age_n.isin(rng(g))].groupby(["year", "sex"], as_index=False).agg(population=("population", "sum"), deaths_annual_single=("deaths_annual", "sum"))
        s["agegrp"] = g; s["db"] = db; pops.append(s)
POP = pd.concat(pops); POP_ALL = POP.groupby(["db", "year", "agegrp"], as_index=False)[["population", "deaths_annual_single"]].sum().assign(sex="A")
POP = pd.concat([POP, POP_ALL], ignore_index=True)

# ---------- 2. monthly counts by age group x sex ----------
# by-sex tables (cells of 1-9 deaths arrive as "Suppressed") and both-sexes tables (never suppressed for these groups). A suppressed
# female (male) cell is recovered internally as both-sexes minus male (female) for period aggregates only (`d_int`); the published
# monthly table keeps it blank (`deaths` NaN, suppressed=True), so no count of 1-9 is presented anywhere.
rows = []
for db in ("d76", "d158"):
    for g in GROUPS:
        d = pd.read_csv(COMP/f"{db}_month_sex_{g}.csv"); d["year"] = num(d.year).astype(int); d["month"] = month_num(d.month); d["deaths"] = num(d.deaths); d["sex"] = d.sex.str[0]
        a = pd.read_csv(COMP/f"{db}_month_all_{g}.csv"); a["year"] = num(a.year).astype(int); a["month"] = month_num(a.month); a["deaths"] = num(a.deaths); a["sex"] = "A"
        d = pd.concat([d[["year", "month", "sex", "deaths"]], a[["year", "month", "sex", "deaths"]]]); d["agegrp"] = g; d["db"] = db; rows.append(d)
M = pd.concat(rows, ignore_index=True); M["suppressed"] = M.deaths.isna(); M["d_int"] = M.deaths
w = M.pivot_table(index=["db", "year", "month", "agegrp"], columns="sex", values="deaths", aggfunc="first")
for sx, other in (("F", "M"), ("M", "F")):
    fill = (w["A"] - w[other]).where(w[sx].isna() & w["A"].notna() & w[other].notna())
    key = M.set_index(["db", "year", "month", "agegrp"]).index; M.loc[(M.sex == sx).values & M.d_int.isna().values, "d_int"] = fill.reindex(key[(M.sex == sx).values & M.d_int.isna().values]).values
print(f"suppressed by-sex cells recovered from both-sexes totals: {int((M.suppressed & M.d_int.notna()).sum())}; still missing: {int(M.d_int.isna().sum())} (groups {sorted(M[M.d_int.isna()].agegrp.unique())})")
M = M.merge(POP[["db", "year", "sex", "agegrp", "population"]], on=["db", "year", "sex", "agegrp"], how="left")
M["days"] = [calendar.monthrange(y, m)[1] for y, m in zip(M.year, M.month)]; M["days_in_year"] = [366 if calendar.isleap(y) else 365 for y in M.year]
M["exposure_py"] = M.population * M.days / M.days_in_year; M["rate"] = 1e5 * M.deaths / M.exposure_py; M["summer"] = M.month.isin(SUMMER).astype(int)
# overlap check 2018-2020 (D76 bridged-race vs D158 single-race): deaths must agree exactly, populations closely
ov = M[M.year.between(2018, 2020)].pivot_table(index=["year", "month", "agegrp", "sex"], columns="db", values=["deaths", "population"]).reset_index()
ov.columns = ["_".join(c).strip("_") for c in ov.columns]; ov["deaths_diff"] = ov.deaths_d158 - ov.deaths_d76; ov["pop_ratio"] = ov.population_d158 / ov.population_d76
ov.to_csv(T/"nvss_db_overlap.csv", index=False)
print(f"D76 vs D158 overlap 2018-2020: {len(ov)} cells; deaths differ in {int((ov.deaths_diff != 0).sum())} cells (max |diff| {ov.deaths_diff.abs().max():.0f}); population ratio D158/D76 range {ov.pop_ratio.min():.4f}-{ov.pop_ratio.max():.4f}")
# series used: D76 for 1999-2020, D158 for 2021-2024
M = M[((M.db == "d76") & (M.year <= 2020)) | ((M.db == "d158") & (M.year >= 2021))].copy()
M["source"] = M.db.map({"d76": "WONDER D76 (UCD 1999-2020)", "d158": "WONDER D158 (UCD 2018-2024 single race)"})
M = M.sort_values(["agegrp", "sex", "year", "month"]).reset_index(drop=True)
mask_small(M[["year", "month", "agegrp", "sex", "deaths", "population", "days", "exposure_py", "rate", "summer", "suppressed", "source"]]).to_csv(T/"nvss_monthly_counts.csv", index=False)
print(f"monthly table: {len(M):,} rows, {M.year.min()}-{M.year.max()}, suppressed cells = {int(M.suppressed.sum())} (groups: {sorted(M[M.suppressed].agegrp.unique())})")
M["deaths"] = M.d_int   # internal: all aggregates below use the recovered series; published tables are masked with mask_small()

# annual rates
A = M.groupby(["agegrp", "sex", "year"], as_index=False).agg(deaths=("deaths", "sum"), exposure_py=("exposure_py", "sum"), population=("population", "first"), n_missing=("deaths", lambda s: int(s.isna().sum())))
A["rate"] = 1e5 * A.deaths / A.exposure_py; mask_small(A).to_csv(T/"nvss_annual.csv", index=False)
print("\nannual suicide rate per 100,000, ages 12-17 by sex (selected years):")
print(A[(A.agegrp == "12-17") & A.year.isin([1999, 2007, 2010, 2013, 2017, 2019, 2020, 2021, 2022, 2023, 2024])].pivot(index="year", columns="sex", values="rate").round(2).to_string())

# ---------- 3. seasonal profiles and summer/school ratios by period ----------
def lrr_ci(d1, e1, d0, e0):
    """rate ratio (d1/e1)/(d0/e0) with Poisson 95% CI on the log scale."""
    rr = (d1 / e1) / (d0 / e0); se = np.sqrt(1 / d1 + 1 / d0); return rr, rr * np.exp(-1.96 * se), rr * np.exp(1.96 * se), se
prof, ratios = [], []
for pname, (y0, y1) in PERIODS.items():
    P = M[M.year.between(y0, y1)]
    for (g, sx), s in P.groupby(["agegrp", "sex"]):
        if s.deaths.isna().any(): continue
        tot_rate = 1e5 * s.deaths.sum() / s.exposure_py.sum()
        bym = s.groupby("month", as_index=False).agg(deaths=("deaths", "sum"), exposure_py=("exposure_py", "sum")); bym["rate"] = 1e5 * bym.deaths / bym.exposure_py
        bym["index"] = bym.rate / tot_rate; bym["se_index"] = bym["index"] / np.sqrt(bym.deaths); bym["period"] = pname; bym["agegrp"] = g; bym["sex"] = sx; prof.append(bym)
        ds, es = s[s.summer == 1].deaths.sum(), s[s.summer == 1].exposure_py.sum(); dw, ew = s[s.summer == 0].deaths.sum(), s[s.summer == 0].exposure_py.sum()
        rr, lo, hi, se = lrr_ci(ds, es, dw, ew)
        dd, ed = s[s.month == 12].deaths.sum(), s[s.month == 12].exposure_py.sum(); dn, en = s[~s.month.isin([12, 6, 7, 8])].deaths.sum(), s[~s.month.isin([12, 6, 7, 8])].exposure_py.sum()
        rr_dec, lo_d, hi_d, _ = lrr_ci(dd, ed, dn, en)
        ratios.append(dict(period=pname, agegrp=g, sex=sx, deaths=s.deaths.sum(), rate=tot_rate, rate_summer=1e5 * ds / es, rate_school=1e5 * dw / ew, deaths_summer=ds, deaths_school=dw,
                           ratio_summer_school=rr, lo=lo, hi=hi, log_se=se, pct_lower_summer=100 * (1 - rr), ratio_dec_vs_other_school=rr_dec, dec_lo=lo_d, dec_hi=hi_d))
PROF = pd.concat(prof, ignore_index=True); mask_small(PROF).to_csv(T/"nvss_seasonal_profile.csv", index=False)
RAT = pd.DataFrame(ratios); mask_small(RAT).to_csv(T/"nvss_season_ratios.csv", index=False)
print("\nsummer (Jun-Aug) / school-month (Sep-May) rate ratio, 1999-2019 pooled:")
print(RAT[RAT.period == "1999-2019"].pivot(index="agegrp", columns="sex", values="ratio_summer_school").round(3).to_string())
print(RAT[(RAT.period == "1999-2019") & (RAT.agegrp.isin(MAIN))][["agegrp", "sex", "deaths", "rate", "rate_summer", "rate_school", "ratio_summer_school", "lo", "hi", "ratio_dec_vs_other_school"]].round(3).to_string(index=False))

# ---------- 4. decomposition of the rise: school months vs summer, pre vs post ----------
def season_cells(y0, y1, g, sx):
    s = M[(M.year.between(y0, y1)) & (M.agegrp == g) & (M.sex == sx)]
    out = {}
    for lab, mask in (("school", s.summer == 0), ("summer", s.summer == 1), ("all", s.summer.notna())):
        out[lab] = (s[mask].deaths.sum(), s[mask].exposure_py.sum())
    return out
dec = []
for pre, post in (("2008-2010", "2015-2019"), ("2005-2009", "2015-2019"), ("1999-2003", "2015-2019"), ("2008-2010", "2021-2024"), ("2015-2019", "2021-2024"), ("2008-2010", "2011-2014")):
    for g in GROUPS:
        for sx in ("F", "M", "A"):
            a, b = season_cells(*PERIODS[pre], g, sx), season_cells(*PERIODS[post], g, sx)
            if any(np.isnan(v[0]) for v in list(a.values()) + list(b.values())): continue
            r = dict(pre=pre, post=post, agegrp=g, sex=sx)
            for lab in ("school", "summer", "all"):
                (d0, e0), (d1, e1) = a[lab], b[lab]; rr, lo, hi, se = lrr_ci(d1, e1, d0, e0)
                r.update({f"rate_pre_{lab}": 1e5 * d0 / e0, f"rate_post_{lab}": 1e5 * d1 / e1, f"deaths_pre_{lab}": d0, f"deaths_post_{lab}": d1, f"ratio_{lab}": rr, f"ratio_{lab}_lo": lo, f"ratio_{lab}_hi": hi,
                          f"pct_change_{lab}": 100 * (rr - 1), f"abs_change_{lab}": 1e5 * (d1 / e1 - d0 / e0)})
            # interaction: ratio of post/pre ratios, school vs summer (>1 = rise concentrated in school months)
            se_int = np.sqrt(sum(1 / x for x in (a["school"][0], b["school"][0], a["summer"][0], b["summer"][0])))
            r["ratio_of_ratios_school_vs_summer"] = r["ratio_school"] / r["ratio_summer"]; r["ror_lo"] = r["ratio_of_ratios_school_vs_summer"] * np.exp(-1.96 * se_int); r["ror_hi"] = r["ratio_of_ratios_school_vs_summer"] * np.exp(1.96 * se_int); r["ror_log_se"] = se_int
            # share of the absolute increase in annual deaths-per-exposure that accrued in school months (person-time share of school months ~ 0.75)
            inc_school = (b["school"][0] / b["all"][1] - a["school"][0] / a["all"][1]); inc_all = (b["all"][0] / b["all"][1] - a["all"][0] / a["all"][1])
            r["share_increase_school_months"] = inc_school / inc_all if inc_all != 0 else np.nan; r["school_person_time_share"] = b["school"][1] / b["all"][1]
            dec.append(r)
DEC = pd.DataFrame(dec); mask_small(DEC).to_csv(T/"nvss_decomposition.csv", index=False)
print("\ndecomposition 2008-2010 -> 2015-2019: % change in rate, school months vs summer (and ratio of ratios):")
print(DEC[(DEC.pre == "2008-2010") & (DEC.post == "2015-2019")][["agegrp", "sex", "rate_pre_school", "rate_post_school", "pct_change_school", "rate_pre_summer", "rate_post_summer", "pct_change_summer", "ratio_of_ratios_school_vs_summer", "ror_lo", "ror_hi", "share_increase_school_months"]].round(3).to_string(index=False))
print("\ndecomposition 2015-2019 -> 2021-2024:")
print(DEC[(DEC.pre == "2015-2019") & (DEC.post == "2021-2024") & DEC.agegrp.isin(MAIN)][["agegrp", "sex", "pct_change_school", "pct_change_summer", "ratio_of_ratios_school_vs_summer", "ror_lo", "ror_hi"]].round(3).to_string(index=False))

# ---------- 5. Poisson / negative-binomial regressions on monthly counts ----------
def fit_models(df, formula, label, g, sx, terms):
    out = []
    df = df.dropna(subset=["deaths"]).copy(); df["lexp"] = np.log(df.exposure_py)
    pois = smf.glm(formula, data=df, family=sm.families.Poisson(), offset=df.lexp).fit(cov_type="HC1")
    # negative binomial with alpha estimated by ML (statsmodels NegativeBinomial discrete model), robust SE
    try:
        nb = smf.negativebinomial(formula, data=df, offset=df.lexp).fit(disp=0, maxiter=500, cov_type="HC1"); alpha = float(nb.params.get("alpha", np.nan))
    except Exception: nb, alpha = None, np.nan
    for t in terms:
        for mname, m in (("poisson", pois), ("negbin", nb)):
            if m is None or t not in m.params: continue
            out.append(dict(model=label, agegrp=g, sex=sx, estimator=mname, term=t, coef=m.params[t], se=m.bse[t], ratio=np.exp(m.params[t]), lo=np.exp(m.params[t] - 1.96 * m.bse[t]), hi=np.exp(m.params[t] + 1.96 * m.bse[t]), n_months=int(m.nobs), deaths=int(df.deaths.sum()), alpha=alpha if mname == "negbin" else np.nan, deviance=getattr(m, "deviance", np.nan) if mname == "poisson" else np.nan))
    return out
reg = []
for g in GROUPS:
    for sx in ("F", "M", "A"):
        base = M[(M.agegrp == g) & (M.sex == sx)]
        if base.deaths.isna().any(): continue
        # (a) seasonality 1999-2019: log rate on summer + December indicators (relative to other school months)
        d = base[base.year.between(1999, 2019)].copy(); d["dec"] = (d.month == 12).astype(int); d["yr"] = d.year - 2010
        reg += fit_models(d, "deaths ~ summer + dec + C(year)", "season_1999_2019", g, sx, ["summer", "dec"])
        # (b) decomposition: pre 2008-2010 vs post 2015-2019; month FE; post x summer interaction
        for pre, post, lab in (("2008-2010", "2015-2019", "rise_0810_1519"), ("2005-2009", "2015-2019", "rise_0509_1519"), ("2015-2019", "2021-2024", "post_1519_2124"), ("2008-2010", "2021-2024", "rise_0810_2124")):
            (a0, a1), (b0, b1) = PERIODS[pre], PERIODS[post]
            d = base[base.year.between(a0, a1) | base.year.between(b0, b1)].copy(); d["post"] = d.year.between(b0, b1).astype(int); d["post_summer"] = d.post * d.summer
            reg += fit_models(d, "deaths ~ C(month) + post + post_summer", lab, g, sx, ["post", "post_summer"])
        # (c) three-period model with year trend within period not needed; keep (b)
# (d) triple difference: 12-17 vs 18-24 (and 25-34), pre 2008-2010 vs post 2015-2019: post x summer x teen
for comp in ("18-24", "25-34"):
    for sx in ("F", "M", "A"):
        d = M[M.agegrp.isin(["12-17", comp]) & (M.sex == sx) & (M.year.between(2008, 2010) | M.year.between(2015, 2019))].copy()
        d["post"] = d.year.between(2015, 2019).astype(int); d["teen"] = (d.agegrp == "12-17").astype(int); d["post_summer"] = d.post * d.summer; d["teen_summer"] = d.teen * d.summer; d["teen_post"] = d.teen * d.post; d["teen_post_summer"] = d.teen * d.post * d.summer
        reg += fit_models(d, "deaths ~ C(month) * teen + post + post_summer + teen_post + teen_post_summer", f"ddd_1217_vs_{comp}_0810_1519", "12-17 vs " + comp, sx, ["post", "post_summer", "teen_post", "teen_post_summer", "teen_summer"])
REG = pd.DataFrame(reg); REG.to_csv(T/"nvss_poisson.csv", index=False)
print("\nPoisson (HC1) post x summer interaction, 2008-2010 -> 2015-2019 (ratio <1 = rise smaller in summer):")
print(REG[(REG.model == "rise_0810_1519") & (REG.term == "post_summer") & (REG.estimator == "poisson")][["agegrp", "sex", "coef", "se", "ratio", "lo", "hi", "n_months", "deaths"]].round(3).to_string(index=False))
print("\nseasonality 1999-2019, summer coefficient (Poisson, year FE):")
print(REG[(REG.model == "season_1999_2019") & (REG.term == "summer") & (REG.estimator == "poisson") & REG.agegrp.isin(MAIN)][["agegrp", "sex", "coef", "se", "ratio", "lo", "hi"]].round(3).to_string(index=False))
print("\ntriple difference teen x post x summer:")
print(REG[REG.model.str.startswith("ddd") & (REG.term == "teen_post_summer") & (REG.estimator == "poisson")][["agegrp", "sex", "coef", "se", "ratio", "lo", "hi"]].round(3).to_string(index=False))

# ---------- 6. 2020 school closures: observed vs expected ----------
cov = []
for g in GROUPS:
    for sx in ("F", "M", "A"):
        base = M[(M.agegrp == g) & (M.sex == sx)].dropna(subset=["deaths"])
        if len(base) == 0 or base[base.year.between(2015, 2019)].deaths.isna().any(): continue
        tr = base[base.year.between(2015, 2019)].copy(); tr["lexp"] = np.log(tr.exposure_py); tr["t"] = tr.year - 2017
        m = smf.glm("deaths ~ C(month) + t", data=tr, family=sm.families.Poisson(), offset=tr.lexp).fit()
        # variant 1: trend model (month FE + linear year trend through 2015-2019) extrapolated; variant 2: 2019 annual rate x 2015-2019 seasonal index
        idx = PROF[(PROF.period == "2015-2019") & (PROF.agegrp == g) & (PROF.sex == sx)].set_index("month")["index"]
        r19 = A[(A.agegrp == g) & (A.sex == sx) & (A.year == 2019)].rate.iloc[0]
        for y in (2020, 2021):
            s = base[base.year == y].copy(); s["lexp"] = np.log(s.exposure_py); s["t"] = s.year - 2017
            pr = m.get_prediction(s, offset=s.lexp); s["exp_trend"] = pr.predicted_mean; s["exp_trend_se"] = pr.se_mean
            s["exp_2019level"] = r19 * s.month.map(idx) * s.exposure_py / 1e5
            for win, months in (("Jan-Feb", [1, 2]), ("Mar-May", [3, 4, 5]), ("Jun-Aug", [6, 7, 8]), ("Sep-Dec", [9, 10, 11, 12]), ("Jan-May", [1, 2, 3, 4, 5]), ("full year", list(range(1, 13)))):
                w = s[s.month.isin(months)]
                if len(w) < len(months): continue
                o, e1, e2 = w.deaths.sum(), w.exp_trend.sum(), w.exp_2019level.sum(); se_log = np.sqrt(1 / o + (np.sqrt((w.exp_trend_se ** 2).sum()) / e1) ** 2)
                cov.append(dict(agegrp=g, sex=sx, year=y, window=win, observed=o, expected_trend=e1, expected_2019level=e2, ratio_trend=o / e1, ratio_lo=o / e1 * np.exp(-1.96 * se_log), ratio_hi=o / e1 * np.exp(1.96 * se_log), ratio_2019level=o / e2, pct_vs_trend=100 * (o / e1 - 1), pct_vs_2019level=100 * (o / e2 - 1), rate_observed=1e5 * o / w.exposure_py.sum(), rate_expected_trend=1e5 * e1 / w.exposure_py.sum()))
COV = pd.DataFrame(cov); mask_small(COV, ("observed",)).to_csv(T/"nvss_covid_2020.csv", index=False)
print("\n2020 observed vs expected (trend model from 2015-2019), main groups:")
print(COV[(COV.year == 2020) & COV.agegrp.isin(MAIN) & COV.window.isin(["Jan-Feb", "Mar-May", "Jun-Aug", "Sep-Dec"])].pivot_table(index=["agegrp", "sex"], columns="window", values="pct_vs_trend").round(1).to_string())
print("\n2021 Jan-May (reopening period) observed vs expected:")
print(COV[(COV.year == 2021) & COV.agegrp.isin(MAIN) & (COV.window == "Jan-May")][["agegrp", "sex", "observed", "expected_trend", "pct_vs_trend", "ratio_lo", "ratio_hi"]].round(2).to_string(index=False))

# ---------- 7. day of week: weekdays vs weekends, school months vs summer ----------
WD = {"Sunday": 7, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
def weekday_days(years, months):
    """number of calendar days falling on each ISO weekday (1=Mon..7=Sun) in the given years x months."""
    n = {k: 0 for k in range(1, 8)}
    for y in years:
        for mo in months:
            for dday in range(1, calendar.monthrange(y, mo)[1] + 1): n[dt_isoweekday(y, mo, dday)] += 1
    return n
import datetime as _dt
def dt_isoweekday(y, m, d): return _dt.date(y, m, d).isoweekday()
# weekday x sex tables pooled by WONDER over the period's school months (Sep-May) or summer months (Jun-Aug) through the year/month filter
wk = []
SEASON_MONTHS = {"school": [9, 10, 11, 12, 1, 2, 3, 4, 5], "summer": [6, 7, 8]}
for db, years in (("d76", range(1999, 2020)), ("d158", range(2021, 2025))):
    for g in MAIN:
        parts = []
        for lab in SEASON_MONTHS:
            f = pd.read_csv(COMP/f"{db}_weekday_sex_{g}_{lab}.csv"); f["wd"] = f.weekday.map(WD); f["deaths"] = num(f.deaths); f["sex"] = f.sex.str[0]; f["season"] = lab; parts.append(f.dropna(subset=["wd"])[["season", "wd", "sex", "deaths"]])
        f = pd.concat(parts); fa = f.groupby(["season", "wd"], as_index=False).deaths.sum().assign(sex="A"); f = pd.concat([f, fa])
        for sx in ("F", "M", "A"):
            s = f[f.sex == sx]
            if s.deaths.isna().any(): continue
            for lab in ("school", "summer", "all"):
                months = SEASON_MONTHS.get(lab, list(range(1, 13))); nd = weekday_days(years, months)
                ss = (s if lab == "all" else s[s.season == lab]).groupby("wd").deaths.sum()
                per_day = {k: ss.get(k, 0) / nd[k] for k in range(1, 8)}
                dw, dwe = sum(ss.get(k, 0) for k in range(1, 6)), sum(ss.get(k, 0) for k in (6, 7)); nw, nwe = sum(nd[k] for k in range(1, 6)), nd[6] + nd[7]
                rr, lo, hi, se = lrr_ci(dw, nw, dwe, nwe)
                wk.append(dict(period=f"{min(years)}-{max(years)}", agegrp=g, sex=sx, season=lab, deaths=int(ss.sum()), per_day_mon=per_day[1], per_day_tue=per_day[2], per_day_wed=per_day[3], per_day_thu=per_day[4], per_day_fri=per_day[5], per_day_sat=per_day[6], per_day_sun=per_day[7],
                               weekday_weekend_ratio=rr, lo=lo, hi=hi, log_se=se))
WK = pd.DataFrame(wk)
# interaction: weekday/weekend ratio in school months relative to summer
inter = []
for (p, g, sx), s in WK.groupby(["period", "agegrp", "sex"]):
    sc, su = s[s.season == "school"].iloc[0], s[s.season == "summer"].iloc[0]; ror = sc.weekday_weekend_ratio / su.weekday_weekend_ratio; se = np.sqrt(sc.log_se ** 2 + su.log_se ** 2)
    inter.append(dict(period=p, agegrp=g, sex=sx, season="school_vs_summer_ratio_of_ratios", deaths=int(sc.deaths + su.deaths), weekday_weekend_ratio=ror, lo=ror * np.exp(-1.96 * se), hi=ror * np.exp(1.96 * se), log_se=se))
WK = pd.concat([WK, pd.DataFrame(inter)], ignore_index=True); mask_small(WK).to_csv(T/"nvss_weekday.csv", index=False)
print("\nweekday (Mon-Fri) / weekend (Sat-Sun) per-day death ratio, by season:")
print(WK[WK.season.isin(["school", "summer", "school_vs_summer_ratio_of_ratios"])].pivot_table(index=["period", "agegrp", "sex"], columns="season", values="weekday_weekend_ratio").round(3).to_string())
print("\nper-day deaths by weekday, 12-17 both sexes 1999-2019, school months vs summer:")
print(WK[(WK.period == "1999-2019") & (WK.agegrp == "12-17") & (WK.sex == "A") & WK.season.isin(["school", "summer"])].set_index("season")[[c for c in WK.columns if c.startswith("per_day_")]].round(2).to_string())
print("\nwrote:", ", ".join(sorted(p.name for p in T.glob("nvss_*.csv"))))
