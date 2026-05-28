from __future__ import annotations

import check_tools_exe


def test_smoke_allows_nonzero_exit_code(monkeypatch, capsys) -> None:
    monkeypatch.setattr(check_tools_exe, "run_exe", lambda: (1, "stdout text\n", "stderr text\n"))

    check_tools_exe.smoke()

    output = capsys.readouterr().out
    assert "Smoke test finished with exit code 1" in output
    assert "stdout text" in output
    assert "stderr text" in output
