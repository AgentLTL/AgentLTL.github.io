# Harnesses

A harness connects AgentLTL to a coding agent. It intercepts every tool call the agent
makes, translates shell commands into structured calls, checks them against the rules, and
returns the agent's own kind of refusal. The rule format, the rule library and the shell
parser are shared; each harness adds what its agent needs: how it installs, how rules are
written and listed, how the human approves an `ask`.

The shared part is a Python package,
[agentltl-coding](agentltl-coding.md): the rule language, the library, the guard and its
state. A harness gives it a `Harness` description (the agent's name, where the user's rules
live, which tools take shell commands, built-in rules of its own) and connects the guard to
the agent's hooks.

| Harness | Status | Hooks into |
|---|---|---|
| [Claude Code](claude-code/index.md) | Available | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `UserPromptSubmit` and `SessionStart` hooks; skills; status line |
| OpenAI Codex | Planned | |
| GitHub Copilot (VS Code) | Planned | |

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
