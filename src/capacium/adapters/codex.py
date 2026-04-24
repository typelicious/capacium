"""Codex (OpenAI CLI/IDE) MCP adapter.

Config: ~/.codex/config.toml
"""
import shutil
from pathlib import Path

from ..storage import StorageManager
from .base import FrameworkAdapter
from .mcp_config_patcher import McpConfigPatcher


class CodexAdapter(FrameworkAdapter):

    def __init__(self):
        self.storage = StorageManager()
        self.config_path = Path.home() / ".codex" / "config.toml"

    def install_skill(self, cap_name: str, version: str, source_dir: Path, owner: str = "global") -> bool:
        print("Codex does not support skill symlinking. Use 'mcp-server' kind.")
        return False

    def remove_skill(self, cap_name: str, owner: str = "global") -> bool:
        return False

    def install_mcp_server(self, cap_name: str, version: str, source_dir: Path, owner: str = "global") -> bool:
        package_dir = self.storage.get_package_dir(cap_name, version, owner=owner)
        if package_dir.exists():
            shutil.rmtree(package_dir)
        shutil.copytree(source_dir, package_dir)

        from ..manifest import Manifest
        manifest = Manifest.detect_from_directory(package_dir)
        mcp_meta = manifest.get_mcp_metadata()
        entry = McpConfigPatcher.build_mcp_entry(cap_name, package_dir, mcp_meta)

        McpConfigPatcher.backup(self.config_path)
        config = McpConfigPatcher.read_toml(self.config_path)
        servers = config.setdefault("mcp_servers", {})
        servers[cap_name] = entry
        McpConfigPatcher.write_toml(self.config_path, config)
        return True

    def remove_mcp_server(self, cap_name: str, owner: str = "global") -> bool:
        config = McpConfigPatcher.read_toml(self.config_path)
        servers = config.get("mcp_servers", {})
        if cap_name in servers:
            McpConfigPatcher.backup(self.config_path)
            del servers[cap_name]
            McpConfigPatcher.write_toml(self.config_path, config)
        return True

    def capability_exists(self, cap_name: str) -> bool:
        config = McpConfigPatcher.read_toml(self.config_path)
        return cap_name in config.get("mcp_servers", {})
