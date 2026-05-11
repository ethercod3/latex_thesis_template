from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from common import PROJECT_DIR


def compose_base_command() -> list[str]:
    if shutil.which("docker") is None:
        raise RuntimeError("Команда docker не найдена. Установите Docker Desktop.")

    result = subprocess.run(
        ["docker", "compose", "version"],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Команда docker compose недоступна. Проверьте Docker Compose plugin.")

    return ["docker", "compose"]


def run(command: list[str], dry_run: bool) -> None:
    print(f"==> {' '.join(command)}", flush=True)
    if dry_run:
        return

    subprocess.run(command, cwd=PROJECT_DIR, check=True)


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

    try:
        command = [*compose_base_command(), "down", "--remove-orphans"]
        if args.images:
            command.extend(["--rmi", "local"])
        run(command, args.dry_run)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"Команда завершилась с ошибкой (код {error.returncode}): {' '.join(error.cmd)}", file=sys.stderr)
        return error.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
