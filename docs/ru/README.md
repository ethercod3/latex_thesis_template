# Исходники диплома

Здесь собраны исходники диплома и все, что нужно для повторной сборки: `LaTeX`-файлы, диаграммы, DOCX-шаблоны титульных страниц, скрипты и Docker-профили.

Если вы впервые открыли проект, начните с [Что нужно установить](requirements.md). Если уже знаете, что хотите сделать, откройте [Частые сценарии](common-scenarios.md): там коротко расписаны сборка PDF, обновление диаграмм, титульных страниц, подключение кода и сравнение версий.

## Быстрый путь

Установите Task:

```powershell
winget install Task.Task
```

Для macOS или Linux с Homebrew:

```bash
brew install go-task/tap/go-task
```

Если эти варианты не подходят, используйте официальную инструкцию установки: <https://taskfile.dev/docs/installation>.

Проверить установку:

```bash
task --version
task --list
```

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

Готовый PDF появится в корне проекта. Для этого сценария нужен Docker; если вы собираете без него, используйте [Сборка без Docker](manual-build.md).

Максимально близкий к оригиналу результат получается, если `Mermaid`-диаграммы пересобирать в Windows. При сборке через Docker шрифт в `KaTeX`-выражениях может немного отличаться.
