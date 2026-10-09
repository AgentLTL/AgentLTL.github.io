# Operating it

For whoever installs AgentLTL for others, or has to answer "what is this running on my
machine?". It covers the Claude Code, Copilot CLI, Mistral Vibe and Codex plugins; the details are
in each plugin's full reference.

## What it is

A set of hooks, run by the agent itself before and after every tool call, plus a Python
program that checks each call against `AGENTLTL.yaml`. It is a rulebook for the agent, not
a sandbox: it sees the commands the agent runs, not what those programs do inside.

## What it needs

- Python 3.10+ and git on the machine.
- In Codex, `agentltl install` to trust the plugin's hooks: Codex runs no hook until it is
  trusted (or approved in its `/hooks`).
- On the first session start (in Mistral Vibe, at `agentltl install`), the plugin builds a
  virtualenv in its data directory (about 10 seconds). It survives updates and is rebuilt only when the pinned dependencies
  change.

## Where things live

| What | Where |
|---|---|
| Project rules | `AGENTLTL.yaml` at the project's root (commit it, so the whole team gets the same rules) |
| Your rules, for every project | `~/.claude/AGENTLTL.yaml` (Claude Code), `~/.copilot/AGENTLTL.yaml` (Copilot CLI), `~/.vibe/AGENTLTL.yaml` (Mistral Vibe), `~/.codex/AGENTLTL.yaml` (Codex) |
| What the agent has done (the trace) | the plugin's data directory, under `sessions/` and `projects/` |
| The environment it runs in | the same data directory (a virtualenv) |

A project file works for every agent. When a user file and a project file both exist, both
apply; a project can switch one of the user's rules off with `disable:`.

## Rolling it out to a team

1. Commit an `AGENTLTL.yaml` to each repository. Start with a few
   [library rules](../rules/library.md) (`use: [no-force-push, protect-env-files]`) in
   `warn` or `log` mode, and move the ones you trust to `block`.
2. For Claude Code, the plugin can be installed on every machine that has a given
   `~/.claude/settings.json`: put the marketplace and `enabledPlugins` entries in it, as
   shown in the [Claude Code reference](claude-code/reference.md#setup).
3. Check a rule file before you ship it, without running anything:

    ```bash
    agentltl validate                       # the rules in force, and where each comes from
    agentltl check "deny: git push -f" "allow: pytest"
    ```

## Checking that it is on

- **Claude Code** shows its state in the status line, for example
  `AgentLTL ● 4 rules · 2 block · 1 ask · 1 warn`. `/agentltl:status` lists the rules in
  force and what was recently refused. `agentltl statusline --install` turns the status
  line on. Mistral Vibe has no status line, and Codex's takes fixed items only:
  `/agentltl:status` (`$agentltl:status` in Codex) and `agentltl trace` show the same.
- A broken rule file shows as `⚠ AGENTLTL.yaml has errors · nothing is enforced`. Run
  `agentltl validate` to see why.
- `agentltl trace` prints what has been recorded for this session and the project.

## Updates

The plugins have no fixed version: every push to `main` is an update. With auto-update on,
Claude Code fetches it in the background and tells the user to run `/reload-plugins`;
without it, the update applies at the next launch, or when you run the update command by
hand. Mistral Vibe has no plugin manager: `agentltl update` pulls the plugin and
reinstalls its hooks. In Codex, `agentltl update` upgrades the plugin, then trusts the new
version's hooks (a hook whose definition changed doesn't run until it is trusted again). If you need a fixed version, leave auto-update off and update on your own schedule.

## Network use

Installing and updating fetch the plugin from GitHub, and the first run installs the
Python packages it pins (from the plugin's own copies, or from GitHub at the commits in
`vendor.lock`). The checking itself runs locally in the Python process: rules are
evaluated on the machine, against a trace stored on the machine.

## When it gets in the way

- **A rule refuses something it should allow.** `agentltl check` replays a command
  against the rules and names the rule that fires. Change that rule's `mode`, narrow its
  target, or switch it off: `agentltl disable RULE-ID` (`--user` for your own file).
- **A rule remembers calls it shouldn't.** `agentltl reset` forgets the session's memory;
  `agentltl reset --project` forgets the project's.
- **Nothing is checked at all.** With no `AGENTLTL.yaml` in the project or the user folder,
  the hooks exit at once and do nothing. Deleting the file is the quickest way to turn
  AgentLTL off without uninstalling.
- **An internal error.** The guard never approves a call on an error: it becomes a
  question to the person at the keyboard. In an unattended run, with nobody to ask, an
  `ask` is refused.

## Uninstalling

Remove the plugin with the agent's own plugin commands (`/plugin` in Claude Code,
`copilot plugin` in Copilot CLI; in Mistral Vibe, `agentltl uninstall`, then delete
`~/.vibe/plugins/agentltl`; in Codex, `agentltl uninstall`, then
`codex plugin remove agentltl@agentltl`). If you installed the status line, run
`agentltl statusline --uninstall` first. Rule files and recorded traces are left where
they are; delete `AGENTLTL.yaml` and the plugin's data directory to remove them.

## Limits worth knowing

- **It sees commands, not programs.** It sees `make test`, not the `pytest` in your
  Makefile: list wrappers in your rules.
- **Some commands can't be analysed:** `eval`, `$CMD args`, `cmd &`. In normal mode the
  person is asked about them; in auto mode they go through and the agent is told they
  weren't checked.
- **In Codex, a hook timeout lets the call through.** Codex allows a call when a hook
  is killed on its timeout (120 s for `PreToolUse`); every other failure is a refusal.
- **Secret leak alerts** recognise credential formats with a distinctive prefix only.
