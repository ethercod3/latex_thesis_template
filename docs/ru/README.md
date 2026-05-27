# Исходники диплома

[![Publish Zensical docs](https://github.com/ethercod3/diploma_latex/actions/workflows/pages.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/pages.yml)
[![Release PDF](https://github.com/ethercod3/diploma_latex/actions/workflows/pdf-release.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/pdf-release.yml)
[![Check tools exe CI](https://github.com/ethercod3/diploma_latex/actions/workflows/check-tools-exe.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/check-tools-exe.yml)
[![Backup git bundle](https://github.com/ethercod3/diploma_latex/actions/workflows/backup.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/backup.yml)

![LaTeX](https://img.shields.io/badge/LaTeX-LuaLaTeX-008080?style=flat-square&logo=latex)
![latexmk](https://img.shields.io/badge/Build-latexmk-008080?style=flat-square&logo=latex)
![biblatex](https://img.shields.io/badge/Bibliography-biblatex-008080?style=flat-square&logo=latex)
![biber](https://img.shields.io/badge/Backend-biber-008080?style=flat-square&logo=latex)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white)
![Zensical](https://img.shields.io/badge/Docs-Zensical-5B5BD6?style=flat-square)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-222222?style=flat-square&logo=githubpages&logoColor=white)
![Task](https://img.shields.io/badge/Tasks-go--task-29BEB0?style=flat-square&logo=task&logoColor=white)
![rclone](https://img.shields.io/badge/Backup-rclone-00AEEF?style=flat-square)
![LibreOffice](https://img.shields.io/badge/DOCX-LibreOffice-18A303?style=flat-square&logo=libreoffice&logoColor=white)

![Last commit](https://img.shields.io/github/last-commit/ethercod3/diploma_latex/main)
![Repo size](https://img.shields.io/github/repo-size/ethercod3/diploma_latex)
![Latest release](https://img.shields.io/github/v/release/ethercod3/diploma_latex)

Здесь собраны исходники диплома и все, что нужно для повторной сборки: `LaTeX`-файлы, диаграммы, DOCX-шаблоны титульных страниц, скрипты и Docker-профили.

Работа выполнена в рамках выпускной квалификационной работы в федеральном государственном бюджетном образовательном учреждении высшего образования «Амурский государственный университет». Упоминание университета приведено как контекст выполнения работы и не означает передачу исключительных прав на материалы репозитория, если иное не указано отдельным соглашением.

## Быстрый путь

!!! info "Что нужно установить"
    Если вы впервые открыли проект, начните с [Что нужно установить](requirements.md). Там кратко перечислены инструменты для Docker-сборки, локальной сборки и сравнения PDF.

!!! tip "Если уже знаете, что хотите сделать"
    Откройте [Частые сценарии](common-scenarios.md): там коротко расписаны сборка PDF, обновление диаграмм и титульных страниц, разделение PDF на цветные/ЧБ страницы, подключение кода, сравнение версий и запуск Stirling PDF.

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
    task build
    ```

=== "Ручной"

    ```bash
    uv run python scripts/build_all.py
    ```

Готовый PDF появится в корне проекта. Для этого сценария нужен Docker; если вы собираете без него, используйте [Сборка без Docker](manual-build.md).

Максимально близкий к оригиналу результат получается, если `Mermaid`-диаграммы пересобирать в Windows. При сборке через Docker шрифт в `KaTeX`-выражениях может немного отличаться.

Если нужен локальный браузерный просмотр PDF без отдельного PDF-viewer на машине, используйте [Stirling PDF](stirling.md).
