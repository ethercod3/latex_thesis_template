from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

from common import require_command

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


def remove_blank_pages(input_file: Path, output_file: Path, tmp_dir: Path) -> None:
    bbox_result = subprocess.run(
        ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=bbox", str(input_file)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )

    keep_pages: list[str] = []
    page = 0

    for line in bbox_result.stderr.splitlines():
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

    subprocess.run(
        ["qpdf", "--empty", "--pages", str(input_file), *keep_pages, "--", str(reduced_file)],
        check=True,
    )

    copy_pdf_contents(reduced_file, output_file)


def convert_docx(source_file: Path, tmp_dir: Path) -> Path:
    print(f"Конвертирую {source_file}")

    subprocess.run(
        [
            "soffice",
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            "--nodefault",
            "--nolockcheck",
            "--convert-to",
            PDF_EXPORT_FILTER,
            "--outdir",
            str(tmp_dir),
            str(source_file),
        ],
        check=True,
    )

    converted_file = tmp_dir / f"{source_file.stem}.pdf"

    if not converted_file.is_file():
        raise FileNotFoundError(f"LibreOffice не создал ожидаемый PDF-файл: {converted_file}")

    return converted_file


def main() -> int:
    required_commands = ["soffice"]

    if SKIP_BLANK_PAGES:
        required_commands.extend(["gs", "qpdf"])

    for command in required_commands:
        require_command(command)

    if not INPUT_DIR.is_dir():
        print(f"Папка с DOCX-файлами не найдена: {INPUT_DIR}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    source_files = sorted(INPUT_DIR.glob("*.docx"))

    if not source_files:
        print(f"В папке {INPUT_DIR} не найдены .docx-файлы для конвертации.", file=sys.stderr)
        return 1

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
    try:
        raise SystemExit(main())
    except FileNotFoundError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    except RuntimeError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
    except subprocess.CalledProcessError as error:
        print(
            f"Команда завершилась с ошибкой (код {error.returncode}): {' '.join(error.cmd)}",
            file=sys.stderr,
        )
        print("Проверьте сообщения выше: там обычно указана причина ошибки.", file=sys.stderr)
        raise SystemExit(error.returncode)
