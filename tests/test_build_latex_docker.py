from __future__ import annotations

from pathlib import Path

import build_latex_docker as latex


def test_main_builds_through_ascii_entrypoint_and_restores_pdf_name(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "Иванов_Г000_диплом.tex"
    target.write_text(r"\documentclass{article}\begin{document}ok\end{document}", encoding="utf-8")
    calls: list[list[str]] = []
    build_tex = latex.build_entrypoint_for(Path(target.name))
    build_pdf = build_tex.with_suffix(".pdf")

    def fake_run_checked(command: list[str]) -> tuple[int, str, str]:
        calls.append(command)
        assert (tmp_path / build_tex).read_text(encoding="utf-8") == target.read_text(encoding="utf-8")
        (tmp_path / build_pdf).write_bytes(b"%PDF-1.4\n%%EOF\n")
        return 0, "", ""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TARGET", target.name)
    monkeypatch.setattr(latex, "run_checked", fake_run_checked)

    assert latex.main() == 0

    assert calls == [
        [
            "latexmk",
            "-lualatex",
            "-shell-escape",
            f"-auxdir={latex.AUX_DIR}",
            "-outdir=.",
            str(build_tex),
        ]
    ]
    assert build_tex.name.startswith("__latex_build_")
    assert build_tex.name.isascii()
    assert not (tmp_path / build_tex).exists()
    assert not (tmp_path / build_pdf).exists()
    assert (tmp_path / "Иванов_Г000_диплом.pdf").read_bytes() == b"%PDF-1.4\n%%EOF\n"
