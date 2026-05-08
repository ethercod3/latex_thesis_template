from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from common import run_command


AUX_DIR = Path(".aux_files_docker")


def main() -> None:
    target = os.environ.get("TARGET")
    if not target:
        raise SystemExit("Не задан TARGET. Укажите TARGET в файле .env.")

    target_path = Path(target)
    if target_path.suffix != ".tex":
        raise SystemExit(f"TARGET должен указывать на .tex файл, получено: {target}")

    base = target_path.stem

    AUX_DIR.mkdir(exist_ok=True)

    run_command(
        [
            "latexmk",
            "-lualatex",
            f"-auxdir={AUX_DIR}",
            "-outdir=.",
            target,
        ]
    )

    pdf_path = Path(f"{base}.pdf")
    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF-файл не был создан там, где ожидалось: {pdf_path}. "
            "Проверьте сообщения latexmk выше."
        )


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    except subprocess.CalledProcessError as error:
        print(
            f"Команда завершилась с ошибкой (код {error.returncode}): {' '.join(error.cmd)}",
            file=sys.stderr,
        )
        print("Проверьте сообщения latexmk выше: там обычно указана причина ошибки сборки.", file=sys.stderr)
        raise SystemExit(error.returncode)
