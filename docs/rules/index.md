# Writing rules

Coding-agent harnesses read rules from `AGENTLTL.yaml`: at a project's root for that project,
and in the harness's user folder (`~/.claude/AGENTLTL.yaml` for Claude Code,
`~/.copilot/AGENTLTL.yaml` for Copilot CLI, `~/.vibe/AGENTLTL.yaml` for Mistral Vibe,
`~/.codex/AGENTLTL.yaml` for Codex) for every project.

This page is a tour; every key is in the [reference](reference.md).

```yaml title="AGENTLTL.yaml"
use: [no-force-push, protect-env-files]     # tested rules from the library

rules:
  - id: tests-before-push
    before: {first: pytest, then: git_push, since: [Edit, Write]}
    why: CI is slow; run the tests locally first.
    fix: Run pytest, then push.
    mode: warn
```

## The five kinds

Each rule has an `id`, exactly one kind, and usually a `why` (shown to the agent when it is
refused) and a `fix` (what to do instead). The first four judge a call as it is made;
`finally` judges the agent's turn when it ends.

`never`
:   The target is never called.

    ```yaml
    - id: no-force-push
      never: {tool: git_push, with: {force: true}}
    ```

`before`
:   The second target only once the first has been called. With `since`, the first must
    come after the last `since` call: "tests after the last edit".

    ```yaml
    - id: plan-before-apply
      before: {first: terraform_plan, then: terraform_apply}
    ```

`require`
:   When the target's tool is called, its arguments must match.

    ```yaml
    - id: subagents-on-sonnet
      require: {tool: Agent, with: {model: sonnet}}
    ```

`at_most`
:   A cap on matching calls.

    ```yaml
    - id: one-pr-per-session
      at_most: {call: gh_pr_create, times: 1}
    ```

`finally`
:   Before the agent finishes its turn, the target has run (with `since`: after the last
    `since` call). It never refuses a call: the agent is sent back to do what is missing,
    a bounded number of times per turn.

    ```yaml
    - id: tests-before-finishing
      finally: {call: pytest, since: [Edit, Write]}
    ```

For anything else, `ltl:` takes a raw formula (`G(now("deploy") -> X(G(!now("deploy"))))`),
including past-time operators: `Y` (previous call), `O` (once), `H` (always so far), `S`
(since).

Each kind compiles to an AgentLTL formula. `never`, `before`, `require` and `at_most` look
back from the call being made, so they judge that call alone: a rule broken earlier (by an
override) never blocks unrelated later calls.

## Targets

A target names a tool, and optionally narrows it by its arguments:

```yaml
{tool: git_push}                                  # any push
{tool: [Edit, Write], where: {file_path: ".env*"}}  # globs on argument values
{tool: kubectl_delete, with: {namespace: prod}}   # equal values
{tool: "*", where: {"*": "migrations/*"}}         # any tool, any argument
{tool: Write, with: {file_path: $f}, exists: true}  # only paths that already exist
{tool: pytest, succeeded: true}                    # only runs that passed (exit status 0)
```

Tool names are the ones commands [translate to](../shell/commands.md): `git push -f` is
`git_push {force: true}`, `echo x > f` writes `redirect_to: [f]`. The harness's own tools
keep their names (`Edit`, `Write`, `Read`, `WebFetch`, `mcp__…`). To see a command's name and
arguments, translate it:

```console
$ agentltl translate "kubectl -n prod delete pod web-1"
kubectl_delete {"namespace": "prod", "all_namespaces": false, "all": false, "force": false, "resource": "pod", "names": ["web-1"]}
```

## Variables

A `$variable` in a `before` rule must take the *same value* in both calls. That is what
lets a rule connect calls instead of judging each one alone:

```yaml
- id: read-before-overwrite
  before:
    first: {tool: Read, with: {file_path: $f}}
    then:  {tool: [Edit, Write], with: {file_path: $f}, exists: true}
```

More in [rules that connect calls](cookbook.md).

## Modes and memory

`mode` says what happens on a violation: `block` (default), `warn`, `ask`, `retry`, `stop`,
`log` ([what each does](../concepts/enforcement.md#modes-what-happens-on-a-violation)).
`scope: project` makes a rule remember calls from earlier sessions.

## Test before you trust

Replay commands through the rules, with the outcome you expect:

```console
$ agentltl check --add draft.yaml "deny: git push" "allow: pytest" "allow: git push"
 1. DENY  git push  [tests-before-push]  ok
 2. ALLOW pytest  ok
 3. ALLOW git push  ok
```

`check` exits 1 if a step doesn't do what you expected, and prints a `WARNING` for any tool
or argument name nothing produces (a rule that would never fire). In Claude Code,
`/agentltl:rules <rule in plain words>` drafts, tests and shows a rule before saving it
(also in Mistral Vibe; `/agentltl-rules` in Copilot CLI, `$agentltl:rules` in Codex).
