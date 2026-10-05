# Shell commands as tool calls

Coding agents do most of their work through one tool: a shell. To a call-by-call checker,
`Bash {command: "git commit -am x && git push -f"}` is a single opaque string. A rule about
force-pushing would have to pattern-match text, and `git -C . push --force`, `git push -f`
and `cd repo && git push origin +main` all look different.

AgentLTL's harnesses first split each command line into the **structured calls** it stands
for, with [cli-to-tools](../shell/cli-to-tools.md):

```
git commit -am x && git push -f
  → git_commit {message: ["x"], all: true}
  → git_push   {force: true}
```

Rules then name tools and arguments, not text: `never: {tool: git_push, with: {force:
true}}` catches every spelling, and nothing else.

## What the parser handles

- **Control flow:** `;`, `&&`, `||` and pipes, in execution order. Calls after `&&` or `||`
  are marked *conditional*; a pipeline's parts run together.
- **Substitutions:** `$(cat VERSION)` runs before the command that uses it, and is checked
  as its own call.
- **Wrappers:** `sudo`, `env`, `nice`, `timeout`, `xargs`, `bash -c "…"`, `find -exec …`
  are unwrapped: the command inside is checked.
- **Writes:** redirections become arguments: `echo x > .env` is `echo {redirect_to:
  [".env"], overwrite_to: [".env"]}`. Sending output to `/dev/null` is not a write.
- **Paths:** relative paths are made absolute, following `cd` within the command line
  (`cd sub && rm a` removes `sub/a`). A `cd` ends with its subshell.
- **Options anywhere:** `kubectl -n prod delete pod x` and `kubectl delete pod x -n prod`
  give the same call.

## Fail closed

What can't be known before the command runs is never treated as harmless:

- **Unknown files:** `xargs rm`, `find -exec rm {}`, `rm $F` and a `cd $D` before a relative
  path make the call's file arguments *unknown*. A rule about files treats them as a
  possible match, so `ls | xargs rm` is refused by a rule protecting `migrations/`.
- **Unanalysable commands:** `eval`, a command named by a variable (`$CMD args`) and
  background jobs (`cmd &`) can't be split. The harness asks the human, or, in an
  unattended mode, lets them through and tells the agent they were not checked.

## Commands without a spec

[94 commands](../shell/commands.md) are understood out of the box: git, docker, kubectl, helm,
terraform, cloud CLIs, secret stores, package managers, coreutils. Any other command is
still checked, as a tool named after the executable with its words in `argv`. A rule file
can add a spec for it under `tools:`, or extend a bundled one. See
[when a command needs a spec](../rules/reference.md#when-a-command-needs-a-spec).
