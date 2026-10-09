# Codex

> Rules Codex can't forget.

`AGENTS.md` is advice: Codex can lose it in a long session or inside a subagent. The AgentLTL
plugin for [OpenAI Codex CLI](https://github.com/openai/codex) checks every tool call against
`AGENTLTL.yaml` **before it runs**, and refuses the ones that break it. Source:
[AgentLTL/agentltl-codex](https://github.com/AgentLTL/agentltl-codex).

It is the [Claude Code plugin](../claude-code/index.md)'s guard on Codex's hooks: the same rule
language, the same [library](../../rules/library.md), the same `AGENTLTL.yaml`. A project can
share one rule file between Codex, Claude Code, [Copilot CLI](../copilot-cli/index.md) and
[Mistral Vibe](../mistral-vibe/index.md). It works with whatever model Codex runs, OpenAI's or
your own.

## Install

Requires Python 3.10+, git, and OpenAI Codex CLI (tested with 0.162).

```bash
codex plugin marketplace add AgentLTL/agentltl-codex
codex plugin add agentltl@agentltl
"$(ls -td ~/.codex/plugins/cache/agentltl/agentltl/*/ | head -1)"bin/agentltl install
```

Codex runs no hook, a plugin's or your own, until you trust it: until then it skips it
without a word. `agentltl install` trusts AgentLTL's hooks by writing their hashes in
`~/.codex/config.toml` (between two marker comments; the rest of the file is kept), and puts
the `agentltl` command in `~/.local/bin`. You can approve each hook in Codex's `/hooks`
instead. The plugin builds its Python environment on first use (in `~/.codex/plugins/data/`)
and does nothing until there is an `AGENTLTL.yaml`: at a project's root for that project, or
in `~/.codex/` for every project. In a Codex session, `$agentltl:setup` picks the first rules.

**Updating:** `agentltl update` (it upgrades the plugin, then trusts the new version's hooks).
**Removing:** `agentltl uninstall`, then `codex plugin remove agentltl@agentltl`.

## Skills

| Skill | What it does |
|---|---|
| `$agentltl:setup` | Pick rules from the [library](../../rules/library.md); also offers the instructions import |
| `$agentltl:rules <rule>` | Add, change or remove a rule in plain words: Codex drafts it, tests it, and shows it before saving |
| `$agentltl:import` | Turn what your instructions (`AGENTS.md`) already say into enforced rules |
| `$agentltl:status` | The rules in force, and what was recently refused |

Type them in a message, or pick them in `/skills`. The `agentltl` command line (`validate`,
`check`, `translate`, `library`, `use`, `trace`, `memory scan`…) is put in `~/.local/bin` by
`agentltl install`.

## Tool names

Rules name tools as the library does, with Claude Code's names, so one file serves every
agent. Codex's tools are mapped onto them:

| Codex | Rules say |
|---|---|
| shell `{command}` | the commands it runs (`git_push`, `pytest`…) |
| `apply_patch` | `Write` (Add File), `Edit` (Update File), `rm` (Delete File), with `file_path`… |
| `cat`, `head`, `tail`, `sed -n`… on a file | also `Read {file_path}`: Codex has no Read tool |
| `view_image`, `spawn_agent`, `web_search` | `Read`, `Task`, `WebSearch` |

An `apply_patch` is checked as the files it adds, updates and deletes, so rules on `Write`,
`Edit` and `rm` hold for it. A file a successful `cat`, `head`, `tail`, `sed` (not `-i`),
`nl`, `less`, `more`, `bat` or `tac` printed counts as read, so rules such as
`read-before-overwrite` work unchanged.

Library entries written for another agent (`no-claude-coauthor`, `subagents-on-sonnet`,
`no-copilot-coauthor`, `no-vibe-coauthor`) switch nothing on in Codex. With commit
attribution on, Codex signs commits (`Co-authored-by: Codex <noreply@openai.com>`) and pull
requests ("Generated with Codex"): `no-codex-coauthor` refuses those commits.

## Rules instead of instructions

When you tell Codex "remember: never push to main", it would write that into `AGENTS.md`,
where it can be forgotten. The built-in `memory-first` rule steers it to an enforced rule
instead. `$agentltl:import` does the same for what `AGENTS.md` and `AGENTS.override.md` (from
the project root down to the working directory) and `~/.codex/AGENTS.md` already hold: it
drafts and tests a rule for each statement about tool calls, and asks which to keep.

## How it works

Codex runs the plugin's hooks (`hooks/hooks.json`) around every tool call, once they are
trusted:

- `SessionStart` and `SubagentStart` list the rules in force to Codex, or to the subagent.
- `PreToolUse` translates the call, checks it against the rules and the trace, and denies it
  (with the reason) or stays silent. After a `stop`, every call is denied until you write
  again.
- `PostToolUse` records calls that ran, and whether they failed (the exit code, read from
  the session's rollout file), and scans their output for credentials.
- `UserPromptSubmit` notes that you replied: it lifts a `stop` and lets an approved `ask`
  through.
- `Stop` sends Codex back, a bounded number of times, while a `finally` rule is unmet.

Codex runs hooks inside subagents too: their calls are checked and recorded in the parent's
session.

Codex's hooks have no "ask" answer, so the plugin emulates it: an `ask` rule refuses the
call, Codex asks you in its reply and ends its turn, and once you have written, the exact
same call goes through once. When Codex's approval policy is `never` (`codex exec`,
`--yolo`) nobody can answer, so an `ask` is refused; in an interactive `--yolo` session,
start Codex with `AGENTLTL_AUTO=0` to be asked.

The rules, the guard and the hooks' logic are [agentltl-coding](../agentltl-coding.md),
shared with the Claude Code plugin. The [full reference](reference.md) maps every feature of
the Claude Code plugin onto Codex.

## Limits

- **Hooks must be trusted.** A hook whose definition changed needs trusting again: re-run
  `agentltl install` after an update that changes `hooks/hooks.json` (Codex's `/hooks` shows
  "review required" otherwise). `agentltl update` does it for you.
- **A hook timeout lets the call through.** Codex allows a call when a hook fails, so the
  plugin's hooks always answer, and refuse a call they couldn't check; but a hook that Codex
  kills on its timeout (120 s for `PreToolUse`) answers nothing, and the call goes ahead.
- **`ask` goes through Codex.** Codex's hooks can't prompt you, so the plugin trusts Codex
  to ask, and to respect a "no".
- **Reads through the shell.** Only the viewer commands above count as reading a file; one
  printed by `python -c` or `awk` doesn't.
- **Exit codes come from the session's rollout file.** If Codex stops writing it, failed
  commands count as successful.
- **Notices** (`systemMessage`) are not shown by `codex exec --json`.
- **Input to a running process** (`write_stdin`) is not checked.
- **No status line.** Codex's status line takes fixed items only: `$agentltl:status` and
  `agentltl trace` show the same.
- As in Claude Code, it sees commands, not programs, and is a rulebook, not a sandbox.
