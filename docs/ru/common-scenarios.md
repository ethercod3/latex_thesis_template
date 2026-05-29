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
    uv run python scripts/build_all.py
    ```

После сборки итоговый PDF появится в корне проекта. Если команда падает, откройте [Проблемы с компиляцией](troubleshooting.md).

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

Подробности: [Сборка без Docker](manual-build.md).

## Обновить диаграммы

Если менялись `mermaid/*.mmd`, пересоберите Mermaid-диаграммы:

=== "Task"

    ```bash
    task mermaid
    ```

=== "Ручной"

    ```bash
    uv run python scripts/compile_mermaid.py
    ```

Если менялись `python_diagrams/*.py`, пересоберите Python-диаграммы:

=== "Task"

    ```bash
    task diagrams
    ```

=== "Ручной"

    ```bash
    uv run python scripts/compile_python_diagrams.py
    ```

После обновления диаграмм пересоберите основной PDF. Подробнее: [Диаграммы](diagrams.md).

## Обрезать поля PDF

Команда обновляет исходный PDF на месте, поэтому перед запуском убедитесь, что выбран правильный файл.

=== "Task"

    ```bash
    task crop -- path/to/file.pdf
    ```

=== "Docker"

    ```bash
    task crop:docker -- path/to/file.pdf
    ```

Локальный вариант требует `pdfcrop` и Ghostscript. Docker-вариант использует отдельный Alpine-образ с `texlive-binextra` и Ghostscript.

## Разделить PDF на цветные и ЧБ страницы

Команда создает два файла рядом с исходным PDF: `*_color.pdf` только с цветными страницами и `*_bw.pdf` только с черно-белыми страницами.

=== "Task"

    ```bash
    task pdf:split-color -- path/to/file.pdf
    ```

=== "Ручной"

    ```bash
    docker compose --profile latex run --build --rm latex python3 scripts/split_pdf_color.py path/to/file.pdf
    ```

Ghostscript определяет цветные страницы через покрытие C/M/Y, а `qpdf` экспортирует страницы без изменения поворота. Подробнее: [Разделение PDF на цветные и ЧБ страницы](pdf-color-split.md).

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
    uv run python scripts/build_all.py
    ```

Если пустые страницы нужно сохранить, используйте `task docx:keep-blank`. Подробнее: [Титульник и задание](title-pages.md).

## Подключить код приложения

Положите код рядом с папкой LaTeX-проекта и проверьте пути в `.env`:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="../vault_diploma"
```

!!! note "Что означает путь"
    `VAULT_OS_PATH` - путь на вашей машине, а `VAULT_PATH` - путь внутри Docker-контейнера.

Подробнее: [Код в приложениях](source-code.md).

## Сравнить PDF между коммитами

Перед запуском убедитесь, что рабочее дерево Git чистое.

=== "Task"

    ```bash
    task diff -- <commit_1> <commit_2>
    ```

=== "Ручной"

    ```bash
    uvx diff-pdf-commits --build "<команда сборки>" --pdf "<PDF из TARGET>" --view <commit_1> <commit_2>
    ```

Подробнее: [Сравнение PDF между коммитами](pdf-diff.md).

## Открыть Stirling PDF

Stirling PDF - это локальный веб-интерфейс, который удобно использовать для ручной проверки и сверки PDF в браузере.

=== "Task"

    ```bash
    task stirling
    ```

=== "Ручной"

    ```bash
    docker compose --profile stirling up -d stirling_pdf
    ```

После запуска откройте:

```text
http://localhost:8080
```

Для управления доступны команды:

```bash
task stirling:logs
task stirling:down
```

Настройки порта и стартового пароля администратора хранятся в `.env`. Подробнее: [Stirling PDF](stirling.md).

## Создать резервную копию Git-истории

Локально создать и проверить bundle без загрузки:

```bash
task backup:local
```

Загрузить bundle в Google Drive и Яндекс Диск через `rclone`:

```bash
task backup
```

Перед бэкапом закоммитьте или спрячьте важные локальные изменения: `git bundle` сохраняет историю, но не незакоммиченные файлы. Подробнее: [Резервное копирование](backup.md).

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

Подробнее: [Документация](zensical.md).
