import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pathlib
FIG = pathlib.Path("results/figures_exploratory"); FIG.mkdir(parents=True, exist_ok=True)
PAL = ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7","#e34948"]
plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.alpha":.25,"figure.dpi":130})
nat = pd.read_csv("results/tables/acs_national_year_sex_age.csv"); nat = nat[nat.year>=2008]
nat["rate"]*=100; nat["se"]*=100
sexlab = {1:"Boys/Men",2:"Girls/Women"}
# Fig 1: 12-14, 15-17 by sex, with 65+ placebo, levels
fig, axes = plt.subplots(1,3, figsize=(12,3.8), sharex=True)
for ax, ag in zip(axes, ["12-14","15-17","65+"]):
    for i,(sx,lab) in enumerate(sexlab.items()):
        d = nat[(nat.agegrp==ag)&(nat.sex==sx)]
        ax.plot(d.year, d.rate, color=PAL[i], lw=2, label=lab); ax.fill_between(d.year, d.rate-1.96*d.se, d.rate+1.96*d.se, color=PAL[i], alpha=.15, lw=0)
        ax.text(d.year.iloc[-1]+.3, d.rate.iloc[-1], lab, color=PAL[i], va="center", fontsize=9)
    ax.axvspan(2019.5,2020.5,color="grey",alpha=.12,lw=0); ax.set_title(f"Ages {ag}", loc="left"); ax.set_xlim(2008,2026)
axes[0].set_ylabel("% with cognitive difficulty (ACS)")
fig.suptitle("ACS cognitive difficulty, 2008-2024: 12-14 and 15-17 rise, 65+ falls (shaded band = 95% CI; 2020 = experimental ACS)", x=0.01, ha="left", fontsize=11)
fig.tight_layout(); fig.savefig(FIG/"fig1_acs_levels_by_sex_age.png"); plt.close()
# Fig 2: index to 2008-10 mean = 100, all age groups, by sex
fig, axes = plt.subplots(1,2, figsize=(12,4.2), sharey=True)
ages = ["05-11","12-14","15-17","18-24","25-49","50-64","65+"]
for ax,(sx,lab) in zip(axes, sexlab.items()):
    for i,ag in enumerate(ages):
        d = nat[(nat.agegrp==ag)&(nat.sex==sx)].set_index("year")
        base = d.loc[2008:2010,"rate"].mean(); idx = 100*d.rate/base
        lw = 2.4 if ag in ("12-14","15-17") else 1.3
        ax.plot(idx.index, idx.values, color=PAL[i], lw=lw, label=ag, alpha=1 if lw>2 else .85)
        ax.text(2024.3, idx.loc[2024], ag, color=PAL[i], va="center", fontsize=8)
    ax.axhline(100,color="k",lw=.8); ax.axvspan(2019.5,2020.5,color="grey",alpha=.12,lw=0)
    ax.set_title(lab, loc="left"); ax.set_xlim(2008,2026)
axes[0].set_ylabel("Rate indexed to 2008-10 average = 100")
fig.suptitle("Age gradient of the rise: relative change in ACS cognitive difficulty by age group and sex", x=0.01, ha="left", fontsize=11)
fig.tight_layout(); fig.savefig(FIG/"fig2_acs_index_age_gradient.png"); plt.close()
# Fig 3: girl/boy change table print
t = nat[nat.agegrp.isin(["12-14","15-17"])].pivot_table(index="year", columns=["agegrp","sex"], values="rate")
b = t.loc[2008:2010].mean(); e = t.loc[2017:2019].mean(); p = t.loc[2022:2024].mean()
print(pd.DataFrame({"2008-10":b,"2017-19":e,"2022-24":p,"rel chg to 17-19 %":100*(e/b-1),"rel chg to 22-24 %":100*(p/b-1),"abs pp to 17-19":e-b}).round(2).to_string())
print("figs written")
