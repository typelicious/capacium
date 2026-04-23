# Marketplace

Capacium includes a built-in web-based marketplace UI and registry server for browsing, searching, and managing capabilities.

## Starting the Marketplace

```bash
cap marketplace
```

This starts the HTTP server on `http://0.0.0.0:8000` with:
- Web UI at `http://localhost:8000/`
- REST API at `http://localhost:8000/v1/`

### Options

```bash
cap marketplace --host 127.0.0.1 --port 8080
cap marketplace --open  # Opens browser automatically
```

## Web UI

The marketplace provides a browser interface for:
- Browsing installed capabilities
- Searching by name, owner, or kind
- Viewing capability metadata and dependencies
- Checking fingerprints and signatures

## REST API

The registry server exposes a RESTful API compatible with the [Remote Registry Protocol](../specs/registry-openapi.yaml).

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/health` | Health check |
| GET | `/v1/capabilities` | List/search capabilities |
| GET | `/v1/capabilities/{owner}/{name}` | Get capability details |
| GET | `/v1/capabilities/{owner}/{name}/versions` | List versions |
| POST | `/v1/capabilities` | Publish a capability (stub) |

### Query Parameters for List

| Param | Type | Description |
|-------|------|-------------|
| `query` | string | Search term (matches name, owner, fingerprint) |
| `kind` | string | Filter by kind (`skill`, `bundle`, etc.) |
| `limit` | int | Max results (default: 50) |
| `offset` | int | Pagination offset (default: 0) |

### Example

```bash
# Health check
curl http://localhost:8000/v1/health

# List all capabilities
curl http://localhost:8000/v1/capabilities

# Search
curl "http://localhost:8000/v1/capabilities?query=web&kind=skill"

# Get capability
curl http://localhost:8000/v1/capabilities/my-org/my-skill

# List versions
curl http://localhost:8000/v1/capabilities/my-org/my-skill/versions
```

### Static Files

The marketplace also serves the web UI assets:
- `GET /` → `index.html`
- `GET /style.css`
- `GET /app.js`

## Programmatic Server

```python
from capacium.registry_server import create_server, run_server

# Create server
server = create_server(host="0.0.0.0", port=8000)

# Or run it directly
run_server(host="0.0.0.0", port=8000, open_browser=True)
```
