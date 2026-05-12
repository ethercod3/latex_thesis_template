# Backups

The project supports backing up Git history through `git bundle` and `rclone`. A bundle stores commits, branches, and tags, but it does not store uncommitted working-tree changes.

!!! warning "Before backing up"
    Commit or stash important local changes first. Otherwise they will not be included in the `git bundle`.

## Local bundle

Create and verify a backup file without uploading it:

```bash
task backup:local
```

The file is written to `.cache/backups/` and verified with `git bundle verify`.

## Cloud backup through rclone

Install `rclone` and configure remotes:

```bash
rclone config
```

By default, the project expects these remote names:

- `gdrive` for Google Drive;
- `ydisk` for Yandex Disk.

The settings can be stored in `.env`:

```env
BACKUP_RCLONE_DESTINATIONS="gdrive:diploma_latex_backups,ydisk:diploma_latex_backups"
BACKUP_KEEP_WEEKS="30"
```

Preview actions without uploading or deleting anything:

```bash
task backup:dry
```

Create a bundle, upload it to both remotes, and keep the latest 30 backup files on each remote:

```bash
task backup
```

If the remotes have different names, pass destinations explicitly:

```bash
task backup -- --destinations "google:latex-backups,yadisk:latex-backups" --keep 30
```

## GitHub Actions

The `.github/workflows/backup.yml` workflow runs manually and every Sunday at 05:00 Asia/Yakutsk. It checks out the full Git history, installs `rclone`, creates a `git bundle`, uploads it to cloud storage, and applies retention.

The workflow requires this repository secret:

```text
RCLONE_CONFIG_CONTENT
```

The secret value is the full contents of the local `rclone.conf`. This command prints the file path:

```bash
rclone config file
```

To override destinations or retention, use repository variables:

```text
BACKUP_RCLONE_DESTINATIONS=gdrive:diploma_latex_backups,ydisk:diploma_latex_backups
BACKUP_KEEP_WEEKS=30
```
