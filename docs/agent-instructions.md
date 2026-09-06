# Kaleidoscope agent instructions

These are the files that tell your agent Kaleidoscope is there, and the command
that installs them. All of it ships today: `npm install -g
@kleos-research/kaleidoscope` gives you the `kscope` command, and a key, which
we send by email, is what lets it run. The same material is explained in full at
https://memory.kleosresearch.xyz/docs/skill/

One command does the whole of it:

```bash
cd ~/your-project
kscope init
```

`kscope init` creates the vault, then looks for the configuration directory each
agent writes in your home directory and treats its existence as evidence that
you run that agent. For every one it finds it registers the memory server,
writes the instruction file and installs the skill, printing a line for each
step as it takes it. When it finds none it writes `AGENTS.md` alone and says so,
because `AGENTS.md` is the one file every agent reads.

Where each file lands depends on the agent, because a skill written to the wrong
directory is a file that is silently never loaded:

- Claude Code reads the skill at `.claude/skills/use-kaleidoscope/SKILL.md` and
  the pointer in `CLAUDE.md`.
- Codex and OpenCode read the skill at
  `.agents/skills/use-kaleidoscope/SKILL.md` and the pointer in `AGENTS.md`.
- Cursor gets `.cursor/rules/kaleidoscope.mdc` and no skill file at all, because
  it has no skill directory to read one from. Asking for one there is refused
  rather than written somewhere it would not be read.

The pointer is added as a marked block, delimited by a comment pair, so what
Kaleidoscope wrote can always be told apart from what you wrote. Nothing else in
your file is touched, running it twice adds nothing a second time, and a file
that was edited inside the markers is refused rather than overwritten. The skill
file carries no marker — a comment injected into its frontmatter is a file a
strict reader can reject — so what records ownership beside it is a receipt,
`.kaleidoscope-instruction-owner.json`.

`kscope init --no-wire` creates the vault and leaves every file of yours alone.
The flag works and is absent from the binary's own `--help`, which is worth
knowing before you go looking for it there.

The files it installs are published here, byte for byte:

- [SKILL.md](/SKILL.md)
- [AGENTS.md snippet](/snippets/AGENTS.md)
- [CLAUDE.md snippet](/snippets/CLAUDE.md)
- [Cursor rule](/snippets/cursor-kaleidoscope.mdc)

Pasting them by hand works, and is what to do for an agent this build has never
heard of. What ships has no command for removing them again: taking the text
back out is done by hand, by deleting the marked block including both of its
comments, or the skill file and the receipt beside it.

Installing and removing one file at a time, with a dry run first, belongs to
`kaleidoscope`, a second executable built only from the product source and
published on no channel. You cannot obtain it, so you cannot run the lines
below; they are written down because that finer-grained half of the mechanism is
real, not because there is a way to reach it today.

```bash
kaleidoscope instructions install skill --host claude-code --project "$PWD"
kaleidoscope instructions install agents --project "$PWD" --dry-run
kaleidoscope instructions install agents --project "$PWD"
kaleidoscope instructions install claude --project "$PWD"
kaleidoscope instructions install cursor --project "$PWD"

kaleidoscope instructions remove cursor --project "$PWD" --dry-run
kaleidoscope instructions remove cursor --project "$PWD"
```

`install skill` requires `--host`, because the skill directory differs per agent
and there is no sensible default to pick; the other three targets take no such
flag.

The skill tells an agent how to use `search` and `remember`, and nothing else.
It does not offer an agent any account, maintenance or diagnostic command as a
tool, because a model never sees one.
