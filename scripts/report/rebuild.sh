#!/bin/bash
# Rebuild every report edition from the committed tables and editable templates.
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--review-only" ) ]]; then
    echo "Usage: bash scripts/report/rebuild.sh [--review-only]" >&2
    exit 2
fi
uv run python scripts/report/90_build_report.py
if [[ "${1:-}" != "--review-only" ]]; then
    bash scripts/report/92_print_editions.sh
fi
uv run python scripts/report/95_build_review.py
uv run python scripts/report/94_build_site.py
