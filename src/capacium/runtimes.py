"""Runtime resolver — detect and validate the local runtimes a capability needs.

Capacium installs MCP servers and other capabilities that shell out to a host
runtime (uv/uvx, node/npm/npx, python, docker, …). The previous adapter pipeline
wrote configs without ever checking whether those runtimes exist; users only
discovered missing dependencies when their MCP client silently failed to start.

This module provides:

* a small registry mapping well-known runtime names → detection + install hints,
* a stdlib-only ``RuntimeResolver`` that probes the host with ``shutil.which``
  and a version subprocess call,
* helpers used by ``cap install`` (pre-flight) and ``cap doctor``.

Conventions
-----------

* Stdlib only — no ``packaging`` or ``semver`` dependency.
* Version requirements support ``"*"`` (any), ``">=X[.Y[.Z]]"`` and bare
  ``"X.Y.Z"`` (treated as ``">=X.Y.Z"``). Anything else is treated as ``"*"``.
* Runtimes ``provides`` a list of executables; auto-inference from
  ``manifest.mcp.command`` maps a wrapper command (``uvx``, ``npx``, …) to the
  parent runtime that ships it.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ──────────────────────────────────────────────────────────────────────────
# Runtime registry
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Runtime:
    """Metadata describing a host runtime Capacium can detect."""

    name: str
    check_cmd: Sequence[str]
    provides: Sequence[str]
    install_hints: Dict[str, str] = field(default_factory=dict)
    homepage: str = ""

    def install_hint_for(self, platform: Optional[str] = None) -> Optional[str]:
        """Return the install hint for the given platform name (sys.platform)."""
        plat = platform if platform is not None else sys.platform
        # Try exact match first, then broad linux/darwin/win prefixes.
        if plat in self.install_hints:
            return self.install_hints[plat]
        if plat.startswith("linux") and "linux" in self.install_hints:
            return self.install_hints["linux"]
        if plat.startswith("darwin") and "darwin" in self.install_hints:
            return self.install_hints["darwin"]
        if plat.startswith("win") and "win32" in self.install_hints:
            return self.install_hints["win32"]
        return None


RUNTIMES: Dict[str, Runtime] = {
    "uv": Runtime(
        name="uv",
        check_cmd=("uv", "--version"),
        provides=("uv", "uvx"),
        install_hints={
            "darwin": "brew install uv",
            "linux": "curl -LsSf https://astral.sh/uv/install.sh | sh",
            "win32": "winget install --id=astral-sh.uv",
        },
        homepage="https://docs.astral.sh/uv/",
    ),
    "node": Runtime(
        name="node",
        check_cmd=("node", "--version"),
        provides=("node", "npm", "npx"),
        install_hints={
            "darwin": "brew install node",
            "linux": "see https://nodejs.org/en/download/package-manager",
            "win32": "winget install OpenJS.NodeJS",
        },
        homepage="https://nodejs.org/",
    ),
    "python": Runtime(
        name="python",
        check_cmd=("python3", "--version"),
        provides=("python", "python3"),
        install_hints={
            "darwin": "brew install python",
            "linux": "see https://www.python.org/downloads/",
            "win32": "winget install Python.Python.3",
        },
        homepage="https://www.python.org/",
    ),
    "pipx": Runtime(
        name="pipx",
        check_cmd=("pipx", "--version"),
        provides=("pipx",),
        install_hints={
            "darwin": "brew install pipx",
            "linux": "python3 -m pip install --user pipx && python3 -m pipx ensurepath",
            "win32": "python -m pip install --user pipx",
        },
        homepage="https://pipx.pypa.io/",
    ),
    "docker": Runtime(
        name="docker",
        check_cmd=("docker", "--version"),
        provides=("docker",),
        install_hints={
            "darwin": "brew install --cask docker",
            "linux": "see https://docs.docker.com/engine/install/",
            "win32": "winget install Docker.DockerDesktop",
        },
        homepage="https://www.docker.com/",
    ),
    "go": Runtime(
        name="go",
        check_cmd=("go", "version"),
        provides=("go",),
        install_hints={
            "darwin": "brew install go",
            "linux": "see https://go.dev/doc/install",
            "win32": "winget install GoLang.Go",
        },
        homepage="https://go.dev/",
    ),
    "bun": Runtime(
        name="bun",
        check_cmd=("bun", "--version"),
        provides=("bun", "bunx"),
        install_hints={
            "darwin": "brew install oven-sh/bun/bun",
            "linux": "curl -fsSL https://bun.sh/install | bash",
            "win32": "powershell -c \"irm bun.sh/install.ps1 | iex\"",
        },
        homepage="https://bun.sh/",
    ),
    "deno": Runtime(
        name="deno",
        check_cmd=("deno", "--version"),
        provides=("deno",),
        install_hints={
            "darwin": "brew install deno",
            "linux": "curl -fsSL https://deno.land/install.sh | sh",
            "win32": "winget install DenoLand.Deno",
        },
        homepage="https://deno.com/",
    ),
}


# ──────────────────────────────────────────────────────────────────────────
# Auto-inference of runtimes from mcp.command
# ──────────────────────────────────────────────────────────────────────────

# Map of well-known wrapper commands → runtime name in RUNTIMES.
_COMMAND_TO_RUNTIME: Dict[str, str] = {
    "uvx": "uv",
    "uv": "uv",
    "npx": "node",
    "npm": "node",
    "node": "node",
    "pipx": "pipx",
    "python": "python",
    "python3": "python",
    "docker": "docker",
    "go": "go",
    "bun": "bun",
    "bunx": "bun",
    "deno": "deno",
}


def runtime_for_command(command: str) -> Optional[str]:
    """Return the runtime name that provides ``command``, or None.

    Examples
    --------
    >>> runtime_for_command("uvx")
    'uv'
    >>> runtime_for_command("npx")
    'node'
    >>> runtime_for_command("rustc") is None
    True
    """
    if not command:
        return None
    base = command.strip().split()[0]
    base = base.split("/")[-1]
    return _COMMAND_TO_RUNTIME.get(base)


def infer_required_runtimes(manifest) -> Dict[str, str]:
    """Compute the runtime requirements for a manifest.

    Merges declared ``manifest.runtimes`` with any auto-inferred runtimes from
    ``manifest.mcp.command`` (when missing). Declared values win over inferred.
    """
    declared: Dict[str, str] = {}
    raw = getattr(manifest, "runtimes", None) or {}
    if isinstance(raw, dict):
        for k, v in raw.items():
            declared[str(k)] = str(v) if v is not None else "*"

    mcp = getattr(manifest, "mcp", None) or {}
    command = mcp.get("command") if isinstance(mcp, dict) else None
    inferred_name = runtime_for_command(command) if command else None
    if inferred_name and inferred_name not in declared:
        declared[inferred_name] = "*"

    return declared


# ──────────────────────────────────────────────────────────────────────────
# Version comparison (stdlib-only)
# ──────────────────────────────────────────────────────────────────────────

_VERSION_RE = re.compile(r"(\d+(?:\.\d+){0,3})")


def parse_version(text: str) -> Tuple[int, ...]:
    """Extract a numeric version tuple from arbitrary version output.

    Stripped down semver: returns up to 4 numeric components, padded with zeros
    so comparisons are total. Returns ``(0,)`` if nothing parses.
    """
    if not text:
        return (0,)
    match = _VERSION_RE.search(text)
    if not match:
        return (0,)
    parts = match.group(1).split(".")
    nums = tuple(int(p) for p in parts)
    # Pad to length 3 for stable comparisons.
    while len(nums) < 3:
        nums = nums + (0,)
    return nums


def _normalize(t: Tuple[int, ...], length: int) -> Tuple[int, ...]:
    if len(t) >= length:
        return t[:length]
    return t + (0,) * (length - len(t))


def satisfies(version: str, requirement: str) -> bool:
    """Return True if ``version`` satisfies ``requirement``.

    Supported requirement forms:

    * ``"*"`` or empty → always True
    * ``">=X[.Y[.Z]]"`` → version must be greater than or equal to X.Y.Z
    * ``"X.Y.Z"`` (bare) → treated as ``">=X.Y.Z"`` (loose)

    Any other form is permissive and returns True (callers should rely on the
    runtime's own self-check rather than fighting unrecognized strings).
    """
    if not requirement or requirement.strip() == "*":
        return True
    req = requirement.strip()
    if req.startswith(">="):
        bound = parse_version(req[2:])
        have = parse_version(version)
        length = max(len(bound), len(have))
        return _normalize(have, length) >= _normalize(bound, length)
    if re.fullmatch(r"\d+(\.\d+)*", req):
        # bare X.Y.Z → loose >=X.Y.Z
        bound = parse_version(req)
        have = parse_version(version)
        length = max(len(bound), len(have))
        return _normalize(have, length) >= _normalize(bound, length)
    return True


# ──────────────────────────────────────────────────────────────────────────
# Resolver
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class RuntimeStatus:
    """Result of probing a single runtime."""

    name: str
    requirement: str
    runtime: Optional[Runtime]
    found: bool
    version: Optional[str]
    satisfied: bool
    install_hint: Optional[str] = None
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.found and self.satisfied

    def describe(self) -> str:
        if self.runtime is None:
            return f"{self.name}: unknown runtime (no detection rule)"
        if not self.found:
            hint = f" — install: {self.install_hint}" if self.install_hint else ""
            return f"{self.name}: missing (need {self.requirement}){hint}"
        if not self.satisfied:
            return (
                f"{self.name}: found {self.version} but requires {self.requirement}"
            )
        return f"{self.name}: ok ({self.version})"


class RuntimeResolver:
    """Probe local runtimes against a requirement map."""

    def __init__(
        self,
        registry: Optional[Dict[str, Runtime]] = None,
        which=shutil.which,
        run=subprocess.run,
    ):
        self._registry = registry if registry is not None else RUNTIMES
        self._which = which
        self._run = run

    def known(self, name: str) -> Optional[Runtime]:
        return self._registry.get(name)

    def detect(self, name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Detect a runtime — returns (found, version, error)."""
        rt = self._registry.get(name)
        if rt is None:
            return False, None, f"unknown runtime: {name}"
        if not self._which(rt.check_cmd[0]):
            return False, None, None
        try:
            result = self._run(
                list(rt.check_cmd),
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return False, None, str(exc)
        out = (result.stdout or "") + "\n" + (result.stderr or "")
        match = _VERSION_RE.search(out)
        version = match.group(1) if match else None
        return True, version, None

    def resolve(self, requirements: Dict[str, str]) -> List[RuntimeStatus]:
        statuses: List[RuntimeStatus] = []
        for name, requirement in requirements.items():
            rt = self._registry.get(name)
            if rt is None:
                statuses.append(
                    RuntimeStatus(
                        name=name,
                        requirement=requirement or "*",
                        runtime=None,
                        found=False,
                        version=None,
                        satisfied=False,
                        error=f"unknown runtime: {name}",
                    )
                )
                continue
            found, version, error = self.detect(name)
            satisfied = bool(found and satisfies(version or "0", requirement or "*"))
            statuses.append(
                RuntimeStatus(
                    name=name,
                    requirement=requirement or "*",
                    runtime=rt,
                    found=found,
                    version=version,
                    satisfied=satisfied,
                    install_hint=rt.install_hint_for(),
                    error=error,
                )
            )
        return statuses


# ──────────────────────────────────────────────────────────────────────────
# Convenience helpers
# ──────────────────────────────────────────────────────────────────────────

def format_failure_report(
    statuses: Iterable[RuntimeStatus],
    *,
    platform: Optional[str] = None,
) -> str:
    """Format a human-friendly error message listing failing runtimes."""
    lines: List[str] = []
    failures = [s for s in statuses if not s.ok]
    if not failures:
        return ""
    lines.append("Missing or incompatible runtimes:")
    for s in failures:
        lines.append(f"  - {s.describe()}")
        if s.runtime is not None:
            hint = s.runtime.install_hint_for(platform)
            if hint and (not s.found):
                lines.append(f"      install: {hint}")
            if s.runtime.homepage:
                lines.append(f"      docs:    {s.runtime.homepage}")
    lines.append("")
    lines.append("Re-run with --skip-runtime-check to bypass this gate.")
    return "\n".join(lines)


def known_runtime_names() -> List[str]:
    return sorted(RUNTIMES.keys())
