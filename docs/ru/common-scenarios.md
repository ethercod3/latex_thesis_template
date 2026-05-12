# Частые сценарии

Здесь собраны короткие маршруты для частых задач. Выберите нужный сценарий и выполните команды из блока `Task`; ручные команды оставлены рядом на случай, если Task не установлен.

## Собрать итоговый PDF

!!! tip "Рекомендуемый путь"
    Используйте Docker-сборку: она последовательно подготовит титульные страницы, Mermaid-диаграммы, Python-диаграммы и итоговый PDF.

=== "Task"

    ```bash
    task build
    ```

=== "Ручной"

    ```bash
    python scripts/build_all.py
    ```

После сборки итоговый PDF появится в корне проекта. Если команда падает, откройте [Проблемы с компиляцией](/troubleshooting/).

!!! note "Когда собирать образы отдельно"
    `task build` запускает профильные контейнеры через `docker compose run --build`, поэтому отдельная команда `task build:images` обычно не нужна. Используйте ее только если хотите заранее пересобрать все Docker-образы.

## Собрать без Docker

1. Установите TeX Live, Python, `latexmk`, `lualatex` и `biber`. Python нужен PyLuaTeX во время компиляции LaTeX.
2. Подготовьте внешние артефакты: титульник, задание, диаграммы и код приложений.
3. Запустите локальную сборку.

=== "Task"

    ```bash
    task latex:local
    ```

=== "Ручной"

    ```bash
    latexmk "Куприянов_И221_диплом.tex"
    ```

Подробности: [Сборка без Docker](/manual-build/).

## Обновить диаграммы

Если менялись `mermaid/*.mmd`, пересоберите Mermaid-диаграммы:

=== "Task"

    ```bash
    task mermaid
    ```

=== "Ручной"

    ```bash
    python scripts/compile_mermaid.py
    ```

Если менялись `python_diagrams/*.py`, пересоберите Python-диаграммы:

=== "Task"

    ```bash
    task diagrams
    ```

=== "Ручной"

    ```bash
    python scripts/compile_python_diagrams.py
    ```

После обновления диаграмм пересоберите основной PDF. Подробнее: [Диаграммы](/diagrams/).

## Обновить титульник или задание

1. Измените DOCX-файл в `docx/`.
2. Пересоберите PDF-версии титульных страниц.
3. Пересоберите основной документ.

=== "Task"

    ```bash
    task docx
    task build
    ```

=== "Ручной"

    ```bash
    docker compose --profile docx up
    python scripts/build_all.py
    ```

Если пустые страницы нужно сохранить, используйте `task docx:keep-blank`. Подробнее: [Титульник и задание](/title-pages/).

## Подключить код приложения

Положите код рядом с папкой LaTeX-проекта и проверьте пути в `.env`:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="../vault_diploma"
```

!!! note "Что означает путь"
    `VAULT_OS_PATH` - путь на вашей машине, а `VAULT_PATH` - путь внутри Docker-контейнера.

Подробнее: [Код в приложениях](/source-code/).

## Сравнить PDF между коммитами

Перед запуском убедитесь, что рабочее дерево Git чистое.

=== "Task"

    ```bash
    task diff -- <commit_1> <commit_2>
    ```

=== "Ручной"

    ```bash
    python scripts/diff_pdf_commits.py <commit_1> <commit_2>
    ```

Подробнее: [Сравнение PDF между коммитами](/pdf-diff/).

## Запустить документацию локально

=== "Task"

    ```bash
    task docs
    ```

=== "Ручной"

    ```bash
    docker compose --profile docs up docs
    ```

После запуска откройте:

```text
http://localhost:8000
```

Подробнее: [Документация](/zensical/).
