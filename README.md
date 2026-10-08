# agentltl.github.io

The documentation site for [AgentLTL](https://github.com/AgentLTL): procedural rules for
tool-using LLM agents, the shell parser, and the coding-agent harnesses that enforce them.
Published at **https://agentltl.github.io**.

## How it is put together

- **Explanations** (home, concepts, tutorials, the cookbook, research) are written here, in
  `docs/`.
- **Reference pages** live next to the code they describe and are copied in at build time by
  `scripts/pull.py`, which also generates the rule library, example and supported-commands
  pages from the YAML in those repositories. Those files are gitignored here: edit them in
  their own repository (each page says which).

The site is rebuilt on every push, every night, and on demand from the Actions tab.

## Working on it

```bash
git clone https://github.com/AgentLTL/AgentLTL.github.io
cd AgentLTL.github.io            # with AgentLTL, cli-to-tools, agentltl-coding,
python -m venv .venv             # agentltl-claude-code, agentltl-copilot-cli and
                                 # agentltl-mistral-vibe cloned next to it
.venv/bin/pip install -r requirements.txt ../cli-to-tools
.venv/bin/python scripts/pull.py --from ..
.venv/bin/mkdocs serve           # http://127.0.0.1:8000
```

`mkdocs build --strict` must pass: CI uses it, and it fails on broken links.

Built with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
