"""``cap runtimes`` — list known runtimes or print install hints.

Two subcommands:

* ``cap runtimes list`` — show all runtimes Capacium knows about, marking which
  are present on this host and at what version.
* ``cap runtimes install <name>`` — print the install command for the host
  platform. Capacium intentionally does not execute it; running package
  managers on the user's behalf is high-blast-radius behavior.
"""

from __future__ import annotations

import sys
from typing import Optional

from ..runtimes import RUNTIMES, RuntimeResolver, known_runtime_names


CHECK = "[ok]"
CROSS = "[--]"


def list_runtimes() -> bool:
    """Print a table of known runtimes + presence + version. Always returns True."""
    resolver = RuntimeResolver()
    print(f"{'Runtime':<10} {'Status':<6} {'Version':<15} Provides")
    print("-" * 60)
    for name in known_runtime_names():
        rt = RUNTIMES[name]
        found, version, _err = resolver.detect(name)
        mark = CHECK if found else CROSS
        version_s = version if version else "-"
        provides = ", ".join(rt.provides)
        print(f"{name:<10} {mark:<6} {version_s:<15} {provides}")
    return True


def show_install_hint(name: str, *, platform: Optional[str] = None) -> bool:
    """Print the install command for a runtime — does NOT execute it."""
    rt = RUNTIMES.get(name)
    if rt is None:
        valid = ", ".join(known_runtime_names())
        print(f"Unknown runtime: {name}")
        print(f"Known runtimes: {valid}")
        return False
    plat = platform or sys.platform
    hint = rt.install_hint_for(plat)
    if not hint:
        print(f"No install hint registered for {name} on {plat}.")
        if rt.homepage:
            print(f"See: {rt.homepage}")
        return False
    print(f"To install {name} on {plat}, run:")
    print("")
    print(f"    {hint}")
    print("")
    print("Capacium does NOT run this for you — copy/paste it yourself.")
    if rt.homepage:
        print(f"Docs: {rt.homepage}")
    return True
