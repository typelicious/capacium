# Core Repository Boundary — `Capacium/capacium`

## Belongs
- CLI entry point (`cap <subcommand>`)
- Manifest parsing (`capability.yaml` validation)
- Packaging primitives: fingerprinting (SHA-256), versioning (semver)
- Local verification: symlink lifecycle, registry DB operations
- Lock file system: generation, enforcement, pinning
- Runtime detection: resolvers for uv, node, python, docker, pipx, go, bun, deno
- Config management: `~/.capacium/` read/write
- Adapter framework: install/remove hooks for opencode, claude-code, gemini-cli
- Doctor command: per-capability runtime health
- `cap runtimes list / install` (print-only; never executes package managers)

## Does NOT Belong
- Exchange domain models: `TrustState`, `Listing`, `Publisher`, `Taxonomy`
- Exchange CRUD, search engine, collections
- Crawler logic: fetch pipeline, normalizer, classifier, dedup, claim prep
- Webhook handlers
- Bridge adapters for WordPress/Voxel
- Exchange API client (the HTTP-speaking side)
- Marketplace UI or any frontend rendering
- Homebrew Formula definitions

## Dependency Direction
```
Core ← Exchange  (Exchange may import from Core)
Core ← Crawler   (Crawler may import from Core)
Core ← Bridge    (Bridge makes HTTP calls to Exchange, never imports Core Python)
Core ← Tap       (Tap distributes Core; no reverse dependency)
```
**Core must NOT import from Exchange, Crawler, Bridge, or Tap.**

## Allowed Dependencies
- Python 3.10+ stdlib only (no FastAPI, SQLAlchemy, psycopg2, etc.)
- Third-party packages are **not** permitted in core

## What "Runs Here"
- Everything invoked via `cap <subcommand>` that operates on the local machine
- Everything that reads or writes `~/.capacium/` (config, cache, active, registry.db)
- Manifest and lock file validation
