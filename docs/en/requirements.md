# Requirements

The required toolset depends on how you build the project.

| Tool | When it is needed | How to check |
| --- | --- | --- |
| Task | Recommended entry point for project commands | `task --version` |
| Docker | Full reproducible build, Zensical, DOCX conversion | `docker --version` |
| Python | Local helper scripts and Python diagrams | `python --version` |
| TeX Live | Local LaTeX build without Docker | `lualatex --version` |
| latexmk | Fast local LaTeX build | `latexmk --version` |
| biber | Bibliography for local builds | `biber --version` |
| diff-pdf | Visual PDF comparison between commits | `diff-pdf --help` |

!!! tip "Shortest path"
    If the goal is only to build the final PDF, install Task and Docker, then run the commands from [Quick start](quick-start.md).

!!! note "Local build without Docker"
    A build without Docker requires TeX Live, `latexmk`, `lualatex`, and `biber`. On Windows, `latexmk` and `biber` usually come with TeX Live.

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
| Investigate a build error | [Compilation issues](troubleshooting.md) |
