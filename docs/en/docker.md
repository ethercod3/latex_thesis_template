# Docker profiles

```mermaid
flowchart LR
    DOCX["docx<br/>DOCX -> PDF"] --> LATEX["latex<br/>diploma build"]
    MERMAID["mermaid<br/>.mmd -> figures/*.pdf"] --> LATEX
    PYTHON["python<br/>python_diagrams -> figures/"] --> LATEX
    LATEX --> PDF["Куприянов_И221_диплом.pdf"]
    DOCS["docs<br/>Zensical build + static serve"] --> SITE["http://localhost:8000"]
```

## Environment variables

Create a `.env` file in the project root:

```env
VAULT_PATH="mount path"
VAULT_OS_PATH="actual path to code on the device"
TARGET="latex file"
```

Example:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="../vault_diploma"
TARGET="Куприянов_И221_диплом.tex"
```

Explanation:

| Variable | Purpose |
| --- | --- |
| `VAULT_PATH` | Any absolute Unix path inside the container |
| `VAULT_OS_PATH` | Where the code is located relative to the current directory |
| `TARGET` | Main `.tex` file |
| `HOST_UID`, `HOST_GID` | Optional user UID/GID for Linux CI so containers can write to bind mounts without permission issues |

## LaTeX

Build the LaTeX image:

=== "Task"

    ```bash
    task build:image -- latex
    ```

=== "Manual"

    ```bash
    docker compose --profile latex build
    ```

Run compilation:

=== "Task"

    ```bash
    task latex:docker
    ```

=== "Manual"

    ```bash
    docker compose --profile latex run --build --rm latex
    ```

The `latex` profile runs `scripts/build_latex_docker.py`. The script reads `TARGET` from environment variables and builds the document through `latexmk`. Auxiliary files are placed into `.aux_files_docker`, and the final PDF stays in the project root. The `run --build` form checks that the image is current before starting it, so Docker does not reuse an old image after Dockerfile changes.

## Building images

Build all Docker images for the project:

=== "Task"

    ```bash
    task build:images
    ```

=== "Manual"

    ```bash
    docker compose --profile docx --profile mermaid --profile python --profile latex --profile crop build
    ```

Build one profile image:

=== "Task"

    ```bash
    task build:image -- latex
    task build:image -- mermaid
    task build:image -- python
    task build:image -- docx
    task build:image -- crop
    ```

=== "Manual"

    ```bash
    docker compose --profile latex build
    docker compose --profile mermaid build
    docker compose --profile python build
    docker compose --profile docx build
    docker compose --profile crop build
    ```

Profile commands use `docker compose run --build`, so Docker checks whether images are current before running containers. The first run still takes time because Docker downloads base images and builds the environment.

## Available profiles

The project uses separate Docker Compose profiles:

| Profile | Purpose |
| --- | --- |
| `docx` | Converts DOCX files from `docx/` to PDF |
| `mermaid` | Generates Mermaid diagrams into `figures/` |
| `python` | Generates diagrams with Python scripts |
| `latex` | Builds the final diploma PDF |
| `crop` | Crops margins of any PDF through `pdfcrop` |
| `docs` | Builds and runs local bilingual documentation |

Run separate profiles:

=== "Task"

    ```bash
    task latex:docker
    task mermaid:docker
    task diagrams:docker
    task docx
    task crop:docker -- path/to/file.pdf
    ```

=== "Manual"

    ```bash
    docker compose --profile latex run --build --rm latex
    docker compose --profile mermaid run --build --rm mermaid_diagrams
    docker compose --profile python run --build --rm python_diagrams
    docker compose --profile docx run --build --rm docx_pdf
    docker compose --profile crop run --build --rm crop_pdf python3 scripts/crop_pdf.py path/to/file.pdf
    ```

Run all profiles with one command:

=== "Task"

    ```bash
    task compose:up
    ```

=== "Manual"

    ```bash
    docker compose --profile docx --profile mermaid --profile python --profile latex up
    ```

When all profiles are started together, Docker Compose starts services together. If you need to guarantee that the document is built with fresh PDFs from DOCX and diagrams, run `docx`, `mermaid`, and `python` first, then run `latex`.

Sequential profile execution is moved into a script:

```mermaid
flowchart LR
    START["task build"] --> DOCX["docx"]
    DOCX --> MERMAID["mermaid"]
    MERMAID --> PYTHON["python"]
    PYTHON --> LATEX["latex"]
    LATEX --> PDF["ready PDF"]
```

=== "Task"

    ```bash
    task build
    ```

=== "Manual"

    ```bash
    python scripts/build_all.py
    ```

`scripts/build_all.py` runs profiles in the order `docx` {{ arrow }} `mermaid` {{ arrow }} `python` {{ arrow }} `latex` and stops at the first error.

!!! note "File permissions in Linux CI"
    In GitHub Actions, the workflow writes `HOST_UID` and `HOST_GID` to `.env`. Docker Compose uses these values in `user: "${HOST_UID:-0}:${HOST_GID:-0}"` so containers create PDFs and diagrams as the runner user. Without these variables, local builds use the `0:0` fallback.
