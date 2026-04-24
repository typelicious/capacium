from abc import ABC, abstractmethod
from pathlib import Path


class FrameworkAdapter(ABC):
    def install_capability(self, cap_name: str, version: str, source_dir: Path, owner: str = "global", kind: str = "skill") -> bool:
        if kind == "mcp-server":
            return self.install_mcp_server(cap_name, version, source_dir, owner)
        return self.install_skill(cap_name, version, source_dir, owner)

    def remove_capability(self, cap_name: str, owner: str = "global", kind: str = "skill") -> bool:
        if kind == "mcp-server":
            return self.remove_mcp_server(cap_name, owner)
        return self.remove_skill(cap_name, owner)

    @abstractmethod
    def install_skill(self, cap_name: str, version: str, source_dir: Path, owner: str = "global") -> bool:
        ...

    @abstractmethod
    def remove_skill(self, cap_name: str, owner: str = "global") -> bool:
        ...

    @abstractmethod
    def install_mcp_server(self, cap_name: str, version: str, source_dir: Path, owner: str = "global") -> bool:
        ...

    @abstractmethod
    def remove_mcp_server(self, cap_name: str, owner: str = "global") -> bool:
        ...

    @abstractmethod
    def capability_exists(self, cap_name: str) -> bool:
        ...
