"""Компиляция Mermaid-диаграмм из mermaid/ в figures/.

Находит локальный mmdc, параллельно обрабатывает исходники диаграмм,
обрезает поля через pdfcrop и сохраняет PDF рядом с остальными
иллюстрациями диплома.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys

from common import PROJECT_DIR, ScriptError, command_path

SRC = PROJECT_DIR / "mermaid"
DST = PROJECT_DIR / "figures"

EXTENSIONS = {".mmd", ".mermaid", ".mmdc"}
MAX_WORKERS_LIMIT = 4
TIMEOUT_SECONDS = 60


def find_mmdc() -> list[str]:
    mmdc = command_path("mmdc") or command_path("mmdc.cmd")
    if mmdc is None:
        raise ScriptError(
            "Не найдена программа mmdc для сборки Mermaid-диаграмм. "
            "Установите Mermaid CLI и убедитесь, что команда 'mmdc' доступна в терминале."
        )

    return [mmdc]


def find_pdfcrop() -> list[str]:
    pdfcrop = command_path("pdfcrop") or command_path("pdfcrop.cmd")
    if pdfcrop is None:
        raise ScriptError(
            "Не найдена программа pdfcrop для обрезки Mermaid-диаграмм. "
            "Установите TeX Live/MiKTeX с pdfcrop или запустите скрипт с флагом --no-crop."
        )

    return [pdfcrop]


def run_external(command: list[str], timeout: int = TIMEOUT_SECONDS) -> tuple[int, str, str]:
    result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def crop_pdf(output_file: Path, pdfcrop: list[str]) -> None:
    cropped_file = output_file.with_name(f"{output_file.stem}.pdfcrop-tmp{output_file.suffix}")
    cmd = [*pdfcrop, str(output_file), str(cropped_file)]

    try:
        code, stdout, stderr = run_external(cmd)
        if code != 0:
            details = (stderr or stdout).strip()
            raise ScriptError(f"Не удалось обрезать Mermaid-PDF.\nКоманда: {' '.join(cmd)}\n{details}")
        os.replace(cropped_file, output_file)
    finally:
        if cropped_file.exists():
            cropped_file.unlink()


def process_file(f: Path, mmdc: list[str], pdfcrop: list[str] | None) -> str | None:
    if not f.is_file():
        return None

    if f.suffix.lower() not in EXTENSIONS:
        return None

    output_file = DST / f"{f.stem}.pdf"
    cmd = [*mmdc, "-i", str(f), "-o", str(output_file), "-f"]

    code, stdout, stderr = run_external(cmd)
    if code != 0:
        details = (stderr or stdout).strip()
        return (
            f"[ОШИБКА] Не удалось собрать диаграмму {f.name}\n"
            f"Команда: {' '.join(cmd)}\n"
            f"Обычный вывод:\n{stdout.strip() or 'вывода нет'}\n"
            f"Вывод ошибок:\n{details or 'вывода ошибок нет'}"
        )

    if pdfcrop is not None:
        crop_pdf(output_file, pdfcrop)

    return f"[OK] {f.name} -> {output_file.name}"


def run(no_crop: bool = False) -> int:
    try:
        if not SRC.exists():
            raise ScriptError(f"Папка с Mermaid-диаграммами не найдена: {SRC}")

        DST.mkdir(parents=True, exist_ok=True)
        mmdc = find_mmdc()
        pdfcrop = None if no_crop else find_pdfcrop()

        files = [f for f in SRC.iterdir() if f.is_file() and f.suffix.lower() in EXTENSIONS]

        if not files:
            print(f"В папке {SRC} не найдены Mermaid-файлы для сборки.")
            return 0

        max_workers = min(MAX_WORKERS_LIMIT, len(files))
        has_errors = False

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_file, f, mmdc, pdfcrop): f for f in files}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        print(result)
                        if result.startswith("[ОШИБКА]"):
                            has_errors = True
                except Exception as e:
                    f = futures[future]
                    print(f"[ОШИБКА] Не удалось обработать {f.name}: {e}")
                    has_errors = True

        if has_errors:
            return 1
    except ScriptError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    return 0


def main(no_crop: bool = False) -> None:
    exit_code = run(no_crop=no_crop)
    if exit_code != 0:
        import typer

        raise typer.Exit(code=exit_code)


def cli() -> int:
    args = sys.argv[1:]
    allowed = {"--no-crop"}
    unknown = [arg for arg in args if arg not in allowed]
    if unknown:
        print(f"Неизвестные аргументы: {' '.join(unknown)}", file=sys.stderr)
        return 2
    return run(no_crop="--no-crop" in args)


if __name__ == "__main__":
    sys.exit(cli())
