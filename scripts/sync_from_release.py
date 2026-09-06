#!/usr/bin/env python3
"""Bring this site into agreement with one engine release, and prove it stays there.

The engine repository is private and this one is public, and truth flows one
way between them: the engine's release job generates a directory of release
assets, runs this script in `--apply` mode against it, and opens a pull request
carrying whatever changed. Nobody retypes a version, a date or a digest. Then
this repository's CI runs the same script in `--check` mode, offline, with no
token and no network, and recomputes every derived file from the two things
that were committed -- the pin and the vendored assets -- failing on any file
that disagrees. So the private repository is the only writer of the pin, and
the public repository verifies its own internal consistency on every push.

    python3 scripts/sync_from_release.py --apply --release <release-assets dir>
    python3 scripts/sync_from_release.py --check

What `--apply` reads is `release.json`, schema `kaleidoscope.release-manifest.v1`,
and every file it names. Every digest in the manifest is re-hashed before a
byte is written, and one mismatch refuses the whole run: a manifest that
disagrees with its own assets is not a release, it is two things claiming to
be one.

What both modes agree on is the DERIVED set, and it is written out once here
so that the two modes cannot drift from each other:

  release-pin.json                     the pin: what the manifest said, minus the
                                       files themselves. Lives at the root, beside
                                       public-docs-release.json, and OUTSIDE the
                                       source roots verify_site.py scans -- it
                                       carries a commit hash and digests, which
                                       gate (b) rightly refuses in anything a
                                       reader can see.
  public-docs-release.json             the four fields the build refuses without.
                                       scripts/release-metadata.mjs rejects a fifth
                                       field, which is why the pin is a separate
                                       file rather than four more keys here.
  src/data/kaleidoscope-cli.txt        `kscope --help`, byte for byte.
  src/data/public/SKILL.md             the skill `kscope init` installs, byte for byte.
  src/data/public/snippets/*           the three blocks `kscope init` writes.
  src/data/status.json                 the version, the npm package names, the
                                       platforms a package is published for, and
                                       the date. Everything else in it is authored
                                       here and left exactly as it is.
  src/data/platform-support.json       'built and published', from the platform
                                       rows. 'run on' and the compiler-checked
                                       block are testing evidence this repository
                                       authors; the manifest does not carry them
                                       and they are left exactly as they are.
  src/data/kscope-surface.json         the verbs, parsed from the help text. The
                                       shape and the not_yet_shipped section are
                                       kept; measured_on and measured_against come
                                       from the manifest, never from the clock.
  scripts/make_manifest.py             the recorded upstream digests of the five
  verify_site.py                       republished files, and the pinned skill
                                       digest. Both files write those digests down
                                       deliberately rather than reading them from
                                       somewhere, and the deliberate record has to
                                       move with the release or the next build
                                       refuses on a drift that is not one.

Two rules this script holds itself to, because the verifier will fail the
build if it does not. Nothing it writes under src/ may carry a private marker
or a word from BANNED_VOCABULARY -- every rendered file is run through
verify_site's own scanners before anything touches the disk. And nothing here
reads a clock: a date on this site is a fact about a release, and a generated
file with the same inputs is byte-identical every time.
"""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import verify_site  # noqa: E402

MANIFEST = "release.json"
MANIFEST_SCHEMA = "kaleidoscope.release-manifest.v1"
PIN = "release-pin.json"
PIN_SCHEMA = "kaleidoscope.docs-release-pin.v1"
RELEASE_RECORD = "public-docs-release.json"
STATUS = "src/data/status.json"
PLATFORM_SUPPORT = "src/data/platform-support.json"
KSCOPE_SURFACE = "src/data/kscope-surface.json"
CLI_HELP = "src/data/kaleidoscope-cli.txt"
MAKE_MANIFEST = "scripts/make_manifest.py"
VERIFY_SITE = "verify_site.py"

# Manifest asset -> where its bytes live in this repository. The manifest keys
# `instruction_assets` by role and `cli_help` on its own; both land in the pin
# under one map keyed by repository path, which is the coordinate `--check`
# needs and the one a person reading the pin recognises.
INSTRUCTION_ASSETS = {
    "skill": "src/data/public/SKILL.md",
    "agents": "src/data/public/snippets/AGENTS.md",
    "claude": "src/data/public/snippets/CLAUDE.md",
    "cursor": "src/data/public/snippets/cursor-kaleidoscope.mdc",
}

# Where each entry's file must be inside the release directory. The engine's
# manifest schema pins these paths as constants, and this script holds the
# manifest to the same constants rather than reading `path` as an address:
# an address can point outside the directory, and two roles' addresses can be
# swapped so that every digest still re-hashes while the skill lands where the
# snippet should be. Neither is a release; both are refused by name.
ASSET_PATHS = {
    "public_contract": "kaleidoscope-public-contract.json",
    "cli_help": "kscope-help.txt",
    "instruction_assets.skill": "instructions/SKILL.md",
    "instruction_assets.agents": "instructions/AGENTS.md",
    "instruction_assets.claude": "instructions/CLAUDE.md",
    "instruction_assets.cursor": "instructions/cursor-kaleidoscope.mdc",
}

PLATFORM_ROW_KEYS = (
    "slug",
    "os",
    "architecture",
    "triple",
    "built",
    "published",
    "native_build_runner",
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION = re.compile(r"^" + verify_site.VERSION_SHAPED + r"$")


class Refusal(SystemExit):
    """A refusal is an exit status of 1 carrying the reasons, one per line."""

    def __init__(self, reasons: list[str]) -> None:
        super().__init__(1)
        self.reasons = reasons


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump_sorted(data: dict) -> str:
    """The house serialisation for records this repository authors.

    `ensure_ascii=False` because status.json carries no escapes and a sync that
    rewrote its punctuation as `\\u2019` would turn every line into a diff.
    """
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def dump_in_order(data: dict) -> str:
    """kscope-surface.json is written in reading order, so it is kept in it."""
    return json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def load_json(path: Path, reasons: list[str]) -> dict | None:
    # Named relative to the repository where it can be, so that a refusal
    # reads as the file a person has to open and never as a coordinate on the
    # machine that happened to run it.
    name = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.name
    if not path.is_file():
        reasons.append(f"{name}: missing")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        reasons.append(f"{name}: not valid JSON ({error.msg} at line {error.lineno})")
        return None
    if not isinstance(data, dict):
        reasons.append(f"{name}: not a JSON object")
        return None
    return data


# ------------------------------------------------------------------ the manifest


def platform_row_problems(rows: object, where: str) -> list[str]:
    """Every way the platform rows can fail to be the table the engine writes.

    Shared by the manifest reader and the pin reader, because the derived
    files are rendered from these rows by truth value: a `"published": "no"` that
    slipped through would put a platform under "built and published" on the strength of a
    non-empty string, and a slug listed twice would print a platform twice.
    """
    reasons: list[str] = []
    if not isinstance(rows, list):
        return [f"{where}: platforms is not a list"]
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            reasons.append(f"{where}: a platform row is not an object")
            continue
        missing = [key for key in PLATFORM_ROW_KEYS if key not in row]
        if missing:
            reasons.append(f"{where}: platform row {row.get('slug')!r} is missing {', '.join(missing)}")
            continue
        slug = row["slug"]
        if not isinstance(slug, str) or not slug:
            reasons.append(f"{where}: a platform row has no slug")
            continue
        if slug in seen:
            reasons.append(f"{where}: platform {slug!r} is listed twice")
        seen.add(slug)
        for key in ("os", "architecture", "triple"):
            if not isinstance(row[key], str) or not row[key]:
                reasons.append(f"{where}: platform {slug!r} {key} is not a non-empty string")
        for key in ("built", "published", "native_build_runner"):
            # `row.get`, not `row[key]`: a pin written by an older version of
            # this script is missing a key rather than carrying a wrong one, and
            # a KeyError traceback tells the reader nothing about which file to
            # regenerate. Every shape problem here leaves by the same door.
            if not isinstance(row.get(key), bool):
                reasons.append(f"{where}: platform {slug!r} {key} is {row[key]!r}, not true or false")
        if all(isinstance(row.get(key), bool) for key in ("built", "published", "native_build_runner")):
            if row["published"] and not row["built"]:
                reasons.append(f"{where}: platform {slug!r} is published but not built")
            if row["native_build_runner"] and not row["built"]:
                reasons.append(
                    f"{where}: platform {slug!r} has a native build runner but was not built"
                )
    return reasons


def channel_problems(channels: object, platforms: list[dict], executables: object, where: str) -> list[str]:
    """The npm channel and the executables map, reconciled with the platform rows.

    The engine derives all three from one table, so here they must agree with
    each other: the packages named are exactly the platforms published, the
    executables digested are exactly the platforms built, and each package is
    the entry package's name with the slug appended. A manifest naming a
    package for a platform its own rows say was not built would otherwise be
    advertised on the status page as installable.
    """
    reasons: list[str] = []
    npm = channels.get("npm") if isinstance(channels, dict) else None
    if not isinstance(npm, dict):
        return [f"{where}: channels.npm is missing"]
    entry = npm.get("entry_package")
    packages = npm.get("platform_packages")
    if not isinstance(entry, str) or not entry:
        reasons.append(f"{where}: channels.npm.entry_package is not a package name")
    if not isinstance(packages, dict):
        reasons.append(f"{where}: channels.npm.platform_packages is not an object")
    if not isinstance(executables, dict):
        reasons.append(f"{where}: executables is not an object")
    if reasons:
        return reasons
    for slug, entry_ in executables.items():
        if not isinstance(entry_, dict) or not HEX64.match(str(entry_.get("sha256"))):
            reasons.append(f"{where}: executables.{slug} must carry a 64-hex sha256")
        if not isinstance(entry_, dict) or not isinstance(entry_.get("bytes"), int) or entry_["bytes"] <= 0:
            reasons.append(f"{where}: executables.{slug} must carry a positive byte count")
    built = {row["slug"] for row in platforms if row["built"]}
    published = {row["slug"] for row in platforms if row["published"]}
    if set(executables) != built:
        reasons.append(
            f"{where}: executables names {sorted(executables)} and the platform rows say "
            f"{sorted(built)} were built; the two must be the same set"
        )
    if set(packages) != published:
        reasons.append(
            f"{where}: channels.npm.platform_packages names {sorted(packages)} and the platform "
            f"rows say {sorted(published)} were published; the two must be the same set"
        )
    for slug, name in sorted(packages.items()):
        if name != f"{entry}-{slug}":
            reasons.append(f"{where}: platform package for {slug!r} is {name!r}, not {entry}-{slug}")
    return reasons


def read_manifest(release_dir: Path) -> dict:
    """Read release.json and re-hash everything it names. Refuse on any doubt."""
    reasons: list[str] = []
    manifest = load_json(release_dir / MANIFEST, reasons)
    if manifest is None:
        raise Refusal(reasons)
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        reasons.append(
            f"{MANIFEST}: schema_version is {manifest.get('schema_version')!r}, "
            f"this script reads {MANIFEST_SCHEMA!r}"
        )
    for key in (
        "release_version",
        "source_commit",
        "released_on",
        "availability",
        "channels",
        "platforms",
        "executables",
        "public_contract",
        "cli_help",
        "instruction_assets",
    ):
        if key not in manifest:
            reasons.append(f"{MANIFEST}: missing {key!r}")
    if reasons:
        raise Refusal(reasons)
    # The shape of every container before anything reads into it, so that a
    # manifest with a list where an object should be is refused by name and
    # not by a traceback from the first subscript.
    for key in ("channels", "public_contract", "cli_help", "instruction_assets", "executables"):
        if not isinstance(manifest[key], dict):
            reasons.append(f"{MANIFEST}: {key} is not an object")
    reasons.extend(platform_row_problems(manifest["platforms"], MANIFEST))
    if reasons:
        raise Refusal(reasons)

    if not VERSION.match(str(manifest["release_version"])):
        reasons.append(f"{MANIFEST}: release_version {manifest['release_version']!r} is not a version")
    if not HEX40.match(str(manifest["source_commit"])):
        reasons.append(f"{MANIFEST}: source_commit is not a 40-character lowercase hex commit")
    if not ISO_DATE.match(str(manifest["released_on"])):
        reasons.append(f"{MANIFEST}: released_on {manifest['released_on']!r} is not YYYY-MM-DD")
    else:
        # The shape and the calendar are two checks. `2026-13-45` has the
        # shape, and the build that reads it as a date refuses far from here.
        try:
            date.fromisoformat(manifest["released_on"])
        except ValueError:
            reasons.append(f"{MANIFEST}: released_on {manifest['released_on']!r} is not a calendar date")
    if manifest["availability"] != verify_site.AVAILABLE_AVAILABILITY:
        # The site's gates read `available_with_key` as the one value under
        # which the pages may say the product can be had. A manifest saying
        # anything else is describing a release this site has no copy for yet.
        reasons.append(
            f"{MANIFEST}: availability is {manifest['availability']!r}; the only "
            f"value this site publishes is {verify_site.AVAILABLE_AVAILABILITY!r}"
        )
    reasons.extend(channel_problems(manifest["channels"], manifest["platforms"], manifest["executables"], MANIFEST))
    if reasons:
        raise Refusal(reasons)

    # Every digest, re-hashed, at the path the release contract fixes for it.
    # The files named are the ones this script copies, so a mismatch here is
    # the mismatch that would otherwise be published under a page saying the
    # bytes are the shipped ones.
    def check(label: str, entry: object) -> None:
        if not isinstance(entry, dict):
            reasons.append(f"{MANIFEST}: {label} is not an object")
            return
        relative = entry.get("path")
        digest = entry.get("sha256")
        if relative != ASSET_PATHS[label]:
            reasons.append(f"{MANIFEST}: {label} names {relative!r}; the release contract fixes it at {ASSET_PATHS[label]!r}")
            return
        if not HEX64.match(str(digest)):
            reasons.append(f"{MANIFEST}: {label} must carry a 64-hex sha256")
            return
        path = release_dir / relative
        if path.is_symlink() or not path.resolve().is_relative_to(release_dir.resolve()):
            # A release asset is a file inside the directory. A link out of it
            # would hash, and then vendor, something the release never shipped.
            reasons.append(f"{MANIFEST}: {label} at {relative} is not a file inside the release assets")
            return
        if not path.is_file():
            reasons.append(f"{MANIFEST}: {label} names {relative}, which is not in the release assets")
            return
        actual = sha256_of(path)
        if actual != digest:
            reasons.append(
                f"{MANIFEST}: {label} says {relative} hashes to {digest}, "
                f"the file hashes to {actual}"
            )

    check("public_contract", manifest["public_contract"])
    check("cli_help", manifest["cli_help"])
    for role in INSTRUCTION_ASSETS:
        check(f"instruction_assets.{role}", manifest["instruction_assets"].get(role))
    if reasons:
        raise Refusal(reasons)

    contract_path = release_dir / ASSET_PATHS["public_contract"]
    contract = load_json(contract_path, reasons)
    if contract is not None:
        expected_schema = manifest["public_contract"].get("schema_version")
        if contract.get("schema_version") != expected_schema:
            reasons.append(
                f"{MANIFEST}: public_contract.schema_version is {expected_schema!r} but the "
                f"contract file says {contract.get('schema_version')!r}"
            )
        revision = manifest["public_contract"].get("mcp_protocol_revision")
        protocol = contract.get("mcp", {}).get("protocol") if isinstance(contract.get("mcp"), dict) else None
        carried = protocol.get("maximum") if isinstance(protocol, dict) else None
        if carried != revision:
            reasons.append(
                f"{MANIFEST}: public_contract.mcp_protocol_revision is {revision!r} but the "
                f"contract's mcp.protocol.maximum is {carried!r}"
            )
        # The contract says which version of the product it observed; the
        # manifest says which version the release is. One release, one number.
        product = contract.get("product")
        stated = product.get("version") if isinstance(product, dict) else None
        if stated != manifest["release_version"]:
            reasons.append(
                f"{MANIFEST}: release_version is {manifest['release_version']!r} but the contract's "
                f"product.version is {stated!r}; the contract describes a different release"
            )
    if reasons:
        raise Refusal(reasons)
    return manifest


def pin_from_manifest(manifest: dict) -> dict:
    """What this repository keeps of the manifest once the assets are vendored."""
    vendored = {CLI_HELP: manifest["cli_help"]["sha256"]}
    for role, relative in INSTRUCTION_ASSETS.items():
        vendored[relative] = manifest["instruction_assets"][role]["sha256"]
    return {
        "schema_version": PIN_SCHEMA,
        "what_this_is": (
            "The one engine release this site describes, as its release job stated "
            "it. Written only by scripts/sync_from_release.py --apply, from the "
            "release manifest; every derived file under src/data and the release "
            "record beside this file are recomputed from it by --check on every "
            "push. Edit the engine, not this file."
        ),
        "release_version": manifest["release_version"],
        "source_commit": manifest["source_commit"],
        "released_on": manifest["released_on"],
        "availability": manifest["availability"],
        "channels": manifest["channels"],
        "platforms": manifest["platforms"],
        "executables": manifest["executables"],
        "public_contract": {
            "sha256": manifest["public_contract"]["sha256"],
            "schema_version": manifest["public_contract"]["schema_version"],
            "mcp_protocol_revision": manifest["public_contract"]["mcp_protocol_revision"],
        },
        "vendored": vendored,
    }


def read_pin(reasons: list[str]) -> dict | None:
    pin = load_json(REPO / PIN, reasons)
    if pin is None:
        return None
    if pin.get("schema_version") != PIN_SCHEMA:
        reasons.append(f"{PIN}: schema_version is {pin.get('schema_version')!r}, expected {PIN_SCHEMA!r}")
        return None
    for key in (
        "release_version",
        "source_commit",
        "released_on",
        "availability",
        "channels",
        "platforms",
        "executables",
        "public_contract",
        "vendored",
    ):
        if key not in pin:
            reasons.append(f"{PIN}: missing {key!r}")
    if reasons:
        return None
    if not isinstance(pin["vendored"], dict) or not isinstance(pin["public_contract"], dict):
        reasons.append(f"{PIN}: vendored and public_contract must be objects")
        return None
    for relative in (CLI_HELP, *INSTRUCTION_ASSETS.values()):
        if not HEX64.match(str(pin["vendored"].get(relative))):
            reasons.append(f"{PIN}: vendored carries no 64-hex digest for {relative}")
    # The same table the manifest was held to, because the derived files are
    # rendered from the pin's rows and a pin is a file somebody could edit.
    reasons.extend(platform_row_problems(pin["platforms"], PIN))
    if not reasons:
        reasons.extend(channel_problems(pin["channels"], pin["platforms"], pin["executables"], PIN))
    if reasons:
        return None
    return pin


# ------------------------------------------------------------ the derived files


def platform_label(row: dict) -> str:
    """'macOS, Apple Silicon' -- the form status.json and platform-support.json use."""
    return f"{row['os']}, {row['architecture']}"


def render_release_record(pin: dict) -> str:
    return dump_sorted(
        {
            "availability": pin["availability"],
            "public_contract_sha256": pin["public_contract"]["sha256"],
            "release_version": pin["release_version"],
            "updated_at": pin["released_on"],
        }
    )


def render_status(existing: dict, pin: dict) -> str:
    status = json.loads(json.dumps(existing))
    npm = pin["channels"]["npm"]
    packages = status.setdefault("packages", {})
    packages["version"] = pin["release_version"]
    packages.setdefault("npm", {})
    packages["npm"]["client"] = npm["entry_package"]
    packages["npm"]["platform packages"] = [
        npm["platform_packages"][slug] for slug in sorted(npm["platform_packages"])
    ]
    packages["the platform package is built for"] = [
        platform_label(row) for row in pin["platforms"] if row["published"]
    ]
    status["as of"] = pin["released_on"]
    return dump_sorted(status)


def render_platform_support(existing: dict, pin: dict) -> str:
    support = json.loads(json.dumps(existing))
    built = support.setdefault("built and published", {})
    built["platforms"] = [
        {"architecture": row["architecture"], "platform": row["os"]}
        for row in pin["platforms"]
        if row["built"] and row["published"]
    ]
    # `run on` is NOT derived, and the omission is the point. The manifest's
    # `native_build_runner` says the release job builds that slug on its own
    # architecture instead of cross-compiling -- a fact about a build machine.
    # Deriving `run on` from it published "run on: macOS Apple Silicon, Linux
    # arm64, Linux x86_64" onto a page whose own prose says the product has been
    # run on one kind of machine. Whether anyone has run it somewhere is testing
    # evidence, this repository authors it, and a release manifest cannot know it.
    return dump_sorted(support)


def parse_help(text: str, subcommand_verbs: list[str], reasons: list[str]) -> dict:
    """Read the command surface off `kscope --help`.

    Verbs are every lowercase word that follows `kscope` at the start of an
    indented usage line; that is how the help lays out its surface, and a flag
    or a placeholder never starts with a lowercase letter. Subcommands are read
    the same way one token further along, but only for the verbs the surface
    already records as having them: `kscope schema remember` is a verb and an
    argument, not a verb and a subcommand, and the difference is not in the
    text. Call operations come from the block the help introduces with
    "OPERATION is one of:".
    """
    verbs: set[str] = set()
    subcommands: dict[str, set[str]] = {verb: set() for verb in subcommand_verbs}
    for line in text.splitlines():
        found = re.match(r"^\s+kscope\s+([a-z][a-z-]*)(?:\s+([a-z][a-z-]*))?", line)
        if not found:
            continue
        verb, second = found.group(1), found.group(2)
        verbs.add(verb)
        if verb in subcommands and second:
            subcommands[verb].add(second)
    if not verbs:
        reasons.append(f"{CLI_HELP}: no `kscope <verb>` usage lines found, so no surface can be read from it")
    for verb, found_subcommands in subcommands.items():
        if verb not in verbs:
            reasons.append(f"{CLI_HELP}: the surface records subcommands for {verb!r}, which the help does not list")
        elif not found_subcommands:
            reasons.append(f"{CLI_HELP}: the help lists no subcommand under `kscope {verb}`")

    operations: set[str] = set()
    block = re.search(r"OPERATION is one of:\n+((?:[^\n]+\n)+)", text)
    if block is None:
        reasons.append(f"{CLI_HELP}: the help no longer says 'OPERATION is one of:', so the call operations cannot be read")
    else:
        operations = set(re.findall(r"\b[a-z_]+\b", block.group(1)))
    return {
        "verbs": sorted(verbs),
        "subcommands": {verb: sorted(found) for verb, found in subcommands.items()},
        "call_operations": sorted(operations),
    }


def render_surface(existing: dict, pin: dict, help_text: str, reasons: list[str]) -> str:
    parsed = parse_help(help_text, list(existing.get("subcommands", {})), reasons)
    surface = json.loads(json.dumps(existing))
    surface["measured_on"] = pin["released_on"]
    surface["measured_against"] = (
        f"kscope {pin['release_version']}, installed from "
        f"{pin['channels']['npm']['entry_package']} on npm: the verbs, the profile "
        "subcommands and the call operations are read from its own help text, "
        "republished beside this file as kaleidoscope-cli.txt"
    )
    surface["verbs"] = parsed["verbs"]
    surface["subcommands"] = parsed["subcommands"]
    surface["call_operations"] = parsed["call_operations"]
    return dump_in_order(surface)


def render_make_manifest(text: str, pin: dict, reasons: list[str]) -> str:
    """Move the recorded upstream digests, and the help's package pin, with the release."""
    for relative, digest in sorted(pin["vendored"].items()):
        pattern = re.compile(
            r'("' + re.escape(relative) + r'":\s*\{.*?"sha256":\s*")([0-9a-f]{64})(")',
            flags=re.S,
        )
        text, count = pattern.subn(lambda m: m.group(1) + digest + m.group(3), text, count=1)
        if count != 1:
            reasons.append(
                f"{MAKE_MANIFEST}: PUBLIC_UPSTREAM_SOURCES has no sha256 entry for {relative}, "
                "so its recorded digest cannot follow the release"
            )
    entry = re.escape(pin["channels"]["npm"]["entry_package"])
    pattern = re.compile(r"(" + entry + r"@)(" + verify_site.VERSION_SHAPED + r")(: `kscope --help`)")
    text, count = pattern.subn(
        lambda m: m.group(1) + pin["release_version"] + m.group(3), text, count=1
    )
    if count != 1:
        reasons.append(
            f"{MAKE_MANIFEST}: the `kscope --help` upstream record names no package version to move"
        )
    return text


def render_verify_site(text: str, pin: dict, reasons: list[str]) -> str:
    pattern = re.compile(r'(PUBLIC_SKILL_SHA256 = \(\s*")([0-9a-f]{64})(")')
    text, count = pattern.subn(
        lambda m: m.group(1) + pin["vendored"][INSTRUCTION_ASSETS["skill"]] + m.group(3),
        text,
        count=1,
    )
    if count != 1:
        reasons.append(f"{VERIFY_SITE}: PUBLIC_SKILL_SHA256 is not where this script expects it")
    return text


def derived_files(pin: dict, tree: Path, help_text: str, reasons: list[str]) -> dict[str, str]:
    """Every file both modes agree on, rendered from the pin. Path -> expected text.

    The vendored files are not here: their expected content is the release's
    bytes, which `--apply` has and `--check` compares by digest.
    """
    rendered: dict[str, str] = {PIN: dump_sorted(pin), RELEASE_RECORD: render_release_record(pin)}
    status = load_json(tree / STATUS, reasons)
    support = load_json(tree / PLATFORM_SUPPORT, reasons)
    surface = load_json(tree / KSCOPE_SURFACE, reasons)
    if status is not None:
        rendered[STATUS] = render_status(status, pin)
    if support is not None:
        rendered[PLATFORM_SUPPORT] = render_platform_support(support, pin)
    if surface is not None:
        rendered[KSCOPE_SURFACE] = render_surface(surface, pin, help_text, reasons)
    for relative, render in ((MAKE_MANIFEST, render_make_manifest), (VERIFY_SITE, render_verify_site)):
        path = tree / relative
        if not path.is_file():
            reasons.append(f"{relative}: missing")
            continue
        rendered[relative] = render(path.read_text(encoding="utf-8"), pin, reasons)
    return rendered


def scan_rendered(relative: str, text: str, reasons: list[str]) -> None:
    """Hold what this script writes to the gates the build will hold it to.

    The scope is the verifier's own: everything under src/ for the path
    markers, the prose roots for the vocabulary. verify_site.py and
    make_manifest.py sit outside it -- the verifier could not scan a file that
    defines the marker list without refusing itself -- and what this script
    changes in them is a digest and a version, which no scan objects to.
    """
    failures: list[str] = []
    if not relative.startswith(verify_site.SOURCE_ROOTS):
        return
    verify_site.scan_private_markers(relative, text, failures)
    if relative.startswith(verify_site.SOURCE_PROSE_ROOTS) and relative not in verify_site.SOURCE_VOCABULARY_EXEMPT:
        verify_site.scan_vocabulary(relative, text, failures)
    reasons.extend(f"refusing to write {failure}" for failure in failures)


# ------------------------------------------------------------------- the modes


def apply(release_dir: Path) -> int:
    manifest = read_manifest(release_dir)
    pin = pin_from_manifest(manifest)
    reasons: list[str] = []

    # The release's bytes, keyed by where they land, read from the paths the
    # release contract fixes -- read_manifest has already held the manifest's
    # own `path` fields to those. Read now so that nothing is written until
    # everything has been read and scanned.
    incoming: dict[str, bytes] = {CLI_HELP: (release_dir / ASSET_PATHS["cli_help"]).read_bytes()}
    for role, relative in INSTRUCTION_ASSETS.items():
        incoming[relative] = (release_dir / ASSET_PATHS[f"instruction_assets.{role}"]).read_bytes()
    help_text = incoming[CLI_HELP].decode("utf-8")

    rendered = derived_files(pin, REPO, help_text, reasons)
    for relative, text in sorted(rendered.items()):
        scan_rendered(relative, text, reasons)
    for relative, content in sorted(incoming.items()):
        # Vendored verbatim, so held to the path markers and nothing else: the
        # engine's voice is the engine's, and a paraphrase is what a verbatim
        # copy exists to not be.
        failures: list[str] = []
        verify_site.scan_private_markers(relative, content.decode("utf-8", errors="replace"), failures)
        reasons.extend(f"refusing to write {failure}" for failure in failures)
    if reasons:
        raise Refusal(reasons)

    written: list[str] = []
    for relative, content in sorted(incoming.items()):
        path = REPO / relative
        if not path.is_file() or path.read_bytes() != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            written.append(relative)
    for relative, text in sorted(rendered.items()):
        path = REPO / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8", newline="\n")
            written.append(relative)
    if written:
        print(
            f"applied release {pin['release_version']} of {pin['released_on']}; "
            f"{len(written)} file(s) changed:\n  " + "\n  ".join(sorted(written))
        )
    else:
        print(f"applied release {pin['release_version']} of {pin['released_on']}; nothing changed")
    return 0


def check() -> int:
    reasons: list[str] = []
    pin = read_pin(reasons)
    if pin is None:
        raise Refusal(
            reasons
            + [
                f"{PIN} is the record every derived file is checked against; without it "
                "there is nothing to check them against, and a check with no reference passes everything"
            ]
        )
    disagreeing: list[str] = []
    for relative, digest in sorted(pin["vendored"].items()):
        path = REPO / relative
        if not path.is_file():
            disagreeing.append(f"{relative}: missing, and {PIN} says it hashes to {digest}")
        elif sha256_of(path) != digest:
            disagreeing.append(
                f"{relative}: hashes to {sha256_of(path)}, and {PIN} says the release shipped {digest}"
            )
    help_path = REPO / CLI_HELP
    help_text = help_path.read_text(encoding="utf-8") if help_path.is_file() else ""
    rendered = derived_files(pin, REPO, help_text, reasons)
    for relative, expected in sorted(rendered.items()):
        if relative == PIN:
            # The pin is the input. What is checked of it is its shape, above,
            # and that it round-trips: a hand edit that reordered or reformatted
            # it is a hand edit, and the pin is not for hands.
            actual = (REPO / relative).read_text(encoding="utf-8")
            if actual != expected:
                disagreeing.append(f"{relative}: is not the canonical rendering of itself; it has been edited by hand")
            continue
        path = REPO / relative
        if not path.is_file():
            disagreeing.append(f"{relative}: missing")
        elif path.read_text(encoding="utf-8") != expected:
            disagreeing.append(f"{relative}: does not match what {PIN} derives; run --apply against the release, or revert the edit")
    if reasons or disagreeing:
        raise Refusal(reasons + disagreeing)
    print(
        f"{PIN} agrees with every derived file: release {pin['release_version']} of "
        f"{pin['released_on']}, {len(pin['vendored'])} vendored assets, "
        f"{len(rendered) - 1} derived files"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync this site to an engine release (--apply), or prove it is in sync (--check)."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true", help="regenerate every derived file from a release-assets directory")
    mode.add_argument("--check", action="store_true", help="recompute every derived file from the committed pin, offline, and fail on any difference")
    parser.add_argument("--release", type=Path, default=None, help="the release-assets directory; required with --apply, refused with --check")
    args = parser.parse_args(argv)
    if args.check and args.release is not None:
        parser.error("--check takes no arguments: it reads the committed pin and nothing else")
    if args.apply and args.release is None:
        parser.error("--apply needs --release <release-assets dir>")
    try:
        if args.apply:
            release_dir = args.release.resolve()
            if not release_dir.is_dir():
                raise Refusal([f"{release_dir} is not a directory"])
            return apply(release_dir)
        return check()
    except Refusal as refusal:
        for reason in refusal.reasons:
            print(f"FAIL: {reason}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
