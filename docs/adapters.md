# Framework Adapters

Adapters bridge Capacium's package format to specific AI agent frameworks and
MCP clients. Each adapter knows how to install, remove, and query capabilities
in its target environment — usually by symlinking a skill into a known
directory or by patching the client's MCP-server configuration file.

## Implementation status (gap matrix)

Capacium ships **28 registered adapters**, but they are not all equal in
capability. The table below records which adapters fully patch a real client
config end-to-end, which work with caveats, and which intentionally print
guidance only because the target client has no local config to patch.

Updated for **v0.7.3** (2026-04-26). When you add or upgrade an adapter,
update this table in the same PR.

### Legend

- ✅ **Full** — installs and patches a real client config in place. Verified
  config path. Both `install` and `remove` are idempotent and safe.
- 🟨 **Partial** — does real work, but with a documented caveat (sidecar
  config, speculative path, missing skill or MCP path, or by-design export).
- ⛔ **Stub** — prints guidance only. The client has no local config Capacium
  can patch, so the adapter exists for completeness but writes nothing.
- — **n/a** — not applicable. Most MCP-only clients don't have a "skill"
  concept; this is by design and not a gap.

### Tier 1 — Development & Engineering

| Adapter ID         | Status | Skill | MCP | Config target |
|--------------------|:------:|:-----:|:---:|---|
| `opencode`         | ✅ | ✅ symlink | ✅ JSON | `~/.opencode/skills/`, `~/.config/opencode/opencode.json` (`mcp` section) |
| `opencode-command` | 🟨 | ✅ commands | — | `~/.opencode/commands/` (skill-only by design — Opencode commands cannot act as MCP servers) |
| `claude-code`      | ✅ | ✅ symlink | ✅ JSON | `~/.claude/skills/`, claude-code MCP config |
| `claude-desktop`   | ✅ | n/a | ✅ JSON | `~/Library/Application Support/Claude/claude_desktop_config.json` (cross-platform paths handled) |
| `gemini-cli`       | ✅ | ✅ symlink | ✅ JSON | `~/.gemini/...` |
| `codex`            | ✅ | n/a | ✅ **TOML** | `~/.codex/config.toml` (only TOML adapter) |
| `windsurf`         | ✅ | n/a | ✅ JSON | `~/.codeium/windsurf/mcp_config.json` |
| `cline`            | ✅ | n/a | ✅ JSON | `~/.vscode/extensions/saoudrizwan.claude-dev/mcp_servers.json` |
| `zed`              | ✅ | n/a | ✅ JSON | `~/.config/zed/settings.json` (`context_servers` section) |
| `sourcegraph-cody` | ✅ | n/a | ✅ JSON | `~/.cody/mcp.json` |
| `antigravity`      | ✅ | n/a | ✅ JSON | `~/.gemini/antigravity/mcp_config.json` |
| `continue-dev`     | ✅ | ✅ providers | ✅ JSON | `~/.continue/config.json` (`contextProviders` + `mcpServers` coexist) |
| `cursor`           | ✅ | ✅ rules | ✅ JSON | `.cursor/rules/<name>.mdc` + `.cursor/mcp.json` (project-local preferred, global fallback) |

### Tier 2 — Specialized / Workflow

| Adapter ID          | Status | Skill | MCP | Config target |
|---------------------|:------:|:-----:|:---:|---|
| `librechat`         | 🟨 | n/a | ✅ JSON | Patches a **sidecar** `~/.librechat/mcp_servers.json` rather than the actual `~/librechat/librechat.yaml` LibreChat reads. Relies on Docker compose injection that isn't shipped here. |
| `chainlit`          | ✅ | n/a | ✅ JSON | `~/.chainlit/mcp_config.json` |
| `cherry-studio`     | ✅ | n/a | ✅ JSON | `~/.cherry-studio/mcp_servers.json` |
| `nextchat`          | ✅ | n/a | ✅ JSON | `~/.nextchat/mcp_config.json` |
| `desktop-commander` | ✅ | n/a | ✅ JSON | `~/.commander/mcp.json` |
| `notebooklm`        | ⛔ | n/a | ⛔ stub | NotebookLM is cloud-only; no local config to patch. Adapter prints the manual server entry the user must paste into the cloud UI. |
| `lutra`             | ⛔ | n/a | ⛔ stub | Lutra AI is cloud-primary. Adapter prints the manual server entry. |
| `serge`             | ⛔ | n/a | ⛔ stub | Serge has no documented MCP integration yet. Adapter prints the manual server entry. |
| `mcp-remote`        | ⛔ | n/a | ⛔ stub | Not a client — `mcp-remote` is a relay tool. Adapter prints `npx mcp-remote <url>` for the user to run. |

### Tier 3 — Extended Skill Clients

| Adapter ID  | Status | Skill | MCP | Config target |
|-------------|:------:|:-----:|:---:|---|
| `roo-code`  | ✅ | n/a | ✅ JSON | `~/.roo-code/mcp.json` |
| `goose`     | ✅ | n/a | ✅ **YAML** in-place (PyYAML opt-dep, JSON fallback) | `~/.config/goose/config.yaml` |
| `aider`     | ✅ | n/a | ✅ **YAML** in-place (PyYAML opt-dep, manual fallback) | `~/.aider.conf.yml` |
| `openclaw`  | 🟨 | n/a | ✅ JSON | Implementation is real (JSON patcher) but the config path `~/.openclaw/mcp_config.json` is **speculative** — OpenClaw has not standardized its config format yet. The adapter's own comment admits this is "subject to change." |

### Tier 4 — Agent Flow Bridges

| Adapter ID  | Status | Skill | MCP | Behavior |
|-------------|:------:|:-----:|:---:|---|
| `langchain` | 🟨 | ✅ export | ✅ export | Doesn't patch any client config (LangChain has no central one). Exports a JSON tool definition to `~/.capacium/langchain-exports/<name>.json` for import into a LangChain agent. By-design export rather than in-place patch. |
| `flowise`   | 🟨 | ✅ export | ✅ export | Same shape as `langchain` — exports a JSON node-definition Flowise/Langflow can import. |

### Summary

| Status | Count | Adapters |
|---|---|---|
| ✅ Full     | **20** | opencode, claude-code, claude-desktop, gemini-cli, codex, windsurf, cline, zed, sourcegraph-cody, antigravity, continue-dev, cursor, chainlit, cherry-studio, nextchat, desktop-commander, roo-code, goose, aider |
| 🟨 Partial  | **5**  | opencode-command, librechat, openclaw, langchain, flowise |
| ⛔ Stub     | **4**  | notebooklm, lutra, serge, mcp-remote |
| **Total**   | **28** | (matches `list_registered_adapters()`) |

The four stubs all live in `src/capacium/adapters/stub_adapters.py` so they are
self-evidently grouped. `cursor` and `continue-dev` were promoted from
**partial → full** in v0.7.1 by closing their MCP gaps.

## Auto-selection

`cap install` reads the `frameworks` field from the manifest and dispatches to
all matching adapters:

```yaml
# capability.yaml
frameworks:
  - opencode
  - claude-code
```

If the `frameworks` list is empty or `null`, the OpenCode adapter is used by
default.

## Custom adapters

```python
from capacium.adapters import register_adapter
from capacium.adapters.base import FrameworkAdapter

class MyAdapter(FrameworkAdapter):
    def install_skill(self, cap_name, version, source_dir, owner="global"):
        ...
        return True

    def remove_skill(self, cap_name, owner="global"):
        return True

    def install_mcp_server(self, cap_name, version, source_dir, owner="global"):
        ...
        return True

    def remove_mcp_server(self, cap_name, owner="global"):
        return True

    def capability_exists(self, cap_name):
        return False

register_adapter("my-framework", MyAdapter)
```

## Adapter API

Every adapter implements the `FrameworkAdapter` ABC. The base class dispatches
`install_capability` / `remove_capability` to either the skill or MCP path
based on the manifest's `kind`:

| Method | When called | Returns |
|---|---|---|
| `install_skill(name, version, source, owner)` | `kind: skill` etc. | `True` on success |
| `remove_skill(name, owner)` | `cap remove` for skills | `True` on success |
| `install_mcp_server(name, version, source, owner)` | `kind: mcp-server` | `True` on success |
| `remove_mcp_server(name, owner)` | `cap remove` for MCP servers | `True` on success |
| `capability_exists(name)` | Used by tooling to check installation state | `bool` |

Adapters with both skill and MCP support (e.g. `cursor`, `continue-dev`,
`opencode`, `claude-code`, `gemini-cli`) handle both kinds; the others return
`False` from the path that doesn't apply, which is correct behavior — not a
bug.

## Shared MCP config patcher

`src/capacium/adapters/mcp_config_patcher.py` provides a single safe pipeline
for the JSON-based MCP configs (~80% of adapters):

- `backup(config_path)` — creates a timestamped `.bak` before any write
- `read_json` / `write_json` — robust against missing files and malformed JSON
- `read_toml` / `write_toml` — TOML support (used by `codex`)
- `build_mcp_entry(cap_name, source_dir, mcp_meta)` — auto-detects the runtime
  command (uvx for Python, npx for Node, etc.) when manifest doesn't specify
- `inject_json_mcp_server(...)` — full pipeline: backup → read → inject → write
- `remove_json_mcp_server(...)` / `mcp_server_exists_json(...)`

YAML adapters (`goose`, `aider`) implement an analogous pipeline inline using
PyYAML when available, with a graceful JSON fallback.

## Closing remaining gaps

If you want to upgrade a 🟨 or ⛔ adapter:

- **`opencode-command`** — would only matter if Opencode commands gain MCP
  semantics upstream; until then the partial status is correct.
- **`librechat`** — needs a maintainer to validate the actual `librechat.yaml`
  format against current LibreChat versions, then patch in place rather than
  via sidecar.
- **`openclaw`** — wait for OpenClaw to publish a stable config-file
  specification, then update the path.
- **`langchain` / `flowise`** — by-design exports; promoting them would
  require a separate "import this JSON" hook each framework would have to
  call. Not a gap so much as the wrong shape for in-place patching.
- **`notebooklm` / `lutra` / `serge` / `mcp-remote`** — these clients don't
  have a local config to patch. Promotion would require those vendors to ship
  one. The stubs are the correct shape until then.
