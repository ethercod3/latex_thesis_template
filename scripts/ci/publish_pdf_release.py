from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import PROJECT_DIR, ScriptError, run_command, script_main

PDF_PATH = PROJECT_DIR / "Куприянов_И221_диплом.pdf"
DIST_DIR = PROJECT_DIR / "dist"


def current_tag() -> str:
    tag = os.environ.get("CURRENT_TAG")
    if not tag:
        raise ScriptError("CURRENT_TAG не задан.")
    return tag


def ensure_release(tag: str) -> None:
    result = run_command(["gh", "release", "view", tag], check=False)
    if result.returncode == 0:
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


def upload_if_exists(tag: str, local_path, asset_name: str) -> None:
    if not local_path.is_file():
        return
    run_command(["gh", "release", "upload", tag, f"{local_path}#{asset_name}", "--clobber"])


def main() -> int:
    tag = current_tag()
    ensure_release(tag)
    upload_if_exists(tag, PDF_PATH, "pdf-Куприянов_И221_диплом.pdf")
    upload_if_exists(tag, DIST_DIR / "diploma-latex-check.exe", "checktool-windows-x64.exe")
    upload_if_exists(tag, DIST_DIR / "SHA256SUMS.txt", "checktool-SHA256SUMS.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
