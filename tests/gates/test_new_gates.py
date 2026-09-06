"""Drive gates (i), (j) and (k) to a known positive, and to a known negative.

`plant_violations.py` mutates a copy of the whole tree and runs the verifier
end to end; that is the authority, and these are the fast half of the same
idea. Each gate is called directly with a scrap of authored text, so a failure
here names the rule that broke rather than the build that noticed.

Both halves matter and neither replaces the other. A gate is only known to work
when it has been seen to REFUSE something it should refuse and to ACCEPT
something it should accept — a verifier that refuses everything catches every
violation and is useless. Every gate below has at least one of each.

Standard library only, no build, no node.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import verify_site  # noqa: E402


def surface() -> dict:
    failures: list[str] = []
    loaded = verify_site.load_kscope_surface(ROOT, failures)
    assert loaded is not None, failures
    return loaded


class RecordedSurfaceTest(unittest.TestCase):
    """The data file the command gate reads is itself a claim about the binary."""

    def setUp(self) -> None:
        self.surface = surface()

    def test_the_shipped_executable_is_the_one_that_is_published(self) -> None:
        self.assertEqual(self.surface["executable"], "kscope")
        self.assertEqual(self.surface["not_yet_shipped"]["executable"], "kaleidoscope")

    def test_the_verbs_measured_on_the_published_binary_are_recorded(self) -> None:
        verbs = set(self.surface["verbs"])
        for shipped in (
            "activate",
            "call",
            "context",
            "gate",
            "init",
            "init-profile",
            "licences",
            "mcp",
            "model",
            "profile",
            "public-contract",
            "schema",
            "serve",
            "vault-verify",
            "where",
        ):
            self.assertIn(shipped, verbs)

    def test_the_verbs_of_the_other_binary_are_not_recorded_as_shipped(self) -> None:
        # Every one of these is real, and none of them is on kscope. They are
        # the reason this gate exists, so the data file is asserted about them
        # rather than left to be quietly widened one line at a time.
        verbs = set(self.surface["verbs"])
        for absent in ("connect", "disconnect", "config", "doctor", "instructions"):
            self.assertNotIn(absent, verbs)
        self.assertNotIn("use", set(self.surface["subcommands"]["profile"]))

    def test_only_search_and_remember_reach_a_model(self) -> None:
        self.assertEqual(sorted(self.surface["tools_a_model_sees"]), ["remember", "search"])

    def test_a_missing_surface_file_is_refused_rather_than_skipped(self) -> None:
        empty = Path(tempfile.mkdtemp(prefix="kdocs-surface-"))
        failures: list[str] = []
        self.assertIsNone(verify_site.load_kscope_surface(empty, failures))
        self.assertTrue(any(verify_site.KSCOPE_SURFACE in f for f in failures), failures)

    def test_a_surface_file_missing_a_key_is_refused(self) -> None:
        partial = Path(tempfile.mkdtemp(prefix="kdocs-surface-"))
        (partial / "src" / "data").mkdir(parents=True)
        (partial / verify_site.KSCOPE_SURFACE).write_text(
            json.dumps({"executable": "kscope", "verbs": ["init"]}), encoding="utf-8"
        )
        failures: list[str] = []
        self.assertIsNone(verify_site.load_kscope_surface(partial, failures))
        self.assertTrue(any("is missing" in f for f in failures), failures)


class CommandGateTest(unittest.TestCase):
    """Gate (i)."""

    def setUp(self) -> None:
        self.surface = surface()

    def scan(self, body: str) -> list[str]:
        failures: list[str] = []
        verify_site.scan_kscope_commands("page.mdx", body, self.surface, failures)
        return failures

    def fence(self, *lines: str, language: str = "sh", marker: str = "") -> str:
        head = f"{marker}\n" if marker else ""
        return f"Some prose.\n\n{head}```{language}\n" + "\n".join(lines) + "\n```\n"

    # ------------------------------------------------------------- positives
    def test_a_verb_the_binary_does_not_have_is_refused(self) -> None:
        failures = self.scan(self.fence("kscope doctor"))
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("verb 'doctor'", failures[0])
        self.assertIn("page.mdx:4", failures[0])

    def test_a_profile_subcommand_the_binary_does_not_have_is_refused(self) -> None:
        failures = self.scan(self.fence("kscope profile use work"))
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("no subcommand 'use'", failures[0])

    def test_a_call_operation_that_does_not_exist_is_refused(self) -> None:
        failures = self.scan(self.fence("kscope call --profile default compile"))
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("no operation 'compile'", failures[0])

    def test_an_unmarked_unobtainable_command_is_refused(self) -> None:
        failures = self.scan(self.fence('kaleidoscope connect claude --project "$PWD"'))
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("is not published on any channel", failures[0])
        self.assertIn(verify_site.NOT_YET_SHIPPED_MARKER, failures[0])

    def test_the_offending_file_line_and_verb_are_all_named(self) -> None:
        # A refusal that does not say where is a refusal somebody has to grep for.
        failures = self.scan("```sh\nkscope where\nkscope connect codex\n```\n")
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("page.mdx:3", failures[0])
        self.assertIn("'connect'", failures[0])

    def test_a_command_after_a_pipe_is_read_as_a_command(self) -> None:
        failures = self.scan(self.fence("echo '{}' | kscope call --profile default nope"))
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("no operation 'nope'", failures[0])

    # ------------------------------------------------------------- negatives
    def test_the_shipped_surface_is_accepted(self) -> None:
        self.assertEqual(
            self.scan(
                self.fence(
                    "kscope --version",
                    "kscope activate KEY",
                    "kscope init",
                    "kscope init --no-wire",
                    "kscope where --root-only",
                    "kscope profile list",
                    "kscope profile show default",
                    "kscope vault-verify /path/to/.kaleidoscope",
                    "kscope schema --list",
                    "echo '{\"mode\":\"inspect\"}' | kscope call --profile default doctor",
                )
            ),
            [],
        )

    def test_a_marked_block_may_carry_the_unobtainable_command(self) -> None:
        body = self.fence(
            'kaleidoscope connect claude --project "$PWD"',
            marker=verify_site.NOT_YET_SHIPPED_MARKER,
        )
        self.assertEqual(self.scan(body), [])

    def test_a_marker_a_paragraph_away_does_not_carry(self) -> None:
        # A marker that reaches past intervening prose is a marker on somebody
        # else's block, and it would be pasted around without being read.
        body = (
            f"{verify_site.NOT_YET_SHIPPED_MARKER}\n\nUnrelated sentence.\n\n"
            "```sh\nkaleidoscope connect claude\n```\n"
        )
        self.assertTrue(self.scan(body))

    def test_a_blank_line_between_marker_and_fence_is_allowed(self) -> None:
        body = (
            f"{verify_site.NOT_YET_SHIPPED_MARKER}\n\n"
            "```sh\nkaleidoscope connect claude\n```\n"
        )
        self.assertEqual(self.scan(body), [])

    def test_a_configuration_block_is_not_a_command_line(self) -> None:
        body = self.fence('{"command": "kscope", "args": ["connect"]}', language="json")
        self.assertEqual(self.scan(body), [])

    def test_prose_outside_a_fence_is_not_scanned(self) -> None:
        # /docs/cli/connect/ has to be able to say the word `kscope connect` in
        # a sentence in order to explain that it is not a command.
        self.assertEqual(self.scan("There is no `kscope connect` on the binary.\n"), [])

    def test_a_commented_line_inside_a_fence_is_not_a_command(self) -> None:
        self.assertEqual(self.scan(self.fence("# kscope connect codex")), [])


class AvailabilityGateTest(unittest.TestCase):
    """Gate (j)."""

    def scan(self, body: str, availability: str = "available_with_key") -> list[str]:
        failures: list[str] = []
        verify_site.scan_unavailability("page.mdx", body, availability, failures)
        return failures

    def test_every_recorded_phrasing_fires(self) -> None:
        for phrasing in verify_site.UNAVAILABILITY_PHRASINGS:
            with self.subTest(phrasing):
                failures = self.scan(f"It is true that {phrasing} today.")
                self.assertEqual(len(failures), 1, failures)
                self.assertIn("available_with_key", failures[0])

    def test_a_phrasing_wrapped_across_a_line_break_still_fires(self) -> None:
        self.assertTrue(self.scan("Kaleidoscope is not\nreleased yet."))

    def test_nothing_fires_while_the_record_says_the_product_is_not_available(self) -> None:
        # The gate is a disagreement check, not an opinion about what is true.
        self.assertEqual(
            self.scan("Kaleidoscope is not released.", availability="documentation_preview"),
            [],
        )

    def test_the_pypi_placeholder_saying_so_of_itself_is_left_alone(self) -> None:
        # kscope-memory's own summary is "Local memory for AI agents. Not yet
        # released." Firing on that would teach people to delete a true fact.
        self.assertEqual(
            self.scan(
                "kscope-memory on PyPI is a 0.0.0 placeholder whose summary says it "
                "is not yet released."
            ),
            [],
        )

    def test_the_unshipped_manager_may_be_described_as_unavailable(self) -> None:
        self.assertEqual(
            self.scan(
                "The kaleidoscope manager is built only inside the product "
                "repository and is published on no channel, so you cannot obtain it."
            ),
            [],
        )


class VersionGateTest(unittest.TestCase):
    """Gate (k)."""

    def scan(self, body: str, version: str = "0.0.5") -> tuple[bool, list[str]]:
        failures: list[str] = []
        stated = verify_site.scan_release_version("page.mdx", body, version, failures)
        return stated, failures

    def test_a_bare_version_counts_as_stating_it(self) -> None:
        stated, failures = self.scan("The current version is 0.0.5.")
        self.assertTrue(stated)
        self.assertEqual(failures, [])

    def test_a_pin_is_not_a_statement_of_the_release_version(self) -> None:
        # `npm install @kleos-research/kaleidoscope@0.0.5` is a command, and it
        # is checked for equality below rather than counted as a second home
        # for the fact.
        stated, failures = self.scan("Run npm i @kleos-research/kaleidoscope@0.0.5 to pin.")
        self.assertFalse(stated)
        self.assertEqual(failures, [])

    def test_a_stale_pin_is_refused_wherever_it_stands(self) -> None:
        stated, failures = self.scan("Pin @kleos-research/kaleidoscope@0.0.4 for now.")
        self.assertFalse(stated)
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("0.0.4", failures[0])

    def test_a_stale_measurement_note_is_refused(self) -> None:
        _, failures = self.scan("Checked against kscope 0.0.3 on a Tuesday.")
        self.assertEqual(len(failures), 1, failures)
        self.assertIn("0.0.3", failures[0])

    def test_another_projects_version_is_not_kaleidoscopes(self) -> None:
        stated, failures = self.scan(
            "kscope-memory on PyPI is a 0.0.0 placeholder, and the editor was 1.18.21."
        )
        self.assertFalse(stated)
        self.assertEqual(failures, [])

    def test_the_file_of_record_is_a_file_that_exists(self) -> None:
        # An exemption naming a path that moved keeps covering nothing; the same
        # is true of a file of record.
        self.assertTrue((ROOT / verify_site.RELEASE_VERSION_FILE_OF_RECORD).is_file())


if __name__ == "__main__":
    unittest.main()
