[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)

![LaTeX](https://img.shields.io/badge/LaTeX-LuaLaTeX-008080?style=flat-square&logo=latex)
![latexmk](https://img.shields.io/badge/Build-latexmk-008080?style=flat-square&logo=latex)
![biblatex](https://img.shields.io/badge/Bibliography-biblatex-008080?style=flat-square&logo=latex)
![biber](https://img.shields.io/badge/Backend-biber-008080?style=flat-square&logo=latex)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![Nushell](https://img.shields.io/badge/Shell-Nushell-4E9A06?style=flat-square&logo=nushell&logoColor=white)
![uv](https://img.shields.io/badge/Deps-uv-6D4AFF?style=flat-square)
![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white)
![Zensical](https://img.shields.io/badge/Docs-Zensical-5B5BD6?style=flat-square)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Task](https://img.shields.io/badge/Tasks-go--task-29BEB0?style=flat-square&logo=task&logoColor=white)
![rclone](https://img.shields.io/badge/Backup-rclone-00AEEF?style=flat-square)
![LibreOffice](https://img.shields.io/badge/DOCX-LibreOffice-18A303?style=flat-square&logo=libreoffice&logoColor=white)

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
