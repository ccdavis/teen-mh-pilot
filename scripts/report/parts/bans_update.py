"""Post-2021 waves and the first post-ban observations: county-mean sadness by state through the newest waves (PA 2025, CA 2021-23),
the 2025 YRBS statewide-mandate DiD with its placebo and event study, and the timing of each state's downturn against its mandate."""
def build(ctx):
    pd, np, go = ctx.pd, ctx.np, ctx.go
    TR = pd.read_csv(ctx.T/"state_survey_trends.csv"); D = pd.read_csv(ctx.T/"yrbs25_ban_did.csv"); EV = pd.read_csv(ctx.T/"yrbs25_ban_event.csv")
    M = pd.read_csv(ctx.T/"yrbs25_ban_means.csv"); N = pd.read_csv(ctx.T/"yrbs25_national_trend.csv"); S = pd.read_csv(ctx.T/"yrbs25_ban_states.csv")
    B = pd.read_csv(ctx.ROOT/"data/compiled/phone_bans/state_phone_bans.csv")
    PC = {"California": "CA", "Illinois": "IL", "Maine": "ME", "Minnesota": "MN", "Pennsylvania": "PA", "Washington": "WA"}
    NAME = {"CA": "California", "IL": "Illinois", "ME": "Maine", "PA": "Pennsylvania", "WA": "Washington", "MN": "Minnesota"}
    sad = TR[TR.item == "sad_hopeless"].copy()
    # --- chart: county-mean sadness by state, all waves
    fig = go.Figure(); order = ["WA", "ME", "IL", "PA", "CA"]
    for i, st in enumerate(order):
        d = sad[sad.state == st].sort_values("year")
        if d.empty: continue
        fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines+markers", name=NAME[st], line=dict(color=ctx.PAL[i], width=2), marker=dict(size=7),
                                 hovertemplate="%{y:.1f}%<extra>" + NAME[st] + "</extra>"))
    nat = N[(N.item == "sad") & (N.sexlab == "all") & (N.year >= 2009)].sort_values("year")
    fig.add_trace(go.Scatter(x=nat.year, y=nat.pct, mode="lines", name="YRBS national", line=dict(color=ctx.MUTED, width=2, dash="dot"), hovertemplate="%{y:.1f}%<extra>YRBS national</extra>"))
    ctx.covid_band(fig)
    # mandate markers: first school year a statewide mandate is in force (fall of the first year) for the states on the chart
    k = 0
    for st in order:
        row = B[B.state == NAME[st]]
        if len(row) and isinstance(row.effective_school_year.iloc[0], str):
            y0 = int(row.effective_school_year.iloc[0][:4]) + 0.5
            fig.add_vline(x=y0, line=dict(color=ctx.PAL[order.index(st)], width=1, dash="dash"), opacity=0.6)
            fig.add_annotation(x=y0, y=0.98 - 0.07 * k, yref="paper", text=f"{st} mandate {row.effective_school_year.iloc[0]}", showarrow=False, font=dict(size=10, color=ctx.PAL[order.index(st)]), xanchor="right", yanchor="top"); k += 1
    ctx.figs["bans_update_state_trends"] = ctx.base(fig, h=400, yaxis_title="% sad or hopeless (2+ weeks, past 12 months)", xaxis=dict(dtick=2))
    # --- numbers for the prose
    def v(st, yr):
        x = sad[(sad.state == st) & (sad.year == yr)].value
        return float(x.iloc[0]) if len(x) else np.nan
    def last_two(st):
        d = sad[sad.state == st].sort_values("year"); return int(d.year.iloc[-2]), float(d.value.iloc[-2]), int(d.year.iloc[-1]), float(d.value.iloc[-1])
    peak = {st: (int(sad[sad.state == st].sort_values("value").year.iloc[-1]), float(sad[sad.state == st].value.max())) for st in order if (sad.state == st).any()}
    pa21, pa23, pa25 = v("PA", 2021), v("PA", 2023), v("PA", 2025); ca19, ca21, ca23 = v("CA", 2019), v("CA", 2021), v("CA", 2023)
    ca25 = v("CA", 2025); wa21, wa25 = v("WA", 2021), v("WA", 2025); il22, il24 = v("IL", 2022), v("IL", 2024); me21, me23 = v("ME", 2021), v("ME", 2023)
    cs = TR[TR.item == "considered_suicide"]
    def cv(st, yr):
        x = cs[(cs.state == st) & (cs.year == yr)].value; return float(x.iloc[0]) if len(x) else np.nan
    # mandate timing vs downturn: first post-peak wave vs first school year with a mandate in force
    rows = []
    for st in order:
        d = sad[sad.state == st].sort_values("year"); pk = peak[st][0]; after = d[d.year > pk]
        first_down = int(after.year.iloc[0]) if len(after) else None
        row = B[B.state == NAME[st]].iloc[0]; eff = row.effective_school_year if isinstance(row.effective_school_year, str) else "none"
        rows.append([NAME[st], f"{pk} ({peak[st][1]:.1f}%)", f"{first_down} ({float(after.value.iloc[0]):.1f}%)" if first_down else "no later wave",
                     f"{d.year.iloc[-1]} ({d.value.iloc[-1]:.1f}%)", row.policy_type, eff,
                     "before the mandate" if first_down and (eff == "none" or first_down <= int(eff[:4])) else ("after" if first_down else "-")])
    timing_tbl = ctx.table(["State (county survey)", "Peak wave", "First wave below the peak", "Newest wave", "Statewide policy (2026-09)", "In force from", "Downturn relative to mandate"], rows)
    # --- DiD table
    LAB = {"sad": "Sad or hopeless", "consider": "Considered suicide", "attempt": "Attempted suicide", "socmed": "Social media several times a day+"}
    def cell(item, sex, design):
        r = D[(D.item == item) & (D.sex == sex) & (D.design == design)]
        if r.empty: return "-"
        r = r.iloc[0]; return f"{ctx.fmt(r.coef, r.se_cluster)} [{r.p_ri:.2f}]"
    def tinfo(item, design):
        r = D[(D.item == item) & (D.sex == "all") & (D.design == design)]
        return (int(r.treated_states.iloc[0]), int(r.control_states.iloc[0]), int(r.n_state_years.iloc[0])) if len(r) else (0, 0, 0)
    did_rows = []
    for item in ["sad", "consider", "attempt", "socmed"]:
        for sex in ["all", "girls", "boys"]:
            t, c, n = tinfo(item, "main"); tp, cp, npl = tinfo(item, "placebo_pre")
            did_rows.append([LAB[item] if sex == "all" else "", sex, cell(item, sex, "main"), cell(item, sex, "main_clean_controls"), cell(item, sex, "placebo_pre"),
                             f"{t} / {c}" + (f"; placebo {tp} / {cp}" if tp else "")])
    did_tbl = ctx.table(["Outcome", "Sex", "DiD 2021-23 vs 2025 (SE) [RI p]", "Clean controls only", "Placebo: 2017-19 vs 2021-23", "Treated / control states"], did_rows)
    r_all = D[(D.item == "sad") & (D.sex == "all") & (D.design == "main")].iloc[0]; r_cl = D[(D.item == "sad") & (D.sex == "all") & (D.design == "main_clean_controls")].iloc[0]
    r_pl = D[(D.item == "sad") & (D.sex == "all") & (D.design == "placebo_pre")].iloc[0]
    r_g = D[(D.item == "sad") & (D.sex == "girls") & (D.design == "main")].iloc[0]; r_b = D[(D.item == "sad") & (D.sex == "boys") & (D.design == "main")].iloc[0]
    r_c = D[(D.item == "consider") & (D.sex == "all") & (D.design == "main")].iloc[0]; r_cpl = D[(D.item == "consider") & (D.sex == "all") & (D.design == "placebo_pre")].iloc[0]
    r_s = D[(D.item == "socmed") & (D.sex == "all") & (D.design == "main")].iloc[0]
    ev = EV[(EV.item == "sad") & (EV.sex == "all")].set_index("year")
    ms = M[(M.item == "sad") & (M.sex == "all")].pivot_table(index="year", columns="group", values="mean_pct")
    treated = S[S.group == "treated"]; ctrl_n = int((S.group != "treated").sum()); clean_n = int((S.group == "control").sum())
    nat_s = N[(N.item == "sad") & (N.sexlab == "all")].set_index("year").pct; nat_g = N[(N.item == "sad") & (N.sexlab == "girls")].set_index("year").pct; nat_b = N[(N.item == "sad") & (N.sexlab == "boys")].set_index("year").pct
    nat_c = N[(N.item == "consider") & (N.sexlab == "all")].set_index("year").pct; nat_sm = N[(N.item == "socmed") & (N.sexlab == "all")].set_index("year").pct
    # --- event-study chart
    fig2 = go.Figure()
    for sex, col in [("all", ctx.ALL), ("girls", ctx.GIRL), ("boys", ctx.BOY)]:
        e = EV[(EV.item == "sad") & (EV.sex == sex)].sort_values("year"); e = pd.concat([e, pd.DataFrame([dict(year=2021, coef=0.0, se=0.0)])]).sort_values("year")
        fig2.add_trace(go.Scatter(x=e.year + {"all": 0, "girls": -0.15, "boys": 0.15}[sex], y=e.coef, mode="markers+lines", name={"all": "All students", "girls": "Girls", "boys": "Boys"}[sex],
                                  line=dict(color=col, width=2), marker=dict(size=8), error_y=dict(type="data", array=1.96 * e.se, visible=True, thickness=1),
                                  hovertemplate="%{y:+.1f} pp<extra>" + sex + "</extra>"))
    fig2.add_hline(y=0, line=dict(color=ctx.MUTED, width=1)); fig2.add_vline(x=2024.5, line=dict(color=ctx.MUTED, width=1, dash="dash"))
    fig2.add_annotation(x=2024.5, y=1.0, yref="paper", text="mandates in force (IN, LA, SC)", showarrow=False, font=dict(size=10, color=ctx.MUTED), xanchor="right", yanchor="bottom")
    ctx.figs["bans_update_event"] = ctx.base(fig2, h=360, yaxis_title="Treated minus control, pp (ref. 2021)", xaxis=dict(dtick=2))
    pa_note = ("" if np.isnan(pa25) else f" Pennsylvania's 2025 wave (fall 2025, no statewide mandate; the state funded lockable pouches) continues the 2021 to 2023 decline: county-mean sadness {pa21:.1f}% (2021), {pa23:.1f}% (2023), {pa25:.1f}% (2025), and considered suicide {cv('PA', 2021):.1f}%, {cv('PA', 2023):.1f}%, {cv('PA', 2025):.1f}%.")
    ca_note = ("" if np.isnan(ca23) else f" California's county reports for 2019-21 and 2021-23 (a mandate applies only from 2026-27) put county-mean sadness at {ca19:.1f}% (2017-19), {ca21:.1f}% (2019-21) and {ca23:.1f}% (2021-23)" + ("" if np.isnan(ca25) else f", falling to {ca25:.1f}% in 2023-25") + ".")
    html = f"""<h3 id="bans-update">Post-2021 waves and the first post-ban observations</h3>
<p>Phase 1 ended with the observation that the post-2021 waves of the state youth surveys showed a broad decline in sadness that began
before any statewide phone mandate. Two new county waves and the 2025 YRBS state files now extend that record. Pennsylvania's 2025
county profile reports (60 counties) and California's CalSCHLS county reports for 2019-21 and 2021-23 (and 2023-25 where posted) were
added to the county panel; the CDC released the 2025 combined YRBS state files on 21 September 2026, which allows the pre-specified
difference-in-differences for the first statewide mandates (Indiana's instructional-time ban and Louisiana's and South Carolina's
bell-to-bell bans, all in force in 2024-25). Minnesota's 2022 and 2025 county tables remain behind a bot-manager CAPTCHA
(<code>notes/state_surveys.md</code>), and Florida, the earliest mandate state, left the YRBS after 2021.</p>
<h4>County-mean sadness through the newest waves</h4>
{ctx.fig_div('bans_update_state_trends')}
<p class="caption">Unweighted county means of the share of students sad or hopeless for two or more weeks, over the grades each state reports in every wave (as in Part 1), with the national YRBS for comparison (dotted). Dashed verticals mark the first school year a statewide mandate is in force (Maine 2026-27; California district-policy mandate 2026-27; Illinois 2027-28); Washington has guidance only and Pennsylvania no mandate. Grey band: 2020.</p>
<p>Every state with a post-2021 wave has now turned down, and in every case the first wave below the peak precedes the state's mandate or
the state has none.{pa_note}{ca_note} Washington fell from {wa21:.1f}% (2021) to {wa25:.1f}% (2025) under guidance only, Illinois from {il22:.1f}% (2022) to {il24:.1f}% (2024) three
years before its 2027-28 ban, and Maine was flat between 2021 ({me21:.1f}%) and 2023 ({me23:.1f}%) before its 2026-27 ban. Nationally the YRBS
shows {nat_s[2021]:.1f}% (2021), {nat_s[2023]:.1f}% (2023) and {nat_s[2025]:.1f}% (2025) sad or hopeless (girls {nat_g[2021]:.1f} to {nat_g[2025]:.1f}%, boys {nat_b[2021]:.1f} to {nat_b[2025]:.1f}%),
considered suicide {nat_c[2021]:.1f}% to {nat_c[2025]:.1f}%, while the share using social media several times a day or more rose from {nat_sm[2023]:.1f}% to {nat_sm[2025]:.1f}%.</p>
{timing_tbl}
<p class="caption">Peak and first post-peak wave of county-mean sadness in each state survey against the first school year with a statewide mandate in force (<code>data/compiled/phone_bans/state_phone_bans.csv</code>, status September 2026).</p>
<h4>2025 YRBS: states with a mandate in force in 2024-25 against states without one</h4>
<p>Treated: {", ".join(f"{r.state} ({r.policy_type.replace('statewide ', '')}, {r.effective_school_year})" for r in treated.itertuples())}. Controls: the {ctrl_n} other states in the 2025 YRBS state files with no mandate in force before 2025-26; the "clean" subset ({clean_n} states) also excludes states that enacted a law before the end of the spring-2025 fieldwork. State-year cells are weighted equally with state and year fixed effects; standard errors are clustered by state, and because only three states are treated the bracketed p-value comes from randomization inference over every possible assignment of three treated states. The placebo repeats the design on 2017-2023 with 2021-23 as a false post period. Florida and Minnesota, the other two 2024-25 mandate states, have no 2025 YRBS data, and item coverage differs across the treated states (South Carolina asked no suicide items in 2021 and has no 2023 wave; Indiana has no 2025 attempt item), so the considered-suicide rows rest on two states and the attempt row on Louisiana alone.</p>
{did_tbl}
<p class="caption">Percentage-point difference-in-differences from <code>results/tables/yrbs25_ban_did.csv</code>; weighted state estimates from the 2023 and 2025 combined YRBS files. The social-media item (several times a day or more) exists only for 2023 and 2025, so it has no placebo. Treated/control counts are the states observed both before and after.</p>
{ctx.fig_div('bans_update_event')}
<p class="caption">Event study for sad or hopeless: treated-minus-control difference by wave relative to 2021 (state and year fixed effects, 95% intervals from state-clustered SEs; 2015-2025, 3 treated and {int(ev.control_states.iloc[0])} control states).</p>
<p>Sadness fell by {ms.loc[2025, 'treated'] - ms.loc[2023, 'treated']:+.1f} points in the treated states between 2023 and 2025 (from {ms.loc[2021, 'treated']:.1f}% in 2021 and {ms.loc[2023, 'treated']:.1f}% in 2023 to {ms.loc[2025, 'treated']:.1f}%) against {ms.loc[2025, 'control'] - ms.loc[2023, 'control']:+.1f} points in the clean controls ({ms.loc[2023, 'control']:.1f}% to {ms.loc[2025, 'control']:.1f}%). The difference-in-differences is {ctx.fmt(r_all.coef, r_all.se_cluster)} points (randomization p = {r_all.p_ri:.2f}; {ctx.fmt(r_cl.coef, r_cl.se_cluster)} with clean controls), larger for boys ({ctx.fmt(r_b.coef, r_b.se_cluster)}) than for girls ({ctx.fmt(r_g.coef, r_g.se_cluster)}), and the sadness placebo on 2017-2023 is {ctx.fmt(r_pl.coef, r_pl.se_cluster)} (p = {r_pl.p_ri:.2f}). Two features argue against reading this as a ban effect yet. First, the treated states had the larger 2019-2021 rise: in the event study their 2017 and 2019 levels sit {-ev.loc[2017, 'coef']:.1f} and {-ev.loc[2019, 'coef']:.1f} points further below 2021 than the controls', so part of the 2025 gap ({ev.loc[2025, 'coef']:+.1f}, SE {ev.loc[2025, 'se']:.1f}) is reversion from a higher peak; measured against 2019 rather than 2021 the differential fall is about {ev.loc[2025, 'coef'] - ev.loc[2019, 'coef']:+.1f} points. Second, considered suicide was already falling faster in Indiana and Louisiana before any mandate (placebo {ctx.fmt(r_cpl.coef, r_cpl.se_cluster)}), so its 2025 estimate ({ctx.fmt(r_c.coef, r_c.se_cluster)}) carries no information about the bans. The mechanism check also fails in the direction opposite to a first stage: daily-plus social-media use rose {ctx.fmt(r_s.coef, r_s.se_cluster)} points more in Indiana and Louisiana than in the controls between 2023 and 2025. The item measures overall frequency rather than use at school, so this is consistent with the English and PISA findings that school bans leave total use unchanged, but it means the YRBS cannot show that in-school exposure fell.</p>
<h5>What has been published on the 2025 waves</h5>
<p>CDC's 2025 release (<a href="https://www.cdc.gov/yrbs/youth-health-in-focus/index.html">Youth Health in Focus</a>, 21 September 2026) reports the national fall in persistent sadness from 40% to 33% and in suicidal ideation from 20% to 14% between 2023 and 2025, with social-media use "every hour or more" unchanged at 36-37%; the accompanying MMWR supplement (<a href="https://dx.doi.org/10.15585/mmwr.su7501a4">Kiplagat et al. 2026</a>) gives {nat_s[2025]:.1f}% overall, {nat_g[2025]:.1f}% for girls and {nat_b[2025]:.1f}% for boys, which the microdata reproduce. State releases describe the same decline in states without a mandate (Vermont 29% to 23%, <a href="https://www.healthvermont.gov/sites/default/files/document/hsi-yrbs-executuve-summary-2025-high-school.pdf">2025 executive summary</a>; North Carolina 29.7% with a "significant" decrease from 2023), and Pennsylvania's commission attributes its improvement to mental-health investment without mentioning phones (<a href="https://www.pa.gov/agencies/pccd/newsroom/new-data-shows-youth-mental-health-is-improving--students-feel-s">PCCD, October 2026</a>). No evaluation of the Florida, Indiana, Louisiana or South Carolina mandates on a mental-health outcome was found as of October 2026: <a href="https://www.nber.org/papers/w34388">Figlio and Özek (2025)</a> cover achievement, discipline and attendance in one Florida district, and the national pouch study (<a href="https://www.nber.org/papers/w35132">Allcott et al. 2026</a>) is the only U.S. quasi-experiment with a well-being outcome. The estimates above are therefore the first state-survey post-ban mental-health numbers, and they should be read with that literature's warning that effects appear in the second post-ban year.</p>
<div class="note"><strong>Assessment.</strong> The newest waves settle the timing question raised in Phase 1: the post-2021 downturn in adolescent sadness is national ({nat_s[2021]:.0f}% to {nat_s[2025]:.0f}% in the YRBS) and, in every county survey with a post-2021 wave, began before the state's phone mandate or in a state without one (Washington, Pennsylvania, Illinois, California, Maine). A broad decline that precedes the policy cannot be attributed to it, which weakens the simplest reading of the Phase 1 "re-restriction" account for H3 and leaves the platform-content and cohort explanations open; it also contradicts a dose model in which sadness tracks total social-media use, which rose nationally while sadness fell (H1). On top of that common decline, the three states with mandates in force in 2024-25 fell a further {abs(r_all.coef):.0f} points in sadness ({ctx.fmt(r_all.coef, r_all.se_cluster)}, randomization p = {r_all.p_ri:.2f}; clean placebo), which is the first state-level post-ban mental-health estimate in U.S. data and points the same way as the Norwegian and Yondr-pouch studies; but with three treated states, a larger 2021 peak in those states, suicidal ideation already trending down before the bans and no first stage on in-school use, it is a lead for the 2027 wave rather than a result. The 2025-26 cohort of fourteen bell-to-bell states and the 2027 YRBS, together with Minnesota's 2025 county tables once released, will give the second post-ban year the ban literature says is needed.</div>"""
    return {"bans_update": html}
