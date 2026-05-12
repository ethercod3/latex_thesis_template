from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import PROJECT_DIR, ScriptError, capture_command, run_command, script_main

DIST_DIR = PROJECT_DIR / "dist"
DOWNLOAD_PATTERNS = [
    "diploma-latex-check.exe",
    "checktool-windows-x64.exe",
    "SHA256SUMS.txt",
    "checktool-SHA256SUMS.txt",
]


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


def download_pattern(tag: str, pattern: str) -> None:
    result = run_command(
        ["gh", "release", "download", tag, "--pattern", pattern, "--dir", str(DIST_DIR), "--clobber"],
        check=False,
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


def main() -> int:
    DIST_DIR.mkdir(exist_ok=True)

    tag = latest_release_tag(current_tag())
    if tag is None:
        print("No previous release found; skipping check tool assets.")
        return 0

    print(f"Downloading check tool assets from {tag}")
    for pattern in DOWNLOAD_PATTERNS:
        download_pattern(tag, pattern)

    normalize_assets()
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
