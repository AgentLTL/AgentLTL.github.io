# Get started

Pick the way you use agents. For the coding-agent plugins you need **Python 3.10+ and
git** on the machine; the plugin builds its own environment the first time it starts
(about 10 seconds). Setting it up for a team? Read
[operating it](harnesses/operating.md) too.

=== "Claude Code"

    Install it by hand:

    ```bash
    claude plugin marketplace add https://github.com/AgentLTL/agentltl-claude-code.git
    claude plugin install agentltl@agentltl
    ```

    Then, in Claude Code, run `/reload-plugins` and `/agentltl:setup`.

    Or let Claude do it: paste this into Claude Code. It installs the plugin, turns on
    updates, and helps you choose the first rules. (It follows the
    [setup file](https://raw.githubusercontent.com/AgentLTL/agentltl-claude-code/main/SETUP.md)
    at that address, so read it first if you want to know what it will do.)

    ```
    Set up the AgentLTL plugin for me by following https://raw.githubusercontent.com/AgentLTL/agentltl-claude-code/main/SETUP.md
    ```

    The plugin does nothing until there is an `AGENTLTL.yaml`, at a project's root for that
    project, or in `~/.claude/` for every project. Setup writes the first one with you.

    **Check that it is on:** the status line shows `AgentLTL ● 4 rules · …` once you run
    `agentltl statusline --install` (setup offers it), and `/agentltl:status` lists the
    rules in force.

    [More on the Claude Code plugin](harnesses/claude-code/index.md)

=== "GitHub Copilot CLI"

    Install the plugin from its marketplace:

    ```bash
    copilot plugin marketplace add AgentLTL/agentltl-copilot-cli
    copilot plugin install agentltl@agentltl
    ```

    Then, in a Copilot CLI session, run `/agentltl-setup` to choose the first rules.

    The plugin does nothing until there is an `AGENTLTL.yaml`, at a project's root for that
    project, or in `~/.copilot/` for every project. Setup writes the first one with you. A
    project's file works for Claude Code, Copilot CLI and Mistral Vibe alike.

    **Check that it is on:** run `agentltl validate` in the project. It lists the rules in
    force and where each comes from.

    [More on the Copilot CLI plugin](harnesses/copilot-cli/index.md)

=== "Mistral Vibe"

    Clone the plugin into Vibe's plugin folder, then add its hooks:

    ```bash
    git clone --recurse-submodules https://github.com/AgentLTL/agentltl-mistral-vibe.git ~/.vibe/plugins/agentltl
    ~/.vibe/plugins/agentltl/bin/agentltl install
    ```

    `install` adds AgentLTL's hooks to `~/.vibe/hooks.toml` (your own are kept) and links
    `agentltl` into `~/.local/bin`. Then, in a Vibe session, run `/agentltl-setup` to choose
    the first rules. It works with any model Vibe runs, Mistral's or an OpenAI-compatible one
    of your own.

    The plugin does nothing until there is an `AGENTLTL.yaml`, at a project's root for that
    project, or in `~/.vibe/` for every project. Setup writes the first one with you.

    **Check that it is on:** run `agentltl validate` in the project. It lists the rules in
    force and where each comes from.

    [More on the Mistral Vibe plugin](harnesses/mistral-vibe/index.md)

=== "Your own agent (Python)"

    ```bash
    pip install agentltl                 # the formula engine, no dependencies
    pip install "agentltl[smolagents]"   # with run-time enforcement for smolagents
    pip install "agentltl[native]"       # or the native OpenAI-compatible loop
    ```

    ```python
    from agentltl import Constraint, Before, CalledNTimes, verify_trace

    trace = {"tool_calls": [{"tool_name": "fetch_data"}, {"tool_name": "save_results"}]}
    constraints = [
        Constraint("fetch_before_save", Before("fetch_data", "save_results")),
        Constraint("save_once", CalledNTimes("save_results", 1, "==")),
    ]
    print(verify_trace(trace, constraints)["compliance_score"])   # 1.0
    ```

    A *trace* is the list of tool calls an agent made. The score is the share of constraints
    the trace satisfies, weighted: `1.0` means all of them. Swap the two calls
    (`save_results` first) and `fetch_before_save` fails, so the score drops below `1.0`.
    To refuse calls while the agent runs, instead of scoring afterwards, see
    [enforcement](concepts/enforcement.md).

    [More on the Python library](python/index.md)

## Your first rule

A rule file is YAML. This one makes the agent run the tests before it pushes, and run them
again after any edit:

```yaml title="AGENTLTL.yaml"
rules:
  - id: tests-before-push
    before: {first: pytest, then: git_push, since: [Edit, Write]}
    why: CI is slow; run the tests locally first.
    fix: Run pytest, then push.
```

Reading it:

- `pytest` and `git_push` are *tool names*. A shell command is translated into one:
  `git push origin main` is `git_push`, and `pytest` is `pytest`
  ([how that works](concepts/shell.md)). `Edit` and `Write` are the agent's own file tools.
- `before` means `git_push` is allowed only once `pytest` has run.
- `since: [Edit, Write]` means that run has to come *after the last edit*, so editing a file
  after the tests ran sends the agent back to run them again.

The agent sees `why` and `fix` when it is refused. In Claude Code, Copilot CLI and Mistral
Vibe you can also write rules in plain words (`/agentltl:rules never push to main`, or
`/agentltl-rules` in Copilot and Vibe), and switch on tested ones from the
[library](rules/library.md).

Next: [what a rule can say](rules/index.md).
