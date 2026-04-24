"""OpenClaw MCP adapter (stub).

OpenClaw is an emerging AI coding assistant. Configuration format is not
yet standardized. This adapter provides the interface and prints guidance.
"""
import shutil
from pathlib import Path

from ..storage import StorageManager
from .base import FrameworkAdapter
from .mcp_config_patcher import McpConfigPatcher


class OpenClawAdapter(FrameworkAdapter):

    def __init__(self):
        self.storage = StorageManager()
        # OpenClaw expected config path (subject to change)
        self.config_path = Path.home() / ".openclaw" / "mcp_config.json"

    def install_skill(self, cap_name: str, version: str, source_dir: Path, owner: str = "global") -> bool:
        print("OpenClaw does not support skill symlinking. Use 'mcp-server' kind.")
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

        return McpConfigPatcher.inject_json_mcp_server(
            config_path=self.config_path,
            server_key=cap_name,
            mcp_section_key="mcpServers",
            cap_name=cap_name,
            source_dir=package_dir,
            mcp_meta=mcp_meta,
        )

    def remove_mcp_server(self, cap_name: str, owner: str = "global") -> bool:
        return McpConfigPatcher.remove_json_mcp_server(
            self.config_path, cap_name, "mcpServers",
        )

    def capability_exists(self, cap_name: str) -> bool:
        return McpConfigPatcher.mcp_server_exists_json(
            self.config_path, cap_name, "mcpServers",
        )
