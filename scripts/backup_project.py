from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path

from common import PROJECT_DIR, ScriptError, env_value, require_command, run_command, script_main

DEFAULT_DESTINATIONS = "gdrive:diploma_latex_backups,ydisk:diploma_latex_backups"
DEFAULT_KEEP = 30
BACKUP_DIR = PROJECT_DIR / ".cache" / "backups"
BACKUP_PREFIX = "diploma_latex"
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


def git_worktree_is_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=PROJECT_DIR,
        check=True,
        text=True,
        capture_output=True,
    )
    return bool(result.stdout.strip())


def create_bundle(bundle_path: Path) -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    run_command(["git", "bundle", "create", str(bundle_path), "--all", "--tags"])
    run_command(["git", "bundle", "verify", str(bundle_path)])


def upload_bundle(bundle_path: Path, destinations: list[str], dry_run: bool) -> None:
    for destination in destinations:
        if dry_run:
            print(f"would run: rclone mkdir {destination}")
        else:
            run_command(["rclone", "mkdir", destination])
        command = ["rclone", "copyto", str(bundle_path), remote_file_path(destination, bundle_path.name)]
        if dry_run:
            command.append("--dry-run")
        run_command(command)


def list_remote_backups(destination: str) -> list[str]:
    result = subprocess.run(
        ["rclone", "lsf", "--files-only", "--format", "p", destination],
        cwd=PROJECT_DIR,
        check=True,
        text=True,
        capture_output=True,
    )
    return sorted(
        line.strip()
        for line in result.stdout.splitlines()
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
        run_command(command)


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


def main() -> int:
    args = parse_args()

    if args.keep < 0:
        raise ScriptError("--keep не может быть отрицательным.")

    require_command("git")
    if not args.local_only:
        require_command("rclone")

    destinations = [] if args.local_only else parse_destinations(args.destinations)

    if git_worktree_is_dirty():
        message = (
            "В рабочем дереве есть незакоммиченные изменения. "
            "git bundle сохраняет только Git-историю, а не текущие незакоммиченные файлы."
        )
        if args.require_clean:
            raise ScriptError(message)
        print(f"warning: {message}")

    bundle_path = BACKUP_DIR / backup_filename()
    create_bundle(bundle_path)

    if args.local_only:
        print(f"local backup created: {bundle_path.relative_to(PROJECT_DIR)}")
        return 0

    upload_bundle(bundle_path, destinations, args.dry_run)

    if not args.no_prune:
        for destination in destinations:
            prune_remote_backups(destination, args.keep, args.dry_run)

    print(f"backup created: {bundle_path.relative_to(PROJECT_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(script_main(main))
