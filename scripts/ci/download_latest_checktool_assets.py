"""Загрузка последних release assets для Windows checktool.

Используется в CI перед PDF-релизом: находит подходящие артефакты прошлого
релиза через GitHub CLI и кладет exe/checksum-файлы в dist.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import typer

from common import PROJECT_DIR, ScriptError

DIST_DIR = PROJECT_DIR / "dist"
DOWNLOAD_PATTERNS = [
    "diploma-latex-check.exe",
    "checktool-windows-x64.exe",
    "SHA256SUMS.txt",
    "checktool-SHA256SUMS.txt",
]


def capture_command(command: list[str]) -> str:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise ScriptError(result.stderr.strip() or result.stdout.strip() or "Команда завершилась с ошибкой.")
    return result.stdout.strip()


def current_tag() -> str:
    tag = os.environ.get("CURRENT_TAG")
    if not tag:
        raise ScriptError("CURRENT_TAG не задан.")
    return tag


def latest_release_tag(excluded_tag: str) -> str | None:
    output = capture_command(
        [
            "gh",
            "release",
            "list",
            "--exclude-drafts",
            "--exclude-pre-releases",
            "--limit",
            "20",
            "--json",
            "tagName",
        ]
    )
    releases = json.loads(output)
    for release in releases:
        tag = release["tagName"]
        if tag != excluded_tag:
            return tag
    return None


def checktool_source_tag(current_release_tag: str) -> str | None:
    source_tag = os.environ.get("CHECKTOOL_SOURCE_TAG")
    if source_tag:
        return source_tag
    return latest_release_tag(current_release_tag)


def download_pattern(tag: str, pattern: str) -> None:
    result = subprocess.run(
        ["gh", "release", "download", tag, "--pattern", pattern, "--dir", str(DIST_DIR), "--clobber"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Asset pattern not found in {tag}: {pattern}")


def normalize_assets() -> None:
    exe_alias = DIST_DIR / "checktool-windows-x64.exe"
    exe_canonical = DIST_DIR / "diploma-latex-check.exe"
    if exe_alias.is_file() and not exe_canonical.is_file():
        shutil.copy2(exe_alias, exe_canonical)

    checksum_alias = DIST_DIR / "checktool-SHA256SUMS.txt"
    checksum_canonical = DIST_DIR / "SHA256SUMS.txt"
    if checksum_alias.is_file() and not checksum_canonical.is_file():
        shutil.copy2(checksum_alias, checksum_canonical)


def main() -> None:
    try:
        DIST_DIR.mkdir(exist_ok=True)

        tag = checktool_source_tag(current_tag())
        if tag is None:
            print("No previous release found; skipping check tool assets.")
            return

        print(f"Downloading check tool assets from {tag}")
        for pattern in DOWNLOAD_PATTERNS:
            download_pattern(tag, pattern)

        normalize_assets()
    except ScriptError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
