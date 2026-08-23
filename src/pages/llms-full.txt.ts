import { DOMAIN, PROVENANCE_ROUTES, indexableEntries, routeOf } from './_site';
import { body as llms } from './llms.txt';
import release from '../../public-docs-release.json';

import skill from '../data/public/SKILL.md?raw';
import cliHelp from '../data/kaleidoscope-cli.txt?raw';
import toolReference from '../data/mcp-reference.json?raw';
import statusRecord from '../data/status.json?raw';
import platformSupport from '../data/platform-support.json?raw';
// The text mirror carries the same chrome the HTML does. Banner.astro paints
// this band on a `legalDraft` page; without it here, a model reading
// llms-full.txt would take an unreviewed draft for settled terms.
import legalDraftNotice from '../data/legal-draft-notice.txt?raw';
// Two variants, same reason Banner.astro has two: the licences INDEX is about
// Apache-2.0 and CC BY 4.0 BEING in force, so the document band contradicts it.
import legalIndexNotice from '../data/legal-index-notice.txt?raw';

const status = JSON.parse(statusRecord) as {
  'as of': string;
  hosts: {
    hosts: {
      name: string;
      version?: string;
      confirmed: string;
      'not confirmed': string;
    }[];
  };
};

/**
 * Values the pages print through an expression.
 *
 * An expression is not prose and cannot survive a text mirror, so the two
 * scalars a page actually prints are resolved here rather than deleted. Both
 * come from the same records the page reads, so this cannot drift into stating
 * something the page does not.
 */
const EXPRESSION_VALUES: [RegExp, string][] = [
  [/\{status\['as of'\]\}/g, status['as of']],
  [/\{release\.release_version\}/g, release.release_version],
];

/**
 * The one table a page builds from JSON rather than writing out.
 *
 * `/status/` renders these rows from `status.json` so the page and the record
 * cannot disagree. Deleting the expression would delete the rows, so they are
 * rebuilt here from the same source, in the place the page puts them.
 */
const HOST_ROWS_ANCHOR = 'From the command line, on that Mac:';
function hostRows(): string {
  const rows = status.hosts.hosts.map((host) => {
    const name = host.version ? `${host.name} ${host.version}` : host.name;
    return `- ${name} — what happened: ${host.confirmed}. What did not: ${host['not confirmed']}.`;
  });
  return rows.join('\n');
}

/**
 * Balanced-brace removal.
 *
 * A regex for `{...}` matches only the innermost pair, so a multi-line
 * expression leaks its outer text into the mirror as raw source. This counts
 * depth instead, which is the whole reason it is not a one-line replace.
 */
function stripExpressions(text: string): string {
  let out = '';
  let depth = 0;
  for (const character of text) {
    if (character === '{') {
      depth += 1;
      continue;
    }
    if (character === '}') {
      if (depth > 0) depth -= 1;
      continue;
    }
    if (depth === 0) out += character;
  }
  return out;
}

/**
 * MDX to plain text.
 *
 * Fenced code survives untouched — a marker comment inside a fence is the point
 * of the skill page, and a tag-stripping pass would eat it. Everything outside a
 * fence loses its imports, its component tags and its expressions.
 */
function plainText(source: string): string {
  return source
    .split(/(^```[\s\S]*?^```$)/m)
    .map((part, index) => {
      if (index % 2 === 1) return part;
      let text = part.replace(/^import\s[^\n]*\n/gm, '');
      for (const [pattern, value] of EXPRESSION_VALUES) {
        text = text.replace(pattern, value);
      }
      // A download card is a file offer; keep the name and the URL, which are
      // the only two things a reader of this file can act on.
      text = text.replace(
        /<DownloadCard\s+href="([^"]+)"\s+name="([^"]+)"\s*>/g,
        (_match, href, name) => `${name} — ${DOMAIN}${href}`,
      );
      return stripExpressions(text)
        .replace(/<\/?[A-Za-z][^>]*>/g, '')
        .replace(/^:::[^\n]*$/gm, '')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    })
    .join('')
    .replace(/[ \t]+$/gm, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

export async function GET() {
  const entries = await indexableEntries();
  const chunks: string[] = [llms.trim()];

  for (const entry of entries) {
    const route = routeOf(entry);
    const releaseLine = PROVENANCE_ROUTES.has(route)
      ? `Release: ${release.release_version}\n`
      : '';
    const data = entry.data as Record<string, unknown>;
    // The four product-terms drafts are `noindex` and `indexableEntries` drops
    // them, so today only the licences index reaches this mirror and the
    // `legalDraftNotice` arm is unreachable. Keep it: a draft that ever becomes
    // indexable must arrive with its band, not without one.
    const notice = route === '/docs/legal/' ? legalIndexNotice : legalDraftNotice;
    const band = data.legalDraft === true ? `${notice.trim()}\n\n` : '';

    let text = plainText(entry.body ?? '');
    if (route === '/status/') {
      if (!text.includes(HOST_ROWS_ANCHOR)) {
        throw new Error(
          'llms-full.txt: the /status/ host-row anchor moved. The rows would ' +
            'be silently dropped from the text mirror; fix the anchor.',
        );
      }
      text = text.replace(
        HOST_ROWS_ANCHOR,
        `${HOST_ROWS_ANCHOR}\n\n${hostRows()}`,
      );
    }

    chunks.push(
      `# ${entry.data.title}\n\nURL: ${DOMAIN}${route}\n${releaseLine}Updated: ${release.updated_at}\n\n${band}${text}`,
    );
  }

  chunks.push(
    `# Public agent skill\n\nURL: ${DOMAIN}/SKILL.md\n\n${skill.trim()}`,
    `# Full CLI help text\n\nURL: ${DOMAIN}/reference/kaleidoscope-cli.txt\n\n${cliHelp.trim()}`,
    `# Tool reference\n\nURL: ${DOMAIN}/reference/kaleidoscope-mcp.json\n\n${toolReference.trim()}`,
    `# Status record\n\nURL: ${DOMAIN}/status.json\n\n${statusRecord.trim()}`,
    `# Platform support record\n\nURL: ${DOMAIN}/platform-support.json\n\n${platformSupport.trim()}`,
  );

  return new Response(`${chunks.join('\n\n---\n\n')}\n`, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
}
