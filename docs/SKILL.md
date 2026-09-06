---
name: use-kaleidoscope
description: Kaleidoscope is the user's local memory for this project — the decisions, preferences, constraints and outcomes a new session would otherwise have to rediscover or ask about twice. Use this skill at the start of any nontrivial task; before you grep the codebase or ask the user how something works; whenever the user states a preference, makes a decision, sets a constraint, or corrects you; when a piece of work produces a result worth keeping; and whenever the user says remember, save, note, forget or "what did we decide". Use it too when a Kaleidoscope call is refused, or when you cannot find its tools — it says what to do instead of quietly working without memory.
---

# Use Kaleidoscope

Kaleidoscope remembers things about *this project* so you do not have to work
them out again: what was decided and why, what the user prefers, what has
already been tried and rejected, what a past piece of work actually produced.

Two things you can do. **Read it** with `search`. **Write to it** with
`remember`. That is the whole surface.

Everything is local. No network call, nothing leaves this machine.

## How to call it

**If you have a shell, use the CLI.** It is much the cheaper route — one
command costs a couple of dozen tokens, while the MCP tool definitions sit in
your context all session whether you use them or not.

```bash
# read
echo '{"query":"why we chose this database","top_k":5}' | kscope call --profile default search

# the write contract, whenever you need it
kscope schema remember
```

If your harness gives you `search` and `remember` as tools and you have no
shell, use those instead. Same engine, same vault, same answers. Your harness
may show them under a prefix — Claude Code prefixes every tool with its server
— so use whatever name your own tool list shows.

## Reading: search first, then go looking

**Before you grep, before you read your way around the codebase, and before you
ask the user how something works — search.**

That includes: why is this built this way, what did we decide about X, what does
the user prefer, what did we already try. The code tells you what *is*.
Kaleidoscope tells you what was *decided*, and why — which the code cannot.

Ask for what you actually need, in plain words:

```bash
echo '{"query":"retry and backoff policy for the payments client","top_k":5}' \
  | kscope call --profile default search
```

One search at the start of a task is usually enough. Search again if the goal
changes, if something you read contradicts it, or if what came back was clearly
stale.

Treat what you get back as good context, not as gospel. If a memory disagrees
with what the user is telling you right now, **the user wins** — and that
disagreement is itself worth writing down.

And the point of all this: **a question already answered here is one you must
not ask the user a second time.**

## Writing: save it when it happens

Call `remember` without being asked. The moments that matter:

- the user states a preference — *"always use X"*, *"never do Y"*
- a decision gets made or rejected
- the user sets a constraint — a budget, a deadline, a rule
- the user corrects something you did or said
- a piece of work produces a result worth keeping
- **you worked something out** — see below

"Remember this", "save this" and "note that" are obvious triggers, but do not
wait for them. And **do not save everything up for the end of the task** — write
when the decision lands, while you still know why it was made.

### Write what you had to dig for

Every trigger above is something the *user* did. This one is about you.

If you established something by reading code, running an experiment, or ruling
out a wrong answer — how a mechanism actually works, why the obvious fix does
not work, what a confusing result really meant — **write it down before you move
on.**

That research is the most expensive thing in the session and the easiest to
lose. The next agent starts with none of it and pays the same cost again: the
same files read, the same false leads followed, the same tokens spent reaching
the same conclusion. Half an hour of digging is worth one `remember` call.

Save the conclusion and what makes it true — the mechanism, the file that
decides it, the measurement — not the transcript of getting there. A finding
that reversed something you believed earlier is worth *more* than a
confirmation, not less: record what was wrong and what actually holds.

### Especially around subagents and workflows

**A subagent cannot see any of this.** Not this skill, not the block in
`CLAUDE.md`, not the vault. Its entire world is the prompt you write it. So the
instruction does not travel down that edge unless you carry it:

- put **"search Kaleidoscope before you start"** and **"record what you
  establish before you return"** into the prompt itself, next to whatever else
  that agent needs to know
- if you forgot, write the findings yourself the moment the agent returns —
  while you still have its report in front of you

A workflow is the worst place to skip this and the easiest place to skip it. It
is where the most research per token in a whole session happens: you fan out to
gather what you do not know, derive something from it, and decide what to do
next. By default none of that is kept. The parent receives a summary, the
reasoning is discarded with the transcript, and the next session starts from
nothing and pays to derive it again.

The asymmetry is what makes it worth a rule: **carrying the instruction costs
two lines in a prompt you were already writing. Not carrying it costs the whole
investigation.**

A write looks like this, and this exact payload works:

```json
{
  "mode": "create",
  "content_md": "# We chose Postgres over DynamoDB\n\nRelational queries across orders and users were the deciding factor; the team already runs Postgres in two other services.",
  "semantic_delta": {
    "memory_type": "decision",
    "title": "We chose Postgres over DynamoDB",
    "facts": [
      {"subject": "the orders service", "predicate": "stores_data_in", "object": "postgres"},
      {"subject": "the team", "predicate": "rejected", "object": "dynamodb"}
    ],
    "entities": [
      {"n": "the orders service", "kind": "artifact", "is": "the service that owns order records in this repository"},
      {"n": "postgres", "kind": "tool", "is": "the relational database chosen for primary storage"},
      {"n": "dynamodb", "kind": "tool", "is": "the key-value store considered and rejected"},
      {"n": "the team", "kind": "org", "is": "the engineers working on this repository"}
    ]
  }
}
```

Four things are worth knowing, because they are easy to get wrong:

- **Write the `title` yourself.** It is not taken from your markdown.
- **Every entity needs an `is`.** It is not a comment — it is how Kaleidoscope
  works out whether your "postgres" is the same thing as one written last month.
  A vague gloss makes a worse match.
- **Dates are not entities.** Put them in `occurred_at`, or a fact's
  `from`/`until`. Work out the actual date yourself; the store does not read
  "last Tuesday".
- **To change your mind, revise the memory** rather than writing a second one
  that contradicts the first. Use `mode: "update"`, or `corrections` and
  `contradicts`.

Got several things to record from one piece of work? Send them as separate
items in one call — one memory per idea, so each can be corrected later on its
own. Do not mash unrelated findings together to save a call.

`kscope schema remember` prints the full contract with every accepted value. It
is the authority; prefer it to any document, including this one.

## What not to save

- secrets, credentials, API keys, tokens
- transcripts of the conversation
- ordinary file contents, logs, command output
- anything the code or git history already records
- ideas you are still turning over — wait until they settle

If you would not want to read it back in three months, do not write it.

## When something goes wrong

**A refused call tells you what to fix.** It names the field and usually the
corrected value. Fix it and send it again.

One refusal is never a reason to stop using memory for the rest of the session.
That is the single most expensive mistake you can make here: the user loses
everything the rest of the session would have remembered, and they will not know
it happened.

If the tools genuinely are not there, carry on with the task, tell the user that
memory was unreachable so they can fix it, and do not invent memory operations.

## Before you finish

Take one look back: did this task settle anything a future session would
otherwise have to work out again? If so, write it now.

If nothing durable happened, write nothing. A memory that says "I did some work"
helps no one.
