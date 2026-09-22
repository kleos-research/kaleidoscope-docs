# Working on the documentation site

The [README](README.md) covers previewing the site and how it deploys. This
file explains the rest: why the toolchain is pinned, what the checks enforce,
which files come from a Kaleidoscope release, and what a page may say.

## Toolchain

The site is built with Node.js and checked with Python.

- **Node is pinned to one exact version**, in `.nvmrc` and in the `engines`
  field of `package.json`. The build has to be reproducible (see
  [Why the built site is committed](#why-the-built-site-is-committed)), and a
  different Node can emit different bytes.
- **`engines` alone is only advisory.** npm warns `EBADENGINE` and installs
  anyway, so `.npmrc` sets `engine-strict=true` to make it refuse. The pin must
  also satisfy the lock file: `undici` in the lock needs Node 22.19.0 or newer.
- **Use `npm ci`, never `npm install`.** `npm install` can resolve a different
  dependency tree from the one `package-lock.json` pins, and a different tree
  can emit different bytes. This matters most in CI and when promoting a build.
- **The checks use the Python standard library only**: `verify_site.py`,
  `scripts/make_manifest.py` and `tests/`.

Building installs the pinned dependencies from npm and does nothing else. It
does not log in, publish or deploy anything.

## Building and publishing

```sh
npm ci
npm run build      # clean, astro build, write site-manifest.json, run verify_site.py
npm run promote    # copy dist/ to docs/, the folder GitHub Pages serves
python3 -m unittest discover -s tests -v
```

`npm run build` writes `dist/`, which git ignores. `docs/` is written only by
`npm run promote` and is never edited by hand. Promotion copies the tree the
checks just passed rather than building again, and it refuses if `dist/` is
missing `CNAME` (the custom domain would go down), `.nojekyll` (Pages would drop
every file under `_astro/`) or `site-manifest.json`. Commit `docs/` with an
explicit path, never with `git add -A`.

GitHub Pages serves `main:/docs` at memory.kleosresearch.xyz. The CI workflow,
`.github/workflows/docs.yml`, runs on every pull request and every push to
`main`. It installs with `npm ci`, checks the release files, builds, runs the
tests and the planted-violation drills, and then requires
`diff --brief --recursive dist docs` to find no difference.

## Files that come from a Kaleidoscope release

The site describes one Kaleidoscope release. `release-pin.json` records which
one, and `scripts/sync_from_release.py` derives these files from it:

| File | What it holds |
| --- | --- |
| `release-pin.json` | the release this site describes |
| `public-docs-release.json` | the four fields the build needs: version, date, availability, contract digest |
| `src/data/kaleidoscope-cli.txt` | `kscope --help`, byte for byte |
| `src/data/public/SKILL.md`, `src/data/public/snippets/*` | the skill and the instruction blocks `kscope init` installs |
| `src/data/status.json` | the version, package names, published platforms and date; the rest of the file is written here |
| `src/data/platform-support.json` | the "built and published" rows; the rest is written here |
| `src/data/kscope-surface.json` | the `kscope` verbs, parsed from the help text |
| `scripts/make_manifest.py`, `verify_site.py` | the recorded digests of the republished files |

To move the site to a new release, run
`python3 scripts/sync_from_release.py --apply --release <release assets directory>`,
then build and promote. CI runs the same script with `--check`, offline, and
fails on any derived file that no longer matches the pin, so a hand edit to one
of these files fails by name.

The four product terms in `src/data/legal/` are also republished word for word
from their source, and are not edited here either.

## What a page may say

These rules decide what the site says. They apply to every page and to the
generated text files.

- **Kaleidoscope is published.** `npm install -g @kleos-research/kaleidoscope`
  installs the `kscope` command, and it needs a key to run.
- **State status as what a reader can and cannot do**, not as what an internal
  check verified.
- **Do not claim something works unless it has been run.** `/status/` is the one
  place that says what has been run, on what, and what has not.
- **The five status grades stay in the records.** `Tested`, `Partly tested`,
  `Compiler-checked only`, `Untested` and `Not available` appear only in
  `src/data/status.json` and `src/data/platform-support.json`, the one place they
  were ever accurate. Pages state availability plainly instead. A `partly
  tested` row must still say which part, and a test enforces it.
- **A compiler check is not a build.** Never state the two as one thing. Four
  platform packages are built, published and installable. Three of the four
  targets that once had only a compiler check were later built and published,
  and appear under both headings in `src/data/platform-support.json`. Windows on
  x86_64 has had the compiler check and nothing more. Calling a compiler check
  "builds for this target" reads as a working build, and it is the one claim
  this repository has already had to retract. Neither heading says anything has
  *run* on a platform. That is a third column, and only macOS on Apple Silicon
  is in it.
- **Say what is missing.** Nothing is signed for release. There is no account
  to sign in to and no command that would use one. The product terms are
  reviewed but not yet in force. The full benchmark method is not published.
  Say each of these plainly rather than leaving a reader to infer it. The status
  strip is checked on every page.
- **Never hand a reader a command they cannot run without saying so.** One
  executable ships, `kscope`. `connect`, `disconnect`, `config`, `doctor` and
  `profile use` are verbs of `kaleidoscope`, a second program that is published
  on no channel. The command check in `verify_site.py` compares every fenced
  shell line with the verbs recorded in `src/data/kscope-surface.json`.
- **State benchmark results in plain words, with no statistics**: no confidence
  interval, no p-value, no "significant", no "±". The full method is not
  published yet. Accuracy comes from choosing claims that need no caveat, not
  from adding caveats.
- **Keep the internal release process off the site.** `verify_site.py` scans
  every published file and the authored source for internal vocabulary. See
  `BANNED_VOCABULARY` and the exemptions beside it.

## The checks

`python3 verify_site.py <root> --mode {staging|public_docs|production}` is the
last step of `npm run build`, so it runs over `dist/` before every promotion,
locally and in CI. Its checks are lettered, and a failure names its letter.

- **(a) Private markers.** No developer path, worktree path or internal
  identifier may appear in anything published. It scans every file that
  decodes as UTF-8, JavaScript included, and the source tree too, so a leak is
  caught before it is built rather than after it is committed.
- **(b) Banned vocabulary.** The internal register must not return. Exemptions
  cover only the files republished word for word, and every exemption must name
  a file that exists: an exemption for a path that has moved would silently
  cover nothing.
- **(c) Release metadata, failing closed.** `astro.config.mjs` imports
  `scripts/release-metadata.mjs` at module scope, so its refusals throw before
  Vite starts. Each refusal has its own message, and the tests assert the
  message, not only the exit status.
- **(d) The committed build matches a fresh one.** See the next section.
- **(e) Content presence.** `astro build` exits 0 even when an Expressive Code
  plugin throws and every page is emitted with an empty body. This check
  refuses empty pages.
- **(f) and (h) Page furniture.** Every page must carry the Kaleidoscope mark and
  the status strip.
- **(i) commands, (j) availability and (k) version** read the authored source.
  [tests/gates/README.md](tests/gates/README.md) describes them, and the drills
  that break each check on purpose to prove it can still fail.

## Why the built site is committed

GitHub Pages serves the committed files, and CI proves they are a fresh build of
the reviewed source. That makes three promises.

1. **What is served is what is committed.** Pages serves the committed bytes
   from `main:/docs`. GitHub enforces this, unconditionally.
2. **What is committed can be reviewed.** A reviewer can read, in the pull
   request, what will be served. This holds for content and not for
   presentation, and the difference was measured:

   | One edit to | Built files that change |
   | --- | ---: |
   | a sentence in `src/content/docs/**` | **3**: the page, `llms-full.txt`, `site-manifest.json` |
   | a rule in `src/styles/brand.css` | **42**: all 41 HTML files, because the hashed stylesheet is renamed in each, plus the stylesheet |

   A content diff is short and readable. A presentation diff is churn nobody
   will read, so for CSS, JavaScript and component changes, review moves to the
   source plus a reproducible build. `.gitattributes` therefore collapses
   `docs/_astro/**` in diffs and nothing else. An earlier version collapsed all
   of `docs/**`, which hid the readable half too. The comparison in CI still
   checks every collapsed file in full.

   One weakness has no compensating check: the built site is not tied to the
   MDX sources. The `public_source_sha256` field in `site-manifest.json` covers
   only the 13 files republished word for word, so the committed tree alone
   cannot say which source revision produced it. Only CI's rebuild can.
3. **What is committed is a fresh build of the reviewed source.** CI enforces
   this with `diff --brief --recursive dist docs`, plus the size and SHA-256 of
   every file in `site-manifest.json`. Reproducibility depends on a pinned
   toolchain, which is why Node is pinned exactly, `npm ci` is required,
   `package-lock.json` is committed, the build clears its caches first, and
   `astro:assets` and sourcemaps are not used. The comparison fails closed.

Three alternatives were considered and not chosen. Building at deploy time
loses promise 2 entirely, because nobody reviews the deployed files. Committing
only a manifest of digests is equivalent for machines, but also loses promise 2
and does not reduce the churn. A bot that commits the build loses promise 2 and
puts unreviewed commits on `main`.

**Promise 3 is only advisory until a repository setting changes.** As of
2026-09-22, `main` requires a pull request but no approving review and no
passing status check. A pull request can merge with the `docs` job red, or never
run, and Pages will serve the committed files anyway. Making `docs` a required
status check and requiring one approval would close that. No file in this
repository can do it.

## Build modes

- `staging` builds with placeholder release metadata and tells search engines
  not to index the site.
- `public_docs` is the mode the site is published in. It requires the release
  metadata in `public-docs-release.json`.
- `production` requires that metadata too, and also refuses pre-release
  language, retired tool names, private paths and links to private
  repositories.

Building a production site is not permission to publish it. The staging
placeholders `unreleased` and `not-yet-bound` are themselves refused by a
production build, so a staging build cannot pass for a production one.

## History: the move to Astro Starlight

The site used to be generated by `build_site.py`, a 117 KB Python generator,
into `index.html` and `assets/site.css` at the repository root. The move to
Starlight deleted that generator, that output and six files that were
byte-identical copies of live sources (`assets/kaleidoscope-og.png`,
`legal/*.txt` and the four favicons). Starlight replaces the generator, and
`public/` and `src/data/` hold the assets. Keeping two generators would have
left a second editable source for every page, and the one nothing builds or
checks would win any argument about what the site says.

`verify_site.py` and `tests/` kept their jobs. They are not the old files
renamed: the old checks have no Starlight equivalent, so they were ported to
run over Starlight's output after the build. `docs/` kept its job too. Pages
still serves it, and only `npm run promote` writes it.

The `CNAME` file at the repository root duplicates `public/CNAME`. It was kept
because the two agree, it costs 25 bytes, and a mistake about which `CNAME` the
custom domain reads would take the domain down. On 2026-09-22 the GitHub Pages
settings reported the source as `main:/docs`, so the root copy is unused and
can be removed in a separate change.

`site-manifest.json` binds each file republished word for word, including the
four product terms and `src/data/public/SKILL.md`, to the SHA-256 of the file
it copies. An edit made only on the website therefore fails the build. That
binding compares the published file with a file in this repository, so it
catches an edit to the built page and nothing else. The copies of files authored
elsewhere could still drift from their originals, and they had: the skill and
the three instruction snippets were three versions behind what `kscope init`
actually installs. `PUBLIC_UPSTREAM_SOURCES` in `scripts/make_manifest.py`
closes that gap. Each entry records where the file came from and its SHA-256
when it was taken. The manifest step refuses when the local copy no longer
matches, and `public_upstream_sha256` carries the record into the built site. A
recorded digest cannot notice that the original has moved on, but it makes the
two disagree the moment either side is edited, which is the failure that
actually happened. Every bound file must be listed in exactly one of
`PUBLIC_UPSTREAM_SOURCES`, `UNRECORDED_UPSTREAM` and `AUTHORED_HERE`. A file in
none of them is refused, because a new file that quietly belongs to no list is
how this check would stop working.
