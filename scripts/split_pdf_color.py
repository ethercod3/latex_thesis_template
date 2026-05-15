"""Разделить PDF на цветные и черно-белые страницы."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from common import ScriptError, command_path, script_main

TIMEOUT_SECONDS = 300
INKCOV_RE = re.compile(
    r"^\s*(?P<c>\d+(?:\.\d+)?)\s+"
    r"(?P<m>\d+(?:\.\d+)?)\s+"
    r"(?P<y>\d+(?:\.\d+)?)\s+"
    r"(?P<k>\d+(?:\.\d+)?)\s+CMYK\b"
)


@dataclass(frozen=True)
class PageInk:
    page: int
    cyan: float
    magenta: float
    yellow: float
    black: float

    def is_color(self, threshold: float) -> bool:
        return max(self.cyan, self.magenta, self.yellow) > threshold


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Создать PDF только с цветными страницами (*_color.pdf) и только с ЧБ страницами (*_bw.pdf)."
    )
    parser.add_argument("pdf", type=Path, help="Путь к исходному PDF.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.00001,
        help="Минимальное покрытие C/M/Y, выше которого страница считается цветной.",
    )
    return parser.parse_args()


def normalize_pdf_path(pdf_path: Path) -> Path:
    return Path(str(pdf_path).replace("\\", "/"))


def ghostscript_path() -> str:
    for command in ("gs", "gswin64c", "gswin32c"):
        path = command_path(command)
        if path is not None:
            return path
    raise ScriptError("Не найден Ghostscript. Установите ghostscript и убедитесь, что команда gs доступна.")


def qpdf_path() -> str:
    path = command_path("qpdf")
    if path is None:
        raise ScriptError("Не найден qpdf. Установите qpdf, чтобы экспортировать страницы без изменения поворота.")
    return path


def run_ghostscript(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else "вывода нет"
        stderr = e.stderr.strip() if e.stderr else "вывода ошибок нет"
        raise ScriptError(
            "Ghostscript завершился с ошибкой.\n"
            f"Команда: {' '.join(e.cmd)}\n"
            f"Обычный вывод:\n{stdout}\n"
            f"Вывод ошибок:\n{stderr}"
        ) from e


def run_qpdf(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.stdout.strip() if e.stdout else "вывода нет"
        stderr = e.stderr.strip() if e.stderr else "вывода ошибок нет"
        raise ScriptError(
            "qpdf завершился с ошибкой.\n"
            f"Команда: {' '.join(e.cmd)}\n"
            f"Обычный вывод:\n{stdout}\n"
            f"Вывод ошибок:\n{stderr}"
        ) from e


def read_page_inks(pdf_path: Path, gs: str) -> list[PageInk]:
    result = run_ghostscript(
        [
            gs,
            "-q",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-o",
            "-",
            "-sDEVICE=inkcov",
            str(pdf_path),
        ]
    )
    pages: list[PageInk] = []
    for line in result.stdout.splitlines():
        match = INKCOV_RE.match(line)
        if match is None:
            continue
        pages.append(
            PageInk(
                page=len(pages) + 1,
                cyan=float(match.group("c")),
                magenta=float(match.group("m")),
                yellow=float(match.group("y")),
                black=float(match.group("k")),
            )
        )

    if not pages:
        raise ScriptError("Ghostscript не вернул данные inkcov. Проверьте, что файл является корректным PDF.")

    return pages


def page_list_arg(pages: list[int]) -> str:
    if not pages:
        return ""

    ranges: list[str] = []
    start = pages[0]
    previous = pages[0]
    for page in pages[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append(f"{start}-{previous}" if start != previous else str(start))
        start = page
        previous = page
    ranges.append(f"{start}-{previous}" if start != previous else str(start))
    return ",".join(ranges)


def export_pages(source: Path, output: Path, pages: list[int], qpdf: str) -> None:
    if not pages:
        if output.exists():
            output.unlink()
        print(f"[SKIP] {output}: страниц нет")
        return

    page_list = page_list_arg(pages)
    run_qpdf(
        [
            qpdf,
            "--empty",
            "--pages",
            str(source),
            page_list,
            "--",
            str(output),
        ]
    )
    print(f"[OK] {output}: страницы {page_list}")


def split_pdf_color(pdf_path: Path, threshold: float = 0.00001) -> tuple[list[int], list[int]]:
    if threshold < 0:
        raise ScriptError("Порог --threshold не может быть отрицательным.")

    source = normalize_pdf_path(pdf_path).expanduser().resolve()
    if not source.is_file():
        raise ScriptError(f"PDF-файл не найден: {pdf_path}")
    if source.suffix.lower() != ".pdf":
        raise ScriptError(f"Ожидался PDF-файл с расширением .pdf: {pdf_path}")

    gs = ghostscript_path()
    qpdf = qpdf_path()
    page_inks = read_page_inks(source, gs)
    color_pages = [ink.page for ink in page_inks if ink.is_color(threshold)]
    bw_pages = [ink.page for ink in page_inks if not ink.is_color(threshold)]

    print(f"Цветные страницы: {page_list_arg(color_pages) if color_pages else 'нет'}")
    print(f"ЧБ страницы: {page_list_arg(bw_pages) if bw_pages else 'нет'}")

    export_pages(source, source.with_name(f"{source.stem}_color{source.suffix}"), color_pages, qpdf)
    export_pages(source, source.with_name(f"{source.stem}_bw{source.suffix}"), bw_pages, qpdf)

    return color_pages, bw_pages


def main() -> int:
    args = parse_args()
    split_pdf_color(args.pdf, threshold=args.threshold)
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
