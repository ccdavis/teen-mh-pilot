"""DHS-8 mental-health module, pooled across the IPUMS DHS samples that carry it (Nepal 2022, Mozambique 2022-23, Bangladesh 2022; women).

Reads data/extracts/dhs/<sample>_slim.parquet (scripts/extract/dhs_extract.py). Outcomes: PHQ-9 >= 10, GAD-7 >= 10, GAD-7 >= 6 (the cutoff the
DHS reports use for "symptoms of anxiety" in these three surveys), and the continuous scores. Exposures: almost-daily internet use, weekly-or-more
internet use (INTERNETMO; never-users count as non-users), owning a smartphone (CELLPHONESMART == 1; women without a phone count as 0) and
owning any phone. Mozambique's IPUMS file does not yet carry the internet items, so the internet exposures pool Nepal and Bangladesh only.
Specification (as in 21_dhs_nepal.py): survey-by-sampling-cluster fixed effects, wealth quintile, education level and single-year age
controls, survey weights PERWEIGHT/1e6, standard errors clustered by sampling cluster; "none" rows replace the cluster FE with an urban dummy.
Pooled rows normalize each survey's weights to sum to its unweighted n and let the wealth, education and age effects differ by survey
(FE sample^WEALTHQ etc.). Age groups 15-19, 20-24 and 25-49 (the 25-49 group is the falsification contrast); urban/rural subsamples.
A secondary set uses the diagnosis-only items (Kenya 2022 women: smartphone; Madagascar 2021 women: ever used the internet; men: internet frequency).
Outputs (results/tables/): dhs8_estimates.csv, dhs8_means.csv, dhs8_published_vs_microdata.csv, dhs8_diag.csv and copies of the compiled
inventory, published-prevalence and literature tables (dhs8_module_inventory.csv, dhs8_prevalence_published.csv, dhs8_literature.csv).
The script first checks that the Nepal 15-19 cluster-FE estimates reproduce results/tables/dhs_nepal_2022.csv.
"""
import pandas as pd, numpy as np, pyfixest as pf, pathlib, shutil, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; EX = ROOT/"data/extracts/dhs"; CMP = ROOT/"data/compiled/dhs8"; pd.set_option("display.width", 220)
LAB = {"np2022ir": "Nepal 2022", "mz2022ir": "Mozambique 2022-23", "bd2022ir": "Bangladesh 2022", "ke2022ir": "Kenya 2022", "mg2021ir": "Madagascar 2021", "mg2021mr": "Madagascar 2021"}
SID = {"np2022ir": "NP2022DHS", "mz2022ir": "MZ2022DHS", "bd2022ir": "BD2022DHS", "ke2022ir": "KE2022DHS", "mg2021ir": "MD2021DHS", "mg2021mr": "MD2021DHS"}
UNIVERSE = {"np2022ir": "all women 15-49 (module subsample)", "mz2022ir": "all women 15-49", "bd2022ir": "ever-married women 15-49"}

def load(s):
    d = pd.read_parquet(EX/f"{s}_slim.parquet"); d["sample"] = s; d["survey"] = LAB[s]; d["w"] = d.PERWEIGHT/1e6
    d["phq"] = d.DEPRESSIONSCORE.where(d.DEPRESSIONSCORE.le(27)).astype(float); d["gad"] = d.GADSCORE.where(d.GADSCORE.le(21)).astype(float)
    for y, src, c in [("phq10", "phq", 10), ("gad10", "gad", 10), ("gad6", "gad", 6)]: d[y] = (d[src] >= c).astype(float).where(d[src].notna())
    netmo = d.INTERNETMO.where(d.INTERNETMO.le(3)).astype(float)
    netmo = netmo.mask(d.INTERNETMO.eq(9) & d.INTERNETEVYR.isin([0, 12]), 0.0)                  # never used / not in the last 12 months -> not a current user
    d["net_daily"] = (netmo == 3).astype(float).where(netmo.notna()); d["net_weekly"] = (netmo >= 2).astype(float).where(netmo.notna())
    d["smart"] = (d.CELLPHONESMART == 1).astype(float).where(d.CELLPHONESMART.isin([0, 1, 9])); d["ownphone"] = (d.CELLPHONSELF == 1).astype(float).where(d.CELLPHONSELF.isin([0, 1]))
    d["urban"] = (d.URBAN == 1).astype(int); d["cl"] = s + "_" + d.CLUSTERNO.astype(str); d["agegrp"] = pd.cut(d.AGE, [14, 19, 24, 49], labels=["15-19", "20-24", "25-49"]).astype(str)
    d["diag"] = d.DEPRESSIONDIAG.where(d.DEPRESSIONDIAG.isin([0, 1])).astype(float) if "DEPRESSIONDIAG" in d else np.nan
    d["net_ever"] = d.INTERNETEVYR.isin([11, 12]).astype(float).where(d.INTERNETEVYR.isin([0, 11, 12]))
    return d

def wmean(x, w):
    m = x.notna() & w.notna(); return float(np.average(x[m], weights=w[m])) if m.any() else np.nan

def fit(df, y, x, fe, pooled=False):
    f = f"{y} ~ {x}" + (" | cl + sample^WEALTHQ + sample^EDUCLVL + sample^AGE" if pooled else (" + C(WEALTHQ) + C(EDUCLVL) + C(AGE) | cl" if fe == "cluster FE" else " + C(WEALTHQ) + C(EDUCLVL) + C(AGE) + urban"))
    d = df.dropna(subset=[y, x])
    if d[x].nunique() < 2 or len(d) < 60: return None
    m = pf.feols(f, data=d, weights="wn" if pooled else "w", vcov={"CRV1": "cl"}); k = 100 if y in ("phq10", "gad10", "gad6") else 1
    return dict(coef=m.coef()[x]*k, se=m.se()[x]*k, n=int(m._N), clusters=int(d.cl.nunique()), surveys=int(d["sample"].nunique()), mean_y=wmean(d[y], d.w)*k, share_x=100*wmean(d[x], d.w))

MH = ["np2022ir", "mz2022ir", "bd2022ir"]; D = {s: load(s) for s in MH + ["ke2022ir", "mg2021ir", "mg2021mr"]}
P = pd.concat([D[s][D[s].phq.notna() & D[s].gad.notna()] for s in MH], ignore_index=True)
P["wn"] = P.w / P.groupby("sample").w.transform("mean")                                           # weights sum to n within each survey
print("module respondents with PHQ-9 and GAD-7:", P.groupby("survey").size().to_dict())

# ---- replication of the Phase 1 Nepal rows (cluster FE, 15-19, daily internet) ----
ref = pd.read_csv(T/"dhs_nepal_2022.csv"); ok = True
for y in ["phq10", "gad10", "phq", "gad"]:
    r = fit(P[(P["sample"] == "np2022ir") & (P.agegrp == "15-19")], y, "net_daily", "cluster FE"); o = ref[(ref.ages == "15-19") & (ref.exposure == "net_daily") & (ref.outcome == y) & (ref.fe == "cluster FE")].iloc[0]
    same = abs(r["coef"] - o.coef) < 1e-6 and abs(r["se"] - o.se) < 1e-6 and r["n"] == o.n; ok &= same
    print(f"  Nepal 15-19 daily internet -> {y}: {r['coef']:+.3f} ({r['se']:.3f}) n={r['n']} | Phase 1: {o.coef:+.3f} ({o.se:.3f}) n={int(o.n)} {'OK' if same else 'MISMATCH'}")
assert ok, "Nepal replication failed"

# ---- means by survey x age group ----
rows = []
for s in MH:
    for ag, g in P[P["sample"] == s].groupby("agegrp"):
        rows.append(dict(sample=s, survey=LAB[s], universe=UNIVERSE[s], ages=ag, n=len(g), n_weighted=g.w.sum(), **{k: (100*wmean(g[k], g.w) if k not in ("phq", "gad") else wmean(g[k], g.w)) for k in ["phq10", "gad10", "gad6", "phq", "gad", "net_daily", "net_weekly", "smart", "ownphone", "urban"]}))
M = pd.DataFrame(rows); M.to_csv(T/"dhs8_means.csv", index=False); print(M.round(1).to_string(index=False))

# ---- estimates: per survey and pooled; all / urban / rural ----
EXPOS = ["net_daily", "net_weekly", "smart", "ownphone"]; OUTS = ["phq10", "gad10", "gad6", "phq", "gad"]; est = []
for ag in ["15-19", "20-24", "25-49"]:
    for x in EXPOS:
        for y in OUTS:
            for sub, mask in [("all", P.urban.isin([0, 1])), ("urban", P.urban == 1), ("rural", P.urban == 0)]:
                base = P[(P.agegrp == ag) & mask]
                for s in MH:
                    for fe in (["cluster FE", "none"] if sub == "all" else ["cluster FE"]):
                        r = fit(base[base["sample"] == s], y, x, fe)
                        if r: est.append(dict(sample=s, survey=LAB[s], ages=ag, exposure=x, outcome=y, fe=fe, subset=sub, **r))
                r = fit(base, y, x, "cluster FE", pooled=True)
                if r and r["surveys"] > 1: est.append(dict(sample="pooled", survey="Pooled (" + ", ".join(LAB[s] for s in MH if base.dropna(subset=[y, x])["sample"].eq(s).any()) + ")", ages=ag, exposure=x, outcome=y, fe="survey x cluster FE", subset=sub, **r))
E = pd.DataFrame(est)
# precision-weighted average of the per-survey cluster-FE estimates (meta-analytic fixed effect), as a check on the pooled regression
for (ag, x, y, sub), g in E[(E.fe == "cluster FE") & (E["sample"] != "pooled")].groupby(["ages", "exposure", "outcome", "subset"]):
    if len(g) > 1:
        wts = 1/g.se**2; E = pd.concat([E, pd.DataFrame([dict(sample="meta", survey="Precision-weighted average", ages=ag, exposure=x, outcome=y, fe="cluster FE", subset=sub, coef=(g.coef*wts).sum()/wts.sum(), se=np.sqrt(1/wts.sum()), n=int(g.n.sum()), clusters=int(g.clusters.sum()), surveys=len(g), mean_y=np.nan, share_x=np.nan)])], ignore_index=True)
E.to_csv(T/"dhs8_estimates.csv", index=False)
v = E[(E.subset == "all") & (E.fe != "none") & (E.outcome.isin(["phq10", "gad10"]))].pivot_table(index=["ages", "exposure", "survey"], columns="outcome", values=["coef", "se", "n"]).round(2)
print(v.to_string())

# ---- published prevalence (final-report tables) vs microdata means, women 15-19 / 20-24 ----
pub = pd.read_csv(CMP/"dhs8_mental_health_prevalence.csv"); cmp_rows = []
for s in MH:
    for ag in ["15-19", "20-24"]:
        p = pub[(pub.survey == SID[s]) & (pub.sex == "women") & (pub.group == ag)]; m = M[(M["sample"] == s) & (M.ages == ag)]
        if len(p) and len(m):
            p, m = p.iloc[0], m.iloc[0]; cmp_rows.append(dict(sample=s, survey=LAB[s], ages=ag, n_unweighted=m.n, report_n_weighted=p.n_weighted, phq10_report=p.phq9_ge10, phq10_microdata=round(m.phq10, 1), anxiety_def=p.anxiety_report_def, anxiety_report=p.anxiety_report_pct, gad6_microdata=round(m.gad6, 1), gad10_microdata=round(m.gad10, 1)))
C = pd.DataFrame(cmp_rows); C.to_csv(T/"dhs8_published_vs_microdata.csv", index=False); print(C.to_string(index=False))

# ---- diagnosis-only surveys ----
dg = []
for s, x in [("ke2022ir", "smart"), ("ke2022ir", "ownphone"), ("mg2021ir", "net_ever"), ("mg2021mr", "net_daily"), ("mg2021mr", "net_weekly")]:
    d = D[s][D[s].diag.notna()]
    for ag in ["15-19", "20-24", "25-49"]:
        g = d[d.agegrp == ag].dropna(subset=[x]);
        if len(g) < 100 or g[x].nunique() < 2: continue
        m = pf.feols(f"diag ~ {x} + C(WEALTHQ) + C(EDUCLVL) + C(AGE) | cl", data=g, weights="w", vcov={"CRV1": "cl"})
        dg.append(dict(sample=s, survey=LAB[s], sex=g.SEX.iloc[0], ages=ag, exposure=x, outcome="ever diagnosed with depression", coef=100*m.coef()[x], se=100*m.se()[x], n=int(m._N), mean_y=100*wmean(g.diag, g.w), share_x=100*wmean(g[x], g.w)))
G = pd.DataFrame(dg); G.to_csv(T/"dhs8_diag.csv", index=False); print(G.round(2).to_string(index=False))

for f in ["dhs8_module_inventory.csv", "dhs8_literature.csv"]: shutil.copy(CMP/f, T/f)
pub.to_csv(T/"dhs8_prevalence_published.csv", index=False)
