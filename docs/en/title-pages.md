# Title page and assignment

LaTeX inserts the title page from `титульник.pdf` at the beginning of the document. Therefore `титульник.pdf` must be in the project root before compilation. The same applies to other PDFs, images, and listings included from `.tex`.

The project contains:

| File | Purpose |
| --- | --- |
| `docx/титульник.docx` | DOCX source for the title page |
| `docx/задание.docx` | DOCX source for the assignment |
| `титульник.pdf` | PDF inserted into LaTeX |
| `задание.pdf` | PDF inserted into LaTeX |

Conversion through Docker:

=== "Task"

    ```bash
    task docx
    ```

=== "Manual"

    ```bash
    docker compose --profile docx up
    ```

The profile takes all `docx/*.docx` files and places PDFs with the same names into the project root, for example:

`docx/титульник.docx` {{ arrow }} `титульник.pdf`

During conversion, the profile skips blank pages.[^blank-pages] If the PDF must be preserved as-is, run the profile with `SKIP_BLANK_PAGES=0`:

=== "Task"

    ```bash
    task docx:keep-blank
    ```

=== "Manual"

    ```bash
    docker compose --profile docx run --rm -e SKIP_BLANK_PAGES=0 docx_pdf
    ```

An alternative is to open the DOCX in Microsoft Word and export it to PDF manually: `File` {{ arrow }} `Export` {{ arrow }} `Create PDF/XPS`.

For the title page and assignment, save the PDFs in the project root as `титульник.pdf` and `задание.pdf`.

[^blank-pages]: This is intended for DOCX templates where a blank page can appear because of layout or export behavior. If a blank page is required by formatting rules, `SKIP_BLANK_PAGES=0` preserves the original conversion result.
