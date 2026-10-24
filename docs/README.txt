Teen Distress Pilot - self-contained site
index.html            the report (open directly, or host the whole folder as-is)
assets/plotly.min.js  chart library (local copy, v2.35.3)
assets/fonts.css + fonts/   IBM Plex Sans, Source Serif 4, IBM Plex Mono (local copies)
figures/              static PNG of every chart
Teen_Distress_Pilot.pdf / .docx   print editions
Teen_Distress_Pilot.md   complete Markdown edition
review/README.md        copy-edit instructions and ordered chunk index
review/chunks/          generated Markdown chunks with editable-source links
review/manifest.json    machine-readable index, source locations and fingerprints
Apply copy edits to scripts/report/90_build_report.py or scripts/report/sections/, then regenerate. Markdown files are generated outputs.
Rebuild every edition from the repository root: bash scripts/report/rebuild.sh
Rebuild HTML and Markdown while editing (print files and images unchanged): bash scripts/report/rebuild.sh --review-only
Check review outputs against the assembled HTML and source fingerprints: uv run python scripts/report/95_build_review.py --check
