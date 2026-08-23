// Gate (c): release metadata, fail closed. Every refusal, plus the control
// that must ACCEPT — a gate that only ever refuses is not a gate either.
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const { readReleaseMetadata } = await import(new URL('../../scripts/release-metadata.mjs', import.meta.url).href);

const dir = mkdtempSync(join(tmpdir(), 'gatec-'));
const VALID = JSON.parse(
  (await import('node:fs')).readFileSync(new URL('../../public-docs-release.json', import.meta.url), 'utf8'));

const run = (label, mode, obj, expect) => {
  let file;
  if (obj === null) { file = '/nonexistent/release.json'; }
  else { file = join(dir, `${Math.random().toString(36).slice(2)}.json`);
         writeFileSync(file, typeof obj === 'string' ? obj : JSON.stringify(obj)); }
  const prev = process.env.KALEIDOSCOPE_DOCS_RELEASE;
  process.env.KALEIDOSCOPE_DOCS_RELEASE = file;
  let verdict, detail = '';
  try { readReleaseMetadata(mode); verdict = 'ACCEPTED'; }
  catch (e) { verdict = 'REFUSED'; detail = String(e.message).split('\n')[0]; }
  if (prev === undefined) delete process.env.KALEIDOSCOPE_DOCS_RELEASE;
  else process.env.KALEIDOSCOPE_DOCS_RELEASE = prev;
  const ok = verdict === expect;
  console.log(`  [${ok ? 'OK  ' : 'MISS'}] ${label.padEnd(52)} ${verdict}${detail ? '  ' + detail : ''}`);
  return ok;
};

let all = true;
console.log('gate (c) — release metadata, fail closed\n');
all &= run('CONTROL: valid metadata, public_docs', 'public_docs', VALID, 'ACCEPTED');
all &= run('(1) no metadata file, public_docs', 'public_docs', null, 'REFUSED');
all &= run('(1) no metadata file, production', 'production', null, 'REFUSED');
all &= run('(1) no metadata file, staging (placeholders)', 'staging', null, 'ACCEPTED');
all &= run('(2) an extra field', 'public_docs', {...VALID, notes: 'x'}, 'REFUSED');
all &= run('(2) a missing field', 'public_docs',
  (({release_version, availability}) => ({release_version, availability}))(VALID), 'REFUSED');
all &= run('(3) a non-string value', 'public_docs', {...VALID, updated_at: 20260822}, 'REFUSED');
all &= run('(4) availability wrong for the mode', 'public_docs', {...VALID, availability: 'nonsense'}, 'REFUSED');
all &= run('(5) a MOVING release version', 'public_docs', {...VALID, release_version: 'latest'}, 'REFUSED');
all &= run('(6) an uppercase contract digest', 'public_docs',
  {...VALID, public_contract_sha256: String(VALID.public_contract_sha256).toUpperCase()}, 'REFUSED');
all &= run('(6) a date that is not YYYY-MM-DD', 'public_docs', {...VALID, updated_at: '22 Aug 2026'}, 'REFUSED');
all &= run('malformed JSON', 'public_docs', '{not json', 'REFUSED');
console.log(`\n  all gate (c) refusals behaved: ${!!all}`);
process.exit(all ? 0 : 1);
