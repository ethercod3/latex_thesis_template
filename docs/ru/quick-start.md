# Быстрый старт

Эта страница для случая, когда нужно быстро получить итоговый PDF и не разбираться во всех деталях проекта.

## Установка инструментов

Если у вас установлен [mise](https://mise.jdx.dev/), используйте его как самый короткий путь к нужным версиям Python, uv и Task:

```bash
mise trust
mise install
mise run setup
mise run check
```

После этого можно запускать основные команды через `mise run build`, `mise run test` или напрямую через `task`.

## Установка Task вручную

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

Если Python еще не установлен, но нужно проверить состояние проекта, можно скачать `diploma-latex-check.exe` из GitHub Releases, положить его в корень проекта и запустить:

```powershell
.\diploma-latex-check.exe
```

## Сборка

!!! tip "Перед первым запуском"
    Проверьте, что установлен Docker, доступна команда `task`, а файл `.env` создан, если проекту нужны локальные пути к коду.

Запустите полную Docker-сборку:

=== "Task"

    ```bash
    task build
    ```

=== "Ручной"

    ```bash
    uv run python scripts/build_all.py
    ```

`scripts/build_all.py` запускает профили по порядку: `docx` {{ arrow }} `mermaid` {{ arrow }} `python` {{ arrow }} `latex`. Так титульные страницы и диаграммы успевают обновиться до сборки основного PDF.

!!! info "Первый запуск"
    Первый `build` обычно долгий: Docker скачивает базовые образы и собирает окружение. Скрипт запускает профили через `docker compose run --build`, поэтому Docker проверяет актуальность образов перед каждым профилем.

После сборки итоговый PDF лежит в корне проекта.

Чтобы посмотреть и удалить сгенерированные артефакты сборки, используйте:

```bash
task clean:dry
task clean
```

Проверить Python-скрипты тестами:

```bash
task python:test
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
    uv run python scripts/build_all.py
    uvx --from git+https://github.com/ethercod3/compile_mermaid.git compile-mermaid
    uv run python scripts/compile_python_diagrams.py
    ```

[^mermaid-fonts]: Mermaid-диаграммы лучше пересобирать в той же среде, где готовился оригинал. При сборке через Docker шрифт для KaTeX-выражений может отличаться от результата из Windows.
