"""Обновление контрольных сумм итогового PDF в README.

Считает набор hash-алгоритмов для собранного диплома и обновляет управляемый
блок README через cog.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

from plumbum import local
import typer

from common import PROJECT_DIR, ScriptError, env_value

README_PATH = PROJECT_DIR / "README.md"
PDF_ENV_VAR = "DIPLOMA_HASH_PDF"

HASH_ALGORITHMS = (
    ("md5", "MD5", None),
    ("sha1", "SHA-1", None),
    ("sha256", "SHA-256", None),
    ("sha3_256", "SHA3-256", None),
    ("blake2s", "BLAKE2s", None),
    ("shake_128", "SHAKE-128 (256-bit output)", 32),
)


def target_pdf_path(pdf_arg: str | None) -> Path:
    if pdf_arg:
        return (PROJECT_DIR / pdf_arg).resolve()

    env_pdf = os.environ.get(PDF_ENV_VAR)
    if env_pdf:
        return Path(env_pdf).resolve()

    target = env_value("TARGET")
    if target:
        return (PROJECT_DIR / f"{Path(target).stem}.pdf").resolve()

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return (PROJECT_DIR / f"{tex_files[0].stem}.pdf").resolve()

    raise ScriptError(
        "Не удалось понять, для какого PDF нужно обновить хеши. "
        "Укажите TARGET в файле .env или передайте путь через --pdf."
    )


def file_hashes(path: Path) -> list[tuple[str, str]]:
    digests = [(label, output_size, hashlib.new(name)) for name, label, output_size in HASH_ALGORITHMS]

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            for _, _, digest in digests:
                digest.update(chunk)

    return [
        (label, digest.hexdigest(output_size) if output_size else digest.hexdigest())
        for label, output_size, digest in digests
    ]


def readme_body(hashes: list[tuple[str, str]]) -> str:
    hash_lines = "\n".join(f"{label}: `{digest}`<br>" for label, digest in hashes)
    return "## Контрольные суммы PDF\n\n" f"{hash_lines}\n"


def cog_readme_block() -> str:
    pdf_path = target_pdf_path(None)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF-файл не найден: {pdf_path}")

    return readme_body(file_hashes(pdf_path))


def run_cog(pdf_path: Path) -> bool:
    before = README_PATH.read_text(encoding="utf-8")
    env = os.environ.copy()
    env[PDF_ENV_VAR] = str(pdf_path)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(PROJECT_DIR / "scripts"), *(path for path in [env.get("PYTHONPATH")] if path)]
    )

    cog = local["python"]
    for arg in ("-m", "cogapp", "-r", str(README_PATH)):
        cog = cog[arg]
    cog = cog.with_cwd(PROJECT_DIR).with_env(**env)
    retcode, stdout, stderr = cog.run(retcode=None)
    if retcode != 0:
        details = (stderr or stdout).strip()
        if "No module named cogapp" in details:
            details = "Синхронизируйте окружение через: uv sync"
        raise ScriptError(f"Не удалось обновить README через cog.\n{details}")

    after = README_PATH.read_text(encoding="utf-8")
    return before != after


def main(
    pdf: str | None = typer.Option(
        None,
        "--pdf",
        help="Имя или путь к PDF-файлу. По умолчанию берется TARGET из .env с расширением .pdf.",
    ),
) -> None:
    try:
        pdf_path = target_pdf_path(pdf)

        if not pdf_path.is_file():
            print(f"PDF-файл не найден, хеши в README.md оставлены без изменений: {pdf_path}")
            return

        changed = run_cog(pdf_path)

        if changed:
            print("Хеши в README.md обновлены.")
        else:
            print("Хеши в README.md уже актуальны.")
    except ScriptError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
