# CI/CD и релизы

В репозитории настроены GitHub Actions для проверки вспомогательных инструментов, сборки PDF и публикации релизных артефактов.

## GitHub Pages

Workflow `Publish Zensical docs` собирает двуязычную документацию командой `task docs:build:pages` и публикует каталог `docs-site/` в GitHub Pages. Для этой сборки используются конфиги `zensical.pages.toml` и `zensical.pages.en.toml`, чтобы ссылки языкового переключателя и `site_url` указывали на публичный адрес Pages.

## Проверка check tools

Workflow `Release check tools exe` запускается при push тегов `v*` и вручную. Он собирает Windows-исполняемый файл проверки состояния проекта:

- `diploma-latex-check.exe`;
- `SHA256SUMS.txt`.

Скрипт публикации лежит в `scripts/ci/release_check_tools.py`, а GitHub-specific Taskfile - в `.github/tasks/check-tools-exe.yml`.

## PDF release

Workflow `Release PDF` собирает итоговый PDF через Docker и загружает его в GitHub Release.

Для тегов `v*` PDF workflow не стартует напрямую от push тега. Он запускается через `workflow_run` после успешного завершения `Release check tools exe`. Так в release попадает актуальный `checktool-windows-x64.exe`, собранный для того же тега.

В release загружаются:

- `pdf-Куприянов_И221_диплом.pdf`;
- `checktool-windows-x64.exe`, если он найден в release;
- `checktool-SHA256SUMS.txt`, если он найден в release.

Workflow проверки также оставляет исходные assets `diploma-latex-check.exe` и `SHA256SUMS.txt`. PDF workflow добавляет алиасы с префиксом `checktool-`, чтобы в списке assets было проще отличать проверочную утилиту от PDF.

## Nightly

Ночная сборка запускается по расписанию в 04:00 по Якутску. GitHub Actions использует UTC, поэтому cron настроен как `0 19 * * *`.

Ночная сборка публикуется в служебный тег и release `nightly`. Скрипт `scripts/ci/publish_pdf_release.py` передвигает тег `nightly` на текущий commit default branch и перезаливает PDF-asset.

## Backup

Workflow `Backup git bundle` запускается вручную и по расписанию каждое воскресенье в 05:00 по Якутску. Он создает `git bundle`, загружает его через `rclone` в настроенные облачные remotes и оставляет последние 30 backup-файлов.

Для workflow нужен repository secret:

```text
RCLONE_CONFIG_CONTENT
```

Значение секрета - полный текст `rclone.conf`. По умолчанию используются destinations:

```text
gdrive:diploma_latex_backups,ydisk:diploma_latex_backups
```

Их можно переопределить через repository variable `BACKUP_RCLONE_DESTINATIONS`. Подробности: [Резервное копирование](backup.md).

## Кэши CI

В Windows workflow для `diploma-latex-check.exe` включен cache `uv` по `uv.lock`. В PDF workflow подключен `docker-compose.ci-cache.yaml`: Docker BuildKit сохраняет слои сборочных образов в GitHub Actions cache отдельно для `latex`, `docx`, `mermaid` и `python`.

## Приватный репозиторий с кодом

Для сборки приложений workflow подтягивает приватный репозиторий `ethercod3/diploma_code` в каталог `vault_diploma`. Для этого в настройках репозитория должен быть GitHub Actions secret:

```text
VIEW_DIPLOMA_CODE
```

Токену достаточно read-only доступа к contents репозитория `ethercod3/diploma_code`.

CI-скрипт `scripts/ci/prepare_pdf_release_env.py` создает `.env` со значениями:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="./vault_diploma"
TARGET="Куприянов_И221_диплом.tex"
```

Также туда записываются `HOST_UID` и `HOST_GID`, чтобы Docker-контейнеры могли писать в bind mount от имени пользователя GitHub runner.

## CI-скрипты

Вся нетривиальная логика workflow вынесена в Python-скрипты:

| Скрипт | Назначение |
| --- | --- |
| `scripts/ci/prepare_pdf_release_env.py` | Создает `.env` для CI-сборки PDF |
| `scripts/ci/resolve_pdf_release_context.py` | Определяет release tag и источник checktool assets |
| `scripts/ci/download_latest_checktool_assets.py` | Скачивает checktool assets из нужного release |
| `scripts/ci/publish_pdf_release.py` | Создает/обновляет release и загружает PDF/checktool assets |
| `scripts/ci/release_check_tools.py` | Публикует exe проверки состояния проекта |

В YAML остаются только базовые команды вида `python ...` и `task build`.
