# Paper review index

This is a generated review edition of the complete assembled paper, including
tables, captions, citations and links to static chart images. Start here to select
chunks, or read the [complete Markdown paper](../Teen_Distress_Pilot.md).

## Copy-edit and regenerate

1. Read the relevant chunks and their neighboring sections. Each chunk gives its
   heading context, a link to the full paper, and editable source entry points.
2. Record suggested edits using the chunk ID, an exact quotation, the replacement,
   and a reason. Check repeated claims against the summary and conclusion. Open
   the linked chart images when reviewing claims about figures; the images are
   not transcribed into Markdown.
3. Apply accepted prose edits to `scripts/report/90_build_report.py` or the
   hand-written HTML in `scripts/report/sections/`. Source links are entry points;
   locate the quoted text there. Preserve Python interpolation and HTML markup.
   Numerical tables come from `results/tables/`; correct their producing analysis
   if a computed result must change.
4. From the repository root, run `bash scripts/report/rebuild.sh`. This rebuilds
   the HTML, PDF, Word, complete Markdown, chunks and this index together. It uses
   the committed result tables and does not rerun microdata analysis.
5. Review the source and generated diffs, then repeat the review as needed.

Edit the Python/HTML sources, rather than these generated Markdown files:
Markdown edits are overwritten on regeneration. The source links identify the
templates used by all editions, so accepted copy edits persist in every format.

## Faster text review

To rebuild HTML and Markdown during editing without rendering print editions:

```sh
bash scripts/report/rebuild.sh --review-only
```

PDF, Word and chart images are refreshed by the full rebuild. For an already
assembled `build/report.html`, export only the review edition with
`uv run python scripts/report/95_build_review.py`. Check that its outputs match
the assembled HTML and source fingerprints without writing files with
`uv run python scripts/report/95_build_review.py --check`.

## Chunk index

Chunks follow document order, split at major headings and then at block boundaries
near 1,200 words. Tables, lists and paragraphs remain intact and can exceed that
target. Heading-based IDs remain stable across prose edits; continuation chunks
get numeric suffixes. Context headings in chunk metadata are not extra paper text.
The [JSON manifest](manifest.json) records order, context, word counts, full-paper
line ranges, source locations and SHA-256 fingerprints. Line ranges refer to the
complete Markdown file; its paper content covers every parsed block exactly once.

| Order | Chunk | Words | Full-paper lines |
| --- | --- | ---: | --- |
| 1 | [Publication note](chunks/publication-note.md) | 10 | 7–7 |
| 2 | [Teen Distress Pilot](chunks/teen-distress-pilot.md) | 144 | 11–13 |
| 3 | [The four hypotheses](chunks/hyp.md) | 274 | 17–26 |
| 4 | [Summary: what the public microdata support today](chunks/verdict.md) | 33 | 30–32 |
| 5 | [Summary: what the public microdata support today](chunks/verdict-2.md) | 1481 | 36–63 |
| 6 | [Part 1 · The rise, and whether public data can measure it](chunks/part1.md) | 75 | 67–69 |
| 7 | [The ACS cognitive-difficulty item, 2008–2024](chunks/acs.md) | 267 | 73–94 |
| 8 | [Does the ACS item measure adolescent distress?](chunks/gates.md) | 537 | 98–133 |
| 9 | [Geographic variation: is there anything to explain?](chunks/geo.md) | 470 | 137–192 |
| 10 | [State youth surveys at county level](chunks/state-youth-surveys-at-county-level.md) | 317 | 196–204 |
| 11 | [Part 2 · Phones and social media (H1)](chunks/part2.md) | 112 | 208–210 |
| 12 | [4G rollout across U.S. metros](chunks/lte.md) | 639 | 214–243 |
| 13 | [Rollout and adoption at county level, state youth surveys](chunks/rollout-and-adoption-at-county-level-state-youth-surveys.md) | 425 | 247–272 |
| 14 | [Continuous broadband coverage and the AT&T 2010 footprint at county level](chunks/broadband.md) | 1119 | 276–411 |
| 15 | [The AT&T 2010 footprint and Minnesota's 1998-2019 county series](chunks/the-att-2010-footprint-and-minnesotas-1998-2019-county-series.md) | 1071 | 415–454 |
| 16 | [What the broadband literature identifies](chunks/what-the-broadband-literature-identifies.md) | 523 | 458–470 |
| 17 | [Adoption rather than rollout: smartphone use against the state youth survey](chunks/adoption-rather-than-rollout-smartphone-use-against-the-state-youth-survey.md) | 204 | 474–485 |
| 18 | [Smartphone adoption in the United States, 2009–2023](chunks/smartphone-adoption-in-the-united-states-20092023.md) | 226 | 489–501 |
| 19 | [Phone-first countries: MICS Child Functioning Module (69 surveys, 2017–2025)](chunks/phone-first-countries-mics-child-functioning-module-69-surveys-20172025.md) | 1107 | 505–554 |
| 20 | [DHS-8 self-reports beyond Nepal](chunks/dhs8.md) | 1094 | 558–615 |
| 21 | [Microdata: pooled within-cluster estimates](chunks/microdata-pooled-within-cluster-estimates.md) | 1111 | 619–637 |
| 22 | [Published analyses of the module](chunks/published-analyses-of-the-module.md) | 205 | 641–641 |
| 23 | [Phone-first countries: GSHS school surveys (149 country-rounds, 2003–2023)](chunks/phone-first-countries-gshs-school-surveys-149-country-rounds-20032023.md) | 987 | 645–695 |
| 24 | [Phone-first countries: census microdata (IPUMS International)](chunks/phone-first-countries-census-microdata-ipums-international.md) | 176 | 699–701 |
| 25 | [Who reports the symptoms: U.S. caregivers and adolescents (NSCH 2016–2025, NHIS 2021–2024)](chunks/informants.md) | 1138 | 705–748 |
| 26 | [Sleep and bullying as pathways](chunks/sleep-and-bullying-as-pathways.md) | 1186 | 752–809 |
| 27 | [The first statewide school phone bans: a first look](chunks/the-first-statewide-school-phone-bans-a-first-look.md) | 1083 | 813–838 |
| 28 | [Prevalence under the two informants](chunks/prevalence-under-the-two-informants.md) | 1175 | 842–902 |
| 29 | [The screen-time gradient under parent and teen report](chunks/the-screen-time-gradient-under-parent-and-teen-report.md) | 719 | 906–925 |
| 30 | [Part 3 · School pressure (H2)](chunks/part3.md) | 77 | 929–931 |
| 31 | [Did school demands rise? Time use of 15–17-year-olds (ATUS, 2003–2025)](chunks/atus.md) | 167 | 935–941 |
| 32 | [Monitoring the Future: homework, socializing, screens and distress among 12th graders, 1996–2012, and the student-level test that still needs the microdata](chunks/mtf.md) | 1146 | 945–991 |
| 33 | [8th and 10th graders, 1991–2014, from a published table](chunks/th-and-10th-graders-19912014-from-a-published-table.md) | 393 | 995–1003 |
| 34 | [What the student-level MTF literature already answers](chunks/what-the-student-level-mtf-literature-already-answers.md) | 1196 | 1007–1026 |
| 35 | [What the student-level MTF literature already answers](chunks/what-the-student-level-mtf-literature-already-answers-2.md) | 342 | 1030–1036 |
| 36 | [Schoolwork pressure across countries (HBSC)](chunks/schoolwork-pressure-across-countries-hbsc.md) | 498 | 1040–1065 |
| 37 | [School-calendar seasonality of adolescent suicide and the summer-vs-school decomposition of the rise (NVSS, 1999–2024)](chunks/nvss.md) | 955 | 1069–1101 |
| 38 | [Did the rise follow the school calendar?](chunks/did-the-rise-follow-the-school-calendar.md) | 1074 | 1105–1152 |
| 39 | [Day of week](chunks/day-of-week.md) | 1042 | 1156–1194 |
| 40 | [U.S. school accountability policy](chunks/policy.md) | 671 | 1198–1229 |
| 41 | [Part 4 · The interaction (H3): phones in the same hours as high-pressure school](chunks/part4.md) | 133 | 1233–1235 |
| 42 | [What the phone-ban evidence says about this](chunks/what-the-phone-ban-evidence-says-about-this.md) | 360 | 1239–1256 |
| 43 | [PISA 2012–2022: school loneliness, life satisfaction and digital use across waves](chunks/pisa-panel.md) | 1044 | 1260–1289 |
| 44 | [Within-country panel: did well-being fall more where digital hours rose more?](chunks/within-country-panel-did-well-being-fall-more-where-digital-hours-rose-more.md) | 759 | 1293–1329 |
| 45 | [Dose–response by wave](chunks/doseresponse-by-wave.md) | 1102 | 1333–1372 |
| 46 | [Related literature](chunks/related-literature.md) | 618 | 1376–1385 |
| 47 | [Did 4G timing matter more in high-pressure states?](chunks/did-4g-timing-matter-more-in-high-pressure-states.md) | 160 | 1389–1404 |
| 48 | [School phone bans](chunks/bans.md) | 1129 | 1408–1458 |
| 49 | [Post-2021 waves and the first post-ban observations](chunks/bans-update.md) | 967 | 1462–1505 |
| 50 | [2025 YRBS: states with a mandate in force in 2024-25 against states without one](chunks/yrbs-states-with-a-mandate-in-force-in-2024-25-against-states-without-one.md) | 665 | 1509–1517 |
| 51 | [What the causal literature already shows](chunks/what-the-causal-literature-already-shows.md) | 1176 | 1521–1549 |
| 52 | [County social-media use and sadness](chunks/county-social-media-use-and-sadness.md) | 762 | 1553–1579 |
| 53 | [How this sits with Haidt's and Twenge's evidence](chunks/reconcile.md) | 211 | 1583–1585 |
| 54 | [What that evidence base contains](chunks/what-that-evidence-base-contains.md) | 414 | 1589–1598 |
| 55 | [Where the pilot agrees](chunks/where-the-pilot-agrees.md) | 510 | 1602–1609 |
| 56 | [Where the pilot finds no effect, and how to interpret the difference](chunks/where-the-pilot-finds-no-effect-and-how-to-interpret-the-difference.md) | 864 | 1613–1621 |
| 57 | [Two empirical patterns the existing debate has largely overlooked](chunks/two-empirical-patterns-the-existing-debate-has-largely-overlooked.md) | 678 | 1625–1630 |
| 58 | [Conclusions and next steps](chunks/next.md) | 1150 | 1634–1647 |
| 59 | [Conclusions and next steps](chunks/next-2.md) | 392 | 1651–1656 |
