"""Monitoring the Future section: published 12th-grade item trends 1996-2012 (homework, evenings out, friends, TV, sleep, loneliness,
self-derogation, depressive affect, happiness) by sex, the 8th/10th-grade year effects 1991-2014 from Johnson et al. (2017), the
student-level literature table, and the status of the microdata pipeline (31_mtf.py)."""
def build(ctx):
    pd, np, go = ctx.pd, ctx.np, ctx.go; T = ctx.T
    S = pd.read_csv(T/"mtf_published_series.csv"); CH = pd.read_csv(T/"mtf_published_changes.csv"); CM = pd.read_csv(T/"mtf_published_comovement.csv")
    COV = pd.read_csv(T/"mtf_published_coverage.csv"); LIT = pd.read_csv(T/"mtf_literature.csv"); ST = pd.read_csv(T/"mtf_microdata_status.csv"); J = pd.read_csv(T/"mtf_johnson2017_year_effects.csv")
    y0, y1 = int(S.year.min()), int(S.year.max()); n_med = int(COV[COV.forms == 1].n_all_median.median()); n_hap = int(COV.loc[COV.series == "happiness", "n_all_median"].iloc[0])
    def v(ind, sex, year): d = S[(S.indicator == ind) & (S.sex == sex) & (S.year == year)]; return float(d.value.iloc[0]) if len(d) else np.nan
    def ch(ind, sex, col="d_1996_2012"): d = CH[(CH.indicator == ind) & (CH.sex == sex)]; return (float(d[col].iloc[0]), float(d[col.replace("d_", "se_")].iloc[0])) if len(d) else (np.nan, np.nan)
    # ---- chart 1: small multiples by sex
    panels = [("homework_mean_h", "Homework, h/week"), ("evenings_out_mean", "Evenings out / week"), ("friends_daily", "Friends almost daily, %"), ("tv_weekday_mean_h", "TV weekday, h"),
              ("internet_mean_h", "Internet (personal), h/week"), ("sleep7_mostdays", "7+ h sleep most days, %"), ("lonely_agree", "Lonely (agree), %"), ("selfderog_mean", "Self-derogation (agree), %"),
              ("depaffect_mean", "Depressive affect, %"), ("very_happy", "Very happy, %")]
    panels = [p for p in panels if p[0] in set(S.indicator)]; ncol = 5; nrow = int(np.ceil(len(panels) / ncol))
    fig = ctx.make_subplots(rows=nrow, cols=ncol, subplot_titles=[p[1] for p in panels], vertical_spacing=0.16, horizontal_spacing=0.05)
    for i, (ind, lab) in enumerate(panels):
        r, c = i // ncol + 1, i % ncol + 1
        for sx, col, name in [("boys", ctx.BOY, "Boys"), ("girls", ctx.GIRL, "Girls"), ("all", ctx.MUTED, "All")]:
            d = S[(S.indicator == ind) & (S.sex == sx)].sort_values("year")
            fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines+markers", line=dict(color=col, width=2 if sx != "all" else 1.2, dash="solid" if sx != "all" else "dot"), marker=dict(size=4),
                                     error_y=dict(type="data", array=1.96 * d.se, color=col, thickness=0.8, width=0) if sx != "all" else None, name=name, showlegend=(i == 0), hovertemplate="%{x}: %{y:.1f}<extra>" + name + "</extra>"), row=r, col=c)
        fig.update_yaxes(rangemode="tozero", row=r, col=c); fig.update_xaxes(tickvals=[1996, 2004, 2012], row=r, col=c)
    ctx.figs["mtf_trends"] = ctx.base(fig, h=520, hovermode="closest")
    # ---- chart 2: Johnson et al. 2017 year effects (8th/10th graders, ref 2008)
    jp = [("Homework hours (1-7 scale)", "Homework hours"), ("Goes out at night for fun (OR, 1+ evenings/week)", "Evenings out (odds ratio)"), ("Depressed mood", "Depressed mood"), ("Self-esteem", "Self-esteem")]
    fig2 = ctx.make_subplots(rows=1, cols=4, subplot_titles=[t for _, t in jp], horizontal_spacing=0.06)
    for i, (o, t) in enumerate(jp):
        d = J[J.outcome == o].sort_values("year"); ref = 1.0 if "OR" in o else 0.0; dd = d.copy(); dd.loc[dd.year == 2008, "estimate"] = ref
        fig2.add_trace(go.Scatter(x=dd.year, y=dd.estimate, mode="lines+markers", connectgaps=False, line=dict(color=ctx.PAL[i]), marker=dict(size=5), name=t, showlegend=False, hovertemplate="%{x}: %{y:.2f}<extra></extra>"), row=1, col=i + 1)
        ns = dd[(dd.ns == 1) & (dd.year != 2008)]; fig2.add_trace(go.Scatter(x=ns.year, y=[ref] * len(ns), mode="markers", marker=dict(symbol="circle-open", size=6, color=ctx.MUTED), name="not significant (≈ 2008)", showlegend=(i == 0), hovertemplate="%{x}: n.s.<extra></extra>"), row=1, col=i + 1)
        fig2.add_hline(y=ref, line=dict(color=ctx.MUTED, width=1), row=1, col=i + 1)
    ctx.figs["mtf_johnson"] = ctx.base(fig2, h=300, hovermode="closest")
    # ---- tables
    key = [("homework_mean_h", "Homework, hours/week (mean)", 1), ("homework_10plus", "Homework 10+ h/week, %", 1), ("evenings_out_mean", "Evenings out per week (mean)", 2), ("friends_daily", "Friends informally almost daily, %", 1),
           ("dating_weekly", "Dates weekly or more, %", 1), ("tv_weekday_mean_h", "TV on a weekday, hours (mean)", 2), ("internet_mean_h", "Internet for personal use, h/week (mean)", 1), ("works", "Works during the school year, %", 1),
           ("sleep7_mostdays", "7+ hours of sleep most days, %", 1), ("lonely_agree", "Lonely: agree, %", 1), ("left_out_agree", "Often feels left out, %", 1), ("selfderog_mean", "Self-derogation, mean % agree (4 items)", 1),
           ("depaffect_mean", "Depressive affect, mean % (4 items)", 1), ("very_happy", "Very happy, %", 1), ("not_too_happy", "Not too happy, %", 1), ("life_sat_mean", "Life satisfaction, mean (1-7)", 2)]
    key = [k for k in key if k[0] in set(CH.indicator)]
    rows = []
    for ind, lab, d_ in key:
        r = [lab]
        for sx in ["boys", "girls"]:
            c = CH[(CH.indicator == ind) & (CH.sex == sx)].iloc[0]; fy, ly = int(c.first_year), int(c.last_year)
            r += [f"{c.v_first:.{d_}f}" + ("" if fy == y0 else f" ({fy})"), f"{c.v_last:.{d_}f}", ctx.fmt(c.d_1996_2010, c.se_1996_2010, d_) if pd.notna(c.d_1996_2010) else ctx.fmt(c.d_first_last, c.se_first_last, d_) + f" ({fy}–{ly})",
                  ctx.fmt(c.d_2010_2012, c.se_2010_2012, d_) if pd.notna(c.d_2010_2012) else "–"]
        rows.append(r)
    t_changes = ctx.table(["Indicator (12th graders)", f"Boys {y0}", f"Boys {y1}", "Δ 1996→2010", "Δ 2010→2012", f"Girls {y0}", f"Girls {y1}", "Δ 1996→2010", "Δ 2010→2012"], rows)
    cm = CM[(CM.sex == "all") & CM.outcome.isin(["lonely_agree", "selfderog_mean", "depaffect_mean"])]; cm_min, cm_max = float(cm.r_first_differences.min()), float(cm.r_first_differences.max()); exl = {"homework_mean_h": "Homework hours", "evenings_out_mean": "Evenings out", "friends_daily": "Friends almost daily", "tv_weekday_mean_h": "TV hours (weekday)", "sleep7_mostdays": "7+ h sleep most days", "works": "Works", "internet_mean_h": "Internet hours (personal)", "games_mean_h": "Games hours"}; ocl = {"lonely_agree": "loneliness", "selfderog_mean": "self-derogation", "depaffect_mean": "depressive affect"}
    _mn = cm.loc[cm.r_first_differences.idxmin()]; _mx = cm.loc[cm.r_first_differences.idxmax()]; cm_min_pair = f"{exl[_mn.exposure].lower()} with {ocl[_mn.outcome]}"; cm_max_pair = f"{exl[_mx.exposure].lower()} with {ocl[_mx.outcome]}"; exl = {"homework_mean_h": "Homework hours", "evenings_out_mean": "Evenings out", "friends_daily": "Friends almost daily", "tv_weekday_mean_h": "TV hours (weekday)", "sleep7_mostdays": "7+ h sleep most days", "works": "Works", "internet_mean_h": "Internet hours (personal)"}
    cm_rows = []
    for ex in [e for e in exl if e in set(cm.exposure)]:
        r = [exl[ex]]
        for oc in ["lonely_agree", "selfderog_mean", "depaffect_mean"]:
            d = cm[(cm.exposure == ex) & (cm.outcome == oc)]; r.append(f"{d.r_levels.iloc[0]:+.2f} / {d.r_first_differences.iloc[0]:+.2f} ({int(d.years.iloc[0])})" if len(d) else "–")
        cm_rows.append(r)
    t_cm = ctx.table(["Year-level exposure", "Lonely", "Self-derogation", "Depressive affect"], cm_rows)
    lit_rows = [[f'<a href="{r.doi_or_url}">{r.study} ({r.year})</a>', r.mtf_sample, f"{r.exposure} → {r.outcome}", r.estimate, r.relevance] for r in LIT.sort_values(["year", "study"]).itertuples()]
    t_lit = ctx.table(["Study", "Data", "Exposure → outcome", "Estimate (as published)", "Bears on"], lit_rows)
    st = ST.iloc[0]; files_found = int(st.files_found)
    # ---- numbers for the prose
    hw_b, hw_g = ch("homework_mean_h", "boys"), ch("homework_mean_h", "girls"); ev_b, ev_g = ch("evenings_out_mean", "boys"), ch("evenings_out_mean", "girls")
    fr_b, fr_g = ch("friends_daily", "boys"), ch("friends_daily", "girls"); lo_b, lo_g = ch("lonely_agree", "boys"), ch("lonely_agree", "girls"); sd_b, sd_g = ch("selfderog_mean", "boys"), ch("selfderog_mean", "girls")
    da_b, da_g = ch("depaffect_mean", "boys"), ch("depaffect_mean", "girls"); sl_b, sl_g = ch("sleep7_mostdays", "boys"), ch("sleep7_mostdays", "girls"); tv_a = ch("tv_weekday_mean_h", "all")
    lo10_g = ch("lonely_agree", "girls", "d_2010_2012"); sd10_g = ch("selfderog_mean", "girls", "d_2010_2012"); hw10_g = ch("homework_mean_h", "girls", "d_2010_2012"); hw10_b = ch("homework_mean_h", "boys", "d_2010_2012")
    jh = J[(J.outcome == "Homework hours (1-7 scale)")].set_index("year").estimate; jo = J[J.outcome == "Goes out at night for fun (OR, 1+ evenings/week)"].set_index("year").estimate; jd = J[J.outcome == "Depressed mood"].set_index("year").estimate
    kreski = LIT[LIT.study.str.startswith("Kreski, Platt")].iloc[0]; twenge18 = LIT[LIT.study.str.startswith("Twenge, Joiner")].iloc[0]; keyes19 = LIT[LIT.study.str.startswith("Keyes, Gary")].iloc[0]
    html = f"""<h3 id="mtf">Monitoring the Future: homework, socializing, screens and distress among 12th graders, {y0}–{y1}, and the student-level test that still needs the microdata</h3>
<p>Monitoring the Future (MTF) is the one U.S. survey that has asked the same adolescents about homework hours, evenings out, time with friends, screen use and
a stable set of distress items every year since 1991, and it is the source behind most of the Twenge-side correlational evidence. Its public-use microdata
(ICPSR/NAHDAP series 35, grades 8, 10 and 12) could not be obtained from this machine: icpsr.umich.edu answers a Cloudflare bot challenge (HTTP 403) to every
non-interactive client tried, and downloads in any case require an ICPSR login with terms acceptance. We therefore use what MTF itself published: the annual
<em>Questionnaire Responses from the Nation's High School Seniors</em> volumes, which print every item's weighted percentage distribution by sex, race, region and
college plans. The volumes for the {y0}–{y1} surveys are the only ones ever posted as PDFs (the series ended with the 2012 volume) and were recovered from Internet
Archive captures; each item is answered by one random sixth of the national sample (about {n_med:,} weighted cases for a single-form item, {n_hap:,} for items on every form).
The 17 volumes were parsed into {len(COV)} item series and pooled across forms weighting by the N answering. Standard errors use a design effect of 2, the midpoint
of the volumes' own guidance.</p>
{ctx.fig_div('mtf_trends')}
<p class="caption">MTF 12th graders, {y0}–{y1}, by sex (boys blue, girls orange, all dotted), with approximate 95% intervals. Homework and TV are means of
category midpoints; the self-derogation and depressive-affect panels average the share endorsing the negative pole over four items each ("I feel I do not have much to
be proud of", "Sometimes I think that I am no good at all", "I feel that I can't do anything right", "I feel that my life is not very useful"; "Life often seems
meaningless", "The future often seems hopeless", disagree "I enjoy life as much as anyone", disagree "It feels good to be alive").</p>
<h4>What moved before 2012, and what did not</h4>
<p>Over {y0}–{y1}, 12th graders' self-reported homework fell by roughly an hour a week (boys {ctx.fmt(*hw_b)} hours, girls {ctx.fmt(*hw_g)}, from
{v('homework_mean_h','all',y0):.1f} to {v('homework_mean_h','all',y1):.1f} hours for all students), so the MTF record does not show the rise in homework load that
ATUS shows for school weekdays after 2003; MTF's weekly self-report is a different quantity from a diary, but Twenge and Park (2019) and Twenge, Spitzberg and
Campbell (2019) read the same series as flat or declining back to 1976. In-person socializing, by contrast, fell steadily and well before smartphones:
evenings out per week {ctx.fmt(*ev_b)} for boys and {ctx.fmt(*ev_g)} for girls, and the share getting together with friends informally almost every day
{ctx.fmt(*fr_b)} and {ctx.fmt(*fr_g)} percentage points. Weekday television was flat ({ctx.fmt(*tv_a)} hours, all students), and the share getting seven or more hours of sleep most days
rose by {ctx.fmt(*sl_b)} points for boys and {ctx.fmt(*sl_g)} for girls. Screen time did rise before the distress turn: personal internet use went from {v('internet_mean_h','all',int(S[S.indicator=='internet_mean_h'].year.min())):.1f} to
{v('internet_mean_h','all',y1):.1f} hours a week between {int(S[S.indicator=='internet_mean_h'].year.min())} and {y1}, daily social-networking from
{v('sns_daily','all',int(S[S.indicator=='sns_daily'].year.min())):.0f}% to {v('sns_daily','all',y1):.0f}% ({int(S[S.indicator=='sns_daily'].year.min())}–{y1}; girls
{v('sns_daily','girls',y1):.0f}%), and electronic games from {v('games_mean_h','all',int(S[S.indicator=='games_mean_h'].year.min())):.1f} to {v('games_mean_h','all',y1):.1f} hours a week.
The distress items were, over the same sixteen years, essentially stable or improving:
loneliness {ctx.fmt(*lo_b)} points for boys and {ctx.fmt(*lo_g)} for girls, self-derogation {ctx.fmt(*sd_b)} and {ctx.fmt(*sd_g)}, depressive affect
{ctx.fmt(*da_b)} and {ctx.fmt(*da_g)}. The last two volumes catch at most the start of the post-2011 turn: between 2010 and 2012 girls' self-derogation rose
{ctx.fmt(*sd10_g)} points while their loneliness did not move ({ctx.fmt(*lo10_g)}), and homework hours moved {ctx.fmt(*hw10_g)} (girls) and {ctx.fmt(*hw10_b)} (boys).</p>
{t_changes}
<p class="caption">Levels in {y0} and {y1} and changes with approximate SEs (design effect 2). Pooled across questionnaire forms; loneliness and the left-out item are on one form
(n ≈ {int(COV.loc[COV.series=='lonely','n_all_median'].iloc[0]):,}), happiness on all six.</p>
<p>At the year level the series that declined together over {y0}–{y1} (friends, evenings out, homework, loneliness, depressive affect) are positively
correlated in levels, which is shared trend rather than evidence of anything; in first differences the correlations of the exposures with loneliness,
self-derogation and depressive affect run from {cm_min:+.2f} ({cm_min_pair}) to {cm_max:+.2f} ({cm_max_pair}) over seventeen points, with nothing in between that
survives the number of pairs tried. Table: Pearson r in levels / in first differences (years).</p>
{t_cm}
<p class="caption">Year-level co-movement of 12th-grade means, all students. Seventeen annual points; these are descriptive, not estimates of an effect.</p>
<h4>8th and 10th graders, 1991–2014, from a published table</h4>
<p>The one tabular annual series that reaches past 2012 is Johnson, Staff, Patrick and Schulenberg's (2017) Table 1, which regresses each MTF 8th/10th-grade
indicator on survey-year dummies with 2008 as reference. Homework hours fall monotonically from {jh.get(1991):+.2f} scale points above 2008 in 1991 to
{jh.get(2014):+.2f} in 2014 (the authors put the 2014 level under five hours a week); the odds of going out at least one evening a week fall from {jo.get(1991):.2f}
times the 2008 level in 1991 to {jo.get(2014):.2f} in 2014; depressed mood is {jd.get(1991):+.2f} points above 2008 in 1991, indistinguishable from 2008 through 2012,
and {jd.get(2014):+.2f} in 2014.</p>
{ctx.fig_div('mtf_johnson')}
<p class="caption">Johnson et al. (2017), Int J Psychol, Table 1: year coefficients (OLS) or odds ratios (logit) relative to 2008, MTF 8th and 10th graders pooled; open markers
are years the authors report as not significantly different from 2008 (no point estimate given). Compiled in <code>data/compiled/mtf/mtf_johnson2017_year_effects.csv</code>.</p>
<h4>What the student-level MTF literature already answers</h4>
<p>Published analyses of the microdata cover the main effects but not the H3 interaction. On the phone side, {twenge18.study} ({twenge18.year}) report that high-school students
using electronic devices five or more hours a day (YRBS) were 66% more likely to report a suicide-related outcome than one-hour users and, in MTF, that time on homework was
<em>negatively</em> correlated with depressive symptoms, i.e. homework enters their models as a protective "nonscreen activity", not as pressure. {kreski.study} ({kreski.year}),
using the same 8th/10th-grade files for 2009–2017, find that the daily-use margin of social networking carries no association with depressive symptoms for girls
(overall OR 1.03, 95% CI 0.97–1.09 at the broadest cut) and a slightly protective one for boys, with any harm confined to 2009–2010. {keyes19.study} ({keyes19.year}) establish
that the post-2012 rise is a period effect (about 0.50 SD for girls and 0.33 SD for boys between 2012 and 2018), and Kaur et al. (2022) that adjusting for the
falling share with seven hours' sleep reduces the period-effect median odds ratio for loneliness from 1.16 to 1.07. No published MTF paper interacts homework hours with social-media
hours, and none reports the homework gradient of the social-media association by sex and grade; the time-use profile papers (Kreski et al. 2022, 2024) treat homework
as one of 17 profile items and conclude that changing time-use composition explains little of the rise.</p>
{t_lit}
<p class="caption">Student-level MTF estimates as published (verified against the abstract, PMC full text or the paper where accessible; two entries flagged in the methods note
could not be verified beyond the abstract). Full citations in <code>data/compiled/mtf/mtf_literature.csv</code>.</p>
<h4>The prepared microdata test</h4>
<p><code>scripts/analysis/31_mtf.py</code> is written to run on the ICPSR files once they are placed in <code>data/external/mtf/icpsr/&lt;study&gt;/</code>
({files_found} files found at this run). It locates variables through the MTF variable labels (the OSIRIS abbreviations printed in the volumes' cross-time index),
with the 8th/10th-grade V-codes from Orben and Przybylski's public replication code as confirmed anchors, and estimates, by sex and grade with year fixed effects,
race/ethnicity, parent education, region and the design weight, depressive affect, loneliness and happiness on homework hours, social-media hours and their product,
followed by a year-effects decomposition of the change since 2012. The study numbers to request are listed in the script header; the 12th-grade files for
2013–2024 are the binding gap, since they carry the hours-per-day social-media item that the published volumes never reached.</p>
<div class="note"><strong>Assessment.</strong> Nothing in the published MTF record supports the H2 premise for 12th graders: self-reported homework fell by about an hour a week from {y0} to {y1}
(boys {ctx.fmt(*hw_b)}, girls {ctx.fmt(*hw_g)}) and fell for 8th/10th graders from 1991 to 2014, while in-person socializing declined steadily through the whole
period and TV time was flat; loneliness and depressive affect were lower in 2012 than in 1996 and self-derogation only slightly higher, with girls' self-derogation
({ctx.fmt(*sd10_g)} points, 2010–2012) the one sign of the turn that Keyes et al. date to 2012. That ordering fits Haidt's and Gray's shared claim that face-to-face time
was eroding before smartphones, and it leaves the H1 question to the 2013–2024 microdata. The literature answers the H1 main effect (a dose gradient in hours, a null
at the daily-use margin) and shows homework as protective at the individual level, but the H3 interaction of homework with social-media hours has not been
estimated by anyone; the pipeline here will estimate it as soon as the ICPSR files can be downloaded by an account holder.</div>"""
    return {"mtf": html}
