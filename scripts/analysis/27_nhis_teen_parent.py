"""NHIS 2021-2024: parent-reported Washington Group anxiety/depression items for 12-17-year-olds (Sample Child public-use files) set beside the
teen-reported NHIS-Teen GAD-2 / PHQ-2 estimates NCHS publishes for the same population and period. NHIS-Teen microdata are RDC-only (no public-use
file), so the comparison is (a) population-level: parent vs teen prevalence by the same subgroups in the same months, and (b) across informants'
own-report gradients: parent-reported 2+ h weekday screen time (2022, 2024) and parent-reported bullying (2021-2022) vs parent-reported symptoms,
against the published teen-reported 4+ h screen-time and bullying gradients in GAD-2/PHQ-2 (NCHS Data Briefs 513/514, Zablotsky et al. 2025).
Weights WTFA_C; SEs clustered on pseudo-stratum x pseudo-PSU (PSTRAT, PPSU). Tables -> results/tables/nhis_*.csv."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; C = ROOT/"data/compiled/nhis"; pd.set_option("display.width", 220)
d = pd.read_parquet(ROOT/"data/extracts/nhis/child_2021_2024.parquet"); d = d[d.AGEP_C.between(5, 17)].copy()
d["w"] = d.WTFA_C.astype(float); d["cl"] = (d.PSTRAT.astype(int)*1000 + d.PPSU.astype(int))
for v, o in [("ANXFREQ_C", "anx"), ("DEPFREQ_C", "dep")]:
    ok = d[v].between(1, 5); d[f"{o}_dw"] = np.where(ok, d[v].le(2).astype(float), np.nan); d[f"{o}_daily"] = np.where(ok, d[v].eq(1).astype(float), np.nan)
d["girl"] = d.SEX_C.map({1: 0.0, 2: 1.0}); d["sex"] = d.SEX_C.map({1: "Male", 2: "Female"})
d["scr2"] = d.SCREENTIME_C.map({1: 1.0, 2: 0.0})
d["bully_any"] = np.where(d.BULLYVIC_C.between(0, 4), d.BULLYVIC_C.ge(1).astype(float), np.nan)
d["bully_month"] = np.where(d.BULLYVIC_C.between(0, 4), d.BULLYVIC_C.ge(2).astype(float), np.nan)
d["therapy"] = d.MHTHRPY_C.map({1: 1.0, 2: 0.0}); d["rx"] = d.MHRX_C.map({1: 1.0, 2: 0.0}); d["mhcare"] = np.fmax(d.therapy, d.rx)
d["agegrp"] = pd.cut(d.AGEP_C, [4, 11, 14, 17], labels=["5-11", "12-14", "15-17"]).astype(str)
d["agegrps"] = d.agegrp.map({"12-14": "12-14 years", "15-17": "15-17 years"})
d["hisprace"] = np.select([d.HISPALLP_C.eq(1), d.HISPALLP_C.between(2, 7)], ["Hispanic", "Non-Hispanic"], None)
d["race"] = d.RACEALLP_C.map({1: "White", 2: "Black", 3: "Asian", 4: "All other races", 5: "All other races", 6: "All other races"})
d["poverty"] = pd.cut(d.RATCAT_C, [0, 7, 11, 14], labels=["Less than 200% FPL", "200-399% FPL", "400% and greater FPL"]).astype(object)
d["metro"] = d.URBRRL.map({1: "Large central and fringe metro", 2: "Large central and fringe metro", 3: "Medium and small metro", 4: "Nonmetropolitan"})
d["education"] = pd.cut(d.MAXEDUCP_C, [-1, 4, 7, 10], labels=["High school diploma, GED, or less", "Some college", "College degree or higher"]).astype(object)
d["parnum"] = d.PCNTPARNTS_C.map({1: "Single parent", 2: "Two parents"}); d["region"] = d.REGION.map({1: "Northeast", 2: "Midwest", 3: "South", 4: "West"})
d["raceeth"] = d.HISPALLP_C.map({1: "Hispanic", 2: "NH White", 3: "NH Black", 4: "NH Asian"}).fillna("NH other")
for c in ["poverty", "education", "metro", "region", "parnum"]: d[c + "_c"] = d[c].fillna("Unknown")
# NHIS-Teen fielding periods: July 2021-Dec 2022 (18 months) and July 2021-Dec 2023 (30 months). 2021 contributes quarters 3-4 only, so its annual
# weights are doubled before pooling so that each calendar period carries the same population total (pooled weights then just rescale).
d["in18"] = ((d.SRVY_YR == 2021) & (d.INTV_QRT >= 3)) | (d.SRVY_YR == 2022); d["in30"] = d.in18 | (d.SRVY_YR == 2023)
d["w_pool"] = d.w * np.where(d.SRVY_YR == 2021, 2.0, 1.0)
teen = d[d.AGEP_C.between(12, 17)].copy()

def wm(df, y, w="w"):
    """Weighted percent with a design-based SE (linearised, clusters = PSTRAT x PPSU, G/(G-1) correction) and the unweighted n."""
    s = df[[y, w, "cl"]].dropna()
    if len(s) < 2: return np.nan, np.nan, len(s)
    p = np.average(s[y], weights=s[w]); z = (s[w]*(s[y]-p)).groupby(s.cl).sum(); G = len(z)
    return 100*p, 100*np.sqrt(G/(G-1)*(z**2).sum())/s[w].sum(), len(s)

# cross-check the hand linearisation against pyfixest's CRV1 intercept once
chk = teen[teen.anx_dw.notna()]; m = pf.feols("anx_dw ~ 1", data=chk, weights="w", vcov={"CRV1": "cl"}); p_, se_, n_ = wm(chk, "anx_dw")
print(f"SE check: pyfixest CRV1 {100*m.se().iloc[0]:.3f} vs linearised {se_:.3f} (mean {p_:.2f}, n={n_})")

# ---- 1. prevalence by year x sex x age -------------------------------------------------------------------------------------------------
OUTS = {"anx_dw": "Anxious daily/weekly (parent)", "anx_daily": "Anxious daily (parent)", "dep_dw": "Depressed daily/weekly (parent)", "dep_daily": "Depressed daily (parent)"}
rows = []
for yr in [2021, 2022, 2023, 2024, "2021-2024"]:
    s0 = d if yr == "2021-2024" else d[d.SRVY_YR == yr]
    for sx, sdf in [("all", s0), ("boys", s0[s0.girl == 0]), ("girls", s0[s0.girl == 1])]:
        for ag in ["12-17", "12-14", "15-17", "5-11"]:
            a = sdf[sdf.AGEP_C.between(12, 17)] if ag == "12-17" else sdf[sdf.agegrp == ag]
            for o in OUTS:
                p, se, n = wm(a, o); rows.append(dict(year=yr, sex=sx, ages=ag, outcome=o, pct=p, se=se, n=n))
prev = pd.DataFrame(rows); prev.to_csv(T/"nhis_prevalence.csv", index=False)
rows = []
for sx, sdf in [("all", d), ("boys", d[d.girl == 0]), ("girls", d[d.girl == 1])]:
    for age in range(5, 18):
        for o in OUTS:
            p, se, n = wm(sdf[sdf.AGEP_C == age], o); rows.append(dict(sex=sx, age=age, outcome=o, pct=p, se=se, n=n))
pd.DataFrame(rows).to_csv(T/"nhis_prevalence_age.csv", index=False)

# ---- 2. parent vs teen prevalence by subgroup in the NHIS-Teen periods ------------------------------------------------------------------
qt = pd.read_csv(C/"nhis_teen_query_tool.csv"); pub = pd.read_csv(C/"nhis_teen_published.csv"); pub.to_csv(T/"nhis_published.csv", index=False)
PAIRS = [("MH_ANX", "anx_dw", "all years in period"), ("MH_ANX", "anx_daily", "all years in period"), ("MH_DEP", "dep_dw", "all years in period"),
         ("MH_DEP", "dep_daily", "all years in period"), ("EVER_BULLIED", "bully_any", "parent item 2021 Q3-Q4 and 2022 only"), ("SCR", "scr2", "parent item 2022 only")]
GROUPS = {"ind": [("Total", None)], "sex": [("Male", "sex"), ("Female", "sex")], "agegrps": [("12-14 years", "agegrps"), ("15-17 years", "agegrps")],
          "hisprace": [("Hispanic", "hisprace"), ("Non-Hispanic", "hisprace")], "race": [(g, "race") for g in ["White", "Black", "Asian", "All other races"]],
          "poverty": [(g, "poverty") for g in ["Less than 200% FPL", "200-399% FPL", "400% and greater FPL"]],
          "metro": [(g, "metro") for g in ["Large central and fringe metro", "Medium and small metro", "Nonmetropolitan"]],
          "education": [(g, "education") for g in ["High school diploma, GED, or less", "Some college", "College degree or higher"]],
          "parnum": [("Single parent", "parnum"), ("Two parents", "parnum")], "region": [(g, "region") for g in ["Northeast", "Midwest", "South", "West"]]}
rows = []
for per, flag in [("July 2021–December 2022", "in18"), ("July 2021–December 2023", "in30")]:
    base = teen[teen[flag]]
    for ind, pv, note in PAIRS:
        b = base if pv not in ("scr2", "bully_any") else (base[base.SRVY_YR == 2022] if pv == "scr2" else base[base.SRVY_YR.isin([2021, 2022])])
        for gv, levels in GROUPS.items():
            for g, col in levels:
                sub = b if col is None else b[b[col] == g]
                p, se, n = wm(sub, pv, "w_pool")
                tq = qt[(qt.indicator_code == ind) & (qt.period == per) & (qt.group_var == gv) & (qt.group == g)]
                tp, lo, hi = (tq.pct.iloc[0], tq.ci_lo.iloc[0], tq.ci_hi.iloc[0]) if len(tq) else (np.nan, np.nan, np.nan)
                tse = (hi - lo)/3.92 if pd.notna(lo) else np.nan
                rows.append(dict(period=per, teen_indicator=ind, parent_item=pv, group_var=gv, group=g, parent_pct=p, parent_se=se, parent_n=n,
                                 teen_pct=tp, teen_ci_lo=lo, teen_ci_hi=hi, teen_se_approx=tse, ratio_parent_teen=p/tp if tp else np.nan,
                                 diff_pp=p - tp, diff_se=np.sqrt(se**2 + tse**2) if pd.notna(tse) else np.nan, parent_years=note))
agree = pd.DataFrame(rows); agree.to_csv(T/"nhis_agreement.csv", index=False)

# ---- 3. own-report gradients: parent-reported screen time / bullying -> parent-reported symptoms; teen rows from NCHS publications -------
COV = "C(AGEP_C) + C(SEX_C) + C(raceeth) + C(poverty_c) + C(education_c) + C(region_c) + C(metro_c)"
def gradient(df, x, y, spec, extra=""):
    f = f"{y} ~ {x} + C(SRVY_YR)" + (f" + {COV}" if spec != "unadjusted" else "") + extra
    s = df.dropna(subset=[x, y]); m = pf.feols(f, data=s, weights="w", vcov={"CRV1": "cl"})
    lo = wm(s[s[x] == 0], y); hi = wm(s[s[x] == 1], y)
    return dict(coef_pp=100*m.coef()[x], se=100*m.se()[x], n=int(m._N), pct_low=lo[0], se_low=lo[1], n_low=lo[2], pct_high=hi[0], se_high=hi[1], n_high=hi[2],
                pr=hi[0]/lo[0] if lo[0] else np.nan)
SAMPLES = lambda df: [("12-17", df[df.AGEP_C.between(12, 17)]), ("12-17 boys", df[df.AGEP_C.between(12, 17) & (df.girl == 0)]), ("12-17 girls", df[df.AGEP_C.between(12, 17) & (df.girl == 1)]),
                      ("12-14", df[df.agegrp == "12-14"]), ("15-17", df[df.agegrp == "15-17"]), ("5-11 (comparison)", df[df.agegrp == "5-11"])]
rows = []
scr = d[d.SRVY_YR.isin([2022, 2024]) & d.scr2.notna()]
for lab, s in SAMPLES(scr):
    for o in ["anx_dw", "anx_daily", "dep_dw", "dep_daily", "mhcare"]:
        for spec in ["unadjusted", "adjusted"]:
            rows.append(dict(informant="parent", exposure="2+ h weekday screen time (parent-reported)", years="2022, 2024", sample=lab, outcome=o, spec=spec, **gradient(s, "scr2", o, spec)))
        if lab.startswith("12-17") and o in ("anx_dw", "dep_dw"):   # 2022 is the only year with both the screen and the bullying item
            s22 = s[s.SRVY_YR == 2022].copy(); s22["bully_c"] = s22.BULLYVIC_C.where(s22.BULLYVIC_C.between(0, 4), 9).astype(int)
            rows.append(dict(informant="parent", exposure="2+ h weekday screen time (parent-reported)", years="2022", sample=lab, outcome=o, spec="adjusted + bullying", **gradient(s22, "scr2", o, "adjusted", " + C(bully_c)")))
            rows.append(dict(informant="parent", exposure="2+ h weekday screen time (parent-reported)", years="2022", sample=lab, outcome=o, spec="adjusted (2022 only)", **gradient(s22, "scr2", o, "adjusted")))
for o, pubo in [("anx_dw", "anxiety"), ("dep_dw", "depression")]:
    p = pub[(pub.exposure == "screen_4plus") & (pub.outcome == pubo)]
    hi, lo = p[p.level == "4+ hours"].iloc[0], p[p.level == "<4 hours"].iloc[0]
    pr, apr = p[p.measure == "PR"].iloc[0], p[p.measure == "APR"].iloc[0]
    rows.append(dict(informant="teen", exposure="4+ h weekday screen time (teen-reported)", years="Jul 2021-Dec 2023", sample="12-17", outcome=o, spec="unadjusted (NCHS Data Brief 513)",
                     coef_pp=hi.value - lo.value, se=np.sqrt(hi.se**2 + lo.se**2), n=1952, pct_low=lo.value, se_low=lo.se, pct_high=hi.value, se_high=hi.se, pr=pr.value, pr_lo=pr.ci_lo, pr_hi=pr.ci_hi))
    rows.append(dict(informant="teen", exposure="4+ h weekday screen time (teen-reported)", years="Jul 2021-Dec 2023", sample="12-17", outcome=o, spec="adjusted (Zablotsky et al. 2025, APR)",
                     n=1952, pr=apr.value, pr_lo=apr.ci_lo, pr_hi=apr.ci_hi))
grad = pd.DataFrame(rows); grad.to_csv(T/"nhis_screen_gradient.csv", index=False)
rows = []
bul = d[d.SRVY_YR.isin([2021, 2022]) & d.bully_any.notna()]
for lab, s in SAMPLES(bul)[:5]:
    for x in ["bully_any", "bully_month"]:
        for o in ["anx_dw", "anx_daily", "dep_dw", "dep_daily"]:
            for spec in ["unadjusted", "adjusted"]:
                rows.append(dict(informant="parent", exposure=f"{x} (parent-reported, 12m)", years="2021, 2022", sample=lab, outcome=o, spec=spec, **gradient(s, x, o, spec)))
for o, pubo in [("anx_dw", "anxiety"), ("dep_dw", "depression")]:
    p = pub[(pub.exposure == "bullied_12m") & (pub.outcome == pubo)]; hi, lo = p[p.level == "Bullied"].iloc[0], p[p.level == "Not bullied"].iloc[0]
    rows.append(dict(informant="teen", exposure="bullied in past 12 months (teen-reported)", years="Jul 2021-Dec 2023", sample="12-17", outcome=o, spec="unadjusted (NCHS Data Brief 514)",
                     coef_pp=hi.value - lo.value, se=np.sqrt(hi.se**2 + lo.se**2), pct_low=lo.value, se_low=lo.se, pct_high=hi.value, se_high=hi.se, pr=hi.value/lo.value))
bgr = pd.DataFrame(rows); bgr.to_csv(T/"nhis_bully_gradient.csv", index=False)

# ---- 4. internal validity of the parent items: treatment by reported symptom frequency; sex ratio ----------------------------------------
rows = []
for v, lab in [("ANXFREQ_C", "anxious"), ("DEPFREQ_C", "depressed")]:
    for code, name in {1: "daily", 2: "weekly", 3: "monthly", 4: "a few times a year", 5: "never"}.items():
        s = teen[teen[v] == code]
        for o in ["therapy", "rx", "mhcare"]:
            p, se, n = wm(s, o); rows.append(dict(item=lab, frequency=name, code=code, outcome=o, pct=p, se=se, n=n, share_pct=100*s.w.sum()/teen[teen[v].between(1, 5)].w.sum()))
pd.DataFrame(rows).to_csv(T/"nhis_validity.csv", index=False)
samp = teen.groupby("SRVY_YR").apply(lambda g: pd.Series(dict(n_12_17=len(g), n_anx_valid=g.anx_dw.notna().sum(), n_dep_valid=g.dep_dw.notna().sum(), n_screen=g.scr2.notna().sum(),
    n_bully=g.bully_any.notna().sum(), n_mhcare=g.mhcare.notna().sum(), n_5_11=int(d[(d.SRVY_YR == g.name) & (d.agegrp == "5-11")].shape[0]), quarters=",".join(map(str, sorted(g.INTV_QRT.unique()))))), include_groups=False).reset_index()
samp.to_csv(T/"nhis_sample.csv", index=False)

# ---- summary -------------------------------------------------------------------------------------------------------------------------
print("\nSample 12-17 by year:\n", samp.to_string(index=False))
pv = prev[(prev.year == "2021-2024") & prev.ages.isin(["12-17", "12-14", "15-17", "5-11"])].pivot_table(index=["ages", "sex"], columns="outcome", values="pct").round(1)
print("\nParent-reported prevalence 2021-2024 (%):\n", pv.to_string())
print("\nBy year, 12-17 (%):\n", prev[(prev.ages == "12-17") & (prev.year != "2021-2024")].pivot_table(index=["sex", "year"], columns="outcome", values="pct").round(1).to_string())
a = agree[(agree.period == "July 2021–December 2023") & agree.group_var.isin(["ind", "sex", "agegrps"]) & agree.parent_item.isin(["anx_dw", "dep_dw", "bully_any", "scr2"])]
print("\nParent vs teen prevalence, Jul 2021-Dec 2023 (%):\n", a[["parent_item", "group", "parent_pct", "parent_se", "teen_pct", "teen_ci_lo", "teen_ci_hi", "ratio_parent_teen"]].round(2).to_string(index=False))
g = grad[grad.outcome.isin(["anx_dw", "dep_dw"]) & grad.spec.isin(["unadjusted", "adjusted", "adjusted + bullying", "unadjusted (NCHS Data Brief 513)", "adjusted (Zablotsky et al. 2025, APR)"])]
print("\nScreen-time gradient (pp, parent 2+ h vs teen 4+ h):\n", g[["informant", "sample", "outcome", "spec", "pct_low", "pct_high", "coef_pp", "se", "pr", "n"]].round(2).to_string(index=False))
b = bgr[bgr.outcome.isin(["anx_dw", "dep_dw"]) & bgr.exposure.str.startswith(("bully_any", "bullied")) & bgr["sample"].isin(["12-17", "12-17 boys", "12-17 girls"])]
print("\nBullying gradient (pp):\n", b[["informant", "sample", "outcome", "spec", "pct_low", "pct_high", "coef_pp", "se", "pr", "n"]].round(2).to_string(index=False))
