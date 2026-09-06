import raw from '../../data/kaleidoscope-cli.txt?raw';

/*
 * The older name for the same bytes, kept resolving.
 *
 * `/reference/kscope-cli.txt` is the canonical route now that the file is the
 * help of the executable that ships. This one is not a redirect: a redirect
 * from a static host would have to be an HTML page, and this route is fetched
 * by programs. It serves the identical bytes, so a published link never breaks
 * and never disagrees with the canonical one.
 */
export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
