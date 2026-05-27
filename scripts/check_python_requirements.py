"""Проверка доступности Python-зависимостей из файла зависимостей.

Используется как легкая диагностика окружения: читает закрепленные
зависимости и сообщает, каких пакетов не хватает в текущем интерпретаторе.
"""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
import re

import typer


def requirement_name(line: str) -> str:
    package = line.strip()
    if not package or package.startswith("#"):
        return ""
    return re.split(r"[<>=!~]", package, maxsplit=1)[0].strip()


def missing_requirements(requirements_path: Path) -> list[str]:
    missing: list[str] = []
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        package = requirement_name(line)
        if not package:
            continue
        try:
            metadata.version(package)
        except metadata.PackageNotFoundError:
            missing.append(package)
    return missing


def main(requirements_path: Path = typer.Argument(..., help="Файл зависимостей для проверки.")) -> None:
    missing = missing_requirements(requirements_path)
    if missing:
        print("\n".join(missing))


if __name__ == "__main__":
    typer.run(main)
