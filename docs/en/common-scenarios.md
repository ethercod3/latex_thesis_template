# Common scenarios

This page helps you choose the shortest path when you do not need to read the whole documentation from start to finish.

## Build the final PDF

!!! tip "Recommended path"
    Use the Docker build: it prepares the title pages, Mermaid diagrams, Python diagrams, and the final PDF in sequence.

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

After the build, the final PDF appears in the project root. If the command fails, go to [Compilation issues](/en/troubleshooting/).

## Build without Docker

1. Install TeX Live, `latexmk`, `lualatex`, and `biber`.
2. Prepare external artifacts: the title page, assignment, diagrams, and appendix code.
3. Run the local build.

=== "Task"

    ```bash
    task latex:local
    ```

=== "Manual"

    ```bash
    latexmk "Куприянов_И221_диплом.tex"
    ```

Details: [Build without Docker](/en/manual-build/).

## Update diagrams

If `mermaid/*.mmd` files changed, rebuild Mermaid diagrams:

=== "Task"

    ```bash
    task mermaid
    ```

=== "Manual"

    ```bash
    python scripts/compile_mermaid.py
    ```

If `python_diagrams/*.py` files changed, rebuild Python diagrams:

=== "Task"

    ```bash
    task diagrams
    ```

=== "Manual"

    ```bash
    python scripts/compile_python_diagrams.py
    ```

After updating diagrams, rebuild the main PDF. Details: [Diagrams](/en/diagrams/).

## Update the title page or assignment

1. Edit the DOCX file in `docx/`.
2. Rebuild the PDF versions of the title pages.
3. Rebuild the main document.

=== "Task"

    ```bash
    task docx
    task build
    ```

=== "Manual"

    ```bash
    docker compose --profile docx up
    python scripts/build_all.py
    ```

If blank pages must be preserved, use `task docx:keep-blank`. Details: [Title page and assignment](/en/title-pages/).

## Connect application source code

Place the code next to the LaTeX project directory and check the paths in `.env`:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="../vault_diploma"
```

!!! note "Path meaning"
    `VAULT_OS_PATH` is the path on your machine, and `VAULT_PATH` is the path inside the Docker container.

Details: [Source code in appendices](/en/source-code/).

## Compare PDFs between commits

Before running the command, make sure the Git working tree is clean.

=== "Task"

    ```bash
    task diff -- <commit_1> <commit_2>
    ```

=== "Manual"

    ```bash
    python scripts/diff_pdf_commits.py <commit_1> <commit_2>
    ```

Details: [PDF comparison between commits](/en/pdf-diff/).

## Run the documentation locally

=== "Task"

    ```bash
    task docs
    ```

=== "Manual"

    ```bash
    docker compose --profile docs up docs
    ```

Then open:

```text
http://localhost:8000
```

Details: [Documentation](/en/zensical/).
