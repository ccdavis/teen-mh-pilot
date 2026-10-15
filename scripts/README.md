# scripts/

Run everything from the repository root with `uv run python <script>`.

- `extract/`: convert IPUMS extracts into the slim files the analyses read. README there lists samples and variables per product.
- `download/`: acquire and compile the public sources. Each subdirectory has its own README or is documented in `notes/`.
- `analysis/`: numbered in the order they were developed; each writes CSVs to `results/tables/`.
  - 02–06, 09: ACS outcome series, geographic variation, composition, exploratory figures
  - 07–08: ATUS time use of 15–17-year-olds
  - 10: LTE event study (needs `data/compiled/lte/`)
  - 11: IPUMS International census arm
  - 12–13: validation against NSDUH, YRBS, NHANES
  - 14, 20, 22: GSHS (penetration, phone hours, ITU coverage)
  - 15: HBSC schoolwork pressure
  - 16, 19: state school-policy tests and the U.S. adoption-dose and Race to the Top follow-ups
  - 18: MICS Child Functioning Module (after `extract/mics_extract.py`)
  - 21: DHS Nepal and Kenya 2022
  - 23–24: state youth survey county panel
  - 25–26: PISA 2022 school phone rules
- `report/`: `90_build_report.py` assembles `build/report.html` from `results/tables/` and the hand-written `sections/`; `91_language_pass.py` is the plain-language edit; `92_print_editions.sh` renders the PDF and Word files into `docs/`; `93_docx_fix.py` makes the Word file schema-valid; `94_build_site.py` writes the self-contained site into `docs/`.
