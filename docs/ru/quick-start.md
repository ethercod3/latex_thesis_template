# Быстрый старт

Эта страница для случая, когда нужно быстро получить итоговый PDF и не разбираться во всех деталях проекта.

## Установка Task

Проект использует [Task](https://taskfile.dev/docs/installation), чтобы не держать в голове длинные команды Docker и Python-скриптов.

Windows:

```powershell
winget install Task.Task
```

macOS или Linux с Homebrew:

```bash
brew install go-task/tap/go-task
```

Любая платформа с Node.js:

```bash
npm install -g @go-task/cli
```

Если эти варианты не подходят, используйте официальную инструкцию установки: <https://taskfile.dev/docs/installation>.

Проверить установку:

```bash
task --version
task --list
```

## Сборка

!!! tip "Перед первым запуском"
    Проверьте, что установлен Docker, доступна команда `task`, а файл `.env` создан, если проекту нужны локальные пути к коду.

Сначала соберите Docker-образы, затем запустите полную сборку:

=== "Task"

    ```bash
    task build:images
    task build
    ```

=== "Ручной"

    ```bash
    docker compose --profile docx --profile mermaid --profile python --profile latex build
    python scripts/build_all.py
    ```

`scripts/build_all.py` запускает профили по порядку: `docx` {{ arrow }} `mermaid` {{ arrow }} `python` {{ arrow }} `latex`. Так титульные страницы и диаграммы успевают обновиться до сборки основного PDF.

!!! info "Первый запуск"
    Первый `build` обычно долгий: Docker скачивает базовые образы и собирает окружение. Повторно выполнять `task build:images` нужно только после изменения Dockerfile, зависимостей или базовых образов.

Когда образы уже собраны, достаточно одной команды:

=== "Task"

    ```bash
    task build
    ```

=== "Ручной"

    ```bash
    python scripts/build_all.py
    ```

После сборки итоговый PDF лежит в корне проекта.

Чтобы посмотреть и удалить сгенерированные артефакты сборки, используйте:

```bash
task clean:dry
task clean
```

Все вспомогательные Python-скрипты запускаются одинаково в Windows, Linux и macOS.[^mermaid-fonts]

=== "Task"

    ```bash
    task build
    task mermaid
    task diagrams
    ```

=== "Ручной"

    ```bash
    python scripts/build_all.py
    python scripts/compile_mermaid.py
    python scripts/compile_python_diagrams.py
    ```

[^mermaid-fonts]: Mermaid-диаграммы лучше пересобирать в той же среде, где готовился оригинал. При сборке через Docker шрифт для KaTeX-выражений может отличаться от результата из Windows.
