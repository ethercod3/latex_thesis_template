import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from common import PROJECT_DIR

SRC = PROJECT_DIR / "mermaid"
DST = PROJECT_DIR / "figures"

EXTENSIONS = {".mmd", ".mermaid", ".mmdc"}
MAX_WORKERS_LIMIT = 4
TIMEOUT_SECONDS = 60


def find_mmdc() -> list[str]:
    mmdc = shutil.which("mmdc") or shutil.which("mmdc.cmd")
    if mmdc is None:
        raise RuntimeError(
            "Не найдена программа mmdc для сборки Mermaid-диаграмм. "
            "Установите Mermaid CLI и убедитесь, что команда 'mmdc' доступна в терминале."
        )

    return [mmdc]


def process_file(f: Path, mmdc: list[str]) -> str | None:
    if not f.is_file():
        return None

    if f.suffix.lower() not in EXTENSIONS:
        return None

    output_file = DST / f"{f.stem}.pdf"

    cmd = [*mmdc, "-i", str(f), "-o", str(output_file), "-f"]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        return f"[OK] {f.name} -> {output_file.name}"

    except subprocess.TimeoutExpired:
        return f"[ОШИБКА] {f.name}: сборка заняла больше {TIMEOUT_SECONDS} секунд"

    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else "вывода нет"
        stderr = e.stderr.strip() if e.stderr else "вывода ошибок нет"

        return (
            f"[ОШИБКА] Не удалось собрать диаграмму {f.name}\n"
            f"Команда: {' '.join(cmd)}\n"
            f"Обычный вывод:\n{stdout}\n"
            f"Вывод ошибок:\n{stderr}"
        )


def main() -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Папка с Mermaid-диаграммами не найдена: {SRC}")

    mmdc = find_mmdc()

    files = [f for f in SRC.iterdir() if f.is_file() and f.suffix.lower() in EXTENSIONS]

    if not files:
        print(f"В папке {SRC} не найдены Mermaid-файлы для сборки.")
        return

    max_workers = min(MAX_WORKERS_LIMIT, len(files))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, f, mmdc): f for f in files}

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    print(result)
            except Exception as e:
                f = futures[future]
                print(f"[ОШИБКА] Не удалось обработать {f.name}: {e}")


if __name__ == "__main__":
    try:
        DST.mkdir(parents=True, exist_ok=True)
        main()
    except (RuntimeError, FileNotFoundError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
