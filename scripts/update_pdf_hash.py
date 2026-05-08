from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from common import PROJECT_DIR, env_value


README_PATH = PROJECT_DIR / "README.md"
START_MARKER = "<!-- DIPLOMA_HASHES_START -->"
END_MARKER = "<!-- DIPLOMA_HASHES_END -->"
LEGACY_START_MARKER = "<!-- DIPLOMA_SHA256_START -->"
LEGACY_END_MARKER = "<!-- DIPLOMA_SHA256_END -->"

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

    target = env_value("TARGET")
    if target:
        return (PROJECT_DIR / f"{Path(target).stem}.pdf").resolve()

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return (PROJECT_DIR / f"{tex_files[0].stem}.pdf").resolve()

    raise RuntimeError(
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


def readme_block(hashes: list[tuple[str, str]]) -> str:
    hash_lines = "\n".join(f"{label}: `{digest}`<br>" for label, digest in hashes)
    return (
        f"{START_MARKER}\n"
        "## Контрольные суммы PDF\n\n"
        f"{hash_lines}\n"
        f"{END_MARKER}"
    )


def update_readme(hashes: list[tuple[str, str]]) -> bool:
    content = README_PATH.read_text(encoding="utf-8")
    block = readme_block(hashes)
    pattern = re.compile(
        rf"(?:{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}|"
        rf"{re.escape(LEGACY_START_MARKER)}.*?{re.escape(LEGACY_END_MARKER)})",
        flags=re.DOTALL,
    )

    if pattern.search(content):
        updated = pattern.sub(block, content)
    else:
        title_end = content.find("\n\n")
        if title_end == -1:
            updated = f"{content.rstrip()}\n\n{block}\n"
        else:
            updated = f"{content[:title_end]}\n\n{block}\n\n{content[title_end + 2:]}"

    if updated == content:
        return False

    README_PATH.write_text(updated, encoding="utf-8", newline="\n")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Обновить хеши PDF-файла в README.md.")
    parser.add_argument(
        "--pdf",
        default=None,
        help="Имя или путь к PDF-файлу. По умолчанию берется TARGET из .env с расширением .pdf.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path = target_pdf_path(args.pdf)

    if not pdf_path.is_file():
        print(f"PDF-файл не найден, хеши в README.md оставлены без изменений: {pdf_path}")
        return 0

    hashes = file_hashes(pdf_path)
    changed = update_readme(hashes)

    if changed:
        print("Хеши в README.md обновлены.")
    else:
        print("Хеши в README.md уже актуальны.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise SystemExit(1)
