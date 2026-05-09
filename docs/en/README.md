# Diploma sources

This repository contains the source files for the diploma project: `LaTeX` documents, `Mermaid` diagrams, Python diagrams, DOCX templates for title pages, and Docker profiles for reproducible builds.

## Main workflow

!!! info "Required tools"
    If you are opening the project for the first time, start with [Requirements](requirements.md). It briefly lists the tools needed for Docker builds, local builds, and PDF comparison.

!!! tip "If you already know what to do"
    Open [Common scenarios](common-scenarios.md): it contains short instructions for building the PDF, updating diagrams and title pages, connecting source code, and comparing versions.

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
    task build:images
    task build
    ```

=== "Manual"

    ```bash
    docker compose --profile docx --profile mermaid --profile python --profile latex build
    python scripts/build_all.py
    ```

The result is closest to the original if Mermaid diagrams are built on Windows. When Mermaid is built through Docker, the font used for KaTeX expressions can differ from the original.

The main workflow requires Docker. If Docker is not used, see [Build without Docker](manual-build.md).
