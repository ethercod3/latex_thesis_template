from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
import pytest

from diff_pdf_commits import parse_profiles, requested_save_path, safe_label
from pdfdiff.cli import main

runner = CliRunner()


def test_safe_label_keeps_filename_friendly_characters() -> None:
    assert safe_label("feature/pdf-diff@HEAD~1") == "feature_pdf-diff_HEAD_1"


def test_parse_profiles_expands_groups() -> None:
    assert parse_profiles("all") == ["docx", "mermaid", "python", "latex"]
    assert parse_profiles("mermaid") == ["mermaid", "latex"]


def test_parse_profiles_orders_explicit_profiles_and_adds_latex() -> None:
    assert parse_profiles("python,docx") == ["docx", "python", "latex"]


def test_parse_profiles_rejects_unknown_profile() -> None:
    with pytest.raises(ValueError):
        parse_profiles("unknown")


def test_requested_save_path_uses_default_path_for_bare_save() -> None:
    path = requested_save_path(True, "HEAD~1", "HEAD", "diploma.pdf")
    assert path is not None
    assert path.name == "diploma_diff_HEAD_1__HEAD.pdf"
    assert path.parent.name == "saved"


def test_requested_save_path_resolves_relative_path_inside_project() -> None:
    path = requested_save_path("out/diff.pdf", "left", "right", "diploma.pdf")
    assert path is not None
    assert path.is_absolute()
    assert path.name == "diff.pdf"


def test_cli_accepts_bare_save_flag_and_path(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeRunner:
        def __init__(self, config: object) -> None:
            captured["config"] = config

        def run(self) -> int:
            return 0

    monkeypatch.setattr("pdfdiff.cli.PdfDiffRunner", FakeRunner)
    monkeypatch.setattr("pdfdiff.cli.target_pdf_name", lambda: "diploma.pdf")

    result = runner.invoke(main, ["left", "right", "--save"], prog_name="diff_pdf_commits.py")
    assert result.exit_code == 0
    assert captured["config"].save_path is not None
    assert captured["config"].save_path.name == "diploma_diff_left__right.pdf"

    captured.clear()
    result = runner.invoke(main, ["left", "right", "--save", "out/diff.pdf"], prog_name="diff_pdf_commits.py")
    assert result.exit_code == 0
    assert captured["config"].save_path is not None
    assert captured["config"].save_path.name == "diff.pdf"
