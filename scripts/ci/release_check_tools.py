"""Проверки перед публикацией Windows checktool-релиза."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import typer

ROOT = Path(__file__).resolve().parents[2]
CHECKSUM_PATH = ROOT / "dist" / "SHA256SUMS.txt"


def run_checked(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def main() -> None:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise typer.BadParameter("GH_TOKEN или GITHUB_TOKEN не задан.")

    if not CHECKSUM_PATH.is_file():
        raise typer.BadParameter(f"Не найден файл checksum: {CHECKSUM_PATH}")

    code, stdout, stderr = run_checked(["gh", "release", "list"])
    if code != 0:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        raise typer.Exit(code=code)

    print(details if (details := stdout.strip()) else "release list OK")


if __name__ == "__main__":
    typer.run(main)
