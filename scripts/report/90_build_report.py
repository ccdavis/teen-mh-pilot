"""Build build/report.html (the pilot report artifact) from results/tables and notes. Re-run after each new result."""
import json, pathlib, pandas as pd, numpy as np, plotly.graph_objects as go
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
        fig.add_trace(go.Scatter(x=list(d.year)+list(d.year[::-1]), y=list(d.rate+1.96*d.se)+list((d.rate-1.96*d.se)[::-1]), fill="toself", fillcolor=col.replace(")",",.15)").replace("#","rgba(") if False else None, line=dict(width=0), hoverinfo="skip", showlegend=False, opacity=.18, marker=dict(color=col)), row=1, col=c)
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
fig.update_xaxes(title_text="Change, 2008–10 → 2017–19 (pp)"); fig.update_yaxes(tickfont=dict(size=9)); figs["state_caterpillar"] = base(fig, h=900, hovermode="closest")

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
figjson = {k: json.loads(v.to_json()) for k, v in figs.items()}

# tables
comp = pd.read_csv(T/"acs_composition_povgrp.csv")
def comp_rows(fname, label):
    d = pd.read_csv(T/fname); d = d[d.iloc[:,0]!="n/a"]
    rows = []
    for _, r in d.iterrows():
        rows.append(f"<tr><td>{r.iloc[0]}</td><td>{'girls' if r.sex==2 else 'boys'}</td><td>{r['2008-10']:.2f}</td><td>{r['2017-19']:.2f}</td><td>{r['rel_chg_1719']:+.0f}%</td><td>{r['rel_chg_2224']:+.0f}%</td><td>{r['share_pop_0810']:.0f}%</td></tr>")
    return f"<h4>{label}</h4><div class='tw'><table><thead><tr><th>Group</th><th>Sex</th><th>2008–10 %</th><th>2017–19 %</th><th>Rel. change to 2017–19</th><th>Rel. change to 2022–24</th><th>Share of 12–17, 2008–10</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
comp_html = comp_rows("acs_composition_povgrp.csv", "By family income relative to poverty line") + comp_rows("acs_composition_schltype.csv", "By school type") + comp_rows("acs_composition_raceeth.csv", "By race / ethnicity")

nat1217 = pd.read_csv(T/"acs_national_year_sex_age.csv"); nat1217 = nat1217[nat1217.agegrp.isin(["12-14","15-17"])]
def per(y0,y1,sx,ag): d = nat1217[(nat1217.year.between(y0,y1))&(nat1217.sex==sx)&(nat1217.agegrp==ag)]; return 100*np.average(d.rate, weights=d["pop"])
sexrows = "".join(f"<tr><td>{ag}</td><td>{s}</td><td>{per(2008,2010,sx,ag):.2f}</td><td>{per(2017,2019,sx,ag):.2f}</td><td>{100*(per(2017,2019,sx,ag)/per(2008,2010,sx,ag)-1):+.0f}%</td><td>{per(2022,2024,sx,ag):.2f}</td><td>{100*(per(2022,2024,sx,ag)/per(2008,2010,sx,ag)-1):+.0f}%</td></tr>" for ag in ["12-14","15-17"] for sx,s in [(1,"boys"),(2,"girls")])


# ---- validation section
SEC = ROOT/"build/sections"; SEC.mkdir(exist_ok=True)
V = pd.read_csv(T/"validation_national_timing.csv")
srcs = [("NSDUH MDE 12-17","NSDUH: depression 12–17"),("YRBS sad/hopeless","YRBS: sad/hopeless"),("YRBS considered suicide","YRBS: considered suicide"),("ACS cognitive difficulty 12-17","ACS: cognitive difficulty"),("NHANES PHQ-9 ≥10, 18-24","NHANES: PHQ-9 ≥10, 18–24")]
fig = make_subplots(rows=1, cols=5, subplot_titles=[t for _,t in srcs], horizontal_spacing=0.045)
for c,(src,_) in enumerate(srcs, start=1):
    for sexlab, col in [("all",ALL),("boys",BOY),("girls",GIRL)]:
        d = V[(V.source==src)&(V.sex==sexlab)].sort_values("year")
        if len(d)==0: continue
        fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines+markers", line=dict(color=col, width=2), marker=dict(size=5), error_y=dict(type="data", array=1.96*d.se, color=col, thickness=1), name=sexlab, showlegend=(c==2 or (c==1 and sexlab=="all")), hovertemplate="%{y:.1f}%<extra>"+sexlab+"</extra>"), row=1, col=c)
    d2 = V[(V.source=="NSDUH MDE 12-17 (2021+ mode)")&(V.sex=="all")]
    if src.startswith("NSDUH") and len(d2): fig.add_trace(go.Scatter(x=d2.year, y=d2.value, mode="markers", marker=dict(color=ALL, size=6, symbol="diamond-open"), name="2021+ (new mode)", hovertemplate="%{y:.1f}%<extra>2021+ mode</extra>"), row=1, col=c)
    fig.update_xaxes(range=[2004,2025], row=1, col=c); fig.update_yaxes(rangemode="tozero", row=1, col=c); covid_band(fig, row=1, col=c)
fig.update_annotations(font_size=11); figs["val_timing"] = base(fig, h=380, hovermode="closest")
Cst = pd.read_csv(T/"validation_state_change.csv")
fig = go.Figure(go.Scatter(x=Cst.d_acs, y=Cst.d_nsduh, mode="markers+text", text=[ST.get(int(x),"?")[:2] if False else "" for x in Cst.statefip], marker=dict(color=ALL, size=8), customdata=[ST.get(int(x),str(x)) for x in Cst.statefip], hovertemplate="%{customdata}<br>ACS Δ %{x:.2f} pp<br>NSDUH Δ %{y:.2f} pp<extra></extra>", name="State"))
b = np.polyfit(Cst.d_acs, Cst.d_nsduh, 1); xs = np.linspace(Cst.d_acs.min(), Cst.d_acs.max(), 10); fig.add_trace(go.Scatter(x=xs, y=np.polyval(b, xs), mode="lines", line=dict(color=MUTED, dash="dash"), showlegend=False, hoverinfo="skip"))
fig.update_xaxes(title_text="ACS cognitive difficulty 12–17, change 2008–10 → 2017–19 (pp)"); fig.update_yaxes(title_text="NSDUH youth MDE, change (pp)"); figs["val_state"] = base(fig, h=420, hovermode="closest", showlegend=False)
def rc(src, sex, y0, y1):
    d = V[(V.source==src)&(V.sex==sex)]; bb = d[d.year.between(*y0)].value.mean(); ee = d[d.year.between(*y1)].value.mean(); return bb, ee, 100*(ee/bb-1)
sexcmp = "".join(f"<tr><td>{lab}</td><td>{sx}</td><td>{rc(src,sx,(2009,2011.9),(2017,2019.9))[0]:.1f}</td><td>{rc(src,sx,(2009,2011.9),(2017,2019.9))[1]:.1f}</td><td>{rc(src,sx,(2009,2011.9),(2017,2019.9))[2]:+.0f}%</td></tr>" for src,lab in [("ACS cognitive difficulty 12-17","ACS cognitive difficulty 12–17"),("YRBS sad/hopeless","YRBS sad/hopeless"),("YRBS considered suicide","YRBS considered suicide"),("NHANES PHQ-9 ≥10, 18-24","NHANES PHQ-9 ≥10, 18–24")] for sx in ["boys","girls"])
val_html = f"""
<p>Three checks: (a) does the ACS item move with a real depression measure at the state level, (b) is its rise concentrated in girls, (c) does its national timing match the survey series. The public NHANES depression screener covers ages 18+ only (the adolescent file is restricted), so NHANES enters as an 18–24 check.</p>
<h3>National timing</h3>
{fig_div('val_timing')}
<p class="caption">All series in percent, with 95% CIs. NSDUH points sit at the midpoint of each two-year period; the 2021+ NSDUH estimates use a new web mode and DSM-5 wording and are not comparable to earlier years. YRBS sad/hopeless was first asked in 1999.</p>
<p>NSDUH youth depression was flat at about 8% from 2005 through 2010–11 and then rose almost every period to 15% in 2018–19. YRBS sadness was flat from 1999 to 2013, then rose sharply in 2017–2019. The ACS item rises gradually from 2012 and accelerates after 2019. The ACS series turns up at roughly the right time but its amplitude is a fraction of NSDUH's: about +13% relative versus +85%.</p>
<h3>Sex pattern (check b)</h3>
<div class="tw"><table><thead><tr><th>Series</th><th>Sex</th><th>2009–11</th><th>2017–19</th><th>Relative change</th></tr></thead><tbody>{sexcmp}</tbody></table></div>
<p>In every source the girls' relative rise exceeds the boys'. The ACS item passes this check: if it were mainly picking up ADHD diagnoses, the boys' change would dominate.</p>
<h3>Do states move together? (check a)</h3>
{fig_div('val_state')}
<p class="caption">51 states. Each point is the state's change in both measures between 2008–10 and 2017–19; dashed line is the OLS fit (slope 0.55, SE 0.21, r = 0.32).</p>
<p>Across states there is no relation between the levels of the two measures (the ACS item is a disability screener, NSDUH is a diagnostic interview), but their <em>changes</em> are related: a state-and-period fixed-effects regression of NSDUH youth MDE on the ACS rate gives a slope of 0.14 (SE 0.05, p = 0.01) across 714 state-by-period observations, and the decade-long changes correlate at 0.32. Against the YRBS state files (39 states, by sex), the ACS rate moves together with "sad or hopeless" at a slope of 0.35 (SE 0.18) with state-by-sex and year-by-sex effects, and not at all with "considered suicide."</p>
<div class="note"><strong>Conclusion.</strong> The ACS item passes the sex check and moves, weakly but genuinely, with depression within states. It can serve as one main outcome, with two caveats: it captures perhaps a sixth of the depression rise, and the part of its change that is specific to girls is small relative to sampling error. The state youth surveys (the YRBS state files here, and the county surveys later in the report) deserve equal standing rather than a supporting role.</div>
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
fig.update_xaxes(title_text="% of persons in households with a 12–17-year-old who use a smartphone for internet"); fig.update_yaxes(tickfont=dict(size=9)); figs["ntia_state"] = base(fig, h=820, hovermode="closest")
ntia_html = f"""
<p>IPUMS CPS carries only part of the Computer and Internet Use Supplement (no mobile items), so the raw Census supplement files for October 2009 through November 2023 were rebuilt following NTIA's own harmonization code. The series below are the pre-2016 adoption measures the ACS cannot supply. The grey band marks the 2015 questionnaire redesign, which breaks the household mobile-plan series (at-home mobile broadband before, any-location data plan after).</p>
{fig_div('ntia')}
<p class="caption">Weighted shares by wave. Smartphone-internet use: "use a cellular phone or smartphone to access the internet" (2011, 2013, all persons), NTIA's internet-enabled-phone definition from 2015. 2012 phone items were asked of the primary respondent only and are omitted here.</p>
<p>Smartphone internet use in households with teenagers went from roughly 30% (2011) to 45% (2013) to 55% (2015), which is the adoption window the design needs; by 2017 it is near saturation. State-level shares in 2011–2015 vary by 20–30 points across states, which is the variation in adoption available for the U.S. tests.</p>
{fig_div('ntia_state')}
<p class="caption">States ordered by the 2013 share. CBSA-level shares for 260–295 metros per wave are in the extract, but some have few respondents (check the unweighted counts before use).</p>
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
<p>The HBSC surveys ask 11-, 13- and 15-year-olds in ~45 countries the same schoolwork-pressure question and the same psychosomatic-complaints checklist every four years. The published country tables (1997/98 to 2021/22, plus the HBSC data browser for 2014–2022) give a direct public test of Gray's mechanism outside the United States. The U.S. took part only through 2009/10, so the U.S.-specific version of the thesis cannot be tested here after 2010.</p>
{fig_div('hbsc_trend')}
<p class="caption">Unweighted means across participating countries (thick lines), with the United States, Canada and England drawn thin. Age 15.</p>
<p>Both series were flat or falling through 2009/10, then rose together: for 15-year-old girls the cross-country mean of schoolwork pressure went from 46% (2010) to 50% (2014), 51% (2018) and 62% (2022), while multiple complaints went from 44% to 50%, 52% and 66%. The U.S. was above average on pressure in the 2000s but its pressure fell between 2006 and 2010, the last U.S. wave.</p>
<h4>Did complaints rise where pressure rose?</h4>
{fig_div('hbsc_change')}
<p class="caption">Each point is a country-sex pair at age 15; dashed line is the pooled fit (slope 0.24, SE 0.07, r = 0.59). For 2010 → 2018 alone: slope 0.16 (SE 0.07), r = 0.31.</p>
<div class="tw"><table><thead><tr><th>Test (age 11–15 pooled unless noted)</th><th>Estimate</th><th>Reading</th></tr></thead><tbody>
<tr><td>Within-country shared movement, complaints on pressure, country×age×sex and wave×age×sex FE, 1,440 observations</td><td>0.14 (SE 0.04); girls 0.16, boys 0.12</td><td>a 10-pp rise in pressure goes with a 1.4-pp rise in complaints</td></tr>
<tr><td>Long change 2010 → 2018, age 15, 72 country-sex pairs</td><td>mean Δpressure +5.5 pp, Δcomplaints +6.6 pp; slope 0.16</td><td>pressure differences explain ~1 pp of the 6.6-pp rise</td></tr>
<tr><td>Long change 2010 → 2022, age 15, 70 pairs</td><td>Δpressure +12.7, Δcomplaints +17.7; slope 0.24, r 0.59</td><td>stronger, but 2022 includes the pandemic</td></tr>
<tr><td>Placebo period 2002 → 2010</td><td>Δpressure −2.9, Δcomplaints −0.1; slope 0.14</td><td>same slope when neither was rising</td></tr>
<tr><td>2018/2022 cross-country: complaints on problematic social media use and pressure, wave×age×sex FE, 496 observations</td><td>PSMU 0.53 (SE 0.15); pressure 0.13 (SE 0.06)</td><td>both independently associated</td></tr>
<tr><td>Same, within-country change 2018 → 2022</td><td>PSMU 0.25 (SE 0.18); pressure 0.12 (SE 0.10)</td><td>underpowered with one change per country</td></tr>
</tbody></table></div>
<div class="note"><strong>What this shows.</strong> Gray's mechanism has cross-national support in the sense that schoolwork pressure rose after 2010 in most HBSC countries, not only the U.S., and complaints rose more where pressure rose more. But the slope is modest and is the same in the placebo comparison period, so pressure behaves like a stable correlate of complaints rather than the driver of the post-2010 break: most of the rise is common to all countries and is absorbed by the wave effects. The concentration test (are complaints increasingly concentrated among high-pressure students?) needs the HBSC microdata.</div>
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
<p>LTE launch dates were compiled from carrier press releases and their press reprints: 967 carrier-market launches (Verizon 442, AT&T 243, Sprint 234, T-Mobile 47), mapped to 2013 CBSA codes, with a first-launch date for 98 of the top 100 metros and for 279 of the 311 metros the ACS identifies. Verizon's December 2010 launch covered 36 of these metros; 125 more launched in 2011, 96 in 2012, 14 in 2013. Onset is assigned to the school year that starts after the launch. Coverage gaps (mainly Verizon's 2013 small-market waves and about 44 AT&T dates among the top 150) are listed in the methods note.</p>
<h3>Descriptive: onset cohorts</h3>
{fig_div('onset_cohorts')}
<p class="caption">Population-weighted ACS cognitive-difficulty rate for 12–17-year-olds in metros grouped by first LTE launch, indexed to each cohort's 2008–10 mean.</p>
<p>The simplest check: metros that got LTE first should have pulled ahead of the later ones around 2011–2013. Through 2013 it does not; the cohorts track each other. From 2014 the December 2010 cohort does drift higher for girls (index 127 by 2019 versus 110–116), but this cohort is the 36 largest metros, where the affluent-teen composition effect is strongest, and the gap opens three years after onset. The event-study coefficients for girls at four to six years after onset are +0.6 to +1.1 pp with standard errors near 1 pp.</p>
<h3>Event study</h3>
{fig_div('event_study')}
<p class="caption">Estimated effect by school year relative to the LTE launch (the year before launch is the reference), market and year fixed effects, population weights, standard errors clustered by market. Green: the 279 metros with a known launch date, so only the timing differences are used. Grey: also includes the 32 metros without a date and the non-metro parts of each state as if never treated (they are really late adopters, so this version is an outer bound).</p>
<div class="tw"><table><thead><tr><th>Onset definition</th><th>Sample</th><th>12–17 all</th><th>Girls</th><th>Boys</th><th>65+ placebo comparison</th><th>25–49</th></tr></thead><tbody>
<tr><td>First carrier</td><td>dated metros</td><td>+0.02 (0.15)</td><td>−0.04 (0.19)</td><td>+0.03 (0.27)</td><td>+0.03 (0.15)</td><td>+0.11 (0.08)</td></tr>
<tr><td>Verizon</td><td>dated metros</td><td>+0.01 (0.16)</td><td>−0.11 (0.20)</td><td>+0.05 (0.29)</td><td>+0.07 (0.16)</td><td>+0.11 (0.08)</td></tr>
<tr><td>Second carrier</td><td>dated metros</td><td>−0.01 (0.15)</td><td>−0.11 (0.17)</td><td>+0.20 (0.23)</td><td>+0.28 (0.14)</td><td>+0.09 (0.07)</td></tr>
<tr><td>First carrier</td><td>+ non-metro as untreated</td><td>0.00 (0.09)</td><td>−0.08 (0.10)</td><td>+0.11 (0.13)</td><td>+0.12 (0.11)</td><td>−0.10 (0.06)</td></tr>
</tbody></table></div>
<p class="caption">Static difference-in-differences coefficient on "LTE in force", percentage points, SE in parentheses. Random-onset placebo comparison runs give SE ≈ 0.07 for the full panel.</p>
<div class="note"><strong>What this shows.</strong> LTE timing across U.S. metros does not predict the timing of the rise in the ACS item. The confidence interval for girls excludes effects larger than about +0.3 pp on the dated sample and +0.1 pp with the untreated controls, against a total 2010–2019 rise of about 0.5 pp. Three things keep this from being a rejection of H1: LTE timing is compressed into 2011–2012 for most large metros, so there is little pre-period for the early cohort; social-media exposure travels through peers and national platforms, which pushes a market-level design toward zero; and the ACS item captures only part of the distress rise. It does mean the rollout design cannot get anywhere with the ACS alone: it needs the state youth surveys or clinical outcomes at the metro level.</div>
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
<p>The WHO Global School-based Student Health Survey asks 13–17-year-olds in 100+ countries the same loneliness, anxiety-related sleep loss and suicidality items, with rounds from 2003 onward. All 165 public-use country-rounds are freely downloadable from the WHO microdata repository; {nall} were stacked and harmonized, of which {nround} rounds in {ncty} countries have two or more rounds and can be used within-country. Exposure here is the World Bank internet-users share for the survey year; ITU coverage and mobile-broadband exposures follow below.</p>
{fig_div('gshs')}
<p class="caption">Each point is a country's change from its first to its last GSHS round (weighted prevalence, ages 13–17), against the change in the national internet-user share over the same years.</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Sex</th><th>Sample</th><th>Effect of +10 pp internet users (SE)</th></tr></thead><tbody>{frows}</tbody></table></div>
<p class="caption">Country and year fixed effects, weights = inverse sampling variance, SE clustered by country. Rows with degenerate SEs (too few countries carrying the item) are omitted.</p>
<div class="note"><strong>What this shows.</strong> With the full stack there is no within-country relation between internet penetration and adolescent distress: for girls, +1.0 pp loneliness per 10-point rise in internet users (SE 0.8) and +0.02 pp for suicidal ideation (SE 1.3); boys' coefficients are slightly negative. A partial stack of 72 rounds earlier in this run had shown +2.5 pp for girls on both items, which did not survive the remaining 77 rounds, a useful reminder of how noisy country-round panels are. Country-level internet penetration is also a coarse exposure: it does not distinguish adolescent from adult access or phone from PC. The two subsections below use, respectively, the 2022–23 rounds that ask adolescents directly about phone hours and the ITU coverage series.</div>
"""
(SEC/"gshs.html").write_text(gshs_html)

# ---- policy section
R = pd.read_csv(T/"policy_t2_results.csv"); Rs = R[~R.policy.str.startswith(("joint","LTE"))]
names = {"rttt_winner":"Race to the Top winner (award year–2015)","waiver_in_force":"ESEA waiver in force","cc_aligned_test_in_force":"Common Core aligned test in force","teacher_eval_test_based_in_force":"Test-based teacher evaluation in force","exit_exam_in_force":"High-school exit exam in force","pressure_index":"Pressure index (sum of the five)"}
outs = ["ACS 12-17 girls","ACS 12-17 boys","YRBS sad/hopeless girls","YRBS sad/hopeless boys","NSDUH youth MDE (2-yr, labelled by end year)"]
def cell(pol, o):
    r = Rs[(Rs.policy==pol)&(Rs.outcome==o)]
    if len(r)==0: return "–"
    r = r.iloc[0]; star = "<strong>" if abs(r.coef) > 1.96*r.se else ""; return f"{star}{r.coef:+.2f} ({r.se:.2f}){'</strong>' if star else ''}"
prow = "".join(f"<tr><td>{names[pol]}</td>" + "".join(f"<td>{cell(pol,o)}</td>" for o in outs) + "</tr>" for pol in names)
Ri = R[R.policy.str.startswith("LTE")]
irow = "".join(f"<tr><td>{r.outcome.replace('ACS market ','')}</td><td>{r.policy.replace('LTE x ','')}</td><td>{'not identified' if r.se>50 else f'{r.coef:+.2f} ({r.se:.2f})'}</td></tr>" for r in Ri.itertuples())
Pm = pd.read_csv(T/"state_year_policy_fips.csv").groupby("year")[list(names)[:-1]].mean().reset_index()
fig = go.Figure()
for i, pol in enumerate(list(names)[:-1]):
    fig.add_trace(go.Scatter(x=Pm.year, y=100*Pm[pol], mode="lines+markers", line=dict(color=PAL[i], width=2), marker=dict(size=5), name=names[pol].split(" (")[0], hovertemplate="%{y:.0f}% of states<extra>"+names[pol].split(" (")[0]+"</extra>"))
fig.update_yaxes(title_text="% of states (incl. DC) with policy in force", range=[0,100]); figs["policy"] = base(fig, h=360)
policy_html = f"""
<p>The state policy table dates five accountability measures for 51 jurisdictions, with a source for every cell: Race to the Top awards (2010–11), ESEA/NCLB waivers (2012–16), the first operational Common Core aligned test (2012–2019, mostly spring 2015), test-based teacher evaluation (implemented statewide 2009–2017), and high-school exit exams (falling from 25 states to 13). Year is the school year ending that spring.</p>
{fig_div('policy')}
<p class="caption">Share of states with each policy in force. The near-simultaneous 2012–2015 adoption of waivers, teacher evaluation and aligned tests is exactly the timing problem the study design anticipated.</p>
<h3>State-year regressions</h3>
<div class="tw"><table><thead><tr><th>Policy (each estimated alone)</th><th>ACS girls</th><th>ACS boys</th><th>YRBS sad girls</th><th>YRBS sad boys</th><th>NSDUH youth MDE</th></tr></thead><tbody>{prow}</tbody></table></div>
<p class="caption">Coefficients in percentage points, state and year fixed effects, inverse-variance weights, SE clustered by state, 2008–2019 (YRBS biennial, 39 states; NSDUH two-year periods labelled by end year). Bold = |t| &gt; 1.96.</p>
<p>Common Core aligned testing, waivers, teacher evaluation, exit exams and the summed index show no relation to any of the three outcomes; several point estimates are negative. The one exception is Race to the Top: winning states saw larger subsequent rises in NSDUH youth depression (+0.36 pp) and in YRBS girls' sadness (+1.1 pp), with the ACS item flat. RTTT winners are a selected group (19 jurisdictions with the capacity to write winning applications, including DC, NY, MA, FL). Tracing the same states year by year around the award, in the U.S. follow-ups below, shows this coefficient is an artifact of how the indicator was coded; there is no rise after the award.</p>
<h3>Does phone timing matter more in high-pressure states? (H3)</h3>
<div class="tw"><table><thead><tr><th>Outcome (ACS 12–17, market panel)</th><th>LTE × policy</th><th>Interaction (SE)</th></tr></thead><tbody>{irow}</tbody></table></div>
<p class="caption">State-by-year fixed effects absorb the policy's own effect; what remains is whether early-LTE metros within a state rose more when the state had the policy. "Not identified": the policy switches on in the same year for nearly every metro in the state, so there is nothing left to compare.</p>
<p>Where identified, the interaction is negative for girls (LTE × pressure index −0.45, SE 0.27; LTE × RTTT −0.93, SE 0.45): early-LTE markets in high-pressure states did not rise more. This is the opposite of what H3 predicts, though with the same market-level caveats as the main event study.</p>
"""
a_, b_ = policy_html.split("<h3>Does phone timing matter more in high-pressure states? (H3)</h3>")
(SEC/"policy.html").write_text(a_); (SEC/"policy_inter.html").write_text(b_)

# ---- MICS section
MP = pd.read_csv(T/"mics_prevalence_sample_age_sex.csv"); MC = pd.read_csv(T/"mics_cluster_dose.csv"); MO = pd.read_csv(T/"mics_own_use_1517.csv")
ch = pd.read_parquet(ROOT/"data/extracts/mics/mics_child_analysis.parquet")
sm = ch[ch.AGEFS.between(10,17)].groupby(["sample","iso3","year"]).apply(lambda g: pd.Series({"anx_g": 100*np.average(g[g.girl==1].anx_dw, weights=g[g.girl==1].wt), "anx_b": 100*np.average(g[g.girl==0].anx_dw, weights=g[g.girl==0].wt), "dose": 100*np.nanmean(g.y_net_daily), "hh_net": 100*np.nanmean(g.hh_net), "n": len(g)}), include_groups=False).reset_index()
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
<p>MICS6 and MICS7 (2017 onward) carry the Washington Group / UNICEF Child Functioning Module for every child aged 5–17: the caregiver reports how often the child "seems very anxious, nervous or worried" and how often "very sad or depressed" on a daily / weekly / monthly / a few times a year / never scale, with identical wording in every country. The same surveys ask women 15–49 (and men in about half the surveys) about mobile ownership and how often they used the internet and a mobile phone in the past three months, and the household questionnaire records internet access. All 68 samples on the IPUMS-MICS server with the module were read from the fixed-width files: {len(ch):,} children with valid responses in {ch['sample'].nunique()} surveys.</p>
<h4>Prevalence across surveys</h4>
{fig_div('mics_scatter')}
<p class="caption">One point per survey, ages 10–17. Cross-survey variation in caregiver-reported anxiety is enormous (from under 1% in Turkmenistan to 40% in Tunisia) and is dominated by reporting culture, which is why all tests below are within country.</p>
<h4>Use and symptoms within countries</h4>
{fig_div('mics_coef')}
<p class="caption">Cluster rows: children's anxiety against the share of 15–24-year-olds in their sampling cluster who use the internet almost daily (or own a mobile, or the household-internet share), with survey-by-region fixed effects, wealth quintile, urban and age controls, SE clustered by sampling cluster. Own-use rows: 15–17-year-olds linked to their own record in the women's or men's questionnaire (85% of girls matched, 24% of boys), comparing users to non-users within the same cluster.</p>
<p>Girls aged 10–17 in clusters where more young adults use the internet daily are reported slightly more anxious (+0.33 pp per 10-point rise in the cluster share, SE 0.13). But the same coefficient appears for 5–9-year-old girls (+0.21, SE 0.12), who are not the exposed group, so this is a property of connected clusters rather than of adolescent phone use. Mobile ownership in the cluster is <em>negatively</em> related to anxiety for every age and sex, household internet is flat, and depression shows no relation to any measure of connectivity. The within-cluster own-use comparison, the closest MICS comes to the individual exposure Haidt describes, shows no effect or negative for girls: daily internet use −0.6 pp on anxiety (SE 1.4) and −2.1 pp on depression (SE 1.2), daily phone use −2.4 pp (SE 1.2). For boys the own-phone-use coefficients are positive (+4.4 and +5.5 pp, SE ~2) but rest on the quarter of boys with a men's-questionnaire record. The learning and friendship functioning items are flat throughout.</p>
<h4>Two-round countries</h4>
<div class="tw"><table><thead><tr><th>Country</th><th>Ages</th><th>Sex</th><th>Rounds</th><th>Anxious daily/weekly %</th><th>Depressed daily/weekly %</th></tr></thead><tbody>{trrows}</tbody></table></div>
<h4>DHS-8 self-reports: Nepal 2022</h4>
<p>The DHS-8 mental-health module gives a self-reported counterpart to the MICS caregiver items. Nepal 2022 administered the PHQ-9 and GAD-7 to a subsample of 7,442 women aged 15–49, alongside internet-use frequency and smartphone ownership; Kenya 2022 asked only about diagnosed depression or anxiety. Among Nepali women aged 15–19 (n = 1,379; 4.5% with PHQ-9 ≥ 10, 42% using the internet almost daily), daily internet users are 2.3 pp more likely to screen positive for depression (SE 2.4) and 3.5 pp for anxiety (SE 2.9) than non-users in the same sampling cluster, with wealth, education and age held fixed; the same coefficients are positive at 20–24 and negative at 25–49. Smartphone ownership itself is unrelated. In Kenya, diagnosed depression among 15–19-year-olds is unrelated to owning a smartphone (−0.1 pp, SE 1.3). These are single-survey cross-sections and too small to be decisive, but they line up with the GSHS hours gradient rather than with the MICS caregiver no effect, which is itself a finding: the association appears when the adolescent reports her own state and her own use.</p>

<p class="caption">Countries with both a MICS6 and a MICS7 round on the server (Pakistan excluded: its rounds are different provinces). Turkmenistan's rise is from a very low base; Kyrgyzstan and Tunisia fall; Mongolia is mixed.</p>
<div class="note"><strong>What this shows.</strong> This is the out-of-sample test the study design asked for, and it does not find the smartphone effect: neither cluster-level connectivity nor a girl's own daily internet or phone use predicts caregiver-reported anxiety or depression once the country and region are held fixed, and the one positive cluster coefficient is matched by the 5–9-year-olds (a placebo comparison, since they are not the exposed group). Qualifications: the outcome is a caregiver report, not self-report; exposure is measured as use rather than as the timing of network coverage, so the design with GSMA coverage maps remains the one that could establish cause; and the before-and-after comparisons will sharpen as more MICS7 rounds are released.</div>
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
<p>If rollout timing is too crude a measure, the next step is how many teenagers actually had smartphone internet. Using the rebuilt NTIA series (share of persons in households with a 12–17-year-old who use a smartphone for internet, by state, interpolated between the 2011–2019 waves) against the YRBS state files, with state and year fixed effects, 39 states, 2011–2019:</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Measure of adoption</th><th>Effect per +10 pp of adoption (SE)</th></tr></thead><tbody>
<tr><td>YRBS sad/hopeless, girls</td><td>teen-household smartphone internet</td><td><strong>+0.90 (0.44)</strong></td></tr>
<tr><td>YRBS sad/hopeless, boys</td><td>same</td><td>+0.28 (0.41)</td></tr>
<tr><td>YRBS sad/hopeless, girls</td><td>household mobile data plan</td><td>+0.50 (0.51)</td></tr>
<tr><td>ACS cognitive difficulty 12–17, girls</td><td>teen-household smartphone internet</td><td>−0.04 (0.07)</td></tr>
</tbody></table></div>
<p>This has the pattern the phone hypothesis predicts (girls, not boys; the self-report sadness item, not the ACS disability item), and it is fragile: five biennial YRBS waves, an interpolated exposure level, and a p-value near 0.04 with 39 clusters. The county-level version in the next subsection does not reproduce it, so it stays suggestive.</p>
<h3>Race to the Top, traced year by year</h3>
{fig_div('rttt_es')}
<p class="caption">State and year fixed effects, coefficients relative to the year before the award (Phase 1 and 2: 2010; Phase 3: 2011), 2005–2019.</p>
<p>The static Race to the Top coefficient from the school-policy section does not survive being traced year by year around the award: afterwards, YRBS sadness and NSDUH youth depression in winning states move flat to downward relative to other states. The static estimate arose from coding the indicator as 1 only for 2010–2015, so the winners' post-2016 years served as controls. There is no evidence that RTTT states' teenagers became more distressed. The U.S. policy-shock version of H2 is therefore not supported; testing H2 further needs school-level pressure items, which no U.S. public survey carries.</p>
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
<p>Five GSHS rounds (Ghana 2022, India 2022, Jamaica 2023, Morocco 2023, Wallis and Futuna 2023) added "hours per day you used a mobile phone in the past 7 days". This puts each student's own reported phone use next to the same student's loneliness and suicidality answers.</p>
{fig_div('gshs_hours')}
<p class="caption">Country fixed effects and age controls, survey weights, SE clustered by school; 5,654 girls and 5,487 boys. The full gradient is monotonic: relative to under an hour a day, girls at 5+ hours report loneliness +21 pp, suicidal ideation +18 pp, attempts +15 pp.</p>
<p>This is the pattern the phone hypothesis predicts: large, concentrated in girls, and rising steadily with hours of use. It is also exactly the kind of one-time self-report association the two camps disagree about, since heavy phone use and distress can share causes or run the other way. It cannot settle the timing question, but it does mark the 2022–23 GSHS rounds (and the MICS7 rounds with adolescent modules) as the place to bring in network-coverage timing, because here the exposure is measured on the adolescent rather than inferred from adults.</p>
"""
(SEC/"gshs.html").write_text((SEC/"gshs.html").read_text() + mh_html)

# ---- GSHS ITU exposure addendum
IT = pd.read_csv(T/"gshs_fe_itu.csv"); IT = IT[IT.item.isin(["lonely","suicide_consider","suicide_attempt"])]
en = {"pop_covered_4g_pct":"4G population coverage (ITU)","pop_covered_3g_pct":"3G population coverage (ITU)","mbb_subs_per100":"Mobile-broadband subs per 100 (ITU)","itu_internet":"Internet users % (ITU)"}
itrows = "".join(f"<tr><td>{en[e]}</td><td>{g.n_countries.iloc[0]} / {g.n_rounds.iloc[0]}</td>" + "".join(f"<td>{g[(g.item==it)&(g.sex==sx)].coef_per10.iloc[0]:+.2f} ({g[(g.item==it)&(g.sex==sx)].se_per10.iloc[0]:.2f})</td>" if len(g[(g.item==it)&(g.sex==sx)]) else "<td>–</td>" for it in ["lonely","suicide_consider","suicide_attempt"] for sx in ["girls","boys"]) + "</tr>" for e, g in IT.groupby("exposure", sort=False))
itu_html = f"""
<h4>Network coverage at country level (ITU)</h4>
<p>With the ITU series, the same comparison can use network coverage rather than reported use. Same model: country and year fixed effects, inverse-variance weights, SE clustered by country, countries with two or more rounds.</p>
<div class="tw"><table><thead><tr><th>Exposure (per +10 points)</th><th>Countries / rounds</th><th>Lonely, girls</th><th>Lonely, boys</th><th>Considered suicide, girls</th><th>…boys</th><th>Attempted, girls</th><th>…boys</th></tr></thead><tbody>{itrows}</tbody></table></div>
<p>Nothing here favors H1: 4G coverage, 3G coverage and mobile-broadband subscriptions all give coefficients within about ±0.5 pp per 10 points, with the girls' loneliness coefficient on 3G coverage negative. Country-level coverage is still a crude measure (within-country changes are large, 20–35 points, but they move with everything else that changed between 2007 and 2019), which leaves local, cluster-level coverage as the remaining test.</p>
"""
(SEC/"gshs.html").write_text((SEC/"gshs.html").read_text() + itu_html)

# ---- state survey section
TR = pd.read_csv(T/"state_survey_trends.csv"); LE = pd.read_csv(T/"state_survey_lte_event.csv"); ND = pd.read_csv(T/"state_survey_ntia_dose.csv")
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
ndrows = "".join(f"<tr><td>{r.item.replace('_',' ')}</td><td>{r.sex}</td><td>{r.coef_per10pp:+.2f} ({r.se:.2f})</td><td>{r.counties} / {r.cbsas}</td><td>{', '.join(eval(r.states))}</td></tr>" for r in ND.itertuples())
ss_html = f"""
<h3>State youth surveys at county level</h3>
<p>The state youth surveys are the self-report outcome the ACS lacks. County tables were compiled for six states: Minnesota (1998–2019, 87 counties), Washington (2010–2025, 38), Maine (2009–2023, 16), California (2013–2019, 54, by sex), Pennsylvania (2015–2023, 60) and Illinois (2018–2024, 78), 34,439 county rows with source and wording recorded for each. Minnesota's pre-2013 sadness item has different wording and is excluded from the sadness series.</p>
{fig_div('state_trends')}
<p class="caption">Unweighted county means; grades pooled. Minnesota's 2022 county tables sit behind a CAPTCHA and are not yet included.</p>
<p>Three things stand out. Sadness rose in every state from about 2013 to a 2021 peak (Washington 28% → 41%, Maine 22% → 37%, Illinois 35% → 41%). Minnesota's suicidal-ideation series, the only one that reaches back to the 1990s, <em>fell</em> from 20% in 1998 to 10.5% in 2013 before turning up. And the post-2021 declines are large: Washington's 2025 sadness rate (27%) is below its 2010 level and Illinois' 2024 ideation rate (13.5%) is the lowest in its series.</p>
<h4>LTE onset at county level</h4>
<p>Counties mapped to 2013 CBSAs and to the LTE first-launch date; county and state-by-year fixed effects; non-metro and undated counties as untreated (a bound, since rural LTE arrived 2013–14).</p>
<div class="tw"><table><thead><tr><th>Panel</th><th>DiD on "LTE in force" (pp)</th></tr></thead><tbody>
<tr><td>Sad/hopeless, WA + ME counties, 2009–2019 (54 counties, 26 dated-metro)</td><td>+0.48 (SE 0.72)</td></tr>
<tr><td>Considered suicide, WA + ME + MN, 1998–2019 (141 counties, 59 dated-metro)</td><td>−0.72 (SE 0.41)</td></tr>
<tr><td>Considered suicide, MN alone, 1998–2019 (87 counties)</td><td>−1.07 (SE 0.52)</td></tr>
</tbody></table></div>
<h4>Smartphone adoption at the metro level</h4>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Sex</th><th>Effect per +10 pp teen-household smartphone internet (SE)</th><th>Counties / CBSAs</th><th>States</th></tr></thead><tbody>{ndrows}</tbody></table></div>
<p class="caption">NTIA CBSA shares interpolated between waves (only areas with 30 or more respondents), county and state-by-year fixed effects, SE clustered by CBSA, 2011–2019.</p>
<div class="note"><strong>What this shows.</strong> With the self-report outcome measured at county level, neither LTE onset nor smartphone adoption predicts where sadness or suicidal thoughts rose. The state-level result for girls reported above does not reappear here (+0.4 pp per 10 points, SE 0.4, in the two states with county data by sex), so it should be read as suggestive at best. The rise was broad, happened at the same time in counties with very different connectivity histories, and, in the latest waves, is reversing.</div>
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
<p>PISA 2022 asked every participating school whether "the use of cell phones is not allowed on the school premises" and asked students about loneliness and belonging at school, digital-device habits, and (in 13 systems) life satisfaction. Merging the two files gives 568,374 students in 19,885 schools across 80 systems; 41% of students attend a ban school, from 7% in Finland to 96% in Greece. The comparison below is within country: ban versus non-ban schools with country fixed effects, controls for socio-economic status, sex, grade and school type, student weights, and standard errors clustered by school.</p>
{fig_div('pisa_ban')}
<p class="caption">Binary items in percentage points; PISA indices in hundredths of a standard deviation. The ICT module (smartphone use at school) covers 51 systems; the well-being module (life satisfaction, experienced well-being) covers 13–14.</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>All</th><th>Girls</th><th>Boys</th><th>Mean</th></tr></thead><tbody>{prrows}</tbody></table></div>
<p>Three findings. First, bans change behaviour, partly: daily smartphone use at school is 12 points lower in ban schools (from a 55% base, so 43% of students in ban schools still use one daily), leisure screen use at school falls, and after-school use is unchanged, which is the right placebo comparison pattern. Second, the well-being differences run in the direction the Norwegian study found and are concentrated in girls: less nervousness without a device, 1.4 pp less loneliness at school for girls (none for boys), and +0.02 to +0.03 SD on belonging and life satisfaction. Third, ban schools report <em>more</em> classroom distraction by devices (+3.7 pp), a sign that schools adopt bans where phones are already a problem. That selection works against finding benefits, so the small favorable girl-specific differences are, if anything, understated, but a cross-section cannot say by how much.</p>
<div class="note"><strong>What this shows.</strong> The only public, multi-country microdata on school phone rules show a modest, girl-specific association between bans and lower loneliness and device anxiety, alongside clear evidence that bans reduce in-school use and clear evidence of selection into bans. Together with Norway's result, that is enough to make the 2024–25 U.S. state bans the most valuable natural experiment now pending in this project; the 2025 YRBS and the 2025–27 state-survey waves are where it will be tested, using the approach set out above.</div>
"""
(SEC/"pisa.html").write_text(pisa_html)

# ---- H3 refined: ban x academic pressure (PISA)
BX = pd.read_csv(T/"pisa_ban_x_pressure.csv")
bxrows = "".join(f"<tr><td>{r.outcome}</td><td>{r.sex}</td><td>{r.ban_lowanx:+.2f} ({r.se_low:.2f})</td><td>{r.ban_hianx:+.2f}</td><td>{r.ban_x_hianx:+.2f} ({r.se_int:.2f})</td><td>{r.hianx_main:+.1f}</td></tr>" for r in BX.itertuples())
h3_html = f"""
<p>The interaction hypothesis in its sharpest form says that what harms adolescents is not phones as such but phones <em>during school hours</em>, on top of high-stakes academic demands in the same hours: social comparison and notifications running through the day that also carries the tests and the grades. If that is right, three things follow. Pressure and phone use should both have risen after 2010 (they did, in most HBSC countries and in U.S. homework time). Removing phones from the school day should bring relief out of proportion to the hours removed, and more relief for students under more academic pressure. And out-of-school use, or use in low-pressure settings, should matter less.</p>
<h3>What the phone-ban evidence says about this</h3>
<p>PISA 2022 allows one direct check: does the ban's association with well-being differ between students under high and low academic anxiety? The only pressure-like measure asked of all students is the mathematics-anxiety index (the schoolwork-anxiety items were not asked in 2022), so "high anxiety" here means above the country median on that index. Same model as before, within country, by sex.</p>
<div class="tw"><table><thead><tr><th>Outcome</th><th>Sex</th><th>Ban, low-anxiety students (SE)</th><th>Ban, high-anxiety students</th><th>Difference (SE)</th><th>High vs low anxiety, no ban</th></tr></thead><tbody>{bxrows}</tbody></table></div>
<p class="caption">Percentage points for the binary items, hundredths of an SD for the indices; country fixed effects, socio-economic status and grade controls, student weights, SE clustered by school; 441,992 students with the anxiety index.</p>
<p>High-anxiety students are far lonelier (about 8 points more), and the ban's association with less loneliness is larger for them: −1.2 points for high-anxiety girls against −0.3 for low-anxiety girls, and −0.8 against +1.1 for boys. The differences run the way the hypothesis predicts, but they are inside their standard errors, and mathematics anxiety is a rough stand-in for schoolwork pressure. Bans reduce in-school phone use by the same amount for both groups (13 points), so the difference, if real, is in what the removal does rather than in who complies. The rest of the ban evidence below is consistent with the hypothesis without testing it: bans cut in-school use, girls in ban schools report less loneliness and less device anxiety, Norway's middle-school bans reduced girls' psychological consultations, and U.S. sadness moved inversely to school prohibitions. The test that would separate this from the plain phone hypothesis is a ban study with a measure of school pressure, which the HBSC microdata (schoolwork pressure plus school-level policy in 2021/22) can provide.</p>
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
<p class="caption">Top: principal-reported share of U.S. public schools prohibiting non-academic phone use during school hours (NCES SSOCS; 2013–14 from a smaller survey; wording changed 2017–18), the 2024–25 School Pulse Panel points (class-time construct), and the share of states with a bell-to-bell or class-time mandate in force, from the policy table. Bottom: NSDUH past-year major depressive episode ages 12–17, YRBS sad/hopeless by sex, and county-mean sadness from the Washington, Maine and Illinois surveys. Grey band = 2020.</p>
<p>Read as a picture, the two panels move in opposite directions twice. Prohibitions fell from 91% to 66% between 2009–10 and 2015–16 while depression and sadness rose from their 2011–13 lows; prohibitions then climbed back through 2019–20 and, after the pandemic peak, sadness fell in every state series as the 2024–25 wave of state mandates arrived. The correlation is far from clean: the sadness series kept rising through 2019–2021 while prohibitions were already recovering, and the post-2021 fall began before most state laws took effect. Two hypotheses fit the shape, and neither is established:</p>
<ul>
<li><strong>Partial re-restriction plus awareness.</strong> The modest recovery in school restrictions from 2016, together with rising attention from parents, schools and adolescents themselves, may have reduced the most acute in-school and late-night exposure even before formal bans. The PISA cross-section (less in-school use, less device anxiety, less loneliness among girls in ban schools) and Norway's staggered bans are consistent with this, but both are small effects and the U.S. timing is loose.</li>
<li><strong>Content rather than access.</strong> If what mattered in 2012–2017 was image-based social comparison (Instagram, Snapchat), the later migration of teen attention toward algorithmic consumption feeds (TikTok, YouTube) could raise total screen time while producing fewer acute internalizing symptoms. This would explain rising hours alongside falling sadness, and it is the mechanism the Facebook-rollout study points to (social comparison), but the pilot has no platform-mix data by year and cannot test it.</li>
</ul>

<h3>Lags and enforcement</h3>
<p>Two features of the policy make the simple overlay above too demanding a test, and both argue for reading the chart with a lag of a year or two.</p>
<ul>
<li><strong>Delayed effects are what the causal studies show.</strong> In the 2026 U.S. pouch study, student well-being <em>fell</em> by 0.2 SD in the adoption year and only turned positive (+0.16 SD) by the second year; Norway's bullying and mental-health effects grew over three years; the Florida district study found suspensions up 12% in year one, fading in year two. The pattern is resistance first, then adjustment, with administrators refining enforcement over a school year or more. Under that pattern the 2015–16 low point in restrictions would be expected to show up in outcomes around 2017–18, and the 2024–25 mandates around 2026–27, which is roughly what the overlay shows and is also why the 2025 YRBS is only the first, weakest post-ban wave. The U.S. test should therefore follow states for at least two years after a ban, not compare a single before and after.</li>
<li><strong>"Policy" is not enforcement.</strong> PISA 2022 measures both. Among schools that report phones are not allowed on the premises, a median 46% of students across 52 systems still used a smartphone at school daily (62% in non-ban schools), and in 24 of the 52 a majority did. The United States is among the weakest: 70% daily use in ban schools against 82% elsewhere, a gap of 12 points, compared with gaps of 30–46 points in Japan, Taiwan and Brunei. Enforcement in the U.S. in 2022 was therefore mostly nominal, which is consistent with the idea that restrictions only began to take hold as administrators gained confidence, and with the SSOCS series measuring stated policy rather than practice. It also means any effect found in the 2025–27 waves will be a lower bound on what full enforcement could do.</li>
</ul>
<p class="caption">Country-by-country daily-use rates in ban and non-ban schools are in <code>results/tables/pisa_ban_enforcement_by_country.csv</code>.</p>

<p>To be clear, this graph raises the question rather than answering it. The 2025 YRBS, the 2025–27 state-survey waves, and the district-level rollouts already in the policy table are what will turn the shape into a test: bans arriving at different times in different states and districts, against outcomes measured before and after, by sex, with the 65+ placebo comparison retained.</p>
"""

SB = pd.read_csv(ROOT/"data/compiled/phone_bans/state_phone_bans.csv"); cnt = SB.groupby(["policy_type","effective_school_year"]).size().reset_index(name="n")
sbrows = "".join(f"<tr><td>{r.policy_type}</td><td>{r.effective_school_year if isinstance(r.effective_school_year,str) else '–'}</td><td>{r.n}</td><td>{', '.join(SB[(SB.policy_type==r.policy_type)&(SB.effective_school_year==r.effective_school_year)].state) if isinstance(r.effective_school_year,str) else ', '.join(SB[(SB.policy_type==r.policy_type)&SB.effective_school_year.isna()].state)}</td></tr>" for r in cnt.sort_values(["policy_type","effective_school_year"]).itertuples())
ST_ = pd.read_csv(ROOT/"data/compiled/phone_bans/phone_ban_studies.csv")
cols = [c for c in ST_.columns]; get = lambda r, k: next((str(getattr(r, c)) for c in cols if k in c.lower() and str(getattr(r, c))!="nan"), "")
strows = "".join(f"<tr><td>{get(r,'author')} ({get(r,'year')})</td><td>{get(r,'country')}</td><td>{get(r,'design')}</td><td>{get(r,'outcome')}</td><td>{get(r,'headline') or get(r,'effect')}</td></tr>" for r in ST_.itertuples())
CS = pd.read_csv(T/"county_screen_dose.csv")
csrows = "".join(f"<tr><td>{r.state}</td><td>{r.dose.replace('_',' ')}</td><td>{r.outcome.replace('_',' ')}</td><td>{r.n}</td><td>{r.cross_coef:+.2f} ({r.cross_se:.2f})</td><td>{r.within_coef:+.2f} ({r.within_se:.2f})</td></tr>" for r in CS.itertuples())
bans_html = f"""
<p>School phone policy is the one policy both theses agree should matter if phones are the mechanism, and it is the observable from the four-hypothesis table that the first pass had not touched. This section sets what public data allow as of September 2026 beside the causal literature.</p>
{overlay_html}
<p>In detail: schools <em>relaxed</em> phone prohibitions exactly when distress rose: from 91% prohibiting in 2009–10 to 66% in 2015–16, during the years when smartphones replaced feature phones. Prohibitions then climbed back (77% by 2019–20) and the 2024–25 wave of state laws has pushed bell-to-bell policies toward a majority of schools. That is a national series, so it cannot separate school policy from everything else that changed; but it means the 2010s rise happened while access to phones <em>in school</em> was expanding, which fits either thesis, and the 2023–25 fall in sadness in the state surveys coincides with the re-tightening.</p>
<h4>The national series in detail</h4>
{fig_div('phone_bans_trend')}
<p class="caption">Principal-reported share of public schools prohibiting non-academic phone use during school hours (NCES SSOCS; the 2013–14 point is a smaller Fast Response Survey; the item wording changed in 2017–18). The 2024–25 School Pulse Panel asks about class time, not school hours: 77% prohibit phones in any class, 30% in all classes and outside class.</p>

<h3>State bans and what can be tested when</h3>
<div class="tw"><table><thead><tr><th>Policy type</th><th>Effective school year</th><th>States</th><th></th></tr></thead><tbody>{sbrows}</tbody></table></div>
<p class="caption">Compiled from Ballotpedia, Education Week, KFF and state statutes; classification disputes between trackers are noted in the data file. Florida's HB 379 (instructional time, 2023–24) is the earliest statewide action.</p>
<p>Almost every statewide ban took effect in fall 2024 or fall 2025. The latest outcome waves in hand are spring 2023 (YRBS, Pennsylvania, Maine), spring 2024 (Illinois) and fall 2025 (Washington, guidance only), so no post-ban statewide outcome exists yet in this project; the 2025 YRBS state files (not released as of this writing) will give the first difference-in-differences: Florida, Indiana, Louisiana and South Carolina (2024–25) against states without a mandate, 2021 → 2023 → 2025, by sex, on sad/hopeless and considered suicide. The county panel then adds Washington 2027, Maine 2025 and Illinois 2026 against their own bans. The model is the same as the LTE one above, with the ban in place of LTE and the 65+ comparison group retained. NCES restricted-use SSOCS files carry state and county identifiers and would allow a school-level version, which is the Phase 2 item.</p>
<h3>What the causal literature already shows</h3>
<div class="tw"><table><thead><tr><th>Study</th><th>Setting</th><th>Design</th><th>Outcome domain</th><th>Headline</th></tr></thead><tbody>{strows}</tbody></table></div>
<p>Two readings. On mental health specifically, the strongest evidence is Norway's staggered middle-school bans (fewer psychological consultations for girls, less bullying, no effect for boys), which is the girl-specific pattern H1 predicts. The English one-time comparison shows no effect on well-being, and the 2026 U.S. Yondr-pouch study finds well-being dips at adoption and recovers by year two with no change in online bullying. Achievement effects are small and positive where found, and vanish in Sweden. So bans are a plausible policy with mixed evidence rather than a settled one, and the mental-health effect, where it appears, is on girls.</p>
<h3>County social-media use and sadness</h3>
<div class="tw"><table><thead><tr><th>State</th><th>County item</th><th>Outcome</th><th>County-years</th><th>Across counties (SE)</th><th>Within county (SE)</th></tr></thead><tbody>{csrows}</tbody></table></div>
<p class="caption">Percentage points of outcome per percentage point of the county item; year fixed effects (across) or county and year fixed effects (within). Washington 2023 and 2025; Maine 2017–2021.</p>
<p>In Washington, counties where more students use social media daily report more sadness, and the 2023-to-2025 changes carry the same slope (both fell: daily social media 74% → 72%, sadness 31% → 27%). General screen time does not. This is the school-survey version of the individual association, with the same limits.</p>
{'<h3>PISA 2022: school phone rules and well-being within countries</h3>' + (ROOT/'build/sections/pisa.html').read_text() if (ROOT/'build/sections/pisa.html').exists() else '<p class="pending">PISA 2022 within-country comparison of students in schools with and without phone rules: pending the microdata extraction.</p>'}
"""
(SEC/"bans.html").write_text(bans_html)

figjson = {k: json.loads(v.to_json()) for k, v in figs.items()}
extra = {}
import shutil
for hand in (ROOT/"scripts/report/sections").glob("*.html"): shutil.copy(hand, SEC/hand.name)
for name in ["validation","lte","policy","hbsc","gshs","ntia","mics","usdose","statesurveys","reconcile","bans","policy_inter","usdose_adopt","usdose_rttt","ss_trends","ss_tests","h3"]:
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
<p class="lede">Two books offer rival explanations for the rise in adolescent anxiety and depression after 2010: Jonathan Haidt's <em>The Anxious Generation</em> (smartphones and social media) and Peter Gray's account of intensified schooling. This report asks what large-scale public microdata can say about them today, before any licensed or restricted data are requested, and whether that gets us closer to an answer than reading either book. Every figure is computed from IPUMS microdata (ACS, ATUS, MICS, IPUMS International) and public files; every chart has hover values.</p>
<nav><a href="#hyp">Hypotheses</a><a href="#verdict">Summary</a><a href="#part1">1 · The rise</a><a href="#part2">2 · Phones</a><a href="#part3">3 · School pressure</a><a href="#part4">4 · Interaction &amp; bans</a><a href="#reconcile">Haidt &amp; Twenge</a><a href="#next">Answer</a></nav>

<h2 id="hyp">The four hypotheses</h2>
<p>The study was designed around four candidate explanations, and every test below is meant to separate at least two of them.</p>
<div class="tw"><table class="verdict"><thead><tr><th>Hypothesis</th><th>Claim</th><th>What it predicts in these data</th></tr></thead><tbody>
<tr><td>H1 · Phones and social media (Haidt, Twenge)</td><td>Smartphone-based social media, arriving 2010–2013, caused the rise, most of all in girls.</td><td>Distress rises first where and when phones and fast mobile data arrive; girls far more than boys; rises in phone-first countries as coverage spreads; heavier users worse off; school phone bans help.</td></tr>
<tr><td>H2 · School pressure (Gray)</td><td>Accountability testing and reduced free play made school more stressful from about 2010, and that caused the rise.</td><td>No difference by phone timing; girls somewhat more than boys; strongest in the high-stakes years (15–17) and in the school year; distress rises where and when schoolwork pressure rises; policy shocks (Race to the Top, Common Core testing) show up in state outcomes.</td></tr>
<tr><td>H3 · Interaction</td><td>Phones did the damage mainly in combination with high school demands: social media running through the same hours that carry the tests and grades, so that neither alone explains the rise and removing phones from the school day brings relief out of proportion to the hours removed.</td><td>Both pressure and phone use rise after 2010; phone-timing effects larger under high pressure; school phone bans help, and help most for students under most academic pressure; out-of-school use matters less.</td></tr>
<tr><td>H0 · Neither, or measurement</td><td>The rise is mostly changed reporting, diagnosis-seeking, or survey drift.</td><td>Adults, including the 65+ placebo comparison, drift the same way; behavioral and self-report measures disagree; no geographic or exposure level pattern at all.</td></tr>
</tbody></table></div>

<h2 id="verdict">Summary: what the public microdata support today</h2>
<p>Each row is one observable from the design, grouped by the hypothesis it bears on most. Details, methods and qualifications are in the sections that follow.</p>
<div class="tw"><table class="verdict"><thead><tr><th>What was measured</th><th>What the pilot found</th><th>Relevant to</th></tr></thead><tbody>
<tr><td colspan="3"><strong>Is there a real rise, and is the outcome usable? (H0)</strong></td></tr>
<tr><td>65+ placebo comparison and adult drift</td><td>The ACS cognitive-difficulty item falls monotonically for people 65+ (12.2% → 9.4%, 2008–19) and is flat at 50–64 while rising for everyone under 50. No generic response drift.</td><td><span class="pill for">against H0</span></td></tr>
<tr><td>Agreement across measures</td><td>Self-report depression (NSDUH), sadness (YRBS), and the ACS item all turn up in 2011–2013 and are concentrated in girls in every source; state-level changes move together. The ACS item captures only about a sixth of the depression rise.</td><td><span class="pill for">real rise; ACS usable but weak</span></td></tr>
<tr><td>Who rose most</td><td>Steepest among affluent, private-school, Hispanic, Asian and foreign-born teens; smallest among poor teens. Fits early affluent adoption and diagnosis-seeking equally.</td><td><span class="pill">ambiguous</span></td></tr>
<tr><td colspan="3"><strong>Phones and social media (H1)</strong></td></tr>
<tr><td>Sex pattern</td><td>Girls' relative rise exceeds boys' everywhere: ACS +17% vs +9% (2008–10 → 2017–19), YRBS sadness +26% vs +19%; after 2020 girls 45–55% vs boys 16–23%.</td><td><span class="pill for">H1 / H3</span></td></tr>
<tr><td>Timing in early vs late LTE markets</td><td>No timing effect. Metros that got LTE early and late track each other through 2013; the event study is 0.02 pp (SE 0.15) on 279 dated metros, −0.04 (0.19) for girls; no effect again at county level in six state surveys.</td><td><span class="pill against">not H1 via rollout timing</span></td></tr>
<tr><td>U.S. adoption exposure level</td><td>Teen-household smartphone-internet share predicts YRBS girls' sadness within states (+0.9 pp per 10 points, SE 0.44) but not at county level (+0.1, SE 0.1). Suggestive at most.</td><td><span class="pill">weak H1</span></td></tr>
<tr><td>Phone-first countries, use-based exposure</td><td>MICS (68 surveys): caregiver-reported anxiety and depression show no relation to cluster connectivity or a girl's own daily phone/internet use; the one positive coefficient is matched by the 5–9-year-olds (a placebo comparison, since they are not the exposed group). GSHS (39 countries): no relation to internet penetration, mobile-broadband subscriptions or 3G/4G coverage. Census cognitive item uninformative.</td><td><span class="pill against">not H1 on adult- or cluster-measured use</span></td></tr>
<tr><td>Self-reported phone hours</td><td>GSHS 2022–23 (five countries): girls on a phone 3+ h/day report loneliness +11 pp and suicidal ideation +12 pp, monotonic in hours; boys about half. Nepal 2022 PHQ-9/GAD-7 point the same way for 15–19-year-olds. One-time self-report, so the direction of cause is open.</td><td><span class="pill for">H1 pattern, not timing</span></td></tr>

<tr><td colspan="3"><strong>School pressure (H2)</strong></td></tr>
<tr><td>Age pattern and seasonality</td><td>Through 2019 the 12–14 and 15–17 rises are similar and 18–24 rises more, so no high-stakes-years signature. Seasonality is not testable in public ACS. ATUS: homework on school weekdays up about 40% (52 → 71 min) between 2003–08 and 2015–19, sleep flat, in-person socializing down.</td><td><span class="pill for">school demand rose</span> (H2 premise)</td></tr>
<tr><td>HBSC schoolwork pressure</td><td>Pressure and psychosomatic complaints both rose after 2009/10 across ~45 countries, and complaints rose more where pressure rose more (slope 0.14–0.24). But the slope is the same in the 2002–2010 placebo comparison period and most of the rise is common to all countries.</td><td><span class="pill">H2 partly</span> pressure is a real correlate, not the break</td></tr>
<tr><td>State accountability policy</td><td>Waivers, Common Core testing, teacher evaluation and exit exams show no relation to ACS, YRBS or NSDUH outcomes; the apparent Race to the Top effect disappears when traced year by year.</td><td><span class="pill against">not H2 via U.S. policy shocks</span></td></tr>
<tr><td colspan="3"><strong>Interaction (H3)</strong></td></tr>
<tr><td>LTE × school pressure</td><td>Early-LTE markets in high-pressure states did not rise more; where the comparison can be made, the interaction is negative for girls.</td><td><span class="pill against">not H3 via state policy</span></td></tr>
<tr><td>School phone bans</td><td>PISA 2022, 80 systems: ban schools have 12 pp less daily in-school use; girls report 1.4 pp less loneliness and 2 pp less device anxiety, +0.02–0.03 SD belonging and life satisfaction; also more reported distraction (selection). U.S. statewide bans (2024–26) not yet testable. Nationally, school prohibitions fell 91% → 66% during 2009–16 and then re-tightened while sadness first rose and then fell.</td><td><span class="pill for">H1 / H3 direction, small; U.S. test pending</span></td></tr>
<tr><td>Bans × academic pressure</td><td>PISA 2022: the ban's association with less loneliness is larger for students with high schoolwork anxiety (girls −1.2 vs −0.3 pp; boys −0.8 vs +1.1), but the difference is within its standard error and the pressure measure is a proxy.</td><td><span class="pill">H3 direction, not established</span></td></tr>
</tbody></table></div>

<h2 id="part1">Part 1 · The rise, and whether public data can measure it</h2>
<p>Before either hypothesis can be tested, the outcome has to be established: is there a rise, is it real rather than a change in reporting, and which public measures track it. This part uses the American Community Survey, the national depression and sadness surveys, and the state youth surveys.</p>
<h3 id="acs">The ACS cognitive-difficulty item, 2008–2024</h3>
<p>The American Community Survey asks, of everyone 5 and older, whether the person has "serious difficulty concentrating, remembering, or making decisions" because of a physical, mental, or emotional condition. The question has been stable since 2008 (2005–07 used different wording and is excluded). Each year samples about 240,000 12–17-year-olds. Standard errors use the 80 successive-difference replicate weights.</p>
{fig_div('acs_levels')}
<p class="caption">Shaded bands are 95% confidence intervals. The grey band marks the 2020 experimental ACS release, which had severe nonresponse problems.</p>
<div class="tw"><table><thead><tr><th>Age</th><th>Sex</th><th>2008–10 %</th><th>2017–19 %</th><th>Rel. change</th><th>2022–24 %</th><th>Rel. change</th></tr></thead><tbody>{sexrows}</tbody></table></div>
<h4>Age gradient</h4>
{fig_div('acs_index')}
<p class="caption">Each line is the group's rate divided by its own 2008–10 mean. Thick lines are the adolescent groups.</p>
<p>Two things stand out. The 2010s rise is real but modest in this item (about half a percentage point on a base of 3–5%), and it is shared by every age under 50, with 18–24 rising most. The post-2020 acceleration is far larger and is concentrated in girls and young women. The item is a disability screener, so it will understate mood disorders that do not impair concentration; the next section tests whether it moves with the depression measures at all.</p>


<h3 id="gates">Does the ACS item measure adolescent distress?</h3>
{extra['validation']}


<h3 id="geo">Geographic variation: is there anything to explain?</h3>
<p>For a rollout design to work, the change among 12–17-year-olds has to differ across places by more than sampling noise. Using metropolitan areas (plus each state's non-metro remainder) as the unit, the average change from 2008–10 to 2017–19 is about half a percentage point, the true spread across metros is about the same size, and the sampling error for a typical metro is a bit larger still. In other words, real differences between places exist, but no single metro's change can be trusted on its own; the metros have to be analysed together. (Statistics: weighted mean +0.47 pp, between-metro SD 0.46 pp, median sampling error 0.64 pp, Cochran's Q 218 on 116 df, I² ≈ 0.47.)</p>
{fig_div('market_funnel')}
<p class="caption">117 markets with at least 1,500 sampled 12–17-year-olds in 2008–10. Dashed lines are the ±1.96 SE funnel around the pooled mean for a market of that size.</p>
<h4>States, by sex</h4>
<p>At the state level the boys' change varies a lot from state to state, but the girls' change is nearly the same everywhere (I² ≈ 0.46 for boys versus 0.05 for girls). Since the girls' component is the one that tracks distress, there is little geographic variation for a U.S. design to work with, which is the main weakness of the U.S. part of the study.</p>
{fig_div('state_caterpillar')}
<h4>Who is driving the rise</h4>
<p>Relative changes by subgroup, ages 12–17. The steepest rises are among the most advantaged teens.</p>
{comp_html}


{extra['ss_trends']}

<h2 id="part2">Part 2 · Phones and social media (H1)</h2>
<p>The phone hypothesis predicts that distress rose first where and when smartphones and mobile data arrived, that heavier users are worse off, and that the same pattern appears in countries that went straight to phones. The tests run from the coarsest exposure (when a metro got 4G) to the finest (an adolescent's own reported hours).</p>
<h3 id="lte">4G rollout across U.S. metros</h3>
<p>The central test of the phone hypothesis: if fast mobile data mattered, teenagers in metros that got 4G first should have turned worse first.</p>
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
<p>Kenya 2009/2019 and Mexico 2010/2020 were scanned as the best pairs. Both 2020-round censuses carry the Washington Group item on difficulty remembering or concentrating, and Kenya 2019 also asks each person about mobile phone ownership and internet use. But the 2010-round items were yes/no "mental disability" questions, so the two-point change is dominated by wording. Within 2019/2020, prevalence at 12–17 is 0.8–1.8% (any difficulty) and 0.2–0.7% (a lot or cannot), boys exceed girls at every child age, and district-level regressions of the 12–17 rate on teen phone ownership or internet use (Kenya, 76 district-sex observations) or household internet (Mexico, 3,259 municipality-sex observations) give coefficients within ±0.01 pp per percentage point of exposure level. The census item behaves like a developmental-disability measure and is not sensitive to adolescent distress. This evidence can only corroborate, not test.</p>


<h2 id="part3">Part 3 · School pressure (H2)</h2>
<p>The school-pressure hypothesis predicts that distress rose where and when schooling became more demanding: in the high-stakes years, in the school year, in states that adopted accountability testing, and in countries where students report more schoolwork pressure. The tests run from time use, to the cross-national HBSC series, to U.S. state policy.</p>
<h3 id="atus">Did school demands rise? Time use of 15–17-year-olds (ATUS, 2003–2024)</h3>
<p>The American Time Use Survey gives a direct look at the school-demand channel. On school-year weekdays, homework time rose from about 50 minutes (2003–08) to about 70 minutes (2015–19) and stayed there; sleep did not fall; in-person socializing drifted down before collapsing after 2020; television fell and games rose. Note the small samples (roughly 200–800 teens per pooled period) and that phone use is mostly recorded as a secondary activity, which ATUS does not capture.</p>
{fig_div('atus')}
<p class="caption">Weighted minutes per day, non-holiday weekdays in September–May, pooled periods; bars are 95% CIs.</p>


<h3>Schoolwork pressure across countries (HBSC)</h3>
{extra['hbsc']}
<h3 id="policy">U.S. school accountability policy</h3>
<p>The central U.S. test of the school-pressure hypothesis: states adopted accountability measures at different times; if school pressure mattered, their teenagers should have turned worse when they did.</p>
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

<h2 id="next">Are we closer to an answer?</h2>
<p>Closer than the books, in three specific ways, and not close on the question the books actually argue about.</p>
<div class="tw"><table class="verdict"><thead><tr><th>Hypothesis</th><th>Where it stands after the pilot</th></tr></thead><tbody>
<tr><td>H1 · Phones and social media</td><td>The individual association is consistent and reappears in places the book's evidence does not reach: girls who use phones heavily report more loneliness and suicidal thoughts in Ghana, India, Jamaica, Morocco and Nepal as in the United States, with the same sex pattern and exposure level gradient. But every test that uses <em>timing</em> or <em>adult-measured</em> exposure shows no effect: 4G rollout across U.S. metros and counties, adoption exposure level at county level, cluster connectivity in 68 MICS surveys, coverage in 39 GSHS countries. Either the effect is real but travels through peers and platforms so evenly that geography cannot see it, or the association is largely reverse causation and shared causes. The public data cannot yet distinguish these; school phone bans (PISA, Norway) lean modestly toward a real effect for girls.</td></tr>
<tr><td>H2 · School pressure</td><td>Gray's premise holds up better than Haidt's collaborative reviews allow: schoolwork pressure rose after 2010 in most HBSC countries, not only the U.S., and U.S. homework time rose about 40%. But pressure behaves as a stable correlate of complaints rather than the cause of the break, U.S. accountability shocks show no effect, and the age pattern lacks the high-stakes-years signature. The real limitation is measurement: "pressure" is one survey item, while phone use can at least be counted in hours, so H2 is harder to test than H1 rather than refuted.</td></tr>
<tr><td>H3 · Interaction</td><td>Not supported through state policy crossed with 4G timing, but the sharper version, phones during school hours on top of high-stakes academics, fits the ban evidence best: bans cut in-school use, girls in ban schools report less loneliness and device anxiety, the association is larger for students under high schoolwork anxiety (not significantly), Norway's bans reduced girls' psychological consultations, and U.S. sadness moved inversely to school prohibitions. It is the hypothesis the pending U.S. ban studies and the HBSC microdata can test directly, and the one that would reconcile the two books.</td></tr>
<tr><td>H0 · Measurement</td><td>Rejected as the main story: the rise is present in self-report, caregiver-report and diagnostic measures, the 65+ placebo comparison moves the other way, and it is concentrated in girls everywhere. Reporting and diagnosis-seeking plausibly add to it (the rise is steepest among affluent teens), but do not create it.</td></tr>
</tbody></table></div>
<p>Three findings that neither book contains. First, the rise was broad and nearly simultaneous across places with very different connectivity and schooling histories, which is why coarse designs cannot separate the theses and why both camps can find support in national trends. Second, the post-2021 reversal in the U.S. state surveys is as large as the 2013–2021 rise, without a comparable fall in phone use, and it coincides with schools re-tightening phone rules; a pure exposure level story and a pure school-pressure story both have to explain it. Third, the association between phone use and distress appears only when the adolescent reports both her own use and her own state; caregiver-reported symptoms in 68 countries show nothing. That is the fact the next phase has to resolve.</p>
<div class="note"><strong>What would settle it, and what this project should do next.</strong>
<ul>
<li>Follow the 2024–26 U.S. state and district phone bans through the 2025–27 YRBS and state-survey waves, by sex, for at least two years after each ban, with the 65+ comparison group retained. The policy table and the model are ready; the first data wave is the 2025 YRBS.</li>
<li>License GSMA coverage polygons and apply for the MICS and DHS cluster coordinates, then test the adolescent-reported phone-hours items (GSHS 2022–23, MICS7) against local coverage timing. This is the one design that measures exposure on the adolescent herself while using something other than her own choices to explain it.</li>
<li>Apply for the HBSC microdata to run the concentration test (are complaints increasingly concentrated among high-pressure students?) and the student-level social-media × pressure interaction, which is the only available test of H3.</li>
<li>Stop extending the ACS market event study and the census cognitive item; they have done what they can. Defer the restricted-data route (the Census Bureau research data centers) until a state-survey or ban result justifies it.</li>
</ul></div>
<p class="caption">Reproducibility: scripts in <code>~/teen-mh-pilot/scripts</code>, tables in <code>results/tables</code>. Data: IPUMS USA (ACS 1-year 2005–2024), IPUMS ATUS 2003–2024, IPUMS International (ke2009a, ke2019a, mx2010a, mx2020a), IPUMS CPS; public NSDUH, NHANES, YRBS, HBSC, GSHS, NTIA files as noted in each section.</p>
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
