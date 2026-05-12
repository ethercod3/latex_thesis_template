from __future__ import annotations

from pathlib import Path

import pytest

import build_latex_manual as latex
from common import ScriptError


@pytest.fixture
def latex_project(tmp_path, monkeypatch) -> Path:
    monkeypatch.setattr(latex, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(latex, "AUX_DIR", tmp_path / ".aux_files")
    return tmp_path


def test_target_tex_path_uses_explicit_relative_path(latex_project: Path) -> None:
    target = latex_project / "main.tex"
    target.write_text("", encoding="utf-8")

    assert latex.target_tex_path("main.tex") == target.resolve()


def test_target_tex_path_falls_back_to_single_tex_file(latex_project: Path, monkeypatch) -> None:
    target = latex_project / "single.tex"
    target.write_text("", encoding="utf-8")
    monkeypatch.setattr(latex, "env_value", lambda name: None)

    assert latex.target_tex_path(None) == target.resolve()


def test_target_tex_path_requires_unambiguous_target(latex_project: Path, monkeypatch) -> None:
    (latex_project / "one.tex").write_text("", encoding="utf-8")
    (latex_project / "two.tex").write_text("", encoding="utf-8")
    monkeypatch.setattr(latex, "env_value", lambda name: None)

    with pytest.raises(ScriptError):
        latex.target_tex_path(None)


def test_latexmk_command_uses_project_relative_path(latex_project: Path) -> None:
    target = latex_project / "chapters" / "main.tex"
    target.parent.mkdir()
    target.write_text("", encoding="utf-8")

    assert latex.latexmk_command(target) == ["latexmk", str(Path("chapters") / "main.tex")]
