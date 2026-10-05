# Rules that connect calls

A per-call checker can say "never run `terraform apply`". It can't say "apply only the plan
that was reviewed": that depends on an earlier call, and on what its arguments were.
AgentLTL can. A `$variable` in a `before` rule must take the same value in both calls.

## Promote only what staging ran

```yaml
- id: promote-what-staging-ran
  before:
    first: {tool: helm_upgrade, with: {chart: $chart, version: $v, namespace: staging}}
    then:  {tool: helm_upgrade, with: {chart: $chart, version: $v, namespace: prod}}
  scope: project       # the staging deploy may have been yesterday, in another session
```

Staging on 1.5.2 doesn't let 1.6.0 into prod, and neither does another chart on 1.6.0: the
two variables must match *together*. Under the hood this is: for every chart `c` and version
`v`, every `helm_upgrade(c, v, prod)` comes after a `helm_upgrade(c, v, staging)`.

## Apply exactly the reviewed plan

```yaml
- id: apply-the-reviewed-plan
  before:
    first: {tool: terraform_plan, with: {out: $plan}}
    then:  {tool: terraform_apply, with: {plan: $plan}}
- id: apply-a-saved-plan
  require: {tool: terraform_apply, where: {plan: "?*"}}
```

The second rule closes the gap the first leaves: `terraform apply` with no plan file at all
computes a fresh plan on the spot.

## Delete only what the agent wrote

```yaml
- id: delete-only-what-you-wrote
  before:
    first: {tool: Write, with: {file_path: $f}}
    then:  {tool: rm, with: {paths: $f}}
```

```
  Bash  rm scratch.txt README.md
  ✗ Rule 'delete-only-what-you-wrote' blocked this call. Nothing was executed.
    Problem: for f='/repo/README.md': no earlier Write call had file_path='/repo/README.md'.
```

Every value is checked: `rm a b` needs both files to have been written.

## Read before you run

```yaml
- id: read-sql-before-running-it
  before:
    first: {tool: Read, with: {file_path: $f}}
    then:  {tool: psql, with: {file: $f}}
```

Paths are compared in one form: `Read migrations/007.sql` and
`psql -f ./migrations/007.sql` name the same file, and so does
`cd migrations && psql -f 007.sql`.

## Read before you overwrite

```yaml
- id: read-before-overwrite
  before:
    first: {tool: Read, with: {file_path: $f}}
    then:
      - {tool: Write, with: {file_path: $f}, exists: true}
      - {tool: [sed, perl], with: {in_place: true, paths: $f}, exists: true}
      - {tool: "*", with: {overwrite_to: $f}, exists: true}   # echo … > f
```

`exists: true` limits it to files that are already there: creating a new file is fine.
`overwrite_to` covers truncating redirections (`>`), not appending ones (`>>`). This one
is in the [library](library.md#read-before-overwrite).

## More

The [example rule files](examples.md) have deploy, git, research-hygiene and
prompt-injection-tripwire rules, each tested with `agentltl check`.
