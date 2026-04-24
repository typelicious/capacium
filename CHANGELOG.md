# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2026-04-24

### Added
- **Universal MCP Client Parity**: Added support for 22+ new MCP clients/adapters.
- New adapters for:
  - **Tier 1 (Dev & Engineering)**: Claude Desktop, Claude Code, Windsurf, Cline, Zed, Codex, Sourcegraph Cody, Antigravity, Continue, Gemini CLI.
  - **Tier 2 (Workflow & Apps)**: LibreChat, Chainlit, Cherry Studio, NextChat, Desktop Commander, NotebookLM, Lutra, Serge, mcp-remote.
  - **Tier 3 (Extended Skills)**: Roo Code, Goose, Aider, OpenClaw.
  - **Tier 4 (Bridges)**: LangChain, Flowise.
- **McpConfigPatcher**: New shared utility for safe JSON/TOML configuration patching with automatic backups (`.bak`).
- **Template Method Pattern in Adapters**: Refactored `FrameworkAdapter` to cleanly separate `SKILL` (symlinking) from `MCP_SERVER` (config patching) installation paths.

### Changed
- Refactored `src/capacium/adapters/` to a more modular structure.
- Updated `cap install` and `cap remove` to pass capability `kind` to adapters.
- Improved error handling and validation during adapter registration.

### Fixed
- Fixed duplicate imports in legacy adapters.
- Enhanced robustness of MCP server auto-detection (package.json, pyproject.toml, etc.).

## [0.5.0] - 2026-04-24
- Native MCP support.
- Headless Client Architecture.
