"""Build the school smartphone-ban tables in data/compiled/phone_bans/.

Re-run from the repository root with:  uv run python scripts/download/phone_bans/build_phone_bans.py

Every row is hard-coded here with its source URL. Downloads and text extractions of the
sources are in data/external/phone_bans/ (see README.md there); notes in notes/phone_bans.md.
Status date for the state table: 2026-09-16.
"""
from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parents[3] / "data" / "compiled" / "phone_bans"
OUT.mkdir(parents=True, exist_ok=True)

BP = "https://ballotpedia.org/State_policies_on_cellphone_use_in_K-12_public_schools"
EW = "https://www.edweek.org/technology/which-states-ban-or-restrict-cellphones-in-schools/2024/06"
KFF = ("https://www.kff.org/affordable-care-act/a-look-at-state-efforts-to-ban-cellphones-in-schools-"
       "and-implications-for-youth-mental-health/")

# policy_type vocabulary (current status as of 2026-09-16):
BELL = "statewide bell-to-bell ban"
INSTR = "ban during instructional time"
REQ = "requires districts to adopt a policy"
GUIDE = "guidance/recommendation only"
NONE = "none"

# (state, policy_type, citation, date_enacted, effective_school_year, grades_covered, source_url, note)
STATES = [
    ("Alabama", BELL, "HB 166 (FOCUS Act, 2025); Alabama SBE resolution 2024-02-11", "2025-05-14", "2025-26", "K-12",
     BP, "No possession of a wireless device on person during the instructional day (must be off and stored). "
         "Feb 2024 SBE resolution only encouraged district limits."),
    ("Alaska", REQ, "HB 57 (2025), enacted by veto override", "2025-05-20", "2025-26", "K-12",
     BP, "Districts must adopt a policy regulating possession/use during school hours incl. lunch and passing; no ban "
         "mandated. Preceded by State Board of Education directive 2024-10-11. Not counted by EdWeek as requiring a ban."),
    ("Arizona", REQ, "HB 2484 (2025)", "2025-04-14", "2025-26", "K-12",
     BP, "Districts must adopt policies that 'limit' wireless device use during the school day and restrict social-media "
         "access on school internet. EdWeek classifies as bell-to-bell; Ballotpedia as 'limits use in classrooms'."),
    ("Arkansas", BELL, "SB 142 (Bell to Bell, No Cell Act, 2025)", "2025-02-21", "2025-26", "K-12",
     BP, "District policies (approved by DESE) must restrict possession and prohibit use during the school day. "
         "2024 pilot grant for pouches (2024-07-02)."),
    ("California", REQ, "AB 3216 (Phone-Free School Act, 2024)", "2024-09-23", "2026-27", "K-12",
     BP, "Districts, county offices and charters must adopt (by 2026-07-01, update every 5 years) a policy to limit or "
         "prohibit smartphone use at school; may be a full ban. AB 272 (2019) had merely permitted limits."),
    ("Colorado", REQ, "HB25-1135 (2025)", "2025-05-01", "2026-27", "K-12",
     BP, "Policy on possession/use during the school day required by 2026-07-01; content left to districts."),
    ("Connecticut", REQ, "HB 7009 (2025) sec. 5; SBE guidance 2024-08-21 and 2026-08", "2025-06", "2026-27", "K-12",
     "https://portal.ct.gov/governor/news/press-releases/2025/05-2025/governor-lamont-applauds-house-approval-of-legislation-on-smartphones-in-schools",
     "2025 law requires every district to adopt a smartphone policy by 2026-27 using CSDE guidance (Public Act number "
     "and signing date not verified). Aug 2026 SBE guidance 'strongly recommends' bell-to-bell; a statutory bell-to-bell "
     "ban failed in the 2026 session. Ballotpedia lists only the 2024 guidance."),
    ("Delaware", REQ, "SB 106 (2026); FY2025 budget pouch pilot 2024-07-01", "2026-03-12", "2026-27", "K-12",
     BP, "Districts/charters must adopt a policy that at minimum limits use during instructional time. Effective year "
         "assumed (not verified). $250k pouch pilot in 2024."),
    ("District of Columbia", BELL, "DCPS Student Cell Phone and Electronic Device Policy (announced 2025-06-06); "
     "DC Council Distraction-Free Learning Amendment Act of 2025 (passed 2025-07-01)", "2025-07-01", "2025-26", "K-12",
     "https://dcps.dc.gov/release/dc-public-schools-will-be-phone-free-beginning-school-year-2025-2026",
     "DCPS bell-to-bell from 2025-26 (all grades); Council act extends to charters, full effect 2026-27 "
     "(council act details from press coverage, not the enrolled act)."),
    ("Florida", BELL, "HB 379 (2023); HB 1105 (2025)", "2023-05-09", "2023-24", "K-8 bell-to-bell (from 2025-26); "
     "9-12 instructional time (6-district full-day pilot 2025-26)",
     BP, "First state law: HB 379 banned use during instructional time from 2023-24 and required social-media blocks "
         "on school Wi-Fi. HB 1105 (signed 2025-05-30) made K-8 phone-free for the whole school day from 2025-26 and "
         "created a 6-district high-school full-day pilot (report due 2026-12-01). Orange County district bell-to-bell "
         "from Aug 2023."),
    ("Georgia", BELL, "HB 340 (Distraction-Free Education Act, 2025); HB 1009 (2026)", "2025-05-09", "2026-27",
     "K-8 from 2026-27; 9-12 from 2027-28",
     BP, "HB 340 signed 2025-05-09 (K-8, effective 2026-07-01); HB 1009 signed 2026-05-05 extends to high school from "
         "2027-07-01."),
    ("Hawaii", BELL, "Hawaii Board of Education policy (adopted 2026-02-12)", "2026-02-12", "2026-27",
     "K-8 bell-to-bell; 9-12 instructional time",
     BP, "Single statewide district; policy, not statute. Ballotpedia table gives 2026-02-02, timeline 2026-02-12."),
    ("Idaho", REQ, "SB 1032 (2025); Executive Order 'Phone-Free Learning' 2024-10-31", "2025-03", "2025-26", "K-12",
     "https://legislature.idaho.gov/sessioninfo/2025/legislation/s1032/",
     "SB 1032 requires each district/charter to adopt a 'distraction-free learning' policy minimizing device use by "
     "2025-12-31; no ban mandated (signing day not verified). EO offered $5,000 to districts adopting policies. "
     "EdWeek counts Idaho as bell-to-bell; Ballotpedia lists only the EO."),
    ("Illinois", BELL, "SB 2427 (2026)", "2026-07-28", "2027-28", "K-12 (districts may allow HS use at lunch/passing)",
     BP, "School boards must adopt policies prohibiting use during school time by start of 2027-28."),
    ("Indiana", INSTR, "SEA 185 (2024)", "2024-03-11", "2024-25", "K-12",
     BP, "Prohibits wireless devices (phones, tablets, laptops) during instructional time; teacher/emergency exceptions."),
    ("Iowa", INSTR, "HF 782 (2025)", "2025-04-30", "2025-26", "K-12",
     BP, "District policies must restrict use during classroom instructional time (from 2025-07-01). Ballotpedia labels "
         "it a statewide ban."),
    ("Kansas", BELL, "HB 2299 (2026); Kansas SBE recommendation 2024-12-11", "2026-03-20", "2026-27", "K-12",
     BP, "Devices off and stored away during the school day. Dec 2024 SBE task-force recommendation was non-binding."),
    ("Kentucky", BELL, "HB 208 (2025)", "2025-03-26", "2025-26", "K-12",
     BP, "District policies must prohibit use during the school day with exceptions; social media blocked on school tech."),
    ("Louisiana", BELL, "SB 207 (Act 2024)", "2024-05-28", "2024-25", "K-12",
     BP, "No possession on person throughout the instructional day; devices off and stowed."),
    ("Maine", BELL, "LD 2212 (2026); LD 1234 (2025)", "2026-04-10", "2026-27", "K-12",
     BP, "LD 1234 (2025-06-09) only required a policy; LD 2212 requires bell-to-bell prohibition by 2026-08-01."),
    ("Maryland", BELL, "HB 525 / SB 928 (Maryland Phone-Free Schools Act, 2026)", "2026-05-26", "2027-28", "K-12",
     "https://www.cbsnews.com/baltimore/news/newly-signed-maryland-bill-restrict-students-use-cellphones-school-day/",
     "County boards must implement bell-to-bell policies by 2027-28; no suspension/expulsion solely for violations. "
     "Montgomery County adopts bell-to-bell district-wide in 2026-27."),
    ("Massachusetts", NONE, "S.2581 passed Senate 2025-08-01 (38-2); H.5366 passed House 2026-04-09 (129-25)", "", "", "",
     "https://www.boston.com/news/local-news/2026/04/09/mass-house-passes-bill-restricting-teen-social-media-and-phones-in-schools/",
     "Both chambers passed bell-to-bell bills but versions were not reconciled/signed as of Aug 2026. No state mandate."),
    ("Michigan", INSTR, "HB 4141 (2026)", "2026-02-10", "2026-27", "K-12",
     BP, "Districts must implement policy prohibiting use on school grounds during instructional time."),
    ("Minnesota", REQ, "SF 3567 (2024), Minn. Stat. 121A.73", "2024-05-17", "2024-25", "K-12",
     BP, "Districts/charters must adopt a cellphone policy by 2025-03-15; content unspecified. A K-8 bell-to-bell / "
         "9-12 classroom ban bill was pending in the 2026 session (outcome not verified; Ballotpedia July 2026 lists "
         "only SF 3567)."),
    ("Mississippi", NONE, "SB 2151 (2025) passed Senate, died; HB 570 (2026) died", "", "", "",
     "https://www.mississippifreepress.org/classroom-cellphone-ban-other-mississippi-senate-education-bills-appear-dead-in-house/",
     "No statewide action."),
    ("Missouri", BELL, "SB 68 (2025)", "2025-07-09", "2025-26", "K-12",
     BP, "Policies must prohibit display/use from start to end of school day incl. meals, breaks, passing. Ballotpedia "
         "table gives 2025-07-07, timeline 2025-07-09."),
    ("Montana", GUIDE, "Governor Gianforte letter to districts 2024-08-22", "2024-08-22", "", "K-12",
     BP, "Letter asking districts to consider 'cell phone-free' policies; no statute."),
    ("Nebraska", BELL, "LB 140 (2025)", "2025-05-20", "2025-26", "K-12",
     BP, "Policies must prohibit use on school property or at school functions, with exceptions."),
    ("Nevada", INSTR, "SB 444 (2025)", "2025-05-28", "2025-26", "K-12",
     BP, "District policies must prohibit access during class (exceptions). Ballotpedia counts NV among bell-to-bell "
         "states; statute text targets class time. Clark County used signal-blocking pouches for grades 6-12 from 2024-25."),
    ("New Hampshire", BELL, "HB 2 (2025 budget trailer)", "2025-06-30", "2025-26", "K-12",
     BP, "Policies must prohibit all personal device use from first bell to dismissal bell."),
    ("New Jersey", BELL, "S3695 / A4882 (P.L. 2026)", "2026-01-08", "2026-27", "K-12",
     BP, "Boards adopt policies per NJDOE guidelines prohibiting non-academic use on school grounds during the school "
         "day; NJDOE updated guidelines Jan 2026."),
    ("New Mexico", REQ, "SB 11 (2025)", "2025-04-10", "2025-26", "K-12",
     BP, "Districts/charters must adopt a wireless-device policy per PED guidelines; no ban mandated."),
    ("New York", BELL, "FY2026 state budget (S3006-C, Education Article VII), enacted 2025-05-09", "2025-05-09", "2025-26",
     "K-12", "https://www.governor.ny.gov/news/distraction-free-schools-governor-hochul-announces-new-york-become-largest-state-nation",
     "Districts/charters must prohibit use during the school day (bell-to-bell) from 2025-26; ~$13.5M for storage. "
     "NYC DOE had banned phones until 2015-03-02 (ban lifted under de Blasio)."),
    ("North Carolina", INSTR, "HB 959 (S.L. 2025-?)", "2025-07-01", "2025-26", "K-12",
     BP, "Policies (submitted by 2026-01-01) must prohibit using, displaying or having a device on during instructional "
         "time; districts may go bell-to-bell. EdWeek counts NC as bell-to-bell."),
    ("North Dakota", BELL, "HB 1160 (2025)", "2025-04-25", "2025-26", "K-12",
     BP, "Devices (incl. smartwatches) stored and inaccessible during the school day; districts must collect data on "
         "mental health, attendance and achievement effects."),
    ("Ohio", BELL, "HB 96 (FY2026-27 budget, 2025); HB 250 (2024)", "2025-07-01", "2025-26", "K-12",
     BP, "HB 250 (2024-05-20) required district policies limiting use (2024-25). HB 96 requires policies prohibiting "
         "all use during the instructional day, adopted by 2026-01-01."),
    ("Oklahoma", BELL, "SB 139 (2025); HB 1276 (2026) made permanent", "2025-05-06", "2025-26", "K-12",
     BP, "SB 139 mandated bell-to-bell for 2025-26 only (optional thereafter); HB 1276 (spring 2026, signing date not "
         "verified) made the prohibition permanent."),
    ("Oregon", BELL, "Executive Order 25-09 (2025); ODE guidance 2024-10-30", "2025-07-02", "2025-26", "K-12",
     BP, "Districts required to adopt policies by 2025-10-31 and implement by 2026-01-01 prohibiting devices during "
         "regular instructional hours (bell-to-bell). Oct 2024 ODE guidance was a recommendation."),
    ("Pennsylvania", NONE, "Act 2024 (School Safety grant amendment, $100M for pouches, 2024-07-11); HB passed House 2026-06-01",
     "", "", "", "https://www.chalkbeat.org/philadelphia/2026/08/20/pennsylvania-still-hasnt-passed-a-school-cellphone-ban-some-philly-principals-arent-waiting/",
     "Grant funding only; a bill requiring district restrictions passed the House June 2026 but not the Senate as of "
     "Aug 2026. Philadelphia leaves policy to schools."),
    ("Rhode Island", BELL, "S 771A / H 5598 (2025)", "2025-06-23", "2026-27", "K-12",
     BP, "Policies must prohibit physical access to devices during the school day; effective 2026-08-01."),
    ("South Carolina", BELL, "FY2024-25 Appropriations Act proviso 1.103; SBE model policy", "2024-07-03", "2024-25", "K-12",
     BP, "Districts must implement SBE model policy prohibiting access during the school day to receive State Aid to "
         "Classrooms; in force from January 2025. Re-enacted in later budgets."),
    ("South Dakota", NONE, "2026 Senate bill failed in House 2026-03-05", "", "", "",
     "https://www.dakotanewsnow.com/2026/03/06/school-cell-phone-ban-voted-down-by-house-after-nearly-hour-long-debate/",
     "Governor Rhoden opposed a statewide ban; no state action."),
    ("Tennessee", INSTR, "SB 897 / HB 825 (2025)", "2025-03-28", "2025-26", "K-12",
     BP, "Policies must prohibit use during instructional time, with exceptions."),
    ("Texas", BELL, "HB 1481 (2025)", "2025-06-20", "2025-26", "K-12",
     BP, "Districts/charters must prohibit use of personal communication devices on school property during the school "
         "day. Houston ISD implemented from Aug 2025."),
    ("Utah", BELL, "SB 69 (2026); SB 178 (2025)", "2026-03-18", "2026-27", "K-12",
     BP, "SB 178 (2025-03-25) banned use during classroom hours from 2025-26 as a default LEAs could modify; SB 69 "
         "extends to the whole school day from 2026-27."),
    ("Vermont", BELL, "H.480 (Act 2025)", "2025-06-27", "2026-27", "K-12 (public and publicly funded independent schools)",
     BP, "Arrival-to-dismissal prohibition per Secretary of Education policy; also restricts school social-media use."),
    ("Virginia", BELL, "HB 1961 / SB 738 (2025); SB 108 (2026); Executive Order 33 (2024-07-09)", "2025-05-30", "2025-26",
     "K-12", BP, "EO 33 directed VDOE guidance (final Sept 2024, in force 2025-01-01). 2025 law codified bell-to-bell from "
     "2025-26; SB 108 (2026-04-06) extends to possession/use anywhere on school property bell to bell from 2026-27."),
    ("Washington", GUIDE, "OSPI superintendent guidance 2024-09-06; SSB 5346 (2026) OSPI study", "2024-09-06", "", "K-12",
     BP, "Superintendent Reykdal 'challenged' districts to restrict in-class use by 2025-26; 2026 law only directs OSPI "
         "to collect policies and report by 2027-12-15. Governor Ferguson plans a bell-to-bell bill for the 2027 session."),
    ("West Virginia", INSTR, "HB 2003 (2025)", "2025-04-29", "2025-26", "K-12",
     BP, "Devices inaccessible during instructional time; boards may go further."),
    ("Wisconsin", INSTR, "AB 2 (2025 Wisconsin Act)", "2025-10-31", "2026-27", "K-12",
     BP, "Policies prohibiting use during instructional time required by 2026-07-01."),
    ("Wyoming", REQ, "SF 35 (2026)", "2026-03-06", "2026-27", "K-12",
     "https://www.wyomingpublicmedia.org/open-spaces/2026-03-20/silos-cellphones-and-literacy-breaking-down-wyomings-new-public-ed-policies",
     "Every district board must adopt a policy on possession/use; no ban required."),
]

DISTRICTS = [
    ("Los Angeles Unified", "CA", "bell-to-bell (K-12)", "2024-06-18", "2025-02-18",
     "https://www.the74million.org/article/lausd-to-enforce-a-district-wide-cell-phone-ban-heres-what-you-need-to-know/",
     "Board vote June 2024; enforcement began 2025-02-18 (delayed from January)."),
    ("New York City DOE", "NY", "ban lifted 2015; statewide bell-to-bell from 2025-26", "2015-03-02", "2025-26",
     BP, "Citywide ban dating to the 1990s/2000s was repealed 2015-03-02 under Mayor de Blasio; NY state budget "
         "mandate restores a bell-to-bell ban from 2025-26."),
    ("Orange County Public Schools", "FL", "bell-to-bell (K-12)", "2023-08-01", "2023-24",
     "https://mynews13.com/fl/orlando/news/2023/08/02/orange-county-school-board-approves-ban-on-cell-phone-use-by-students",
     "Board approved all-day ban (incl. lunch) for the start of 2023-24, going beyond HB 379."),
    ("Clark County School District", "NV", "signal-blocking pouches in class, grades 6-12", "2024-08", "2024-25",
     "https://www.ktnv.com/ccsd-to-require-all-students-grades-6-12-to-carry-cell-phones-in-signal-blocking-pouches-non-locking-safety-electronic-devices-airplane-mode",
     "Non-locking pouches during class from 2024-25; state SB 444 (2025) followed."),
    ("District of Columbia Public Schools", "DC", "bell-to-bell (K-12)", "2025-06-06", "2025-26",
     "https://dcps.dc.gov/release/dc-public-schools-will-be-phone-free-beginning-school-year-2025-2026",
     "Middle schools and several high schools piloted earlier; Council act covers charters from 2026-27."),
    ("Houston ISD", "TX", "bell-to-bell (K-12), per HB 1481", "2025-08-01", "2025-26",
     "https://www.houstonpublicmedia.org/articles/education/2025/08/01/527760/houston-isd-announces-student-cell-phone-policy-to-comply-with-new-state-law/",
     "District policy issued to comply with the state mandate."),
    ("Montgomery County Public Schools", "MD", "bell-to-bell (K-12)", "2026-07", "2026-27",
     "https://wtop.com/maryland/2026/07/bell-to-bell-ban-on-cellphone-use-to-start-for-all-montgomery-co-students-in-upcoming-school-year/",
     "Ahead of the state's 2027-28 deadline."),
]

D21 = "https://nces.ed.gov/programs/digest/d21/tables/dt21_233.50.asp"
D23 = "https://nces.ed.gov/programs/digest/d23/tables/dt23_233.50.asp"
SPP = "https://nces.ed.gov/learn/press-release/more-half-public-school-leaders-say-cell-phones-hurt-academic-performance"
ITEM_OLD = "prohibited use of cell phones and text messaging devices during school hours"
ITEM_NEW = "prohibited non-academic use of cell phones or smartphones during school hours"

# (year, survey, share_pct, se, item, grade_level_breakdown, source_url, note)
NATIONAL = [
    ("2009-10", "NCES SSOCS 2009-10", 90.9, 0.67, ITEM_OLD, "", D23,
     "Digest of Education Statistics 2023 table 233.50 (also d21). Principal-reported; item asked only from 2009-10."),
    ("2013-14", "NCES FRSS 106 'School Safety and Discipline: 2013-14'", 75.9, 1.07, ITEM_OLD, "", D23,
     "Not SSOCS: smaller Fast Response Survey with mixed mode; Digest footnote 1 cautions on comparability."),
    ("2015-16", "NCES SSOCS 2015-16", 65.8, 1.36, ITEM_OLD, "", D23,
     "Also reported in NCES Data Point 2019-053 (65.8%); schools prohibiting phones reported more daily/weekly "
     "cyberbullying (16.4% vs 9.7%)."),
    ("2017-18", "NCES SSOCS 2017-18", 70.3, 1.30, ITEM_NEW, "", D23,
     "Wording changed in 2017-18 to 'non-academic use ... cell phones or smartphones' (Digest footnote 9)."),
    ("2019-20", "NCES SSOCS 2019-20", 76.9, 1.03, ITEM_NEW, "", D23,
     "Pandemic affected collection (Digest footnote 2). By-school-level breakdown is in Digest 2022 table 233.60 "
     "(downloaded; row not machine-extracted)."),
    ("2021-22", "NCES SSOCS 2021-22", 76.1, 0.76, ITEM_NEW, "", D23,
     "Latest SSOCS cycle in Digest 2023 table 233.50. No SSOCS was fielded for 2023-24."),
    ("2024-25", "NCES School Pulse Panel, December 2024 collection (n=1,490 schools)", 77.0, None,
     "students cannot have their cell phones during any classes (item Tech2b)",
     "elementary 86%; high/secondary 55%; schools with 1,000+ students 61% (middle not reported in release)", SPP,
     "Released 2025-02-19. Different construct from SSOCS (class time, not school hours). 38% of schools with a policy "
     "also restrict use outside class; 30% of all schools prohibit phones in all classes AND outside class "
     "(closest to bell-to-bell). 53%/72% of leaders say phones hurt academic performance/mental health."),
    ("2024-25", "NCES School Pulse Panel, December 2024 collection (n=1,490 schools)", 30.0, None,
     "prohibits phones in all classes and in out-of-class situations (meals, free periods, between periods, "
     "extracurriculars, on grounds) - derived from items Tech2b/Tech2c", "", SPP,
     "Bell-to-bell proxy from the same release."),
    ("2023-24", "NCES School Pulse Panel, 2023-24 (item on unpermitted device use)", None, None,
     "share of schools reporting 'use of cell phones ... when not permitted' had a severe/moderate negative impact "
     "on learning", "", "https://nces.ed.gov/whatsnew/press_releases/7_18_2024.asp",
     "No prohibition-share item in 2023-24 SPP; 16% reported this behaviour as a severe negative impact in 2023-24 "
     "(16% in 2022-23). Recorded as a placeholder only (share column left blank)."),
    ("2024-25", "Phones in Focus national educator survey (non-probability, ~17% of US public schools)", 60.0, None,
     "school has a bell-to-bell phone policy (educator-reported)", "HS ~50% in 2025-26 vs ~90% elementary/middle",
     "https://fordschool.umich.edu/news/2026/first-its-kind-national-educator-survey-reveals-both-promise-and-peril-school-cell-phone",
     "Not NCES; 68,000+ educator responses; convenience sample. Use only as a trend indicator."),
    ("2025-26", "Phones in Focus national educator survey (non-probability, ~17% of US public schools)", 74.0, None,
     "school has a bell-to-bell phone policy (educator-reported)", "HS ~50%; elementary/middle ~90%",
     "https://fordschool.umich.edu/news/2026/first-its-kind-national-educator-survey-reveals-both-promise-and-peril-school-cell-phone",
     "Not NCES. No NCES SPP cellphone-policy release for 2025-26 was found as of 2026-09-16."),
]

# (authors, year, country, design, sample, ban_type, outcomes, outcome_domain, headline_effect, url, causal_flag, note)
STUDIES = [
    ("Beland & Murphy", 2016, "England",
     "DiD across schools with staggered school-level bans (school survey on ban timing + NPD administrative data)",
     "91 secondary schools in Birmingham, London, Leicester, Manchester; GCSE cohorts 2001-2013",
     "school-level bans on phone possession/use", "GCSE test scores", "achievement",
     "Post-ban test scores +6.41% of a SD; gains concentrated among lowest-achieving students (~+14% SD); no effect "
     "for high achievers (published: Labour Economics 41, 61-76)",
     "https://cep.lse.ac.uk/pubs/download/dp1350.pdf", "quasi-experimental", ""),
    ("Kessel, Hardardottir & Tyrefors", 2020, "Sweden",
     "DiD replication of Beland & Murphy with school survey on ban timing (~75% response) + register data",
     "Swedish compulsory-school grade 9 schools, bans up to 2016",
     "school-level phone bans", "grade 9 test scores / GPA", "achievement",
     "No impact on student performance; 'can reject even small-sized gains' (Economics of Education Review 77, 102009)",
     "https://www.ifn.se/media/fcxcel1o/wp1288.pdf", "quasi-experimental", ""),
    ("Beneito & Vicente-Chirivella", 2022, "Spain",
     "Synthetic control (Galicia) + DiD (Galicia, Castilla-La Mancha) vs other regions",
     "Regional bans from end-2014 (CLM) / early 2015 (Galicia); PISA 2015-2017 and official bullying case counts",
     "regional government bans on phones in schools", "PISA math/science; reported bullying cases", "achievement; bullying",
     "Galicia PISA math +10.7 and science +12.7 points by 2017 (0.6-0.8 and ~0.7-1 years of learning); CLM positive but "
     "insignificant; bullying cases per 10,000 down 15-18% (ages 12-14) and 9.5-18% (15-17), no effect under 12 "
     "(Applied Economic Analysis 30(90), 153-175)",
     "https://www.emerald.com/aea/article/30/90/153/59588/Banning-mobile-phones-in-schools-evidence-from",
     "quasi-experimental", "Two treated regions only; PISA regional samples."),
    ("Abrahamsson", 2024, "Norway",
     "Event study / staggered DiD using a survey of middle schools' smartphone policies linked to administrative "
     "health, education and family registers and the national pupil survey",
     "~400+ Norwegian middle schools (grades 8-10) adopting bans at different times up to 2018",
     "school-level smartphone bans (possession/use)", "GP and specialist consultations for psychological symptoms; "
     "reported bullying; GPA; academic high-school track", "mental health; bullying; achievement",
     "Girls: fewer GP visits for psychological symptoms (about -0.2 to -0.3 visits, a sizeable share of the mean) and "
     "~60% fewer specialist mental-health visits; bullying down for both genders (girls exposed 3 years ~-46%); girls' "
     "GPA +0.08 SD and higher academic-track enrolment; effects larger for low-SES girls; no effects for boys "
     "(NHH DP 01/2024; forthcoming Journal of Human Resources per Allcott et al. 2026)",
     "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4735240", "quasi-experimental",
     "Magnitudes taken from the abstract and press summaries (Boston Globe, Marginal Revolution); the PDF could not be "
     "downloaded (NHH/SSRN hosts unreachable), so verify against the paper before citing numbers."),
    ("Goodyear, Randhawa, Adab, et al. (SMART Schools)", 2025, "England",
     "Cross-sectional comparison of schools with restrictive vs permissive recreational-phone policies (not causal)",
     "30 secondary schools (20 restrictive, 10 permissive); 1,227 pupils aged 12-15",
     "school policy prohibiting recreational phone use during the school day", "WEMWBS mental wellbeing; anxiety; "
     "depression; sleep; attainment; phone/social-media time", "mental health (well-being); achievement",
     "No difference in wellbeing: adjusted mean WEMWBS difference -0.48 (95% CI -2.05 to 1.06, p=0.62); no differences in "
     "anxiety, depression, sleep, attainment or total daily phone/social-media use; less use during school hours only "
     "(Lancet Regional Health - Europe 51, 101211)",
     "https://www.thelancet.com/journals/lanepe/article/PIIS2666-7762(25)00003-1/fulltext", "observational (null)", ""),
    ("Figlio & Ozek", 2025, "United States (Florida)",
     "DiD comparing schools with high vs low pre-ban student phone activity (Advan building-level GPS) before/after "
     "the 2023 statewide ban, within one district",
     "One anonymous large urban county district (top-10 nationally); student-level records 2021-22 to 2024-25",
     "statewide law (HB 379) enforced as district 'no-show' rule (phones silenced and out of sight all day)",
     "test scores (3x/year), disciplinary incidents, suspensions, absences", "achievement; discipline; attendance",
     "Year 1: incidents/suspensions +~25% raw, DiD +12% suspensions, in-school suspensions +~30% for Black male students, "
     "fading by year 2; year-2 test scores +0.6 percentiles overall, +1.1 percentiles on spring test (1.3 in middle/high, "
     "1.4 for boys); unexcused absences significantly reduced in both years (NBER WP 34388)",
     "https://www.nber.org/papers/w34388", "quasi-experimental", "No mental-health outcomes."),
    ("Allcott, Baron, Dee, Duckworth, Gentzkow & Jacob", 2026, "United States (national)",
     "Staggered DiD (Callaway-Sant'Anna) of Yondr lockable-pouch adoption using pouch sales records, teacher survey, "
     "GPS pings, state test scores and administrative data; pre-registered",
     "~5,000 pouch-adopting schools by 2026 among 40,000+ schools, 2019-2026",
     "lockable magnetic pouches (bell-to-bell)", "phone use; test scores; attendance; discipline; student well-being; "
     "classroom attention; perceived online bullying", "achievement; mental health (well-being); bullying; discipline",
     "Phone use sharply down (teacher-reported personal use in class 61% -> 13%); test scores ~0 on average (rules out "
     ">0.007 student SD), high-school math +0.024 SD, middle school slightly negative; suspensions +~11% in year 1 then "
     "fade; subjective well-being -0.2 SD at adoption recovering to +0.16 SD by year 2; no effect on attendance, "
     "attention or online bullying (NBER WP 35132)",
     "https://www.nber.org/papers/w35132", "quasi-experimental", ""),
    ("Lichand, Moreno-Louzada, da Costa & Gentzkow", 2026, "Brazil (Rio de Janeiro)",
     "DiD contrasting middle schools without strict pre-existing rules (treated) vs schools already strict (control) "
     "around the Aug 2023 municipal ban (school-wide from Feb 2024); principal survey + admin data",
     "Municipal system (>1,000 schools); grades 6-9", "district-wide ban on non-pedagogical phone use",
     "standardized test scores; in-school phone use", "achievement",
     "Test scores +0.06 SD in treated relative to control schools; in-school phone use fell substantially",
     "https://web.stanford.edu/~gentzkow/research/RioPhoneBans.pdf", "quasi-experimental", ""),
    ("Kohnstamm Instituut & Oberon (for Dutch Ministry OCW)", 2025, "Netherlands",
     "Descriptive monitoring: school-leader surveys and group interviews; no comparison group",
     "Secondary (VO), primary (BO) and special education schools (317 secondary and 313 primary leaders per press "
     "coverage); 12 focus groups", "national agreement: no phones in class from Jan 2024 (secondary) / 2024-25 (primary)",
     "leader-reported concentration, social climate, learning, well-being, enforcement", "well-being/climate (reported)",
     "Secondary: 75% report better concentration, 59% better social climate, 28% better learning; share seeing "
     "non-educational phone use as a problem 62% -> 29%; some teachers report more physical bullying/disruption and "
     "enforcement workload. Primary: mostly no effect; 23% see better well-being/climate",
     "https://kohnstamminstituut.nl/rapport/monitoring-landelijke-afspraak-mobiele-telefoons-en-andere-devices-in-de-klas/",
     "descriptive (not causal)", "Summary PDF from tweedekamer.nl saved locally."),
    ("OECD, PISA 2022 Results Volume II (ch. 5) and 'Managing screen time' (2024)", 2023,
     "OECD/partner countries (cross-national)", "Cross-sectional associations using PISA 2022 student/school questionnaires",
     "~690,000 15-year-olds, 81 systems", "school reports that cell phone use on premises is not allowed",
     "self-reported distraction by digital devices; in-school phone use; notification habits; performance",
     "distraction/achievement (associational)",
     "About one in three OECD students attend schools banning phones; students in ban schools less likely to report "
     "distraction, but 29-30% of them still use a phone several times a day (+21% every day/almost) so bans are often "
     "unenforced; in 9 systems bans are concentrated in lower-performing schools; in some systems banned students are "
     "less likely to turn off notifications at night. No causal claim.",
     "https://www.oecd.org/en/publications/pisa-2022-results-volume-ii_a97db61c-en.html", "observational", ""),
    ("Bottger & Zierer", 2024, "Multi-country (review)", "Rapid review + meta-analysis of 5 quantitative studies",
     "5 studies with effect sizes", "school smartphone bans", "social well-being (incl. bullying); academic performance",
     "well-being; bullying; achievement",
     "Pooled d = 0.162 (p<0.05); larger for social well-being than for achievement (Education Sciences 14(8), 906)",
     "https://www.mdpi.com/2227-7102/14/8/906", "review", ""),
    ("Campbell, Edwards, Pennell, et al.", 2024, "Multi-country (review)", "Scoping review",
     "22 studies", "school phone bans/policies", "academic outcomes; mental health and wellbeing; cyberbullying",
     "achievement; mental health; bullying",
     "Mixed: 4 studies report achievement gains (2 restricted to low-achieving/low-SES samples); as many null or negative; "
     "no consistent effect on mental health or cyberbullying (J. Psychologists and Counsellors in Schools)",
     "https://journals.sagepub.com/doi/10.1177/20556365241270394", "review", ""),
]


def write(name: str, header: list[str], rows) -> Path:
    p = OUT / name
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return p


def main() -> None:
    assert len(STATES) == 51, len(STATES)
    p1 = write("state_phone_bans.csv",
               ["state", "policy_type", "law_or_rule_citation", "date_enacted", "effective_school_year",
                "grades_covered", "source_url", "note"], STATES)
    p2 = write("district_phone_bans.csv",
               ["district", "state", "ban_type", "date_adopted", "effective", "source_url", "note"], DISTRICTS)
    p3 = write("school_phone_prohibition_national.csv",
               ["year", "survey", "share_of_schools_pct", "se", "item_wording", "grade_level_breakdown",
                "source_url", "note"],
               [(y, s, "" if v is None else v, "" if se is None else se, it, gl, u, n)
                for (y, s, v, se, it, gl, u, n) in NATIONAL])
    p4 = write("phone_ban_studies.csv",
               ["authors", "year", "country", "design", "sample", "ban_type", "outcomes", "outcome_domain",
                "headline_effect", "url", "causal_flag", "note"], STUDIES)
    from collections import Counter
    print(Counter(r[1] for r in STATES))
    for p in (p1, p2, p3, p4):
        print(p, sum(1 for _ in p.open()) - 1, "rows")


if __name__ == "__main__":
    main()
