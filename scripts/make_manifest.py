#!/usr/bin/env python3
"""Write site-manifest.json for a built Kaleidoscope documentation artifact.

The old generator wrote this file as its last act, from data it already had in
memory. Astro emits the artifact and knows nothing about it, so the manifest is
now a separate step that runs after `astro build` and before `verify_site.py`.

Three things it must keep true, because the verifier checks all three:

* the declared file set equals the actual file set, exactly;
* every declared sha256 and size matches the bytes on disk;
* `public_source_sha256` binds each verbatim-republished file to the digest of
  the SOURCE it claims to reproduce, so a page that "republishes" a file it has
  quietly edited fails.

That third check compares the artifact to a file in this repository, which
catches an edit made to the built page and nothing else: for the files this
repository does not author, the copy was free to drift from the thing it is a
copy OF, and it had. `PUBLIC_UPSTREAM_SOURCES` closes that half. Each entry
records where the bytes came from and the sha256 they had when they were taken,
and the manifest step refuses when the local copy no longer matches. The digest
is written down here rather than fetched because this build reaches nothing but
npm: a recorded digest cannot notice that upstream has moved on, but it does
make the two disagree out loud the moment either side is edited, which is the
failure that actually happened.

Six files still have no upstream record: the four product terms under
`src/data/legal/`, the CC BY text beside them, and the documentation licence.
They are named in `UNRECORDED_UPSTREAM` rather than left unmentioned, so the
gap is a line someone can close rather than an absence nobody sees. Every bound
source is in exactly one of the three sets, and a binding in none of them is
refused, because the way this check stops working is a new file that quietly
belongs to no category.

The release block is not re-validated here in a second implementation. It is
read back out of `scripts/release-metadata.mjs` through node, so the manifest
carries the same four fields the build itself refused-or-accepted on. A second
Python copy of those six refusals would be a second thing to drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCHEMA_VERSION = "kaleidoscope.docs-artifact.v1"

# artifact path -> the source file it republishes verbatim.
# Thirteen bindings. Each one is a promise that the published bytes are the
# source's bytes; the verifier turns the promise into a check.
PUBLIC_SOURCE_BINDINGS = {
    "SKILL.md": "src/data/public/SKILL.md",
    "agent-instructions.md": "src/data/public/agent-instructions.md",
    "snippets/AGENTS.md": "src/data/public/snippets/AGENTS.md",
    "snippets/CLAUDE.md": "src/data/public/snippets/CLAUDE.md",
    "snippets/cursor-kaleidoscope.mdc": "src/data/public/snippets/cursor-kaleidoscope.mdc",
    "documentation-license.txt": "src/data/documentation-license.txt",
    "legal/CC-BY-4.0.txt": "src/data/legal/CC-BY-4.0.txt",
    "legal/ENGINE-EULA.txt": "src/data/legal/ENGINE-EULA.txt",
    "legal/PRIVACY-NOTICE.txt": "src/data/legal/PRIVACY-NOTICE.txt",
    "legal/SECURITY-POLICY.txt": "src/data/legal/SECURITY-POLICY.txt",
    "legal/SUPPORT-POLICY.txt": "src/data/legal/SUPPORT-POLICY.txt",
    "reference/kaleidoscope-cli.txt": "src/data/kaleidoscope-cli.txt",
    "reference/kscope-cli.txt": "src/data/kaleidoscope-cli.txt",
}

# repository source -> where those bytes came from, and what they hashed then.
#
# `where` is a coordinate a person can follow; `sha256` is what makes the copy
# checkable without following it. A local copy that no longer hashes to its
# recorded digest is a fork, and this script refuses rather than publishing it
# under a page that says the bytes are the installed ones.
PUBLIC_UPSTREAM_SOURCES = {
    "src/data/public/SKILL.md": {
        "where": (
            "kaleidoscope: crates/kaleidoscope-manager/skills/"
            "use-kaleidoscope/SKILL.md"
        ),
        "what": "the skill file `kscope init` installs",
        "sha256": "ec3a59d62887c0839e59caf072abfebf14ad150536f51087fb3d0321ee33096e",
    },
    "src/data/public/snippets/AGENTS.md": {
        "where": "kaleidoscope: crates/kaleidoscope-manager/snippets/AGENTS.md",
        "what": "the block `kscope init` appends to AGENTS.md",
        "sha256": "252091b601ea27da5317a4265d28739bfdcf894318d15f27e1bf1bcdf97f11bf",
    },
    "src/data/public/snippets/CLAUDE.md": {
        "where": "kaleidoscope: crates/kaleidoscope-manager/snippets/CLAUDE.md",
        "what": "the block `kscope init` appends to CLAUDE.md",
        "sha256": "ab8e49389f1bb6d3e4f41703600df7de0abb3ff3b90678ec1bea76e67112b4a2",
    },
    "src/data/public/snippets/cursor-kaleidoscope.mdc": {
        "where": (
            "kaleidoscope: crates/kaleidoscope-manager/snippets/"
            "cursor-kaleidoscope.mdc"
        ),
        "what": "the rule file `kscope init` writes for Cursor",
        "sha256": "452d17ab59f5a826de697974d602d62f01ebe3f57d788a14291842b51e7f3cbc",
    },
    "src/data/kaleidoscope-cli.txt": {
        "where": "@kleos-research/kaleidoscope@0.0.5: `kscope --help`",
        "what": "the help text of the executable the package installs",
        "sha256": "e3b2e40b0680d8468af78ab156a888252b3d5607e223e65e0679e076aa2db0c5",
    },
}

# Bound sources whose upstream is not recorded, and which therefore have only
# the self-comparison. Naming them is the point: an unrecorded upstream that
# nobody lists is indistinguishable from one that needs no record.
UNRECORDED_UPSTREAM = {
    "src/data/documentation-license.txt",
    "src/data/legal/CC-BY-4.0.txt",
    "src/data/legal/ENGINE-EULA.txt",
    "src/data/legal/PRIVACY-NOTICE.txt",
    "src/data/legal/SECURITY-POLICY.txt",
    "src/data/legal/SUPPORT-POLICY.txt",
}

# Bound sources this repository writes. There is nothing upstream to compare
# them to, which is a different statement from "we have not looked".
AUTHORED_HERE = {
    "src/data/public/agent-instructions.md",
}


def read_release_metadata(repo_root: Path, mode: str, metadata_path: Path | None) -> dict:
    """Ask scripts/release-metadata.mjs, the one implementation of gate (c)."""
    module = (repo_root / "scripts" / "release-metadata.mjs").as_posix()
    program = (
        "import('file://%s')"
        ".then(m => console.log(JSON.stringify(m.readReleaseMetadata(process.argv[1]))))"
        ".catch(error => { console.error(error.message); process.exit(1); })" % module
    )
    env = None
    if metadata_path is not None:
        import os

        env = dict(os.environ)
        env["KALEIDOSCOPE_DOCS_RELEASE"] = str(metadata_path)
    completed = subprocess.run(
        ["node", "-e", program, mode],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(
            "release metadata refused the build: "
            + (completed.stderr.strip() or "no message")
        )
    return json.loads(completed.stdout)


def build_manifest(root: Path, repo_root: Path, mode: str, release: dict) -> dict:
    manifest_path = root / "site-manifest.json"
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path == manifest_path:
            continue
        content = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "size_bytes": len(content),
            }
        )
    emitted = {entry["path"] for entry in files}

    public_source_sha256 = {}
    public_upstream = {}
    missing = []
    unclassified = []
    drifted = []
    for relative, source_relative in sorted(PUBLIC_SOURCE_BINDINGS.items()):
        source = repo_root / source_relative
        if not source.is_file():
            missing.append(source_relative)
            continue
        if relative not in emitted:
            missing.append(f"{relative} (declared source {source_relative} is present)")
            continue
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        public_source_sha256[relative] = digest

        upstream = PUBLIC_UPSTREAM_SOURCES.get(source_relative)
        if upstream is None:
            if source_relative not in UNRECORDED_UPSTREAM | AUTHORED_HERE:
                unclassified.append(source_relative)
            continue
        if digest != upstream["sha256"]:
            drifted.append(
                f"{source_relative}: {digest} here, {upstream['sha256']} at "
                f"{upstream['where']}"
            )
            continue
        public_upstream[relative] = {
            "sha256": upstream["sha256"],
            "what": upstream["what"],
            "where": upstream["where"],
        }
    if missing:
        # Fail closed. A binding that quietly drops out of the manifest is a
        # verbatim-republication claim that nothing checks any more.
        raise SystemExit(
            "cannot bind verbatim-republished sources: " + ", ".join(sorted(missing))
        )
    if unclassified:
        raise SystemExit(
            "bound source with no upstream record and no reason given: "
            + ", ".join(sorted(unclassified))
            + " — add it to PUBLIC_UPSTREAM_SOURCES, UNRECORDED_UPSTREAM or "
            "AUTHORED_HERE"
        )
    if drifted:
        # The failure this check exists for: the site keeps saying it publishes
        # the installed bytes while the copy quietly becomes its own document.
        # Re-copy from the named source, or, if the source moved first, record
        # its new digest deliberately.
        raise SystemExit(
            "a republished file no longer matches the source it copies: "
            + "; ".join(sorted(drifted))
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "release": dict(release),
        "public_source_sha256": public_source_sha256,
        "public_upstream_sha256": public_upstream,
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="the built artifact, normally dist")
    parser.add_argument(
        "--mode", choices=("staging", "public_docs", "production"), required=True
    )
    parser.add_argument(
        "--release-metadata",
        type=Path,
        default=None,
        help="path to the immutable release metadata; omitted, staging uses placeholders",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"no built artifact at {root}")
    repo_root = Path(__file__).resolve().parents[1]
    metadata_path = (
        args.release_metadata.resolve() if args.release_metadata is not None else None
    )
    if args.mode == "staging":
        # A staging build uses the placeholders and does not read the
        # public-docs file, even when the npm script passes its path
        # unconditionally. Matching scripts/release-metadata.mjs here is what
        # makes `DOCS_MODE=staging npm run build` produce a staging artifact
        # rather than one stamped `documentation_preview` that the verifier then
        # refuses for a reason nobody would have guessed from the message.
        metadata_path = None
    if metadata_path is not None and not metadata_path.is_file() and args.mode != "staging":
        # The same refusal the JS module makes, reached before node is asked, so
        # the message is identical whichever half of the build notices first.
        raise SystemExit(f"{args.mode} build requires immutable release metadata")
    release = read_release_metadata(repo_root, args.mode, metadata_path)
    manifest = build_manifest(root, repo_root, args.mode, release)
    (root / "site-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"wrote {root / 'site-manifest.json'}: {len(manifest['files'])} files, "
        f"{len(manifest['public_source_sha256'])} bound sources, "
        f"{len(manifest['public_upstream_sha256'])} of them checked against "
        f"their upstream, mode {args.mode}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
