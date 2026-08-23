import raw from '../../data/kaleidoscope-cli.txt?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
