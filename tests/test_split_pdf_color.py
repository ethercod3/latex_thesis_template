from __future__ import annotations

from pathlib import Path

import pytest

import split_pdf_color
from common import ScriptError


def test_split_pdf_color_exports_color_and_bw_pages(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "document.pdf"
    source.write_text("pdf", encoding="utf-8")
    calls: list[tuple[str, ...]] = []

    def fake_run(command: list[str], **kwargs: object) -> object:
        calls.append(tuple(command))
        if "-sDEVICE=inkcov" in command:
            return subprocess_result(
                " 0.00000  0.00000  0.00000  0.10000 CMYK OK\n"
                " 0.01000  0.00000  0.00000  0.20000 CMYK OK\n"
                " 0.00000  0.00000  0.02000  0.30000 CMYK OK\n"
            )
        output = Path(command[-1])
        output.write_text("exported", encoding="utf-8")
        return subprocess_result("")

    monkeypatch.setattr(split_pdf_color, "command_path", lambda command: command if command in {"gs", "qpdf"} else None)
    monkeypatch.setattr(split_pdf_color.subprocess, "run", fake_run)

    color_pages, bw_pages = split_pdf_color.split_pdf_color(source)

    assert color_pages == [2, 3]
    assert bw_pages == [1]
    assert (tmp_path / "document_color.pdf").read_text(encoding="utf-8") == "exported"
    assert (tmp_path / "document_bw.pdf").read_text(encoding="utf-8") == "exported"
    assert any(call[:5] == ("qpdf", "--empty", "--pages", str(source.resolve()), "2-3") for call in calls)
    assert any(call[:5] == ("qpdf", "--empty", "--pages", str(source.resolve()), "1") for call in calls)


def test_page_list_arg_compacts_ranges() -> None:
    assert split_pdf_color.page_list_arg([1, 2, 3, 5, 8, 9]) == "1-3,5,8-9"


def test_split_pdf_color_rejects_non_pdf(tmp_path: Path) -> None:
    source = tmp_path / "document.txt"
    source.write_text("not pdf", encoding="utf-8")

    with pytest.raises(ScriptError, match="Ожидался PDF-файл"):
        split_pdf_color.split_pdf_color(source)


def test_read_page_inks_rejects_empty_inkcov(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "document.pdf"
    source.write_text("pdf", encoding="utf-8")
    monkeypatch.setattr(split_pdf_color, "run_ghostscript", lambda command: subprocess_result(""))

    with pytest.raises(ScriptError, match="не вернул данные inkcov"):
        split_pdf_color.read_page_inks(source, "gs")


def test_normalize_pdf_path_accepts_windows_relative_path() -> None:
    assert split_pdf_color.normalize_pdf_path(Path(r".\build\document.pdf")) == Path("./build/document.pdf")


def subprocess_result(stdout: str) -> object:
    class Result:
        pass

    result = Result()
    result.stdout = stdout
    result.stderr = ""
    return result
