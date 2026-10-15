"""Step 4: event study of ACS 12-17 cognitive difficulty on LTE onset by market (CBSA + state non-metro).
Usage: uv run python scripts/10_event_study.py [path/to/onset.csv]
onset.csv needs columns: market (MET2013 code, or statefip*100000 for non-metro), onset_date (YYYY-MM-DD).
Without an onset file, runs a placebo with random onset years (mechanics check only).
Estimation: pyfixest feols, weights = pop, market + year FE, event-time dummies (ref = -1), cluster by market; by sex; 65+ and sensory placebos.
"""
import sys, pathlib, numpy as np, pandas as pd, pyfixest as pf
OUT = pathlib.Path("results/tables"); FIG = pathlib.Path("results/figures_exploratory")
cells = pd.concat([pd.read_parquet(f) for f in sorted(pathlib.Path("data/extracts/acs").glob("cells_us20*.parquet"))])
cells = cells[cells.year.between(2008, 2019)]
cells["market"] = np.where(cells.met2013 > 0, cells.met2013, cells.statefip*100000)
def panel(agegrps, sex=None):
    d = cells[cells.agegrp.isin(agegrps)]
    if sex: d = d[d.sex == sex]
    g = d.groupby(["market","year"]).agg(n=("n_unwt","sum"), pop=("n_w","sum"), rem=("rem_w","sum"), sens=("sens_w","sum")).reset_index()
    g["y"] = 100*g.rem/g["pop"]; g["y_sens"] = 100*g.sens/g["pop"]; g["statefip"] = np.where(g.market >= 100000, g.market//100000, np.nan)
    return g
if len(sys.argv) > 1:
    onset = pd.read_csv(sys.argv[1]); od = pd.to_datetime(onset.onset_date, format="mixed"); onset["onset_year"] = od.dt.year + (od.dt.month > 6).astype(int)  # school-year exposure: launches after June count from next year
    onset = onset[["market","onset_year"]]; tag = pathlib.Path(sys.argv[1]).stem.replace("lte_onset_","") + ("_dated_only" if "--dated-only" in sys.argv else "_with_untreated")
else:
    rng = np.random.default_rng(0); mk = cells.market.unique(); onset = pd.DataFrame({"market": mk, "onset_year": rng.choice([2011,2012,2013,2014,np.nan], size=len(mk))}); tag = "placebo_random"
def run(g, label):
    g = g.merge(onset, on="market", how="left"); g = g[g.n >= 100]
    if "--dated-only" in sys.argv: g = g[g.onset_year.notna()]
    g["rel"] = (g.year - g.onset_year).clip(-4, 6); g.loc[g.onset_year.isna(), "rel"] = -1  # never-treated as controls at ref
    g["rel"] = g.rel.fillna(-1).astype(int); g["treated"] = (g.year >= g.onset_year).astype(int)
    m_es = pf.feols("y ~ i(rel, ref=-1) | market + year", data=g, weights="pop", vcov={"CRV1": "market"})
    m_dd = pf.feols("y ~ treated | market + year", data=g, weights="pop", vcov={"CRV1": "market"})
    es = m_es.tidy().reset_index(); es["k"] = es["Coefficient"].astype(str).str.extract(r"(-?\d+)\]?$")[0].astype(float); es = es.dropna(subset=["k"]).sort_values("k")
    print(f"\n{label}: DiD coef on treated = {m_dd.coef().iloc[0]:.3f} (se {m_dd.se().iloc[0]:.3f}), N={m_dd._N}")
    print(es[["k","Estimate","Std. Error"]].round(3).to_string(index=False)); return es, m_dd
results = {}
for lab, kw in {"12-17 all": (["12-14","15-17"], None), "12-17 girls": (["12-14","15-17"], 2), "12-17 boys": (["12-14","15-17"], 1), "65+ placebo": (["65+"], None), "25-49": (["25-49"], None)}.items():
    es, dd = run(panel(*kw), lab); es["group"] = lab; results[lab] = es
pd.concat(results.values()).to_csv(OUT/f"event_study_{tag}.csv", index=False)
