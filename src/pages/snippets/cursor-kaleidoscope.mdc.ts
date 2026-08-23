import raw from '../../data/public/snippets/cursor-kaleidoscope.mdc?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/markdown; charset=utf-8' },
  });
