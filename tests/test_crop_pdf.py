from __future__ import annotations

from pathlib import Path

import pytest

import crop_pdf
from common import ScriptError


def test_crop_pdf_replaces_source_with_cropped_file(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "document.pdf"
    source.write_text("original", encoding="utf-8")

    calls: list[tuple[str, ...]] = []

    def fake_run(source_path: Path, cropped_path: Path) -> tuple[int, str, str]:
        calls.append((str(source_path), str(cropped_path)))
        cropped_path.write_text("cropped", encoding="utf-8")
        return 0, "", ""

    monkeypatch.setattr(crop_pdf, "run_pdfcrop", fake_run)

    crop_pdf.crop_pdf(source)

    assert source.read_text(encoding="utf-8") == "cropped"
    assert calls == [(str(source.resolve()), str(source.with_name("document.pdfcrop-tmp.pdf").resolve()))]
    assert not source.with_name("document.pdfcrop-tmp.pdf").exists()


def test_crop_pdf_rejects_non_pdf(tmp_path: Path) -> None:
    source = tmp_path / "document.txt"
    source.write_text("not pdf", encoding="utf-8")

    with pytest.raises(ScriptError, match="Ожидался PDF-файл"):
        crop_pdf.crop_pdf(source)


def test_normalize_pdf_path_accepts_windows_relative_path() -> None:
    assert crop_pdf.normalize_pdf_path(Path(r".\figures\languages.pdf")) == Path("./figures/languages.pdf")
