<!-- >>> kaleidoscope-manager owner=kaleidoscope-manager-v1 instruction=claude -->
## Kaleidoscope memory

This project's memory across sessions: decisions made, preferences stated, constraints, corrections, and what past work produced. `search` reads it, `remember` writes it. All local -- no network, nothing leaves this machine.

**Prefer the CLI when you have a shell.** One invocation costs a couple of dozen tokens; the MCP tool definitions sit in your context all session (~1,800) whether or not you call them. Use the MCP `search`/`remember` tools only when you have no shell -- same engine, same vault.

```bash
echo '{"query":"how we handle retries","top_k":5}' | kscope call --profile default search
kscope schema remember   # the write contract, when you need it
```

**Search before you go looking.** Before grepping, reading your way around the code, or asking the user how this project works -- search first. Code shows what *is*; memory shows what was *decided*, and why. A question already settled here must not be asked twice.

**Write without being asked** when the user states a preference, makes or rejects a decision, sets a constraint, corrects you, or work produces a result worth keeping. Don't wait for "remember this", and don't batch writes to the end of the task -- write when it lands, while you still know why.

**Write what you had to dig for.** Those triggers are things the *user* did; this one is you. Whatever you established by reading code, running an experiment, or ruling out a wrong answer is the most expensive thing in a session to rediscover. **That applies hardest to agents you spawn.** A subagent or workflow agent sees only the prompt you write it, so put "search Kaleidoscope first, record what you establish" in that prompt -- or write its findings yourself when it reports back.

Never store secrets, transcripts, ordinary file contents, anything the code or git history already records, or ideas still in flux.

A refusal names the field to fix and what to change it to: correct it and resend. One refusal is never a reason to stop using memory.

Full write contract: `.claude/skills/use-kaleidoscope/SKILL.md`, or `kscope schema remember`.
<!-- <<< kaleidoscope-manager owner=kaleidoscope-manager-v1 instruction=claude -->
