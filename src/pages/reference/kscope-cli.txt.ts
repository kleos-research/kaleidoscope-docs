import raw from '../../data/kaleidoscope-cli.txt?raw';

/*
 * The canonical name for the served help text.
 *
 * The file behind it is `kscope --help`, printed by the executable the npm
 * package installs. It used to be a hand-typed copy of a second program's
 * help, and the route was named after that program; the bytes are now the
 * shipped one's, so the route is named after the command a reader types.
 * `/reference/kaleidoscope-cli.txt` still resolves, and serves these same
 * bytes, because links to it are already published.
 */
export const GET = () =>
  new Response(raw, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
