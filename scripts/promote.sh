#!/bin/sh
# Gate (d): promotion. `dist/` becomes the committed, reviewed `docs/` that
# GitHub Pages serves from main:/docs.
#
# The build is NOT re-run here. Promotion copies the artifact the verifier just
# passed, so what lands in `docs/` is the exact tree that was checked. Run
# `npm run build` first; this script refuses if its output is not there.
#
# `rm -rf docs && cp -R dist docs` rather than a plain copy: a copy over the top
# leaves stale routes behind, and a stale route is a page nobody reviewed still
# being served. `docs/` is fully generated, so removing it loses nothing. This
# is not `git checkout` and nothing here recovers a bad promotion — rebuild and
# promote again.
set -eu

MODE="${DOCS_MODE:-public_docs}"

test -d dist || { echo "promote: no dist/ — run npm run build first" >&2; exit 1; }
test -f dist/index.html || { echo "promote: dist/index.html is missing" >&2; exit 1; }
# A promotion that loses the CNAME takes the custom domain down, and a
# promotion that loses .nojekyll makes Pages strip every _astro/ asset — the
# whole stylesheet and script set — from the served site. Both are copied from
# public/ by Astro; assert them rather than trust them.
test -f dist/CNAME || { echo "promote: dist/CNAME is missing — the custom domain would go down" >&2; exit 1; }
test -f dist/.nojekyll || { echo "promote: dist/.nojekyll is missing — Pages would strip _astro/" >&2; exit 1; }
test -f dist/site-manifest.json || { echo "promote: dist/site-manifest.json is missing — run scripts/make_manifest.py" >&2; exit 1; }

python3 verify_site.py dist --mode "$MODE"

rm -rf docs
cp -R dist docs

echo "promoted dist/ to docs/ in mode $MODE; review the diff, then commit docs/ with an explicit pathspec"
