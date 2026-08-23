import raw from '../../data/public/snippets/AGENTS.md?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/markdown; charset=utf-8' },
  });
