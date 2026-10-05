# Agents and integrations

[`AgentWithConstraints`][agentltl.agents.AgentWithConstraints] checks every tool call before
it runs, with a smolagents or LangChain backend. The lower-level integrations plug the same
checks into an agent you build yourself.

## Agent wrappers

::: agentltl.agents
    options:
      heading_level: 3

## smolagents

::: agentltl.integrations.smolagents.constrained_agent.ToolCallingAgentWithConstraints
    options:
      show_root_heading: true
      heading_level: 3

## LangChain

::: agentltl.integrations.langchain.constrained_agent.ConstraintEnforcementMiddleware
    options:
      show_root_heading: true
      heading_level: 3
