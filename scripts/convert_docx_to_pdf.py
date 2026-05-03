from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile


INPUT_DIR = Path(os.environ.get("DOCX_INPUT_DIR", "/data/docx"))
OUTPUT_DIR = Path(os.environ.get("PDF_OUTPUT_DIR", "/data"))
PDF_EXPORT_FILTER = (
    'pdf:writer_pdf_Export:{"IsSkipEmptyPages":{"type":"boolean","value":"true"}}'
)
SKIP_BLANK_PAGES = os.environ.get("SKIP_BLANK_PAGES", "1") == "1"


def require_command(command: str) -> bool:
    if shutil.which(command) is None:
        print(f"Required command was not found in PATH: {command}", file=sys.stderr)
        return False

    return True


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
            print(f"Skipping blank page {page} in {input_file}")
        else:
            keep_pages.append(str(page))

    if page == 0 or len(keep_pages) == page:
        shutil.copy2(input_file, output_file)
        return

    if not keep_pages:
        print(f"All pages look blank in {input_file}; keeping original PDF", file=sys.stderr)
        shutil.copy2(input_file, output_file)
        return

    reduced_file = tmp_dir / f"{input_file.stem}.without_blank_pages.pdf"

    subprocess.run(
        ["qpdf", "--empty", "--pages", str(input_file), *keep_pages, "--", str(reduced_file)],
        check=True,
    )

    shutil.copy2(reduced_file, output_file)


def convert_docx(source_file: Path, tmp_dir: Path) -> Path:
    print(f"Converting {source_file}")

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
        raise FileNotFoundError(f"LibreOffice did not produce expected file: {converted_file}")

    return converted_file


def main() -> int:
    required_commands = ["soffice"]

    if SKIP_BLANK_PAGES:
        required_commands.extend(["gs", "qpdf"])

    if not all(require_command(command) for command in required_commands):
        return 1

    if not INPUT_DIR.is_dir():
        print(f"Input directory not found: {INPUT_DIR}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    source_files = sorted(INPUT_DIR.glob("*.docx"))

    if not source_files:
        print(f"No .docx files found in {INPUT_DIR}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        for source_file in source_files:
            output_file = OUTPUT_DIR / f"{source_file.stem}.pdf"
            converted_file = convert_docx(source_file, tmp_dir)

            print(f"Writing {output_file}")

            if SKIP_BLANK_PAGES:
                remove_blank_pages(converted_file, output_file, tmp_dir)
            else:
                shutil.copy2(converted_file, output_file)

            converted_file.unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(f"Command failed with exit code {error.returncode}: {error.cmd}", file=sys.stderr)
        raise SystemExit(error.returncode)
