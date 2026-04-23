# Framework Adapters

Adapters bridge Capacium's package format to specific AI agent frameworks. Each adapter knows how to install, remove, and query capabilities in its target framework's environment.

## Available Adapters

| Adapter | Framework | Install Target |
|---------|-----------|----------------|
| OpenCode | OpenCode CLI | `~/.opencode/skills/` |
| Claude Code | Claude Code CLI | `~/.claude/skills/` |
| Gemini CLI | Google Gemini CLI | `~/.gemini/capabilities/` |
| Cursor | Cursor Editor | `.cursor/rules/` (project) or `~/.cursor/rules/` (global) |
| Continue Dev | Continue.dev | `~/.continue/config.json` providers |

## Auto-Selection

When installing, Capacium reads the `frameworks` field from the manifest and selects the appropriate adapter:

```yaml
# capability.yaml
frameworks:
  - opencode
  - claude-code
```

If the `frameworks` list is empty or null, the OpenCode adapter is used by default.

## Custom Adapters

You can register custom adapters programmatically:

```python
from capacium.adapters import register_adapter
from capacium.adapters.base import FrameworkAdapter

class MyAdapter(FrameworkAdapter):
    def install_capability(self, cap_name, version, source_dir, owner="global"):
        # Custom install logic
        return True

    def remove_capability(self, cap_name, owner="global"):
        return True

    def capability_exists(self, cap_name):
        return False

register_adapter("my-framework", MyAdapter)
```

## Adapter API

Every adapter implements the `FrameworkAdapter` ABC:

| Method | Description |
|--------|-------------|
| `install_capability(name, version, source, owner)` | Copy to storage, create symlink/registration |
| `remove_capability(name, owner)` | Remove symlink/registration |
| `capability_exists(name)` | Check if installed in target framework |

Some adapters (Cursor, Continue) also implement:
- `list_capabilities()` — List all installed capabilities
- `get_capability_metadata(name)` — Get metadata for a capability
