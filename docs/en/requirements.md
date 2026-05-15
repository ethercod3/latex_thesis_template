# Requirements

The required toolset depends on how you build the project.

| Tool | When it is needed | How to check |
| --- | --- | --- |
| Task | Recommended entry point for project commands | `task --version` |
| Docker | Full reproducible build, Zensical, DOCX conversion | `docker --version` |
| Python | Local LaTeX compilation through PyLuaTeX, helper scripts, and Python diagrams | `python --version` |
| TeX Live | Local LaTeX build without Docker | `lualatex --version` |
| latexmk | Fast local LaTeX build | `latexmk --version` |
| biber | Bibliography for local builds | `biber --version` |
| Mermaid CLI | Local Mermaid diagram build | `mmdc --version` |
| pdfcrop | Cropping PDFs after local Mermaid build | `pdfcrop --version` |
| Ghostscript | Required by `pdfcrop`, DOCX conversion, and PDF page color analysis | `gs --version` |
| qpdf | Extracting PDF pages without changing rotation or geometry | `qpdf --version` |
| diff-pdf | Visual PDF comparison between commits | `diff-pdf --help` |
| rclone | Backing up `git bundle` files to cloud storage | `rclone version` |

!!! tip "Shortest path"
    If the goal is only to build the final PDF, install Task and Docker, then run the commands from [Quick start](quick-start.md).

!!! tip "Environment check"
    After installing the tools, run `task check`. It checks programs, Python packages, and PyLuaTeX, then reports what is ready and what still needs to be installed.

    If Python is not installed yet and you only need to check the environment, download `diploma-latex-check.exe` from GitHub Releases, put it into the project root, and run:

    ```powershell
    .\diploma-latex-check.exe
    ```

    This check does not require Python to start the checker itself, but a local LaTeX build without Docker still requires the `python` command in `PATH` because the document uses PyLuaTeX.

!!! note "Local build without Docker"
    A build without Docker requires TeX Live, Python, `latexmk`, `lualatex`, and `biber`. On Windows, `latexmk` and `biber` usually come with TeX Live. Python is needed by the LaTeX document itself too: it uses PyLuaTeX and runs the `python` command during compilation.

!!! note "PDF crop without Docker"
    The local `task mermaid` and `task crop -- path/to/file.pdf` commands require `pdfcrop` and Ghostscript. To generate Mermaid diagrams without cropping margins, run `task mermaid -- --no-crop`. If local dependencies are not installed, use Docker profiles: `task mermaid:docker` or `task crop:docker -- path/to/file.pdf`.

!!! note "Splitting PDF into color and B/W pages"
    `task pdf:split-color -- path/to/file.pdf` runs in the LaTeX Docker image. Inside the container, Ghostscript detects color pages through `inkcov`, and `qpdf` exports the selected pages into `*_color.pdf` and `*_bw.pdf` without redrawing the original pages.

!!! note "Script tests"
    Python dependencies in `requirements.txt` include `pytest`. After `task deps`, run helper-script tests with `task python:test`.

## Common scenarios

| What you need to do | Where to go |
| --- | --- |
| Build the final PDF | [Quick start](quick-start.md) |
| Build without Docker | [Build without Docker](manual-build.md) |
| Configure TeXstudio | [TeXstudio setup](texstudio.md) |
| Rebuild the title page and assignment | [Title page and assignment](title-pages.md) |
| Rebuild diagrams | [Diagrams](diagrams.md) |
| Connect application source code | [Source code in appendices](source-code.md) |
| Compare PDFs between commits | [PDF comparison between commits](pdf-diff.md) |
| Split PDF into color and B/W pages | [Splitting PDF into color and B/W pages](pdf-color-split.md) |
| Configure backups | [Backups](backup.md) |
| Investigate a build error | [Compilation issues](troubleshooting.md) |
| Check CI/CD and release assets | [CI/CD and releases](ci.md) |
