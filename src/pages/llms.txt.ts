import { DOMAIN } from './_site';

/**
 * llms.txt is linked from the footer of every page, so it is reader-facing copy
 * and not a machine record. Every claim in the closing paragraph is one a human
 * has to be able to check.
 */
export const body = `# Kaleidoscope

> Local native memory for agents. Your memory lives in a vault on your machine, and every editor or agent you connect shares one profile through a command-line tool and a long-lived stdio MCP server. Kaleidoscope is not released: nothing installs from a registry, and signing in does not work.

- [Documentation](${DOMAIN}/docs/): what Kaleidoscope is, and which page answers your question
- [Getting started](${DOMAIN}/docs/getting-started/): the five commands you will run, in order
- [Give your agent the skill](${DOMAIN}/docs/skill/): how an agent is told Kaleidoscope exists, and the four files it installs
- [Install](${DOMAIN}/docs/packages/): the two package names, what is inside them, and why you cannot install them yet
- [CLI reference](${DOMAIN}/docs/cli/): every \`kaleidoscope\` command and flag
- [MCP reference](${DOMAIN}/docs/mcp/): the two tools an agent sees, \`search\` and \`remember\`, and how to call them
- [Integrations](${DOMAIN}/docs/integrations/): Codex, Claude Code, Cursor, OpenCode, LangChain, LangGraph, Claude Agent SDK, OpenAI Agents SDK, CrewAI, and any standard MCP client
- [Security](${DOMAIN}/docs/security/): what is isolated from what, what is not signed, and how to report a vulnerability
- [Privacy](${DOMAIN}/docs/privacy/): what stays on your machine, where a credential would be kept, and what this website itself does
- [Licenses and terms](${DOMAIN}/docs/legal/): Apache-2.0 and CC BY 4.0 are in force; the product terms are reviewed drafts, not yet adopted
- [Privacy notice](${DOMAIN}/docs/legal/privacy-notice/): a counsel-reviewed draft of the production privacy terms, not yet in force
- [Security policy](${DOMAIN}/docs/legal/security-policy/): a counsel-reviewed draft of the disclosure and supported-version policy, not yet in force
- [Support policy](${DOMAIN}/docs/legal/support-policy/): a counsel-reviewed draft of the support scope and response targets, not yet in force
- [Account](${DOMAIN}/docs/account/): you do not need an account, and you cannot create one yet
- [Operations](${DOMAIN}/docs/operations/): back up your memory, move it, uninstall, and delete a vault safely
- [Platforms](${DOMAIN}/docs/compatibility/): which platforms Kaleidoscope is for, and the one thing Windows does differently
- [Benchmarks](${DOMAIN}/docs/benchmarks/): two separate experiments — on the larger corpus, twelve times the memories at the same answer quality; on the smaller one, level with mem0 at 24% fewer tokens
- [Status](${DOMAIN}/status/): whether anything is available, whether anything is down, and what has actually been run
- [Public agent skill](${DOMAIN}/SKILL.md): how an agent should retrieve and write memory
- [Agent instructions](${DOMAIN}/agent-instructions.md): the short pointers Kaleidoscope installs into AGENTS.md, CLAUDE.md, or a Cursor rule
- [Status record](${DOMAIN}/status.json): the same status these pages state, in machine-readable form
- [Platform support record](${DOMAIN}/platform-support.json): which platforms have been run on and which have only had a compiler check
- [Full CLI help text](${DOMAIN}/reference/kaleidoscope-cli.txt): the complete \`kaleidoscope\` help output
- [Tool reference](${DOMAIN}/reference/kaleidoscope-mcp.json): the fields of the two tools an agent sees

Kaleidoscope has only ever been run on one kind of machine: a Mac with Apple Silicon. On that machine you can run a build you already have, connect Claude Code, Codex, OpenCode, Cursor, a standard MCP client or an agent framework to it, and have them all share one local memory. You cannot install it from npm or PyPI, because neither package is published; you cannot download a build for any platform; and you cannot sign in, because no sign-in service is configured and every account command answers \`provider not configured\`. macOS on Intel, Linux on x86_64 and arm64, and Windows on x86_64 have had a compiler check for the memory engine and nothing more — nothing was ever assembled into a program for them and nothing has been run there. Windows on arm64 has not had even that, and on Windows creating a new vault is refused on purpose until its filesystem work lands. Three connections carry a limit: Codex's configuration entry is written, read back and removed exactly, but Codex offers no way to confirm it then starts the server; Cursor's configuration and project rule are written and removed exactly, but Cursor has never been launched against them; and the agent frameworks were run against stand-in models rather than a live provider. Nothing has been driven through an editor's graphical interface. Nothing is signed for release. Apache-2.0 covers the public code and CC BY 4.0 covers this documentation, and both are in force; the product terms — the engine licence, the privacy notice, the security policy and the support policy — have been reviewed by counsel but not adopted, and none of them is yet in force. There is no support commitment and no published security contact yet. Hosted memory does not exist: there is no service, endpoint, API or waitlist, and nothing syncs your memory anywhere. Benchmark results are stated in plain words on the benchmarks page; the full benchmark method is not published yet, and there is no build you could reproduce it with. The memory engine ships as proprietary object code, and its source is not in any public surface.
`;

export const GET = () =>
  new Response(body, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
