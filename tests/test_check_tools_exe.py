from __future__ import annotations

import subprocess
import check_tools_exe


def test_smoke_allows_nonzero_exit_code(monkeypatch, capsys) -> None:
    monkeypatch.setattr(check_tools_exe, "run_exe", lambda: (1, "stdout text\n", "stderr text\n"))

    check_tools_exe.smoke()

    output = capsys.readouterr().out
    assert "Smoke test finished with exit code 1" in output
    assert "stdout text" in output
    assert "stderr text" in output


def test_run_exe_decodes_utf8_output(monkeypatch) -> None:
    result = subprocess.CompletedProcess(
        args=[str(check_tools_exe.EXE_PATH)],
        returncode=1,
        stdout="Проверка состояния проекта\n".encode("utf-8"),
        stderr="Ошибка\n".encode("utf-8"),
    )
    monkeypatch.setattr(check_tools_exe.subprocess, "run", lambda *args, **kwargs: result)

    code, stdout, stderr = check_tools_exe.run_exe()

    assert code == 1
    assert stdout == "Проверка состояния проекта\n"
    assert stderr == "Ошибка\n"


def test_encode_safe_replaces_unencodable_characters() -> None:
    assert check_tools_exe.encode_safe("Проверка", "cp1252") == "????????"
