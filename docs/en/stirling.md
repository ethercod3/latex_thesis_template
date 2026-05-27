# Stirling PDF

Stirling PDF is a local web interface for working with PDFs. In this project it is exposed as a separate Docker profile for manual PDF review and side-by-side checking in the browser.

## Launch

=== "Task"

    ```bash
    task stirling
    ```

=== "Manual"

    ```bash
    docker compose --profile stirling up -d stirling_pdf
    ```

After startup, the interface is available at `http://localhost:8080`.

## Configuration

Set these variables in `.env`:

| Variable | Purpose |
| --- | --- |
| `STIRLING_PORT` | Host port, defaults to `8080` |
| `STIRLING_ADMIN_PASSWORD` | Initial administrator password for the first startup |

Example:

```env
STIRLING_PORT="8080"
STIRLING_ADMIN_PASSWORD="stirling"
```

The admin password is only used on the first start, before anything exists in `pdf_diff/stirling/configs`. If the container already ran once, changing `.env` will not rewrite the existing database.

The `stirling` service in `docker-compose.yaml` also enables:

- `SECURITY_ENABLELOGIN=true`
- `DISABLE_ADDITIONAL_FEATURES=false`
- `LANGS=en_GB`

## Related commands

```bash
task stirling:logs
task stirling:down
```

## Data directories

The profile mounts these directories:

- `pdf_diff/stirling/configs`
- `pdf_diff/stirling/logs`
- `pdf_diff/stirling/pipeline`

They keep settings and logs persistent across container recreation.

## When to use it

Stirling PDF is useful when you need to:

- open a finished PDF in the browser without a local PDF viewer;
- quickly inspect how a rebuilt document looks;
- manually compare two PDF versions in separate tabs or windows;
- share a PDF for review without installing extra tooling.

If you need an automated diff between two commits, the project already has `task diff` for that workflow.
