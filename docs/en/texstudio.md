# TeXstudio setup

The project uses `LuaLaTeX` and `biblatex` with the `biber` backend. The recommended TeXstudio setup is to run `latexmk`, which reads settings from `.latexmkrc`.

1. Open `Options` {{ arrow }} `Configure TeXstudio` {{ arrow }} `Commands`.

<img src="/assets/texstudio_conf.png" height=500>

2. In the `Latexmk` field, enter:

```text
latexmk %.tex
```

3. Open `Options` {{ arrow }} `Configure TeXstudio` {{ arrow }} `Build`.

4. In `Default Compiler`, choose `Latexmk`.

<img src="/assets/texstudio_build.png" height=500>

Before the first build, make sure `python`, `latexmk`, `lualatex`, and `biber` are available in `PATH`. When TeX Live is installed, `latexmk`, `lualatex`, and `biber` are usually available together with the distribution. Python is required by PyLuaTeX during LaTeX compilation. The ready PDF will be created in the project root, and auxiliary files will be placed into `.aux_files`.

The fully manual scheme with separate `lualatex` and `biber` runs is described at the end of [Build without Docker](manual-build.md#fully-manual-compilation).
