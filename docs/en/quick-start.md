# Quick start

## Install Task

The project uses [Task](https://taskfile.dev/docs/installation) as the single entry point for builds and helper commands.

Windows:

```powershell
winget install Task.Task
```

macOS or Linux with Homebrew:

```bash
brew install go-task/tap/go-task
```

Any platform with Node.js:

```bash
npm install -g @go-task/cli
```

If these options do not fit your environment, use the official installation guide: <https://taskfile.dev/docs/installation>.

Check the installation:

```bash
task --version
task --list
```

If Python is not installed yet but you need to check the environment, download `diploma-latex-check.exe` from GitHub Releases, put it into the project root, and run:

```powershell
.\diploma-latex-check.exe
```

## Build

!!! tip "Before the first run"
    - [ ] Docker is installed;
    - [ ] Task is installed, or the manual commands are ready;
    - [ ] `.env` is created if the build needs local paths to source code;
    - [ ] the title page, assignment, and diagrams can be rebuilt from source.

Build Docker images and run the full build:

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

The `scripts/build_all.py` script runs profiles in this order: `docx` {{ arrow }} `mermaid` {{ arrow }} `python` {{ arrow }} `latex`.

!!! info "First run"
    The first `build` will take a while. Run `build` again only after changing a Dockerfile, dependencies, or base images.

If the Docker images are already built, this is enough:

=== "Task"

    ```bash
    task build
    ```

=== "Manual"

    ```bash
    python scripts/build_all.py
    ```

To preview and remove generated build artifacts, use:

```bash
task clean:dry
task clean
```

All helper Python scripts are started the same way on Windows, Linux, and macOS.[^mermaid-fonts]

=== "Task"

    ```bash
    task build
    task mermaid
    task diagrams
    ```

=== "Manual"

    ```bash
    python scripts/build_all.py
    python scripts/compile_mermaid.py
    python scripts/compile_python_diagrams.py
    ```

[^mermaid-fonts]: Mermaid diagrams are best rebuilt in the same environment where the original was prepared: when built through Docker, the font for KaTeX expressions can differ from the Windows result.
