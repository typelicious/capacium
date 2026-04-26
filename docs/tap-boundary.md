# Homebrew Tap Repository Boundary — `Capacium/homebrew-tap`

## Naming
- Repository: `Capacium/homebrew-tap` (not `homebrew-capacium`)
- Install command: `brew install capacium/tap/capacium`
- Formula files: `Formula/capacium.rb`, `Formula/envctl.rb`

## Belongs
- Homebrew Formula for `capacium` core CLI
- Homebrew Formula for related tools (e.g., `envctl`)
- Formula updates that track core releases (must stay in sync with `Capacium/capacium` tags)
- Formula tests (brew test) verifying the CLI installs and runs

## Does NOT Belong
- Any Python source code
- Exchange models, domain logic, or CRUD
- Crawler pipeline code
- Bridge/WordPress PHP code
- Core CLI source code (Formula references PyPI or GitHub releases; does not vendor source)
- Manifest parsing, fingerprinting, versioning logic
- Configuration management for `~/.capacium/`

## Dependency Direction
```
Tap → Core      (Tap distributes Core binaries; no code-level dependency)
Core → Tap      (FORBIDDEN — Core must never reference the Tap)
Exchange → Tap  (FORBIDDEN — Exchange must never reference the Tap)
```
**The Tap is a distribution channel only. It contains no application logic.**

## Allowed Dependencies
- Ruby (Homebrew DSL)
- Formula inherits from `Homebrew::Formula`
- No external gems beyond what Homebrew provides

## What "Runs Here"
- `brew install capacium/tap/capacium` — installs the latest core CLI
- `brew upgrade capacium/tap/capacium` — upgrades to the latest published version
- Formula audit and test runs in CI

## Version Policy
- The Tap formula MUST be updated with each core release.
- Formula version = core release tag (e.g., `v0.7.3`).
- A lagging formula is a bug.
