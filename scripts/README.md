# scripts/

Run everything from the repository root with `uv run python <script>`. Every script resolves its paths from its own location, so other working directories also work.

- `extract/`: turn IPUMS extracts into the slim files the analyses read. `acs_extract_sql.py`, `cps_extract_sql.py` and `atus_extract.py` write duckdb SQL plus a runner into `build/sql/`; `ipumsi_extract.sql` and `dhs_extract.sql` are run directly; `mics_extract.py` reads the IPUMS MICS fixed-width files. The README there lists samples, variables, weight scales and the column-name conventions.
- `download/`: acquire and compile the public sources. Compiled tables go to `data/compiled/` (committed); microdata-derived files go to `data/extracts/` (not committed). Each subdirectory has its own README or is documented in `notes/`.
- `analysis/`: numbered in the order they were developed; each writes CSVs to `results/tables/`.
  - 02–06, 09: ACS outcome series, geographic variation, composition, exploratory figures
  - 07–08: ATUS time use of 15–17-year-olds
  - 10a, 10: onset tables from `data/compiled/lte/`, then the market event study (`10_event_study.py <onset.csv> [--dated-only]`, run for the first-launch, Verizon and second-carrier dates)
  - 11: IPUMS International census arm
  - 12–13: validation against NSDUH, YRBS, NHANES (13 reads both the 2023 and the 2025 YRBS combined releases; 12 uses the 2025 national file)
  - 14, 20, 22: GSHS (penetration, phone hours, ITU coverage)
  - 15: HBSC schoolwork pressure
  - 16, 19: state school-policy tests and the U.S. adoption-dose and Race to the Top follow-ups
  - 18: MICS Child Functioning Module (after `extract/mics_extract.py`); also writes the survey-level summary the report reads
  - 21: DHS Nepal and Kenya 2022
  - 23–24: state youth survey county panel
  - 25–26: PISA 2022 school phone rules
  - 27: NHIS Sample Child 2021–2024 against the published NHIS-Teen estimates (parent vs. adolescent report; after `download/nhis/`)
  - 28: NSCH 2016–2025 caregiver screen gradient, trends, state adoption and the first phone-ban difference-in-differences (after `download/nsch/`)
  - 29: DHS-8 mental-health modules pooled across Nepal, Mozambique and Bangladesh (after `extract/dhs_extract.py`; published prevalence from `download/dhs8/`)
  - 30: NVSS monthly suicide seasonality and the summer-vs-school decomposition (after `download/nvss/wonder_fetch.py`)
  - 31: Monitoring the Future published 12th-grade series 1996–2012 (after `download/mtf/`); its student-level models run once ICPSR files are present
  - 32: PISA 2012–2022 four-wave panel and the 2015 test-anxiety interaction (after `download/pisa_panel/`)
  - 33: YRBS state phone-ban difference-in-differences (placebo on the 2023 files until the 2025 files are released)
  - 34: county broadband availability and the AT&T 2010 mobile footprint against the state-survey county panels (after `download/broadband/`)
- `report/`: `bash scripts/report/rebuild.sh` runs the complete report pipeline; `--review-only` skips print rendering while editing. `90_build_report.py` assembles `build/report.html` from `results/tables/`, the hand-written `sections/`, and the Phase 2 section modules in `parts/` (each `parts/<name>.py` builds one source's text, tables and charts from its results tables; `report_lib.py` holds the shared helpers and the loader; preview one with `parts/_run_part.py <name>`; see `parts/README.md`); `92_print_editions.sh` renders the PDF and Word files into `docs/` (needs Chromium for Playwright, installed with `uv run playwright install chromium`, and pandoc); `93_docx_fix.py` makes the Word file schema-valid; `94_build_site.py` writes the self-contained site into `docs/`; `95_build_review.py` exports the assembled HTML to a complete Markdown paper and indexed chunks with source links in `docs/review/`. Its `--check` option detects stale review outputs without writing files. Apply copy edits to the Python/HTML sources, then regenerate; generated Markdown is not an editable source. Run `uv run python -m unittest discover -s scripts/report -p 'test_*.py'` to check the review exporter. `archive/91_language_pass.py` is the one-time plain-language edit applied to the report text in September 2026, kept for the record; it is not part of the pipeline.
