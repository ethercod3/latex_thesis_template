"""Проверки перед публикацией Windows checktool-релиза."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

import typer

ROOT = Path(__file__).resolve().parents[2]
DIST_DIR = ROOT / "dist"
EXE_PATH = DIST_DIR / "diploma-latex-check.exe"
CHECKSUM_PATH = ROOT / "dist" / "SHA256SUMS.txt"


def run_checked(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def release_tag() -> str:
    tag = os.environ.get("RELEASE_TAG") or os.environ.get("GITHUB_REF_NAME")
    if not tag:
        raise typer.BadParameter("RELEASE_TAG или GITHUB_REF_NAME не задан.")
    return tag


def run_or_exit(command: list[str]) -> None:
    code, stdout, stderr = run_checked(command)
    if code != 0:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        raise typer.BadParameter(f"Команда завершилась с ошибкой: {' '.join(command)}\n{details}")


def ensure_release(tag: str) -> None:
    code, _, _ = run_checked(["gh", "release", "view", tag])
    if code == 0:
        return
    run_or_exit(["gh", "release", "create", tag, "--title", tag, "--notes", "Автоматическая сборка check tools."])


def upload_release_assets(tag: str) -> None:
    run_or_exit(["gh", "release", "upload", tag, f"{EXE_PATH}#checktool-windows-x64.exe", "--clobber"])
    run_or_exit(["gh", "release", "upload", tag, f"{CHECKSUM_PATH}#checktool-SHA256SUMS.txt", "--clobber"])


def main() -> None:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise typer.BadParameter("GH_TOKEN или GITHUB_TOKEN не задан.")

    if not EXE_PATH.is_file():
        raise typer.BadParameter(f"Не найден exe: {EXE_PATH}")

    if not CHECKSUM_PATH.is_file():
        raise typer.BadParameter(f"Не найден файл checksum: {CHECKSUM_PATH}")

    code, stdout, stderr = run_checked(["gh", "release", "list"])
    if code != 0:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        raise typer.Exit(code=code)

    print(details if (details := stdout.strip()) else "release list OK")
    tag = release_tag()
    ensure_release(tag)
    upload_release_assets(tag)


if __name__ == "__main__":
    typer.run(main)
