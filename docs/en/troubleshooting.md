# Compilation issues

If you use `latexmk`, you do not need to repeat compilation manually: it runs `lualatex` and `biber` as many times as required. The first `latexmk` run in this project can take about 74 seconds because `latexmk` builds service state and analyzes dependencies. Repeated builds take about 18 seconds, while the manual `--no-latexmk` mode takes about 53-54 seconds every time. Repeated manual runs are only needed for fully manual compilation from [Build without Docker](manual-build.md#fully-manual-compilation). For `scripts/build_latex_manual.py`, the old manual mode is enabled with `--no-latexmk`.

!!! tip "Minimal diagnostics"
    If the project does not compile:

    1. Run the command from `cmd`, not PowerShell.
    2. If that does not work, rename the `.tex` file to `main.tex` or another Latin-only name.
    3. Try the minimal command:

=== "Task"

    ```bash
    task latex:local -- --target main.tex
    ```

=== "Manual"

    ```bash
    latexmk main.tex
    ```

If the build fails because of bibliography, check that `biber` is used instead of `bibtex`.[^biber]

!!! note "PDF did not update"
    If the final PDF did not update, check `.aux_files` and `.aux_files_docker`: the result may have stayed inside an auxiliary directory.

[^biber]: The project uses `biblatex` with the `biber` backend; `bibtex` reads a different auxiliary file format and will not process this bibliography correctly.
