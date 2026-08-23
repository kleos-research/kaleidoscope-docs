/**
 * Gate (c): release metadata, read fail-closed at Astro config evaluation.
 *
 * Ported refusal for refusal from `load_metadata` in the deleted
 * `build_site.py`; read it in git history at the migration commit if a message
 * here ever needs its original.
 *
 * This is imported at MODULE SCOPE by `astro.config.mjs` on purpose. A refusal
 * raised inside an integration hook can be caught and downgraded to a warning
 * by something upstream; a throw during config evaluation cannot. The build
 * stops before Vite starts.
 *
 * Every refusal below carries its OWN message. The old generator gave several
 * of them one shared sentence, which is why the CI negative test could only
 * assert "it exited nonzero" — a pass condition that is satisfied hardest when
 * the check itself is broken, because an ImportError also exits nonzero. The
 * tests in tests/test_docs.py assert the message, not just the exit status.
 */
import { readFileSync } from 'node:fs';

const MODES = new Set(['staging', 'public_docs', 'production']);
const FIELDS = ['availability', 'public_contract_sha256', 'release_version', 'updated_at'];
const HEX64 = /^[0-9a-f]{64}$/;
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;
const PLACEHOLDER_VERSIONS = ['', 'unreleased', 'latest'];

/**
 * The staging placeholders. Both `unreleased` and `not-yet-bound` are
 * PRODUCTION_BLOCKERS in verify_site.py, so a staging artifact is poisoned
 * against a production build by its own values. Do not tidy either string
 * without changing that list.
 *
 * `updated_at` is a placeholder rather than a date on purpose: there is no
 * build clock anywhere on this site. A date taken from the wall clock makes two
 * builds of the same source differ, and the recursive diff between `dist/` and
 * the committed `docs/` is what enforces the reviewed-artifact guarantee.
 */
const STAGING = Object.freeze({
  release_version: 'unreleased',
  public_contract_sha256: 'not-yet-bound',
  availability: 'staging',
  updated_at: 'unreleased',
});

/** The build mode, from $DOCS_MODE. Defaults to public_docs, as `npm run build` does. */
export function releaseMode() {
  const mode = process.env.DOCS_MODE || 'public_docs';
  if (!MODES.has(mode)) throw new Error(`unknown documentation build mode: ${mode}`);
  return mode;
}

/**
 * $KALEIDOSCOPE_DOCS_RELEASE exists so the negative tests can point a build at
 * a file that is not there. It is not a way to supply different metadata to a
 * real build.
 */
export function releaseMetadataPath() {
  return process.env.KALEIDOSCOPE_DOCS_RELEASE ?? 'public-docs-release.json';
}

export function readReleaseMetadata(mode = 'staging') {
  if (!MODES.has(mode)) throw new Error(`unknown documentation build mode: ${mode}`);

  // A staging build that was handed no metadata uses the placeholders, and does
  // NOT quietly pick up the public-docs file that happens to sit in the tree.
  // The old generator behaved this way because the path arrived as an explicit
  // argument; here the default path would otherwise stamp a staging artifact
  // with `documentation_preview`, which verify_site.py refuses — correctly, and
  // for a reason nobody would have guessed from the message.
  if (mode === 'staging' && !process.env.KALEIDOSCOPE_DOCS_RELEASE) {
    return { ...STAGING };
  }

  const path = releaseMetadataPath();
  let raw;
  try {
    raw = readFileSync(path, 'utf8');
  } catch {
    // (1) no metadata file at all. A staging build may run without one;
    //     nothing that could be published may.
    if (mode !== 'staging') {
      throw new Error(`${mode} build requires immutable release metadata`);
    }
    return { ...STAGING };
  }

  let data;
  try {
    data = JSON.parse(raw);
  } catch (error) {
    throw new Error(`release metadata at ${path} is not valid JSON: ${error.message}`);
  }
  if (data === null || typeof data !== 'object' || Array.isArray(data)) {
    throw new Error(`release metadata at ${path} is not a JSON object`);
  }

  // (2) exactly the four fields. An extra key fails as loudly as a missing one:
  //     it is either a typo for a field that is now absent, or a second source
  //     of truth that nothing validates.
  const keys = Object.keys(data).sort();
  const sameSet = keys.length === FIELDS.length && keys.every((k, i) => k === FIELDS[i]);
  if (!sameSet) {
    const missing = FIELDS.filter((k) => !keys.includes(k));
    const extra = keys.filter((k) => !FIELDS.includes(k));
    throw new Error(
      'release metadata must contain exactly four fields ' +
        `(${FIELDS.join(', ')}); missing=[${missing.join(', ')}] extra=[${extra.join(', ')}]`
    );
  }

  // (3) every value is a string.
  const nonString = FIELDS.filter((k) => typeof data[k] !== 'string');
  if (nonString.length) {
    throw new Error(`release metadata field ${nonString.join(', ')} must be a string`);
  }

  if (mode !== 'staging') {
    // (4) availability must match the mode.
    const allowed =
      mode === 'public_docs'
        ? ['documentation_preview']
        : ['release_candidate', 'released'];
    if (!allowed.includes(data.availability)) {
      throw new Error(`${mode} build has an invalid availability value`);
    }
    // (5) a moving name is not a release identity.
    if (PLACEHOLDER_VERSIONS.includes(data.release_version)) {
      throw new Error(`${mode} build requires an immutable release version`);
    }
    // (6) digest shape, then date shape.
    if (!HEX64.test(data.public_contract_sha256)) {
      throw new Error(`${mode} build requires a lowercase 64-hex public contract digest`);
    }
    if (!ISO_DATE.test(data.updated_at) || Number.isNaN(Date.parse(data.updated_at))) {
      throw new Error('updated_at must be YYYY-MM-DD');
    }
  }

  return { ...data };
}

export default readReleaseMetadata;
