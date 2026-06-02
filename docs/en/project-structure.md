# Project Structure

| Path | Purpose |
| --- | --- |
| `*.tex` | Main LaTeX document |
| `preamble/` | Preamble settings |
| `bibliography.bib` | Dummy bibliography |
| `scripts/` | Selected helper scripts |
| `tasks/` | Task commands |
| `docs/` | Documentation, if enabled |

Code listings depend on `code_listing_mode`: `inline` means manual `lstlisting`
blocks, while `external` allows LaTeX to reference a separate source directory.
