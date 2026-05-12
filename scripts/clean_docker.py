from __future__ import annotations

import argparse

from common import docker_compose_command, run_command, script_main


def run(command: list[str], dry_run: bool) -> None:
    print(f"==> {' '.join(command)}", flush=True)
    if dry_run:
        return

    run_command(command)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Очистить Docker-артефакты текущего Compose-проекта.")
    parser.add_argument(
        "--images",
        action="store_true",
        help="Удалить локальные образы, собранные Docker Compose для этого проекта.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Показать команды без выполнения.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    command = [*docker_compose_command(), "down", "--remove-orphans"]
    if args.images:
        command.extend(["--rmi", "local"])
    run(command, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
