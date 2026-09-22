# Kaleidoscope documentation

This repository is the source of
[memory.kleosresearch.xyz](https://memory.kleosresearch.xyz), the documentation
site for Kaleidoscope, local memory for AI coding agents. It holds the site
only, built with [Astro Starlight](https://starlight.astro.build/). Kaleidoscope
itself installs from npm as `@kleos-research/kaleidoscope`, and its source is
not here.

## Where the content lives

| What | Where |
| --- | --- |
| Pages, written in MDX | `src/content/docs/` |
| Status records, legal terms, the agent skill, CLI help | `src/data/` |
| Theme, components and plugins | `src/styles/`, `src/components/`, `src/plugins/` |
| `llms.txt`, `llms-full.txt`, sitemap and other generated files | `src/pages/` |
| Images, icons and other static files | `public/` |
| The built site, as it is served | `docs/` |

Some files in `src/data/` are copied from a Kaleidoscope release by a script,
and change only when the site moves to a new release.
[CONTRIBUTING.md](CONTRIBUTING.md) lists them.

## Preview it locally

You need Node.js 22.23.2, the exact version in `.nvmrc`. npm refuses to install
with any other version. The checks also need Python 3.

```sh
npm ci           # install the locked dependencies
npm run dev      # serve the site at http://localhost:4321
```

`npm run dev` reloads pages as you edit them. To see exactly what would be
published, build the site and serve the result:

```sh
npm run build    # build into dist/ and check it
npm run preview  # serve dist/ at http://localhost:4321
```

## How it deploys

GitHub Pages serves the `docs/` folder on the `main` branch. Nothing is built
at deploy time, so a change reaches the site only as committed files in
`docs/`:

1. Edit the source.
2. Run `npm run build`, then `npm run promote` to copy the checked build into
   `docs/`.
3. Commit the source and `docs/` together, and open a pull request.

CI rebuilds the site and fails if the result differs from the committed `docs/`.
Merging to `main` publishes the site.
[CONTRIBUTING.md](CONTRIBUTING.md) explains the build, the checks and the rules
for what a page may say. Agents: read [AGENTS.md](AGENTS.md) first.

## Licence

The documentation is licensed under CC BY 4.0. The Kaleidoscope software, the
product terms, trademarks and third-party material are excluded. See
[LICENSE](LICENSE).
