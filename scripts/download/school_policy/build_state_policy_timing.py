"""Build state x year school accountability / testing-pressure policy timing tables, 2005-2019.

Outputs (data/compiled/school_policy/):
  state_policy_timing.csv   one row per state (50 + DC)
  state_policy_events.csv   long: one row per (state, policy, date, source_url)
  state_year_policy.csv     long: state x year 2005-2019 with 0/1 in-force indicators

Every dated cell in state_policy_timing.csv has a corresponding row in state_policy_events.csv
carrying the source URL and a note. See notes/school_policy.md for conventions and caveats.
Run:  uv run python scripts/school_policy/build_state_policy_timing.py
"""
import csv, os

ROOT = str(__import__("pathlib").Path(__file__).resolve().parents[2])
OUT = os.path.join(ROOT, "data/compiled/school_policy")
os.makedirs(OUT, exist_ok=True)

STATES = {
 "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut",
 "DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois",
 "IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts",
 "MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada",
 "NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota",
 "OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota",
 "TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia",
 "WI":"Wisconsin","WY":"Wyoming"}
FIPS = {"AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11","FL":"12","GA":"13","HI":"15",
 "ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21","LA":"22","ME":"23","MD":"24","MA":"25","MI":"26","MN":"27","MS":"28",
 "MO":"29","MT":"30","NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38","OH":"39","OK":"40","OR":"41",
 "PA":"42","RI":"44","SC":"45","SD":"46","TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53","WV":"54","WI":"55","WY":"56"}

# ----------------------------------------------------------------------------- sources
S = {
 "rttt_awards": "https://web.archive.org/web/20150905000000/https://www2.ed.gov/programs/racetothetop/awards.html",
 "rttt_wiki": "https://en.wikipedia.org/wiki/Race_to_the_Top",
 "esea_map": "https://web.archive.org/web/20150905/https://www2.ed.gov/policy/elsec/guid/esea-flexibility/map/{st}.html",
 "esea_index": "https://web.archive.org/web/20150905000000/https://www2.ed.gov/policy/elsec/guid/esea-flexibility/index.html",
 "core_waiver": "https://edsource.org/2013/duncan-grants-nclb-waiver-to-eight-california-districts/36918",
 "wa_revoke": "https://www.edweek.org/teaching-learning/nclb-waiver-loss-puts-washington-state-on-uncertain-ground/2014/04",
 "ok_revoke": "https://www.edweek.org/teaching-learning/oklahoma-loses-waiver-over-academic-standards-indiana-kansas-waivers-extended/2014/08",
 "ok_restore": "https://www.inhofe.senate.gov/newsroom/press-releases/inhofe-statement-on-extension-of-oklahomas-esea-flexibility",
 "waiver_end": "https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/federal-programs/essa/transitioning%20to%20essa.pdf",
 "cc_states_2012": "https://web.archive.org/web/20120609052048/http://www.corestandards.org/in-the-states",
 "cc_az_adopt": "https://www.edgate.com/standards/us/a-c/standard-az",
 "cc_mn_adopt": "https://education.mn.gov/mde/dse/stds/ela/052565",
 "cc_wiki_state": "https://en.wikipedia.org/wiki/Common_Core_implementation_by_state",
 "cc_wiki": "https://en.wikipedia.org/wiki/Common_Core",
 "ecs_cc_memo": "https://www.ecs.org/wp-content/uploads/State_Info_Request_Common_Core_Standards_and_Assessments.pdf",
 "achieve2013": "https://www.achieve.org/files/2013ClosingtheExpectationsGapReport.pdf",
 "ky_test": "https://www.edweek.org/teaching-learning/scores-drop-on-ky-s-common-core-aligned-tests/2012/11",
 "ny_test": "https://www.engageny.org/3-8",
 "parcc_wiki": "https://en.wikipedia.org/wiki/PARCC",
 "sbac_wiki": "https://en.wikipedia.org/wiki/Smarter_Balanced_Assessment_Consortium",
 "edweek_1617": "https://www.edweek.org/teaching-learning/which-states-were-using-parcc-or-smarter-balanced-in-2016-17",
 "edweek_1415": "https://edweek.org/ew/section/multimedia/map-common-core-2015-test-results.html",
 "edfirst2018": "https://education-first.com/wp-content/uploads/2018/02/Education-First-What-Happened-To-State-Tests-Feb-2018-1.pdf",
 "in_repeal": "https://www.npr.org/sections/thetwo-way/2014/03/24/293894857/indiana-becomes-first-state-to-back-out-of-common-core",
 "fl_rename": "https://stateimpact.npr.org/florida/2014/02/18/state-board-tweaks-standards-despite-objections/",
 "tn_repeal": "https://www.usnews.com/news/articles/2015/05/12/tennessee-gov-bill-haslam-signs-bill-removing-common-core-standards",
 "nj_replace": "https://www.njsba.org/news-publications/school-board-notes/may-10-2016-vol-xxxix-no-38/revised-academic-standards-adopted-state-board/",
 "wv_repeal": "https://wvmetronews.com/2015/12/17/state-boe-repeals-next-gencommon-core-adopts-new-academic-standards/",
 "mo_hb1490": "https://house.mo.gov/billtracking/bills141/biltxt/truly/HB1490T.htm",
 "mo_mls": "https://www.stlpr.org/education/2016-04-19/new-missouri-learning-standards-win-final-approval",
 "la_lss": "https://doe.louisiana.gov/school-system-leaders/academic-strategy/louisiana-student-standards",
 "az_repeal": "https://cronkitenews.azpbs.org/2015/10/26/arizona-education-board-reverses-common-core-adoption/",
 "kraft": "https://edworkingpapers.com/sites/default/files/ai19-169.pdf",
 "nctq2011": "https://www.nctq.org/wp-content/uploads/2025/03/State_of_the_States_Teacher_Evaluation_and_Effectiveness_Policies_NCTQ_Report.pdf",
 "nctq2015": "https://files.eric.ed.gov/fulltext/ED581451.pdf",
 "nctq2019": "https://teacherquality.nctq.org/pages/State-of-the-States-2019:-Teacher-and-Principal-Evaluation-Policy",
 "cep2010": "https://files.eric.ed.gov/fulltext/ED514155.pdf",
 "cep2012": "https://files.eric.ed.gov/fulltext/ED535957.pdf",
 "fairtest2017": "https://web.archive.org/web/20170601/http://fairtest.org/graduation-test-update-states-recently-eliminated",
 "ecs_exit2016": "https://www.ecs.org/wp-content/uploads/Info_Request_States_with_exit_exams.pdf",
 "nces2017": "https://nces.ed.gov/programs/statereform/tab2_10.asp",
 "al_exit": "https://www.apr.org/business-education/2013-11-14/alabama-high-school-graduation-exam-dropped",
 "ak_exit": "https://www.adn.com/education/article/alaska-students-who-didnt-pass-exit-exam-can-now-get-diplomas/2014/06/05/",
 "az_exit": "https://www.azpm.org/p/headlines/2015/2/20/57344-az-high-school-students-no-longer-required-to-pass-standardized-tests/",
 "ga_exit": "https://www.edweek.org/teaching-learning/georgia-enacts-new-law-retroactively-eliminating-high-school-exit-exams/2015/03",
 "ga_exit2": "https://gosa.georgia.gov/report-card-dashboards-data/report-card/contents-report-card/retired-georgia-assessments",
 "id_exit": "https://www.idahoednews.org/news/senate-committee-nixes-isat-graduation-requirement/",
 "mn_exit": "https://www.americanexperiment.org/minnesota-highest-graduation-rate-paired-with-lowest-proficiency/",
 "ms_exit": "https://msachieves.mdek12.org/high-school-students-offered-multiple-pathways-to-graduation/",
 "nv_exit": "https://lasvegassun.com/news/2013/jun/05/proficiency-exams-out-students/",
 "ok_exit": "https://okpolicy.org/new-federal-education-law-means-oklahoma-part-2/",
 "sc_exit": "https://ed.sc.gov/newsroom/high-school-exit-exam-elimination/",
 "wa_exit": "https://wapave.org/washingtons-2019-law-adjusts-graduation-requirements/",
 "ri_exit": "https://www.thewesterlysun.com/news/necap-testing-moratorium-becomes-law-in-r-i/article_a2017fd7-ae16-5f01-ac61-86335de576cc.html",
 "edweek_2023_exit": "https://www.edweek.org/teaching-learning/states-have-soured-on-the-high-school-exit-exam-heres-why/2023/01",
 "ets_optout": "https://files.eric.ed.gov/fulltext/EJ1124755.pdf",
 "fairtest_optout": "http://fairtest.org/more-500000-refused-tests-2015/",
 "edweek_optout": "https://www.edweek.org/education/education-department-asks-13-states-to-address-low-test-participation-rates/2015/12",
 "nj_optout": "http://blogs.edweek.org/edweek/parentsandthepublic/2015/04/nj_opt-out_rates_low_for_early_grades_higher_for_secondary_students.html",
 "brookings_optout": "https://www.brookings.edu/articles/who-opts-out-of-state-tests/",
}

events = []
def ev(st, policy, date, value, source, note="", conflict=""):
    events.append({"state": st, "policy": policy, "date": date, "value": value,
                   "source_url": source, "note": note, "conflict_or_alt": conflict})

# ----------------------------------------------------------------------------- 1. Race to the Top
RTTT = {"DE":(1,"2010-03"),"TN":(1,"2010-03"),
        "DC":(2,"2010-08"),"FL":(2,"2010-08"),"GA":(2,"2010-08"),"HI":(2,"2010-08"),"MD":(2,"2010-08"),"MA":(2,"2010-08"),
        "NC":(2,"2010-08"),"NY":(2,"2010-08"),"OH":(2,"2010-08"),"RI":(2,"2010-08"),
        "AZ":(3,"2011-12"),"CO":(3,"2011-12"),"IL":(3,"2011-12"),"KY":(3,"2011-12"),"LA":(3,"2011-12"),"NJ":(3,"2011-12"),"PA":(3,"2011-12")}
RTTT_DATES = {1:"2010-03-29",2:"2010-08-24",3:"2011-12-22"}
for st,(ph,d) in RTTT.items():
    ev(st,"rttt_award",RTTT_DATES[ph],f"phase {ph}",S["rttt_awards"],
       "Archived ed.gov awards page: Phase 1 announced Mar 29 2010; Phase 2 Aug 24 2010; Phase 3 Dec 22 2011. Phase 3 awards were smaller and went to Phase 2 finalists.",
       "Wikipedia gives Dec 23 2011 for Phase 3 announcement" if ph==3 else "")

# ----------------------------------------------------------------------------- 2. ESEA flexibility waivers
# (approval date as stated on the archived ed.gov state page; window = submission window)
WAIVER = {
 "AK":("2013-05-20",""),"AL":("2013-06-12","ed.gov page text says approved June 12 2013; the posted approved request is dated June 21 2013"),
 "AR":("2012-06-29",""),"AZ":("2012-07-19","placed on high-risk status 2014 over teacher evaluation"),
 "CO":("2012-02-09",""),"CT":("2012-05-29",""),"DC":("2012-07-19",""),"DE":("2012-05-29",""),"FL":("2012-02-09",""),
 "GA":("2012-02-09",""),"HI":("2013-05-20",""),"ID":("2012-09-28","ed.gov text says Sept 28 2012; posted approved request dated Oct 17 2012"),
 "IL":("2014-04-18","archived page header still says 'under review' but lists 'Approved ESEA Flexibility Request (Current) (April 18, 2014)'; Illinois was approved April 18 2014"),
 "IN":("2012-02-09",""),"KS":("2012-07-19","placed on high-risk status 2014"),"KY":("2012-02-09",""),"LA":("2012-05-29",""),
 "MA":("2012-02-09",""),"MD":("2012-05-29",""),"ME":("2013-08-12",""),"MI":("2012-07-19",""),"MN":("2012-02-09",""),
 "MO":("2012-06-29",""),"MS":("2012-07-19",""),"NC":("2012-05-29",""),"NH":("2013-06-26",""),"NJ":("2012-02-09",""),
 "NM":("2012-02-15",""),"NV":("2012-08-08",""),"NY":("2012-05-29",""),"OH":("2012-05-29",""),
 "OK":("2012-02-09","revoked Aug 28 2014 after Common Core repeal; reinstated Nov 2014"),
 "OR":("2012-07-19","placed on high-risk status 2014"),"PA":("2013-08-20",""),"RI":("2012-05-29",""),"SC":("2012-07-19",""),
 "SD":("2012-06-29",""),"TN":("2012-02-09",""),"TX":("2013-09-30",""),"UT":("2012-06-29",""),"VA":("2012-06-29",""),
 "WA":("2012-07-06","REVOKED April 24 2014 (first state to lose waiver; teacher-evaluation test-score requirement not enacted)"),
 "WI":("2012-07-06",""),"WV":("2013-05-20",""),
}
NO_WAIVER = {
 "CA":"No statewide waiver (request withdrawn/never approved). Eight CORE districts (LA, Long Beach, SF, Sacramento, Oakland, Fresno, Santa Ana, Sanger) received a district-level waiver Aug 6 2013.",
 "IA":"Never approved: ed.gov page shows request 'under review' (submitted Feb 28 2012); initially denied June 2012 because state lacked authority to require test-based teacher evaluation.",
 "MT":"Never applied / no approved request (no state page archived).",
 "NE":"Never approved: original submission March 31 2015 listed as 'under review'.",
 "ND":"Never approved: request listed as 'under review'.",
 "VT":"Never approved: request (Feb 28 2012) never approved; Vermont later declined to pursue.",
 "WY":"Never approved: request 'currently under review'.",
}
for st,(d,n) in WAIVER.items():
    ev(st,"esea_waiver_approved",d,"approved",S["esea_map"].format(st=st.lower()),n)
for st,n in NO_WAIVER.items():
    ev(st,"esea_waiver_approved","","none",S["esea_map"].format(st=st.lower()) if st!="MT" else S["esea_index"],n)
ev("CA","esea_waiver_core_districts","2013-08-06","approved (8 CORE districts only)",S["core_waiver"],"One-year district-level waiver; renewed 2014 for seven districts.")
ev("WA","esea_waiver_revoked","2014-04-24","revoked",S["wa_revoke"],"NCLB requirements (AYP, SES set-asides) returned for 2014-15.")
ev("OK","esea_waiver_revoked","2014-08-28","revoked",S["ok_revoke"],"Revoked because post-repeal PASS standards not certified college/career-ready.")
ev("OK","esea_waiver_reinstated","2014-11","reinstated",S["ok_restore"],"Reinstated Nov 2014 after state higher-ed certified PASS standards (month from press release; day not verified).")
for st in WAIVER:
    ev(st,"esea_waiver_expired","2016-08-01","void",S["waiver_end"],"ED ESSA-transition FAQ: all ESEA flexibility waivers null and void on August 1, 2016 (ESSA signed Dec 10 2015).")

# ----------------------------------------------------------------------------- 3. Common Core
# Adoption dates from archived corestandards.org "In the States" map (June 2012 capture); per-state source links in
# data/external/school_policy/corestandards_2012_adoption_dates.csv
CC_ADOPT = {}
with open(os.path.join(ROOT,"data/external/school_policy/corestandards_2012_adoption_dates.csv")) as f:
    import datetime
    name2st = {v:k for k,v in STATES.items()}
    for r in csv.DictReader(f):
        if r["state"] not in name2st: continue
        d = datetime.datetime.strptime(r["adopted_date_text"], "%B %d, %Y")
        CC_ADOPT[name2st[r["state"]]] = (d.strftime("%Y-%m-%d"), r["source_href"])
for st,(d,href) in CC_ADOPT.items():
    conflict = ""
    if st=="WY":
        conflict = "corestandards.org map lists 'June 16, 2010' but Wyoming's State Board adopted CCSS in June 2012 (Wikipedia: 'Wyoming adopted last, in 2012'); 2012-06 used in the state table."
    ev(st,"common_core_adopted",d,"adopted (ELA+math)",S["cc_states_2012"],f"State-board/agency source linked from corestandards.org: {href}",conflict)
CC_ADOPT["AZ"] = ("2010-06-28", S["cc_az_adopt"]); ev("AZ","common_core_adopted","2010-06-28","adopted (ELA+math)",S["cc_az_adopt"],"Arizona State Board of Education vote June 28 2010; not on the archived corestandards map capture.")
CC_ADOPT["MN"] = ("2010", S["cc_mn_adopt"]); ev("MN","common_core_adopted","2010","adopted (ELA only)",S["cc_mn_adopt"],"Minnesota adopted CCSS for ELA only (2010 Minnesota Academic Standards in ELA, effective 2012-13); kept own 2007 math standards. Month not verified.")
for st,n in {"AK":"never adopted (own Alaska standards 2012)","NE":"never adopted","TX":"never adopted","VA":"never adopted (SOL retained)"}.items():
    ev(st,"common_core_adopted","","not adopted",S["ecs_cc_memo"],n)

# Full K-12 implementation school year (both ELA and math K-12) per Achieve, Closing the Expectations Gap 2013, p.39 table.
CC_IMPL = {"AL":"2013-14","AK":"","AZ":"2013-14","AR":"2013-14","CA":"2014-15","CO":"2013-14","CT":"2013-14","DE":"2012-13",
 "DC":"2012-13","FL":"2013-14","GA":"2014-15","HI":"2013-14","ID":"2013-14","IL":"2013-14","IN":"2013-14","IA":"2014-15",
 "KS":"2013-14","KY":"2011-12","LA":"2013-14","ME":"2012-13","MD":"2013-14","MA":"2013-14","MI":"2012-13","MN":"2012-13",
 "MS":"2013-14","MO":"2014-15","MT":"2013-14","NE":"","NV":"2012-13","NH":"2014-15","NJ":"2013-14","NM":"2013-14","NY":"2013-14",
 "NC":"2012-13","ND":"2013-14","OH":"2013-14","OK":"2014-15","OR":"2014-15","PA":"2013-14","RI":"2013-14","SC":"2013-14",
 "SD":"2014-15","TN":"2013-14","TX":"","UT":"2013-14","VT":"2013-14","VA":"","WA":"2014-15","WV":"2014-15","WI":"2014-15","WY":"2014-15"}
CC_IMPL_NOTE = {"AL":"math K-12 2012-13, ELA K-12 2013-14","DC":"ELA K-12 2011-12, math K-12 2012-13","GA":"ELA K-12 2012-13; math phased to K-12 by 2014-15",
 "MN":"ELA only (math = state standards 2010-11)","IN":"planned; Indiana paused CCSS May 2013 and replaced Apr 2014","OK":"planned; repealed June 2014 before full implementation",
 "NJ":"ELA K-12 2012-13, math K-12 2013-14","IA":"9-12 in 2012-13, K-12 in 2014-15"}
for st,y in CC_IMPL.items():
    if y: ev(st,"common_core_full_implementation_sy",y,"full K-12 implementation (ELA+math)",S["achieve2013"],"Achieve 2013 survey of state-reported timelines (p.39). "+CC_IMPL_NOTE.get(st,""))

# First spring administration of an operational statewide CCSS-aligned test; consortium; exits.
# (year, consortium_2010_membership -> test used spring 2015, test name, note, source)
CC_TEST = {
 "AL":(2014,"PARCC->own","ACT Aspire (gr 3-8, 2014); ACT (HS)","Left PARCC Feb 2013; Achieve: CCSS-aligned 3-8 test in 2013-14.",S["parcc_wiki"]),
 "AK":("", "SBAC affiliate (2013)->own","AMP (2015, Alaska standards)","Never adopted CCSS; no CCSS-aligned test.",S["sbac_wiki"]),
 "AZ":(2015,"PARCC->own","AzMERIT (2015)","Left PARCC May 2014.",S["parcc_wiki"]),
 "AR":(2015,"PARCC->own","PARCC (2015 only); ACT Aspire 2016-","Left PARCC July 2015 after one administration.",S["parcc_wiki"]),
 "CA":(2015,"SBAC","Smarter Balanced/CAASPP (2015; 2014 field test)","",S["sbac_wiki"]),
 "CO":(2015,"PARCC","PARCC/CMAS (2015-2017); CMAS with PARCC items after","Used PARCC through 2017; 2018+ state-owned CMAS (exit date not verified).",S["edweek_1617"]),
 "CT":(2015,"SBAC","Smarter Balanced (2015)","",S["sbac_wiki"]),
 "DE":(2015,"SBAC","Smarter Balanced (2015)","",S["sbac_wiki"]),
 "DC":(2013,"PARCC","DC CAS aligned to CCSS (2013, Achieve p.43); PARCC 2015-2023","Achieve: 'administering a CCSS-aligned assessment in grades 3-8 and high school in 2012-13'.",S["achieve2013"]),
 "FL":(2015,"PARCC->own","Florida Standards Assessments (2015)","Left PARCC Sept 2013.",S["parcc_wiki"]),
 "GA":(2015,"PARCC->own","Georgia Milestones (2015)","Left PARCC July 2013.",S["parcc_wiki"]),
 "HI":(2015,"SBAC","Smarter Balanced (2015)","",S["sbac_wiki"]),
 "ID":(2015,"SBAC","Smarter Balanced/ISAT 2.0 (2015; 2014 field test statewide)","",S["achieve2013"]),
 "IL":(2015,"PARCC","PARCC (2015-2018); IAR 2019","Achieve: transitional CCSS items on ISAT in 2014. Left PARCC Mar 2019 (IAR keeps PARCC items).",S["parcc_wiki"]),
 "IN":("", "PARCC->own","ISTEP+ re-aligned to Indiana Academic Standards (2015)","CCSS repealed Mar 2014 before any CCSS-aligned operational test; left PARCC June 2014.",S["parcc_wiki"]),
 "IA":(2019,"SBAC affiliate->own","Iowa Assessments (not aligned) until ISASP 2019","Iowa never administered a consortium test; ISASP (2019) first Iowa Core-aligned test.",S["edfirst2018"]),
 "KS":(2015,"SBAC->own","Kansas Assessment Program (2015, KU-built)","Withdrew from SBAC Dec 2013.",S["cc_wiki_state"]),
 "KY":(2012,"PARCC->own","K-PREP (2012)","First state with fully CCSS-aligned tests, spring 2012. Left PARCC Jan 2014.",S["ky_test"]),
 "LA":(2015,"PARCC","PARCC (2015); LEAP 2025 hybrid with PARCC items after","Governor EO June 2014 to exit; still administered PARCC-based test 2015; hybrid thereafter.",S["edweek_1617"]),
 "ME":(2015,"SBAC->own","Smarter Balanced (2015 only); eMPowerME 2016","Withdrew from SBAC 2015.",S["cc_wiki_state"]),
 "MD":(2015,"PARCC","PARCC (2015-2018); MCAP 2019","Left PARCC Sept 2018.",S["parcc_wiki"]),
 "MA":(2015,"PARCC (district choice)","PARCC or legacy MCAS by district (2015-16); Next-Gen MCAS statewide 2017","Delayed decision Nov 2013; 2015-16 district choice; hybrid MCAS with PARCC items from 2017.",S["edweek_1617"]),
 "MI":(2015,"SBAC (blended)","M-STEP with Smarter Balanced items (2015)","",S["edweek_1617"]),
 "MN":(2013,"none","MCA-III reading aligned to 2010 ELA standards (2013)","ELA only; Achieve p.43: CCSS-aligned reading assessment gr 3-8 and 10 in 2012-13.",S["achieve2013"]),
 "MS":(2015,"PARCC->own","PARCC (2015 only); MAP 2016","Board voted Jan 16 2015 to withdraw; PARCC still given spring 2015.",S["parcc_wiki"]),
 "MO":(2015,"SBAC->own","Smarter Balanced (2015 only); MAP (own) 2016","Legislature barred SBAC use after 2015.",S["cc_wiki_state"]),
 "MT":(2015,"SBAC","Smarter Balanced (2015; 2014 field test)","",S["sbac_wiki"]),
 "NE":("", "none","NeSA (state standards)","Never adopted CCSS.",S["ecs_cc_memo"]),
 "NV":(2015,"SBAC","Smarter Balanced (2015)","",S["sbac_wiki"]),
 "NH":(2015,"SBAC->own","Smarter Balanced (2015-2017); NH SAS 2018","",S["sbac_wiki"]),
 "NJ":(2015,"PARCC","PARCC (2015-2018); NJSLA 2019","Left PARCC Feb 2019.",S["parcc_wiki"]),
 "NM":(2015,"PARCC","PARCC (2015-2018)","Left PARCC Jan 2019.",S["parcc_wiki"]),
 "NY":(2013,"PARCC (member, never used)","NY State 3-8 tests re-aligned to CCSS (April 2013); Regents Common Core Algebra I/ELA 2014","Piloted PARCC in 25 schools 2015; never adopted.",S["ny_test"]),
 "NC":(2013,"SBAC affiliate->own","READY EOG/EOC aligned to CCSS (2013)","Achieve p.43: CCSS-aligned assessment gr 3-8 and HS in 2012-13.",S["achieve2013"]),
 "ND":(2015,"SBAC","Smarter Balanced (2015)","Left PARCC July 2013 (was dual member).",S["sbac_wiki"]),
 "OH":(2015,"PARCC->own","PARCC (2015 only); AIR-built Ohio State Tests 2016","Dropped PARCC June 30 2015.",S["parcc_wiki"]),
 "OK":("", "PARCC->own","OCCT aligned to PASS standards","Left PARCC July 2013; CCSS repealed June 2014 before any aligned test.",S["parcc_wiki"]),
 "OR":(2015,"SBAC","Smarter Balanced (2015)","",S["sbac_wiki"]),
 "PA":(2015,"PARCC->own","PSSA aligned to PA Core (2015); Keystone Exams (2013)","Left PARCC Mar 2014; PA Core = CCSS-based rebrand.",S["parcc_wiki"]),
 "RI":(2015,"PARCC->own","PARCC (2015-2017); RICAS (MA-based) 2018","Left PARCC Apr 2017.",S["parcc_wiki"]),
 "SC":(2015,"SBAC->own","ACT Aspire (2015, CCSS-aligned); SC READY 2016 (SC CCR standards)","Withdrew from SBAC 2014; CCSS replaced for 2015-16.",S["cc_wiki_state"]),
 "SD":(2015,"SBAC","Smarter Balanced (2015; 2014 field test)","",S["sbac_wiki"]),
 "TN":(2017,"PARCC->own","TNReady (2016 administration largely failed/cancelled; first complete 2017)","Left PARCC June 2014; 2016 online failure - grades 3-8 cancelled; standards replaced 2017-18.",S["parcc_wiki"]),
 "TX":("", "none","STAAR (TEKS)","Never adopted CCSS.",S["ecs_cc_memo"]),
 "UT":(2014,"SBAC->own","SAGE (2014)","Withdrew from SBAC Aug 2012.",S["cc_wiki_state"]),
 "VT":(2015,"SBAC","Smarter Balanced (2015)","",S["sbac_wiki"]),
 "VA":("", "none","SOL","Never adopted CCSS.",S["ecs_cc_memo"]),
 "WA":(2015,"SBAC","Smarter Balanced (2015)","",S["sbac_wiki"]),
 "WV":(2015,"SBAC->own","Smarter Balanced (2015-2017); WV General Summative 2018","",S["sbac_wiki"]),
 "WI":(2015,"SBAC->own","Badger Exam/Smarter Balanced (2015 only); Forward Exam 2016","",S["sbac_wiki"]),
 "WY":(2015,"SBAC affiliate->own","PAWS re-aligned (2015; UNVERIFIED)","Year of first CCSS-aligned PAWS not verified.",S["edfirst2018"]),
}
for st,(y,cons,test,note,src) in CC_TEST.items():
    ev(st,"common_core_aligned_test_first_year",str(y) if y else "", test, src, note+" Consortium path: "+cons)
# PARCC exit dates (Wikipedia PARCC 'Test participation by states' table; month-level)
PARCC_EXIT = {"AL":"2013-02","AZ":"2014-05","AR":"2015-07","FL":"2013-09","GA":"2013-07","IL":"2019-03","IN":"2014-06","KY":"2014-01",
 "MD":"2018-09","MS":"2015-01","NJ":"2019-02","NM":"2019-01","ND":"2013-07","OH":"2015-06","OK":"2013-07","PA":"2014-03","RI":"2017-04","TN":"2014-06"}
for st,d in PARCC_EXIT.items():
    ev(st,"parcc_exit",d,"left PARCC",S["parcc_wiki"],"Wikipedia PARCC participation table (secondary source; month-level).")
SBAC_EXIT = {"UT":("2012-08",S["cc_wiki_state"]),"KS":("2013-12",S["cc_wiki_state"]),"SC":("2014",S["cc_wiki_state"]),"ME":("2015",S["cc_wiki_state"]),
 "MO":("2015",S["cc_wiki_state"]),"WI":("2015",S["edfirst2018"]),"NH":("2018",S["edfirst2018"]),"WV":("2018",S["edfirst2018"])}
for st,(d,src) in SBAC_EXIT.items():
    ev(st,"sbac_exit",d,"left/stopped using Smarter Balanced",src,"Secondary source; year-level unless month given.")

# Repeal / replace / rename events
CC_REPEAL = {
 "IN":("2014-03-24","repeal","Gov. Pence signed SB 91 voiding CCSS; Indiana Academic Standards adopted Apr 2014 (widely judged similar).",S["in_repeal"]),
 "OK":("2014-06-05","repeal","HB 3399 signed; reverted to PASS standards; new Oklahoma Academic Standards 2016.",S["cc_wiki_state"]),
 "SC":("2014-06","repeal","Act 200 (H.3893) signed June 2014 requiring replacement standards for 2015-16 (SC College- and Career-Ready Standards adopted Mar 2015).",S["cc_wiki_state"]),
 "MO":("2014-07-14","repeal_review_law","HB 1490 signed 2014 requiring new standards; Missouri Learning Standards adopted Apr 19 2016, implemented 2016-17.",S["mo_hb1490"]),
 "TN":("2015-05-11","repeal_review_law","Law signed May 2015 requiring review/replacement; Tennessee Academic Standards implemented 2017-18.",S["tn_repeal"]),
 "WV":("2015-12-17","repeal_replace","State BOE repealed 'Next Generation' (CCSS) standards; WV College- and Career-Readiness Standards effective July 2016.",S["wv_repeal"]),
 "AZ":("2015-10-26","repeal_vote","State Board voted 6-2 to rescind 2010 adoption; standards remained in use until new Arizona standards adopted Dec 2016 (implemented 2018-19). Renamed 'AZ College and Career Ready Standards' by executive order 2013.",S["az_repeal"]),
 "LA":("2016-03","replace","BESE adopted Louisiana Student Standards (CCSS revision) by Mar 4 2016 per 2015 Act; implemented 2016-17.",S["la_lss"]),
 "NJ":("2016-05","replace","State Board adopted New Jersey Student Learning Standards (minor CCSS revision), effective 2017-18.",S["nj_replace"]),
 "FL":("2014-02-18","rename","State Board adopted 'Florida Standards' (CCSS plus additions, e.g., cursive); HB 7031 removed 'Common Core' from statute. B.E.S.T. standards replaced them 2020.",S["fl_rename"]),
 "GA":("2015-02-19","rename","Renamed 'Georgia Standards of Excellence' with revisions.",S["cc_wiki_state"]),
 "AL":("2013-11","rename","State Board rescinded CCSS MOU Nov 2013 but kept standards as 'Alabama College- and Career-Ready Standards'.",S["cc_wiki_state"]),
 "KY":("2017-02","review_law","SB 1 (2017) required review; new Kentucky Academic Standards 2019.",S["ecs_cc_memo"]),
}
for st,(d,typ,n,src) in CC_REPEAL.items():
    ev(st,"common_core_repeal_or_replace",d,typ,src,n)

# ----------------------------------------------------------------------------- 4. Teacher evaluation
# Kraft, Brunner, Dougherty & Schwegman (2020, JPubE; EdWorkingPaper 19-169) Appendix Table A1: year state passed
# high-stakes evaluation reform (student growth/test scores required) and year implemented statewide.
TEVAL = {"AL":(2013,2016),"AK":(2012,2016),"AZ":(2010,2013),"AR":(2011,2014),"CA":("",""),"CO":(2010,2013),"CT":(2012,2014),
 "DE":(2010,2012),"FL":(2011,2011),"GA":(2012,2014),"HI":(2010,2013),"ID":(2011,2014),"IL":(2010,2016),"IN":(2011,2014),"IA":("",""),
 "KS":(2012,2014),"KY":(2013,2014),"LA":(2010,2012),"ME":(2012,2016),"MD":(2010,2013),"MA":(2011,2013),"MI":(2010,2011),
 "MN":(2011,2014),"MS":(2012,2014),"MO":(2011,2013),"MT":("",""),"NE":(2012,""),"NV":(2011,2015),"NH":(2013,2016),"NJ":(2012,2013),
 "NM":(2011,2013),"NY":(2010,2012),"NC":(2010,2011),"ND":(2011,2015),"OH":(2011,2013),"OK":(2010,2013),"OR":(2011,2013),
 "PA":(2012,2013),"RI":(2010,2012),"SC":(2013,2014),"SD":(2010,2015),"TN":(2010,2011),"TX":(2013,2016),"UT":(2012,2015),
 "VT":("",""),"VA":(2011,2012),"WA":(2012,2015),"WV":(2011,2013),"WI":(2012,2014),"WY":(2012,""),
 "DC":(2009,2009)}
NCTQ2011_SIGNIFICANT = ["AZ","CO","DE","DC","FL","ID","IL","IN","LA","MD","MI","MN","NV","NY","OH","OK","RI","TN"]
NCTQ2015_NONE = ["CA","IA","MT","NE","VT"]; NCTQ2015_WAIVER_ONLY = ["AL","NH","TX"]
NCTQ2019_DROPPED = ["AK","AR","KS","KY","ME","NM","NC","OK","WI","WY","DC"]
for st,(p,i) in TEVAL.items():
    if st=="DC":
        ev(st,"teacher_eval_test_based_law_year","2009","DCPS IMPACT (district-level; not state law)",S["nctq2011"],"NCTQ 2011 treats DCPS IMPACT (launched 2009-10) as the DC policy; OSSE has no statewide requirement. Not in Kraft et al. Table A1.")
        ev(st,"teacher_eval_implemented_year","2009","DCPS IMPACT first ratings 2009-10",S["nctq2011"],"")
        continue
    ev(st,"teacher_eval_test_based_law_year",str(p) if p else "","passed" if p else "no state policy (as of 2016)",S["kraft"],
       "Kraft et al. Table A1 'Pass Evaluation' = year state adopted a law/regulation requiring student growth/test-based measures in teacher evaluations."
       + (" NCTQ 2011: evaluations 'significantly' informed by growth." if st in NCTQ2011_SIGNIFICANT else "")
       + (" NCTQ 2015: no formal state policy requiring objective student-achievement measures." if st in NCTQ2015_NONE else "")
       + (" NCTQ 2015: policy exists only in ESEA waiver request." if st in NCTQ2015_WAIVER_ONLY else ""))
    ev(st,"teacher_eval_implemented_year",str(i) if i else "","implemented statewide" if i else "not implemented by 2016",S["kraft"],
       "Kraft et al. Table A1 'Implement Evaluation' = first year new evaluations were implemented statewide."
       + (" NCTQ 2019: state dropped the student-growth requirement between 2015 and 2019 (exact year not captured)." if st in NCTQ2019_DROPPED else ""))

# ----------------------------------------------------------------------------- 5. High school exit exams
# (exam_for_class_of_2010 [1/0], first_year_in_force, last_year_in_force (class year), dropped_year, note, sources)
EXIT = {
 "AL":(1,2001,2013,2014,"AHSGE; State Board voted Nov 2013 to drop requirement for first-time 9th graders of 2010-11 onward (=class of 2014+). Earlier 2009 board vote had planned phase-out after class of 2015.",[S["cep2010"],S["al_exit"]]),
 "AK":(1,2004,2014,2014,"HSGQE repealed by HB 278 effective July 1 2014 with retroactive diplomas; class of 2014 nominally still subject during the school year.",[S["cep2010"],S["ak_exit"]]),
 "AZ":(1,2006,2014,2015,"AIMS requirement repealed by law signed Feb 20 2015, effective immediately (class of 2015 not required).",[S["cep2010"],S["az_exit"]]),
 "AR":(1,2010,2014,2015,"Algebra I EOC with remediation requirement counted by CEP as exit exam from class of 2010. Not among ECS's 17 exit-exam states for class of 2016; FairTest 2017 'recently ended'. Drop year 2015 approximate/UNVERIFIED.",[S["cep2010"],S["ecs_exit2016"],S["fairtest2017"]]),
 "CA":(1,2006,2014,2015,"CAHSEE: 2015 administration cancelled; SB 725 (Aug 2015) exempted class of 2015; SB 172 (Oct 2015) suspended requirement for classes of 2016-2018; retroactive diplomas to 2006; permanently repealed 2017.",[S["cep2010"],S["ecs_exit2016"],S["fairtest2017"]]),
 "CO":(0,"","","","No exit exam; graduation 'minimum metric' first for class of 2021.",[S["ecs_exit2016"]]),
 "CT":(0,"","","","No exit exam in force; EOC requirement planned for class of 2018 then 2021, never enforced.",[S["cep2010"],S["ecs_exit2016"]]),
 "DE":(0,"","","","",[S["cep2010"]]),"DC":(0,"","","","",[S["cep2010"]]),
 "FL":(1,2003,2019,"","FCAT reading then grade-10 FSA ELA + Algebra I EOC; still required through 2019 (and 2023).",[S["cep2010"],S["edweek_2023_exit"]]),
 "GA":(1,1994,2014,2015,"GHSGT not administered to students entering 9th grade after July 1 2011 (class of 2015 first not required; board transition plan Apr 13 2011); HB 91 (Mar 2015) retroactively eliminated requirement.",[S["cep2010"],S["ga_exit"],S["ga_exit2"]]),
 "HI":(0,"","","","",[S["cep2010"]]),
 "ID":(1,2006,2016,2017,"ISAT 10th-grade requirement; ECS lists ID as exit-exam state for class of 2016; State Board rule removed requirement for class of 2017 onward (legislative committee Jan 2017).",[S["cep2010"],S["ecs_exit2016"],S["id_exit"]]),
 "IL":(0,"","","","",[S["cep2010"]]),
 "IN":(1,2000,2019,"","GQE then Algebra I/English 10 ECAs (class of 2012+), ISTEP+ grade 10 (classes 2019-2022); graduation pathways from class of 2023.",[S["cep2010"],S["nces2017"]]),
 "IA":(0,"","","","",[S["cep2010"]]),"KS":(0,"","","","",[S["cep2010"]]),"KY":(0,"","","","",[S["cep2010"]]),
 "LA":(1,2003,2019,"","GEE then EOC (class of 2014+); still required.",[S["cep2010"],S["edweek_2023_exit"]]),
 "ME":(0,"","","","",[S["cep2010"]]),
 "MD":(1,2009,2019,"","HSA/EOC (English, algebra, biology, government) still required through 2019.",[S["cep2010"],S["nces2017"]]),
 "MA":(1,2003,2019,"","MCAS ELA/math (+science from class of 2010); required through 2019 (voters ended it Nov 2024).",[S["cep2010"],S["edweek_2023_exit"]]),
 "MI":(0,"","","","",[S["cep2010"]]),
 "MN":(1,2010,2012,2013,"GRAD reading/writing/math (diplomas first withheld class of 2010); 2013 legislature eliminated the GRAD requirement.",[S["cep2010"],S["mn_exit"],S["fairtest2017"]]),
 "MS":(1,2006,2016,2017,"SATP2 EOCs; 2014 board policy added alternate routes; ECS: from 2016-17 students must take but not pass EOCs (scores = 25% of grade). NCES 2017 says 'through class of 2018' (conflict).",[S["cep2010"],S["ecs_exit2016"],S["ms_exit"],S["nces2017"]]),
 "MO":(0,"","","","",[S["cep2010"]]),"MT":(0,"","","","",[S["cep2010"]]),"NE":(0,"","","","",[S["cep2010"]]),
 "NV":(1,2003,2016,2017,"HSPE; AB 288 (2013) replaced with EOCs; class of 2016 last required to pass HSPE; classes 2017-18 take-but-not-pass; EOC pass requirement later repealed.",[S["cep2010"],S["nv_exit"],S["ecs_exit2016"]]),
 "NH":(0,"","","","",[S["cep2010"]]),
 "NJ":(1,2003,2019,"","HSPA through class of 2015; PARCC/alternative-assessment requirement after; still required.",[S["cep2010"],S["ecs_exit2016"]]),
 "NM":(1,1990,2019,"","NMHSCE then SBA/HSGA (class of 2011+) then PARCC-based; requirement ended for students graduating 2024.",[S["cep2010"],S["edweek_2023_exit"]]),
 "NY":(1,2000,2019,"","Regents exams; still required.",[S["cep2010"],S["edweek_2023_exit"]]),
 "NC":(1,2010,2010,2011,"Competency EOC requirement eliminated beginning with class of 2011 (EOCs count 25% of course grade).",[S["cep2010"]]),
 "ND":(0,"","","","",[S["cep2010"]]),
 "OH":(1,2007,2019,"","OGT through class of 2017; EOC-points/alternative pathways from class of 2018; test-based requirement continued through 2019.",[S["cep2010"],S["nces2017"]]),
 "OK":(1,2012,2016,2017,"EOI requirement first for class of 2012 (not yet in force for class of 2010); HB 3218 (2016) eliminated EOIs from 2016-17 (class of 2017 not required).",[S["cep2010"],S["ok_exit"]]),
 "OR":(1,2012,2019,"","Essential Skills requirement (reading class of 2012; writing 2013; math 2014) met via OAKS/Smarter Balanced or alternatives; not in force for class of 2010; suspended 2021 onward.",[S["cep2010"],S["fairtest2017"]]),
 "PA":(0,"","","","Keystone requirement planned for class of 2017, delayed (Act 1 of 2016, Act 6 of 2017) and replaced by pathways (Act 158 of 2018, class of 2023); never in force 2010-2019.",[S["ecs_exit2016"],S["fairtest2017"]]),
 "RI":(0,"","","","NECAP requirement planned for class of 2014; 2014 law imposed moratorium to 2017; requirement dropped; never in force.",[S["cep2010"],S["ri_exit"],S["fairtest2017"]]),
 "SC":(1,2006,2014,2015,"HSAP; Act 155 signed Apr 14 2014: beginning with class of 2015 not required (retroactive to 1990).",[S["cep2010"],S["sc_exit"]]),
 "SD":(0,"","","","",[S["cep2010"]]),
 "TN":(1,2005,2011,2012,"Gateway exams sunset with class of 2012 (replaced by EOCs counted in grades).",[S["cep2010"]]),
 "TX":(1,2005,2019,"","TAKS then STAAR EOCs (reduced from 15 to 5 in 2013); still required.",[S["cep2010"],S["edweek_2023_exit"]]),
 "UT":(0,"","","","",[S["cep2010"]]),"VT":(0,"","","","",[S["cep2010"]]),
 "VA":(1,2004,2019,"","SOL verified credits; still required.",[S["cep2010"],S["edweek_2023_exit"]]),
 "WA":(1,2008,2019,2020,"WASL required from class of 2008; HSPE from class of 2011 (CEP 'current exam' date); HB 1599 (2019) delinked tests from graduation beginning class of 2020.",[S["cep2010"],S["wa_exit"]]),
 "WV":(0,"","","","",[S["cep2010"]]),"WI":(0,"","","","",[S["cep2010"]]),"WY":(0,"","","","",[S["cep2010"]]),
}
# Predecessor exit exams in force before the "current exam" listed by CEP (CEP 2010 Table 1, 'Prior Exit Exam Being Phased Out'
# column, plus CEP's exit-exam series). Approximate first class; used only so the 2005-2009 indicator is not understated.
PRIOR_EXAM = {"AL":1985,"FL":1983,"GA":1985,"IN":2000,"LA":1991,"MD":1990,"MN":2000,"MS":2000,"NV":1994,"NJ":1994,"NM":1990,
              "NY":1979,"NC":1980,"OH":1994,"SC":1990,"TN":1990,"TX":1994,"VA":1994}
for st,y in PRIOR_EXAM.items():
    ev(st,"hs_exit_exam_prior_exam","%d (approx.)"%y,"predecessor exit exam in force before the 2009-10 'current exam'",S["cep2010"],
       "CEP 2010 Table 1 'Prior Exit Exam Being Phased Out' column; first affected class approximate. Ensures exit_exam_in_force=1 in 2005-2009 for these states.")
for st,(c10,f,l,d,n,srcs) in EXIT.items():
    ev(st,"hs_exit_exam_class_of_2010","2010","required" if c10 else "not required",srcs[0],
       "CEP 2010 Table 1 (Major Characteristics of State Exit Exams 2009-10): year diplomas first withheld. "+n)
    if d: ev(st,"hs_exit_exam_dropped",str(d),f"first class not required = {d}",srcs[-1],n)

# ----------------------------------------------------------------------------- 6. Opt-out 2015
OPTOUT = {  # pct = share of eligible students not tested (grades 3-8 unless noted)
 "NY":(20.0,"240,000","NYSED: 20% of eligible grades 3-8 students not tested 2015",S["ets_optout"]),
 "CO":(11.0,"100,000","CDE: median nonparticipation across grades 11% ELA / 10% math; 7-12 ranged 50-89% participation",S["ets_optout"]),
 "RI":(12.0,"10,300","RIDE: 12% ELA / 10% math nonparticipation",S["ets_optout"]),
 "NJ":(4.6,"130,000","NJDOE: refusal rate 4.6% grades 3-8 (higher in HS; up to 14% overall reported)",S["nj_optout"]),
 "WA":("","50,000+","count only (FairTest)",S["fairtest_optout"]),"IL":("","44,000","count only",S["fairtest_optout"]),
 "CA":("","20,386","count only; ED letter says ~97% statewide participation",S["fairtest_optout"]),"OR":("","~20,000","count only",S["fairtest_optout"]),
 "FL":("","20,000","count only (FairTest lists 20,000 and 2,200)",S["fairtest_optout"]),"CT":("","11,200","count only",S["fairtest_optout"]),
 "NM":("","10,000","count only",S["fairtest_optout"]),"WI":("","8,100","count only",S["fairtest_optout"]),"LA":("","~5,000","count only",S["fairtest_optout"]),
 "PA":("","4,600","count only",S["fairtest_optout"]),
}
ED_LETTER_2015 = ["CA","CO","CT","DE","ID","IL","ME","NY","NC","OR","RI","WA","WI"]
for st,(p,c,n,src) in OPTOUT.items():
    ev(st,"optout_2015",'2015-spring',f"pct={p}; count={c}",src,n)
for st in ED_LETTER_2015:
    ev(st,"ed_participation_letter_2015","2015-12","below 95% participation (statewide or districts/subgroups)",S["edweek_optout"],"ED sent letters to 13 states in Dec 2015.")

# ----------------------------------------------------------------------------- state table
rows = []
for st in STATES:
    r = {"state":st,"state_name":STATES[st],"fips":FIPS[st]}
    r["rttt_phase"] = RTTT[st][0] if st in RTTT else "none"
    r["rttt_award_date"] = RTTT[st][1] if st in RTTT else ""
    r["esea_waiver_approved_date"] = WAIVER[st][0][:7] if st in WAIVER else ""
    r["esea_waiver_note"] = WAIVER[st][1] if st in WAIVER else NO_WAIVER.get(st,"")
    r["esea_waiver_revoked_date"] = {"WA":"2014-04","OK":"2014-08 (reinstated 2014-11)"}.get(st,"")
    a = CC_ADOPT.get(st)
    r["common_core_adopted_date"] = ("2012-06" if st=="WY" else a[0][:7]) if a else ""
    r["common_core_adoption_scope"] = "ELA only" if st=="MN" else ("not adopted" if st in ("AK","NE","TX","VA") else "ELA+math")
    r["common_core_first_full_implementation_school_year"] = CC_IMPL[st]
    y,cons,test,note,src = CC_TEST[st]
    r["common_core_aligned_test_first_year"] = y
    r["consortium"] = cons
    r["consortium_test_spring_2015"] = test
    r["parcc_exit_date"] = PARCC_EXIT.get(st,"")
    r["sbac_exit_date"] = SBAC_EXIT.get(st,("",""))[0]
    rep = CC_REPEAL.get(st)
    r["common_core_repeal_or_replace_date"] = rep[0][:7] if rep else ""
    r["common_core_repeal_type"] = rep[1] if rep else ""
    p,i = TEVAL[st]
    r["teacher_eval_test_based_law_year"] = p; r["teacher_eval_implemented_year"] = i
    r["teacher_eval_nctq2011_significant"] = int(st in NCTQ2011_SIGNIFICANT)
    r["teacher_eval_nctq2015_status"] = "none" if st in NCTQ2015_NONE else ("waiver_only" if st in NCTQ2015_WAIVER_ONLY else "state_policy")
    r["teacher_eval_dropped_by_2019"] = int(st in NCTQ2019_DROPPED)
    c10,f,l,d,n,srcs = EXIT[st]
    r["hs_exit_exam_class_of_2010"] = c10
    r["hs_exit_exam_first_class"] = f; r["hs_exit_exam_last_class_required"] = l
    r["hs_exit_exam_prior_exam_first_class_approx"] = PRIOR_EXAM.get(st,"")
    r["hs_exit_exam_dropped_year"] = d
    o = OPTOUT.get(st)
    r["optout_2015_pct"] = o[0] if o else ""
    r["optout_2015_count"] = o[1] if o else ""
    r["ed_participation_letter_2015"] = int(st in ED_LETTER_2015)
    rows.append(r)

with open(os.path.join(OUT,"state_policy_timing.csv"),"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT,"state_policy_events.csv"),"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["state","policy","date","value","source_url","note","conflict_or_alt"]); w.writeheader(); w.writerows(events)

# ----------------------------------------------------------------------------- state x year (school year ending in `year`)
sy = []
for st in STATES:
    for year in range(2005,2020):
        d = {"state":st,"year":year}
        # RTTT: grant period from award year through 2015 (4-year grants, most with no-cost extensions into 2015)
        d["rttt_winner"] = int(st in RTTT and year >= int(RTTT[st][1][:4]) and year <= 2015)
        # Waiver: approvals in Feb-Sept 2012 cover SY 2011-12 (year 2012) onward; SY convention = spring of year
        wf = 0
        if st in WAIVER:
            ad = WAIVER[st][0]; ay = int(ad[:4]); am = int(ad[5:7])
            start = ay if am <= 9 else ay+1   # approvals Oct-Dec would start next SY (none occur)
            wf = int(start <= year <= 2016)
            if st=="WA" and year >= 2015: wf = 0      # revoked Apr 2014 -> NCLB rules back for 2014-15
            if st=="OK" and year == 2015: wf = 1      # revoked Aug 28 2014, reinstated Nov 2014
        d["waiver_in_force"] = wf
        # Common Core aligned test in force: from first aligned test year; 0 after formal repeal (IN, OK, SC)
        y = CC_TEST[st][0]
        cc = int(bool(y) and year >= int(y))
        if st=="SC" and year >= 2016: cc = 0
        d["cc_aligned_test_in_force"] = cc
        # Teacher eval: from statewide implementation year (Kraft); DC from 2010 (IMPACT 2009-10)
        i = TEVAL[st][1]
        d["teacher_eval_test_based_in_force"] = int(bool(i) and year >= int(i))
        # Exit exam: 1 if the class of `year` had to pass an exam
        c10,f,l,dd,n,srcs = EXIT[st]
        f_eff = min(int(f), PRIOR_EXAM.get(st, int(f))) if f else None
        d["exit_exam_in_force"] = int(bool(f) and f_eff <= year <= int(l))
        d["pressure_index"] = d["rttt_winner"]+d["waiver_in_force"]+d["cc_aligned_test_in_force"]+d["teacher_eval_test_based_in_force"]+d["exit_exam_in_force"]
        sy.append(d)
with open(os.path.join(OUT,"state_year_policy.csv"),"w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(sy[0].keys())); w.writeheader(); w.writerows(sy)
print("states",len(rows),"events",len(events),"state-years",len(sy))
