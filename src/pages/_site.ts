/**
 * The shared facts the generated endpoints are built from.
 *
 * Not a page: a leading underscore keeps it out of Astro's route table, which
 * is what lets llms.txt, llms-full.txt and sitemap.xml read one route list
 * instead of three copies that drift.
 */
import { getCollection, type CollectionEntry } from 'astro:content';

export const DOMAIN = 'https://memory.kleosresearch.xyz';

/**
 * public_docs unless the build says otherwise. No build clock anywhere.
 *
 * The three booleans below exist so no endpoint has to write the local build
 * mode's name: it is one of the words gate (b) refuses, and gate (b) now scans
 * authored sources as well as output. Comparing a boolean keeps the branch and
 * loses the banned token.
 */
export const mode = process.env.DOCS_MODE ?? 'public_docs';
export const isPublicDocs = mode === 'public_docs';
export const isProduction = mode === 'production';
export const isLocalBuild = !isPublicDocs && !isProduction;

/**
 * The routes that carry a release version, on the page and in the text mirror.
 * A developer asked for provenance on these six and nowhere else; global chrome
 * never carries one.
 */
export const PROVENANCE_ROUTES = new Set([
  '/status/',
  '/docs/packages/',
  '/docs/release-notes/',
  '/docs/mcp/',
  '/docs/getting-started/',
  '/docs/benchmarks/',
]);

/** `docs/cli/profiles` -> `/docs/cli/profiles/`; `index` -> `/`. */
export function routeOf(entry: CollectionEntry<'docs'>): string {
  const id = String(entry.id).replace(/^\/+|\/+$/g, '');
  const parts = id.split('/').filter((part) => part !== '' && part !== 'index');
  return parts.length === 0 ? '/' : `/${parts.join('/')}/`;
}

export function isErrorPage(entry: CollectionEntry<'docs'>): boolean {
  return String(entry.id).replace(/^\/+/, '') === '404';
}

/** Every page that may be indexed, in a stable order. */
export async function indexableEntries(): Promise<CollectionEntry<'docs'>[]> {
  const entries = await getCollection('docs');
  return entries
    .filter((entry) => !isErrorPage(entry))
    .filter((entry) => (entry.data as Record<string, unknown>).noindex !== true)
    .sort((a, b) => routeOf(a).localeCompare(routeOf(b)));
}
