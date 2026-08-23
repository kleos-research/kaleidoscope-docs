import { DOMAIN, indexableEntries, routeOf } from './_site';

/**
 * Written here rather than by `@astrojs/sitemap`, because the verifier asserts
 * that the sitemap URL set equals the indexable route set exactly and the
 * integration will not honour that. No `lastmod`: a date that is not read off
 * the release record would be a build clock.
 */
export async function GET() {
  const entries = await indexableEntries();
  const urls = entries
    .map((entry) => `  <url><loc>${DOMAIN}${routeOf(entry)}</loc></url>`)
    .join('\n');
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>
`;
  return new Response(xml, {
    headers: { 'content-type': 'application/xml; charset=utf-8' },
  });
}
