from __future__ import annotations

from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import ScriptError, run_command, script_main


def main() -> int:
    tag = os.environ.get("GITHUB_REF_NAME")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    if not tag:
        raise ScriptError("GITHUB_REF_NAME не задан, публикация release assets невозможна.")

    if not token:
        raise ScriptError("GH_TOKEN или GITHUB_TOKEN не задан, публикация release assets невозможна.")

    assets = [Path("dist/diploma-latex-check.exe"), Path("dist/SHA256SUMS.txt")]
    missing = [str(path) for path in assets if not path.is_file()]
    if missing:
        raise ScriptError(f"Не найдены файлы для release assets: {', '.join(missing)}")

    release = run_command(["gh", "release", "view", tag], check=False)
    if release.returncode != 0:
        run_command(
            [
                "gh",
                "release",
                "create",
                tag,
                "--title",
                tag,
                "--notes",
                "Автоматическая сборка",
            ]
        )

    run_command(["gh", "release", "upload", tag, *(str(path) for path in assets), "--clobber"])
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
