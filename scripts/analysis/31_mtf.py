"""Monitoring the Future (MTF), U.S. 8th/10th/12th graders. Two parts.

(A) Published 12th-grade item trends, 1996-2012, from the MTF data volumes ("Questionnaire Responses from the Nation's High School
    Seniors"; parsed by scripts/download/mtf/parse_datavolumes.py into data/compiled/mtf/mtf_published_trends.csv). Items on several
    questionnaire forms are pooled weighting by the weighted N answering. Derived indicators by sex (all / boys / girls):
    homework hours (category midpoints), evenings out per week, daily informal time with friends, dating weekly, weekday TV hours,
    hours of paid work, 7+ hours of sleep most days, loneliness ("A lot of times I feel lonely", % agree), self-derogation (mean % agree
    over four items), depressive affect (mean % endorsing the depressive pole of four items), happiness, life satisfaction. SEs are
    sqrt(p(1-p)/n) x sqrt(DEFF) with DEFF = 2 (the volumes' Appendix B guideline range for single-form 12th-grade percentages is roughly
    1.5-3). Changes 1996->2010, 2010->2012 and 1996->2012, and year-level co-movement (levels and first differences, 17 years).
    The data-volume series ends with the 2012 survey (the last volume published); 2013-2024 require the microdata in (B).
    Also copied to results: the literature table (data/compiled/mtf/mtf_literature.csv) and Johnson et al. 2017's 8th/10th-grade
    year effects 1991-2014 (data/compiled/mtf/mtf_johnson2017_year_effects.csv).

(B) Student-level H3 test on ICPSR/NAHDAP public-use microdata (series 35), when files are present in
    data/external/mtf/icpsr/<ICPSR study number>/ (Stata .dta, SPSS .sav, SAS .sas7bdat or .tsv as delivered by ICPSR):
    depressive affect / loneliness / happiness ~ homework hours x social-media hours + race/ethnicity + parent education + region
    | year FE, by sex and grade, design weights (V5), heteroskedasticity-robust SEs (the public files carry no school or PSU
    identifier), plus a year-FE decomposition (how much of the change in depressive affect since 2012 the time-use variables account
    for). Variables are located codebook-style: the ICPSR variable labels are the MTF OSIRIS abbreviations printed in the data
    volumes' cross-time index (e.g. "-MUCH TO B PROUD", "VRY HPY THS DAYS"), so LABEL_PATTERNS matches them from the file metadata
    (pyreadstat), with the 8th/10th-grade V-codes used by Orben & Przybylski (2019; github.com/OrbenAmy/NHB_2019, 2008-2016 files) as
    confirmed overrides. The script prints the match table for inspection and writes results/tables/mtf_microdata_status.csv.
    As of 2026-10-24 no file is present: icpsr.umich.edu answers HTTP 403 (Cloudflare bot challenge) to curl, headless Chromium and
    remote fetchers from this host, and downloads need an ICPSR login with terms acceptance. Studies to download (12th grade / 8th+10th):
    1991 -/02521, 1992 -/02522, 1993 -/02523, 1994 -/02475, 1995 06716/02390, 1996 02268/02350, 1997 02477/02476, 1998 02751/02752,
    1999 02939/02940, 2000 03184/03183, 2001 03425/03426, 2002 03753/03752, 2003 04019/04018, 2004 04264/04263, 2005 04536/04537,
    2006 20022/20180, 2007 22480/22500, 2008 25382/25422, 2009 28401/28402, 2010 30985/30984, 2011 34409/33902, 2012 34861/34574,
    2013 35218/35166, 2014 36263/36149, 2015 36408/36407, 2016 36798/36799, 2017 37182/37183, 2018 37416/37415, 2019 37841/37842,
    2020 38156/38189, 2021 38503/38502, 2022 38882/38883, 2023 39172/39171, 2024 39444/39445 (12th-grade 1976-1994 studies also exist).

Outputs (results/tables/): mtf_published_series.csv, mtf_published_changes.csv, mtf_published_comovement.csv, mtf_published_coverage.csv,
mtf_literature.csv, mtf_johnson2017_year_effects.csv, mtf_microdata_status.csv and, with microdata, mtf_micro_models.csv,
mtf_micro_decomposition.csv, mtf_micro_varmap.csv.
"""
import re, glob, pathlib, shutil, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; C = ROOT/"data/compiled/mtf"; MICRO = ROOT/"data/external/mtf/icpsr"
pd.set_option("display.width", 220); T.mkdir(parents=True, exist_ok=True); DEFF = 2.0

# ----------------------------------------------------------------------------------------------------------------------------- (A)
# indicator definitions: series name in mtf_published_trends.csv -> (label, kind, spec). kind "share": percent in the listed response
# codes; kind "mean": sum of code midpoints x share; "neg" marks indicators where higher = worse (for the co-movement table).
IND = {
    "lonely_agree":        ("Lonely: 'A lot of times I feel lonely' (% mostly agree + agree)", "share", ("lonely", [4, 5]), 1),
    "left_out_agree":      ("'I often feel left out of things' (% agree)", "share", ("left_out", [4, 5]), 1),
    "not_much_proud":      ("'I feel I do not have much to be proud of' (% agree)", "share", ("not_much_proud", [4, 5]), 1),
    "no_good_at_all":      ("'Sometimes I think that I am no good at all' (% agree)", "share", ("no_good_at_all", [4, 5]), 1),
    "cant_do_right":       ("'I feel that I can't do anything right' (% agree)", "share", ("cant_do_anything_right", [4, 5]), 1),
    "life_not_useful":     ("'I feel that my life is not very useful' (% agree)", "share", ("life_not_useful", [4, 5]), 1),
    "life_meaningless":    ("'Life often seems meaningless' (% agree)", "share", ("life_meaningless", [4, 5]), 1),
    "future_hopeless":     ("'The future often seems hopeless' (% agree)", "share", ("future_hopeless", [4, 5]), 1),
    "not_enjoy_life":      ("'I enjoy life as much as anyone' (% disagree)", "share", ("enjoy_life", [1, 2]), 1),
    "not_good_alive":      ("'It feels good to be alive' (% disagree)", "share", ("good_to_be_alive", [1, 2]), 1),
    "very_happy":          ("Very happy these days (%)", "share", ("happiness", [3]), 0),
    "not_too_happy":       ("Not too happy these days (%)", "share", ("happiness", [1]), 1),
    "life_sat_mean":       ("Satisfaction with life as a whole (mean, 1-7)", "mean", ("life_satisfaction", None), 0),
    "homework_mean_h":     ("Homework, hours per week (mean of category midpoints)", "mean", ("homework_hours", {1: 0, 2: 2.5, 3: 7, 4: 12, 5: 17, 6: 22, 7: 27.5}), None),
    "homework_10plus":     ("Homework 10+ hours per week (%)", "share", ("homework_hours", [4, 5, 6, 7]), None),
    "homework_lt5":        ("Homework under 5 hours per week (%)", "share", ("homework_hours", [1, 2]), None),
    "evenings_out_mean":   ("Evenings out for fun per week (mean of midpoints)", "mean", ("evenings_out", {1: 0.5, 2: 1, 3: 2, 4: 3, 5: 4.5, 6: 6.5}), None),
    "evenings_out_3plus":  ("Three or more evenings out per week (%)", "share", ("evenings_out", [4, 5, 6]), None),
    "friends_daily":       ("Gets together with friends informally almost every day or more (%)", "share", ("friends_informal_freq", [5, 6]), None),
    "dating_weekly":       ("Goes out on a date once a week or more (%)", "share", ("dating_freq", [4, 5, 6]), None),
    "tv_weekday_mean_h":   ("TV on an average weekday, hours (mean of midpoints)", "mean", ("tv_hours_weekday", {1: 0, 2: 0.25, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5.5}), None),
    "tv_3plus":            ("TV 3+ hours on an average weekday (%)", "share", ("tv_hours_weekday", [5, 6, 7]), None),
    "internet_mean_h":     ("Internet for personal use, hours per week (mean of midpoints)", "mean", ("internet_hours_week", "labels"), None),
    "internet_10plus":     ("Internet for personal use 10+ hours per week (%)", "share", ("internet_hours_week", [6, 7, 8, 9]), None),
    "games_mean_h":        ("Electronic games, hours per week (mean of midpoints)", "mean", ("games_hours_week", "labels"), None),
    "computer_school_mean_h": ("Computer for school work, hours per week (mean of midpoints)", "mean", ("computer_hours_week", "labels"), None),
    "life_sat_satisfied":  ("Quite or completely satisfied with life as a whole (%)", "share", ("life_satisfaction", [6, 7]), 0),
    "sns_daily":           ("Visits social networking sites almost every day or more (%)", "share", ("social_network_freq", [5, 6]), None),
    "works":               ("Works in a paid or unpaid job during the school year (%)", "share", ("work_hours", [2, 3, 4, 5, 6, 7, 8]), None),
    "work_16plus":         ("Works 16+ hours per week (%)", "share", ("work_hours", [5, 6, 7, 8]), None),
    "sleep7_mostdays":     ("Gets 7+ hours of sleep most days or more often (%)", "share", ("sleep_7h", [4, 5, 6]), 0),
    "short_sleep_often":   ("Gets less sleep than they should nearly every day or every day (%)", "share", ("less_sleep_than_should", [5, 6]), 1),
}
COMPOSITES = {"selfderog_mean": ("Self-derogation: mean % agree over four items", ["not_much_proud", "no_good_at_all", "cant_do_right", "life_not_useful"]),
              "depaffect_mean": ("Depressive affect: mean % endorsing the depressive pole over four items", ["life_meaningless", "future_hopeless", "not_enjoy_life", "not_good_alive"])}
def hours_midpoint(label):
    """Midpoint of a printed hours category: 'None' 0, 'Less than 1' 0.5, '1-2 hours' 1.5, '3-5' 4, '6-9' 7.5, '10-19' 14.5, '20-29' 24.5, '30-39' 34.5,
    '40 or more' 45, '30 or more' 35 (top codes: lower bound + 5)."""
    if not isinstance(label, str) or label.strip() in ("", "None"): return 0.0
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", label)]
    if re.search(r"less than", label, re.I) and nums: return nums[0] / 2
    if re.search(r"or more|more than|\+", label) and nums: return nums[0] + 5
    return float(np.mean(nums)) if nums else np.nan
def pooled(P):
    """Pool forms within year x series x response code, weighting percentages by the weighted N answering (per sex)."""
    rows = []
    for (y, s, code), g in P.groupby(["year", "series", "response_code"]):
        r = dict(year=y, series=s, response_code=code, response_label=g.response_label.iloc[0], wording=g.wording.iloc[0], item_ref=g.item_ref.iloc[0], forms=len(g))
        for sx, pc, nc in [("all", "pct_total", "n_total"), ("boys", "pct_male", "n_male"), ("girls", "pct_female", "n_female")]:
            n = g[nc].fillna(0).values; p = g[pc].values; r[f"pct_{sx}"] = np.average(p, weights=n) if n.sum() > 0 else np.nan; r[f"n_{sx}"] = n.sum()
        rows.append(r)
    return pd.DataFrame(rows)
def indicators(Q):
    out = []
    for name, (label, kind, (series, spec), neg) in IND.items():
        d = Q[Q.series == series]
        if d.empty: continue
        for y, g in d.groupby("year"):
            for sx in ["all", "boys", "girls"]:
                p = g.set_index("response_code")[f"pct_{sx}"]; n = g[f"n_{sx}"].iloc[0]
                if kind == "share":
                    v = p.reindex(spec).fillna(0).sum(); se = 100 * np.sqrt(max(v / 100 * (1 - v / 100), 0) / n * DEFF) if n > 0 else np.nan
                else:
                    if spec == "labels": mid = pd.Series({int(r.response_code): hours_midpoint(r.response_label) for r in g.itertuples()}).reindex(p.index)
                    else: mid = pd.Series(spec) if spec else pd.Series({c: c for c in p.index}); mid = mid.reindex(p.index)
                    v = float((p / 100 * mid).sum()); var = float((p / 100 * (mid - v) ** 2).sum()); se = np.sqrt(var / n * DEFF) if n > 0 else np.nan
                out.append(dict(indicator=name, label=label, year=y, sex=sx, value=v, se=se, n=n, forms=g.forms.iloc[0], item_ref=g.item_ref.iloc[0], kind=kind, higher_is_worse=neg))
    S = pd.DataFrame(out)
    for cname, (label, parts) in COMPOSITES.items():
        d = S[S.indicator.isin(parts)]
        for (y, sx), g in d.groupby(["year", "sex"]):
            if g.indicator.nunique() < len(parts): continue
            S = pd.concat([S, pd.DataFrame([dict(indicator=cname, label=label, year=y, sex=sx, value=g.value.mean(), se=np.sqrt((g.se ** 2).sum()) / len(g), n=g.n.min(), forms=np.nan, item_ref=np.nan, kind="composite", higher_is_worse=1)])])
    return S.sort_values(["indicator", "sex", "year"]).reset_index(drop=True)
def changes(S, periods=((1996, 2010), (2010, 2012), (1996, 2012), (2005, 2012))):
    rows = []
    for (ind, sx), g in S.groupby(["indicator", "sex"]):
        g = g.set_index("year"); r = dict(indicator=ind, label=g.label.iloc[0], sex=sx, first_year=int(g.index.min()), last_year=int(g.index.max()))
        for y in [1996, 2000, 2005, 2010, 2012]: r[f"v{y}"] = g.value.get(y, np.nan)
        for a, b in periods:
            if a in g.index and b in g.index: r[f"d_{a}_{b}"] = g.value[b] - g.value[a]; r[f"se_{a}_{b}"] = np.sqrt(g.se[a] ** 2 + g.se[b] ** 2)
            else: r[f"d_{a}_{b}"] = np.nan; r[f"se_{a}_{b}"] = np.nan
        fy, ly = int(g.index.min()), int(g.index.max()); r["v_first"] = g.value[fy]; r["v_last"] = g.value[ly]; r["d_first_last"] = g.value[ly] - g.value[fy]; r["se_first_last"] = np.sqrt(g.se[fy] ** 2 + g.se[ly] ** 2)
        rows.append(r)
    return pd.DataFrame(rows)
def comovement(S, exposures=("homework_mean_h", "evenings_out_mean", "friends_daily", "tv_weekday_mean_h", "sleep7_mostdays", "works", "internet_mean_h", "games_mean_h"), outcomes=("lonely_agree", "selfderog_mean", "depaffect_mean", "not_too_happy", "life_sat_mean")):
    rows = []
    for sx in ["all", "boys", "girls"]:
        W = S[S.sex == sx].pivot(index="year", columns="indicator", values="value")
        for x in exposures:
            for y in outcomes:
                if x not in W or y not in W: continue
                d = W[[x, y]].dropna()
                if len(d) < 8: continue
                r_lvl = d[x].corr(d[y]); dd = d.diff().dropna(); r_dif = dd[x].corr(dd[y])
                rows.append(dict(sex=sx, exposure=x, outcome=y, years=len(d), r_levels=r_lvl, r_first_differences=r_dif, y0=int(d.index.min()), y1=int(d.index.max())))
    return pd.DataFrame(rows)
def part_a():
    P = pd.read_csv(C/"mtf_published_trends.csv", keep_default_na=False, na_values=[""]); P["response_label"] = P.response_label.astype(str)
    for c in ["n_total", "n_male", "n_female", "pct_total", "pct_male", "pct_female"]: P[c] = pd.to_numeric(P[c], errors="coerce")
    sums = P.groupby(["year", "series", "form"]).pct_total.sum(); bad = sums[~sums.between(99, 101)]
    assert bad.empty, f"distributions not summing to 100:\n{bad}"
    Q = pooled(P); S = indicators(Q)
    S.to_csv(T/"mtf_published_series.csv", index=False); CH = changes(S); CH.to_csv(T/"mtf_published_changes.csv", index=False)
    CM = comovement(S); CM.to_csv(T/"mtf_published_comovement.csv", index=False)
    cov = Q.groupby("series").agg(item_ref=("item_ref", "first"), wording=("wording", "first"), first_year=("year", "min"), last_year=("year", "max"), years=("year", "nunique"), forms=("forms", "max"), n_all_median=("n_all", "median")).reset_index()
    cov.to_csv(T/"mtf_published_coverage.csv", index=False)
    for f in ["mtf_literature.csv", "mtf_johnson2017_year_effects.csv"]: shutil.copy(C/f, T/f)
    print("published series:", S.indicator.nunique(), "indicators,", S.year.min(), "-", S.year.max()); print(cov[["series", "item_ref", "first_year", "last_year", "forms", "n_all_median"]].to_string())
    key = ["homework_mean_h", "homework_10plus", "evenings_out_mean", "friends_daily", "tv_weekday_mean_h", "internet_mean_h", "sleep7_mostdays", "lonely_agree", "selfderog_mean", "depaffect_mean", "very_happy"]
    print("\nAll 12th graders, selected years:"); print(S[(S.sex == "all") & S.indicator.isin(key) & S.year.isin([1996, 2000, 2005, 2010, 2012])].pivot(index="indicator", columns="year", values="value").round(2).to_string())
    print("\nChanges 1996->2012 (SE), girls vs boys:"); print(CH[CH.indicator.isin(key)].pivot(index="indicator", columns="sex", values="d_1996_2012").round(2).to_string())
    print("\nCo-movement (all, levels / first differences):"); print(CM[CM.sex == "all"].pivot(index="exposure", columns="outcome", values="r_levels").round(2).to_string())
    return S
# ----------------------------------------------------------------------------------------------------------------------------- (B)
LABEL_PATTERNS = {  # concept -> regex on the ICPSR variable label (MTF OSIRIS abbreviations) ; case-insensitive
    "year": r"^YEAR|YEAR OF ADMIN", "form": r"FORM ID|^FORM|QUESTIONNAIRE FORM", "weight": r"SAMPL.*W(EI)?GH?T|^WEIGHT|ARCHIVE WEIGHT", "grade": r"GRADE", "sex": r"R'?S SEX|^SEX",
    "race": r"R'?S RACE|RACE", "region": r"REGION", "father_educ": r"FATHR? EDUC|FATH.*ED LEV", "mother_educ": r"MOTHR? EDUC|MOTH.*ED LEV",
    "happy": r"VRY HPY|HPY THS DAYS|HAPPY", "life_satisfaction": r"CMP SATFD W/LIFE|SATISF.*LIFE", "lonely": r"FEEL LONELY|LOT.*LONELY|OFT.*LONELY", "left_out": r"LEFT OUT",
    "not_much_proud": r"MUCH TO B PROUD|PROUD OF", "no_good_at_all": r"I AM NO GOOD|NO GOOD AT ALL", "cant_do_anything_right": r"ANYTH.*RIGHT|CANT DO|CAN'T DO", "life_not_useful": r"LIFE NT USEFL|LIFE.*USEF",
    "life_meaningless": r"MEANINGLESS|MEANINGLS", "future_hopeless": r"HOPELESS|HOPELS", "enjoy_life": r"ENJOY LIFE|ENJY LIFE", "good_to_be_alive": r"GOOD.*ALIVE|GD.*ALIVE",
    "homework_hours": r"HMWK|HMWRK|HOMEWORK|HOMEWRK", "evenings_out": r"EVE.*OUT|EVNGS OUT|#EVE", "friends_informal": r"GET TOGETHER|GT TOGTHR|TOGTHR.*FRND|W/FRIENDS|FRNDS INFRML",
    "social_network_freq": r"SOC(IAL)? ?NETW|SNS|FACEBOOK", "social_media_hours": r"HRS.*SOC(IAL)? ?NETW|SOC(IAL)? ?NETW.*HRS|HRS.*SOCIAL MEDIA", "internet_hours": r"INTERNET|INTRNT", "texting": r"TEXT",
    "tv_weekday": r"TV.*WKDAY|TV.*WEEKDAY|HRS TV|WATCH TV", "sleep_7h": r"7 ?HRS? SLEEP|SEVEN HRS|HRS SLEEP|7\+? HOURS SLEEP", "work_hours": r"HRS/WK WORK|HRS WORK|PAID JOB",
}
ORBEN_8_10 = {  # confirmed V-codes for the 8th/10th-grade files 2008-2016 (Orben & Przybylski 2019 code: 1_2_prep_mtf.R, 2_2_sca_mtf.R)
    "year": "V1", "grade": "V501", "sex": "V7202", "race": "V1070", "happy": "V7302", "life_meaningless": "V8502", "enjoy_life": "V8505", "future_hopeless": "V8509",
    "good_to_be_alive": "V8514", "not_much_proud": "V8503", "no_good_at_all": "V8507", "cant_do_anything_right": "V8511", "life_not_useful": "V8513",
    "self_positive": "V8501", "self_worth": "V8504", "self_dowell": "V8508", "self_satisfied": "V8512", "someone_to_turn_to": "V7502", "lonely_block_first": "V7501",
    "tv_weekday": "V7325", "tv_weekend": "V7326", "internet_news": "V7381", "social_network_freq": "V7552", "computer_school": "V7544", "internet_hours": "V7551",
    "games_hours": "V7553", "social_media_hours": "V7589", "video_chat": "V7590", "texting": "V7562", "calling": "V7563", "mother_educ": "V7216", "siblings": "V7208",
    "mother_job": "V7217", "enjoy_school": "V7329", "grades": "V7221", "talk_parents": "V7254", "short_sleep": "V8531",
}  # V7501 is the first item of the loneliness block ("A lot of times I feel lonely") by questionnaire order; confirm in the codebook before use
def read_meta(f):
    import pyreadstat
    rd = {".dta": pyreadstat.read_dta, ".sav": pyreadstat.read_sav, ".sas7bdat": pyreadstat.read_sas7bdat}.get(f.suffix.lower())
    if rd is None: return None, None
    _, m = rd(str(f), metadataonly=True); return rd, m
def locate(meta):
    labs = {v: (meta.column_labels[i] or "") for i, v in enumerate(meta.column_names)}; found = {}
    for concept, pat in LABEL_PATTERNS.items():
        hits = [v for v, l in labs.items() if re.search(pat, l, re.I)]
        if hits: found[concept] = hits
    return labs, found
def part_b():
    files = sorted(p for p in MICRO.glob("*/**/*") if p.suffix.lower() in (".dta", ".sav", ".sas7bdat", ".tsv")) if MICRO.exists() else []
    status = [dict(checked=pd.Timestamp.today().date().isoformat(), microdata_dir=str(MICRO.relative_to(ROOT)), files_found=len(files),
                   blocked="ICPSR (icpsr.umich.edu) returns HTTP 403 Cloudflare bot challenge to curl, headless Chromium and remote fetchers from this host; downloads require an ICPSR login with terms acceptance; no credentials available",
                   needed="ICPSR series 35 public-use files, 12th grade 1991-2024 and 8th/10th 1991-2024 (study numbers in the script header), Stata format recommended, one directory per study")]
    if not files:
        pd.DataFrame(status).to_csv(T/"mtf_microdata_status.csv", index=False); print("\n(B) microdata: none found in", MICRO, "- see the script header for the ICPSR studies to download"); return
    import pyfixest as pf
    maps, frames = [], []
    for f in files:
        study = f.relative_to(MICRO).parts[0]; rd, meta = read_meta(f)
        if meta is None: continue
        labs, found = locate(meta); grades = "8_10" if any(re.search(r"GRADE", l, re.I) for l in labs.values()) and "V501" in labs else "12"
        for c, hits in found.items(): maps.append(dict(study=study, file=f.name, grades=grades, concept=c, candidates=";".join(hits[:6]), labels=" | ".join(labs[h][:40] for h in hits[:6])))
        use = {c: h[0] for c, h in found.items()}
        if grades == "8_10": use.update({k: v for k, v in ORBEN_8_10.items() if v in labs})
        need = ["year", "weight", "sex", "homework_hours", "social_media_hours"]
        if not all(k in use for k in need): print(f"  {study}/{f.name}: missing {[k for k in need if k not in use]} - skipped"); continue
        cols = sorted(set(use.values())); df, _ = rd(str(f), usecols=cols); df = df.rename(columns={v: k for k, v in use.items()}); df["study"] = study; df["grades"] = grades; frames.append(df)
    pd.DataFrame(maps).to_csv(T/"mtf_micro_varmap.csv", index=False); print(pd.DataFrame(maps).to_string())
    if not frames: pd.DataFrame(status).to_csv(T/"mtf_microdata_status.csv", index=False); return
    D = pd.concat(frames, ignore_index=True)
    for c in ["not_much_proud", "no_good_at_all", "cant_do_anything_right", "life_not_useful", "life_meaningless", "future_hopeless", "lonely", "happy", "homework_hours", "social_media_hours", "year", "weight", "sex"]:
        if c in D: D[c] = pd.to_numeric(D[c], errors="coerce").where(lambda s: s > 0)  # MTF missing codes are negative (-9, -8)
    D["enjoy_life_r"] = 6 - D["enjoy_life"] if "enjoy_life" in D else np.nan; D["good_alive_r"] = 6 - D["good_to_be_alive"] if "good_to_be_alive" in D else np.nan
    D["depaffect"] = D[[c for c in ["life_meaningless", "future_hopeless", "enjoy_life_r", "good_alive_r"] if c in D]].mean(axis=1)
    D["selfderog"] = D[[c for c in ["not_much_proud", "no_good_at_all", "cant_do_anything_right", "life_not_useful"] if c in D]].mean(axis=1)
    D["girl"] = (D.sex == 2).astype(int) if "sex" in D else np.nan   # MTF: 1 = male, 2 = female
    HW = {1: 0, 2: 2.5, 3: 7, 4: 12, 5: 17, 6: 22, 7: 27.5}; D["hw_h"] = D.homework_hours.map(HW)
    SM = {1: 0, 2: 0.25, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5.5, 8: 7, 9: 9}; D["sm_h"] = D.social_media_hours.map(SM)  # hours/day categories: none, <1/2 h, ~1, ~2, ~3, ~4, ~5, 6-8, 9+ (confirm in codebook)
    rows = []
    for y in ["depaffect", "selfderog", "lonely", "happy"]:
        if y not in D or D[y].notna().sum() < 1000: continue
        for g, dg in D.groupby("grades"):
            for sx, lab in [(None, "all"), (1, "girls"), (0, "boys")]:
                d = dg if sx is None else dg[dg.girl == sx]; d = d.dropna(subset=[y, "hw_h", "sm_h", "weight", "year"])
                if len(d) < 2000: continue
                ctrl = " + ".join(f"C({c})" for c in ["race", "mother_educ", "father_educ", "region"] if c in d and d[c].notna().mean() > 0.5)
                m = pf.feols(f"{y} ~ hw_h * sm_h" + (f" + {ctrl}" if ctrl else "") + " | year", data=d, weights="weight", vcov="hetero")
                for term in ["hw_h", "sm_h", "hw_h:sm_h"]:
                    rows.append(dict(outcome=y, grades=g, sex=lab, term=term, coef=m.coef()[term], se=m.se()[term], n=m._N, years=f"{int(d.year.min())}-{int(d.year.max())}", mean_y=np.average(d[y], weights=d.weight)))
    R = pd.DataFrame(rows); R.to_csv(T/"mtf_micro_models.csv", index=False); print(R.to_string())
    # decomposition: year effects with and without time-use covariates (reference = first year with social-media hours)
    dec = []
    for g, dg in D.groupby("grades"):
        d = dg.dropna(subset=["depaffect", "hw_h", "sm_h", "weight", "year"])
        if d.year.nunique() < 3: continue
        y0 = int(d.year.min()); m0 = pf.feols(f"depaffect ~ i(year, ref={y0})", data=d, weights="weight", vcov="hetero"); m1 = pf.feols(f"depaffect ~ i(year, ref={y0}) + hw_h + sm_h + hw_h:sm_h", data=d, weights="weight", vcov="hetero")
        for k in m0.coef().index:
            yy = int(re.search(r"(\d{4})", k).group(1)); dec.append(dict(grades=g, year=yy, ref_year=y0, change_unadjusted=m0.coef()[k], change_adjusted_timeuse=m1.coef()[k], share_accounted=1 - m1.coef()[k] / m0.coef()[k] if m0.coef()[k] else np.nan, n=m0._N))
    pd.DataFrame(dec).to_csv(T/"mtf_micro_decomposition.csv", index=False); status[0]["files_found"] = len(files); pd.DataFrame(status).to_csv(T/"mtf_microdata_status.csv", index=False)
if __name__ == "__main__":
    part_a(); part_b()
