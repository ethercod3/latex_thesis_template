"""Обрезать поля PDF через pdfcrop и заменить исходный файл."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from plumbum import local
import typer

from common import ScriptError, command_path

TIMEOUT_SECONDS = 120


def normalize_pdf_path(pdf_path: Path) -> Path:
    return Path(str(pdf_path).replace("\\", "/"))


def run_pdfcrop(source: Path, cropped: Path) -> tuple[int, str, str]:
    pdfcrop = command_path("pdfcrop") or command_path("pdfcrop.cmd")
    if pdfcrop is None:
        raise ScriptError("Не найдена программа pdfcrop. Установите TeX Live/MiKTeX с pdfcrop.")

    print(f"==> {pdfcrop} {source} {cropped}", flush=True)
    command = local[pdfcrop]
    for arg in (str(source), str(cropped)):
        command = command[arg]
    return command.run()


def crop_pdf(pdf_path: Path) -> None:
    normalized_path = normalize_pdf_path(pdf_path)
    source = normalized_path.expanduser().resolve()
    if not source.is_file():
        raise ScriptError(f"PDF-файл не найден: {pdf_path}")
    if source.suffix.lower() != ".pdf":
        raise ScriptError(f"Ожидался PDF-файл с расширением .pdf: {pdf_path}")

    cropped = source.with_name(f"{source.stem}.pdfcrop-tmp{source.suffix}")
    try:
        code, stdout, stderr = run_pdfcrop(source, cropped)
        if code != 0:
            details = (
                "Не удалось обрезать PDF.\n"
                f"Команда: pdfcrop {source} {cropped}\n"
                f"Обычный вывод:\n{stdout.strip() or 'вывода нет'}\n"
                f"Вывод ошибок:\n{stderr.strip() or 'вывода ошибок нет'}"
            )
            raise ScriptError(details)
        os.replace(cropped, source)
    finally:
        if cropped.exists():
            cropped.unlink()

    print(f"[OK] {source}")


def main(pdf: Path = typer.Argument(..., help="Путь к PDF-файлу.")) -> None:
    try:
        crop_pdf(pdf)
    except ScriptError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
