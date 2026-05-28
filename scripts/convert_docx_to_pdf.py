"""Конвертация DOCX-документов в PDF через LibreOffice.

Используется в Docker-сервисе docx_pdf: берет входные файлы из DOCX_INPUT_DIR,
экспортирует PDF и по умолчанию удаляет пустые страницы из результата.
"""

from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

from common import ScriptError, require_command, script_main

INPUT_DIR = Path(os.environ.get("DOCX_INPUT_DIR", "/data/docx"))
OUTPUT_DIR = Path(os.environ.get("PDF_OUTPUT_DIR", "/data"))
PDF_EXPORT_FILTER = 'pdf:writer_pdf_Export:{"IsSkipEmptyPages":{"type":"boolean","value":"true"}}'
SKIP_BLANK_PAGES = os.environ.get("SKIP_BLANK_PAGES", "1") == "1"


def copy_pdf_contents(source: Path, destination: Path) -> None:
    shutil.copyfile(source, destination)


def is_blank_bbox_line(line: str) -> bool:
    parts = line.split()

    if len(parts) < 5:
        return False

    return parts[1:5] == ["0", "0", "0", "0"]


def run_external(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def run_checked(command: list[str]) -> tuple[int, str, str]:
    print(f"==> {' '.join(command)}", flush=True)
    code, stdout, stderr = run_external(command)
    if code != 0:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        raise ScriptError(f"Команда завершилась с ошибкой (код {code}): {' '.join(command)}\n{details}")
    return code, stdout, stderr


def remove_blank_pages(input_file: Path, output_file: Path, tmp_dir: Path) -> None:
    _, _, stderr = run_checked(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=bbox", str(input_file)])

    keep_pages: list[str] = []
    page = 0

    for line in stderr.splitlines():
        if not line.startswith("%%BoundingBox:"):
            continue

        page += 1

        if is_blank_bbox_line(line):
            print(f"Пропускаю пустую страницу {page} в файле {input_file}")
        else:
            keep_pages.append(str(page))

    if page == 0 or len(keep_pages) == page:
        copy_pdf_contents(input_file, output_file)
        return

    if not keep_pages:
        print(
            f"Все страницы выглядят пустыми в файле {input_file}; оставляю исходный PDF.",
            file=sys.stderr,
        )
        copy_pdf_contents(input_file, output_file)
        return

    reduced_file = tmp_dir / f"{input_file.stem}.without_blank_pages.pdf"

    run_checked(["qpdf", "--empty", "--pages", str(input_file), *keep_pages, "--", str(reduced_file)])

    copy_pdf_contents(reduced_file, output_file)


def convert_docx(source_file: Path, tmp_dir: Path) -> Path:
    print(f"Конвертирую {source_file}")
    libreoffice_profile = tmp_dir / "libreoffice-profile"

    run_checked(
        [
            "soffice",
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            "--nodefault",
            "--nolockcheck",
            f"-env:UserInstallation=file://{libreoffice_profile}",
            "--convert-to",
            PDF_EXPORT_FILTER,
            "--outdir",
            str(tmp_dir),
            str(source_file),
        ]
    )

    converted_file = tmp_dir / f"{source_file.stem}.pdf"

    if not converted_file.is_file():
        raise ScriptError(f"LibreOffice не создал ожидаемый PDF-файл: {converted_file}")

    return converted_file


def main() -> int:
    required_commands = ["soffice"]

    if SKIP_BLANK_PAGES:
        required_commands.extend(["gs", "qpdf"])

    for command in required_commands:
        require_command(command)

    if not INPUT_DIR.is_dir():
        raise ScriptError(f"Папка с DOCX-файлами не найдена: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    source_files = sorted(INPUT_DIR.glob("*.docx"))

    if not source_files:
        raise ScriptError(f"В папке {INPUT_DIR} не найдены .docx-файлы для конвертации.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        for source_file in source_files:
            output_file = OUTPUT_DIR / f"{source_file.stem}.pdf"
            converted_file = convert_docx(source_file, tmp_dir)

            print(f"Записываю {output_file}")

            if SKIP_BLANK_PAGES:
                remove_blank_pages(converted_file, output_file, tmp_dir)
            else:
                copy_pdf_contents(converted_file, output_file)

            converted_file.unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    sys.exit(script_main(main))
