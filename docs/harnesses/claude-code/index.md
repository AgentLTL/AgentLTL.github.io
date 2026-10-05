# Claude Code

> Rules Claude Code can't forget.

`CLAUDE.md` is advice: Claude can lose it after compaction or inside a subagent. The
AgentLTL plugin checks every tool call against `AGENTLTL.yaml` **before it runs**, and
refuses the ones that break it. Source:
[AgentLTL/agentltl-claude-code](https://github.com/AgentLTL/agentltl-claude-code).

## Install

Requires Python 3.10+ and git. Paste this into Claude Code:

```
Set up the AgentLTL plugin for me by following https://raw.githubusercontent.com/AgentLTL/agentltl-claude-code/main/SETUP.md
```

Claude installs the plugin, turns on automatic updates, prepares its environment, and helps
you pick the first rules. Or by hand:

```bash
claude plugin marketplace add https://github.com/AgentLTL/agentltl-claude-code.git
claude plugin install agentltl@agentltl
```

Then turn on auto-update (`/plugin` → **Marketplaces** → `agentltl`) and run
`/reload-plugins`. The plugin does nothing until there is an `AGENTLTL.yaml`: at a project's
root for that project, or in `~/.claude/` for every project.

**Updating:** with auto-update on, new versions arrive at startup. To update now:
`claude plugin marketplace update agentltl && claude plugin update agentltl@agentltl`,
then `/reload-plugins`.

## Commands

| Command | What it does |
|---|---|
| `/agentltl:setup` | Pick rules from the [library](../../rules/library.md); also offers the memory import and the status line |
| `/agentltl:rules <rule>` | Add, change or remove a rule in plain words: Claude drafts it, tests it, and shows it before saving |
| `/agentltl:import` | Turn what `CLAUDE.md` and memory already say into enforced rules |
| `/agentltl:status` | The rules in force, and what was recently refused |

Claude also uses the `agentltl` command line (`validate`, `check`, `translate`, `tools`,
`library`, `use`, `memory scan`…), and so can you: see the [full reference](reference.md#cli).

## See that it's on

Claude Code doesn't show a plugin's startup messages, so the plugin puts its state in the
status line:

```
AgentLTL ● 4 rules · 2 block · 1 ask · 1 warn
```

`/agentltl:setup` offers to turn it on, or run `agentltl statusline --install`. It adds a
`statusLine` entry to `~/.claude/settings.json`, never replaces a status line you already
have, and keeps working across plugin updates. A broken rule file shows as
`⚠ AGENTLTL.yaml has errors · nothing is enforced`.

## Rules instead of memory

When you tell Claude "remember: never push to main", it would normally write that to
`CLAUDE.md` or its auto memory, where it can be forgotten. A built-in rule, `memory-first`,
steers it to an enforced rule instead, and keeps memory for facts, preferences and style.

For what memory already holds, `/agentltl:import` reads your `CLAUDE.md` files,
`.claude/rules/` and auto memory, picks out the statements that are rules about tool calls,
drafts and tests a rule for each, and asks which to keep:

```
"git submodule update --init  # NEVER --recursive"   (CLAUDE.md:9)
  → no-recursive-submodules  [block]  git submodule update --recursive

"Do not pip-install into a host env"   (CLAUDE.md:29)
  → no-host-pip  [warn]  pip install …   (docker compose run … pip install stays allowed)

"Prefer vLLM + parallel workers over TransformersModel"
  → not a rule: it's about code, which the guard doesn't see. It stays in memory.
```

Each rule keeps a `from:` link to its statement, so the next import only shows what's new.

## Secret leak alerts

A rule stops a call before it runs. When a program prints a credential anyway, the plugin
scans each call's output for well-known formats (cloud access key IDs, GitHub, GitLab,
Slack, Stripe, npm tokens, Google, Anthropic and OpenAI API keys, private keys). You see
which kind of credential appeared, never the value, so you can rotate it; Claude is told not
to repeat or store it. The [`devops-secrets`](../../rules/library.md#bundles) bundle adds
rules against revealing secrets in the first place.

## How it works

Four hooks:

- `SessionStart` lists the rules to Claude, again after compaction.
- `PreToolUse` translates the call, checks it against the rules and the trace, and allows,
  refuses (with the reason), asks you, or stops. A stop leaves Claude its turn to explain;
  every tool call is refused until you reply.
- `UserPromptSubmit` lifts a stop when you reply.
- `PostToolUse` records calls that ran, and scans their output.

State is kept per session and per project in the plugin's data folder, under a lock, since
Claude Code may run tool calls in parallel. Everything else is in the
[full reference](reference.md).

## Limits

- **It sees commands, not programs.** It sees `make test`, not the `pytest` in your Makefile:
  list wrappers in your rules. It's a rulebook for Claude, not a sandbox.
- **Some commands can't be analysed:** `eval`, `$CMD args`, `cmd &`. In normal mode you're
  asked about them; in auto mode they go through and Claude is told they weren't checked.
- **Leak alerts** recognise formats with a distinctive prefix only.
