"""Компиляция Mermaid-диаграмм из mermaid/ в figures/.

Находит локальный mmdc, параллельно обрабатывает исходники диаграмм,
обрезает поля через pdfcrop и сохраняет PDF рядом с остальными
иллюстрациями диплома.
"""

import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from common import PROJECT_DIR, ScriptError, command_path, script_main

SRC = PROJECT_DIR / "mermaid"
DST = PROJECT_DIR / "figures"

EXTENSIONS = {".mmd", ".mermaid", ".mmdc"}
MAX_WORKERS_LIMIT = 4
TIMEOUT_SECONDS = 60


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Сгенерировать Mermaid-диаграммы из mermaid/ в figures/.")
    parser.add_argument(
        "--no-crop",
        action="store_true",
        help="Не запускать pdfcrop после генерации PDF.",
    )
    return parser.parse_args()


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


def crop_pdf(output_file: Path, pdfcrop: list[str]) -> None:
    cropped_file = output_file.with_name(f"{output_file.stem}.pdfcrop-tmp{output_file.suffix}")
    cmd = [*pdfcrop, str(output_file), str(cropped_file)]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
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

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        if pdfcrop is not None:
            crop_pdf(output_file, pdfcrop)

        return f"[OK] {f.name} -> {output_file.name}"

    except subprocess.TimeoutExpired:
        return f"[ОШИБКА] {f.name}: сборка заняла больше {TIMEOUT_SECONDS} секунд"

    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else "вывода нет"
        stderr = e.stderr.strip() if e.stderr else "вывода ошибок нет"

        return (
            f"[ОШИБКА] Не удалось собрать диаграмму {f.name}\n"
            f"Команда: {' '.join(e.cmd)}\n"
            f"Обычный вывод:\n{stdout}\n"
            f"Вывод ошибок:\n{stderr}"
        )


def main() -> int:
    args = parse_args()

    if not SRC.exists():
        raise ScriptError(f"Папка с Mermaid-диаграммами не найдена: {SRC}")

    DST.mkdir(parents=True, exist_ok=True)
    mmdc = find_mmdc()
    pdfcrop = None if args.no_crop else find_pdfcrop()

    files = [f for f in SRC.iterdir() if f.is_file() and f.suffix.lower() in EXTENSIONS]

    if not files:
        print(f"В папке {SRC} не найдены Mermaid-файлы для сборки.")
        return 0

    max_workers = min(MAX_WORKERS_LIMIT, len(files))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, f, mmdc, pdfcrop): f for f in files}

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    print(result)
            except Exception as e:
                f = futures[future]
                print(f"[ОШИБКА] Не удалось обработать {f.name}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
