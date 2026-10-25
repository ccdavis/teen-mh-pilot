"""Pre-specified difference-in-differences for the first statewide school phone mandates in the YRBS state panel.

Treated: states whose mandate (per data/compiled/phone_bans/state_phone_bans.csv) was in force during the 2024-25 school year, i.e.
effective_school_year 2023-24 or 2024-25 (Florida, Indiana, Louisiana, South Carolina, Minnesota); of these only Indiana (instructional-
time ban), Louisiana and South Carolina (bell-to-bell) have 2025 YRBS data (Florida left the YRBS after 2021; Minnesota runs its own
survey). Control: states with 2025 YRBS data and no mandate in force before the 2025-26 school year ('clean' subset: no mandate enacted
before the spring-2025 fieldwork either, i.e. date_enacted after 2025-06-30 or no mandate). Outcomes (percent, weighted state estimates
from 13_yrbs_state.py): sad/hopeless, considered suicide, attempted suicide, by sex and pooled; first stage / mechanism: used social
media several times a day or more (asked 2023 and 2025 only). Model: y_st = a_s + l_t + b Treat_s x Post_t, state-year cells weighted
equally (precision-weighted version reported alongside), SE clustered by state (CRV1) and a randomization-inference p-value from
re-assigning treatment to every possible set of the same number of states (exact enumeration). Placebo: the same model on 2017-2023 with
2023 as the fake post period (no mandate was in force anywhere before 2023-24). Event study: Treat x year relative to 2021.

Reads results/tables/yrbs_state_year_sex.csv, data/compiled/phone_bans/state_phone_bans.csv; the national file
data/external/yrbs/sadc_2025/sadc_2025_national.dat for the national trend. Writes results/tables/yrbs25_ban_states.csv,
yrbs25_ban_means.csv, yrbs25_ban_did.csv, yrbs25_ban_event.csv, yrbs25_national_trend.csv.
Usage: uv run python scripts/analysis/33_yrbs_ban_did.py [--post 2025] (default 2025; --post 2023 reproduces the placebo on its own)."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib, itertools, sys, glob
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; pd.set_option("display.width", 220)
POST = int(sys.argv[sys.argv.index("--post") + 1]) if "--post" in sys.argv else 2025
PC = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"}
B = pd.read_csv(ROOT/"data/compiled/phone_bans/state_phone_bans.csv"); B["st"] = B.state.map(PC)
B["eff_start"] = B.effective_school_year.str.extract(r"^(\d{4})")[0].astype(float)  # fall of the first school year in force
B["enacted"] = pd.to_datetime(B.date_enacted, format="mixed", errors="coerce")
B["group"] = np.where(B.eff_start <= POST - 1, "treated", "control")  # in force during the school year ending in the survey spring
B.loc[(B.group == "control") & B.enacted.notna() & (B.enacted <= pd.Timestamp(f"{POST}-06-30")), "group"] = "control_enacted_pre_fieldwork"
Y = pd.read_csv(T/"yrbs_state_year_sex.csv", dtype={"sitecode": str}); Y["st"] = Y.sitecode.str[:2]; Y = Y[Y.year.between(2013, POST)]
# pooled sexes from the weighted sums; keep per-sex rows
pool = Y.groupby(["st", "year", "item"])[["sw", "sw2", "swy", "n"]].sum().reset_index(); pool["sexlab"] = "all"
Y = pd.concat([Y[["st", "year", "item", "sexlab", "sw", "sw2", "swy", "n"]], pool], ignore_index=True)
Y["p"] = 100 * Y.swy / Y.sw; Y["neff"] = Y.sw**2 / Y.sw2; pc = (Y.p / 100).clip(lower=0.5 / Y.n, upper=1 - 0.5 / Y.n); Y["se"] = 100 * np.sqrt(pc * (1 - pc) / Y.neff)
Y = Y.merge(B[["st", "state", "policy_type", "effective_school_year", "date_enacted", "group"]], on="st", how="left")
has_post = set(Y[Y.year == POST].st)
S = B[B.st.isin(has_post)].copy()
for it in ["sad", "consider", "attempt", "socmed"]: S[f"waves_{it}"] = S.st.map(Y[(Y.item == it) & (Y.year >= 2013)].groupby("st").year.apply(lambda s: " ".join(map(str, sorted(s.unique())))))
S[["st", "state", "policy_type", "date_enacted", "effective_school_year", "group", "waves_sad", "waves_consider", "waves_attempt", "waves_socmed"]].sort_values(["group", "st"]).to_csv(T/"yrbs25_ban_states.csv", index=False)
print(f"states with {POST} data: {len(S)} | treated: {sorted(S[S.group=='treated'].st)} | control: {len(S[S.group=='control'])} | control but enacted before fieldwork: {sorted(S[S.group=='control_enacted_pre_fieldwork'].st)}")
print("treated states missing from the YRBS state files:", sorted(set(B[(B.group == "treated")].st) - has_post))
ITEMS = {"sad": "Sad or hopeless (2+ weeks, past 12 months)", "consider": "Seriously considered suicide", "attempt": "Attempted suicide", "socmed": "Social media several times a day or more"}
def ri_pvalue(d, beta, k):
    """randomization inference: re-assign 'treated' to every k-subset of the states in d and recompute the two-way-FE DiD coefficient
    (FWL: y and the re-assigned Treat x Post are residualised on the state and year dummies with one precomputed annihilator matrix);
    two-sided p = share of |b_perm| >= |beta|. Exact enumeration up to 4000 subsets, otherwise 4000 random subsets."""
    sts = sorted(d.st.unique()); combos = list(itertools.combinations(sts, k))
    if len(combos) > 4000: rng = np.random.default_rng(7); combos = [tuple(rng.choice(sts, k, replace=False)) for _ in range(4000)]
    D = np.column_stack([pd.get_dummies(d.st).values, pd.get_dummies(d.year).values[:, 1:]]).astype(float)
    M = np.eye(len(d)) - D @ np.linalg.pinv(D.T @ D) @ D.T; yr = M @ d.y.values; post = d.post.values; stv = d.st.values
    bs = []
    for c in combos:
        tp = np.isin(stv, c).astype(float) * post; tr = M @ tp; bs.append((tr @ yr) / (tr @ tr))
    bs = np.array(bs); return float((np.abs(bs) >= abs(beta) - 1e-9).mean()), len(combos)
rows, ev_rows, mean_rows = [], [], []
for item, label in ITEMS.items():
    for sex in ["all", "girls", "boys"]:
        for design, years, post_year, groups in [("main", [POST - 4, POST - 2, POST], POST, ["treated", "control", "control_enacted_pre_fieldwork"]),
                                                  ("main_clean_controls", [POST - 4, POST - 2, POST], POST, ["treated", "control"]),
                                                  ("placebo_pre", [POST - 8, POST - 6, POST - 4, POST - 2], POST - 2, ["treated", "control", "control_enacted_pre_fieldwork"])]:
            d = Y[(Y.item == item) & (Y.sexlab == sex) & Y.year.isin(years) & Y.st.isin(has_post) & Y.group.isin(groups)].copy()
            if item == "socmed" and design == "placebo_pre": continue
            d["y"] = d.p; d["post"] = (d.year >= post_year).astype(int); d["treat"] = (d.group == "treated").astype(int); d["tp"] = d.treat * d.post
            ok = d.groupby("st").post.nunique() == 2; d = d[d.st.isin(ok[ok].index)]  # states observed both before and after
            k = d[d.treat == 1].st.nunique()
            if k == 0 or d[d.treat == 0].st.nunique() < 5: continue
            m = pf.feols("y ~ tp | st + year", data=d, vcov={"CRV1": "st"}); mw = pf.feols("y ~ tp | st + year", data=d, weights="neff", vcov={"CRV1": "st"})
            p_ri, n_perm = ri_pvalue(d, m.coef().iloc[0], k)
            g = d.groupby(["treat", "post"]).y.mean()
            rows.append(dict(item=item, outcome=label, sex=sex, design=design, post_year=post_year, years=" ".join(map(str, years)), coef=m.coef().iloc[0], se_cluster=m.se().iloc[0], p_cluster=m.pvalue().iloc[0], p_ri=p_ri, n_perm=n_perm,
                             coef_weighted=mw.coef().iloc[0], se_weighted=mw.se().iloc[0], n_state_years=len(d), treated_states=k, control_states=d[d.treat == 0].st.nunique(),
                             treated_pre=g.get((1, 0)), treated_post=g.get((1, 1)), control_pre=g.get((0, 0)), control_post=g.get((0, 1)), treated_list=" ".join(sorted(d[d.treat == 1].st.unique()))))
            print(f"{item:8s} {sex:5s} {design:20s} b={m.coef().iloc[0]:+.2f} (cl se {m.se().iloc[0]:.2f}, p_cl {m.pvalue().iloc[0]:.2f}, p_RI {p_ri:.2f}) wtd {mw.coef().iloc[0]:+.2f} ({mw.se().iloc[0]:.2f}) | T={k} C={d[d.treat==0].st.nunique()} N={len(d)} | T pre->post {g.get((1,0)):.1f}->{g.get((1,1)):.1f}, C {g.get((0,0)):.1f}->{g.get((0,1)):.1f}")
        # event study 2015-POST relative to 2021 (all controls), treated x year
        d = Y[(Y.item == item) & (Y.sexlab == sex) & Y.year.between(POST - 10, POST) & Y.st.isin(has_post)].copy(); d["treat"] = (d.group == "treated").astype(int); d["y"] = d.p
        if d[d.treat == 1].st.nunique() and d.year.nunique() > 2 and (d.year == POST - 4).any():
            e = pf.feols(f"y ~ i(year, treat, ref={POST - 4}) | st + year", data=d, vcov={"CRV1": "st"}); t = e.tidy().reset_index()
            t["year"] = t.Coefficient.str.extract(r"\[T\.(\d{4})\]")[0].astype(int) if t.Coefficient.str.contains(r"\[T\.").any() else t.Coefficient.str.extract(r"(\d{4})")[0].astype(int)
            for _, r in t.iterrows(): ev_rows.append(dict(item=item, sex=sex, year=int(r.year), coef=r.Estimate, se=r["Std. Error"], treated_states=d[d.treat == 1].st.nunique(), control_states=d[d.treat == 0].st.nunique()))
        # means by wave and group
        for (grp, yr), x in Y[(Y.item == item) & (Y.sexlab == sex) & Y.st.isin(has_post) & Y.year.between(POST - 10, POST)].groupby(["group", "year"]):
            mean_rows.append(dict(item=item, sex=sex, group=grp, year=yr, mean_pct=x.p.mean(), states=x.st.nunique(), state_list=" ".join(sorted(x.st))))
R = pd.DataFrame(rows); R.to_csv(T/"yrbs25_ban_did.csv", index=False)
pd.DataFrame(ev_rows).to_csv(T/"yrbs25_ban_event.csv", index=False); pd.DataFrame(mean_rows).to_csv(T/"yrbs25_ban_means.csv", index=False)
# national trend from the 2025 SADC national file (same columns as the 2025 state files)
cs = [(0,5),(113,121),(124,134),(161,164),(265,266),(266,267),(268,269),(313,314)]; names = ["site","year","weight","sex","q_sad","q_consider","q_attempt","q_socmed"]; nat = []
for ch in pd.read_fwf(ROOT/"data/external/yrbs/sadc_2025/sadc_2025_national.dat", colspecs=cs, names=names, dtype={c: str for c in names if c != "weight"}, chunksize=300000):
    ch = ch[ch.weight.notna() & ch.sex.isin(["1", "2"])]
    ch["sad"] = ch.q_sad.map({"1": 1.0, "2": 0.0}); ch["consider"] = ch.q_consider.map({"1": 1.0, "2": 0.0}); ch["attempt"] = ch.q_attempt.map({"1": 0.0, "2": 1.0, "3": 1.0, "4": 1.0, "5": 1.0}); ch["socmed"] = ch.q_socmed.map({"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0, "6": 1.0, "7": 1.0, "8": 1.0})
    for col in ["sad", "consider", "attempt", "socmed"]:
        c = ch[ch[col].notna()]; sx = c.assign(sw=c.weight, swy=c.weight * c[col], n=1)
        for lab, sub in [("all", sx), ("girls", sx[sx.sex == "1"]), ("boys", sx[sx.sex == "2"])]:
            g = sub.groupby("year")[["sw", "swy", "n"]].sum().reset_index(); g["item"] = col; g["sexlab"] = lab; nat.append(g)
N = pd.concat(nat).groupby(["item", "sexlab", "year"]).sum().reset_index(); N["pct"] = 100 * N.swy / N.sw; N["year"] = N.year.astype(int)
N[["item", "sexlab", "year", "pct", "n"]].to_csv(T/"yrbs25_national_trend.csv", index=False)
print("\nNational YRBS (2025 SADC):"); print(N[N.year >= 2011].pivot_table(index="year", columns=["item", "sexlab"], values="pct").round(1).to_string())
print("\nMeans by group and wave (sad, all):"); print(pd.DataFrame(mean_rows).query("item=='sad' and sex=='all'").pivot_table(index="year", columns="group", values="mean_pct").round(1).to_string())
