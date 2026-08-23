import raw from '../../data/public/snippets/CLAUDE.md?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/markdown; charset=utf-8' },
  });
