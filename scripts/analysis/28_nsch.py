"""NSCH 2016-2025 (parent reports, children 6-17): the U.S. caregiver screen-time gradient in current anxiety/depression, national and state
trends, state smartphone adoption (NTIA) and the first statewide school phone bans (Florida 2023-24; IN/LA/SC 2024-25; the 2025-26 wave).
Input : data/extracts/nsch/nsch_6_17.parquet (scripts/download/nsch/extract_nsch.py), data/compiled/ntia/ntia_state_year.csv,
        data/compiled/phone_bans/state_phone_bans.csv
Output: results/tables/nsch_sample.csv, nsch_screen_prevalence.csv, nsch_screen_gradient.csv, nsch_trends_state_year.csv, nsch_adoption.csv,
        nsch_ban_did.csv, nsch_florida_series.csv, nsch_mediators.csv, nsch_literature.csv
Run:    uv run python scripts/analysis/28_nsch.py
Design notes: one sampled child per household and no clusters below the state stratum, so individual-level models use heteroskedasticity-robust
SEs (HC1) with survey weights FWC; state-year panels and the ban/adoption models cluster by state (CRV1). Screen time is comparable only from
2018 (single SCREENTIME item); 2016-17 (two items summed) is reported separately.
"""
import pandas as pd, numpy as np, pyfixest as pf, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; pd.set_option("display.width", 230)
d = pd.read_parquet(ROOT/"data/extracts/nsch/nsch_6_17.parquet")
d = d[d.wt.notna() & (d.wt > 0)].copy()
d["fpl_cat"] = d.fpl_cat.replace("nan", np.nan); d["sex"] = np.where(d.girl == 1, "girls", "boys")
for c in ["anx_cur", "dep_cur", "adhd_cur", "beh_cur", "anx_modsev", "dep_modsev", "anx_ever", "dep_ever", "screen_4plus", "screen_3plus", "sleep_lt8", "bullied_monthly", "bullied_weekly", "bullied_any", "engaged", "physact_daily", "mh_treat_12m"]:
    d[c + "100"] = 100 * d[c]
for k, c in {"scr_lt1": 1, "scr_2": 3, "scr_3": 4, "scr_4p": 5}.items():   # reference category: 1 hour (code 2)
    d[k] = (d.screentime == c).astype(float).where(d.screentime.notna())
COVS = "C(age) + girl + C(raceeth) + C(fpl_cat) + C(pared)"
FIPS = {"Alabama":1,"Alaska":2,"Arizona":4,"Arkansas":5,"California":6,"Colorado":8,"Connecticut":9,"Delaware":10,"District of Columbia":11,"Florida":12,"Georgia":13,"Hawaii":15,"Idaho":16,"Illinois":17,"Indiana":18,"Iowa":19,"Kansas":20,"Kentucky":21,"Louisiana":22,"Maine":23,"Maryland":24,"Massachusetts":25,"Michigan":26,"Minnesota":27,"Mississippi":28,"Missouri":29,"Montana":30,"Nebraska":31,"Nevada":32,"New Hampshire":33,"New Jersey":34,"New Mexico":35,"New York":36,"North Carolina":37,"North Dakota":38,"Ohio":39,"Oklahoma":40,"Oregon":41,"Pennsylvania":42,"Rhode Island":44,"South Carolina":45,"South Dakota":46,"Tennessee":47,"Texas":48,"Utah":49,"Vermont":50,"Virginia":51,"Washington":53,"West Virginia":54,"Wisconsin":55,"Wyoming":56}
NAME = {v: k for k, v in FIPS.items()}

def wmean(x, w):
    m = x.notna() & w.notna(); return np.average(x[m], weights=w[m]) if w[m].sum() > 0 else np.nan
def wse(x, w):  # approximate design-free SE of a weighted mean (one child per household; stratification ignored)
    m = x.notna() & w.notna(); x, w = x[m], w[m]
    if len(x) < 2: return np.nan
    p = np.average(x, weights=w); return np.sqrt(np.sum((w * (x - p)) ** 2)) / w.sum()
def fe(fml, dd, w="wt", vc="hetero"):
    return pf.feols(fml, data=dd, weights=w, vcov=vc if vc in ("hetero", "iid", "HC1", "HC2", "HC3") else {"CRV1": vc})
def grab(m, term, scale=1.0):
    return dict(coef=scale * m.coef()[term], se=scale * m.se()[term], n=int(m._N))
SEXES = [("all", None), ("girls", 1), ("boys", 0)]; AGES = [("12-17", "12-17"), ("6-11", "6-11"), ("6-17", None)]
def sub(dd, sx, ag):
    if sx is not None: dd = dd[dd.girl == sx]
    if ag is not None: dd = dd[dd.agegrp == ag]
    return dd

# ---------------------------------------------------------------- 0. sample and coverage
rows = []
for (y, ag), g in d.groupby(["year", "agegrp"]):
    rows.append(dict(year=y, agegrp=ag, n=len(g), n_girls=int((g.girl == 1).sum()), wsum=g.wt.sum(),
                     **{c: 100 * wmean(g[c], g.wt) for c in ["anx_cur", "dep_cur", "adhd_cur", "anx_modsev", "dep_modsev", "screen_4plus", "sleep_lt8", "bullied_monthly", "mh_treat_12m"]},
                     screen_hrs_1617=wmean(g.screen_hrs_1617, g.wt), screen_hrs=wmean(g.screen_hrs, g.wt)))
S = pd.DataFrame(rows); S.to_csv(T/"nsch_sample.csv", index=False)
print("NSCH 6-17 sample by year:\n", S[["year", "agegrp", "n", "anx_cur", "dep_cur", "screen_4plus"]].round(1).to_string(index=False))

# ---------------------------------------------------------------- 1. screen-time gradient (2018-2025, SCREENTIME item)
d18 = d[d.year >= 2018]
OUTS = {"anx_cur": "Current anxiety", "dep_cur": "Current depression", "adhd_cur": "Current ADD/ADHD (contrast)", "anx_modsev": "Current anxiety, moderate/severe", "dep_modsev": "Current depression, moderate/severe", "beh_cur": "Current behavior/conduct problems"}
prev = []
for sl, sx in SEXES:
    for al, ag in AGES:
        g = sub(d18, sx, ag)
        for cat, gg in g.groupby("screen_cat"):
            prev.append(dict(sex=sl, agegrp=al, screen_cat=cat, n=len(gg), share_of_group=100 * gg.wt.sum() / g[g.screen_cat.notna()].wt.sum(),
                             **{o: 100 * wmean(gg[o], gg.wt) for o in OUTS}, **{o + "_se": 100 * wse(gg[o], gg.wt) for o in ["anx_cur", "dep_cur", "adhd_cur"]}))
P = pd.DataFrame(prev); P.to_csv(T/"nsch_screen_prevalence.csv", index=False)
PERIODS = {"2018-2025": (2018, 2025), "2018-2019": (2018, 2019), "2022-2025": (2022, 2025)}
TERMS = {"scr_lt1": "<1 h vs 1 h", "scr_2": "2 h vs 1 h", "scr_3": "3 h vs 1 h", "scr_4p": "4+ h vs 1 h"}
grad = []
for per, (y0, y1) in PERIODS.items():
    for sl, sx in SEXES:
        for al, ag in AGES:
            if per != "2018-2025" and (al == "6-17" or sl == "all"): continue
            g = sub(d[(d.year >= y0) & (d.year <= y1)], sx, ag).dropna(subset=["screentime", "raceeth", "fpl_cat", "pared"])
            for o, ol in OUTS.items():
                gg = g.dropna(subset=[o])
                if len(gg) < 2000: continue
                m = fe(f"{o}100 ~ scr_lt1 + scr_2 + scr_3 + scr_4p + {COVS} | state^year", gg)
                mean = 100 * wmean(gg[o], gg.wt)
                for t, tl in TERMS.items(): grad.append(dict(period=per, outcome=o, outcome_label=ol, sex=sl, agegrp=al, term=t, term_label=tl, spec="covariates + state x year FE", mean=mean, **grab(m, t)))
                m2 = fe(f"{o}100 ~ screen_hrs + {COVS} | state^year", gg); grad.append(dict(period=per, outcome=o, outcome_label=ol, sex=sl, agegrp=al, term="per_hour", term_label="per weekday hour (linear)", spec="covariates + state x year FE", mean=mean, **grab(m2, "screen_hrs")))
                m3 = fe(f"{o}100 ~ scr_4p + scr_lt1 + scr_2 + scr_3 | year", gg); grad.append(dict(period=per, outcome=o, outcome_label=ol, sex=sl, agegrp=al, term="scr_4p_raw", term_label="4+ h vs 1 h, year FE only", spec="year FE only", mean=mean, **grab(m3, "scr_4p")))
# 2016-17: two items summed (TV + devices), hours 0-9; linear slope and 4+ summed hours vs <4
for sl, sx in SEXES:
    for al, ag in AGES:
        g = sub(d[d.year <= 2017], sx, ag).dropna(subset=["screen_hrs_1617", "raceeth", "fpl_cat", "pared"]).copy(); g["sum4p"] = (g.screen_hrs_1617 >= 4).astype(float)
        for o in ["anx_cur", "dep_cur", "adhd_cur"]:
            gg = g.dropna(subset=[o])
            if len(gg) < 2000: continue
            mean = 100 * wmean(gg[o], gg.wt)
            m = fe(f"{o}100 ~ screen_hrs_1617 + {COVS} | state^year", gg); grad.append(dict(period="2016-2017", outcome=o, outcome_label=OUTS[o], sex=sl, agegrp=al, term="per_hour", term_label="per weekday hour, TV + device items summed", spec="covariates + state x year FE", mean=mean, **grab(m, "screen_hrs_1617")))
            m = fe(f"{o}100 ~ sum4p + {COVS} | state^year", gg); grad.append(dict(period="2016-2017", outcome=o, outcome_label=OUTS[o], sex=sl, agegrp=al, term="sum4p", term_label="4+ summed hours vs <4", spec="covariates + state x year FE", mean=mean, **grab(m, "sum4p")))
G = pd.DataFrame(grad); G.to_csv(T/"nsch_screen_gradient.csv", index=False)
print("\nGradient 2018-2025, 4+ h vs 1 h (pp, SE), covariates + state x year FE:")
print(G[(G.period == "2018-2025") & (G.term == "scr_4p")].pivot_table(index=["outcome"], columns=["agegrp", "sex"], values="coef", sort=False).round(2).to_string())

# ---------------------------------------------------------------- 2. trends: national and state by year, sex, age group
TR = ["anx_cur", "dep_cur", "adhd_cur", "anx_modsev", "dep_modsev", "anx_ever", "dep_ever", "screen_4plus", "sleep_lt8", "bullied_monthly", "mh_treat_12m"]
tr = []
def cell(g, **k):
    r = dict(n=len(g), wsum=g.wt.sum(), **k)
    for o in TR: r[o] = 100 * wmean(g[o], g.wt); r[o + "_se"] = 100 * wse(g[o], g.wt); r[o + "_n"] = int(g[o].notna().sum())
    return r
for (y, ag), g in d.groupby(["year", "agegrp"]):
    tr.append(cell(g, year=y, state=0, state_name="United States", sex="all", agegrp=ag))
    for sl in ["girls", "boys"]: tr.append(cell(g[g.sex == sl], year=y, state=0, state_name="United States", sex=sl, agegrp=ag))
for (y, st, ag), g in d.groupby(["year", "state", "agegrp"]):
    tr.append(cell(g, year=y, state=st, state_name=NAME.get(st, str(st)), sex="all", agegrp=ag))
    for sl in ["girls", "boys"]: tr.append(cell(g[g.sex == sl], year=y, state=st, state_name=NAME.get(st, str(st)), sex=sl, agegrp=ag))
TRD = pd.DataFrame(tr); TRD.to_csv(T/"nsch_trends_state_year.csv", index=False)
nat = TRD[(TRD.state == 0) & (TRD.agegrp == "12-17")].pivot_table(index="year", columns="sex", values=["anx_cur", "dep_cur"]).round(1)
print("\nNational 12-17 current anxiety / depression (%), by sex:\n", nat.to_string())

# ---------------------------------------------------------------- 3. state smartphone adoption (NTIA, teen households) vs state-year rates
N = pd.read_csv(ROOT/"data/compiled/ntia/ntia_state_year.csv")
N = N[(N.group == "hh_teen12_17") & (N.indicator == "person_uses_smartphone_internet") & (N.year >= 2017)][["state", "year", "share"]].rename(columns={"share": "smart"})
rows = []
for st, g in N.groupby("state"):
    g = g.set_index("year").reindex(range(2016, 2026)); g["smart"] = g.smart.interpolate(limit_direction="both"); g["state"] = st; rows.append(g.reset_index())
NI = pd.concat(rows); NI["smart10"] = 100 * NI.smart / 10; NI["observed_window"] = NI.year.between(2017, 2023)
panel = TRD[TRD.state > 0].merge(NI, on=["state", "year"], how="inner")
ad = []
for spec, yrs in {"2017-2023 (within NTIA waves)": (2017, 2023), "2016-2025 (flat extrapolation outside waves)": (2016, 2025)}.items():
    for al in ["12-17", "6-11"]:
        for sl in ["girls", "boys", "all"]:
            for o in ["anx_cur", "dep_cur", "adhd_cur"]:
                p = panel[(panel.agegrp == al) & (panel.sex == sl) & panel.year.between(*yrs) & panel[o].notna()].copy(); p["y"] = p[o]
                m = fe("y ~ smart10 | state + year", p, w="n", vc="state")
                ad.append(dict(spec=spec, outcome=o, sex=sl, agegrp=al, coef_per10pp=m.coef()["smart10"], se=m.se()["smart10"], n_state_years=int(m._N), states=p.state.nunique(), mean_outcome=np.average(p.y, weights=p.n), smart_mean=100 * np.average(p.smart, weights=p.n)))
AD = pd.DataFrame(ad)
sd = NI[NI.year.isin([2017, 2019, 2021, 2023])].groupby("year").smart.agg(["mean", "std", "min", "max"]).mul(100).round(1).reset_index().rename(columns={"mean": "smart_mean", "std": "smart_sd", "min": "smart_min", "max": "smart_max"})
AD = pd.concat([AD, sd.assign(spec="NTIA cross-state distribution (wave year)")], ignore_index=True); AD.to_csv(T/"nsch_adoption.csv", index=False)
print("\nAdoption: pp of outcome per +10 pp teen-household smartphone-internet share, state + year FE, cluster state:")
print(AD[AD.outcome.notna()].pivot_table(index=["spec", "outcome"], columns=["agegrp", "sex"], values="coef_per10pp", sort=False).round(2).to_string())
print(sd.to_string(index=False))

# ---------------------------------------------------------------- 4. statewide school phone bans: DiD / event study
B = pd.read_csv(ROOT/"data/compiled/phone_bans/state_phone_bans.csv"); B["state"] = B.state.map(FIPS)
B["start"] = B.effective_school_year.str.slice(0, 4).astype(float)
MAND = ["statewide bell-to-bell ban", "ban during instructional time"]
B["mandate_start"] = B.start.where(B.policy_type.isin(MAND)); B["polreq_start"] = B.start.where(B.policy_type == "requires districts to adopt a policy")
bans = B[["state", "policy_type", "mandate_start", "polreq_start", "law_or_rule_citation"]]
def code(df):
    df = df.merge(bans, on="state", how="left")
    df["post_full"] = (df.year >= df.mandate_start + 1).astype(float).fillna(0)       # mandate in force for the whole school year before/during the interview
    df["post_partial"] = (df.year == df.mandate_start).astype(float).fillna(0)       # interview year in which the mandate took effect (June-Jan field period straddles the start)
    df["polreq_post"] = (df.year >= df.polreq_start).astype(float).fillna(0)
    df["k"] = df.year - df.mandate_start
    for kk in [-3, -2, 0, 1, 2]: df[f"ev_{'m' if kk < 0 else 'p'}{abs(kk)}"] = (df.k == kk).astype(float).fillna(0)
    df["ev_m4plus"] = (df.k <= -4).astype(float).fillna(0)
    return df
sp = code(TRD[TRD.state > 0].copy()); di = code(d.copy())
treated = bans[bans.mandate_start.notna()].sort_values("mandate_start")
print("\nMandate states and first school year:", ", ".join(f"{NAME[s]} {int(y)}-{int(y)+1-2000:02d}" for s, y in zip(treated.state, treated.mandate_start)))
EV = ["ev_m4plus", "ev_m3", "ev_m2", "ev_p0", "ev_p1", "ev_p2"]
did = []
def add(design, sample, al, sl, o, m, terms, nst, extra=""):
    for t in terms: did.append(dict(design=design, sample=sample, agegrp=al, sex=sl, outcome=o, term=t, treated_states=nst, note=extra, **grab(m, t)))
for al in ["12-17", "6-11"]:
    for sl in ["girls", "boys", "all"]:
        for o in ["anx_cur", "dep_cur", "adhd_cur", "anx_modsev", "dep_modsev"]:
            p = sp[(sp.agegrp == al) & (sp.sex == sl) & sp[o].notna()].copy(); p["y"] = p[o]
            nst = p[p.post_full + p.post_partial > 0].state.nunique()
            m = fe("y ~ post_full + post_partial + polreq_post | state + year", p, w="n", vc="state"); add("state-year panel DiD", "all mandate states", al, sl, o, m, ["post_full", "post_partial", "polreq_post"], nst, "weights = cell n")
            m = fe("y ~ " + " + ".join(EV) + " + polreq_post | state + year", p, w="n", vc="state"); add("state-year event study", "all mandate states", al, sl, o, m, EV, nst, "ref k = -1; weights = cell n")
            m = fe("y ~ post_full + post_partial + polreq_post | state + year", p, w="wsum", vc="state"); add("state-year panel DiD, population-weighted", "all mandate states", al, sl, o, m, ["post_full", "post_partial", "polreq_post"], nst, "weights = cell sum of FWC")
            # Florida alone (the only state with two full post years): drop other mandate states once treated
            pf_ = p[~((p.state != 12) & (p.post_full + p.post_partial > 0))].copy()
            m = fe("y ~ post_full + post_partial + polreq_post | state + year", pf_, w="n", vc="state"); add("state-year panel DiD", "Florida only (other mandate states dropped once treated)", al, sl, o, m, ["post_full", "post_partial"], 1, "weights = cell n")
            if o in ["anx_cur", "dep_cur", "adhd_cur"]:
                g = sub(di, {"girls": 1, "boys": 0, "all": None}[sl], al).dropna(subset=[o, "raceeth", "fpl_cat", "pared"]).copy(); g["y"] = 100 * g[o]
                m = fe(f"y ~ post_full + post_partial + polreq_post + {COVS} | state + year", g, vc="state"); add("individual DiD", "all mandate states", al, sl, o, m, ["post_full", "post_partial", "polreq_post"], nst, "survey weights FWC, covariates, cluster state")
                m = fe("y ~ " + " + ".join(EV) + f" + polreq_post + {COVS} | state + year", g, vc="state"); add("individual event study", "all mandate states", al, sl, o, m, EV, nst, "ref k = -1; survey weights FWC, covariates, cluster state")
DID = pd.DataFrame(did); DID.to_csv(T/"nsch_ban_did.csv", index=False)
# permutation inference: reassign the observed mandate schedule (one state from 2023-24, three from 2024-25, the rest from 2025-26) to
# random states and re-estimate the state-year DiD; reports the permutation SD and the two-sided share of placebo |coef| >= observed
rng = np.random.default_rng(28); sched = treated.mandate_start.values; perm = []
for al, sl in [("12-17", "girls"), ("12-17", "boys"), ("12-17", "all"), ("6-11", "all")]:
    for o in ["anx_cur", "dep_cur", "adhd_cur"]:
        p = sp[(sp.agegrp == al) & (sp.sex == sl) & sp[o].notna()].copy(); p["y"] = p[o]; states = np.array(sorted(p.state.unique()))
        for wname, wcol in [("cell n", "n"), ("population (sum of FWC)", "wsum")]:
            obs = fe("y ~ post_full + post_partial + polreq_post | state + year", p, w=wcol, vc="state"); draws = []
            for r in range(400):
                st = dict(zip(rng.choice(states, size=len(sched), replace=False), sched)); ms = p.state.map(st)
                q = p.assign(pf=(p.year >= ms + 1).astype(float).fillna(0), pp=(p.year == ms).astype(float).fillna(0))
                m = pf.feols("y ~ pf + pp | state + year", data=q, weights=wcol, vcov="iid"); draws.append((m.coef()["pf"], m.coef()["pp"]))
            dr = np.array(draws); bf, bp = obs.coef()["post_full"], obs.coef()["post_partial"]
            perm.append(dict(agegrp=al, sex=sl, outcome=o, weights=wname, coef_full=bf, se_cluster_full=obs.se()["post_full"], perm_sd_full=dr[:, 0].std(), perm_p_full=float((np.abs(dr[:, 0]) >= abs(bf)).mean()),
                             coef_partial=bp, se_cluster_partial=obs.se()["post_partial"], perm_sd_partial=dr[:, 1].std(), perm_p_partial=float((np.abs(dr[:, 1]) >= abs(bp)).mean()), n_perm=len(dr), n_cells=int(obs._N)))
PERM = pd.DataFrame(perm); PERM.to_csv(T/"nsch_ban_permutation.csv", index=False)
# single-state placebo for the Florida-only design: each eligible other state in turn is treated as the sole mandate state from 2023-24
# (Florida removed, other real mandate states dropped once treated, as in the Florida-only specification); exact placebo distribution
flp = []
for al, sl in [("12-17", "girls"), ("12-17", "boys"), ("12-17", "all"), ("6-11", "all")]:
    for o in ["anx_cur", "dep_cur", "adhd_cur"]:
        p = sp[(sp.agegrp == al) & (sp.sex == sl) & sp[o].notna()].copy(); p["y"] = p[o]
        base = p[~((p.state != 12) & (p.post_full + p.post_partial > 0))]
        obs = fe("y ~ post_full + post_partial + polreq_post | state + year", base, w="n", vc="state"); draws = []
        for st in sorted(base.state.unique()):
            if st in treated.state.values: continue
            q = base[base.state != 12].assign(pf=lambda x: ((x.state == st) & (x.year >= 2024)).astype(float), pp=lambda x: ((x.state == st) & (x.year == 2023)).astype(float))
            m = pf.feols("y ~ pf + pp + polreq_post | state + year", data=q, weights="n", vcov="iid"); draws.append((m.coef()["pf"], m.coef()["pp"]))
        dr = np.array(draws); bf, bp = obs.coef()["post_full"], obs.coef()["post_partial"]
        flp.append(dict(agegrp=al, sex=sl, outcome=o, coef_full=bf, coef_partial=bp, placebo_sd_full=dr[:, 0].std(), placebo_p_full=float((np.abs(dr[:, 0]) >= abs(bf)).mean()), placebo_sd_partial=dr[:, 1].std(),
                        placebo_p_partial=float((np.abs(dr[:, 1]) >= abs(bp)).mean()), n_placebo_states=len(dr), states_below_full=int((dr[:, 0] < bf).sum())))
FLP = pd.DataFrame(flp); FLP.to_csv(T/"nsch_ban_florida_placebo.csv", index=False)
print("\nFlorida-only design, single-state placebo distribution:\n", FLP.round(2).to_string(index=False))
print("\nPermutation inference (state-year DiD):\n", PERM[["agegrp", "sex", "outcome", "weights", "coef_full", "se_cluster_full", "perm_sd_full", "perm_p_full", "coef_partial", "perm_sd_partial", "perm_p_partial"]].round(2).to_string(index=False))
print("\nBan DiD (pp), 12-17, state-year panel and individual, cluster state:")
print(DID[(DID.agegrp == "12-17") & DID.design.isin(["state-year panel DiD", "individual DiD"]) & (DID["sample"] == "all mandate states") & DID.term.isin(["post_full", "post_partial"])].pivot_table(index=["design", "outcome", "term"], columns="sex", values=["coef", "se"], sort=False).round(2).to_string())
print(DID[(DID.agegrp == "12-17") & (DID.design == "individual event study") & (DID.outcome == "anx_cur")].pivot_table(index="term", columns="sex", values=["coef", "se"], sort=False).round(2).reindex(EV).to_string())
# Florida vs other states, raw series
fl = []
for (y, ag, sl), g in d.groupby(["year", "agegrp", "sex"]):
    for grp, gg in [("Florida", g[g.state == 12]), ("Other states", g[g.state != 12]), ("No statewide mandate by 2025-26", g[~g.state.isin(treated.state)])]:
        fl.append(dict(year=y, agegrp=ag, sex=sl, group=grp, n=len(gg), **{o: 100 * wmean(gg[o], gg.wt) for o in ["anx_cur", "dep_cur", "adhd_cur", "screen_4plus"]}, **{o + "_se": 100 * wse(gg[o], gg.wt) for o in ["anx_cur", "dep_cur", "adhd_cur"]}))
FL = pd.DataFrame(fl)
for (y, ag), g in d.groupby(["year", "agegrp"]):
    for grp, gg in [("Florida", g[g.state == 12]), ("Other states", g[g.state != 12]), ("No statewide mandate by 2025-26", g[~g.state.isin(treated.state)])]:
        FL.loc[len(FL)] = dict(year=y, agegrp=ag, sex="all", group=grp, n=len(gg), **{o: 100 * wmean(gg[o], gg.wt) for o in ["anx_cur", "dep_cur", "adhd_cur", "screen_4plus"]}, **{o + "_se": 100 * wse(gg[o], gg.wt) for o in ["anx_cur", "dep_cur", "adhd_cur"]})
FL.to_csv(T/"nsch_florida_series.csv", index=False)
print("\nFlorida vs other states, 12-17 current anxiety (%):\n", FL[(FL.agegrp == "12-17") & (FL.group != "No statewide mandate by 2025-26")].pivot_table(index="year", columns=["sex", "group"], values="anx_cur").round(1).to_string())

# ---------------------------------------------------------------- 5. mediators: screen time -> sleep, bullying; gradient with and without them
med = []
for al in ["12-17", "6-11"]:
    for sl, sx in SEXES:
        g = sub(d18, sx, al).dropna(subset=["screentime", "raceeth", "fpl_cat", "pared"])
        for o, ol in {"sleep_lt8": "Sleeps < 8 h on weeknights", "bullied_monthly": "Bullied monthly or more (past 12 m)", "bullied_weekly": "Bullied weekly or more", "engaged": "Engaged in school (cares + does homework, always/usually)", "physact_daily": "Physically active 60 min every day"}.items():
            gg = g.dropna(subset=[o])
            if len(gg) < 2000: continue
            m = fe(f"{o}100 ~ scr_lt1 + scr_2 + scr_3 + scr_4p + {COVS} | state^year", gg)
            for t in TERMS: med.append(dict(block="screen -> mediator", outcome=o, outcome_label=ol, sex=sl, agegrp=al, term=t, term_label=TERMS[t], spec="covariates + state x year FE", mean=100 * wmean(gg[o], gg.wt), **grab(m, t)))
        gg = g.dropna(subset=["anx_cur", "dep_cur", "sleep_lt8", "bullied_monthly", "bullied_weekly"])
        for o in ["anx_cur", "dep_cur", "adhd_cur"]:
            g2 = gg.dropna(subset=[o])
            for spec, extra in [("base", ""), ("+ sleep < 8 h", " + sleep_lt8"), ("+ bullying", " + bullied_monthly + bullied_weekly"), ("+ sleep and bullying", " + sleep_lt8 + bullied_monthly + bullied_weekly")]:
                m = fe(f"{o}100 ~ scr_lt1 + scr_2 + scr_3 + scr_4p{extra} + {COVS} | state^year", g2)
                med.append(dict(block="gradient with mediators", outcome=o, outcome_label=OUTS[o], sex=sl, agegrp=al, term="scr_4p", term_label=TERMS["scr_4p"], spec=spec, mean=100 * wmean(g2[o], g2.wt), **grab(m, "scr_4p")))
                m2 = fe(f"{o}100 ~ screen_hrs{extra} + {COVS} | state^year", g2)
                med.append(dict(block="gradient with mediators", outcome=o, outcome_label=OUTS[o], sex=sl, agegrp=al, term="per_hour", term_label="per weekday hour (linear)", spec=spec, mean=100 * wmean(g2[o], g2.wt), **grab(m2, "screen_hrs")))
                if spec == "+ sleep and bullying":
                    for t, tl in [("sleep_lt8", "Sleeps < 8 h (direct)"), ("bullied_monthly", "Bullied monthly+ (direct)"), ("bullied_weekly", "Bullied weekly+ (additional)")]:
                        med.append(dict(block="mediator -> outcome", outcome=o, outcome_label=OUTS[o], sex=sl, agegrp=al, term=t, term_label=tl, spec=spec, mean=100 * wmean(g2[o], g2.wt), **grab(m, t)))
M = pd.DataFrame(med); M.to_csv(T/"nsch_mediators.csv", index=False)
print("\nMediators, 12-17: 4+ h vs 1 h coefficient on anxiety by spec:\n", M[(M.block == "gradient with mediators") & (M.agegrp == "12-17") & (M.term == "scr_4p")].pivot_table(index=["outcome", "spec"], columns="sex", values="coef", sort=False).round(2).to_string())

# ---------------------------------------------------------------- 6. literature (hand-entered; verified against abstract/full text unless flagged)
LIT = [
 dict(study="Twenge & Campbell (2018)", data="NSCH 2016, ages 2-17, n = 40,337 (unweighted)", design="Cross-sectional; TV + device items summed (0 to 7+ h/day)", finding="Adolescents 14-17 at 7+ h/day vs 1 h/day: anxiety diagnosis RR 2.26 (95% CI 1.59-3.22), depression RR 2.39 (1.54-3.70); inflection after about 1 h/day; stronger for adolescents than younger children", url="https://doi.org/10.1016/j.pmedr.2018.10.003", verified="yes (PMC full text)"),
 dict(study="Leung & Torres (2021)", data="NSCH 2018, ages 13-17, n = 10,907", design="Cross-sectional logistic models; sleep as mediator", finding="4+ h vs <1 h weekday screen time: depression OR 2.23 (1.27-3.91), anxiety OR 1.85 (1.26-2.72) fully adjusted; no association at 1-3 h; sleep duration did not mediate", url="https://doi.org/10.1016/j.sleep.2021.02.031", verified="yes (PMC full text; some table entries internally inconsistent)"),
 dict(study="Lebrun-Harris, Ghandour, Kogan & Warren (2022)", data="NSCH 2016-2020, ages 0-17, n = 174,551", design="Weighted trends", finding="Anxiety 7.1% to 9.2% (+29%), depression 3.1% to 4.0% (+27%), 2016 to 2020; mental-health care use flat", url="https://doi.org/10.1001/jamapediatrics.2022.0056", verified="yes (abstract)"),
 dict(study="Wu, Li & Tsurumi (2024)", data="NSCH 2018-2021, ages 6-17, n = 88,823", design="Pooled cross-sections; composite well-being index", finding="Share with 4+ h weekday screen time 22.7% (2018) to 32.8% (2020) and 29.4% (2021); each screen hour associated with +0.32 points on a 0-6 problem index; 2016-17 excluded because TV and device hours were asked separately", url="https://doi.org/10.1186/s13034-023-00688-7", verified="yes (PMC full text)"),
 dict(study="HRSA MCHB data brief, Adolescent mental and behavioral health (2024)", data="NSCH 2016-2023, ages 12-17", design="Weighted trends", finding="Diagnosed anxiety 10.0% (2016) to 16.1% (2023), depression 5.8% to 8.4%; 61% of adolescents with a current condition who needed treatment had difficulty obtaining it in 2023", url="https://mchb.hrsa.gov/sites/default/files/mchb/data-research/nsch-data-brief-adolescent-mental-behavioral-health-2023.pdf", verified="no: PDF returns Akamai 'Access Denied' (HTTP 403) from this host; figures from search-engine summary"),
 dict(study="Forrest, Koenigsberg, Harvey, Maltenfort & Halfon (2025)", data="NSCH and four other national surveys, mortality files, PEDSnet, 2007-2023", design="Descriptive trends in 172 indicators", finding="Chronic-condition prevalence among 3-17-year-olds rose from 25.8% to 31.0% in the general population; anxiety and depression among the fastest-rising diagnoses", url="https://doi.org/10.1001/jama.2025.9855", verified="partial: citation and headline from press coverage; NSCH-specific anxiety/depression figures not verified"),
]
pd.DataFrame(LIT).to_csv(T/"nsch_literature.csv", index=False)
print("\nwrote", ", ".join(p.name for p in sorted(T.glob("nsch_*.csv"))))
