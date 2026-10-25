#!/bin/bash
# Download the PISA 2012, 2015 and 2018 questionnaire files used by scripts/analysis/32_pisa_panel.py (PISA 2022 is in data/external/pisa2022).
# Run from the repository root: bash scripts/download/pisa_panel/download.sh      (resumable: curl -C -; each zip is verified with unzip -t)
# Sources are documented in data/external/pisa_panel/README.md. The 2012 data zips are no longer served to non-browser clients by
# www.oecd.org (HTTP 403 from the content/dam URLs, 404 from webfs.oecd.org), so they come from the Internet Archive's Wayback copies
# (2022-04-02) of the former OECD URLs; the 2012 SPSS control files are still served by www.oecd.org.
set -u
R="$(cd "$(dirname "$0")/../../.." && pwd)/data/external/pisa_panel"; mkdir -p "$R/2012" "$R/2015" "$R/2018"
dl() { d=$1; url=$2; f=${3:-$(basename "$url")}; echo "[$(date +%T)] $f"; curl -sS -L -C - -o "$R/$d/$f" "$url" --retry 5 --retry-delay 15 || echo "  curl failed for $url"; }
# 2015 (CY6): combined public-use SPSS files and codebook
dl 2015 https://webfs.oecd.org/pisa/PUF_SPSS_COMBINED_CMB_STU_QQQ.zip
dl 2015 https://webfs.oecd.org/pisa/PUF_SPSS_COMBINED_CMB_SCH_QQQ.zip
dl 2015 https://webfs.oecd.org/pisa/Codebook_CMB.xlsx
# 2018 (CY07): SPSS files and codebook
dl 2018 https://webfs.oecd.org/pisa2018/SPSS_STU_QQQ.zip
dl 2018 https://webfs.oecd.org/pisa2018/SPSS_SCH_QQQ.zip
dl 2018 https://webfs.oecd.org/pisa2018/PISA2018_CODEBOOK.xlsx
# 2012: SPSS control files (OECD) and fixed-width data (Wayback copies of www.oecd.org/pisa/pisaproducts/INT_*12_DEC03.zip)
B='https://www.oecd.org/content/dam/oecd/en/data/datasets/pisa/pisa-2012-datasets/main-survey/sas-and-spss-control-files'
dl 2012 "$B/SPSS%20syntax%20to%20read%20in%20student%20questionnaire%20data%20file.txt" PISA2012_SPSS_student.sps
dl 2012 "$B/SPSS%20syntax%20to%20read%20in%20school%20questionnaire%20data%20file.txt" PISA2012_SPSS_school.sps
dl 2012 "https://web.archive.org/web/20220402010813id_/https://www.oecd.org/pisa/pisaproducts/INT_STU12_DEC03.zip" INT_STU12_DEC03.zip
dl 2012 "https://web.archive.org/web/20220402010754id_/https://www.oecd.org/pisa/pisaproducts/INT_SCQ12_DEC03.zip" INT_SCQ12_DEC03.zip
for f in "$R"/*/*.zip; do printf '%s: ' "$f"; unzip -tq "$f" | tail -1; done
ls -l "$R"/*/
