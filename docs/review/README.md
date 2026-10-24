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
| 2 | [Teen Distress Pilot](chunks/teen-distress-pilot.md) | 83 | 11–13 |
| 3 | [The four hypotheses](chunks/hyp.md) | 274 | 17–26 |
| 4 | [Summary: what the public microdata support today](chunks/verdict.md) | 807 | 30–53 |
| 5 | [Part 1 · The rise, and whether public data can measure it](chunks/part1.md) | 75 | 57–59 |
| 6 | [The ACS cognitive-difficulty item, 2008–2024](chunks/acs.md) | 267 | 63–84 |
| 7 | [Does the ACS item measure adolescent distress?](chunks/gates.md) | 537 | 88–123 |
| 8 | [Geographic variation: is there anything to explain?](chunks/geo.md) | 470 | 127–182 |
| 9 | [State youth surveys at county level](chunks/state-youth-surveys-at-county-level.md) | 273 | 186–194 |
| 10 | [Part 2 · Phones and social media (H1)](chunks/part2.md) | 76 | 198–200 |
| 11 | [4G rollout across U.S. metros](chunks/lte.md) | 639 | 204–233 |
| 12 | [Rollout and adoption at county level, state youth surveys](chunks/rollout-and-adoption-at-county-level-state-youth-surveys.md) | 425 | 237–262 |
| 13 | [Adoption rather than rollout: smartphone use against the state youth survey](chunks/adoption-rather-than-rollout-smartphone-use-against-the-state-youth-survey.md) | 204 | 266–277 |
| 14 | [Smartphone adoption in the United States, 2009–2023](chunks/smartphone-adoption-in-the-united-states-20092023.md) | 226 | 281–293 |
| 15 | [Phone-first countries: MICS Child Functioning Module (68 surveys, 2017–2024)](chunks/phone-first-countries-mics-child-functioning-module-68-surveys-20172024.md) | 1039 | 297–342 |
| 16 | [Phone-first countries: GSHS school surveys (149 country-rounds, 2003–2023)](chunks/phone-first-countries-gshs-school-surveys-149-country-rounds-20032023.md) | 987 | 346–396 |
| 17 | [Phone-first countries: census microdata (IPUMS International)](chunks/phone-first-countries-census-microdata-ipums-international.md) | 176 | 400–402 |
| 18 | [Part 3 · School pressure (H2)](chunks/part3.md) | 59 | 406–408 |
| 19 | [Did school demands rise? Time use of 15–17-year-olds (ATUS, 2003–2024)](chunks/atus.md) | 137 | 412–418 |
| 20 | [Schoolwork pressure across countries (HBSC)](chunks/schoolwork-pressure-across-countries-hbsc.md) | 498 | 422–447 |
| 21 | [U.S. school accountability policy](chunks/policy.md) | 657 | 451–482 |
| 22 | [Part 4 · The interaction (H3): phones in the same hours as high-pressure school](chunks/part4.md) | 109 | 486–488 |
| 23 | [What the phone-ban evidence says about this](chunks/what-the-phone-ban-evidence-says-about-this.md) | 360 | 492–509 |
| 24 | [Did 4G timing matter more in high-pressure states?](chunks/did-4g-timing-matter-more-in-high-pressure-states.md) | 160 | 513–528 |
| 25 | [School phone bans](chunks/bans.md) | 1114 | 532–582 |
| 26 | [What the causal literature already shows](chunks/what-the-causal-literature-already-shows.md) | 1176 | 586–614 |
| 27 | [County social-media use and sadness](chunks/county-social-media-use-and-sadness.md) | 762 | 618–644 |
| 28 | [How this sits with Haidt's and Twenge's evidence](chunks/reconcile.md) | 125 | 648–650 |
| 29 | [What that evidence base contains](chunks/what-that-evidence-base-contains.md) | 263 | 654–662 |
| 30 | [Where the pilot agrees](chunks/where-the-pilot-agrees.md) | 175 | 666–671 |
| 31 | [Where the pilot finds no effect, and how to interpret the difference](chunks/where-the-pilot-finds-no-effect-and-how-to-interpret-the-difference.md) | 548 | 675–681 |
| 32 | [Two empirical patterns the existing debate has largely overlooked](chunks/two-empirical-patterns-the-existing-debate-has-largely-overlooked.md) | 238 | 685–690 |
| 33 | [Conclusions and next steps](chunks/next.md) | 872 | 694–714 |
