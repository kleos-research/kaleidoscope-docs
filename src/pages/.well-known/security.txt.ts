import { DOMAIN, isLocalBuild, isPublicDocs } from '../_site';

const heading = isLocalBuild
  ? '# LOCAL BUILD ONLY — no production security intake is published.'
  : isPublicDocs
    ? '# DOCUMENTATION PREVIEW — no production security intake is published.'
    : '# No production security intake is published.';

const body = `${heading}
Contact: ${DOMAIN}/docs/security/
Canonical: ${DOMAIN}/.well-known/security.txt
Expires: 2026-09-30T23:59:59Z
Preferred-Languages: en
Policy: ${DOMAIN}/docs/security/
`;

export const GET = () =>
  new Response(body, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
