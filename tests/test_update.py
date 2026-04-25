import json


def test_update_reconciles_unique_unqualified_mcp_name(tmp_home, tmp_path):
    source = tmp_path / "mempalace"
    source.mkdir()
    (source / "capability.yaml").write_text(
        "kind: mcp-server\n"
        "name: mempalace\n"
        "version: 1.0.0\n"
        "frameworks: [opencode]\n"
        "mcp:\n"
        "  transport: stdio\n"
        "  command: uvx\n"
        "  args: [mempalace-mcp]\n"
    )

    from capacium.commands.install import install_capability
    assert install_capability(
        "MemPalace/mempalace",
        source_dir=source,
        no_lock=True,
        skip_runtime_check=True,
    ) is True

    config_path = tmp_home / ".config" / "opencode" / "opencode.json"
    config_path.write_text(json.dumps({}))

    from capacium.commands.update import update_capability
    assert update_capability("mempalace", skip_runtime_check=True) is True

    data = json.loads(config_path.read_text())
    assert data["mcp"]["mempalace"] == {
        "type": "local",
        "command": ["uvx", "mempalace-mcp"],
        "enabled": True,
    }


def test_update_reports_ambiguous_unqualified_name(tmp_home, tmp_path, capsys):
    from capacium.registry import Registry
    from capacium.models import Capability, Kind
    from datetime import datetime

    registry = Registry()
    for owner in ("alice", "bob"):
        registry.add_capability(Capability(
            owner=owner,
            name="shared",
            version="1.0.0",
            kind=Kind.SKILL,
            fingerprint="fp",
            install_path=tmp_path,
            installed_at=datetime.now(),
            framework="opencode",
        ))

    from capacium.commands.update import update_capability
    assert update_capability("shared", skip_runtime_check=True) is False

    out = capsys.readouterr().out
    assert "ambiguous" in out
    assert "alice/shared" in out
    assert "bob/shared" in out
