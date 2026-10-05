# Shell commands

Rules name the structured calls a command line translates to, not its text. Why, and what
the parser handles: [shell commands as tool calls](../concepts/shell.md).

**Find a command's tool name and arguments**

:   `agentltl translate "<command>"` shows the calls a command line stands for, and
    `agentltl tools 'git_*'` lists tools and their arguments. The
    [supported commands](commands.md) page lists every bundled one.

**Teach it a command**

:   A command without a spec becomes a tool named after the executable, with its words in
    `argv`. To give a rule named options to work with, add a spec under `tools:` in
    `AGENTLTL.yaml`; a spec for a bundled command extends it:

    ```yaml
    tools:
      deploy:
        options: [{flags: [--prod], type: bool}, {flags: [-r, --region]}]
        positionals: [{name: service}]
    ```

    `deploy --prod web` is then `deploy {prod: true, service: web}`. The spec format:
    [cli-to-tools specs](cli-to-tools.md#specs), and
    [when a command needs a spec](../rules/reference.md#when-a-command-needs-a-spec).

**Use the parser in your own harness**

:   [cli-to-tools](cli-to-tools.md) is a standalone Python package:
    `Translator().translate(command)` returns the calls, and `cli_to_tools.agentltl`
    plugs them into AgentLTL's enforcer.
