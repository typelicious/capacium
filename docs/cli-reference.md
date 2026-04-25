# CLI Reference

## Usage

```bash
cap [command] [options]
cap --help
cap --version
```

## Commands

### `cap install`

Install a capability from a registry, local path, git URL, or source directory.

```bash
cap install <capability>
cap install <owner/name>[@<version>]
cap install <path>
cap install <git-url>
cap install --source <directory> <name>
cap install --no-lock <capability>
```

Options:
- `--source <dir>` — Source directory containing the capability (default: current directory)
- `--no-lock` — Bypass lock file enforcement
- `--version <ver>` — Specific version to install

### `cap remove`

Remove an installed capability.

```bash
cap remove <capability>
cap remove --force <capability>
```

Options:
- `--force` — Force removal including sub-capabilities with active dependents

### `cap list`

List installed capabilities.

```bash
cap list
cap list --kind <kind>
```

Options:
- `--kind <kind>` — Filter by capability kind (`skill`, `bundle`, `tool`, `prompt`, `template`, `workflow`)

### `cap update`

Update a capability to the latest compatible version.

```bash
cap update <capability>
cap update <capability> --force
cap update <capability> --skip-runtime-check
```

Options:
- `--force` — Reconcile adapter configuration even when package content is unchanged
- `--skip-runtime-check` — Skip MCP runtime pre-flight checks during update

### `cap search`

Search for capabilities in the registry.

```bash
cap search <query>
cap search --kind <kind>
cap search --registry <url>
```

Options:
- `--kind <kind>` — Filter results by kind
- `--registry <url>` — Target a specific registry URL

### `cap verify`

Verify capability fingerprint and optional signature.

```bash
cap verify <capability>
cap verify --all
cap verify <capability> --key <key-name>
cap verify --all --key <key-name>
```

Options:
- `--all` — Verify all installed capabilities
- `--key <name>` — Verify against a cryptographic signature

### `cap lock`

Generate or update a lock file for an installed capability.

```bash
cap lock <capability>
cap lock --update <capability>
```

Options:
- `--update` — Refresh an existing lock file

### `cap package`

Package a capability for distribution.

```bash
cap package <path>
cap package <path> --output <archive.tar.gz>
```

Options:
- `--output <path>` — Output archive path

### `cap publish`

Publish a capability to a registry (stub).

```bash
cap publish <path>
cap publish --registry <url>
```

Options:
- `--registry <url>` — Target registry URL

### `cap marketplace`

Start the marketplace web UI and registry server.

```bash
cap marketplace
cap marketplace --host 127.0.0.1 --port 8080
cap marketplace --open
```

Options:
- `--host <host>` — Bind address (default: `0.0.0.0`)
- `--port <port>` — Port number (default: `8000`)
- `--open` — Open browser automatically

### `cap key`

Manage Ed25519 signing keys.

```bash
cap key generate <name>
cap key list
cap key export <name>
cap key import <name> <pem-file>
```

### `cap sign`

Sign a capability with a private key.

```bash
cap sign <capability> --key <key-name>
```

Options:
- `--key <name>` — Key name to sign with

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User error (invalid input, missing args) |
| 2 | System error (I/O, database, network) |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CAPACIUM_REGISTRY_URL` | Default remote registry URL |
| `CAPACIUM_REGISTRY_TOKEN` | Bearer token for registry auth |
