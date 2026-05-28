"""Публикация собранного PDF как GitHub Release asset.

Определяет целевой tag, копирует PDF в dist и через GitHub CLI загружает
артефакт в nightly или tag-релиз с предсказуемым именем файла.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from plumbum import local
import typer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import PROJECT_DIR, ScriptError

PDF_PATH = PROJECT_DIR / "Куприянов_И221_диплом.pdf"
DIST_DIR = PROJECT_DIR / "dist"
NIGHTLY_TAG = "nightly"


def current_tag() -> str:
    tag = os.environ.get("CURRENT_TAG")
    if not tag:
        raise ScriptError("CURRENT_TAG не задан.")
    return tag


def run_command(command: list[str], check: bool = True):
    runner = local[command[0]]
    for arg in command[1:]:
        runner = runner[arg]
    code, stdout, stderr = runner.run()

    class Result:
        pass

    result = Result()
    result.returncode = code
    result.stdout = stdout
    result.stderr = stderr
    if check and code != 0:
        raise ScriptError(f"Команда завершилась с ошибкой (код {code}): {' '.join(command)}")
    return result


def ensure_release(tag: str) -> None:
    result = run_command(["gh", "release", "view", tag])
    if getattr(result, "returncode", 1) == 0:
        return

    run_command(
        [
            "gh",
            "release",
            "create",
            tag,
            "--title",
            tag,
            "--notes",
            "Автоматическая сборка PDF.",
        ]
    )


def move_nightly_tag(tag: str) -> None:
    if tag != NIGHTLY_TAG:
        return

    run_command(["git", "tag", "-f", tag, "HEAD"])
    run_command(["git", "push", "origin", f"refs/tags/{tag}", "--force"])


def upload_if_exists(tag: str, local_path: Path, asset_name: str) -> None:
    if not local_path.is_file():
        return
    run_command(["gh", "release", "upload", tag, f"{local_path}#{asset_name}", "--clobber"])


def main() -> None:
    tag = current_tag()
    move_nightly_tag(tag)
    ensure_release(tag)
    upload_if_exists(tag, PDF_PATH, "pdf-Куприянов_И221_диплом.pdf")
    upload_if_exists(tag, DIST_DIR / "diploma-latex-check.exe", "checktool-windows-x64.exe")
    upload_if_exists(tag, DIST_DIR / "SHA256SUMS.txt", "checktool-SHA256SUMS.txt")
    return 0


if __name__ == "__main__":
    typer.run(main)
