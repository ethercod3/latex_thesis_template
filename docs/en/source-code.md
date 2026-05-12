# Source code in appendices

## If there is no code

If there are no source files and you need to compile the project without them, comment out these lines at the end of the `.tex` file:

```latex
\newpage
\input{appendix_b.tex}
\newpage
\input{include_listings.tex}
```

In LaTeX, comments start with `%`.

## If code exists

Place the code at the same level as the LaTeX project directory.[^vault-path]

For Docker builds, the code path is configured through `.env`:

```env
VAULT_PATH="/vault_code"
VAULT_OS_PATH="../vault_diploma"
```

`VAULT_OS_PATH` is the path on your machine, and `VAULT_PATH` :material-information-outline:{ title="Path inside the Linux container where Docker mounts the source code directory." } is the path inside the container.

## In CI

The PDF GitHub Actions workflow checks out the private repository `ethercod3/diploma_code` into `vault_diploma`. This requires the `VIEW_DIPLOMA_CODE` secret with read-only access to that repository.

CI creates `.env` itself with `VAULT_OS_PATH="./vault_diploma"` and `VAULT_PATH="/vault_code"`, so the local `.env` file is not committed.

[^vault-path]: During local LaTeX compilation, files are referenced by the path `../vault_diploma/<file>`. In Docker builds, `VAULT_OS_PATH` points to this directory on your machine, while `VAULT_PATH` sets the path where the same directory is visible inside the Linux container.
