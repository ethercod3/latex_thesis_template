from pathlib import Path
import subprocess
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_DIR / "python_diagrams"
OUTPUT_DIR = PROJECT_DIR / "figures"

DIAGRAM_SCRIPTS = [
    "languages.py",
    "methodologies.py",
]


def run_diagram(script_name: str) -> int:
    script_path = SOURCE_DIR / script_name

    if not script_path.is_file():
        print(f"[ОШИБКА] Не найден скрипт для диаграммы: {script_path}", file=sys.stderr)
        return 1

    print(f"==> {script_name}", flush=True)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_DIR,
    )

    if result.returncode == 0:
        print(f"[OK] {script_name}")

    return result.returncode


def main() -> int:
    if not SOURCE_DIR.is_dir():
        print(f"Папка со скриптами диаграмм не найдена: {SOURCE_DIR}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for script_name in DIAGRAM_SCRIPTS:
        exit_code = run_diagram(script_name)
        if exit_code != 0:
            return exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
