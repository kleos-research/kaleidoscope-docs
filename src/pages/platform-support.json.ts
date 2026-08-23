import raw from '../data/platform-support.json?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
