# How AgentLTL works

## Traces

An agent's run is a **trace**: the sequence of tool calls it made, each with its name, its
arguments, and (once it ran) its result.

```
1. Read        {file_path: "src/app.py"}
2. Edit        {file_path: "src/app.py", ...}
3. pytest      {paths: ["tests"]}
4. git_commit  {message: ["fix"], all: true}
5. git_push    {remote: "origin", refspecs: ["main"]}
```

A *procedure* is a property of that sequence, not of any single call: "the tests ran after
the last edit and before the push" is true or false of the whole trace, and only the order
of calls 2, 3 and 5 decides it.

## Constraints are temporal formulas

In practice: a constraint is a rule about the *order* of calls and the *values* in them,
checked against everything the agent has done so far. Under the hood, AgentLTL writes
procedures in **first-order linear temporal logic** (FOLTL) over traces. Linear temporal
logic talks about order ("always", "eventually", "before", "next"); first-order adds
quantifiers over the *values* in the calls ("for every file that was read…"). You don't
need the theory to write rules: the table shows what the formulas express.

| Procedure | Formula |
|---|---|
| Fetch before processing | `Before("fetch_data", "process_data")` |
| Deploy at most once | `CalledNTimes("deploy", 1, "<=")` |
| Never call a forbidden tool | `Not(Called("drop_database"))` |
| Every file written was read first | `ForAll(f ∈ written files, Before(Read(f), Write(f)))` |
| Prod only gets what staging ran | `∀c, v: helm_upgrade(c, v, prod) → earlier helm_upgrade(c, v, staging)` |

You rarely write formulas by hand. In the Python library you compose them from operators
(`Before`, `CalledWith`, `ForAll`, `Globally`…, see the
[formula reference](../python/index.md#foltl-formula-reference)). In a coding-agent harness
you write [rules in YAML](../rules/index.md) (`never`, `before`, `require`, `at_most`), and
they compile to these formulas.

## One specification, three uses

The same constraints serve three purposes:

<div class="grid cards" markdown>

-   **Measure**: after a run, `verify_trace` checks each constraint on the finished trace
    and gives a compliance score, `C = 1 − Σ(violated weights) / Σ(all weights)`.

-   **Enforce**: during a run, each tool call is checked *before it executes*, against the
    trace so far plus that call. A call that would break a constraint is refused.
    [More](enforcement.md).

-   **Train**: the compliance score is a reward signal for fine-tuning agents to follow
    procedures, with no separate grader.

</div>

## What a check sees

A constraint is checked on what the agent actually did, as data: tool names, arguments,
results, order. That is what makes it precise ("the *same* chart and version"), and also
its limit: it does not read the agent's reasoning, and in a coding agent it sees commands,
not what the programs they run do inside. A rule about `pytest` doesn't see the `pytest`
that `make test` runs, unless the rule names `make test` too.

For coding agents, which act through a single shell tool, one command line is many calls.
AgentLTL splits it first: see [shell commands as tool calls](shell.md).
