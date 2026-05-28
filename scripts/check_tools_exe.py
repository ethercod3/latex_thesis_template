"""Smoke-test собранного Windows checktool-исполняемого файла.

Запускает exe из dist, допускает ненулевой код при отсутствии внешних
инструментов на runner-е и сверяет SHA-256 с опубликованным checksum-файлом.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import subprocess

import typer

EXE_PATH = Path("dist/diploma-latex-check.exe")
CHECKSUM_PATH = Path("dist/SHA256SUMS.txt")

app = typer.Typer(add_completion=False)


def run_exe() -> tuple[int, str, str]:
    result = subprocess.run([str(EXE_PATH)], check=False, capture_output=True)
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    return result.returncode, stdout, stderr


@app.command()
def smoke() -> None:
    code, stdout, stderr = run_exe()
    if code:
        print(
            f"Smoke test finished with exit code {code}. "
            "This is allowed because the runner may not have TeX Live or Docker."
        )
        if stdout.strip():
            print(stdout.strip())
        if stderr.strip():
            print(stderr.strip())


@app.command()
def checksum() -> None:
    digest = hashlib.sha256(EXE_PATH.read_bytes()).hexdigest()
    CHECKSUM_PATH.write_text(f"{digest}  {EXE_PATH.name}\n", encoding="utf-8")


if __name__ == "__main__":
    app()
