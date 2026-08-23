import raw from '../../data/legal/SUPPORT-POLICY.txt?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
