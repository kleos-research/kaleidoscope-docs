/**
 * Wrap every Markdown table in a keyboard-reachable horizontal scroller.
 *
 * The verifier asserts that a clipped scroll container carries a tab stop:
 * a table that scrolls sideways inside a div with no `tabindex` has content
 * no keyboard user can reach. Starlight emits a bare `<table>`, so the wrapper
 * is added here, in the Markdown pipeline.
 *
 * Idempotent: a table already inside `.table-scroll` is left alone.
 */
export default function rehypeTableScroll() {
  return (tree) => {
    visit(tree, null);
  };

  function visit(node, parent) {
    if (!node || typeof node !== 'object') return;
    const children = node.children;
    if (!Array.isArray(children)) return;

    for (let i = 0; i < children.length; i += 1) {
      const child = children[i];
      if (
        child &&
        child.type === 'element' &&
        child.tagName === 'table' &&
        !isScroller(node)
      ) {
        children[i] = {
          type: 'element',
          tagName: 'div',
          properties: { className: ['table-scroll'], tabindex: '0' },
          children: [child],
        };
        visit(child, children[i]);
        continue;
      }
      visit(child, node);
    }
  }

  function isScroller(node) {
    if (!node || node.type !== 'element') return false;
    const className = node.properties && node.properties.className;
    if (!className) return false;
    const list = Array.isArray(className) ? className : String(className).split(/\s+/);
    return list.includes('table-scroll');
  }
}
