from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, check=check)


def main() -> int:
    tag = os.environ.get("GITHUB_REF_NAME")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    if not tag:
        print("GITHUB_REF_NAME не задан, публикация release assets невозможна.", file=sys.stderr)
        return 1

    if not token:
        print("GH_TOKEN или GITHUB_TOKEN не задан, публикация release assets невозможна.", file=sys.stderr)
        return 1

    assets = [Path("dist/diploma-latex-check.exe"), Path("dist/SHA256SUMS.txt")]
    missing = [str(path) for path in assets if not path.is_file()]
    if missing:
        print(f"Не найдены файлы для release assets: {', '.join(missing)}", file=sys.stderr)
        return 1

    release = run(["gh", "release", "view", tag], check=False)
    if release.returncode != 0:
        run(
            [
                "gh",
                "release",
                "create",
                tag,
                "--title",
                tag,
                "--notes",
                "Автоматическая сборка diploma-latex-check.exe.",
            ]
        )

    run(["gh", "release", "upload", tag, *(str(path) for path in assets), "--clobber"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
