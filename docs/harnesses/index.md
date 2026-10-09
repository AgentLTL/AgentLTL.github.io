# Harnesses

Installing it for yourself or a team? Start with [Get started](../get-started.md) and
[operating it](operating.md). The rest of this page is for people who build or extend a
harness.

A harness connects AgentLTL to a coding agent. It intercepts every tool call the agent
makes, translates shell commands into structured calls, checks them against the rules, and
returns the agent's own kind of refusal. The rule format, the rule library and the shell
parser are shared; each harness adds what its agent needs: how it installs, how rules are
written and listed, how the human approves an `ask`.

The shared part is a Python package,
[agentltl-coding](agentltl-coding.md): the rule language, the library, the guard and its
state, and what the hooks do. A harness gives it a `Harness` description (the agent's name,
where the user's rules live, its tool names mapped onto the canonical ones, which tools take
shell commands, where its memory lives, built-in rules of its own) and connects the guard to
the agent's hooks. One `AGENTLTL.yaml` serves every harness.

| Harness | Status | Hooks into |
|---|---|---|
| [Claude Code](claude-code/index.md) | Available | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `UserPromptSubmit` and `SessionStart` hooks; skills; status line |
| [GitHub Copilot CLI](copilot-cli/index.md) | Available | `preToolUse`, `postToolUse`, `postToolUseFailure`, `agentStop`, `userPromptSubmitted` and `sessionStart` hooks; skills; status line (experimental) |
| [Mistral Vibe](mistral-vibe/index.md) | Available | `pre_tool`, `post_tool` and `post_agent` hooks (no session-start or user-prompt hook, no "ask" answer: the plugin emulates them); skills |
| [Codex](codex/index.md) | Available | `PreToolUse`, `PostToolUse`, `Stop`, `UserPromptSubmit`, `SessionStart` and `SubagentStart` hooks, once trusted (no "ask" answer: the plugin emulates it); skills |
| GitHub Copilot (VS Code) | Planned | not started: [open an issue](https://github.com/AgentLTL/agentltl-claude-code/issues) if you need it |

## What every harness does

1. **Before each call**, translate it (a shell command becomes several calls), check every
   rule against the trace plus the call, and refuse or ask according to the rule's
   [mode](../concepts/enforcement.md#modes-what-happens-on-a-violation).
2. **After each call**, record it in the trace, with whether it failed, so later rules can
   see it ran.
3. **When the agent finishes**, check the `finally` rules and send it back if one is unmet.
4. **At the start**, tell the agent which rules are in force, so it plans around them
   instead of discovering them by being refused.
5. **Fail safe**: an internal error never approves a call; it becomes a question to the
   human.

Interested in a harness for another agent? [Open an issue](https://github.com/AgentLTL/agentltl-claude-code/issues).
