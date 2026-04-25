# Runtimes

Many Capacium capabilities — particularly **`mcp-server`** kinds — shell out to a host
runtime such as `uv`/`uvx`, `node`/`npx`, `python`, `docker`, `go`, `bun` or `deno`.
Before v0.7.0, `cap install` would happily write an MCP config like

```json
{ "command": "uvx", "args": ["mempalace-mcp"] }
```

into Claude Desktop, Claude Code, OpenCode and Codex without ever checking that
`uvx` was actually installed. The MCP client would then silently fail to start
the server, leaving the user staring at "no tools available."

The runtime resolver replaces that failure mode with a pre-flight check, a
diagnostic command, and a single source of truth for which runtimes Capacium
knows about.

## The `runtimes:` manifest field

Declare runtime requirements alongside the rest of `capability.yaml`:

```yaml
kind: mcp-server
name: mempalace-mcp
version: 1.0.0

runtimes:
  uv: ">=0.4.0"      # provides: uv, uvx
  python: ">=3.10"   # provides: python, python3

mcp:
  transport: stdio
  supported_clients: [claude-desktop, claude-code]
  command: uvx
  args: [mempalace-mcp]
```

### Supported requirement syntax

| Form          | Meaning                                          |
|---------------|--------------------------------------------------|
| `"*"`         | Any version (just check that the runtime exists) |
| `">=X[.Y[.Z]]"` | Greater-or-equal lower bound                   |
| `"X.Y.Z"`     | Bare version — treated as `">=X.Y.Z"` (loose)    |

Capacium intentionally implements only the minimal comparator it needs. There
is no dependency on `packaging`, `semver`, or any other PyPI library — the core
stays stdlib-only, per the project's standards.

### Auto-inference for MCP servers

If you omit `runtimes:` and your manifest is an `mcp-server` whose `mcp.command`
is a well-known wrapper, the required runtime is inferred automatically:

| `mcp.command` | Inferred runtime |
|---------------|------------------|
| `uvx`, `uv`   | `uv`             |
| `npx`, `npm`, `node` | `node`     |
| `pipx`        | `pipx`           |
| `python`, `python3` | `python`   |
| `docker`      | `docker`         |
| `go`          | `go`             |
| `bun`, `bunx` | `bun`            |
| `deno`        | `deno`           |

If you declare a runtime explicitly, it always wins over inference — declare
`uv: ">=0.4.0"` if you need a real lower bound rather than the `*` you'd get
from inference.

## Pre-flight check on `cap install`

When you run `cap install`, the resolver probes every required runtime and
fails the install if any are missing or out of date:

```text
$ cap install needs-uv --source ./pkg
Missing or incompatible runtimes:
  - uv: missing (need >=0.4.0) — install: brew install uv
      install: brew install uv
      docs:    https://docs.astral.sh/uv/

Re-run with --skip-runtime-check to bypass this gate.
```

Exit codes follow `agents.md`:

- `0` — install succeeded
- `1` — user error, including missing runtimes (the most common case)
- `2` — system error (I/O, database)

Need to install anyway? Pass `--skip-runtime-check` and Capacium will dispatch
to the adapters without probing first.

## `cap doctor`

`cap doctor` walks the local registry and reports the runtime health of every
installed capability:

```text
$ cap doctor
cap doctor — checking 3 capabilities

[ok] alice/skill-without-runtimes@1.0.0  (no runtime requirements)
[--] alice/mempalace-mcp@1.0.0
     [--] uv         missing         (need >=0.4.0)
          install: brew install uv
[ok] alice/node-mcp@2.0.0
     [ok] node       v20.11.1        (need >=20)

Some runtimes are missing or out of date — see above.
```

Pass an optional capability spec to scope the check: `cap doctor alice/mempalace-mcp`.

Exit code is `0` when everything is green, `1` otherwise — convenient in CI.

## `cap runtimes`

`cap runtimes list` shows every runtime Capacium knows about, whether it's
present, and what the host reports as its version:

```text
$ cap runtimes list
Runtime    Status Version         Provides
------------------------------------------------------------
bun        [ok]   1.3.11          bun, bunx
deno       [--]   -               deno
docker     [ok]   29.3.1          docker
go         [ok]   1.19.2          go
node       [ok]   25.9.0          node, npm, npx
pipx       [--]   -               pipx
python     [ok]   3.14.4          python, python3
uv         [--]   -               uv, uvx
```

`cap runtimes install <name>` prints the install command for the host platform
— it does **not** execute it. Running package managers on the user's behalf is
high-blast-radius behavior we deliberately avoid:

```text
$ cap runtimes install uv
To install uv on darwin, run:

    brew install uv

Capacium does NOT run this for you — copy/paste it yourself.
Docs: https://docs.astral.sh/uv/
```

## Why `runtimes:` and not `dependencies:`?

The existing `dependencies:` field expresses _capability-on-capability_
dependencies (other things you can `cap install`). `runtimes:` expresses
_capability-on-host_ dependencies — things the user has to obtain through their
own package manager. The two concepts have different blast radii, different
trust models, and different resolution strategies, so they live in separate
fields. `dependencies:` is unchanged in v0.7.0.
