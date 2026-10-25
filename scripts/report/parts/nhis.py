"""NHIS 2021-2024 Sample Child (parent-reported Washington Group items) vs NHIS-Teen (teen-reported GAD-2/PHQ-2, screen hours): prevalence under the
two informants, and the screen-time gradient under parent vs teen report. Reads results/tables/nhis_*.csv (built by scripts/analysis/27_nhis_teen_parent.py)."""
def build(ctx):
    pd, np, go = ctx.pd, ctx.np, ctx.go
    prev = pd.read_csv(ctx.T/"nhis_prevalence.csv"); agree = pd.read_csv(ctx.T/"nhis_agreement.csv"); grad = pd.read_csv(ctx.T/"nhis_screen_gradient.csv")
    bgr = pd.read_csv(ctx.T/"nhis_bully_gradient.csv"); pub = pd.read_csv(ctx.T/"nhis_published.csv"); samp = pd.read_csv(ctx.T/"nhis_sample.csv"); val = pd.read_csv(ctx.T/"nhis_validity.csv")
    mics = pd.read_csv(ctx.T/"mics_prevalence_sample_age_sex.csv")
    P30 = "July 2021–December 2023"
    def row(df, **kw):
        s = df
        for k, v in kw.items(): s = s[s[k] == v]
        assert len(s) == 1, (kw, len(s)); return s.iloc[0]
    def pubv(**kw): return row(pub, **kw).value
    n_teen = int(samp.n_12_17.sum()); n_anx = int(samp.n_anx_valid.sum()); n_scr = int(samp.n_screen.sum()); n_bul = int(samp.n_bully.sum())
    resp = dict(elig=int(pubv(exposure="response", level="eligible sample children 12-17")), perm=pubv(exposure="response", level="parent permission rate"),
                part=pubv(exposure="response", level="teen participation rate"), overall=pubv(exposure="response", level="overall response rate"), n=int(pubv(exposure="response", level="completed teen interviews")))
    # ---- informant comparison (period Jul 2021-Dec 2023) ----
    A = agree[agree.period == P30]
    def ag(item, grp): return row(A, parent_item=item, group=grp)
    GR = [("Total", "All"), ("Male", "Boys"), ("Female", "Girls"), ("12-14 years", "Ages 12–14"), ("15-17 years", "Ages 15–17")]
    fig = ctx.make_subplots(rows=1, cols=2, subplot_titles=("Anxiety: parent daily/weekly vs teen GAD-2 ≥ 3", "Depression: parent daily/weekly vs teen PHQ-2 ≥ 3"), shared_yaxes=True)
    for c, item in enumerate(["anx_dw", "dep_dw"], start=1):
        r = [ag(item, g) for g, _ in GR]
        fig.add_trace(go.Bar(name="Parent report (NHIS Sample Child)", x=[l for _, l in GR], y=[x.parent_pct for x in r], error_y=dict(type="data", array=[1.96*x.parent_se for x in r], thickness=1),
                             marker_color=ctx.MUTED, showlegend=(c == 1), hovertemplate="%{x}: %{y:.1f}%<extra>parent</extra>"), row=1, col=c)
        fig.add_trace(go.Bar(name="Teen self-report (NHIS-Teen)", x=[l for _, l in GR], y=[x.teen_pct for x in r], error_y=dict(type="data", symmetric=False, array=[x.teen_ci_hi - x.teen_pct for x in r], arrayminus=[x.teen_pct - x.teen_ci_lo for x in r], thickness=1),
                             marker_color=ctx.ALL, showlegend=(c == 1), hovertemplate="%{x}: %{y:.1f}%<extra>teen</extra>"), row=1, col=c)
    fig.update_yaxes(title_text="% of 12–17-year-olds", row=1, col=1); fig.update_layout(barmode="group")
    ctx.figs["nhis_informants"] = ctx.base(fig, h=380, hovermode="closest")
    # ---- screen-time gradient under parent vs teen report ----
    G = grad[grad.spec.isin(["adjusted", "unadjusted (NCHS Data Brief 513)"])]
    def gr(sample, out, informant): return row(G, sample=sample, outcome=out, informant=informant)
    ROWS = [("Teen: 4+ vs <4 h, all 12–17", "12-17", "teen", ctx.PAL[6]), ("Parent: 2+ vs <2 h, all 12–17", "12-17", "parent", ctx.ALL),
            ("Parent: boys 12–17", "12-17 boys", "parent", ctx.BOY), ("Parent: girls 12–17", "12-17 girls", "parent", ctx.GIRL), ("Parent: ages 5–11 (comparison)", "5-11 (comparison)", "parent", ctx.MUTED)]
    fig = ctx.make_subplots(rows=1, cols=2, subplot_titles=("Anxiety (% with symptoms)", "Depression (% with symptoms)"), shared_yaxes=True, horizontal_spacing=0.06)
    for c, out in enumerate(["anx_dw", "dep_dw"], start=1):
        for lab, smp, inf, col in ROWS[::-1]:
            x = gr(smp, out, inf)
            fig.add_trace(go.Scatter(x=[x.pct_low, x.pct_high], y=[lab, lab], mode="lines+markers", line=dict(color=col, width=3), marker=dict(size=[8, 12], color=col, symbol=["circle-open", "circle"]),
                                     error_x=dict(type="data", array=[1.96*x.se_low, 1.96*x.se_high], thickness=0.8, width=2, color=col), showlegend=False,
                                     hovertemplate="%{x:.1f}%<extra>" + lab + "</extra>"), row=1, col=c)
    fig.update_xaxes(range=[0, 32]); fig.update_xaxes(title_text="% with symptoms: open marker = lighter screen use, filled = heavier", row=1, col=1); fig.update_yaxes(autorange="reversed")
    ctx.figs["nhis_screen_gradient"] = ctx.base(fig, h=360, hovermode="closest", margin=dict(l=215, r=16, t=36, b=48))
    # ---- numbers for the prose ----
    t_anx, t_dep = ag("anx_dw", "Total"), ag("dep_dw", "Total"); b_anx, g_anx = ag("anx_dw", "Male"), ag("anx_dw", "Female"); b_dep, g_dep = ag("dep_dw", "Male"), ag("dep_dw", "Female")
    y_anx, o_anx = ag("anx_dw", "12-14 years"), ag("anx_dw", "15-17 years"); t_bul, t_scr = ag("bully_any", "Total"), ag("scr2", "Total"); d_anx = ag("anx_daily", "Total")
    pa = gr("12-17", "anx_dw", "parent"); pd_ = gr("12-17", "dep_dw", "parent"); ta = gr("12-17", "anx_dw", "teen"); td = gr("12-17", "dep_dw", "teen")
    pab, pag = gr("12-17 boys", "anx_dw", "parent"), gr("12-17 girls", "anx_dw", "parent"); pdb, pdg = gr("12-17 boys", "dep_dw", "parent"), gr("12-17 girls", "dep_dw", "parent")
    ya, yd = gr("5-11 (comparison)", "anx_dw", "parent"), gr("5-11 (comparison)", "dep_dw", "parent")
    apr_a = row(grad, informant="teen", outcome="anx_dw", spec="adjusted (Zablotsky et al. 2025, APR)"); apr_d = row(grad, informant="teen", outcome="dep_dw", spec="adjusted (Zablotsky et al. 2025, APR)")
    ab = row(grad, sample="12-17", outcome="anx_dw", spec="adjusted + bullying"); db = row(grad, sample="12-17", outcome="dep_dw", spec="adjusted + bullying")
    ab0 = row(grad, sample="12-17", outcome="anx_dw", spec="adjusted (2022 only)"); db0 = row(grad, sample="12-17", outcome="dep_dw", spec="adjusted (2022 only)")
    B = bgr[bgr.exposure.str.startswith("bully_any") | (bgr.informant == "teen")]
    bp_a = row(B, informant="parent", sample="12-17", outcome="anx_dw", spec="adjusted"); bp_d = row(B, informant="parent", sample="12-17", outcome="dep_dw", spec="adjusted")
    bt_a = row(B, informant="teen", outcome="anx_dw"); bt_d = row(B, informant="teen", outcome="dep_dw")
    yr = prev[(prev.ages == "12-17") & (prev.year != "2021-2024")]
    def yv(sex, year, out): return row(yr, sex=sex, year=str(year), outcome=out).pct
    v_daily = row(val, item="anxious", frequency="daily", outcome="mhcare"); v_never = row(val, item="anxious", frequency="never", outcome="mhcare"); v_week = row(val, item="anxious", frequency="weekly", outcome="mhcare")
    m = mics[(mics.agegrp == "15-17") & (mics.girl == 1)]; mics_med_anx, mics_med_dep, mics_n = m.anx_dw.median(), m.dep_dw.median(), m["sample"].nunique()
    us_g = row(prev, year="2021-2024", sex="girls", ages="15-17", outcome="anx_dw").pct; us_gd = row(prev, year="2021-2024", sex="girls", ages="15-17", outcome="dep_dw").pct
    pct = lambda v, d=1: f"{v:.{d}f}%"; f = ctx.fmt
    # ---- tables ----
    agree_rows = []
    for item, lab in [("anx_dw", "Anxious daily/weekly ↔ GAD-2 ≥ 3"), ("anx_daily", "Anxious daily ↔ GAD-2 ≥ 3"), ("dep_dw", "Sad/depressed daily/weekly ↔ PHQ-2 ≥ 3"), ("dep_daily", "Sad/depressed daily ↔ PHQ-2 ≥ 3"),
                      ("bully_any", "Bullied in past 12 months (parent 2021–22)"), ("scr2", "2+ h weekday screen time (parent 2022)")]:
        for g, gl in GR:
            x = ag(item, g); agree_rows.append([lab if g == "Total" else "", gl, f"{x.parent_pct:.1f} ({x.parent_se:.1f})", f"{x.teen_pct:.1f} ({x.teen_ci_lo:.1f}–{x.teen_ci_hi:.1f})", f"{x.ratio_parent_teen:.2f}", f"{int(x.parent_n):,}"])
    agree_tbl = ctx.table(["Item pair (parent ↔ teen)", "Group", "Parent % (SE)", "Teen % (95% CI)", "Parent ÷ teen", "Parent n"], agree_rows)
    grad_rows = []
    for lab, smp in [("All 12–17", "12-17"), ("Boys 12–17", "12-17 boys"), ("Girls 12–17", "12-17 girls"), ("Ages 12–14", "12-14"), ("Ages 15–17", "15-17"), ("Ages 5–11 (comparison)", "5-11 (comparison)")]:
        for out, ol in [("anx_dw", "anxious daily/weekly"), ("dep_dw", "sad/depressed daily/weekly")]:
            u = row(grad, informant="parent", sample=smp, outcome=out, spec="unadjusted"); a = row(grad, informant="parent", sample=smp, outcome=out, spec="adjusted")
            grad_rows.append([f"Parent: {lab}" if out == "anx_dw" else "", ol, f"{a.pct_low:.1f} → {a.pct_high:.1f}", f(u.coef_pp, u.se, 1), f(a.coef_pp, a.se, 1), f"{a.pr:.2f}", f"{int(a.n):,}"])
    for out, ol, x, apr in [("anx_dw", "GAD-2 ≥ 3", ta, apr_a), ("dep_dw", "PHQ-2 ≥ 3", td, apr_d)]:
        grad_rows.append(["Teen: all 12–17, 4+ h vs <4 h" if out == "anx_dw" else "", ol, f"{x.pct_low:.1f} → {x.pct_high:.1f}", f(x.coef_pp, x.se, 1), "—", f"{x.pr:.2f} (adj. {apr.pr:.2f}, {apr.pr_lo:.2f}–{apr.pr_hi:.2f})", f"{int(x.n):,}"])
    grad_tbl = ctx.table(["Informant and sample", "Outcome", "% lighter → heavier screen use", "Unadjusted (SE), pp", "Adjusted (SE), pp", "Prevalence ratio", "n"], grad_rows)
    yr_rows = [[y, pct(yv("boys", y, "anx_dw")), pct(yv("girls", y, "anx_dw")), pct(yv("boys", y, "dep_dw")), pct(yv("girls", y, "dep_dw"))] for y in [2021, 2022, 2023, 2024]]
    yr_tbl = ctx.table(["NHIS year", "Boys anxious d/w", "Girls anxious d/w", "Boys depressed d/w", "Girls depressed d/w"], yr_rows)
    html = f"""<h3 id="nhis">United States: parents and teenagers describing the same population (NHIS 2021–2024 and NHIS-Teen)</h3>
<p>The National Health Interview Survey's Sample Child interview asks a parent the Washington Group / UNICEF child-functioning items used in MICS, with
identical wording: how often the child "seems very anxious, nervous, or worried" and how often the child "seems very sad or depressed" (daily, weekly,
monthly, a few times a year, never). From July 2021 NCHS invited the 12–17-year-old sample children themselves to complete NHIS-Teen, a self-administered
web questionnaire with the PHQ-2 and GAD-2 screeners, weekday non-school screen hours, sleep, bullying and support items. It is the one national U.S. survey in
which the MICS caregiver items and an adolescent self-report screener describe the same children in the same months. The public-use Sample Child files
for 2021–2024 give {n_teen:,} adolescents aged 12–17 ({n_anx:,} with a valid anxiety item; the screen-time item was asked in 2022 and 2024, n = {n_scr:,}, and
the bullying item in 2021–2022, n = {n_bul:,}). The NHIS-Teen microdata, however, are released only through the NCHS Research Data Center ("there is no
public-use NHIS-Teen file"), so the person-level link cannot be made from public data. Of {resp['elig']:,} eligible sample children, {resp['perm']:.1f}% of parents
gave permission and {resp['part']:.1f}% of permitted teenagers responded (overall {resp['overall']:.1f}%, n = {resp['n']:,}); NCHS publishes weighted estimates from this
sample by parent-reported subgroup in its Interactive Summary Health Statistics for Teens and in a series of data briefs. This section therefore compares
the two informants at the population level (the same months, the same subgroups) and compares each informant's own screen-time gradient, rather than
agreement on linked individuals.</p>
<h4>Prevalence under the two informants</h4>
{ctx.fig_div('nhis_informants')}
<p class="caption">Children aged 12–17, {P30}. Parent report: NHIS Sample Child public-use files (2021 Q3–Q4, 2022, 2023; weighted with WTFA_C, 2021 weights
doubled for the half year; 95% CIs from SEs clustered on pseudo-stratum × PSU). Teen report: NCHS Interactive Summary Health Statistics for Teens
(NHIS-Teen weight, Korn–Graubard CIs). Subgroups follow the parent-reported classification used in both sources.</p>
<p>For anxiety the two informants land in the same place overall: {pct(t_anx.parent_pct)} of parents say their 12–17-year-old seems very anxious daily or weekly, and
{pct(t_anx.teen_pct)} of teenagers score 3 or more on the GAD-2. The composition differs. Parents report boys at {pct(b_anx.parent_pct)} against {pct(b_anx.teen_pct)} by the boys
themselves (ratio {b_anx.ratio_parent_teen:.2f}), and girls at {pct(g_anx.parent_pct)} against {pct(g_anx.teen_pct)} (ratio {g_anx.ratio_parent_teen:.2f}); the girl-to-boy ratio is {g_anx.parent_pct/b_anx.parent_pct:.1f} in parent reports and
{g_anx.teen_pct/b_anx.teen_pct:.1f} in self-reports. Parents also flatten the age gradient ({pct(y_anx.parent_pct)} at 12–14 and {pct(o_anx.parent_pct)} at 15–17, against {pct(y_anx.teen_pct)} and {pct(o_anx.teen_pct)} by the teenagers).
For depression the gap is large and uniform: {pct(t_dep.parent_pct)} of parents report daily or weekly sadness while {pct(t_dep.teen_pct)} of teenagers screen positive on the PHQ-2 (ratio
{t_dep.ratio_parent_teen:.2f}; {b_dep.ratio_parent_teen:.2f} for boys, {g_dep.ratio_parent_teen:.2f} for girls). The same direction appears for more observable items: parents report that {pct(t_bul.parent_pct)} of 12–17-year-olds were
bullied in the past year against {pct(t_bul.teen_pct)} by the teenagers, and that {pct(t_scr.parent_pct)} spend more than two hours a weekday on screens against {pct(t_scr.teen_pct)} who say so themselves.
Part of the depression gap is the instrument rather than the informant: when adults answered both sets of items about themselves in the 2019 NHIS, the PHQ
classified more people as depressed than the Washington Group item and the Washington Group item classified more as anxious than the GAD-7, with about
{pubv(source="NCHS NHSR 172", level="anxiety (WG-ANX vs GAD-7)"):.0f}% agreement for each pair after collapsing the lowest categories (NHSR 172).</p>
{agree_tbl}
<p class="caption">Parent and teen prevalence for the same population, {P30}, with the parent ÷ teen ratio. Parent n is the unweighted number of 12–17-year-olds with
a valid parent item in the period (the bullying item was asked in 2021–2022 and the screen item in 2022 only, so those rows use the parent data available
within the period). Teen estimates and CIs are NCHS's published values; GAD-2 and PHQ-2 are scored 0–6 with 3+ as symptomatic. The "daily" rows show that the
overall anxiety match depends on counting weekly as well as daily reports: only {pct(d_anx.parent_pct)} of 12–17-year-olds are described as anxious daily.</p>
<h4>The screen-time gradient under parent and teen report</h4>
{ctx.fig_div('nhis_screen_gradient')}
<p class="caption">Each row joins the share with symptoms among lighter users (open marker) and heavier users (filled marker), with 95% CIs. Teen row: NHIS-Teen,
{P30}, 4+ versus fewer than 4 weekday non-school screen hours and GAD-2 / PHQ-2 ≥ 3 (NCHS Data Brief 513, n = {int(ta.n):,}). Parent rows: NHIS Sample Child 2022 and 2024,
parent-reported "more than 2 hours a weekday" versus not and parent-reported daily/weekly anxiety or sadness. NCHS has not published the teen gradient by sex.</p>
<p>NCHS reports that teenagers with four or more hours of daily screen time were more than twice as likely to screen positive for anxiety ({pct(ta.pct_low)} → {pct(ta.pct_high)},
prevalence ratio {ta.pr:.2f}; {apr_a.pr:.2f} after adjustment for age, sex, race and Hispanic origin, urbanization, parental education and income) and for depression
({pct(td.pct_low)} → {pct(td.pct_high)}, ratio {td.pr:.2f}; adjusted {apr_d.pr:.2f}, 95% CI {apr_d.pr_lo:.2f}–{apr_d.pr_hi:.2f}). In the parent interview, where the same adult reports both the child's screen time and the
child's mood, the gradient is present but, for anxiety, far shallower: 12–17-year-olds whose parents say they exceed two hours a weekday are {f(pa.coef_pp, pa.se, 1)} pp more likely to be
described as anxious daily or weekly ({pct(pa.pct_low)} → {pct(pa.pct_high)}, ratio {pa.pr:.2f}, with age, sex, race/ethnicity, income, parental education, region, urbanicity and year controls)
and {f(pd_.coef_pp, pd_.se, 1)} pp more likely to be described as sad or depressed ({pct(pd_.pct_low)} → {pct(pd_.pct_high)}, ratio {pd_.pr:.2f}). The parent-reported gradient is similar for boys
({f(pab.coef_pp, pab.se, 1)} anxiety, {f(pdb.coef_pp, pdb.se, 1)} depression) and girls ({f(pag.coef_pp, pag.se, 1)} and {f(pdg.coef_pp, pdg.se, 1)}), survives a control for parent-reported bullying in 2022
({f(ab.coef_pp, ab.se, 1)} and {f(db.coef_pp, db.se, 1)}, against {f(ab0.coef_pp, ab0.se, 1)} and {f(db0.coef_pp, db0.se, 1)} without it in the same year), and is weaker among 5–11-year-olds ({f(ya.coef_pp, ya.se, 1)} and {f(yd.coef_pp, yd.se, 1)}), the
group for which the MICS analysis found a comparable cluster-level association. The exposure thresholds differ (2+ hours, which {pct(t_scr.parent_pct)} of parents affirm, against 4+ hours, which
about half of teenagers report), so the pp differences are not directly comparable; the prevalence ratios are the better comparison, and they put the parent-reported depression
gradient ({pd_.pr:.2f}) close to the teen-reported one ({td.pr:.2f}) but the parent-reported anxiety gradient ({pa.pr:.2f}) well below it ({ta.pr:.2f}).</p>
{grad_tbl}
<p class="caption">Linear probability models, weighted, SEs clustered on pseudo-stratum × PSU. Parent rows pool NHIS 2022 and 2024 (the years with the screen-time item);
adjusted models add single-year age, sex, race/ethnicity, income-to-poverty category, parental education, region, urbanicity and year. Teen rows are NCHS's published
estimates (Data Brief 513 for the percentages; Zablotsky et al. 2025 for the Poisson prevalence ratios, with the adjusted ratio and its 95% CI in parentheses).</p>
<p>Bullying provides a benchmark for how well a parent-reported exposure tracks a parent-reported symptom when the exposure is salient to the parent. Among
12–17-year-olds in 2021–2022, those whose parents report that they were bullied in the past year are {f(bp_a.coef_pp, bp_a.se, 1)} pp more often described as anxious daily or weekly
({pct(bp_a.pct_low)} → {pct(bp_a.pct_high)}, ratio {bp_a.pr:.2f}) and {f(bp_d.coef_pp, bp_d.se, 1)} pp more often as sad or depressed (ratio {bp_d.pr:.2f}); in the teenagers' own reports the corresponding
differences are {bt_a.coef_pp:.1f} pp (ratio {bt_a.pr:.2f}) and {bt_d.coef_pp:.1f} pp (ratio {bt_d.pr:.2f}) (Data Brief 514). The parent items also behave as expected against treatment: {pct(v_daily.pct)} of
12–17-year-olds described as anxious daily received mental-health therapy or medication in the past year, against {pct(v_week.pct)} of those anxious weekly and {pct(v_never.pct)} of those never anxious.</p>
<h4>Level and trend, 2021–2024</h4>
{yr_tbl}
<p class="caption">Parent-reported daily/weekly anxiety and sadness among 12–17-year-olds by NHIS year (weighted; d/w = daily or weekly). Full table with SEs and
single-year ages in <code>results/tables/nhis_prevalence.csv</code> and <code>nhis_prevalence_age.csv</code>.</p>
<p>Parent-reported anxiety among 12–17-year-olds moved from {pct(yv("all", 2021, "anx_dw"))} in 2021 to {pct(yv("all", 2022, "anx_dw"))} in 2022 and back to {pct(yv("all", 2024, "anx_dw"))} in 2024, with the swing concentrated among girls
({pct(yv("girls", 2021, "anx_dw"))} → {pct(yv("girls", 2022, "anx_dw"))} → {pct(yv("girls", 2024, "anx_dw"))}); parent-reported sadness followed the same path ({pct(yv("all", 2021, "dep_dw"))} → {pct(yv("all", 2022, "dep_dw"))} → {pct(yv("all", 2024, "dep_dw"))}). The post-2022 decline matches the downturn in
self-reported sadness in the state youth surveys and the 2023 YRBS described above. On the MICS scale the U.S. parent reports sit in the upper middle of the international
range: {pct(us_g)} of U.S. girls aged 15–17 are described as anxious daily or weekly and {pct(us_gd)} as sad or depressed, against medians of {pct(mics_med_anx)} and {pct(mics_med_dep)} across the {mics_n} MICS samples in the prevalence table.</p>
<p>Published work with the linked NHIS-Teen file, all from NCHS, points the same way as the population comparison. Parents report more health-care use than their
teenagers do, with weighted Cohen's kappa between {pubv(source="NCHS NHSR 219", measure="kappa", level="min (personal doctor or nurse)"):.2f} and {pubv(source="NCHS NHSR 219", measure="kappa", level="max (time alone with doctor)"):.2f} across items
(<a href="https://dx.doi.org/10.15620/cdc/174622">Ng et al. 2025, NHSR 219</a>); parents report fewer adverse experiences than their teenagers, for instance {pubv(source="Ng et al. 2025 Child Abuse Negl", level="parent"):.1f}% against {pubv(source="Ng et al. 2025 Child Abuse Negl", level="teen"):.1f}% for
witnessing neighborhood violence, with kappas of {pubv(source="Ng et al. 2025 Child Abuse Negl", measure="kappa", level="min"):.2f}–{pubv(source="Ng et al. 2025 Child Abuse Negl", measure="kappa", level="max"):.2f} (<a href="https://doi.org/10.1016/j.chiabu.2025.107339">Ng et al. 2025</a>);
teenagers who rarely receive social and emotional support report anxiety symptoms at {pubv(source="NCHS NHSR 206", level="No", outcome="anxiety"):.1f}% against {pubv(source="NCHS NHSR 206", level="Yes", outcome="anxiety"):.1f}%
(<a href="https://dx.doi.org/10.15620/cdc/156514">Zablotsky et al. 2024, NHSR 206</a>); and the screen-time gradient above is from <a href="https://www.cdc.gov/nchs/products/databriefs/db513.htm">Data Brief 513</a> and
<a href="https://doi.org/10.5888/pcd22.240537">Zablotsky et al. 2025</a>. The broader literature puts parent–youth agreement on internalizing symptoms at a mean correlation of
{pubv(source="De Los Reyes et al. 2015", level="internalizing"):.2f} across {int(row(pub, source="De Los Reyes et al. 2015", level="internalizing").n)} studies (<a href="https://doi.org/10.1037/a0038498">De Los Reyes et al. 2015</a>). No NCHS publication has yet reported parent–teen agreement on the
anxiety and depression items themselves; that is the first table an RDC proposal should produce.</p>
<div class="note"><strong>Assessment.</strong> The NHIS pair does not resolve the caregiver–adolescent divergence, but it narrows it. Both informants show a screen-time gradient
in their own reports, so the MICS null is not explained simply by parents being unable to see a link between heavy use and distress; the parent-reported gradient for
anxiety is, however, much shallower than the teenagers' ({pa.pr:.2f} against {ta.pr:.2f}), and parents compress exactly the contrasts that dominate the self-report literature on H1: the
girl–boy gap ({g_anx.parent_pct/b_anx.parent_pct:.1f}× against {g_anx.teen_pct/b_anx.teen_pct:.1f}×) and the age gradient, while reporting less than half the depression the teenagers report. A caregiver-reported outcome therefore
has limited power to detect a girl-specific, adolescence-specific association even when one exists, which is consistent with the MICS own-use estimates being near zero for
girls while GSHS self-reports show a steep gradient. Because parent exposure and parent outcome come from one respondent here, as teen exposure and teen outcome do in GSHS,
neither gradient separates a real association from shared-informant reporting; the cross-informant test on linked individuals requires the NHIS-Teen restricted file (RDC).
The 2022 peak and subsequent decline in parent-reported anxiety and sadness independently corroborate the post-2021 downturn seen in self-report surveys (H0: not a
self-report artifact).</div>"""
    return {"nhis": html}
