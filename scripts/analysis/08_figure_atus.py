import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
import duckdb, pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pathlib
FIG = ROOT/"results/figures_exploratory"; FIG.mkdir(parents=True, exist_ok=True); PAL = ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7","#e34948"]
plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.alpha":.25,"figure.dpi":130})
con = duckdb.connect()
con.sql(f"""create view a as select *, case when YEARP=2020 then WT20/1e6 else try_cast(WT as double) end as w
  from read_parquet('{ROOT.as_posix()}/data/extracts/atus/atus_*.parquet', union_by_name=true) where AGE between 15 and 17""")
cats = {"Homework":"ACTIVITY between 60300 and 60399","Sleep":"ACTIVITY between 10100 and 10199","In-person socializing":"ACTIVITY between 120100 and 120299",
        "TV & movies":"ACTIVITY in (120303,120304)","Games":"ACTIVITY=120307","Computer leisure (non-game)":"ACTIVITY=120308","Sports & exercise":"ACTIVITY between 130100 and 130199","Class time":"ACTIVITY between 60100 and 60199"}
sel = ", ".join(f'sum(case when {c} then DURATION else 0 end) as "{k}"' for k,c in cats.items())
r = con.sql(f"""select YEARP as year, CASEIDA, any_value(w) w, any_value(SEX) sex, any_value(MONTH) as mon, any_value(DAY) as dow, any_value(HOLIDAY) as hol, {sel}
   from a group by 1,2""").df()
r = r[(~r.mon.isin([6,7,8])) & (~r.dow.isin([1,7])) & (r.hol!=1)]
r["period"] = pd.cut(r.year, [2002,2005,2008,2011,2014,2017,2019,2022,2025], labels=["2003-05","2006-08","2009-11","2012-14","2015-17","2018-19","2020-22","2023-25"])
mid = {"2003-05":2004,"2006-08":2007,"2009-11":2010,"2012-14":2013,"2015-17":2016,"2018-19":2018.5,"2020-22":2021,"2023-25":2024}
def wstats(g, k):
    w = g.w/g.w.sum(); m = np.sum(w*g[k]); v = np.sum(w**2*(g[k]-m)**2); return pd.Series({"mean":m,"se":np.sqrt(v),"n":len(g)})
fig, axes = plt.subplots(2,4, figsize=(13,6.2)); axes = axes.ravel()
for i,(k,ax) in enumerate(zip(cats, axes)):
    s = r.groupby("period", observed=True).apply(lambda g: wstats(g,k), include_groups=False).reset_index(); s["x"] = s.period.map(mid)
    ax.errorbar(s.x, s["mean"], yerr=1.96*s.se, fmt="o-", color=PAL[i%8], lw=2, ms=5, capsize=2)
    ax.axvspan(2019.5,2020.5,color="grey",alpha=.12,lw=0); ax.set_title(k, loc="left", fontsize=10); ax.set_ylim(bottom=0)
    if i%4==0: ax.set_ylabel("Minutes per day")
fig.suptitle("ATUS, ages 15-17, school-year weekdays (non-holiday): weighted minutes per day, pooled 2-3 year periods, 95% CI", x=0.01, ha="left", fontsize=11)
fig.tight_layout(); fig.savefig(FIG/"fig5_atus_1517_mediators.png"); plt.close()
t = pd.concat({k: r.groupby("period", observed=True).apply(lambda g: wstats(g,k), include_groups=False) for k in cats}, axis=1); t.to_csv(ROOT/"results/tables/atus_1517_schoolweekday_period_se.csv"); print(t.round(1).to_string())
