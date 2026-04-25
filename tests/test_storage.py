from capacium.storage import StorageManager


def test_storage_preserves_owner_name_layout(tmp_path):
    base = tmp_path / "packages"
    cap = base / "MemPalace" / "mempalace" / "1.0.0"
    cap.mkdir(parents=True)
    (cap / "capability.yaml").write_text("name: mempalace\n")

    StorageManager(base)

    assert (base / "MemPalace" / "mempalace" / "1.0.0").exists()
    assert not (base / "global" / "MemPalace").exists()


def test_storage_migrates_legacy_name_version_layout(tmp_path):
    base = tmp_path / "packages"
    legacy = base / "mempalace" / "1.0.0"
    legacy.mkdir(parents=True)
    (legacy / "capability.yaml").write_text("name: mempalace\n")

    StorageManager(base)

    assert (base / "global" / "mempalace" / "1.0.0").exists()
    assert not (base / "mempalace").exists()
