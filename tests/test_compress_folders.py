"""
Tests for scripts/compress_folders_filtered.py

Coverage
--------
- find_7z()            : found on PATH / explicit path / not found / invalid explicit
- build_7z_command()   : happy path, empty dict_size, empty threads, missing repo
- list_repo_subfolders(): happy path, empty dir, non-existent dir, file (not dir)
- run_archive()        : mocked happy path, non-zero exit, timeout, permission error

Run
---
    pytest tests/test_compress_folders.py -v
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Import module under test ──────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from compress_folders_filtered import (
    find_7z,
    build_7z_command,
    list_repo_subfolders,
    run_archive,
)


# ─────────────────────────────────────────────────────────────────────────────
# find_7z
# ─────────────────────────────────────────────────────────────────────────────

class TestFindSevenZip:
    """Tests for find_7z()."""

    def test_explicit_path_valid(self, tmp_path: Path) -> None:
        """Explicit path that exists is returned as-is (resolved)."""
        fake_exe = tmp_path / "7z.exe"
        fake_exe.touch()
        result = find_7z(str(fake_exe))
        assert Path(result).resolve() == fake_exe.resolve()

    def test_explicit_path_missing_raises_value_error(self, tmp_path: Path) -> None:
        """Explicit path that does NOT exist raises ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            find_7z(str(tmp_path / "nonexistent_7z.exe"))

    def test_found_on_path(self) -> None:
        """When 7z is on PATH, it is returned."""
        with patch("shutil.which", side_effect=lambda x: "/usr/bin/7z" if x == "7z" else None):
            result = find_7z()
        assert result == "/usr/bin/7z"

    def test_found_via_7za_fallback(self) -> None:
        """7za is used when 7z is not on PATH."""
        def _which(name: str) -> str | None:
            return "/usr/bin/7za" if name == "7za" else None
        with patch("shutil.which", side_effect=_which):
            result = find_7z()
        assert result == "/usr/bin/7za"

    def test_found_at_windows_default(self, tmp_path: Path) -> None:
        """Falls back to %ProgramFiles%\\7-Zip\\7z.exe when not on PATH."""
        fake_dir = tmp_path / "7-Zip"
        fake_dir.mkdir()
        fake_exe = fake_dir / "7z.exe"
        fake_exe.touch()
        with patch("shutil.which", return_value=None), \
             patch.dict("os.environ", {"ProgramFiles": str(tmp_path)}):
            result = find_7z()
        assert Path(result) == fake_exe

    def test_not_found_raises_file_not_found(self, tmp_path: Path) -> None:
        """FileNotFoundError raised when 7-Zip cannot be located anywhere."""
        with patch("shutil.which", return_value=None), \
             patch.dict("os.environ", {"ProgramFiles": str(tmp_path)}):
            with pytest.raises(FileNotFoundError, match="7-Zip"):
                find_7z()

    def test_none_explicit_path_skipped(self) -> None:
        """Passing None for explicit_path skips the explicit-path check."""
        with patch("shutil.which", return_value="/usr/bin/7z"):
            result = find_7z(None)
        assert result == "/usr/bin/7z"


# ─────────────────────────────────────────────────────────────────────────────
# build_7z_command
# ─────────────────────────────────────────────────────────────────────────────

class TestBuild7zCommand:
    """Tests for build_7z_command()."""

    @pytest.fixture()
    def repo_dir(self, tmp_path: Path) -> Path:
        d = tmp_path / "my_repo"
        d.mkdir()
        return d

    def test_happy_path_structure(self, repo_dir: Path, tmp_path: Path) -> None:
        """Command starts with 7z, add, and contains required flags."""
        archive = tmp_path / "my_repo.7z"
        cmd = build_7z_command(
            sevenzip="7z",
            archive_path=archive,
            repo_path=repo_dir,
            dict_size="256m",
            threads="on",
            solid=True,
            exclude_dirs=[".venv", "node_modules"],
            exclude_globs=["*.pyc"],
        )
        assert cmd[0] == "7z"
        assert cmd[1] == "a"
        assert "-t7z" in cmd
        assert "-m0=lzma2" in cmd
        assert "-mx=9" in cmd
        assert "-md=256m" in cmd
        assert "-mmt=on" in cmd
        assert "-ms=on" in cmd
        assert "-xr!.venv" in cmd
        assert "-xr!node_modules" in cmd
        assert "-xr!*.pyc" in cmd
        assert str(archive) in cmd
        assert str(repo_dir) in cmd

    def test_solid_false(self, repo_dir: Path, tmp_path: Path) -> None:
        cmd = build_7z_command(
            "7z", tmp_path / "out.7z", repo_dir, "128m", "4", False, [], []
        )
        assert "-ms=off" in cmd
        assert "-ms=on" not in cmd

    def test_empty_dict_size_raises(self, repo_dir: Path, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="dict_size"):
            build_7z_command("7z", tmp_path / "out.7z", repo_dir, "", "on", True, [], [])

    def test_empty_threads_raises(self, repo_dir: Path, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="threads"):
            build_7z_command("7z", tmp_path / "out.7z", repo_dir, "256m", "", True, [], [])

    def test_missing_repo_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError, match="does not exist"):
            build_7z_command("7z", tmp_path / "out.7z", missing, "256m", "on", True, [], [])

    def test_exclude_dirs_and_globs_length(self, repo_dir: Path, tmp_path: Path) -> None:
        dirs = [".venv", ".git", "node_modules"]
        globs = ["*.pyc", "*.log"]
        cmd = build_7z_command("7z", tmp_path / "out.7z", repo_dir, "256m", "on", True, dirs, globs)
        xr_entries = [c for c in cmd if c.startswith("-xr!")]
        assert len(xr_entries) == len(dirs) + len(globs)


# ─────────────────────────────────────────────────────────────────────────────
# list_repo_subfolders
# ─────────────────────────────────────────────────────────────────────────────

class TestListRepoSubfolders:
    """Tests for list_repo_subfolders()."""

    def test_returns_sorted_subdirs(self, tmp_path: Path) -> None:
        for name in ["zebra", "alpha", "mango"]:
            (tmp_path / name).mkdir()
        result = list_repo_subfolders(tmp_path)
        assert [p.name for p in result] == ["alpha", "mango", "zebra"]

    def test_ignores_files(self, tmp_path: Path) -> None:
        (tmp_path / "a_file.txt").touch()
        (tmp_path / "a_dir").mkdir()
        result = list_repo_subfolders(tmp_path)
        assert len(result) == 1
        assert result[0].name == "a_dir"

    def test_empty_parent_returns_empty_list(self, tmp_path: Path) -> None:
        result = list_repo_subfolders(tmp_path)
        assert result == []

    def test_nonexistent_parent_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "ghost"
        with pytest.raises(FileNotFoundError):
            list_repo_subfolders(missing)

    def test_file_as_parent_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "iam_a_file.txt"
        f.touch()
        with pytest.raises(NotADirectoryError):
            list_repo_subfolders(f)


# ─────────────────────────────────────────────────────────────────────────────
# run_archive
# ─────────────────────────────────────────────────────────────────────────────

class TestRunArchive:
    """Tests for run_archive() — all subprocess calls are mocked."""

    def _mock_run(self, returncode: int, stdout: str = "", stderr: str = "") -> MagicMock:
        m = MagicMock()
        m.returncode = returncode
        m.stdout = stdout
        m.stderr = stderr
        return m

    def test_happy_path_returns_zero(self) -> None:
        cmd = ["7z", "a", "out.7z", "src/"]
        with patch("subprocess.run", return_value=self._mock_run(0, stdout="Everything is Ok")):
            rc, out, err = run_archive(cmd)
        assert rc == 0
        assert "Everything is Ok" in out
        assert err == ""

    def test_non_zero_exit_code_returned(self) -> None:
        cmd = ["7z", "a", "out.7z", "src/"]
        with patch("subprocess.run", return_value=self._mock_run(2, stderr="Fatal error")):
            rc, out, err = run_archive(cmd)
        assert rc == 2
        assert "Fatal error" in err

    def test_timeout_raises(self) -> None:
        cmd = ["7z", "a", "out.7z", "src/"]
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd, 10)):
            with pytest.raises(subprocess.TimeoutExpired):
                run_archive(cmd, timeout=10)

    def test_permission_error_raises(self) -> None:
        cmd = ["7z", "a", "out.7z", "src/"]
        with patch("subprocess.run", side_effect=PermissionError("access denied")):
            with pytest.raises(PermissionError, match="Permission denied"):
                run_archive(cmd)

    def test_subprocess_called_with_timeout(self) -> None:
        """Verify timeout is always passed to subprocess.run."""
        cmd = ["7z", "a", "out.7z", "src/"]
        with patch("subprocess.run", return_value=self._mock_run(0)) as mock_run:
            run_archive(cmd, timeout=120)
        _, kwargs = mock_run.call_args
        assert kwargs.get("timeout") == 120
