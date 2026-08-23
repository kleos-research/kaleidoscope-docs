#!/usr/bin/env python3
"""Clone the verified artifact + source, mutate ONE thing, run the verifier.

A gate that has never been driven to a known positive is a gate that has never
been shown to be able to fail.
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORK = Path(tempfile.mkdtemp(prefix="kdocs-plant-")) / "work"

def fresh():
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    shutil.copytree(REPO / "dist", WORK / "dist")
    for d in ("src", "scripts"):
        shutil.copytree(REPO / d, WORK / d)
    for f in ("verify_site.py", "astro.config.mjs", "public-docs-release.json"):
        shutil.copy2(REPO / f, WORK / f)
    return WORK

def run(mode="public_docs"):
    r = subprocess.run(
        [sys.executable, str(WORK / "verify_site.py"), str(WORK / "dist"),
         "--mode", mode, "--source-root", str(WORK)],
        capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

def show(label, rc, out, expect_fail=True):
    ok = (rc != 0) if expect_fail else (rc == 0)
    lines = [l for l in out.splitlines() if l.startswith("FAIL") or l.startswith("verified")]
    body = "\n".join("      " + l for l in lines[:3]) or "      (no output)"
    print(f"  [{'CAUGHT' if ok else 'MISSED'}] {label}")
    print(body)
    return ok

def sub(path, old, new, count=1):
    p = WORK / path
    t = p.read_text()
    assert old in t, f"anchor not found in {path}: {old[:60]}"
    p.write_text(t.replace(old, new, count))

PLANTS = []
def plant(label):
    def deco(fn):
        PLANTS.append((label, fn)); return fn
    return deco

# ---- gate (a) private markers -------------------------------------------
@plant("(a) developer path in a page")
def _(): sub("dist/docs/concepts/index.html", "<p>", "<p>/Users/someone/ ", 1)

@plant("(a) developer path in a vendor JS chunk")
def _(): (WORK/"dist/_astro/page.Dwipeu-R.js").write_text(
    (WORK/"dist/_astro/page.Dwipeu-R.js").read_text() + '\n//# /Users/x\n')

@plant("(a) the PRIVATE product repo linked from a page")
def _(): sub("dist/docs/index.html", 'href="/docs/skill/"',
             'href="https://github.com/kleos-research/kaleidoscope"', 1)

@plant("(a) developer path in the SOURCE tree, before a build")
def _(): (WORK/"src/styles/brand.css").write_text(
    (WORK/"src/styles/brand.css").read_text() + "\n/* /Users/me/x */\n")

# ---- gate (b) banned vocabulary -----------------------------------------
@plant("(b) internal register in a page")
def _(): sub("dist/docs/security/index.html", "<p>", "<p>This is a staging build. ", 1)

@plant("(b) a build digest in prose")
def _(): sub("dist/docs/release-notes/index.html", "<p>", "<p>Built from 9ff9ef5ce0b1c07aa12f. ", 1)

@plant("(b) internal register in the .mdc snippet")
def _(): (WORK/"dist/snippets/cursor-kaleidoscope.mdc").write_text(
    (WORK/"dist/snippets/cursor-kaleidoscope.mdc").read_text() + "\nRun the smoke pass.\n")

@plant("(b) NEW — reader-visible text injected via CSS content:")
def _():
    css = next((WORK/"dist/_astro").glob("common.*.css"))
    css.write_text(css.read_text() + '.k-nav a[href="/status/"]::after{content:" staging"}')

@plant("(b) NEW — the same, in the authored stylesheet")
def _(): (WORK/"src/styles/brand.css").write_text(
    (WORK/"src/styles/brand.css").read_text() + '\n.x::after{content:" staging";}\n')

@plant("(b) an exemption naming a file the artifact no longer has")
def _(): (WORK/"dist/legal/ENGINE-EULA.txt").rename(WORK/"dist/legal/ENGINE-EULA-RENAMED.txt")

# ---- gate (d) manifest ---------------------------------------------------
@plant("(d) a page edited after the manifest was written")
def _(): sub("dist/docs/mcp/index.html", "<p>", "<p>edited. ", 1)

@plant("(d) an extra route in the artifact")
def _(): (WORK/"dist/docs/rogue.html").write_text("<html><body>rogue</body></html>")

@plant("(d) a republished public source altered on the website")
def _(): (WORK/"dist/SKILL.md").write_text(
    (WORK/"dist/SKILL.md").read_text() + "\nadded here, not at the source\n")

# ---- gate (e) content presence -------------------------------------------
@plant("(e) a page builds clean and ships empty")
def _():
    p = WORK/"dist/docs/privacy/index.html"
    t = p.read_text()
    t = re.sub(r'(<div class="sl-markdown-content">).*?(</div>)', r'\1\2', t, count=1, flags=re.S)
    p.write_text(t)

# ---- gate (f) the mark ---------------------------------------------------
@plant("(f) the Kaleidoscope mark dropped from a page")
def _():
    p = WORK/"dist/docs/security/index.html"
    p.write_text(re.sub(r'<svg class="kaleidoscope-mark".*?</svg>', '', p.read_text(), count=1, flags=re.S))

@plant("(f) the mark's opacity cascade drifts")
def _(): sub("dist/docs/mcp/index.html", 'opacity="0.56"', 'opacity="0.5"', 1)

@plant("(f) the mark is rounded")
def _(): sub("dist/docs/mcp/index.html", '<rect x="28.5"', '<rect rx="2" x="28.5"', 1)

# ---- gate (h) the status strip -------------------------------------------
@plant("(h) the pre-release status strip is dropped")
def _(): sub("dist/docs/getting-started/index.html",
             "Kaleidoscope is not publicly released", "Kaleidoscope is available", 1)

# ---- legal ----------------------------------------------------------------
@plant("legal: the review-draft band removed from a draft")
def _(): sub("dist/docs/legal/privacy-notice/index.html",
             "not been reviewed by legal counsel", "been reviewed by legal counsel", 1)

@plant("legal: an overclaim, WRAPPED ACROSS A LINE BREAK")
def _(): sub("dist/docs/legal/support-policy/index.html", "<p>",
             "<p>These terms have been reviewed by legal\n      counsel. ", 1)

@plant("legal: the draft band renders after the article")
def _():
    p = WORK/"dist/docs/legal/engine-eula/index.html"
    t = p.read_text()
    m = re.search(r'<div class="notice-band">.*?</div>', t, re.S)
    t = t.replace(m.group(0), "", 1).replace("</main>", m.group(0) + "</main>", 1)
    p.write_text(t)

# ---- brand / theme --------------------------------------------------------
@plant("theme: a drifted token reaches the bundle")
def _():
    css = next((WORK/"dist/_astro").glob("common.*.css"))
    css.write_text(css.read_text().replace("#cfa757", "#d2aa5b"))

@plant("theme: NEW — a foreign SYNTAX colour (the github-dark class of defect)")
def _(): sub("dist/docs/getting-started/index.html", "--0:#EAE7E0", "--0:#9ecbff", 1)

@plant("theme: NEW — a colour EC derived on its own (#908C83)")
def _(): sub("dist/docs/skill/index.html", "--0:#8C887F", "--0:#908C83", 1)

@plant("brand: the border-radius reset removed from the source")
def _(): sub("src/styles/brand.css", "*, *::before, *::after { border-radius: 0; }",
             "*, *::before, *::after { border-radius: 3px; }", 1)

# ---- build hygiene ---------------------------------------------------------
@plant("build: Starlight's own sitemap integration left enabled")
def _(): (WORK/"dist/sitemap-index.xml").write_text("<urlset/>")

@plant("build: a sourcemap ships")
def _(): (WORK/"dist/_astro/app.css.map").write_text("{}")

@plant("build: NEW — unreachable JavaScript in the served directory")
def _(): (WORK/"dist/_astro/ui-core.orphan.js").write_text("export const x=1;\n" * 200)

# ---- records ---------------------------------------------------------------
@plant("records: NEW — the banned status grade returns to status.json")
def _():
    p = WORK/"dist/status.json"; d = json.loads(p.read_text())
    d["hosts"]["hosts"][0]["status"] = "partly tested"
    p.write_text(json.dumps(d, indent=2, sort_keys=True))

@plant("records: NEW — a host row stops saying which part")
def _():
    p = WORK/"dist/status.json"; d = json.loads(p.read_text())
    d["hosts"]["hosts"][0]["not confirmed"] = ""
    p.write_text(json.dumps(d, indent=2, sort_keys=True))

@plant("records: the renamed benchmark key reverts")
def _():
    p = WORK/"dist/status.json"; d = json.loads(p.read_text())
    d["still true before any release"]["full benchmark method published"] = True
    p.write_text(json.dumps(d, indent=2, sort_keys=True))

# ---- source-side, NEW ------------------------------------------------------
@plant("source: NEW — the CLAUDE.md fence stops matching the file it claims to be")
def _(): sub("src/content/docs/docs/skill.mdx",
             "## Kaleidoscope memory\n\nFor nontrivial tasks",
             "## Kaleidoscope Memory\n\nFor nontrivial tasks", 1)

# ---- links / seo -----------------------------------------------------------
@plant("links: a broken internal link")
def _(): sub("dist/docs/index.html", 'href="/docs/skill/"', 'href="/docs/skil/"', 1)

@plant("seo: a page is marked noindex that must be indexed")
def _(): sub("dist/docs/concepts/index.html",
             'name="robots" content="index,follow"',
             'name="robots" content="noindex,nofollow"', 1)

@plant("deploy: CNAME lost from the artifact")
def _(): (WORK/"dist/CNAME").unlink()

@plant("deploy: .nojekyll lost (Pages would strip every _astro/ asset)")
def _(): (WORK/"dist/.nojekyll").unlink()

@plant("scan: no source tree, so the source half cannot run")
def _(): shutil.rmtree(WORK/"src/styles")

def main():
    print("=" * 74)
    print("CONTROL — the artifact as promoted, unmodified")
    print("=" * 74)
    fresh(); rc, out = run()
    control_ok = show("clean build must be ACCEPTED", rc, out, expect_fail=False)
    print()
    print("=" * 74)
    print(f"{len(PLANTS)} PLANTED VIOLATIONS — each is one mutation of that same tree")
    print("=" * 74)
    caught = 0
    for label, fn in PLANTS:
        fresh(); fn(); rc, out = run()
        if show(label, rc, out): caught += 1
    print()
    print("=" * 74)
    print(f"control accepted: {control_ok}   planted: {len(PLANTS)}   caught: {caught}   MISSED: {len(PLANTS)-caught}")
    print("=" * 74)
    return 0 if (control_ok and caught == len(PLANTS)) else 1

sys.exit(main())
