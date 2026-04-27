import pytest
import subprocess
from pathlib import Path


class TestResolveSource:
    def test_local_path_returns_dir(self, tmp_path):
        d = tmp_path / "my-cap"
        d.mkdir()
        from capacium.commands.install import _resolve_source
        result = _resolve_source(d)
        assert result is not None
        assert result[0] == d

    def test_local_path_with_git_remote(self, tmp_path):
        d = tmp_path / "git-cap"
        d.mkdir()
        subprocess.run(["git", "init"], cwd=d, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=d, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=d, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/foo/bar.git"], cwd=d, capture_output=True)
        (d / "readme.md").write_text("x")
        subprocess.run(["git", "add", "."], cwd=d, capture_output=True)
        subprocess.run(["git", "commit", "-m", "x"], cwd=d, capture_output=True)

        from capacium.commands.install import _resolve_source
        result = _resolve_source(d)
        assert result is not None
        assert result[1] == "https://github.com/foo/bar.git"

    def test_missing_path_returns_none(self, tmp_path):
        from capacium.commands.install import _resolve_source
        assert _resolve_source(tmp_path / "nope") is None

    def test_git_url_returns_clone(self, tmp_path):
        from capacium.commands.install import _is_git_remote_url
        assert _is_git_remote_url("https://github.com/foo/bar.git")

    def test_github_shortcut_clones(self, tmp_path):
        from unittest.mock import patch
        from capacium.commands.install import _resolve_source

        with patch("capacium.commands.install.tempfile.mkdtemp", return_value=str(tmp_path / "_tmp")):
            (tmp_path / "_tmp").mkdir(parents=True, exist_ok=True)
            repo_dir = tmp_path / "_tmp" / "repo"
            repo_dir.mkdir(parents=True)
            (repo_dir / "readme.md").write_text("hello")

            with patch("capacium.commands.install.subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = _resolve_source(Path("owner/repo"))
                assert result is not None
                clone_call = [c for c in mock_run.call_args_list if "clone" in str(c)][0]
                assert "github.com/owner/repo.git" in str(clone_call)


class TestAutoGenerateManifest:
    def test_generates_when_missing(self, tmp_path):
        d = tmp_path / "repo"
        d.mkdir()
        (d / "readme.md").write_text("hello")
        from capacium.commands.install import _auto_generate_manifest
        _auto_generate_manifest(d, "https://github.com/typelicious/SkillWeave.git")
        manifest = d / "capability.yaml"
        assert manifest.exists()
        content = manifest.read_text()
        assert "typelicious" in content
        assert "SkillWeave" in content

    def test_skips_when_already_exists(self, tmp_path):
        d = tmp_path / "repo"
        d.mkdir()
        (d / "capability.yaml").write_text("kind: skill\nname: existing\ndescription: original\n")
        from capacium.commands.install import _auto_generate_manifest
        _auto_generate_manifest(d, "https://github.com/x/y.git")
        content = (d / "capability.yaml").read_text()
        assert "original" in content
        assert "y" not in content or "owner: x" not in content


class TestInstallFromSourceFlag:
    def test_install_from_local_path(self, tmp_home, tmp_path, sample_capability_dir):
        from capacium.commands.install import install_capability
        result = install_capability(
            "test-cap",
            source_dir=sample_capability_dir,
            no_lock=True,
            skip_runtime_check=True,
        )
        assert result is True

    def test_install_rejects_cwd_without_capability(self, tmp_home, tmp_path, capsys, monkeypatch):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        from capacium.commands.install import install_capability
        result = install_capability("test-cap", no_lock=True, skip_runtime_check=True)
        assert result is False
        out = capsys.readouterr().out
        assert "No capability source specified" in out
        assert "Usage:" in out

    def test_install_accepts_cwd_with_capability(self, tmp_home, tmp_path, capsys, monkeypatch):
        from capacium.commands.install import install_capability
        monkeypatch.chdir(tmp_path)
        result = install_capability(
            "cwd-cap",
            no_lock=True,
            skip_runtime_check=True,
        )
        assert result is False
        out = capsys.readouterr().out
        assert "not found" not in out


class TestFetchRemoteTags:
    def test_fetch_tags_from_local_bare(self, tmp_path):
        remote = tmp_path / "remote.git"
        remote.mkdir()
        subprocess.run(["git", "init", "--bare"], cwd=remote, capture_output=True)

        clone = tmp_path / "clone"
        clone.mkdir()
        subprocess.run(["git", "init"], cwd=clone, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=clone, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=clone, capture_output=True)
        (clone / "readme.md").write_text("hello")
        subprocess.run(["git", "add", "."], cwd=clone, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=clone, capture_output=True)
        subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=clone, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=clone, capture_output=True)
        subprocess.run(["git", "tag", "v0.6.0"], cwd=clone, capture_output=True)
        subprocess.run(["git", "tag", "v0.7.0"], cwd=clone, capture_output=True)
        subprocess.run(["git", "push", "origin", "--tags"], cwd=clone, capture_output=True)

        from capacium.commands.install import _fetch_remote_tags
        tags = _fetch_remote_tags(str(remote))
        assert "0.6.0" in tags
        assert "0.7.0" in tags
        assert "0.7.0" > "0.6.0"

    def test_fetch_tags_no_remote(self):
        from capacium.commands.install import _fetch_remote_tags
        assert _fetch_remote_tags("https://invalid.local/repo.git") == []


class TestIsGitRemoteUrl:
    def test_detects_remote_urls(self):
        from capacium.commands.install import _is_git_remote_url
        assert _is_git_remote_url("https://github.com/foo/bar.git")
        assert _is_git_remote_url("git@github.com:foo/bar.git")
        assert _is_git_remote_url("http://example.com/repo")
        assert not _is_git_remote_url("/local/path")
        assert not _is_git_remote_url("")
