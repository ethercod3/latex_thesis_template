# Project structure

```mermaid
flowchart LR
    TEX["*.tex<br/>preamble/"] --> PDF["Final PDF"]
    DOCX["docx/*.docx"] --> TITLE["титульник.pdf<br/>задание.pdf"]
    MMD["mermaid/*.mmd"] --> FIGURES["figures/*.pdf"]
    PYD["python_diagrams/*.py"] --> FIGURES
    TITLE --> TEX
    FIGURES --> TEX
    SCRIPTS["scripts/*.py"] --> DOCX
    SCRIPTS --> MMD
    SCRIPTS --> PYD
    CI["scripts/ci/*.py<br/>.github/workflows"] --> RELEASE["GitHub Releases"]
    BACKUP["scripts/backup_project.py<br/>backup.yml"] --> CLOUD["Google Drive<br/>Yandex Disk"]
    DOCKER["docker/<br/>docker-compose.yaml"] --> SCRIPTS
    DOCS["docs/ru/*.md<br/>docs/en/*.md"] --> SITE["docs-site/"]
```

| Path | Purpose |
| --- | --- |
| `*.tex`, `preamble/` | LaTeX documents and preamble settings |
| `docx/` | DOCX sources for the title page and assignment |
| `mermaid/` | Mermaid diagram sources |
| `python_diagrams/` | Python scripts that generate diagrams |
| `figures/` | Generated images and PDFs inserted into the document |
| `scripts/` | Helper scripts for building, conversion, PDF comparison, and backups |
| `scripts/ci/` | Python scripts for GitHub Actions and release publishing |
| `docker/` | Dockerfiles for separate build profiles |
| `docs/ru/`, `docs/en/` | Zensical documentation for the project |
| `docs/includes/` | Shared Markdown includes for Zensical documentation |
| `tasks/` | Thematic Taskfiles with build and maintenance commands; the command list is available through `task --list` |
| `tests/` | Pytest tests for pure helper-script logic |
| `.github/workflows/` | GitHub Actions for Pages, check tools, PDF releases, and backups |

Key files:

| File | Purpose |
| --- | --- |
| `Куприянов_И221_диплом.tex` | Main LaTeX file of the diploma |
| `bibliography.bib` | Bibliography for `biblatex` |
| `requirements.txt` | Python dependencies for scripts and diagrams |
| `pyproject.toml` | Python tooling settings, including Black |
| `docker-compose.yaml` | Docker Compose profiles for the project |
| `docker-compose.ci-cache.yaml` | CI-only Compose override for Docker BuildKit cache in GitHub Actions |
| `Taskfile.yml` | Single Task entry point that includes files from `tasks/` |
| `.env` | Local environment variables for the build |

The `.env` file is not committed because it contains local paths.[^env-local]

[^env-local]: `.env` can contain absolute paths for a specific machine, for example the path to the directory with appendix code. If this file is committed, the build on another machine will almost certainly point to a nonexistent location.
