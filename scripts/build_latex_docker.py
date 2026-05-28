"""Сборка основного LaTeX-документа внутри Docker-контейнера.

Берет имя целевого .tex-файла из переменной TARGET, запускает latexmk с
docker-специфичной директорией временных файлов и очищает промежуточные
артефакты перед сборкой.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from common import ScriptError, script_main

AUX_DIR = Path(".aux_files_docker")


def run_checked(command: list[str]) -> tuple[int, str, str]:
    print(f"==> {' '.join(command)}", flush=True)
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    code, stdout, stderr = result.returncode, result.stdout, result.stderr
    if code != 0:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        raise ScriptError(f"Команда завершилась с ошибкой (код {code}): {' '.join(command)}\n{details}")
    return code, stdout, stderr


def main() -> int:
    target = os.environ.get("TARGET")
    if not target:
        raise ScriptError("Не задан TARGET. Укажите TARGET в файле .env.")

    target_path = Path(target)
    if target_path.suffix != ".tex":
        raise ScriptError(f"TARGET должен указывать на .tex файл, получено: {target}")

    base = target_path.stem

    AUX_DIR.mkdir(exist_ok=True)

    run_checked(
        [
            "latexmk",
            "-lualatex",
            "-shell-escape",
            f"-auxdir={AUX_DIR}",
            "-outdir=.",
            target,
        ]
    )

    pdf_path = Path(f"{base}.pdf")
    if not pdf_path.is_file():
        raise ScriptError(
            f"PDF-файл не был создан там, где ожидалось: {pdf_path}. " "Проверьте сообщения latexmk выше."
        )

    return 0


if __name__ == "__main__":
    sys.exit(script_main(main))
