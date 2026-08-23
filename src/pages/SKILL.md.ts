import raw from '../data/public/SKILL.md?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/markdown; charset=utf-8' },
  });
