import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pathlib
FIG = ROOT/"results/figures_exploratory"; FIG.mkdir(parents=True, exist_ok=True); PAL = ["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300","#4a3aa7","#e34948"]
plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False,"axes.grid":True,"grid.alpha":.25,"figure.dpi":130})
lab = pd.read_csv(ROOT/"notes/acs_value_labels.csv"); st = lab[lab.variable=="STATEFIP"].set_index("outputcode")["label"].to_dict()
met = lab[lab.variable=="MET2013"].set_index("outputcode")["label"].to_dict()
# Fig 3: state changes by sex, caterpillar
s = pd.read_csv(ROOT/"results/tables/acs_state_year_sex_1217.csv").rename(columns={"pop":"pop_"})
def pool(d, yrs):
    d = d[d.year.isin(yrs)]; w = d.pop_/d.pop_.sum(); return pd.Series({"rate": np.sum(w*d.rate), "se": np.sqrt(np.sum(w**2*d.se**2))})
rows=[]
for (sf,sx),d in s.groupby(["statefip","sex"]):
    b=pool(d,[2008,2009,2010]); e=pool(d,[2017,2018,2019])
    rows.append({"statefip":sf,"sex":sx,"delta":100*(e.rate-b.rate),"se":100*np.sqrt(b.se**2+e.se**2),"base":100*b.rate})
ch = pd.DataFrame(rows)
fig, axes = plt.subplots(1,2, figsize=(12,8), sharey=False)
for ax,(sx,title) in zip(axes,[(1,"Boys 12-17"),(2,"Girls 12-17")]):
    d = ch[ch.sex==sx].sort_values("delta").reset_index(drop=True)
    ax.errorbar(d.delta, range(len(d)), xerr=1.96*d.se, fmt="o", ms=4, color=PAL[sx-1], ecolor=PAL[sx-1], alpha=.8, lw=1)
    ax.set_yticks(range(len(d))); ax.set_yticklabels([st.get(x, x) for x in d.statefip], fontsize=7)
    ax.axvline(0,color="k",lw=.8); ax.axvline(np.average(d.delta, weights=1/d.se**2), color="grey", ls="--", lw=1)
    ax.set_title(title, loc="left"); ax.set_xlabel("Change in % cognitive difficulty, 2008-10 to 2017-19 (pp, 95% CI)")
fig.suptitle("State-level change is heterogeneous for boys (I²≈0.46) but nearly uniform for girls (I²≈0.05)", x=0.01, ha="left")
fig.tight_layout(); fig.savefig(FIG/"fig3_state_change_caterpillar.png"); plt.close()
# Fig 4: market change vs baseline sample size (funnel), 117 markets
m = pd.read_csv(ROOT/"results/tables/acs_market_change_0810_to_1719.csv")
m["name"] = [met.get(x, f"{st.get(x//100000,'?')} non-metro") for x in m.market]
fig, ax = plt.subplots(figsize=(8,5))
ax.scatter(m.b_n, 100*m.delta, s=18, color=PAL[0], alpha=.7)
ns = np.linspace(m.b_n.min(), m.b_n.max(), 200); se_typ = 100*np.median(m.se*np.sqrt(m.b_n))/np.sqrt(ns)
mu = np.average(m.delta, weights=1/m.se**2)*100
ax.plot(ns, mu+1.96*se_typ, color="grey", ls="--", lw=1); ax.plot(ns, mu-1.96*se_typ, color="grey", ls="--", lw=1); ax.axhline(mu,color="grey",lw=1)
for _,r in m.nlargest(5,"delta").iterrows(): ax.annotate(r["name"].split(",")[0], (r.b_n, 100*r.delta), fontsize=7, xytext=(3,3), textcoords="offset points")
for _,r in m.nsmallest(4,"delta").iterrows(): ax.annotate(r["name"].split(",")[0], (r.b_n, 100*r.delta), fontsize=7, xytext=(3,-8), textcoords="offset points")
ax.set_xscale("log"); ax.set_xlabel("Sampled 12-17-year-olds, 2008-10 (log)"); ax.set_ylabel("Change in % cognitive difficulty 12-17, 2008-10 to 2017-19 (pp)")
ax.set_title("Market-level changes (CBSA + state non-metro): spread exceeds the sampling funnel (I²≈0.47)", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(FIG/"fig4_market_change_funnel.png"); plt.close()
ch.to_csv(ROOT/"results/tables/acs_state_change_by_sex.csv", index=False); print("ok")
