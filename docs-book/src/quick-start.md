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

Соберите Docker-образы и запустите полную сборку:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task build:images
task build
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
docker compose --profile docx --profile mermaid --profile python --profile latex build
python scripts/build_all.py
```

{{#endtab}}

{{#endtabs}}

Скрипт `scripts/build_all.py` запускает профили в порядке: `docx` \\(\\rightarrow\\) `mermaid` \\(\\rightarrow\\) `python` \\(\\rightarrow\\) `latex`.

Первый `build` будет долгим. Повторно выполнять `build` нужно только после изменения Dockerfile, зависимостей или базовых образов.

Если Docker-образы уже собраны, достаточно:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task build
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
python scripts/build_all.py
```

{{#endtab}}

{{#endtabs}}

Все вспомогательные Python-скрипты запускаются одинаково в Windows, Linux и macOS:

{{#tabs global="runmode"}}

{{#tab name="Task"}}

```bash
task build
task mermaid
task diagrams
```

{{#endtab}}

{{#tab name="Ручной"}}

```bash
python scripts/build_all.py
python scripts/compile_mermaid.py
python scripts/compile_python_diagrams.py
```

{{#endtab}}

{{#endtabs}}
