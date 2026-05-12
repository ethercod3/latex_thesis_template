from __future__ import annotations

from importlib import metadata

import check_python_requirements as requirements


def test_requirement_name_ignores_comments_and_blank_lines() -> None:
    assert requirements.requirement_name("") == ""
    assert requirements.requirement_name("   # comment") == ""


def test_requirement_name_strips_version_specifiers() -> None:
    assert requirements.requirement_name("pytest==9.0.3") == "pytest"
    assert requirements.requirement_name("black>=26") == "black"
    assert requirements.requirement_name("python-dotenv~=1.2") == "python-dotenv"


def test_missing_requirements_reports_only_missing_packages(tmp_path, monkeypatch) -> None:
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text("installed==1\nmissing>=2\n# ignored\n\n", encoding="utf-8")

    def fake_version(package: str) -> str:
        if package == "missing":
            raise metadata.PackageNotFoundError(package)
        return "1.0"

    monkeypatch.setattr(requirements.metadata, "version", fake_version)

    assert requirements.missing_requirements(requirements_path) == ["missing"]
