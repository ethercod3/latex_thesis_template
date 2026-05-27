"""Генерация диаграмм, описанных Python-скриптами.

Запускает фиксированный набор файлов из python_diagrams/ и ожидает, что они
запишут итоговые изображения в figures/.
"""

from __future__ import annotations

import sys

from plumbum import local
import typer

from common import PROJECT_DIR, ScriptError

SOURCE_DIR = PROJECT_DIR / "python_diagrams"
OUTPUT_DIR = PROJECT_DIR / "figures"

DIAGRAM_SCRIPTS = [
    "languages.py",
    "methodologies.py",
]


def run_diagram(script_name: str) -> int:
    script_path = SOURCE_DIR / script_name

    if not script_path.is_file():
        raise ScriptError(f"Не найден скрипт для диаграммы: {script_path}")

    print(f"==> {script_name}", flush=True)

    code, stdout, stderr = local[sys.executable][str(script_path)].run()

    if code == 0:
        print(f"[OK] {script_name}")
    else:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        print(f"[ОШИБКА] {script_name}\n{details}")

    return code


def main() -> None:
    if not SOURCE_DIR.is_dir():
        raise ScriptError(f"Папка со скриптами диаграмм не найдена: {SOURCE_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for script_name in DIAGRAM_SCRIPTS:
        exit_code = run_diagram(script_name)
        if exit_code != 0:
            raise typer.Exit(code=exit_code)


if __name__ == "__main__":
    typer.run(main)
