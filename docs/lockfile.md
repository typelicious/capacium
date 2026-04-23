# Lock File System

The lock file (`capability.lock`) pins exact versions and fingerprints of a capability and its dependency tree, ensuring reproducible installations.

## Generating a Lock File

```bash
cap lock my-skill
```

This creates `capability.lock` inside the capability's install directory, recording:
- The capability's own fingerprint at the current state
- The installed version and fingerprint of each dependency

### Refreshing a Lock File

```bash
cap lock my-skill --update
```

## Lock File Format

Lock files are serialized as YAML (preferred) or JSON (fallback if PyYAML is unavailable):

```yaml
name: my-org/my-skill
version: 1.0.0
fingerprint: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
dependencies:
  - name: my-org/helper-cap
    version: 0.5.0
    fingerprint: f1e2d3c4b5a6987...
source: opencode
created_at: "2025-06-01T12:00:00"
```

## Enforcement

During installation, `cap install` checks for an existing lock file:

1. Verifies the capability's current fingerprint matches the lock file
2. Checks each dependency's version matches the locked version
3. Verifies each dependency's fingerprint matches

If any check fails, installation is aborted with an error message.

### Bypassing Lock Enforcement

```bash
cap install my-skill --no-lock
```

## When to Use Lock Files

- **Distribution** — Consumers get pinned, verified dependencies
- **CI/CD** — Ensures consistency across environments
- **Release Artifacts** — Lock files document exact dependency trees

## Lock File Location

Lock files are stored inside the capability's install directory:

```
~/.capacium/cache/my-skill/1.0.0/
├── capability.yaml
├── capability.lock    # ← Lock file
├── prompt.md
└── ...
```
