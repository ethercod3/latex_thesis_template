# Splitting PDF into color and B/W pages

Use this command when you need two versions of the final PDF: one file with color pages only and one file with black-and-white pages only.

=== "Task"

    ```bash
    task pdf:split-color -- Куприянов_И221_диплом.pdf
    ```

=== "Manual"

    ```bash
    docker compose --profile latex run --build --rm latex python3 scripts/split_pdf_color.py Куприянов_И221_диплом.pdf
    ```

For an input file named `document.pdf`, the script creates:

| File | Contents |
| --- | --- |
| `document_color.pdf` | Only pages where C, M, or Y coverage is above the threshold |
| `document_bw.pdf` | All remaining pages |

## How color is detected

`scripts/split_pdf_color.py` runs Ghostscript with the `inkcov` device:

```bash
gs -q -dSAFER -dBATCH -dNOPAUSE -o - -sDEVICE=inkcov document.pdf
```

A page is considered color if the maximum C/M/Y coverage is above the threshold. The default threshold is `0.00001` to ignore zero values and small numeric noise.

To use a different threshold:

```bash
task pdf:split-color -- document.pdf --threshold 0.001
```

## Why qpdf is used

Ghostscript is useful for color analysis, but exporting through `pdfwrite` redraws pages and may change their rotation or geometry. Exporting is therefore done by `qpdf`, which copies selected pages from the source PDF without redrawing them.

The total number of pages in `*_color.pdf` and `*_bw.pdf` should match the number of pages in the source PDF.

## Dependencies

The Docker command uses the project LaTeX image, where Ghostscript and `qpdf` are already installed.

For a local run without Docker, install:

| Tool | Check |
| --- | --- |
| Ghostscript | `gs --version` |
| qpdf | `qpdf --version` |

```bash
uv run python scripts/split_pdf_color.py document.pdf
```
