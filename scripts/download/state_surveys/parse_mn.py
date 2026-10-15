"""Minnesota Student Survey: county + community health board + state trends 1998-2019.
Source: MDH 'Minnesota Student Survey selected single-year results by state, county and community health board, 1998-2019 (XLS)'
https://www.health.state.mn.us/data/mchs/surveys/mss/docs/singleyear/msssingleyr2019.xlsx
Sheet 'Template 4' (Section 4: Mental Health) holds the county x (indicator, year, grade) matrix; header row 0 = indicator
(block start), row 1 = year (block start), row 2 = grade. Values '--' / '="--"' = suppressed/not asked."""
import re, openpyxl, pandas as pd
SRC = "data/external/state_surveys/mn/msssingleyr2019.xlsx"
URL = "https://www.health.state.mn.us/data/mchs/surveys/mss/docs/singleyear/msssingleyr2019.xlsx"
ITEMS = [  # (regex on header, item code, wording note)
    (r"^Q50 Felt under great stress", "stress_high", "MN 1998-2010 Q50: felt under great stress or pressure (almost more than I could take) in the last 30 days; general, not school-specific"),
    (r"^Q51 Felt sad all or most", "sad_hopeless", "MN 1998-2010 Q51: felt sad all or most of the time in the last 30 days (NOT the YRBS 2-week sad/hopeless item)"),
    (r"^Q53 Felt nervous", "nervous_30d", "MN 1998-2010 Q53: felt nervous, worried or upset all or most of the time in the last 30 days"),
    (r"^Q52 Felt discouraged or hopeless", "hopeless_30d", "MN 1998-2010 Q52: felt discouraged or hopeless (extremely so or quite a bit) in the last 30 days"),
    (r"^Q54b Had suicidal thoughts", "considered_suicide", "MN 1998-2010 Q54b: had suicidal thoughts in the last year"),
    (r"^Q54c Tried to kill self", "attempted_suicide", "MN 1998-2010 Q54c: tried to kill self in the last year"),
    (r"^Q61B Had suicidal thoughts", "considered_suicide_alt", "MN 2013/2016 Q61B: had suicidal thoughts in the last year (mostly suppressed)"),
    (r"^Q62 Tried to kill self", "attempted_suicide_alt", "MN 2013/2016 Q62 (mostly suppressed)"),
    (r"^Q61b Seriously considered attempting suicide", "considered_suicide", "MN 2013/2016 Q61b: seriously considered attempting suicide during the last year"),
    (r"^Q60 Purposely hurt self", "self_harm", "MN 2013/2016 Q60: purposely hurt self in last 12 months"),
    (r"^P50a Bothered by little interest", "anhedonia_2wk", "MN 2016/2019 P50a: PHQ-2 little interest or pleasure in doing things, past two weeks (more than half the days or nearly every day)"),
    (r"^P50b Bothered by feeling down", "depressed_2wk", "MN 2016/2019 P50b: PHQ-2 bothered by feeling down, depressed or hopeless over the past two weeks (more than half the days or nearly every day)"),
    (r"^P51 Purposely hurt self", "self_harm", "MN 2019 P51: purposely hurt self in last 12 months"),
    (r"^P52b Seriously considered attempting suicide", "considered_suicide", "MN 2019 P52b: seriously considered attempting suicide during the last year"),
    (r"^P53b Attempted suicide", "attempted_suicide", "MN 2019 P53b: attempted suicide during the last year"),
]
wb = openpyxl.load_workbook(SRC, read_only=True)
rows = list(wb["Template 4"].iter_rows(values_only=True))
h0, h1, h2 = rows[0], rows[1], rows[2]
cols = []  # (col, item, note, year, grade, header)
cur = None; year = None; seen_block = {}
for j in range(2, len(h0)):
    if h0[j] not in (None, ""):
        cur = str(h0[j]).strip().replace("\n", " ")
        seen_block[cur] = seen_block.get(cur, 0) + 1
        cur_key = (cur, seen_block[cur])
    if h1[j] not in (None, ""):
        year = int(str(h1[j]).strip())
    g = h2[j]
    if cur is None or year is None or not g: continue
    grade = re.sub(r"\D", "", str(g))
    for pat, code, note in ITEMS:
        if re.search(pat, cur, re.I):
            # the second block labelled 'Q61b Seriously considered...' (cols 322-327) carries attempted-suicide-sized values;
            # per the lookup sheet it is the 'attempted suicide during the last year' (Q62) block for 2013/2016.
            if code == "considered_suicide" and cur.startswith("Q61b") and seen_block[cur] == 2:
                code, note = "attempted_suicide", "MN 2013/2016 Q62: attempted suicide during the last year (source header mislabelled 'Q61b'; identified via lookup-sheet formulas)"
            cols.append((j, code, note, year, grade, cur)); break
out = []
for row in rows[3:]:
    geo = row[1]
    if not geo or geo == "TEST": continue
    geo = str(geo).strip()
    gtype = "CHB" if geo.startswith("CHB") else ("state" if geo.startswith("State") else "county")
    for j, code, note, y, grade, hdr in cols:
        v = row[j]
        try: v = float(v)
        except (TypeError, ValueError): continue
        out.append(dict(state="MN", geography_type=gtype, geography_name=geo, geography_fips=None, year=y, grade_or_age=grade, sex="all",
                        item=code, value_pct=round(v, 2), n=None, source_url=URL, note=note))
df = pd.DataFrame(out)
df.to_csv("data/compiled/state_surveys/mn_mss_county.csv", index=False)
print(df.groupby(["item", "year"]).size().unstack(fill_value=0))
print(df.geography_type.value_counts().to_dict())
print(df[(df.geography_name=="State of Minnesota")&(df.grade_or_age.isin(["9","11"]))].pivot_table(index=["item","grade_or_age"],columns="year",values="value_pct"))
