from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values

import run_pdf_diff as diff


def test_build_command_resolves_project_env_and_derives_pdf(tmp_path: Path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                'TARGET="main.tex"',
                'VAULT_OS_PATH="../vault_diploma"',
                'VAULT_PATH="/vault_code"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(diff, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(diff, "CONFIG_PATH", tmp_path / "diff_config.toml")
    monkeypatch.setattr(diff, "env_value", lambda name: dotenv_values(env_path).get(name))

    config = {
        "build": "task pdf",
        "pdf_from_target": True,
        "view": True,
        "env": {
            "VAULT_PATH": {"from_env": "VAULT_PATH"},
            "VAULT_OS_PATH": {"from_env": "VAULT_OS_PATH", "resolve": True},
            "PYTHONUTF8": "1",
        },
        "copy": {"paths": [".env", "docker-compose.yaml"]},
    }

    command = diff.build_command(config, ["--env", "TARGET=diff.tex", "left", "right"])

    assert command[:5] == ["uvx", "diff-pdf-commits", "--build", "task pdf", "--pdf"]
    assert command[5] == "diff.pdf"
    assert "--view" in command
    assert ["--copy", ".env"] == command[command.index("--copy") : command.index("--copy") + 2]
    assert f"VAULT_OS_PATH={(tmp_path.parent / 'vault_diploma').resolve()}" in command
    assert "VAULT_PATH=/vault_code" in command
    assert command[-4:] == ["--env", "TARGET=diff.tex", "left", "right"]


def test_build_command_preserves_explicit_pdf(tmp_path: Path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text('TARGET="main.tex"\n', encoding="utf-8")
    monkeypatch.setattr(diff, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(diff, "env_value", lambda name: dotenv_values(env_path).get(name))

    config = {"build": "task pdf", "pdf_from_target": True, "env": {}, "copy": {"paths": []}}

    command = diff.build_command(config, ["--pdf", "custom.pdf", "left", "right"])

    assert command.count("--pdf") == 1
    assert command[-4:] == ["--pdf", "custom.pdf", "left", "right"]
