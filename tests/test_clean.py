from __future__ import annotations

from pathlib import Path

import pytest

import clean


@pytest.fixture
def clean_root(tmp_path, monkeypatch) -> Path:
    monkeypatch.setattr(clean, "ROOT", tmp_path)
    return tmp_path


def test_collect_targets_finds_root_artifacts_and_recursive_cache(clean_root: Path) -> None:
    (clean_root / ".aux_files").mkdir()
    (clean_root / "main.aux").write_text("", encoding="utf-8")
    package_cache = clean_root / "package" / "__pycache__"
    package_cache.mkdir(parents=True)
    (package_cache / "module.pyc").write_bytes(b"")

    targets = {path.relative_to(clean_root).as_posix() for path in clean.collect_targets()}

    assert ".aux_files" in targets
    assert "main.aux" in targets
    assert "package/__pycache__" in targets
    assert "package/__pycache__/module.pyc" not in targets


def test_collect_targets_ignores_excluded_directories(clean_root: Path) -> None:
    node_cache = clean_root / "node_modules" / "pkg" / "__pycache__"
    node_cache.mkdir(parents=True)
    (node_cache / "module.pyc").write_bytes(b"")

    assert clean.collect_targets() == []


def test_outside_paths_are_not_inside_root_and_are_excluded(clean_root: Path, tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-clean-target.tmp"
    outside.write_text("", encoding="utf-8")
    try:
        assert not clean.is_inside_root(outside)
        assert clean.is_excluded(outside)
    finally:
        outside.unlink(missing_ok=True)


def test_remove_path_dry_run_keeps_file(clean_root: Path) -> None:
    target = clean_root / "main.log"
    target.write_text("log", encoding="utf-8")

    clean.remove_path(target, dry_run=True)

    assert target.exists()
