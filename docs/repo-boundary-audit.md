# Repository Boundary Audit — Capacium Ecosystem

**Date:** 2026-04-26
**Author:** AI Agent (automated audit)

---

## Repo Inventory

| Repo | Local Path | Domain | Stack | Status |
|------|-----------|--------|-------|--------|
| `Capacium/capacium` | `.../capacium/` | Core CLI, manifest, packaging, local verification | Python 3.10+ (stdlib only) | Active — v0.7.3 |
| `Capacium/capacium-exchange` | `.../capacium-exchange/` | Exchange API server, listing CRUD, trust state machine | Python, FastAPI, SQLAlchemy | Active — v0.1.0 |
| `Capacium/capacium-crawler` | `.../capacium-crawler/` | Agent network discovery crawler | Python (stdlib) | Active — v0.1.0 |
| `Capacium/capacium-bridge` | `.../capacium-bridge/` | WordPress plugin syncing Exchange → Voxel CPT | PHP (WordPress) | Stub — v0.1.0 |
| `Capacium/homebrew-tap` | `.../homebrew-tap-capacium/` | Homebrew formula distribution | Ruby (Formula) | Active — v0.6.1 (lags behind v0.7.3) |

---

## Boundary Violations — Core Repo (`capacium`)

### 1. `TrustState` enum in `models.py`
- **File:** `src/capacium/models.py:19-53`
- **Severity:** Minor
- **Description:** `TrustState` is an Exchange domain concept (trust state machine: DISCOVERED → INDEXED → CLAIMED → VERIFIED → AUDITED) that lives in the core models module. It is only referenced locally by `registry.py` for a migration hook.
- **Action:** Move to Exchange repo; replace with a simple `Optional[str]` in core if needed for registry metadata.

### 2. `registry.py:_run_v2_migration()` dead code
- **File:** `src/capacium/registry.py:104-112`
- **Severity:** Minor
- **Description:** Attempts to import `migrations.v2_exchange_crawler` which does not exist on disk. Silently passes via `try/except`. Introduced at startup (`__init__` calls it).
- **Action:** Remove the entire method and its call from `__init__`.

### 3. `search.py` Exchange filter messages
- **File:** `src/capacium/commands/search.py:36-38`
- **Severity:** Cosmetic
- **Description:** Detects Exchange-specific flags and prints a user-facing message directing users to the V2 Exchange API.
- **Action:** Keep — harmless user guidance. No Exchange API call made.

### 4. `cli.py` extraction comments
- **Files:** `src/capacium/cli.py:108, 206`
- **Severity:** Cosmetic
- **Description:** Comments noting that V2 Platform Commands were extracted to V3 Platform Services.
- **Action:** Keep — useful historical documentation.

---

## Cross-Repo Dependencies

### Dependency Direction

```
capacium-core (stdlib only)
  ├── capacium-exchange (FastAPI, SQLAlchemy)
  │   └── pyproject.toml declares `capacium` dep but code does NOT import from core
  ├── capacium-crawler (stdlib)
  │   └── pyproject.toml declares `capacium` dep but code does NOT import from core
  ├── capacium-bridge (PHP/WordPress)
  │   └── No dependency on core (separate stack)
  └── homebrew-tap (Ruby Formula)
       └── Distributes core, no reverse dependency
```

All dependencies flow **outward only** — core does not depend on any external repo. The declared `capacium` dependency in exchange/crawler `pyproject.toml` is **not actually used** in code.

### Implicit/Circular Dependency

- **None detected.** The dependency graph is a clean tree: core → {exchange, crawler, bridge, tap}.

---

## Duplicate Models

| Concept | In Core | In Exchange | Action |
|---------|---------|-------------|--------|
| `TrustState` | `models.py:19-53` | `exchange/models.py` (presumed) | Move to Exchange only |
| Capability/Kind | `models.py` (core) | Not duplicated | Proper — core owns this |
| Listing/Publishing | Not in core | Exchange only | Proper |

---

## Maintenance Gaps

| Issue | Repo | Severity |
|-------|------|----------|
| Homebrew formula at v0.6.1, core at v0.7.3 | `homebrew-tap` | Medium |
| Exchange code does not actually use `capacium` dependency | `capacium-exchange` | Cosmetic |
| `capacium-bridge` is a PHP stub, no CI/tests | `capacium-bridge` | Low (pre-alpha) |

---

## Summary

**The Capacium ecosystem is already well-partitioned.** The extraction of V2 Exchange & Crawler from the core was largely successful. Only minor cleanup remains:

1. Remove `TrustState` from core `models.py`
2. Remove dead `_run_v2_migration()` from `registry.py`
