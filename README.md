# Kaleidoscope documentation

This repository builds the public documentation site served at
`memory.kleosresearch.xyz`. It contains no product source.

## Toolchain

The site is [Astro Starlight](https://starlight.astro.build/). The repository
therefore needs **Node**, which it did not before this migration — it used to
need nothing but the Python standard library. Calling that out is the point of
this section:

- The Node version is pinned exactly, in `.nvmrc` and in `package.json`'s
  `engines`. Not a range. See "the reviewed-artifact guarantee" below for why.
  `engines` alone is **advisory** — npm warns `EBADENGINE` and installs anyway —
  so `.npmrc` sets `engine-strict=true` and the pin refuses. Without that, the
  precondition the reviewed-artifact guarantee rests on was documented and
  unenforced, and every local build silently proceeded on whatever Node was
  present.
- `npm ci` installs the dependencies pinned by `package-lock.json`, from npm.
  **`npm install` is forbidden** in CI and in the promotion path: it may resolve
  a different tree than the lock file pins, and a different tree can emit
  different bytes.
- The verification half stayed Python, standard library only, no dependencies:
  `verify_site.py`, `scripts/make_manifest.py`, `tests/`.

The old sentence *"Building it performs no network access, no login, no
publication and no deployment"* is no longer true at `npm ci`, and is replaced
by: **building it installs pinned dependencies from npm and does nothing else —
no login, no publication, no deployment.**

```sh
npm ci
npm run build      # clean -> astro build -> site-manifest.json -> verify_site.py
npm run promote    # dist/ -> docs/, the artifact GitHub Pages serves
python3 -m unittest discover -s tests -v
```

`npm run build` writes `dist/`, which is gitignored. `docs/` is produced **only**
by `npm run promote` and is never hand-edited.

## What the site says, and the rule that governs it

Kaleidoscope is not released. Every page states status as **what a reader can
and cannot do** — not as what an internal check verified. Concretely:

- Never claim something works that has not been run. `/status/` is the single
  place that says what has been run, on what, and what has not.
- The five status words (`Tested`, `Partly tested`, `Compiler-checked only`,
  `Untested`, `Not available`) **no longer appear in reader-facing prose.** They
  govern the machine records only — `src/data/status.json` and
  `src/data/platform-support.json` — which is the one place they were ever
  accurate. Pages state availability plainly instead. A `partly tested` row in
  the record must still say which part, and a test enforces it.
- A compiler check is not a build. Four platforms have had a compiler check for
  the memory engine and nothing else: nothing was assembled into a program for
  them and nothing has ever run there. Calling that "builds for this target"
  reads as a working build and is the one claim this repository has already had
  to retract. `/docs/compatibility/` says Kaleidoscope *targets* those
  platforms, and the verb is deliberate.
- Pre-release honesty is required, not optional. Say plainly that nothing
  installs from a registry, nothing is signed, sign-in does not work, and the
  product terms are unreviewed drafts. The status strip carrying the first of
  these is now checked on every page rather than trusted.
- Benchmark results are stated in plain words; the full method is not published
  yet, and **no page carries a statistic** — no confidence interval, no p-value,
  no "significant", no "±". Accuracy comes from choosing claims that need no
  caveat, not from adding caveats.
- Our internal release process does not appear anywhere. `verify_site.py`
  enforces this with a vocabulary scan over every published file **and over the
  authored source**; see `BANNED_VOCABULARY` and the exemptions beside it.

## Where things live

| what | where |
| --- | --- |
| page content | `src/content/docs/**` |
| verbatim republished sources and machine records | `src/data/**` |
| theme, components, plugins | `src/styles/`, `src/components/`, `src/plugins/` |
| the served artifact | `docs/`, generated — never hand-edited |
| the gates | `verify_site.py`, `scripts/release-metadata.mjs`, `tests/` |

### What the migration removed, and what kept its job

`build_site.py` — the 117 KB bespoke generator this site used to be built by —
**is deleted**, along with the artifact it wrote by hand at the repository root
(`index.html`, `assets/site.css`) and six files that were byte-identical
duplicates of live sources (`assets/kaleidoscope-og.png`, `legal/*.txt`, the
four favicons). Starlight replaces the generator; `public/` and `src/data/`
hold the assets. Two generators in one tree is one editable second source for
every page's copy, and the second one wins any argument about what the site
says because nothing builds it and nothing checks it.

`verify_site.py` and `tests/` **kept their jobs and are not the old files
renamed** — the four safety gates have no Starlight equivalent, so they were
ported to run as post-build checks over Starlight output. `docs/` also keeps its
job: it is what GitHub Pages serves. Its *contents* are now written only by
`npm run promote`.

One deliberate non-deletion: the `CNAME` at the repository root is a leftover
duplicate of `public/CNAME`, and Pages serves `main:/docs`, so it should be
inert. It is kept because the two agree, it costs 25 bytes, and being wrong
about which CNAME the custom domain reads takes the domain down. Remove it once
the Pages source is confirmed in the repository settings.

The four product terms under `src/data/legal/` and the agent skill at
`src/data/public/SKILL.md` are republished verbatim from their sources and are
not edited from here. `site-manifest.json` binds each of them to the sha256 of
the source it claims to reproduce, so an edit made "just on the website" fails
the build.

## The four gates

`python3 verify_site.py <root> --mode {staging|public_docs|production}` runs over
`dist/` before promotion and over `docs/` in CI.

- **(a) Private markers.** No developer path, worktree path or internal
  identifier in anything published. It scans every file that decodes as UTF-8 —
  JavaScript chunks included — plus the source tree, so a leak is caught before
  it is built rather than after it is committed.
- **(b) Banned vocabulary.** The internal register must not return. Exemptions
  cover the verbatim-republished files only, and every exemption must name a
  file that actually exists: an exemption for a path that moved keeps covering
  nothing, silently.
- **(c) Release metadata, fail closed.** `scripts/release-metadata.mjs` is
  imported at module scope by `astro.config.mjs`, so its six refusals throw
  before Vite starts. Each refusal has its own message, and the tests assert the
  message rather than only the exit status.
- **(d) The reviewed-artifact guarantee.** Below.

Two more exist because Astro can fail in a way the old Python emitter could not:
**(e) content presence** — `astro build` exits 0 while emitting structurally
valid pages with empty bodies if an Expressive Code plugin throws — and
**(f)/(h) chrome sentinels**, which require the Kaleidoscope mark and the
pre-release status strip on every page.

## The reviewed-artifact guarantee, and where it weakens

The property is three claims, enforced in three places.

1. **Served equals committed.** GitHub Pages serves the committed bytes from
   `main:/docs`. Enforced by GitHub, unconditionally. **Unchanged.**
2. **Committed equals reviewable.** A human can read, in the pull-request diff,
   what will be served. **This weakens for half the changes, and the half was
   measured rather than guessed.**

   | one edit to | artifact paths that differ |
   | --- | ---: |
   | a sentence in `src/content/docs/**` | **3** — the page, `llms-full.txt`, `site-manifest.json` |
   | a rule in `src/styles/brand.css` | **42** — all 41 HTML files, because the content-hashed stylesheet is renamed in every one, plus the bundle |

   So a **content** diff is as short and as readable as it ever was, and review
   of what the site *says* is untouched. A **presentation** diff is churn a
   person will not read, and for CSS, JavaScript and component changes review
   moves to the source plus a reproducible build. `.gitattributes` therefore
   collapses `docs/_astro/**` and nothing else — an earlier draft collapsed
   `docs/**`, which threw away the readable half too — while the recursive diff
   in CI still compares every collapsed file in full.

   **One weakening that nothing compensates for:** the artifact is not bound to
   the MDX sources. `site-manifest.json`'s `public_source_sha256` covers the 12
   verbatim republished files only, so a reader of the committed tree alone
   cannot tell which source revision produced it. Only CI's rebuild can. That is
   a real reduction against the old model, and it is not mitigated here.
3. **Committed equals a fresh build of the reviewed source.** Enforced by
   `diff --brief --recursive dist docs` plus the per-file sha256 and size in
   `site-manifest.json`. **Unchanged in force, but its precondition is new:**
   reproducibility used to be a property of a stdlib-only Python emitter and is
   now a property of a pinned toolchain. That is why Node is pinned exactly, why
   `npm ci` is mandatory, why `package-lock.json` is committed, why the build
   clears its caches first, and why `astro:assets` and sourcemaps are forbidden.
   The recursive diff is load-bearing rather than ceremonial, and it fails
   closed.

Alternatives not chosen: a **deploy-time build** loses claim 2 entirely, since
nobody ever reviews the deployed bytes; a **committed digest manifest only** is
machine-equivalent to what we chose but also loses claim 2 and does not even
solve the churn; a **bot committing `dist/`** loses claim 2 and puts unreviewed
commits on `main`.

**One thing that is already weaker than it looks, and is not caused by this
migration:** `main` has no required status checks and requires zero approving
reviews. A pull request can merge with the `docs` job red or never run, and
Pages will serve the committed bytes anyway. Until the `docs` job is a required
status check and approvals are raised to 1, claim 3 is advisory. No file in this
repository can fix that; it is a repository setting.

## Modes

`staging` builds with placeholder metadata and disallows indexing.
`public_docs` is the mode the site is published in and requires immutable
release metadata in `public-docs-release.json`. `production` requires it too and
additionally refuses pre-release language, retired tool contracts, private paths
and private repository links. **Building a production artifact is not permission
to publish it.** The staging placeholders `unreleased` and `not-yet-bound` are
themselves production blockers, so a staging artifact is poisoned against a
production build by its own values.

The [documentation license](LICENSE) applies CC BY 4.0 to original documentation
while excluding software, proprietary engine material, trademarks, third-party
content, and the product terms themselves.
