# Teen Distress Pilot

What large-scale public microdata can say about the two leading explanations for the rise in adolescent anxiety and depression after 2010: Jonathan Haidt's smartphone-and-social-media thesis (*The Anxious Generation*) and Peter Gray's school-pressure thesis. The project tests four hypotheses (phones, school pressure, their interaction, and measurement artifacts) against IPUMS microdata and public survey series, and sets the results beside the evidence the two camps cite. The October 2026 revision (Phase 2, planned in `notes/phase2_plan.md`) adds NHIS and NSCH parent reports, the pooled DHS-8 self-report modules, monthly NVSS suicide seasonality, four PISA waves, Monitoring the Future's published series, new county survey waves with the first post-ban observations, and county broadband and early-smartphone coverage instruments, plus the ATUS 2025 and Bangladesh MICS 2025 releases.

**Read the report:** https://ccdavis.github.io/teen-mh-pilot/ (GitHub Pages, served from `docs/`), or open `docs/index.html` locally (self-contained; works offline), or the print editions `docs/Teen_Distress_Pilot.pdf` and `docs/Teen_Distress_Pilot.docx`.

**Review the paper:** [complete Markdown](docs/Teen_Distress_Pilot.md), or start at the [indexed review chunks](docs/review/README.md) for copy editing with an LLM. Each chunk links to the editable sources and its place in the complete paper.

## What is in this repository

| Path | Contents |
|---|---|
| `docs/` | The report as a static site (interactive charts), PDF, Word and Markdown editions, indexed review chunks in `review/`, and a PNG of every chart |
| `results/tables/` | Every computed table the report draws on (CSV) |
| `data/compiled/` | Public-source tables constructed for this project: LTE launch dates by metro, state school phone-ban timing, state accountability-policy timing, HBSC published trend series, ITU connectivity series, NTIA adoption aggregates, state youth-survey county panel, GSHS catalog, World Bank indicators; Phase 2 adds the CDC WONDER monthly suicide tables, DHS-8 module inventory and published prevalence, Monitoring the Future published item series, NHIS-Teen published aggregates, and the county broadband panel |
| `data/` (ignored) | Raw downloads and microdata extracts are not committed; `data/README.md` says how to obtain each |
| `scripts/extract/` | Turning IPUMS extracts into the slim files the analysis uses (ACS, CPS, ATUS, MICS, IPUMS International, DHS), with the sample and variable lists |
| `scripts/download/` | Acquiring and compiling the public sources (NSDUH, YRBS, NHANES, NTIA/CPS supplement, GSHS, HBSC, PISA 2012–2022, ITU, WDI, state youth surveys, school policy, phone bans, LTE launches, NHIS, NSCH, DHS-8 reports, NVSS via CDC WONDER, Monitoring the Future volumes, broadband maps) |
| `scripts/analysis/` | The numbered analyses, in the order they were run |
| `scripts/report/` | Report builder, print editions, site builder, hand-written sections, and the per-source Phase 2 section modules in `parts/` |
| `notes/` | Methods notes on each source: wording, coding, weights, gaps |

`DATA_SOURCES.md` lists every dataset with its provider, access route, the variables used, and the script that consumes it.

## Reproducing

Python is managed with [uv](https://docs.astral.sh/uv/); `uv sync` installs the environment from `pyproject.toml`. Run everything from the repository root (scripts resolve their paths from their own location, so other working directories also work). The print editions need Chromium for Playwright (`uv run playwright install chromium`) and [pandoc](https://pandoc.org). The LTE builder needs `xlrd` (`uv run --with xlrd ...`); LibreOffice is used only to convert the 2010 Washington survey reports from `.doc`.

1. Obtain the IPUMS extracts and public files described in `DATA_SOURCES.md` and `data/README.md`.
2. `scripts/extract/`: build the slim microdata files (see its README for the exact variable lists).
3. `scripts/download/`: fetch and compile the public sources (the compiled outputs are already committed in `data/compiled/`).
4. `scripts/analysis/`: run the numbered scripts in order (10a before 10; 18 before the report builder); they write to `results/tables/`.
5. `bash scripts/report/rebuild.sh` to rebuild all editions in `docs/` (HTML, PDF, Word, complete Markdown and indexed review chunks).

Step 5 can be run from the committed `results/tables/` and `data/compiled/` alone; steps 1 to 4 are needed only to regenerate those results from the sources.

## Copy editing and regenerating the paper

Read [the review index](docs/review/README.md), select chunks in document order, and record edits by chunk ID and exact quotation. Apply accepted edits to `scripts/report/90_build_report.py` or the hand-written files in `scripts/report/sections/`, using the source links in each chunk. These Python/HTML templates are the authoritative text; the Markdown edition and chunks are generated and overwritten on rebuild. Computed tables still come from the analysis outputs.

Run `bash scripts/report/rebuild.sh` after edits to regenerate every edition together. During editing, `bash scripts/report/rebuild.sh --review-only` rebuilds the HTML and Markdown without rendering PDF, Word or chart images; finish with the full rebuild before sharing. Neither command reruns the microdata analyses. The [JSON manifest](docs/review/manifest.json) provides chunk order, context, word counts, source locations, full-paper line ranges and fingerprints for automated review tools.

## Data access

Microdata are not redistributed here. The IPUMS data used (ACS via IPUMS USA, CPS, ATUS, IPUMS International, IPUMS DHS, IPUMS MICS) are available to registered users through the extract systems at [usa.ipums.org](https://usa.ipums.org), [cps.ipums.org](https://cps.ipums.org), [timeuse.ipums.org](https://timeuse.ipums.org), [international.ipums.org](https://international.ipums.org), [idhs.ipums.org](https://www.idhs.ipums.org), and [mics.ipums.org](https://mics.ipums.org). The other sources are public downloads from SAMHSA, CDC, NTIA/Census, WHO, OECD, ITU, the World Bank, NCES, state education and health departments, and the policy trackers named in `DATA_SOURCES.md`.

## License

- **Code** (`scripts/`, `pyproject.toml`): [MIT License](LICENSE).
- **Report, compiled tables, results and notes** (`docs/`, `data/compiled/`, `results/`, `notes/`, `DATA_SOURCES.md`): [Creative Commons Attribution 4.0 International](LICENSE-CC-BY-4.0.txt) (CC BY 4.0). You may share and adapt them with attribution.
- The compiled tables are derived from the public sources listed in `DATA_SOURCES.md`, whose own terms continue to apply; IPUMS-derived results are aggregates and are shared in line with the IPUMS terms, which require citation of each data collection and prohibit redistribution of the microdata (none is included here).
- Bundled third-party files in `docs/assets/` (Plotly.js, IBM Plex and Source Serif 4 fonts) keep their own licenses, reproduced in `docs/assets/LICENSES.txt`.

## Citation

Please cite this repository (a `CITATION.cff` file is included, so GitHub's "Cite this repository" button gives a formatted reference) together with the underlying providers listed in `DATA_SOURCES.md`:

> Davis, Colin (2026). *Teen Distress Pilot: public-data tests of the smartphone and school-pressure explanations for the post-2010 rise in adolescent distress.* https://github.com/ccdavis/teen-mh-pilot (report: https://ccdavis.github.io/teen-mh-pilot/).
