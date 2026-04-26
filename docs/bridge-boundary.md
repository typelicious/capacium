# Bridge Repository Boundary — `Capacium/capacium-bridge`

## Belongs
- WordPress plugin code (PHP)
- Voxel CPT sync: mapping Exchange listings to Voxel custom post types
- Exchange API client: HTTP calls from WordPress to the Exchange API server
- Dashboard widget: WordPress admin UI for browsing/searching capabilities
- Activation/deactivation hooks for the WordPress plugin
- Composer dependencies (PHP)

## Does NOT Belong
- Python code of any kind
- CLI logic (`cap install`, `cap remove`, etc.)
- Crawler pipeline or crawl logic
- Exchange API server or listing CRUD
- Core domain models (`Capability`, `Kind`, etc.)
- Homebrew Formula definitions
- Exchange trust state machine

## Dependency Direction
```
Bridge → Exchange API  (Bridge makes HTTP REST calls to the Exchange server)
Bridge → Core          (FORBIDDEN — Bridge is PHP; Core is Python on a different stack)
Core → Bridge          (FORBIDDEN — Core must never import Bridge)
```
**Bridge communicates with Exchange exclusively via HTTP. No shared code imports.**

## Allowed Dependencies
- PHP 8.0+
- WordPress plugin API
- Composer (PHP dependency manager)
- Guzzle or WordPress HTTP API for outbound REST calls to Exchange

## What "Runs Here"
- WordPress plugin activation, deactivation, and uninstall
- Voxel CPT registration and sync logic
- Dashboard widget rendering
- Exchange API client that fetches listings for display inside WordPress admin
