# Manifest Format

The `capability.yaml` file is the heart of every Capacium package. It describes metadata, dependencies, framework targets, and (for bundles) sub-capabilities.

## Basic Structure

```yaml
kind: skill                     # Required: capability kind
name: my-skill                  # Required: kebab-case name
version: 1.0.0                  # Required: semver MAJOR.MINOR.PATCH
description: Does something     # Optional
author: Your Name               # Optional
license: Apache-2.0             # Optional
owner: your-org                 # Optional (default: "global")
repository: https://...         # Optional
homepage: https://...           # Optional
keywords:                       # Optional
  - code-review
  - automation

frameworks:                     # Optional (default: agnostic)
  - opencode
  - claude-code

dependencies:                   # Optional (version ranges)
  helper-cap: "^0.5.0"
  lint-tool: ">=1.0.0"
```

## Capability Kinds

| Kind | Description | Example Use |
|------|-------------|-------------|
| `skill` | Agent skill/prompt | Code review, documentation gen |
| `bundle` | Collection of sub-capabilities | Toolkits, skill suites |
| `tool` | Function/tool definition | Web search, calculator |
| `prompt` | Reusable prompt template | System prompts, instructions |
| `template` | Project/code template | Skill scaffolds, adapter templates |
| `workflow` | Multi-step agent workflow | CI pipelines, data chains |

## Bundle Manifests

Bundle manifests include a `capabilities` section listing sub-capabilities:

```yaml
kind: bundle
name: dev-toolkit
version: 2.0.0
description: Developer tool suite

capabilities:
  - name: code-reviewer
    source: ./sub-caps/code-reviewer
    version: latest
  - name: lint-helper
    source: ../lint-helper
    version: "1.5.0"
  - name: doc-gen
    source: https://github.com/user/doc-gen.git
```

Validation rules:
- At least one entry in `capabilities`
- Each entry must have `name` and `source`
- Source can be relative path, absolute path, or git URL

## Dependency Version Ranges

Dependencies use semver-compatible range notation:

| Pattern | Meaning |
|---------|---------|
| `"1.2.3"` | Exact version |
| `"^1.2.0"` | Compatible with 1.x |
| `">=1.0.0"` | Minimum version |
| `">=1.0.0, <2.0.0"` | Range |
| `"*"` | Any version |

## File Detection

Capacium discovers manifests in this priority order in a directory:

1. `capability.yaml`
2. `capability.yml`
3. `capability.json`
4. `.skillpkg.json` (legacy)

If none found, it creates a default manifest using the directory name and auto-detected version.
