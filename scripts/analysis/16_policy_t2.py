"""Pilot step 6: T2 school-pressure policies. State x year panels of ACS 12-17 (by sex), YRBS state sad/hopeless, NSDUH youth MDE on policy indicators
with state + year FE; and the T1 x T2 interaction at market level (LTE in force x state pressure index) with state x year FE."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; pd.set_option("display.width", 220)
P = pd.read_csv(ROOT/"data/compiled/school_policy/state_year_policy.csv")
fips = {"AL":1,"AK":2,"AZ":4,"AR":5,"CA":6,"CO":8,"CT":9,"DE":10,"DC":11,"FL":12,"GA":13,"HI":15,"ID":16,"IL":17,"IN":18,"IA":19,"KS":20,"KY":21,"LA":22,"ME":23,"MD":24,"MA":25,"MI":26,"MN":27,"MS":28,"MO":29,"MT":30,"NE":31,"NV":32,"NH":33,"NJ":34,"NM":35,"NY":36,"NC":37,"ND":38,"OH":39,"OK":40,"OR":41,"PA":42,"RI":44,"SC":45,"SD":46,"TN":47,"TX":48,"UT":49,"VT":50,"VA":51,"WA":53,"WV":54,"WI":55,"WY":56}
scol = [c for c in P.columns if c.lower() in ("state","st","state_abbr","postal")][0]; P["statefip"] = P[scol].astype(str).map(fips).astype(int)
pol = ["rttt_winner","waiver_in_force","cc_aligned_test_in_force","teacher_eval_test_based_in_force","exit_exam_in_force","pressure_index"]
P = P[["statefip","year"]+pol]; P.to_csv(T/"state_year_policy_fips.csv", index=False)
print(P.groupby("year")[pol].mean().round(2).to_string())
out = []
def run(df, y, wcol, label, extra_fe=""):
    d = df.merge(P, on=["statefip","year"]); d = d[d.year.between(2008,2019)]
    for v in pol:
        m = pf.feols(f"{y} ~ {v} | statefip + year{extra_fe}", data=d, weights=wcol, vcov={"CRV1":"statefip"})
        out.append(dict(outcome=label, policy=v, coef=m.coef().iloc[0], se=m.se().iloc[0], n=m._N))
    m = pf.feols(f"{y} ~ " + " + ".join(pol[:-1]) + f" | statefip + year{extra_fe}", data=d, weights=wcol, vcov={"CRV1":"statefip"})
    for v in pol[:-1]: out.append(dict(outcome=label, policy="joint:"+v, coef=m.coef()[v], se=m.se()[v], n=m._N))
a = pd.read_csv(T/"acs_state_year_sex_1217.csv"); a["y"] = 100*a.rate; a["wt"] = 1/(100*a.se)**2
run(a[a.sex==2], "y", "wt", "ACS 12-17 girls"); run(a[a.sex==1], "y", "wt", "ACS 12-17 boys")
yr = pd.read_csv(T/"yrbs_state_year_sex.csv"); yr = yr[yr.item=="sad"]; yr["statefip"] = yr.sitecode.astype(str).str[:2].map(fips); yr = yr[yr.statefip.notna()]; yr["statefip"] = yr.statefip.astype(int); yr["y"] = 100*yr.p; yr["wt"] = 1/(100*yr.se)**2
run(yr[yr.sexlab=="girls"], "y", "wt", "YRBS sad/hopeless girls"); run(yr[yr.sexlab=="boys"], "y", "wt", "YRBS sad/hopeless boys")
ns = pd.read_csv(T/"validation_state_nsduh_vs_acs.csv"); ns["year"] = (ns.year+0.5).astype(int); ns["wt"] = 1/ns.nsduh_se**2  # period label = second year
run(ns, "nsduh", "wt", "NSDUH youth MDE (2-yr, labelled by end year)")
O = pd.DataFrame(out); O.to_csv(T/"policy_t2_results.csv", index=False)
print(O[~O.policy.str.startswith("joint")].pivot(index="policy", columns="outcome", values="coef").round(3).to_string())
print(O[~O.policy.str.startswith("joint")].pivot(index="policy", columns="outcome", values="se").round(3).to_string())
# T1 x T2 interaction at market level
cells = pd.concat([pd.read_parquet(f) for f in sorted((ROOT/"data/extracts/acs").glob("cells_us20*.parquet"))]); cells = cells[cells.year.between(2008,2019)&cells.agegrp.isin(["12-14","15-17"])]
cells["market"] = np.where(cells.met2013>0, cells.met2013, cells.statefip*100000)
g = cells.groupby(["market","statefip","year","sex"]).agg(n=("n_unwt","sum"), pop=("n_w","sum"), rem=("rem_w","sum")).reset_index(); g["y"] = 100*g.rem/g["pop"]
on = pd.read_csv(T/"lte_onset_first_launch_date.csv"); od = pd.to_datetime(on.onset_date, format="mixed"); on["onset_year"] = od.dt.year + (od.dt.month>6).astype(int)
g = g.merge(on[["market","onset_year"]], on="market"); g["treated"] = (g.year >= g.onset_year).astype(int); g = g.merge(P, on=["statefip","year"]); g = g[g.n>=100]
g["sy"] = g.statefip.astype(str)+"_"+g.year.astype(str)
print("\nT1 x T2 interaction (market panel, dated metros, state x year FE absorbs T2):")
for sx, lab in [(2,"girls"),(1,"boys")]:
    d = g[g.sex==sx]
    for v in ["pressure_index","cc_aligned_test_in_force","waiver_in_force","rttt_winner"]:
        d["inter"] = d.treated*d[v]; m = pf.feols("y ~ treated + inter | market + sy", data=d, weights="pop", vcov={"CRV1":"market"})
        print(f"  {lab:5s} {v:32s} treated={m.coef()['treated']:+.3f} ({m.se()['treated']:.3f})  treated x {v}={m.coef()['inter']:+.3f} ({m.se()['inter']:.3f})  N={m._N}")
        out.append(dict(outcome=f"ACS market {lab}", policy="LTE x "+v, coef=m.coef()["inter"], se=m.se()["inter"], n=m._N))
pd.DataFrame(out).to_csv(T/"policy_t2_results.csv", index=False)
