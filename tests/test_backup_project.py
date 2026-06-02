from __future__ import annotations

from datetime import datetime

import pytest

import backup_project
from common import ScriptError


def test_parse_destinations_splits_and_trims() -> None:
    assert backup_project.parse_destinations("gdrive:backups, yandex: диплом ") == [
        "gdrive:backups",
        "yandex: диплом",
    ]


def test_parse_destinations_rejects_paths_without_remote() -> None:
    with pytest.raises(ScriptError):
        backup_project.parse_destinations("plain-folder")


def test_remote_file_path_handles_remote_root_and_directory() -> None:
    assert backup_project.remote_file_path("gdrive:", "backup.bundle") == "gdrive:backup.bundle"
    assert backup_project.remote_file_path("gdrive:folder", "backup.bundle") == "gdrive:folder/backup.bundle"


def test_backup_filename_is_lexicographically_sortable() -> None:
    assert backup_project.backup_filename(datetime(2026, 5, 12, 4, 5, 6)) == "diploma_template_2026-05-12_04-05-06.bundle"


def test_parse_args_accepts_local_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["backup_project.py", "--local-only"])

    args = backup_project.parse_args()

    assert args.local_only is True


def test_prune_remote_backups_keeps_latest_files(monkeypatch: pytest.MonkeyPatch) -> None:
    deleted: list[list[str]] = []
    monkeypatch.setattr(
        backup_project,
        "list_remote_backups",
        lambda _destination: [
            "diploma_template_2026-01-01_00-00-00.bundle",
            "diploma_template_2026-01-08_00-00-00.bundle",
            "diploma_template_2026-01-15_00-00-00.bundle",
        ],
    )
    monkeypatch.setattr(backup_project, "run_command", lambda command: deleted.append(command))

    backup_project.prune_remote_backups("gdrive:backups", keep=2, dry_run=False)

    assert deleted == [["rclone", "deletefile", "gdrive:backups/diploma_template_2026-01-01_00-00-00.bundle"]]
