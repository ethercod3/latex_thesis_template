from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re


PROJECT_DIR = Path(__file__).resolve().parents[1]
README_PATH = PROJECT_DIR / "README.md"
ENV_PATH = PROJECT_DIR / ".env"
START_MARKER = "<!-- DIPLOMA_SHA256_START -->"
END_MARKER = "<!-- DIPLOMA_SHA256_END -->"


def env_value(name: str) -> str | None:
    if not ENV_PATH.exists():
        return None

    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        if key.strip() != name:
            continue

        return value.strip().strip("\"'")

    return None


def target_pdf_path(pdf_arg: str | None) -> Path:
    if pdf_arg:
        return (PROJECT_DIR / pdf_arg).resolve()

    target = env_value("TARGET")
    if target:
        return (PROJECT_DIR / f"{Path(target).stem}.pdf").resolve()

    tex_files = sorted(PROJECT_DIR.glob("*.tex"))
    if len(tex_files) == 1:
        return (PROJECT_DIR / f"{tex_files[0].stem}.pdf").resolve()

    raise RuntimeError("Cannot determine target PDF. Set TARGET in .env or pass --pdf.")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def readme_block(pdf_path: Path, digest: str) -> str:
    relative_pdf = pdf_path.relative_to(PROJECT_DIR)
    return (
        f"{START_MARKER}\n"
        "## Контрольная сумма PDF\n\n"
        f"**Файл:** `{relative_pdf.as_posix()}`\n\n"
        f"**SHA-256:** `{digest}`\n"
        f"{END_MARKER}"
    )


def update_readme(pdf_path: Path, digest: str) -> bool:
    content = README_PATH.read_text(encoding="utf-8")
    block = readme_block(pdf_path, digest)
    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
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
    parser = argparse.ArgumentParser(description="Update README.md with SHA-256 of the latest diploma PDF.")
    parser.add_argument("--pdf", default=None, help="PDF filename/path. Defaults to TARGET from .env with .pdf extension.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path = target_pdf_path(args.pdf)

    if not pdf_path.is_file():
        print(f"PDF not found, keeping existing README hash: {pdf_path}")
        return 0

    digest = sha256_file(pdf_path)
    changed = update_readme(pdf_path, digest)

    if changed:
        print(f"Updated README.md SHA-256 for {pdf_path.name}: {digest}")
    else:
        print(f"README.md SHA-256 is already up to date for {pdf_path.name}: {digest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
