# Monitoring the Future (MTF): methods note

Compiled 2026-10-24. Scripts: `scripts/download/mtf/fetch_datavolumes.py` (acquisition), `scripts/download/mtf/parse_datavolumes.py` (PDF parser ->
`data/compiled/mtf/mtf_published_trends.csv`), `scripts/download/mtf/parse_published_papers.py` (Johnson et al. 2017 Table 1 ->
`data/compiled/mtf/mtf_johnson2017_year_effects.csv`), `scripts/analysis/31_mtf.py` (indicators, changes, co-movement; microdata pipeline),
`scripts/report/parts/mtf.py` (report section). Raw files documented in `data/external/mtf/README.md`. Literature in `data/compiled/mtf/mtf_literature.csv`.

## 1. What was asked for and what could be obtained

The Phase 2 plan (item 1.B.2) asks for (i) a student-level test of the H3 interaction homework hours x social-media hours on depressive affect and
loneliness by sex and grade, and (ii) 1991-2024 trends in homework, unstructured in-person socializing and screen hours alongside depressive affect,
loneliness and self-derogation, from the MTF public-use microdata (ICPSR/NAHDAP series 35).

Microdata: blocked. `https://www.icpsr.umich.edu/web/NAHDAP/series/35` rendered once in headless Chromium (Playwright, Chrome UA) and listed 84 studies;
every subsequent request to a study page (`/web/NAHDAP/studies/37841`), its documentation page (`/datadocumentation`) or a download URL
(`/versions/V1/download/stata?path=NAHDAP`) returned HTTP 403 with Cloudflare's "Performing security verification" page, in fresh and in persistent browser
contexts and after 40-second waits; curl and the remote WebFetch service get the same 403. Data downloads also require an ICPSR account and terms
acceptance, which were not available. The ICPSR online analysis (SDA) could not be reached for the same reason. No attempt was made to circumvent the
bot check or the login (an attempt to use a different Chromium mode was stopped by the session's permission policy). Codebooks were not obtainable either
(same host), nor from the Wayback Machine. `deepblue.lib.umich.edu` (ISR's repository, same Cloudflare configuration) and `monitoringthefuture.org`
were blocked identically; `catalog.hathitrust.org` returned 403.

Published tables: obtained for 1996-2012 (12th grade). MTF's reference volumes "Questionnaire Responses from the Nation's High School Seniors"
(one per survey year 1975-2012; the series then ended) print every item's weighted percentage distribution. Only the 1996-2012 volumes were ever posted as
PDFs (`monitoringthefuture.org/datavolumes/<year>/<year>dv.pdf`); the Internet Archive holds one capture of each (CDX query in the README) and these 17
PDFs (120.8 MB) were downloaded from `web.archive.org/web/<timestamp>id_/<url>`. The 1991-1995 volumes exist in print only. 8th/10th-grade distributions
were never published in this form; the only tabular annual series found for 8th/10th graders is Johnson et al. (2017), Table 1 (1991-2014, year effects relative
to 2008), taken from the PubMed Central XML. Also checked: ERIC (full text of the drug-use volumes 1992-2025 only), the ICPSR variable search (none indexed for
NAHDAP MTF), DataCite (used for the study list), Semantic Scholar (rate-limited), publisher sites (SAGE and Wiley 403; APA PsycNet JS-only; Nature paywalled).

## 2. The data volumes and the parser

Layout (identical 1996-2012): for each questionnaire item a question line (`E13: About how many hours do you spend in an average week on all your homework
...`), one line per response option with one weighted percentage per column (Total; Sex M/F; Race White/Black; Region NE/NC/S/W; College plans Yes/No;
lifetime illicit drug use None / Marijuana only / Few pills / More pills / Any heroin; 16 columns in every year parsed), and a trailer
`Item <reference number> Subject <codes> N <weighted N answering per column>`. The item reference number is permanent across years (the volumes' cross-time
index is organised by it), so series are matched on it rather than on form/question position, which changes. Items on several forms (independent random
sixths of the sample) are kept separately in the compiled file and pooled in the analysis weighting by N. `-` = 0.0, `*` = less than 0.05 percent (both 0.0).
Validation: every parsed distribution sums to 100 +/- 0.2 (1,078 item x form distributions in 1996); 870-890 items per volume. Form 1 question numbers have
three digits (A001), which the first parser version missed; fixed. The 2007-2009 PDFs are image-heavier (11-15 MB) but extract as text.

Items used (reference number: wording; response options; indicator):
- 7640 homework: "About how many hours do you spend in an average week on all your homework including both in school and out of school?" 0 / 1-4 / 5-9 / 10-14 /
  15-19 / 20-24 / 25+ hours; mean of midpoints (0, 2.5, 7, 12, 17, 22, 27.5) and % 10+ hours. Form 2 (one sixth of the sample).
- 620 evenings out (core, all forms): "During a typical week, on how many evenings do you go out for fun and recreation?" less than one / one / two / three /
  four or five / six or seven; mean of midpoints (0.5, 1, 2, 3, 4.5, 6.5) and % three or more.
- 5920 friends: "How often do you do each of the following? Get together with friends, informally" never ... almost every day (5 options; "every day" added
  as a sixth option in later volumes); % almost every day or more.
- 630 dating (core): "On the average, how often do you go out with a date?" never ... over 3 times a week; % once a week or more.
- 10550 TV: "How much TV do you estimate you watch on an average weekday?" none / half hour or less / about one hour / two / three / four / five or more;
  mean of midpoints (0, 0.25, 1, 2, 3, 4, 5.5) and % 3+ hours.
- 31680 internet (2009-2012 volumes): "Not counting work for school or a job, about how many hours a week do you spend on the Internet ...", 29625 social
  networking frequency ("Visit social networking Web sites like MySpace or Facebook", almost every day = daily), 31990 electronic games hours, 29930 computer
  hours. Midpoints for the weekly-hours items are set from the printed category labels (see `IND` in 31_mtf.py).
- 590 work (core): hours per week in a paid or unpaid job during the school year; % working and % 16+ hours.
- 20780 sleep: "How often do you ... Get at least seven hours of sleep?" never / seldom / sometimes / most days / nearly every day / every day; % most days or
  more often. 20790 "Get less sleep than you think you should?" % nearly every day or every day.
- 12650 loneliness: "A lot of times I feel lonely" (disagree / mostly disagree / neither / mostly agree / agree); % mostly agree + agree. One form (Form 5).
  12690 "I often feel left out of things" likewise.
- Self-derogation (Kaplan items; Forms 2, 5 and 6): 12660 "I feel I do not have much to be proud of", 12680 "Sometimes I think that I am no good at all",
  12720 "I feel that I can't do anything right", 12750 "I feel that my life is not very useful"; % agree each; composite = mean of the four.
- Depressive affect (the four items used by Keyes et al. 2019; Form 6 in the 12th-grade questionnaire): 23700 "Life often seems meaningless", 23720 "The future
  often seems hopeless" (% agree), 23710 "I enjoy life as much as anyone", 23730 "It feels good to be alive" (% disagree); composite = mean of the four.
- 1190 happiness (all forms): very / pretty / not too happy. 6840 life satisfaction: "How satisfied are you with your life as a whole these days?" 1-7; mean.
- 12620 "On the whole, I'm satisfied with myself" (self-esteem, positive pole) is compiled but not used in the section.

Weights and errors: the printed percentages are weighted by MTF's sampling weights (the volumes' Appendix B). Standard errors are approximated as
sqrt(p(1-p)/N) x sqrt(DEFF) with DEFF = 2; Appendix B of each volume gives design-effect guidelines that for single-form 12th-grade percentages lie roughly
between 1.5 and 3, so the intervals shown are indicative. Weighted N answering per form is about 2,000-2,500 (about 14,000 for all-form items).

## 3. Analysis on the published series (`31_mtf.py`, part A)

Outputs in `results/tables/`: `mtf_published_series.csv` (indicator x sex x year, value, se, n), `mtf_published_changes.csv` (levels 1996/2000/2005/2010/2012
and changes 1996->2010, 2010->2012, 1996->2012, 2005->2012 with SEs), `mtf_published_comovement.csv` (Pearson r between year-level exposure and distress
series in levels and first differences; 17 points, descriptive only), `mtf_published_coverage.csv`, copies of the literature and Johnson tables, and
`mtf_microdata_status.csv`. The requested 2010->2019 and 2019->2024 changes cannot be computed from published tables: the volume series ends in 2012 and no
later MTF publication tabulates these items by year. Results are read by the report part.
Results (all 12th graders unless stated; levels 1996 -> 2012, change with approximate SE; from `results/tables/mtf_published_changes.csv`):
- Homework: 6.86 -> 5.92 hours/week (boys 6.32 -> 5.54, -0.78 (0.42); girls 7.32 -> 6.28, -1.04 (0.42)); 10+ hours/week 25.0% -> 19.0%. 2010 -> 2012: girls -0.33 (0.40), boys -0.08 (0.41).
- Evenings out: 2.78 -> 2.56 per week (boys -0.19 (0.04), girls -0.25 (0.04)); friends informally almost every day 49.5% -> 39.4% (boys -12.4 (2.1), girls -8.8 (2.0) pp);
  dates weekly or more 45.6% -> 30.8%; works during the school year 75.9% -> 59.5%.
- Screens: TV weekday 2.14 -> 2.09 hours (flat); personal internet 6.6 (2006) -> 11.0 (2012) hours/week; daily social-networking 49% (2008) -> 71% (2012; girls 78%);
  electronic games 6.6 (2008) -> 9.9 (2012) hours/week.
- Sleep: 7+ hours most days or more 51.8% -> 57.1% (boys +4.7 (2.8), girls +5.0 (2.7) pp).
- Distress: lonely (agree) 33.0% -> 27.2% (boys -2.8 (2.7), girls 37.3% -> 29.2%, -8.1 (2.8) pp); self-derogation mean % agree 14.2 -> 15.4 (boys +1.8 (0.6), girls +0.4 (0.6));
  depressive affect mean % 12.1 -> 10.1 (boys -1.6 (1.0), girls -2.7 (0.9)); very happy 18.6% -> 24.0%; life satisfaction mean 4.99 -> 5.12.
  2010 -> 2012, girls: self-derogation +1.10 (0.62), loneliness -1.40 (2.76), depressive affect +0.10 (0.90).
- Year-level co-movement (17 points, all students): in levels the declining series are positively correlated (shared trend); in first differences the strongest
  pairs are evenings out with self-derogation r = -0.67 and homework hours with loneliness r = +0.50 (`mtf_published_comovement.csv`); descriptive only.
- Johnson et al. 2017 (8th/10th, ref. 2008): homework +0.55 scale points in 1991 -> +0.05 in 2014; evenings-out OR 1.29 (1991) -> 0.67 (2014); depressed mood +0.07 (1991),
  n.s. 2008-2012, +0.13 (2014).


## 4. Microdata pipeline (`31_mtf.py`, part B)

Runs when ICPSR files are present in `data/external/mtf/icpsr/<study>/` (study numbers in the script header and the README). Variable location is
codebook-driven without the codebooks: MTF's ICPSR variable labels are the OSIRIS abbreviations that also appear in the volumes' cross-time index
(e.g. `VRY HPY THS DAYS`, `-MUCH TO B PROUD`, `I AM NO GOOD`, `MY LIFE NT USEFL`, `CMP SATFD W/LIFE`), so `LABEL_PATTERNS` matches concepts to variables from
the file metadata (pyreadstat), prints the match table (`mtf_micro_varmap.csv`) for inspection, and applies confirmed overrides. Confirmed 8th/10th-grade V-codes
(2008-2016 files), from Orben & Przybylski's public replication code (github.com/OrbenAmy/NHB_2019, `1_2_prep_mtf.R`, `2_2_sca_mtf.R`): V1 year, V501 grade,
V7202 sex, V1070 race, V7302 happiness, V8501/V8504/V8508/V8512 self-esteem, V8503 not much to be proud of, V8507 no good at all, V8511 can't do anything right,
V8513 life not useful, V8502 life meaningless, V8505 enjoy life, V8509 future hopeless, V8514 good to be alive, V7501-V7508 loneliness block (V7502 "always
someone I can turn to"; V7501 is the first item of the block and by questionnaire order "A lot of times I feel lonely" - confirm), V7325/V7326 TV weekday/weekend
hours, V7551 internet hours at home, V7553 electronic games hours, V7552 social-networking frequency, V7589 social-networking hours, V7590 video chat, V7562
texting, V7563 calling, V7381 internet news, V7544 computer for school, V8531 sleeps less than should, V7216 mother's education, V7208 siblings, V7217 mother's
job, V7329 enjoys school, V7221 grades, V7254 talks with parents. Not yet confirmed: the 8th/10th homework-hours and evenings-out codes, the weight (V5 in both
file families by MTF convention), and all 12th-grade codes; the label matcher is the fallback for these and the script refuses to model a file where year,
weight, sex, homework and social-media hours are not all located.

Model: `y ~ hw_h * sm_h + C(race) + C(mother_educ) + C(father_educ) + C(region) | year`, weights V5, heteroskedasticity-robust SEs (the public files have no
school or PSU identifiers, so design clustering is impossible; MTF's own DEFF guidance suggests multiplying SEs by about 1.4), by sex and grade group, for
depressive affect (4-item mean), self-derogation, loneliness and happiness; homework midpoints as above; social-media hours midpoints to be checked against the
codebook labels (the item has nine categories from none to 9+ hours per day, which the script maps to 0, 0.25, 1, 2, 3, 4, 5.5, 7, 9). Decomposition: year
dummies with and without the time-use terms, reference = first year the social-media hours item is present; share accounted = 1 - adjusted/unadjusted year
coefficient. The requested trend decomposition 1991-2024 for homework, socializing and screens follows the same template once the files exist.

## 5. Literature (student-level MTF estimates)

See `data/compiled/mtf/mtf_literature.csv` (18 entries) and the section table. Verification status: Twenge, Joiner, Rogers & Martin 2018 from the full text
(course-site copy of the SAGE PDF); Kreski et al. 2021, Kreski et al. 2022, Keyes et al. 2019, Johnson et al. 2017, Askari et al. 2022, Keyes & Platt 2024 from PMC
full text (plus supplements for Kreski 2022 and Askari 2022, via Europe PMC); Twenge Martin & Campbell 2018, Twenge & Campbell 2019, Keyes et al. 2015,
Twenge Krizan & Hisler 2017, Kaur et al. 2022, Twenge & Farley 2021, Orben & Przybylski 2019 from PubMed abstracts; Twenge Spitzberg & Campbell 2019, Twenge & Park
2019 from Crossref abstracts. Not verifiable from this host: the dose-response numbers of Twenge Martin & Campbell 2018 (press release only) and the by-sex
r values in Twenge, Haidt, Joiner & Campbell 2020 (paywalled). Where the literature answers the questions: the H1 main effect in MTF is a cross-sectional dose
gradient in hours (Twenge et al.) that disappears at the daily-use margin (Kreski 2021) and is small in variance terms (Orben & Przybylski); the post-2012 rise is
a period effect (Keyes 2019; Askari 2022) partly absorbed by falling sleep (Kaur 2022); homework is protective at the individual level (Twenge 2018) and its hours
fell for 8th/10th graders (Johnson 2017) and were flat for 12th graders (Twenge & Park 2019); in-person socializing fell steadily from the 1990s (Twenge,
Spitzberg & Campbell 2019; Kreski 2022). Not answered anywhere: the homework x social-media interaction, by sex and grade, or whether the social-media gradient is
steeper for students under high academic load (H3).

## 6. Gaps and what a follow-up needs

1. An ICPSR account holder downloads the Stata versions of the 64 studies listed (about 30 minutes of clicking; the files are a few MB each) into
   `data/external/mtf/icpsr/<study>/`, then runs `uv run python scripts/analysis/31_mtf.py`; the match table should be checked against the codebooks and the
   12th-grade V-codes added to the overrides.
2. The 1991-1995 data volumes (print) would extend the 12th-grade published series back to 1991; a library scan would do.
3. Without microdata, the 2013-2024 trends in homework, evenings out and social-media hours by sex remain unmeasured here; the Johnson et al. (2017) table covers
   8th/10th graders to 2014 only.
