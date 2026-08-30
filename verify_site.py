#!/usr/bin/env python3
"""Verify a built Kaleidoscope documentation artifact.

Runs over `dist/` before promotion and over the committed `docs/` in CI. Python,
standard library only, one file, one entry point:

    python3 verify_site.py <root> --mode {staging|public_docs|production}

The four gates this file carries are older than the site generator that used to
sit beside it — `build_site.py`, now deleted — and none of them has a Starlight
equivalent, which is why this file survived the migration and that one did not:

  (a) private-marker leak scan — no developer paths, no worktree paths, no
      internal identifiers, in anything published.
  (b) banned-vocabulary scan — the internal release register must not return.
  (c) release metadata, fail closed. The refusal itself lives in
      scripts/release-metadata.mjs, imported at module scope by
      astro.config.mjs so a build cannot start without it; what this file checks
      is that the artifact carries the metadata the build was given.
  (d) the reviewed-artifact guarantee — the per-file digests and sizes in
      site-manifest.json, plus the recursive diff CI runs between a fresh
      `dist/` and the committed `docs/`.

Two more were added in the migration, because Astro can do something the old
Python emitter could not:

  (e) content presence. `astro build` exits 0 while emitting structurally valid
      pages with empty bodies if an Expressive Code plugin throws. Measured: 35
      files, every `sl-markdown-content` empty, exit status 0.
  (f)/(h) chrome sentinels. The Kaleidoscope mark and the pre-release status
      strip are required on every page and, until now, were required by nobody
      — they were strings in one Python function. A required claim with no gate
      is one refactor away from gone.

Scope note, and it is deliberate: gates (a) and (b) now scan the SOURCE tree as
well as the artifact, so a leak is caught before it is built rather than after
it is committed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

DOMAIN = "https://memory.kleosresearch.xyz"
SOCIAL_IMAGE = f"{DOMAIN}/assets/kaleidoscope-og.png"
# The social card is the product's identity on every share surface, and a PNG
# magic-byte test cannot see that it is the wrong drawing in the wrong colour.
# Pin the composed brand card itself: ink ground, the real swept mark in brass,
# the wordmark in Newsreader. Regenerate the card, then update this digest.
SOCIAL_IMAGE_SHA256 = (
    "d84723af1329236dc663243909771784a4a056a6359f1f0cbd3243390c27ebf5"
)
EXPECTED_CNAME = "memory.kleosresearch.xyz"
PUBLIC_SKILL_SHA256 = (
    "c688db1b84ee20b6786d6109c68fbf8a21fd87486b9fe37e525d85170b77c9ad"
)

# ---------------------------------------------------------------- gate (a)
# Ported verbatim. No exemptions, and none may be added: every one of these is
# a coordinate on somebody's machine or a private repository, and a reader has
# no use for any of them.
#
# The trailing quote in the repository marker is load-bearing. It bans the
# private product repository as it appears in an href, while allowing the org
# link `https://github.com/kleos-research` that the top navigation uses on
# every page. Do not "improve" it into a regex without the quote.
PRIVATE_MARKERS = (
    "/Users/",
    "\\Users\\",
    ".codex/worktrees",
    ".claude/worktrees",
    'github.com/kleos-research/kaleidoscope"',
    "KSCOPE_ROOT",
    "KSCOPE_WORKSPACE",
    "KSCOPE_PRINCIPAL",
    "KSCOPE_JOURNAL",
)
# Suffixes that are legitimately not text. Everything else in the artifact must
# decode as UTF-8 and is scanned. This inverts the old rule, which scanned an
# allowlist of six suffixes and therefore silently skipped
# `snippets/cursor-kaleidoscope.mdc` — a file a human wrote — and would skip
# every JavaScript chunk Astro now emits.
BINARY_SUFFIXES = {
    ".png", ".ico", ".jpg", ".jpeg", ".webp", ".avif", ".gif",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".pdf", ".mp4", ".webm", ".zip", ".gz", ".pagefind", ".pf_meta", ".pf_fragment",
}

LEGACY_TOOLS = ("compile", "recall", "read_memory", "ingest_memory")

# ---------------------------------------------------------------- gate (b)
# Words that state our internal release process instead of what a reader can
# and cannot do. Every one of them was published on this site at least once,
# and the owner rejected the copy that carried them. The scan runs over the
# whole lowercased text of every published file, so it also sees class names,
# JSON keys, SVG ids and aria labels, and "-" is a word boundary.
BANNED_VOCABULARY = (
    r"dx-\d",
    r"facades?",
    r"harnesse?s?",
    r"conformance",
    r"signature_verified",
    r"milestones",
    r"\bslices?\b",
    r"\bsmoke\b",
    r"\blanes?\b",
    r"\bstaging\b",
    r"\bcandidates?\b",
    r"\bpromotion\b",
    r"\bcanary\b",
    r"\bexercised\b",
    # A commit or a build digest is our coordinate, not the reader's. Twelve
    # characters is the shortest form that was ever published in prose.
    r"\b[0-9a-f]{12,}\b",
)
# Files the site republishes verbatim rather than writes. The four product
# terms are unreviewed draft source under a mandatory not-in-force notice, and
# SKILL.md is the agent skill exactly as the product installs it — its
# "candidates" and "milestone" are ordinary English about memories, not about
# this release. Editing either from this repository would make the published
# copy differ from the source it claims to reproduce byte for byte.
#
# Every key is asserted to EXIST in the artifact. Without that assertion a
# route rename turns an exemption into dead configuration, and the exemption
# goes on covering a path that no longer holds the file it was argued for.
VOCABULARY_EXEMPT = {
    "SKILL.md",
    "legal/ENGINE-EULA.txt",
    "legal/PRIVACY-NOTICE.txt",
    "legal/SECURITY-POLICY.txt",
    "legal/SUPPORT-POLICY.txt",
    "docs/legal/engine-eula/index.html",
    "docs/legal/privacy-notice/index.html",
    "docs/legal/security-policy/index.html",
    "docs/legal/support-policy/index.html",
    # every file digest in the build manifest is a 64-character hex string
    "site-manifest.json",
}
# The same four sources, and the skill, on the source side.
SOURCE_VOCABULARY_EXEMPT = {
    "src/data/public/SKILL.md",
    "src/data/legal/ENGINE-EULA.txt",
    "src/data/legal/PRIVACY-NOTICE.txt",
    "src/data/legal/SECURITY-POLICY.txt",
    "src/data/legal/SUPPORT-POLICY.txt",
}
# llms-full.txt inlines the exempt skill; scan the chunks the site wrote.
VOCABULARY_EXEMPT_CHUNKS = ("# Public agent skill",)
# Starlight's own minified vendor CSS and JavaScript contain `slice`, which is
# a JavaScript method and not our vocabulary. Our stylesheet is bundled into
# the same directory, which is why gate (b) also runs over the authored source
# — the exclusion below is a scope decision, not a loophole.
VENDOR_BUNDLE_DIR = "_astro"

PRODUCTION_BLOCKERS = (
    "unreleased",
    "not-yet-bound",
    "under conformance",
    "not released",
    "staging candidate",
    "not installable yet",
    "generation pending release binding",
    "no support claim yet",
    "will be published here",
    "local staging",
    "local-only",
    "test-only",
    "not public",
    "unapproved",
    "provider not configured",
    "production login remains disabled",
    "review draft",
    "not for production",
    "not live-host accepted",
    "verified local, unpublished",
    "verified without live provider",
    "no package or production login is public",
)

# ------------------------------------------------------------- the routes
# 38 pages plus the error page. Adding a route still requires a human edit in a
# reviewed file, which is the point of writing them out.
EXPECTED_HTML = {
    "404.html",
    "index.html",
    "status/index.html",
    # Start
    "docs/index.html",
    "docs/getting-started/index.html",
    "docs/skill/index.html",
    "docs/packages/index.html",
    "docs/concepts/index.html",
    # CLI
    "docs/cli/index.html",
    "docs/cli/profiles/index.html",
    "docs/cli/connect/index.html",
    "docs/cli/instructions/index.html",
    "docs/cli/diagnostics/index.html",
    "docs/cli/account/index.html",
    # Reference
    "docs/mcp/index.html",
    "docs/integrations/index.html",
    "docs/integrations/claude-code/index.html",
    "docs/integrations/codex/index.html",
    "docs/integrations/cursor/index.html",
    "docs/integrations/opencode/index.html",
    "docs/integrations/generic-mcp/index.html",
    "docs/integrations/claude-agent-sdk/index.html",
    "docs/integrations/openai-agents-sdk/index.html",
    "docs/integrations/langchain/index.html",
    "docs/integrations/langgraph/index.html",
    "docs/integrations/crewai/index.html",
    # Operate
    "docs/operations/index.html",
    "docs/account/index.html",
    "docs/troubleshooting/index.html",
    # Boundaries
    "docs/security/index.html",
    "docs/privacy/index.html",
    "docs/legal/index.html",
    "docs/legal/engine-eula/index.html",
    "docs/legal/privacy-notice/index.html",
    "docs/legal/security-policy/index.html",
    "docs/legal/support-policy/index.html",
    # Availability
    "docs/compatibility/index.html",
    "docs/benchmarks/index.html",
    "docs/release-notes/index.html",
}
# Hand-authored stubs in public/. Pages cannot redirect server-side, and both
# old URLs are linked from outside this site. They are exempt from every
# per-page check and carry three of their own.
REDIRECT_HTML = {
    "docs/status/index.html": "/status/",
    "docs/hosted/index.html": "/docs/privacy/",
}
# The one route rendered with Starlight's splash template. Its h1 is the hero
# title, which sits ABOVE `.sl-markdown-content`, so heading order and the
# content-presence count are measured over <main> instead.
SPLASH_HTML = {"index.html"}
NOINDEX_HTML = {
    "404.html",
    "docs/legal/engine-eula/index.html",
    "docs/legal/privacy-notice/index.html",
    "docs/legal/security-policy/index.html",
    "docs/legal/support-policy/index.html",
}
# Routes where a developer has asked for technical provenance. Global chrome
# must not carry a release version, availability value, or contract digest.
PROVENANCE_ROUTES = {
    "status/index.html",
    "docs/packages/index.html",
    "docs/release-notes/index.html",
    "docs/mcp/index.html",
    "docs/getting-started/index.html",
    "docs/benchmarks/index.html",
}
LEGAL_DRAFT_ROUTES = {
    "docs/legal/index.html",
    "docs/legal/engine-eula/index.html",
    "docs/legal/privacy-notice/index.html",
    "docs/legal/security-policy/index.html",
    "docs/legal/support-policy/index.html",
}
# Counsel reviewed and directed these documents on 2026-08-23, so the old
# sentinel ("not been reviewed by legal counsel") is now FALSE and asserting it
# would force the site to lie. The boundary that still holds, and that this gate
# now defends, is ADOPTION: reviewed, but not adopted and therefore not in force.
# Note "not yet in force" does not contain the substring "not in force", which is
# why this constant changed rather than gaining a member.
LEGAL_DRAFT_SENTINELS = ("not yet in force",)
LEGAL_OVERCLAIMS = (
    "legally binding",
    "counsel-approved",
    "legally effective",
    # "reviewed by counsel" and its variants were overclaims until 2026-08-23 and
    # are now simply true, so they are no longer listed. What remains forbidden is
    # any claim of ADOPTION or binding effect, which has not happened.
    "now in force",
    "currently in force",
    "adopted by kleos research",
    "reviewed by outside counsel",
    "counsel-reviewed",
    "approved by counsel",
)
# Gate (h). Whitespace is normalised before the comparison because the strip's
# copy wraps across lines in the component source.
#
# This asserted "Kaleidoscope is not publicly released" until 0.0.5 went to npm,
# at which point the gate was enforcing a false claim and its own negative
# control planted the TRUE sentence as the violation. What a reader needs from
# this strip is no longer whether the package exists -- it does, and
# `npm install -g @kleos-research/kaleidoscope` works -- but that it will not
# run without a key. That is what the gate holds now, so the site cannot go back
# to publishing an install command with no mention of the thing that blocks it.
STATUS_STRIP_SENTINEL = "Kaleidoscope needs a key to run"

# kaleidoscope-dark, brand/tokens/tokens.json.
REQUIRED_TOKENS = ("#0B0B0C", "#131315", "#232325", "#8C887F", "#EAE7E0", "#CFA757")
# Values that must not reappear: the five drifted ones from the rejected design,
# plus #605D57, which was a rebuild extension token used for real text at
# 9.5-12px and measures 3.00:1 on --bg and 2.83:1 on --raised.
DRIFTED_TOKENS = (
    "#2c2c30",
    "#ece8df",
    "#918b80",
    "#d2aa5b",
    "#e0be7b",
    "#9bc6a4",
    "#605d57",
)
# The complete palette: the six canonical tokens plus the three sanctioned
# extensions declared in src/styles/brand.css. Nothing else may colour a
# character on this site.
#
# This exists because DRIFTED_TOKENS is a DENYLIST, and a denylist only catches
# the colours somebody already knew to be wrong. It did not catch #e1e4e8 /
# #9ecbff / #79b8ff / #b392f0 — an entire foreign palette on 19 of 39 pages,
# arriving through `expressiveCode.themes: ['github-dark']` — and it did not
# catch #908C83, which Expressive Code DERIVED on its own by raising --k-muted
# to clear its 5.5:1 default. A tenth colour nobody chose and no denylist could
# have listed. The syntax-token scan below is the allowlist half.
PALETTE = (
    "#0b0b0c", "#131315", "#232325", "#8c887f", "#eae7e0", "#cfa757",
    "#1b1b1d", "#2e2e30", "#c3bfb6",
)

# Files Astro or an integration can emit that must never reach the artifact.
# A sourcemap ships absolute developer paths and would trip gate (a) correctly
# — but only after it had already been committed. Starlight adds
# @astrojs/sitemap unless an integration of that name is already present; its
# output is a second, differently named sitemap that the URL-set check below
# cannot see.
FORBIDDEN_EMITTED = ("sitemap-index.xml", "sitemap-0.xml")
FORBIDDEN_EMITTED_SUFFIXES = (".map",)

# Authored sources that gates (a) and (b) read before anything is built.
# Gate (a) runs over every authored source file. Gate (b) runs over authored
# PROSE and records only — `src/content/**` and `src/data/**`. The distinction
# is not a relaxation: everything a reader can see is scanned in the ARTIFACT,
# which is the authority, and the compiled text of every component lands there.
# What the source-side vocabulary scan must not do is read a build-mode
# identifier as published copy. `robots.txt.ts` says `mode === 'staging'`
# because that is the name of a mode; the word reaches no page, and a gate that
# cannot tell a literal from a sentence gets switched off by whoever meets it.
SOURCE_TEXT_SUFFIXES = {".mdx", ".md", ".mdc", ".json", ".txt", ".xml", ".css"}
# `src/styles` is here because CSS PUBLISHES TEXT. A single
# `.k-nav a::after { content: " staging" }` put the word on the top nav of all
# 41 pages and the verifier called the artifact clean: the source side did not
# scan `src/styles`, and the artifact side skips `_astro/`, so the one file
# that is both authored by us and bundled with the vendor fell between the two
# halves. The artifact-side `content:` scan below is the authority; this is the
# half that names the file you have to edit.
SOURCE_PROSE_ROOTS = ("src/content", "src/data", "src/styles")
SOURCE_ROOTS = ("src",)
SOURCE_FILES = ("astro.config.mjs",)
BRAND_CSS = "src/styles/brand.css"


class DocumentParser(HTMLParser):
    """One pass over a page.

    Collects the document-level metadata the old parser collected, and in
    addition tracks two regions by tag depth: `.sl-markdown-content` and
    `<main>`. Heading order and the content-presence count are measured inside
    a region, because Starlight emits an `<h2 id="starlight__on-this-page">`
    for the mobile table of contents BEFORE the article's own `<h1>` — a
    document-order heading check reads that as "the first heading is h2" on
    every page, forever.
    """

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.h1_count = 0
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.descriptions: list[str] = []
        self.meta: dict[str, list[str]] = {}
        self.structured_data: list[str] = []
        self._structured_buffer: list[str] | None = None
        self._stack: list[str] = []
        # region name -> (depth at which it opened, headings, text chunks)
        self._open_regions: dict[str, int] = {}
        self.region_headings: dict[str, list[int]] = {"content": [], "main": []}
        self.region_text: dict[str, list[str]] = {"content": [], "main": []}
        self._suppress_text = 0

    def _region_names(self) -> list[str]:
        return list(self._open_regions)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: (value or "") for key, value in attrs}
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag in {"img", "script", "link"} and values.get("src"):
            self.links.append(values["src"])
        if tag == "link" and values.get("href"):
            self.links.append(values["href"])
            if values.get("rel") == "canonical":
                self.canonicals.append(values["href"])
        if tag == "meta":
            key = values.get("name") or values.get("property")
            if key:
                self.meta.setdefault(key, []).append(values.get("content", ""))
            if values.get("name") == "robots":
                self.robots.append(values.get("content", ""))
            if values.get("name") == "description":
                self.descriptions.append(values.get("content", ""))
        if tag == "script" and values.get("type") == "application/ld+json":
            self._structured_buffer = []
        if tag in {"script", "style", "template"}:
            self._suppress_text += 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            if tag == "h1":
                self.h1_count += 1
            for name in self._region_names():
                self.region_headings[name].append(level)

        if tag not in self.VOID:
            self._stack.append(tag)
            depth = len(self._stack)
            classes = values.get("class", "").split()
            if "sl-markdown-content" in classes and "content" not in self._open_regions:
                self._open_regions["content"] = depth
            if tag == "main" and "main" not in self._open_regions:
                self._open_regions["main"] = depth

    def handle_startendtag(self, tag, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self._structured_buffer is not None:
            self._structured_buffer.append(data)
        if self._suppress_text:
            return
        for name in self._region_names():
            self.region_text[name].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._structured_buffer is not None:
            self.structured_data.append("".join(self._structured_buffer))
            self._structured_buffer = None
        if tag in {"script", "style", "template"} and self._suppress_text:
            self._suppress_text -= 1
        if tag in self.VOID:
            return
        if tag in self._stack:
            while self._stack:
                closed = self._stack.pop()
                depth = len(self._stack) + 1
                for name, opened_at in list(self._open_regions.items()):
                    if opened_at >= depth:
                        del self._open_regions[name]
                if closed == tag:
                    break


def word_count(chunks: list[str]) -> int:
    text = " ".join(chunks)
    return sum(1 for token in text.split() if any(ch.isalnum() for ch in token))


def local_target(root: Path, link: str) -> Path | None:
    parsed = urlparse(link)
    if parsed.scheme or parsed.netloc or link.startswith(("mailto:", "#")):
        return None
    path = parsed.path
    if not path.startswith("/"):
        return None
    if path == "/":
        return root / "index.html"
    candidate = root / path.lstrip("/")
    if path.endswith("/"):
        return candidate / "index.html"
    return candidate


def read_text_or_none(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, ValueError):
        return None


def scan_private_markers(relative: str, text: str, failures: list[str]) -> None:
    for marker in PRIVATE_MARKERS:
        if marker in text:
            failures.append(f"private marker {marker!r} in {relative}")


def scan_vocabulary(relative: str, text: str, failures: list[str]) -> None:
    lowered = text.lower()
    for pattern in BANNED_VOCABULARY:
        found = re.search(pattern, lowered)
        if found:
            failures.append(f"internal vocabulary {found.group(0)!r} in {relative}")


def verify(
    root: Path,
    expected_mode: str,
    source_root: Path | None = None,
    scan_sources: bool = True,
) -> list[str]:
    failures: list[str] = []
    root = Path(root)
    if source_root is None:
        source_root = root.parent

    manifest_path = root / "site-manifest.json"
    if not manifest_path.is_file():
        return ["missing site-manifest.json"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "kaleidoscope.docs-artifact.v1":
        failures.append("wrong manifest schema")
    if manifest.get("mode") != expected_mode:
        failures.append(
            f"manifest mode is {manifest.get('mode')!r}, expected {expected_mode!r}"
        )

    # ------------------------------------------------------------ gate (c)
    # The refusal happens in scripts/release-metadata.mjs before Vite starts.
    # What the artifact can still be wrong about is carrying metadata that does
    # not match the mode it claims, so check the shape here too.
    release = manifest.get("release")
    if not isinstance(release, dict):
        failures.append("manifest carries no release metadata")
        release = {}
    else:
        expected_fields = {
            "release_version",
            "public_contract_sha256",
            "availability",
            "updated_at",
        }
        if set(release) != expected_fields:
            failures.append(
                "manifest release metadata must contain exactly "
                f"{sorted(expected_fields)}, found {sorted(release)}"
            )
        elif not all(isinstance(value, str) for value in release.values()):
            failures.append("manifest release metadata has a non-string field")
        else:
            allowed_availability = {
                "staging": {"staging"},
                "public_docs": {"documentation_preview", "available_with_key"},
                "production": {"release_candidate", "released"},
            }[expected_mode]
            if release["availability"] not in allowed_availability:
                failures.append(
                    f"manifest availability {release['availability']!r} is not valid "
                    f"for a {expected_mode} artifact"
                )
            if expected_mode != "staging":
                if release["release_version"] in {"", "unreleased", "latest"}:
                    failures.append(
                        f"{expected_mode} artifact carries a placeholder release version"
                    )
                if not re.fullmatch(r"[0-9a-f]{64}", release["public_contract_sha256"]):
                    failures.append(
                        f"{expected_mode} artifact carries no 64-hex public contract digest"
                    )

    cname_path = root / "CNAME"
    if not cname_path.is_file():
        failures.append("missing CNAME")
    elif cname_path.read_text(encoding="utf-8").strip() != EXPECTED_CNAME:
        failures.append("CNAME does not match the canonical documentation domain")
    if not (root / ".nojekyll").is_file():
        failures.append(
            "missing .nojekyll — Pages strips leading-underscore directories, "
            "which would remove every stylesheet and script in _astro/"
        )

    social_image = root / "assets" / "kaleidoscope-og.png"
    if not social_image.is_file():
        failures.append("missing or invalid Kaleidoscope social image")
    else:
        social_bytes = social_image.read_bytes()
        if not social_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            failures.append("missing or invalid Kaleidoscope social image")
        else:
            width, height = struct.unpack(">II", social_bytes[16:24])
            if (width, height) != (1200, 630):
                failures.append(
                    f"social image is {width}x{height}, expected 1200x630"
                )
            digest = hashlib.sha256(social_bytes).hexdigest()
            if digest != SOCIAL_IMAGE_SHA256:
                failures.append(
                    "social image is not the composed Kaleidoscope brand card "
                    f"(sha256 {digest}); it must carry the swept mark in brass "
                    "on ink, not a second palette or a substitute drawing"
                )

    # ------------------------------------------------------------ gate (d)
    declared = {entry["path"]: entry for entry in manifest.get("files", [])}
    actual = {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and path != manifest_path
    }
    if set(declared) != set(actual):
        failures.append(
            f"manifest inventory mismatch: declared-only={sorted(set(declared) - set(actual))}, actual-only={sorted(set(actual) - set(declared))}"
        )
    for relative, entry in declared.items():
        path = actual.get(relative)
        if path is None:
            continue
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != entry.get("sha256"):
            failures.append(f"manifest digest mismatch: {relative}")
        if len(content) != entry.get("size_bytes"):
            failures.append(f"manifest size mismatch: {relative}")

    for forbidden in FORBIDDEN_EMITTED:
        if forbidden in actual:
            failures.append(
                f"{forbidden} was emitted — this site generates its own sitemap.xml "
                "from the route table, and a second sitemap is one the URL-set "
                "check cannot see"
            )
    for relative in actual:
        if relative.endswith(FORBIDDEN_EMITTED_SUFFIXES):
            failures.append(
                f"{relative}: a sourcemap ships absolute developer paths into a "
                "committed artifact"
            )
        name = Path(relative).name
        if re.search(r"[0-9a-f]{12,}", name):
            failures.append(
                f"{relative}: emitted filename carries a 12+ character hex digest; "
                "pin a deterministic asset name rather than relaxing the prose rule"
            )

    public_sources = manifest.get("public_source_sha256")
    if not isinstance(public_sources, dict) or not public_sources:
        failures.append("missing public source bindings")
    else:
        for relative, digest in sorted(public_sources.items()):
            path = actual.get(relative)
            if path is None:
                failures.append(f"missing bound public source: {relative}")
            elif not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
                failures.append(f"invalid public source digest: {relative}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                failures.append(f"public source binding mismatch: {relative}")
    skill_path = actual.get("SKILL.md")
    if skill_path is None:
        failures.append("missing canonical public skill")
    elif hashlib.sha256(skill_path.read_bytes()).hexdigest() != PUBLIC_SKILL_SHA256:
        failures.append("canonical public skill digest changed")

    # ---------------------------------------------------- the machine records
    status_path = actual.get("status.json")
    if status_path is None:
        failures.append("missing status.json")
    else:
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            failures.append("status.json is not valid JSON")
        else:
            if status.get("schema_version") != "kaleidoscope.docs-status.v1":
                failures.append("status.json has the wrong schema")
            # Every one of these is a claim a reader would act on, so each is
            # pinned to the value that is true and a build that flips one fails
            # until somebody changes this file on purpose. Three flipped when
            # 0.0.5 published; they are still asserted, in the other direction.
            for field in ("released", "publicly available"):
                if status.get(field) is not True:
                    failures.append(f"status.json must keep {field!r} true")
            packages = status.get("packages", {})
            if packages.get("published to a registry") is not True:
                failures.append("status.json must keep packages 'published to a registry' true")
            # NOT flipped, and the one a reader most needs before installing.
            if packages.get("signed for release") is not False:
                failures.append("status.json must keep packages 'signed for release' false")
            if sorted(packages.get("the platform package is built for") or []) != [
                "Linux, arm64",
                "Linux, x86_64",
                "macOS, Apple Silicon",
                "macOS, x86_64",
            ]:
                failures.append("status.json has the wrong built-for platform")
            licences = status.get("licences", {})
            if "not yet in force" not in licences.get("the product terms", ""):
                failures.append("status.json must keep the product terms not yet in force")
            if "not adopted" not in licences.get("the product terms", ""):
                failures.append("status.json must say the product terms are not adopted")
            holds = status.get("still true before any release", {})
            # This block lists what has NOT been done, so a finished item
            # LEAVES it rather than flipping to true -- which is also what
            # `test_the_benchmark_key_was_renamed_not_deleted` asserts of every
            # value here. Three left when 0.0.5 published: registry publication
            # (now asserted true through `packages`), the counsel review, and
            # verification on a platform other than Apple Silicon (now carried
            # by the built-for list above).
            for field in (
                "builds signed for release",
                "sign-in service configured",
                "support offered",
                "security contact published",
                "any editor run against a live model provider",
                # Renamed. /docs/benchmarks/ now publishes results in plain
                # words, so "benchmark score published: false" became a lie the
                # verifier was enforcing. What remains true is that the method
                # is not out, and that is what the key now says.
                "full benchmark method published",
                "hosted memory built",
            ):
                if holds.get(field) is not False:
                    failures.append(f"status.json must keep {field!r} false")
            if "benchmark score published" in holds:
                failures.append(
                    "status.json still carries 'benchmark score published': "
                    "/docs/benchmarks/ publishes results, so that key is now false "
                    "in the wrong direction — it is 'full benchmark method published'"
                )
            host_rows = status.get("hosts", {}).get("hosts", [])
            hosts = {host.get("name") for host in host_rows}
            expected_hosts = {"Codex", "Claude Code", "OpenCode", "Cursor"}
            if hosts != expected_hosts:
                failures.append("status.json has the wrong host inventory")
            # The five status words are gone from the machine record too, not
            # just from prose. `status.json` is LINKED FROM /status/ as "the
            # same facts, in machine-readable form", and llms-full.txt inlines
            # it, so a `"status": "partly tested"` key was reader-reachable
            # copy wearing a schema's clothes. It also carried no information:
            # every row already states what was confirmed AND what was not, and
            # that pair is both the honest form and strictly more than a grade.
            # What the grade was introduced to guarantee is enforced directly.
            for host in host_rows:
                if "status" in host:
                    failures.append(
                        f"status.json row {host.get('name')!r} carries a 'status' "
                        "grade — the five status words are deleted; state what is "
                        "confirmed and what is not"
                    )
                for side in ("confirmed", "not confirmed"):
                    if not str(host.get(side, "")).strip():
                        failures.append(
                            f"status.json row {host.get('name')!r} has an empty "
                            f"{side!r}: every row must say which part was "
                            "established and which part was not"
                        )
            if "not tested at all" in status.get("hosts", {}):
                failures.append(
                    "status.json still carries 'not tested at all' — nothing was "
                    "tested there because nothing was run there; the key is "
                    "'not run at all'"
                )
            if status.get("hosts", {}).get("tools_a_model_sees") != [
                "remember",
                "search",
            ]:
                failures.append("status.json exposes the wrong tools to a model")

    platform_path = actual.get("platform-support.json")
    if platform_path is None:
        failures.append("missing platform-support.json")
    else:
        try:
            platforms = json.loads(platform_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            failures.append("platform-support.json is not valid JSON")
        else:
            if (
                platforms.get("schema_version")
                != "kaleidoscope.docs-platform-support.v1"
            ):
                failures.append("platform-support.json has the wrong schema")
            if platforms.get("run on") != ["macOS, Apple Silicon"]:
                failures.append("platform-support.json has the wrong run-on list")
            checked = platforms.get("compiler checked only", {})
            # The claim these four rows carry is a compiler check and nothing
            # more. Published once as "the code builds for this target", it read
            # as a working build for platforms nothing has ever been built for.
            meaning = checked.get("meaning", "")
            for phrase in (
                "The compiler accepts",
                "Nothing was ever assembled",
                "nothing has been run there",
            ):
                if phrase not in meaning:
                    failures.append(
                        f"platform-support.json must keep {phrase!r} in the compiler-check meaning"
                    )
            checked_platforms = {
                (row.get("platform"), row.get("architecture"), row.get("result"))
                for row in checked.get("platforms", [])
            }
            expected_checked = {
                ("macOS", "x86_64", "passed"),
                ("Linux", "x86_64", "passed"),
                ("Linux", "arm64", "passed"),
                ("Windows", "x86_64", "passed"),
            }
            if checked_platforms != expected_checked:
                failures.append("platform-support.json has the wrong checked inventory")
            if platforms.get("not checked at all") != [
                {"platform": "Windows", "architecture": "arm64"}
            ]:
                failures.append("platform-support.json has the wrong unchecked list")
            if not platforms.get("does not establish"):
                failures.append(
                    "platform-support.json must keep the limits of a compiler check"
                )

    cli_reference = actual.get("reference/kaleidoscope-cli.txt")
    if cli_reference is None:
        failures.append("missing CLI reference")
    else:
        cli_text = cli_reference.read_text(encoding="utf-8")
        for command in (
            "kaleidoscope [--engine PATH] init",
            "connect HOST",
            "disconnect HOST",
            "instructions install TARGET",
            "doctor",
        ):
            if command not in cli_text:
                failures.append(f"CLI reference missing {command!r}")

    mcp_reference = actual.get("reference/kaleidoscope-mcp.json")
    if mcp_reference is None:
        failures.append("missing MCP tool reference")
    else:
        try:
            mcp = json.loads(mcp_reference.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            failures.append("MCP tool reference is not valid JSON")
        else:
            if mcp.get("schema_version") != "kaleidoscope.docs-mcp-reference.v2":
                failures.append("MCP tool reference has the wrong schema")
            if mcp.get("protocol_revision") != "2025-11-25":
                failures.append("MCP tool reference has the wrong protocol revision")
            tools = {tool.get("name") for tool in mcp.get("model_tools", [])}
            if tools != {"remember", "search"}:
                failures.append(
                    "MCP tool reference must expose exactly remember and search"
                )
            for tool in mcp.get("model_tools", []):
                if tool.get("name") == "remember" and tool.get(
                    "maximum_batch_items"
                ) != 20:
                    failures.append("MCP tool reference has the wrong batch bound")
                if tool.get("name") == "search" and tool.get("ledger_values") != [True]:
                    failures.append(
                        "MCP tool reference must keep ranked search ledgered"
                    )
            if mcp.get("operator_commands_are_model_tools") is not False:
                failures.append("MCP tool reference exposes operator commands")
            if mcp.get("release_readiness_claimed") is not False:
                failures.append("MCP tool reference claims release readiness")
            for field in ("released", "publicly available"):
                if mcp.get(field) is not False:
                    failures.append(f"MCP tool reference must keep {field!r} false")

    # ------------------------------------------------- gates (a) and (b), artifact
    exempt_present = set(actual) | {"site-manifest.json"}
    for relative in sorted(VOCABULARY_EXEMPT):
        if relative not in exempt_present:
            failures.append(
                f"vocabulary exemption {relative!r} names a file the artifact does not "
                "contain — an exemption for a path that moved keeps covering nothing"
            )
    for relative, path in sorted(actual.items()):
        suffix = path.suffix.lower()
        text = None if suffix in BINARY_SUFFIXES else read_text_or_none(path)
        if text is None:
            if suffix not in BINARY_SUFFIXES:
                failures.append(
                    f"{relative}: not UTF-8 and not a known binary type — nothing "
                    "unreadable may be published, because no scan can see inside it"
                )
            continue
        # gate (a) runs over EVERYTHING that decodes, vendor bundles included.
        scan_private_markers(relative, text, failures)
        # gate (b) runs over authored output only.
        in_vendor_bundle = relative.split("/", 1)[0] == VENDOR_BUNDLE_DIR
        if not in_vendor_bundle and relative not in VOCABULARY_EXEMPT:
            scanned = text
            if relative == "llms-full.txt":
                scanned = "\n\n---\n\n".join(
                    chunk
                    for chunk in text.split("\n\n---\n\n")
                    if not chunk.lstrip().startswith(VOCABULARY_EXEMPT_CHUNKS)
                )
            scan_vocabulary(relative, scanned, failures)
        for placeholder in ("{FINAL_PACKAGE_EVIDENCE_SHA256", "{PLATFORM_HARNESS_COMMIT"):
            if placeholder in text:
                failures.append(f"unexpanded placeholder {placeholder!r} in {relative}")
        if expected_mode == "production":
            lowered = text.lower()
            for blocker in PRODUCTION_BLOCKERS:
                if blocker in lowered:
                    failures.append(f"production blocker {blocker!r} in {relative}")

    # ------------------------------------------------- gates (a) and (b), source
    if scan_sources:
        source_root = Path(source_root)
        brand_css_path = source_root / BRAND_CSS
        if not brand_css_path.is_file():
            failures.append(
                f"source root {source_root} has no {BRAND_CSS}: the source-side half of "
                "gates (a) and (b) cannot run, and a skipped scan passes"
            )
        else:
            source_paths: list[Path] = []
            for directory in SOURCE_ROOTS:
                source_paths.extend(
                    p for p in (source_root / directory).rglob("*") if p.is_file()
                )
            source_paths.extend(
                source_root / name
                for name in SOURCE_FILES
                if (source_root / name).is_file()
            )
            for path in sorted(set(source_paths)):
                relative = path.relative_to(source_root).as_posix()
                if path.suffix.lower() in BINARY_SUFFIXES:
                    continue
                text = read_text_or_none(path)
                if text is None:
                    continue
                scan_private_markers(f"source:{relative}", text, failures)
                if (
                    path.suffix.lower() in SOURCE_TEXT_SUFFIXES
                    and relative.startswith(SOURCE_PROSE_ROOTS)
                    and relative not in SOURCE_VOCABULARY_EXEMPT
                ):
                    scan_vocabulary(f"source:{relative}", text, failures)

            # /docs/skill/ shows the CLAUDE.md block in a fence and says "This
            # is the whole of it", then tells the reader to paste it by hand.
            # That is a byte claim about a file that lives somewhere else, and
            # it was already false once: the fence hard-wrapped a 419-character
            # paragraph that the manager writes as one line, so a hand-paster
            # would not have produced the file the page promised. Assert it.
            skill_page = source_root / "src/content/docs/docs/skill.mdx"
            snippet = source_root / "src/data/public/snippets/CLAUDE.md"
            if skill_page.is_file() and snippet.is_file():
                fence = re.search(
                    r'```md title="CLAUDE\.md"[^\n]*\n(.*?)```',
                    skill_page.read_text(encoding="utf-8"),
                    flags=re.S,
                )
                if fence is None:
                    failures.append(
                        "src/content/docs/docs/skill.mdx: the CLAUDE.md fence is gone, "
                        "and with it the check that what the page shows is what the "
                        "manager writes"
                    )
                elif fence.group(1) != snippet.read_text(encoding="utf-8"):
                    failures.append(
                        "src/content/docs/docs/skill.mdx: the CLAUDE.md fence is not "
                        "byte-identical to src/data/public/snippets/CLAUDE.md — the "
                        "page says 'This is the whole of it' and tells the reader to "
                        "paste it by hand"
                    )

            brand_css = brand_css_path.read_text(encoding="utf-8")
            # Nothing in the system is rounded except the app-icon tile, which
            # this site does not draw. Starlight rounds badges, cards, code
            # frames, the sidebar and the search modal; one unlayered global
            # reset beats all of them, so the check is that the reset is there
            # and that our own stylesheet never re-rounds anything. Vendor CSS
            # is deliberately NOT scanned — the reset overrides it — and this
            # is a stated re-scope, not a quiet relaxation.
            if not re.search(
                r"\*\s*,\s*\*::before\s*,\s*\*::after\s*\{[^}]*border-radius\s*:\s*0",
                brand_css,
            ):
                failures.append(
                    f"{BRAND_CSS}: the unlayered global border-radius reset is absent — "
                    "Starlight's own rounded components then ship"
                )
            rounded = [
                value
                for value in re.findall(r"border-radius\s*:\s*([^;}]+)", brand_css)
                if value.strip().rstrip(";").strip() != "0"
            ]
            if rounded:
                failures.append(
                    f"{BRAND_CSS}: rounded corners {rounded!r} — nothing in the system "
                    "is rounded except the app-icon tile, which this site does not draw"
                )
            prose_code = re.search(
                r"\.sl-markdown-content p code[^{]*\{([^}]*)\}", brand_css, flags=re.S
            )
            if prose_code is None or "overflow-wrap" not in prose_code.group(1):
                failures.append(
                    f"{BRAND_CSS}: inline prose code has no overflow-wrap — a "
                    "64-character digest then scrolls the whole page sideways"
                )

    # ---------------------------------------------------------- the pages
    html_files = sorted(path for path in actual.values() if path.suffix == ".html")
    html_relatives = {path.relative_to(root).as_posix() for path in html_files}
    expected_all = EXPECTED_HTML | set(REDIRECT_HTML)
    if html_relatives != expected_all:
        failures.append(
            f"HTML route inventory mismatch: expected-only={sorted(expected_all - html_relatives)}, actual-only={sorted(html_relatives - expected_all)}"
        )

    css_bundles = [
        path
        for relative, path in actual.items()
        if relative.startswith(f"{VENDOR_BUNDLE_DIR}/") and relative.endswith(".css")
    ]
    bundled_css = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in css_bundles
    )

    # Gate (b), artifact side, over CSS-GENERATED TEXT.
    #
    # `_astro/` is skipped by the whole-file vocabulary scan because Starlight's
    # minified vendor JavaScript contains `slice` and similar as language, not
    # as our register. But CSS in that same directory can PUT WORDS ON THE PAGE:
    # `content:` on ::before/::after renders, is selectable, and is read aloud
    # by a screen reader. One planted `content:" staging"` reached the top nav
    # of every page and the verifier passed the artifact. Only the string
    # literals are scanned, so vendor identifiers outside quotes stay quiet.
    for literal in re.findall(
        r"""content\s*:\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')""",
        bundled_css,
    ):
        scan_vocabulary(f"{VENDOR_BUNDLE_DIR}/*.css content:{literal}", literal, failures)
        scan_private_markers(
            f"{VENDOR_BUNDLE_DIR}/*.css content:{literal}", literal, failures
        )

    for path in html_files:
        relative = path.relative_to(root).as_posix()
        document = path.read_text(encoding="utf-8")
        parser = DocumentParser()
        parser.feed(document)

        if relative in REDIRECT_HTML:
            # A stub is not a page. It carries three things and is exempt from
            # everything else.
            target = REDIRECT_HTML[relative]
            if "noindex,nofollow" not in document:
                failures.append(f"{relative}: redirect stub is not noindex,nofollow")
            if f'<link rel="canonical" href="{DOMAIN}{target}"' not in document:
                failures.append(
                    f"{relative}: redirect stub has no canonical to {target}"
                )
            if not re.search(
                r'<meta http-equiv="refresh" content="0;\s*url=' + re.escape(target),
                document,
            ):
                failures.append(f"{relative}: redirect stub does not refresh to {target}")
            for link in parser.links:
                local = local_target(root, link)
                if local is not None and not local.exists():
                    failures.append(f"{relative}: broken internal link {link}")
            continue

        if parser.h1_count != 1:
            failures.append(
                f"{relative}: expected exactly one h1, found {parser.h1_count}"
            )
        # Heading order is measured over <main>. Starlight puts the article's
        # own <h1> in a `content-panel` ABOVE `.sl-markdown-content`, and emits
        # an <h2 id="starlight__on-this-page"> for the mobile table of contents
        # before <main> opens. Measured over the document it is "h2 first" on
        # every page; measured over the markdown region it is "h2 first" on
        # every page as well, because the h1 is not in that region. <main> is
        # the one region that contains the h1 and excludes the mobile TOC.
        region = "main" if relative in SPLASH_HTML else "content"
        headings = parser.region_headings["main"]
        if not headings:
            failures.append(f"{relative}: no heading inside <main>")
        else:
            if headings[0] != 1:
                failures.append(
                    f"{relative}: the first heading in the article is h{headings[0]}, not h1"
                )
            for previous, level in zip(headings, headings[1:]):
                if level > previous + 1:
                    failures.append(
                        f"{relative}: heading order skips h{previous} -> h{level}"
                    )
                    break

        # -------------------------------------------------------- gate (e)
        # astro build exits 0 while emitting structurally valid pages with
        # empty bodies if an Expressive Code plugin throws. The old Python
        # emitter got this property for free by writing prose directly.
        minimum = 80 if relative in SPLASH_HTML else 40
        words = word_count(parser.region_text[region])
        if relative != "404.html" and words <= minimum:
            failures.append(
                f"{relative}: the article carries {words} words, expected more than "
                f"{minimum} — a page can build clean and ship empty"
            )

        if len(parser.canonicals) != 1 or not parser.canonicals[0].startswith(
            f"{DOMAIN}/"
        ):
            failures.append(f"{relative}: missing or invalid canonical")
        expected_robots = (
            "index,follow"
            if expected_mode in {"public_docs", "production"}
            and relative not in NOINDEX_HTML
            else "noindex,nofollow"
        )
        if parser.robots != [expected_robots]:
            failures.append(
                f"{relative}: robots is {parser.robots!r}, expected {[expected_robots]!r}"
            )
        if len(parser.descriptions) != 1 or not parser.descriptions[0].strip():
            failures.append(f"{relative}: expected one non-empty meta description")
        for name, expected in (
            ("og:image", SOCIAL_IMAGE),
            ("og:image:width", "1200"),
            ("og:image:height", "630"),
            ("og:image:alt", "Kaleidoscope — local memory for agents"),
            ("twitter:card", "summary_large_image"),
            ("twitter:image", SOCIAL_IMAGE),
            ("twitter:image:alt", "Kaleidoscope — local memory for agents"),
        ):
            if parser.meta.get(name) != [expected]:
                failures.append(
                    f"{relative}: {name} is {parser.meta.get(name)!r}, expected {[expected]!r}"
                )
        if len(parser.structured_data) != 1:
            failures.append(
                f"{relative}: expected one JSON-LD block, found {len(parser.structured_data)}"
            )
        else:
            try:
                structured = json.loads(parser.structured_data[0])
            except json.JSONDecodeError:
                failures.append(f"{relative}: JSON-LD is invalid")
            else:
                if structured.get("@context") != "https://schema.org":
                    failures.append(f"{relative}: JSON-LD has wrong schema context")
                if relative.startswith("docs/"):
                    graph = structured.get("@graph")
                    if not isinstance(graph, list) or {
                        item.get("@type")
                        for item in graph
                        if isinstance(item, dict)
                    } != {"TechArticle", "BreadcrumbList"}:
                        failures.append(
                            f"{relative}: JSON-LD must contain TechArticle and BreadcrumbList"
                        )
        flat = " ".join(document.split())
        lowered_flat = flat.lower()
        lowered = document.lower()
        for tool in LEGACY_TOOLS:
            if re.search(rf"\b{re.escape(tool)}\b", lowered):
                failures.append(f"retired tool name {tool!r} in {relative}")

        if "fonts.googleapis.com/css2" not in document and not (
            "@font-face" in bundled_css and 'as="font"' in document
        ):
            failures.append(
                f"{relative}: no webfont is loaded; the type system falls back silently"
            )

        # -------------------------------------------------------- gate (f)
        # Select the mark by class. The first <svg> on a Starlight page is one
        # of its own UI icons, so the old by-position selector would read a
        # chevron and report the mark as malformed on all 39 pages.
        mark = re.search(
            r'<svg[^>]*class="[^"]*kaleidoscope-mark[^"]*"[\s\S]*?</svg>', document
        )
        if mark is None:
            failures.append(
                f"{relative}: the Kaleidoscope mark is missing (no inline svg with "
                'class="kaleidoscope-mark")'
            )
        else:
            mark_text = mark.group(0)
            bars = mark_text.count('width="28" height="7"')
            if bars != 4:
                failures.append(
                    f"{relative}: the mark is one bar swept four times — "
                    f"found {bars} bars"
                )
            for angle in ("rotate(90 32 32)", "rotate(180 32 32)", "rotate(270 32 32)"):
                if angle not in mark_text:
                    failures.append(f"{relative}: the mark is missing {angle}")
            for step in ("0.78", "0.56", "0.34"):
                if f'opacity="{step}"' not in mark_text:
                    failures.append(
                        f"{relative}: the mark has no opacity cascade at {step} — "
                        "flat sweeps are prohibited"
                    )
            if 'x="28.5" y="28.5" width="7" height="7"' not in mark_text:
                failures.append(
                    f"{relative}: the inline mark has no centre square"
                )
            if "rx=" in mark_text or "ry=" in mark_text:
                failures.append(
                    f"{relative}: the mark has rounded corners — nothing in the "
                    "system is rounded except the app-icon tile"
                )

        # -------------------------------------------------------- gate (h)
        if STATUS_STRIP_SENTINEL not in flat:
            failures.append(
                f"{relative}: the pre-release status strip is missing — every page "
                f"must carry {STATUS_STRIP_SENTINEL!r}"
            )

        for opening in re.findall(r"<pre\b[^>]*>", document):
            if "tabindex=" not in opening:
                failures.append(
                    f"{relative}: a <pre> scrolls horizontally with no tab stop — "
                    "its clipped content is unreachable by keyboard"
                )
                break
        for opening in re.findall(r'<div class="table-scroll"[^>]*>', document):
            if "tabindex=" not in opening:
                failures.append(
                    f"{relative}: a table scroll container has no tab stop"
                )
                break
        if re.search(r"<table\b", document) and not re.search(
            r'<div class="table-scroll"', document
        ):
            failures.append(
                f"{relative}: a bare <table> — a wide table then scrolls the page "
                "sideways instead of scrolling inside its own container"
            )
        if '<link rel="icon" href="/favicon.ico"' not in document:
            failures.append(f"{relative}: favicon.ico is shipped but not linked")

        if expected_mode in {"public_docs", "production"} and relative not in PROVENANCE_ROUTES:
            for label, value in (
                ("availability", release.get("availability", "")),
                ("release version", release.get("release_version", "")),
                ("contract digest", release.get("public_contract_sha256", "")[:12]),
            ):
                if value and value in document:
                    failures.append(
                        f"{relative}: {label} {value!r} appears outside the provenance pages"
                    )
        if expected_mode in {"staging", "public_docs"}:
            lowered_document = lowered_flat
            if relative in LEGAL_DRAFT_ROUTES:
                for sentinel in LEGAL_DRAFT_SENTINELS:
                    if sentinel not in lowered_document:
                        failures.append(
                            f"{relative}: review-draft boundary is missing {sentinel!r}"
                        )
                if 'class="draft-notice"' not in document:
                    failures.append(
                        f"{relative}: the review-draft notice component is absent"
                    )
                if 'class="notice-band"' not in document:
                    failures.append(
                        f"{relative}: the review-draft notice is not a page-level "
                        "band — inside the article it falls below the navigation "
                        "on a narrow viewport"
                    )
                elif "sl-markdown-content" not in document:
                    failures.append(
                        f"{relative}: no article region to place the review-draft band above"
                    )
                elif document.index('class="notice-band"') > document.index(
                    "sl-markdown-content"
                ):  # noqa: E501 — raw document order, not the flattened copy
                    # The old assertion compared against the sidebar, which in
                    # Starlight precedes the content in source order and can
                    # never pass. The property is unchanged: the band renders
                    # above the article.
                    failures.append(
                        f"{relative}: the review-draft band renders after the article"
                    )
            for overclaim in LEGAL_OVERCLAIMS:
                if overclaim in lowered_document:
                    failures.append(
                        f"{relative}: legal overclaim {overclaim!r} — nothing has had counsel review"
                    )
        for link in parser.links:
            target = local_target(root, link)
            if target is not None and not target.exists():
                failures.append(f"{relative}: broken internal link {link}")

    # ------------------------------------------------------------ the palette
    if not css_bundles:
        failures.append(
            f"no stylesheet under {VENDOR_BUNDLE_DIR}/ — the palette cannot be checked"
        )
    else:
        lowered_css = bundled_css.lower()
        for required in REQUIRED_TOKENS:
            if required.lower() not in lowered_css:
                failures.append(
                    f"{VENDOR_BUNDLE_DIR}/*.css: canonical kaleidoscope-dark token "
                    f"{required} is absent"
                )
        for drifted in DRIFTED_TOKENS:
            if drifted in lowered_css:
                failures.append(
                    f"{VENDOR_BUNDLE_DIR}/*.css: drifted token {drifted} — use the "
                    "kaleidoscope-dark value"
                )

    # Every syntax colour, positively. Expressive Code emits each highlighted
    # run as `style="--0:#RRGGBB"` inline in the HTML, so the set of colours a
    # reader sees in code is enumerable from the artifact with no browser and
    # no guessing. Measured across 24 routes and 8,865 rendered elements, the
    # whole site draws from nine values; this asserts the code half of that and
    # names the file to edit when it stops being true.
    syntax_colours: dict[str, str] = {}
    for relative, path in sorted(actual.items()):
        if path.suffix != ".html":
            continue
        for colour in re.findall(
            r"--\d+:(#[0-9a-fA-F]{6})", path.read_text(encoding="utf-8", errors="replace")
        ):
            syntax_colours.setdefault(colour.lower(), relative)
    for colour in sorted(syntax_colours):
        if colour not in PALETTE:
            failures.append(
                f"syntax colour {colour} is outside the kaleidoscope-dark palette "
                f"(first seen in {syntax_colours[colour]}) — the code theme is "
                "`kaleidoscopeCode` in astro.config.mjs, and Expressive Code will "
                "also derive its own colour unless minSyntaxHighlightingColorContrast "
                "is 0"
            )

    # Dead weight in the served directory. Starlight bundled `ui-core` +
    # `Search` — 96,669 bytes, a mutually-importing pair reachable from 0 of 41
    # pages — even with pagefind off. No browser fetched it, so nothing looked
    # wrong; it was simply committed and served on every deploy, and it is
    # exactly the kind of thing that makes an artifact diff unreadable. A chunk
    # is reachable if a page names it, or if a chunk a page names imports it.
    js_chunks = {
        relative.rsplit("/", 1)[-1]: path
        for relative, path in actual.items()
        if relative.startswith(f"{VENDOR_BUNDLE_DIR}/") and relative.endswith(".js")
    }
    if js_chunks:
        chunk_text = {
            name: path.read_text(encoding="utf-8", errors="replace")
            for name, path in js_chunks.items()
        }
        named_by_page = {
            name
            for name in js_chunks
            if any(
                name in path.read_text(encoding="utf-8", errors="replace")
                for relative, path in actual.items()
                if relative.endswith(".html")
            )
        }
        reachable = set(named_by_page)
        changed = True
        while changed:
            changed = False
            for name in list(reachable):
                for other in js_chunks:
                    if other not in reachable and other in chunk_text[name]:
                        reachable.add(other)
                        changed = True
        for name in sorted(set(js_chunks) - reachable):
            failures.append(
                f"{VENDOR_BUNDLE_DIR}/{name}: {js_chunks[name].stat().st_size} bytes "
                "no page can reach — override the component that pulls it in, "
                "rather than shipping it"
            )

    robots_path = root / "robots.txt"
    robots = robots_path.read_text(encoding="utf-8") if robots_path.is_file() else ""
    if not robots:
        failures.append("missing robots.txt")
    if expected_mode in {"public_docs", "production"} and "Allow: /" not in robots:
        failures.append(f"{expected_mode} robots does not allow root")
    if expected_mode == "staging" and "Disallow: /" not in robots:
        failures.append("staging robots does not disallow root")

    sitemap_path = root / "sitemap.xml"
    if not sitemap_path.is_file():
        failures.append("missing sitemap.xml")
    else:
        try:
            sitemap = ElementTree.parse(sitemap_path)
        except ElementTree.ParseError:
            failures.append("sitemap.xml is invalid")
        else:
            namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            sitemap_urls = {
                element.text
                for element in sitemap.findall("s:url/s:loc", namespace)
                if element.text
            }
            expected_urls = {f"{DOMAIN}/"}
            expected_urls.update(
                f"{DOMAIN}/" + relative.removesuffix("index.html")
                for relative in EXPECTED_HTML - NOINDEX_HTML - {"index.html"}
            )
            if sitemap_urls != expected_urls:
                failures.append(
                    f"sitemap URL inventory mismatch: expected-only={sorted(expected_urls - sitemap_urls)}, actual-only={sorted(sitemap_urls - expected_urls)}"
                )

    security_path = root / ".well-known" / "security.txt"
    security = security_path.read_text(encoding="utf-8") if security_path.is_file() else ""
    if not security:
        failures.append("missing .well-known/security.txt")
    if expected_mode == "staging" and "LOCAL BUILD ONLY" not in security:
        failures.append("staging security.txt is not marked as a local build")
    if expected_mode == "public_docs" and "DOCUMENTATION PREVIEW" not in security:
        failures.append("public documentation security.txt is not marked as preview")
    if expected_mode == "production" and "LOCAL BUILD ONLY" in security:
        failures.append("production security.txt still carries the local-build marker")

    llms_path = root / "llms.txt"
    llms = llms_path.read_text(encoding="utf-8") if llms_path.is_file() else ""
    if not llms:
        failures.append("missing llms.txt")
    llms_lower = " ".join(llms.split()).lower()
    # llms.txt is linked from the footer of every page, so it is reader-facing
    # copy and not a machine record. It used to close with a paragraph of
    # internal work-item identifiers and build digests; these are the honest
    # claims that replaced it, and each one is load-bearing.
    for required in (
        "`search` and `remember`",
        "proprietary object code",
        # Five claims were removed here when 0.0.5 published, because each had
        # become false and the gate was requiring the site to state it:
        # "kaleidoscope is not released", "neither package is published",
        # "you cannot download a build for any platform", "provider not
        # configured", and "a compiler check for the memory engine and nothing
        # more". Four platforms now build and publish, and the package installs.
        #
        # What replaced them is the one thing a reader most needs and cannot
        # discover by trying: it will not run without a key.
        "npm install -g @kleos-research/kaleidoscope",
        "needs a key to run",
        "contact@kleosresearch.xyz",
        "windows is not supported",
        "nothing is signed for release",
        "reviewed by counsel but not adopted",
        "hosted memory does not exist",
        # /docs/benchmarks/ publishes results now. What is still true, and
        # what this file must still say, is that the method is not out.
        "the full benchmark method is not published yet",
        "/docs/privacy/",
        "/status/",
        "/docs/skill/",
        "/skill.md",
        "/status.json",
        "/platform-support.json",
        "/reference/kaleidoscope-cli.txt",
        "/reference/kaleidoscope-mcp.json",
    ):
        if required.lower() not in llms_lower:
            failures.append(f"llms.txt missing {required!r}")
    if "no benchmark score is published" in llms_lower:
        failures.append(
            "llms.txt still says no benchmark score is published; /docs/benchmarks/ "
            "publishes results, so the site would contradict itself"
        )

    llms_full_path = root / "llms-full.txt"
    llms_full = (
        llms_full_path.read_text(encoding="utf-8") if llms_full_path.is_file() else ""
    )
    if not llms_full:
        failures.append("missing llms-full.txt")
    for relative in sorted(EXPECTED_HTML - NOINDEX_HTML - {"index.html"}):
        route = "/" + relative.removesuffix("index.html")
        if f"URL: {DOMAIN}{route}" not in llms_full:
            failures.append(f"llms-full.txt missing canonical section for {route}")
    for required in (
        "# Public agent skill",
        "# Full CLI help text",
        "# Tool reference",
        "# Status record",
        "# Platform support record",
    ):
        if required not in llms_full:
            failures.append(f"llms-full.txt missing {required!r}")

    # The text mirror carries the same chrome the HTML does. Scanning only the
    # HTML let a per-page release tag survive here after it was removed there.
    provenance_paths = {
        "/" + relative.removesuffix("index.html") for relative in PROVENANCE_ROUTES
    }
    identifiers = [
        ("availability", release.get("availability", "")),
        ("release version", release.get("release_version", "")),
        ("contract digest", release.get("public_contract_sha256", "")[:12]),
    ]
    for chunk in llms_full.split("\n\n---\n\n"):
        url = re.search(rf"^URL: {re.escape(DOMAIN)}(\S*/)$", chunk, flags=re.M)
        if url is None:
            continue
        route = url.group(1)
        if expected_mode in {"public_docs", "production"} and (
            route not in provenance_paths
        ):
            for label, value in identifiers:
                if value and value in chunk:
                    failures.append(
                        f"llms-full.txt {route}: {label} {value!r} appears "
                        "outside the provenance pages"
                    )
        page_path = route.lstrip("/") + "index.html"
        if expected_mode in {"staging", "public_docs"} and (
            page_path in LEGAL_DRAFT_ROUTES
        ):
            for sentinel in LEGAL_DRAFT_SENTINELS:
                if sentinel not in " ".join(chunk.split()).lower():
                    failures.append(
                        f"llms-full.txt {route}: review-draft boundary is "
                        f"missing {sentinel!r}"
                    )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify a built Kaleidoscope documentation artifact."
    )
    parser.add_argument("root", type=Path)
    parser.add_argument(
        "--mode", choices=("staging", "public_docs", "production"), required=True
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=None,
        help="the repository root holding src/ and astro.config.mjs; "
        "defaults to the artifact's parent directory",
    )
    parser.add_argument(
        "--skip-source-scan",
        action="store_true",
        help="verify a standalone artifact with no source tree beside it. The "
        "source half of gates (a) and (b) does not run, and the artifact half "
        "is not a substitute for it.",
    )
    args = parser.parse_args()
    failures = verify(
        args.root.resolve(),
        args.mode,
        source_root=args.source_root.resolve() if args.source_root else None,
        scan_sources=not args.skip_source_scan,
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    note = " (source scan skipped)" if args.skip_source_scan else ""
    print(f"verified {args.mode} documentation artifact at {args.root}{note}")


if __name__ == "__main__":
    main()
