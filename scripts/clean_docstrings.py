"""
A griffe extension for the API pages: AgentLTL's docstrings are Google-style with a few
Sphinx habits that read badly in Markdown. This tidies them as they are loaded:

- the ``agentltl/_constraints.py – `` prefix of a module docstring is dropped;
- ``:class:`Trace``` and the other Sphinx roles become plain code, ```Trace```;
- a paragraph ending in ``::`` (a reStructuredText literal block) ends in ``:``.
"""

from __future__ import annotations

import re
from typing import Any

import griffe

_PREFIX = re.compile(r"\A\s*agentltl[\w/.]*\.py\s*(?:–|--|-|—)\s*")
_ROLE = re.compile(r":(?:class|func|meth|mod|attr|data|exc|obj|const):`~?([^`]+)`")
_LITERAL = re.compile(r"(\S)::[ \t]*$", re.M)
_BARE_LITERAL = re.compile(r"^[ \t]*::[ \t]*$\n?", re.M)


def clean(text: str) -> str:
    text = _PREFIX.sub("", text)
    if text[:1].islower():
        text = text[0].upper() + text[1:]
    text = _ROLE.sub(lambda m: f"`{m.group(1).split('.')[-1] if m.group(0).count('~') else m.group(1)}`", text)
    text = _LITERAL.sub(r"\1:", text)
    return _BARE_LITERAL.sub("", text)


class CleanDocstrings(griffe.Extension):
    def on_instance(self, *, obj: griffe.Object, **kwargs: Any) -> None:
        if obj.docstring is not None:
            obj.docstring.value = clean(obj.docstring.value)
