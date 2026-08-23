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
# Twelve bindings. Each one is a promise that the published bytes are the
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
    missing = []
    for relative, source_relative in sorted(PUBLIC_SOURCE_BINDINGS.items()):
        source = repo_root / source_relative
        if not source.is_file():
            missing.append(source_relative)
            continue
        if relative not in emitted:
            missing.append(f"{relative} (declared source {source_relative} is present)")
            continue
        public_source_sha256[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
    if missing:
        # Fail closed. A binding that quietly drops out of the manifest is a
        # verbatim-republication claim that nothing checks any more.
        raise SystemExit(
            "cannot bind verbatim-republished sources: " + ", ".join(sorted(missing))
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "release": dict(release),
        "public_source_sha256": public_source_sha256,
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
        f"{len(manifest['public_source_sha256'])} bound sources, mode {args.mode}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
