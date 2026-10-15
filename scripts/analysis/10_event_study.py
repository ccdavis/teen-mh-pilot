"""Step 4: event study of ACS 12-17 cognitive difficulty on LTE onset by market (CBSA + state non-metro).
Usage: uv run python scripts/analysis/10_event_study.py results/tables/lte_onset_first_launch_date.csv [--dated-only]
The onset CSV (written by 10a_lte_onset_tables.py) has columns market (MET2013 code) and onset_date (YYYY-MM-DD or YYYY-MM).
--dated-only keeps only markets with a recorded launch date; this is the primary specification. Without it, markets with no
recorded launch (small metros and the state non-metro remainders) are treated as never treated, which is a bound rather than
an estimate, since most of them received LTE in 2013-14. Without an onset file, runs a placebo with random onset years
(mechanics check only).
Estimation: pyfixest feols, weights = pop, market + year FE, event-time dummies (ref = -1), cluster by market; by sex; 65+ and 25-49 placebos.
Output: results/tables/event_study_<onset>_<dated_only|with_untreated>.csv
"""
import argparse, pathlib, numpy as np, pandas as pd, pyfixest as pf
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = ROOT/"results/tables"
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("onset", nargs="?", help="CSV with columns market, onset_date; omit for the random placebo")
ap.add_argument("--dated-only", action="store_true", help="drop markets without an onset date (primary specification)")
args = ap.parse_args()
cells = pd.concat([pd.read_parquet(f) for f in sorted((ROOT/"data/extracts/acs").glob("cells_us20*.parquet"))])
cells = cells[cells.year.between(2008, 2019)]
cells["market"] = np.where(cells.met2013 > 0, cells.met2013, cells.statefip*100000)
def panel(agegrps, sex=None):
    d = cells[cells.agegrp.isin(agegrps)]
    if sex: d = d[d.sex == sex]
    g = d.groupby(["market","year"]).agg(n=("n_unwt","sum"), pop=("n_w","sum"), rem=("rem_w","sum"), sens=("sens_w","sum")).reset_index()
    g["y"] = 100*g.rem/g["pop"]; g["y_sens"] = 100*g.sens/g["pop"]; g["statefip"] = np.where(g.market >= 100000, g.market//100000, np.nan)
    return g
if args.onset:
    onset = pd.read_csv(args.onset); od = pd.to_datetime(onset.onset_date, format="mixed"); onset["onset_year"] = od.dt.year + (od.dt.month > 6).astype(int)  # school-year exposure: launches after June count from next year
    onset = onset[["market","onset_year"]]; tag = pathlib.Path(args.onset).stem.replace("lte_onset_","") + ("_dated_only" if args.dated_only else "_with_untreated")
else:
    rng = np.random.default_rng(0); mk = cells.market.unique(); onset = pd.DataFrame({"market": mk, "onset_year": rng.choice([2011,2012,2013,2014,np.nan], size=len(mk))}); tag = "placebo_random"
def run(g, label):
    g = g.merge(onset, on="market", how="left"); g = g[g.n >= 100]
    if args.dated_only: g = g[g.onset_year.notna()]
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
