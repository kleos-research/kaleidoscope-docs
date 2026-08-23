import raw from '../../data/legal/CC-BY-4.0.txt?raw';

export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
