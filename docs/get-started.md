# Get started

Pick the way you use agents.

=== "Claude Code"

    Paste this into Claude Code. It installs the plugin, turns on updates, and helps you
    choose the first rules:

    ```
    Set up the AgentLTL plugin for me by following https://raw.githubusercontent.com/AgentLTL/agentltl-claude-code/main/SETUP.md
    ```

    Or install it by hand:

    ```bash
    claude plugin marketplace add https://github.com/AgentLTL/agentltl-claude-code.git
    claude plugin install agentltl@agentltl
    ```

    Then, in Claude Code, run `/reload-plugins` and `/agentltl:setup`.

    The plugin does nothing until there is an `AGENTLTL.yaml`, at a project's root for that
    project, or in `~/.claude/` for every project. Setup writes the first one with you.

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
    project's file works for Claude Code and Copilot CLI alike.

    [More on the Copilot CLI plugin](harnesses/copilot-cli/index.md)

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

The agent sees `why` and `fix` when it is refused. In Claude Code and Copilot CLI you can
also write rules in plain words (`/agentltl:rules never push to main`, or `/agentltl-rules`
in Copilot), and switch on tested ones from the [library](rules/library.md).

Next: [what a rule can say](rules/index.md).
