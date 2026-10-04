#!/bin/sh
# Publiceert enkel wat publiek mag (root-site) + jobs/site onder /jobs.
# Data, markdown en scripts in de repo worden NIET gepubliceerd.
set -eu
rm -rf _site
mkdir -p _site/jobs
for f in index.html favicon.ico favicon.svg robots.txt; do
  [ -f "$f" ] && cp "$f" _site/
done
[ -d assets ] && cp -r assets _site/
cp -r jobs/site/. _site/jobs/
echo "build ok: $(find _site -type f | wc -l) bestanden"
