# Резервное копирование

Проект поддерживает резервное копирование Git-истории через `git bundle` и `rclone`. Bundle хранит коммиты, ветки и теги, но не сохраняет незакоммиченные изменения рабочей копии.

!!! warning "Перед бэкапом"
    Если есть важные локальные правки, сначала сделайте commit или stash. Иначе они не попадут в `git bundle`.

## Локальный bundle

Создать и проверить backup-файл без загрузки в облако:

```bash
task backup:local
```

Файл будет создан в `.cache/backups/` и проверен командой `git bundle verify`.

## Облачный backup через rclone

Установите `rclone` и настройте remotes:

```bash
rclone config
```

По умолчанию проект ожидает такие имена:

- `gdrive` для Google Drive;
- `ydisk` для Яндекс Диска.

Настройки можно хранить в `.env`:

```env
BACKUP_RCLONE_DESTINATIONS="gdrive:diploma_latex_backups,ydisk:diploma_latex_backups"
BACKUP_KEEP_WEEKS="30"
```

Проверить действия без загрузки и удаления:

```bash
task backup:dry
```

Создать bundle, загрузить его в оба облака и оставить последние 30 backup-файлов на каждом remote:

```bash
task backup
```

Если remote называются иначе, передайте destinations явно:

```bash
task backup -- --destinations "google:latex-backups,yadisk:latex-backups" --keep 30
```

## GitHub Actions

Workflow `.github/workflows/backup.yml` запускается вручную и каждое воскресенье в 05:00 по Якутску. Он делает полный checkout истории, устанавливает `rclone`, создает `git bundle`, загружает его в облака и применяет retention.

Для работы workflow нужен repository secret:

```text
RCLONE_CONFIG_CONTENT
```

Значение секрета - полный текст локального `rclone.conf`. Путь к файлу показывает команда:

```bash
rclone config file
```

Если нужно переопределить destinations или retention, используйте repository variables:

```text
BACKUP_RCLONE_DESTINATIONS=gdrive:diploma_latex_backups,ydisk:diploma_latex_backups
BACKUP_KEEP_WEEKS=30
```
