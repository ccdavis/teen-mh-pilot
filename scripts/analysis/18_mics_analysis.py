"""MICS6/7 Child Functioning Module (anxiety, depression, ages 5-17) vs mobile/internet exposure.
A. Country-round prevalence by age group and sex.  B. Cluster-level dose-response (young-adult daily internet use, mobile ownership, household internet)
with sample x region FE.  C. Own-use for 15-17 linked to the women's/men's file, within-cluster.  D. Placebos: 5-9-year-olds; functioning items."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
pd.set_option("display.width", 230); T = ROOT/"results/tables"; E = ROOT/"data/extracts/mics"
fs = pd.read_parquet(E/"mics_fs.parquet"); wm = pd.read_parquet(E/"mics_wm.parquet"); mn = pd.read_parquet(E/"mics_mn.parquet"); hh = pd.read_parquet(E/"mics_hh.parquet")
fs = fs[(fs.RESULTFS==1)&fs.AGEFS.between(5,17)&fs.SEXFS.isin([1,2])&fs.ANXIFREQ.between(1,5)&fs.DEPRESSFREQ.between(1,5)&(fs.WEIGHTFS>0)].copy()
fs["anx_dw"] = fs.ANXIFREQ.le(2).astype(float); fs["dep_dw"] = fs.DEPRESSFREQ.le(2).astype(float); fs["anx_daily"] = fs.ANXIFREQ.eq(1).astype(float); fs["dep_daily"] = fs.DEPRESSFREQ.eq(1).astype(float)
fs["learn_alot"] = fs.DIFFLEARN.isin([3,4]).astype(float).where(fs.DIFFLEARN.between(1,4)); fs["remem_alot"] = fs.DIFFREMEM.isin([3,4]).astype(float).where(fs.DIFFREMEM.between(1,4)); fs["friend_alot"] = fs.DIFFFRIEND.isin([3,4]).astype(float).where(fs.DIFFFRIEND.between(1,4))
fs["agegrp"] = pd.cut(fs.AGEFS, [4,9,14,17], labels=["5-9","10-14","15-17"]); fs["girl"] = (fs.SEXFS==2).astype(int); fs["urban"] = (fs.URBAN==1).astype(float).where(fs.URBAN.isin([1,2])); fs["wealth"] = fs.WINDEX5.where(fs.WINDEX5.between(1,5))
fs["year"] = fs.YEAR; fs["iso3"] = fs.COUNTRY_ISO3; fs["region"] = fs["sample"]+"_"+fs.REGIONW.astype(str); fs["cl"] = fs["sample"]+"_"+fs.CLUSTER.astype(str); fs["hhid"] = fs["cl"]+"_"+fs.HHNO.astype(str)
print("children:", len(fs), "samples:", fs["sample"].nunique())
# ---- A. prevalence
def wm_(g, col): 
    g = g[g[col].notna()]; return 100*np.average(g[col], weights=g.WEIGHTFS) if len(g) else np.nan
A = fs.groupby(["sample","iso3","year","agegrp","girl"], observed=True).apply(lambda g: pd.Series({"n": len(g), "anx_dw": wm_(g,"anx_dw"), "dep_dw": wm_(g,"dep_dw"), "anx_daily": wm_(g,"anx_daily"), "dep_daily": wm_(g,"dep_daily")}), include_groups=False).reset_index()
A.to_csv(T/"mics_prevalence_sample_age_sex.csv", index=False)
piv = A[A.agegrp!="5-9"].pivot_table(index="sample", columns=["agegrp","girl"], values="anx_dw"); print("anx daily/weekly %, 10-14 & 15-17 by sex (girl=1):"); print(piv.round(1).describe().round(1).to_string())
# ---- dose from wm/mn/hh
for d, agecol, mob in [(wm,"AGEWM","MOBILEWM"),(mn,"AGEMN","MOBILEMN")]:
    d["age"] = d[agecol]; d["net_daily"] = d.INTFREQ3MO.eq(1).astype(float).where(d.INTFREQ3MO.isin([1,2,3,4]) | (d.INTFREQ3MO.eq(9) & d.INTEVER.eq(0)))  # 9 = not applicable: 0 for never-users, missing otherwise
    d["net_weekly"] = d.INTFREQ3MO.isin([1,2]).astype(float).where(d.net_daily.notna()); d["mobile"] = d[mob].where(d[mob].isin([0,1])); d["phone_daily"] = d.PHONEFREQ3MO.eq(1).astype(float).where(d.PHONEFREQ3MO.isin([1,2,3,4]))
    d["cl"] = d["sample"]+"_"+d.CLUSTER.astype(str)
ind = pd.concat([wm[["sample","cl","HHNO","age","net_daily","net_weekly","mobile","phone_daily"]].assign(female=1, LINE=wm.LINEWM), mn[["sample","cl","HHNO","age","net_daily","net_weekly","mobile","phone_daily"]].assign(female=0, LINE=mn.LINEMN)])
young = ind[ind.age.between(15,24)].groupby("cl").agg(y_net_daily=("net_daily","mean"), y_net_weekly=("net_weekly","mean"), y_mobile=("mobile","mean"), y_phone_daily=("phone_daily","mean"), y_n=("age","size"))
adult = ind[ind.age.between(25,49)].groupby("cl").agg(a_net_daily=("net_daily","mean"), a_mobile=("mobile","mean"), a_n=("age","size"))
hh["cl"] = hh["sample"]+"_"+hh.CLUSTER.astype(str); hh["hh_net"] = hh.INTERNET.where(hh.INTERNET.isin([0,1])); hh["hh_mob"] = hh.MOBILE.where(hh.MOBILE.isin([0,1]))
hhc = hh.groupby("cl").agg(hh_net=("hh_net","mean"), hh_mob=("hh_mob","mean"), hh_n=("hh_net","count"))
fs = fs.join(young, on="cl").join(adult, on="cl").join(hhc, on="cl")
cl_dose = fs.groupby(["sample","cl"])[["y_net_daily","y_mobile","hh_net","a_net_daily"]].first().reset_index(); print("\ncluster dose summary:"); print(cl_dose[["y_net_daily","y_mobile","hh_net","a_net_daily"]].describe().round(2).to_string())
# ---- B. cluster dose-response
fs["wt"] = fs.WEIGHTFS; res = []
for dose in ["y_net_daily","y_mobile","hh_net","a_net_daily"]:
    for ag in ["10-17","5-9"]:
        for sx in [1,0]:
            d = fs[(fs.girl==sx)&(fs.agegrp.isin(["10-14","15-17"]) if ag=="10-17" else fs.agegrp.eq("5-9"))&fs[dose].notna()&fs.wealth.notna()&fs.urban.notna()].copy()
            for y in ["anx_dw","dep_dw","learn_alot","friend_alot"]:
                dy = d[d[y].notna()]
                m = pf.feols(f"{y} ~ {dose} + urban + C(wealth) + C(AGEFS) | region", data=dy, weights="wt", vcov={"CRV1":"cl"})
                res.append(dict(dose=dose, ages=ag, sex="girls" if sx else "boys", outcome=y, coef_per_100pct=100*m.coef()[dose], se=100*m.se()[dose], n=m._N, mean=100*np.average(dy[y], weights=dy.wt)))
R = pd.DataFrame(res); R.to_csv(T/"mics_cluster_dose.csv", index=False)
print("\nB. cluster dose-response (pp change in outcome for 0->100% cluster dose; region FE, urban, wealth, age):")
print(R[R.outcome.isin(["anx_dw","dep_dw"])].pivot_table(index=["dose","ages","sex"], columns="outcome", values=["coef_per_100pct","se"]).round(2).to_string())
print(R[R.outcome.isin(["learn_alot","friend_alot"])].pivot_table(index=["dose","ages","sex"], columns="outcome", values=["coef_per_100pct","se"]).round(2).to_string())
# ---- C. own use for 15-17 (link fs LINECH to wm LINEWM / mn LINEMN within household)
own = ind.rename(columns={"LINE":"LINECH"})[["sample","cl","HHNO","LINECH","female","net_daily","net_weekly","mobile","phone_daily"]]
t = fs[fs.agegrp=="15-17"].merge(own, on=["sample","cl","HHNO","LINECH"], how="left")
t = t[(t.female.isna()) | (t.female==t.girl)]
print("\nC. own-use link 15-17: matched", t.net_daily.notna().mean().round(3), "of", len(t), "(girls", t[t.girl==1].net_daily.notna().mean().round(3), "boys", t[t.girl==0].net_daily.notna().mean().round(3), ")")
res2 = []
for sx in [1,0]:
    d0 = t[(t.girl==sx)&t.net_daily.notna()&t.wealth.notna()&t.urban.notna()]; d = d0[d0.EDCURR_FS.isin([0,1])].copy()
    print(f"  {'girls' if sx else 'boys'}: {len(d0)-len(d)} of {len(d0)} linked 15-17-year-olds dropped for unknown school attendance (EDCURR_FS not 0/1)")
    for x in ["net_daily","net_weekly","mobile","phone_daily"]:
        for y in ["anx_dw","dep_dw","anx_daily","dep_daily","learn_alot","friend_alot"]:
            dy = d[d[y].notna()&d[x].notna()]
            for fe, lab in [("region","region FE"),("cl","cluster FE")]:
                m = pf.feols(f"{y} ~ {x} + urban + C(wealth) + C(AGEFS) + EDCURR_FS | {fe}", data=dy, weights="wt", vcov={"CRV1":"cl"})
                res2.append(dict(sex="girls" if sx else "boys", exposure=x, outcome=y, fe=lab, coef_pp=100*m.coef()[x], se=100*m.se()[x], n=m._N, mean=100*np.average(dy[y], weights=dy.wt)))
R2 = pd.DataFrame(res2); R2.to_csv(T/"mics_own_use_1517.csv", index=False)
print(R2[R2.outcome.isin(["anx_dw","dep_dw"])].pivot_table(index=["sex","exposure","fe"], columns="outcome", values=["coef_pp","se"]).round(2).to_string())
print(R2[R2.outcome.isin(["learn_alot","friend_alot"])&(R2.fe=="cluster FE")].pivot_table(index=["sex","exposure"], columns="outcome", values=["coef_pp","se"]).round(2).to_string())
# ---- D. two-round countries
pairs = A[A.agegrp!="5-9"].groupby(["iso3","agegrp","girl"]).filter(lambda g: g.year.nunique()>=2)
if len(pairs):
    p = pairs.sort_values("year").groupby(["iso3","agegrp","girl"]).agg(y0=("year","first"), y1=("year","last"), anx0=("anx_dw","first"), anx1=("anx_dw","last"), dep0=("dep_dw","first"), dep1=("dep_dw","last")).reset_index()
    print("\nD. two-round countries (anx/dep daily-weekly %, 10-17):"); print(p.round(1).to_string()); p.to_csv(T/"mics_two_round.csv", index=False)
# ---- E. survey-level summary for the report (ages 10-17): anxiety by sex, cluster-mean young-adult daily internet use, household internet
sm = fs[fs.AGEFS.between(10,17)].groupby(["sample","iso3","year"]).apply(lambda g: pd.Series({"anx_g": 100*np.average(g[g.girl==1].anx_dw, weights=g[g.girl==1].wt), "anx_b": 100*np.average(g[g.girl==0].anx_dw, weights=g[g.girl==0].wt), "dose": 100*np.nanmean(g.y_net_daily), "hh_net": 100*np.nanmean(g.hh_net), "n": len(g)}), include_groups=False).reset_index()
sm.to_csv(T/"mics_survey_summary.csv", index=False)
fs[["sample","iso3","year","cl","hhid","AGEFS","girl","urban","wealth","anx_dw","dep_dw","anx_daily","dep_daily","learn_alot","friend_alot","y_net_daily","y_mobile","hh_net","a_net_daily","wt"]].to_parquet(E/"mics_child_analysis.parquet")
