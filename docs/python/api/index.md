# API reference

Generated from the docstrings of [`agentltl`](https://github.com/AgentLTL/AgentLTL)
(`src/agentltl`), at every site build. Everything on these pages is importable from the
module named in its section; the most used names are re-exported from `agentltl` itself
(`from agentltl import Before, Constraint, verify_trace`).

| Page | Module | What's there |
|---|---|---|
| [Formulas](formulas.md) | `agentltl` | The formula nodes (atoms, temporal operators, connectives, quantifiers) and `parse` |
| [Traces and verification](verification.md) | `agentltl` | `Trace`, `ToolCall`, `Constraint`, `verify_trace`, `LTLEvaluator` |
| [Enforcement](enforcement.md) | `agentltl.enforcement`, `agentltl.runtime_safety` | Severities, soft-block modes, violations, runtime-safety classification |
| [Agents and integrations](agents.md) | `agentltl.agents`, `agentltl.integrations` | `AgentWithConstraints` and the smolagents / LangChain integrations |
| [Trace-relative predicates](predicates.md) | `agentltl.matching`, `agentltl.relative` | Argument matching, and predicates whose expected value comes from the trace |
| [Open predicates](translation.md) | `agentltl.translation` | Boolean expressions over a closed grammar, and the template library |

For the shape of the dicts the API returns, see [return values](../return-values.md).
