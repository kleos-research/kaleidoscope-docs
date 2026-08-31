"""Tests for the documentation gates.

Python, standard library only. The generator these tests used to import is
gone, so the shape changed: they run against a BUILT artifact (`dist/`, built
on demand if it is not there) and against the committed `docs/`, and they drive
the release-metadata refusals through node, which is where that gate now lives.

Nothing here skips. A test that skips when its input is missing is a pass
condition satisfied hardest when the thing under test is broken; if node is not
installed or the build fails, these fail and say so.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import verify_site  # noqa: E402

RELEASE_METADATA = ROOT / "public-docs-release.json"
GOOD_METADATA = {
    "availability": "documentation_preview",
    "public_contract_sha256": "a" * 64,
    "release_version": "0.1.0-rc.1",
    "updated_at": "2026-08-22",
}


def npm(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    return subprocess.run(
        ["npm", *args], cwd=ROOT, env=merged, capture_output=True, text=True
    )


def make_manifest(target: Path, mode: str) -> subprocess.CompletedProcess:
    argv = [
        sys.executable,
        str(ROOT / "scripts" / "make_manifest.py"),
        str(target),
        "--mode",
        mode,
    ]
    if mode != "staging":
        argv += ["--release-metadata", str(RELEASE_METADATA)]
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)


def ensure_dist() -> Path:
    """The public-docs build, built once per test run if it is not already there."""
    dist = ROOT / "dist"
    if (dist / "site-manifest.json").is_file():
        return dist
    result = npm("run", "build")
    if result.returncode != 0:
        raise AssertionError(
            "npm run build failed; the gates cannot be checked against an "
            f"artifact that does not exist.\n{result.stdout}\n{result.stderr}"
        )
    return dist


def node_release_metadata(mode: str, metadata_path: Path | None) -> tuple[int, str]:
    """Call readReleaseMetadata through node and report (exit status, message)."""
    program = (
        "import('./scripts/release-metadata.mjs')"
        ".then(m => { m.readReleaseMetadata(process.argv[1]); console.log('ACCEPTED'); })"
        ".catch(error => { console.log(error.message); process.exit(1); })"
    )
    env = dict(os.environ)
    if metadata_path is not None:
        env["KALEIDOSCOPE_DOCS_RELEASE"] = str(metadata_path)
    result = subprocess.run(
        ["node", "-e", program, mode], cwd=ROOT, env=env, capture_output=True, text=True
    )
    return result.returncode, (result.stdout + result.stderr).strip()


class ReleaseMetadataGateTest(unittest.TestCase):
    """Gate (c). Six refusals, each asserted by its own message.

    The old CI test asserted only that the build exited nonzero, which an
    ImportError or a renamed flag satisfies just as well as a working refusal.
    """

    def write(self, **overrides) -> Path:
        payload = dict(GOOD_METADATA)
        for key, value in overrides.items():
            if value is ...:
                payload.pop(key, None)
            else:
                payload[key] = value
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(payload, handle)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return Path(handle.name)

    def test_valid_metadata_is_accepted(self) -> None:
        status, message = node_release_metadata("public_docs", self.write())
        self.assertEqual(status, 0, message)
        self.assertIn("ACCEPTED", message)

    def test_refusal_1_no_metadata_file(self) -> None:
        for mode in ("public_docs", "production"):
            with self.subTest(mode=mode):
                status, message = node_release_metadata(
                    mode, Path("/nonexistent/release.json")
                )
                self.assertNotEqual(status, 0)
                self.assertIn(f"{mode} build requires immutable release metadata", message)

    def test_refusal_1_staging_may_run_without_a_file(self) -> None:
        status, message = node_release_metadata(
            "staging", Path("/nonexistent/release.json")
        )
        self.assertEqual(status, 0, message)

    def test_refusal_2_field_set_must_be_exact(self) -> None:
        for label, payload in (
            ("extra key", {"notes": "x"}),
            ("missing key", {"updated_at": ...}),
        ):
            with self.subTest(label):
                status, message = node_release_metadata(
                    "public_docs", self.write(**payload)
                )
                self.assertNotEqual(status, 0)
                self.assertIn("exactly four fields", message)

    def test_refusal_3_every_value_is_a_string(self) -> None:
        status, message = node_release_metadata("public_docs", self.write(updated_at=20260822))
        self.assertNotEqual(status, 0)
        self.assertIn("must be a string", message)

    def test_refusal_4_availability_matches_the_mode(self) -> None:
        status, message = node_release_metadata(
            "public_docs", self.write(availability="released")
        )
        self.assertNotEqual(status, 0)
        self.assertIn("invalid availability value", message)
        status, message = node_release_metadata(
            "production", self.write(availability="documentation_preview")
        )
        self.assertNotEqual(status, 0)
        self.assertIn("invalid availability value", message)

    def test_refusal_5_release_version_is_immutable(self) -> None:
        for placeholder in ("", "unreleased", "latest"):
            with self.subTest(placeholder):
                status, message = node_release_metadata(
                    "public_docs", self.write(release_version=placeholder)
                )
                self.assertNotEqual(status, 0)
                self.assertIn("immutable release version", message)

    def test_refusal_6_digest_and_date_shapes(self) -> None:
        status, message = node_release_metadata(
            "public_docs", self.write(public_contract_sha256="A" * 64)
        )
        self.assertNotEqual(status, 0)
        self.assertIn("64-hex public contract digest", message)
        status, message = node_release_metadata(
            "public_docs", self.write(updated_at="22 August 2026")
        )
        self.assertNotEqual(status, 0)
        self.assertIn("updated_at must be YYYY-MM-DD", message)


class BuiltArtifactTest(unittest.TestCase):
    def test_staging_build_passes_the_full_verifier(self) -> None:
        # Built OUTSIDE the repository on purpose. A staging tree left behind by
        # an interrupted run is an untracked directory full of HTML sitting next
        # to the one directory in this repository that is served to the public,
        # and `.gitignore` should not have to be the only thing standing between
        # them. The source scan is pointed back at the repository explicitly.
        staging = Path(tempfile.mkdtemp(prefix="kaleidoscope-docs-staging-"))
        self.addCleanup(lambda: shutil.rmtree(staging, ignore_errors=True))
        built = subprocess.run(
            ["npx", "astro", "build", "--outDir", str(staging)],
            cwd=ROOT,
            env={**os.environ, "DOCS_MODE": "staging"},
            capture_output=True,
            text=True,
        )
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        manifest = make_manifest(staging, "staging")
        self.assertEqual(manifest.returncode, 0, manifest.stdout + manifest.stderr)
        self.assertEqual(verify_site.verify(staging, "staging", source_root=ROOT), [])

    def test_checked_in_artifact_matches_a_fresh_build(self) -> None:
        # Gate (d): what deploys is what was reviewed.
        checked_in = ROOT / "docs"
        self.assertTrue(
            (checked_in / "site-manifest.json").is_file(),
            "docs/ carries no manifest; run npm run build && npm run promote",
        )
        self.assertEqual(verify_site.verify(checked_in, "public_docs", source_root=ROOT), [])
        dist = ensure_dist()
        self.assertEqual(
            json.loads((checked_in / "site-manifest.json").read_text(encoding="utf-8")),
            json.loads((dist / "site-manifest.json").read_text(encoding="utf-8")),
            "the committed artifact is not a fresh build of the reviewed source",
        )

    def test_the_promotion_script_refuses_an_incomplete_build(self) -> None:
        # A promotion that loses the CNAME takes the domain down; one that
        # loses .nojekyll makes Pages strip every stylesheet and script.
        script = (ROOT / "scripts" / "promote.sh").read_text(encoding="utf-8")
        for guard in ("dist/CNAME", "dist/.nojekyll", "dist/site-manifest.json"):
            self.assertIn(guard, script, f"promote.sh does not assert {guard}")
        self.assertIn("verify_site.py", script)


class SourceContractTest(unittest.TestCase):
    """Facts that live in the source tree and must not drift."""

    def data(self, name: str) -> Path:
        path = ROOT / "src" / "data" / name
        self.assertTrue(path.is_file(), f"missing republished source {path}")
        return path

    def test_public_skill_and_tool_contract_are_exact(self) -> None:
        skill = self.data("public/SKILL.md")
        self.assertEqual(
            hashlib.sha256(skill.read_bytes()).hexdigest(),
            verify_site.PUBLIC_SKILL_SHA256,
        )
        mcp = json.loads(self.data("mcp-reference.json").read_text(encoding="utf-8"))
        self.assertEqual({tool["name"] for tool in mcp["model_tools"]}, {"search", "remember"})
        self.assertFalse(mcp["operator_commands_are_model_tools"])
        status = json.loads(self.data("status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["hosts"]["tools_a_model_sees"], ["remember", "search"])

    def test_every_host_row_says_which_part(self) -> None:
        # The five status words are deleted from the MACHINE RECORD too, not
        # just from prose. status.json is linked from /status/ as "the same
        # facts, in machine-readable form" and llms-full.txt inlines it, so a
        # `"status": "partly tested"` key was reader-reachable copy wearing a
        # schema's clothes — and it carried nothing the two prose fields beside
        # it did not already say. What the grade was introduced to guarantee is
        # now asserted on every row directly, which is strictly stronger: it
        # used to bind only the rows that happened to be labelled.
        status = json.loads(self.data("status.json").read_text(encoding="utf-8"))
        rows = status["hosts"]["hosts"]
        self.assertTrue(rows)
        for host in rows:
            self.assertNotIn(
                "status",
                host,
                f"{host['name']} carries a status grade; the five words are deleted",
            )
            for side in ("confirmed", "not confirmed"):
                self.assertTrue(
                    str(host.get(side, "")).strip(),
                    f"{host['name']} has an empty {side!r}",
                )
        self.assertNotIn(
            "not tested at all",
            status["hosts"],
            "nothing was tested there because nothing was run there",
        )

    def test_the_benchmark_key_was_renamed_not_deleted(self) -> None:
        # /docs/benchmarks/ publishes results in plain words, so
        # "benchmark score published: false" became a claim the site
        # contradicts. What is still true is that the method is not out.
        status = json.loads(self.data("status.json").read_text(encoding="utf-8"))
        holds = status["still true before any release"]
        self.assertNotIn("benchmark score published", holds)
        self.assertIs(holds["full benchmark method published"], False)
        for value in holds.values():
            self.assertFalse(value)

    def test_the_compiler_check_is_never_described_as_a_build(self) -> None:
        # Published once as "the code builds for this target", four platforms
        # nothing has ever been built for read as working builds.
        platforms = json.loads(
            self.data("platform-support.json").read_text(encoding="utf-8")
        )
        meaning = platforms["compiler checked only"]["meaning"]
        for phrase in (
            "The compiler accepts",
            "Nothing was ever assembled",
            "nothing has been run there",
        ):
            self.assertIn(phrase, meaning)
        platform_pages = [
            ROOT / "src/content/docs/docs/compatibility.mdx",
            ROOT / "src/content/docs/status.mdx",
        ]
        for page in platform_pages:
            self.assertTrue(page.is_file(), f"missing {page}")
            text = page.read_text(encoding="utf-8")
            for forbidden in ("builds for", "Builds only"):
                self.assertNotIn(
                    forbidden,
                    text,
                    f"{page.name} calls a compiler check a build",
                )

    def test_public_machine_records_have_no_private_coordinates(self) -> None:
        # The three records this site AUTHORS are held to everything.
        authored = "\n".join(
            [
                self.data("mcp-reference.json").read_text(encoding="utf-8"),
                self.data("status.json").read_text(encoding="utf-8"),
                self.data("platform-support.json").read_text(encoding="utf-8"),
            ]
        )
        for marker in verify_site.PRIVATE_MARKERS:
            self.assertNotIn(marker, authored)
        for pattern in verify_site.BANNED_VOCABULARY:
            self.assertIsNone(
                re.search(pattern, authored.lower()),
                f"internal vocabulary matching {pattern} in a public machine record",
            )

        # The CLI help is REPUBLISHED, not authored: it is `kscope --help`,
        # captured verbatim from the executable the npm package installs. It is
        # held to the path markers, which no published artifact may ever carry,
        # and not to the house vocabulary or to the four environment names the
        # shipped binary prints itself. Editing it to satisfy either would make
        # it a paraphrase, and a paraphrase is the thing this file exists to
        # stop being published.
        republished = self.data("kaleidoscope-cli.txt").read_text(encoding="utf-8")
        for marker in verify_site.PRIVATE_MARKERS:
            self.assertNotIn(
                marker,
                republished,
                f"{marker} in a republished artifact: no exemption reaches a path",
            )
        status = json.loads(self.data("status.json").read_text(encoding="utf-8"))
        # These three flipped when 0.0.5 published. The assertion is kept, not
        # deleted: the record must still state each one, and a machine reading
        # it must not have to infer availability from the absence of a field.
        self.assertTrue(status["released"])
        self.assertTrue(status["publicly available"])
        self.assertTrue(status["packages"]["published to a registry"])
        # Still false, and the one that matters most to a reader deciding
        # whether to install: nothing is signed.
        self.assertFalse(status["packages"]["signed for release"])
        self.assertIn("not yet in force", status["licences"]["the product terms"])


class RouteInventoryTest(unittest.TestCase):
    def test_every_expected_route_is_named_in_the_navigation(self) -> None:
        config = (ROOT / "astro.config.mjs").read_text(encoding="utf-8")
        missing = []
        for relative in sorted(verify_site.EXPECTED_HTML):
            if relative in {"404.html", "index.html"}:
                continue
            slug = relative.removesuffix("/index.html")
            if slug not in config and f"/{slug}/" not in config:
                missing.append(slug)
        self.assertEqual(
            missing,
            [],
            "these routes are expected by the verifier but named nowhere in the "
            "sidebar or navigation; a route the sidebar does not name is a page "
            "nobody can reach",
        )

    def test_the_redirect_stubs_exist_and_point_at_live_routes(self) -> None:
        for relative, target in sorted(verify_site.REDIRECT_HTML.items()):
            stub = ROOT / "public" / relative
            self.assertTrue(stub.is_file(), f"missing redirect stub public/{relative}")
            body = stub.read_text(encoding="utf-8")
            self.assertIn("noindex,nofollow", body)
            self.assertIn(f'href="{target}"', body)
            landing = target.strip("/")
            landing_route = f"{landing}/index.html" if landing else "index.html"
            self.assertIn(
                landing_route,
                verify_site.EXPECTED_HTML,
                f"public/{relative} redirects to {target}, which is not a route",
            )

    def test_the_dropped_hosted_page_is_a_stub_and_not_a_page(self) -> None:
        self.assertNotIn("docs/hosted/index.html", verify_site.EXPECTED_HTML)
        self.assertIn("docs/hosted/index.html", verify_site.REDIRECT_HTML)
        for candidate in ("hosted.mdx", "hosted.md", "hosted/index.mdx"):
            self.assertFalse(
                (ROOT / "src/content/docs/docs" / candidate).exists(),
                f"/docs/hosted/ is both a page and a redirect stub ({candidate})",
            )


if __name__ == "__main__":
    unittest.main()
