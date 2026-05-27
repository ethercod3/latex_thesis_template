"""Удаление сгенерированных артефактов сборки и локальных кэшей.

Чистит известные временные директории, LaTeX-артефакты и файлы публикации,
не затрагивая исходники и пользовательские документы проекта.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import typer

from common import ScriptError

ROOT = Path(__file__).resolve().parents[1]

EXPLICIT_DIRS = [
    ".aux_files",
    ".aux_files_docker",
    ".cache",
    ".pdf_diff",
    "_minted",
    "docs-site",
]

RECURSIVE_DIR_NAMES = [
    "__pycache__",
]

ROOT_FILE_PATTERNS = [
    "*.aux",
    "*.bbl",
    "*.bcf",
    "*.blg",
    "*.bkp",
    "*.fdb_latexmk",
    "*.fls",
    "*.lof",
    "*.log",
    "*.lot",
    "*.minted",
    "*.out",
    "*.run.xml",
    "*.synctex.gz",
    "*.toc",
    "$*.docx",
    "~$*.docx",
]

RECURSIVE_FILE_PATTERNS = [
    "*.pyc",
]

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
}


def is_inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    return True


def is_excluded(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(ROOT)
    except ValueError:
        return True

    return any(part in EXCLUDED_DIR_NAMES for part in relative.parts)


def unique_existing(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    result: list[Path] = []

    for path in paths:
        resolved = path.resolve()
        if resolved in seen or not path.exists() or is_excluded(path):
            continue
        if not is_inside_root(path):
            raise ScriptError(f"Refusing to remove path outside project root: {path}")
        seen.add(resolved)
        result.append(path)

    return sorted(result, key=lambda item: str(item).lower())


def collect_targets() -> list[Path]:
    dir_targets: list[Path] = []
    file_targets: list[Path] = []

    dir_targets.extend(ROOT / name for name in EXPLICIT_DIRS)

    for name in RECURSIVE_DIR_NAMES:
        dir_targets.extend(path for path in ROOT.rglob(name) if path.is_dir())

    for pattern in ROOT_FILE_PATTERNS:
        file_targets.extend(ROOT.glob(pattern))

    for pattern in RECURSIVE_FILE_PATTERNS:
        file_targets.extend(ROOT.rglob(pattern))

    dirs = unique_existing(dir_targets)
    dir_roots = [path.resolve() for path in dirs]
    files = [
        path
        for path in unique_existing(file_targets)
        if not any(path.resolve().is_relative_to(root) for root in dir_roots)
    ]

    return unique_existing([*dirs, *files])


def remove_path(path: Path, dry_run: bool) -> None:
    relative = path.relative_to(ROOT)
    action = "would remove" if dry_run else "remove"
    print(f"{action}: {relative}")

    if dry_run:
        return

    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def main(dry_run: bool = typer.Option(False, "--dry-run", help="Показать цели без удаления.")) -> None:
    targets = collect_targets()

    if not targets:
        print("nothing to clean")
        return

    for target in targets:
        remove_path(target, dry_run)


if __name__ == "__main__":
    typer.run(main)
