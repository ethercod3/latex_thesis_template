# Исходники диплома

<!-- [![Publish Zensical docs](https://github.com/ethercod3/diploma_latex/actions/workflows/pages.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/pages.yml)
[![Release PDF](https://github.com/ethercod3/diploma_latex/actions/workflows/pdf-release.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/pdf-release.yml)
[![Check tools exe CI](https://github.com/ethercod3/diploma_latex/actions/workflows/check-tools-exe.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/check-tools-exe.yml)
[![Backup git bundle](https://github.com/ethercod3/diploma_latex/actions/workflows/backup.yml/badge.svg)](https://github.com/ethercod3/diploma_latex/actions/workflows/backup.yml) -->

![LaTeX](https://img.shields.io/badge/LaTeX-LuaLaTeX-008080?style=flat-square&logo=latex)
![latexmk](https://img.shields.io/badge/Build-latexmk-008080?style=flat-square&logo=latex)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Test count](https://img.shields.io/badge/Test%20suite-43%20passed-2EA44F?style=flat-square)
![Coverage](https://img.shields.io/badge/Coverage-35%25-orange?style=flat-square)
![Black](https://img.shields.io/badge/Style-Black-000000?style=flat-square)
![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![Mermaid](https://img.shields.io/badge/Diagrams-Mermaid-FF3670?style=flat-square&logo=mermaid&logoColor=white)
![Zensical](https://img.shields.io/badge/Docs-Zensical-5B5BD6?style=flat-square)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-222222?style=flat-square&logo=githubpages&logoColor=white)
![Task](https://img.shields.io/badge/Tasks-go--task-29BEB0?style=flat-square&logo=task&logoColor=white)
![rclone](https://img.shields.io/badge/Backup-rclone-00AEEF?style=flat-square)
![LibreOffice](https://img.shields.io/badge/DOCX-LibreOffice-18A303?style=flat-square&logo=libreoffice&logoColor=white)

Здесь собраны исходники диплома и все, что нужно для повторной сборки: `LaTeX`-файлы, диаграммы, DOCX-шаблоны титульных страниц, скрипты и Docker-профили.

Если вы впервые открыли проект, начните с [Что нужно установить](/requirements/). Если уже знаете, что хотите сделать, откройте [Частые сценарии](/common-scenarios/): там коротко расписаны сборка PDF, обновление диаграмм, титульных страниц, подключение кода и сравнение версий.

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
    task build
    ```

=== "Ручной"

    ```bash
    python scripts/build_all.py
    ```

Готовый PDF появится в корне проекта. Для этого сценария нужен Docker; если вы собираете без него, используйте [Сборка без Docker](/manual-build/).

Максимально близкий к оригиналу результат получается, если `Mermaid`-диаграммы пересобирать в Windows. При сборке через Docker шрифт в `KaTeX`-выражениях может немного отличаться.
