# Резервное копирование

Этот раздел добавляется, если включена опция `include_backup_tools`.

Backup-скрипт создаёт `git bundle` и может отправлять его в rclone destinations:

```bash
task backup:local
task backup:dry
task backup
```
