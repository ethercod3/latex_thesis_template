"""Очистка Docker Compose ресурсов проекта.

Останавливает сервисы, удаляет контейнеры/сети текущего Compose-проекта и
опционально чистит локальные образы; поддерживает dry-run для проверки команд.
"""

from __future__ import annotations

import sys

from plumbum import local
import typer

from common import ScriptError, docker_compose_command


def run(command: list[str], dry_run: bool) -> None:
    print(f"==> {' '.join(command)}", flush=True)
    if dry_run:
        return

    proc = local[command[0]]
    for arg in command[1:]:
        proc = proc[arg]
    code, stdout, stderr = proc.run()
    if code != 0:
        details = (stderr or stdout).strip()
        raise ScriptError(f"Docker Compose command failed: {' '.join(command)}\n{details}")


def main(
    images: bool = typer.Option(
        False,
        "--images",
        help="Удалить локальные образы, собранные Docker Compose для этого проекта.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Показать команды без выполнения."),
) -> None:
    try:
        command = [*docker_compose_command(), "down", "--remove-orphans"]
        if images:
            command.extend(["--rmi", "local"])
        run(command, dry_run)
    except ScriptError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    typer.run(main)
