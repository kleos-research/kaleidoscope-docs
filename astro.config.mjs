// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

import { readReleaseMetadata } from './scripts/release-metadata.mjs';
import rehypeTableScroll from './src/plugins/rehype-table-scroll.mjs';
import preTabIndexPlugin from './src/plugins/ec-pre-tabindex.mjs';

/**
 * Gate (c): release metadata, fail closed.
 *
 * This runs at CONFIG EVALUATION, before Vite starts. A refusal raised inside
 * an integration hook can be swallowed upstream; a throw here cannot. A
 * public-docs or production build with no immutable release metadata does not
 * emit a partial site — it does not start.
 */
const DOCS_MODE = process.env.DOCS_MODE ?? 'public_docs';
const RELEASE = readReleaseMetadata(DOCS_MODE);
if (!RELEASE.release_version) throw new Error('release metadata carries no version');

const SITE = 'https://memory.kleosresearch.xyz';
const SOCIAL_IMAGE = `${SITE}/assets/kaleidoscope-og.png`;
const SOCIAL_ALT = 'Kaleidoscope — local memory for agents';

/**
 * @astrojs/sitemap is FORBIDDEN (spec pin): the verifier asserts the sitemap
 * URL set equals the indexable route set exactly, and the integration will not
 * honour that. Starlight injects it automatically unless an integration of
 * that name is already present, so this inert stub claims the name and keeps
 * it out. The real /sitemap.xml is generated from the same route table the
 * sidebar uses, by an endpoint in src/pages/.
 */
const noSitemap = { name: '@astrojs/sitemap', hooks: {} };

const meta = (attrs) => ({ tag: 'meta', attrs });
const link = (attrs) => ({ tag: 'link', attrs });

/**
 * The code theme, built from kaleidoscope-dark and nothing else.
 *
 * Every value below is one of the six canonical tokens or one of the three
 * sanctioned extensions in src/styles/brand.css. There is no fourth hue, and
 * the verifier's drifted-token scan will say so if one appears.
 *
 *   --k-ink    #EAE7E0  code, and anything the eye should land on first
 *   --k-body   #C3BFB6  strings, values, punctuation — the quieter run
 *   --k-muted  #8C887F  comments, and only comments
 *
 * A VS Code theme is what Expressive Code takes; this is the smallest one that
 * covers every scope Shiki emits for the languages on this site (bash, json,
 * md, ts, toml). Anything it does not name falls through to `foreground`,
 * which is ink — so an unmapped scope degrades to correct, not to blue.
 */
const CODE_INK = '#EAE7E0';
const CODE_BODY = '#C3BFB6';
const CODE_MUTED = '#8C887F';
const kaleidoscopeCode = {
  name: 'kaleidoscope-dark',
  type: 'dark',
  colors: {
    'editor.background': '#131315',
    'editor.foreground': CODE_INK,
    'editorLineNumber.foreground': CODE_MUTED,
    'editor.selectionBackground': '#2E2E30',
    'terminal.background': '#131315',
    'terminal.foreground': CODE_INK,
  },
  tokenColors: [
    { scope: ['comment', 'punctuation.definition.comment', 'string.comment'], settings: { foreground: CODE_MUTED, fontStyle: 'italic' } },
    { scope: ['string', 'constant.other.symbol', 'meta.embedded.assembly'], settings: { foreground: CODE_BODY } },
    { scope: ['constant.numeric', 'constant.language', 'constant.character', 'constant.other'], settings: { foreground: CODE_BODY } },
    { scope: ['punctuation', 'meta.brace', 'meta.delimiter'], settings: { foreground: CODE_BODY } },
    { scope: ['keyword', 'storage', 'storage.type', 'keyword.operator'], settings: { foreground: CODE_INK } },
    { scope: ['entity.name.function', 'support.function', 'variable.function'], settings: { foreground: CODE_INK } },
    { scope: ['variable', 'variable.other', 'variable.parameter'], settings: { foreground: CODE_INK } },
    { scope: ['entity.name.type', 'entity.name.class', 'support.type', 'support.class'], settings: { foreground: CODE_INK } },
    { scope: ['support.type.property-name.json', 'support.type.property-name'], settings: { foreground: CODE_INK } },
    { scope: ['entity.name.tag', 'entity.other.attribute-name'], settings: { foreground: CODE_INK } },
    { scope: ['markup.heading', 'markup.bold'], settings: { foreground: CODE_INK, fontStyle: 'bold' } },
    { scope: ['markup.inline.raw', 'markup.fenced_code', 'markup.raw'], settings: { foreground: CODE_BODY } },
    { scope: ['markup.underline.link', 'string.other.link'], settings: { foreground: CODE_BODY, fontStyle: 'underline' } },
    { scope: ['invalid', 'invalid.illegal'], settings: { foreground: CODE_INK } },
  ],
};

export default defineConfig({
  site: SITE,
  base: '/',
  trailingSlash: 'always',
  outDir: './dist',
  // NEVER ./docs — Astro empties outDir before building, and a failed build
  // would leave the directory GitHub Pages serves wiped.
  build: { format: 'directory', assets: '_astro', sourcemap: false },
  compressHTML: true,
  // astro:assets is forbidden (spec pin). The no-op service means `sharp` can
  // never enter the output, which keeps the build reproducible across hosts.
  image: { service: { entrypoint: 'astro/assets/services/noop' } },
  // DEPRECATED IN ASTRO 7.2.4 and it warns on every build: "pass them to
  // unified({...}) from @astrojs/markdown-remark directly". It is not migrated
  // here because constructing the processor by hand risks reordering the
  // plugins Starlight injects, and the current form demonstrably works.
  //
  // The danger in a deprecation is that a version bump turns it into a SILENT
  // no-op. That one is covered: verify_site.py fails on a bare <table>, so a
  // dropped table-scroll plugin is a red build, not a page that scrolls
  // sideways on a phone. Driven to a known positive — disabling the plugin
  // produces "a bare <table>" on every page that has one.
  markdown: { rehypePlugins: [rehypeTableScroll] },
  // A sourcemap ships absolute developer paths. It would trip the private
  // marker gate correctly, but only after it had already been committed.
  vite: {
    build: { sourcemap: false },
    // The build mode has to reach the components (Head.astro decides `robots`
    // from it). Injecting it here rather than reading process.env inside a
    // component keeps the value in the config, where it is also the thing that
    // chose the release metadata above.
    define: { 'import.meta.env.PUBLIC_DOCS_MODE': JSON.stringify(DOCS_MODE) },
  },

  integrations: [
    noSitemap,
    starlight({
      title: 'Kaleidoscope',
      description:
        'Local memory for AI agents. Your memory stays in a vault on your machine, and every editor or agent you connect shares one profile through exactly two tools.',
      titleDelimiter: '—',
      favicon: '/favicon.svg',
      // No build clock anywhere: every date on this site comes from
      // public-docs-release.json or src/data/status.json.
      lastUpdated: false,
      credits: false,
      // Off by decision, not by omission: pagefind indexes at build time and
      // ships an index plus a search UI into the committed artifact, which is
      // weight in a diff a human is meant to read. 39 pages do not need it.
      pagefind: false,
      customCss: ['./src/styles/brand.css'],

      components: {
        // The nav lives in the site-title slot: the only header slot that
        // renders on every route, which is what puts the inline mark on
        // every page.
        SiteTitle: './src/components/SiteTitle.astro',
        Head: './src/components/Head.astro',
        Banner: './src/components/Banner.astro',
        // Suppresses the duplicate h1 on the splash route; see the component.
        PageTitle: './src/components/PageTitle.astro',
        Footer: './src/components/Footer.astro',
        // A control that cannot change anything is a lie about the design.
        ThemeSelect: './src/components/Empty.astro',
        // pagefind is off, so the search UI cannot work — but Starlight still
        // BUNDLED it: `ui-core` + `Search`, 96,669 bytes, a mutually-importing
        // pair reachable from 0 of 41 pages. No browser ever fetched it and no
        // reader ever saw it; it was simply committed to the served directory
        // on every deploy. Overriding the component removes it from the graph.
        Search: './src/components/Empty.astro',
      },

      head: [
        // Fonts stay on Google Fonts. Self-hosting them would falsify the
        // third-party-request paragraph on /docs/privacy/, which is a claim
        // about what a visitor's browser does.
        //
        // Newsreader 300 and 500 are requested and never used: `--k-font-serif`
        // is set at weight 400 in the only two rules that use it. It costs
        // nothing — Google serves ONE variable file per family, verified: three
        // woff2 fetched for three families — so this is left alone rather than
        // churned, but do not read the weight list as a statement of intent.
        link({ rel: 'preconnect', href: 'https://fonts.googleapis.com' }),
        link({ rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true }),
        link({
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,300;6..72,400;6..72,500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap',
        }),
        link({ rel: 'icon', href: '/favicon-32.png', sizes: '32x32', type: 'image/png' }),
        link({ rel: 'icon', href: '/favicon.ico', sizes: '16x16 32x32' }),
        link({ rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }),
        // Starlight points this at /sitemap-index.xml, which we do not emit.
        link({ rel: 'sitemap', href: '/sitemap.xml' }),
        meta({ name: 'theme-color', content: '#0B0B0C' }),
        meta({ property: 'og:image', content: SOCIAL_IMAGE }),
        meta({ property: 'og:image:width', content: '1200' }),
        meta({ property: 'og:image:height', content: '630' }),
        meta({ property: 'og:image:alt', content: SOCIAL_ALT }),
        meta({ name: 'twitter:card', content: 'summary_large_image' }),
        meta({ name: 'twitter:image', content: SOCIAL_IMAGE }),
        meta({ name: 'twitter:image:alt', content: SOCIAL_ALT }),
      ],

      expressiveCode: {
        // `github-dark` was the only place in the whole site where a colour
        // from outside the system reached a reader — #e1e4e8 x447, #9ecbff
        // x299, #79b8ff x127, #b392f0 x79 across 19 of 39 pages, none of them
        // in tokens.json. The site this replaces had no syntax highlighting at
        // all (`code { color: var(--ink) }`), so blue and purple in code was
        // new, not inherited.
        //
        // KALEIDOSCOPE_CODE IS DELIBERATELY MONOCHROME AND CARRIES NO BRASS.
        // brand/README.md: "Brass exists nowhere else. It is Kaleidoscope's."
        // Painting every keyword brass would make the accent a syntax colour
        // and dilute the one thing it marks. Three values do all the work —
        // ink for code, body for the quieter runs, muted for comments — which
        // is the same three-step the prose uses. Brass survives only as the
        // active editor tab's indicator, which is chrome, not syntax.
        themes: [kaleidoscopeCode],
        // One theme, so Starlight must not emit a light/dark toggle for it.
        themeCssSelector: () => null,
        useDarkModeMediaQuery: false,
        // EC RAISES CONTRAST BY DERIVING NEW COLOURS, AND THAT IS THE ONE
        // BEHAVIOUR THE BRAND SYSTEM CANNOT HAVE. Its default floor is 5.5:1;
        // --k-muted on --k-raised measures 5.33:1, so it silently shipped
        // #908C83 for every comment — a tenth colour, in nobody's tokens file,
        // that no gate names and no designer chose. 5.33 clears WCAG AA (4.5)
        // and brand.css already states --k-muted is the dimmest value the
        // system permits on text. Turning the lift off makes every colour in
        // every code block exactly one of the nine, which is checkable.
        minSyntaxHighlightingColorContrast: 0,
        styleOverrides: {
          borderRadius: '0',
          borderColor: '#232325',
          codeBackground: '#131315',
          codeFontFamily: 'var(--sl-font-mono)',
          codeFontSize: '12.5px',
          frames: {
            shadowColor: 'transparent',
            terminalBackground: '#131315',
            terminalTitlebarBackground: '#131315',
            // The two editor-tab surfaces were left at the theme default and
            // drew a #24292E / #1f2428 GitHub-slate tab on the one titled
            // frame in the build (/docs/skill/). Pinned to raised.
            editorTabBarBackground: '#131315',
            editorActiveTabBackground: '#131315',
            editorActiveTabForeground: '#EAE7E0',
            editorActiveTabBorderColor: '#232325',
            editorTabBarBorderBottomColor: '#232325',
            editorActiveTabIndicatorTopColor: '#CFA757',
            // Three more EC defaults that were still off-system and DO paint.
            // `terminalTitlebarForeground` shipped #cccccc — a tenth grey, on
            // the title of every terminal frame. The copy button's success
            // tooltip shipped #098656, a green: the only green anywhere in the
            // system, and it appears the moment a reader copies a command,
            // which is the single most-used control on this site.
            terminalTitlebarForeground: '#8C887F',
            terminalTitlebarBorderBottomColor: '#232325',
            // Measured, not assumed: EC paints the copy ICON with the mask
            // colour it calls `inlineButtonBackground`, so this pair reads
            // backwards from its own names. Muted at rest, ink on hover, which
            // is what the rest of the chrome does.
            inlineButtonBackground: '#8C887F',
            inlineButtonForeground: '#EAE7E0',
            inlineButtonBorder: '#232325',
            tooltipSuccessBackground: '#232325',
            tooltipSuccessForeground: '#EAE7E0',
          },
        },
        plugins: [preTabIndexPlugin()],
      },

      // The order below is the sidebar. It names every route BEFORE the pages
      // exist, so a missing page is a build error. That is the forcing
      // function, not an accident.
      sidebar: [
        {
          label: 'Start',
          items: [
            { slug: 'docs' },
            { slug: 'docs/getting-started' },
            { slug: 'docs/skill' },
            { slug: 'docs/packages' },
            { slug: 'docs/ui' },
            { slug: 'docs/concepts' },
          ],
        },
        {
          label: 'CLI',
          items: [
            { slug: 'docs/cli' },
            { slug: 'docs/cli/profiles' },
            { slug: 'docs/cli/connect' },
            { slug: 'docs/cli/instructions' },
            { slug: 'docs/cli/diagnostics' },
            { slug: 'docs/cli/account' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { slug: 'docs/mcp' },
            { slug: 'docs/integrations' },
            {
              label: 'Integrations',
              collapsed: true,
              items: [
                { slug: 'docs/integrations/claude-code' },
                { slug: 'docs/integrations/codex' },
                { slug: 'docs/integrations/cursor' },
                { slug: 'docs/integrations/opencode' },
                { slug: 'docs/integrations/generic-mcp' },
                { slug: 'docs/integrations/claude-agent-sdk' },
                { slug: 'docs/integrations/openai-agents-sdk' },
                { slug: 'docs/integrations/langchain' },
                { slug: 'docs/integrations/langgraph' },
                { slug: 'docs/integrations/crewai' },
              ],
            },
            { slug: 'docs/brand' },
          ],
        },
        {
          label: 'Operate',
          items: [
            { slug: 'docs/operations' },
            { slug: 'docs/account' },
            { slug: 'docs/troubleshooting' },
          ],
        },
        {
          label: 'Boundaries',
          items: [
            { slug: 'docs/security' },
            { slug: 'docs/privacy' },
            { slug: 'docs/legal' },
            {
              label: 'Terms and licences',
              collapsed: true,
              items: [
                { slug: 'docs/legal/engine-eula' },
                { slug: 'docs/legal/privacy-notice' },
                { slug: 'docs/legal/security-policy' },
                { slug: 'docs/legal/support-policy' },
              ],
            },
          ],
        },
        {
          label: 'Availability',
          items: [
            { slug: 'docs/compatibility' },
            { slug: 'docs/benchmarks' },
            { slug: 'docs/release-notes' },
          ],
        },
        { label: 'Status', slug: 'status' },
        {
          label: 'Kleos Research ↗',
          link: 'https://kleosresearch.xyz/',
          attrs: { target: '_blank', rel: 'noopener' },
        },
      ],
    }),
  ],
});
