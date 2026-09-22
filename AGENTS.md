# Instructions for agents

This repository is the public documentation site for Kaleidoscope, served at
https://memory.kleosresearch.xyz. Merging to `main` publishes it. Read
[CONTRIBUTING.md](CONTRIBUTING.md) before you change anything; it gives the
reason for every rule below.

1. **Never edit `docs/` by hand.** Change the source, run `npm run build` and
   then `npm run promote`, and commit the source and `docs/` together.
2. **Install with `npm ci`, never `npm install`**, on the Node version in
   `.nvmrc`. `npm install` can resolve a different tree and change the built
   bytes.
3. **Do not hand-edit the files derived from a Kaleidoscope release** (listed in
   CONTRIBUTING.md under "Files that come from a Kaleidoscope release"), or the
   product terms in `src/data/legal/`. Release files change only through
   `python3 scripts/sync_from_release.py --apply`.
4. **Commit with explicit paths.** Never `git add -A`.
5. **Run what CI runs before you open a pull request**, and read each exit code:

   ```sh
   python3 scripts/sync_from_release.py --check
   npm run build && npm run promote
   python3 -m unittest discover -s tests -v
   python3 tests/gates/plant_violations.py
   node tests/gates/gate_c_refusals.mjs
   diff --brief --recursive dist docs
   ```

6. **Follow "What a page may say" in CONTRIBUTING.md.** In short: state status as
   what a reader can and cannot do; never claim something works unless it has
   been run; never show a command a reader cannot run without saying so; say
   what is missing; give benchmark results without statistics; keep internal
   release vocabulary off the site.
7. **When you add a check to `verify_site.py`, add a planted violation for it**
   in `tests/gates/plant_violations.py` in the same change. See
   [tests/gates/README.md](tests/gates/README.md).
