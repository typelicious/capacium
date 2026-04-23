# Bundle Support

A bundle is a capability that contains multiple sub-capabilities installed together. Bundles are useful for distributing tool suites, skill collections, or multi-component systems.

## Creating a Bundle

Create a `capability.yaml` with `kind: bundle` and a `capabilities` section:

```yaml
kind: bundle
name: dev-toolkit
version: 1.0.0
description: Developer tool suite

capabilities:
  - name: code-reviewer
    source: ./sub-caps/code-reviewer
    version: latest
  - name: linter
    source: ../linter
    version: "1.5.0"
  - name: doc-generator
    source: https://github.com/user/doc-generator.git
```

Each capability entry requires:
- `name` — Unique name within the bundle
- `source` — Path (relative, absolute, or git URL)

Optionally:
- `version` — Version specifier (default: `latest`)

## Installing a Bundle

```bash
cap install dev-toolkit --source .
```

Installation:
1. Parses the bundle manifest
2. Installs each sub-capability from its source
3. Registers all sub-capabilities in the registry
4. Computes a bundle fingerprint from ordered sub-cap fingerprints
5. Records bundle membership in the `bundle_members` table

## Bundle Fingerprint

The bundle fingerprint is a SHA-256 hash computed from the **sorted** fingerprints of all sub-capabilities. This makes the fingerprint order-independent — adding or removing sub-caps changes the fingerprint, but reordering does not.

```python
# Computation logic
import hashlib
hasher = hashlib.sha256()
for fp in sorted(sub_cap_fingerprints):
    hasher.update(fp.encode("utf-8"))
return hasher.hexdigest()
```

## Verification

Bundle verification (`cap verify`) traverses every sub-capability:

1. Verifies each sub-capability's fingerprint independently
2. Recomputes the bundle fingerprint from sub-cap fingerprints
3. Compares against the stored bundle fingerprint

```bash
cap verify dev-toolkit
cap verify --all
```

## Reference Counting

The registry tracks bundle membership via reference counts. A sub-capability cannot be removed if it belongs to any active bundle:

```bash
cap remove linter
# Error: capability is referenced by bundle(s)
cap remove dev-toolkit --force
# Removes bundle AND all sub-capabilities
```

Use `--force` to remove a bundle and all its members at once.
