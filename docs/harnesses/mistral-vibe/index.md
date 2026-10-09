# Mistral Vibe

> Rules Vibe can't forget.

`AGENTS.md` is advice: Vibe can lose it in a long session or inside a subagent. The AgentLTL
plugin for [Mistral Vibe](https://github.com/mistralai/mistral-vibe) checks every tool call
against `AGENTLTL.yaml` **before it runs**, and refuses the ones that break it. Source:
[AgentLTL/agentltl-mistral-vibe](https://github.com/AgentLTL/agentltl-mistral-vibe).

It is the [Claude Code plugin](../claude-code/index.md)'s guard on Vibe's hooks: the same rule
language, the same [library](../../rules/library.md), the same `AGENTLTL.yaml`. A project can
share one rule file between Vibe, Claude Code and [Copilot CLI](../copilot-cli/index.md). It
works with whatever model Vibe runs, Mistral's or your own.

## Install

Requires Python 3.10+, git, and Mistral Vibe 2.26 or later.

```bash
git clone --recurse-submodules https://github.com/AgentLTL/agentltl-mistral-vibe.git ~/.vibe/plugins/agentltl
~/.vibe/plugins/agentltl/bin/agentltl install
```

Vibe has no plugin installer and doesn't run hooks from plugin folders. `agentltl install`
builds the plugin's Python environment (in `~/.vibe/plugin-data/agentltl`), adds AgentLTL's
three hooks to `~/.vibe/hooks.toml` (your own hooks there are kept), and links the `agentltl`
command into `~/.local/bin`. The plugin does nothing until there is an `AGENTLTL.yaml`: at a
project's root for that project, or in `~/.vibe/` for every project. In a Vibe session,
`/agentltl:setup` picks the first rules.

**Updating:** `agentltl update`. **Removing:** `agentltl uninstall`, then delete the folder.

## Commands

| Command | What it does |
|---|---|
| `/agentltl:setup` | Pick rules from the [library](../../rules/library.md); also offers the instructions import |
| `/agentltl:rules <rule>` | Add, change or remove a rule in plain words: Vibe drafts it, tests it, and shows it before saving |
| `/agentltl:import` | Turn what your instructions already say into enforced rules |
| `/agentltl:status` | The rules in force, and what was recently refused |

The `agentltl` command line (`validate`, `check`, `translate`, `library`, `use`, `trace`,
`memory scan`…) is linked into `~/.local/bin` by `agentltl install`.

## Tool names

Rules name tools as the library does, with Claude Code's names. Vibe's tools are mapped onto
them, and their arguments already have Claude Code's names, so every library rule works
unchanged:

| Mistral Vibe | Rules say |
|---|---|
| `bash {command}` | the commands it runs (`git_push`, `pytest`…) |
| `write_file`, `edit`, `read_file` | `Write`, `Edit`, `Read` (same arguments: `file_path`…) |
| `grep`, `web_fetch`, `web_search` | `Grep`, `WebFetch`, `WebSearch` |
| `agent_spawn` (`task` in the legacy runtime) | `Task` |

Library entries written for another agent (`no-claude-coauthor`, `subagents-on-sonnet`,
`no-copilot-coauthor`) switch nothing on in Vibe. Vibe signs commits by default
(`Co-Authored-By: Mistral Vibe`): `no-vibe-coauthor` refuses those commits, and
`include_commit_signature = false` in `~/.vibe/config.toml` stops Vibe from trying.

## Rules instead of instructions

When you tell Vibe "remember: never push to main", it would write that into `AGENTS.md`,
where it can be forgotten. The built-in `memory-first` rule steers it to an enforced rule
instead. `/agentltl:import` does the same for what `AGENTS.md`, `~/.vibe/AGENTS.md`, the
`instructions` of custom agents (`agents/*.toml`) and prompts (`prompts/*.md`) already hold:
it drafts and tests a rule for each statement about tool calls, and asks which to keep.

## Your own model

Vibe runs any OpenAI-compatible model, and AgentLTL doesn't depend on it: the hooks see tool
calls, whoever makes them. For a self-hosted model (vLLM serving Qwen, for example, with
`--enable-auto-tool-choice --tool-call-parser <parser>`), in `~/.vibe/config.toml`:

```toml
active_model = "qwen"

[[providers]]
name = "vllm"
api_base = "http://my-server:8000/v1"
api_key_env_var = "VLLM_API_KEY"   # its value in ~/.vibe/.env; "" for none
backend = "generic"
api_style = "openai"

[[models]]
name = "Qwen/Qwen3-Coder-30B-A3B-Instruct"   # the served model name
provider = "vllm"
alias = "qwen"
max_context_length = 131072
```

## How it works

Three hooks, in `~/.vibe/hooks.toml`:

- `pre_tool` translates the call, checks it against the rules and the trace, and denies it
  (with the reason) or stays silent. After a `stop`, every call is denied until you write
  again. It is installed with `strict = true`: if the guard crashes or times out, Vibe
  refuses the call. Vibe runs it before its own permission check, so the rules hold under
  `--auto-approve` too.
- `post_tool` records calls that ran, and whether they failed, scans their output for
  credentials, and passes on notes for calls that went ahead. On a session's first call, it
  lists the rules in force to Vibe.
- `post_agent` sends Vibe back, a bounded number of times, while a `finally` rule is unmet.

Vibe has no session-start or user-prompt hook, and no "ask" answer: the plugin emulates them.
The rules arrive with the first call's result, a stop is lifted by the call that follows your
reply, and an `ask` refuses the call and has Vibe ask you.

The rules, the guard and the hooks' logic are [agentltl-coding](../agentltl-coding.md),
shared with the Claude Code plugin. The [full reference](reference.md) maps every feature of
the Claude Code plugin onto Mistral Vibe.

## Limits

- **Subagents are not checked.** Vibe (2.26, default runtime) runs no hooks inside a
  subagent, so the calls a subagent makes escape the rules. The built-in rule
  `subagents-unchecked` makes spawning one a warning: Vibe is told to do the work itself, may
  insist by repeating the call, and you get a notice when a subagent starts.
  `subagents_unchecked: false` in `settings:` switches it off; `mode: block` (a project rule
  with the same id) forbids subagents.
- **`ask` goes through Vibe.** Vibe's hooks can't prompt you, so an `ask` rule refuses the
  call and Vibe asks you itself; the plugin lets the call through once Vibe has asked or you
  have written, trusting Vibe to respect a "no".
- **Notices name the tool, not the rule.** When a call is refused, Vibe shows you "Denied
  tool 'bash'"; the reason and the rule go to the model, which is asked to name the rule in
  its reply. `agentltl trace` lists every refusal with its rule.
- **Calls from `run_typescript`** (Vibe's sandbox that calls tools from code) are checked like
  any other, but a refused one only reads "skipped by Runtime policy" to the model.
- **The rules arrive with the first call's result**, not before Vibe's first message.
- **Unattended runs.** Set `AGENTLTL_AUTO=1` for `vibe -p`, so `ask` rules refuse and commands
  the guard can't analyse follow `unparseable.auto`.
- **Project hooks.** AgentLTL's hooks live in your `~/.vibe/hooks.toml`; it doesn't use a
  project's `.vibe/hooks.toml`, which Vibe only runs in trusted folders.
- **No status line.** Vibe has none: `/agentltl:status` and `agentltl trace` show the same.
- As in Claude Code, it sees commands, not programs, and is a rulebook, not a sandbox.
