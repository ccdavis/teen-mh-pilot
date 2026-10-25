"""NSCH 2016-2025 (parent reports): trends in current anxiety/depression, the U.S. caregiver screen-time gradient, sleep and bullying as
mediators, state smartphone adoption, and a first look at the statewide school phone bans (Florida 2023-24, IN/LA/SC 2024-25, the 2025-26 wave)."""
def build(ctx):
    pd, np, go = ctx.pd, ctx.np, ctx.go
    T, f = ctx.T, ctx.fmt
    S = pd.read_csv(T/"nsch_sample.csv"); P = pd.read_csv(T/"nsch_screen_prevalence.csv"); G = pd.read_csv(T/"nsch_screen_gradient.csv")
    TR = pd.read_csv(T/"nsch_trends_state_year.csv"); AD = pd.read_csv(T/"nsch_adoption.csv"); D = pd.read_csv(T/"nsch_ban_did.csv")
    FL = pd.read_csv(T/"nsch_florida_series.csv"); M = pd.read_csv(T/"nsch_mediators.csv"); L = pd.read_csv(T/"nsch_literature.csv")
    def pick(df, **k):
        q = df
        for a, b in k.items(): q = q[q[a] == b]
        assert len(q) >= 1, f"no row for {k}"
        return q.iloc[0]
    def fm(df, **k):
        r = pick(df, **k); return f(r.coef, r.se)
    def pct(x, d=1): return f"{x:.{d}f}%"
    n_all = int(S.n.sum()); n_teen = int(S[S.agegrp == "12-17"].n.sum()); y0, y1 = int(S.year.min()), int(S.year.max())
    nat = TR[(TR.state == 0)]
    def natv(sex, ag, y, o): return pick(nat, sex=sex, agegrp=ag, year=y)[o]
    def natse(sex, ag, y, o): return pick(nat, sex=sex, agegrp=ag, year=y)[o + "_se"]
    CAT = ["<1 h", "1 h", "2 h", "3 h", "4+ h"]

    # ---------------- chart 1: national trends by sex and age group
    fig = ctx.make_subplots(rows=1, cols=2, subplot_titles=("Currently has anxiety problems (%)", "Currently has depression (%)"), horizontal_spacing=0.08)
    for j, o in enumerate(["anx_cur", "dep_cur"], start=1):
        for sex, col in [("girls", ctx.GIRL), ("boys", ctx.BOY)]:
            for ag, dash, w in [("12-17", "solid", 2.4), ("6-11", "dot", 1.6)]:
                s = nat[(nat.sex == sex) & (nat.agegrp == ag)].sort_values("year")
                fig.add_trace(go.Scatter(x=s.year, y=s[o], mode="lines+markers", name=f"{sex} {ag}", line=dict(color=col, dash=dash, width=w), marker=dict(size=5),
                                         error_y=dict(type="data", array=1.96 * s[o + "_se"], visible=True, thickness=0.8, width=0), showlegend=(j == 1)), row=1, col=j)
        ctx.covid_band(fig, row=1, col=j)
    fig.update_yaxes(rangemode="tozero"); ctx.figs["nsch_trends"] = ctx.base(fig, h=380)

    # ---------------- chart 2: gradient by screen-time category, sex and age group (2018-2025)
    fig = ctx.make_subplots(rows=1, cols=2, subplot_titles=("Current anxiety by weekday screen hours (%)", "Current depression by weekday screen hours (%)"), horizontal_spacing=0.08)
    for j, o in enumerate(["anx_cur", "dep_cur"], start=1):
        for sex, col in [("girls", ctx.GIRL), ("boys", ctx.BOY)]:
            for ag, dash, w in [("12-17", "solid", 2.4), ("6-11", "dot", 1.6)]:
                s = P[(P.sex == sex) & (P.agegrp == ag)].set_index("screen_cat").reindex(CAT)
                fig.add_trace(go.Scatter(x=CAT, y=s[o], mode="lines+markers", name=f"{sex} {ag}", line=dict(color=col, dash=dash, width=w), marker=dict(size=6),
                                         error_y=dict(type="data", array=1.96 * s[o + "_se"], visible=True, thickness=0.8, width=0), showlegend=(j == 1)), row=1, col=j)
    fig.update_yaxes(rangemode="tozero"); ctx.figs["nsch_gradient"] = ctx.base(fig, h=380, hovermode="x")

    # ---------------- chart 3: Florida vs other states, and the event-study coefficients
    fig = ctx.make_subplots(rows=1, cols=2, subplot_titles=("Current anxiety, ages 12-17 (%): Florida vs. other states", "Event study (pp) by years from the first ban school year"), horizontal_spacing=0.08)
    for sex, col in [("girls", ctx.GIRL), ("boys", ctx.BOY)]:
        for grp, dash, w in [("Florida", "solid", 2.4), ("Other states", "dash", 1.4)]:
            s = FL[(FL.agegrp == "12-17") & (FL.sex == sex) & (FL.group == grp)].sort_values("year")
            fig.add_trace(go.Scatter(x=s.year, y=s.anx_cur, mode="lines+markers", name=f"{sex}, {grp}", line=dict(color=col, dash=dash, width=w), marker=dict(size=5),
                                     error_y=dict(type="data", array=1.96 * s.anx_cur_se, visible=(grp == "Florida"), thickness=0.8, width=0)), row=1, col=1)
    fig.add_vrect(x0=2023.5, x1=2025.5, fillcolor="rgba(235,104,52,.08)", line_width=0, row=1, col=1)
    EV = ["ev_m4plus", "ev_m3", "ev_m2", "ref", "ev_p0", "ev_p1", "ev_p2"]; EVX = ["<= -4", "-3", "-2", "-1 (ref)", "0 (took effect)", "+1", "+2"]
    for o, sym in [("anx_cur", "circle"), ("dep_cur", "diamond")]:
        for sex, col, off in [("girls", ctx.GIRL, -0.12), ("boys", ctx.BOY, 0.12)]:
            e = D[(D.design == "individual event study") & (D.agegrp == "12-17") & (D.sex == sex) & (D.outcome == o)].set_index("term")
            ys = [0 if t == "ref" else e.loc[t, "coef"] for t in EV]; es = [0 if t == "ref" else 1.96 * e.loc[t, "se"] for t in EV]
            fig.add_trace(go.Scatter(x=[i + off for i in range(len(EV))], y=ys, mode="markers", name=f"{sex}, {'anxiety' if o == 'anx_cur' else 'depression'}", marker=dict(color=col, symbol=sym, size=8, opacity=1 if o == "anx_cur" else 0.55),
                                     error_y=dict(type="data", array=es, visible=True, thickness=1, width=3), showlegend=True), row=1, col=2)
    fig.add_hline(y=0, line=dict(color=ctx.MUTED, width=1), row=1, col=2)
    fig.update_xaxes(tickmode="array", tickvals=list(range(len(EV))), ticktext=EVX, row=1, col=2)
    ctx.figs["nsch_bans"] = ctx.base(fig, h=400, hovermode="closest")

    # ---------------- numbers for the prose
    g18 = G[(G.period == "2018-2025") & (G.term == "scr_4p")]
    def gr(o, sex, ag): return pick(g18, outcome=o, sex=sex, agegrp=ag)
    share4 = pick(P, sex="all", agegrp="12-17", screen_cat="4+ h").share_of_group; share4y = pick(P, sex="all", agegrp="6-11", screen_cat="4+ h").share_of_group
    peak_g = nat[(nat.sex == "girls") & (nat.agegrp == "12-17")].sort_values("anx_cur").iloc[-1]; peak_gd = nat[(nat.sex == "girls") & (nat.agegrp == "12-17")].sort_values("dep_cur").iloc[-1]
    def chg(sex, ag, o, a, b):
        da = natv(sex, ag, b, o) - natv(sex, ag, a, o); se = (natse(sex, ag, a, o) ** 2 + natse(sex, ag, b, o) ** 2) ** 0.5; return f(da, se)
    # external comparisons (GSHS self-report gradient; MICS caregiver own-use null), read from the Phase 1 tables when present
    comp = ""
    try:
        MH = pd.read_csv(T/"gshs_mobile_hours.csv"); MO = pd.read_csv(T/"mics_own_use_1517.csv")
        gl = pick(MH, sex="girls", outcome="lonely"); gs = pick(MH, sex="girls", outcome="suicide_consider")
        mn = pick(MO, sex="girls", exposure="net_daily", outcome="anx_dw", fe="cluster FE"); mp = pick(MO, sex="girls", exposure="phone_daily", outcome="anx_dw", fe="cluster FE")
        comp = (f" For scale, the self-reported GSHS gradient for girls using a mobile phone three or more hours a day was {f(gl.coef_3plus, gl.se)} pp on loneliness and "
                f"{f(gs.coef_3plus, gs.se)} pp on suicidal ideation, while the MICS caregiver reports gave {f(mn.coef_pp, mn.se)} pp (daily internet use) and {f(mp.coef_pp, mp.se)} pp (daily phone use) on girls' anxiety within sampling clusters. "
                f"U.S. caregivers, asked about diagnosed and current conditions rather than how often the child seems anxious, report a gradient at least as steep as the adolescents' own reports in GSHS.")
    except Exception:
        pass
    # mediators
    def md(o, sex, term, spec=None, block="screen -> mediator", ag="12-17"):
        q = M[(M.block == block) & (M.outcome == o) & (M.sex == sex) & (M.term == term) & (M.agegrp == ag)]
        if spec is not None: q = q[q.spec == spec]
        return q.iloc[0]
    def atten(o, sex):
        b = md(o, sex, "scr_4p", "base", "gradient with mediators"); m = md(o, sex, "scr_4p", "+ sleep and bullying", "gradient with mediators"); return b, m, 100 * (1 - m.coef / b.coef)
    # adoption
    adw = AD[AD.spec == "2017-2023 (within NTIA waves)"]; ad = lambda o, sex, ag="12-17": pick(adw, outcome=o, sex=sex, agegrp=ag)
    sdrow = AD[AD.spec == "NTIA cross-state distribution (wave year)"].set_index("year")
    # bans
    ind = D[(D.design == "individual DiD") & (D["sample"] == "all mandate states")]; pan = D[(D.design == "state-year panel DiD") & (D["sample"] == "all mandate states")]
    flo = D[(D.design == "state-year panel DiD") & (D["sample"].str.startswith("Florida"))]
    def bd(df, o, sex, term, ag="12-17"): return pick(df, outcome=o, sex=sex, term=term, agegrp=ag)
    nst_full = int(pick(ind, outcome="anx_cur", sex="all", term="post_full").treated_states)
    evg = D[(D.design == "individual event study") & (D.agegrp == "12-17") & (D.outcome == "anx_cur")]
    def ev(sex, t): return pick(evg, sex=sex, term=t)
    def flv(grp, sex, y, o="anx_cur"): return pick(FL, agegrp="12-17", group=grp, sex=sex, year=y)[o]

    # ---------------- tables
    def row_grad(o, lab):
        return [lab] + [fm(g18, outcome=o, sex=s, agegrp=a) for s, a in [("girls", "12-17"), ("boys", "12-17"), ("girls", "6-11"), ("boys", "6-11")]] + [pct(gr(o, "all", "12-17")["mean"]), pct(gr(o, "all", "6-11")["mean"])]
    t_grad = ctx.table(["Parent-reported outcome", "Girls 12–17", "Boys 12–17", "Girls 6–11", "Boys 6–11", "Mean 12–17", "Mean 6–11"],
                       [row_grad("anx_cur", "Currently has anxiety problems"), row_grad("anx_modsev", "… moderate or severe"), row_grad("dep_cur", "Currently has depression"), row_grad("dep_modsev", "… moderate or severe"),
                        row_grad("adhd_cur", "Currently has ADD/ADHD (contrast)"), row_grad("beh_cur", "Currently has behavior/conduct problems (contrast)")])
    def row_per(o, lab):
        cells = []
        for per in ["2018-2019", "2022-2025", "2018-2025"]:
            cells.append(" / ".join(fm(G, period=per, outcome=o, sex=s, agegrp="12-17", term="per_hour") for s in ["girls", "boys"]))
        cells.append(" / ".join(fm(G, period="2016-2017", outcome=o, sex=s, agegrp="12-17", term="per_hour") for s in ["girls", "boys"]))
        return [lab] + cells
    t_per = ctx.table(["Outcome, ages 12–17 (girls / boys)", "2018–19", "2022–25", "2018–25", "2016–17, two items summed"], [row_per("anx_cur", "Current anxiety, pp per weekday hour"), row_per("dep_cur", "Current depression, pp per weekday hour"), row_per("adhd_cur", "Current ADD/ADHD, pp per weekday hour")])
    def row_med(o, lab):
        cells = []
        for sex in ["girls", "boys"]:
            b, m, a = atten(o, sex); cells += [f(b.coef, b.se), f(m.coef, m.se), f"{a:.0f}%"]
        return [lab] + cells
    t_med = ctx.table(["4+ h vs 1 h, ages 12–17", "Girls: base", "Girls: + sleep, bullying", "Girls: attenuation", "Boys: base", "Boys: + sleep, bullying", "Boys: attenuation"],
                      [row_med("anx_cur", "Current anxiety"), row_med("dep_cur", "Current depression"), row_med("adhd_cur", "Current ADD/ADHD")])
    def row_ad(o, lab): return [lab] + [f(ad(o, s, a).coef_per10pp, ad(o, s, a).se) for s, a in [("girls", "12-17"), ("boys", "12-17"), ("girls", "6-11"), ("boys", "6-11")]] + [f"{int(ad(o, 'girls').n_state_years):,}"]
    t_ad = ctx.table(["Outcome", "Girls 12–17", "Boys 12–17", "Girls 6–11", "Boys 6–11", "State-years"], [row_ad("anx_cur", "Current anxiety"), row_ad("dep_cur", "Current depression"), row_ad("adhd_cur", "Current ADD/ADHD")])
    FP0 = pd.read_csv(T/"nsch_ban_florida_placebo.csv")
    def row_ban(o, lab):
        r = [lab]
        for sex in ["girls", "boys"]:
            fp = pick(FP0, outcome=o, sex=sex, agegrp="12-17")
            r += [f(bd(ind, o, sex, "post_full").coef, bd(ind, o, sex, "post_full").se), f(bd(ind, o, sex, "post_partial").coef, bd(ind, o, sex, "post_partial").se), f(fp.coef_full, fp.placebo_sd_full)]
        r += [f(bd(ind, o, "all", "post_full", "6-11").coef, bd(ind, o, "all", "post_full", "6-11").se)]
        return r
    t_ban = ctx.table(["Outcome", "Girls 12–17: in force, full year", "Girls: took effect during field period", "Girls: Florida only, full years (placebo SD)", "Boys 12–17: in force, full year", "Boys: took effect during field period", "Boys: Florida only, full years (placebo SD)", "Ages 6–11: in force, full year"],
                      [row_ban("anx_cur", "Current anxiety"), row_ban("dep_cur", "Current depression"), row_ban("adhd_cur", "Current ADD/ADHD (contrast)")])
    t_ev = ctx.table(["Years relative to the mandate's first school year", "Girls 12–17, anxiety", "Boys 12–17, anxiety", "Girls 12–17, depression", "Boys 12–17, depression"],
                     [[lab] + [f(pick(D, design="individual event study", agegrp="12-17", sex=s, outcome=o, term=t).coef, pick(D, design="individual event study", agegrp="12-17", sex=s, outcome=o, term=t).se) for o in ["anx_cur", "dep_cur"] for s in ["girls", "boys"]]
                      for t, lab in [("ev_m4plus", "≤ −4 (placebo)"), ("ev_m3", "−3 (placebo)"), ("ev_m2", "−2 (placebo)"), ("ev_p0", "0: first school year, field period straddles the start"), ("ev_p1", "+1: in force for a full school year"), ("ev_p2", "+2 (Florida only)")]])
    PM = pd.read_csv(T/"nsch_ban_permutation.csv"); FP = pd.read_csv(T/"nsch_ban_florida_placebo.csv")
    def pm(o, sex, w, ag="12-17"): return pick(PM, outcome=o, sex=sex, weights=w, agegrp=ag)
    def row_pm(o, sex, lab, ag="12-17"):
        a, b = pm(o, sex, "cell n", ag), pm(o, sex, "population (sum of FWC)", ag)
        return [lab, f(a.coef_full, a.se_cluster_full), f"{a.perm_sd_full:.2f}", f"{a.perm_p_full:.2f}", f(b.coef_full, b.se_cluster_full), f"{b.perm_sd_full:.2f}", f"{b.perm_p_full:.2f}"]
    t_perm = ctx.table(["Mandate in force, full year", "Equal state weights: coef (cluster SE)", "Permutation SD", "Permutation p", "Population weights: coef (cluster SE)", "Permutation SD", "Permutation p"],
                       [row_pm("anx_cur", "girls", "Anxiety, girls 12–17"), row_pm("anx_cur", "boys", "Anxiety, boys 12–17"), row_pm("dep_cur", "girls", "Depression, girls 12–17"), row_pm("dep_cur", "boys", "Depression, boys 12–17"),
                        row_pm("adhd_cur", "girls", "ADD/ADHD (contrast), girls 12–17"), row_pm("adhd_cur", "boys", "ADD/ADHD (contrast), boys 12–17"), row_pm("anx_cur", "all", "Anxiety, ages 6–11 (comparison)", "6-11")])
    pan_pop = D[(D.design == "state-year panel DiD, population-weighted") & (D["sample"] == "all mandate states")]
    fpg = pick(FP, outcome="anx_cur", sex="girls", agegrp="12-17"); fpb = pick(FP, outcome="anx_cur", sex="boys", agegrp="12-17"); fpa = pick(FP, outcome="adhd_cur", sex="girls", agegrp="12-17")
    nperm = int(PM.n_perm.iloc[0])
    t_lit = ctx.table(["Study", "NSCH data", "Finding"], [[f'<a href="{r.url}">{r.study}</a>' + ("" if str(r.verified).startswith("yes") else " <span class=\"muted\">(not verified against the source)</span>"), r.data, r.finding] for _, r in L.iterrows()])

    b_anx_g, m_anx_g, a_anx_g = atten("anx_cur", "girls"); b_dep_g, m_dep_g, a_dep_g = atten("dep_cur", "girls")
    sl_g = md("sleep_lt8", "girls", "scr_4p"); bu_g = md("bullied_monthly", "girls", "scr_4p"); sl_b = md("sleep_lt8", "boys", "scr_4p"); bu_b = md("bullied_monthly", "boys", "scr_4p")
    dir_sl = md("anx_cur", "girls", "sleep_lt8", "+ sleep and bullying", "mediator -> outcome"); dir_bu = md("anx_cur", "girls", "bullied_monthly", "+ sleep and bullying", "mediator -> outcome")
    raw4 = pick(G, period="2018-2025", outcome="anx_cur", sex="girls", agegrp="12-17", term="scr_4p_raw")

    html = f"""<h3 id="nsch">Parent-reported anxiety and depression in the United States: NSCH 2016–2025</h3>
<p>The National Survey of Children's Health (HRSA/Census) asks a parent or caregiver each year whether a doctor or other health care provider has <em>ever</em> told them the child has anxiety problems or depression, whether the child <em>currently</em> has the condition, and how severe it is, alongside a single weekday screen-time item ("on most weekdays, about how much time did this child spend in front of a TV, computer, cellphone or other electronic device … do not include time spent doing schoolwork"), weeknight sleep, bullying victimization, school engagement, and the state of residence. It is the U.S. counterpart to the MICS caregiver reports above: the same informant, but asked about diagnosed conditions rather than how often the child seems anxious or sad. We use the public-use topical files for {y0}–{y1} ({n_all:,} children aged 6–17, of whom {n_teen:,} are 12–17; the 2025 file was released in October 2026), with survey weights, and treat 2016–17 separately because the screen-time item was split into TV and device questions in those two years.</p>
<h4>Trends 2016–2025</h4>
{ctx.fig_div('nsch_trends')}
<p class="caption">Weighted share of children whose parent reports a current condition, by survey year, with 95% intervals (one child per household; stratification ignored). Solid lines ages 12–17, dotted lines ages 6–11. Grey band = 2020; the NSCH is fielded from June into the following winter, so a survey year straddles two school years.</p>
<p>Parent-reported current anxiety among girls aged 12–17 rose from {pct(natv('girls','12-17',2016,'anx_cur'))} in 2016 to a peak of {pct(peak_g.anx_cur)} in {int(peak_g.year)}, and current depression from {pct(natv('girls','12-17',2016,'dep_cur'))} to {pct(peak_gd.dep_cur)} in {int(peak_gd.year)}; boys rose from {pct(natv('boys','12-17',2016,'anx_cur'))} to {pct(natv('boys','12-17',2024,'anx_cur'))} on anxiety with little change on depression. The 2025 survey is the first in the series to fall: girls' anxiety dropped by {chg('girls','12-17','anx_cur',2024,2025)} pp to {pct(natv('girls','12-17',2025,'anx_cur'))} and depression by {chg('girls','12-17','dep_cur',2024,2025)} pp to {pct(natv('girls','12-17',2025,'dep_cur'))}, while boys changed by {chg('boys','12-17','anx_cur',2024,2025)} pp and {chg('boys','12-17','dep_cur',2024,2025)} pp. Among 6–11-year-olds anxiety rose from {pct(natv('all','6-11',2016,'anx_cur'))} to {pct(natv('all','6-11',2024,'anx_cur'))} and was {pct(natv('all','6-11',2025,'anx_cur'))} in 2025. The parent series therefore matches the self-report surveys in the report on both ends: a female-led rise through the early 2020s and a downturn in the most recent wave, here between the 2024 and 2025 field periods. Two cautions apply to the last point: the 2025 response rate (34.7%) is the lowest in the series and the field period was extended to March 2026, and a single-year drop in a diagnosis-based item can reflect access to care as well as symptoms.</p>
<h4>The caregiver screen-time gradient</h4>
{ctx.fig_div('nsch_gradient')}
<p class="caption">Pooled 2018–2025, weighted prevalence by the parent's answer to the weekday screen-time item, with 95% intervals. {pct(share4)} of 12–17-year-olds and {pct(share4y)} of 6–11-year-olds are reported at four or more hours.</p>
{t_grad}
<p class="caption">Percentage-point difference between children at 4+ hours and children at 1 hour on most weekdays (the reference category), from weighted linear probability models with single-year age, sex, race/ethnicity, income as a share of the poverty line, highest parental education, and state-by-year fixed effects; heteroskedasticity-robust standard errors in parentheses (one sampled child per household). 2018–2025 pooled.</p>
<p>Unlike the MICS caregivers, U.S. parents report a steep gradient. Girls aged 12–17 whose parents place them at four or more weekday hours are {fm(g18, outcome='anx_cur', sex='girls', agegrp='12-17')} pp more likely to be reported with current anxiety and {fm(g18, outcome='dep_cur', sex='girls', agegrp='12-17')} pp more likely with current depression than girls at one hour, against means of {pct(gr('anx_cur','all','12-17')['mean'])} and {pct(gr('dep_cur','all','12-17')['mean'])}; for boys the differences are {fm(g18, outcome='anx_cur', sex='boys', agegrp='12-17')} and {fm(g18, outcome='dep_cur', sex='boys', agegrp='12-17')} pp. The covariates and state-by-year effects remove little of the raw gap ({f(raw4.coef, raw4.se)} pp for girls' anxiety with year effects only). The gradient is roughly linear from one hour upward and is absent or reversed below one hour, as in the published NSCH analyses.{comp} Three features argue against reading the U.S. gradient as a phone effect on its own. It is present at ages 6–11 ({fm(g18, outcome='anx_cur', sex='girls', agegrp='6-11')} pp for girls' anxiety), where phone ownership is uncommon and the item mostly captures television and games. It is as large or larger for the contrast outcomes that no phone account predicts: current ADD/ADHD is {fm(g18, outcome='adhd_cur', sex='boys', agegrp='12-17')} pp higher for boys and behavior or conduct problems {fm(g18, outcome='beh_cur', sex='boys', agegrp='6-11')} pp higher for 6–11-year-old boys at 4+ hours, a pattern consistent with children who already have a condition spending more time on screens, or with parents who worry about a child also counting their hours more. And it barely changed across the periods when adolescent screen time jumped and then receded:</p>
{t_per}
<p class="caption">Linear slope in percentage points per reported weekday hour (categories coded 0.5, 1, 2, 3 and 4.5 hours), same specification as above. The 2016–17 column sums the separate TV and device items of those years (0 to 9 hours), so its scale is not identical.</p>
<h4>Sleep and bullying as pathways</h4>
{t_med}
<p class="caption">The 4+ hour coefficient on anxiety and depression (ages 12–17, 2018–2025) before and after adding weeknight sleep below 8 hours and bullying victimization (monthly or more, weekly or more) as controls; attenuation is the share of the base coefficient removed.</p>
<p>Parents who report heavy screen use also report less sleep and more bullying: four or more weekday hours is associated with {f(sl_g.coef, sl_g.se)} pp more girls and {f(sl_b.coef, sl_b.se)} pp more boys sleeping under eight hours, and with {f(bu_g.coef, bu_g.se)} pp (girls) and {f(bu_b.coef, bu_b.se)} pp (boys) more being bullied at least monthly. Both predict current anxiety strongly in the same models (short sleep {f(dir_sl.coef, dir_sl.se)} pp, monthly bullying {f(dir_bu.coef, dir_bu.se)} pp for girls), but adding them removes only {a_anx_g:.0f}% of the girls' 4+ hour anxiety gradient ({f(b_anx_g.coef, b_anx_g.se)} to {f(m_anx_g.coef, m_anx_g.se)}) and {a_dep_g:.0f}% of the depression gradient. Most of the cross-sectional association runs through neither sleep nor bullying as the NSCH measures them; the Leung and Torres (2021) finding below that sleep does not mediate the 2018 gradient holds in the pooled years.</p>
<h4>State smartphone adoption</h4>
{t_ad}
<p class="caption">Percentage points of the parent-reported outcome per 10-point rise in the NTIA share of persons in teen households who use a smartphone for internet access (CPS supplements, November 2017, 2019, 2021 and 2023, interpolated between waves), on state-by-year cells 2017–2023 with state and year fixed effects, weighted by cell size, standard errors clustered by state (51 jurisdictions).</p>
<p>By the time the NSCH begins, teen-household smartphone use had already reached {sdrow.loc[2017, 'smart_mean']:.0f}% nationally with a cross-state standard deviation of {sdrow.loc[2017, 'smart_sd']:.1f} points, and it moved to {sdrow.loc[2023, 'smart_mean']:.0f}% (SD {sdrow.loc[2023, 'smart_sd']:.1f}) by 2023. The within-state changes left are small and noisy, and the coefficients are correspondingly unstable: {f(ad('anx_cur','girls').coef_per10pp, ad('anx_cur','girls').se)} pp per 10 points for girls' anxiety and {f(ad('dep_cur','girls').coef_per10pp, ad('dep_cur','girls').se)} pp for depression at ages 12–17, with similar-sized estimates at ages 6–11. This is the saturation problem anticipated in the adoption section: after 2017 the NTIA series has no adoption transition left to exploit, so the NSCH cannot repeat the 2011–2019 YRBS test and these rows should be read as a null-variation result rather than a null effect.</p>
<h4>The first statewide school phone bans: a first look</h4>
{ctx.fig_div('nsch_bans')}
<p class="caption">Left: weighted share of 12–17-year-olds with parent-reported current anxiety in Florida (HB 379, instructional-time ban from the 2023–24 school year; shaded) and in all other states, with 95% intervals for Florida. Right: event-study coefficients from the individual-level model (ages 12–17, covariates, state and year fixed effects, standard errors clustered by state), relative to the year before each mandate's first school year; treated states are Florida (2023–24), Indiana, Louisiana and South Carolina (2024–25) and the {nst_full - 4 if nst_full > 4 else 0} states whose mandates took effect in 2025–26 and are observed only at event time 0.</p>
{t_ban}
<p class="caption">Difference-in-differences coefficients (pp) from weighted individual-level models with covariates, state and year fixed effects, and state-clustered standard errors. "In force, full year" = survey years after the mandate's first school year; "took effect during field period" = the survey year whose June–winter field period straddles the mandate's start. States that only require districts to adopt a policy (Minnesota 2024–25; Alaska, Arizona, Idaho and New Mexico 2025–26) carry a separate indicator. The Florida-only columns come from the state-year panel with the other mandate states dropped once treated; because one treated state leaves no valid cluster-robust standard error, the figure in parentheses is the standard deviation of the same coefficient across the {int(FP0.n_placebo_states.iloc[0])} states without any mandate when each is treated alone from 2023–24. Ages 6–11 are also covered by the bans but rarely carry phones.</p>
{t_ev}
<p class="caption">Event-study coefficients (pp) with the year before the first school year as the reference; "≤ −4" pools all earlier years. The "0" row is identified by {nst_full} states, "+1" by Florida, Indiana, Louisiana and South Carolina, and "+2" by Florida alone.</p>
<p>Florida's parent-reported anxiety among 12–17-year-old girls was {pct(flv('Florida','girls',2022))} in 2022 and {pct(flv('Florida','girls',2023))} in 2023 against {pct(flv('Other states','girls',2022))} and {pct(flv('Other states','girls',2023))} elsewhere, then {pct(flv('Florida','girls',2024))} and {pct(flv('Florida','girls',2025))} in the two full post-ban years against {pct(flv('Other states','girls',2024))} and {pct(flv('Other states','girls',2025))} in other states. The Florida series rests on roughly 100–190 girls a year, so its year-to-year swings of five to ten points are mostly noise. In the pooled, population-weighted individual model a mandate in force for a full school year is associated with {f(bd(ind,'anx_cur','girls','post_full').coef, bd(ind,'anx_cur','girls','post_full').se)} pp on girls' current anxiety and {f(bd(ind,'dep_cur','girls','post_full').coef, bd(ind,'dep_cur','girls','post_full').se)} pp on depression, and with {f(bd(ind,'anx_cur','boys','post_full').coef, bd(ind,'anx_cur','boys','post_full').se)} and {f(bd(ind,'dep_cur','boys','post_full').coef, bd(ind,'dep_cur','boys','post_full').se)} pp for boys; with each treated state counted once (the state-year panel) the girls' anxiety estimate shrinks to {f(bd(pan,'anx_cur','girls','post_full').coef, bd(pan,'anx_cur','girls','post_full').se)} pp while the boys' is {f(bd(pan,'anx_cur','boys','post_full').coef, bd(pan,'anx_cur','boys','post_full').se)} pp, so the answer depends on whether Florida, Texas and New York are weighted by population. The placebo leads are small ({f(ev('girls','ev_m2').coef, ev('girls','ev_m2').se)} and {f(ev('girls','ev_m3').coef, ev('girls','ev_m3').se)} pp for girls at −2 and −3), and the 6–11 comparison group moves the other way ({f(bd(ind,'anx_cur','all','post_full','6-11').coef, bd(ind,'anx_cur','all','post_full','6-11').se)} pp).</p>
{t_perm}
<p class="caption">State-year difference-in-differences (ages 12–17 unless noted; state and year fixed effects) with two weightings, and permutation inference: the observed mandate schedule (one state from 2023–24, three from 2024–25, the rest from 2025–26) is reassigned to random states {nperm} times; "permutation SD" is the standard deviation of the placebo coefficients and "permutation p" the share of placebo draws at least as large in absolute value as the observed one.</p>
<p>Two checks argue against reading these declines as a ban effect. First, the ADD/ADHD contrast moves as much as anxiety: {f(pm('adhd_cur','girls','cell n').coef_full, pm('adhd_cur','girls','cell n').se_cluster_full)} pp for girls with equal state weights (permutation p {pm('adhd_cur','girls','cell n').perm_p_full:.2f}) and {f(pm('adhd_cur','girls','population (sum of FWC)').coef_full, pm('adhd_cur','girls','population (sum of FWC)').se_cluster_full)} pp with population weights, whereas depression, the other internalizing outcome, is {f(pm('dep_cur','girls','cell n').coef_full, pm('dep_cur','girls','cell n').se_cluster_full)} and {f(pm('dep_cur','girls','population (sum of FWC)').coef_full, pm('dep_cur','girls','population (sum of FWC)').se_cluster_full)} pp. Whatever lowered parent-reported anxiety diagnoses in the early-ban states in 2024–25 lowered reported ADHD diagnoses by about as much, which a phone ban does not predict. Second, the only state observed two years after its mandate is Florida, whose full-year coefficient of {f"{fpg.coef_full:+.2f}"} pp for girls' anxiety is {"lower than the placebo coefficient of every one of" if int(fpg.states_below_full) == 0 else f"lower than those of all but {int(fpg.states_below_full)} of"} the {int(fpg.n_placebo_states)} states without any mandate when each is treated alone from 2023–24 (placebo SD {fpg.placebo_sd_full:.2f}, two-sided p {fpg.placebo_p_full:.2f}); for boys the Florida coefficient is {f"{fpb.coef_full:+.2f}"} (p {fpb.placebo_p_full:.2f}), and for girls' ADHD it is {f"{fpa.coef_full:+.2f}"} (p {fpa.placebo_p_full:.2f}), again lower than every placebo state. Florida's post-2023 decline is therefore unusual, but it is a decline in reported diagnoses of every kind. With one state identifying the second post-ban year, four the first, and 2025 the year the national series turned down everywhere, this is a first look rather than an evaluation: it finds no ban-specific signal, and the design will sharpen as the 2026 and 2027 files add full post-ban years for the 19 states that started in 2025–26.</p>
<h4>Published NSCH analyses</h4>
{t_lit}
<div class="note"><strong>Assessment.</strong> The NSCH shows that U.S. caregivers do report a steep screen-time gradient in diagnosed, current anxiety and depression, larger for girls and at least as large as the adolescents' own GSHS gradient, so the MICS null is not a general property of caregiver reports; it is specific to asking caregivers how often a child <em>seems</em> anxious in settings where phone use is measured for the household rather than the child. But the U.S. gradient is equally present at ages 6–11, for ADHD and conduct problems, and before and after the pandemic screen-time surge, which points to selection and reverse causation as much as to H1. The parent series reproduces the female-led 2016–2024 rise and, in 2025, the first decline, placing a national parent-report marker beside the post-2021 state-survey downturn documented in the state youth surveys. The adoption test has no variation left to use (H1 untestable here). The phone-ban difference-in-differences (H1/H3) shows lower parent-reported anxiety in the early-ban states after their mandates, but the decline is matched by ADD/ADHD, absent for depression, sensitive to weighting, and identified two years out by Florida alone; it is not evidence of a ban effect and should be re-run when the 2026 NSCH file is released.</div>"""
    return {"nsch": html}
