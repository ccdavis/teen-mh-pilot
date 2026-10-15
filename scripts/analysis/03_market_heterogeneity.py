"""Do market-level (CBSA + state non-metro) changes in 12-17 cognitive difficulty vary more than sampling noise?"""
import pandas as pd, numpy as np, pathlib
OUT = pathlib.Path("results/tables")
def pool(d, yrs):
    d = d[d.year.isin(yrs) & (d.pop_ > 0)]
    if len(d) < len(yrs): return pd.Series({"rate": np.nan, "se": np.nan, "n": 0})
    w = d.pop_ / d.pop_.sum()
    return pd.Series({"rate": np.sum(w*d.rate), "se": np.sqrt(np.sum(w**2 * d.se**2)), "n": d.n_unwt.sum()})
def hetero(df, key, label, minn):
    df = df.rename(columns={"pop": "pop_"})
    b = df.groupby(key).apply(lambda d: pool(d, [2008, 2009, 2010]), include_groups=False).add_prefix("b_")
    e = df.groupby(key).apply(lambda d: pool(d, [2017, 2018, 2019]), include_groups=False).add_prefix("e_")
    ch = b.join(e).dropna(); ch = ch[ch.b_n >= minn]
    ch["delta"] = ch.e_rate - ch.b_rate; ch["se"] = np.sqrt(ch.b_se**2 + ch.e_se**2); ch["z"] = ch.delta/ch.se
    w = 1/ch.se**2; mu = np.sum(w*ch.delta)/np.sum(w); Q = np.sum(w*(ch.delta-mu)**2); k = len(ch)
    tau2 = max(0, (Q-(k-1))/(np.sum(w)-np.sum(w**2)/np.sum(w)))
    print(f"{label}: units={k}  IVW mean change={100*mu:.2f} pp  Q={Q:.0f} on {k-1} df  I2={max(0,(Q-(k-1))/Q):.2f}  "
          f"tau={100*np.sqrt(tau2):.2f} pp  median SE={100*ch.se.median():.2f} pp  share z>1.96={np.mean(ch.z>1.96):.2f}  z<-1.96={np.mean(ch.z<-1.96):.2f}")
    print("   change quantiles (pp):", (100*ch.delta.quantile([.1,.25,.5,.75,.9])).round(2).to_dict())
    return ch
m = pd.read_csv(OUT/"acs_met_year_1217.csv")
ch = hetero(m, "market", "MARKETS (>=1500 sampled 12-17 in 2008-10)", 1500); ch.to_csv(OUT/"acs_market_change_0810_to_1719.csv")
s = pd.read_csv(OUT/"acs_state_year_sex_1217.csv")
for sex, lab in [(1,"boys"),(2,"girls")]:
    hetero(s[s.sex==sex], "statefip", f"STATES {lab}", 0)
sc = hetero(pd.read_csv(OUT/"acs_state_year_1217.csv"), "statefip", "STATES all", 0); sc.to_csv(OUT/"acs_state_change_0810_to_1719.csv")
print((100*sc.delta).round(2).sort_values().to_string())
