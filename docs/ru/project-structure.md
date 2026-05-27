# Структура проекта

```mermaid
flowchart LR
    TEX["*.tex<br/>preamble/"] --> PDF["Итоговый PDF"]
    DOCX["docx/*.docx"] --> TITLE["титульник.pdf<br/>задание.pdf"]
    MMD["mermaid/*.mmd"] --> FIGURES["figures/*.pdf"]
    PYD["python_diagrams/*.py"] --> FIGURES
    TITLE --> TEX
    FIGURES --> TEX
    SCRIPTS["scripts/*.py"] --> DOCX
    SCRIPTS --> MMD
    SCRIPTS --> PYD
    CI["scripts/ci/*.py<br/>.github/workflows"] --> RELEASE["GitHub Releases"]
    BACKUP["scripts/backup_project.py<br/>backup.yml"] --> CLOUD["Google Drive<br/>Яндекс Диск"]
    DOCKER["docker/<br/>docker-compose.yaml"] --> SCRIPTS
    DOCS["docs/ru/*.md<br/>docs/en/*.md"] --> SITE["docs-site/"]
```

| Путь | Назначение |
| --- | --- |
| `*.tex`, `preamble/` | LaTeX-документы и настройки преамбулы |
| `docx/` | DOCX-исходники титульника и задания |
| `mermaid/` | Исходники Mermaid-диаграмм |
| `python_diagrams/` | Python-скрипты генерации диаграмм |
| `figures/` | Сгенерированные изображения и PDF для вставки в документ |
| `scripts/` | Вспомогательные скрипты сборки, конвертации, сравнения PDF и резервного копирования |
| `scripts/ci/` | Python-скрипты для GitHub Actions и публикации релизов |
| `docker/` | Dockerfile для отдельных профилей сборки |
| `docs/ru/`, `docs/en/` | Zensical-документация проекта |
| `docs/includes/` | Общие Markdown-вставки для Zensical-документации |
| `tasks/` | Тематические Taskfile с командами сборки и обслуживания; список команд доступен через `task --list` |
| `tests/` | Pytest-тесты чистой логики вспомогательных скриптов |
| `.github/workflows/` | GitHub Actions для Pages, check tools, PDF releases и backup |

Ключевые файлы:

| Файл | Назначение |
| --- | --- |
| `Куприянов_И221_диплом.tex` | Основной LaTeX-файл диплома |
| `bibliography.bib` | Библиография для `biblatex` |
| `pyproject.toml` | Python-зависимости и настройки Python-инструментов, включая Black |
| `uv.lock` | Зафиксированные версии зависимостей |
| `docker-compose.yaml` | Docker Compose профили проекта |
| `docker-compose.ci-cache.yaml` | CI-only Compose override для кэша Docker BuildKit в GitHub Actions |
| `Taskfile.yml` | Единая точка входа Task, подключающая файлы из `tasks/` |
| `.env` | Локальные переменные окружения для сборки |

Файл `.env` не коммитится, потому что содержит локальные пути.[^env-local]

[^env-local]: В `.env` могут быть абсолютные пути конкретной машины, например путь к каталогу с кодом для приложений. Если такой файл попадет в репозиторий, сборка на другой машине почти наверняка будет смотреть в несуществующее место.
