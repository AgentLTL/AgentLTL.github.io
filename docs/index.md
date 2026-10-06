---
hide: [navigation, toc]
---

# AgentLTL

<div class="hero" markdown>

**A rulebook for AI coding agents, enforced on every tool call.**

You write rules in a YAML file (*never force-push*, *run the tests before pushing*,
*deploy to prod only what staging ran*). AgentLTL checks each command the agent is about to
run against them, and refuses the ones that break a rule, **before they run**.

An agent's instructions are only advice: it can lose them after a long context, inside a
subagent, or under pressure to finish. A rule in AgentLTL is checked every time.

Works with Claude Code and GitHub Copilot CLI, and as a Python library for your own
agents. Needs Python 3.10+ and git.

[Get started](get-started.md){ .md-button .md-button--primary }
[How it works](concepts/index.md){ .md-button }
[Running it for a team](harnesses/operating.md){ .md-button }

</div>

```
> ship 1.6.0 to prod

  Bash  helm upgrade web repo/web --version 1.6.0 -n prod
  ✗ Rule 'promote-what-staging-ran' blocked this call. Nothing was executed.
    Problem: for chart='repo/web', v='1.6.0': no earlier helm_upgrade call had
             namespace='staging', chart='repo/web', version='1.6.0'.

  Bash  helm upgrade web repo/web --version 1.6.0 -n staging    ✓
  Bash  curl -fsS https://staging.example.com/health            ✓
  Bash  helm upgrade web repo/web --version 1.6.0 -n prod       ✓
```

One rule did that:

```yaml
- id: promote-what-staging-ran
  before:
    first: {tool: helm_upgrade, with: {chart: $chart, version: $v, namespace: staging}}
    then:  {tool: helm_upgrade, with: {chart: $chart, version: $v, namespace: prod}}
  scope: project       # the staging deploy may have been yesterday, in another session
```

A command filter can only allow or forbid `helm upgrade`. This rule knows the **order** of
calls (prod after staging), ties **values across calls** (the same chart and version), keeps
**memory across sessions**, and reads **the real command line** (`-n prod` is the namespace
wherever it appears).

<div class="grid cards" markdown>

-   :material-shield-check-outline: **Enforced, not advised**

    ---

    A call that breaks a rule is refused before it runs, with the reason and the way to
    comply. Six modes, from "just log it" to "ask the human" to "stop the agent".

    [Enforcement](concepts/enforcement.md)

-   :material-timeline-clock-outline: **Rules over the whole trace**

    ---

    Order, counts, and `$variables` that tie calls together: apply only the plan that was
    reviewed, delete only the files the agent wrote.

    [Rules that connect calls](rules/cookbook.md)

-   :material-console: **Real shell parsing**

    ---

    `git commit -am x && git push -f` is checked as `git_commit` then
    `git_push {force: true}`. Dozens of common commands understood out of the box.

    [Shell commands](concepts/shell.md)

-   :material-puzzle-outline: **For your coding agent**

    ---

    Plugins for Claude Code and GitHub Copilot CLI, sharing one rule file, a rule library,
    plain-language rule writing, and an importer for what your agent's instructions already
    say. More harnesses to come.

    [Harnesses](harnesses/index.md)

-   :material-language-python: **A Python library**

    ---

    The same formulas score finished traces, gate smolagents agents or any agent loop at run
    time, or serve as a reward signal.

    [Python library](python/index.md)

-   :material-school-outline: **Research**

    ---

    The paper behind it: how AgentLTL measures, enforces and trains procedural compliance
    in tool-using agents.

    [The paper](research.md)

</div>
