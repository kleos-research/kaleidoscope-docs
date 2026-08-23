import { DOMAIN, isLocalBuild } from './_site';

const body = isLocalBuild
  ? 'User-agent: *\nDisallow: /\n'
  : `User-agent: *\nAllow: /\nSitemap: ${DOMAIN}/sitemap.xml\n`;

export const GET = () =>
  new Response(body, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
