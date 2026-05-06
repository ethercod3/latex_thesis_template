from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


AUX_DIR = Path(".aux_files_docker")


def run(command: list[str], *, allow_failure: bool = False) -> None:
    print("+ " + " ".join(command), flush=True)
    result = subprocess.run(command)
    if result.returncode != 0 and not allow_failure:
        raise subprocess.CalledProcessError(result.returncode, command)


def main() -> None:
    target = os.environ.get("TARGET")
    if not target:
        raise SystemExit("Не задан TARGET. Укажите TARGET в файле .env.")

    target_path = Path(target)
    base = target_path.name.removesuffix(".tex")

    AUX_DIR.mkdir(exist_ok=True)
    for suffix in (".bcf", ".bbl", ".blg", ".run.xml", ".fdb_latexmk"):
        (AUX_DIR / f"{base}{suffix}").unlink(missing_ok=True)
        Path(f"{base}{suffix}").unlink(missing_ok=True)

    lualatex = [
        "lualatex",
        "-synctex=0",
        "-interaction=nonstopmode",
        f"-output-directory={AUX_DIR}",
        target,
    ]

    run(lualatex, allow_failure=True)
    run(["biber", str(AUX_DIR / f"{base}.bcf")])
    run(lualatex)
    run(lualatex)

    aux_pdf = AUX_DIR / f"{base}.pdf"
    if not aux_pdf.is_file():
        raise FileNotFoundError(
            f"PDF-файл не был создан там, где ожидалось: {aux_pdf}. "
            "Проверьте сообщения LaTeX выше."
        )

    shutil.copy2(aux_pdf, Path(".") / f"{base}.pdf")


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
        print("Проверьте сообщения выше: там обычно указана причина ошибки сборки.", file=sys.stderr)
        raise SystemExit(error.returncode)
