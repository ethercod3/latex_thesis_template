"""Сборка основного LaTeX-документа внутри Docker-контейнера.

Берет имя целевого .tex-файла из переменной TARGET, запускает latexmk с
docker-специфичной директорией временных файлов и очищает промежуточные
артефакты перед сборкой.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

from common import ScriptError, script_main

AUX_DIR = Path(".aux_files_docker")


def build_entrypoint_for(target_path: Path) -> Path:
    digest = hashlib.sha256(target_path.as_posix().encode("utf-8")).hexdigest()[:12]
    return Path(f"__latex_build_{digest}.tex")


def run_checked(command: list[str]) -> tuple[int, str, str]:
    print(f"==> {' '.join(command)}", flush=True)
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    code, stdout, stderr = result.returncode, result.stdout, result.stderr
    if code != 0:
        parts = []
        if stdout.strip():
            parts.append(f"[stdout]\n{stdout.strip()}")
        if stderr.strip():
            parts.append(f"[stderr]\n{stderr.strip()}")
        details = "\n\n".join(parts) or "вывода нет"
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
    build_tex = build_entrypoint_for(target_path)
    build_pdf = build_tex.with_suffix(".pdf")

    AUX_DIR.mkdir(exist_ok=True)
    if build_pdf.exists():
        build_pdf.unlink()
    if pdf_path.exists():
        pdf_path.unlink()
    shutil.copy2(target_path, build_tex)

    try:
        run_checked(
            [
                "latexmk",
                "-lualatex",
                "-shell-escape",
                f"-auxdir={AUX_DIR}",
                "-outdir=.",
                str(build_tex),
            ]
        )
    finally:
        if build_tex.exists():
            build_tex.unlink()

    if build_pdf.is_file():
        shutil.move(str(build_pdf), pdf_path)
    if not pdf_path.is_file():
        raise ScriptError(
            f"PDF-файл не был создан там, где ожидалось: {pdf_path}. " "Проверьте сообщения latexmk выше."
        )

    return 0


if __name__ == "__main__":
    sys.exit(script_main(main))
