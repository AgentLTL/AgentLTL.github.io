# GitHub Copilot CLI

> Rules Copilot can't forget.

Custom instructions are advice: Copilot can lose them in a long session or inside a
subagent. The AgentLTL plugin for [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/copilot-cli)
checks every tool call against `AGENTLTL.yaml` **before it runs**, and refuses the ones that
break it. Source:
[AgentLTL/agentltl-copilot-cli](https://github.com/AgentLTL/agentltl-copilot-cli).

It is the [Claude Code plugin](../claude-code/index.md)'s guard on Copilot CLI's hooks: the
same rule language, the same [library](../../rules/library.md), the same `AGENTLTL.yaml`. A
project can share one rule file between both agents.

## Install

Requires Python 3.10+, git, and Copilot CLI.

```bash
copilot plugin marketplace add AgentLTL/agentltl-copilot-cli
copilot plugin install agentltl@agentltl
```

The plugin builds its Python environment on first use, in `~/.copilot/plugin-data/`, and
does nothing until there is an `AGENTLTL.yaml`: at a project's root for that project, or in
`~/.copilot/` for every project. In a Copilot session, `/agentltl-setup` picks the first rules.

**Updating:** `copilot plugin update agentltl`.

## Commands

| Command | What it does |
|---|---|
| `/agentltl-setup` | Pick rules from the [library](../../rules/library.md); also offers the instructions import and the status line |
| `/agentltl-rules <rule>` | Add, change or remove a rule in plain words: Copilot drafts it, tests it, and shows it before saving |
| `/agentltl-import` | Turn what your custom instructions already say into enforced rules |
| `/agentltl-status` | The rules in force, and what was recently refused |

The `agentltl` command line (`validate`, `check`, `translate`, `library`, `use`,
`memory scan`…) is in the plugin's `bin/`. Copilot CLI doesn't put it on the PATH;
`agentltl install-cli` links it into `~/.local/bin`:

```bash
~/.copilot/installed-plugins/agentltl/agentltl/bin/agentltl install-cli
```

## Tool names

Rules name tools as the library does, with Claude Code's names. Copilot's tools are mapped
onto them, arguments included, so every library rule works unchanged:

| Copilot CLI | Rules say |
|---|---|
| `bash {command}` | the commands it runs (`git_push`, `pytest`…) |
| `create {path, file_text}` | `Write {file_path, content}` |
| `edit {path, old_str, new_str}` | `Edit {file_path, old_string, new_string}` |
| `view {path}` | `Read {file_path}` |
| `glob`, `grep`, `task`, `web_fetch` | `Glob`, `Grep`, `Task`, `WebFetch` |

Library entries written for one agent (`no-claude-coauthor` and `subagents-on-sonnet` for
Claude Code, `no-copilot-coauthor` for Copilot) switch nothing on in the other.

## Rules instead of instructions

When you tell Copilot "remember: never push to main", it would write that into
`copilot-instructions.md` or `AGENTS.md`, where it can be forgotten. The built-in
`memory-first` rule steers it to an enforced rule instead. `/agentltl-import` does the same
for what `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`,
`AGENTS.md` and `~/.copilot/copilot-instructions.md` already hold: it drafts and tests a rule
for each statement about tool calls, and asks which to keep.

## How it works

Six hooks, in the plugin's `hooks.json`:

- `sessionStart` lists the rules to Copilot.
- `preToolUse` translates the call, checks it against the rules and the trace, and denies it
  (with the reason), asks you, or stays silent. After a `stop`, every call is denied until
  you write again.
- `postToolUse` and `postToolUseFailure` record calls that ran, and whether they failed,
  scan their output for credentials, and pass on notes for calls that went ahead.
- `agentStop` sends Copilot back, a bounded number of times, while a `finally` rule is unmet.
- `userPromptSubmitted` lifts a stop when you reply.

The rules, the guard and the hooks' logic are [agentltl-coding](../agentltl-coding.md),
shared with the Claude Code plugin. The [full reference](reference.md) maps every feature of
the Claude Code plugin onto Copilot CLI.

## Limits

- **Copilot CLI only.** Copilot in VS Code and the cloud agent are not covered yet.
- **Notes come late.** Copilot's `preToolUse` answer has no field for a note on a call that
  goes ahead, so a `log` rule's note reaches Copilot with the call's result.
- **Unattended runs.** In `copilot -p`, an `ask` is refused, even with `--allow-all-tools`.
  Copilot doesn't tell hooks which mode it runs in: set `AGENTLTL_AUTO=1` for unattended
  runs so commands the guard can't analyse follow `unparseable.auto` instead of being refused.
- **The status line is experimental** in Copilot CLI (`agentltl statusline --install` turns
  on its feature flag).
- As in Claude Code, it sees commands, not programs, and is a rulebook, not a sandbox.
