"""Build build/report.html (the pilot report artifact) from results/tables and notes. Re-run after each new result."""
import json, ast, pathlib, pandas as pd, numpy as np, plotly.graph_objects as go
from plotly.subplots import make_subplots
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; OUT = ROOT/"build/report.html"
BOY, GIRL, ALL, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#8a919c"
PAL = ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7","#e34948"]
lab = pd.read_csv(ROOT/"notes/acs_value_labels.csv"); ST = lab[lab.variable=="STATEFIP"].set_index("outputcode")["label"].to_dict(); MET = lab[lab.variable=="MET2013"].set_index("outputcode")["label"].to_dict()
figs = {}
def base(fig, h=380, **kw):
    lay = dict(template="none", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=h, margin=dict(l=48,r=16,t=36,b=40),
        font=dict(family="'IBM Plex Sans', system-ui, sans-serif", size=12), hovermode="x unified", legend=dict(orientation="h", y=-0.18, x=0)); lay.update(kw)
    fig.update_layout(**lay)
    fig.update_xaxes(showgrid=False, zeroline=False); fig.update_yaxes(gridcolor="rgba(128,128,128,.18)", zeroline=False)
    return fig
def covid_band(fig, row=None, col=None):
    fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor="rgba(128,128,128,.12)", line_width=0, row=row, col=col)

# 1. ACS levels by sex, 12-14 / 15-17 / 65+
nat = pd.read_csv(T/"acs_national_year_sex_age.csv"); nat = nat[nat.year>=2008]; nat["rate"]*=100; nat["se"]*=100
fig = make_subplots(rows=1, cols=3, subplot_titles=["Ages 12–14","Ages 15–17","Ages 65+ (placebo)"], shared_xaxes=False, horizontal_spacing=0.06)
for c, ag in enumerate(["12-14","15-17","65+"], start=1):
    for sx, col, name in [(1,BOY,"Boys / men"),(2,GIRL,"Girls / women")]:
        d = nat[(nat.agegrp==ag)&(nat.sex==sx)]
        fig.add_trace(go.Scatter(x=list(d.year)+list(d.year[::-1]), y=list(d.rate+1.96*d.se)+list((d.rate-1.96*d.se)[::-1]), fill="toself", fillcolor=None, line=dict(width=0), hoverinfo="skip", showlegend=False, opacity=.18, marker=dict(color=col)), row=1, col=c)
        fig.add_trace(go.Scatter(x=d.year, y=d.rate, mode="lines", line=dict(color=col, width=2.2), name=name, showlegend=(c==1), hovertemplate="%{y:.2f}%<extra>"+name+"</extra>"), row=1, col=c)
    covid_band(fig, row=1, col=c)
fig.update_yaxes(title_text="% with cognitive difficulty", row=1, col=1); figs["acs_levels"] = base(fig, h=360)

# 2. Index by age group, by sex
fig = make_subplots(rows=1, cols=2, subplot_titles=["Boys / men","Girls / women"], shared_yaxes=True, horizontal_spacing=0.05)
ages = ["05-11","12-14","15-17","18-24","25-49","50-64","65+"]
for c, sx in enumerate([1,2], start=1):
    for i, ag in enumerate(ages):
        d = nat[(nat.agegrp==ag)&(nat.sex==sx)].set_index("year"); idx = 100*d.rate/d.loc[2008:2010,"rate"].mean()
        fig.add_trace(go.Scatter(x=idx.index, y=idx.values, mode="lines", name=ag, line=dict(color=PAL[i], width=2.6 if ag in ("12-14","15-17") else 1.4), showlegend=(c==1), hovertemplate="%{y:.0f}<extra>"+ag+"</extra>"), row=1, col=c)
    fig.add_hline(y=100, line=dict(color=MUTED, width=1), row=1, col=c); covid_band(fig, row=1, col=c)
fig.update_yaxes(title_text="Index, 2008–10 = 100", row=1, col=1); figs["acs_index"] = base(fig, h=400)

# 3. State caterpillar by sex
ch = pd.read_csv(T/"acs_state_change_by_sex.csv")
fig = make_subplots(rows=1, cols=2, subplot_titles=["Boys 12–17","Girls 12–17"], horizontal_spacing=0.18)
for c,(sx,col) in enumerate([(1,BOY),(2,GIRL)], start=1):
    d = ch[ch.sex==sx].sort_values("delta"); names = [ST.get(x, str(x)) for x in d.statefip]
    fig.add_trace(go.Scatter(x=d.delta, y=names, mode="markers", marker=dict(color=col, size=6), error_x=dict(type="data", array=1.96*d.se, color=col, thickness=1), name="", showlegend=False, hovertemplate="%{y}: %{x:.2f} pp<extra></extra>"), row=1, col=c)
    fig.add_vline(x=0, line=dict(color=MUTED, width=1), row=1, col=c)
fig.update_xaxes(title_text="Change, 2008–10 → 2017–19 (pp)"); fig.update_yaxes(tickfont=dict(size=9)); figs["state_caterpillar"] = base(fig, h=900, hovermode="closest", margin=dict(l=120, r=16, t=36, b=40))

# 4. Market funnel
m = pd.read_csv(T/"acs_market_change_0810_to_1719.csv"); m["name"] = [MET.get(x, f"{ST.get(x//100000,'?')} non-metro") for x in m.market]
mu = np.average(m.delta, weights=1/m.se**2)*100; ns = np.linspace(m.b_n.min(), m.b_n.max(), 200); se_typ = 100*np.median(m.se*np.sqrt(m.b_n))/np.sqrt(ns)
fig = go.Figure()
fig.add_trace(go.Scatter(x=ns, y=mu+1.96*se_typ, mode="lines", line=dict(color=MUTED, dash="dash", width=1), showlegend=False, hoverinfo="skip"))
fig.add_trace(go.Scatter(x=ns, y=mu-1.96*se_typ, mode="lines", line=dict(color=MUTED, dash="dash", width=1), showlegend=False, hoverinfo="skip"))
fig.add_trace(go.Scatter(x=m.b_n, y=100*m.delta, mode="markers", marker=dict(color=ALL, size=7, opacity=.8), text=m.name, name="Market", hovertemplate="%{text}<br>n=%{x:,}<br>Δ=%{y:.2f} pp<extra></extra>"))
fig.update_xaxes(type="log", title_text="Sampled 12–17-year-olds, 2008–10"); fig.update_yaxes(title_text="Change in % cognitive difficulty (pp)"); figs["market_funnel"] = base(fig, h=420, hovermode="closest")

# 5. ATUS mediators
at = pd.read_csv(T/"atus_1517_schoolweekday_period_se.csv", header=[0,1], index_col=0)
mid = {"2003-05":2004,"2006-08":2007,"2009-11":2010,"2012-14":2013,"2015-17":2016,"2018-19":2018.5,"2020-22":2021,"2023-24":2023.5}
cats = [c for c in at.columns.get_level_values(0).unique()]
fig = make_subplots(rows=2, cols=4, subplot_titles=cats, vertical_spacing=0.16, horizontal_spacing=0.06)
for i, k in enumerate(cats):
    r, c = i//4+1, i%4+1; x = [mid[p] for p in at.index]
    fig.add_trace(go.Scatter(x=x, y=at[(k,"mean")], mode="lines+markers", line=dict(color=PAL[i%8], width=2), marker=dict(size=6), error_y=dict(type="data", array=1.96*at[(k,"se")], color=PAL[i%8], thickness=1), name=k, showlegend=False, text=list(at.index), hovertemplate="%{text}: %{y:.0f} min<extra></extra>"), row=r, col=c)
    fig.update_yaxes(rangemode="tozero", row=r, col=c); covid_band(fig, row=r, col=c)
figs["atus"] = base(fig, h=520, hovermode="closest")

def fig_div(key):
    return f'<div class="chart" id="fig-{key}"></div>'

# tables
comp = pd.read_csv(T/"acs_composition_povgrp.csv")
def comp_rows(fname, label):
    d = pd.read_csv(T/fname); d = d[d.iloc[:,0].notna() & ~d.iloc[:,0].astype(str).str.startswith("not computed")]  # drop the group-quarters row, which has no poverty status
    rows = []
    for _, r in d.iterrows():
        rows.append(f"<tr><td>{r.iloc[0]}</td><td>{'girls' if r.sex==2 else 'boys'}</td><td>{r['2008-10']:.2f}</td><td>{r['2017-19']:.2f}</td><td>{r['rel_chg_1719']:+.0f}%</td><td>{r['rel_chg_2224']:+.0f}%</td><td>{r['share_pop_0810']:.0f}%</td></tr>")
    return f"<h4>{label}</h4><div class='tw'><table><thead><tr><th>Group</th><th>Sex</th><th>2008–10 %</th><th>2017–19 %</th><th>Rel. change to 2017–19</th><th>Rel. change to 2022–24</th><th>Share of 12–17, 2008–10</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
comp_html = comp_rows("acs_composition_povgrp.csv", "By family income relative to poverty line") + comp_rows("acs_composition_schltype.csv", "By school type") + comp_rows("acs_composition_raceeth.csv", "By race / ethnicity")

nat1217 = pd.read_csv(T/"acs_national_year_sex_age.csv"); nat1217 = nat1217[nat1217.agegrp.isin(["12-14","15-17"])]
def per(y0,y1,sx,ag): d = nat1217[(nat1217.year.between(y0,y1))&(nat1217.sex==sx)&(nat1217.agegrp==ag)]; return 100*np.average(d.rate, weights=d["pop"])
sexrows = "".join(f"<tr><td>{ag}</td><td>{s}</td><td>{per(2008,2010,sx,ag):.2f}</td><td>{per(2017,2019,sx,ag):.2f}</td><td>{100*(per(2017,2019,sx,ag)/per(2008,2010,sx,ag)-1):+.0f}%</td><td>{per(2022,2024,sx,ag):.2f}</td><td>{100*(per(2022,2024,sx,ag)/per(2008,2010,sx,ag)-1):+.0f}%</td></tr>" for ag in ["12-14","15-17"] for sx,s in [(1,"boys"),(2,"girls")])


# ---- validation section
SEC = ROOT/"build/sections"; SEC.mkdir(parents=True, exist_ok=True)
V = pd.read_csv(T/"validation_national_timing.csv")
srcs = [("NSDUH MDE 12-17","NSDUH: depression 12–17"),("YRBS sad/hopeless","YRBS: sad/hopeless"),("YRBS considered suicide","YRBS: considered suicide"),("ACS cognitive difficulty 12-17","ACS: cognitive difficulty"),("NHANES PHQ-9 ≥10, 18-24","NHANES: PHQ-9 ≥10, 18–24")]
fig = make_subplots(rows=1, cols=5, subplot_titles=[t for _,t in srcs], horizontal_spacing=0.045)
for c,(src,_) in enumerate(srcs, start=1):
    for sexlab, col in [("all",ALL),("boys",BOY),("girls",GIRL)]:
        d = V[(V.source==src)&(V.sex==sexlab)].sort_values("year")
        if len(d)==0: continue
        fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines+markers", line=dict(color=col, width=2), marker=dict(size=5), error_y=dict(type="data", array=1.96*d.se, color=col, thickness=1), name=sexlab, showlegend=((c==1 and sexlab=="all") or (c==2 and sexlab!="all")), hovertemplate="%{y:.1f}%<extra>"+sexlab+"</extra>"), row=1, col=c)
    d2 = V[(V.source=="NSDUH MDE 12-17 (2021+ mode)")&(V.sex=="all")]
    if src.startswith("NSDUH") and len(d2): fig.add_trace(go.Scatter(x=d2.year, y=d2.value, mode="markers", marker=dict(color=ALL, size=6, symbol="diamond-open"), name="2021+ (new mode)", hovertemplate="%{y:.1f}%<extra>2021+ mode</extra>"), row=1, col=c)
    fig.update_xaxes(range=[2004,2025], row=1, col=c); fig.update_yaxes(rangemode="tozero", row=1, col=c); covid_band(fig, row=1, col=c)
fig.update_annotations(font_size=11); figs["val_timing"] = base(fig, h=380, hovermode="closest")
Cst = pd.read_csv(T/"validation_state_change.csv")
fig = go.Figure(go.Scatter(x=Cst.d_acs, y=Cst.d_nsduh, mode="markers", marker=dict(color=ALL, size=8), customdata=[ST.get(int(x),str(x)) for x in Cst.statefip], hovertemplate="%{customdata}<br>ACS Δ %{x:.2f} pp<br>NSDUH Δ %{y:.2f} pp<extra></extra>", name="State"))
b = np.polyfit(Cst.d_acs, Cst.d_nsduh, 1); xs = np.linspace(Cst.d_acs.min(), Cst.d_acs.max(), 10); fig.add_trace(go.Scatter(x=xs, y=np.polyval(b, xs), mode="lines", line=dict(color=MUTED, dash="dash"), showlegend=False, hoverinfo="skip"))
fig.update_xaxes(title_text="ACS cognitive difficulty 12–17, change 2008–10 → 2017–19 (pp)"); fig.update_yaxes(title_text="NSDUH youth MDE, change (pp)"); figs["val_state"] = base(fig, h=420, hovermode="closest", showlegend=False)
def rc(src, sex, y0, y1):
    d = V[(V.source==src)&(V.sex==sex)]; bb = d[d.year.between(*y0)].value.mean(); ee = d[d.year.between(*y1)].value.mean(); return bb, ee, 100*(ee/bb-1)
sexcmp = "".join(f"<tr><td>{lab}</td><td>{sx}</td><td>{rc(src,sx,(2009,2011.9),(2017,2019.9))[0]:.1f}</td><td>{rc(src,sx,(2009,2011.9),(2017,2019.9))[1]:.1f}</td><td>{rc(src,sx,(2009,2011.9),(2017,2019.9))[2]:+.0f}%</td></tr>" for src,lab in [("ACS cognitive difficulty 12-17","ACS cognitive difficulty 12–17"),("YRBS sad/hopeless","YRBS sad/hopeless"),("YRBS considered suicide","YRBS considered suicide"),("NHANES PHQ-9 ≥10, 18-24","NHANES PHQ-9 ≥10, 18–24")] for sx in ["boys","girls"])
val_html = f"""
<p>Before using the ACS cognitive-difficulty item as an outcome, we test it against three criteria: whether its national timing matches established adolescent depression and sadness surveys, whether its increase is concentrated among girls, and whether state-level changes in the ACS item move with state-level changes in clinical depression. Because the public NHANES depression screener (PHQ-9) is released only for respondents aged 18 and older (the adolescent file is restricted), NHANES enters as an 18–24 benchmark.</p>
<h3>National timing</h3>
{fig_div('val_timing')}
<p class="caption">All series in percent, with 95% CIs. NSDUH points sit at the midpoint of each two-year period; the 2021+ NSDUH estimates use a new web mode and DSM-5 criteria and are not directly comparable to earlier years. YRBS sad/hopeless was first asked in 1999.</p>
<p>NSDUH past-year major depressive episodes among 12–17-year-olds held steady at roughly 8% from 2005 through 2010–11 and then rose in nearly every two-year wave to 15% by 2018–19. YRBS persistent sadness was flat from 1999 through 2011 before rising through 2019. The ACS cognitive-difficulty series turns upward around 2012 and accelerates after 2019. It inflects at roughly the same time as the mental-health surveys, though its relative increase over the 2010s is much smaller—about +13% overall, compared with +85% in NSDUH.</p>
<h3>Sex pattern</h3>
<div class="tw"><table><thead><tr><th>Series</th><th>Sex</th><th>2009–11</th><th>2017–19</th><th>Relative change</th></tr></thead><tbody>{sexcmp}</tbody></table></div>
<p>Across all four sources, the relative increase is larger for girls than for boys. The ACS item passes this check: if the 2010s increase were driven primarily by childhood ADHD or learning-disability diagnoses, boys would dominate the change.</p>
<h3>Do states move together?</h3>
{fig_div('val_state')}
<p class="caption">51 jurisdictions (50 states plus DC). Each point plots a state's change in both measures between 2008–10 and 2017–19; the dashed line is the OLS fit (slope 0.37, SE 0.18, r = 0.22).</p>
<p>In cross-section, state levels of the ACS item and NSDUH depression do not correlate, which is unsurprising given that one is a broad disability screener and the other is a diagnostic interview. Over time, however, their within-state changes move together: a state-and-period fixed-effects regression of NSDUH youth depression on the ACS cognitive-difficulty rate yields a slope of 0.14 (SE 0.05, p = 0.01) across 714 state-period observations, and the decade-long changes from 2008–10 to 2017–19 correlate at r = 0.22 (slope 0.37, SE 0.18). Against the YRBS state files (39 states, by sex), the ACS rate co-moves with persistent sadness at a slope of 0.35 (SE 0.18) with state-by-sex and year-by-sex fixed effects, though not with suicidal ideation.</p>
<div class="note"><strong>Assessment.</strong> The ACS cognitive-difficulty item reproduces the female-led rise and co-moves with depression within states, making it usable for fine-grained geographic tests where no mental-health survey exists. Even so, it captures only about a sixth of the proportional rise in adolescent depression, and its girl-specific change is small relative to metro-level sampling error. For that reason, we pair every U.S. ACS test with state and county youth mental-health surveys.</div>
"""
(SEC/"validation.html").write_text(val_html)

# ---- NTIA adoption dose section
N = pd.read_csv(ROOT/"data/compiled/ntia/ntia_national_sanity.csv")
inds = [("hh_mobile_data_plan","Household mobile data plan"),("person_uses_smartphone_internet","Uses a smartphone for internet"),("person_mobile_device_internet","Internet on a mobile device"),("person_internet_any","Uses the internet at all")]
fig = make_subplots(rows=1, cols=4, subplot_titles=[t for _,t in inds], horizontal_spacing=0.05)
for c,(ind,_) in enumerate(inds, start=1):
    for grp, col, lab in [("all",MUTED,"All persons 3+"),("age15_24",BOY,"Ages 15–24"),("hh_teen12_17",GIRL,"Households with a 12–17-year-old")]:
        d = N[(N.indicator==ind)&(N.group==grp)].sort_values("year")
        if ind != "person_internet_any": d = d[d.year != 2012]
        if len(d)==0: continue
        fig.add_trace(go.Scatter(x=d.year, y=100*d.share, mode="lines+markers", line=dict(color=col, width=2), marker=dict(size=6), name=lab, showlegend=(c==1), hovertemplate="%{y:.0f}%<extra>"+lab+"</extra>"), row=1, col=c)
    fig.add_vrect(x0=2013.5, x1=2014.5, fillcolor="rgba(128,128,128,.12)", line_width=0, row=1, col=c); fig.update_yaxes(range=[0,100], row=1, col=c)
fig.update_annotations(font_size=11); figs["ntia"] = base(fig, h=360)
S = pd.read_csv(ROOT/"data/compiled/ntia/ntia_state_year.csv"); S = S[(S.group=="hh_teen12_17")&(S.indicator=="person_uses_smartphone_internet")&(S.year.isin([2011,2013,2015]))]
piv = S.pivot_table(index="state", columns="year", values="share")*100; piv["name"] = [ST.get(int(i), str(i)) for i in piv.index]; piv = piv.sort_values(2013)
fig = go.Figure()
for yr, col in [(2011,PAL[3]),(2013,BOY),(2015,PAL[6])]:
    fig.add_trace(go.Scatter(x=piv[yr], y=piv.name, mode="markers", marker=dict(color=col, size=7), name=str(yr), hovertemplate="%{y}: %{x:.0f}%<extra>"+str(yr)+"</extra>"))
fig.update_xaxes(title_text="% of persons in households with a 12–17-year-old who use a smartphone for internet"); fig.update_yaxes(tickfont=dict(size=9)); figs["ntia_state"] = base(fig, h=820, hovermode="closest", margin=dict(l=120, r=16, t=36, b=40))
ntia_html = f"""
<p>Because IPUMS CPS includes only a subset of the Computer and Internet Use Supplement and omits the mobile-phone questions, we rebuilt the adoption series from the raw Census supplement files from October 2009 through November 2023 following NTIA's harmonization code. These files supply the pre-2016 smartphone and mobile-data adoption measures that the ACS lacks. The grey band marks the 2015 questionnaire redesign, which breaks the household mobile-data series (capturing at-home mobile broadband before 2015 and any-location mobile data plans from 2015 onward).</p>
{fig_div('ntia')}
<p class="caption">Weighted shares by wave. Smartphone-internet use reflects "use a cellular phone or smartphone to access the internet" in 2011 and 2013 (all persons) and NTIA's internet-enabled-phone definition from 2015 onward. In 2012 the phone items were asked only of the primary household respondent and are omitted here.</p>
<p>Smartphone internet use in households with a teenager rose from roughly 30% in 2011 to 45% in 2013 and 55% in 2015, before approaching saturation by 2017. Across states, teen-household smartphone use varied by 20 to 30 percentage points during the 2011–2015 transition window, providing the cross-state adoption variation used in our U.S. regression tests.</p>
{fig_div('ntia_state')}
<p class="caption">States ordered by their 2013 share. CBSA-level shares for 260–295 metropolitan areas per wave are also included in the compiled extract; county regressions restrict to CBSAs with at least 30 unweighted respondents.</p>
"""
(SEC/"ntia.html").write_text(ntia_html)

# ---- HBSC section
Hw = pd.read_csv(T/"hbsc_wide.csv"); Hw = Hw[Hw.age==15]
avg = Hw.groupby(["year_end","sex"])[["schoolwork_pressure","multiple_complaints"]].mean().reset_index()
fig = make_subplots(rows=1, cols=2, subplot_titles=["Pressured by schoolwork (some / a lot), age 15","Two or more psychosomatic complaints weekly, age 15"], horizontal_spacing=0.07)
for c, item in enumerate(["schoolwork_pressure","multiple_complaints"], start=1):
    for sx, col, lab in [("boy",BOY,"Boys"),("girl",GIRL,"Girls")]:
        d = avg[avg.sex==sx]
        fig.add_trace(go.Scatter(x=d.year_end, y=d[item], mode="lines+markers", line=dict(color=col, width=2.4), marker=dict(size=7), name=lab, showlegend=(c==1), hovertemplate="%{y:.1f}%<extra>"+lab+"</extra>"), row=1, col=c)
        for cty, dash in [("United States","dot"),("Canada","dash"),("England","dashdot")]:
            dd = Hw[(Hw.country==cty)&(Hw.sex==sx)].sort_values("year_end")
            fig.add_trace(go.Scatter(x=dd.year_end, y=dd[item], mode="lines", line=dict(color=col, width=1, dash=dash), name=f"{cty} ({lab.lower()})", showlegend=(c==1), opacity=.7, hovertemplate="%{y:.1f}%<extra>"+cty+" "+lab.lower()+"</extra>"), row=1, col=c)
    fig.update_yaxes(rangemode="tozero", row=1, col=c)
fig.update_annotations(font_size=11); figs["hbsc_trend"] = base(fig, h=420)
C = pd.read_csv(T/"hbsc_change_2010_2022_age15.csv")
fig = go.Figure()
for sx, col, lab in [("boy",BOY,"Boys"),("girl",GIRL,"Girls")]:
    d = C[C.sex==sx]; fig.add_trace(go.Scatter(x=d.d_pressure, y=d.d_complaints, mode="markers", marker=dict(color=col, size=8, opacity=.8), name=lab, text=d.country, hovertemplate="%{text}<br>Δpressure %{x:+.0f} pp<br>Δcomplaints %{y:+.0f} pp<extra>"+lab+"</extra>"))
b = np.polyfit(C.d_pressure, C.d_complaints, 1); xs = np.linspace(C.d_pressure.min(), C.d_pressure.max(), 10); fig.add_trace(go.Scatter(x=xs, y=np.polyval(b, xs), mode="lines", line=dict(color=MUTED, dash="dash"), showlegend=False, hoverinfo="skip"))
fig.update_xaxes(title_text="Change in % pressured by schoolwork, 2009/10 → 2021/22 (pp)"); fig.update_yaxes(title_text="Change in % with multiple complaints (pp)"); figs["hbsc_change"] = base(fig, h=440, hovermode="closest")
hbsc_html = f"""
<p>The WHO Health Behaviour in School-aged Children (HBSC) surveys ask 11-, 13-, and 15-year-olds across roughly 45 European and North American countries the same question on schoolwork pressure and the same psychosomatic-complaints checklist every four years. Published country tables from 1997/98 through 2021/22 (supplemented by the HBSC data browser for 2014–2022) allow a direct cross-national test of Gray's school-pressure mechanism. Because the United States participated only through the 2009/10 wave, post-2010 U.S. trends cannot be tracked in HBSC.</p>
{fig_div('hbsc_trend')}
<p class="caption">Unweighted means across participating countries (thick lines), with the United States, Canada, and England shown as thin dashed lines. Age 15.</p>
<p>Both series were flat or declining through 2009/10 and then rose in tandem: among 15-year-old girls, the cross-country mean of perceived schoolwork pressure increased from 46% in 2010 to 50% in 2014, 51% in 2018, and 62% in 2022, while the share reporting two or more weekly psychosomatic complaints rose from 44% to 50%, 52%, and 66%. In the 2000s, American 15-year-olds reported above-average schoolwork pressure, though U.S. pressure fell between 2006 and 2010, the final U.S. wave.</p>
<h4>Did complaints rise where pressure rose?</h4>
{fig_div('hbsc_change')}
<p class="caption">Each point is a country-sex cell at age 15; the dashed line is the pooled OLS fit (slope 0.24, SE 0.07, r = 0.59). Over the pre-pandemic 2010 → 2018 window alone, the slope is 0.16 (SE 0.07, r = 0.31).</p>
<div class="tw"><table><thead><tr><th>Specification (ages 11–15 pooled unless noted)</th><th>Estimate</th><th>Interpretation</th></tr></thead><tbody>
<tr><td>Within-country panel regression of complaints on pressure, with country×age×sex and wave×age×sex FE (1,440 cells)</td><td>0.14 (SE 0.04); girls 0.16, boys 0.12</td><td>A 10-pp rise in pressure corresponds to a 1.4-pp rise in complaints</td></tr>
<tr><td>Long difference 2010 → 2018, age 15 (72 country-sex pairs)</td><td>mean Δpressure +5.5 pp, Δcomplaints +6.6 pp; slope 0.16</td><td>Cross-country pressure differences account for ~1 pp of the 6.6-pp rise</td></tr>
<tr><td>Long difference 2010 → 2022, age 15 (70 pairs)</td><td>Δpressure +12.7, Δcomplaints +17.7; slope 0.24, r = 0.59</td><td>Stronger relationship, though 2022 includes pandemic disruptions</td></tr>
<tr><td>Pre-smartphone baseline period 2002 → 2010</td><td>Δpressure −2.9, Δcomplaints −0.1; slope 0.14</td><td>Same within-country slope during a period when neither series was rising</td></tr>
<tr><td>2018 &amp; 2022 cross-country: complaints on problematic social media use (PSMU) and pressure, wave×age×sex FE (496 cells)</td><td>PSMU 0.53 (SE 0.15); pressure 0.13 (SE 0.06)</td><td>Both predictors are independently associated with complaints</td></tr>
<tr><td>Within-country change 2018 → 2022 on PSMU and pressure</td><td>PSMU 0.25 (SE 0.18); pressure 0.12 (SE 0.10)</td><td>Imprecisely estimated with a single four-year change per country</td></tr>
</tbody></table></div>
<div class="note"><strong>Assessment.</strong> Perceived schoolwork pressure rose after 2010 across most HBSC countries, and psychosomatic complaints rose more in countries where pressure increased more. However, the within-country slope is modest (0.14) and identical to the slope during the 2002–2010 baseline period when neither measure was rising. Perceived pressure thus behaves like a steady correlate of complaints rather than the sole driver of the post-2010 inflection, most of which is absorbed by common wave effects across countries. Testing whether complaints became more concentrated among high-pressure students within countries requires the student-level HBSC microdata.</div>
"""
(SEC/"hbsc.html").write_text(hbsc_html)

# ---- LTE section
ES = pd.read_csv(T/"event_study_first_launch_date_dated_only.csv"); ES2 = pd.read_csv(T/"event_study_first_launch_date_with_untreated.csv")
fig = make_subplots(rows=1, cols=3, subplot_titles=["Ages 12–17, all","Girls 12–17","Boys 12–17"], shared_yaxes=True, horizontal_spacing=0.05)
for c, grp in enumerate(["12-17 all","12-17 girls","12-17 boys"], start=1):
    for df, col, lab, dx in [(ES, ALL, "Dated metros only (279)", -0.1), (ES2, MUTED, "With non-metro as untreated", 0.1)]:
        d = df[df.group==grp].sort_values("k"); d = pd.concat([d, pd.DataFrame({"k":[-1],"Estimate":[0],"Std. Error":[0]})]).sort_values("k")
        fig.add_trace(go.Scatter(x=d.k+dx, y=d.Estimate, mode="markers", marker=dict(color=col, size=7), error_y=dict(type="data", array=1.96*d["Std. Error"], color=col, thickness=1), name=lab, showlegend=(c==1), hovertemplate="k=%{x:.0f}: %{y:.2f} pp<extra>"+lab+"</extra>"), row=1, col=c)
    fig.add_hline(y=0, line=dict(color=MUTED, width=1), row=1, col=c); fig.add_vline(x=-0.5, line=dict(color=MUTED, width=1, dash="dot"), row=1, col=c)
    fig.update_xaxes(title_text="School years since LTE onset", row=1, col=c)
fig.update_yaxes(title_text="Effect on % cognitive difficulty (pp)", row=1, col=1); figs["event_study"] = base(fig, h=400, hovermode="closest")
# onset cohorts descriptive
on = pd.read_csv(T/"lte_onset_first_launch_date.csv"); od = pd.to_datetime(on.onset_date, format="mixed"); on["cohort"] = np.select([od < "2011-01-01", od < "2012-01-01"], ["Dec 2010 wave (36 metros)","2011 (125 metros)"], "2012–13 (110 metros)")
mm = pd.read_csv(T/"acs_met_year_sex_1217.csv").merge(on[["market","cohort"]], on="market")
mm["pop_"] = mm["pop"]; agg = mm.groupby(["cohort","year","sex"]).apply(lambda g: pd.Series({"rate": 100*np.average(g.rate, weights=g.pop_), "se": 100*np.sqrt(np.sum((g.pop_/g.pop_.sum())**2*g.se**2))}), include_groups=False).reset_index()
fig = make_subplots(rows=1, cols=2, subplot_titles=["Girls 12–17","Boys 12–17"], horizontal_spacing=0.07)
for c, sx in enumerate([2,1], start=1):
    for i, coh in enumerate(["Dec 2010 wave (36 metros)","2011 (125 metros)","2012–13 (110 metros)"]):
        d = agg[(agg.cohort==coh)&(agg.sex==sx)&(agg.year.between(2008,2019))].set_index("year"); idx = d.rate/d.loc[2008:2010,"rate"].mean()*100
        fig.add_trace(go.Scatter(x=idx.index, y=idx.values, mode="lines+markers", line=dict(color=PAL[i], width=2), marker=dict(size=5), name=coh, showlegend=(c==1), hovertemplate="%{y:.0f}<extra>"+coh+"</extra>"), row=1, col=c)
    fig.add_hline(y=100, line=dict(color=MUTED, width=1), row=1, col=c)
fig.update_yaxes(title_text="Rate indexed to 2008–10 = 100", row=1, col=1); figs["onset_cohorts"] = base(fig, h=400)
lte_html = f"""
<p>We compiled commercial 4G LTE launch dates from carrier press releases and trade-press archives covering 967 carrier-market launches (Verizon 442, AT&amp;T 243, Sprint 234, T-Mobile 47). Mapped to 2013 CBSA boundaries, these records establish a first-launch date for 98 of the 100 largest metropolitan areas and 279 of the 311 metros identified in the public ACS. Verizon's initial December 2010 rollout covered 36 of these metros, followed by 125 metros in 2011, 96 in 2012, and 14 in 2013. Each market's treatment onset is assigned to the first school year beginning after its initial commercial launch. Remaining coverage gaps (primarily Verizon's smaller 2013 rural market waves and roughly 44 AT&amp;T launch dates outside the top 100 metros) are documented in the methods note.</p>
<h3>Descriptive: onset cohorts</h3>
{fig_div('onset_cohorts')}
<p class="caption">Population-weighted ACS cognitive-difficulty rate for 12–17-year-olds in metros grouped by first commercial LTE launch, indexed to each cohort's 2008–10 mean.</p>
<p>If early 4G availability accelerated adolescent distress, metros in the December 2010 and 2011 launch waves should have pulled ahead of the 2012–13 wave between 2011 and 2013. Through 2013, however, the three cohorts move closely together. Starting in 2014, girls in the December 2010 cohort drift higher (reaching an index of 127 by 2019 versus 110–116 in later cohorts), but that earliest cohort consists of the 36 largest metros—where the affluent-teen composition shift documented in Part 1 is concentrated—and the divergence appears three years after launch. In the event-study regressions below, the coefficients for girls four to six years after launch are +0.6 to +1.1 pp with standard errors near 1 pp.</p>
<h3>Event study</h3>
{fig_div('event_study')}
<p class="caption">Estimated effect by school year relative to initial LTE launch (with the year prior to launch as the reference period), including market and year fixed effects, population weights, and standard errors clustered by market. Green: the 279 metros with a dated launch, identifying off rollout timing alone. Grey: adds the 32 undated metros and state non-metro remainders coded as never treated (an upper-bound contrast, since rural areas received LTE around 2013–14).</p>
<div class="tw"><table><thead><tr><th>Onset definition</th><th>Sample</th><th>12–17 all</th><th>Girls</th><th>Boys</th><th>65+ placebo</th><th>25–49</th></tr></thead><tbody>
<tr><td>First carrier</td><td>dated metros</td><td>+0.02 (0.15)</td><td>−0.04 (0.19)</td><td>+0.03 (0.27)</td><td>+0.03 (0.15)</td><td>+0.11 (0.08)</td></tr>
<tr><td>Verizon</td><td>dated metros</td><td>+0.01 (0.16)</td><td>−0.11 (0.20)</td><td>+0.05 (0.29)</td><td>+0.07 (0.16)</td><td>+0.11 (0.08)</td></tr>
<tr><td>Second carrier</td><td>dated metros</td><td>−0.01 (0.15)</td><td>−0.11 (0.17)</td><td>+0.20 (0.23)</td><td>+0.28 (0.14)</td><td>+0.09 (0.07)</td></tr>
<tr><td>First carrier</td><td>+ non-metro as untreated</td><td>0.00 (0.09)</td><td>−0.08 (0.10)</td><td>+0.11 (0.13)</td><td>+0.12 (0.11)</td><td>−0.10 (0.06)</td></tr>
</tbody></table></div>
<p class="caption">Static difference-in-differences coefficient on "LTE in force" in percentage points, with standard errors in parentheses. Permuting onset dates across markets yields a placebo standard error of roughly 0.07 pp for the full panel.</p>
<div class="note"><strong>Assessment.</strong> Staggered 4G LTE launch dates across U.S. metropolitan areas do not predict the timing of the rise in the ACS cognitive-difficulty item. For girls, the 95% confidence interval rules out effects larger than +0.33 pp on the dated-metro sample and +0.12 pp when including non-metro controls, compared with a national 2010–2019 increase of roughly 0.5 pp. Three limitations prevent this null result from ruling out H1: commercial LTE launches were compressed into a narrow 2011–2012 window across most major metros; adolescent social-media norms spread across markets through national platforms; and the ACS disability item captures only a fraction of internalizing distress. What the result does establish is that a metro-level rollout design using the ACS cannot detect a smartphone effect. In the next subsection we re-run the same geographic timing test on county-level youth mental-health surveys, and in the reconciliation section we compare our setup with Elaine Guo's British Columbia wireless study, which found a large effect on clinical school designations in rural mountain towns.</div>
"""
(SEC/"lte.html").write_text(lte_html)

# ---- GSHS section
G = pd.read_csv(T/"gshs_country_round_rates.csv"); G = G[G.groupby("iso3").year.transform("nunique") >= 2]
first = G.sort_values("year").groupby(["iso3","sex","item"]).first().reset_index(); last = G.sort_values("year").groupby(["iso3","sex","item"]).last().reset_index()
D = first.merge(last, on=["iso3","sex","item"], suffixes=("_0","_1")); D["d_rate"] = D.rate_1 - D.rate_0; D["d_net"] = D.internet_users_pct_1 - D.internet_users_pct_0; D["span"] = D.year_1 - D.year_0
fig = make_subplots(rows=1, cols=3, subplot_titles=["Felt lonely most of the time / always","Seriously considered suicide","So worried could not sleep"], horizontal_spacing=0.06)
for c, it in enumerate(["lonely","suicide_consider","worried_sleep"], start=1):
    for sx, col, lab in [("boys",BOY,"Boys"),("girls",GIRL,"Girls")]:
        d = D[(D.item==it)&(D.sex==sx)&D.d_net.notna()]
        fig.add_trace(go.Scatter(x=d.d_net, y=d.d_rate, mode="markers", marker=dict(color=col, size=8, opacity=.8), name=lab, showlegend=(c==1), text=[f"{i} {a}→{b}" for i,a,b in zip(d.iso3,d.year_0,d.year_1)], hovertemplate="%{text}<br>Δinternet %{x:+.0f} pp<br>Δrate %{y:+.1f} pp<extra>"+lab+"</extra>"), row=1, col=c)
    fig.add_hline(y=0, line=dict(color=MUTED, width=1), row=1, col=c); fig.update_xaxes(title_text="Δ internet users, % of pop.", row=1, col=c)
fig.update_yaxes(title_text="Change in prevalence, 13–17 (pp)", row=1, col=1); fig.update_annotations(font_size=11); figs["gshs"] = base(fig, h=400, hovermode="closest")
F = pd.read_csv(T/"gshs_fe_internet.csv"); F = F[(F.se_per10pp > 0.001)]
frows = "".join(f"<tr><td>{r.item.replace('_',' ')}</td><td>{r.sex}</td><td>{r.n_rounds} rounds / {r.n_countries} countries</td><td>{r.coef_per10pp:+.2f} ({r.se_per10pp:.2f})</td></tr>" for r in F.itertuples())
inv = pd.read_csv(ROOT/"data/compiled/gshs/gshs_inventory.csv") if (ROOT/"data/compiled/gshs/gshs_inventory.csv").exists() else None
nround = G.groupby(["iso3","year"]).ngroups; ncty = G.iso3.nunique(); nall = pd.read_csv(T/"gshs_country_round_rates.csv").groupby(["iso3","year"]).ngroups
gshs_html = f"""
<p>The WHO Global School-based Student Health Survey (GSHS) asks school-attending adolescents (primarily ages 13–17) in over 100 low- and middle-income countries identical questions on loneliness, anxiety-related sleep loss, and suicidality in waves starting in 2003. From the 165 public-use country-round files in the WHO microdata repository, {nall} rounds contained usable mental-health items and survey weights after harmonization, including {nround} rounds across {ncty} countries surveyed at least twice. We first test whether within-country changes in adolescent distress track national internet penetration from the World Bank (controlling for log GDP per capita), and then examine student-level phone hours and ITU mobile-network coverage below.</p>
{fig_div('gshs')}
<p class="caption">Each point plots a country's change from its first to its last GSHS wave (weighted prevalence) against the change in the national internet-user share over the same interval.</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Sex</th><th>Sample</th><th>Effect of +10 pp internet users (SE)</th></tr></thead><tbody>{frows}</tbody></table></div>
<p class="caption">Country and year fixed effects, log GDP per capita control, inverse-variance weights, and standard errors clustered by country.</p>
<div class="note"><strong>Assessment.</strong> Across the full 34-country panel, within-country growth in national internet penetration shows no statistically significant relationship with adolescent distress: for girls, a 10-percentage-point increase in internet users is associated with +1.04 pp in loneliness (SE 0.83) and +0.02 pp in suicidal ideation (SE 1.27), while the point estimates for boys are slightly negative. (An earlier partial extract of 72 rounds had suggested a +2.5 pp effect for girls on both outcomes, which disappeared once the remaining 77 rounds were added—a useful illustration of how sensitive country-round panels are to sample coverage.) National internet penetration is also a coarse proxy that pools adult and youth access. The two subsections below turn to the 2022–23 GSHS waves that ask students directly about daily mobile-phone hours and to the ITU mobile-broadband coverage series.</div>
"""
(SEC/"gshs.html").write_text(gshs_html)

# ---- policy section
R = pd.read_csv(T/"policy_t2_results.csv"); Rs = R[~R.policy.str.startswith(("joint","LTE"))]
names = {"rttt_winner":"Race to the Top winner (award year–2015)","waiver_in_force":"ESEA waiver in force","cc_aligned_test_in_force":"Common Core aligned test in force","teacher_eval_test_based_in_force":"Test-based teacher evaluation in force","exit_exam_in_force":"High-school exit exam in force","pressure_index":"Pressure index (sum of the five)"}
outs = ["ACS 12-17 girls","ACS 12-17 boys","YRBS sad/hopeless girls","YRBS sad/hopeless boys","NSDUH youth MDE (2-yr periods, policy averaged over both years)"]
def cell(pol, o):
    r = Rs[(Rs.policy==pol)&(Rs.outcome==o)]
    if len(r)==0: return "–"
    r = r.iloc[0]; star = "<strong>" if abs(r.coef) > 1.96*r.se else ""; return f"{star}{r.coef:+.2f} ({r.se:.2f}){'</strong>' if star else ''}"
prow = "".join(f"<tr><td>{names[pol]}</td>" + "".join(f"<td>{cell(pol,o)}</td>" for o in outs) + "</tr>" for pol in names)
Ri = R[R.policy.str.startswith("LTE")]
irow = "".join(f"<tr><td>{r.outcome.replace('ACS market ','')}</td><td>{r.policy.replace('LTE x ','')}</td><td>{f'{r.coef:+.2f} ({r.se:.2f})' if r.se < 50 else 'not identified'}</td></tr>" for r in Ri.itertuples())
Pm = pd.read_csv(T/"state_year_policy_fips.csv").groupby("year")[list(names)[:-1]].mean().reset_index()
fig = go.Figure()
for i, pol in enumerate(list(names)[:-1]):
    fig.add_trace(go.Scatter(x=Pm.year, y=100*Pm[pol], mode="lines+markers", line=dict(color=PAL[i], width=2), marker=dict(size=5), name=names[pol].split(" (")[0], hovertemplate="%{y:.0f}% of states<extra>"+names[pol].split(" (")[0]+"</extra>"))
fig.update_yaxes(title_text="% of states (incl. DC) with policy in force", range=[0,100]); figs["policy"] = base(fig, h=360)
policy_html = f"""
<p>We compiled implementation dates across all 51 jurisdictions for five major state accountability policies, documenting a primary source for each cell: Race to the Top awards (2010–11), ESEA/NCLB flexibility waivers (2012–16), the first operational Common Core–aligned state assessment (2012–2019, concentrated in spring 2015), statewide test-based teacher evaluation (2009–2017), and mandatory high-school exit exams (which declined from 25 states to 13 over the decade). Years refer to the school year ending that spring.</p>
{fig_div('policy')}
<p class="caption">Share of states (including DC) with each policy in force. Most states adopted ESEA waivers, teacher-evaluation rules, and Common Core–aligned tests within a narrow 2012–2015 window, leaving limited timing variation across states.</p>
<h3>State-year regressions</h3>
<div class="tw"><table><thead><tr><th>Policy (each estimated alone)</th><th>ACS girls</th><th>ACS boys</th><th>YRBS sad girls</th><th>YRBS sad boys</th><th>NSDUH youth MDE</th></tr></thead><tbody>{prow}</tbody></table></div>
<p class="caption">Coefficients in percentage points from regressions with state and year fixed effects, inverse-variance weights, and standard errors clustered by state, 2008–2019 (YRBS biennial across 39 states). NSDUH estimates are reported in two-year waves and matched to the average policy indicator across the two survey years; state clustering accounts for the half-sample overlap between consecutive waves (restricting to non-overlapping waves changes every NSDUH coefficient by less than 0.15 pp). Bold = |t| &gt; 1.96.</p>
<p>Common Core–aligned testing, ESEA waivers, test-based teacher evaluations, high-school exit exams, and the five-policy sum show no positive relationship with any of the three distress measures; several point estimates are slightly negative. The only statistically significant positive coefficient in the table is for Race to the Top on YRBS sadness (+1.21 pp for girls, SE 0.41; +0.68 pp for boys, SE 0.34), while the corresponding NSDUH estimate is +0.16 pp (SE 0.14) and the ACS coefficients are near zero. However, the 19 Race to the Top winners were a selected group of states (including DC, New York, Massachusetts, and Florida), and the static indicator was coded as 1 only during the 2010–2015 grant window—treating the winners' higher post-2015 sadness levels as part of the control baseline. When we trace the winning states year by year around the award date in the event study below, the apparent effect disappears.</p>
<h3>Does phone timing matter more in high-pressure states? (H3)</h3>
<div class="tw"><table><thead><tr><th>Outcome (ACS 12–17, market panel)</th><th>LTE × policy</th><th>Interaction (SE)</th></tr></thead><tbody>{irow}</tbody></table></div>
<p class="caption">State-by-year fixed effects absorb the direct effect of state policies; the interaction tests whether early-LTE metros rose more than late-LTE metros within states that had each policy in force. "Not identified" indicates that the policy turned on in the same year as LTE for nearly all dated metros in the state.</p>
<p>Where the interaction is identified, the point estimates for girls are negative (LTE × pressure index −0.34 pp, SE 0.25; LTE × Race to the Top −0.94 pp, SE 0.49). Early-LTE markets inside high-accountability states did not experience a larger rise in the ACS cognitive-difficulty item, though this test carries the same metro-level limitations as the main LTE event study.</p>
"""
a_, b_ = policy_html.split("<h3>Does phone timing matter more in high-pressure states? (H3)</h3>")
(SEC/"policy.html").write_text(a_); (SEC/"policy_inter.html").write_text(b_)

# ---- MICS section
MP = pd.read_csv(T/"mics_prevalence_sample_age_sex.csv"); MC = pd.read_csv(T/"mics_cluster_dose.csv"); MO = pd.read_csv(T/"mics_own_use_1517.csv")
sm = pd.read_csv(T/"mics_survey_summary.csv")  # survey-level summary written by scripts/analysis/18_mics_analysis.py
fig = make_subplots(rows=1, cols=2, subplot_titles=["Girls 10–17","Boys 10–17"], shared_yaxes=True, horizontal_spacing=0.05)
for c,(col,colr) in enumerate([("anx_g",GIRL),("anx_b",BOY)], start=1):
    fig.add_trace(go.Scatter(x=sm.dose, y=sm[col], mode="markers", marker=dict(color=colr, size=8, opacity=.75), text=[f"{i} {y}" for i,y in zip(sm.iso3, sm.year)], name="Survey", showlegend=False, hovertemplate="%{text}<br>young-adult daily internet %{x:.0f}%<br>anxious daily/weekly %{y:.1f}%<extra></extra>"), row=1, col=c)
    fig.update_xaxes(title_text="% of 15–24-year-olds using the internet almost daily", row=1, col=c)
fig.update_yaxes(title_text="% anxious/nervous daily or weekly (caregiver report)", row=1, col=1); figs["mics_scatter"] = base(fig, h=400, hovermode="closest")
# coefficient plot: cluster dose (10-17 vs 5-9) and own use, girls
rows = []
for dose, lab in [("y_net_daily","Cluster: 15–24 daily internet"),("y_mobile","Cluster: 15–24 own mobile"),("hh_net","Cluster: households with internet")]:
    for ag in ["10-17","5-9"]:
        for sx in ["girls","boys"]:
            r = MC[(MC.dose==dose)&(MC.ages==ag)&(MC.sex==sx)&(MC.outcome=="anx_dw")].iloc[0]; rows.append(dict(lab=f"{lab}, ages {ag}", sex=sx, coef=r.coef_per_100pct/10, se=r.se/10))
for x, lab in [("net_daily","Own daily internet use (15–17)"),("phone_daily","Own daily phone use (15–17)"),("mobile","Owns a mobile (15–17)")]:
    for sx in ["girls","boys"]:
        r = MO[(MO.exposure==x)&(MO.sex==sx)&(MO.outcome=="anx_dw")&(MO.fe=="cluster FE")].iloc[0]; rows.append(dict(lab=f"{lab}, within cluster", sex=sx, coef=r.coef_pp, se=r.se))
CF = pd.DataFrame(rows); labs = list(dict.fromkeys(CF.lab))
fig = go.Figure()
for sx, col, dy in [("girls",GIRL,0.15),("boys",BOY,-0.15)]:
    d = CF[CF.sex==sx]; yv = [labs.index(l)+dy for l in d.lab]
    fig.add_trace(go.Scatter(x=d.coef, y=yv, mode="markers", marker=dict(color=col, size=8), error_x=dict(type="data", array=1.96*d.se, color=col, thickness=1), name=sx.capitalize(), hovertemplate="%{x:+.2f} pp<extra>"+sx+"</extra>"))
fig.add_vline(x=0, line=dict(color=MUTED, width=1)); fig.update_yaxes(tickvals=list(range(len(labs))), ticktext=labs, autorange="reversed", tickfont=dict(size=10)); fig.update_xaxes(title_text="Effect on % anxious daily/weekly (pp): per +10 pp cluster-level use, or own use yes vs no")
figs["mics_coef"] = base(fig, h=440, hovermode="closest", margin=dict(l=300, r=16, t=30, b=50))
tr = pd.read_csv(T/"mics_two_round.csv"); tr = tr[tr.iso3!="PAK"]
trrows = "".join(f"<tr><td>{r.iso3}</td><td>{r.agegrp}</td><td>{'girls' if r.girl==1 else 'boys'}</td><td>{int(r.y0)} → {int(r.y1)}</td><td>{r.anx0:.1f} → {r.anx1:.1f}</td><td>{r.dep0:.1f} → {r.dep1:.1f}</td></tr>" for r in tr.itertuples())
mics_html = f"""
<p>MICS6 and MICS7 surveys (2017 onward) administer the Washington Group / UNICEF Child Functioning Module for children aged 5–17, asking the mother or primary caregiver how often the child "seems very anxious, nervous or worried" and how often the child seems "very sad or depressed" (daily, weekly, monthly, a few times a year, or never), using identical wording across countries. In the same households, women aged 15–49 (and men in roughly half the surveys) report mobile-phone ownership and how often they used the internet and a mobile phone over the past three months, while the household questionnaire records home internet access. Reading all 68 MICS samples with the module on the IPUMS-MICS server yields {int(MP.n.sum()):,} children with valid responses and weights across {MP['sample'].nunique()} surveys (53 of which also include the young-adult internet items).</p>
<h4>Prevalence across surveys</h4>
{fig_div('mics_scatter')}
<p class="caption">One point per survey (ages 10–17, across the 53 surveys that also record young-adult internet use). Cross-survey variation in caregiver-reported anxiety is wide—ranging from under 1% in Laos, Tuvalu, Vietnam, and Turkmenistan to 40–50% in Tunisia, Afghanistan, the Central African Republic, and Chad—and largely reflects national reporting norms, which is why all tests below compare children within the same country and region.</p>
<h4>Use and symptoms within countries</h4>
{fig_div('mics_coef')}
<p class="caption">Cluster rows regress children's daily/weekly anxiety on the share of 15–24-year-olds in their sampling cluster who use the internet almost daily (or own a mobile phone, or the household internet share), with survey-by-region fixed effects, household wealth quintile, urban/rural status, and age controls, and standard errors clustered by sampling cluster. Own-use rows link 15–17-year-olds to their own individual record in the women's or men's questionnaire (85% of girls matched, 24% of boys) and compare users with non-users within the same sampling cluster.</p>
<p>Girls aged 10–17 living in sampling clusters where more young adults use the internet daily are reported as slightly more anxious (+0.34 pp per 10-percentage-point rise in the cluster share, SE 0.13). However, a similar positive association appears for 5–9-year-old girls (+0.19 pp, SE 0.13), who are too young to use phones themselves, indicating that this reflects characteristics of more connected communities rather than adolescent phone use. Cluster-level mobile-phone ownership is <em>negatively</em> associated with caregiver-reported anxiety across all age and sex groups; household internet access shows a small positive association for 10–17-year-old girls (+0.26 pp per 10 points, SE 0.12, and +0.02 pp at ages 5–9); and caregiver-reported depression shows no positive relationship with any connectivity measure. Comparing 15–17-year-olds who use the internet or a phone daily with non-users in the same sampling cluster—the closest MICS equivalent to individual-level screen exposure—yields point estimates for girls that are near zero or slightly negative: −0.1 pp on anxiety (SE 1.4) and −1.8 pp on depression (SE 1.3) for daily internet use, and −2.2 pp on anxiety (SE 1.2) for daily phone use. For boys, the within-cluster own-phone-use coefficients are positive (+4.4 pp on anxiety and +5.5 pp on depression, SE ~2.0), though these rely on the roughly one-quarter of boys interviewed in the men's sub-sample. The learning and friendship functioning items show no meaningful association in either sex.</p>
<h4>Two-round countries</h4>
<div class="tw"><table><thead><tr><th>Country</th><th>Ages</th><th>Sex</th><th>Rounds</th><th>Anxious daily/weekly %</th><th>Depressed daily/weekly %</th></tr></thead><tbody>{trrows}</tbody></table></div>
<p class="caption">Countries with both a MICS6 and a MICS7 round on the server (Pakistan is excluded because its rounds sample different provinces). Turkmenistan rises from a very low baseline; Kyrgyzstan and Tunisia decline; Mongolia is mixed.</p>
<h4>DHS-8 self-reports: Nepal 2022</h4>
<p>The DHS-8 mental-health module provides a self-reported counterpart to the MICS caregiver reports. In 2022, Nepal administered the PHQ-9 and GAD-7 screeners to a subsample of 7,442 women aged 15–49 alongside questions on internet-use frequency and smartphone ownership (Kenya 2022 asked only whether a doctor had ever diagnosed depression or anxiety). Among Nepali women aged 15–19 (n = 1,379; 4.5% with PHQ-9 ≥ 10, 42% using the internet almost daily), daily internet users are 2.3 pp more likely to screen positive for depression (SE 2.4) and 3.5 pp more likely to screen positive for anxiety (SE 2.9) than non-users in the same sampling cluster (n = 1,293 in within-cluster regressions controlling for wealth, education, and age); the corresponding estimates are also positive at ages 20–24 and turn negative at ages 25–49. Smartphone ownership itself shows no positive association, and in Kenya diagnosed depression among 15–19-year-olds is unrelated to owning a smartphone (−0.1 pp, SE 1.3). Although these single-survey cross-sections are too small to be precise, their pattern matches the self-reported GSHS phone-hours gradient rather than the null results in the MICS caregiver reports: the positive association with screen use appears when adolescents report both their own use and their own symptoms.</p>
<div class="note"><strong>Assessment.</strong> Across 67 MICS surveys, neither local young-adult connectivity nor a teenage girl's own daily internet or phone use predicts caregiver-reported anxiety or depression within sampling clusters, and the small positive cluster correlation for girls' anxiety is shared by 5–9-year-olds. Three qualifications apply: the outcome is reported by caregivers rather than adolescents themselves; the exposure measures current use rather than exogenous network rollout timing; and only four countries currently offer repeated MICS rounds with the module.</div>
"""
(SEC/"mics.html").write_text(mics_html)
# ---- US dose + RTTT correction section
E = pd.read_csv(T/"rttt_event_time.csv")
fig = go.Figure()
for ser, col in [("YRBS sad/hopeless girls",GIRL),("YRBS sad/hopeless boys",BOY),("NSDUH youth MDE",ALL)]:
    d = E[E.series==ser].sort_values("k"); d = pd.concat([d, pd.DataFrame({"k":[-1],"Estimate":[0],"Std. Error":[0]})]).sort_values("k")
    fig.add_trace(go.Scatter(x=d.k, y=d.Estimate, mode="lines+markers", line=dict(color=col, width=2), marker=dict(size=6), error_y=dict(type="data", array=1.96*d["Std. Error"], color=col, thickness=1), name=ser, hovertemplate="k=%{x}: %{y:+.2f} pp<extra>"+ser+"</extra>"))
fig.add_hline(y=0, line=dict(color=MUTED, width=1)); fig.add_vline(x=-0.5, line=dict(color=MUTED, width=1, dash="dot")); fig.update_xaxes(title_text="Years relative to Race to the Top award"); fig.update_yaxes(title_text="Effect (pp), ref = year before award")
figs["rttt_es"] = base(fig, h=380, hovermode="closest")
usdose_html = f"""
<h3>Adoption rather than rollout: smartphone use against the state youth survey</h3>
<p>Because commercial 4G launch dates are a coarse measure of when teenagers actually went online on phones, we next test whether state-level smartphone adoption predicts adolescent sadness. Using the harmonized NTIA series (the share of persons in households with a 12–17-year-old who use a smartphone for internet, interpolated between the 2011–2019 CPS waves) against the YRBS state files across 39 states from 2011 to 2019, with state and year fixed effects:</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Measure of adoption</th><th>Effect per +10 pp of adoption (SE)</th></tr></thead><tbody>
<tr><td>YRBS sad/hopeless, girls</td><td>teen-household smartphone internet</td><td><strong>+0.90 (0.44)</strong></td></tr>
<tr><td>YRBS sad/hopeless, boys</td><td>same</td><td>+0.28 (0.41)</td></tr>
<tr><td>YRBS sad/hopeless, girls</td><td>household mobile data plan</td><td>+0.50 (0.51)</td></tr>
<tr><td>ACS cognitive difficulty 12–17, girls</td><td>teen-household smartphone internet</td><td>−0.04 (0.07)</td></tr>
</tbody></table></div>
<p>The state-level estimates align with the pattern predicted by H1—positive for girls rather than boys, and appearing on the self-reported YRBS sadness item rather than the ACS disability screener—but the evidence is fragile: it rests on five biennial YRBS waves, interpolated state adoption shares, and a p-value near 0.04 across 39 state clusters. Moreover, the county-level version of the same regression in the state youth surveys does not reproduce this relationship, so we treat the state-level correlation as suggestive.</p>
<h3>Race to the Top, traced year by year</h3>
{fig_div('rttt_es')}
<p class="caption">State and year fixed effects, plotting coefficients relative to the year before the award (the school year ending spring 2010 for Phase 1 and 2 winners, and spring 2012 for the December 2011 Phase 3 winners), 2005–2019. Both award cohorts are observed in the YRBS wave prior to their award (2009 and 2011); event years 6 or more before and 8 or more after are pooled into endpoint bins.</p>
<p>Tracing Race to the Top winners year by year around the grant award shows why the static regression coefficient in the previous section was misleading: after winning an award, states' YRBS sadness and NSDUH youth depression rates actually trended flat to downward relative to non-winning states. The positive static coefficient was an artifact of coding the grant indicator as 1 only during 2010–2015, which placed the winning states' post-2015 observations into the reference group. The event study provides no evidence that Race to the Top increased adolescent distress. Within the U.S. public data, state accountability policy shocks do not explain the post-2010 rise.</p>
"""
a_, b_ = usdose_html.split("<h3>Race to the Top, traced year by year</h3>")
(SEC/"usdose_adopt.html").write_text(a_); (SEC/"usdose_rttt.html").write_text("<h3>Race to the Top, traced year by year</h3>" + b_)

# ---- GSHS mobile hours addendum
MH = pd.read_csv(T/"gshs_mobile_hours.csv")
fig = go.Figure()
for sx, col in [("girls",GIRL),("boys",BOY)]:
    d = MH[MH.sex==sx]; names = {"lonely":"Lonely","worried_sleep":"Worried, lost sleep","suicide_consider":"Considered suicide","suicide_plan":"Made a plan","suicide_attempt":"Attempted"}
    fig.add_trace(go.Bar(x=[names[o] for o in d.outcome], y=d.coef_3plus, error_y=dict(type="data", array=1.96*d.se, thickness=1), marker=dict(color=col), name=sx.capitalize(), hovertemplate="%{x}: %{y:+.1f} pp<extra>"+sx+"</extra>"))
fig.update_layout(barmode="group", bargap=.3); fig.update_yaxes(title_text="Difference, 3+ h/day vs less (pp)"); figs["gshs_hours"] = base(fig, h=360, hovermode="closest")
mh_html = f"""
<h4>Asking adolescents directly: mobile-phone hours in the 2022–23 rounds</h4>
<p>Five recent GSHS rounds (Ghana 2022, India 2022, Jamaica 2023, Morocco 2023, and Wallis and Futuna 2023) added a question on "hours per day you used a mobile phone in the past 7 days," pairing each student's self-reported phone time with the same student's loneliness and suicidality responses.</p>
{fig_div('gshs_hours')}
<p class="caption">Regressions include country fixed effects and age controls, survey weights, and standard errors clustered by school across 7,708 girls and 7,102 boys (including students without a phone). Compared with students using a phone under three hours a day or not at all, girls at three or more hours report loneliness +8.2 pp (SE 1.4), suicidal ideation +10.1 pp (SE 1.5), and suicide attempts +5.6 pp (SE 1.6); the corresponding differences for boys are +5.3, +3.6, and +1.9 pp. Distress rises steadily across higher-use categories: relative to under one hour per day, girls reporting more than eight hours per day have +19.5 pp higher loneliness, +17.4 pp higher suicidal ideation, and +13.7 pp higher suicide attempts. Students without a mobile phone sit a few percentage points above the under-one-hour group rather than below it.</p>
<p>This individual-level dose-response gradient matches the pattern documented in Western surveys: substantial in magnitude, roughly twice as steep for girls as for boys, and increasing monotonically with daily hours above one hour. Because it is a cross-sectional self-report association, however, it cannot distinguish the effect of phone use on distress from reverse causation or shared underlying vulnerabilities. What it does show is that the 2022–23 GSHS rounds (alongside incoming MICS7 adolescent modules) are strong candidates for linking to subnational mobile-coverage rollout maps, since exposure is measured directly on the adolescent rather than inferred from national or adult averages.</p>
"""
(SEC/"gshs.html").write_text((SEC/"gshs.html").read_text() + mh_html)

# ---- GSHS ITU exposure addendum
IT = pd.read_csv(T/"gshs_fe_itu.csv"); IT = IT[IT.item.isin(["lonely","suicide_consider","suicide_attempt"])]
en = {"pop_covered_4g_pct":"4G population coverage (ITU)","pop_covered_3g_pct":"3G population coverage (ITU)","mbb_subs_per100":"Mobile-broadband subs per 100 (ITU)","itu_internet":"Internet users % (ITU)"}
itrows = "".join(f"<tr><td>{en[e]}</td><td>{g.n_countries.iloc[0]} / {g.n_rounds.iloc[0]}</td>" + "".join(f"<td>{g[(g.item==it)&(g.sex==sx)].coef_per10.iloc[0]:+.2f} ({g[(g.item==it)&(g.sex==sx)].se_per10.iloc[0]:.2f})</td>" if len(g[(g.item==it)&(g.sex==sx)]) else "<td>–</td>" for it in ["lonely","suicide_consider","suicide_attempt"] for sx in ["girls","boys"]) + "</tr>" for e, g in IT.groupby("exposure", sort=False))
itu_html = f"""
<h4>Network coverage at country level (ITU)</h4>
<p>Replacing World Bank internet penetration with the ITU mobile-network series allows us to test country-level 3G and 4G population coverage and active mobile-broadband subscriptions using the same two-way fixed-effects specification (country and year fixed effects, inverse-variance weights, and country-clustered standard errors across countries with two or more GSHS rounds).</p>
<div class="tw"><table><thead><tr><th>Exposure (per +10 points)</th><th>Countries / rounds (loneliness)</th><th>Lonely, girls</th><th>Lonely, boys</th><th>Considered suicide, girls</th><th>…boys</th><th>Attempted, girls</th><th>…boys</th></tr></thead><tbody>{itrows}</tbody></table></div>
<p class="caption">Sample counts in the second column refer to the loneliness item; suicidal ideation and suicide attempts are available in 1 to 3 fewer countries per row.</p>
<p>None of the country-level ITU series supports H1. Across the 15 countries with repeated 4G data, a 10-percentage-point increase in 4G coverage has slightly negative point estimates across all outcomes (from −0.20 to −0.64 pp, with standard errors of 0.38–0.69). For 3G coverage (17 countries), the coefficient on girls' loneliness is negative (−0.72 pp, SE 0.28) and the suicidality estimates are near zero; for active mobile-broadband subscriptions (22 countries), estimates range from +0.03 to +0.35 pp with standard errors around 0.4–0.5 pp. Because national coverage series move with broader economic development and pool urban and rural areas together, local cluster-level coverage remains the necessary test.</p>
"""
(SEC/"gshs.html").write_text((SEC/"gshs.html").read_text() + itu_html)

# ---- state survey section
TR = pd.read_csv(T/"state_survey_trends.csv"); LE = pd.read_csv(T/"state_survey_lte_event.csv"); ND = pd.read_csv(T/"state_survey_ntia_dose.csv"); LD = pd.read_csv(T/"state_survey_lte_did.csv")
fig = make_subplots(rows=1, cols=2, subplot_titles=["Sad or hopeless ≥2 weeks (YRBS wording)","Seriously considered suicide"], horizontal_spacing=0.06)
stcol = {"WA":PAL[0],"ME":PAL[1],"CA":PAL[2],"PA":PAL[3],"IL":PAL[4],"MN":PAL[6]}
for c, it in enumerate(["sad_hopeless","considered_suicide"], start=1):
    for st, col in stcol.items():
        d = TR[(TR.item==it)&(TR.state==st)].sort_values("year")
        if st=="MN" and it=="sad_hopeless": continue
        if len(d)==0: continue
        fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines+markers", line=dict(color=col, width=2), marker=dict(size=5), name=st, showlegend=(c==2), hovertemplate="%{y:.1f}%<extra>"+st+"</extra>"), row=1, col=c)
    fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor="rgba(128,128,128,.12)", line_width=0, row=1, col=c)
fig.update_yaxes(title_text="% of students (mean across counties)", row=1, col=1); figs["state_trends"] = base(fig, h=400)
lerows = "".join(f"<tr><td>{s_}</td><td>{g[g.k==0].Estimate.iloc[0] if len(g[g.k==0]) else float('nan'):+.2f}</td></tr>" for s_, g in LE.groupby('series'))
ldrows = "".join(f"<tr><td>{r.series.replace('counties ', 'counties, ').replace('WA+ME+MN', 'WA + ME + MN').replace('WA+ME', 'WA + ME')} ({r.counties} counties, {r.dated_counties} dated-metro, {r.units} county-grade series)</td><td>{r.did:+.2f} (SE {r.se:.2f})</td></tr>" for r in LD.itertuples())
ndrows = "".join(f"<tr><td>{r.item.replace('_',' ')}</td><td>{r.sex}</td><td>{r.coef_per10pp:+.2f} ({r.se:.2f})</td><td>{r.counties} / {r.cbsas}</td><td>{', '.join(r.states.split(';'))}</td></tr>" for r in ND.itertuples())
ss_html = f"""
<h3>State youth surveys at county level</h3>
<p>To measure self-reported adolescent distress below the state level, we compiled county-level school survey tables from six states: Minnesota (1998–2019, 87 counties), Washington (2010–2025, 38 counties), Maine (2009–2023, 16 counties), California (2013–2019, 55 counties, by sex), Pennsylvania (2015–2023, 60 counties), and Illinois (2018–2024, 82 counties for sadness and 75 for suicidal ideation), totaling 34,439 county-grade-year cells with documented question wording and primary sources. Minnesota's pre-2013 sadness question asked about feeling sad over the past 30 days rather than the standard YRBS two-week item and is excluded from the sadness panel.</p>
{fig_div('state_trends')}
<p class="caption">Unweighted county means across the grade levels each state reports in every survey wave (Washington grades 8, 10, and 12; Maine's 9–12 and Pennsylvania's 6–12 all-grade aggregates; Minnesota grade 9; California grades 7, 9, and 11 for sadness and 9 and 11 for suicidal ideation; Illinois grades 8, 10, and 12 for sadness and 10 and 12 for suicidal ideation). Minnesota's 2022 county tables are behind a web portal CAPTCHA and are not yet included.</p>
<p>The county panels highlight three notable patterns. First, persistent sadness rose across every state from roughly 2013 to a peak in 2021 (for example, from 28% to 41% in Washington, 23% to 37% in Maine, and 35% to 41% in Illinois). Second, Minnesota's 9th-grade suicidal-ideation series—the only county series extending back to the 1990s—<em>fell</em> steadily from 24% in 1998 to 12% in 2013 before turning upward to 15% by 2019. Third, the post-2021 waves show a substantial downturn: Washington's 2025 sadness rate (27%) is below its 2010 baseline, and Illinois's 2024 suicidal-ideation rate (13.5%) is the lowest in its county series.</p>
<h4>LTE onset at county level</h4>
<p>We link counties to 2013 CBSAs and their initial commercial 4G LTE launch dates. The unit of observation is a county-by-grade panel series with county-by-grade and state-by-year fixed effects, ensuring that changes in which grades a state surveys cannot register as changes in distress. Non-metro and undated counties serve as the comparison group (providing an upper-bound contrast, since rural LTE arrived around 2013–14), and standard errors are clustered by CBSA (or by county outside metro areas). Because the state surveys are biennial or triennial, no single pre-launch year is observed for every cohort, so event-study specifications pool the three years prior to LTE launch as the reference period.</p>
<div class="tw"><table><thead><tr><th>Panel</th><th>DiD on "LTE in force" (pp)</th></tr></thead><tbody>
{ldrows}
</tbody></table></div>
<h4>Smartphone adoption at the metro level</h4>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Sex</th><th>Effect per +10 pp teen-household smartphone internet (SE)</th><th>Counties / CBSAs</th><th>States</th></tr></thead><tbody>{ndrows}</tbody></table></div>
<p class="caption">NTIA CBSA smartphone-internet shares interpolated between waves (restricted to CBSAs with at least 30 unweighted respondents), with county-by-grade and state-by-year fixed effects and standard errors clustered by CBSA, 2011–2019.</p>
<div class="note"><strong>Assessment.</strong> Measuring self-reported sadness and suicidal ideation at the county level yields the same conclusion as the ACS metro panel: neither 4G LTE launch timing nor metro-level smartphone adoption predicts where adolescent distress rose fastest. The only coefficient exceeding two standard errors—Minnesota suicidal ideation after LTE onset (−1.82 pp, SE 0.67)—is negative and reflects the continuation of metro counties' steeper pre-2011 decline rather than a discrete break at LTE launch. Likewise, the positive state-level YRBS correlation between smartphone adoption and girls' sadness does not carry over to the county panels (+0.13 pp per 10 points overall across five states, SE 0.13; +0.22 pp for girls in California and Maine, SE 0.25). Across counties with very different connectivity timelines, the 2010s rise occurred almost simultaneously, and the recent post-2021 waves show a broad decline.</div>
"""
a_, b_ = ss_html.split("<h4>LTE onset at county level</h4>")
(SEC/"ss_trends.html").write_text(a_); (SEC/"ss_tests.html").write_text("<h3>Rollout and adoption at county level, state youth surveys</h3><h4>LTE onset at county level</h4>" + b_)

# ---- PISA phone-ban subsection
PR = pd.read_csv(T/"pisa_phone_ban_results.csv"); order = list(dict.fromkeys(PR.outcome))
fig = go.Figure()
for sx, col, dy in [("girls",GIRL,0.18),("boys",BOY,-0.18),("all",ALL,0.0)]:
    d = PR[PR.sex==sx]; yv = [order.index(o)+dy for o in d.outcome]; xv = [c if u=="pp" else 100*c for c,u in zip(d.coef, d.unit)]; ev = [e if u=="pp" else 100*e for e,u in zip(d.se, d.unit)]
    fig.add_trace(go.Scatter(x=xv, y=yv, mode="markers", marker=dict(color=col, size=7 if sx!="all" else 5, symbol="circle" if sx!="all" else "diamond-open"), error_x=dict(type="data", array=[1.96*e for e in ev], color=col, thickness=1), name=sx.capitalize(), hovertemplate="%{x:+.2f}<extra>"+sx+"</extra>"))
fig.add_vline(x=0, line=dict(color=MUTED, width=1)); fig.update_yaxes(tickvals=list(range(len(order))), ticktext=[o.replace(" (SD units)"," (×100 SD)") for o in order], autorange="reversed", tickfont=dict(size=10)); fig.update_xaxes(title_text="Ban school minus non-ban school: percentage points (binary items) or hundredths of an SD (indices)")
figs["pisa_ban"] = base(fig, h=520, hovermode="closest", margin=dict(l=330, r=16, t=30, b=60))
CB = pd.read_csv(T/"pisa_country_ban_summary.csv")
prrows = ""
for o in order:
    cells = ""
    for sx in ["all","girls","boys"]:
        r = PR[(PR.outcome==o)&(PR.sex==sx)]
        cells += f"<td>{r.coef.iloc[0]:+.2f} ({r.se.iloc[0]:.2f})</td>" if len(r) else "<td>–</td>"
    ra = PR[(PR.outcome==o)&(PR.sex=="all")].iloc[0]; prrows += f"<tr><td>{o}</td>{cells}<td>{ra['mean']:.1f} {ra.unit}</td></tr>"
pisa_html = f"""
<p>PISA 2022 asked school principals whether "the use of cell phones is not allowed on the school premises" and asked 15-year-old students about loneliness and belonging at school, digital-device habits, and (in 13 education systems) overall life satisfaction. Merging the student and school files yields 568,374 students across 19,885 schools in 80 systems; overall, 41% of students attend a school that bans phones on premises, ranging from 7% in Finland to 96% in Greece. We compare students in ban versus non-ban schools within the same country, controlling for student socio-economic status (ESCS), sex, grade, and private/public school status, using student survey weights and clustering standard errors by school.</p>
{fig_div('pisa_ban')}
<p class="caption">Binary outcomes are in percentage points; PISA scale indices are in hundredths of a standard deviation. The ICT familiarity module (smartphone use at school) covers 51 systems; the well-being module (life satisfaction and experienced well-being) covers 13–14 systems.</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>All</th><th>Girls</th><th>Boys</th><th>Mean</th></tr></thead><tbody>{prrows}</tbody></table></div>
<p>The within-country comparisons show three consistent patterns. First, school bans reduce in-school phone use, though compliance is far from complete: daily smartphone use at school is 12.1 percentage points lower in ban schools (from an overall mean of 55.3%, meaning roughly 43% of students in ban schools still use a phone daily), leisure digital use of more than an hour per day at school falls by 3.7 points, and after-school leisure screen use (>3 hours/day) is nearly unchanged (−0.8 pp)—a useful check that ban schools are not simply attended by students who avoid screens outside school. Second, students in ban schools report less classroom distraction by digital devices (−3.5 pp overall; −4.2 pp for girls and −2.8 pp for boys). Third, well-being differences are small, favorable, and concentrated among girls: girls in ban schools are 2.0 pp less likely to feel nervous or anxious without their device, 1.4 pp less likely to report feeling lonely at school (versus +0.3 pp for boys), and score +0.02 to +0.03 SD higher on school belonging and life satisfaction. Because this is a cross-sectional comparison across schools, however, it cannot separate the causal effect of a phone ban from unobserved differences in school leadership or student composition.</p>
<div class="note"><strong>Assessment.</strong> Across 80 education systems in PISA 2022, school phone prohibitions are associated with lower in-school phone use, less classroom digital distraction, and slightly lower loneliness and device anxiety among girls. While cross-sectional school comparisons cannot rule out selection into bans, the girl-specific pattern aligns with the quasi-experimental evidence from Norway's middle-school bans and underscores the value of evaluating the 2024–26 U.S. state phone bans as post-ban YRBS and state-survey waves become available.</div>
"""
(SEC/"pisa.html").write_text(pisa_html)

# ---- H3 refined: ban x academic pressure (PISA)
BX = pd.read_csv(T/"pisa_ban_x_pressure.csv")
bxrows = "".join(f"<tr><td>{r.outcome}</td><td>{r.sex}</td><td>{r.ban_lowanx:+.2f} ({r.se_low:.2f})</td><td>{r.ban_hianx:+.2f}</td><td>{r.ban_x_hianx:+.2f} ({r.se_int:.2f})</td><td>{r.hianx_main:+.1f}</td></tr>" for r in BX.itertuples())
h3_html = f"""
<p>In its sharpest form, the interaction hypothesis (H3) proposes that smartphones harm adolescents primarily when they pervade the school day alongside high-stakes academic pressure—layering constant social comparison and notifications onto the same hours that carry grades and testing. That mechanism implies three testable predictions: academic demands and smartphone use should both have risen after 2010 (as seen in HBSC schoolwork pressure and U.S. weekday homework time); removing phones from the school day should improve well-being, particularly for students experiencing high academic pressure; and screen use outside high-pressure school environments should be less strongly tied to distress.</p>
<h3>What the phone-ban evidence says about this</h3>
<p>PISA 2022 allows an initial test of whether school phone bans matter more for academically anxious students. Because PISA 2022 did not include general schoolwork-anxiety items, we use the PISA mathematics-anxiety index (asked of all students) as a proxy for academic pressure, splitting students at their country's median. We estimate the same within-country regression as above, interacting the school ban indicator with high mathematics anxiety separately by sex.</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Sex</th><th>Ban, low-anxiety students (SE)</th><th>Ban, high-anxiety students</th><th>Difference (SE)</th><th>High vs low anxiety, no ban</th></tr></thead><tbody>{bxrows}</tbody></table></div>
<p class="caption">Binary items in percentage points and scale indices in hundredths of an SD; regressions include country fixed effects, socio-economic status, private/public school type, and grade controls, student weights, and school-clustered standard errors across 441,992 students with non-missing mathematics anxiety.</p>
<p>Students with above-median mathematics anxiety are substantially lonelier at school (+8.2 pp among girls and +7.4 pp among boys in non-ban schools), and the association between attending a ban school and lower loneliness is larger for them: −1.15 pp for high-anxiety girls versus −0.27 pp for low-anxiety girls (interaction −0.88 pp, SE 0.93), and −0.81 pp versus +1.12 pp for boys (interaction −1.94 pp, SE 0.98). These interaction estimates point in the direction H3 predicts, though they are noisy and rely on mathematics anxiety as a proxy for broader academic pressure. Notably, school bans reduce daily in-school phone use by virtually the same amount (~13 percentage points) in both anxiety groups, so any difference in well-being would reflect differential sensitivity to removing phones rather than differential compliance. A more direct test of H3 requires pairing school phone policies with a direct measure of schoolwork pressure, which the 2021/22 HBSC microdata can support.</p>
"""
(SEC/"h3.html").write_text(h3_html)

# ---- phone bans section
PB = pd.read_csv(ROOT/"data/compiled/phone_bans/school_phone_prohibition_national.csv"); PB = PB[PB.share_of_schools_pct.notna()]
PB["y"] = PB.year.astype(str).str[:4].astype(int) + 0.5; nces = PB[PB.survey.str.contains("SSOCS|FRSS")]; spp = PB[PB.survey.str.contains("School Pulse")]; pif = PB[PB.survey.str.contains("Phones in Focus")]
fig = go.Figure()
fig.add_trace(go.Scatter(x=nces.y, y=nces.share_of_schools_pct, mode="lines+markers", line=dict(color=BOY, width=2), marker=dict(size=7), error_y=dict(type="data", array=1.96*nces.se.fillna(0), thickness=1, color=BOY), name="Prohibit phones during school hours (SSOCS/FRSS)", hovertemplate="%{y:.1f}%<extra>SSOCS</extra>"))
fig.add_trace(go.Scatter(x=spp.y, y=spp.share_of_schools_pct, mode="markers", marker=dict(color=GIRL, size=9, symbol="diamond"), name="School Pulse Panel 2024–25 (any class / bell-to-bell)", text=spp.item_wording.str[:60], hovertemplate="%{y:.0f}%<br>%{text}<extra>SPP</extra>"))
fig.add_trace(go.Scatter(x=pif.y, y=pif.share_of_schools_pct, mode="markers", marker=dict(color=MUTED, size=8, symbol="square-open"), name="Educator survey, bell-to-bell (non-probability)", hovertemplate="%{y:.0f}%<extra>Phones in Focus</extra>"))
fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor="rgba(128,128,128,.12)", line_width=0); fig.update_yaxes(title_text="% of U.S. public schools", range=[0,100]); figs["phone_bans_trend"] = base(fig, h=380)
# ---- bans vs sadness overlay (two stacked panels, shared x)
SBv = pd.read_csv(ROOT/"data/compiled/phone_bans/state_phone_bans.csv")
SBv["eff"] = SBv.effective_school_year.astype(str).str.extract(r"(20\d\d)-?(\d\d)?")[0].astype(float) + 1  # school year 2024-25 -> in force spring 2025
mand = SBv[SBv.policy_type.str.contains("bell-to-bell|instructional", case=False, na=False)]
yrs = list(range(2009, 2029)); cum = [100*(mand.eff <= y).sum()/51 for y in yrs]
Vn = pd.read_csv(T/"validation_national_timing.csv"); TRs = pd.read_csv(T/"state_survey_trends.csv")
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.42, 0.58], subplot_titles=["School phone restrictions", "Adolescent sadness and depression"])
nc = nces.sort_values("y")
fig.add_trace(go.Scatter(x=nc.y, y=nc.share_of_schools_pct, mode="lines+markers", line=dict(color=BOY, width=2.4), marker=dict(size=7), error_y=dict(type="data", array=1.96*nc.se.fillna(0), thickness=1, color=BOY), name="% of schools prohibiting phones during school hours (NCES)", hovertemplate="%{y:.1f}%<extra>NCES</extra>"), row=1, col=1)
fig.add_trace(go.Scatter(x=spp.y, y=spp.share_of_schools_pct, mode="markers", marker=dict(color=BOY, size=9, symbol="diamond-open"), name="School Pulse 2024–25: any class (77) / all day (30)", hovertemplate="%{y:.0f}%<extra>SPP</extra>"), row=1, col=1)
fig.add_trace(go.Scatter(x=yrs, y=cum, mode="lines", line=dict(color=PAL[6], width=2, shape="hv"), name="% of states with a statewide ban in force (bell-to-bell or class time)", hovertemplate="%{y:.0f}% of states<extra>state mandates</extra>"), row=1, col=1)
for src, sx, col, dash, lab in [("NSDUH MDE 12-17","all",ALL,"solid","NSDUH: past-year depression, 12–17"),("YRBS sad/hopeless","girls",GIRL,"solid","YRBS: sad/hopeless, girls"),("YRBS sad/hopeless","boys",BOY,"solid","YRBS: sad/hopeless, boys")]:
    d = Vn[(Vn.source==src)&(Vn.sex==sx)&(Vn.year>=2005)].sort_values("year")
    fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines+markers", line=dict(color=col, width=2.2, dash=dash), marker=dict(size=6), name=lab, hovertemplate="%{y:.1f}%<extra>"+lab+"</extra>"), row=2, col=1)
d2 = Vn[(Vn.source=="NSDUH MDE 12-17 (2021+ mode)")&(Vn.sex=="all")]; fig.add_trace(go.Scatter(x=d2.year, y=d2.value, mode="markers", marker=dict(color=ALL, size=7, symbol="diamond-open"), name="NSDUH 2021+ (new mode)", hovertemplate="%{y:.1f}%<extra>NSDUH new mode</extra>"), row=2, col=1)
for st_, dash in [("WA","dot"),("ME","dashdot"),("IL","longdash")]:
    d = TRs[(TRs.item=="sad_hopeless")&(TRs.state==st_)].sort_values("year")
    fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines", line=dict(color=MUTED, width=1.4, dash=dash), name=f"{st_} county mean, sad/hopeless", hovertemplate="%{y:.1f}%<extra>"+st_+"</extra>"), row=2, col=1)
for r in (1,2): fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor="rgba(128,128,128,.12)", line_width=0, row=r, col=1)
fig.update_yaxes(title_text="% of schools / states", range=[0,100], row=1, col=1); fig.update_yaxes(title_text="% of adolescents", rangemode="tozero", row=2, col=1); fig.update_xaxes(range=[2004.5, 2028.5], row=2, col=1)
fig.update_annotations(font_size=11); figs["bans_vs_sadness"] = base(fig, h=720, legend=dict(orientation="h", y=-0.1, x=0))
overlay_html = f"""
<h3>Bans and sadness on one time axis</h3>
{fig_div('bans_vs_sadness')}
<p class="caption">Top: principal-reported share of U.S. public schools prohibiting non-academic phone use during school hours (NCES SSOCS; 2013–14 is from a smaller Fast Response Survey; question wording changed in 2017–18), the 2024–25 School Pulse Panel estimates (77% prohibiting use during any class, 30% all day), and the cumulative share of states with a statewide bell-to-bell or instructional-time mandate in force. Bottom: NSDUH past-year major depressive episode (ages 12–17), YRBS persistent sadness by sex, and county-mean sadness from the Washington, Maine, and Illinois youth surveys. Grey band = 2020.</p>
<p>Plotted on a common timeline, U.S. school phone restrictions and adolescent distress moved in opposite directions over two successive cycles. Between 2009–10 and 2015–16—the years when smartphones replaced feature phones—the share of public schools prohibiting cell-phone use fell from 91% to 66%, while youth depression and sadness rose from their 2011–13 lows. School prohibitions then rebounded to 77% by 2019–20, and a wave of state legislation between 2023 and 2026 has pushed mandatory class-time or bell-to-bell bans into a majority of states; over the same post-2021 window, adolescent sadness fell across every state survey with recent data. Because these are aggregate national series, however, the timing alignment is only suggestive: sadness continued to rise through 2019–2021 even after school prohibitions began recovering, and the post-2021 downturn started before most state laws took effect. Two non-exclusive mechanisms could account for the recent decline:</p>
<ul>
<li><strong>Gradual school re-restriction and broader norm shifts.</strong> The recovery in school restrictions after 2016, combined with growing concern among parents, educators, and teenagers themselves, may have curbed the most disruptive in-school phone use even before statutory state mandates arrived. That interpretation is consistent with the PISA 2022 cross-section and Norway's middle-school ban study, though the aggregate U.S. timing is loose.</li>
<li><strong>Shifts in platform content.</strong> If the 2012–2019 rise was driven primarily by peer social comparison on photo-sharing networks (Instagram, Snapchat), the subsequent shift of teen screen time toward algorithmic short-form video feeds (TikTok, YouTube) could keep total screen hours high while generating less acute social-comparison distress. Because public surveys do not track platform mix over time, our data cannot test this channel directly.</li>
</ul>

<h3>Lags and enforcement</h3>
<p>Two practical features of school phone bans also affect how the aggregate timeline and upcoming state evaluations should be interpreted:</p>
<ul>
<li><strong>Effects take a year or two to materialize.</strong> Quasi-experimental studies consistently find adjustment lags after a ban is introduced. In the 2026 U.S. Yondr-pouch study (Allcott et al.), student subjective well-being <em>dipped</em> by 0.20 SD in the adoption year before turning positive (+0.16 SD) in year two; in Norway (Abrahamsson 2024), reductions in bullying and mental-health visits grew over three years; and in Florida (Figlio and Özek 2025), student suspensions rose 12% in year one before fading in year two as test-score gains emerged. If school bans require a year of administrative adjustment before improving school climate, the 2015–16 trough in U.S. restrictions would register around 2017–18 and the 2024–25 state mandates around 2026–27. Evaluations of the new U.S. laws will therefore need at least two post-ban waves rather than a single immediate post-year.</li>
<li><strong>Stated policy differs from actual enforcement.</strong> PISA 2022 measures both principal-reported school bans and student-reported daily smartphone use at school. Across 52 education systems with both items, a median 46% of students in ban schools still reported using a smartphone at school daily (versus 62% in non-ban schools), and in 24 systems a majority of students in ban schools did so. Enforcement in the United States in 2022 was particularly weak: 70.1% of students in U.S. ban schools used a smartphone daily at school compared with 81.7% in non-ban schools (an 11.6-point gap, versus gaps of 30–46 points in Japan, Taiwan, Switzerland, and Brunei). Stated school policies in the pre-2024 U.S. data were thus loosely enforced, and any effects estimated from early state mandates will represent a lower bound on strict bell-to-bell enforcement.</li>
</ul>
<p class="caption">Country-by-country daily in-school smartphone rates in ban and non-ban schools are reported in <code>results/tables/pisa_ban_enforcement_by_country.csv</code>.</p>
"""

SB = pd.read_csv(ROOT/"data/compiled/phone_bans/state_phone_bans.csv"); cnt = SB.groupby(["policy_type","effective_school_year"]).size().reset_index(name="n")
sbrows = "".join(f"<tr><td>{r.policy_type}</td><td>{r.effective_school_year if isinstance(r.effective_school_year,str) else '–'}</td><td>{r.n}</td><td>{', '.join(SB[(SB.policy_type==r.policy_type)&(SB.effective_school_year==r.effective_school_year)].state) if isinstance(r.effective_school_year,str) else ', '.join(SB[(SB.policy_type==r.policy_type)&SB.effective_school_year.isna()].state)}</td></tr>" for r in cnt.sort_values(["policy_type","effective_school_year"]).itertuples())
ST_ = pd.read_csv(ROOT/"data/compiled/phone_bans/phone_ban_studies.csv")
cols = [c for c in ST_.columns]; get = lambda r, k: next((str(getattr(r, c)) for c in cols if k in c.lower() and str(getattr(r, c))!="nan"), "")
strows = "".join(f"<tr><td>{get(r,'author')} ({get(r,'year')})</td><td>{get(r,'country')}</td><td>{get(r,'design')}</td><td>{get(r,'outcome')}</td><td>{get(r,'headline') or get(r,'effect')}</td></tr>" for r in ST_.itertuples())
CS = pd.read_csv(T/"county_screen_dose.csv")
csrows = "".join(f"<tr><td>{r.state}</td><td>{r.dose.replace('_',' ')}</td><td>{r.outcome.replace('_',' ')}</td><td>{r.n}</td><td>{r.cross_coef:+.2f} ({r.cross_se:.2f})</td><td>{r.within_coef:+.2f} ({r.within_se:.2f})</td></tr>" for r in CS.itertuples())
bans_html = f"""
<p>School phone restrictions are the one policy intervention that both the phone-centered and interaction hypotheses predict should matter, and they have shifted markedly over the past fifteen years. Below we combine national school-policy surveys, our 51-state legislative tracker, existing quasi-experimental evaluations, and PISA 2022 microdata to assess what school phone bans do.</p>
{overlay_html}
<h4>The national school-policy series</h4>
{fig_div('phone_bans_trend')}
<p class="caption">Principal-reported share of public schools prohibiting non-academic cell-phone use during school hours (NCES SSOCS; the 2013–14 point comes from a smaller Fast Response Survey, and the item wording changed in 2017–18). The 2024–25 School Pulse Panel asks about class time rather than all school hours: 77% prohibit phones in any class, and 30% prohibit them both in class and outside class.</p>

<h3>State bans and what can be tested when</h3>
<div class="tw"><table><thead><tr><th>Policy type</th><th>Effective school year</th><th>N</th><th>States</th></tr></thead><tbody>{sbrows}</tbody></table></div>
<p class="caption">Compiled from Ballotpedia, Education Week, KFF, and enacted state statutes; classification differences across trackers are documented in the data file. Florida's HB 379 (instructional time, 2023–24) was the earliest statewide mandate.</p>
<p>Nearly all statewide phone bans took effect in fall 2024, fall 2025, or fall 2026. Because the latest mental-health survey waves currently in hand are from spring 2023 (YRBS, Pennsylvania, Maine), spring 2024 (Illinois), and fall 2025 (Washington, which has state guidance rather than a mandate), post-ban statewide mental-health outcomes are not yet observed in our panel. The upcoming 2025 YRBS state files will permit an initial difference-in-differences test comparing early-ban states—Florida (2023–24) and Indiana, Louisiana, and South Carolina (2024–25)—against states without a mandate across the 2021, 2023, and 2025 waves, by sex. As subsequent waves of the state county surveys are released, the county panel will test Minnesota's 2024–25 district-policy mandate, Maine's and California's 2026–27 mandates, and Illinois's 2027–28 bell-to-bell ban using the same county-by-grade panel structure developed for LTE above. Obtaining NCES restricted-use SSOCS files (which include state and county identifiers) would also enable a school-level panel design across the 2010–2024 relaxation and re-tightening cycle.</p>
<h3>What the causal literature already shows</h3>
<div class="tw"><table><thead><tr><th>Study</th><th>Setting</th><th>Design</th><th>Outcome domain</th><th>Headline</th></tr></thead><tbody>{strows}</tbody></table></div>
<p>Across existing evaluations, evidence on school phone bans is mixed overall but points to girl-specific benefits when mental health is measured over multiple years. The strongest mental-health evidence comes from Abrahamsson's (2024) staggered difference-in-differences study of more than 400 Norwegian middle schools, which finds that bans reduced girls' general-practitioner and specialist visits for psychological symptoms, reduced bullying for both sexes, and raised girls' GPA, with no mental-health or achievement effect for boys. By contrast, an English cross-sectional study (Goodyear et al. 2025) finds no difference in student well-being between restrictive and permissive schools, and the 2026 U.S. Yondr-pouch study (Allcott et al.) finds an initial year-one dip in subjective well-being (−0.20 SD) followed by a year-two recovery (+0.16 SD) and no change in perceived online bullying. On academic achievement, Beland and Murphy (2016) in England, Beneito and Vicente-Chirivella (2022) in Spain, Figlio and Özek (2025) in Florida, and Lichand et al. (2026) in Rio de Janeiro find small positive test-score gains, whereas Kessel et al. (2020) in Sweden and Allcott et al. (2026) in the U.S. overall find near-zero average test-score effects (with modest high-school math gains in the U.S.).</p>
<h3>County social-media use and sadness</h3>
<div class="tw"><table><thead><tr><th>State</th><th>County item</th><th>Outcome</th><th>County-grade-years</th><th>Across counties (SE)</th><th>Within county and grade (SE)</th></tr></thead><tbody>{csrows}</tbody></table></div>
<p class="caption">Percentage points of outcome per percentage point of the county screen-use item, estimated on county-by-grade cells so that exposure and outcome cover identical grades; "Across counties" includes year fixed effects, and "Within county and grade" includes county-by-grade and year fixed effects, with standard errors clustered by county. Washington covers grades 8, 10, and 12 in 2023 and 2025; Maine covers grades 9–12 in 2017, 2019, and 2021.</p>
<p>In Washington, county-grade cells where a higher share of students use social media daily also report higher rates of persistent sadness (+0.22 pp per percentage point, SE 0.04), and a similar cross-sectional relationship holds for three or more hours of daily screen time (+0.25 pp, SE 0.06). Between 2023 and 2025, both screen measures and sadness declined statewide in Washington (daily social media fell from 74.9% to 72.9%, 3+ hours of screen time from 68.9% to 65.5%, and sadness from 31.2% to 27.4%), but county-by-county changes over the two-year window do not line up: within the same county and grade, two-year changes in sadness are unrelated to changes in either screen-time measure (−0.09 pp, SE 0.16 for daily social media; +0.01 pp, SE 0.08 for 3+ hours of screen time). Maine's county panel from 2017 to 2021 likewise shows no within-county relationship. Just as in the national literature, the cross-sectional correlation between screen time and sadness is clear, while short-run within-area changes are noisy and null.</p>
{'<h3>PISA 2022: school phone rules and well-being within countries</h3>' + (ROOT/'build/sections/pisa.html').read_text() if (ROOT/'build/sections/pisa.html').exists() else '<p class="pending">PISA 2022 within-country comparison of students in schools with and without phone rules: pending the microdata extraction.</p>'}
"""
(SEC/"bans.html").write_text(bans_html)

figjson = {k: json.loads(v.to_json()) for k, v in figs.items()}
extra = {}
import shutil
for hand in (ROOT/"scripts/report/sections").glob("*.html"): shutil.copy(hand, SEC/hand.name)
for name in ["validation","lte","policy","hbsc","gshs","ntia","mics","reconcile","bans","policy_inter","usdose_adopt","usdose_rttt","ss_trends","ss_tests","h3"]:
    p = ROOT/f"build/sections/{name}.html"; extra[name] = p.read_text() if p.exists() else f'<p class="pending">Pending: this section fills in when the {name} inputs arrive.</p>'
    if name in ("validation","lte","policy","policy_inter","usdose_rttt","ntia","mics","gshs","hbsc","bans"):
        extra[name] = extra[name].replace("<h4>", "<h5>").replace("</h4>", "</h5>").replace("<h3>", "<h4>").replace("</h3>", "</h4>").replace("<h3 id=", "<h4 id=")

html = f"""<title>Teen Distress Pilot</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.3/plotly.min.js"></script>
<style>
:root{{--bg:#f4f6f9;--surface:#ffffff;--ink:#1a2130;--muted:#5d6675;--rule:#d6dbe3;--accent:#2a78d6;--girl:#eb6834;--boy:#2a78d6;--soft:#e9eef5;--warn:#b45309;--good:#0f7a4a;color-scheme:light}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#15181e;--surface:#1d2129;--ink:#e6e8ec;--muted:#a3a9b4;--rule:#2f3540;--accent:#3987e5;--girl:#f07a4a;--boy:#3987e5;--soft:#242a34;--warn:#f0a04b;--good:#4fc38a;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#15181e;--surface:#1d2129;--ink:#e6e8ec;--muted:#a3a9b4;--rule:#2f3540;--accent:#3987e5;--girl:#f07a4a;--boy:#3987e5;--soft:#242a34;--warn:#f0a04b;--good:#4fc38a;color-scheme:dark}}
body{{background:var(--bg);color:var(--ink);font-family:'Source Serif 4',Georgia,serif;font-size:16px;line-height:1.55;margin:0;padding-block:0 64px;padding-inline:16px}}
.wrap{{max-width:960px;margin:0 auto}}
h1,h2,h3,h4,h5{{font-family:'IBM Plex Sans',system-ui,sans-serif;text-wrap:balance;line-height:1.2;margin:0}}
h1{{font-size:2rem;font-weight:600;margin-top:40px}} h2{{font-size:1.35rem;font-weight:600;margin-top:56px;padding-top:16px;border-top:1px solid var(--rule)}} h3{{font-size:1.05rem;font-weight:600;margin-top:28px}} h4{{font-size:1rem;font-weight:600;margin-top:24px}} h5{{font-size:.92rem;font-weight:500;margin-top:18px;color:var(--muted)}}
p{{max-width:68ch;margin:12px 0}} .lede{{font-size:1.1rem;color:var(--muted);max-width:68ch}}
.eyebrow{{font-family:'IBM Plex Sans',sans-serif;font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:32px}}
nav{{position:sticky;top:env(safe-area-inset-top,0px);background:var(--bg);border-bottom:1px solid var(--rule);padding:8px 0;margin:24px -16px 0;padding-inline:16px;z-index:5;font-family:'IBM Plex Sans',sans-serif;font-size:.85rem;display:flex;gap:14px;flex-wrap:wrap}}
nav a{{color:var(--muted);text-decoration:none}} nav a:hover,nav a:focus{{color:var(--accent);outline:none;text-decoration:underline}}
.chart{{width:100%;min-height:300px;margin:16px 0;background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:8px}}
.tw{{overflow-x:auto;margin:12px 0}} table{{border-collapse:collapse;font-family:'IBM Plex Sans',sans-serif;font-size:.86rem;font-variant-numeric:tabular-nums;min-width:520px}} th,td{{padding:6px 10px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}} th{{background:var(--soft);font-weight:500}} td:nth-child(n+3),th:nth-child(n+3){{text-align:right}}
.verdict td:first-child{{font-weight:500}} .verdict td{{text-align:left}}
.pill{{display:inline-block;font-family:'IBM Plex Sans',sans-serif;font-size:.72rem;letter-spacing:.04em;padding:2px 8px;border-radius:10px;background:var(--soft);color:var(--ink)}} .pill.for{{color:var(--good)}} .pill.against{{color:var(--warn)}}
.pending{{color:var(--muted);font-style:italic;border-left:3px solid var(--rule);padding-left:12px}}
.note{{background:var(--soft);border-radius:6px;padding:12px 16px;max-width:72ch;font-size:.95rem}}
.caption{{font-family:'IBM Plex Sans',sans-serif;font-size:.82rem;color:var(--muted);max-width:80ch;margin:-8px 0 20px}}
code{{font-family:'IBM Plex Mono',monospace;font-size:.85em;background:var(--soft);padding:1px 4px;border-radius:3px}}
@media (max-width:600px){{h1{{font-size:1.5rem}} .chart{{padding:2px}}}}
</style>
<div class="wrap">
<div class="eyebrow">Public-data pilot · smartphones vs. school pressure · updated 2026-09-17</div>
<h1>Teen Distress Pilot</h1>
<p class="lede">Two recent accounts offer competing explanations for the post-2010 rise in adolescent anxiety and depression: Jonathan Haidt's <em>The Anxious Generation</em> attributes the shift to smartphones and social media, while Peter Gray points to intensified schooling and declining autonomy. This pilot report asks how far large-scale public microdata can go toward separating those hypotheses before any restricted or licensed datasets are requested. Every figure and table is computed from public microdata (ACS, ATUS, MICS, PISA, GSHS, IPUMS International) and published survey series.</p>
<nav><a href="#hyp">Hypotheses</a><a href="#verdict">Summary</a><a href="#part1">1 · The rise</a><a href="#part2">2 · Phones</a><a href="#part3">3 · School pressure</a><a href="#part4">4 · Interaction &amp; bans</a><a href="#reconcile">Haidt &amp; Twenge</a><a href="#next">Answer</a></nav>

<h2 id="hyp">The four hypotheses</h2>
<p>The study is organized around four candidate explanations, with each empirical test designed to distinguish between at least two of them.</p>
<div class="tw"><table class="verdict"><thead><tr><th>Hypothesis</th><th>Claim</th><th>What it predicts in these data</th></tr></thead><tbody>
<tr><td>H1 · Phones and social media (Haidt, Twenge)</td><td>Smartphone-based social media, arriving between 2010 and 2013, caused the rise in adolescent distress, particularly among girls.</td><td>Distress rises earlier where smartphones and fast mobile data arrive first; increases are much larger for girls than for boys; distress rises in developing countries as mobile internet spreads; heavy users report worse outcomes; school phone bans reduce distress.</td></tr>
<tr><td>H2 · School pressure (Gray)</td><td>Accountability testing, heavier homework loads, and reduced free play made schooling more stressful from around 2010 onward.</td><td>No difference by local mobile-network timing; girls affected somewhat more than boys; increases concentrated in the high-stakes high-school years (15–17) and during the school year; distress rises where perceived schoolwork pressure rises; state accountability reforms (Race to the Top, Common Core testing) predict state outcomes.</td></tr>
<tr><td>H3 · Interaction</td><td>Smartphones are most harmful when combined with high-stakes schooling—social comparison and notifications running through the same school hours that carry tests and grades—so that removing phones from the school day brings disproportionate relief.</td><td>Both academic pressure and phone use rise after 2010; mobile-rollout effects are larger in high-pressure settings; school phone bans improve well-being, especially for academically anxious students; out-of-school screen use matters less.</td></tr>
<tr><td>H0 · Reporting or measurement drift</td><td>The observed rise largely reflects changing diagnostic thresholds, mental-health awareness, or survey reporting norms.</td><td>Older adults (including the 65+ comparison group) trend upward in the same way; behavioral, clinical, and self-report series diverge; no geographic or dose-response pattern appears.</td></tr>
</tbody></table></div>

<h2 id="verdict">Summary: what the public microdata support today</h2>
<p>Each row summarizes one empirical test from the pilot, grouped by the hypothesis it addresses most directly. Full specifications, data sources, and caveats follow in Parts 1–4.</p>
<div class="tw"><table class="verdict"><thead><tr><th>What was measured</th><th>What the pilot found</th><th>Relevant to</th></tr></thead><tbody>
<tr><td colspan="3"><strong>Is there a real rise, and is the outcome usable? (H0)</strong></td></tr>
<tr><td>65+ comparison group and adult trends</td><td>The ACS cognitive-difficulty rate falls steadily for adults 65+ (12.2% → 9.4% between 2008 and 2019) and is flat at ages 50–64 while rising for all age groups under 50, ruling out generic survey-wide response drift.</td><td><span class="pill for">against H0</span></td></tr>
<tr><td>Agreement across measures</td><td>Clinical depression interviews (NSDUH), persistent sadness (YRBS), and the ACS cognitive-difficulty item all turn upward between 2011 and 2013, with girls rising faster in every source; within-state changes move together. However, the ACS item captures only about a sixth of the proportional rise in depression.</td><td><span class="pill for">real rise; ACS usable but weak</span></td></tr>
<tr><td>Subgroup gradient</td><td>Relative increases in the ACS item are steepest among affluent, private-school, Hispanic, Asian, and foreign-born teens, and smallest among low-income teens—a pattern consistent with both early smartphone adoption and differential diagnosis-seeking.</td><td><span class="pill">ambiguous</span></td></tr>
<tr><td colspan="3"><strong>Phones and social media (H1)</strong></td></tr>
<tr><td>Sex pattern</td><td>Girls' relative increase exceeds boys' across all sources: ACS +17% vs. +9% (2008–10 → 2017–19), YRBS sadness +26% vs. +19%, and post-2020 ACS increases of +45–55% for girls vs. +16–23% for boys.</td><td><span class="pill for">H1 / H3</span></td></tr>
<tr><td>Timing in early vs. late LTE markets</td><td>No rollout-timing effect. Early- and late-LTE metropolitan areas track each other closely through 2013; the static DiD estimate is +0.02 pp (SE 0.15) across 279 dated metros and −0.04 pp (SE 0.19) for girls, with similarly null results across county panels in six state youth surveys.</td><td><span class="pill against">not H1 via rollout timing</span></td></tr>
<tr><td>U.S. smartphone adoption</td><td>State-level teen-household smartphone-internet share predicts YRBS girls' sadness within states (+0.90 pp per 10 points, SE 0.44), but metro adoption does not predict sadness at the county level (+0.13 pp overall across five states, SE 0.13; +0.22 pp for girls in California and Maine, SE 0.25).</td><td><span class="pill">weak H1</span></td></tr>
<tr><td>Phone-first countries, adult- or cluster-measured exposure</td><td>MICS (67 surveys with valid responses): caregiver-reported anxiety and depression show no meaningful relation to local young-adult connectivity or a teenage girl's own daily phone/internet use; the small positive cluster correlation for girls' anxiety also appears among 5–9-year-olds. GSHS (34 countries): no within-country relation to national internet users, mobile-broadband subscriptions, or 3G/4G coverage. Census cognitive-difficulty items in Kenya and Mexico are uninformative.</td><td><span class="pill against">not H1 on adult- or cluster-measured use</span></td></tr>
<tr><td>Adolescent self-reported phone hours</td><td>GSHS 2022–23 (five countries): girls using a phone 3+ hours/day report loneliness +8.2 pp and suicidal ideation +10.1 pp higher than lighter users, rising monotonically with hours; effects for boys are roughly half as large. Nepal 2022 DHS PHQ-9/GAD-7 self-reports point in the same direction for 15–19-year-old women. Cross-sectional self-reports, leaving causal direction open.</td><td><span class="pill for">H1 pattern, not timing</span></td></tr>

<tr><td colspan="3"><strong>School pressure (H2)</strong></td></tr>
<tr><td>Age pattern and time use</td><td>Through 2019, the ACS increases at ages 12–14 and 15–17 are similar and 18–24 rises faster, showing no high-stakes high-school signature (seasonality is not available in public ACS files). In ATUS, school-weekday homework time rose nearly 40% (from ~50 to ~71 minutes) between 2003–08 and 2015–19 while sleep held steady and in-person socializing fell.</td><td><span class="pill for">school demand rose</span> (H2 premise)</td></tr>
<tr><td>HBSC schoolwork pressure</td><td>Perceived schoolwork pressure and psychosomatic complaints both rose after 2009/10 across ~45 countries, and complaints rose more where pressure rose more (slope 0.14–0.24). However, the within-country slope is identical in the 2002–2010 baseline period, and most of the post-2010 increase is common across countries.</td><td><span class="pill">H2 partly</span> pressure is a stable correlate, not the break</td></tr>
<tr><td>State accountability policy</td><td>ESEA waivers, Common Core–aligned testing, test-based teacher evaluation, and exit exams show no positive relation to ACS, YRBS, or NSDUH distress; the apparent static Race to the Top coefficient disappears in an event study around the award year.</td><td><span class="pill against">not H2 via U.S. policy shocks</span></td></tr>
<tr><td colspan="3"><strong>Interaction (H3)</strong></td></tr>
<tr><td>LTE × school pressure</td><td>Early-LTE metros inside high-accountability states did not experience a larger rise in the ACS item; where identified, the interaction point estimates for girls are negative.</td><td><span class="pill against">not H3 via state policy</span></td></tr>
<tr><td>School phone bans</td><td>PISA 2022 (80 systems): school phone bans reduce daily in-school smartphone use by 12.1 pp and reported classroom distraction by 3.5 pp; girls in ban schools report 1.4 pp less loneliness, 2.0 pp less device anxiety, and +0.02–0.03 SD higher belonging and life satisfaction. Cross-sectional comparison across schools. Nationally, U.S. school prohibitions fell from 91% to 66% during 2009–16 and re-tightened after 2016 as sadness rose and then fell.</td><td><span class="pill for">H1 / H3 direction, small; U.S. test pending</span></td></tr>
<tr><td>Bans × academic pressure</td><td>PISA 2022: the association between school phone bans and lower loneliness is larger for students with above-median mathematics anxiety—the available proxy for academic pressure—(girls −1.15 vs. −0.27 pp; boys −0.81 vs. +1.12 pp), though the interaction is imprecisely estimated.</td><td><span class="pill">H3 direction, not established</span></td></tr>
</tbody></table></div>

<h2 id="part1">Part 1 · The rise, and whether public data can measure it</h2>
<p>Testing either hypothesis requires first establishing the outcome in public data: verifying that adolescent distress rose after 2010, checking whether the increase reflects a genuine shift rather than survey reporting drift, and evaluating how closely the Census disability screener tracks clinical depression and self-reported sadness. This section combines the American Community Survey with national mental-health surveys (NSDUH, YRBS, NHANES) and county-level state youth surveys.</p>
<h3 id="acs">The ACS cognitive-difficulty item, 2008–2024</h3>
<p>The American Community Survey asks of every household member aged 5 and older whether the person has "serious difficulty concentrating, remembering, or making decisions" because of a physical, mental, or emotional condition. The question wording has been unchanged since 2008 (2005–07 used different wording and is excluded). Each annual wave samples roughly 240,000 adolescents aged 12–17. All standard errors are computed using the 80 Census successive-difference replicate weights.</p>
{fig_div('acs_levels')}
<p class="caption">Shaded bands are 95% confidence intervals. The grey band marks the 2020 experimental ACS release, which suffered from pandemic-related nonresponse bias.</p>
<div class="tw"><table><thead><tr><th>Age</th><th>Sex</th><th>2008–10 %</th><th>2017–19 %</th><th>Rel. change</th><th>2022–24 %</th><th>Rel. change</th></tr></thead><tbody>{sexrows}</tbody></table></div>
<h4>Age gradient</h4>
{fig_div('acs_index')}
<p class="caption">Each series plots the age group's rate indexed to its own 2008–10 mean (= 100). Thick lines highlight the adolescent age groups (12–14 and 15–17).</p>
<p>The ACS age series establish two basic facts. First, the pre-pandemic 2010s increase in cognitive difficulty is statistically clear but modest in absolute terms (about half a percentage point on a baseline of 3–5%), and it appears across all age groups under 50—rising fastest among 18–24-year-olds—while falling steadily among adults 65 and older. Second, the post-2020 surge is much steeper and is heavily concentrated among girls and young women. Because the ACS question is a severe disability screener, it will miss mood or anxiety disorders that do not impair daily concentration; the next section evaluates how well it tracks direct measures of adolescent depression.</p>


<h3 id="gates">Does the ACS item measure adolescent distress?</h3>
{extra['validation']}


<h3 id="geo">Geographic variation: is there anything to explain?</h3>
<p>For a geographic rollout design to have statistical power, 2010s changes in adolescent distress must vary across local markets by more than sampling noise. Grouping the ACS into metropolitan areas (plus each state's non-metro remainder), the weighted mean change from 2008–10 to 2017–19 among 12–17-year-olds is +0.47 percentage points, the estimated true between-market standard deviation is 0.46 points, and the median market-level sampling error is 0.64 points (Cochran's Q = 218 on 116 df, I² ≈ 0.47). Real cross-market differences exist, but individual metro estimates are noisy and must be pooled in regression models.</p>
{fig_div('market_funnel')}
<p class="caption">117 markets with at least 1,500 sampled 12–17-year-olds in 2008–10. Dashed curves show the ±1.96 SE funnel around the pooled mean for a market of a given sample size.</p>
<h4>States, by sex</h4>
<p>Disaggregating state-level changes by sex reveals a major constraint for U.S. geographic designs: while boys' changes vary substantially across states (I² ≈ 0.46), girls' changes are nearly uniform nationwide (I² ≈ 0.05). Because the female series is the component that reflects internalizing distress, there is very little cross-state variation in the ACS for either a phone-rollout or a school-policy design to exploit.</p>
{fig_div('state_caterpillar')}
<h4>Who is driving the rise</h4>
<p>Relative changes by demographic and socioeconomic subgroup, ages 12–17. The largest proportional increases occur among adolescents in higher-income families and private schools.</p>
{comp_html}


{extra['ss_trends']}

<h2 id="part2">Part 2 · Phones and social media (H1)</h2>
<p>The phone hypothesis predicts that adolescent distress rose earlier in places where smartphones and fast mobile data arrived first, that heavier users experience worse mental health, and that similar patterns hold in developing countries where mobile phones are the primary way young people go online. The tests below move from coarse geographic exposure (metro 4G launch dates and state adoption shares) to individual-level exposure in low- and middle-income countries.</p>
<h3 id="lte">4G rollout across U.S. metros</h3>
<p>If the arrival of fast mobile data drove the initial upturn in adolescent distress, teenagers in metropolitan areas that received commercial 4G LTE earliest should have experienced an earlier rise in cognitive difficulty and sadness.</p>
{extra['lte']}


{extra['ss_tests']}
{extra['usdose_adopt']}
<h3>Smartphone adoption in the United States, 2009–2023</h3>
{extra['ntia']}
<h3>Phone-first countries: MICS Child Functioning Module (68 surveys, 2017–2024)</h3>
{extra['mics']}
<h3>Phone-first countries: GSHS school surveys (149 country-rounds, 2003–2023)</h3>
{extra['gshs']}
<h3>Phone-first countries: census microdata (IPUMS International)</h3>
<p>We also examined the 2009/2019 Kenya and 2010/2020 Mexico census pairs in IPUMS International, the two best candidates carrying disability items alongside connectivity measures. Both 2020-round censuses include the Washington Group question on difficulty remembering or concentrating, and the 2019 Kenya census asks each person directly about mobile-phone ownership and internet use. However, the 2010-round censuses asked narrow yes/no questions about "mental disability," so changes between the 2010 and 2020 rounds are dominated by questionnaire wording. Within the 2019/2020 cross-sections, cognitive-difficulty prevalence at ages 12–17 is low (0.8–1.8% for any difficulty and 0.2–0.7% for "a lot of difficulty" or "cannot do at all"), boys exceed girls at every age, and subnational regressions of the 12–17 rate on adolescent phone ownership or internet use across 76 Kenyan district-sex cells or on household internet across 3,259 Mexican municipality-sex cells yield coefficients within ±0.01 pp per percentage point of phone ownership or internet access. In developing-country censuses, this item behaves like a measure of severe developmental disability and is insensitive to adolescent internalizing distress.</p>


<h2 id="part3">Part 3 · School pressure (H2)</h2>
<p>The school-pressure hypothesis predicts that adolescent distress rose when and where academic demands intensified: during the high-stakes high-school years, in states that introduced test-based accountability reforms, and in countries where students report rising schoolwork pressure. We test this channel using U.S. adolescent time-use diaries, the cross-national HBSC schoolwork-pressure series, and state accountability policy timelines.</p>
<h3 id="atus">Did school demands rise? Time use of 15–17-year-olds (ATUS, 2003–2024)</h3>
<p>The American Time Use Survey (ATUS) measures how U.S. 15–17-year-olds allocate their time on school-year weekdays. Between 2003–08 and 2015–19, average weekday homework time rose from roughly 50 minutes to 71 minutes per day (+40%) and remained near 69 minutes through 2023–24. Over the same period, sleep duration did not decline (averaging 8.7–9.1 hours), in-person socializing drifted downward before dropping sharply after 2020, television viewing fell, and time spent playing computer or video games more than doubled. Sample sizes are modest (roughly 100 to 800 teens per pooled period), and because ATUS records only primary activities, background smartphone checking during homework or socializing is not captured.</p>
{fig_div('atus')}
<p class="caption">Weighted minutes per day on non-holiday weekdays during the school year (September–May), pooled periods; vertical bars show 95% confidence intervals.</p>


<h3>Schoolwork pressure across countries (HBSC)</h3>
{extra['hbsc']}
<h3 id="policy">U.S. school accountability policy</h3>
<p>In the United States, states adopted test-based accountability reforms on staggered schedules between 2009 and 2017; if those policy shifts drove adolescent distress, states implementing them should show corresponding increases in youth depression and sadness.</p>
{extra['policy']}
{extra['usdose_rttt']}



<h2 id="part4">Part 4 · The interaction (H3): phones in the same hours as high-pressure school</h2>
{extra['h3']}
<h3>Did 4G timing matter more in high-pressure states?</h3>
{extra['policy_inter']}
<h3 id="bans">School phone bans</h3>
{extra['bans']}

<h2 id="reconcile">How this sits with Haidt's and Twenge's evidence</h2>
{extra['reconcile']}

<h2 id="next">Conclusions and next steps</h2>
<p>Combining public microdata across the United States and more than 80 other countries narrows the debate in several ways while leaving the core causal question open.</p>
<div class="tw"><table class="verdict"><thead><tr><th>Hypothesis</th><th>Where it stands after the pilot</th></tr></thead><tbody>
<tr><td>H1 · Phones and social media</td><td>The cross-sectional individual association is robust and extends to developing countries: teenage girls who use mobile phones heavily report substantially higher loneliness and suicidal ideation in Ghana, India, Jamaica, Morocco, and Nepal just as in Western surveys, with the same sex asymmetry and dose-response gradient. Yet every test based on rollout timing or adult- and cluster-measured exposure is null: 4G launch dates across U.S. metros and counties, metro adoption rates in the county panels, cluster connectivity and own use in 67 MICS caregiver surveys, and national 3G/4G coverage in 34 GSHS countries. Either the causal effect operates through peer norms and national platforms too uniformly for subnational timing designs to detect, or the individual correlation largely reflects reverse causation and shared vulnerabilities. School phone bans in PISA 2022 and Norway provide modest evidence of a girl-specific benefit.</td></tr>
<tr><td>H2 · School pressure</td><td>The descriptive premise of Gray's account holds up better than critics often acknowledge: perceived schoolwork pressure rose after 2010 across most HBSC countries, and U.S. weekday homework time rose by roughly 40%. However, perceived pressure behaves like a steady correlate of psychosomatic complaints (with the same within-country slope before and after 2010) rather than the driver of the post-2010 break; U.S. state accountability reforms show no effect; and the ACS age gradient does not peak in the high-stakes high-school years. A key constraint is measurement: public U.S. surveys lack longitudinal school-level pressure items, making H2 harder to test subnationally than H1.</td></tr>
<tr><td>H3 · Interaction</td><td>State accountability policies interacted with metro 4G launch dates show no positive effect on the ACS item, but the school-day version of the interaction hypothesis—smartphones operating inside high-pressure school hours—is consistent with the school-ban evidence: bans reduce daily in-school phone use and classroom distraction, girls in ban schools report lower loneliness and device anxiety, the loneliness reduction is directionally larger among students with high mathematics anxiety, Norway's middle-school bans reduced girls' psychological consultations, and U.S. adolescent sadness moved inversely to national school phone restrictions.</td></tr>
<tr><td>H0 · Measurement</td><td>Ruled out as the primary explanation: the post-2010 rise appears simultaneously across diagnostic interviews, self-report school surveys, and the ACS cognitive-difficulty item; the 65+ comparison group trends downward over the same decade; and the increase is consistently concentrated among girls. Differential awareness and diagnosis-seeking likely contribute to the steeper relative rise among affluent and private-school teens, but do not account for the overall trend.</td></tr>
</tbody></table></div>
<p>Three empirical findings from the pilot stand out beyond the existing book-length arguments. First, the 2010s rise in adolescent distress occurred almost simultaneously across U.S. states and counties with very different mobile-rollout and school-policy timelines, which explains why coarse geographic designs struggle to separate the competing hypotheses and why national time series can be cited in support of either view. Second, post-2021 waves of the U.S. state youth surveys show a substantial decline in sadness and suicidal ideation—returning to or below 2010 levels in Washington and Illinois—without a matching drop in daily phone or social-media use, coinciding instead with the re-tightening of school phone rules. Any purely dose-based account of screen time or school pressure has to account for that downturn. Third, across developing-country surveys, the link between phone use and distress appears consistently when adolescents report both their own hours and their own symptoms (GSHS, Nepal DHS), but vanishes when symptoms are reported by caregivers (67 MICS surveys). Resolving why self-reports and caregiver reports diverge is central to the next phase of work.</p>
<div class="note"><strong>Priority next steps for Phase 2.</strong>
<ul>
<li>Track the 2023–27 U.S. state and district school phone bans through the 2025–27 YRBS and county youth survey waves, separately by sex and across at least two post-ban years, retaining the 65+ comparison group. The 51-state policy table and panel code are in place; the 2025 YRBS state files will provide the first post-ban wave.</li>
<li>License GSMA mobile-coverage polygons and request MICS and DHS cluster coordinates to test adolescent-reported phone use and mental health (GSHS 2022–23, incoming MICS7 rounds, and DHS-8 mental-health modules) against local network rollout timing.</li>
<li>Request the student-level HBSC microdata to test whether psychosomatic complaints became more concentrated among high-pressure students after 2010 and to estimate the student-level interaction between problematic social-media use, schoolwork pressure, and school phone rules.</li>
<li>Further extensions of the ACS market event study or the IPUMS International census cognitive-difficulty item are unlikely to add much; both measures are too coarse for a geographic timing design. Federal Statistical Research Data Center (FSRDC) applications for restricted NSDUH or NHANES geocodes should wait until the state-survey or phone-ban evaluations establish a clearer subnational signal.</li>
</ul></div>
<p class="caption">Reproducibility: analysis scripts are in <code>scripts/</code> and output tables are in <code>results/tables/</code> of the project repository. Data sources: IPUMS USA (ACS 1-year 2005–2024), IPUMS ATUS 2003–2024, IPUMS MICS (68 surveys), IPUMS International (Kenya 2009/2019, Mexico 2010/2020), Census CPS Computer and Internet Use Supplements (2009–2023), OECD PISA 2022, WHO GSHS (165 country-rounds), WHO HBSC, DHS-8 (Nepal 2022, Kenya 2022), and public NSDUH, NHANES, YRBS, NCES SSOCS/School Pulse, and state youth survey files as documented in each section.</p>
</div>
<script>
const FIGS = {json.dumps(figjson)};
function ink(){{ const cs = getComputedStyle(document.documentElement); return {{ink: cs.getPropertyValue('--ink').trim(), muted: cs.getPropertyValue('--muted').trim(), rule: cs.getPropertyValue('--rule').trim()}}; }}
function draw(){{ const c = ink();
  for (const [k, f] of Object.entries(FIGS)) {{ const el = document.getElementById('fig-'+k); if (!el) continue;
    const lay = Object.assign({{}}, f.layout, {{font: Object.assign({{}}, f.layout.font, {{color: c.ink}}), autosize: true}});
    for (const key of Object.keys(lay)) if (key.startsWith('xaxis')||key.startsWith('yaxis')) lay[key] = Object.assign({{}}, lay[key], {{color: c.ink, linecolor: c.rule}});
    if (lay.annotations) lay.annotations = lay.annotations.map(a => Object.assign({{}}, a, {{font: Object.assign({{}}, a.font||{{}}, {{color: c.ink}})}}));
    Plotly.react(el, f.data, lay, {{displayModeBar: false, responsive: true}}); }} }}
draw(); window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw); new MutationObserver(draw).observe(document.documentElement, {{attributes: true, attributeFilter: ['data-theme']}});
</script>
"""
OUT.write_text(html); print("wrote", OUT, f"{OUT.stat().st_size/1e6:.2f} MB")
