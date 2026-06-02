# LaTeX-шаблон дипломной работы

Обезличенный шаблон дипломного проекта на LaTeX с поддержкой Copier, Task,
Docker и вспомогательных Python-скриптов.

## Создание проекта

```bash
uvx copier copy https://github.com/ethercod3/latex_thesis_template my-diploma
```

После генерации скопируйте `.env.example` в `.env` и проверьте `TARGET`.

Copier спросит, какие наборы tooling добавить:

| Опция | Что добавляет |
| --- | --- |
| `code_listing_mode` | `none`, `inline` или `external` для листингов кода |
| `include_docs` | Zensical-документацию и docs-разделы |
| `include_docker` | Docker Compose и Docker-профили |
| `include_ci` | GitHub Actions и release scripts |
| `include_backup_tools` | backup через `git bundle` и `rclone` |
| `include_docx_tools` | конвертацию DOCX в PDF |
| `include_diagram_tools` | Mermaid/Python diagram tooling |
| `include_pdf_tools` | PDF hash/crop/split/diff tooling |

Режим кода отдельный от набора скриптов. `inline` подходит, если листинги будут
вставляться прямо через `lstlisting`; `external` добавляет вопросы про внешний
каталог с кодом. Отдельный remote-репозиторий спрашивается только для CI и
только если вы явно включили скачивание внешнего кода в CI.

Документация генерируется под выбранные опции: например, без
`include_diagram_tools` не появятся страницы про диаграммы, а без
`include_docs` не появятся `docs/` и `zensical*.toml`.

## Содержимое

| Путь | Назначение |
| --- | --- |
| `*.tex`, `preamble/` | Основной документ и настройки LaTeX |
| `bibliography.bib` | Dummy-библиография |
| `scripts/` | Вспомогательные скрипты сборки и проверки |
| `tasks/`, `Taskfile.yml` | Команды Task |
| `docker/`, `docker-compose.yaml` | Docker-профили сборки |
| `tests/` | Тесты вспомогательных скриптов |

Основной `.tex`-файл содержит только реферат, введение с dummy-текстом и
список dummy-источников. Все предметные данные должны добавляться автором
нового проекта самостоятельно.
