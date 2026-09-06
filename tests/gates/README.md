# Driving the gates to a known positive

A gate that has never been made to fail has not been shown to be able to fail.
Both scripts here take the tree as it stands, break exactly one thing, and check
that the refusal arrives — then put it back.

```sh
python3 tests/gates/plant_violations.py    # 48 planted violations + a control
node    tests/gates/gate_c_refusals.mjs    # every gate (c) refusal + a control
python3 -m unittest discover -s tests      # includes test_new_gates.py and
                                           # test_release_sync.py, below
```

Each exits non-zero if any planted violation goes uncaught **or if the control
build is refused**. The control matters as much as the plants: a verifier that
refuses everything catches every violation and is useless.

Neither script writes to `dist/`, `docs/` or `src/`. `plant_violations.py`
copies the artifact and the source into a temporary directory and mutates the
copy.

When you add a gate, add a plant for it in the same change. The eight labelled
`NEW` in the first round were added because a real defect got past the gates
that existed: reader-visible text injected through CSS `content:`, a foreign
syntax palette arriving with a Shiki theme, a colour Expressive Code derived on
its own, unreachable JavaScript in the served directory, the banned status grade
returning to a machine record, and the on-page snippet drifting from the file it
claims to reproduce byte for byte.

## How a plant is judged

`@plant` takes three forms, and the difference between them is the difference
between a test that means something and one that only looks like it does.

- **Bare** — `@plant("label")`. The verifier exited nonzero. That is enough only
  while the rest of the tree is clean, and it stops being enough the moment ANY
  unrelated failure exists: every plant then "passes" while proving nothing.
  This is how all of the first round is written, and it is why the control line
  at the bottom of the run has to be read before the plant lines above it.
- **`expect="…"`** — a refusal naming this plant must appear in the output. A
  plant judged this way stays meaningful while the tree is red, which is the
  state a repository is in for most of the time anybody is working in it. Every
  plant added for gates (i), (j) and (k) is written this way.
- **`absent="…"`** — no refusal naming this string may appear. This is how a
  NEGATIVE control is written. There is one: the `{/* not-yet-shipped */}`
  marker, which must make an otherwise-refused block acceptable. Without it the
  command gate could be refusing every `kaleidoscope` line unconditionally and
  every positive plant would still pass.

Plants that append to `/docs/privacy/` do so on purpose. That page has no fenced
commands of its own, so a refusal naming it can only be the plant's; a `sub()`
anchored to a sentence in a CLI page breaks the moment somebody rewrites the
sentence, and a broken plant reads as a broken gate.

## The three gates added after the 0.0.5 audit

`verify_site.py` calls them (i), (j) and (k), and all three read the authored
source rather than the built artifact, because each one names a file a person
has to open.

- **(i) the command gate.** Every fenced shell line invoking `kscope` must name
  a verb the shipped binary has. The allowed surface is data, not a literal in
  the verifier: it lives in `src/data/kscope-surface.json`, measured against the
  published 0.0.5 build, so the person who changes the binary edits a file they
  can find. A line invoking `kaleidoscope` — a second program, built only inside
  the product repository and published on no channel — must sit in a block
  preceded by `{/* not-yet-shipped */}` on a line of its own. That marker is an
  MDX comment: it renders nothing, and it is a statement by the author that the
  block was written knowingly. It is not a substitute for telling the reader in
  prose, which no gate can check.
- **(j) the availability gate.** No page may say the product cannot be had while
  `public-docs-release.json` says `available_with_key`. The list of phrasings is
  a smoke alarm, not a proof — read the comment above it in `verify_site.py`.
- **(k) the version gate.** The release version is stated as a fact in exactly
  one authored file, and any pin that names Kaleidoscope must match the release
  record wherever it stands.

`test_new_gates.py` drives all three directly, with a scrap of authored text
rather than a whole tree, and asserts both halves: what each gate refuses and
what it must go on accepting.

## The release sync

`scripts/sync_from_release.py --check` is the gate that runs first in CI. The
engine repository is private and is the only writer of `release-pin.json`; the
check recomputes every file derived from that pin -- `public-docs-release.json`,
the vendored skill, snippets and help text, and the three machine records under
`src/data` -- offline, and refuses by name on any difference.

`test_release_sync.py` drives it the way `plant_violations.py` drives the
verifier: copy the tree, assemble a release-assets directory from the copy's
own vendored files, run `--apply` against it, and confirm the unmodified result
is ACCEPTED. Then one thing at a time: one byte of the vendored `SKILL.md`, the
version in `status.json`, the pin itself removed, a manifest whose digest
disagrees with its own asset, an asset carrying a developer path. Each must be
REFUSED with a message naming the file, and a refused `--apply` must leave the
tree exactly as it found it.
