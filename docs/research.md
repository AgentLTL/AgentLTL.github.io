# Research

AgentLTL is a language derived from first-order linear temporal logic for expressing
procedural rules over agent traces. The same specification can:

- **measure** procedural compliance on completed traces, separately from task correctness;
- **enforce** it at run time, by gating each tool call before it executes;
- **train** for it, as a reward signal for fine-tuning.

> **AgentLTL: A Trace-Verification Framework for Measuring, Enforcing, and Training
> Procedural Compliance in Tool-Using LLM Agents**  
> Laïla Elkoussy, Julien Perez. [arXiv:2607.02599](https://arxiv.org/abs/2607.02599), 2026.

```bibtex
@misc{elkoussy2026agentltl,
  title         = {AgentLTL: A Trace-Verification Framework for Measuring, Enforcing, and Training Procedural Compliance in Tool-Using LLM Agents},
  author        = {Elkoussy, La{\"\i}la and Perez, Julien},
  year          = {2026},
  eprint        = {2607.02599},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SE},
  url           = {https://arxiv.org/abs/2607.02599}
}
```

## Repositories

| Repository | What it is |
|---|---|
| [AgentLTL](https://github.com/AgentLTL/AgentLTL) | The formula engine, post-hoc verification, and run-time enforcement for smolagents or any agent loop |
| [cli-to-tools](https://github.com/AgentLTL/cli-to-tools) | Shell command lines → ordered, structured tool calls |
| [agentltl-claude-code](https://github.com/AgentLTL/agentltl-claude-code) | The Claude Code harness |
| [AgentLTL.github.io](https://github.com/AgentLTL/AgentLTL.github.io) | This site |

## Contact

Laïla Elkoussy · [laila.elkoussy@epita.fr](mailto:laila.elkoussy@epita.fr)
