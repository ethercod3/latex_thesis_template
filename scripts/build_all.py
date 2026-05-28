"""Полная Docker-сборка всех публикуемых артефактов проекта.

Последовательно запускает Compose-профили для DOCX, Mermaid, Python-диаграмм
и LaTeX, останавливая цепочку на первом неуспешном профиле.
"""

from __future__ import annotations

import subprocess
import sys

import typer

from common import ScriptError, docker_compose_command

PROFILES = [
    ("docx", "docx_pdf"),
    ("mermaid", "mermaid_diagrams"),
    ("python", "python_diagrams"),
    ("latex", "latex"),
]


def run_profile(profile: str, service: str) -> int:
    print(f"\n==> {profile}", flush=True)
    command = [*docker_compose_command(), "--profile", profile, "run", "--build", "--rm", service]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise ScriptError(f"Профиль {profile} завершился с ошибкой.\n{details}")
    return 0


def main() -> None:
    try:
        for profile, service in PROFILES:
            run_profile(profile, service)
    except ScriptError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
