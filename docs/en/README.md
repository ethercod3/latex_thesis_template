# Diploma sources

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

This repository contains the source files for the diploma project: `LaTeX` documents, `Mermaid` diagrams, Python diagrams, DOCX templates for title pages, and Docker profiles for reproducible builds.

## Main workflow

!!! info "Required tools"
    If you are opening the project for the first time, start with [Requirements](/en/requirements/). It briefly lists the tools needed for Docker builds, local builds, and PDF comparison.

!!! tip "If you already know what to do"
    Open [Common scenarios](/en/common-scenarios/): it contains short instructions for building the PDF, updating diagrams and title pages, connecting source code, and comparing versions.

Install Task:

```powershell
winget install Task.Task
```

For macOS or Linux with Homebrew:

```bash
brew install go-task/tap/go-task
```

If these options do not fit your environment, use the official installation guide: <https://taskfile.dev/docs/installation>.

Check the installation:

```bash
task --version
task --list
```

=== "Task"

    ```bash
    task build
    ```

=== "Manual"

    ```bash
    python scripts/build_all.py
    ```

The result is closest to the original if Mermaid diagrams are built on Windows. When Mermaid is built through Docker, the font used for KaTeX expressions can differ from the original.

The main workflow requires Docker. If Docker is not used, see [Build without Docker](/en/manual-build/).
