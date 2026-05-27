# Build without Docker

The recommended way to build the LaTeX document without Docker is `latexmk`. It runs `lualatex` and `biber` the required number of times using the rules from `.latexmkrc`.

!!! warning "Important"
    In this project, `latexmk` noticeably reduces repeat compilation time. The first run through `latexmk` takes about 74 seconds, and a repeated run takes about 18 seconds. The `--no-latexmk` mode with the manual chain takes about 53-54 seconds every time.

The first `latexmk` run can be longer than a manual build because it builds its service state, analyzes dependencies, creates `.fdb_latexmk`, and performs a full build cycle.[^latexmk-cache] On following runs, `latexmk` uses this information and rebuilds only what actually changed.

## What must be prepared separately

!!! warning "External artifacts"
    `latexmk` builds only the LaTeX document. Before building without Docker, prepare all external artifacts included from `.tex`:

    - `титульник.pdf` and `задание.pdf` must be in the project root. They can be created manually from `docx/*.docx` through Microsoft Word or LibreOffice; see [Title pages](title-pages.md).
    - Mermaid diagrams from `mermaid/*.mmd` must be generated in advance into `figures/`; see [Diagrams](diagrams.md).
    - Python diagrams must be generated in advance with `task diagrams` or manually with `uv run python scripts/compile_python_diagrams.py`.
    - If appendix code is included, it must be located at the expected path; see [Source code in appendices](source-code.md).

    If these files are not prepared, `latexmk` can fail because of missing PDFs, images, or listings.

## Preparation

1. Install a LaTeX distribution. TeX Live is recommended on Windows. `latexmk` usually comes with TeX Live, so it does not need to be installed separately. The project compiler is LuaLaTeX.
2. Install Python and make sure the `python` command is available in `PATH`. It is not only for helper scripts: the document uses PyLuaTeX during LaTeX compilation.
3. Make sure `latexmk`, `lualatex`, and `biber` commands are available.
4. Clone the repository.
5. Install Python dependencies for helper scripts:

=== "Task"

    ```bash
    task deps
    ```

=== "Manual"

    ```bash
    uv sync
    ```

6. Create a `.env` file in the project root and specify the main `.tex` file:

```env
TARGET="Куприянов_И221_диплом.tex"
```

## Build through latexmk

Build the main document:

=== "Task"

    ```bash
    task latex:local
    ```

=== "Manual"

    ```bash
    latexmk "Куприянов_И221_диплом.tex"
    ```

For another `.tex` file:

=== "Task"

    ```bash
    task latex:local -- --target "<file>.tex"
    ```

=== "Manual"

    ```bash
    latexmk "<file>.tex"
    ```

Configuration lives in `.latexmkrc`: it uses `LuaLaTeX` with `--shell-escape`, `biber`, auxiliary files go to `.aux_files`, and the ready PDF stays in the project root. `--shell-escape` is required by PyLuaTeX so it can start Python during compilation.

## Build through the Python script

If it is more convenient to read `TARGET` from `.env`, use the script. By default it also builds the document through `latexmk`:

=== "Task"

    ```bash
    task latex:local
    ```

=== "Manual"

    ```bash
    uv run python scripts/build_latex_manual.py
    ```

To build another file without changing `.env`, pass it explicitly:

=== "Task"

    ```bash
    task latex:local -- --target "<file>.tex"
    ```

=== "Manual"

    ```bash
    uv run python scripts/build_latex_manual.py --target "<file>.tex"
    ```

To disable `latexmk` and run the old manual chain `lualatex`, `biber`, `lualatex`, `lualatex`, pass the flag:

=== "Task"

    ```bash
    task latex:manual_chain
    ```

=== "Manual"

    ```bash
    uv run python scripts/build_latex_manual.py --no-latexmk
    ```

!!! note "When manual mode is needed"
    This mode is slower on repeated builds: in the current project it takes about 53-54 seconds every time, compared with about 18 seconds for a repeated `latexmk` run.

## Fully manual compilation

This method is only needed for diagnostics or when `latexmk` is unavailable. In a normal build without Docker, use `latexmk`: the first run in this project can take about 74 seconds, while repeated builds drop to about 18 seconds. The manual chain through `--no-latexmk` takes about 53-54 seconds every time. In `scripts/build_latex_manual.py`, this mode is enabled with `--no-latexmk`.

Create a directory for auxiliary files:

```bash
mkdir .aux_files
```

Because the project uses `biblatex` with the `biber` backend and PyLuaTeX, one `lualatex` run is not enough, and every `lualatex` run must include `--shell-escape`:

??? example "Manual chain for any `.tex` file"
    ```bash
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<file>.tex"
    biber ".aux_files/<file>.bcf"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<file>.tex"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "<file>.tex"
    ```

For the main project file:

??? example "Manual chain for the main project file"
    ```bash
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    biber ".aux_files/Куприянов_И221_диплом.bcf"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    lualatex --shell-escape -synctex=1 -interaction=nonstopmode -output-directory=".aux_files" "Куприянов_И221_диплом.tex"
    ```

After the build, the final PDF will be in `.aux_files`. Move it to the project root:

```bash
mv ".aux_files/<file>.pdf" .
```

In Windows `cmd` for the main file:

```bat
move ".aux_files\Куприянов_И221_диплом.pdf" .
```

[^latexmk-cache]: `latexmk` service files help determine which document dependencies changed: bibliography, included `.tex` files, images, and auxiliary LaTeX artifacts. That is why a repeated build is usually shorter than the full manual chain.
