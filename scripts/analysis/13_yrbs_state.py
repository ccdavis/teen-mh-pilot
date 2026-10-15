"""YRBS state files: sad/hopeless and considered suicide by state x year x sex (weighted), and state-level check vs ACS 12-17."""
import pandas as pd, numpy as np, pathlib, glob, pyfixest as pf
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; EXT = ROOT/"data/external/yrbs/sadc_2023"
cs = [(0,5),(113,121),(124,134),(158,161),(161,164),(280,281),(281,282),(282,283)]; names = ["sitecode","year","weight","age","sex","q26","q27","q28"]
out = []
for f in sorted(glob.glob(str(EXT/"sadc_2023_state_*.dat"))):
    for chunk in pd.read_fwf(f, colspecs=cs, names=names, dtype={"sitecode":str,"age":str,"sex":str,"q26":str,"q27":str,"q28":str}, chunksize=300000):
        chunk["sad"] = chunk.q26.map({"1":1.0,"2":0.0}); chunk["consider"] = chunk.q27.map({"1":1.0,"2":0.0})
        chunk = chunk[chunk.weight.notna() & chunk.sex.isin(["1","2"])]
        for col in ["sad","consider"]:
            c = chunk[chunk[col].notna()].assign(sw=lambda d: d.weight, sw2=lambda d: d.weight**2, swy=lambda d: d.weight*d[col], n=1)
            g = c.groupby(["sitecode","year","sex"])[["sw","sw2","swy","n"]].sum().reset_index(); g["item"] = col; out.append(g)
d = pd.concat(out).groupby(["sitecode","year","sex","item"]).sum().reset_index()
d["p"] = d.swy/d.sw; d["neff"] = d.sw**2/d.sw2
pc = d.p.clip(lower=0.5/d.n, upper=1-0.5/d.n); d["se"] = np.sqrt(pc*(1-pc)/d.neff)  # floor keeps SE > 0 when every respondent answered the same way
d["sexlab"] = d.sex.map({"1":"girls","2":"boys"}); d.to_csv(T/"yrbs_state_year_sex.csv", index=False)
print(d.groupby(["item","year"]).sitecode.nunique().unstack(0).to_string())
# state FIPS from postal code
fips = {"AL":1,"AK":2,"AZ":4,"AR":5,"CA":6,"CO":8,"CT":9,"DE":10,"DC":11,"FL":12,"GA":13,"HI":15,"ID":16,"IL":17,"IN":18,"IA":19,"KS":20,"KY":21,"LA":22,"ME":23,"MD":24,"MA":25,"MI":26,"MN":27,"MS":28,"MO":29,"MT":30,"NE":31,"NV":32,"NH":33,"NJ":34,"NM":35,"NY":36,"NC":37,"ND":38,"OH":39,"OK":40,"OR":41,"PA":42,"RI":44,"SC":45,"SD":46,"TN":47,"TX":48,"UT":49,"VT":50,"VA":51,"WA":53,"WV":54,"WI":55,"WY":56}
d["statefip"] = d.sitecode.str[:2].map(fips)
a = pd.read_csv(T/"acs_state_year_sex_1217.csv"); a["sexlab"] = a.sex.map({1:"boys",2:"girls"}); a["acs"] = 100*a.rate; a["acs_se"] = 100*a.se
for item in ["sad","consider"]:
    x = d[(d.item==item)&(d.year>=2008)].merge(a[["statefip","year","sexlab","acs","acs_se"]], on=["statefip","year","sexlab"]); x["y"] = 100*x.p; x["wt"] = 1/(100*x.se)**2
    print(f"\n{item}: state x year x sex panel n={len(x)}, states={x.statefip.nunique()}")
    for fe, lab in [("statefip + year", "state+year FE"), ("statefip^sexlab + year^sexlab", "state×sex + year×sex FE")]:
        m = pf.feols(f"y ~ acs | {fe}", data=x, weights="wt", vcov={"CRV1":"statefip"}); print(f"  {lab}: slope={m.coef().iloc[0]:.3f} se={m.se().iloc[0]:.3f}")
    x.to_csv(T/f"validation_state_yrbs_{item}_vs_acs.csv", index=False)
