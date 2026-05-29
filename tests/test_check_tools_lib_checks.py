from __future__ import annotations

import importlib
from pathlib import Path

from check_tools_lib import checks
from check_tools_lib.checks import diagram_state_checks


def test_local_tex_tools_are_optional() -> None:
    items = {item.name: item for item in checks()}

    for name in ("LuaLaTeX", "latexmk", "biber", "kpsewhich", "Пакет PyLuaTeX"):
        assert items[name].required is False


def test_mermaid_state_checks_include_supported_extensions(tmp_path: Path, monkeypatch) -> None:
    source_dir = tmp_path / "mermaid"
    figures_dir = tmp_path / "figures"
    source_dir.mkdir()
    figures_dir.mkdir()
    for name in ("one.mmd", "two.mermaid", "three.mmdc"):
        (source_dir / name).write_text("flowchart TD\nA-->B\n", encoding="utf-8")

    check_module = importlib.import_module("check_tools_lib.checks")

    monkeypatch.setattr(check_module, "PROJECT_DIR", tmp_path)

    result = diagram_state_checks("Mermaid", source_dir, ("*.mmd", "*.mermaid", "*.mmdc"))

    assert len(result) == 1
    assert result[0].warning is True
    assert "one.pdf" in result[0].detail
    assert "two.pdf" in result[0].detail
    assert "three.pdf" in result[0].detail
