"""Создание резервных копий проекта через git bundle и rclone.

Скрипт собирает локальный bundle репозитория, выгружает его в один или
несколько remote-хранилищ и удаляет старые архивы сверх заданного лимита.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from plumbum import local
import typer

from common import PROJECT_DIR, ScriptError, env_value, require_command

DEFAULT_DESTINATIONS = "gdrive:diploma_template_backups,ydisk:diploma_template_backups"
DEFAULT_KEEP = 30
BACKUP_DIR = PROJECT_DIR / ".cache" / "backups"
BACKUP_PREFIX = "diploma_template"
BACKUP_SUFFIX = ".bundle"


def parse_destinations(value: str | None) -> list[str]:
    raw_value = value or env_value("BACKUP_RCLONE_DESTINATIONS") or DEFAULT_DESTINATIONS
    destinations = [item.strip().rstrip("/") for item in raw_value.split(",") if item.strip()]

    if not destinations:
        raise ScriptError("Не задан ни один rclone destination для бэкапа.")

    for destination in destinations:
        if ":" not in destination:
            raise ScriptError(f"Некорректный rclone destination: {destination}. Ожидается формат remote:path.")

    return destinations


def remote_file_path(destination: str, filename: str) -> str:
    if destination.endswith(":"):
        return f"{destination}{filename}"

    return f"{destination}/{filename}"


def backup_filename(now: datetime | None = None) -> str:
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
    return f"{BACKUP_PREFIX}_{timestamp}{BACKUP_SUFFIX}"


def run_command(command: list[str], *, check: bool = True, cwd: Path = PROJECT_DIR):
    print(f"==> {' '.join(command)}", flush=True)
    runner = local[command[0]]
    for arg in command[1:]:
        runner = runner[arg]

    with local.cwd(cwd):
        code, stdout, stderr = runner.run()

    class Result:
        pass

    result = Result()
    result.returncode = code
    result.stdout = stdout
    result.stderr = stderr
    if check and code != 0:
        raise ScriptError(
            f"Команда завершилась с ошибкой (код {code}): {' '.join(command)}\n{stderr.strip() or stdout.strip()}"
        )
    return result


def run_checked(command: list[str], *, cwd: Path = PROJECT_DIR) -> tuple[int, str, str]:
    result = run_command(command)
    if result is None:
        return 0, "", ""
    code = getattr(result, "returncode", 0)
    stdout = getattr(result, "stdout", "")
    stderr = getattr(result, "stderr", "")
    if code != 0:
        details = stderr.strip() or stdout.strip() or "вывода нет"
        raise ScriptError(f"Команда завершилась с ошибкой (код {code}): {' '.join(command)}\n{details}")
    return code, stdout, stderr


def git_worktree_is_dirty() -> bool:
    _, stdout, _ = run_checked(["git", "status", "--porcelain"])
    return bool(stdout.strip())


def create_bundle(bundle_path: Path) -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    run_checked(["git", "bundle", "create", str(bundle_path), "--all", "--tags"])
    run_checked(["git", "bundle", "verify", str(bundle_path)])


def upload_bundle(bundle_path: Path, destinations: list[str], dry_run: bool) -> None:
    for destination in destinations:
        if dry_run:
            print(f"would run: rclone mkdir {destination}")
        else:
            run_checked(["rclone", "mkdir", destination])

        command = ["rclone", "copyto", str(bundle_path), remote_file_path(destination, bundle_path.name)]
        if dry_run:
            command.append("--dry-run")
        run_checked(command)


def list_remote_backups(destination: str) -> list[str]:
    _, stdout, _ = run_checked(["rclone", "lsf", "--files-only", "--format", "p", destination])
    return sorted(
        line.strip()
        for line in stdout.splitlines()
        if line.strip().startswith(f"{BACKUP_PREFIX}_") and line.strip().endswith(BACKUP_SUFFIX)
    )


def prune_remote_backups(destination: str, keep: int, dry_run: bool) -> None:
    backups = list_remote_backups(destination)
    old_backups = backups[:-keep] if keep > 0 else backups

    if not old_backups:
        print(f"retention: {destination}: nothing to remove")
        return

    for filename in old_backups:
        command = ["rclone", "deletefile", remote_file_path(destination, filename)]
        if dry_run:
            command.append("--dry-run")
        run_checked(command)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Создать git bundle проекта, загрузить через rclone и оставить последние N архивов."
    )
    parser.add_argument(
        "--destinations",
        default=None,
        help=(
            "Список rclone destinations через запятую. "
            f"По умолчанию BACKUP_RCLONE_DESTINATIONS или {DEFAULT_DESTINATIONS}."
        ),
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=int(env_value("BACKUP_KEEP_WEEKS") or DEFAULT_KEEP),
        help=f"Сколько последних bundle-файлов хранить на каждом remote. По умолчанию {DEFAULT_KEEP}.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Показать rclone-изменения без загрузки и удаления.")
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Только создать и проверить локальный git bundle без rclone-загрузки.",
    )
    parser.add_argument("--no-prune", action="store_true", help="Не удалять старые backup-файлы после загрузки.")
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Завершиться ошибкой, если в рабочем дереве есть незакоммиченные изменения.",
    )
    return parser.parse_args()


def main(
    destinations: str | None = typer.Option(
        None,
        "--destinations",
        help=(
            "Список rclone destinations через запятую. "
            f"По умолчанию BACKUP_RCLONE_DESTINATIONS или {DEFAULT_DESTINATIONS}."
        ),
    ),
    keep: int = typer.Option(
        int(env_value("BACKUP_KEEP_WEEKS") or DEFAULT_KEEP),
        "--keep",
        help=f"Сколько последних bundle-файлов хранить на каждом remote. По умолчанию {DEFAULT_KEEP}.",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Показать rclone-изменения без загрузки и удаления."),
    local_only: bool = typer.Option(
        False,
        "--local-only",
        help="Только создать и проверить локальный git bundle без rclone-загрузки.",
    ),
    no_prune: bool = typer.Option(False, "--no-prune", help="Не удалять старые backup-файлы после загрузки."),
    require_clean: bool = typer.Option(
        False,
        "--require-clean",
        help="Завершиться ошибкой, если в рабочем дереве есть незакоммиченные изменения.",
    ),
) -> None:
    if keep < 0:
        raise typer.BadParameter("--keep не может быть отрицательным.")

    require_command("git")
    if not local_only:
        require_command("rclone")

    remote_destinations = [] if local_only else parse_destinations(destinations)

    if git_worktree_is_dirty():
        message = (
            "В рабочем дереве есть незакоммиченные изменения. "
            "git bundle сохраняет только Git-историю, а не текущие незакоммиченные файлы."
        )
        if require_clean:
            raise ScriptError(message)
        print(f"warning: {message}")

    bundle_path = BACKUP_DIR / backup_filename()
    create_bundle(bundle_path)

    if local_only:
        print(f"local backup created: {bundle_path.relative_to(PROJECT_DIR)}")
        return 0

    upload_bundle(bundle_path, remote_destinations, dry_run)

    if not no_prune:
        for destination in remote_destinations:
            prune_remote_backups(destination, keep, dry_run)

    print(f"backup created: {bundle_path.relative_to(PROJECT_DIR)}")
    return 0


if __name__ == "__main__":
    typer.run(main)
