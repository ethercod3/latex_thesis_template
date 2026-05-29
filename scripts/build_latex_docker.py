"""Сборка основного LaTeX-документа внутри Docker-контейнера.

Берет имя целевого .tex-файла из переменной TARGET, запускает latexmk с
docker-специфичной директорией временных файлов и очищает промежуточные
артефакты перед сборкой.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

from common import ScriptError, script_main

AUX_DIR = Path(".aux_files_docker")
BUILD_TEX = Path("__latex_build_entrypoint__.tex")
BUILD_PDF = Path("__latex_build_entrypoint__.pdf")


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
    if target_path.is_absolute() or ".." in target_path.parts:
        raise ScriptError(f"TARGET должен быть путем внутри проекта, получено: {target}")
    if not target_path.is_file():
        raise ScriptError(f"TARGET не найден: {target}")

    base = target_path.stem
    pdf_path = Path(f"{base}.pdf")

    AUX_DIR.mkdir(exist_ok=True)
    if BUILD_PDF.exists():
        BUILD_PDF.unlink()
    if pdf_path.exists():
        pdf_path.unlink()
    shutil.copy2(target_path, BUILD_TEX)

    try:
        run_checked(
            [
                "latexmk",
                "-lualatex",
                "-shell-escape",
                f"-auxdir={AUX_DIR}",
                "-outdir=.",
                str(BUILD_TEX),
            ]
        )
    finally:
        if BUILD_TEX.exists():
            BUILD_TEX.unlink()

    if BUILD_PDF.is_file():
        shutil.move(str(BUILD_PDF), pdf_path)
    if not pdf_path.is_file():
        raise ScriptError(
            f"PDF-файл не был создан там, где ожидалось: {pdf_path}. " "Проверьте сообщения latexmk выше."
        )

    return 0


if __name__ == "__main__":
    sys.exit(script_main(main))
