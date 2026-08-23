/**
 * Expressive Code plugin: give every rendered `<pre>` a tab stop.
 *
 * A code block scrolls horizontally. Without `tabindex`, its clipped content
 * is unreachable by keyboard, and the verifier fails the page for it. A rehype
 * plugin cannot do this: Expressive Code renders outside the Markdown pipeline,
 * so its output never passes through `markdown.rehypePlugins`. The
 * `postprocessRenderedBlock` hook is the only place the emitted tree is visible.
 */
export default function preTabIndexPlugin() {
  return {
    name: 'pre-tabindex',
    hooks: {
      postprocessRenderedBlock: ({ renderData }) => {
        addTabIndex(renderData.blockAst);
      },
    },
  };
}

function addTabIndex(node) {
  if (!node || typeof node !== 'object') return;
  if (node.type === 'element' && node.tagName === 'pre') {
    node.properties = node.properties || {};
    if (node.properties.tabindex === undefined && node.properties.tabIndex === undefined) {
      node.properties.tabindex = '0';
    }
  }
  if (Array.isArray(node.children)) {
    for (const child of node.children) addTabIndex(child);
  }
}
