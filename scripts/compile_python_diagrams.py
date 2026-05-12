"""Генерация диаграмм, описанных Python-скриптами.

Запускает фиксированный набор файлов из python_diagrams/ и ожидает, что они
запишут итоговые изображения в figures/.
"""

import sys

from common import PROJECT_DIR, ScriptError, run_command, script_main

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

    result = run_command(
        [sys.executable, str(script_path)],
        check=False,
    )

    if result.returncode == 0:
        print(f"[OK] {script_name}")

    return result.returncode


def main() -> int:
    if not SOURCE_DIR.is_dir():
        raise ScriptError(f"Папка со скриптами диаграмм не найдена: {SOURCE_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for script_name in DIAGRAM_SCRIPTS:
        exit_code = run_diagram(script_name)
        if exit_code != 0:
            return exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
