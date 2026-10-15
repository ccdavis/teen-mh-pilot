"""Pilot step 7: HBSC published tables. Does schoolwork pressure rise where/when psychosomatic complaints rise? Is the U.S. an outlier?"""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; pd.set_option("display.width", 220)
h = pd.read_csv(ROOT/"data/compiled/hbsc/hbsc_published_trends.csv"); h = h[h.sex.isin(["boy","girl"])&(h.country!="HBSC average")]
wide = h.pivot_table(index=["country","year_end","age","sex"], columns="item", values="value_pct").reset_index()
wide.to_csv(T/"hbsc_wide.csv", index=False)
W = wide.dropna(subset=["schoolwork_pressure","multiple_complaints"]).copy()
print("country-wave-age-sex cells with both items:", len(W), "countries:", W.country.nunique(), "waves:", sorted(W.year_end.unique()))
# HBSC-average trend by wave, age 15
avg = W.groupby(["year_end","age","sex"])[["schoolwork_pressure","multiple_complaints"]].mean().round(1); print(avg.loc[(slice(None),15,slice(None)),:].to_string())
# within-country co-movement: complaints on pressure with country×age×sex and wave×age×sex FE
W["cell"] = W.country+"_"+W.age.astype(str)+"_"+W.sex; W["wave_as"] = W.year_end.astype(str)+"_"+W.age.astype(str)+"_"+W.sex
m = pf.feols("multiple_complaints ~ schoolwork_pressure | cell + wave_as", data=W, vcov={"CRV1":"country"}); print("\nWithin-country: complaints on pressure:", round(m.coef().iloc[0],3), "se", round(m.se().iloc[0],3), "N", m._N)
for sex in ["girl","boy"]:
    d = W[W.sex==sex]; m = pf.feols("multiple_complaints ~ schoolwork_pressure | cell + wave_as", data=d, vcov={"CRV1":"country"}); print(f"  {sex}: {m.coef().iloc[0]:.3f} (se {m.se().iloc[0]:.3f})")
# long changes 2010 -> 2018 and 2010 -> 2022, age 15, by country: did pressure rise where complaints rose?
def chg(y0, y1, age=15):
    a = W[(W.year_end==y0)&(W.age==age)].set_index(["country","sex"]); b = W[(W.year_end==y1)&(W.age==age)].set_index(["country","sex"])
    c = (b[["schoolwork_pressure","multiple_complaints"]] - a[["schoolwork_pressure","multiple_complaints"]]).dropna(); c.columns = ["d_pressure","d_complaints"]; return c.reset_index()
for y0, y1 in [(2010,2018),(2010,2022),(2002,2010),(2014,2022)]:
    c = chg(y0,y1); r = c[["d_pressure","d_complaints"]].corr().iloc[0,1]
    m = pf.feols("d_complaints ~ d_pressure | sex", data=c, vcov="hetero")
    print(f"{y0}->{y1}, age 15: n={len(c)} country-sex; mean Δpressure={c.d_pressure.mean():+.1f} pp, mean Δcomplaints={c.d_complaints.mean():+.1f} pp; corr={r:.2f}; slope={m.coef().iloc[0]:.2f} (se {m.se().iloc[0]:.2f})")
    c.to_csv(T/f"hbsc_change_{y0}_{y1}_age15.csv", index=False)
# U.S. vs others, 2002 -> 2010 (the only U.S. waves), all ages
us = W[W.country=="United States"].groupby(["year_end","sex"])[["schoolwork_pressure","multiple_complaints"]].mean().round(1); print("\nUnited States:"); print(us.to_string())
oth = W[W.country!="United States"].groupby(["year_end","sex"])[["schoolwork_pressure","multiple_complaints"]].mean().round(1); print("Other countries mean:"); print(oth.loc[[2002,2006,2010]].to_string())
# 2018/2022: complaints vs problematic social media, cross-country, with pressure as control
S = wide.dropna(subset=["problematic_social_media","multiple_complaints","schoolwork_pressure"]).copy(); S["cell"]=S.year_end.astype(str)+"_"+S.age.astype(str)+"_"+S.sex
m1 = pf.feols("multiple_complaints ~ problematic_social_media + schoolwork_pressure | cell", data=S, vcov={"CRV1":"country"}); print("\nCross-country 2018/2022: complaints on PSMU and pressure (wave×age×sex FE):", m1.coef().round(3).to_dict(), m1.se().round(3).to_dict(), "N", m1._N)
S["cc"] = S.country+"_"+S.age.astype(str)+"_"+S.sex
m2 = pf.feols("multiple_complaints ~ problematic_social_media + schoolwork_pressure | cc + cell", data=S, vcov={"CRV1":"country"}); print("Within-country 2018->2022 change:", m2.coef().round(3).to_dict(), m2.se().round(3).to_dict(), "N", m2._N)
