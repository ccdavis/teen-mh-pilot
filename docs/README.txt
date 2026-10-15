Teen Distress Pilot - self-contained site
index.html            the report (open directly, or host the whole folder as-is)
assets/plotly.min.js  chart library (local copy, v2.35.3)
assets/fonts.css + fonts/   IBM Plex Sans, Source Serif 4, IBM Plex Mono (local copies)
figures/              static PNG of every chart
Teen_Distress_Pilot.pdf / .docx   print editions
Rebuild from the repository root: uv run python scripts/report/90_build_report.py && bash scripts/report/92_print_editions.sh && uv run python scripts/report/94_build_site.py
