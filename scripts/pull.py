"""
Pull the reference pages into docs/ from the repositories they document.

Explanations live in this repository; reference material lives next to the code it
describes, so a change and its documentation land in the same commit. This script copies
those pages here, rewrites their links, and generates the pages that are tables of data
(the rule library, the supported commands, the example rule files).

    python scripts/pull.py                 # repositories checked out in _sources/<name>
    python scripts/pull.py --from ..       # or next to this one (local development)

Pulled and generated files are listed in docs/.pulled and are not committed.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

import yaml

ORG = "https://github.com/AgentLTL"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(HERE, "docs")

# (repository, file in it, page here, title to put on top or None to keep the file's own)
PAGES: List[Tuple[str, str, str, Optional[str]]] = [
    ("agentltl-claude-code", "skills/rules/reference.md", "rules/reference.md",
     "AGENTLTL.yaml reference"),
    ("agentltl-claude-code", "docs/REFERENCE.md", "harnesses/claude-code/reference.md",
     "Claude Code: full reference"),
    ("AgentLTL", "README.md", "python/index.md", "The AgentLTL Python library"),
    ("AgentLTL", "docs/reference.md", "python/return-values.md", "Return values"),
    ("cli-to-tools", "README.md", "shell/cli-to-tools.md", "cli-to-tools"),
]

# Where a local checkout of a repository may be called something else.
ALIASES = {"AgentLTL": ["AgentLTL", "AgentLTL-cli"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--from", dest="base", default=os.path.join(HERE, "_sources"),
                        help="the folder holding the repositories (default: _sources/)")
    args = parser.parse_args()
    repos = {name: _find(args.base, name) for name in {p[0] for p in PAGES}}
    missing = [n for n, path in repos.items() if path is None]
    if missing:
        print(f"Not found in {args.base}: {', '.join(missing)}", file=sys.stderr)
        return 1
    _link_sources(repos)
    written: List[str] = []
    targets = {(repo, path): page for repo, path, page, _ in PAGES}
    for repo, path, page, title in PAGES:
        with open(os.path.join(repos[repo], path), encoding="utf-8") as fh:
            text = fh.read()
        text = _links(text, repo, path, page, targets)
        text = text.replace("${CLAUDE_PLUGIN_ROOT}/", f"{ORG}/agentltl-claude-code/blob/main/")
        if title:
            text = re.sub(r"\A\s*# [^\n]*\n", "", text, count=1)
            text = _drop_badges(text)
            text = f"# {title}\n\n" + _source_note(repo, path) + text.lstrip()
        written.append(_write(page, text))
    written.append(_write("rules/library.md", _library(repos["agentltl-claude-code"])))
    written.append(_write("rules/examples.md", _examples(repos["agentltl-claude-code"])))
    written.append(_write("shell/commands.md", _commands(repos["cli-to-tools"])))
    with open(os.path.join(DOCS, ".pulled"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(sorted(written)) + "\n")
    print(f"Pulled {len(written)} page(s) into docs/.")
    return 0


def _link_sources(repos: Dict[str, str]) -> None:
    """Make _sources/<name> point at each repository, as in CI: the API pages read the
    AgentLTL sources from _sources/AgentLTL/src (see mkdocs.yml)."""
    folder = os.path.join(HERE, "_sources")
    os.makedirs(folder, exist_ok=True)
    for name, path in repos.items():
        link = os.path.join(folder, name)
        if not os.path.exists(link) and not os.path.islink(link):
            os.symlink(os.path.abspath(path), link)


def _find(base: str, name: str) -> Optional[str]:
    for candidate in ALIASES.get(name, [name]):
        path = os.path.join(base, candidate)
        if os.path.isdir(path):
            return path
    return None


def _write(page: str, text: str) -> str:
    path = os.path.join(DOCS, page)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.rstrip() + "\n")
    return page


def _source_note(repo: str, path: str) -> str:
    url = f"{ORG}/{repo}/blob/main/{path}"
    return (f'!!! info "This page comes from [`{repo}/{path}`]({url})"\n'
            "    It is kept with the code it documents. Edit it there.\n\n")


def _drop_badges(text: str) -> str:
    """Without the badges, and without the README's pointer to this site."""
    text = re.sub(r"\A(?:\s*\[!\[[^\n]*\n)+", "", text)
    return re.sub(r"^📖 \*\*Documentation:.*?(?:\n\n|\Z)", "", text, flags=re.M | re.S)


_LINK = re.compile(r"(\]\()([^)\s]+)(\))")


def _links(text: str, repo: str, path: str, page: str, targets: Dict[Tuple[str, str], str]) -> str:
    """Relative links: to a page pulled here, the page; to anything else, GitHub."""
    def fix(m: "re.Match[str]") -> str:
        target = m.group(2)
        if re.match(r"[a-z]+:|#|/", target):
            return m.group(0)
        file, _, anchor = target.partition("#")
        resolved = os.path.normpath(os.path.join(os.path.dirname(path), file))
        anchor = f"#{anchor}" if anchor else ""
        if (repo, resolved) in targets:
            rel = os.path.relpath(targets[(repo, resolved)], os.path.dirname(page))
            return f"{m.group(1)}{rel}{anchor}{m.group(3)}"
        kind = "tree" if not os.path.splitext(resolved)[1] else "blob"
        return f"{m.group(1)}{ORG}/{repo}/{kind}/main/{resolved}{anchor}{m.group(3)}"
    return _LINK.sub(fix, text)


# ── generated pages ───────────────────────────────────────────────────────────

def _library(plugin: str) -> str:
    folder = os.path.join(plugin, "library")
    entries = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".yaml"):
            with open(os.path.join(folder, name), encoding="utf-8") as fh:
                entries.append((name[:-5], yaml.safe_load(fh) or {}))
    bundles = [e for e in entries if e[1].get("include")]
    singles = [e for e in entries if not e[1].get("include")]
    out = ["# The rule library", "",
           _source_note("agentltl-claude-code", "library/").replace("This page comes from",
                                                                    "Generated from"),
           "Tested rules you switch on by name, instead of writing them. In a rule file:", "",
           "```yaml", "use:", "  - no-force-push", "  - {tests-before-push: {mode: warn}}",
           "```", "",
           "In Claude Code, `/agentltl:setup` lets you tick them. Each entry's rules get fixes "
           "with plugin updates; a rule of your own with the same id replaces the packaged one.",
           "", "| Entry | What it does | Mode | Tags |", "|---|---|---|---|"]
    for name, e in singles:
        modes = sorted({r.get("mode", "block") for r in e.get("rules") or []})
        out.append(f"| [`{name}`](#{name}) | {e.get('summary', '')} | {', '.join(modes)} | "
                   f"{', '.join(e.get('tags') or [])} |")
    if bundles:
        out += ["", "## Bundles", "", "| Bundle | Switches on |", "|---|---|"]
        for name, e in bundles:
            out.append(f"| `{name}` | {', '.join(f'`{i}`' for i in e['include'])} |")
    out += ["", "## The rules in full", ""]
    for name, e in singles:
        body = {k: v for k, v in e.items() if k in ("rules", "tools")}
        out += [f"### {name}", "", e.get("summary", ""), "", "```yaml",
                yaml.safe_dump(body, sort_keys=False, allow_unicode=True, width=96).rstrip(),
                "```", ""]
    return "\n".join(out)


def _examples(plugin: str) -> str:
    out = ["# Example rule files", "",
           _source_note("agentltl-claude-code", "examples/").replace("This page comes from",
                                                                     "Generated from")]
    for name in ("showcase.yaml", "creative.yaml", "AGENTLTL.yaml"):
        path = os.path.join(plugin, "examples", name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        intro = next((line.lstrip("# ").strip() for line in text.splitlines()
                      if line.startswith("#") and len(line) > 3), "")
        out += [f"## {name}", "", intro, "", "```yaml", text.rstrip(), "```", ""]
    return "\n".join(out)


PACK_TITLES = {"shell": "Shell and coreutils", "files": "Other file writers", "git": "Git",
               "docker": "Docker and Compose", "python": "Python", "network": "Network",
               "cloud": "Cloud and infrastructure", "secrets": "Secrets and credentials"}


def _commands(c2t: str) -> str:
    """Every bundled spec, by pack: the tools it produces and their arguments, as
    cli-to-tools itself reports them."""
    sys.path.insert(0, os.path.join(c2t, "src"))
    from cli_to_tools import SpecRegistry
    from cli_to_tools._spec import available_packs

    out = ["# Supported commands", "",
           _source_note("cli-to-tools", "src/cli_to_tools/packs/").replace(
               "This page comes from", "Generated from"),
           "Each command below is parsed into a tool named after it and its subcommand, with "
           "named arguments: `git push -f origin main` is `git_push {force: true, remote: "
           "origin, refspecs: [main]}`. Rules name these tools and arguments.", "",
           "Any other command is still checked, as a tool named after the executable with its "
           "words in `argv`. A rule file can add specs for more commands, or more options of "
           "these (`tools:` in [AGENTLTL.yaml](../rules/reference.md)).", ""]
    for pack in available_packs():
        registry = SpecRegistry(packs=[pack])
        by_spec: Dict[int, Tuple[object, List[str]]] = {}
        for exe, spec in registry._specs.items():
            by_spec.setdefault(id(spec), (spec, []))[1].append(exe)
        out += [f"## {PACK_TITLES.get(pack, pack)} (`{pack}`)", ""]
        for spec, names in by_spec.values():
            schemas = spec.tool_schemas()
            title = " / ".join(f"`{n}`" for n in names)
            out += [f'??? note "{title}: {len(schemas)} tool{"s" if len(schemas) != 1 else ""}"',
                    "", "    | Tool | Arguments |", "    |---|---|"]
            for schema in schemas:
                props = schema.get("parameters", {}).get("properties", {})
                args = ", ".join(f"`{k}`" for k in props) or "—"
                out.append(f"    | `{schema['name']}` | {args} |")
            out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
