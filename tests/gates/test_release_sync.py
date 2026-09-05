"""Drive the release sync to a known positive, and to a known negative.

`scripts/sync_from_release.py --check` is the gate that keeps this public
repository internally consistent with the one engine release it describes:
every derived file under src/data and the release record at the root are
recomputed from the committed pin and the committed vendored assets, offline,
and any file that disagrees fails the build by name.

As with every other gate here, the proof has two halves. The unmodified tree
must be ACCEPTED, or a check that refuses everything would catch every planted
violation and prove nothing. And a tree with exactly one thing wrong must be
REFUSED, with a message naming the file that is wrong -- because a refusal that
does not say where is a refusal somebody has to grep for.

Nothing here touches the repository. The tree is copied into a temporary
directory, a release-assets directory is assembled from that copy's own
vendored files, `--apply` is run against it there, and the plants mutate the
copy. Standard library only, no build, no node.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYNC = "scripts/sync_from_release.py"

# One row per row of the engine's packaging table. Four ship; the two Windows
# rows are in the table so that a manifest can say, by name, that nothing was
# built for them -- which is a different statement from leaving them out.
PLATFORMS = (
    ("darwin-arm64", "macOS", "Apple Silicon", "aarch64-apple-darwin", True, True),
    ("darwin-x64", "macOS", "x86_64", "x86_64-apple-darwin", True, False),
    ("linux-arm64", "Linux", "arm64", "aarch64-unknown-linux-gnu", True, False),
    ("linux-x64", "Linux", "x86_64", "x86_64-unknown-linux-gnu", True, False),
    ("win32-arm64", "Windows", "arm64", "aarch64-pc-windows-msvc", False, False),
    ("win32-x64", "Windows", "x86_64", "x86_64-pc-windows-msvc", False, False),
)
ENTRY_PACKAGE = "@kleos-research/kaleidoscope"
CONTRACT_SCHEMA = "kaleidoscope.public-contract.v1"
MCP_PROTOCOL_REVISION = "2025-11-25"

# Manifest path -> the repository file whose bytes it carries.
ASSETS = {
    "kscope-help.txt": "src/data/kaleidoscope-cli.txt",
    "instructions/SKILL.md": "src/data/public/SKILL.md",
    "instructions/AGENTS.md": "src/data/public/snippets/AGENTS.md",
    "instructions/CLAUDE.md": "src/data/public/snippets/CLAUDE.md",
    "instructions/cursor-kaleidoscope.mdc": "src/data/public/snippets/cursor-kaleidoscope.mdc",
}


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def build_release_assets(
    tree: Path,
    out: Path,
    *,
    version: str = "0.0.5",
    source_commit: str = "a26de88dfee9a6d18fe0cfe59cc01fd7c8f77f9c",
    released_on: str = "2026-08-30",
    contract: bytes | None = None,
) -> Path:
    """Assemble a release-assets directory from a tree's own vendored files.

    What the engine's release job would produce, built from what this
    repository already carries, so the manifest describes a release whose
    assets are known to be the committed ones. `contract` is the public
    contract's bytes; when none is given a minimal one is written, because the
    sync reads three fields of it and nothing more.
    """
    out.mkdir(parents=True, exist_ok=True)
    (out / "instructions").mkdir(exist_ok=True)
    entries: dict[str, dict] = {}
    for relative, source in ASSETS.items():
        content = (tree / source).read_bytes()
        (out / relative).write_bytes(content)
        entries[relative] = {"path": relative, "sha256": digest(content)}

    if contract is None:
        contract = (
            json.dumps(
                {
                    "schema_version": CONTRACT_SCHEMA,
                    "mcp": {"protocol": {"maximum": MCP_PROTOCOL_REVISION, "minimum": MCP_PROTOCOL_REVISION}},
                    "product": {"executable": "kscope", "name": "Kaleidoscope", "version": version},
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
    (out / "kaleidoscope-public-contract.json").write_bytes(contract)
    (out / "kaleidoscope-public-contract.provenance.json").write_text(
        json.dumps(
            {
                "schema_version": "kaleidoscope.public-contract-provenance.v1",
                "contract_sha256": digest(contract),
                "source_commit": source_commit,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schema_version": "kaleidoscope.release-manifest.v1",
        "release_version": version,
        "source_commit": source_commit,
        "released_on": released_on,
        "availability": "available_with_key",
        "channels": {
            "npm": {
                "entry_package": ENTRY_PACKAGE,
                "platform_packages": {
                    slug: f"{ENTRY_PACKAGE}-{slug}" for slug, *_, built, _run in PLATFORMS if built
                },
            }
        },
        "platforms": [
            {
                "slug": slug,
                "os": os_name,
                "architecture": architecture,
                "triple": triple,
                "built": built,
                "published": built,
                "native_build_runner": run,
            }
            for slug, os_name, architecture, triple, built, run in PLATFORMS
        ],
        # No executable is in the fixture: the digest of the platform package's
        # program is a fact the docs record and never verify, so a stand-in
        # that is at least the right shape is what a fixture can honestly carry.
        "executables": {
            slug: {"sha256": digest(f"kscope for {slug}".encode()), "bytes": 1}
            for slug, *_, built, _run in PLATFORMS
            if built
        },
        "public_contract": {
            "path": "kaleidoscope-public-contract.json",
            "sha256": digest(contract),
            "schema_version": CONTRACT_SCHEMA,
            "mcp_protocol_revision": MCP_PROTOCOL_REVISION,
        },
        "cli_help": entries["kscope-help.txt"],
        "instruction_assets": {
            "skill": entries["instructions/SKILL.md"],
            "agents": entries["instructions/AGENTS.md"],
            "claude": entries["instructions/CLAUDE.md"],
            "cursor": entries["instructions/cursor-kaleidoscope.mdc"],
        },
    }
    (out / "release.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return out


class ReleaseSyncGateTest(unittest.TestCase):
    """--apply against a fixture, then --check with one thing broken at a time."""

    def setUp(self) -> None:
        work = Path(tempfile.mkdtemp(prefix="kdocs-sync-"))
        self.addCleanup(shutil.rmtree, work, True)
        self.tree = work / "tree"
        self.tree.mkdir()
        for directory in ("src", "scripts"):
            shutil.copytree(ROOT / directory, self.tree / directory)
        for name in ("verify_site.py", "public-docs-release.json"):
            shutil.copy2(ROOT / name, self.tree / name)
        self.release = build_release_assets(self.tree, work / "release-assets")

    def sync(self, *argv: str) -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(self.tree / SYNC), *argv],
            cwd=self.tree,
            capture_output=True,
            text=True,
        )
        return result.returncode, (result.stdout + result.stderr).strip()

    def applied(self) -> None:
        status, out = self.sync("--apply", "--release", str(self.release))
        self.assertEqual(status, 0, out)

    def snapshot(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.tree).as_posix(): path.read_bytes()
            for path in self.tree.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }

    # ------------------------------------------------------------- controls
    def test_the_synced_tree_is_accepted(self) -> None:
        self.applied()
        status, out = self.sync("--check")
        self.assertEqual(status, 0, out)
        self.assertIn("agrees with every derived file", out)

    def test_apply_is_deterministic(self) -> None:
        # A generated file with the same inputs is byte-identical every time,
        # or the pull request the engine opens would never be empty.
        self.applied()
        before = self.snapshot()
        status, out = self.sync("--apply", "--release", str(self.release))
        self.assertEqual(status, 0, out)
        self.assertIn("nothing changed", out)
        self.assertEqual(self.snapshot(), before)

    def test_apply_touches_only_the_derived_set(self) -> None:
        # The fixture is built from the tree's own vendored files, so the only
        # files --apply may change are the ones it derives. Everything authored
        # here -- every page, every other record -- must come through untouched.
        before = self.snapshot()
        self.applied()
        after = self.snapshot()
        changed = sorted(path for path in before if after.get(path) != before[path])
        allowed = {
            "release-pin.json",
            "public-docs-release.json",
            "src/data/status.json",
            "src/data/platform-support.json",
            "src/data/kscope-surface.json",
            "scripts/make_manifest.py",
            "verify_site.py",
        }
        self.assertLessEqual(set(changed), allowed, changed)
        self.assertEqual(sorted(set(after) - set(before)), ["release-pin.json"])

    def test_nothing_written_carries_a_private_marker_or_the_internal_register(self) -> None:
        sys.path.insert(0, str(ROOT))
        import verify_site  # noqa: E402

        self.applied()
        for relative in (
            "src/data/status.json",
            "src/data/platform-support.json",
            "src/data/kscope-surface.json",
        ):
            text = (self.tree / relative).read_text(encoding="utf-8")
            failures: list[str] = []
            verify_site.scan_private_markers(relative, text, failures)
            verify_site.scan_vocabulary(relative, text, failures)
            self.assertEqual(failures, [])

    def test_check_takes_no_arguments(self) -> None:
        status, out = self.sync("--check", "--release", str(self.release))
        self.assertNotEqual(status, 0)
        self.assertIn("--check takes no arguments", out)

    # ------------------------------------------------------------- positives
    def test_one_byte_of_the_vendored_skill_is_refused_by_name(self) -> None:
        self.applied()
        skill = self.tree / "src/data/public/SKILL.md"
        content = bytearray(skill.read_bytes())
        content[-1] = ord("X") if content[-1] != ord("X") else ord("Y")
        skill.write_bytes(bytes(content))
        status, out = self.sync("--check")
        self.assertNotEqual(status, 0)
        self.assertIn("FAIL: src/data/public/SKILL.md", out)

    def test_a_hand_edited_version_in_the_file_of_record_is_refused_by_name(self) -> None:
        self.applied()
        status_path = self.tree / "src/data/status.json"
        text = status_path.read_text(encoding="utf-8")
        self.assertIn('"version": "0.0.5"', text)
        status_path.write_text(text.replace('"version": "0.0.5"', '"version": "9.9.9"', 1), encoding="utf-8")
        status, out = self.sync("--check")
        self.assertNotEqual(status, 0)
        self.assertIn("FAIL: src/data/status.json", out)

    def test_a_missing_pin_is_refused_rather_than_skipped(self) -> None:
        self.applied()
        (self.tree / "release-pin.json").unlink()
        status, out = self.sync("--check")
        self.assertNotEqual(status, 0)
        self.assertIn("release-pin.json", out)

    def test_a_manifest_that_disagrees_with_its_own_assets_writes_nothing(self) -> None:
        before = self.snapshot()
        manifest_path = self.release / "release.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["instruction_assets"]["agents"]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        status, out = self.sync("--apply", "--release", str(self.release))
        self.assertNotEqual(status, 0)
        self.assertIn("instruction_assets.agents", out)
        self.assertEqual(self.snapshot(), before, "a refused --apply must leave the tree as it found it")

    def test_an_asset_carrying_a_developer_path_is_refused_before_it_is_written(self) -> None:
        # Gate (a) has no exemption anywhere, and neither does this script.
        agents = self.release / "instructions/AGENTS.md"
        content = agents.read_bytes() + b"\nSee /Users/someone/notes.md\n"
        agents.write_bytes(content)
        manifest_path = self.release / "release.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["instruction_assets"]["agents"]["sha256"] = digest(content)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        before = self.snapshot()
        status, out = self.sync("--apply", "--release", str(self.release))
        self.assertNotEqual(status, 0)
        self.assertIn("private marker", out)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
