"""Compile the public NHIS-Teen aggregates (no microdata are public) into two small committed tables:
  data/compiled/nhis/nhis_teen_query_tool.csv  - tidy version of NCHS "Interactive Summary Health Statistics for Teens" (data.cdc.gov 5pqj-rvh4):
      teen-reported indicators (GAD-2/PHQ-2 symptoms, 2+ h screen time, bullying, sleep, support, ...) by parent-reported subgroup, two periods.
  data/compiled/nhis/nhis_teen_published.csv   - numbers transcribed from NCHS publications on NHIS-Teen and related NHIS reports (screen-time and
      bullying gradients in teen symptoms, parent-teen agreement studies, adult WG vs GAD-7/PHQ-8 agreement, NHIS-Teen response rates), each with
      its source and URL; every value was checked against the PDF/HTML text saved under data/external/nhis/teen/.
Usage: uv run python scripts/download/nhis/03_compile_teen_published.py"""
import pandas as pd, numpy as np, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[3]; RAW = ROOT/"data/external/nhis/teen"; OUT = ROOT/"data/compiled/nhis"; OUT.mkdir(parents=True, exist_ok=True)
q = pd.read_csv(RAW/"data_cdc_gov_5pqj-rvh4.csv")
q["period"] = q["Date Range"].str.replace("^DY", "", regex=True).str.replace("-", "–")
ci = q["Confidence Interval"].fillna("").str.extract(r"([\d.]+)\s*,\s*([\d.]+)")
t = pd.DataFrame(dict(indicator_code=q.stat_var, indicator=q["Outcome (or Indicator)"], topic=q.stat_group.str.replace(r"\s+$", "", regex=True),
                      period=q.period, group_var=q.col_var, group_label=q.col_label, group=q.Group,
                      pct=np.where(q.Percentage >= 999, np.nan, q.Percentage), ci_lo=pd.to_numeric(ci[0]), ci_hi=pd.to_numeric(ci[1]),
                      reliable=q.CR_P_RELIABLE.eq(1), definition=q.new_caption2))
t["topic"] = t.topic.replace({"Experiences with discriminatio": "Experiences with discrimination", "Mental health care and unmet n": "Mental health care and unmet need"})
t = t.sort_values(["indicator_code", "period", "group_var", "group"]).reset_index(drop=True)
t.to_csv(OUT/"nhis_teen_query_tool.csv", index=False)
print(f"query tool: {len(t):,} rows, {t.indicator_code.nunique()} indicators, periods {sorted(t.period.unique())}")

DB513 = "https://www.cdc.gov/nchs/products/databriefs/db513.htm"; DB514 = "https://www.cdc.gov/nchs/products/databriefs/db514.htm"
PCD = "https://doi.org/10.5888/pcd22.240537"; N206 = "https://dx.doi.org/10.15620/cdc/156514"; N219 = "https://dx.doi.org/10.15620/cdc/174622"
N172 = "https://www.cdc.gov/nchs/data/nhsr/nhsr172.pdf"; ACE = "https://doi.org/10.1016/j.chiabu.2025.107339"; WT30 = "https://www.cdc.gov/nchs/data/nhis/teen/NHIS-Teen-Weighting-30m-Report.pdf"
DLR = "https://doi.org/10.1037/a0038498"
P30, P18 = "July 2021–December 2023", "July 2021–December 2022"
rows = [
 # Data Brief 513 (Zablotsky, Arockiaraj, Haile, Ng 2024): teen-reported weekday non-school screen time and GAD-2/PHQ-2 symptoms, data table for Figure 4
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus", level="4+ hours", outcome="anxiety", value=27.1, ci_lo=23.7, ci_hi=30.8, se=1.76, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus", level="<4 hours", outcome="anxiety", value=12.3, ci_lo=9.8, ci_hi=15.2, se=1.32, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus", level="4+ hours", outcome="depression", value=25.9, ci_lo=22.2, ci_hi=29.8, se=1.89, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus", level="<4 hours", outcome="depression", value=9.5, ci_lo=7.2, ci_hi=12.1, se=1.20, url=DB513),
 # Data Brief 513 Figure 1-2: distribution of teen-reported screen hours and 4+ hours by sex/age
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_hours", level="<1 hour", outcome="share", value=3.0, ci_lo=2.0, ci_hi=4.2, se=0.54, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_hours", level="1 hour", outcome="share", value=6.1, ci_lo=4.8, ci_hi=7.6, se=0.71, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_hours", level="2 hours", outcome="share", value=17.8, ci_lo=15.8, ci_hi=19.9, se=1.04, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_hours", level="3 hours", outcome="share", value=22.8, ci_lo=20.6, ci_hi=25.1, se=1.13, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_hours", level="4+ hours", outcome="share", value=50.4, ci_lo=47.6, ci_hi=53.2, se=1.40, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus_by_group", level="Male", outcome="share", value=48.3, ci_lo=44.4, ci_hi=52.2, se=1.95, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus_by_group", level="Female", outcome="share", value=52.5, ci_lo=48.5, ci_hi=56.5, se=2.00, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus_by_group", level="12-14 years", outcome="share", value=45.6, ci_lo=41.5, ci_hi=49.8, se=2.07, url=DB513),
 dict(source="NCHS Data Brief 513", period=P30, measure="pct", exposure="screen_4plus_by_group", level="15-17 years", outcome="share", value=55.0, ci_lo=51.2, ci_hi=58.9, se=1.93, url=DB513),
 # Zablotsky et al. 2025, Prev Chronic Dis 22:240537 (n = 1,952): prevalence ratios 4+ vs <4 hours, adjusted for age, sex, race/Hispanic origin, urbanization, parental education, family income
 dict(source="Zablotsky et al. 2025 PCD", period=P30, measure="PR", exposure="screen_4plus", level="4+ vs <4 hours", outcome="anxiety", value=2.21, ci_lo=1.72, ci_hi=2.82, n=1952, url=PCD),
 dict(source="Zablotsky et al. 2025 PCD", period=P30, measure="APR", exposure="screen_4plus", level="4+ vs <4 hours", outcome="anxiety", value=2.12, ci_lo=1.67, ci_hi=2.71, n=1952, url=PCD),
 dict(source="Zablotsky et al. 2025 PCD", period=P30, measure="PR", exposure="screen_4plus", level="4+ vs <4 hours", outcome="depression", value=2.74, ci_lo=2.04, ci_hi=3.67, n=1952, url=PCD),
 dict(source="Zablotsky et al. 2025 PCD", period=P30, measure="APR", exposure="screen_4plus", level="4+ vs <4 hours", outcome="depression", value=2.51, ci_lo=1.89, ci_hi=3.35, n=1952, url=PCD),
 # Data Brief 514 (Haile et al. 2024): teen-reported bullying in past 12 months and GAD-2/PHQ-2 symptoms, data table for Figure 4
 dict(source="NCHS Data Brief 514", period=P30, measure="pct", exposure="bullied_12m", level="Bullied", outcome="anxiety", value=29.8, ci_lo=25.4, ci_hi=34.5, se=2.25, url=DB514),
 dict(source="NCHS Data Brief 514", period=P30, measure="pct", exposure="bullied_12m", level="Not bullied", outcome="anxiety", value=14.5, ci_lo=12.2, ci_hi=17.0, se=1.20, url=DB514),
 dict(source="NCHS Data Brief 514", period=P30, measure="pct", exposure="bullied_12m", level="Bullied", outcome="depression", value=28.5, ci_lo=23.9, ci_hi=33.3, se=2.33, url=DB514),
 dict(source="NCHS Data Brief 514", period=P30, measure="pct", exposure="bullied_12m", level="Not bullied", outcome="depression", value=12.1, ci_lo=9.9, ci_hi=14.6, se=1.18, url=DB514),
 dict(source="NCHS Data Brief 514", period=P30, measure="pct", exposure="bullied_12m", level="Total", outcome="share", value=34.0, ci_lo=31.4, ci_hi=36.7, url=DB514),
 # NHSR 206 (Zablotsky et al. 2024): teen-reported social/emotional support (always/usually vs not) and symptoms; parent vs teen support estimates
 dict(source="NCHS NHSR 206", period=P18, measure="pct", exposure="support_always_usually", level="Yes", outcome="anxiety", value=12.9, url=N206),
 dict(source="NCHS NHSR 206", period=P18, measure="pct", exposure="support_always_usually", level="No", outcome="anxiety", value=33.1, url=N206),
 dict(source="NCHS NHSR 206", period=P18, measure="pct", exposure="support_always_usually", level="Yes", outcome="depression", value=8.0, url=N206),
 dict(source="NCHS NHSR 206", period=P18, measure="pct", exposure="support_always_usually", level="No", outcome="depression", value=31.1, url=N206),
 dict(source="NCHS NHSR 206", period=P18, measure="n", exposure="sample", level="teen (NHIS-Teen)", outcome="support", value=1157, url=N206),
 dict(source="NCHS NHSR 206", period=P18, measure="n", exposure="sample", level="parent (Sample Child 12-17)", outcome="support", value=4379, url=N206),
 # NHSR 219 (Ng et al. 2025): parent vs teen reports of health-care use, same teens (linked, RDC), weighted Cohen's kappa
 dict(source="NCHS NHSR 219", period=P30, measure="pct", exposure="informant", level="parent", outcome="doctor visit 12m", value=91.4, url=N219),
 dict(source="NCHS NHSR 219", period=P30, measure="pct", exposure="informant", level="teen", outcome="doctor visit 12m", value=83.0, url=N219),
 dict(source="NCHS NHSR 219", period=P30, measure="pct", exposure="informant", level="parent", outcome="usual place of care", value=96.3, url=N219),
 dict(source="NCHS NHSR 219", period=P30, measure="pct", exposure="informant", level="teen", outcome="usual place of care", value=87.0, url=N219),
 dict(source="NCHS NHSR 219", period=P30, measure="pct", exposure="informant", level="parent", outcome="time alone with doctor", value=46.5, url=N219),
 dict(source="NCHS NHSR 219", period=P30, measure="pct", exposure="informant", level="teen", outcome="time alone with doctor", value=37.6, url=N219),
 dict(source="NCHS NHSR 219", period=P30, measure="kappa", exposure="informant", level="min (personal doctor or nurse)", outcome="health-care use", value=0.08, url=N219),
 dict(source="NCHS NHSR 219", period=P30, measure="kappa", exposure="informant", level="max (time alone with doctor)", outcome="health-care use", value=0.42, url=N219),
 # Ng et al. 2025 Child Abuse & Neglect: parent vs teen ACEs (linked, RDC)
 dict(source="Ng et al. 2025 Child Abuse Negl", period=P30, measure="pct", exposure="informant", level="parent", outcome="victim/witness of neighborhood violence", value=6.5, url=ACE),
 dict(source="Ng et al. 2025 Child Abuse Negl", period=P30, measure="pct", exposure="informant", level="teen", outcome="victim/witness of neighborhood violence", value=15.5, url=ACE),
 dict(source="Ng et al. 2025 Child Abuse Negl", period=P30, measure="kappa", exposure="informant", level="min", outcome="ACEs", value=0.27, url=ACE),
 dict(source="Ng et al. 2025 Child Abuse Negl", period=P30, measure="kappa", exposure="informant", level="max", outcome="ACEs", value=0.53, url=ACE),
 # NHSR 172 (Zablotsky et al. 2022): adults answering both WG items and GAD-7/PHQ-8 in the 2019 NHIS
 dict(source="NCHS NHSR 172", period="2019", measure="pct_agreement", exposure="WG item vs scale (self-report, adults)", level="anxiety (WG-ANX vs GAD-7)", outcome="agreement", value=90, url=N172),
 dict(source="NCHS NHSR 172", period="2019", measure="pct_agreement", exposure="WG item vs scale (self-report, adults)", level="depression (WG-DEP vs PHQ-8)", outcome="agreement", value=90, url=N172),
 dict(source="NCHS NHSR 172", period="2019", measure="pct", exposure="WG item vs scale (self-report, adults)", level="highest on one, lowest on other: anxiety", outcome="extreme discordance", value=2.1, url=N172),
 dict(source="NCHS NHSR 172", period="2019", measure="pct", exposure="WG item vs scale (self-report, adults)", level="highest on one, lowest on other: depression", outcome="extreme discordance", value=1.6, url=N172),
 # De Los Reyes et al. 2015 meta-analysis (341 studies): cross-informant correlations
 dict(source="De Los Reyes et al. 2015", period="1989–2014", measure="r", exposure="cross-informant", level="internalizing", outcome="correlation", value=0.25, n=341, url=DLR),
 dict(source="De Los Reyes et al. 2015", period="1989–2014", measure="r", exposure="cross-informant", level="externalizing", outcome="correlation", value=0.30, n=341, url=DLR),
 # NHIS-Teen 30-month weighting report: eligibility, permission, participation
 dict(source="NHIS-Teen weighting report (30 m)", period=P30, measure="n", exposure="response", level="eligible sample children 12-17", outcome="n", value=7323, url=WT30),
 dict(source="NHIS-Teen weighting report (30 m)", period=P30, measure="n", exposure="response", level="parent permission given", outcome="n", value=4242, url=WT30),
 dict(source="NHIS-Teen weighting report (30 m)", period=P30, measure="n", exposure="response", level="completed teen interviews", outcome="n", value=1958, url=WT30),
 dict(source="NHIS-Teen weighting report (30 m)", period=P30, measure="pct", exposure="response", level="parent permission rate", outcome="rate", value=60.4, url=WT30),
 dict(source="NHIS-Teen weighting report (30 m)", period=P30, measure="pct", exposure="response", level="teen participation rate", outcome="rate", value=46.2, url=WT30),
 dict(source="NHIS-Teen weighting report (30 m)", period=P30, measure="pct", exposure="response", level="overall response rate", outcome="rate", value=27.9, url=WT30),
]
p = pd.DataFrame(rows); p.to_csv(OUT/"nhis_teen_published.csv", index=False); print(f"published: {len(p)} rows from {p.source.nunique()} sources")
