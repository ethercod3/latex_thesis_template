"""Обрезать поля PDF через pdfcrop и заменить исходный файл."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from common import ScriptError, command_path, script_main

TIMEOUT_SECONDS = 120


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Обрезать поля PDF и обновить исходный файл.")
    parser.add_argument("pdf", type=Path, help="Путь к PDF-файлу.")
    return parser.parse_args()


def normalize_pdf_path(pdf_path: Path) -> Path:
    return Path(str(pdf_path).replace("\\", "/"))


def crop_pdf(pdf_path: Path) -> None:
    normalized_path = normalize_pdf_path(pdf_path)
    source = normalized_path.expanduser().resolve()
    if not source.is_file():
        raise ScriptError(f"PDF-файл не найден: {pdf_path}")
    if source.suffix.lower() != ".pdf":
        raise ScriptError(f"Ожидался PDF-файл с расширением .pdf: {pdf_path}")

    pdfcrop = command_path("pdfcrop") or command_path("pdfcrop.cmd")
    if pdfcrop is None:
        raise ScriptError("Не найдена программа pdfcrop. Установите TeX Live/MiKTeX с pdfcrop.")

    cropped = source.with_name(f"{source.stem}.pdfcrop-tmp{source.suffix}")
    try:
        subprocess.run(
            [pdfcrop, str(source), str(cropped)],
            check=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        os.replace(cropped, source)
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else "вывода нет"
        stderr = e.stderr.strip() if e.stderr else "вывода ошибок нет"
        raise ScriptError(
            "Не удалось обрезать PDF.\n"
            f"Команда: {' '.join(e.cmd)}\n"
            f"Обычный вывод:\n{stdout}\n"
            f"Вывод ошибок:\n{stderr}"
        ) from e
    finally:
        if cropped.exists():
            cropped.unlink()

    print(f"[OK] {source}")


def main() -> int:
    args = parse_args()
    crop_pdf(args.pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
