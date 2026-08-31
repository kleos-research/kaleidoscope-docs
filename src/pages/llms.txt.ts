import { DOMAIN } from './_site';

/**
 * llms.txt is linked from the footer of every page, so it is reader-facing copy
 * and not a machine record. Every claim in the closing paragraph is one a human
 * has to be able to check.
 */
export const body = `# Kaleidoscope

> Local memory for coding agents. Your agent forgets everything between sessions; Kaleidoscope gives it a memory that lives in a folder on your own machine and is shared by every editor and agent you use. Install it with \`npm install -g @kleos-research/kaleidoscope\`. It needs a key to run — email contact@kleosresearch.xyz.

- [Documentation](${DOMAIN}/docs/): what Kaleidoscope is, and which page answers your question
- [Getting started](${DOMAIN}/docs/getting-started/): install, activate with your key, and give a project a memory
- [Give your agent the skill](${DOMAIN}/docs/skill/): how an agent is told Kaleidoscope exists, and the four files it installs
- [Install](${DOMAIN}/docs/packages/): the package names and what is inside them
- [CLI reference](${DOMAIN}/docs/cli/): every \`kscope\` command and flag
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

Kaleidoscope is installable today: \`npm install -g @kleos-research/kaleidoscope\` gives you the \`kscope\` command on macOS and Linux, on both Apple Silicon and x86_64. It needs a key to run. We send keys by email — write to contact@kleosresearch.xyz. Windows is not supported: creating a vault there is refused on purpose until the filesystem work lands.

Once it is installed, \`kscope init\` in a project creates the memory and connects whichever agent you use. Claude Code, Codex, Cursor, OpenCode, standard MCP clients and the agent frameworks all read the same vault. Two of those connections have a limit worth stating: Codex's configuration entry is written and removed exactly, but Codex offers no way to confirm it then starts the server, and Cursor's has never been checked by launching Cursor itself. The agent frameworks were tested against stand-in models rather than a live provider.

What is not here: hosted memory does not exist -- there is no service, endpoint, API or waitlist, and nothing syncs your memory anywhere. It stays in a folder in your project. Apache-2.0 covers the public code and CC BY 4.0 covers this documentation, and both are in force; the engine licence, privacy notice, security policy and support policy have been reviewed by counsel but not adopted, so none of them is yet in force and there is no support commitment. Nothing is signed for release. The part that stores and searches your memory ships as proprietary object code, and its source is not public. Benchmark results are described in plain words on the benchmarks page; the full benchmark method is not published yet.
`;

export const GET = () =>
  new Response(body, {
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  });
