# Быстрый старт

## Установка Task

Проект использует [Task](https://taskfile.dev/docs/installation) как единую точку входа для сборки и вспомогательных команд.

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
    - [ ] установлен Docker;
    - [ ] установлен Task или подготовлены ручные команды;
    - [ ] создан `.env`, если сборка требует локальные пути к коду;
    - [ ] титульник, задание и диаграммы можно пересобрать из исходников.

Соберите Docker-образы и запустите полную сборку:



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





Скрипт `scripts/build_all.py` запускает профили в порядке: `docx` {{ arrow }} `mermaid` {{ arrow }} `python` {{ arrow }} `latex`.

!!! info "Первый запуск"
    Первый `build` будет долгим. Повторно выполнять `build` нужно только после изменения Dockerfile, зависимостей или базовых образов.

Если Docker-образы уже собраны, достаточно:



=== "Task"


    ```bash
    task build
    ```



=== "Ручной"


    ```bash
    python scripts/build_all.py
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

[^mermaid-fonts]: Mermaid-диаграммы лучше пересобирать в той же среде, где готовился оригинал: при сборке через Docker шрифт для KaTeX-выражений может отличаться от Windows-результата.

